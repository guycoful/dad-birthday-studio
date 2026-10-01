#!/usr/bin/env python3
"""Join Stop & Save MP4 parts into one birthday film.

MediaRecorder cannot append into an existing file, so the studio saves each
stretch as its own part. Download dad-60-parts.json from the studio and run:

    bash scripts/concat_mp4_parts.sh dad-60-parts.json

Or pass files directly (no per-part trim):

    bash scripts/concat_mp4_parts.sh dad-60-part-01.mp4 dad-60-part-02.mp4
"""
import json
import os
import shlex
import subprocess
import sys


def has_audio(path):
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=index", "-of", "csv=p=0", path,
        ],
        capture_output=True, text=True,
    )
    return bool(probe.stdout.strip())


def load_parts(args):
    if args[0].endswith(".json"):
        with open(args[0], encoding="utf-8") as fh:
            data = json.load(fh)
        parts = data.get("parts") or []
        output = data.get("output") or "dad-60-birthday.mp4"
        base = os.path.dirname(os.path.abspath(args[0])) or "."
        return parts, output, base
    return [{"file": name, "trimToSec": None} for name in args], "dad-60-birthday.mp4", os.getcwd()


def resolve_file(name, base):
    if os.path.isabs(name) and os.path.isfile(name):
        return name
    for folder in (base, os.getcwd()):
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate):
            return candidate
    sys.exit(f"Missing part: {name}")


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)
    parts, output, base = load_parts(sys.argv[1:])
    if not parts:
        sys.exit("No parts listed")

    inputs = []
    for part in parts:
        path = resolve_file(part["file"], base)
        trim = part.get("trimToSec")
        inputs.append((path, trim, has_audio(path)))

    cmd = ["ffmpeg", "-y"]
    for path, _, _ in inputs:
        cmd += ["-i", path]
    extra = []
    for i, (path, trim, audio) in enumerate(inputs):
        if audio:
            continue
        # duration for anullsrc: trim, or container duration
        if trim:
            dur = float(trim)
        else:
            probe = subprocess.run(
                [
                    "ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", path,
                ],
                capture_output=True, text=True, check=True,
            )
            dur = max(0.1, float(probe.stdout.strip() or "0.1"))
        extra.append((i, dur))

    for _, dur in extra:
        cmd += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]

    extra_input_at = {slide_i: (len(inputs) + n) for n, (slide_i, _) in enumerate(extra)}
    filters = []
    labels = []
    for i, (_, trim, audio) in enumerate(inputs):
        v, a = f"v{i}", f"a{i}"
        if trim:
            filters.append(f"[{i}:v]trim=duration={trim},setpts=PTS-STARTPTS[{v}]")
        else:
            filters.append(f"[{i}:v]setpts=PTS-STARTPTS[{v}]")
        if audio:
            if trim:
                filters.append(f"[{i}:a]atrim=duration={trim},asetpts=PTS-STARTPTS[{a}]")
            else:
                filters.append(f"[{i}:a]asetpts=PTS-STARTPTS[{a}]")
        else:
            src = extra_input_at[i]
            filters.append(f"[{src}:a]asetpts=PTS-STARTPTS[{a}]")
        labels.append(f"[{v}][{a}]")
    n = len(inputs)
    filters.append("".join(labels) + f"concat=n={n}:v=1:a=1[v][a]")
    cmd += [
        "-filter_complex", ";".join(filters),
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        output,
    ]
    print("Running:", " ".join(shlex.quote(c) for c in cmd))
    subprocess.check_call(cmd)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()

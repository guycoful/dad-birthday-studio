#!/usr/bin/env bash
# Remux/transcode a browser-exported slideshow so picky players (TV, QuickTime)
# get H.264 video + AAC audio. Video is copied when it is already H.264.
set -euo pipefail
in="${1:-}"
if [[ -z "$in" || ! -f "$in" ]]; then
  echo "Usage: bash scripts/make_compatible_mp4.sh dad-60-birthday.mp4" >&2
  exit 1
fi
out="${2:-${in%.*}-aac.mp4}"
ffmpeg -y -i "$in" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 160k -movflags +faststart "$out"
echo "Wrote $out"

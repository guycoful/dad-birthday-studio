#!/usr/bin/env bash
# Stitch studio MP4 parts into one file. The browser cannot append into an
# open MP4, so Stop & Save writes part files plus dad-60-parts.json.
#
#   bash scripts/concat_mp4_parts.sh dad-60-parts.json
#   bash scripts/concat_mp4_parts.sh dad-60-part-01.mp4 dad-60-part-02.mp4
#
# A part saved with Stop & Save mid-slide is trimmed to the last fully
# finished slide (trimToSec in the json) so the next part can restart that
# slide without duplicating it.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$root/scripts/concat_mp4_parts.py" "$@"

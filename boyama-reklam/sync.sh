#!/bin/sh
# Copy the shared library, vendor scripts and fonts into every ad project.
cd "$(dirname "$0")"
for d in reklam-1 reklam-2 reklam-3; do
  mkdir -p "$d/assets/audio"
  rm -rf "$d/shared" "$d/vendor" "$d/assets/fonts"
  cp -r ortak/shared ortak/vendor ortak/base.css "$d/"
  rm -f "$d/shared/base.css"
  cp -r ortak/assets/fonts "$d/assets/"
  cp hyperframes.json "$d/"
  [ -f "$d/meta.json" ] || printf '{"id":"%s","name":"%s"}\n' "$d" "$d" > "$d/meta.json"
done

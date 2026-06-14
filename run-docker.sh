#!/usr/bin/env bash

docker run --rm -it \
  -v "$(pwd):/work" \
  -w /work \
  ig-bild \
  ig_bild "$@"
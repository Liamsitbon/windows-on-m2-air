#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
[ "$#" = 2 ] && [ "$1" = --disk ] || { echo "usage: sudo $0 --disk diskXsY" >&2; exit 2; }
DISK=$2
case "$DISK" in *[!a-zA-Z0-9]*|'') exit 2;; esac
case "$DISK" in disk[0-9]*s[0-9]*) ;; *) exit 2;; esac
exec python3 "$ROOT/tools/read_efi_log.py" "/dev/r$DISK" --output "$ROOT/.local/efi-logs/latest.log"

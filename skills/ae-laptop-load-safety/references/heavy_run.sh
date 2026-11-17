#!/bin/sh
# heavy_run.sh: run ONE heavy command at a time, at low priority, behind a lock.
# Usage: sh heavy_run.sh COMMAND [ARGS...]
# Example: sh heavy_run.sh ffmpeg -v error -y -threads 4 -i in.mp4 out.mp4
# The lock is a folder (mkdir is atomic). A stale lock whose process is gone is removed.
LOCK="${AE_LOCK_DIR:-${TMPDIR:-/tmp}/agent-editor-heavy.lock}"
WAIT_MAX="${AE_WAIT_MAX_S:-900}"
HERE="$(cd "$(dirname "$0")" && pwd)"
waited=0
while ! mkdir "$LOCK" 2>/dev/null; do
  OLD="$(cat "$LOCK/pid" 2>/dev/null)"
  if [ -n "$OLD" ] && ! kill -0 "$OLD" 2>/dev/null; then
    echo "removing stale lock from process $OLD"; rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null; continue
  fi
  [ "$waited" -ge "$WAIT_MAX" ] && { echo "gave up waiting for another heavy job after ${WAIT_MAX}s" >&2; exit 3; }
  echo "another heavy job is running (pid ${OLD:-unknown}); waiting"; sleep 20; waited=$((waited + 20))
done
echo $$ > "$LOCK/pid"
trap 'rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null' EXIT INT TERM
if [ -z "$AE_SKIP_CALM" ]; then
  tries=0
  until sh "$HERE/calm_check.sh" "${AE_DISK_PATH:-.}"; do
    tries=$((tries + 1)); [ "$tries" -ge 30 ] && { echo "machine never became calm" >&2; exit 4; }
    sleep 20
  done
fi
nice -n 15 "$@"

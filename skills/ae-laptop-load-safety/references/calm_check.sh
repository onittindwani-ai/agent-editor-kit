#!/bin/sh
# calm_check.sh: read only check that the machine is calm enough to start ONE heavy job.
# Usage: sh calm_check.sh [PATH_TO_CHECK_DISK_ON]   (default: current folder)
# Exit 0 = calm, exit 1 = wait, exit 2 = cannot decide. Thresholds are starting values, tune them.
P="${1:-.}"
MIN_FREE_GB="${AE_MIN_FREE_GB:-5}"
MAX_LOAD_FRACTION="${AE_MAX_LOAD_FRACTION:-0.7}"
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
  NCPU="$(sysctl -n hw.ncpu)"
else
  NCPU="$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)"
fi
LOAD="$(uptime | sed 's/.*load averages*: *//' | awk '{gsub(",","",$1); print $1}')"
FREE_GB="$(df -Pk "$P" | awk 'NR==2 {printf "%d", $4/1048576}')"
BUSY="$(ps -axo comm= | grep -ciE '(^|/)(ffmpeg|mlx_whisper|whisper|whisper-cli|blender)$|remotion' || true)"
PAGING="unknown"
if [ "$OS" = "Darwin" ]; then
  A="$(vm_stat | awk '/Pageouts/ {gsub("\\.","",$2); print $2}')"
  sleep 5
  B="$(vm_stat | awk '/Pageouts/ {gsub("\\.","",$2); print $2}')"
  PAGING="$((B - A)) pageouts in 5 s"
  PAGEDELTA=$((B - A))
else
  PAGEDELTA=0
fi
echo "cpus=$NCPU load1=$LOAD free_gb=$FREE_GB heavy_processes=$BUSY paging=$PAGING"
FAIL=0
awk -v l="$LOAD" -v n="$NCPU" -v f="$MAX_LOAD_FRACTION" 'BEGIN{exit !(l > n*f)}' && { echo "WAIT: load too high"; FAIL=1; }
[ "$FREE_GB" -lt "$MIN_FREE_GB" ] && { echo "WAIT: under $MIN_FREE_GB GB free disk"; FAIL=1; }
[ "$PAGEDELTA" -gt 300 ] && { echo "WAIT: the machine is paging memory to disk"; FAIL=1; }
[ "$BUSY" -gt 0 ] && { echo "WAIT: $BUSY heavy looking processes already running"; FAIL=1; }
[ "$FAIL" -eq 0 ] && echo "calm"
exit "$FAIL"

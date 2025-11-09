#!/bin/bash

TOTAL_LOOPS=380
STEP_SLEEP=0.1
LOOP_SLEEP=1
CHECK_SLEEP=5      # 檢查前等待 5 秒
CHECK_EACH=10

# 取得腳本執行所在目錄
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_FLAG="$DIR/running.txt"

# ==================
command -v xdotool >/dev/null 2>&1 || { echo "請先安裝 xdotool"; exit 1; }

# ==================
# 建立 running.txt（寫入開始時間與 PID）
{
  echo "START_AT=$(date '+%Y-%m-%d %H:%M:%S.%3N')"
  echo "PID=$$"
  echo "status=running"
} > "$RUN_FLAG"

# ==================
press() { xdotool key "$@"; sleep "$STEP_SLEEP"; check_flag; }
type_text() { xdotool type --delay 0 "$1"; sleep "$STEP_SLEEP"; check_flag; }

check_flag() {
  # 只要 running.txt 被刪掉就立即退出
  [[ -f "$RUN_FLAG" ]] || { echo "偵測到 $RUN_FLAG 已移除，停止。"; exit 0; }
}

# ==================
for i in $(seq 1 "$TOTAL_LOOPS"); do
  check_flag
  sleep "$LOOP_SLEEP"

  press Right

  # 每 10 次檢查一次 running.txt
  if (( i % "$CHECK_EACH" == 0 )); then
    sleep "$CHECK_SLEEP"
    check_flag
  fi
done

rm $RUN_FLAG
#!/bin/bash

TOTAL_LOOPS=10
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

sleep "$LOOP_SLEEP"

# ==================
for i in $(seq 1 "$TOTAL_LOOPS"); do
  check_flag
  

  # =====================

  
  # 1) 開啟選單（預設用鍵盤的「Menu」鍵；若要叫出功能表列可改成 Alt）
  press shift+F10
  # 若你的應用是用 Alt 叫出功能表，改用這行：
  # press alt

  # 2) 上
  press Up

  # 3) Enter
  press Return

  # 4) Ctrl + A（全選）
  press Home

  # 5) 輸入檔名：現在的時間：YYYYMMDD-HHmmSS.png
  #    注意：冒號在部分檔案系統不可用，若要存檔請考慮改成空格或底線。
  seqnum=$(printf "%04d" "$i")
  fname="$(date +%Y%m%d-%H%M%S.%3N)-${seqnum}-"
  type_text "$fname"

  press End
  type_text ".png"

  # 6) Enter
  press Return
  sleep 0.5

  xdotool click 1
  sleep 0.2

  press Shift+Tab

  # press Esc

  # sleep 1

  # press Esc

  # sleep 1

  # press Esc

  # 7) 下
  press Down

  # =====================

  # 每 10 次檢查一次 running.txt
  if (( i % "$CHECK_EACH" == 0 )); then
    sleep "$CHECK_SLEEP"
    check_flag
  fi
done


rm $RUN_FLAG
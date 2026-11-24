#!/usr/bin/env bash
# Chạy TOÀN BỘ cổng và trả về mã thoát đúng.
#
# Vì sao tệp này tồn tại (docs/46 §3.3): tôi từng chạy vòng quét bằng
#   for s in ...; do out=$(python3 scripts/$s.py 2>&1 | tail -1); case "$out" in *FAIL*) ...
# và nó báo "FAIL=0" trong khi cổng 23 đang ĐỎ. Lý do: `tail -1` lấy dòng CUỐI,
# mà dòng cuối của một cổng đỏ là một dòng chi tiết ("  - seed lệch sổ ..."),
# không phải dòng tổng kết "FAIL —". Phép so khớp không bao giờ chạy.
# Một vòng quét báo xanh sai còn tệ hơn không quét.
#
# Quy tắc: dùng MÃ THOÁT của cổng, không dùng chữ trong output.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1

PY_GATES=(
  check_portal check_decisions check_actions check_pm_supabase check_gate_wiring
  check_claims check_docs_links find_contradictions check_agent_rules
  check_egress_lock verify_kit_bundle verify_invariants check_invariants_coverage
  kvu_invariants check_sdk check_sdk_errors check_sdk_manifest check_gate_ladder
  verify_pop_decay verify_protocol_math receipt_lock check_sdk_drift check_specs
)
NODE_GATES=(check_portal_render)
# check_pitch_deck cần pypdf — chạy trong CI (có requirements), không chạy ở máy trống.

fail=0
ran=0
# Cổng nào cần cờ mới THẬT SỰ kiểm. `check_specs.py` không có cờ thì in help
# và trả 0 — một cổng "xanh" vì không làm gì. Đây đúng lỗi docs/40: một cổng
# chưa từng chạy thì không phải một cổng.
declare -A GATE_ARGS=(
  [check_specs]="--tick --self-test"
)

for s in "${PY_GATES[@]}"; do
  [ -f "scripts/$s.py" ] || continue
  ran=$((ran + 1))
  args=${GATE_ARGS[$s]:-}
  # shellcheck disable=SC2086
  out=$(python3 "scripts/$s.py" $args 2>&1)
  rc=$?
  if [ $rc -eq 0 ]; then
    printf '✅ %-26s %s\n' "$s" "$(printf '%s' "$out" | grep -E 'PASS|passed|PASSED|OK' | tail -1 | cut -c1-64)"
  else
    fail=1
    printf '❌ %-26s rc=%d\n' "$s" "$rc"
    printf '%s\n' "$out" | tail -6 | sed 's/^/     /'
  fi
done

for s in "${NODE_GATES[@]}"; do
  [ -f "scripts/$s.mjs" ] || continue
  ran=$((ran + 1))
  out=$(node "scripts/$s.mjs" 2>&1)
  rc=$?
  if [ $rc -eq 0 ]; then
    printf '✅ %-26s %s\n' "$s" "$(printf '%s' "$out" | tail -1 | cut -c1-64)"
  else
    fail=1
    printf '❌ %-26s rc=%d\n' "$s" "$rc"
    printf '%s\n' "$out" | tail -6 | sed 's/^/     /'
  fi
done

if [ $fail -eq 0 ]; then
  echo "TẤT CẢ XANH — $ran cổng (mã thoát, không đọc chữ)"
  exit 0
fi
echo "CÓ CỔNG ĐỎ — $ran cổng đã chạy"
exit 1

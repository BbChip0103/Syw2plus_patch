# APPROVALS lap723 압축 보존 (2026-09-28, lap727 work)

원문 20줄, SHA256 `635e86c33226c4417fa99d50ef10a00b00685ce668b353e80c3351982bfa3ed8`.
lap723의 middle 검수 요청(R3 raw CONFIRMED, v5 수정 PASS, ALT/Ctrl/Shift 드래그·공격·부대저장로드
미완결)은 lap724가 같은 세션에서 v5로 직접 재측정해 전부 PASS로 해소했다(STATUS lap724 참고).
전문 아래 원문 그대로 보존, 삭제·재해석 없음.

---

- [ ] **2026-09-28 lap723 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G5 R3 raw CONFIRMED,
  v5 수정 PASS):** 2026-09-28 01:30/01:31 사용자 지시(R3 최우선, G5 완료 체크리스트 A~H)를 수행.
  신규 진단 브리지 op(`patches/population/g5_r3_death_bridge.c`, 원본 사망처리 함수
  `FUN_00409C70`을 thiscall로 직접 호출 — 공유 `runtime_bridge.c`와 G2가 pin한
  `G2_APPROVED_BRIDGE_SHA256`은 무수정·무영향, `--bridge-source` 옵션 1개만 `build_runtime_bridge.py`에
  추가)로 v4에서 50선택→인덱스0~29 30기 실제 사망→count=20·생존20기(인덱스30~49) 상태를 만들어
  STOP·MOVE 측정 — **생존 20/20 전부 미수신(R3 정적 PLAUSIBLE→raw CONFIRMED)**. 신규
  `patches/selection/g5_selection_cap50_v5.py`(check_count 게이트를 "count>20 또는 entries[20:50]에
  살아있는 칸"으로 확장, 나머지 v4와 byte-identical — pytest 5개로 구조 확정)로 같은 절차 재측정 —
  **생존 20/20 전부 수신(PASS)**. 원본 대조(20선택→10제거, 인덱스10~19 생존)도 10/10 PASS(방법론 자체
  유효 확인). v5 STOP/HOLD/PATROL 50/50 회귀(`g5_stop_hold_patrol_v4_probe.py` monkeypatch, 파일
  무수정) PASS. 원본 SHA 4회 전부 `source_unchanged=true`, cleanup 매회 프로세스 잔류 0, 크래시 0.
  `make check` **1106 passed(898.62s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **미완결:**
  ALT/Ctrl/Shift 드래그·공격·부대지정/저장로드는 `g5_command_coverage_probe.py`의 자체 목적지 캘리브레이션
  단계(이번 world(93,56) 지형에서 후보 destination 7개 중 1개만 `move_ok`)가 2회 연속 실패해 v5로
  직접 재측정하지 못했다 — v5 게이트에 도달하기 전 단계의 실패이므로 이 도구 자체의 기존 취약점으로
  판단했으나 middle 검수 필요. **work tier 판단으로 다음 middle 독립 검수를 요청한다**(R3 raw 재계산,
  v5가 check_count 외 v4와 byte-identical이라는 pytest 근거의 타당성, 미완결 회귀를 "byte-identical
  이므로 이전됨" 추론으로 충분히 볼지 여부, G5 완료 체크리스트 다음 항목 순서). 근거
  `../history/laps/20260928_lap723_work_g5_r3_live_confirmed_v5_fix_pass.md`, `loop/ESCALATE_SOL` lap721 절 참고.

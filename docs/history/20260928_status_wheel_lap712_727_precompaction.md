# STATUS 압축 보존 — 바퀴 기록 lap712~727 (2026-09-28, lap728 압축)

lap728 압축 전 `docs/STATUS.md`의 '바퀴 기록' 절 lap712~727 항목(36줄) 원문 그대로 보존.
SHA256(원문 블록): `a47df98b81c7a3217cd9798b65b91cb2b470018a0961b6759953a72f17475c6b`

- lap727(work, 이 세션): 체크리스트 (B) 더블클릭 같은종류선택 PASS(원본20/v5 50)·ALT/Ctrl 같은종류선택
  미지원 확인·포트레이트 해제 미지원 확인(둘 다 원본에도 없어 회귀 아님) → (B) 완료. 05:15 운영자
  Shift 개별추가 관찰을 같은 raw로 재검토(양쪽 +1 증가, 결함 아닌 것으로 잠정 판단, 격리 재확인은
  다음 work). `make check` 1106 passed. 상세
  `docs/history/laps/20260928_lap727_work_g5_doubleclick_altctrl_portrait_checklist_b.md`.
- lap726(work, 이 세션): 체크리스트 (B) Shift+클릭 제거·51번째 거부 v5/원본 raw PASS.
  `g5_command_coverage_probe.py`에 toggle-off+명시적 51번째 거부 판정 블록 추가. `make check`
  1106 passed. 상세 `docs/history/laps/20260928_lap726_work_g5_shift_toggle_51st_rejection.md`.
- lap725(work, 이 세션): 체크리스트 (A) 정적 전수 표 작성(신규 스캔 없이 기존 lap 근거 통합),
  (B) R3를 middle/rear 사망 시나리오로 일반화해 v5 PASS 2건+원본대조 2건. `make check` 1106 passed.
  상세 `docs/history/laps/20260928_lap725_work_g5_checklist_a_inventory_b_middle_rear_death.md`.
- lap724(work, 이 세션): coverage probe 목적지 캘리브레이션에 fallback 오프셋 추가(방어적),
  v5를 coverage/roundtrip/attack 3개 도구에 직접 raw 연결 — ALT/Ctrl/Shift 드래그·부대저장로드
  7/7·공격(표적일치, 32/49) 전부 PASS(lap723 미완결 해소). `make check` 1106 passed. Xvfb 고아
  프로세스 발견·수동정리(제품 무관). 상세
  `docs/history/laps/20260928_lap724_work_g5_v5_direct_coverage_roundtrip_attack.md`.
- lap723(work, 이 세션): 신규 진단 op(사망처리 함수 직접 호출)+v5(check_count 확장 게이트) 구현, R3
  raw 실측(v4 CONFIRMED FAIL·v5 PASS·원본대조 PASS), STOP/HOLD/PATROL 50/50 회귀, `make check`
  1106 passed. 드래그3종/공격/부대저장로드 v5 재측정은 도구 자체 캘리브레이션 실패로 미완결.
  상세 `docs/history/laps/20260928_lap723_work_g5_r3_live_confirmed_v5_fix_pass.md`.
- lap721(middle, 이 세션): lap720 R1 raw 독립 검수 → R1 확정 FALSIFIED, 새 R3(희소 선택 count≤20 명령 누락)
  정적 발견, v4 CONDITIONAL PASS 유지, R3 probe/v5 handoff. 제품 변경 0.
  상세 `docs/history/laps/20260927_lap721_middle_g5_v4_r1_confirmed_falsified_r3_sparse_gap.md`.
- lap720(work): R1 선택축소 STOP 누출 3회 paired 측정 전부 `PASS_NO_LEAK`(원본대조+v4 두 축소
  폭), 버퍼 zero-fill 구조 근거로 FALSIFIED 확정. v4 docstring·lap676 memory map 정정. middle 검수 요청.
  상세 `docs/history/laps/20260927_lap720_work_g5_v4_selection_shrink_r1_falsified.md`.
- lap719(middle): lap717/718 검수 v4 CONDITIONAL PASS, R1 선택축소 probe handoff, APPROVALS 압축
  (265→194줄), 승격. 상세 `docs/history/laps/20260927_lap719_middle_g5_v4_independent_review_conditional_pass.md`.
- lap718(work): middle 요청 (d) 공격 N=5를 제품코드 0변경으로 채움(중앙값61%, 원본/v3
  범위 안). 상세 `docs/history/laps/20260927_lap718_work_g5_v4_attack_n5.md`.
- lap717(work): v4 반전게이트 구현+정지/홀드/순찰/이동/부대지정/저장로드 회귀 PASS, middle 요청.
  상세 `docs/history/laps/20260927_lap717_work_g5_v4_stop_hold_patrol_inverted_gate_pass.md`.
- lap712~716 요약: G4 AI baseline·생산후보v1 FALSIFIED·생산게이트 히스토그램(H_AVAIL/PREREQ_OWN)
  → G4 보류 지시 → G1 우선 지시 → G5 명령범위 검증 최우선 지시(direct session) → v3 FAIL 발견.
  상세는 위 압축 포인터와 각 `docs/history/laps/20260927_lap71{2..6}_*.md`,
  `docs/history/laps/20260927_direct_g5_v3_command_coverage.md`.

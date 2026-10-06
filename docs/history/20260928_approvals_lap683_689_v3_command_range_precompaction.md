# APPROVALS 색인 압축 보존 (lap665·683~689, 원문 18줄)

lap724 압축 시점의 `docs/feedback/APPROVALS.md` "미해결·반려·판정 불명 색인" 절에서 lap665·683~689
(v3 후보 명령범위/공격 검증 계보) 원문 18줄, SHA256
`e06d2986fdde49d2cbcf398d21af75760efd61d9624d89e80b054d34329d5761`. 이 항목들은 이후 v4/v5로
교체·재검증됐다(STATUS, `docs/history/laps/20260927_lap717_*`~`20260928_lap724_*`). 아래 그대로 보존한다.

---

- [ ] 2026-09-26 lap685 work tier(Claude Code Sonnet, 다음 middle 검수 대기): lap684 handoff("청크 재호출 사이 order-type4 전용 필드 손실") 가설과 17:55 운영자 지시("옛 선택 배열 리터럴 잔여") 가설을 gdb 트레이스 3종+v2 대조군+정적 전수 xref 스캔으로 **모두 반증**. 빌더(`FUN_004AE550`) 내부 상태·빌더→writer 디스패치 루프(`0x4AEC60→0x40FF90→0x412540`)는 move/attack 동일(50/50) — 청킹 무관 확정. **v2(청킹 없음) 후보도 `ever_command4_count=0/49`**로 v3와 동일 실패 — 재배치 이후 v2/v3 공통 회귀로 좁혀짐. 옛 배열(`0x899024/28/2A/78`) 리터럴 참조는 원본 전체(raw 52건) 전부 v1 `DIRECT_SITES`/`END_SITES`로 이미 재타깃돼 잔여 0건. 제품 코드 미수정(원인 미확정 상태에서 추측 수정 없음), 신규 도구 5개+테스트 4개, `make check`980 passed(683s). 근거 `../history/laps/20260926_lap685_work_g5_attack_broadcast_field_loss_falsified_relocated_downstream.md`.
- [ ] 2026-09-26 lap684 work tier(Claude Code Sonnet, 다음 middle 검수 대기): v3 후보 `e5004764…` roundtrip(선택/그룹/호출/save-load) **PASS**(후보50/50/50, 원본20/20/20, crash0). 공격은 `command==4` 살아있는 상태 기준이 원본에서도 0으로 나와 판정 필드 결함으로 확인, `+0x384==0x1000004`+3초 누적 `ever_command4_count`로 교체해 원본 2/2 **100%(19/19)** 대비 후보 2/2 **≤1/49**의 재현 가능한 FAIL을 얻었다. 전체 2단은 아직 middle 미검수. 근거 `../history/laps/20260926_lap684_work_g5_v3_roundtrip_pass_attack_command4_blocked.md`.
- [!] 2026-09-26 lap683 중간 tier 독립 검수(Claude Code Opus): v3 후보 `e5004764…`의 크래시 수정과 이동 paired(후보 `command==3` 50/50, 원본 20/20)는 **승인**. 공격 브로드캐스트50은 **불인정** — lap680 `pending!=1` 판정식이 이동 계열 값(`0x1000001`)도 세며, 같은 phase `command==4`는 0/50이었다. lap681 41/50은 원본 paired가 없고 재현되지 않았다. 부대/호출/save-load roundtrip은 v3에서 미실행. 전체 2단 `HOLD/INCONCLUSIVE`, 제품 G5 PASS 아님. 근거 `../history/laps/20260926_lap683_middle_g5_v3_independent_review_hold.md`.
- [!] 2026-09-26 lap665 중간 tier 독립 검수: 후보 `ae495fa5…`의 선택/호출/이동/save-load `50/50/50`과 원본20 대조는 제한 승인. 그러나 DESIGN G5의 **실제 적 대상 공격 명령 50** 증거가 없어 전체 2단은 `INCONCLUSIVE/HOLD`; 제품 G5 PASS 아님.
- [ ] **2026-09-26 lap689 중간 tier 독립 검수(Claude Code Opus 5.5) — G5 사용자 milestone 3단 판단 요청:** 후보 v3
  `e5004764…`, 원본 `b56986e0…`. 단일플레이 2단 **조건부 PASS** — 드래그50(55기 중 5기 미선택)·부대 저장/호출/저장로드
  50/50/50·이동 ever 50/50·크래시0·UI 스크린샷 대조를 원본20 대비 raw로 재확인. 공격50은 `ever_command4`(표적 무관·
  자동교전 오염 가능)가 아니라 t=0 스냅샷 49기 동시 `pending==0x1000004`+클릭 xy(후보-1/2)와 49/49 표적 handle(후보-3)로 승인.
  멀티 동기화 `UNKNOWN`(명령당 레코드 최대 3회 발행). 사용자 승인 전 제품 G5 PASS 아님. 근거
  `../history/laps/20260926_lap689_middle_g5_full_independent_review_conditional_pass.md`.
- [x] 2026-09-26 lap688 work tier(Claude Code Sonnet, lap689 middle이 검수 완료): 19:25 판정("흔들림 원인 1개
  raw로 고정 → N=5 반복 측정") 실행. 원인 확정: 공격 표적을 드래그/MOVE 이전에 스폰해 자동교전이
  명시적 클릭 전에 표적을 죽이는 레이스였다(원본 5회 중 2회 완전실패, `observed_target_uids` 전 구간
  공백으로 확인). 표적 스폰을 ATTACK 클릭 직전으로 옮겨 수정, 완전실패 재현 소거. 수정 후 N=5: 원본20
  `ever_command4/19`=19,19,5,11,4(중앙값58%), 후보v3(50) `.../49`=30,33,49,27,32(중앙값65%, 원본보다
  낮지 않음). 원본·후보 SHA 10회 전부 불변, cleanup 전부 ok, 제품 EXE 0 변경. 19:25 판정문의 원본
  기준선(85~95%)은 이 표본에서 원본도 미달 — 문자 그대로 PASS 적용 가부는 middle 판정 필요. 근거
  `../history/laps/20260926_lap688_work_g5_attack_probe_spawn_timing_fix_and_n5_measurement.md`.

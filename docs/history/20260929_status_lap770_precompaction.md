# STATUS — 매 바퀴 갱신하는 기억

lap676~763 전문은 기존 압축 포인터와 `docs/history/laps/`에 보존했다. 이번 압축 전 원문은
`docs/history/20260929_status_lap764_precompaction.md`(SHA256
`97d1dbb2dc855bcb394637aa54dde57d5750a07a2262b4800848fea0ea3d8854`, 152줄)에 보존했다.

## 지금 상태

G5는 2026-09-28 01:31 지시로 A~H 전부 재검수 조건부며 v10이 기준 후보다. lap767 middle이
lap766 original20/v10 50 paired raw·fixture·클릭 계약을 독립 재계산해 양쪽 Shift 추가 `1→2`, 제거
`2→1`, 제거 anchor 명령 배제를 확인했다. lap765 이상치는 제품 회귀가 아니라 재현되지 않은 단일 실행
이상치로 해소한다. lap768 work는 진단 gate 조건에서 미니맵 이동·공격·순찰 좌클릭을 원본20/v10 50으로
각각 전원 전달 확인했고, lap769 middle이 raw·명령 신호·후보 SHA를 독립 재계산해 원본 parity를 수용했다.
G5 2단은 제한부 `PASS_WITH_LIMITS`이고 18:4x 사용자 사전 승인 조건을 충족해 **18:45 운영자가 G5 v10
3단 승인·종료를 적용**했다(APPROVALS 확정). 이제 활성 목표는 **G1**이며 G2 전체 점검은 G1 뒤로 순연.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료, **재착수**(lap612 native DirectDraw 2배 계보 `BLOCKED(attribution)`에서) | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(근거 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류 | candidate AI 정책 없음, 사용자 승인 |
| G5 | **v10 종료(사용자 3단 승인, 2026-09-29 18:45)** | 제한 수용: G `BLOCKED(env)`, 미니맵 진단 gate 조건, E 조건부, N/A·edge |

## 지금 막힌 것 (Blockers)

Shift 제품 회귀 의심은 lap767 독립 재검수로 해소됐다. 남은 제한은 G 멀티 `BLOCKED(env)`, 미니맵
정상 game_type UI 경로 미검증, E 조건부와 기존 N/A/edge다. G5는 이 제한을 달고 종료됐다. G1의 마지막
상태는 lap612: native DirectDraw 2배 계보 `BLOCKED(attribution)`·모델 권한 경로 소진이다.

## 검증 상태

lap717~760 상세는 `docs/history/20260929_status_lap751_760_verification_precompaction.md` 및 기존
포인터에 보존했다. lap762~763은 라우터 체인과 `0x97597c` 게이트를 특정했고, lap764가 그 게이트를
격리 write로 연 뒤 실제 명령효과를 paired PASS했다.

- `make doctor`: PASS, 원본 SHA verified, runtime 도구/라이브러리 존재.
- `make check`: **1136 passed, 5 skipped**; ruff/compileall/mypy/context PASS; `SAFETY_PASS`.
- lap765: v10 결정적 재빌드 SHA·길이 불변·byte-exact 원복 PASS, `SAFETY_PASS`; fresh coverage raw
  SHA `660f1d2e…2cb31`, source unchanged/cleanup PASS. Shift add/remove만 의미 기준 FAIL/HOLD.
- lap766: original/v10 fresh paired 모두 `COMPLETE`, source unchanged/cleanup PASS. Shift add는 양쪽
  `1→2`, 제거는 `2→1`, `removed_anchor1=true`, `kept_anchor2=true`, 잔여 anchor 명령 배제 true;
  선택은 원본20/20·v10 50/50. 결과 JSON SHA는 original `5e8f742d…2deb7f`, candidate
  `813435cb…863bf4`; 집중 pytest `12 passed`, 전체 Fast `1134 passed·5 skipped`.
- lap767: 두 raw/fixture/클릭 계약 독립 재계산과 v10 patch-validation PASS. selection patch 59 passed,
  copy-only/버전 거부/원복·범위 PASS; 현재 source Fast 1134 passed·5 skipped, `SAFETY_PASS`.
- lap768: 원본/v10 새 격리 실행에서 이동·공격·순찰 버튼→미니맵 좌클릭 `pending_xy`가 각각 20/20·50/50
  전원 변화, 명령 신호 대응, gate 0→1·LUT 16200·trace fatal0·crash0·cleanup/source unchanged PASS.
  집중 pytest 5 passed, 결과 JSON·캡처·로그 보존, game 사본 삭제. 상세 `docs/history/laps/20260929_lap768_work_g5_minimap_command_modes_paired.md`.
- lap769: lap768 raw 독립 재계산에서 이동 즉시 command3 20/20·50/50, 공격 command3 19/20·49/50+
  pending4 각1, 순찰 지연 command35 20/20·50/50의 원본 parity 확인. v10 결정적 재빌드·원복·거부·범위
  PASS, 현재 source `make check` 1136 passed·5 skipped, `SAFETY_PASS`. 상세
  `docs/history/laps/20260929_lap769_middle_g5_v10_minimap_modes_review_pass_escalate.md`.
- lap764 원본: SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 55기 fixture,
  선택20/20, center `(90,553)` baked, pending_xy20/20, hit-test 성공2967, crash0, cleanup OK.
- lap764 v10: 후보 SHA `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`, 같은 fixture,
  선택50/50, pending_xy50/50, 명령50/50, hit-test 성공1441, crash0, cleanup OK, source unchanged.
- 첫 probe의 0/20은 선행 클릭과 pending_xy-only 측정 오류였고, 보정 후 결과만 채택했다. 실행 사본
  `game/` 3개는 삭제했으며 output/manifest/prefix/log/캡처/JSON은 보존했다.

## 다음 한 가지
- **2026-09-29 18:45 운영자:** G5 종료 적용. 다음 한 가지 = **G1 재착수 전략 1회**(strategy): lap607~612 G1 기록·DESIGN G1 합격 조건(800×600 최종버퍼 2배 확대 불가)을 읽고 BLOCKED(attribution)를 넘는 새 구현 경로 1개를 정해 work 카드로 넘긴다. 이후 work가 구현→실측.
- **2026-09-29 18:4x 사용자(최신):** G5 재질문 금지·lap769 PASS_WITH_LIMITS면 G5 종료 → 다음 한 가지 = **G1 착수**. G2 점검은 G1 뒤로 순연.
- lap768 측정과 lap769 middle 독립 재검수가 완료돼 사전 승인 조건을 충족했다. **다음 한 가지:**
  승격 작업자가 v10 SHA·제한과 사전 승인 적용 조건을 확인해 G5 3단 승인·종료를 기록하고, 재질문 없이
  G1(원본 구도 유지 1600×1200) 착수로 전환한다. G2 전체 점검은 G1 뒤로 순연한다.

## 바퀴 기록

- lap769(middle): lap768 미니맵 이동·공격·순찰 raw/fixture/명령 신호를 독립 재계산해 원본20/v10 50
  parity를 수용했다. v10 패치 안전과 현재 Fast도 fresh PASS. 마일스톤 경계라 `ESCALATE_SOL`; 상세
  `docs/history/laps/20260929_lap769_middle_g5_v10_minimap_modes_review_pass_escalate.md`.
- lap767(middle): lap766 paired raw를 독립 재계산해 Shift 추가/제거·명령 배제 원본/v10 parity를
  확인하고 lap765 이상치를 해소했다. v10 패치 안전·Fast도 fresh PASS. 마일스톤 경계라
  `ESCALATE_SOL`; 상세 `docs/history/laps/20260929_lap767_middle_g5_v10_shift_recheck_pass_escalate.md`.
- lap768(work): 미니맵 이동·공격·순찰 모드의 버튼→좌클릭을 원본20/v10 50으로 fresh paired 측정하고
  probe/test를 확장했다. 세 모드 모두 전원 `pending_xy` 변화·원본 대응, `make check` 1136 passed·5 skipped.
  사용자 3단 경계라 `ESCALATE_SOL`; 상세 `docs/history/laps/20260929_lap768_work_g5_minimap_command_modes_paired.md`.

- lap766(work): original20/v10 50 fresh paired에서 Shift add/remove를 재측정해 양쪽 모두
  `1→2`/`2→1` 및 명령 배제 PASS로 lap765 이상치를 재현하지 못했다. 원본/v10 결과 JSON과
  source/cleanup 불변, 집중 pytest 12 passed, `make check` 1134 passed·5 skipped. 상세
  `docs/history/laps/20260929_lap766_work_g5_shift_paired.md`.

- lap765(middle): 항목 (1)+(2) 제한부 수용, v10 patch/restore·Fast PASS. fresh 핵심 coverage에서
  Shift add `2→0`, remove `0→1` 충돌을 발견해 전체 `HOLD`, 재시도 없이 work paired로 승격. 상세
  `docs/history/laps/20260929_lap765_middle_g5_v10_final_review_hold_shift_click.md`.
- lap764(work): 신규 v2 probe와 회귀 테스트로 원본/v10 paired. 격리 `0x97597c=1`, 55기 fixture,
  baked center 우클릭 결과 `pending_xy` 원본20/20·v10 50/50, 명령 필드도 전원 변화. 상세
  `docs/history/laps/20260929_lap764_work_g5_minimap_command_effect_paired_pass.md`.
- lap763(work, Sonnet5): 12:37/12:57 지시 처리 — 3-필터 브레이크포인트로 `0x41e332`/`0x41e365`가
  무해한 커서-아이콘 분기임을 확정, 유일한 실제 게이트 `call 0x41c450`이 관측 9430회 전부
  `eax=0x0` 반환함을 실측. 게이트 조건을 로비 "게임 타입"(`0x975914==3`) 선택값까지 정적 추적.
  **`0x97597c`를 격리 사본에서 진단 write로 1로 강제하자 `FUN_004516A0` 호출이 0→6232회
  (성공4195/실패2037)로 급증** — 미니맵 렌더/좌표 서브시스템이 죽은 게 아니라 게이트 플래그
  하나가 잠가놓았을 뿐임을 실증(12:37 지시 "성립하면 열어라" 조항 충족). fixture 명령효과는 미측정
  (다음 work 과제). 제품 코드 0 변경(진단 도구 2개 수정), `source_unchanged` 2/2, `cleanup.ok`
  2/2, 크래시 0. `ruff`/`compileall` PASS, `SAFETY_PASS`/`CONTEXT_PASS` PASS(제품 코드 무변경이므로
  lap758~762와 동일 판단으로 전체 `make check` 생략). 상세
  `docs/history/laps/20260929_lap763_work_g5_minimap_router_gate_flag_confirmed.md`.
- **[압축 포인터] lap762 바퀴 기록**(원문 7줄, SHA256
  `94203d7fe82d29d349c6bc97c81006286735ddb788846cc905459dc06b2061cb`, 위 "검증 상태"에 같은 수치
  요약 있음)는 `docs/history/20260929_status_lap762_wheel_precompaction.md`에 원문 보존 — 12:37
  지시 처리, 클릭 라우팅 체인 신규 특정(enqueue→라우터→히트테스트→폴백), LUT 50% 베이킹 확인
  (렌더-죽음 가설 부분 반증), gdb 5-breakpoint로 히트테스트 0회 호출 확정 → 차단 지점을 필터 체인
  3곳으로 좁힘(lap763이 그중 실제 게이트를 확정). 상세
  `docs/history/laps/20260929_lap762_work_g5_minimap_click_router_hittest_blocked_upstream.md`.
- **[압축 포인터] lap756~758 바퀴 기록**(원문 7줄, SHA256 `00822f5735b61c815dc3256f036be49a2835105cc4511cb920179496a4ebd16f`, 이미 위
  "검증 상태"에 같은 수치 요약 있음)는 `docs/history/20260929_status_lap756_758_wheel_precompaction.md`에
  원문 보존. v10 구현+50기 save/load PASS(lap756), 중간값/부대혼합 보완측정 PASS(lap757),
  능력v/미니맵 provenance(lap758)이며 이후 lap759(위젯초기화 확인)·lap760(수확V PASS, 미니맵
  override 반증)으로 이어졌다.
- lap754(middle, Opus5): lap753 v9 독립 재검수 = **(F) PASS**, S3는 정적 전수+runtime 차분 커버로
  재분류, (A) 표 §2b 추가. A~H 2단 판정 완료 → 사용자 3단 재상정(ESCALATE_SOL). `make check` 1122
  passed·5 skipped, `SAFETY_PASS`. 상세 `docs/history/laps/20260928_lap754_middle_g5_f_s3_v9_review_pass_milestone_resubmit.md`.
- **[압축 포인터] lap751~753 바퀴 기록**(원문 17줄, SHA256
  `73369b17116c3a86a7bc05cd6967a38496745d9d803e0547df6f3d2b1f4c1375`, 이미 위 "검증 상태"에 같은
  수치 요약 있음)는 `docs/history/20260929_status_lap751_753_wheel_precompaction.md`에 원문 보존.
- **[압축 포인터] lap739~750 바퀴 기록**(v7 F-2 미지정선택 save/load, v8 H-STALE-TAIL 수정, S3/S4/S5
  탐색, 홀드버튼 편차·해소, lap745·750 middle HOLD 판정 2회)는 위 헤더 압축 파일
  (`docs/history/20260928_status_lap751_precompaction.md`, 그리고 그 파일이 가리키는
  `docs/history/20260928_status_lap717_741_precompaction_v2.md`)에 원문 그대로 보존했다.

G5의 선택/호출/이동/save-load/장시간 runtime 증거와 과거 실패 provenance는 `docs/history/laps/`
및 공유 `temp/Syw2plus_patch/`에 보존한다.

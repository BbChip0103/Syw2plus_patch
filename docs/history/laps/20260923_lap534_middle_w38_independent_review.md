# 2026-09-23 | lap 534 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, middle(진단·컨펌). 게임 코드 hands-on 수정 없음.
- 가설 / 입력: lap533 work W38 자기판정 `PROMOTED_NO_MOVE`·`CONTROL_NA`가 원시와 일치하는지 재계산하고,
  카드 `docs/work/active/G2_STRATEGY_N192_APPROACH_PATH_LAP532.md` §3 분기표 밖 조합(`PROMOTED_NO_MOVE`×`CONTROL_NA`)의
  다음 한 가지를 정한다.
- 예상 PASS / FAIL 조건: 카드 §2 판정식을 `run_summary.json` 없이 원시(`trace.jsonl`·`t0_positions.json`·`waves.jsonl`·
  `control_wave.json`·`events.jsonl`)만으로 재계산 → 라벨 일치 여부. 분기표 적용 가능 여부는 표의 조건·전제와 원시를 대조.
- 변경 파일 / 커밋: repo source 변경 0. 문서만 — 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` §88, `docs/feedback/INBOX.md` 추기 1줄,
  STATUS 전문 보존 `docs/history/20260923_status_lap534_precompaction.md`(원문 SHA `852d5c8d510f6184913b78ec3f5340747471b0e35cb9a8f65dc85c13d6bde5d2`, 130줄).
  temp 재계산 산출물 `temp/Syw2plus_patch/g2_capacity/20260923_lap534_middle_w38_review/`:
  `recompute_w38.py` `721f58ae…d527261`, `recompute_w38.json` `4b1e350d…04768096`, `blockage_w38.py` `e1e0218a…df95a323e`,
  `blockage_w38.json` `00e652e5…c7e7c`. 커밋 0(LOOP_ALLOW_COMMITS 기본0).
- 원본 SHA / 후보 SHA / 환경: 원본 `b56986e0…c9c08a8ac` 불변(`sha256sum` 재확인). 게이트 3파일 SHA가 카드 §2 경계1 핀과 같다
  (`runtime_bridge.c` `3555848d…`, 핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`). 게임 실행 0.
- 원시 SHA(lap533 기록과 대조): `trace.jsonl` `a2ff394e…`, `t0_positions.json` `04653a7c…`, `waves.jsonl` `7e4ad317…`,
  `control_wave.json` `0247d1a9…` 전부 일치. `events.jsonl` `99e9dbcd…d040bf860`(lap533 기록에 SHA 없음, 이번에 고정).
- 실행 명령: `python3 recompute_w38.py`, `python3 blockage_w38.py`(temp 폴더 안, 원시 읽기만).

## 측정값 / 판정

1. **라벨 재계산 = 일치.** op8 요청·수락 144/144, 전원 선택 거리 ≥2(4:77·5:61·6:3·7:3) ⇒ |S|=144.
   promoted 142(98.6%)·moved 22(15.3%)·hit 0·hit 짝 0 ⇒ `PROMOTED_NO_MOVE`. 대조 `CONTROL_NA`(두 쌍 no_living_type110). uid 변경 0.
   추적 창 600~606 tick으로 9 checkpoint 전부 존재.
2. **N196(신규) 승격 즉시 철회:** 소스 `+0x290` 순서가 `1,4,1,1,…`인 것이 113/144(78%)다 — op8 직후 4가 되고 +25 tick 전에
   1(idle)로 돌아가며 위치 변화 0. 나머지는 4를 50~450 tick 유지한 뒤 3을 거쳐 1로 끝난다.
3. **N197(신규) 움직인 22기는 접근하지 않고 제자리로 돌아온다:** 전부 owner3(16)·owner7(6), 같은 슬롯이 파동마다 반복(결정적).
   변위 3~9칸이지만 소스-목표 최소 거리는 4~5에서 줄지 않았고, 마지막 checkpoint 위치가 출발점과 같다(21/22).
   S 전체 최소 도달 거리는 4(79)·5(65)이며 4 미만은 0이다. 목표 144개 중 141개는 변위 0이다.
4. **N198(신규) 유닛 밀집으로는 막힘이 설명되지 않는다(지형 미측정, 낙관 상한):** T0 위치표로 유닛 점유 칸만 막힌 것으로 두고
   8방향 BFS를 했다. 목표 인접 빈칸까지 경로가 있는 소스가 120/144이고, 그중 98기가 움직이지 않았다. owner0은 18/18 경로가 있고
   목표 인접 빈칸 7개인데도 0기가 움직였다. 소스 주변 8칸이 T0에 꽉 찬 경우는 6/144뿐이다.
   ⇒ 카드 §3의 `PROMOTED_NO_MOVE` 해석 "밀집 블록이 경로를 막는다"는 유닛 점유로는 지지되지 않는다. 지형 통행성은 원시에 없어 미판정.
5. **N195 정정(work 해석 반증):** type110은 stock 시작유닛이 아니다. `events.jsonl` 출생 이벤트에 phase B 중 AI 생산으로 태어난
   type110 3기(owner6 tick466, owner1 tick466·882)가 있다. T0 1,656슬롯의 구성은 owner당 207 = type5 100·type7 26·type2 60·type46 20·type49 1이며,
   PS3 시점 owner당 count 2(used 20)가 stock 시작분이다. W35(lap524)에서 type110이 있었던 것도 T0 뒤 AI 생산분으로 보는 것이 일관된다.
   ⇒ H7 대조는 "type110 = 시작유닛"이라는 lap525 이후 문서 전제 위에 설계됐고, 시딩으로 cap이 4,950까지 차면 AI 생산 여지가 거의 없어
   대조 가용성이 우연에 맡겨진다. `CONTROL_NA`는 하네스 결함이 아니라 대조 설계 전제의 결함이다.
6. **분기표 적용 판정:** §3 표에 `CONTROL_NA` 행이 없다(`PROBE_VOID`·`BLOCKED`도 아님). 가장 가까운 `PROMOTED_NO_MOVE ∧ CONTROL_MOVED`
   (전열 배치 W39)는 대조 조건이 불충족이고 해석 전제가 N198과 충돌한다. 카드는 "표 안의 경로만 strategy 재판정 없이 진행"이라 했으므로
   **middle은 표를 확장 적용하지 않고 strategy에 회부한다**(`ESCALATE_SOL` §88).
   참고: 움직인 22기가 모두 재배치 슬롯(>1200)이므로 "재배치 후보에서 op8 이동 자체가 불가"(`CONTROL_STILL` 가설)는 약해졌다. 단, 대조가 아니다.

## PASS / FAIL / SKIP

- 라벨 재계산 PASS(일치). 분기표 적용 = 표 밖 → strategy 회부. G2 합격 판정 대상 아님(probe 라벨).
- `make check` SKIP: source 변경 0(N22). `checks/safety.sh check`·`checks/context_limits.py`는 문서 갱신 뒤 실행(결과는 STATUS 바퀴 기록).
- 게임 실행 0. W38 실행 예산(카드 §2 경계4 최대 2회)은 1회 소진, 2회째는 하네스 결함 조건 불충족이라 쓰지 않는다.

## middle 권고(strategy가 고른다, 사용자 번복 가능)

- **권고 R1(1순위): 철회 구간 정적 추적 1회.** N196 `+0x290` 4→1(변위 0, ≤25 tick)을 되돌리는 writer만 찾는다.
  입력 = 원본 바이트의 `+0x290` writer 목록 중 op8 pending 소비(`0x40C640`) 이후 경로. 원시 `+0x384` 순서(65537 유지 92/144)도 대조한다.
  성공 = "경로 탐색 실패/목표 도달 불가/사거리·능력 거절" 중 하나를 바이트 근거로 특정. 실패 = 60분 또는 후보 2개 반증 뒤 `BLOCKED`.
  비용이 문서 1회이고 다음 work probe의 측정 필드를 정해 준다.
- **권고 R2(대조 재설계, R1 뒤):** type110 대신 AI 생산에 의존하지 않는 대조 — 예) 같은 fixture에서 시딩 type2 1기를 개방 구역의
  먼 적 유닛(G4 2026-09-16처럼 거리 수십)으로 op8. 지형 통행성 원시(셀 통행 정보) 1회 덤프를 함께 요구한다. 주소 근거는 middle이 R1에서 확인.
- **비권고:** 전열 배치 W39 즉시 실행 — N198로 전제가 지지되지 않아 게임 1회를 해석 불능 결과에 쓸 위험이 크다.

## 회귀 / 남은 위험 / 독립 검수·사용자 승인 상태

- 이 회차는 lap533 work 결과의 독립 검수다(2단). 사용자 3단 판정 아님.
- 지형 통행성 미측정이라 N198은 "유닛 점유로는 설명 안 됨"까지만 말한다. 지형이 원인일 가능성은 열려 있다.
- checkpoint 간격(25~150 tick)이 성겨 움직인 22기의 실제 궤적은 모른다(N197은 표본 위치 기준).
- streak: lap531(문서)·532(문서)·533(게임 실행)·534(문서). implementation-unchanged-streak는 이 회차로 2가 될 수 있다 — 다음 strategy는 문서만 쌓지 말고
  R1 정적 추적 결과로 바로 work probe가 이어지게 정해야 한다.
- 다음 행동: **strategy(Opus5.5): `ESCALATE_SOL` §88 — W38 표 밖 결과 처리(R1/R2 채택 여부, H7 대조 재정의, 전열 배치 보류 여부) 판정.**

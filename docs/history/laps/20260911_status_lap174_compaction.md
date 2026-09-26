# STATUS pre-compaction snapshot — lap 174

Stage A 구현 독립 검수와 A-6~A-9 조건부 반려 직후 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `25019a38502957de262dc8f2fe7ade104eedfce4c4755f11edc8ec8c44132d84`
- line count: `207`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

진단 하네스는 원본 800×600 경로의 입력·장면 전이·정상 종료와 cleanup을 통과했다. pinned
DxWrapper 후보에는 private install/uninstall, SHA 고정, byte-exact restore, opt-in `ddraw=n,b`,
module evidence가 있다.

lap154/158/160/164/166의 fresh 후보 runtime은 client/capture 1600×1200, logical DirectDraw
800×600, scale 2×2, 선변환 없는 `(184,560)` 입력, PS9→PS7→PS3를 반복 확인했다. lap166 P4에서는
close 전 30초 동안 tick `46→1013`(약 33.3/s)과 서로 다른 캡처 4장으로 **후보가 실제 인게임
프레임을 계속 합성함**을 확인했다. 따라서 2배 표시·논리 구도·기본 입력·지속 렌더 핵심 경로는
성립한다.

그러나 WM_CLOSE 뒤 tick은 1026에서 50.04초간 0 증가했고, 두 finalization 캡처는 동일 고정
프레임이었다. close 전 38.1초 동안 wrapper의 `DDERR_SURFACELOST`는 0줄이지만 close 직후 같은
타임스탬프에 `Lock2 DDERR_SURFACELOST`가 정확히 100줄 발생한다. 주 DirectDraw 스레드가 CPU의
약 96%를 쓰고 process exit/summary/DLL detach가 없어 90초 timeout으로 BLOCKED한다.

lap167 Opus/high는 P4 산출물 4/4와 source 2/2 SHA, 보호 EXE와 config 원복을 독립 확인했다.
J(close 상관)를 확정했고, 현 최선 가설은 WM_CLOSE→surface lost→주 스레드 Lock2 retry→메시지
펌프 미복귀다. 단, retry 주체가 게임인지 DxWrapper 내부인지는 아직 미분리다. 현재 harness의
내장 ddraw 대조군 P5가 가장 싼 다음 판별이다.

lap168 P5 builtin 대조군은 fresh private copy/prefix/display에서 `--dxwrapper-2x` 없이 정확히 1회
실행했다. `ddraw=b`가 Wine builtin ddraw를 로드했고 PS3 dwell 30초 tick `45→1012` 및 캡처 4/4
unique, WM_CLOSE helper PASS 뒤 process exit `0`, summary `1`, validator `PASS`, raw trace
`651`건/마지막 `seq=651`/`call_seq=19786`, detach/flush complete, prefix 잔류 0을 얻었다.
보존된 `dxwrapper*.log`의 `DDERR_SURFACELOST` 줄은 0이다. 따라서 N을 확정하여 close 후 정지를
DxWrapper native ddraw 경로에 귀속한다. 이 run의 800×600은 builtin 대조군의 정상 출력이며 G1
표시 회귀가 아니다. finalization screenshot은 process exit 때문에 생성되지 않아 고정 SHA 비교는
N/A다. 상세는 `docs/history/laps/20260911_lap168_luna_g1_p5_builtin_ddraw_control.md`.

lap169 Opus5/high middle이 P5 산출물 SHA 4/4와 `process_exit=0`/`summary_count=1`/
`winedlloverrides=ddraw=b`/loaded ddraw 단일 builtin 모듈을 독립 재계산해 **N을 CONFIRMED**했다.
같은 바퀴에 세 가지를 정정했다. (1) **close 후 tick 정지는 결함 신호가 아니다** — 정상 종료한
builtin 대조군도 finalization 표본 3건이 `tick=1022` 고정이었고 그 뒤 정상 종료했다. 결함
signature는 tick 정지가 아니라 **teardown 미완료**다. (2) lap166 후보 wrapper 로그는 마지막 줄이
`Lock2 DDERR_SURFACELOST`이고 거기서 파일이 끝난다 — **100줄은 재시도 횟수가 아니라 로그 상한**으로
읽어야 한다. (3) 현재 trace 훅은 `original_*` 반환 뒤에만 기록하고 `Lock`/`Unlock`을 후킹하지
않으므로, **"게임이 재호출"과 "wrapper 내부 스핀"이 계측상 동일하게 보인다.**

그래서 **wrapper 수리 착수는 NOT APPROVED**다. 재시도 주체가 미분리이고, 저장소에 DxWrapper
소스가 없어 고정 4키 프로필 밖에는 손댈 표면이 없다. 대신 판별 probe **P6**(우리 소유
`direct_draw_trace.c`에 Lock/Unlock entry+exit 훅 추가)를 정의해 2순위로 주차했다.

이 종료 결함은 실제 사용자 창 닫기에서도 재현되는 실제 결함이며 G1 출하 전 해소해야 하지만,
`docs/DESIGN.md` §G1 합격 조건(구도·비율·클릭 좌표·표시 정책)은 아니다. 그리고 §G1이 요구하는
원본/후보 나란히 캡처 + 실제 입력 증거는 lap148~168 동안 **한 번도 생산되지 않았다.** 원본 쪽조차
lap73에서 production fail-closed 중단으로 `drag_select`/`minimap`에 도달한 적이 없다.
그래서 다음 한 가지를 카드2로 돌린다.

lap171 Opus5/high middle이 lap170의 P5 재검증 BLOCKED를 해소했다. 산출물은 유실이 아니라 **문서
경로 오류**였다 — 실제 위치는 `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/`다.
SHA 6/6(evidence·provenance·verdict·trace·trace_raw·manifest)과 `process_exit=0`,
`summary_count=1`, `winedlloverrides=ddraw=b`, builtin ddraw 단일 모듈, 보호 EXE SHA를 독립 재대조해
**N CONFIRMED를 현물로 재확인**했다. 같은 바퀴에 카드2의 구현 근거 결손 3건을 코드로 확정했다.
(a) A-1을 lap169 문안대로 구현하면 실패한다 — production 클릭을 안 보내도 바로 다음
`_wait_state`(`:2464`)가 단계 마감시한 없이 run 전체 timeout까지 돌아 `drag_select`/`minimap`이
여전히 실행되지 않는다. BLOCKED면 효과 대기까지 건너뛰어야 한다. (b) menu는 미정의가 아니라
**비대칭**이다 — 양쪽에 이미 있고 PS9→PS7도 실제 관측되지만, 후보는 술어 없이 무조건 PASS를
기록하고 레코드 키가 달라 기계 대조가 안 된다. 공용 헬퍼가 menu까지 덮기 전에는 **4/5를 주장하지
않는다.** (c) Stage B의 "같은 시작 상태" 전제에 근거가 없다 — 장면은 seed 미노출 random game이고
재현 식별자가 same-run fingerprint뿐이라, 고정 논리 좌표가 두 run에서 같은 대상을 친다는 보장이
없다. 그래서 Stage B 판정을 Tier-1(장면 독립: menu·좌표 불변식)과 Tier-2(장면 의존: 선택·드래그·
미니맵, 장면 대조 필드 일치 시에만 비교, 아니면 UNKNOWN)로 나누고 무반응(delta=0)의 PASS를 막았다.
결정 전문은 카드2 handoff의 `lap171 middle 보강` 절(L171-0~L171-6)이다.

lap172 work가 승인된 G1 카드2 Stage A를 구현했다. baseline/후보가 공용 입력·메뉴 판정·PS3 이후
시퀀스를 공유하고 production은 클릭·효과 대기·after 캡처 없이 `BLOCKED`로 기록한다. 단계별
atomic flush와 논리좌표 `content_crop + (X,Y)`, 기존 승인 scene 필드(owner/unit/HQ/camera/
bounds/tick)를 적용했다. Fast는 PASS했지만 실제 비교 실행·제품/마일스톤 승인·Stage B 개시는 없다.
상세는 `docs/history/laps/20260911_lap172_luna_g1_card2_stageA.md`.

lap173 Opus5/high middle이 Stage A를 독립 검수해 **조건부 반려**했다. source SHA 2/2 MATCH,
허용 파일 범위 PASS, 원본·제품 EXE/DLL/baseline/golden 변경 0을 `find -newermt` 전수 목록으로
확인했다. A-1(a)(b)(c)·A-2(menu 대칭 술어·무-선변환 좌표)·A-3(단계별 즉시 flush)·A-5(승인 주소
`0xB3DE34/36`만, 새 오프셋 0)는 코드 근거로 **승인**한다. 반려 사유는 두 가지다. (B1) 후보
verdict(`runtime_env.py:3187`)가 입력 결과를 전혀 보지 않아 **production BLOCKED인데도
`overall="PASS"`가 될 수 있다** — 지금 PASS가 안 나오는 유일한 이유는 무관한 close 결함의 우연한
차폐이고, close가 고쳐지는 순간 세탁이 실재화한다. A-1의 필수 불변식 위반이다. (B2) L171-1이
"네 가지를 모두 고정"하라고 못박은 회귀 중 **(d) `required_inputs` FAIL/overall PASS 불가를
검사하는 테스트가 0건**이다 — B1이 정확히 이 공백으로 통과했다. 부수로 (B3) 시퀀스 테스트가
클릭 좌표를 기록하지 않아 `(670,490)` 전송 금지가 고정돼 있지 않고, (B5) L171-1이 요구한
`_wait_state` 예산 판단이 lap172 기록에 없다. 결정 전문은 카드2 handoff의 `lap173 middle 검수
결과` 절(A-6~A-9)이다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 자동/정기 호출하지 않고 **큰 분기·반복 교착에서만**, 대략 work/middle 10 lap당 1회
이하로 쓴다. high는 medium으로 고위험 복수 경로를 결정할 수 없을 때만 명시한다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 후보 2배 표시·논리 구도·입력·30초 지속 렌더 PASS; 실제 비교/입력 합격 증거 없음; WM_CLOSE 종료 결함 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**G1 카드2 Stage A 반려분 수리 — work tier(Luna/high 또는 Claude Sonnet5/high).**
기준은 `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`의 **`lap173 middle 검수 결과` 절**이며
그 절이 lap171·lap169 본문보다 우선한다. 허용 파일은 `tools/runtime_env.py`와
`tests/test_runtime_env.py`뿐이고 **게임을 실행하지 않는다.**

- **A-6(블로킹)** 후보 verdict(`:3187`)에 baseline `required_inputs`(`:2793~2794`)와 **같은 술어**를
  넣어 `--g1-input-sequence` on에서 5개 태그가 전부 PASS일 때만 입력 체크가 참이 되게 한다.
  하나라도 아니면 `overall`은 PASS 불가. off면 기록만 하고 판정에 개입하지 않는다.
  L171-4대로 입력 관측값 / production BLOCKED / teardown 실패를 **별도 필드**로 남긴다.
- **A-7(블로킹)** L171-1의 회귀 (d)를 테스트로 고정한다 — baseline과 후보 **양쪽** verdict가
  production BLOCKED에서 PASS 불가임을, 그리고 5개 전부 PASS인 대조 케이스에서는 체크가 참이 됨을
  함께 단언한다. verdict 조립을 순수 함수로 추출해 게임 실행 없이 검사한다.
- **A-8** 시퀀스 테스트의 `click`/`drag`가 좌표를 기록하게 하고 `(670,490)` 미전송과
  `(410,270)`/`(350,180)->(550,350)`/`(150,520)`의 무-선변환 전달을 같은 테스트에서 단언한다.
- **A-9(기록)** `_wait_state` 단계별 마감시한 도입 여부와 90초 예산 실측 계획을 work 기록에 명시한다.
- 승인돼 그대로 두는 것: 공용 헬퍼 구조, menu 대칭 술어, 무-선변환 좌표 계약, 단계별 즉시 flush,
  A-5 필드와 승인 주소. **새 오프셋 추가 금지.**

**Stage B는 A-6~A-9 수리 후 새 middle 재검수를 거쳐야 열린다**(lap18→19→20→21 선례).
P6 보류, 활성 카드 2개 유지. G1 마감이나 G2 전환은 하지 않는다.
lap170의 인계 원문과 `loop/ESCALATE_SOL` 원문은 lap171 이력에 보존했다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 EXE SHA:
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실패 run/prefix/display/build 재사용, 임의 retry, validator/summary/exit 요구 완화 금지.
- lap168 P5는 lap166 명령에서 `--dxwrapper-2x` 제거 외 단일 변수를 바꾸지 않았다.
- runtime interpreter는 `.venv/bin/python`; helper build만 `python3 -m tools.win32_close_fixture`.
- P5 대조군의 800×600 출력은 정상이며 G1 표시 회귀로 기록하지 않는다.
- dxwrapper 미사용 run의 `dxwrapper_config_restored=true`는 의미가 없으므로 game copy ini SHA를 직접 기록한다.
- trace 상세 상한 256과 Lock/Unlock 미후킹, 정상 종료 때만 aggregate flush되는 맹점이 있다.
  추가로 모든 표면 훅이 `original_*` **반환 뒤에만** 기록하므로 **반환하지 않는 호출은 trace에
  전혀 남지 않는다**(lap169). P6는 Lock entry를 위임 **전에** 기록해야 성립한다.
- wrapper close 수리는 **NOT APPROVED**(재시도 주체 미분리 + DxWrapper 소스 부재).
  고정 4키 프로필 밖의 dxwrapper 키/오프셋 변경은 별도 승인·별도 SHA pin 대상이다.
- G1 §21의 다섯 입력 중 **production은 primary field/action mapping 미승인으로 fail-closed**다.
  카드2는 최대 4/5(선택·드래그·미니맵·메뉴)까지만 덮으며 **§G1을 닫지 못한다.** 그 4/5도 menu
  레코드를 공용 헬퍼로 대칭화한 뒤에만 주장할 수 있다(lap171 L171-2).
- Stage B의 **동일 시작 상태 근거가 없다**. 장면은 seed 미노출 random game이고 재현 식별자가
  same-run fingerprint뿐이다(`runtime_env.py:2412~2416`). A-5 장면 대조 필드가 두 run에서 일치하지
  않으면 장면 의존 입력(선택·드래그·미니맵) 비교는 **UNKNOWN**이며 PASS도 발산 FAIL도 아니다.
- `_wait_state`(`:2138`)에는 **단계별 마감시한이 없다.** 효과가 오지 않는 단계는 run 전체 timeout을
  소모한다. 입력 단계를 추가/건너뛸 때 이 예산 문제를 항상 같이 판단한다. `--g1-input-sequence`는
  PS3 이후 대기를 3회 추가하므로 Stage B 전에 A-9 판단이 필요하다.
- 후보 verdict의 세탁 방지 불변식이 **아직 미충족**이다(lap173 B1/A-6). 현재 PASS가 나오지 않는
  이유는 close 결함의 우연한 차폐뿐이므로 close 수리와 A-6 중 **A-6이 먼저**다.
- `--g1-input-sequence` **off** 경로도 lap172에서 엄격해졌다 — 후보 menu 술어 실패와 scene 상세
  state 부재가 이제 예외다. lap168 P5 대조군 재실행이 이전과 다른 지점에서 멈출 수 있으며 이는
  새 회귀가 아니다(lap173 B4).
- Claude 세션은 비대화형 권한 거부로 `make check`/safety/pytest를 직접 실행하지 못한다
  (lap167·169·171·173 반복). middle 검수의 Fast 수치는 work tier 보고에 의존하며 이는 구조적
  검증 공백이다. 사용자 승인이 필요하면 INBOX로 올린다.
- G1 실제 나란히 비교/입력 증거와 G2~G4 제품 증거는 아직 없다.

## 검증 상태

- lap146~154: diagnostic 종료 PASS; config/private 적용/논리 입력 수립; 후보 1600×1200/800×600/
  2×2/input/PS3 PASS, 종료 BLOCKED. Fast 182/safety PASS.
- lap155~161: 종료 P1/P2와 middle 검수. PS3 78회·검은 동일 캡처·process 생존. Fast 187/safety.
- lap162~165: tick 계측과 실행 표면 수정; P3에서 close 후 tick 정지. Fast 190/safety/build PASS.
- lap166: P4 dwell 구현, fresh 후보 runtime 1회. close 전 tick·서로 다른 캡처 4장; close 후 정지.
  `make check` 192 passed, Ruff/mypy/safety, build/cleanup/config 원복 PASS.
- lap167: Opus 독립 검수. source 2/2·산출물 4/4 SHA, 보호 EXE/config SHA PASS; J 확정.
  make/safety 재실행은 권한상 SKIP, 코드 변경 없음. P5 승인.
- lap168: P5 builtin 대조군 1회. `make check` 192 passed, `SAFETY_PASS`. N 판정.
- lap169: Opus 독립 검수. P5 산출물 SHA 4/4·evidence 필드 일치로 **N CONFIRMED**; tick 정지·
  100줄·훅 시점 3건 정정; wrapper 수리 NOT APPROVED, P6 정의, 카드2 Stage A 승인.
  `make check`/safety는 비대화형 권한 거부로 **SKIP**(코드 변경 0이며 `runtime_env.py` SHA가
  lap168과 동일하므로 lap168의 192 passed가 현재 트리의 마지막 유효 Fast 근거다).
- lap171: Opus5/high middle 독립 검수. P5 산출물 SHA **6/6 MATCH**(경로는
  `<run>/output/g1_presentation_trace/`)로 lap170 BLOCKED 해소, N 재확인. 카드2 결손 3건 확정·결정.
  `make check`/safety는 비대화형 권한 거부로 **SKIP**(2회 시도, 재시도 없음). 코드 변경 0이며
  `runtime_env.py` SHA가 lap168과 동일하므로 lap168의 192 passed가 여전히 마지막 유효 Fast 근거다.
- lap173: Opus5/high middle 독립 검수. source SHA **2/2 MATCH**, 허용 파일 범위·원본 보호 PASS,
  A-1(a)(b)(c)·A-2·A-3·A-5 코드 승인, **A-1(d) 후보 절반 FAIL + 회귀 (d) 부재로 Stage A 조건부
  반려**. 코드 변경 0, 게임 run 0. `make check`/safety/pytest는 비대화형 권한 거부로 **SKIP**
  (3회 형태 시도, 재시도 없음) — 현재 트리의 `196 passed`는 lap172 자기 보고이며 독립 재현 없음.
- lap172: Stage A work 구현. `make check` **196 passed**/Ruff/compileall/mypy/CONTEXT_PASS/
  `SAFETY_PASS`; P5 현물 SHA 6/6 재대조. 게임 run 0, 원본·제품 EXE/DLL/assets/baseline/golden
  변경 0, Stage B·P6·마일스톤 승인 0. source SHA는 lap 이력에 기록한다.
- pre-compaction snapshot SHA `810344f38fa5c4b59f1f108ae56a86528821c2a30a0f0642760404be2adcd587`;
  원문은 `docs/history/laps/20260911_status_lap168_compaction.md`에 보존했다.

## 바퀴 기록

- lap2~165 및 이전 STATUS 원문: `docs/history/laps/`.
- latest snapshot: `docs/history/laps/20260911_status_lap168_compaction.md`.
- lap166 work: `docs/history/laps/20260911_lap166_luna_g1_ps3_dwell_close_causality.md`.
- lap167 middle: `docs/history/laps/20260911_lap167_middle_g1_close_causality_confirmation.md`.
- lap168 work: `docs/history/laps/20260911_lap168_luna_g1_p5_builtin_ddraw_control.md`.
- lap169 middle: `docs/history/laps/20260911_lap169_middle_g1_p5_confirmation_and_scope.md`.
- lap171 middle: `docs/history/laps/20260911_lap171_middle_card2_stageA_reconfirm.md`.
- lap172 work: `docs/history/laps/20260911_lap172_luna_g1_card2_stageA.md`.
- lap173 middle: `docs/history/laps/20260911_lap173_middle_card2_stageA_verification.md`.
- current escalation: **없음.** lap170 `loop/ESCALATE_SOL`은 lap171 middle이 3건 모두 해소하고
  파일을 제거했다. 원문은 lap171 이력 말미에 보존했다.
- current handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` (1순위, Stage A 조건부 반려;
  **`lap173 middle 검수 결과` 절(A-6~A-9)이 lap171·lap169 본문보다 우선**).
- parked handoff: `docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md` (2순위, P6 착수 미승인).
- model routing: `docs/history/20260911_model_routing_update.md`.

- lap170 Astra: source/handoff SHA 3/3 일치; P5 evidence 지정 경로 FileNotFoundError로 재검증 BLOCKED, 재시도 없음. Fast/runtime SKIP; 문서만 변경, 제품·계획 PASS 없음. 상세: `docs/history/laps/20260911_lap170_astra_card2_verification_boundary.md`.

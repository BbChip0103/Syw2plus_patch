# INBOX 압축 보존 — lap589 (op9 핀 승인·S1 (라) 이동 후 공격 계보)

- 압축 주체: lap589 strategy(Claude Code `claude-opus-5-5`), 2026-09-25 KST.
- 원 INBOX 전문 SHA256 `1528f05d2ab0138b576af00cf33e82a527ace30d94fc042ab9aa985f2dabb050`, 345줄. 아래 발췌는 그 파일 63~83행(21줄) 원문 그대로이며 발췌 SHA256 `981e47f67a335d5ee567884fe7a7ae86a4483709b488ef303872064b123994aa`.
- 종결 사유: op9 승인은 lap550에서 반영 완료, S1 (라)→W42/W43/W43R→Q10 (마)→H29′ `BLOCKED(harness_budget)` 계보는 lap560에서 사용자 지정 fallback (다)로 S1 중단 확정(`ESCALATE_SOL` §114). 삭제·재해석 없음.
- 원 INBOX 전문은 아래 '전문' 절에 함께 보존한다.

## 발췌 (63~83행)

```text
- [ ] 2026-09-24 14:31 KST: 사용자 **op9 핀 테스트 갱신 승인** (lap549 `BLOCKED(gate)` §103 응답). `runtime_bridge.c` 가드
  `op > 8`→`op > 9`와 함께 `test_operation_gate_widened_from_7_to_8`의 기대 리터럴만 `op > 9`로 갱신한다(다른 핀·허용목록 불변).
  middle/strategy 재회부 없이 다음 work가 W42 카드 §2를 이어서 실행(op9 구현→게임 1회 foreground→`make check`).
- [ ] 2026-09-24 03:15 KST: 사용자 **S1 교전 = (라) 이동 후 공격** 선택(lap547 §4 STOP 응답). 원본 이동 명령으로 먼저 적
  인접까지 보낸 뒤 op8 공격을 거는 2단 입력으로 S1 교전을 재시도한다. AI/게임 코드 변경 없음((가)·(나)·(다) 미선택).
  strategy가 경로·합격 기준(A1~A8' 불변)·실행 예산을 판정한다. Q9·Q7-B·"8인" 정의는 미결 그대로.
  **lap548(strategy, Opus5.5) 처리 — 통지(질문 아님, 번복 가능):** W42 1회로 진행한다. 원본 "이동" 명령 함수(`0x4AEDE0`, 게임 안 44곳에서 씀)로 전투 유닛을 적 옆 빈칸까지 최소 7칸 걷게 하고, 도착하면 공격 명령을 건다.
  정적으로 보면 이동 명령에는 공격을 멈추게 한 "두 틱 막히면 포기" 규칙이 없다(N204, 실행으로는 미확인). 트인 들판 2짝과 기존 띠 배치 2짝을 한 번에 본다. 합격 기준은 그대로다. 첫 명령을 낸 뒤에는 재시도하지 않는다.
  교전이 되면 24k 교전 시험으로 넘어가고, 안 되면 남은 (가)·(나)·(다)를 여쭙는다. 문서 `docs/work/active/G2_STRATEGY_W42_MOVE_THEN_ATTACK_LAP548.md`, `ESCALATE_SOL` §102. 다음은 work의 구현과 게임 1회다.
  **lap549(work, Sonnet5) 처리:** 카드대로 가드를 `op > 8`→`op > 9`로 편집했더니 **기존 op8 계약 핀 테스트가 깨졌다**(카드가 미리 적어 둔 정지 조건). 원복해 소스는 원본과 동일하게 남겼고, op9 구현·게임 실행은 하지 않았다(가드가 막혀 있어 op9 요청 자체가 브리지에 닿지 못한다). 다음은 middle 독립검수 → strategy가 "핀 테스트를 op9에 맞게 갱신할지" 또는 "op9를 다른 방식으로 열지" 판정한다. `ESCALATE_SOL` §103.
  **lap550(work, Sonnet5) 처리:** 이 승인대로 가드를 `op > 9`로 넓히고 해당 테스트 리터럴만 갱신 → op9(원본 이동 발행자 `0x4AEDE0`) 구현 → `w42_run.py` 작성·실행. 게임 1회 완주(96초), **자기 라벨 `ENGAGED_2STAGE`** — 전열 2짝(0,1)(4,5) 모두 도착 후 `hit_attr`≥1·중앙 walk≥7·A5 위반 0(첫 A2 교전 증거). 띠 2짝(2,3)(6,7)은 도착 0(`band_engaged=0`). `make check` 835 passed·`SAFETY_PASS`, 원본 불변, 커밋 0. 다음은 middle 독립검수 → 일치 시 W43(S1 24k soak) 발행. `ESCALATE_SOL` §104, `docs/history/laps/20260924_lap550_work_w42_move_then_attack_engaged.md`.
  **lap551(middle, Codex) 처리:** raw assignment/trace/events/samples/T0 독립 재계산으로 `ENGAGED_2STAGE` 일치·ACCEPT. 현재 source `make check` 835 passed·`SAFETY_PASS`를 새로 확인하고 W43 24k 카드를 발행했다. report-only `move_stop_early`는 read 시점 차이로 raw trace 완전 재현 불가라 W43 원시 기록을 강화했다. 다음은 work W43 게임 1회다(`ESCALATE_SOL` §105).
  **lap552(work)·lap553(middle)·lap554(strategy) 처리 — 통지(질문 아님, 번복 가능):** W43은 24k까지 돌았지만 시험 도구가 카드대로 배치·방향 교대를 하지 않아 무효가 됐다(게임 결함 증거는 없다). 도구를 고쳐 **1회만 다시 실행**한다. 합격 기준은 그대로이고, 재생산 기준은 원래 정의(lap532)로 되돌렸다.
  새 위험 N205: 게임이 새 유닛을 빈 슬롯의 한쪽 끝부터 채우는 것으로 보인다. 그렇다면 "죽은 자리 재사용"이 24k 안에 안 나올 수 있다. 기준은 낮추지 않았다. 네 짝 배치가 불가능하거나 교전이 안 되면 이 경로를 닫고 (가)(나)(다)를 다시 여쭙는다. `ESCALATE_SOL` §108.
  **lap555(work)·lap557(middle)·lap558(strategy, Opus5.5) 처리 — 질문 Q10(사용자 선택 필요, STOP 대기):** 도구를 고친 재실행(W43R)도 **교전 전 배치 단계에서 무효**가 됐다.
  원인은 게임이 아니라 우리 시험 도구의 배치 예측이다. 건물형 유닛(type46)은 3×3칸을 차지하는데 도구는 1칸으로 셌다. 배치 순서도 실제(진영마다 전투 유닛→건물)와 달랐다. 그래서 건물들이 두 줄 사이 빈 띠로 밀려 들어갔다.
  lap554에서 미리 정한 규칙대로 **모델 판단의 재시도는 여기서 닫는다.** 이 경로에서 "마지막 1회"를 이미 네 번 늘렸기 때문이다. 게임이 안 된다는 증거는 없고 네 짝 배치가 가능한지는 아직 모른다.
  **다음 중 하나를 골라 주세요(모델은 고르지 않음):** (가) G2 한정 최소 AI 변경 예외 · (나) "8인"을 사람 슬롯으로 fixture 재구성(가능성 미조사) · (다) S1 교전 트랙 중단(교전 없는 "안정 동작"으로 해석 약화) ·
  **(마) 신규·strategy 권고:** 시험 도구만 고쳐 정확히 1회 더 실행한다. 건물 3×3 반영, 실제 순서 재현, 건물 위치도 함께 탐색, 진영마다 배치 직후 확인해 어긋나면 교전 전에 멈춘다. 비용은 work 1회(게임 15~25분)와 middle 1회다.
  주의: 건물 위치를 옮겨도 지형상 네 짝이 안 들어갈 수 있다(N206). 그때는 그것이 실측 결론이다. **"(마), 실패 시 (다)"처럼 대체안까지 함께 주시면** (마)가 실패해도 다시 묻지 않고 바로 넘어간다.
  문서 `docs/work/active/G2_STRATEGY_S1_BUDGET_CLOSE_LAP558.md`, `ESCALATE_SOL` §112.
```

## 전문 (압축 직전 INBOX)

```text
# INBOX — 사용자 지시 원문과 처리 상태

체크는 문서 반영 여부이며 제품 구현 완료가 아니다. 체크된 상시 요구도 계속 유효하다.

## 처리 대기

- [ ] 2026-09-25 lap588 middle: lap587 PNG 3장·manifest·receipt·0B samples/events·원본/cleanup을 summary와 분리해 재계산하고 직접 확인해 **raw 무결성 `ACCEPT`, W49R 화면 `REJECT / BLOCKED(capture_contract)`**. V1 `0.009159091/0.009159091/0.108306818`, camera `[94,6]` 불변이며 H2 상승은 설정 메뉴 픽셀이다. 최종 fingerprint `2ee4c561…cd6c1` Fast 835 passed/500.58s·`SAFETY_PASS`; fresh 실행·제품 변경0, G2 PASS·제품 렌더 결함·사용자 승인 아님. 마일스톤 경계라 strategy가 추가 실행 없이 S5′ 제출문을 검증하도록 `ESCALATE_SOL` §138로 승격. 상세 `docs/history/laps/20260925_lap588_middle_w49r_g0_independent_review.md`.
- [ ] 2026-09-25 lap586 middle: lap585 W49R runner SHA/parent/원본, 모든 receipt snapshot의 JSON 비순환성, lap584 두 PNG·manifest(V1 `0.009159`, camera `[94,6]`, H1 key0), V1/V2 회귀와 owned cleanup을 독립 검수해 **`ACCEPT / W49R_RUNNER_READY`**. 현재 fingerprint `9a573415…b788dd`에서 Fast 835 passed/497.45s·`SAFETY_PASS`; 게임 fresh는 0회이며 G2/화면 PASS·사용자 승인 아님. 다음 work가 같은 계약으로 foreground 정확히 1회 실행하고, 결과와 무관하게 다음 middle이 raw를 재계산한다. `docs/history/laps/20260925_lap586_middle_w49r_runner_independent_review.md`, `ESCALATE_SOL` §136.
- [ ] 2026-09-25 lap583 strategy(Opus5.5) — **통지(질문 아님, 번복 가능):** 지난 화면 캡처(W49)는 상단 자원·전비 표시만 보이고 맵은 검게 나왔습니다. 같은 환경에서 9월 20일에 찍은 캡처에는 지형·건물·유닛이 보이므로 캡처 도구 문제는 아닙니다. 시험 도구가 화면(카메라)을 우리 진영 쪽으로 옮기지 않은 것이 원인으로 보입니다.
  그래서 **카메라를 우리 유닛 쪽으로 옮기는 입력을 넣고 정확히 한 번만** 다시 찍습니다(W49R). 맵이 보이는지는 미리 정한 수치로 판정하고, 이번이 화면 시험의 마지막입니다. 미니맵은 이 환경에서 원래 늘 검게 나와 합격 조건에서 뺐습니다. 그다음 마일스톤 제출문을 올립니다. `docs/work/active/G2_STRATEGY_W49R_SCREEN_CAMERA_LAP583.md`, `ESCALATE_SOL` §133.
- [ ] 2026-09-25 lap582 middle: W49 raw는 269표본/tick10027/8 AI/used4950~5000/장부·VM 정합성을 독립 재계산해 `ACCEPT / W49_RAW_10K_STABLE`. 그러나 5 PNG는 비검정 픽셀이 좌상단800×600 안에만 있고 월드·유닛이 보이지 않으며, runner가 미니맵 입력 없이 연속 저장한 +10000/minimap 파일도 byte-identical이라 **화면 축 `REJECT / BLOCKED(capture_contract)`**. N211은 역어셈블로 GetCaps 외 14콜백의 `E_NOTIMPL`을 확인해 ACCEPT. Fast 835 passed/512.44s·`SAFETY_PASS`. 필수 화면 검증 실패+S5′ 마일스톤 경계라 `ESCALATE_SOL` §132로 strategy 판정 대기; G2 PASS·사용자 승인 아님.
- [ ] 2026-09-25 lap581 work: W49 결합 후보 fresh foreground 1회 완주(`tick=10027`). 시딩 전/T0/+2000/+10000/미니맵 PNG 5장(1600x1200)과 owner raw를 보존했고, raw269행에서 tick 역행0·live/count 불일치0·used4950~5000·VM 고정을 확인했다. `make check` 835 passed/495.93s·`SAFETY_PASS`; G2 PASS·사용자 승인 아님. 다음 middle이 raw/캡처 SHA와 N211을 독립 검수한다. 상세 `docs/history/laps/20260925_lap581_work_w49_screen_evidence.md`.
- [ ] 2026-09-25 lap580 strategy(Opus5.5) — **통지(질문 아님, 번복 가능):** 멀티 연결 시험(W48)은 다시 돌리지 않습니다. 이 컴퓨터에 깔린 Wine 9.0의 DirectPlay TCP/IP 부품은
  세션 찾기·만들기·보내기 기능이 비어 있는(stub) 상태로 보입니다(N211, 파일 문자열로 확인, 다음 검수에서 재확인). 그래서 IP를 제대로 넣어 다시 돌려도 새로 알 게 없습니다.
  W48은 "시험 방식 결함으로 판정 불가"로 남기고, 다음은 사전 허가된 화면 캡처(W49)를 한 번 찍습니다. 멀티를 실제로 확인하려면 새 Wine·네이티브 DirectPlay·Windows 기기 중 하나가
  필요하거나 "환경 미검증"으로 제출해야 하는데, 새 프로그램 설치가 걸려 있어 제가 고르지 않고 제출문에서 여쭙겠습니다. `docs/work/active/G2_STRATEGY_W48_DISPOSITION_LAP580.md`, `ESCALATE_SOL` §131.

- [ ] 2026-09-25 lap579 middle: W48 raw를 독립 검수해 PS3 0/2·tick 0/0과 원본/격리/캡처는 확인했지만,
  runner에 `127.0.0.1` 입력이 없고 client는 빈 목록의 `찾아보기`만 사용했으며 실행 당시 pre/post
  `ss` 출력도 보존되지 않아 lap578의 `BLOCKED(env)` 원인 귀속을 **`REJECT / BLOCKED(harness_contract)`**로
  판정했다. 게임쌍 2회 예산을 middle이 재개하지 않고 strategy가 corrected C0 1회 허용 또는
  `UNKNOWN(harness_contract)` 제출을 결정하도록 `ESCALATE_SOL` §130에 승격했다. G2 PASS·사용자 승인 아님.

- [ ] 2026-09-25 lap578 work: W48 S4-0 원본 C0를 정적 조사와 허용된 쌍 실행 2회로 확인했다. 원본은
  `DPLAYX.dll`/`WSOCK32.dll`과 멀티 경로 문자열을 갖지만, 두 fresh prefix/display에서 PS13 세션
  목록 이후 host/client가 연결되지 않아 PS3 0/2·tick 0/0으로 `BLOCKED(env)` 판정했다. 결합 후보
  C1은 C0 PASS 조건 때문에 실행하지 않았다. raw·캡처·다음 middle 검수는
  `docs/history/laps/20260925_lap578_work_g2_s4_transport_c0_blocked.md`와 `ESCALATE_SOL` §129에 남겼다.

- [ ] 2026-09-24 23:05 KST: 사용자 Q11 응답. **Q11-2 = (나)** 저장/로드 판별형 1회 허가(N208 수정식: 저장 뒤 ≥300 tick 진행 후 로드,
  `load.tick_after ≤ save.tick_after < load.tick_before`, 로드 직전 풀≠저장 직전 풀, 로드 직후 풀·장부=저장 직전).
  **Q11-1은 사용자가 "나한테 묻지 말고 너가 알아서 좀 해"로 위임** → 운영자 결정 **(A) 부분 증거 인정**, §4 남은 조건 1~7 기록 후 다음 축 진행.
  **상시 지시(신규):** 절차·증거 해석·재시도 예산 같은 판단은 사용자에게 묻지 말고 strategy가 권고안으로 결정·기록·진행한다.
  사용자 질문은 비가역·범위 밖(원본/참고 쓰기, 커밋/푸시/유료, 제품 목표 자체 변경)에만 한정한다.
  **lap568~571 처리:** W45는 자연 변화가 없어 판별 전제가 실패했고(lap569 middle ACCEPT), W45R은 저장 307 tick 뒤 type7 1기 UID `526601`을 주입했다가 load로 소멸·저장 전 pool/8 owner 장부 복원을 기록했다. lap571 middle이 summary 제외 raw를 2회 재계산해 B1~B6 `ACCEPT / STABLE_MIXED_24K`; Q11-2 기술 검수는 충족했다. G2 전체 PASS는 아니며 혼합144k·S3(Q9)·S4 멀티/“8인” 정의·중단된 교전/사망/재생산·사용자 3단 승인은 남는다. 다음은 strategy 경계 판정(`ESCALATE_SOL` §124).
  **lap572 strategy(Opus5.5) 처리 — 통지(질문 아님, 번복 가능):** 건물 섞은 저장/로드 확인은 이제 통과로 봅니다(raw로 다시 확인함). 다음은 **이미 승인하신 32-bit 전비 장부(F4)를 지금 후보에 합친 버전**으로 같은 24k+저장/로드 시험을 한 번 돌리는 것입니다(W46). 최종 후보가 바뀌기 전에 144k(약 73분)를 먼저 쓰지 않으려고 순서를 이렇게 정했습니다. 두 패치가 같은 바이트를 건드리지 않는 것은 읽기 전용으로 확인했습니다. 통과하면 같은 후보로 혼합 144k를 한 번 돌립니다.
  Q9는 상시 지시에 따라 제가 정했습니다. "패치본(2601·2606) 실행 제외"는 커뮤니티 배포본 EXE로 읽었고, 우리 F4 후보 실행은 여기에 들지 않는다고 봤습니다. 다르게 뜻하셨으면 말씀만 주세요. "8인"이 사람인지 AI인지는 제품 목표 정의라 계속 여쭤 둔 상태로 둡니다. 문서 `docs/work/active/G2_STRATEGY_S3_F4_INTEGRATED_W46_LAP572.md`, `ESCALATE_SOL` §125.
  **lap573 work·lap574 middle 처리:** 결합 후보 `dfdc91ad…3883` W46은 fresh 혼합24k+판별형 저장/로드를 완주했고, lap574가 summary 없이 raw·보존 실행 사본을 2회 재계산해 B1~B6/F1~F3 전부 `ACCEPT / STABLE_MIXED_24K_F4`로 확인했다. 다음은 사전 허가된 같은 후보 혼합144k W47 정확히 1회다. G2 PASS·사용자 3단 승인은 아니며 S4/“8인” 정의와 제외된 교전·사망·재생산 등은 남는다. `ESCALATE_SOL` §126.
  **lap575 work·lap576 middle 처리:** 같은 결합 후보 W47은 혼합144k를 1회 완주했고, lap576이 summary 제외 raw·보존 실행 EXE·패치 old/new/원복을 두 번 재계산해 F1/B1/B2/B3/B5/B6/F2 전부 `ACCEPT / STABLE_MIXED_144K_F4`로 확인했다. G2 PASS나 사용자 승인으로 승격하지 않았고, S4/“8인” 정의·Q10 `(다)`로 제외된 교전/사망/재생산·N141·화면 증거는 남는다. 다음은 strategy 경계 판정(`ESCALATE_SOL` §127).
  **lap577 strategy(Opus5.5) 처리 — 통지(질문 아님, 번복 가능):** 144k 결과는 제가 다시 계산해도 같았습니다. 이제 건물 섞은 저장/로드, 혼합 144k, 32-bit 전비 장부 통합은 모두 통과한 상태입니다.
  다음은 **멀티 연결이 되는지부터** 봅니다(W48). 같은 컴퓨터에서 게임 두 개를 띄워 원본끼리 먼저 DirectPlay 세션이 이어지는지 확인하고, 되면 우리 후보끼리도 확인합니다. 60분 안에 되는지·안 되는지·환경 때문에 막혔는지를 정합니다. 외부 네트워크로는 내보내지 않고 127.0.0.1만 씁니다. 추가 프로그램은 설치하지 않습니다.
  그다음 사람이 볼 수 있는 화면 캡처를 한 번 만들고(W49), 둘을 묶어 마일스톤 제출문을 다시 올리겠습니다. 장부가 멈춰 보이는 현상(N141)은 교전을 뺀 결과로 보고 따로 시험하지 않습니다. "8인"이 사람인지 AI인지는 여전히 여쭤 둔 상태입니다. 문서 `docs/work/active/G2_STRATEGY_S4_TRANSPORT_W48_LAP577.md`, `ESCALATE_SOL` §128.
- [ ] 2026-09-24 21:57 KST **lap567 strategy(Opus5.5) — 질문 Q11(사용자 선택 필요, STOP 대기).** 건물을 섞은 재실행(W44R)은 24k 동안 깨지지 않았다(B1·B2·B3·B5·B6 통과).
  하지만 저장/로드 확인(B4)은 통과하지 못했다. 원인은 게임이 아니다. lap564에서 제가 정한 확인식이 애초에 참이 될 수 없는 식이었고(N208), 시험 도구도 그 식을 빠뜨렸다. 게다가 저장과 로드 사이가 1 tick뿐이라 "로드가 실제로 상태를 되돌렸는지"를 가려낼 힘이 약하다.
  미리 정한 규칙대로 다시 돌리지 않고 **3단 제출문**을 올린다: `docs/reports/20260924_G2_S5_MILESTONE_SUBMISSION_LAP567.md`. G2 합격 주장은 아니다.
  **Q11-1** (A) 부분 증거로 인정하고 남은 조건(교전 제외·혼합 저장/로드·혼합 144k·Q9·"8인" 정의·N141 정지 성격·화면 캡처 없음)을 기록 / (B) 인정 안 함, 필요한 축 지정.
  **Q11-2 (혼합 저장/로드)** (가) 미검증으로 닫음 · **(나) strategy 권고:** 저장 뒤 300 tick 이상 진행 후 로드하는 판별형 확인 1회(게임 15~25분, 실패 시 재실행 없음) · (다) 1 tick 역행을 증거로 인정(모델 비권고).
  "(A)+(나)"처럼 함께 주시면 바로 진행한다. 기록 `docs/history/laps/20260924_lap567_strategy_s5_submission.md`, `ESCALATE_SOL` §121.
- [ ] 2026-09-24 19:02 KST: 사용자 **Q10 = (마), 실패 시 (다)** (lap558 STOP 응답). 시험 도구(H29 planner가 type46 anchor도 live mask로
  함께 선택)만 고쳐 fresh 게임 **정확히 1회**. 게임·AI·기준 불변. middle `ACCEPT`+교전 성립이 아니면 재질문 없이 **(다) S1 교전 트랙 중단**.
  다음 work가 `G2_STRATEGY_S1_BUDGET_CLOSE_LAP558.md` §5 계약대로 계획 회차 없이 바로 착수.
  **lap559 work 처리:** H29′ owner순 `type2→type46`, type별 full footprint, type46 anchor 탐색, preseed mask raw 저장과 T0 type46 exact-match gate를 반영한 파생 도구로 fresh foreground 1회를 시작했다. PS3/cap `[5000]*8`/H21a 8/8/type5·7 시딩까지 PASS했지만 planner가 약 20분 동안 `layout_plan.json`을 만들지 못해 `KeyboardInterrupt`로 `RUN_ERROR/BLOCKED`가 됐다. 원본/후보/source는 불변, op9/op8/24k 0회. 사용자 대체안 **(다)를 적용해 S1 교전 트랙을 중단**하고 `ESCALATE_SOL` §113에 승격한다. raw/history는 `20260924_lap559_work_w43r2_h29_planner_timeout.md`에 보존했다.
  **lap560 middle 처리:** 저장 mask와 H29′를 게임 없이 독립 재생해 후보1,116개·첫 leaf type46 anchor 시도6,206회 뒤 owner7 type2 drift 기각을 확인했다. DFS가 gap 행을 상태에 예약하지 않고 leaf마다 owner별 최대9,900 anchor full replay를 수행하므로 lap559 `BLOCKED(harness_budget)`를 ACCEPT한다. 제품 결함·`no_four_pair_layout`은 여전히 UNKNOWN이고, Q10의 필요조건인 “middle ACCEPT+교전 성립”은 아니므로 지정 fallback **(다) S1 중단**을 확정해 `ESCALATE_SOL` §114로 넘겼다. 현재-source `make check` 835 passed; 새 게임·수리·24k/144k 없음.
  **lap561 strategy(Opus5.5) 처리 — 통지(질문 아님, 번복 가능):** 교전 시험(S1)은 말씀대로 닫았다. 남은 G2 증거를 살펴보니 같은 후보에서 24k·144k·저장/로드는 이미 있다.
  다만 모두 건물 없는 구성(전투 유닛 99%)이었다. 그래서 **건물까지 섞은 8인 cap5000 상태를 교전 명령 없이 24k 돌리고 중간에 저장/로드 1회**만 하는 시험(W44)을 한 번 실행한다. 재시도는 없다.
  통과하든 실패하든 그다음은 사용자 마일스톤 제출(3단)이다. 제출문에는 교전·사망·재생산 제외((다)), Q9, "8인" 정의, 혼합 구성 144k 미실행을 미충족으로 적는다. 문서 `docs/work/active/G2_STRATEGY_S1_CLOSED_W44_STABLE_MIXED_LAP561.md`, `ESCALATE_SOL` §115.
  **lap562(work)·lap563(middle)·lap564(strategy, Opus5.5) 처리 — 통지(질문 아님, 번복 가능):** W44는 시작 직후 멈췄다. 시험 도구가 유닛 비용표 주소를 잘못 읽어, 실제로는 맞게 깔린 건물 혼합 구성을 "구성 불합격"으로 오판했기 때문이다. 게임 결함 증거는 없고, 24k 동작과 저장/로드는 한 번도 돌지 않았다.
  lap561에서는 "재시도 없음"이라고 했다. 하지만 이대로 제출하면 확인하려던 건물 혼합 구성 동작이 빈 채로 남는다. 그래서 **주소만 고친 도구로 정확히 1회만** 다시 실행한다. 기준은 그대로이고, 이것이 모델 판단으로 도는 마지막 실행이다.
  결과가 통과가 아니면 원인이 도구여도 다시 돌리지 않고 실패로 제출한 뒤 멈춘다. 문서 `docs/work/active/G2_STRATEGY_W44R_TYPE_TABLE_FRESH_ONCE_LAP564.md`, `ESCALATE_SOL` §118.
- [ ] 2026-09-24 14:34 KST: 사용자 "미들이랑 워크를 코덱스로" → **middle=`codex/gpt-5.6-sol`, work=`codex/gpt-5.6-luna`**(effort high),
  strategy는 `claude-opus-5-5` 유지. `loop/env.local.sh` `LOOP_MIDDLE_PROVIDER`·`LOOP_WORKER`=codex, 두 모델 CLI 응답 확인.
  lap550(claude-sonnet-5) 종료 뒤 다음 lap부터 적용. 다른 세대 자동 폴백 없음.
- [ ] 2026-09-24 14:31 KST: 사용자 **op9 핀 테스트 갱신 승인** (lap549 `BLOCKED(gate)` §103 응답). `runtime_bridge.c` 가드
  `op > 8`→`op > 9`와 함께 `test_operation_gate_widened_from_7_to_8`의 기대 리터럴만 `op > 9`로 갱신한다(다른 핀·허용목록 불변).
  middle/strategy 재회부 없이 다음 work가 W42 카드 §2를 이어서 실행(op9 구현→게임 1회 foreground→`make check`).
- [ ] 2026-09-24 03:15 KST: 사용자 **S1 교전 = (라) 이동 후 공격** 선택(lap547 §4 STOP 응답). 원본 이동 명령으로 먼저 적
  인접까지 보낸 뒤 op8 공격을 거는 2단 입력으로 S1 교전을 재시도한다. AI/게임 코드 변경 없음((가)·(나)·(다) 미선택).
  strategy가 경로·합격 기준(A1~A8' 불변)·실행 예산을 판정한다. Q9·Q7-B·"8인" 정의는 미결 그대로.
  **lap548(strategy, Opus5.5) 처리 — 통지(질문 아님, 번복 가능):** W42 1회로 진행한다. 원본 "이동" 명령 함수(`0x4AEDE0`, 게임 안 44곳에서 씀)로 전투 유닛을 적 옆 빈칸까지 최소 7칸 걷게 하고, 도착하면 공격 명령을 건다.
  정적으로 보면 이동 명령에는 공격을 멈추게 한 "두 틱 막히면 포기" 규칙이 없다(N204, 실행으로는 미확인). 트인 들판 2짝과 기존 띠 배치 2짝을 한 번에 본다. 합격 기준은 그대로다. 첫 명령을 낸 뒤에는 재시도하지 않는다.
  교전이 되면 24k 교전 시험으로 넘어가고, 안 되면 남은 (가)·(나)·(다)를 여쭙는다. 문서 `docs/work/active/G2_STRATEGY_W42_MOVE_THEN_ATTACK_LAP548.md`, `ESCALATE_SOL` §102. 다음은 work의 구현과 게임 1회다.
  **lap549(work, Sonnet5) 처리:** 카드대로 가드를 `op > 8`→`op > 9`로 편집했더니 **기존 op8 계약 핀 테스트가 깨졌다**(카드가 미리 적어 둔 정지 조건). 원복해 소스는 원본과 동일하게 남겼고, op9 구현·게임 실행은 하지 않았다(가드가 막혀 있어 op9 요청 자체가 브리지에 닿지 못한다). 다음은 middle 독립검수 → strategy가 "핀 테스트를 op9에 맞게 갱신할지" 또는 "op9를 다른 방식으로 열지" 판정한다. `ESCALATE_SOL` §103.
  **lap550(work, Sonnet5) 처리:** 이 승인대로 가드를 `op > 9`로 넓히고 해당 테스트 리터럴만 갱신 → op9(원본 이동 발행자 `0x4AEDE0`) 구현 → `w42_run.py` 작성·실행. 게임 1회 완주(96초), **자기 라벨 `ENGAGED_2STAGE`** — 전열 2짝(0,1)(4,5) 모두 도착 후 `hit_attr`≥1·중앙 walk≥7·A5 위반 0(첫 A2 교전 증거). 띠 2짝(2,3)(6,7)은 도착 0(`band_engaged=0`). `make check` 835 passed·`SAFETY_PASS`, 원본 불변, 커밋 0. 다음은 middle 독립검수 → 일치 시 W43(S1 24k soak) 발행. `ESCALATE_SOL` §104, `docs/history/laps/20260924_lap550_work_w42_move_then_attack_engaged.md`.
  **lap551(middle, Codex) 처리:** raw assignment/trace/events/samples/T0 독립 재계산으로 `ENGAGED_2STAGE` 일치·ACCEPT. 현재 source `make check` 835 passed·`SAFETY_PASS`를 새로 확인하고 W43 24k 카드를 발행했다. report-only `move_stop_early`는 read 시점 차이로 raw trace 완전 재현 불가라 W43 원시 기록을 강화했다. 다음은 work W43 게임 1회다(`ESCALATE_SOL` §105).
  **lap552(work)·lap553(middle)·lap554(strategy) 처리 — 통지(질문 아님, 번복 가능):** W43은 24k까지 돌았지만 시험 도구가 카드대로 배치·방향 교대를 하지 않아 무효가 됐다(게임 결함 증거는 없다). 도구를 고쳐 **1회만 다시 실행**한다. 합격 기준은 그대로이고, 재생산 기준은 원래 정의(lap532)로 되돌렸다.
  새 위험 N205: 게임이 새 유닛을 빈 슬롯의 한쪽 끝부터 채우는 것으로 보인다. 그렇다면 "죽은 자리 재사용"이 24k 안에 안 나올 수 있다. 기준은 낮추지 않았다. 네 짝 배치가 불가능하거나 교전이 안 되면 이 경로를 닫고 (가)(나)(다)를 다시 여쭙는다. `ESCALATE_SOL` §108.
  **lap555(work)·lap557(middle)·lap558(strategy, Opus5.5) 처리 — 질문 Q10(사용자 선택 필요, STOP 대기):** 도구를 고친 재실행(W43R)도 **교전 전 배치 단계에서 무효**가 됐다.
  원인은 게임이 아니라 우리 시험 도구의 배치 예측이다. 건물형 유닛(type46)은 3×3칸을 차지하는데 도구는 1칸으로 셌다. 배치 순서도 실제(진영마다 전투 유닛→건물)와 달랐다. 그래서 건물들이 두 줄 사이 빈 띠로 밀려 들어갔다.
  lap554에서 미리 정한 규칙대로 **모델 판단의 재시도는 여기서 닫는다.** 이 경로에서 "마지막 1회"를 이미 네 번 늘렸기 때문이다. 게임이 안 된다는 증거는 없고 네 짝 배치가 가능한지는 아직 모른다.
  **다음 중 하나를 골라 주세요(모델은 고르지 않음):** (가) G2 한정 최소 AI 변경 예외 · (나) "8인"을 사람 슬롯으로 fixture 재구성(가능성 미조사) · (다) S1 교전 트랙 중단(교전 없는 "안정 동작"으로 해석 약화) ·
  **(마) 신규·strategy 권고:** 시험 도구만 고쳐 정확히 1회 더 실행한다. 건물 3×3 반영, 실제 순서 재현, 건물 위치도 함께 탐색, 진영마다 배치 직후 확인해 어긋나면 교전 전에 멈춘다. 비용은 work 1회(게임 15~25분)와 middle 1회다.
  주의: 건물 위치를 옮겨도 지형상 네 짝이 안 들어갈 수 있다(N206). 그때는 그것이 실측 결론이다. **"(마), 실패 시 (다)"처럼 대체안까지 함께 주시면** (마)가 실패해도 다시 묻지 않고 바로 넘어간다.
  문서 `docs/work/active/G2_STRATEGY_S1_BUDGET_CLOSE_LAP558.md`, `ESCALATE_SOL` §112.
- [ ] 2026-09-23 18:43 KST: 사용자 **Q8 = (ㄱ) 목표 재정의** 선택(lap521 §79 트랙② `CLOSED`·STOP 대기 응답).
  G2 합격 기준을 "AI 자연 도달" 대신 **시딩(자원/유닛 주입) 기반 cap 5000 근접 + 안정 동작 증거**로 재정의한다.
  AI 건설 로직은 건드리지 않는다((ㄴ) 미선택, W34 계수 probe 발행 안 함). 144k 발행 금지 재검토는 새 strategy 판정으로.
  Q9·Q7-B·"8인" 정의는 미결 그대로.
  **lap522~lap547 처리 계보(W35~W41R, 62줄)는 lap558에서 종결 계보로 압축했다:** 원문 그대로 `docs/history/20260924_inbox_lap558_q8_s1_lineage_archive.md`(발췌 SHA256 `2977d75a6affdb1e4dd2b08549404afb9ac14a9cf0cab89b60ceaa7d9fe0da58`, 압축 직전 INBOX 전문 SHA256 `262882a0dd69abe09fb1052bcaf1eafdb370c22064acb6fd837126d87a203240`, 346줄 동봉). 삭제·재해석 없음; 이후 흐름은 위 03:15 (라) 항목.
- [ ] 2026-09-23 KST: 사용자 "opus 5.5 나왔는데, 한동안 fable 대신 opus 5.5 사용해보자. effort도 high로".
  **strategy 역할 모델을 `claude-fable-5`/medium → `claude-opus-5-5`/high로 교체**(`loop/env.local.sh`
  `LOOP_CLAUDE_STRATEGY_MODEL`·`LOOP_ASTRA_EFFORT`). `loopctl.sh models` 반영·CLI 응답 확인. middle(opus-5)·
  work(sonnet-5)는 불변. 임시 조치("한동안")라 `docs/MODEL_ROUTING.md`·CLAUDE.md의 Fable 기본값 문구는 고치지 않았다.
- [ ] 2026-09-23 KST: 사용자 "middle이랑 work도 각 모델 최신 버전으로 쓰도록 해". **middle을 `claude-opus-5`→
  `claude-opus-5-5`로 교체**(`LOOP_CLAUDE_MIDDLE_MODEL`). work는 CLI 확인 결과 `claude-sonnet-5-5`·`-5-1`이 카탈로그에
  없어 최신 Sonnet인 `claude-sonnet-5`를 유지한다(다른 세대 폴백 없음). effort는 둘 다 high로 변경 없음. `loopctl.sh models`로 반영 확인.


- [ ] 2026-09-23 12:55 KST: 사용자 "3은 앞으로 말하지 말고, 1 2 바로 ㄱㄱ". **두 트랙을 이 순서로**
  진행한다. **① F4(B) 전비 장부 32-bit 확장** — 2026-09-23 04:13 사용자 승인(APPROVALS 기록) 이미
  받았고 선행조건이던 AI 생산 정지 분석은 lap501~508로 종료됐으므로 **지금 착수 가능**. middle이
  카드부터 발행한다(writer 2곳 `0x43EE9B`/`0x43EF8B`·reader 3곳·필드폭·bulk save/load 포맷,
  저장 호환 방침 포함). **② 건설 선택 로직 분석**(읽기 전용, (ㄴ) 불필요) — 27종 중 18종을 AI가
  왜 안 짓는지. `FUN_00406C70` 추첨 로직 해부 + H-CROWD 채널 주소 정정이 시작점이다.
  **③ 패치본(2601·2606) 실행 검증은 사용자가 제외했다 — 앞으로 제안하지 않는다.**

  **lap509~lap521 진행 추기(lap522 압축 — 원문 전량 보존, 삭제 없음):** 83줄 원문은
  `docs/history/20260923_inbox_lap522_f4b_track2_lineage_archive.md`(발췌 SHA256 `71400fe3…`, 83줄)에 그대로 있다.
  요지: 트랙① W30 `CLOSED`(lap514, 후보 `1893ff50…` 실행0·Q9 미결) · 트랙② W31~W33 `CLOSED`(lap521) ⇒ lap521 STOP → 18:43 Q8=(ㄱ) 응답.

- [ ] 2026-09-23 04:14 KST: 사용자 "AI 생산 정지 원인 분석부터 ㄱㄱ". **N81/N82가 배제만 하고
  코드 원인을 찾지 않은 지점을 먼저 판다.** 실측 사실: 8 AI가 자원 96.8%를 쥔 채 정지하고
  (`used` 최대 1,708/cap 5,000=34%, `count` 108/1,200, `live` 774/4,001) 감쇠가 아니라 **완전 정지**
  (owner5 tick14,641 이후 9,371tick=39% 무증가, `r_late` 정확히 0.0). 즉 자원·count_cap·supply cap·
  풀 **넷 다 원인이 아니다**. 이번 작업은 **읽기 전용 정적 분석**이라 (ㄴ) 승인이 필요 없다 —
  AI 생산 결정 경로(참고 저장소가 `production_pick_context 0x406D15`로 부르는 지점 등)를 추적해
  owner5를 tick14,641에 멈춘 조건을 특정한다. **AI/생산 로직 변경·패치 착수는 금지**(여전히 (ㄴ) 대기).
  `analysis/`에 AI 생산 결정 로직 문서가 **0건**이라 새 근거 문서를 남긴다.
  **lap501~507 진행 추기(lap509 압축 — 원문 전량 보존, 삭제 없음):** 이 지시에 lap501·502·504·505·
  506→507이 덧붙인 추기 77줄은 `docs/history/20260923_inbox_lap509_ai_production_lineage_archive.md`
  (SHA256 `02e057116931a157b0e71dc14b466c96e45fc023e8c1582ba946d32eb8f47db4`, 77줄)에 그대로 있다.
  요지: lap501 정적 추적으로 `FUN_00406770`→`FUN_00406B00`→`FUN_0043E7F0`/`FUN_00406C70` 경로를
  바이트 확정(자원 게이트 0개 ⇒ "자원 잔존+정지"는 정상 동작) → lap502 §7 런타임 probe `UNKNOWN`
  → lap504 독립 재계산 ACCEPT + 해석 반증 N147~N150 → lap505 strategy Q8 = CONTINUE·예산 한정
  + W29 발행 → lap507 W29 실행 `PROBE_OK`·k=8 → **lap508 독립 재계산 ACCEPT ⇒ 라벨
  `NATURAL_ARRIVAL_ARITH_INFEASIBLE` 확정, 단서 정정 N151~N153**(전문 `ESCALATE_SOL`§64~§69,
  `docs/history/laps/20260923_lap50{1,2,4,5,7,8}_*.md`). 이 계보는 **종결**이며, 2026-09-23 12:55
  사용자 지시가 다음 트랙(F4(B) → 건설 선택 로직)을 지정했다. AI/생산 로직 변경은 여전히 0건이고
  (ㄴ)·Q8((ㄱ)/(ㄷ))은 사용자 전권 대기 불변이다.


- [ ] 2026-09-23 lap501 운영 보고 2건 (숨기지 않고 남긴다, 사용자 판정 불필요하면 그대로 둬도 됨):
  **① 연속 3회차 제품 증거 무증가 경계.** lap499(strategy 문서)·lap500(middle 문서)·lap501(middle
  문서)로 **제품 코드/바이너리/실제 실행 증거가 늘지 않은 회차가 연속 3회**다. PROMPT ③은 연속 최대
  2회이고 세 번째는 strategy/Sol이 목표 계속 여부를 먼저 판정하도록 한다. **다만 lap501은
  2026-09-23 04:14 사용자 지시가 "읽기 전용 정적 분석"으로 명시 지정한 작업**이므로 루프 내부 규칙이
  아니라 사용자 지시를 따랐다. **다음 회차는 실제 관측 증거를 만드는 §7 probe여야 하며**, 그것도
  문서로 끝나면 strategy 판정 없이 더 쌓지 않는다(`ESCALATE_SOL` §64 handoff 1).
  **② 참고 저장소에 하네스 scratch 쓰기가 발생한다.** `Syw2plus_re/.omc/` 아래에 세션 state 파일이
  생성된다(이번 세션분 1건, `.omc/state/sessions/eed5d653…/pre-tool-advisory-throttle.json`,
  `analysis/ghidra_output/.omc/`도 동일 계열). AGENTS.md는 참고 저장소를 **읽기 전용**으로 규정하므로
  보고한다. 완화 사실: 해당 경로는 그 저장소 `.gitignore`가 덮고 있어 **추적 대상이 아니고**,
  세션 디렉터리가 386개로 **2026-07-30부터 누적된 기존 패턴**이며, **이번 세션이 추적 파일을 하나도
  변경하지 않았음을 확인**했다(`git status --untracked-files=no` 목록 전체가 2026-09-23 이전 mtime).
  분석 자체는 읽기 전용이었다. 정리·차단이 필요하면 사용자 판정 사항으로 남긴다.

- [ ] 2026-09-23 04:13 KST: 사용자 "전비가 일시적으로 5000을 넘어 보이는 표시를 허용하고, 32비트도 괜찮아".
  **되물음 2건이 사용자 전결로 마감됐다.** ① lap404 = **(가) 채택** — 일시 `used+reserved` 초과
  표시를 허용하고 **라이브 `used` ≤5000만 강제**한다((나) strict 5000 기각). ② F4 = **(B) 채택** —
  전비 장부를 **32-bit로 확장**한다(저장포맷 동반, 큰 작업). (C) 도달성 실측 선행은 기각.
  **두 건 모두 lap404 strategy 권고((가) 권고·F4는 (C) 선행 권고)와 ①은 일치, ②는 반대다.**
  모델이 사용자에게 고지한 단서 원문: (가)는 N19대로 "한 tick 창"이 아니라 owner당 수 분
  (owner6 16,213tick≈490초·owner5 19,904tick≈600초, 초과 owner-표본 216건, 값은 전부
  `used=5000·reserved=10`)이고, "원본 1200-slot 대조군에서도 동일"이라는 귀속은 **미증명**이다.
  F4(B)는 5 사이트+필드폭+bulk save/load 포맷 변경이라 기존 통합 blocker와 동일 성격이다.
  **미결로 남은 판정: Q7-A=(ㄴ) AI 변경 허용 여부 · Q7-B 3단 마일스톤 · (ㄱ)/(ㄷ).**

- [ ] lap462~498 종결 계보 3건(W24~W28-R·W26 144k / lap469~471 Step C / lap462~465 Step A~D; lap519 압축 — 원문 전량 보존, 삭제 없음): 세 항목 전문과 그 안의 precompaction 포인터 연쇄는 `docs/history/20260923_inbox_lap519_precompaction.md`(INBOX 전문 SHA256 `13d5325562b133b2efdd5f88c054fc5a57eb33e8dcf9cb5b6639fd8b2f2f0a60`, 353줄) 138~165행에 그대로 있다. (ㄴ)·Q7-B 등 미결은 불변.

- [ ] 2026-09-21 01:10 KST 운영 회수 — W10 P-A 실제 완료. lap415 입력의 PID 원인 서술은
  **정정**한다: PID는 맞았고 최초 PE mapping 전 일시 `EFAULT`를 retry하지 않은 것이 원인이었다.
  lap416 probe 수정본을 root 소유 동기 세션에서 새 run2로 실행해 709표본/동일 tick11,928 정지를
  재현했다. fault 직전 생존 high-slot **3565/type76/owner4**의 `+0x692`가 tick11,921에서 -6599,
  tick11,928에서 19579로 폭증했고 low band 이상은 0이다. 따라서 카드 P-A의 **H1 지지** 조건을
  충족한다. 증거 `temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/`;
  후보 SHA `4331d9cd…`, 원본 전후 `b56986e0…`, 709 lines, `SAFETY_PASS`, 잔류0. 다음 work는
  W10 P-B의 1200-bound 전수 인벤토리와 이 손상을 만드는 단일 site를 좁힌 뒤 P-C 최소 수리한다.

- [ ] 2026-09-21 01:01 KST 운영 규칙: loop agent가 장시간 Wine probe를 셸 background로 띄운 뒤
  회차를 종료하면 loop cleanup이 자식도 정리해 실행이 지속되지 않는다. 장기 probe는 모델 세션이
  직접 기다리거나 root가 소유한 exec 세션으로 실행·회수한다. “background 실행 중” 문구만으로
  활성 프로세스를 주장하지 않고 PID/산출물 갱신을 확인한다.

- [ ] 2026-09-21 00:51 KST 운영 회수: lap415 W10 P-A probe는 실제 샘플링에 진입하지 못했다.
  `movement_state_probe.py`가 `subprocess.Popen(["wine", ...]).pid`인 Wine 런처 PID 2435667을
  게임 내부 PID로 사용해 PS 주소 `0x4ED818` read가 `EFAULT`로 종료됐고 `samples.jsonl`은 0B다.
  게임 후보 실패나 H1/H2 판정으로 세지 않는다. 산출물은
  `temp/Syw2plus_patch/g2_capacity/20260921_lap415_fault_root_cause_pa/`에 보존됐다. 다음 work는
  기존 `tools.runtime_env`/`runtime_driver`의 검증된 Windows game PID 발견 방식을 재사용해 같은
  P-A를 재실행한다. 새 독자 PID 추측을 추가하지 않는다.

- [ ] 2026-09-21 00:20 KST: 사용자 목표 우선순위 확정. **G2(8인 각각 전비 5000 안정 플레이)가
  성립하기 전까지 G1(1600×1200 원본 구성)과 G4(AI/길찾기 개선)는 잠정 중단**한다. G3(최대
  16인)는 잠정 중단이 아니라 **계속 포기한 범위**로 고정한다. 현재 lap414의 G2 독립 검수는
  이 지시와 일치하므로 중단하지 않으며, 이후 루프도 G2의 직접 조사·수리·실행검증 외 목표로
  전환하지 않는다.

- [ ] 2026-09-20 21:58 KST: 사용자 “아니 뭐 이렇게 굼떠”. 같은 소스에 대해 784개 전체
  `make check`를 회차마다 반복해 실제 게임 실행을 늦추지 않는다. 직전 동일 source의 full gate가
  PASS이면 다음 독립 검수는 원시 산출물·표적 테스트·원본/안전검사만 수행하고 제품 런타임으로
  즉시 이동한다. 전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다.
  **2026-09-20 lap410 적용(상시 규칙이라 체크는 두지 않음):** 이 지시를 처음 적용했다. lap410은 동일
  source·직전 full gate PASS이므로 784 `make check`를 재실행하지 않고 원시 산출물 재계산 + 표적 테스트
  (`test_g2_full_capacity_persistence_compat_v1.py` 5 passed) + 원본 해시 + `checks/safety.sh check`만
  수행했다. 발행한 다음 카드 W8에도 §6으로 같은 규칙을 박아 두었다.
  **2026-09-20 lap412 오적용 정정(N22):** 이 규칙은 "동일 source일 때 면제"이지 "항상 면제"가 아니다.
  lap411은 스스로 `patches/population/runtime_driver.py`(`control_goal_payload`)와 신규 테스트
  `tests/test_runtime_env.py::test_runtime_driver_control_goal_uses_protocol_string_request_id`를
  추가해 **source를 바꿨는데도** "동일 source"를 근거로 전체 gate를 건너뛰었다. 규칙 후단
  "전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다"가 걸리는 경우였다. lap412 middle이
  그 통합 경계 gate를 대신 실행했다(collected **785** = 784+신규1). **규칙 자체는 유효하며 변경 없다** —
  앞으로 면제를 주장하는 회차는 "이번 회차에 source를 바꾸지 않았다"를 함께 적는다.

- [ ] 2026-09-20 00:33 KST: 사용자 "그래 그 1200을 늘릴 수는 없냐고" 이후 "ㄱㄱ".
  G2의 즉시 최우선 작업을 전비 장부 단독 조사에서 **전역 UnitStruct 풀 1,200칸 확장 실행
  스파이크**로 전환한다. 첫 성공 기준은 격리된 실제 게임에서 slot index **1,200 이상** 개체를
  정상 생성하고, 기존 reader로 관측한 뒤 사망·슬롯 재사용까지 증명하는 것이다. 단순 `0x4B0`
  상수 변경이나 다음 상태영역 덮어쓰기는 금지한다. 새 풀/보조배열 주소 재배치와 참조 fixup을
  최소 범위로 구현하고, 실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로
  판정한다. 저장/LAN은 이 첫 스파이크의 PASS 조건이 아니지만 후속 필수 blocker로 명시한다.
  2026-09-20 lap396 전비 probe는 이 최신 우선순위에 따라 안전 종료(exit143, safety ok)했다.
  2026-09-20 lap397 middle이 정적 표면을 측정해 최소 변경 범위를 확정하고 즉시 실행 가능한
  work 카드 `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`(W3)로 인계했다.
  건드릴 것은 재배치3영역(pool/existence/age)+상수4개+fixup1,016건뿐이며 active/catA/catB·
  PlayerStruct roster·`0x892410` 별칭179건은 불필요함을 바이트로 확인했다. 제자리 확장은
  `NOT_FEASIBLE`(풀이 bulk에 밀착·age뒤 구멍 참조9건), 재배치 경로는 구조적으로 `FEASIBLE`.
  lap399 후보는 lap400이 REJECT(제자리 성장), lap401 work가 꼬리 재배치를 구현, lap402 middle이
  독립 검수해 **재배치·fixup·패처 수리는 ACCEPT**하되 **후보 기동은 REJECT**했다 — 재배치 블록의
  99.24%가 어떤 PE 섹션에도 매핑되지 않는 신규 결함(D1, `.data` VirtualSize 산출 한 줄). 수리 카드는
  `docs/work/active/G2_POOL_SECTION_COVERAGE_REPAIR_LAP402.md`(W5).
  lap406 middle이 자칭 lap410/412 런타임 계보를 2단 검수해 항목1/2/4/5 ACCEPT·항목3(커버리지
  앵커)만 게이트 추가 지시(W6)했고, lap408 middle이 그 W6 게이트 2건을 독립 검수해 **CLOSED**
  했다(`make check` 783 passed=779+4, 역주입으로 D1 계열 포착 확인, 원본·pin 불변). lap408은
  같은 계열의 남은 사각 하나를 W7 `G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`로 발행했다
  (`.rsrc` cave wrapper 4건에 컨테인먼트 앵커 없음, 마지막 `LEGACY_COPY` 여유 49B).
  **아직 실제 게임 실행 증거가 없으므로 제품 구현 완료가 아니다** — 체크는 그대로 둔다.
  다음 회차는 W7 뒤 **즉시 P1(near-4000 live 실제 실행)** 이며, 이 첫 성공 기준(slot≥1200
  생성→관측→사망→재사용)의 독립 재현은 여전히 미검증이다.
  **2026-09-20 lap409 work 추기(원문 위는 보존):** W7 앵커 완료 뒤 P1을 착수해 marked compat
  (`4331d9cd…`) 후보로 격리 Wine에서 near-4000(3,991 live, 8owner) 규모 gate-legal 시딩→마킹저장
  (마커 `S2P1N4K1` 파일 오프셋 `0x38` 확인)→마킹로드 왕복을 슬롯 단위로 무손실 확인(소실0·id불일치0).
  slot≥1200 생성→관측→재사용 자체는 이 lap 이전에 이미 실측됐고(seed 시 slot 3977 등 관측),
  이번 lap이 새로 더한 것은 **marked compat 저장/로드가 near-4000에서 실제로 무손실**이라는 증거다.
  **이번 lap은 work 역할의 자기 결과이며 독립(다음 middle) 검수는 아직 없다.** 상세
  `docs/history/laps/20260920_lap409_work_g2_p1_compat_near4000_live_execution.md`.
  **2026-09-20 lap410 middle 추기(위 원문 보존):** lap409 P1을 원시 산출물 재계산으로 독립 검수해
  **ACCEPT**했다(후보 재현·save 해시/마커·스냅샷 diff·receipts·브리지 4001 소스·표적 5 passed·
  `SAFETY_PASS`·원본 불변). 위 21:58 지시에 따라 전체 784 게이트는 재실행하지 않았다(동일 source).
  **신규 근거:** `trace.jsonl`의 tick **2328→1567 역행**이 로드가 실제로 엔진 상태를 교체했음을 직접
  증명한다 — 이것이 없으면 "소실0"은 로드가 아무 일도 안 한 경우와 구분되지 않는다.
  **정정1:** presave 스냅샷이 저장 시점보다 ~535 tick 앞서므로 "5기는 로드 후 생산"은 사실과 다르다.
  4기는 저장 이전 생산(세이브에 포함), 로드 후 생산은 1기. 카운트는 저장 3,995→로드 3,995로 정확
  일치하나 id 단위 검증 범위는 3,995 중 3,991기다.
  **정정2(신규 결함):** 배포 진단 DLL의 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c`가
  stock 유닛 존재배열 `0x008990C8`과 1200 경계를 하드코딩해, 재배치 후보에서 유닛을 0기로 관측한다
  (`C:\inmm_unit_ticks.jsonl`이 3,991기 생존 중 0바이트로 실증). 전부 읽기 전용이라 손상 위험은 없고
  P1 판정에도 영향이 없으나, 향후 lap이 이 채널을 근거로 "전멸"을 오판할 위험이 있다.
  **여전히 제품 구현 완료가 아니다** — 단발 왕복 1회이며 장시간 안정성·원본 생산 경로·LAN 미검증.
  다음 회차는 work 카드 `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`(W8, compat 장시간 soak)다.
  상세 `docs/history/laps/20260920_lap410_middle_g2_p1_independent_review.md`.
  **2026-09-21 lap413~414 추기(위 원문 보존):** W8은 lap411 실행·lap412 ACCEPT로 닫혔고, lap413이 W9(P2,
  원본 생산 명령으로 near-cap 도달)를 실행해 **FAIL**했다 — 자원만 공급(op7)한 8인 AI 대전에서 N=4001
  후보가 **두 번 모두 tick 11,928에서 `read 0x00338400 @ 0x00414133` page fault**로 죽었고, stock-layout
  대조군은 같은 tick을 fault 없이 통과했다. lap414 middle이 요약본을 쓰지 않고 원시 산출물만으로
  재계산해 그 FAIL을 **ACCEPT**하고, fault 기전을 바이트로 확정했다(100칸 stack 배열을
  `((경로점수-1)×|유닛 이동진행도 +0x692|)/100`로 인덱싱하며, 그 명령 바이트는 원본과 동일).
  또 후보가 `.text`의 1200 즉치 54곳 중 **2곳만** 4001로 바꿨고 풀을 순회하는 잔존 1200-bound site가
  최소 3곳 남아 있음을 확인했다. **이 첫 성공 기준(slot≥1200 생성→관측→사망→재사용)은 진단 시딩으로는
  충족됐지만 원본 생산·AI 전투 경로의 안정성은 여전히 미충족이므로 체크는 그대로 둔다.**
  다음 회차는 `docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`(W10)다.

- [x] 2026-09-17 12:23 KST: "일단 그 세 부분 가능 여부를 더 확실하게 알아봐". G1/G2/G4 핵심 blocker를 구별하는 제한 실행 조사; G3 재개 없음. 계측 실패를 전체 목표 불가능으로 치환하지 않는다. 세 bounded 실행카드 종료·Sol검수 리포트 `docs/reports/20260917_THREE_GOAL_FEASIBILITY_UPDATE.md` 작성; 목표완료 아님.

- [ ] 2026-09-15 11:46 KST: "조금 조사한 뒤 안 될 것 같으면 빠르게 불가능하다고 보고하고,
  될 것 같으면 빠르게 작업에 착수"한다. 조사와 문서 자체를 목표로 삼지 않는다. 각 핵심 분기는
  짧은 feasibility 판정(`FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`)으로 끝내고, `FEASIBLE`이면 다음 work
  회차부터 구현·실행 증거를 만든다. `NOT_FEASIBLE`/`BLOCKED`이면 추측성 반복 대신 근거·대안·영향을
  사용자에게 즉시 보고한다.

- [ ] 2026-09-15 11:35 KST: "대목표 4개 중 완료 0개인데 왜 진행 속도가 이렇게 느린가".
  제품 구현보다 해시·스냅샷·시간경계 등 증거 하네스 자체 보수에 과도하게 머문 운영을 교정한다.
  Astra가 큰 방향을 재판단해 G1의 남은 실제 제품 판정을 최단 경로로 닫고, 독립 파일의 G2 구조
  조사를 함께 활성화한다. 이미 충분한 안전 근거가 있는 항목을 반복 검수하지 말고, 새 제품 증거를
  만드는 작업을 우선한다. 정확성·원본 보호·저장/메모리 안전은 계속 타협하지 않는다.

- [ ] 2026-09-10 23:06 KST: 실제 루프 시작. 10분마다 한국 시간과 함께 진행상황 보고.
  Astra/high 상위 전략 → Sol/high 중간 계획·컨펌 → Luna/high 실무 순으로 명시적 1바퀴씩 진행한다.
  자동 서비스/무한 실행/자동 커밋·푸시는 사용하지 않는다.

## 처리 완료

- [x] **2026-09-22 lap487 압축:** 이 섹션의 체크 완료 항목 전량(목표1~4 원문, 모델 역할, 환경세팅, 구조 이관, G3 중단 리포트, astra→fable 전환 2건)은 `docs/history/20260922_inbox_completed_section_lap487_archive.md`(SHA256 `ce6f8daeeda7f235d199dec62350614d2f2458b7ff2a8bd7b678b1eb7e1f8b90`, 34줄)에 **원문 그대로** 보존했다. 삭제 없음. 체크된 상시 요구는 계속 유효하며, 재참조가 필요하면 그 파일을 읽는다.

## 되물음

- [x] 2026-09-20 lap404 되물음 2건(일시 초과 표시 허용 / 전비 장부 16-bit 랩 마감) — **사용자
  2026-09-23 04:13 판정으로 종결**(lap404=(가)·F4=(B), APPROVALS 기록). N19·lap412 기전 확정·
  N68 재현 등 원문 45줄은 `docs/history/20260923_inbox_resolved_questions_lap505_archive.md`
  (발췌 SHA256 `329114042fbffe088b2a237182e52e5448b1376d75f5d5e5bfce102fb20c6077`)에 그대로 있다.
- [ ] 2026-09-21 lap458 work — **W23 A1 24k 연장 결과 `DECAYED` ⇒ (가) 자연 도달은 fixture/config
  축에서 NOT_FEASIBLE 확정.** 카드 `G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md` §4 고정 판정식대로
  W22 최유망 레버 A1(지도140×140)을 tick24,000까지 연장 실행한 결과, `r_late`(owner1,
  16k→24k)=0.008747 < `r_need`=0.033042(=(5000−U_min24 1,035)/120,000) ⇒ `DECAYED`.
  `U_min8`=661(owner5)로 W22 결정성 재확인, 무결성 위반 전부 0, 게임실행1회·source변경0·
  targeted7 passed·`SAFETY_PASS`. 카드가 예약한 대로 **모델은 AI/경로/생산 로직 변경에
  착수하지 않았고** 아래 되물음을 그대로 승격한다(고르지 않음, `G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`
  §7 · `loop/ESCALATE_SOL` §36):
  - **(ㄱ)** 시딩 기반 cap 근접 + 왕복 증거(W21)를 G2 안정성 증거 축으로 인정하고 (가)를 재정의할지.
  - **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 — 2026-09-21 00:20 G4 잠정 중단의 명시 예외 승인 여부.
  - **(ㄷ)** 현재 기준(자연 도달 요구) 유지, (가) 보류.
  이 3건은 바로 위 lap404 되물음(전비 장부 16-bit 랩 마감 방식)과 함께 사용자/strategy 판정
  대기 상태다. 상세 `docs/history/laps/20260921_lap458_work_g2_w23_a1_long_window_decayed.md`.
  - **2026-09-21 lap459 middle 독립검수 = ACCEPT(재계산 불일치 0)**, 위 원문 유지·선택지 미변경.
    원시 721표본만으로 비참조 재계산해 `U_min24`=1,035(owner1, tick24,012)·`r_late`=0.008747·
    `r_need`=0.033042·`DECAYED` 전부 일치, `U_min8`=661/owner5로 W22 결정성 정확 재현, 실행 **전**
    고정 기대 band 1,050~1,073 대비 실측 1,035(−1.4%).
    **판정 방향에 영향을 줄 신규 실측:** **(N81)** 정체 원인은 자원·cap·풀이 전부 아니다 — 최소
    rice 967,672/wood 969,464(지급 1,000,000의 **96.8%가 최악 시점에도 잔존**), `count` 최대
    108/1,200, `used` 최대 1,708/5,000 ⇒ **AI가 자원을 거의 손대지 않은 채 스스로 생산을 멈춘다.**
    **(N82)** 부드러운 감쇠가 아니라 owner별 **완전 정지** — owner5는 tick14,641 이후 런의 39.0%
    동안 `used` 불변(`r_late` 정확히 0.0), owner7 31.8%, owner6 15.4%.
    ⇒ 두 실측은 **(ㄴ)이 유일하게 남은 기술적 진입로**임을 시사하나, 이는 사용자 지시
    (2026-09-21 00:20)의 명시 예외 승인이므로 **모델은 착수하지 않고 승인을 기다린다.**
    **(N83) 경고:** 이 run은 바로 위 lap404 되물음에 **새 증거를 주지 않는다** —
    `used+reserved>5000` 0건(아무도 cap 근처에 못 감)이라 N68 현상이 발생할 수 없다.
    **(N84) 표현 정정:** "전 owner 감쇠"는 과장 — owner0(0.04498)·owner2(0.03749)는 `r_need`를
    후반에도 넘는다. 판정이 유지되는 이유는 G2가 "8인 **각각** 5,000"이라 최저 owner가 구속
    조건이기 때문이다. 정확한 서술은 "8인 합계가 24k에서 11,207 = 8×5,000의 **28.0%**".
    상세 `docs/history/laps/20260921_lap459_middle_g2_w23_a1_independent_review.md`.
  - **2026-09-21 lap460 strategy(Fable5) 처분(`ESCALATE_SOL`§38, 원문 보존·사용자 번복 가능):**
    **(ㄱ) 채택·(ㄷ) 기각** — G2 원문 계약은 "cap5000 플레이 안정"이므로 gate-legal 시딩
    cap근접+soak+왕복을 증거 축으로 인정(마일스톤 승인 대체 아님, 자연 도달 계속 요구 시 번복).
    **(ㄴ)은 모델이 고르지 않고 사용자 승인 대기 유지**(승인 전 AI/설정 변경 착수 금지).
    lap404는 **(가) 잠정 채택**(stock cap5000 `reserved` rider probe를 W24에 의무화, 미재현 시
    회귀 승격·재심). F4는 **(C) 채택**(soak에서 랩/음수 관측 시 즉시 STOP 후 (B) 재심). 다음은
    middle이 **W24**(혼합 구성+전투/사망/재사용 순환 24k) 1장 발행, **144k 금지는 W24 ACCEPT까지 유지**.
  - **2026-09-21 lap461 middle 신규 실측 N87 — (ㄴ)의 무게가 커졌다(선택지 미변경, 모델은 고르지 않음):** lap448에서 8 owner의 배치 주사 구간은 전 쌍에서 겹쳐(2-3 501셀·6-7 484셀 등) 적 유닛이 24,000tick 내내 셀 단위로 인접했는데도 소실은 **4기/1,166기**뿐이었다 ⇒ "전투/사망/슬롯 재사용" 축도 **기하(fixture)로는 만들 수 없음**이 실측됐고, 남은 fixture 내 가설은 구성(타입) 하나뿐이다. 그것마저 실패하면 자연 도달에 이어 **전투 축까지 (ㄴ) 승인 없이는 닫히지 않는다.** W24는 그 결과를 `NO_ENGAGEMENT`로 정직하게 보고하도록 실행 전에 고정했고 **승인 전 AI/생산 정책 변경에는 착수하지 않는다.** 근거 `docs/history/laps/20260921_lap461_middle_g2_w24_issue_and_combat_axis_finding.md`·`ESCALATE_SOL`§39.

실제 구현 선택이 목표·안전·배포 범위를 바꿀 때만 새 질문을 추가한다.

## 2026-09-17 15:20 KST — G2 최우선 루프 재개
- [x] 사용자: "8인 각각 전비 5000 안정 플레이 이걸 최우선 목표로 좀 파보자. 루프 ㄱㄱ". 큐/우선순위 반영(제품완료 아님). G1/G4 후순위, G3중단 유지.

## 2026-09-17 21:16 KST — 사용자 루프 시간 상한
- 사용자: “한국시간 기준12시까지만 루프 돌릴거야. 이후는 진행속도나 가능성 생각해서 볼테니까 그거 생각해서 진행해봐”.
- 현재21:16이므로 Root는 **오늘밤자정2026-09-18 00:00KST**를 보수상한으로 잡았다고 사용자에게 명시했다. 정오를 뜻한 경우 정정 대기; 답변전에는 더짧은상한 유지.
- 10분마다KST보고, 상한에서신규작업중단/ownedcleanup/성과·가능성정리. 기존 STOP 예산리셋·목표축소·제품승인 아님.

## 2026-09-18T17:56:55.515225+09:00 — Claude Code 전환 및 루프 재개
- 사용자: “ㅇㅇ 그렇게 가보고 루프 다시 돌려”. 중간계획/검수ClaudeCode Opus5/high, 실무ClaudeCode Sonnet5/high, 큰분기Astra medium(필요high) 유지. 새명시재개는어제00상한종료이후재개허가이며원제품목표/원본안전/실패보존유지. 이전STOP기술카드예산자동리셋/제품승인아님. 10분KST보고 유지,서비스/커밋/자동push안함.

## 2026-09-21 종결 계보 3건 (2026-09-23 압축 — 원문 전량 보존, 삭제 없음)

lap423·429·438·440·442 운영 회수 계보 / lap425·427·428 계보 / Root 회수 lap448 W21 Step1 24k soak —
세 섹션 전문은 `docs/history/20260923_inbox_closed_lineages_lap500_archive.md`
(SHA256 `5f62ae8d7922d393f0bb6211719dbce8b7f192363bb93e30259f8cbf053d3e50`, 36줄)에 그대로 있다. 전부 종결된 계보이며 재참조 시 그 파일을 읽는다.
```

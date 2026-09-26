# G1-S1 결정성 연구 계약 (1쪽) — lap271 middle 초안

작성: Claude Code `claude-opus-5`/high, middle tier. lap267 Astra **항목4** 이행.
수신: 다음 work tier(Luna 또는 Sonnet5/high). **이 문서는 연구 계약이지 Stage B 실행 허가가 아니다.**

> **lap277 middle 판정:** 아래 §3의 **요약 측정식은 반려됐다**(공허한 참 + 항목1·5·6 미포함,
> 기계 증거 `logs/lap277/s1_formula_probe.json`). 여섯 항목과 tick 규칙, work 산출물 표는
> `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §3~§4를 따른다.
> §3의 여섯 항목 목록과 §4~§7의 허용/금지/경계는 그대로 유효하다. 원문은 보존한다.

## 1. 왜 필요한가 (실측된 문제)

Stage B 카드가 overall `PASS`에 도달하려면 원본 run과 후보 run이 **같은 장면**이어야 하고
(`_scene_report` → `UNKNOWN_SCENE_MISMATCH`), 그 위에 **같은 엔진 slot id**까지 나와야 한다
(`compare_g1_stage_b.py`의 `UNKNOWN_SLOT_CORRESPONDENCE`, lap221 F2-R2). 그런데 현재 fixture는
producer가 스스로 기록하듯 무작위다:

- `tools/runtime_env.py:3548` — `"map": "default two-player random game; map name/seed not exposed
  by approved read-only offsets"`
- `tools/runtime_env.py:3551`, `:3919` — `"replay_seed_observed": False`
- `tools/runtime_env.py:3740` — `"fixture": {"kind": "new private copy; default two-player random game"`
- 실행 경로는 실제 메뉴다: solo 모드 → lobby(`G1_SETUP_POINTS["lobby_start"]`) → ready DWORD →
  PS5→PS3. 즉 장면은 매 run 엔진이 새로 생성한다(lap214 재현).

그래서 **원본↔원본 대조조차 mismatch**가 난다(S1). 장면만 맞춰도 slot 대응이 남는다(F2-R2).

## 2. 조사 가설 (미검증 — 존재 여부부터 확인할 것)

> 원본에는 "동일한 초기 상태를 복원하는" 경로가 이미 있고, 그것을 fixture로 쓰면 S1과 F2-R2가
> 동시에 풀린다.

후보 두 갈래와 **실재하는 출발 자산**(읽기 전용, 이번 lap에 목록/해시만 확인):

| 갈래 | 자산 | 근거 |
|---|---|---|
| (a) 저장/불러오기 | `Syw2plus/save/save000.dat` `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`, `save006.dat` `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` (총 2개) | 진행 중 상태를 통째로 담은 것으로 보이는 3MB급 파일이 실제로 존재 |
| (b) 고정 시나리오/맵 | `Syw2plus/stagemap/plus01..plus24.map` (24개, 예: `plus01.map` `d9676e5eea935c8a3aba9c716971ba3b3c0ac8a9a3fa80a0d67ed3ba4475e67e`), `Syw2plus/cusmap/*.map`, `Syw2plus/OnlineBattleMap.dat` `74c6132ccdd056de7521d2c47bbcbf8032d5c0ad94430313ecc16fe67f3af5ab` | 모든 `.map`이 정확히 1,132,876바이트로 동일 포맷. 8인 표기 맵 다수 |

**이 표는 "경로가 있다"는 증거가 아니라 "조사할 지점이 있다"는 증거다.** 저장 파일이 존재한다는
사실이 로드 후 slot id 재현을 보장하지 않는다.

## 3. 합격/불합격 측정식 (work tier가 반드시 먼저 적고 시작)

S1 해법이 **충분**하려면 같은 fixture를 두 번 적용했을 때 아래 6개가 **전부** 재현돼야 한다.
하나라도 빠지면 "부분 해결"이 아니라 **불충분**으로 기록한다.

1. `scene.owners`의 nation / player 구성
2. `scene.unit_slots`의 owner별 unit type 집합
3. `scene.unit_slots`의 **상대 world offset** 집합 (`_unit_records`의 anchor 기준)
4. `scene.world_bounds`
5. **엔진 slot id 그 자체** (F2-R2가 요구. 3까지만 맞으면 카드는 `UNKNOWN_SLOT_CORRESPONDENCE`)
6. 첫 입력 직전 상태 — `G1_SELECTION_COUNT_ADDRESS` 계열이 읽는 selection count / 카메라 / tick 기준점

측정식: 같은 fixture로 얻은 두 evidence를 `compare_g1_stage_b.compare_evidence`에 넣었을 때
`scene.status == "PASS"` **그리고** 세 stage 모두 `UNKNOWN_SLOT_CORRESPONDENCE`가 **아님**.
그 전 단계(게임 예산 0인 지금)는 **파일 근거만으로** "이 6개를 함께 복원할 수 있다고 볼 근거가
있는가"를 답하는 것이다.

## 4. 이번 조사에서 **허용되는 것** (게임 실행 0)

- `Syw2plus/` 원본 트리 **읽기 전용** 조사: 파일 목록, 크기, 해시, 헤더/구조 정적 판독.
- 기존 승인된 읽기 전용 오프셋(`analysis/memory_maps/`, `tools/runtime_env.py`의
  `G1_*_ADDRESS` 상수)과 그 근거 문서 대조.
- 원본 EXE/DLL의 **정적** 문자열·임포트 조사로 save/load·map 로딩 진입점의 **존재 여부** 확인.
- 과거 lap 기록·스크린샷·evidence JSON에서 메뉴에 저장/불러오기 항목이 보이는지 대조.
- 결론을 `docs/history/laps/`에 기록하고 필요한 오프셋 후보는 근거와 함께 `analysis/memory_maps/`에 제안.

## 5. **금지** (위반 시 즉시 STOP)

- **RNG seed 주소/시드 패치 추측 금지.** 승인된 seed 오프셋은 존재하지 않는다. 다른 버전의
  오프셋을 옮겨 적지 않는다.
- **원본 트리 쓰기 금지.** `Syw2plus/`의 save·map·EXE·DLL을 수정/이동/삭제하지 않는다.
  이 파일들을 커밋하지 않는다(해시만 기록).
- **게임/Wine/Xvfb 실행 금지, Stage B run 금지, 원본 재실행 금지, R6-A/R6-C 금지.**
  S1/F2-R2 상위 재결 전까지 STATUS blocker가 유효하다. 실행 예산은 0이다.
- 저장 파일 포맷을 **추측으로** 파싱해 "복원 가능"이라고 쓰지 않는다. 구조를 못 읽으면 못 읽었다고 쓴다.
- F2-R2의 slot 강등 규칙을 완화하지 않는다(상위 tier 소관). 새 PASS 경로를 만들지 않는다.

## 6. 산출물 (둘 중 하나. 둘 다 합격이다)

**(A) 실행 가능한 fixture 설계** — 6개 항목을 어떻게 함께 복원하는지, 어떤 메뉴/파일/오프셋을
쓰는지, 무엇을 아직 모르는지. 여기에는 **게임 실행 예산 요청**이 포함되며, 그 요청은
상위 tier(Astra/사용자) 승인 전에는 집행되지 않는다.

**(B) research blocker** — "지원 경로가 없다/확인 불가"를 **정확한 누락 근거**와 함께 반환한다.
무엇을 봤고(파일·오프셋·문서 경로와 해시), 무엇이 없어서 막혔고, 그것을 얻으려면 어떤 **좁은**
다음 probe가 필요한지. Astra 항목4가 명시적으로 허용한 결과이므로 실패가 아니다.

두 경우 모두 **"모르겠다"를 PASS로 바꾸지 않는다.** 부분 결과는 부분으로 기록한다.
프로세스 exit 0은 계획 승인도 검증 통과도 아니다.

## 7. 순서와 경계

- 이 계약은 **F3-R2 수리 다음**이다(lap271 분류: offline 큐에서 Stage B 선행조건은 F3-R2 하나).
  다만 F3-R2를 고쳐도 S1/F2-R2가 풀리지 않으면 Stage B는 여전히 잠겨 있다.
- 한 바퀴 한 가지. 첫 조사 60~90분 또는 실패 가설 2회 후 재평가하고 구체적 blocker를 남긴다.
- 결과는 다음 새 middle 세션이 독립 검수한다. 자기 승인 금지.
- 이 문서는 middle 초안이며 **상위(Astra/사용자) 재결 대상**이다. 특히 (A)의 실행 예산 요청과
  F2-R2 slot 규칙은 이 tier가 결정하지 않는다.

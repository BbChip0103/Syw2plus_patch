# lap334 middle — 후보 R1 관측 봉투 (ACCEPT) 와 lap333 문서 실패 검수

2026-09-12 / lap334 / Claude Code `claude-opus-5` / high / middle(진단·계획·확인).
상위 방향은 `G1_CANDIDATE_R1_DIRECTION_LAP333.md`(Astra), 승격 요청 원문은 부록 A.
이 문서는 **봉투(실행 전 계약)** 이며 구현이 아니다. middle은 게임 코드/하네스를 직접 고치지 않는다.
제품 G1 합격·Stage B 허가·마일스톤 종료/이동·사용자 승인은 이 문서에 없다.

## 0. 이번 바퀴 판정 요약

| 항목 | 판정 | 근거 |
|---|---|---|
| lap333 STATUS 문서 실패(131>130) 사후 상태 | **PASS(보존 확인)** | §1 |
| 정정 C1 독립 재유도 | **CONFIRMED** | §2 |
| Astra 선택 2(후보 R1 관측 우선) | **ACCEPT** | §3 |
| 후보 식별 근거 | **확정 가능** | §4 |
| 후보 입력 좌표 변환 | **확정(보존 증거로 판별됨)** | §5 |
| 후보 R1 봉투 발효 | **ACCEPT (구현 카드만; 실행 예산 여전히 0)** | §4~§12 |

검증 probe: `docs/history/laps/probes/20260912_lap334_middle_candidate_r1_envelope_probe.py`
(`698993b8007999f0b0008fecc057df9f75315cf530e839f8afc5798ba55f7e2c`), rc0, `failures=[]`,
stdout SHA256 `d0b3c7225a904c2fc6aa066624c198438ba4faa275a3c9173cadec31e7eba893` (연속 2회 byte-identical).
**N12(자기 정정, 수치 영향 0):** probe 초판은 lap333 보존 검사를 **살아 있는 STATUS**와 비교해, 이 바퀴가
STATUS를 갱신하는 순간 영구 실패하는 자기무효 검사였다(W3 함정과 같은 형태). 기대값을 고쳐 통과시키지 않고,
비교 대상을 **불변 압축본 두 개**(lap332 종료본·lap333 종료본)로 바꿔 판정 자체를 재현 가능하게 만들었다.
같은 이유로 probe 출력에서 **살아 있는 STATUS 해시를 제거**했다(출력 SHA가 이후 모든 STATUS 편집에 딸려
바뀌면 기록된 SHA가 무의미해진다). 검수한 STATUS 해시는 아래 문단과 lap334 기록에만 남긴다.
이번 검수 대상 STATUS(편집 전, lap333 종료본) SHA256 `b2d2c230…7ee1e5d`, 130줄.
`make check` 368 passed(56.31s)·Ruff/compileall/mypy/CONTEXT_PASS·rc0, `checks/safety.sh check` SAFETY_PASS.
게임 실행 0회, 입력 0회, 메모리 쓰기 0회, PNG 0장, 커밋 0건.

## 1. lap333 문서 실패 검수 — 손실 없음 (PASS)

lap333은 STATUS 편집안이 131줄이 되어 쓰기 **전** 중단했다고 기록했다. 현물로 확인한다.

- 현재 `docs/STATUS.md`는 **130줄**, SHA256 `b2d2c230c907d0e34629cdd2e188013ee41d49d680aa2be2b45597f617ee1e5d`,
  `## ` 표제 5개, `## 지금 막힌 것 (Blockers)` **정확히 1개**, 개행 종료. loop/PROMPT.md 계약 충족.
- 편집 전 원문은 `docs/history/laps/20260912_status_lap332_compaction.md`의 fenced block에 보존되어 있고
  그 body SHA256은 기록된 `ec10aaec…8982cbbf`와 **일치**, 줄 수 130으로 일치한다.
- 보존본과 현재 STATUS를 줄 단위로 비교하면 차이 나는 줄은 **0-based 인덱스 `[20,21,22,23,25,128]`뿐**이다:
  「다음 한 가지」4줄, 블로커 첫 항목의 **머리말 한 줄**, 「바퀴 기록」한 줄. 블로커 본문·미결·반려·
  provenance 회귀 항목은 한 줄도 삭제·축약되지 않았다.
- 즉 실패는 **사전 assert에서 멈춘 정상 방어**였고, 디스크에는 절단·유실 흔적이 없다. 재시도도 없었다.

**주의(수치 영향 0, N10):** 압축 파일 이름 규칙은 "`status_lapN_compaction` = lapN 종료 시점 STATUS"이다.
lap332 파일의 제목이 "lap333 편집 전"인 것은 같은 뜻이며 lap331 파일(126줄)과도 일관된다. 혼동 방지를 위해
이번 lap334 보존본은 `20260912_status_lap333_compaction.md`로 둔다. 규칙을 바꾸지 않는다.

## 2. 정정 C1 — 원본 바이트에서 독립 재유도 (CONFIRMED)

lap333은 Capstone으로 C1을 재확인했다. 이번 probe는 **디스어셈블러 없이** PE 섹션 매핑과 원시 바이트만으로
같은 결론을 재유도했다(원본 SHA `b56986e0…c08a8ac` 실측 불변).

`0x4233B8`부터 39바이트 = `0fbf0518d84e00 83f828 0f8f57010000 0f8447010000 48 83f822 0f87f0feffff ff248538374200`
→ `movsx eax, word[0x4ED818]` / `cmp eax,0x28` / `jg 0x42351F` / `je 0x423515` / `dec eax` / `cmp eax,0x22` /
`ja 0x4232C8` / `jmp [eax*4+0x423738]`. rel32 3건을 직접 계산해 목적지를 얻었다.
**추가 재유도:** 테이블 `0x423738`의 34번 엔트리(인덱스 PS-1)는 `0x0042341B`로, STATUS의 PS35 도달 판정식과
일치한다. 따라서 C1은 판정식에 **수치 영향 0**이며, PS `40/150/180`이 정당한 상태값이라는 lap332 정정도 유지된다.
PS 레지스터 store 33건 fail-open과 계산/간접 writer 미배제는 **그대로 열려 있다**.

## 3. Astra 선택 2 검수 — ACCEPT

선택 2(후보 R1형 읽기 관측 우선)를 받아들인다. 이유는 범위가 아니라 **차단 구조**다:
Stage B(선택 1)는 WM_CLOSE teardown 결함과 S1/F2-R2 결정성이 앞에 있고, 원본 n>1(선택 3)은
후보 차이를 전혀 측정하지 못한다. 후보 1 run은 "원본 A → 후보에서 무엇이 되는가"를 처음으로 측정한다.

다만 lap333 §5가 "후보 식별·좌표 변환·PS 판정식 적용 가능성 **미확정**"이라 적은 세 항목은
**이번 검수에서 보존 증거로 확정된다**(§4·§5·§6). 그래서 BLOCKED가 아니라 ACCEPT다.

## 4. 후보 식별 — 무엇이 "후보"인가 (고정)

후보는 새 렌더러도 새 게임 패치도 아니다. **동일 EXE + 고정된 dxwrapper 프로필**이다.

1. 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 사본도 동일해야 한다
   (`prepare`가 복사 후 해시로 이미 강제). EXE/DLL 바이트 패치 **0건**.
2. 프로필: `patches/resolution/dxwrapper_config.py`의 고정 pin —
   원본 ini `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`,
   후보 ini `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`.
   변경은 3줄(`LoadCustomDllPath` 비움 / `DdrawIntegerScalingClamp=1` / `DdrawMaintainAspectRatio=1`).
   설치는 `install_private`(사본 전용, 백업+patch.json 사이드카), 원복은 `uninstall_private`.
3. 실행 명령: 그 run만 `WINEDLLOVERRIDES=ddraw=n,b`. 나머지 환경은 원본 R1과 동일.
4. **실제 주입 대상 확인:** 모듈 증거에서 private `game/ddraw.dll`이 로드됐음을 확인하고,
   `syw2x.dll`(QHD 커스텀 경로)은 로드되지 **않았음**을 함께 기록한다. 둘 중 하나라도 어긋나면 실행 중단.
5. artifact에 `prepare`의 support 해시(`ddraw.dll`, `dxwrapper.dll`, `_inmm*.dll`, `syw2x.dll` 존재분)를
   **실측값 그대로** 남긴다. 기대 SHA를 새로 pin하지 않는다(기존 pin 자동 수정 금지).

## 5. 입력 좌표 변환 — 보존 증거가 이미 판별한다 (확정)

Astra는 "(296,505) 또는 2배 값을 무근거로 복사 금지"라고 했다. 근거는 **있다**. 두 후보 run이 서로를 판별한다.

- **lap148**(`docs/history/laps/20260911_lap148_luna_g1_config_2x_block.md`, `f066bd82…d90e8`):
  root/client 1600×1200, scale 2.0×2.0에서 **scaled(×2) 메뉴 클릭 1회 → PS9/tick0 그대로, PS7 미도달 = FAIL**.
- **lap154**(`…lap154_luna_g1_dxwrapper_install_finalization_block.md`, `bd74b47f…cae11`):
  같은 후보 구성(candidate ini `f0ce…6785` 설치, private ddraw 로드)에서
  **unscaled `(184,560)` → PS9→PS7→PS3 PASS**, logical `[800,600]`, client `[1600,1200]`, scale `[2,2]`.

결론: 후보에서도 게임은 **논리 800×600 좌표를 받는다**. 표시층만 정수 2배다.
따라서 후보 R1 클릭은 `root = (content_child.x + 296, content_child.y + 505)`, **배율 곱 없음**이다.
현재 하네스도 같은 규약이다 — presentation-trace의 모든 클릭이 `content_crop + 논리좌표`이고
`input_scale`은 **기록용 메타데이터일 뿐 클릭에 곱해지지 않는다**(probe `trace_click_is_unscaled`).

**N11(수치 영향 0, 이름 오해 위험):** `input_scale`/`scale`이라는 필드명은 "적용된 변환"처럼 읽히지만
실제로는 적용되지 않는 관측값이다. 이번 카드에서 이름을 바꾸지 말고, 후보 artifact에
`input.scale_applied = [1.0, 1.0]`를 **명시**해 오독을 막는다.

**기하 게이트(클릭 전):** root 1600×1200 + content child 1600×1200 + scale 정확히 `[2.0,2.0]`.
content child가 800×600이면 프로필이 먹지 않은 것이므로(lap152 선례) **클릭 없이**
`BLOCKED_PRECONDITION`으로 종료한다. root만 1600×1200인 것은 후보 성립 근거가 아니다.

## 6. 읽기와 PS35 판정식의 후보 적용 가능성

- 주소·폭은 원본 R1과 동일: PS `WORD@0x004ED818`(+ dword 교차 읽기), pending `WORD@0x00B92CC0`,
  origin `x,y,tag = 3×WORD@0x01088B5C`. 수단은 `process_vm_readv` 폴링뿐. 쓰기·ptrace·int3·디버거 0회.
- **적용 가능한 이유:** EXE가 byte-identical이고 이미지 베이스 `0x400000` 고정, 위 주소는 전부 정적 전역이다.
  후보는 ddraw 계층만 바꾼다. 디스패처·점프테이블(§2)도 같은 바이트다.
- **적용되지 않는 것:** PS 레지스터 store 33건 fail-open, 계산/간접 writer, `0x4D60B0` 조기 반환 시
  `post==pre==0` UNKNOWN은 후보에서도 그대로 열려 있다. 후보 run은 이를 닫지 못한다.
- 짧은/실패 read는 성공으로 올리지 않고 원시 바이트와 함께 `COLLECTION_ERROR`로 남긴다.
- **N8 반영:** PS 표본은 9/35뿐 아니라 관측된 **모든 값**(40/150/180 포함)을 시계열로 공개한다.
- **N9 반영:** prepare 스모크 설정과 실제 run 설정을 artifact에서 **별도 출처**로 표시한다
  (`manifest.runtime_config` 값을 run 설정으로 재사용하지 않는다).

## 7. 격리·소유·정리

- 새 `prepare` run(새 전체 사본·새 prefix·새 빈 Xvfb display), 소유 PID만. 전역 pkill 금지.
- 사전 조건: `_prefix_pids(prefix)` 비어 있음, 기존 state 없음, 후보 artifact 파일 부재, 전용 lock
  (`.r1-load-origin-candidate.lock`)을 원본 lock과 **다른 이름**으로 잡는다.
- 정리: 소유 자식 terminate→(5초)→kill, `wineserver -k`/`-w`, Xvfb 종료, `prefix_processes_after` 빈 배열,
  그리고 **dxwrapper 원복**(`uninstall_private` → ini가 `918e7043…a5a2`로 복귀, 사이드카 2개 삭제).
  원복 실패는 숨기지 말고 `cleanup.error`로 남긴다. dxwrapper 로그는 run 출력으로 보존한다.
- **WM_CLOSE 결함은 이 run의 게이트가 아니다.** R1 경로는 WM_CLOSE를 보내지 않고 terminate/kill +
  `wineserver -k`로 끝낸다(probe `r1_cleanup_is_terminate_kill_not_wm_close`). 후보 native ddraw의
  teardown 미완료(lap155·lap167~169)는 **이 카드에서 조사·수리 대상이 아니다.** P6도 착수하지 않는다.

## 8. 시간 봉투

총 **≤90초 단일 deadline**, 배분 상한 유지: 준비/PS9 40초, 클릭→PS35 20초, 관측 15초, 종료 15초 확보.
lap331의 elapsed 4.278초는 **n=1 전체값**이므로 배분을 줄이는 근거로 쓰지 않는다(Astra §4 유지).
artifact에 구간별 monotonic 시작/끝을 `stage_timeline`으로 남긴다. 자동 연장·재시도·재클릭 **0회**.

## 9. 실패 모드와 PASS 정의

선언 필수 실패 모드: `NOT_REACHED`(PS9 또는 PS35 미도달), `NO_CHANGE`(전역 미변화), `TIMEOUT`,
`COLLECTION_ERROR`, 그리고 `BLOCKED_PRECONDITION`(PS9 origin≠(0,0,0) / 기하 게이트 / 모듈 게이트 실패).
이들 중 하나를 원시 표본과 함께 남기는 것도 **정당한 연구 결과**다. 실패 시 연장·재시도 금지.

**PASS(수집 유효성) =** 검수한 후보/하네스 SHA 일치 + 소유·격리 확인 + 기하/모듈 게이트 통과 +
입력 정확히 1회 + 독립 PS 도달 근거 + 일관된 pre/post 표본(WORD==DWORD·단조 시계열) + 예산 준수 +
cleanup·원복 성공 + 원시 artifact 보존.
**값 분류는 PASS와 분리한다.** 후보 A/B 예측은 그 run 자신의 스프라이트 헤더로 계산하고,
원본 A `(240,145)`를 후보의 정답으로 고정하지 않는다. 다른 유효값도 연구 결과다.
`pre==post`, 불완전 read, 불일치는 성공으로 승격하지 않는다.

## 10. 출력 artifact — 이름 분리가 필수다

후보 결과는 **`output/r1_load_origin_candidate.json`** 에 쓴다. 이유는 취향이 아니다:
lap332 probe가 `local/runtime/*/output/r1_load_origin.json`을 glob해 **전 저장소 정확히 1건**을 단언한다
(probe `e8dc8c75…a1f9c367`). 같은 이름을 쓰면 과거 exact-once 단언이 깨지고, 그것을 통과시키려
기대 건수를 고치는 것은 **금지**다. 원본 artifact·원본 전용 probe·그 범위는 그대로 둔다.

필수 필드: `variant="candidate-dxwrapper-2x"`, `run_id`, 모든 관련 SHA(EXE/ini old·candidate/지원 DLL/
manifest/하네스), `window`(root·content child·physical/logical·scale·tree 해시), `input`(client·root·
`scale_applied`·count=1), `pending_state`/`ps_word`/`ps_dword` 시계열 전량, `origin_tag` pre/post,
`stage_timeline`, `cleanup`(원복 포함), `classification`, `status`, `failure` 상세.
PNG 0장, 제품 comparator/baseline/golden 소비 0. 후보 run 역시 **전 저장소 1건**으로 별도 단언한다.

## 11. work tier 구현 지시 (Luna/Sonnet5 high, 실행 0회)

허용 파일: `tools/runtime_env.py`(새 서브커맨드 `g1-r1-candidate-load-origin`), 해당 테스트 파일.
`patches/resolution/dxwrapper_config.py`의 pin은 **건드리지 않는다**.

1. 기존 `g1_r1_load_origin`의 **원본 경로 거동을 바꾸지 않는다.** 공통 부분은 헬퍼로 뽑되
   원본 경로의 입력/게이트/artifact 이름/실패 분류는 이번 변경 전후로 동일해야 한다.
2. 후보 경로: `ddraw=n,b` + `install_private`/`uninstall_private`(finally) + 모듈 게이트 + 기하 게이트 +
   §5 무배율 클릭 + §10 artifact.
3. 테스트(합성/오프라인, 게임 실행 없이): 기하 게이트 FAIL(800×600 content) → `BLOCKED_PRECONDITION`,
   모듈 게이트 FAIL → 중단, 클릭 좌표가 `content_crop + (296,505)`임을 단언(×2 방지 회귀 테스트),
   artifact 이름 분리 단언, 원복 실패 시 `cleanup.ok=false` 단언, 네 실패 모드 + 사전조건 모드 분류 단언.
4. `make check` 전체 통과 + `checks/safety.sh check` SAFETY_PASS. **실행은 0회.** 기록은 lap 템플릿대로.
5. 자기 결과를 자기가 승인하지 않는다. 다음 새 middle이 구현을 독립 검수한 뒤에야 1 run이 발효한다.

## 12. 금지·발효 순서

금지(유지): W3 재pin, 원본 n>1, 재클릭, 예산 확대, Stage B, PNG, baseline/golden/안전 pin 갱신,
원본·참고 저장소 쓰기, ptrace/int3/winedbg/gdb, 새 의존성, G2~G4 확대, 기대 SHA/건수 자동 수정,
WM_CLOSE/P6 착수, 커밋(`LOOP_ALLOW_COMMITS=0`).

발효 순서: **이 ACCEPT → work 구현/검사(실행 0) → 다음 새 middle 독립 검수 → work 정확히 1회 실행 →
다음 새 middle artifact 판정.** 현재 실행 예산은 여전히 **0회**다. 이 문서는 실행 허가가 아니다.

## 13. 이 문서가 아닌 것

제품 G1 합격, Stage B 허가, 마일스톤 종료/이동, 사용자 승인이 아니다. G2~G4 증거는 0이다.
`make check` 368 passed·SAFETY_PASS·probe rc0은 계획 승인도 제품 검증도 아니며, 프로세스 exit0은
어떤 승인도 대신하지 않는다. 후보 1 run은 결정성(n>1), hitbox, 실제 save/load, 동일상태 pair,
WM_CLOSE 해결, S1/F2-R2 결정성을 증명하지 못한다.

## 부록 A — 소비한 lap333 `loop/ESCALATE_SOL` 원문

원문 SHA256: `299a1f1789f340bbb676de516aef4b8e8d5c0e3ee30b61144e04505585572a2d`
소비 규칙은 lap325→lap326, lap332→lap333 선례를 따른다. 원문을 아래에 그대로 수록한 뒤 파일을 제거한다.

```markdown
# ESCALATE — lap333 Astra → middle 봉투 검토

lap333 / 2026-09-12 / Codex gpt-6-astra / high.
기존 lap332 파일 원문은 docs/work/active/G1_CANDIDATE_R1_DIRECTION_LAP333.md 부록 A에 SHA와 함께 소비·보존했다.
이번 상위 결정은 후보 R1 관측 우선이며 현재 실행 예산은 0회다. 마일스톤 종료/이동 없음.

승격 사유: 후보 식별·좌표 변환·PS35 적용 가능성 및 원본 전용 검사 분리가 실행 가능한 근거로 아직 확정되지 않았다.
승격 작업자는 위 문서 §2~3의 후보 SHA/로딩 증거·좌표·읽기·실패모드·원본/후보 artifact 분리·cleanup을
한 봉투로 구체화하고 ACCEPT/BLOCKED를 판정하라. W3 재pin/원본 재클릭/예산 확대는 불허다.
ACCEPT 뒤 work 구현/검사와 다음 새 middle 독립 검수를 거쳐서만 후보 1 fresh run이 발효한다.
필수 검사 실패나 근거 충돌이면 재시도 없이 보존·반환하라. 세부 검증 결과는 lap333 history를 따른다.
사용자 지시의 Sol 승격과 MODEL_ROUTING의 Opus5 선택은 runner가 실제 모델을 기록하며 처리하고 몰래 대체하지 않는다.

## 필수 문서 검사 실패 — 즉시 중단
STATUS 편집안 사전 줄 수 assert가 131>130으로 실패했다. 디스크 쓰기 전이라 기존 STATUS 130줄은 보존되었다.
후속 context_limits.py의 CONTEXT_PASS는 저장되지 않은 편집안을 검증한 결과가 아니며 이 실패를 상쇄하지 않는다.
실패 뒤 확장/검증 재시도 없이 STATUS의 현재 인계 문장만 바꾸고 상세 실패를 lap333 기록에 보존했다.
승격 작업자는 STATUS 최종 현물의 줄 수·블로커 섹션·미결 보존 및 방향 문서의 실행 게이트를 먼저 검수하라.
```

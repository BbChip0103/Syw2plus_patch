# lap199 middle — 새 사용자 승인 확인, STOP 해제, R5 계약 발행

- 날짜: 2026-09-12 01:57~02:05 KST
- lap: 199
- 역할: middle tier (진단·계획·확인). 실제 모델 Claude Code `claude-opus-5`/high.
  **구현하지 않았다. 게임을 실행하지 않았다.**
- 목표: lap198이 남긴 STOP(승인 대기)의 해소 여부를 판정하고, 해소됐다면
  Stage B 재개 전 사전 게이트를 걸고 R5 범위를 승인 문구대로 확정한다.

## 가설

lap198은 "승인 없이 가능한 안전 작업 큐가 비었다 → STOP"으로 끝났다.
가설: `docs/feedback/APPROVALS.md`의 현재 본문이 lap190~198이 인용한 승인 범위
("원본1회+후보1회, 원본 1회 소진")와 다르며, 그렇다면 STOP 전제가 이미 낡았다.

## 판정 1 — 새 사용자 승인이 존재한다 (STOP 해제)

파일 mtime 증거(모두 동일 파일시스템, `--time-style=full-iso`):

| 파일 | mtime |
|---|---|
| `docs/STATUS.md` (lap198 작성) | 2026-09-12 01:55:10 |
| `loop/ESCALATE_SOL` (lap198 작성) | 2026-09-12 01:55:23 |
| lap198 세션 종료 작업 `.omc/state/session-end-jobs/...` | 2026-09-12 01:56:11 |
| **`docs/feedback/APPROVALS.md`** | **2026-09-12 01:56:57** |
| `loop/.lap_counter` → `199` | 2026-09-12 01:57:07 |
| lap199 세션 시작 | 2026-09-12 01:57:08 |

APPROVALS.md는 **lap198 세션이 끝난 뒤, lap199가 시작되기 전**에 수정됐다.
lap198의 ESCALATE_SOL은 자신이 바꾼 파일을 "docs/STATUS.md, lap 기록, 카드, this file"로
명시했고 APPROVALS.md는 거기에 없다. 따라서 이 수정은 **모델 lap의 산출물이 아니라
사람의 편집**이다. `docs/`는 git 미추적이라 diff 이력은 없으며, 이 귀속은 mtime 순서와
lap198의 자기신고 변경목록에 근거한 **추론**임을 명시한다.

현재 본문(해시 `4b67e172056422f5...`)의 「실행 승인 (사람 판정)」:

> 2026-09-12 01:03 KST — 사용자가 "승인. 루프 계속 돌아"라고 명시했다.
> 승인 범위는 G1 카드2 Stage B의 격리된 원본/1600×1200 후보 실제 비교를 **증거가 성립할
> 때까지 bounded repair → fresh validation으로 계속하는 것**과 그 독립 검수다. 실패를 보존하지
> 않는 무변경 blind retry는 금지하며, 각 수리 뒤 검증 run은 handoff의 exact-once/fresh 규칙을
> 지킨다. **R5처럼 Stage B가 무엇을 증명하는지 조이는 변경은 포함한다.** 제품 G1 합격·출시 승인,
> P6 착수, G2~G4 승인은 포함하지 않는다.

날짜 stamp는 01:03 그대로다. 즉 사람이 **새 승인을 추가한 것이 아니라 기존 01:03 승인의
범위를 다시 적어 명확히 했다.** 어느 쪽이든 현재 문면이 사람의 최신 판정이며 다음 둘을
직접 뒤집는다:

1. **"원본 1회 소진 → 재실행 새 승인 필요"** → 실제 범위는 회차 상한이 아니라
   *증거가 성립할 때까지 bounded repair → fresh validation 반복*이다.
2. **"R5는 사용자 승인 경계"** → R5류(조이는 방향)는 **승인에 포함**된다.

따라서 lap191·193·196·198이 8바퀴 동안 이월한 "사용자 승인 필요" 블로커는 **해소됐다.**
lap190~198의 기록은 그 시점 문면 기준으로는 정당했으므로 결함으로 적지 않는다.

경계는 그대로다: 제품 G1 합격/출시, P6 착수, G2~G4는 **여전히 미승인**이다.

## 판정 2 — Stage B 재개 전 사전 게이트 (이번 바퀴 실측)

STATUS의 "승인이 오면 Stage B 재실행 **전에** 사전 게이트를 먼저 건다"를 이번 바퀴에 집행했다.

| 게이트 | 명령 | 결과 |
|---|---|---|
| 원본 EXE 해시 | `sha256sum Syw2plus/syw2plus_original.exe` | `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` = `checks/safety.py:15` ORIGINAL_SHA **일치** |
| safety (게임 필수 모드) | `LOOP_DRY_RUN=0 bash checks/safety.sh check` (`--require-game`) | `SAFETY_PASS`, exit 0 |
| safety (기본) | `bash checks/safety.sh check` | `SAFETY_PASS`, exit 0 |
| Fast | `make check` | **213 passed**, Ruff/compileall/mypy(9 files)/`CONTEXT_PASS`, exit 0 |
| 도구 가용성 | `tools/check_setup.py --require-game` | `ok:true`, `original_status:"verified"`, wine/wineboot/wineserver/Xvfb/scrot/xwininfo/xdotool/mingw/make **전부 present**, `missing_tools:[] missing_libraries:[]` |
| fresh prefix/display | `local/runtime/` 구조 확인 | run마다 `<ts>_<pid>_0/{game,prefix,output,manifest.json}` 신규 생성. 최근 예: `20260912_010714_2914723_0` (lap190) |
| 디스크 예산 | `df -h .` / `du -sh` | free **277G**, run 1회 ≈ **2.7G** (`local/runtime` 누적 88G). 페어 run 1회 ≈ 5.4G → 여유 충분 |
| 입력 예산 | `tools/runtime_env.py:1982-1995` | `unit_select/drag_select/minimap` 각 10.0s, 합 30.0s ≤ `G1_INPUT_PHASE_WALL_CLOCK_BUDGET=31.5` **변경 없음** |

**사전 게이트 전부 PASS. Stage B 재개를 막는 환경/안전 사유는 없다.**

비블로킹 관측(결함 아님): `check_setup.py`의 `runtime.ok:false`는 고정 경로
`local/runtime/manifest.json`을 보는데 manifest는 run별 디렉터리에만 생성되기 때문이다.
상위 `ok`는 true이고 도구/원본은 전부 verified다. 보고 표현 문제이므로 카드 발행하지 않는다.

## 판정 3 — R5는 새 메모리 오프셋 없이 구현 가능하다 (계약의 근거)

R5는 "`unit_select`/`drag_select` 단언을 type 검증까지 조인다"이다. 실현 가능성을 현물로 확인했다.

- 현재 `_read_selection`(`tools/runtime_env.py:1338-1342`)은 `count`와 `first_slot`만 읽는다.
  그래서 PASS 술어가 `count>=1`(`:2346`) / `count>=2`(`:2438`)뿐이고 기대 문자열
  "owner0 HQ visible"(`:2355`,`:2367`) / "HQ and worker"(`:2438`,`:2451`)를 **증명하지 못한다**(H3).
- 그러나 slot→type 읽기는 **이미 구현돼 있고 문서화된 주소**다:
  `G1_UNIT_BASE_ADDRESS=0x0066B790`(`:181`), `G1_UNIT_STRIDE=0x758`(`:182`),
  `G1_UNIT_TYPE_OFFSET=0x8D`(`:183`) → `_read_g1_command_selection_identity`가
  `unit_address + 0x8D`를 BYTE로 읽어 `unit.type`을 만든다(`:1598-1610`).
  `analysis/memory_maps/player_offsets.md` lap57(:536)·lap61(:558)이 이 경로로 관측한
  type58/type70을 독립 확정했다.
- **결론: R5는 새 오프셋 추측이 필요 없다.** AGENTS.md의 "다른 버전 오프셋을 추측 적용하지
  않는다"와 카드의 "근거 없는 HQ type 목록 하드코딩 금지"를 둘 다 지킬 수 있다.

### R5 설계 결정 — 절대 type 술어가 아니라 **baseline 대비 parity**

R4가 확정한 대로 HQ type은 fixture/nation에 따라 49/58/70으로 달라지며 절대 판별식은 UNKNOWN이다.
그러므로 "type==49" 같은 in-run 절대 술어는 만들 수 없다(만들면 R4를 되돌리는 추측이다).
대신 Stage B의 원래 측정식이 이미 **비교**다("`selection_count` 델타 일치, `camera` 이동 결과 일치").
여기에 **선택된 slot/type의 일치**를 더하면, 같은 논리 좌표가 *같은 개체*를 잡았음을 증명한다 —
"같은 개수"보다 엄격하며, 어떤 type이 옳은지는 주장하지 않는다. 이것이 승인 문면의
"Stage B가 무엇을 증명하는지 조이는 변경"에 정확히 해당한다.

**중요: wait 술어/예산/timeout은 건드리지 않는다.** type은 *증거*로 기록하고, 판정은 비교
계층에서 한다. type 읽기가 실패하면 `UNKNOWN` + provenance로 남기고 그 차원은
**INCONCLUSIVE**다 — INCONCLUSIVE는 PASS가 아니다(fail-closed 유지). 정상 원본 분기를
FAIL로 올렸던 lap190의 실수를 반복하지 않기 위해, type 읽기 실패는 치명 오류가 아니다.

## 판정 4 — 비교기(comparator)가 존재하지 않는다

`tools/` 전체를 확인했다: `check_binary_contract.py`, `check_g1_presentation_trace.py`,
`check_runtime_evidence.py`, `check_setup.py`, `loop_context.py`, `runtime_env.py`,
`win32_*`, `x11_*`. **원본 evidence와 후보 evidence를 맞대어 Stage B 측정식을 계산하는
도구가 없다.** `check_g1_presentation_trace.py`는 단일 trace 검증기다.

즉 지금 Stage B를 돌리면 "델타 일치" 판정이 사람 눈대중이 된다. 이는 ⑥의
"모델의 exit0을 제품 완료로 쓰지 않는다"와 같은 종류의 구멍이다. 다만 evidence는
디스크에 보존되므로 비교기는 **run 이후에 소급 적용할 수 있다.** 따라서 비교기는
run을 막지 않는다(R5-B는 비블로킹).

## 변경 파일

`docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
`loop/ESCALATE_SOL`, 이 파일. **문서만 변경.**
source/tests/EXE/DLL/assets/baseline/golden 변경 0. 게임 run 0회. Stage B 0회. PNG 0장.
커밋 없음(`LOOP_ALLOW_COMMITS=0`).

검수 시점 해시(이번 바퀴 무변경 확인): `tools/runtime_env.py` `fd28e3a1aab1d4be...`,
`tests/test_runtime_env.py` `9082d1567b46a83e...` — lap198 기록과 동일.

## 다음 행동

R5-A(work) → middle 검수 + run 인가 → Stage B 페어 run(work) → R5-B 비교기.
상세는 카드의 「lap199 middle 판정」과 `loop/ESCALATE_SOL`.

## 미검증 (변동 없음)

G1 실제 원본/후보 입력 비교, WM_CLOSE teardown 결함, random seed 미노출,
minimap camera 절대 목적지, 2.5초 잘림 임계값(첫 실제 run이 재평가), G2~G4 제품 증거 전부.

# 2026-09-20 | lap 412 | G2 — lap411 W8 장시간 soak 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 코드 hands-on 수정 0, 게임 실행 0, 바이너리 변경 0, 커밋 0.
- 검수 대상: lap411 work 회차의 W8 판정(`PASS_W8_WITH_STRICT_CAP_CAVEAT`)과 그 원시 증거.
  기록 `docs/history/laps/20260920_lap411_work_g2_compat_long_soak.md`,
  카드 `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`.
- 원시 증거 경로:
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260920_lap411_compat_soak_retry2/`
- 이번 검수 산출물:
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260920_lap412_middle_review/`
  (`recompute_lap411.py`, `recompute_lap411.json`)

## 가설 / 검수 방법

가설: lap411의 `soak_summary.json` 수치가 원시 산출물에서 독립적으로 재유도되지 않거나,
카드 W8 §2의 PASS 조건 중 산출물이 뒷받침하지 않는 항목이 있다.

방법: `soak_summary.json`을 **믿지 않고** 원시 파일(`trace.jsonl` 732행, 10개 스냅샷 JSON,
`save_response.json`/`load_response.json`, `progress.json`, 디스크의 `save092.dat`)만으로
모든 수치를 재계산한 뒤, 마지막에 요약본과 필드 단위로 diff했다.
lap411이 **측정하지 않은** 필드(type/owner/hp/x/y/command/progress 일치, owner별 reserved 시계열,
used 분포)도 함께 계산해 새 결함을 찾았다.

## 재계산 결과 — 요약본과의 불일치 0건

`recompute_lap411.json`의 `summary_disagreement_count = 0`. 대조한 필드:

| 항목 | 재계산값 | 요약본 | 판정 |
|---|---|---|---|
| soak Δtick (presoak snap 145 → final snap 24325) | 24,180 | 24,180 | 일치 |
| PS3 trace 표본 | 728 (전체 레코드 732, ps∈{3,7,9,40}) | 728 | 일치 |
| 라이브 `used > 5000` 표본 | **0** / 5,824 owner-표본 | 0 | 일치 |
| owner별 max `used` | 4,990~5,000, cap 전 표본 5000 단일값 | 동일 | 일치 |
| `used+reserved > 5000` 표본 | **2,053** | 2,053 | 일치 |
| 스냅샷 10개 slot중복 / id중복 / owner손상 | 전부 **0** | 0 | 일치 |
| 스냅샷 10개 tick·units·slots≥1200 | 전건 일치 | — | 일치 |
| save/load lost / id mismatch / new | 0 / 0 / 0 (4,000 슬롯 대조) | 0/0/0 | 일치 |
| slot≥1200 사망→재사용 | **8건**, 슬롯 집합 동일 | 8 | 일치 |
| RSS 기울기 18.799 → 5.358 KiB/s, 감속 71.5%, 총 +8,776 KiB/727.3s | 동일 | 동일 | 일치 |

## 독립 확인한 provenance

- 원본 2경로 재해시 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**
  (`Syw2plus/syw2plus_original.exe`, `../Syw2plus_re/Syw2plus/syw2plus_original.exe`).
- 격리 run에서 **실제 실행된** exe = `local/runtime/20260920_223253_1458431_0/game/syw2plus_original.exe`
  = `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe` (핀된 marked compat 후보와 동일).
  같은 디렉터리의 `game.exe`는 stock `b56986e0…`이지만 `progress.json.session.exe`가 후보를 가리키고,
  slot 최대 4000·slot≥1200 2,801건 관측이 stock(1200) 불가이므로 **후보가 실행된 것이 맞다**.
- 배포 `_inmm.dll` = `bab1b72d71e1820251f8bcd902b3b52b461bc12094e9934a060feaf51e16c49c`,
  브리지 `unit_pool_base=0x0108C000` / `unit_existence_base=0x017B8658` (N=4001 전용, stock 재사용 아님).
- `save092.dat` **디스크 원본 재해시**: `9bfe52cf8f1c31c1828359e796fed2fa8dba3e560afba9b6916cc2c870c1efbe`,
  9,281,722 B, 마커 `S2P1N4K1` 파일 전체에서 **정확히 1회, 오프셋 `0x38`** — 요약본과 일치.
- 잔류: 우리 run의 pid 1460549 / display `:3128` 모두 없음(`/tmp/.X11-unix`에 `X3128` 부재).
  남아있는 Xvfb/게임 프로세스는 전부 `Syw2plus_re_loop` 등 **다른 저장소·다른 세션** 소유라 손대지 않았다.
- `checks/safety.sh check` → `SAFETY_PASS`.

## 신규 근거 1 — 로드 실재의 독립 채널 확인, 단 수치는 정정

lap411 기록은 "load tick 12,295→12,257 역행"을 로드 증거로 적었는데 그 값은
`load_response.json`(제어 브리지 **자기 보고**)에서 온 것이다. 카드 W8 §3이 요구한
"`trace.jsonl`의 tick 역행"을 별도 채널로 재계산하니 전체 732 레코드 중 tick 역행은
**단 1건, 12,273 → 12,269**였다. 방향은 같고 시점도 로드와 일치하나 크기가 다르다 —
trace 표본 간격이 약 33 tick이라 로드 직전 표본 12,273, 복원(12,257) 후 12 tick 진행한 12,269가
찍혔기 때문이다. **로드가 실제로 엔진 상태를 교체했다는 결론은 유지**되며, 제어 응답과 독립된
채널에서도 성립한다. 다만 향후 기록은 두 값을 구분해 적어야 한다.

## 신규 근거 2 — save/load 충실도는 lap411이 주장한 것보다 강하다

lap411은 슬롯 존재 여부와 `internal_id`만 대조했다. 이번에 presave(tick 12,252) 대 postload(tick 12,262)
**4,000 슬롯 전건**을 나머지 필드까지 대조했다:

- `type` 불일치 **0**, `owner` 불일치 **0**, `hp` 불일치 **0**, `internal_id` 불일치 **0**.
- `x,y` 불일치 165건 — 전부 맨해튼 거리 **1(62건) 또는 2(103건)**, 최대값도 2.
- `command` 변경 74건, `progress` 변경 1건.

두 스냅샷 사이에는 실제로 10 tick(presave→save 5 tick + 복원→postload 5 tick)이 흘렀으므로
"타일 1~2칸 이동 + 명령 상태 전이"는 **정상 시뮬레이션 진행과 정확히 부합**하고, 포인터 손상이나
좌표 깨짐의 징후(큰 점프, 범위 밖 좌표)는 0건이다. 즉 이 항목은 결함이 아니라 **보강 증거**다.

## 신규 근거 3 — `used+reserved=5010`은 "일시 초과"가 아니라 **해소되지 않는 예약**이다

되물음 원문은 "생산 완료 직전 한 tick 창", lap406 N19는 "수 분 지속"으로 정정했다.
이번 owner별 시계열 재계산으로 **기전이 확정**됐다:

- owner7: 728 표본 중 `reserved=10`이 **726 표본**. `reserved=10 AND used<5000`인 표본은 시딩 중
  tick 88·122 단 2건이고, tick 158부터 24,298까지(span 24,140 tick, 전 soak의 **99.45%**)
  `used=5000, reserved=10`으로 **고정**됐다. owner7의 유닛 `count`는 전 구간 500에서 변하지 않았다.
- owner3: `reserved=10`이 617 표본이나 그중 120 표본은 `used<5000`(예: `used=4990`)이라 합이 cap 이하다.
  초과는 `used`가 정확히 5000일 때만 발생했고, owner3은 사망으로 `used`가 내려가면 예약이 해소됐다
  (`reserved=0`이 111 표본).
- owner0/6: `reserved`가 전 구간 0, 초과 표본 0.

⇒ 이것은 오버슈트가 아니라 **비용 10짜리 생산 주문 1건이 큐에 걸린 상태**이고, `used`가 cap 아래로
내려가야만 해소된다. owner7은 24k tick 동안 유닛을 한 기도 잃지 않아 영원히 해소되지 않았다.
라이브 `used`는 5,824 owner-표본 전부에서 cap을 넘지 않았다(장부 무결성 유지).

되물음(가)/(나)에 대한 middle 의견: 선택지 문구 자체가 사실과 어긋난다. (가)는 "일시 초과 허용"이
아니라 **"cap에 붙은 owner가 대기 주문 1건을 무기한 보유하는 것을 허용"** 으로 다시 써야 한다.
관측 범위에서 이 상태의 해악은 0(크래시·손상·라이브 초과 전부 0)이다.
**단 원본 귀속은 여전히 미증명이다**(INBOX 미증명 귀속 항목 유효) — 이 soak도 stock 대조군을 돌리지
않았다. 값싼 결판 probe를 아래 「다음 한 가지」에 구체화했다.

## 신규 근거 4 — CPU 정체 없음(lap411이 측정하지 않은 축)

AGENTS.md는 "개체 제한/풀 손상/OOM/**CPU 정체**를 실제 증거로 구분한다"를 요구하는데 lap411은
CPU/처리율을 재지 않았다. `trace.jsonl`의 wall-clock과 tick을 함께 재계산했다:

- PS3 표본 728건의 wall 간격 중앙값 **1.00초**, 최대 **1.10초** (730.5초 구간). 1초를 크게 넘는
  구간이 0건이므로 **행(hang)·스톨 없음**이 표본 단위로 확인된다.
- tick 진행률 **33.2 tick/s**, 첫 1/3 **33.3** 대 마지막 1/3 **33.2** — 4,000 live 유닛에서
  24k tick 동안 **처리율 저하가 사실상 0**이다.
- 표본당 tick 증가가 0 이하인 경우는 **1건뿐이고 그것이 정확히 로드 지점**(12,273→12,269)이다.

⇒ "확장 풀이 시간이 지나며 느려진다"는 축은 이 구간에서 **음성**이다. 단 stock 대조군 처리율을
같이 재지 않았으므로 "시간에 따른 열화 없음"만 증명됐고 "stock 대비 느리지 않음"은 미증명이다.

## 신규 결함 N21 — W8 §4가 요구한 명시 문장이 산출물에 없다

카드 W8 §4는 "이 soak의 **어떤 결론도** `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c`
채널 산출물에 근거하지 않는다는 것을 **산출물에 명시**"하라고 요구했다. `soak_summary.json`·
`progress.json`·lap411 기록 어디에도 이 문장이 없고, lap410 정정2 자체가 언급되지 않았다.

실질 판정: **무해**. 이번 검수가 쓴 근거는 전부 `runtime_driver` 외부 스냅샷·`trace.jsonl`·
제어 응답·디스크 save 파일이며, 재배치 후보에서 0기로 보이는 stub 채널 산출물은 한 건도 쓰이지
않았다(해당 파일이 증거 디렉터리에 존재하지도 않는다). 따라서 REJECT 사유가 아니라 **문서 누락**이다.
§4의 선택적 20분 stub 주소 치환 작업도 수행/미수행 기록이 없다.

## 신규 결함 N22 — 전체 gate가 밀렸다(이번 lap에서 해소)

lap411 기록은 "동일 source에 대해 직전 784 full gate가 PASS였으므로 전체 suite는 반복하지 않았다"고
적었다. 그러나 lap411은 **스스로 source를 바꿨다** — `patches/population/runtime_driver.py`의
`control_goal_payload()`(`request_id`를 `str()`로 직렬화)와 신규 테스트
`tests/test_runtime_env.py::test_runtime_driver_control_goal_uses_protocol_string_request_id`.
카드 W8 §6과 INBOX 2026-09-20 21:58은 "**source를 바꿨을 때만** 통합 경계에서 `make check` 1회"이므로
lap411에는 전체 gate 1회가 **남아 있었고**, 면제 근거로 쓴 "동일 source" 전제가 틀렸다.

이번 lap이 그 통합 경계 gate를 대신 실행했다: `make check` **collected 785 items**
(784 + 신규 1, 수와 정확히 일치). 결과는 아래 「검증」에 적었다.

하네스 수리 자체는 유효함을 확인했다: `control_goal_payload`는 `runtime_driver.py:426`의 **실제 송신
경로**에서 호출되고(테스트 전용 헬퍼가 아님), 역주입(payload의 `request_id`를 `int`로 되돌림)으로
해당 테스트가 FAIL함을 확인했다 — 포착력 있는 앵커다.

## 신규 관찰 N23 — 이 soak은 풀을 100% 채운 채 돌았고 N=4001은 공학 시험값이다

- 시딩은 8 owner 전부 `fixture_exceeds_unreserved_supply`로 멈췄다. **풀 한계가 아니라 전비 cap이
  한계였다** — 비용 10 유닛 500기 × 8 owner = 4,000기.
- 풀 용량 4001(slot 0 예약, 사용 가능 1..4000)에 대해 tick 12,252·15,331에서 live가 **정확히 4,000**,
  final 스냅샷 `slot_max`도 4000이다. 즉 **여유 슬롯 0칸**으로 운전됐고 크래시는 없었다.
- 그러나 `docs/work/active/G2_STORAGE_LAYOUT_SONNET_HANDOFF_LAP381.md:72`는 "`4001/9601/9904`는
  **공학 테스트 값이며 최종 용량이 아니다**"라고, `docs/history/laps/20260917_g2_capacity_policy_middle.md:9`는
  "neutral/effect/non-rostered 할당과 pending production이 추가 공유 여유를 요구할 수 있으므로
  용량 적정성이 아니다"라고 이미 적어 두었다.
- ⇒ **풀 고갈 경로는 이번 soak에서 실행되지 않았다.** cap에 붙은 owner는 더 생산할 수 없어
  4,000을 넘는 할당 요청 자체가 발생하지 않았기 때문이다. "여유 0에서 정상 동작"은
  "여유 0에서 할당 요청이 와도 안전"과 다른 명제다. 최종 용량 결정 시 이 구분을 잃지 않아야 한다.

## 관찰 N24 — W8 soak 번들에는 재사용 가능한 오프라인 검증기가 없다

`patches/population/verify_g2_persistence_artifacts.py`를 이 번들에 돌리면
`frozen4000_sidecars.bin` 부재로 즉시 실패한다 — 그 검증기는 자칭 lap410/412 계보의 persistence
번들 스키마 전용이고, lap411 번들은 다른 스키마(`g2_compat_long_soak_summary_v1`)다. 결함은 아니지만
**W8 soak 산출물에는 기계 게이트가 하나도 없다**는 뜻이고, 이번 검수의 유일한 교차검증은 이 lap이
새로 쓴 `recompute_lap411.py`다. P4(반복·장기 soak)로 갈 때 이 스크립트를 재사용 가능한 형태로
승격하면 검수 비용이 내려간다 — **우선순위는 낮고, 이것 때문에 P2 실제 실행을 미루지 않는다**
(INBOX 2026-09-20 21:58).

## 항목별 판정 — W8 §2 PASS 조건

| 조건 | 판정 | 독립 근거 |
|---|---|---|
| (a) 크래시/행 0, 24k tick 완주 | **ACCEPT(강화)** | Δ24,180 ≥ 24,000, `driver_exit=0`, trace 연속 732 레코드, 잔류 0. 추가로 표본 wall 간격 최대 1.10초·처리율 33.2 tick/s가 전 구간 평탄(신규 근거 4) |
| (b) 라이브 `used` ≤ 5000 위반 0 | **ACCEPT** | 5,824 owner-표본 재계산, 위반 0. cap 값은 전 표본 5000 단일 |
| (c) 풀 무결성 | **ACCEPT** | 스냅샷 10개 전건 slot중복·id중복·owner손상 0 (직접 재계산) |
| (d) slot≥1200 사망→재사용 ≥1 | **ACCEPT** | 8건 독립 재유도, 슬롯 집합 일치, 8건 전부 final까지 동일 `new_internal_id`로 생존(예: slot 2066 → id 67602가 tick 24,009 owner1 AI 그룹 멤버로 실동작) |
| (e) RSS 비발산 | **조건부 ACCEPT** | 3점 수치 재계산 일치. 단 727초/3표본은 누수 부재 증명이 아니며, 후반 기울기 5.358 KiB/s를 외삽하면 **약 18.8 MiB/시간**이다. 카드 문구(3점+기울기)는 충족, 제품 판정으로는 부족 |
| (f) soak 중간 저장/로드 무손실 | **ACCEPT(강화)** | 4,000 슬롯 전건 id/type/owner/hp 일치, 좌표차는 10 tick 이동과 정합. presave→save 간격 **5 tick**(lap410 정정1의 535 tick에서 실제로 개선됨) |

**종합: lap411 W8 판정 ACCEPT.** `PASS_W8_WITH_STRICT_CAP_CAVEAT`를 유지한다.
정정 2건(로드 역행 수치의 출처, save/load 충실도 범위)과 신규 N21/N22/N23을 함께 남긴다.

## 검증

- `make check` rc **0** — **785 passed in 572.10s** (784 + lap411 신규 1, 수와 정확히 일치),
  `ruff check patches tools tests checks` All checks passed, `compileall` 통과,
  `mypy` 10개 대상 **Success: no issues found**, `checks/context_limits.py` → `CONTEXT_PASS`.
  로그 `/tmp/lap412_makecheck.log`. ⇒ **N22(밀린 통합 경계 gate) 해소, 실패 0건.**
- `checks/safety.sh check` → `SAFETY_PASS`.
- 원본 2경로 재해시 `b56986e0…08a8ac` **불변**(검수 전후).
- 독립 재계산 스크립트: `temp/.../20260920_lap412_middle_review/recompute_lap411.py`
  (원시만 읽고 요약본은 마지막 diff에만 사용, 불일치 0).
- 역주입 확인: `control_goal_payload`의 `request_id`를 `int`로 되돌리면 신규 테스트 단언이 깨진다.

## 변경 파일 / 커밋 (LOOP_ALLOW_COMMITS 미설정 = 0 → **uncommitted**, SHA256 앞 16자)

`LOOP_ALLOW_COMMITS`가 설정되지 않아 커밋·push **0건**. PROMPT ⑤대로 해시로 이력을 남긴다.
게임 코드·바이너리·핀·golden·baseline 변경 **0**(문서와 검수 스크립트만).

| 파일 | SHA256[0:16] |
|---|---|
| `docs/STATUS.md` (120줄) | `277f5552551b9207` |
| `docs/feedback/INBOX.md` | `7e049e0485f6f948` |
| `docs/history/laps/20260920_lap412_middle_g2_w8_soak_independent_review.md` | (이 파일) |
| `docs/history/laps/20260920_status_lap412_precompaction.md` (136줄 원문) | `fcfae74298ce8c62` |
| `docs/work/active/G2_ORIGINAL_PRODUCTION_PATH_LAP412.md` (W9 신규) | `2e2013c84d85e1c2` |
| `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md` (W8 CLOSED 헤더 추가) | `fe97a228c0eab2aa` |
| `temp/.../20260920_lap412_middle_review/recompute_lap411.py` | `1f36f1bc192d9b9a` |
| `temp/.../20260920_lap412_middle_review/recompute_lap411.json` | `03ef84b56850d08f` |

## 회귀 / 남은 위험 / 승인 상태

- 제품 완료 아님. G2는 여전히 **diagnostic seeding 의존**이다 — AGENTS "원본 명령을 우회한 성공은
  부족하다" 조항이 그대로 걸려 있다(P2).
- strict cap(P3)은 사용자 되물음 대기. 이번 lap이 기전을 확정했을 뿐 정책을 정하지 않았다.
- 장시간·반복 soak와 LAN(P4) 미검증. RSS 외삽 18.8 MiB/h는 P4에서 다시 본다.
- 풀 고갈 경로 미시험(N23). N=4001은 공학 시험값이며 최종 용량 결정이 아니다.
- F4(안전상한 UNKNOWN), G2 구조통합 blocker는 이 검수로 **변하지 않았다**.
- 사용자 마일스톤 승인 없음. 이 ACCEPT는 기술 컨펌이며 제품/출시 승인이 아니다.

## 다음 한 가지

**work(Sonnet5/high)가 P2에 착수한다** — diagnostic op=6 시딩을 **원본 생산/재생산 명령 경로**로
대체해 near-cap(8 owner × used 5000)에 도달·유지하고, 그 상태를 원본 명령만으로 재현한다.
strategy 큐(`G2_STRATEGY_DIRECTION_LAP404.md` D)와 lap411의 다음 지시가 모두 P2를 가리키므로
재계획 회차를 끼우지 않는다. 전체 suite는 source 변경 시 통합 경계 1회만 돈다.

**회차 예산 경고:** 이 lap412는 지정 역할(middle)대로 제품 코드·게임 실행이 0이다.
직전 lap411이 실제 실행을 냈으므로 PROMPT ③의 "제품 증거가 늘지 않는 회차 연속 최대 2회"는
이번이 1회차다. **따라서 다음 회차는 반드시 실제 실행(P2)이어야 하며, 계획·검수·하네스 정비 회차를
한 번 더 끼우면 strategy 판정 대상이 된다.** N21/N24는 P2를 미룰 사유가 아니다.

곁들여 **비용 0에 가까운 귀속 probe**를 P2와 같은 회차에 넣는다(별도 회차 금지):
stock 원본을 cap 5000으로 띄워 한 owner를 `used=5000`까지 채운 뒤 생산 주문 1건을 걸고
`reserved`를 관측한다. `used=5000, reserved=10`이 stock에서도 나오면 되물음 1의 "원본 고유 동작"
귀속이 **증명**되어 (가) 선택이 확정되고, 안 나오면 후보 고유 회귀로 승격해 P3를 앞당긴다.
INBOX 「미증명 귀속」 항목을 이 한 번의 관측으로 닫을 수 있다.

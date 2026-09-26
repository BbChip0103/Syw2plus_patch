# 2026-09-23 | lap 502 | G2 — AI 생산 정지 원인 읽기 전용 런타임 probe (lap501 §7 인계)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-sonnet-5` / high / **work**
  (실무 조사·실행, 게임 코드/AI 로직 변경 없음). 이 lap은 자기 결과를 최종 승인하지 않는다
  — 다음 middle의 독립 재검수가 필요하다.
- **가설 / 사용자 관찰:** lap501(middle) 정적 추적이 owner5 tick14,641 완전 정지를 설명할
  후보 게이트 6개(G-1 상태·G-3 플래그·G-5 AI활성·G-6 H-RATIO/H-TYPEMAX/H-AVAIL·G-7 H-CROWD)를
  특정했으나, 이 게이트들이 읽는 표(`0x9B5228`·`0x89A388`·`0xB3DE70`/`0xB3E000`)가 전부
  파일 밖(런타임 전용)이라 실제 값은 정적으로 알 수 없었다. 가설: 정지 tick 부근에서 이 값들을
  **읽기 전용으로** 관측하면, owner5가 만들 수 있는 (건물,kind) 쌍이 6개 분류(H-TYPEMAX/H-RATIO/
  H-AVAIL/H-CROWD/H-STATE/UNEXPLAINED) 중 어디로 떨어지는지 가릴 수 있다.
- **예상 PASS / FAIL 조건 (PREREGISTRATION.md, 데이터 개봉 전 고정):** 모든 쌍이 1~5로 분류되면
  원인 특정 PASS. 1개 이상 UNEXPLAINED가 남으면 "원인은 8게이트 밖" UNKNOWN. 같은 쌍이 tick마다
  분류가 바뀌면 UNSTABLE_CLASSIFICATION으로 별도 보고(억지로 하나를 고르지 않음).

## 이 lap이 발견/수행한 것 (중요: 게임 세션 실행 시각과 이 lap의 분석 시각이 다르다)

이 작업 디렉터리(`temp/Syw2plus_patch/g2_capacity/20260923_lap502_work_ai_production_stop_runtime_probe/`)는
이 세션이 열렸을 때 **이미 `verdict=PROBE_OK`로 완주된 상태**였다(`orchestrator.log`
04:40:12~04:49:24 KST, `run_summary.json`). 이 lap은 그 원시 산출물(`samples.jsonl` 511줄,
479개 raw sample + `owner5_probe.classifications` 74개 분류-보유 sample)을 **재실행하지 않고**
`PREREGISTRATION.md`의 판정식을 원시 데이터에 **처음으로 기계적으로 집계**해 검증 가능한 결론을
냈다. `run_summary.json`은 실행 성공(`PROBE_OK`=크래시 없음·STOP_TICK 도달)만 기록했을 뿐
6분류 집계·최종 판정은 이 lap 전까지 어디에도 없었다.

## 변경 파일 / source fingerprint / 커밋

- **제품 source 변경 0.** `tools/` `patches/` `tests/` `checks/` 무변경.
- 신규(제품 트리): 이 lap 기록 파일(본 파일) · `docs/STATUS.md` 갱신(+정밀압축) ·
  `docs/feedback/INBOX.md` 추기 · `loop/ESCALATE_SOL` §65 · 신규 precompaction 스냅샷
  `docs/history/20260923_status_lap502_precompaction.md`.
- 분석 스크립트(신규, 공유 temp, 제품 트리 밖):
  `temp/Syw2plus_patch/g2_capacity/20260923_lap502_work_ai_production_stop_runtime_probe/`
  아래 이미 존재하던 `lap502_probe_run.py`(704줄, SHA256
  `d248598dd576f092e3abb63328e70b028e2b138fe9d911c1f72430f9d0429ecd`)를 이 lap은 **읽기만
  했고 수정하지 않았다.** 이 lap이 새로 만든 것은 집계용 1회성 python 커맨드(제품 트리에 없음,
  파일로 저장하지 않았고 stdout만 이 기록에 옮김 — §"집계 방법" 참조)뿐이다.
- **커밋 0**(`LOOP_ALLOW_COMMITS` 미설정=0 기본, uncommitted 보존). 이 저장소는 현재
  `git log`에 커밋이 하나도 없는 상태(`## No commits yet on main`)이므로 "이전 커밋 대비 변경"
  개념 자체가 적용되지 않는다 — 파일 SHA256으로만 이력을 남긴다.

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

(전부 `fingerprint.json`/`run_summary.json`에서 읽은 값, 이 lap이 재확인만 함)

- 원본 `syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (`source_sha_before` == `source_sha_after`, `source_unchanged: true`).
- 후보(N=4001 persistence-compat, lap448/456/458과 **동일 계보**) SHA256
  `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68` — 현재 소스에서 재빌드
  후 SHA 확인, lap448 이후 재배치·fixup 로직 무변경 재확인.
  브리지 DLL(진단·probe 채널, `SYW2_SUPPLY_PROBE=1`) SHA256
  `d7e84831c86aa28b091ca21f6908112f875f33e92124f31979b2ef027f732808`,
  소스 `control_executor.c` SHA256 `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
  (실행 전/후 저장소 원본과 동일, `control_executor_c_unchanged: true`).
- 지도 140×140, seed 42, 활성 8인(owner0~7), goal `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`
  — **lap448/lap456/lap458 W22/W23 A1과 동일 fixture**(자연 도달 축, 시딩 없음).
- fixture: op7(자원만) 1회, rice=wood=1,000,000 전원 적용. **op4/op5/op6(장부 조작/시딩) 0건.**
  `WriteProcessMemory` 호출 0건 — 모든 읽기는 `patches.population.runtime_driver.read`
  (`process_vm_readv`)만 사용.
- **N144(lap500) 제약 준수:** 이 fixture는 lap458과 동일 결정적 궤적이므로 "새 독립 run" 주장이
  아니다. `used`/`count` 구조적 대조로 재확인(아래).

## 실행 명령 / 로그 / 캡처 경로 및 해시

```
# 이 lap이 실행: 원시 데이터 재집계(신규 게임 실행 0)
python3 - samples.jsonl <<'PY'
  # per (building_kind, produce_kind) 쌍별 owner5_probe.classifications 74-sample 집계
PY
```
- 원시 산출물: `.../20260923_lap502_work_ai_production_stop_runtime_probe/`
  - `samples.jsonl` (511 lines, SHA256 `779031893700ed8dc6863ec210d7687041ed4e582dfe63f7a1eae6cfee0ae999`)
  - `PREREGISTRATION.md` (93 lines, SHA256 `710bd41467aed7ab4cf66d4bc89debe444fc274c34a78b937dc60a6decb3da7c`)
  - `run_summary.json` (SHA256 `6cc65b9ed863efab9b9a603e8219cbeef7ce1d7e7ae374d2321286ba5a88cbdd`)
  - `lap502_probe_run.py` (704 lines, SHA256 `d248598dd576f092e3abb63328e70b028e2b138fe9d911c1f72430f9d0429ecd`)
  - `orchestrator.log`, `stdout.log`, `stderr.log`(빌드 경고만, 오류 없음)
- 안전 검사(이 lap이 재확인): `bash checks/safety.sh check` → `SAFETY_PASS`.
  `python3 checks/context_limits.py check` → `CONTEXT_PASS`.
- **동일 source이므로 전체 784계열 `make check`는 재실행하지 않았다**(2026-09-20 21:58 규칙,
  이번 회차에 제품 source를 바꾸지 않았음을 명시) — `source_unchanged`/`control_executor_c_unchanged`
  플래그로 대체 확인.

## 집계 방법 (판정식은 PREREGISTRATION.md에 데이터 개봉 전 고정, 이 lap은 기계적으로만 적용)

`samples.jsonl` 511 샘플 중 `owner5_probe.classifications`가 채워진 74개(전부 tick∈[14590,17027],
사전 등록된 "정지 이후 관측 창"과 일치)를 모아 `(building_kind, produce_kind)` 쌍별로 74개 분류값을
전부 모았다. 쌍은 owner5가 실제 보유한 생산 건물 7채(kind 41/44/47/49/50/51/105) ×
`DAT_004EC514` 65 생산행 중 그 kind가 만들 수 있는 kind 전부 = **17쌍**.

## 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN)

**구조 대조(선행 확인):** owner5 `used`는 tick 14,624부터 마지막 샘플 tick 17,027까지 정확히
**1070으로 고정**(`count`는 79→80으로 1회만 변동, 생산이 아니라 연구/기타 경로로 추정 — 이 lap은
그 1건의 출처를 조사하지 않았다). 이는 lap458/459가 보고한 owner5 tick14,641 완전 정지(N82)와
**정합** — 같은 궤적을 관측했다는 구조적 증거.

**분류 집계(17쌍, 74-sample 안정성 포함):**

| building_kind | produce_kind | 74-sample 분류 | 비고 |
|---|---|---|---|
| 41 | 38 | H-TYPEMAX (안정) | |
| 41 | 27 | **UNSTABLE**(tick14590 1회 UNEXPLAINED→이후 73개 H-TYPEMAX) | 첫 표본 과도상태로 추정, 조사 안 함 |
| 41 | 26 | **UNEXPLAINED**(74/74) | cur=0, typemax_eff=5, ratio 0%≤30%, avail=1, crowd 미적용, 건물 dispatch OK |
| 44 | 11 | H-TYPEMAX (안정) | |
| 44 | 79 | **UNEXPLAINED**(74/74) | cur=0, typemax_eff=10, ratio 0%≤30% |
| 47 | 10 | H-TYPEMAX (안정) | |
| 47 | 80 | **UNEXPLAINED**(74/74) | |
| 49 | 7 | H-TYPEMAX (안정) | |
| 49 | 110 | H-TYPEMAX (안정) | |
| 49 | 94 | **UNEXPLAINED**(74/74) | |
| 50 | 2 | H-TYPEMAX (안정) | |
| 50 | 4 | H-TYPEMAX (안정) | |
| 50 | 76 | **UNEXPLAINED**(74/74) | |
| 51 | 77 | **UNEXPLAINED**(74/74) | cur=1, typemax_eff=10, ratio 1%≤30% |
| 51 | 78 | **UNEXPLAINED**(74/74) | |
| 51 | 96 | **UNEXPLAINED**(74/74) | |
| 105 | 95 | H-STATE (안정) | 건물 dispatch 조건 자체가 불성립 |

집계: **H-TYPEMAX 7 / H-STATE 1 / UNEXPLAINED 8(74/74 안정) / UNSTABLE 1**.

**사전 고정 판정 규칙 적용 결과 → 판정 = `UNKNOWN`(8게이트 밖 원인).**
17쌍 중 8쌍(47%)이 tick14,590~17,027 전 구간에서 6가지 거부 사유 중 어느 것에도 해당하지 않는데도
발주되지 않았다 — `cur`가 상한에 한참 못 미치고(0 또는 1, 상한 5~10) 비율도 여유가 크며(0~1% ≤ 상한
30%) 가용 플래그도 1이고 건물도 dispatch 가능(state==100, auto-respond 비트 set)인 채로 74개 표본
내내 아무 발주도 없었다. PREREGISTRATION §"검증 규칙"대로 **이 8쌍을 강제로 6개 사유 중 하나로
재분류하지 않고 UNEXPLAINED로 그대로 보고**한다.

**중요 한계(이 lap이 스스로 발견, 과대주장 방지용 — 다음 middle이 검증할 것):** lap501 §3의
`FUN_00406B00`은 매 dispatch마다 `FUN_00406C70(0)`을 **한 번 호출해 후보 kind 하나를 추첨**하고,
`FUN_0043E7F0`(G-6)은 **그 추첨된 한 kind만** 검증한다 — 이 probe가 추적한 6개 분류(H-TYPEMAX 등)는
**한 쌍이 이미 추첨된 뒤의 거부 사유만** 모델링하며, `FUN_00406C70` 자신의 추첨/후보 필터링 로직은
이 pre-registration이 다루지 않았다. 따라서 "UNEXPLAINED 8쌍"은 (a) 실제로 8게이트 밖의 새 거부
메커니즘이 있거나, (b) **단순히 74개 표본(20-tick 케이던스) 동안 추첨에서 한 번도 뽑히지 않았을
가능성**(추첨 로직 자체를 아직 읽지 않았으므로 배제할 수 없음)의 둘 중 하나이며 **이 lap은 (a)/(b)를
가르지 않는다.** PREREGISTRATION이 사전에 "재해석/억제 금지"를 명시했으므로 그대로 UNEXPLAINED로
보고하고, 원인 추정은 다음 tier로 넘긴다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 회귀: 없음(제품 source 무변경, `SAFETY_PASS`).
- 남은 위험: `FUN_00406C70` 추첨 로직 미해부 — 위 (a)/(b) 모호성이 그대로 남는다.
- **독립 검수 없음(work 자기 결과)** — 다음 새 세션(middle, Claude Code `claude-opus-5`/high)이
  `samples.jsonl` 원시에서 이 lap의 집계를 재계산해 ACCEPT/REJECT해야 2단이 선다.
- 사용자 승인: 해당 없음(읽기 전용 조사, (ㄴ) 승인 대상 아님 — lap501/사용자 04:14 지시와 동일 범위).
  (ㄴ) 착수·Q7-B 3단 마일스톤·(ㄱ)·(ㄷ)은 여전히 사용자 전권 대기, 이 lap은 손대지 않았다.

## 다음 한 가지

**middle 1회차:** 이 집계를 `samples.jsonl` 원시에서 독립 재계산(불일치 0 확인)하고, 8개
UNEXPLAINED 쌍의 (a)/(b) 모호성을 좁힐 다음 probe를 설계할지(= `FUN_00406C70` 추첨 로직의
정적 추적, 여전히 읽기 전용·(ㄴ) 불필요) 판단한다. 판단이 서면 work 카드로 인계하고, 서지 않으면
이 lap의 한계를 그대로 들고 사용자/strategy에 보고한다.

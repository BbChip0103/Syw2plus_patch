# lap714 (work) — G4 AI 생산 게이트 라이브 거부 사유 히스토그램

- 날짜: 2026-09-27
- lap: 714
- 역할: work (Claude Code Sonnet 5 / high)
- 지시: `docs/feedback/INBOX.md` 2026-09-27 13:45 운영자 방향("라이브로 어느 게이트가 owner1
  발주를 막는지 계측") — lap713이 H-CROWD 상수 7→14 후보로 무효과(`FALSIFIED`)를 확정한 뒤,
  추측으로 상수를 더 바꾸지 말고 실측하라는 지시.

## 목표

`analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`(lap501)가 정적으로
확정한 AI 생산 결정 경로(G-1~G-8, `FUN_00406770`→`FUN_00406B00`→`FUN_0043E7F0`/`FUN_00406C70`)
가운데, 어느 게이트가 실제로 lap712 seed1 자유대전 fixture에서 owner0/owner1의 유닛 생산을
막는지 라이브로 특정한다.

## 가설

lap712/713은 "owner1(nation2)이 자원을 쌓아두고 쓰지 않는다"를 전제로 H-CROWD(밀집 상한)를
의심했으나 무효과였다. 이번 lap의 가설: 8게이트 중 lap501이 "런타임에만 있어 정적으로 못
가린다"고 명시한 나머지 게이트(H-TYPEMAX/H-RATIO/H-AVAIL, 그리고 lap501 §7이 다루지 않은
`FUN_00406C70`의 선행조건/기술 게이트) 중 하나가 실제 거부 사유일 것이다.

## 방법 (읽기 전용, 새 breakpoint/EXE 패치 없음)

1. **생산표 레이아웃 신규 해독** (`tools/g4_ai_production_table.py`): lap501은 생산표
   `DAT_004EC514`의 위치·레코드 크기(18바이트)·종료 센티널만 확정하고 필드 레이아웃은
   미해독으로 남겼다. `FUN_00406C70`을 capstone으로 디스어셈블해 필드를 전부 역산했다:
   `+0x00` nation_mask, `+0x02` building_type, `+0x04` produce_kind(-1=연구행),
   `+0x06` research_kind(-1=생산행), `+0x08/+0x0A` prereq_count_kind/min, `+0x0C`/`+0x0E`
   prereq_own_kind_a/b(둘 다 "소유 개수>=1" 검사, 같은 테이블), `+0x10` tech_kind. 원본 EXE
   바이트에서 직접 파싱해 143행(생산65+연구78, 건물타입27종)을 얻었고 lap501의 수치와
   정확히 일치했다(교차검증). 이 모듈은 게임을 실행하지 않는다.
2. **게이트 분류기** (`tools/g4_ai_gate_histogram_probe.py`): `FUN_00406C70`→`FUN_0043E7F0`→
   `FUN_00406B00` 크라우드체크 순서를 그대로 따르는 순수 함수 `classify_candidate`가, 이미
   읽은 테이블 값(있으면)으로 각 (건물, 생산레코드) 쌍을 정확히 하나의 사유로 분류한다:
   `NATION_MISMATCH`/`PREREQ_COUNT`/`PREREQ_OWN`/`TECH_NOT_RESEARCHED`/`HERO_COOLDOWN`/
   `HERO_CAP`/`H_AVAIL`/`H_TYPEMAX`/`H_RATIO`/`H_CROWD`/`WOULD_ACCEPT`. 라이브 값은
   `patches.population.runtime_driver.read`(기존 `process_vm_readv` 기반, 이 저장소의 모든
   probe가 쓰는 것과 동일 API)로 읽는다 — 새 detour/breakpoint를 EXE에 심지 않는다. 정적
   테이블(타입 스펙, 시나리오 override, 기술 정의)은 런 시작에 1회 캐시하고, tick마다 변하는
   테이블(보유 개수, 총 유닛 수, 선행조건/기술 완료 여부)만 매 표본 재읽음.
3. **오케스트레이션**: `tools/g4_ai_behavior_probe.py`(lap712)와 같은 방식으로
   `tools/runtime_env.py prepare`+`g1-baseline --g4-chain-goal _custom_game_chain_inject_seed1
   --g4-sample-seconds 280`을 실행하되, `g1-baseline`은 자신의 pid로 직접 게이트 테이블을
   읽을 수 없으므로(그 프로세스 밖에서 도는 별도 파이썬 프로세스), `g1-baseline`을 서브프로세스로
   백그라운드 실행한 뒤 `/proc/*/cmdline`에서 격리 사본 경로로 실제 게임 프로세스 pid를 찾아
   **같은 pid에 대해 병렬로 읽기만** 한다(그 프로세스에 쓰기/주입 없음). `g1-baseline` 자신의
   `g4_ai_smoke` 샘플링과 이 히스토그램 샘플링은 서로 간섭하지 않는 두 개의 순수 읽기 클라이언트다.

## 실행

- Fixture: lap712와 동일 `_custom_game_chain_inject_seed1`(owner0=nation1 HQ type49/worker7,
  owner1=nation2 HQ type58/worker31), 원본 `syw2plus_original.exe`
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전/후 3회 확인
  전부 `source_unchanged=true`).
- run1(스모크, `--sample-seconds 20`): 18 표본, 코드 경로 확인용. 결과: owner0
  H_AVAIL=26/PREREQ_OWN=13, owner1 PREREQ_OWN=26/H_AVAIL=26 — 조기 확인 성공.
- run2(전체, `--sample-seconds 280`, by_record 이전 버전): 278 표본. owner0
  PREREQ_OWN=403/H_AVAIL=776, owner1 PREREQ_OWN=696/H_AVAIL=623, 나머지 전부 0.
- `by_record`(레코드별 집계) 추가 후 run3(전체 280초 재실행, 동일 fixture): 278 표본.
  owner0 PREREQ_OWN=398/H_AVAIL=772, owner1 PREREQ_OWN=692/H_AVAIL=620(run2와 <2% 오차,
  같은 결정적 fixture의 재현 범위) — **아래 by_record 상세**.

## 결과

owner0(HQ type49, 이후 type50/51도 건설):

| building_type | produce_kind | reason | count(278중) |
|---|---|---|---|
| 49 | 7 | H_AVAIL | 274 |
| 49 | 94 | PREREQ_OWN | 274 |
| 49 | 110 | H_AVAIL | 274 |
| 50 | 2 | H_AVAIL | 112 |
| 50 | 4 | H_AVAIL | 112 |
| 50 | 76 | PREREQ_OWN | 112 |
| 51 | 78 | PREREQ_OWN | 4 |
| 51 | 77 | PREREQ_OWN | 4 |
| 51 | 96 | PREREQ_OWN | 4 |

owner1(HQ type58, 이후 type60도 건설):

| building_type | produce_kind | reason | count(278중) |
|---|---|---|---|
| 58 | 31 | H_AVAIL | 274 |
| 58 | 75 | H_AVAIL | 274 |
| 58 | 102 | PREREQ_OWN | 274 |
| 58 | 98 | PREREQ_OWN | 274 |
| 60 | 3 | H_AVAIL | 72 |
| 60 | 12 | PREREQ_OWN | 72 |
| 60 | 83 | PREREQ_OWN | 72 |

**모든 (건물, 레코드) 쌍이 280초 내내 정확히 100% 거부된다.** `NATION_MISMATCH`·
`PREREQ_COUNT`·`TECH_NOT_RESEARCHED`·`HERO_COOLDOWN`·`HERO_CAP`·`H_TYPEMAX`·`H_RATIO`·
`H_CROWD`·`WOULD_ACCEPT`는 owner0/owner1 어느 쪽도 단 1회도 나오지 않았다.

## 판정

**FEASIBLE(측정 완료, 원인 특정) — 그러나 lap712/713이 전제한 "owner1 전용 약점"은 성립하지
않는다.** owner0와 owner1 모두, 초기 HQ와 이후 지은 모든 건물에서, 생산 가능한 모든 레코드가
`H_AVAIL`(시나리오 가용 플래그 `0x00B3E000`=0) 또는 `PREREQ_OWN`(선행 유닛 미보유, 테이블
`0x009598CC`) 둘 중 하나로 100% 막힌다. H-TYPEMAX/H-RATIO(런타임 표라 lap501이 정적으로
못 가렸던 것)와 H-CROWD(lap713이 시험한 것)는 이 fixture에서 관측 가능한 역할이 전혀 없다.

owner0(생산 21·군대 16)가 owner1(생산 12·군대 10)보다 나은 것은 이 두 게이트를 더 잘
피해서가 아니라(둘 다 100% 막힘), owner0가 더 많은 건물 종류(type49/50/51 3종)를 짓고
owner1은 2종(type58/60)만 지어서 "막힌 레코드 수"만 더 늘어난 것으로 보인다 — 실제 생산은
이 `FUN_00406B00` 경로가 아닌 다른 경로(관측되지 않은 별도 issuer, 또는 초기 부여분)에서
나왔을 가능성이 있다. 이 lap은 그 경로를 추적하지 않았다(범위 밖).

## 안전/범위

- 제품 EXE/원본 미변경. 새 breakpoint·detour·패치 없음 — 순수 `process_vm_readv` 읽기.
- 원본 SHA256 3회(스모크1+전체2) 전부 `source_unchanged=true`.
- 격리 사본/전용 Xvfb display만 사용, 게임 프로세스에 대한 쓰기 없음(읽기 전용 두 번째
  파이썬 프로세스가 같은 pid를 병렬로 읽음).
- `run_one()`이 종료 시 격리 game 사본(`game_root`)을 삭제(디스크 위생), output/manifest/log는
  `local/runtime/g4-lap714-*`와 공유 temp
  `temp/Syw2plus_patch/g4_ai/20260927_lap714_g4_gate_histogram/`에 보존.

## 검증

- `make check` **1079 passed(835.61s)**, ruff/mypy/`compileall`/`checks/context_limits.py`
  (`CONTEXT_PASS`) 전부 PASS.
- `checks/safety.sh check` → `SAFETY_PASS`.
- 신규 테스트 18개: `tests/test_g4_ai_production_table.py`(5, 실제 원본 EXE로 143/65/78/27종
  재확인 + synthetic 레코드 디코드 2건) + `tests/test_g4_ai_gate_histogram_probe.py`(13,
  `classify_candidate`의 모든 분기 synthetic pin + 주소 상수 lap501 대조 1건).
- 원본 SHA 3회 `source_unchanged=true`, cleanup(`game_root` 삭제) 매 실행 확인, 후보 EXE 없음
  (이 lap은 candidate를 만들지 않았다 — 순수 계측).

## 산출물

- `tools/g4_ai_production_table.py`(신규), `tools/g4_ai_gate_histogram_probe.py`(신규)
- `tests/test_g4_ai_production_table.py`(신규), `tests/test_g4_ai_gate_histogram_probe.py`(신규)
- 원시 결과 JSON: 공유 temp
  `temp/Syw2plus_patch/g4_ai/20260927_lap714_g4_gate_histogram/probe-result-run{1,3}*.json`

## 다음 work (운영자 2026-09-27 14:45 방향으로 대체)

이 lap이 마감한 시점에 운영자가 위 결과를 반영해 STATUS/INBOX/APPROVALS에 직접 다음 방향을
적었다: 병목은 유닛 발주 게이트가 아니라 **AI가 선행 건물을 짓지 않는 것**이므로, v2는 AI
건설 결정 루틴에 같은 방법(라이브 거부 사유 히스토그램)을 적용해 owner1이 선행 건물을 못
짓는 최다 사유를 찾고, 그 사유를 완화한 후보로 원본 N=3 대 v2 N=3 paired 비교를 한다. 상세는
`docs/STATUS.md` "다음 한 가지"와 `docs/feedback/INBOX.md`/`APPROVALS.md` 2026-09-27 14:45
항목 원문.

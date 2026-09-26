# 2026-09-20 | lap 406 | middle (Claude Code claude-opus-5/high) — 자칭 lap410/412 런타임 계보 독립 검수

## 목표

`docs/work/active/G2_STRATEGY_DIRECTION_LAP404.md` §C의 수용 기준 1~6에 따라 자칭
lap410/412 계보(전면 재배치 N=1250/4001, 8인 전비5000 24k/144k soak, 확장 save/load
왕복, `S2P1N4K1` 마커 호환 경로)를 2단 독립 검수한다. 컨펌 역할이므로 게임 코드는
고치지 않는다. 게임 실행은 이 검수의 필수가 아니다(정적 + 보존 산출물 재검증).

## 가설 / 측정식

- H: 기록된 후보 SHA 4건이 **현재 소스에서 재생성되어 byte-equal**이고, 재배치 블록이
  PE 섹션에 100% 매핑되며, 수리 2건이 원본 바이트에서 재유도되고, 기록된 런타임 산출물이
  디스크 원본과 해시 일치한다.
- 측정식: 후보 SHA 일치 4/4, 미매핑 바이트 0, fixup 창 겹침 0, 산출물 해시 불일치 0,
  오프라인 검증기 rc0 + `ok:true`.

## 변경 파일

- 신규 read-only probe `docs/history/laps/probes/20260920_lap406_middle_g2_full_capacity_runtime_review_probe.py`
- 본 기록, `docs/STATUS.md`, `docs/feedback/INBOX.md`(되물음 1 정정 추기 — 원문 보존),
  `docs/work/active/G2_FULL_CAPACITY_COVERAGE_GATE_LAP406.md`(신규 work 카드)
- **제품 코드/바이너리/게임 실행/메모리 쓰기/커밋 0.**

## 실행 명령

```
PYTHONPATH=. python3 docs/history/laps/probes/20260920_lap406_middle_g2_full_capacity_runtime_review_probe.py
PYTHONPATH=. python3 -m patches.population.verify_g2_persistence_artifacts \
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260920_n4001_persistence_sidecar/runtime_20260920_174739
make check ; bash checks/safety.sh check
```

probe **rc0, `failures=[]`**, notes 2건(아래 N19/G-c 항목).

## 항목별 판정

### C1 원본/게이트 — ACCEPT

- 원본 2경로 재해시 **불변**: `Syw2plus/syw2plus_original.exe`,
  `../Syw2plus/syw2plus_original.exe` 모두 `b56986e0…08a8ac`(세션 시작·종료 양쪽).
- `make check` **rc0, 779 passed**(lap402 739 → +40) 485.17s, Ruff/compileall/mypy 10 파일
  Success, `CONTEXT_PASS`. `checks/safety.sh check` **`SAFETY_PASS`**.

### C2 후보 재현 — ACCEPT (단서 1건, 결함 아님)

현재 소스에서 메모리 상으로 재빌드한 4건이 기록 SHA와 **전부 byte-equal**:

| 후보 | 재생성 SHA | 판정 |
| --- | --- | --- |
| N=1250 + supply5000 | `c3bd799fefd31ffb8d02ed7e1d08bb734890c7e637c7eb3ffe4dc236004df5d3` | 일치 |
| N=4001 + supply5000 + owner1200 | `20b95a94711590e1bd41559ce76a9de6e40c155948f8d559b1090909fc342794` | 일치 |
| persistence sidecar N=4001 | `1e90f62fdcecb49d47d85af54bef17744bb7ae9d895a43b1923fd59405a30093` | 일치 |
| persistence compat N=4001 | `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe` | 일치 |

**N=1200 항등:** 재배치 단계(`g2_full_unit_capacity_v1`)는 원본과 **완전 byte-identical**
이고 내부 `capacity_report.candidate_sha256 == original_sha256`, `applied_fixup_counts`
전 영역 0, `category_slot_list_b` 사이트 수가 10→**9**로 줄어 self_count 수리가 N=1200에
새지 않음이 함께 확인된다.

**단서(결함 아님):** 두 persistence 모듈은 N=1200에서 원본과 **7바이트 다르다**(3 run:
파일 오프셋 `0x0001B56E`/2B, `0x0001B579`/2B, `0x0003FFD4`/3B). 디스어셈블 재유도 결과
전부 용량과 무관한 **의도된 상수 편집**이다 — `mov edx,0xFA`→`0x4B0`(owner 250→1200),
`mov word ptr [eax],0x5DC`→`0x1388`(1500→5000), `add eax,0x5DC`→`mov eax,0x1388`.
두 후보는 N=1200에서 supply5000+owner1200 제품 후보와 **정확히 동일**하고 wrapper/헤더를
설치하지 않는다(`compatibility_header: False`). 즉 재배치 항등은 유지된다. 다만 이
불변식을 강제하는 pytest 앵커는 없다(C3 카드에 포함).

### C3 커버리지 게이트(lap402 G-c) — 측정 ACCEPT, 게이트 부족 → work 지시

probe가 네 후보를 실제로 빌드해 각 섹션 `[VA, VA+VirtualSize)` 합집합 대비 재배치 블록
전 바이트를 측정:

| 후보 | 블록 | 블록 크기 | 섹션 밖 바이트 |
| --- | --- | ---: | ---: |
| N=1250 + supply5000 | `0x0108C000`–`0x012CE012` | 2,367,506 | **0** |
| N=4001 제품 후보 | `0x0108C000`–`0x017C612C` | 7,577,900 | **0** |
| persistence sidecar N=4001 | 동일 | 7,577,900 | **0** |
| persistence compat N=4001 | 동일 | 7,577,900 | **0** |

lap402가 REJECT 사유로 삼았던 D1(99.24% 미매핑)은 **해소됐다**. 그러나 pytest 앵커
`test_n1250_data_section_covers_every_relocated_region`은 **N=1250만** 강제하고
**실제 제품 용량 N=4001에는 앵커가 없다**. 카드 §C-3의 "없으면 REJECT가 아니라 게이트
추가를 work에 지시한다"에 따라 REJECT하지 않고 카드
`G2_FULL_CAPACITY_COVERAGE_GATE_LAP406.md`로 인계한다.

### C4 런타임 산출물 재검증 — ACCEPT

- 기록된 산출물 **20/20 해시 일치**(불일치 0, 부재 0). lap410/412가 인용한 경로는 실제로
  타임스탬프 하위 디렉토리(`runtime_*/`)에 있으며 basename 탐색으로 전건 확인했다.
  포함: `n4001_integrity_soak(.jsonl/_summary.json)`, `n4001_integrity_144k_extension*`,
  `postload_integrity_soak*`, `active_integrity_soak*`, `persistence_roundtrip_summary`,
  `frozen4000_verification/snapshot`, `legacy_fallback_verification`, `legacy_smoke`,
  `compat_new_format_verification`, 그리고 **거부된** 실험1/2 증거 4건.
- 오프라인 검증기 재실행 **rc0 / `ok:true`**: capacity 4001, live 3993, existence=catB=
  active=active_unique=3993, missing/unexpected 0, save 9,268,562 B, sidecar 오프셋
  1,704,974, `sidecar_sha256 == serialized_sha256 == 163da098…4ebab2`(기록과 일치).
- **요약을 믿지 않고 원시 jsonl에서 무결성 판정을 독립 재계산**(총 1,146 표본):
  네 soak 전부 **무결성 위반 0** (active_exact 거짓 0, existence≠active 0, 중복 0,
  catB≠existence 0, missing/unexpected 0). 24k=144표본/tick 2261→26337,
  144k 연장=714표본/tick 27541→147693, postload=144표본/tick 3646→27731,
  N=1250 catB 수리본=144표본/tick 1380→25407(최대 live 1249).

### C5 수리 2건 바이트 재유도 — ACCEPT

**(1) `active_base - 2` 별칭 2건.** 원본에서 직접 디코드:

- `0x00443075` : `mov cx, word ptr [ecx*2 + 0x974fa6]` (8B)
- `0x0044308C` : `mov word ptr [ecx*2 + 0x974fa6], bx` (8B)

두 사이트 모두 메모리 피연산자 변위가 정확히 `0x00974FA6`이고, 명령 자신의 길이 안에서
그 4바이트 인코딩이 **유일**(위치 4). N=1250 후보에서 `4ad62c01` = `0x012CD64A` =
재배치 active 배열 시작 −2로 패치됨(기대값 일치). 적용된 fixup 새 값 중
`[0x974FA4, 0x974FA8)`(무관 스칼라)을 가리키는 것 **0건** — "이웃 DWORD는 건드리지 않는다"는
주장이 바이트로 확인된다.

**(2) `0x004A3692` category-B self-count.** 원본에서 `mov bp, word ptr [ecx + 0x9eb8]`
(7B). `ecx = 0x00892410`(bulk base)이므로 실제 대상은 `0x0089C2C8`이고, 이는
category **A**의 count WORD(`0x0089B008 + 4×1200`)와 **정확히 일치**한다 —
`FUN_004A3690`이 B를 탐색/스왑/감소시키면서 A의 count를 읽는다는 주장은 사실이다
(B 배열은 바로 2B 뒤 `0x0089C2CA`에서 시작). 확장 레이아웃에서만 B 자신의 재배치 count로
바뀌고, **N=1200에서는 인벤토리에서 제외**되어(`present_at_n1200: false`) 항등이 유지된다.

**비중첩:** N=1250에서 적용되는 fixup 창 **1,348개 × 4B = 5,392개 서로 다른 바이트**,
겹침 **0건**. 모든 사이트에서 old 값 인코딩이 명령 길이 안에서 유일.

### C6 종합 판정

**항목 1·2·4·5 ACCEPT. 항목 3은 측정 PASS·게이트 부족(REJECT 아님, work 인계).**
카드 §F의 "2/4/5 중 하나라도 REJECT면 D 큐 동결" 조건에 **해당하지 않으므로 D 큐는
동결하지 않는다.** 단 §C-6대로 **제품 완료 선언은 금지**한다.

## 신규 결함 — N19 (되물음 1의 사실관계 오류, 승격 금지 사유 아님)

INBOX 되물음 1(lap404 작성)은 전비 초과를 "생산 완료 직전 **한 tick 창**에서
`used+reserved=5010` 같은 일시 pending 초과"로 기술한다. 144k 연장 로그를 owner별로
재계산한 실측은 다르다:

- 초과 owner-표본 **216건**, 값은 **전부 정확히 `used=5000, reserved=10`**.
- owner 6: tick **33917 → 50130**(16,213 tick, 97 표본).
- owner 5: tick **101643 → 121547**(19,904 tick, 119 표본).
- 살아있는 `used`가 cap을 넘은 표본은 전 soak 통틀어 **0건** — lap412의 "live used ≤5000"
  주장 자체는 참이다.

즉 "한 tick"이 아니라 **owner당 16k~20k tick(각각 약 490초·600초) 지속**이다. 사용자가
(가)"일시 초과 허용, live used만 강제"를 고르면 실제로는 UI/장부 총합 5010이 **수 분간**
표시되는 것을 허용하게 된다. 이 수치 차이는 되물음의 답을 바꿀 수 있으므로 원문을 고치지
않고 INBOX에 정정을 **추기**했다.

**부가:** lap412는 이 상태를 "stock 1200-slot control history에 이미 포착된 같은 부류라
재배치 풀 탓이 아니다"라고 귀속한다. 이 귀속을 뒷받침하는 산출물은 이 계보에 **없다** —
같은 계보의 stock 대조군(`20260920_stock1199_control`)은 cap 1500에 max used 40,
`used+reserved>cap` 표본 **0건**이라 애초에 cap 근처에 가지 않았다. 파일로 남은 유일한
stock 초과 증거는 2026-09-17 `stock_cap_overshoot_audit_v1`의 **owner1 live `used`=5003
(7표본, 원인 UNKNOWN, 소유권 이전이 유력)** 이며 이는 pending reservation과 **다른
현상**이다. 따라서 "선재 결함이라 재배치 탓이 아니다"는 **미증명 귀속**으로 남긴다
(수치 자체는 무효화되지 않는다). STATUS의 owner1 USED5003 계보(lap389 정적 원인확정)와도
혼동하지 않는다.

## 미검증으로 남는 것 (제품 완료 아님)

1. **이번 검수는 게임을 실행하지 않았다.** 런타임 주장은 보존 산출물의 해시 동일성과
   그 내용 재계산으로만 확인했고, 재실행 재현은 아니다.
2. diagnostic bridge seeding 의존(카드 §D P2) — 원본 생산/재생산 명령 경로 커버리지 미대체.
3. marked compat 경로의 near-4000 반복(§D P1) 미실행 — 382 유닛 규모만 통과.
4. LAN 직렬화/결정론(§D P4) 미검증.
5. strict cap 판정(§D P3) — 되물음 2건 답변 대기, N19로 되물음 1의 전제 수치가 정정됨.
6. N=4001 커버리지 pytest 앵커 및 persistence 합성의 N=1200 항등 앵커 부재(work 카드).
7. 자칭 lap 번호 불일치(N18, lap404)는 그대로 미해결 — 두 기록의 번호는 고쳐 쓰지 않았다.

## 파일 해시 (LOOP_ALLOW_COMMITS=0 — uncommitted 보존)

| 파일 | SHA256 |
| --- | --- |
| `docs/STATUS.md` | `af5b598973379e0b5d42eb52a8ddda3ed4e9e909f9a6a440b4c8067112d17ff5` (128줄) |
| `docs/feedback/INBOX.md` | `3db976aa95e62fb16f844850220d1c26b202fa95b235d2eaa3f72ca0caf8d2cc` |
| `docs/work/active/G2_FULL_CAPACITY_COVERAGE_GATE_LAP406.md` | `0edf9c40c7427517437fbd92017a42f65abdcb67f24bd441c0d77be2f21c4a15` |
| `loop/ESCALATE_SOL` | `baaf4bad161821e0cd6c66e3aac7f98e9881a292d4ed04084f140927e8c74f91` (§12 추기) |
| `docs/history/laps/20260920_status_lap406_precompaction.md` | `cd8696cd18b279bd1c2bb9d185238627b413249a623e66214d37d82018c7db73` (126줄, 압축 전 원문) |
| probe | `61822332e525bb9393743829c49cfed31a79f2204a34bc509a9f6d8afef629f3` |
| probe 산출물 `probes/out/20260920_lap406_middle_g2_full_capacity_runtime_review.json` | `481686e5bf0e1da5ed168166ee27002875bed73a4ea623ec8bda54b2783cb971` |

커밋/푸시 **0**(`LOOP_ALLOW_COMMITS=0`, 저장소에 커밋 자체가 없음).

## 다음 행동

work(Sonnet5/high) 회차가 `G2_FULL_CAPACITY_COVERAGE_GATE_LAP406.md`의 게이트 2건을
추가한 뒤, 카드 §D 우선순위 큐 **P1(marked compat near-4000 반복)** 을 착수한다.
P3는 사용자 답변 대기이므로 착수하지 않는다.

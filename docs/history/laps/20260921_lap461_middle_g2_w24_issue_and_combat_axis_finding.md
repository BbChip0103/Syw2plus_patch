# lap461 (middle) — W24 발행 + 전투 축 실측 정정(N87~N89)

- **날짜:** 2026-09-21 KST
- **lap:** 461 (`loop/.lap_counter` = 461)
- **역할/모델:** middle(중간계획·컨펌) — Claude Code `claude-opus-5` / high
- **목표:** `docs/STATUS.md` 「다음 한 가지」 = `loop/ESCALATE_SOL` §38 판정5 집행 —
  **W24 카드 1장 발행**(수리후보 N=4001, gate-legal 시딩, 혼합 구성(건물 포함) + 전투/사망/
  슬롯 재사용 순환 cap 근접 24k soak, 판정식 실행 전 고정, N85/N86 선수리, lap404 rider 동봉,
  (U4) smaps_rollup 유지, 활성 카드 1장)
- **게임 실행:** **0회** · **제품/도구 source 변경:** **0** (N22: 이번 회차에 source를 바꾸지 않았다)
- **커밋:** 0 (`LOOP_ALLOW_COMMITS=0`)

## 1. 이전 바퀴 검수 (PROMPT ④-2, 독립 재확인)

lap460은 strategy 판정 회차라 바이트 산출물이 없다. 검수 대상은 §38이 **인용한 수치**다.
lap460의 서술을 읽기 전 판정 입력으로 삼지 않고
`temp/.../20260921_lap459_middle_review/recheck459_output.json`을 **직접 재독**했다:

| 항목 | recheck459 원시값 | §38 인용 | 일치 |
|---|---|---|---|
| `U_min24` | 1035 (owner1, tick24,012) | 1,035 | ✓ |
| `U_min8` | 661 (owner5) | 661 | ✓ |
| `r_late` | 0.008746719980007497 | 0.008747 | ✓ |
| `r_need` | 0.033041666666666664 | 0.033042 | ✓ |
| `verdict` | `DECAYED` | `DECAYED` | ✓ |
| 무결성 | `live_vs_sumcount_mismatch`0·`used_over_5000`0·`tick_regressions`0·`used+reserved>5000`**0** | 전부 0 | ✓ |
| 자원 | `min_rice`967,672 / `min_wood`969,464 | 96.8% 잔존 | ✓ |

⇒ **§38이 근거로 쓴 수치는 원시 재계산과 불일치 0.** 판정 5건의 처분 자체는 strategy 권한이며
middle이 뒤집지 않는다. 다만 판정5가 지시한 W24의 **실행 가능성**은 이번 회차에 실측으로
검증했고, 그 결과가 아래 §2다.

부수 관찰: `recheck459_output.json`의 `owner0_departs_20_2_at_tick`은 **349**다(lap446 Step0의
284와 다른 run·다른 빌드축이므로 모순 아님). N59 재확인은 양쪽 모두 성립.

## 2. 신규 발견 — W24 설계를 바꾼 3건

### N87 (결정적) — "앵커를 붙이면 싸운다"는 레버는 **이미 소진됐다**

lap451이 STATUS에 적은 **"앵커 8개 전부 disjoint"** 는 **앵커 좌표가 서로 다르다**는 뜻이지
**배치 범위가 분리됐다는 뜻이 아니다.** `patches/population/runtime_bridge.c:200-205`의 배치는
앵커 셀에서 `candidate=(candidate+1)%cells`로 맵 전체를 **선형 주사**한다.
lap448 `seed_receipts.json` 16건의 `anchor`와 `fixture_attempts`로 주사 구간을 재계산했다
(맵 100×100 실측):

| owner | anchor | 주사 구간(셀) | | owner | anchor | 주사 구간(셀) |
|---|---|---|---|---|---|---|
| 0 | (2,2) | 202‥381 | | 4 | (2,52) | 5202‥5363 |
| 1 | (27,2) | 227‥573 | | 5 | (27,52) | 5227‥5604 |
| 2 | (52,2) | 252‥777 | | 6 | (52,52) | 5252‥5760 |
| 3 | (77,2) | 277‥934 | | 7 | (77,52) | 5277‥5930 |

**겹침(셀 수):** 0-1 155 · 0-2 130 · 0-3 105 · 1-2 322 · 1-3 297 · **2-3 501** ·
4-5 137 · 4-6 112 · 4-7 87 · 5-6 353 · 5-7 328 · **6-7 484**.

⇒ 적 소속 유닛이 **같은 행에 셀 단위로 뒤섞여 24,000 tick 동안 인접**해 있었다.
그럼에도 lap448 원시 712표본에서 owner `count` 감소 표본은 **단 2건**
(tick **10,587**, owner0 `152→150`, owner1 `154→152`) = **소실 4기 / 1,166기 / 24k tick**.

**함의:** W24가 요구하는 "전투/사망/슬롯 재사용 순환"을 **기하 배치로는 만들 수 없다**.
남은 fixture 내 가설은 **구성(타입)** 뿐이고, 그것도 실패하면 정답은 `NO_ENGAGEMENT`이며
(ㄴ)(사용자 승인 대기)가 유일한 진입로라는 보고다. 이 사실을 카드 §2-2·§7에 박았다.

### N88 — 건물 계층은 **정적으로 결정 불가**, 그러나 런타임 읽기 1회로 결정 가능

`runtime_bridge.c:177`이 `fixture_type = op==5 ? 5u : 7u`로 **타입을 하드코딩**한다 ⇒ op5/op6으로는
type5(cost 35)·type7(cost 10) 외 아무것도 시딩할 수 없다. 그리고 타입 표 `0x9B5238`은
`.data` raw 끝 `0x4F9000` **바깥(BSS)** 이라(STATUS F4 블로커 · W2 실측) **파일 정적 분석으로
타입 목록을 얻는 것은 원리적으로 불가능**하다.

**그러나** 필드 오프셋은 소스에서 전부 확정된다 — cost `+0x00`(L179), width `+0x06`(L182),
height `+0x08`(L182), flags `+0x14`(L192). 샘플러는 이미 Linux 쪽에서 게임 메모리를 직접 읽으므로
**PS3 진입 후 `0x9B5238 + t*0x394`(t=0..199)를 읽기만 하면** 전 타입 인벤토리를 얻는다.
**DLL 변경도 새 op도 필요 없다.** ⇒ W24 Step A로 채택(기계적 B/C 집합 정의 + 실행 전 고정 판정).

**가드 완화 금지 명시:** op5/op6의 `(flags & 14) != 0` 거부와 `width/height 1..8` 제한의 의미는
아직 모른다(원본 동작). 건물이 여기 걸리면 **가드를 풀지 않고** `BUILDING_BLOCKED`로 보고한다.

### N89 — lap404 rider의 차량·수단은 **이미 저장소에 있다** (새 패치 모듈 금지)

- 차량: `patches/population/fixed_supply_5000.py` — 원본에 **2곳만·길이 변화 없이** 편집해
  **stock 1200 레이아웃 + 전비 cap 5000**을 만든다
  (`0x1B576` `66c700dc05`→`66c7008813`, `0x3FFD4` `05dc050000`→`b888130000`
  = `add eax,0x5DC` → `mov eax,0x1388`. **즉치만이 아니라 opcode도 바뀐다**).
- 브리지는 **기본 capacity 1200**으로 빌드 ⇒ `runtime_bridge.c`의 1200 리터럴 치환이 일어나지
  않고 op1의 `slot < 1200` 가드가 그대로 맞는다.
- 주문 1건을 거는 수단: **op1**(`runtime_bridge.c:137-147`)이 살아 있는 owner 소유 producer를
  검증한 뒤 **원본 `0x4AF5E0`(Train)** 을 호출한다. 장부 직접 write(op4)가 아니므로 rider에 적법.

## 3. 발행한 카드

`docs/work/active/G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md` (W24)
SHA256 `66441185c3e90172de3cf5117a42d65a7de06fa334fe2678a324536ef1171142`

§38 판정5 의무 5건 이행:

| 의무 | 반영 위치 |
|---|---|
| ① 판정식 실행 전 고정(ARM_FAIL 게이트 포함) | §7 (배타 순서 1~4, `ARM_FAIL` 최우선) |
| ② N85(활성 owner 필터)·N86(ARM_FAIL) 선수리 | §4 Step B + **음성 대조 2건 발화 증명 의무** |
| ③ lap404 rider 동봉 | §5 Step C — **Step D보다 앞에 배치**(N66 3연속 누락 선례) |
| ④ (U4) smaps_rollup 유지 | §6-4 |
| ⑤ 활성 카드 1장 | 머리말 + §0 |

판정식 요지(실행 전 고정): 활성 owner = 표본 `ai==1`. `D` = owner `count` 감소 합(사망 하한),
`R` = C1·C3 census에서 live 유지이면서 `internal_id`가 바뀐 슬롯 수(재사용 직접 증거),
`P_max` = 비용 기준 최대 단일 type 비중.
`ARM_FAIL`(도달<24k 또는 fault>0, 배타·최우선) → `CYCLE_UNSTABLE`(used>5000 또는 장부 불일치
또는 랩/음수) → `CYCLE_STABLE`(cap 근접 전원 ∧ `D≥50` ∧ `R≥1`) → `NO_ENGAGEMENT`(나머지).
**고정 임계 `D≥50`의 근거를 실행 전에 박았다** — lap448 동일 fixture·인접 배치·24k에서 `D=4`
였으므로 50은 그 12.5배이며 우발 소모로는 도달 불가. **실행 전 기대값도 박았다**:
구성 변경이 무효하면 `D≈4`, `R=0`, `NO_ENGAGEMENT`, `P_max` 목표 ≤0.85(lap448은 0.990, N67).

## 4. fixture / 원본·후보 SHA

- 원본 EXE **직접 재해시**: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (`Syw2plus/syw2plus_original.exe`·`Syw2plus_patch/Syw2plus/syw2plus_original.exe` 둘 다 불변)
- 카드가 지정한 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (이번 회차에 빌드·실행하지 않았다. work가 **재빌드로 SHA 확인**, N53)
- 이번 회차 fixture: **없음**(게임 실행 0). 판정 입력은 기존 원시 산출물뿐 —
  `20260921_lap448_..._root_recovery/{samples.jsonl,seed_receipts.json,run_summary.json}`,
  `20260921_lap459_middle_review/recheck459_output.json`,
  `20260921_lap458_w23_a1_long_window/compute_verdict458.py`.

## 5. 실행 명령 / 검사 결과

```
python3 -m pytest tests/test_g2_eight_owner_setup.py \
        patches/population/test_fixed_supply_5000.py -q      → 17 passed
checks/safety.sh check                                        → SAFETY_PASS
python3 checks/context_limits.py                              → CONTEXT_PASS
sha256sum Syw2plus/syw2plus_original.exe                      → b56986e0…c9c08a8ac (불변)
```

INBOX 2026-09-20 21:58 규칙 적용: **이번 회차에 source를 바꾸지 않았으므로** 전체
`make check`를 재실행하지 않고 표적 테스트 + `SAFETY_PASS` + 원본 직접 재해시만 수행했다(N22).

### 변경 파일 (커밋 0 — 경로와 sha256으로 이력 보존)

| 경로 | sha256 |
|---|---|
| `docs/work/active/G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md` (신규) | `66441185c3e90172de3cf5117a42d65a7de06fa334fe2678a324536ef1171142` |
| `docs/STATUS.md` | `0b8d73aa3724c18a59e36368ee1b90fe972a73599be431564fbced5b75b1dc06` (128줄) |
| `docs/feedback/INBOX.md` | `b2105e0aa72c40da94474038ef60486b8e5fcc4fd457baa606c663399a986960` (399줄) |
| `loop/ESCALATE_SOL` (§39 추가) | `528a1e8108d5018007fdbc9ea50eac8ca0778ff369220cb6b445343950192a07` |
| `docs/history/laps/20260921_status_lap461_precompaction.md` (신규, 압축 전 원문) | `6b1433e3ef07b9ce1a961ac47c87b3ef2bdbe52d6d1b0652af914cb670b73b1e` (129줄) |

이 lap 기록 파일 자신의 해시는 자기참조라 생략한다.
**제품 코드/도구 source/바이너리 변경 0** — 위는 전부 문서다.
STATUS 압축 대상은 「다음 한 가지」 블록 교체(−2줄)와 「바퀴 기록」 lap456~459 항목에 lap461을
같은 줄로 흡수한 것뿐이고, **삭제한 결론은 없다**(압축 전 원문은 위 precompaction 파일에 보존).

## 6. PASS / FAIL / SKIP

- **PASS** — lap460 §38 인용 수치 독립 재확인(불일치 0). W24 발행(§38 의무 5건 전부 반영).
  N87~N89 실측/소스 확정. 표적 17 passed · `SAFETY_PASS` · `CONTEXT_PASS` · 원본 불변.
- **FAIL** — 없음.
- **SKIP** — 전체 `make check`(동일 source, N22 규칙). 게임 실행(middle 역할이므로 구현·실행 안 함).

## 7. 다음 행동 (work 회차)

`G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md`(W24)를 **Step A → B → C → D 순서로** 실행한다.
Step D가 60분 상자를 넘으면 Step D만 **그다음 work 회차가 곧바로 실행**한다(재계획·새 카드 금지).
**제품 완료·마일스톤 승인 아님.** 144k 발행 금지는 W24 실행 + 독립검수 ACCEPT까지 유지된다.
(ㄴ)은 여전히 **사용자 전권 대기**이며 승인 전 AI/경로/생산 로직·설정 변경에 착수하지 않는다.

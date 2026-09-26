# lap389 middle — owner transfer(0x476ED0) vs 전비 cap 판정

- 날짜: 2026-09-19 (KST)
- lap: 389 (`loop/.lap_counter`=389)
- 역할: middle / 중간계획·컨펌 (Claude Code claude-opus-5 / high)
- 목표: STATUS「다음 한 가지」— owner transfer가 `used5003 > cap5000`을 만드는 경로를
  원본 명령경계에서 좁게 확인하고, strict 제품불변식 `used<=cap`의 최소안전처리를
  **GO / NO_GO** 로 판정한다. 게임 구현은 하지 않는다.
- 판정: **NO_GO (계획된 0x476ED0 transfer 사전거부 패치)** + **신규 산술 위험 F4 발견 → `loop/ESCALATE_SOL`**

## 0. 이전 바퀴 독립 검수 (PROMPT ④2)

lap388 이후 9/19 actual 24k run 보고
(`docs/reports/20260919_G2_EIGHT_OWNER_5000_ACTUAL_24K.md`)의 핵심 주장을
원본 `samples.jsonl`에서 직접 재계산해 검수했다. 보고서 텍스트를 신뢰하지 않고 수치를 다시 냈다.

| 보고서 주장 | 독립 재계산 | 판정 |
|---|---|---|
| 146 samples | 146 | ACCEPT |
| sample140 tick33185부터 마지막까지 owner1 `used=5003>cap=5000` 7회 연속 | violations=7, samples 140~146, tick 33185~34185, owner1 5003/5000 | **ACCEPT (완전일치)** |
| 8명 모두 첫 sample `used=cap=5000` | 첫 sample 전역합 40,000 = 8×5000 | ACCEPT |

**검수 중 새로 계산한 값(보고서에 없던 것):** 전역 `used` 합은 첫 sample **40,000**,
마지막 **35,427**(유닛 사망으로 감소), 관측 최대 단일 owner used는 **5,003**.
이 40,000이 아래 F4의 근거다.

## 1. 가설과 측정식

- 가설 H: `0x476ED0` owner transfer 경로에 전비 cap(`+0x2012`) 비교가 없어 `+0x200C`가 cap을 넘는다.
- 측정식: 원본 EXE(SHA `b56986e0…c9c08a8ac`) 바이트에서 명령경계 디스어셈블로
  (Q1) 0x476ED0 본문의 cap 참조·반환값, (Q2) `+0x200C` 실제 변경 지점과 그 admission,
  (Q3) 0x476ED0 직접 caller와 반환값 소비 여부, (Q4) cap을 실제로 비교하는 생성 gate,
  (Q5) 장부 폭/부호를 각각 확인한다. Ghidra 디컴파일은 **주소 선정에만** 쓰고 판정 근거로 쓰지 않는다.

## 2. 변경 파일

- 신규(읽기전용 정적 probe): `docs/history/laps/probes/20260919_lap389_middle_g2_owner_transfer_cap_probe.py`
- 신규 기록: 이 파일
- 신규 handoff: `docs/work/active/G2_OWNER_TRANSFER_CAP_MIDDLE_JUDGMENT_LAP389.md`
- 신규 marker: `loop/ESCALATE_SOL`
- **제품코드/바이너리/게임 실행 0. 원본·참고·공유 저장소 쓰기 0. 커밋 0.**

## 3. 실행 명령과 결과

```
python3 docs/history/laps/probes/20260919_lap389_middle_g2_owner_transfer_cap_probe.py
  → rc0, failures=[]
bash checks/safety.sh check → SAFETY_PASS
make check → (§7)
```
원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재확인.
0x476ED0 본문 `[0x476ED0,0x477019)` 329 B, 바이트 SHA `e39a1824…13cf197e`,
선두 16 B `568bf1803e0175096a006a00e8afbef9`.

## 4. 확정 사실 (전부 원본 바이트·명령경계)

**F1 — transfer 경로에는 전비 cap 비교가 없다 (CONFIRMED).**
`0x476ED0` 본문 전체에 `+0x200C`/`+0x2012` 참조가 **0건**이다. 전비 장부는 본문이 부르는
두 함수 안에서만 움직인다:
- `0x476F83 call 0x43EEC0` (구 owner PlayerStruct, `ecx = 0x956770 + old*0x3ABC`) →
  roster 제거 + `sub word [ecx+0x200C], cost`
- `0x476FCF call 0x43EE30` (신 owner PlayerStruct, `ecx = 0x956770 + new*0x3ABC`) →
  `0043EE30 cmp ax,0x4B0 / jl` 즉 **roster 개수 < 1200 하나뿐**이고,
  통과하면 `0043EE9B add word ptr [ecx+0x200C], dx` 를 **무조건** 실행한다.
  이 함수 어디에도 `+0x2012` 참조가 없다.

⇒ `used > cap`은 **원본의 설계상 허용 상태**다. cap(`+0x2012`)은 *생산 admission gate*의
입력일 뿐이며 원본은 이를 유지되는 불변식으로 취급하지 않는다. 5000 패치가 만든 결함이 아니다.
(가감이 짝을 이루므로 전역 합은 transfer로 보존된다 — 넘치는 것은 **받는 쪽 owner 하나**뿐이다.)

**F2 — 반환값을 통한 사전거부는 실현 불가 (CONFIRMED).**
`0x476ED0`은 단일 exit다: `ret`이 `0x477016` 한 곳뿐이고, 조건분기는
`0x476ED6 jne 0x476EE1` 하나이며 그 대상이 본문 안이라 조기 반환 경로가 없다.
꼬리는 `0x477010 mov eax,1 / pop esi / ret 4` 로 **항상 1**을 돌려준다.
직접 caller는 E8 rel32 기준 **정확히 5개**이고, 각 call 직후 2명령을 확인한 결과
**반환값을 소비하는 caller는 0개**다.

| call site | 직후 명령 | 반환값 소비 |
|---|---|---|
| `0x4082E5` | `movsx ecx, word [esi+0x64A]` | 아니오 |
| `0x40F8AC` | `ret 8` | 아니오 |
| `0x47716E` | `mov eax,[esi+0x29C]` | 아니오 |
| `0x477295` | `mov edx,[esi+0x29C]` | 아니오 |
| `0x47795D` | `mov edx,[esi+0x29C]` | 아니오 |

⇒ `mov eax,1`을 `xor eax,eax`로 바꾸는 류의 "거부 반환" 최소 패치는 **아무도 읽지 않으므로
동작상 no-op**이다. STATUS가 미리 지정한 NO_GO 조건("반환/호출자가 거부를 처리하지 못하면 NO_GO")에 정확히 해당한다.

**F3 — caller별 행동 분리 (디컴파일로 분류, 주소는 바이트로 확인).**

| call site | 포함 함수 | 실제 행동 | 부작용 선행 여부 |
|---|---|---|---|
| `0x47716E` | `FUN_004770D0` state `0xF` | **점령(capture) 완료** — 대상 건물/유닛을 점령자 owner로 | 상태기계 `+0x1F0`, 사운드/이펙트 이미 진행 |
| `0x477295` | `FUN_004770D0` 같은 state의 루프 | 점령 대상에 딸린 **부속 2기** 동반 이전 | 위와 동일 |
| `0x47795D` | `FUN_004777E0` | **시간형 점령/전향** (진행 카운터 `+0x1C8`, 표 `0x9B5428/0x9B542C`) | 진행도 소모·자원 차감 후 |
| `0x4082E5` | `FUN_00407930` case `0xC` | `+0x64A` 대상 유닛의 owner로 **자기 자신 편입**(승선/합류) | 명령 상태 진행 후 |
| `0x40F8AC` | `FUN_0040F890` (2인자 thin wrapper) | 두 곳에서 호출: `FUN_00444EF0` = **owner A의 전 유닛을 owner B로 일괄 이전**(패배/흡수), `FUN_00470A00` = type `0x51` 능력의 **단일 대상 전향(charm)** | 일괄 루프 중 |

즉 이 transfer는 capture / 승선합류 / charm / **일괄 흡수** 네 종류이며, script 전용 경로는 아니다.

**F4 — 신규 위험: 전비 장부는 16-bit signed이고 8×5000은 그 범위를 넘는다 (CONFIRMED 산술 + 측정된 전역합).**
- 장부 기록: `0043EE9B add word ptr [ecx+0x200C], dx` — **16-bit** 덧셈(랩어라운드).
- 생산 gate 읽기: `0043EDFC movsx edx, word ptr [ecx+0x200C]` 와
  `0043EE03 movsx ecx, word ptr [ecx+0x2012]` → **부호있는** 비교
  (`0043EE0F cmp edx,ecx / jle` 통과 시 `0043EE1B call 0x442FA0` 할당).
- 따라서 `+0x200C`의 도달 가능 범위는 `[-32768, 32767]`이다.
- **cap 5000 × 8인 = 40,000**이고, 9/19 run에서 **실제 전역 used 합이 첫 sample 40,000**으로 측정됐다.
  `32767 − 40000 = **−7,233**` → 한 owner에 충분히 집중되면 word가 **음수로 랩**한다.
- 원본 cap 1500에서는 `8×1500 = 12,000`, 여유 `+20,767`이라 **원리적으로 도달 불가**였다.
- 랩이 발생하면 `movsx`가 음수 used를 주므로 생산 gate `used+cost <= cap`이 **항상 참**이 되어
  전비 제한이 사실상 해제되고 전역 1199 슬롯 풀이 고갈될 때까지 생산이 가능해진다.

⇒ **8인 각 5000이라는 숫자 자체가 원본 장부 폭과 충돌한다.** 이는 관측된 `+3` 초과보다
훨씬 제품 안정성에 직결되는 결함이며, 이번 lap 전까지 어떤 기록에도 없다.
**단, 트리거 도달성은 미측정이다** — 40,000 중 32,767 초과를 한 owner가 실제로 모으려면
`FUN_00444EF0`(일괄 흡수) 같은 대량 집중이 일어나야 하고, 9/19 run의 관측 최대 단일 owner used는
5,003이다. 산술과 전역합은 확정, **랩 재현은 UNKNOWN**이다.

**F5 — 공유 경계.** `0x43EE30`의 직접 caller는 2개(`0x476FCF` transfer, `0x48BCFE` 비-transfer),
`0x43EEC0`도 2개(`0x476F83` transfer, `0x443156` 비-transfer)다. 생산 gate `0x43EDA0`의 직접
caller는 7개이며 그중 transfer 본문 `[0x476ED0,0x477019)` 안에 있는 것은 **0개**다.
⇒ transfer는 생산 gate를 **의도적으로 우회**하며, roster 함수는 transfer 전용이 아니다.

## 5. 판정

**계획된 최소패치(0x476ED0 transfer 사전거부): NO_GO.**
1. 반환값 거부는 F2로 동작상 no-op이다.
2. `0x43EE30` 안에 cap 비교를 넣는 안은 F5로 **금지**다. 이 함수는 비-transfer caller
   `0x48BCFE`와 공유되고, 생산 경로는 이미 `0x43EDA0`에서 cap을 통과한 뒤 등록하러 온다.
   여기서 조용히 거부하면 유닛은 월드에 존재하는데 owner roster·장부에는 없는
   **포인터/장부 불일치**가 생긴다(AGENTS.md 금지 항목).
3. caller 5곳(+wrapper 2곳)에서 사전검사 후 skip하는 안은 F3로 **정상 game semantics를 깬다**.
   다섯 곳 모두 이미 되돌릴 수 없는 부작용(상태기계 진행·자원 차감·이펙트)을 적용한 뒤 호출하며,
   특히 `FUN_00444EF0` 일괄 흡수를 건너뛰면 패배한 owner에게 유닛이 남는 더 나쁜 상태가 된다.
4. ledger clamp와 비용 미반영 이전은 STATUS가 이미 금지했다.

**그리고 요구 자체가 재정의 대상이다.** `used<=cap`은 원본이 유지하는 불변식이 아니므로(F1),
이를 transfer에 강제하는 것은 버그 수정이 아니라 **정책 변경**이다(점령이 cap 근처에서 실패하게 된다).
숨기지 않고 명시한다.

**대신 실제 제품 위험은 F4다.** `8×5000 = 40,000 > 32,767`은 숫자 선택과 원본 장부 폭의 충돌이며,
`+3` 초과를 막아도 그대로 남는다.

## 6. 목표 영향

G2 「활성8인 전비5000 안정성」의 합격 기준을 다시 잡아야 한다.
- `used<=cap` 전 sample 무위반을 합격 조건으로 두면, 원본 정책과 충돌하므로 제품은
  원본과 달라진다(점령 실패). 사용자/Astra 판정이 필요하다.
- `used<=cap`을 버리고 **생산 gate 무결성 + `+0x200C` 부호 랩 없음**을 합격 조건으로 두면
  원본 semantics를 지키면서 실제 불안정만 막는다. 이쪽이 중간 tier 권고다.
- 어느 쪽이든 **cap 5000이라는 숫자가 16-bit signed 장부와 안전한지**가 선결 문제다.

## 7. 검사

- `bash checks/safety.sh check` → **`SAFETY_PASS`**
- probe → **rc0 `failures=[]`**
- `make check` → **rc0, 715 passed 153.18s** + Ruff `All checks passed` + compileall +
  mypy 10 source files `Success` + `CONTEXT_PASS`. 테스트 수는 lap388과 동일한 715로,
  이 lap의 변경이 probe 1개뿐이고 필수 게이트 대상 밖이라는 것과 일치한다
  (lap339 확인: `docs/history/laps/probes`는 pytest testpaths·ruff 대상·mypy 명시 파일·safety 전부 밖).
- `docs/STATUS.md` 127줄 (PROMPT 상한 130 이하), `## 지금 막힌 것 (Blockers)` 정확히 1개.
- Fast일 뿐이며 실제 앱/24k/144k/멀티 증거가 아니다.

## 8. fixture / 증거

- 원본 EXE: `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/syw2plus_original.exe`
  SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (읽기 전용)
- 주소 선정 참고(읽기 전용): `Syw2plus_re/analysis/ghidra_output/FUN_00476ed0.c`,
  `FUN_0043ee30.c`, `FUN_0043eec0.c`, `FUN_0043eda0.c`, `FUN_004770d0.c`,
  `FUN_004777e0.c`, `FUN_00407930.c`, `FUN_0040f890.c`, `FUN_00444ef0.c`, `FUN_00470a00.c`
- 이전 바퀴 검수 대상: `…/g2_capacity/20260919_eight_owner_5000_stability_actual_v1/official_run1/g2_stock_24k_observation/samples.jsonl`
- 외부 보존: `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap389_middle_static_judgment/`
  `probe_output.json` SHA `012033bf0e29f4c1d0c9e2b16c9991002c9dbc97643e8f75ca6fbcfc08c5cdf7`,
  `probe.py` SHA `eb5b3be15ca3fa9cdb9da5aa9afe2510edcbdf1c1d58ccaee05c3e69b5a59b45`

## 8b. uncommitted 파일 해시 (LOOP_ALLOW_COMMITS=0, 커밋 0)

`git log` = 커밋 없음(브랜치 main에 커밋 0). 이 lap의 변경은 아래 5개뿐이다.

| 파일 | SHA256 |
|---|---|
| `docs/STATUS.md` | `6d0f31f32361c879cfbf3de8417a884f2935232e1fd9684c497323c6341d2915` |
| `docs/history/laps/20260919_lap389_middle_g2_owner_transfer_cap_judgment.md` | (이 파일, 본 추가 이전 `c02b1f60…0ba9e239`) |
| `docs/history/laps/probes/20260919_lap389_middle_g2_owner_transfer_cap_probe.py` | `eb5b3be15ca3fa9cdb9da5aa9afe2510edcbdf1c1d58ccaee05c3e69b5a59b45` |
| `docs/work/active/G2_OWNER_TRANSFER_CAP_MIDDLE_JUDGMENT_LAP389.md` | `56356b79ccd20ad5b8c1c661a9289e079b7f02e83fbe79934ed865c1cfea6f4b` |
| `loop/ESCALATE_SOL` | `f329ce999a5ea976ea9812463c4e63975cc2b952a0ca2ac5123aae6f78f20c7b` |

원본 EXE 재확인 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
게임 프로세스 기동 0, 잔류 0, 새 Wine prefix 0.

## 9. 다음 행동

1. **`loop/ESCALATE_SOL` 판정 대기 항목(Astra/사용자):** G2 합격 기준을
   `used<=cap`으로 둘지, `생산 gate 무결성 + 장부 랩 없음`으로 둘지. 그리고 cap 5000이
   16-bit signed 장부와 양립하는 숫자인지.
2. **승인 없이도 안전한 독립 work 카드(handoff 발행):** F4 랩 도달성 측정.
   바이너리 변경 0·관측 전용으로 `FUN_00444EF0` 일괄 흡수의 트리거 도달성과
   단일 owner used 최대치를 실제 run에서 확인한다. 상세는
   `docs/work/active/G2_OWNER_TRANSFER_CAP_MIDDLE_JUDGMENT_LAP389.md`.
3. 계획된 0x476ED0 사전거부 패치 카드는 **NO_GO로 닫는다**. 같은 추측을 반복하지 않는다.

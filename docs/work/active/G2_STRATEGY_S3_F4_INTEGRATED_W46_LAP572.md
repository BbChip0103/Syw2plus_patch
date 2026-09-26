# G2 strategy — W45R 이후 다음 한 축: S3 F4(B) 통합 후보 W46 (lap572)

- 판정: lap572 strategy (Claude Code `claude-opus-5-5`/high; INBOX 2026-09-23 strategy 모델 교체 · 2026-09-24 14:34 "strategy는 claude-opus-5-5 유지"), 2026-09-25 KST.
- 입력: `loop/ESCALATE_SOL` §124(lap571 middle W45R `ACCEPT / STABLE_MIXED_24K`), INBOX 2026-09-24 23:05 상시 지시(절차·해석·예산 판단은 strategy가 결정), lap522 §4 S3/S4, lap561 §1-3 축 대조표, S5 제출문 §4.
- 이 문서는 게임 코드·브리지·하네스·후보를 바꾸지 않는다. G2 합격이나 사용자 마일스톤 승인이 아니다. 사용자가 번복할 수 있다.

## 1. 이전 바퀴 검수 (lap571 → 독립 확인)

- lap570 raw SHA 앞자리 seed `7b77af47`, T0 `04653a7c`, samples `3bf57033`, save/load `63ae5320`가 §124와 같다. `samples.jsonl` 638행.
- `save_load_result.json`에서 직접 재계산: save `16061→16061`, mutation `16367`, pre-load `16368`(저장 뒤 307 tick), load `16369→16061`. Q11 식 `16061 ≤ 16061 < 16369` 성립.
- 풀 크기 1,687 → 1,688 → 1,687. `pre_load − pre_save = {(2313,526601,7,0)}` 정확히 1건, 반대 방향 0건, `post_load == pre_save`. 8 owner `(used,reserved,count)` 저장 전후 동일(owner0 `(4980,10,209)` … owner7 `(4995,15,212)`).
- **lap571 `ACCEPT / STABLE_MIXED_24K` 동의.** 건물 혼합 구성 24k 안정 동작과 판별형 저장/로드가 같은 후보 `a10024de…`에서 2단 성립했다. G2 PASS는 아니다.

## 2. 남은 G2 축 (S5 제출문 §4 갱신)

| # | 축 | 상태(lap572) | 누가 여는가 |
|---|---|---|---|
| 1 | 전투·사망·재생산 | Q10 `(다)`로 시험 제외 | 사용자 |
| 2 | 건물 혼합 저장/로드 | **W45R 2단 ACCEPT로 충족** | — |
| 3 | 혼합 구성 144k | 미실행 | strategy(예산 판단) |
| 4 | S3 F4(B) 32-bit 장부 통합 | 후보 실행 0 | **이번 판정(§3)** |
| 5 | S4 멀티 동기화 | "8인" 정의 미결 | 사용자(제품 목표 정의) |
| 6 | 실제 플레이 성격(N141) | W44R에서도 동결 경향 | 보고 전용 |
| 7 | 화면 증거 | 없음 | 3단 제출 전 보강 후보 |

## 3. 판정

1. **Q9 해석을 strategy가 정한다(상시 지시 적용, 사용자 번복 가능).** 2026-09-23 12:55 "③ 패치본(2601·2606) 실행 검증 제외"는 **커뮤니티 배포 EXE**를 가리킨다고 본다. 근거: 원본 폴더에 `조선의반격 ESL 2601 (멀티용).exe` 같은 배포본 파일이 실제로 있다. 사용자는 판번호를 직접 적었다. F4 후보는 우리가 만든 제품 후보이고, 사용자가 (B)를 채택했다(APPROVALS 2026-09-23 04:13). 이것을 실행하지 않으면 DESIGN §4의 실행 증거 없이 채택안이 남는다. **결론: F4 통합 후보의 격리 실행 검증은 제외 범위 밖이다.** 커뮤니티 배포본 실행은 계속 제안하지 않는다. 격리 prefix에서만 도는 되돌릴 수 있는 실행이므로 비가역 질문 대상이 아니다.
2. **다음 한 축 = S3(F4 통합) 먼저, 혼합 144k는 그다음.** DESIGN §1은 "마지막에는 함께 적용한 동일 후보"를 요구한다. F4는 채택된 제품 변경이다. 그러므로 최종 G2 후보는 `a10024de` 단독이 아니라 `a10024de`+F4다. 144k(약 73분)를 곧 대체될 후보에 먼저 쓰면 결합 후보에서 다시 돌려야 한다. 통합 24k를 먼저 닫고 144k는 결합 후보에서 한 번만 돈다.
3. **정적 가능성 `FEASIBLE`(lap572 읽기 전용 probe, 파일 쓰기 0).** `docs/history/laps/probes/20260925_lap572_strategy_f4_on_a10024de_overlap.py`, exit 0, 사전 고정 단언 5/5 PASS:
   - A1 원본 SHA `b56986e0…a8ac` 일치(전후 불변).
   - A2 `build_candidate(original, 4001)` 메모리 재생성 SHA = `a10024de…2d68`.
   - A3 F4 15곳의 old bytes가 후보에도 모두 있다.
   - A4 후보 diff 5,912B와 F4 편집 범위의 겹침 0.
   - A5 원본 단독 적용 SHA = `1893ff50…53ae1` 재현.
   - 결합 메모리 SHA **`dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`**. 파일로 쓰지 않았다.
4. **판독 폭 위험 R-W(신규, 실행으로 닫아야 함).** 브리지 `runtime_bridge.c:102,210,227`과 W26 헬퍼 `read_owners_full`은 `used`를 `+0x200c` int16으로 읽는다. F4 후보에서 `used`는 dword이고 building_count는 `+0x2016`으로 옮겨진다. 값이 5,000 이하이면 하위 16비트 판독이 같은 값을 준다. 하지만 상위 워드 오염은 보이지 않는다. W46은 dword와 이동한 building_count를 **원시 메모리에서 따로 읽어** 대조해야 한다. 브리지 source는 바꾸지 않는다.

## 4. W46 work 계약 (다음 work 회차가 계획 회차 없이 착수, 게임 정확히 1회)

1. **파생:** lap570 `w45r_run.py`(SHA `c34c50ece905e01777f498743cf6695cb5bd54b83cf62775f364307febf40cc0`)를 새 비중첩 공유 temp 디렉터리 `temp/Syw2plus_patch/g2_capacity/<date>_lap<lap>_w46_f4_integrated_mixed_24k/`의 `w46_run.py`로 복사해 아래만 바꾼다. 새 prefix, 사용 중이 아닌 새 display. 기존 raw·`bridge_build`는 읽기만 한다.
2. **후보 구성(하네스 안, 메모리):** `build_candidate(original,4001)` → SHA `a10024de…` 확인 → `supply_ledger_32bit.EDITS` 15곳 old bytes 확인 후 적용 → SHA **`dfdc91ad…3883`** 확인 → 새 게임 복사본에만 쓴다. 역적용(15곳 new→old)이 `a10024de…`로 돌아오는지 게임 전에 확인한다. 하나라도 어긋나면 게임 0회로 `ARM_FAIL(candidate)`다. 제품 source(`patches/`)는 바꾸지 않는다.
3. **추가 원시 판독:** 모든 표본·저장/로드 스냅샷에서 owner별 `used32 = dword[PS+0x200c]`, `used_hi = word[PS+0x200e]`, `bldg = int16[PS+0x2016]`을 원시 `read()`로 남긴다. 기존 int16 `used`도 그대로 남긴다.
4. **그대로 두는 것:** W45R의 fixture(8 AI, map100×100, type5×100·type7×25·type2×60·type46×20, 띠 anchor), 시딩 순서, T0 gate, save tick≥16,000, 저장 뒤 ≥300 tick, headroom owner type7 1기 op6 주입, load 1회, tick≥24,000 종료, 허용 op 집합.
5. **게임 전 검증:** `py_compile`. W45R 합성 회귀에 음성 2건을 추가한다: (a) `used_hi≠0` 표본이 F2 FAIL, (b) post-load `used32`/`bldg`가 pre-save와 다르면 F3 FAIL. 그다음 허용 op 정적 검사, 원본 SHA, `checks/safety.sh check`=`SAFETY_PASS`. 남은 시간이 40분 미만이면 시작하지 않고 기록한다. foreground로 완주까지 기다린다. background는 금지한다.

### 합격 기준 (실행 전 고정 — middle은 강화만 가능, 완화 금지)

| ID | 기준 |
|---|---|
| B1~B6 | lap561 §2 표와 W45R 카드 §2 그대로(B4는 Q11-2 판별형: 저장 뒤 ≥300 tick, `load.after ≤ save.after < load.before`, 주입 UID pre-load 존재·post-load 소멸, 풀 4-튜플·8 owner `(used,reserved,count)` = pre-save) |
| F1 후보 | 게임에 쓴 EXE SHA = `dfdc91ad…3883`, 역적용 = `a10024de…`, 원본 SHA 전후 불변 |
| F2 장부 폭 | 전 표본·전 owner에서 `used_hi == 0`, `used32 == used(int16)`, `0 ≤ used32 ≤ 5000` |
| F3 이동 필드 | 전 표본 `bldg ≥ 0`, 저장/로드에서 8 owner `(used32, bldg)` pre-save = post-load |

- 보고 전용(합격 기준 아님, 사후 재채점 금지): owner별 `bldg` 값과 type46 live 수의 관계, N141 동결 비율, 자연 사망/출생 수.
- 라벨(우선순위 순): `RUN_ERROR` > `ARM_FAIL`(F1·B1·B2) > `LEDGER_WIDTH_FAIL`(F2·F3) > `CYCLE_UNSTABLE`(B3·B6) > `SAVELOAD_FAIL`(B4) > `WINDOW_SHORT`(B5) > `STABLE_MIXED_24K_F4`(전부 PASS).

## 5. 결과 분기 (strategy 추가 예외 없음)

- **다음 middle:** summary를 입력에서 빼고 raw로 B1~B6·F1~F3를 독립 재계산한다.
- **ACCEPT + `STABLE_MIXED_24K_F4`:** 결합 후보 `dfdc91ad…`를 G2 통합 후보로 삼는다. 이 문서로 **혼합 구성 144k 1회(W47)를 미리 허가한다.** 같은 fixture와 결합 후보를 쓰고 B1·B2·B3·B6·F2를 tick≥144,000까지 적용한다. 저장/로드는 W46에서 닫혔으므로 144k에서는 빼도 된다. middle이 카드 1장으로 고정하고 strategy 재판정은 없다.
- **`LEDGER_WIDTH_FAIL` / `CYCLE_UNSTABLE` / `SAVELOAD_FAIL`이 결합 후보에서만 나올 때:** W45R(`a10024de`)과 같은 fixture에서 달라진 것은 F4뿐이다. 그러므로 **F4 통합 결함 후보**로 분류하고 재실행하지 않는다. strategy가 F4 수리 범위를 판정한다. 그동안 144k는 닫는다.
- **`RUN_ERROR` / 하네스 결함:** 재실행하지 않는다. middle이 원인을 분류하고 strategy가 예산을 판정한다.

## 6. 금지와 streak

- AI/생산/건설 로직 패치, op4, 허용목록 확장, `(flags&14)` 가드 완화, 브리지·제품 source 변경, 커뮤니티 배포본(2601·2606 등) 실행, S1 교전 재개, 결합 후보 실행 전 144k. 새 middle ACCEPT 전 G2 PASS 주장 금지.
- PROMPT ③ 무증가 streak: lap571(middle)과 lap572(strategy)는 문서 회차 2회다. lap572에는 읽기 전용 정적 probe 1건이 있지만 런타임 증거는 아니다. **다음 회차는 반드시 W46 실제 게임 실행이다.** 추가 계획·카드 회차를 허가하지 않는다.
- S4 "8인" 정의는 제품 목표 정의라서 사용자 전권으로 남긴다. 새로 묻지 않고, 제출문에 미충족으로 적는다. 화면 증거(#7)는 144k 이후 3단 제출 직전에 1장 보강할지 strategy가 판단한다.

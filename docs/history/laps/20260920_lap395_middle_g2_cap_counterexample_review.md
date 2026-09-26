# 2026-09-20 KST | lap395 | G2 — lap394 Astra 반례 독립 검수 / 안전상한 UNKNOWN 확정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 구현·바이너리 수정·게임 실행·커밋 **0**. lap 번호는 `loop/.lap_counter`=395 읽기 전용.
- 가설 / 사용자 관찰: lap394 Astra의 "이전 뒤 재생산" 반례가 lap393 P1~P4 바이트 전제를 지키면서
  전역합 불변식을 깨는가. 깬다면 §7.2~7.6의 어떤 결론이 무효인가. 반복 이전+생산을 배제하는
  **다른 상한**이 존재하는가(Astra 지정 3항목).
- 예상 PASS / FAIL 조건: 반례가 P1~P4 전제 아래 재현되면 P9 귀결 REJECT 확정. 다른 상한이
  32,767을 밑돌면 안전상한 복구, 밑돌지 않으면 **안전상한 UNKNOWN 확정**.

## 판정 요약

**lap394 Astra 반례는 타당하다 — 독립 재현 PASS. 그리고 Astra가 쓴 것보다 강하다.**
추가로 **cap≤4095 안전상한도 무효**임을 이번 lap이 새로 확정했다. 안전상한 **UNKNOWN 확정**.

## 1. A2 — lap393 `failures=[]`가 증명하지 않는 것 (probe가 소스를 텍스트로 감사)

lap393 probe(`97a7679b…c73292f0`)를 **import하지 않고 텍스트로** 열어 P9 블록의 assertion을 추출했다.
P9 블록의 assertion은 **정확히 2개**이고 둘 다 상수 산술이다:
`OWNERS*1500 <= SIGNED16_MAX`, `OWNERS*5000 > SIGNED16_MAX`.
probe 전체 어디에도 전이(이전→생산) 평가가 없다(`used[`/`transfer(`/`produce(`/`for _ in range` 0건).
⇒ lap393의 `failures=[]`는 **32767//8 나눗셈을 인증했을 뿐** `notes["invariant"]` 산문을 인증하지 않는다.
Astra 지적대로다. **P1~P4(바이트 사실)는 무효가 아니며 이번 lap도 전부 재확인했다.**

## 2. A3 — 반례 독립 재현 (lap393 산문이 아니라 바이트 semantics로 모델)

전이 semantics는 §3(A5)에서 직접 디스어셈블해 세웠다: `transfer(a,b,d)`는 cap을 **참조하지 않고**
`used[a]-=d, used[b]+=d`; `produce(o,d)`는 `used[o]+d<=cap[o]`일 때만.

| cap | 이전 후 합 | gate 충족 | 재생산 후 합 | 주장 상한 8C | 판정 |
|---|---|---|---|---|---|
| 1,500 | 12,000 | yes | **12,001** | 12,000 | 반례 성립 |
| 4,095 | 32,760 | yes | **32,761** | 32,760 | 반례 성립 |
| 5,000 | 40,000 | yes | **40,001** | 40,000 | 반례 성립 |

lap394가 게시한 12001/32761/40001 **3값 전부 일치**. P9의 오류 지점은 특정 가능하다:
"생산은 그 owner를 `U_o<=cap_o`로 남긴다"에서 "따라서 `ΣU_o<=Σcap_o`"로 넘어가는 단계다.
이전으로 **이미 cap을 넘긴 다른 owner**가 있는 동안 생산이 가능하므로 합 보존이 성립하지 않는다.
경험적으로도 9/19 실측이 `owner1 used=5003>cap=5000`을 이미 보였다(∀o U_o≤cap_o는 실측 거짓).

## 3. A5 — 왜 반례가 성립하는가 (원본 바이트, 이번 lap 재유도)

생산 gate `0x43EDA0`와 `roster_add 0x43EE30`이 **서로 다른 한계**를 건다:

| 경로 | roster count `+0x200A` | count cap `+0x2010` | supply used `+0x200C` | supply cap `+0x2012` |
|---|---|---|---|---|
| 생산 gate `0x43EDA0` | 2 | **2 (강제)** | 1 | **1 (강제)** |
| `roster_add 0x43EE30` | 2 | **0** | 1 (`add`) | **0** |

- 생산: `cmp ax,[ecx+0x2010]/jl`(arg==1) 또는 `count < count_cap-8`, **그리고**
  `movsx used[0x200C]; movsx cap[0x2012]; add; cmp; jle` 통과 시에만 등록.
- 이전: `roster_del`(`sub word[ecx+0x200C],dx` @`0x43EF8B`) + `roster_add`
  (`add word[ecx+0x200C],dx` @`0x43EE9B`). `roster_add`의 유일한 한계는
  `cmp ax,0x4B0; jl` = **배열 1200칸**뿐이고 `+0x2010`/`+0x2012` 참조 **0건**.
- 두 writer의 비용 유도는 동일 골격(`0x66B81D` type → `0x9B5238` 비용표) ⇒ 이전은 합을 보존한다(P2/P3 유지).

⇒ **이전은 supply cap도 count cap도 통과하지 않는다.** 한 owner의 used/count는 이전만으로
자기 cap과 자기 count_cap을 넘어 **1200칸까지** 올라갈 수 있다. 이것이 반례의 바이트 근거다.

## 4. A4 — 반례는 일회성 `+d`가 아니라 **펌프**다 (Astra 기술보다 강함)

donor가 1기 넘기고 gate-legal하게 1기 재생산하는 사이클을 반복하면 수신 owner의 장부는
`Σcap`이 아니라 **자기 roster/유닛 풀**까지 자란다. 수신 owner는 생산자가 아니므로 gate를 영원히 만나지 않는다.
비용은 실측 최저 owner 평균 **29.43**(owner1 최종 5003/170), 풀 1199(STATUS 관측 peak 1176) 사용:

| cap | 시작 유닛/owner | 이전 횟수 | gate-legal 재생산 | 수신 used | signed16 랩 |
|---|---|---|---|---|---|
| 1,500 (원본) | 50 | 1,064 | 799 | **32,785** | **발생** |
| 4,095 (lap393 "안전") | 139 | 975 | 87 | **32,785** | **발생** |
| 5,000 (목표) | 149 | 965 | 7 | **32,785** | **발생** |

⇒ cap은 랩 가능성을 **결정하지 않는다**. 세 cap의 차이는 필요한 재생산 횟수(799 vs 87 vs 7)뿐이다.

## 5. A6 — Astra 질문 "다른 상한이 있는가"에 대한 답: **있지만 구제하지 못한다**

남은 유일한 구조적 상한은 `max_o used_o <= min(roster 1200, 유닛풀) × 최대 단위비용`이다.
- 1200칸 roster가 천장 32,767에 정확히 닿는 **손익분기 평균비용 = 27.31**.
- 실측 8 owner 평균비용(146 sample) = **31.66 ~ 34.42** — 전부 손익분기 초과.
- 따라서 상한 평가값 = **37,988 ~ 41,309**, 전부 32,767 **초과**.
- 이 상한은 **cap 비의존**이다: 원본 1500에서도 같은 값이다.
- FO-2 독립 재확인: 비용표 `0x9B5238`·type표 `0x66B81D`는 `.data` raw 끝(`0x4F9000`) **바깥 BSS**라
  **최대 단위비용을 정적으로 읽을 수 없다**(평균으로 대신했다). ⇒ 정밀 상한은 런타임 측정이 필요하다.

## 6. A7 — cap 5000에서는 펌프조차 필요 없다

핀된 9/19 fixture는 전 세계 **1160기 / 총 supply 40,000**이다. `1160 <= 1200`이므로 `roster_add`는
그 1160기를 **한 owner에 전부 받아들인다**. 생산 0회로 40,000 > 32,767. cap≤4095에서는 이 경로만은
천장 아래(8×4095=32,760)라서 §4의 펌프가 필요하다 — 그래서 펌프가 결정적이다.

## 7. 무효화되는 결론 (Astra 지정 1항: 어떤 결론이 무효인가)

- **§7.2 불변식 `max_o used_o ≤ Σcap_o`** — **무효**(§2/§4). P1~P4 전제는 유지.
- **§7.3 표의 "1500 → 랩 불가능(증명)", "4095 → 랩 불가능(증명)"** — **둘 다 무효**(§4).
  "5000 배제 불가"는 결론만 살아남되 근거가 바뀐다(§6의 cap 비의존 상한).
- **§7.3 "cap ≤ 4,095"라는 결정수치** — **무효**. 4095는 안전상한이 아니다.
- **§7.6 분기 A("cap≤4095 채택 = 원본 랩 불가능성 유지")** — **전제가 무효**. A를 택해도 랩은 남는다.
  즉치 2개 패치 카드(`G2_SUPPLY_CAP_LEDGER_DECISION_LAP393.md` §C)는 **착수 근거 상실**.
- **§7.5 "랩 트리거 fixture 불필요"** — 불변식에 의존한 부분 **철회**. 단 §7.1(`FUN_00444EF0`은
  캠페인 스크립트지 패배 핸들러 아님)은 독립 근거라 **유지**되며, 이는 흡수 경로가 아닌
  **정상 이전 경로**로 질문을 옮긴다.
- **유지되는 것:** P1~P4 바이트 사실, lap389 A(이전 사전거부 NO_GO), lap385/388 저장포맷 통합 blocker,
  lap391 수치(M1~M4·위반7건·per-owner 범위), N16 정정.

## 8. Astra 지정 2항 — 변위 검색 5건 vs writer 완전성 (구분해 적는다)

`+0x200C` 직접 변위 참조 5건은 **`[reg + 0x200C]` 주소지정 형태만** 덮는다. 계산/별칭 base를 통한 쓰기
(절대 VA, bulk blob 복원, PlayerStruct memcpy)는 **덮지 않으며 이번 lap도 주장하지 않는다**.
save/load의 bulk blob 복원은 두 writer 바깥이다(lap393 FO-3 유지). 원시 증거 삭제 0건.

## 9. 변경 파일 / 해시 / 게이트

- 변경: **probe 1개 + 문서**. 제품코드·바이너리·게임실행·커밋 **0**. uncommitted 유지.
- probe `docs/history/laps/probes/20260920_lap395_middle_g2_cap_counterexample_probe.py`
  SHA256 `30ed79deb127235f5eb4bff93326daec094f6293a9674c9335cfd31d85d182e6`, **rc0 `failures=[]`**.
- 외부보존 `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap395_middle_counterexample_review/probe_output.json`
  SHA256 `ce1dfe7df727ffc5fb2a33c4a7269ca6eb3d03438149547ed74653ba2707d6be`.
- 입력 fixture: `samples.jsonl` SHA256 `76903a8d…f0e7180`(146 samples, tick10020→34185, cap 균일 5000) — probe가 해시 검증.
- 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **재해시 불변**. 후보 없음.
- 게이트: `make check` **rc0 / 715 passed 151.06s** + Ruff/compileall/mypy10 Success + `CONTEXT_PASS`;
  `checks/safety.sh check` **`SAFETY_PASS`**. 로그 `/tmp/lap395_makecheck.log`.
- **Fast일 뿐이다.** 실제 앱/24k/144k/멀티/LAN 실행 증거 아님 — 이번 lap 게임 실행 **0**.

## 10. 측정값 / 판정

- lap394 반례 독립 재현: **PASS**(12001/32761/40001 3값 일치).
- lap393 §7.2 불변식: **REJECT 확정**. §7.3 4095 안전상한: **REJECT(신규)**.
- 대체 상한 존재 여부: **존재하나 천장 미달 구제 실패** → **안전상한 UNKNOWN 확정**(Astra 지정 3항 답).
- 실제 게임 도달성(정상 이전으로 1100기 집중이 지원 8인 자유대전에서 일어나는가): **UNKNOWN** — 미측정.
- 최대 단위비용: **UNKNOWN(정적 불가, BSS)** — 런타임 측정 필요. 평균 31.66~34.42만 확보.

## 11. 회귀 / 남은 위험 / 독립 검수 상태

- 이번 판정은 **정적 + 산술 + 기존 fixture 재분석**이다. 제품/런타임/마일스톤 승인 **아님**.
- middle은 목표 숫자(5000)를 바꿀 권한도, 통합 NO_GO를 뒤집을 권한도 없다 ⇒ `loop/ESCALATE_SOL` §9 보존.
- 다음 새 middle이 이 lap을 독립 검수한다. 자가 승인 없음.
- implementation-unchanged-streak: 세션 시작 시 러너 값 **1**, 이번 회차도 제품 변화 0 ⇒ **2**.
  PROMPT ③에 따라 **다음 회차는 측정 가능한 제품/실행 변화여야 한다** — 그래서 §12 work 카드를
  실행 가능한 조건으로 확정해 인계했다. 추가 계획 회차를 쌓지 않는다.

## 12. 다음 한 가지 (work 인계 — Astra 지정 4항)

`docs/work/active/G2_SUPPLY_LEDGER_WRAP_PROBE_LAP395.md` 카드 **W2**로 확정 인계.
Astra가 요구한 "정상 이전 뒤 원 소유자 재생산 + 장부 대 실소유 비용합/roster/pool 대조"에
이번 lap이 특정한 **결정적 미지수 1개(최대 단위비용, BSS라 정적 불가)** 측정을 합쳤다.
관측 전용·바이너리 변경 0·기존 격리/원본SHA/원복 계약 안. `FEASIBLE`이면 다음 work 회차에 즉시 실행한다.

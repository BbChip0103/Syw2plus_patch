# 2026-09-21 | lap 418 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  게임 코드 hands-on 수정 없음. lap417 work 결과의 독립 검수(⑥ 2단).
- 가설 / 사용자 관찰: lap417이 W10 P-B로 "풀-경계 미패치 site 3곳 중 2곳은 fixture에서 배제, `0x00422dc0`만
  호출경로 미해결"이라 판정하고, STATUS의 「다음 한 가지」로 **Wine 디버거/계측 probe로 `0x00422dc0` 도달
  여부를 동적 확인 → 도달 시 `0x00422dc7`의 `0x4B0`을 `0xFA1`로 최소 수리**를 큐에 올렸다.
  이 검수는 그 인벤토리와 미해결 판정을 요약본이 아닌 **바이트에서 직접 재계산**한다.
- 예상 PASS / FAIL 조건: lap417 주장 각각에 대해 (a) 독립 재현 일치 → CONFIRM, (b) 불일치 → 수치와 함께
  정정, (c) 다음 한 가지의 전제가 무너지면 그 카드를 무효화하고 대체 카드를 발행. 이 lap은 계획·컨펌
  역할이므로 후보 바이너리/제품 코드를 고치지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 저장소 **source 변경 0**(N22 문구: 이번 회차에
  source를 바꾸지 않았다). 문서만 갱신 — `docs/STATUS.md`, 이 lap 기록(신규),
  `docs/work/active/G2_POOL_FAULT_H2_STALE_REFERENCE_LAP418.md`(신규 W11 카드),
  `docs/feedback/INBOX.md`(lap415/416 미기록 N29에 대한 처리 표기 없음 — 원문 무수정).
  uncommitted(LOOP_ALLOW_COMMITS=0, 저장소에 커밋 자체가 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 2경로
  (`Syw2plus/syw2plus_original.exe`, `syw2plus_original.exe`) 검수 후 재해시 **불변**.
  후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe` —
  `patches.population.g2_full_capacity_persistence_compat_v1.build_candidate(original, 4001)`로
  in-process 재빌드해 SHA 일치 확인. **게임 실행 0회**(정적 분석 + lap416 run2 원시 샘플 재집계).
  재집계 대상 fixture는 lap416의 op7 resource-only / 7 AI / N=4001(709 표본).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 자체 작성 스크립트·산출물
  `temp/Syw2plus_patch/g2_capacity/20260921_lap418_middle_review/`
  (`verify_build.py`, `scan418b.py`, `xref418.py`, `trace418.py`, `scan418_sites.json`,
  `xref418.json`, `findings.json`). lap417의 `scan_4b0_sites.py`를 재사용하지 않고 별도로 작성했다.
  검사: `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(기준선 동일);
  `bash checks/safety.sh check` → **SAFETY_PASS**; 원본 2경로 `sha256sum` 불변.
  source 미변경이므로 전체 `make check`는 재실행하지 않았다(2026-09-20 21:58 지시 + N22).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  1. **site 카운트 — 정정(lap417 FAIL).** resync 선형 sweep(capstone, 306,811 insn)으로 `.text`의
     0x4B0 피연산자를 재계산: **원본 37곳**(즉치 36 + 메모리 변위 1), **후보 36곳**(즉치 35 + 변위 1).
     lap417이 "후보의 0x4B0 즉치 36곳"이라 적은 값은 실제로는 **원본의 즉치 수**다 — lap417 자신의
     `sites_4b0_raw.json` 키가 `total_sites_0x4b0_original = 36`이다. 후보 기준 즉치는 **35**다.
     (숫자 36이 우연히 겹쳐 오류가 드러나지 않았다: 원본 36 − 패치2 + 후보고유1 = 35, 여기에 변위 1을
     더하면 36.) N27의 "54"는 별개로 raw byte 패턴 수치이며 내 재계산에서도 원본 `b0 04` 54건으로 일치.

  2. **lap417이 놓친 후보 고유 site — `0x0041b56d`(신규).** 원본 `ba fa 00 00 00`(`mov edx,0xFA`=250)이
     후보에서 `ba b0 04 00 00`(`mov edx,0x4B0`=1200)이다. 인접 워드 기록도 `0x5DC`(1500)→`0x1388`(5000).
     즉 후보 패치가 스스로 만들어 낸 0x4B0이며, PlayerStruct `+0x2010` 개수 cap / `+0x2012` 전비 cap을
     쓰는 자리다(F4의 생산 gate 기술과 일치). **분류: 풀 순회 아님**, lap397이 확정한
     `roster_add cmp ax,0x4B0`(owner당 개수 상한)과 정합. 판정에는 영향이 없으나 **방법론 결함**이다 —
     원본 기준 스캔은 패치가 도입한 site를 원리적으로 볼 수 없는데 카드는 "후보의 전수 인벤토리"를
     요구했다. 앞으로 P-B류 인벤토리는 후보를 1차 기준으로 스캔한다.

  3. **누락된 피연산자 종류 — `0x004c5598`.** `mov dword ptr [ebx+0x4b0], 0x9600`의 0x4B0은 메모리
     변위인데 lap417의 즉치 전용 필터가 조용히 제외했다. 구조체 필드 오프셋이며 풀과 무관(무해).

  4. **호출자 집합 — CONFIRMED(lap417 일치).** 독립 xref로 `FUN_004183a0` 호출자 **정확히 3곳**
     (`0x0043ff8d`, `0x0049ba0e`, `0x004a863f`), `FUN_00444ef0` 호출자 **정확히 8곳**
     (`0x004be25f`/`0x004bf035`/`0x004bf97e`/`0x004bff74`/`0x004c0281`/`0x004c1f8d`/`0x004c1f9c`/`0x004c1faa`,
     전부 `0x004be000~0x004c2000`). 주소·개수 모두 lap417 보고와 일치한다.

  5. **`0x00422dc0` 호출 경로 — 정적으로 해결됨(lap417 "미해결" FAIL).** lap417은 `call`과 절대주소
     dword만 찾아 0건이라 결론했으나, **`jmp` thunk를 놓쳤다**:
     - `0x00422db0: jmp 0x00422dc0` (thunk)
     - `.data` `0x004ec02c` → `0x00422db0` (함수 포인터 표의 5번째 항목)
     - 표 범위 `[0x004ec000, 0x004ec1bc)`, 비-null 항목 **110개**, 종단자 0이 `0x004ec1bc`
     - `0x004de0a2 push 0x4ec1bc` / `0x004de0a7 push 0x4ec000` / `0x004de0ac call 0x4de170`
     - `0x004de170` = 교과서적 `_initterm(start,end)`: dword 배열을 훑으며 non-null마다 `call eax`
     ⇒ `FUN_00422dc0`은 **MSVC CRT 정적 초기화 표(`.CRT$XC`)에 등록된 C++ 전역 생성자**이며,
     매 틱이 아니라 **main 이전 1회** 실행된다. 동적 probe 없이 확정. **PASS(정적 해결).**

  6. **큐에 있던 수리는 무효(no-op) — 결정적.** 그 루프가 슬롯마다 부르는
     `FUN_0048aff0` = `push esi; mov esi,ecx; call 0x4119f0; mov eax,esi; pop esi; ret`이고,
     `FUN_004119f0` = **`mov eax,ecx; ret`(빈 생성자)** 이다. `esi`는 `0x758`씩 전진하지만 **한 번도
     역참조되지 않는다**. ⇒ 1200회 루프는 **풀 메모리를 단 1바이트도 읽거나 쓰지 않는다.**
     따라서 STATUS의 「다음 한 가지」인 `0x00422dc7`의 `0x4B0`→`0xFA1` 최소 수리는 **시작 시 빈 루프를
     1200회 대신 4001회 도는 것 외에 아무 것도 바꾸지 않는다.** 그 카드를 **무효화**한다.
     (부수: 빈 기본 생성자라도 컴파일러가 배열 생성 루프를 발행한 흔적이며, 후보의 풀 재배치
     주소 `0x0108c000`은 이 루프에도 반영돼 있다 — 재배치 fixup 자체는 정상 동작했다는 방증.)

  7. **onset 재분석 — CONFIRMED + 정정.** lap416 run2 `samples.jsonl` 709줄을 직접 재집계:
     tick 11,904까지 전 표본에서 hi 밴드 이상 **0건**, tick 11,921에 **6599**, 11,928에 **19579**,
     lo 밴드는 전 구간 0건, 이상 개체는 **slot 3565 / type 76 / owner 4 단 1기**(`anomaly_count=1`),
     동시 표본의 이웃 필드는 10~13. INBOX의 lap416 서술과 **일치**한다.
     **정정:** `movement_state_probe.py`는 `max_abs`를 **`absmove > 100` 분기 안에서만** 갱신한다.
     따라서 `max_abs == 0`은 "`+0x692`가 정확히 0이었다"가 **아니라** "±100을 넘은 슬롯이 없었다"는
     뜻이다. lap417 `onset_reanalysis.md`와 STATUS의 "매치 내내 0이다가"는 과잉 서술이며,
     ±100 **안에서의** 완만한 drift는 이 지표로 보이지 않는다. 다만 "tick 11,904까지 범위 이탈 0건,
     이후 2 표본 안에 폭증"이라는 **돌발성 결론 자체는 유효**하다.
     **신규 관측:** `bands.lo.live`가 **709 표본 전부에서 0**이다 — 크래시 tick뿐 아니라 **매치 전
     구간에서** 슬롯 <1200에는 살아있는 유닛이 한 기도 없다(W10 §1.6의 위→아래 할당을 전 구간으로 확장).
     또한 468 생존 중 **정확히 1기만** 손상됐다.

  8. **섹션 안전성(신규).** 후보 `.data`는 VA `0x004ec000..0x017c6f04`, 4001 슬롯 풀 구간은
     `0x0108c000..0x017b8658`로 **전부 `.data` 안**이다(raw 0xd000뿐이라 대부분 로더 zero-fill).
     원본에서 `0x0108c000`에 있던 `.rsrc`는 후보에서 `0x017c7000`으로 밀렸다 — 꼬리 재배치와 정합.
     ⇒ 고슬롯 접근 자체에 섹션 커버리지 반대 근거는 없다.

  9. **종합 판정: lap417 P-B는 부분 ACCEPT / 부분 REJECT.**
     - ACCEPT: 호출자 집합 2건(항목4), onset 돌발성 결론(항목7), 무관 site 분류의 대부분.
     - REJECT/정정: 후보 기준 site 수(항목1), 후보 고유 site 누락(항목2), 변위 피연산자 제외(항목3),
       그리고 **`0x00422dc0` 미해결 판정과 그로부터 나온 「다음 한 가지」(항목5·6)**.
     - **H1 재판정: 현재 형태의 H1은 남은 기전이 없다.** "잔존 1200-bound 순회 중 하나가 슬롯 ≥1200의
       초기화/수명주기를 건너뛴다"는 세 후보 전부에서 성립하지 않는다 — `0x00422dc0`은 아무것도 쓰지
       않고 main 이전 1회 돌며, `0x004183a0`/`0x00444ef0`은 커서 조회 함수이고 호출자 전 집합이
       매치 설정/UI라 op7 무입력 fixture에서 도달하지 않는다. 468기 중 **1기만** 갑자기 손상되는
       모양도 구간 전체 초기화 누락과 맞지 않는다. **UNKNOWN이 아니라 기전 부재로 기각**한다.
       H2(stale 포인터/수명주기)와 H3(원본 고유 엣지)는 **미검정으로 살아 있다**.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품코드/게임 바이너리 변경 0, 게임 실행 0, 커밋 0.
  원본 2경로 재해시 불변, `SAFETY_PASS`, 표적 6 passed(기준선 동일), 잔류 프로세스 해당 없음.
  이 회차 결론은 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c` stub 채널에 근거하지
  않는다(N21). **미검증으로 남은 것:** (a) `0x004183a0`/`0x00444ef0`이 실제로 쓰기를 하지 않는지는
  호출자 집합만 확인했을 뿐 함수 본문 전수 확인은 하지 않았다 — 다만 fixture 도달 불가라 결론에
  영향 없음. (b) H2/H3는 실행 증거가 있어야 판정된다. (c) 이 lap은 middle 자기 판단이며 work 회차의
  재현·반박 대상이다. 사용자 마일스톤 승인 해당 없음.
  **N29(미기록 회차) 유지:** lap415/416은 여전히 `docs/history/laps/` 기록이 없다. 이번 lap이 lap416
  원시 샘플을 독립 재확인해 수치 신뢰성은 확보했으나 소급 기록은 만들지 않는다(날조 금지).
  **N30(신규): 원본 기준 인벤토리의 구조적 사각.** 패치가 도입한 상수는 원본 스캔으로 볼 수 없다.
  **N31(신규): 조건부 최댓값 지표 오독.** `max_abs`처럼 임계 분기 안에서만 갱신되는 집계를 "필드의
  실제 최댓값"으로 읽지 않는다. 두 건 모두 게이트 승격 여부는 미결로 둔다.
  **연속 회차 경고:** lap417(실행/제품 0)에 이어 이번 lap418도 실행/제품 0이다 — PROMPT ③의 "연속 최대
  2회"에 도달했다. **다음 lap419는 반드시 실제 실행 증거를 만드는 work 회차여야 하며**, 또 계획/정적
  회차가 필요하다고 판단되면 그 전에 strategy(Astra/Fable)/Sol 판정을 받아야 한다. 이번 lap의 산출물은
  그 실행 회차가 추가 조사 없이 바로 착수할 수 있도록 설계했다(W11 카드).

- 다음 한 가지: **W11 `docs/work/active/G2_POOL_FAULT_H2_STALE_REFERENCE_LAP418.md`** — work(Sonnet5/high)가
  W10 §3 P-A가 이미 규정한 **H1 기각 분기**를 실행한다. lap416의 `movement_state_probe.py`를 그대로
  재사용하되 (a) 사망/미할당 슬롯의 같은 필드를 함께 남기고, (b) 이상 슬롯 3565를 tick 11,860~11,928
  구간에서 **매 tick** 추적하며, (c) `absmove > 100` 분기와 무관하게 `|+0x692|`의 **실제 최댓값과
  분포**를 기록해 N31 정정을 흡수한다. 목적은 손상 순간 그 유닛이 살아 있었는지(H1 잔존형) 아니면
  이미 죽은/재할당된 슬롯을 참조당했는지(H2)를 **한 번의 실행으로** 가르는 것이다.
  `0x00422dc7` 수리는 착수하지 않는다(no-op으로 확정).

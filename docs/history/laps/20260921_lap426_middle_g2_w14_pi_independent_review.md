# 2026-09-21 | lap 426 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  **middle(중간계획·컨펌)**. lap425 work(`claude-sonnet-5`/high)의 W14 P-I 결과를 독립 검수.
  게임 실행 0회, 제품 코드 변경 0, 커밋 0, source 변경 0. 게임 코드 hands-on 수정 없음.

- 가설 / 사용자 관찰: lap425가 원시 457표본으로 카드 판정식 **(B) `+0x700`(K) 자체가 표적**을
  주장했다. 검수 질문은 셋이다. (1) 원시 `samples.jsonl`만으로 같은 수치가 재계산되는가.
  (2) probe가 읽은 주소(`0x9b5258+916*type`, `0x669c7c+140*K`, `unit+0x700`, `unit+0x68c`)가
  실제 게임 코드가 쓰는 주소와 같은가 — 아니면 base=10 관측 자체가 무의미하다.
  (3) "K가 0~48 밖이라 표 밖 읽기"의 `0~48`은 lap424가 **인접 객체 기준으로 추정**한 값이라
  판정의 핵심 근거가 미증명 상수에 걸려 있다. 이 셋을 각각 독립 근거로 닫는다.

- 예상 PASS / FAIL 조건: (1) 457표본 재계산이 lap425 서술과 불일치 0이면 ACCEPT 방향.
  (2) 정적 역산으로 stride 140/916과 base `0x669c7c`/`0x9b5258`이 명령 바이트에서 나오면 주소 확정.
  (3) 코드에서 유도되는 **하드 상한**을 찾으면 추정 상수 의존을 제거, 못 찾으면 판정을 PLAUSIBLE로
  낮추고 그 사실을 적는다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **이번 회차에 source를 바꾸지 않았다**
  (N22 면제 요건 충족 → `make check` 전체 게이트 생략). 신규 문서 3건만 uncommitted:
  `docs/history/laps/20260921_lap426_middle_g2_w14_pi_independent_review.md`(이 파일),
  `docs/work/active/G2_UNIT_0x700_WRITER_ATTRIBUTION_LAP426.md`(W15),
  `docs/history/laps/20260921_status_lap426_precompaction.md`(STATUS 압축 전 원문, SHA
  `792c0ad26ecba2f871d9157b83d9c760d761654de434f4bcf1e2f731e0b5e782`, 130줄 — 압축 대상은
  lap424·lap425 두 항목뿐이며 각 전문은 자기 lap 파일에 그대로 남아 있다) 및 `docs/STATUS.md`
  갱신(갱신 후 SHA `0840288848f6a9f143f9faef63da5392f0d4447c27e96174e63f3b64c060ef5b`, 130줄).
  제품 코드/바이너리/패처 변경 0. `LOOP_ALLOW_COMMITS=0`이므로 **커밋 없음** — 파일 해시:
  W15 카드 `8ae3c118f98333db90758730a4dc058d802a9cebcb374c477ffc141352bbdf27`.

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 4경로
  (`Syw2plus/`, `Syw2plus_patch/Syw2plus/`, `Syw2plus_re/Syw2plus/`, 공유 루트) 전부 재해시 일치.
  후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`(핀 불변).
  검수 대상 fixture는 lap425와 동일(op7 resource-only, 8 owner, N=4001, seed42, display `:3845`).
  이번 lap은 게임을 띄우지 않았다 — 원시 산출물 + 정적 바이너리만 읽었다.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 원시 입력 `temp/Syw2plus_patch/g2_capacity/20260921_lap425_stat_recompute_input_700/samples.jsonl`
    (457줄), `run_summary.json`, `movement_state_probe_pi.py`.
  - 정적 입력 `temp/Syw2plus_patch/g2_capacity/20260921_lap424_middle_review/original.bin`·
    `candidate.bin`·`chain424_disasm.txt`·`scan424_sites_700.json`.
  - 재계산/역산은 임시 python(capstone 5.0.7 + pefile) 스크립트로 수행, 산출물 없이 표준출력만.
  - 표적 테스트 `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
    patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(105.46s).
  - `bash checks/safety.sh check` → **SAFETY_PASS**.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **ACCEPT — 판정 (B) 확정. 원시 불일치 0.**

  **V1 표본/커버리지.** 457표본, tick 16→10528. dense 145표본이 tick **10363~10460**을 덮고
  그 98 tick 중 **미샘플 0개**. 전이 경계 `(10400, 10401]`은 표본 누락이 아니다(lap424 N35와 동형).
  dense 간격 p50 **20.3ms**(min 20.2 / max 25.3).

  **V2 K 전이(단일 변화점).** 슬롯3565의 `K=[unit+0x700]`은 전 구간 **정확히 한 번** 바뀐다:
  `s363 tick10400 K=0` → `s364 tick10400 K=22432`. 이후 s457(tick10528)까지 22432 고정(93표본).
  `K` 히스토그램 `{0: 364, 22432: 93}`.

  **V3 인과 순서가 원시에서 직접 보인다(lap425 서술보다 강함).** s363→s364에서 바뀐 필드는
  `K`뿐이다(`P`는 가드로 null, `p_skipped_out_of_range` false→true). s364→s365(tick10401)에서
  바뀐 필드는 `m(+0x68c) 0→347349`와 `f688 10→19679` **둘뿐**이다. 즉 **K가 먼저 튀고 한 표본
  뒤에 m·f688이 따라온다** — 체인 방향 `K → m → f688`이 관측으로 확인된다. 추적 24필드 중
  나머지 21필드(`alive/move/type/owner/f674/f676/f2a2/f2a4/f2b8/f2ba/f2bc/f2be/f2b0/f2b2/f2d8/
  f690/f1d8` 등)는 전이 전후 불변이다.

  **V4 (A) 배제.** `base`는 슬롯3565가 살아 있는 **152표본 전부에서 10**이고
  `(type, owner)`도 전부 `(76, 4)`, `alive`는 s305 이후 전부 True(전이는 s304 tick10195 →
  s305 tick10229 사이, 이 구간은 coarse 1초 샘플링이라 lap424의 dense 확정값 **tick10201**과
  모순 없이 포함관계다). 스탯표 런타임 손상은 관측되지 않았다.

  **V5 대조 슬롯으로 격리 확인.** ref 슬롯 **3562**(owner4, type110) 148표본(tick10363~10528)에서
  `K=0`·`base=9`·`m=0`·`P=0`·`f688=9`·`alive=True` **전부 불변**. 같은 owner의 다른 유닛은
  무사하다 ⇒ 전역 손상이 아니라 슬롯3565 국소 현상. 저대역(slot<1200) band_scan은 314표본
  전부 `live=0`·anomaly **0건**.

  **V6 산술 정합.** `(base + m) mod 65536 = (10 + 347349) mod 65536 = 19679` — probe가 16bit로
  읽은 `f688`과 32bit로 읽은 `m`이 정확히 일치. 역산하면 게임이 읽은 `P ∈ [3,473,490 .. 3,473,499]`
  (`m = base*P/100`, base=10).

  **V7 probe 주소가 옳다(정적 역산, 원본 바이트에서 직접).** `chain424_disasm.txt`를 명령 단위로
  다시 읽어 stride를 내가 계산했다:
  - `48c8c7 ecx=[esi+0x700]` → `48c8cd eax=ecx*8` → `48c8d4 eax-=ecx`(=7K) → `48c8d6 edx=eax+eax*4`(=35K)
    → `48c8d9 edx=DWORD[edx*4+0x669c7c]` = **`[0x669c7c + 140*K]`** ✔ (stride 140, base `0x669c7c`)
  - `48c8e6 al=[esi+0x8d]`(type) → `48c8ec/48c8ef/48c8f2/48c8f5`가 `229*type` 산출 →
    `48c8f8 movsx ecx, WORD[eax*4+0x9b5258]` = **`[0x9b5258 + 916*type]`** ✔ (stride 916, base `0x9b5258`)
  - `48c900 imul ecx,edx` → `0x51eb851f` + `sar 5` + 부호보정 → `48c914 [esi+0x68c]=edx` = `base*P/100` ✔
  ⇒ probe의 `STAT_TABLE_BASE=0x9B5258`/`STRIDE=916`/`CORR_TABLE_BASE=0x669C7C`/`STRIDE=140`은
  전부 명령 바이트와 일치한다. 추가 교차근거: `base(type76)=10`이 전이 전 `f688=10`과, 
  `base(type110)=9`가 ref 슬롯 `f688=9`와 정확히 같다 — `0x411ec0`의 "생성 시 `f688=base`"와 맞물려
  **서로 다른 두 타입에서** 스탯표 주소가 옳음을 뒷받침한다.

  **V8 STATUS 정밀도 정정(문서 오류, 사실 변경 아님).** STATUS 「검증 상태」 lap424 항목의
  "스탯표는 base `0x9b5228`/stride 916B"는 **다른 접근을 가리킨다**. `0x48cad8 lea ecx,[edx*4+0x9b5228]`은
  916B **레코드의 선두 주소**를 함수에 넘기는 코드이고, 이 체인이 실제로 읽는 필드는 레코드+0x30인
  **`0x9b5258`**이다(`48c8f8`, `48cb40`, `411eb9` 세 곳 모두 `0x9b5258`). 둘 다 참이나 STATUS 문장이
  체인 입력으로 읽히면 오해를 부른다. 아래 STATUS에서 이 한 줄을 정정했다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:

  **정정 1 — "0~48 범위 밖"의 근거를 추정에서 코드 유도 상한으로 교체한다(판정은 유지, 강화).**
  카드/lap425가 쓴 `K_MAX=48`은 lap424가 "인접 객체 기준 약49"로 **추정**한 값이라 판정의
  핵심 조건이 미증명 상수에 걸려 있었다. `+0x700` write site를 직접 디스어셈해 **코드에서
  유도되는 상한**을 찾았다:
  - `0x40d799 mov ecx,[esi+0x388]` → `0x40d79f mov [esi+0x700],ecx` ⇒ `+0x700`에 들어가는 값은
    `[esi+0x388]`에서 복사된 **작업/항목 인덱스**다(포인터 아님).
  - 같은 인덱스가 owner별 WORD 카운터 배열을 찍는다:
    `0x40d72b inc word [eax*2+0x959a8c]`, `0x40f038 dec word [eax*2+0x959a8c]`,
    여기서 `eax = edx + 3759*owner` (`0x8e` owner 바이트로 `3759*owner` 산출).
    ⇒ 배열 주소 = `0x959a8c + 2*(index + 3759*owner)`, owner당 **3,759 WORD(7,518B)** 스트라이드.
  - 따라서 **정당한 인덱스는 반드시 `< 3759`** 여야 한다(아니면 owner N이 owner N+1의 카운터를
    침범한다). 8 owner 배열 전체 범위는 `0x959a8c..0x96857C`.
  - 관측된 `K=22432`는 이 하드 상한의 **5.97배**다. `0~48`이 옳든 틀리든 out-of-range다.

  **정정 2 — 표 밖 읽기가 "어디로" 갔는지 특정했다(추정 제거).**
  `0x669c7c + 140*22432 = **0x9687FC**`, 그리고 같은 레코드의 주기 필드
  `0x669c88 + 140*22432 = 0x968808`. 두 주소 모두 핀된 bulk 라이브 상태 blob
  **`[0x892410, 0x975D8C)`**(save src `0x440F02`, len `0xE397C`) **내부**다(blob 오프셋 `0xD63EC`).
  카운터 배열 쓰기 주소 `0x959a8c + 2*(22432 + 3759*4) = 0x96BF44`도 같은 blob 내부다.
  ⇒ "표 끝을 약간 넘었다"가 아니라 **3.1MB 떨어진 다른 데이터 영역(살아있는 게임 상태)을 읽고
  있다**. `P ≈ 3.47M`이 백분율일 수 없는 이유가 여기서 닫힌다. (A)/(C)/(D)는 성립하지 않는다.

  **정정 3 — 다음 표적의 전제를 좁히지 말 것(lap425 제안 수정).** lap425는 다음 회차를
  "`+0x700` 비상수 write 4곳 중 tick10400 실행분 특정"으로 제안했으나 **그 4곳은 닫힌 집합이
  아니다**. lap424 `scan424_700.py`는 `.text`에서 **변위 리터럴이 0x700이고 베이스 레지스터가
  있는** 명령만 매칭한다. 따라서 다음은 구조적으로 보이지 않는다:
  (a) 다른 객체/배열에서 넘쳐 `unit+0x700`에 **우연히 착지하는 OOB write**,
  (b) 변위가 다른 인덱스형 write `[reg+reg*s+other_disp]`,
  (c) `rep stos`/`memcpy` 계열 블록 write.
  G2 회귀의 현행 유력 가설이 **잔존 1200-bound site의 풀 밖 write**(lap414 확인)인 이상
  (a)는 배제 대상이 아니라 **1순위 용의자**다. 다음 카드는 "4곳 중 하나"를 전제하지 않는다.

  **신규 판별식(값싸다, 긴 run 추가 불필요).** 정당 경로(`0x40d79f`/`0x40f040`)로 K가 쓰였다면
  같은 tick에 `[esi+0x388]`도 22432여야 하고 카운터 `0x959a8c+2*(22432+3759*4)`가 증가했어야 한다.
  `[unit+0x388]`이 정상(0 또는 <3759)인데 `+0x700`만 22432라면 **그 4곳이 아니라 외부 write**다.
  → 같은 probe에 읽기 2개(`[unit+0x388]`, `[unit+0x6fc]`)만 더하면 한 번의 재현 run으로 갈린다.
  이 판별식은 W15 카드 P-J로 발행했다.

  **정정 4 — 주기 게이트는 범인이 아니다(다음 lap의 헛수고 차단).** `0x48c8b1`이 전역 tick
  `ds:0x8924b8`를 읽어 `div [0x669c88+140*K]` 후 나머지 0이면 `0x48c8c2 call 0x413cb0(1)`을 한다.
  `0x413cb0`을 디스어셈한 결과 그 함수는 `[ecx+0xb4] += arg; if > [ecx+0x120] then = [ecx+0x120]; ret 4`
  — **`+0x700`을 쓰지 않는다**(회복/누산 clamp). 주기 게이트 경로는 오염 경로가 아니다.
  다만 K 오염 후에는 이 `div`의 제수도 blob 안에서 읽히므로 **하류 2차 영향**으로 남긴다.

  **살아있는 한계(승격 금지).**
  - **1회 관측이다.** `K=22432`라는 **값 자체**의 재현은 아직 0회다. lap413/414/419/420/421/423과
    같은 fixture로 tick11,928 fault가 반복 재현된 계보(N25 결정성)가 있으나, 값 22432는 이번 run에서만
    봤다. W15는 재현 1회를 필수로 둔다.
  - probe는 가드로 `P`를 읽지 않았다 — **게임이 실제로 읽은 `P` 값은 미측정**이다. 위 `[3,473,490..
    3,473,499]`는 `m`에서의 역산이지 직접 관측이 아니다.
  - `0x669c7c` 테이블의 **진짜 길이**는 여전히 미증명이다. 이번에 얻은 것은 `+0x700` 인덱스의
    상한 3759이지 보정표 레코드 수가 아니다.
  - `base`는 슬롯 구조체와 **다른 syscall**로 읽혔다(구조체 1,880B는 한 번에 읽힘). 같은 표본 안에서
    `K/m/f688`은 일관된 스냅샷이지만 `base`는 수십 µs 어긋날 수 있다. 값이 전 구간 상수 10이라
    이번 판정에는 영향이 없다.
  - **원본과 경로가 동일한데 후보만 죽는다는 점은 여전히 화해되지 않았다.** 이번 lap이 옮긴 것은
    "무엇이 오염됐나"(`+0x700`)까지이고 "왜 후보에서만"은 W15가 답해야 한다.
  - P2 near-cap **FAIL 판정 유지**. 기준을 낮추지 않았다. 제품 완료 아님.
  - 이 검수는 middle 역할의 독립 재계산이며 **사용자 마일스톤 승인이 아니다**.

  **검사 요약:** targeted **6 passed**, `SAFETY_PASS`, 원본 4경로 SHA 불변, source 변경 0
  (전체 `make check`는 N22 면제 요건 충족으로 생략), 게임 실행 0회, 커밋 0.

- 다음 한 가지: **work(Sonnet5/high)가 W15
  `docs/work/active/G2_UNIT_0x700_WRITER_ATTRIBUTION_LAP426.md`의 P-J를 수행한다** — 같은 fixture로
  재현 1회를 뜨면서 `[unit+0x388]`·`[unit+0x6fc]` 읽기 2개만 추가해, `+0x700=22432`가
  **정당 site의 잘못된 값**인지 **외부 write**인지 한 run으로 가른다. 그 결과가 정당 site면
  `0x40d79f`/`0x40f040` 입력(`[esi+0x388]`)을 거슬러 올라가고, 외부 write면 잔존 1200-bound site
  전수(lap414가 센 최소 3곳)를 `unit+0x700` 착지 가능성으로 정적 평가한다. 명령 바이트 패치는
  계속 범위 밖이며 `0x00414133`/`0x0043ee39`/`0x00422dc7`/`0x0040bc86~0x40bcfe`/`0x0040c1c2`/
  `0x48cba9`/`0x48c914`/`0x411ec0`은 패치 금지를 유지한다.

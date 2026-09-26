# 2026-09-20 KST | lap393 | G2 전비 장부 전역합 불변식 / middle 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, 중간 tier(진단·계획·확인).
  게임 코드 hands-on 수정 0. 게임 실행 0. 바이너리 변경 0. 커밋 0.
- 번호: 읽은 `loop/.lap_counter`=393(쓰기 0). 날짜: 세션 시작 2026-09-19T23:57+09:00,
  기록 시점 2026-09-20T00:03+09:00. 파일명은 기록 시점 기준.
- 가설: lap391 V2의 "표본 roster 최소>0 ⇒ 간격 내 `FUN_00444EF0` 발화 불가"가 불변식인가,
  그리고 "원본 cap1500 ⇒ 전역합 12000 ⇒ 랩 불가"가 산술 예시가 아니라 불변식인가.
- 예상 PASS / FAIL 조건: 두 주장 각각을 원본 바이트(주소·명령·경로)로 재유도하면 PASS,
  전제가 바이트로 지지되지 않으면 해당 주장을 UNKNOWN으로 정정한다. probe rc0 `failures=[]` 필수.
- 판정: **lap392 Astra의 이의 두 건 모두 처리. ①V2 전제 반증 → UNKNOWN 정정. ②cap1500 주장은
  불변식으로 승격(증명). ③신규 결정수치: 8인 균일 cap의 장부 안전 상한 = 4,095.**

## ① lap392 Astra 항목1 — V2는 UNKNOWN으로 정정한다 (Astra 이의 **인용**)

lap391 V2는 `FUN_00444EF0`을 "패배 owner의 전 유닛 일괄 흡수"로 보고, 표본 roster 최소가
`{112,136,145,144,144,112,133,138}`이므로 패배 owner가 0건 ⇒ 간격 안에서도 발화 불가라고 했다.
**그 전제가 원본 바이트에 없다.**

`0x444EF0` 본문(54 insn, `[0x444EF0,0x444F9A)`)을 재유도한 결과:
- `+0x200A`(roster count) / `+0x200C`(전비) / `+0x2010` / `+0x2012` 참조 **0건**. 패배 판정식이 없다.
- 구조는 slot 루프다: `esi=0..0x4B0`, 각 slot에 대해 존재확인(`0x416F40`) → owner==arg1 확인
  (`0x40F560`, `cmp ax,bx`) → `0x40F890`(transfer wrapper)로 owner를 arg2로 재지정.
  즉 **"owner arg1의 모든 유닛을 owner arg2로 넘긴다"**일 뿐 패배와 무관하다.
- 직접 caller **8개**: `0x4BE25F 0x4BF035 0x4BF97E 0x4BFF74 0x4C0281 0x4C1F8D 0x4C1F9C 0x4C1FAA`.
  **전부 `0x4BE000~0x4C2000` 한 구역**에 있다. cdecl이므로 마지막 push=arg1(넘겨주는 owner)인데
  7건이 **즉치(`7`,`4`,`7`,`6`,`7`,`7`,`6`)**, 1건(`0x4C1F9C`)이 로컬 플레이어 전역 `word[0xB63FC4]`다.
  8개 caller 어디에도 roster/전비에서 유도한 인자가 없다(probe가 창 동기화 후 전수 확인).
  주변은 미션 상태 전역(`0x975D20/0x975D24/0x975D2C`)·문자열(`0x4F5B28`)·메시지 호출이다.

⇒ `FUN_00444EF0`은 **패배 핸들러가 아니라 하드코딩 owner를 쓰는 캠페인/시나리오 스크립트 로직**이다.
따라서 "패배 0건 ⇒ 발화 불가"는 **비약**이고, V2는 불변식으로 성립하지 않는다.
**V2 → UNKNOWN으로 정정한다. lap392 Astra의 이의가 옳다.**
단 lap391이 재계산한 **수치 자체(M1~M4·위반7건·per-owner 범위)는 그대로 유효**하다. 철회되는 것은
gap-proof **추론**뿐이다. 또한 이것은 간격 내 랩/흡수가 실제로 일어났다는 뜻도 아니다.

부수 결과: 8인 자유대전(G2 fixture)은 캠페인 스크립트 구역을 타지 않으므로 `FUN_00444EF0`은
**그 fixture에서 애초에 도달 불가일 가능성이 높다**(caller 도달성 자체는 미추적 — 아래 한계 참조).

## ② lap392 Astra 항목2 — cap1500 주장은 **불변식으로 승격**한다 (증명)

Astra는 "조건부 산술 예시로만 제한하라"고 했으나, 필요한 전제 세 개가 모두 바이트로 성립한다.
`U_o = word[PlayerStruct_o + 0x200C]`라 하자.

**P1 — 장부 writer는 정확히 2개다.** `.text` 전 구간 선형 스윕(306,840 insn 디코드, 재동기 skip 42):
`+0x200C` 참조는 **전부 5건**뿐이다.
```
[R] 0043edfc  movsx edx, word ptr [ecx + 0x200c]   (생산 gate)
[W] 0043ee9b  add   word ptr [ecx + 0x200c], dx    (roster_add)
[W] 0043ef8b  sub   word ptr [ecx + 0x200c], dx    (roster_del)
[R] 0043f0e9  movsx eax, word ptr [esi + 0x200c]
[R] 0043f3b3  movsx eax, word ptr [ebp + 0x200c]
```
쓰기 2건은 둘 다 `word ptr`(16-bit), 읽기 3건은 전부 `movsx`(부호확장)다.
재동기 skip 42곳 ±8바이트 창에 `0x200C/0x200A/0x2012` 변위 바이트열이 **없음**을 별도 확인했다
(fail-open 차단). lap389의 F4 장부 폭·부호 주장은 이로써 전수 근거를 얻는다.

**P2 — 두 writer는 같은 유닛에 대해 같은 값을 쓴다(전역합 보존).** 두 tail의 비용 유도는
레지스터 pop 배치만 다르고 산술 골격이 **완전히 동일**하다(probe가 정규화 후 리스트 비교):
```
movsx edx, <unit id>    ; roster_add는 ax, roster_del은 di
lea eax,[edx+edx*2]; shl eax,4; sub eax,edx      ; *47
xor edx,edx; lea eax,[eax+eax*4]; shl eax,3      ; *1880  (UnitStruct stride)
mov dl, byte ptr [eax + 0x66b81d]                ; 유닛 type 바이트
lea esi,[edx+edx*8]; lea esi,[edx+esi*2]; lea esi,[esi+esi*2]; lea edx,[edx+esi*4]  ; *916
mov dx, word ptr [edx*4 + 0x9b5238]              ; 비용 테이블
```
⇒ `roster_del(u)` 직후 `roster_add(u)`는 **같은 값을 빼고 더한다**. 소유권 이전은
`ΣU_o`를 **정확히 보존**한다(유닛 type이 그 사이에 바뀌지 않는 한 — FO-1).

**P3 — 생산은 `used + cost <= cap`으로 막힌다.** 생산 gate `0x43EDA0`:
```
0043edfc movsx edx, word[ecx+0x200c]   ; used
0043ee03 movsx ecx, word[ecx+0x2012]   ; cap
0043ee0a movsx eax, ax                 ; cost
0043ee0d add  edx, eax
0043ee0f cmp  edx, ecx
0043ee11 jle  0x43ee1a                 ; 통과
0043ee13 xor  ax, ax / ret 8           ; 거부
```
따라서 **생산 경로만으로는 `U_o`가 `cap_o`를 넘을 수 없다**. 관측된 `5003>5000`은 cap 참조가
0건인 transfer 경로(lap389) 때문이며, 그 경로는 P2에 의해 전역합을 늘리지 않는다.

**⇒ 불변식:** 매 순간 `Σ_o U_o ≤ Σ_o cap_o`, 그리고 `U_o ≥ 0`이므로 `max_o U_o ≤ Σ_o cap_o`.
- 원본 cap1500: 상한 **12,000 ≤ 32,767** ⇒ **부호16 랩은 원리적으로 불가능**(증명됨, fixture 불필요).
- 목표 cap5000: 상한 **40,000 > 32,767** ⇒ **랩을 배제할 수 없다**. 랩에는 한 owner가
  전역 전비의 **81.92% 이상**을 동시 보유해야 한다(`32767/40000`).

정직한 표현: cap5000에서 "랩이 일어난다"가 아니라 **"엔진 구조만으로는 랩 없음을 증명할 수 없다"**이다.
실제 도달성은 여전히 게임플레이 의존이며 UNKNOWN이다(lap391 V3와 같은 선). cap≤4095에서는
게임플레이와 **무관하게** 불가능하다 — 이 차이가 이번 판정의 핵심이다.

## ③ 신규 — 장부 안전 상한은 **cap 4,095**다 (결정 수치)

`8 × cap ≤ 32,767` ⇔ `cap ≤ 4,095`. (`8×4095=32,760 ≤ 32,767 < 8×4096=32,768`.)

원본의 cap 즉치는 두 곳이며, 기존 `patches/population/fixed_supply_5000.py`가 바로 이 둘을 고친다.
핀 없이 원본에서 바이트를 재확인했다(probe P8):
| 파일 오프셋 | VA | 원본 바이트 | 의미 |
|---|---|---|---|
| `0x3FFD4` | `0x43FFD4` | `05 dc 05 00 00` | `add eax, 0x5DC` → `mov word[ebp+0x2012], ax` |
| `0x1B576` | `0x41B576` | `66 c7 00 dc 05` | `mov word ptr [eax], 0x5DC` |

⇒ **"8인 각 5000"이라는 목표 숫자는 원본 16-bit 부호 장부와 양립하지 않는다.**
`ESCALATE_SOL` §2 판정요청 2번에 대한 답이다. 선택지는 둘뿐이다:
- **A. cap ≤ 4,095**로 목표를 조정 — 원본의 랩 불가능성을 그대로 유지. 변경은 즉치 2개.
- **B. cap 5,000 유지** — `+0x200C`를 32-bit로 확장해야 하고, 이는 5개 명령 사이트 + PlayerStruct
  필드 폭 + **bulk save/load blob 포맷**을 함께 건드린다 ⇒ lap385/388이 굳힌 **저장포맷·즉치 fixup
  통합 blocker와 동일 성격**이며 현행 NO_GO 아래에 있다.

부수 근거 — 한 owner의 roster 상한은 마법수가 아니다. `roster_add` 입구는
`cmp word[ecx+0x200A], 0x4B0; jl`이고, roster 배열이 `[ecx + idx*4 + 0xD4A]`이므로
`0xD4A + 0x4B0*4 = 0x200A` — **배열 용량이 정확히 count 필드에서 끝난다**. 즉 1200은 배열 자체의
크기다. 초과 시 `0x465250` 오류 로그 후 `+0x200C`를 건드리지 않고 `ret 4`한다(장부 오염 없음).

## ④ lap392 Astra 항목3·lap391 §5 — 랩 트리거 fixture는 **만들지 않기를 권고**

lap391 §5가 승격 판정으로 올린 "랩 트리거 fixture를 만들 것인가"에 대한 middle 권고: **불필요**.
- cap ≤ 4095이면 ②가 **불가능을 증명**했다. 실행할 것이 없다.
- cap 5000이면 결정은 이미 ③에서 나온다. fixture는 "집중이 얼마나 어려운가"를 잴 뿐이고
  **판정을 바꾸지 못한다**(음성이 나와도 상한 40,000은 그대로다 — lap391 V3가 이미 겪은 함정).
- 게다가 ①에 따라 `FUN_00444EF0` 반복 유도는 캠페인 스크립트 경로라 8인 자유대전에서 재현 자체가
  의심스럽다. 새 게임 실행·새 생성 fixture 승인을 여기에 쓰지 말 것을 권고한다.

## 남은 fail-open (숨기지 않음)

- **FO-1** P2는 짝지어진 `roster_del`↔`roster_add` 사이에 유닛 type 바이트
  (`0x66B81D + 1880*id`)가 불변임을 가정한다. 이전 도중 type이 바뀌는 변신/승선이 있으면
  보존이 정확히 성립하지 않는다. 미추적.
- **FO-2** 비용 테이블 `0x9B5238`은 `.data`의 raw 크기를 넘는 런타임 초기화 영역이라
  **단일 유닛 최대 비용을 정적으로 읽을 수 없다**. 이번 불변식은 이 값이 필요 없지만,
  `roster상한 × max_cost` 형태의 별도 한계는 계산 불가다.
- **FO-3** save/load는 bulk blob으로 `+0x200C`를 복원하므로 두 writer 밖이다. 불변식은
  진행 중 플레이를 덮고 조작된 save를 덮지 않는다.
- **FO-4** gate `0x43EDA0`와 등록 `0x48BC00`은 별개 호출이다. 모든 생산 caller가 등록 직전에
  gate를 통과함을 전수 증명하지 않았다(TOCTOU 창 미측정). `0x48BC00`은 직접 caller 1개
  (`0x48B1EC`)·절대 dword 참조 0건이라 경로는 좁다.
- **FO-5** 원본 cap은 `<base> + 0x5DC`이고 `base = dword[esp+0x18]`(@`0x43FFD0`)를 정적으로
  풀지 않았다. 따라서 "원본=1500"은 `base==0`일 때만 단언된다. 5000 패치는 식 전체를 상수로
  바꾸므로 9/19 fixture의 cap 5000 자체는 영향받지 않는다.

## 보존 / 검증 / 한계

- 변경 파일(전부 uncommitted): probe `docs/history/laps/probes/20260919_lap393_middle_g2_supply_ledger_invariant_probe.py`
  (SHA256 `97a7679b218aef5bae4f6900fa304a4180305fc5ad29c92b9de36a08c73292f0`),
  본 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` §7, work 카드.
- 산출물(외부 temp, 메인레포 밖):
  `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap393_middle_defeat_invariant/probe_output.json`
  (SHA256 `237f5698ec67e077029c3a68f7ac4923aac4ffd828eaaf4ce68d4638f2df29d1`).
- probe 실행: `python3 docs/history/laps/probes/20260919_lap393_middle_g2_supply_ledger_invariant_probe.py`
  → **rc0 `failures=[]`**. 어떤 이전 lap의 스크립트도 import하지 않는다.
- 원본 SHA 재해시: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**. 후보 없음.
- Fast: `make check` **rc0, 715 passed 140.76s** + Ruff `All checks passed` + compileall +
  mypy 10파일 `Success` + `CONTEXT_PASS`. `checks/safety.sh check` **`SAFETY_PASS`**.
  Fast일 뿐이며 실제 앱/24k/144k/멀티 증거가 아니다.
- 환경/활성 인원/지도/군대/fixture: **신규 실행 없음**. 원본 EXE 정적 분석만.
- 게임 실행 0 / 바이너리 변경 0 / 원본·참고·공유 저장소 쓰기 0 / 커밋 0 / owned PID 0.
- 제품 코드 변경 0이므로 implementation-unchanged-streak를 리셋하지 않는다(러너 헤더 세션시작값=1).
  다만 이번 회차는 문서 반복이 아니라 **제품 목표 수치 자체를 바꾸는 판정**을 산출했고,
  다음 제품 카드가 사용자/Astra 결정에 직접 걸려 있으므로 `ESCALATE_SOL`로 올린다.
- 다음 한 가지: STATUS 참조. `ESCALATE_SOL` §7의 cap 결정(A/B)이 내려오면
  분기 A는 즉시 착수 가능한 work 카드다(아래 handoff).

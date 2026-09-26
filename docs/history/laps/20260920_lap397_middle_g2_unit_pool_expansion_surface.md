# 2026-09-20 | lap 397 | 목표 G2 (전역 UnitStruct 풀 1,200칸 확장 스파이크)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / **middle
  (진단·계획·확인)**. 게임 코드 hands-on 수정 없음. 게임 실행 0, 바이너리 변경 0, 커밋 0.

## 가설 / 사용자 관찰

사용자 2026-09-20 00:33 KST 지시로 **최우선이 전비 장부 → 전역 UnitStruct 풀 1,200칸 확장
실행 스파이크**로 바뀌었다(INBOX). 첫 성공 기준은 "격리 실제 게임에서 slot index 1,200 이상
개체 생성 → 기존 reader 관측 → 사망 → 슬롯 재사용"이며, 단순 `0x4B0` 상수 변경과 인접
상태영역 덮어쓰기는 **금지**다.

**이 스파이크가 실제로 무엇을 건드려야 하는지를 측정한 회차가 저장소에 하나도 없다.**
lap397 가설: 그 표면(surface)은 STATUS가 전제해 온 것보다 **작고**, 지금까지 G2 전체를 막아 온
저장포맷/PlayerStruct 통합 blocker의 상당 부분은 **이 스파이크의 임계경로가 아니다**.

## 예상 PASS / FAIL 조건

| ID | 측정 | PASS | 결과 |
|---|---|---|---|
| A1 | 6개 영역 기하 독립 재유도 | 5개 사이드카 전부 정확히 1200엔트리, pool_end==0x892410 | **PASS** |
| A2 | 각 사이드카가 slot-id 색인인가 count 색인인가 (바이트로) | 분류가 바이트에서 결정됨 | **PASS** |
| A3 | 할당자 `FUN_00442FA0`의 레이아웃 상수 열거 | 인코딩된 상수가 전부 잡힘 | **PASS** |
| A4 | 풀 변위 후보 986건의 stride 버킷 분포 | 버킷0 비율 확정 | **PASS (1.0)** |
| A5 | `age_end`~`catA_base` 3,200B 구멍이 비어 있는가 | 참조수 확정 | **PASS(측정) / 가설은 반증** |
| A6 | 재배치 공간 후보 | PE 기하 확정 | **PASS** |
| A7 | roster가 slot-id를 제한하는가 | 제한하지 않음이 바이트로 확정 | **PASS** |
| A8 | `0x892410` 별칭 179건 중 "pool end" 의미 개수 | 개수 확정 | **PASS (0건)** |
| A9 | 풀 base 정확값 참조 분해 | 115건 분해 | **PASS** |

## 변경 파일 / source fingerprint / 커밋

- `docs/history/laps/probes/20260920_lap397_middle_g2_unit_pool_expansion_probe.py`
  SHA256 `b0761f19a84e619b6973ff92021f1992f36cb58730404d324a42a64beaebe27f`
- `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md` (신규 work 카드)
- `docs/STATUS.md`(압축 전 원문 130줄 / SHA256
  `abaf1a9aa769b05b17967406b47644b6bed091213daa945af6a16453834b75b1` 을
  `docs/history/laps/20260920_status_lap397_precompaction.md` 에 먼저 보존한 뒤 갱신,
  종료 시 130줄 / `CONTEXT_PASS` / `## 지금 막힌 것` 정확히 1개.
  압축은 lap392 Astra 항목을 lap393 항목 끝으로 합친 1줄뿐이고 **원문 삭제 0**)
- `docs/feedback/INBOX.md`, 본 기록
- **커밋 없음(uncommitted).** `LOOP_ALLOW_COMMITS` 미설정.
- 제품 코드/패치/바이너리 변경 **0**.

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

- 원본 `Syw2plus/syw2plus_original.exe`
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — **회차 종료 시 재해시 불변**.
- 후보 없음. **게임 fixture 없음** — 이번 회차는 순수 정적 측정이라 Wine/Xvfb/save 미사용.
- 참고 디컴파일은 형제 읽기전용 트리 `../Syw2plus_re/analysis/ghidra_output/`에서 읽기만 했다.

## 실행 명령 / 로그 / 캡처 경로 및 해시

```
.venv/bin/python docs/history/laps/probes/20260920_lap397_middle_g2_unit_pool_expansion_probe.py \
  --output .../g2_capacity/20260920_unit_pool_expansion/lap397_middle_static_surface/probe_output.json
```

- probe **rc0 `failures=[]`**
- 산출물 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/
  20260920_unit_pool_expansion/lap397_middle_static_surface/probe_output.json`
  SHA256 `dd7269662c342692a47a709784f8e8baeb36b104989d8c151a082f1dde79dd41`
- `checks/safety.sh check` → **`SAFETY_PASS`**
- `make check` 결과는 「측정값」 절 말미에 기록.
- 캡처 없음(게임 미실행).

## 측정값 / 판정

### A1 — 기하 (독립 재유도, `tools/g2_unit_pool_xrefs.py` import 안 함)

풀 `[0x0066B790, 0x00892410)`, stride `0x758`=1880, 1200칸, 2,256,000 B.
`pool_end == 0x892410 == bulk start`. 사이드카 5개 전부 정확히 1200 엔트리:
existence `0x8990C8`(2B), age `0x899A28`(2B), active `0x974FA8`(2B),
catA `0x89B008`(4B), catB `0x89C2CA`(4B). existence 끝 == age base(인접). **PASS**

⇒ **풀은 bulk 바로 아래에 밀착해 있어 위로 자랄 공간이 0이다.** 사용자가 금지한 "다음
상태영역 덮어쓰기"는 곧 단순 상수 확장의 필연적 결과이며, 이번 측정이 그 금지를 **독립 확인**한다.

### A2 — slot 색인 vs count 색인 (`FUN_0048BC00` 52 insn 바이트에서 결정) **[핵심]**

| 영역 | index 레지스터 생산자 | 판정 |
|---|---|---|
| existence | `movsx eax, word [esi+0x29c]` (유닛의 slot id) | **SLOT_INDEXED** |
| age | `movsx edx, word [esi+0x29c]` | **SLOT_INDEXED** |
| active | `movsx eax, word [0x975908]` (자기 count) + `inc [0x975908]` | **COUNT_INDEXED** |
| catA | `movsx ecx, word [0x89c2c8]` + `inc [0x89c2c8]` | **COUNT_INDEXED** |
| catB | `movsx eax, word [0x89d58a]` + `inc [0x89d58a]` | **COUNT_INDEXED** |

**결론: slot-id로 색인되는 영역은 정확히 pool / existence / age 3개뿐이다.**
active·catA·catB는 **살아 있는 유닛 수**로만 자라는 packed list이고 slot id를 원소로 담을 뿐이다.
원소 폭은 signed WORD / DWORD라 slot id `[1200, 32767)`이 그대로 들어간다.
⇒ 살아 있는 유닛이 1200 미만인 한 **이 3개는 확장할 필요가 없다**.

### A3 — 할당자 `FUN_00442FA0` (25 insn) 과 전멸 루프

인코딩된 레이아웃 상수는 **정확히 3개**다:

| 주소 | 바이트 | 의미 |
|---|---|---|
| `0x00442FAC` | `b9 2a 9a 89 00` `mov ecx,0x899a2a` | 스캔 시작 = age_base+2 |
| `0x00442FB1` | `66 83 b9 a0 f6 ff ff 00` `cmp word [ecx-0x960],0` | existence 상대 변위 = **-2N** |
| `0x00442FD1` | `81 f9 88 a3 89 00` `cmp ecx,0x89a388` | 스캔 배타적 끝 = age_base+2N |

정책: existence[slot]==0인 자유 슬롯 중 age 최대값(LRU형)을 고른다. slot 0은 할당 안 하고,
꽉 차면 0을 돌려준다 ⇒ 현재 실사용 namespace는 **1..1199**(STATUS의 "global1199"와 일치).
전멸 루프 `FUN_00443170`: `0x0044317D` `81 fe b0 04 00 00` `cmp esi,0x4b0`. **PASS**

⇒ N칸으로 바꾸려면 위 3개 + 전멸 루프 1개, **총 4개 상수**만 손대면 된다.

### A4 — 풀 재배치 표면 **[핵심]**

풀 범위에 드는 base/index 변위 후보 **986건**, 절대메모리 **0건**, 범위내 즉시값 **30건**.
stride 버킷 히스토그램: **`{0: 986}`** — 버킷0 비율 **1.000**, 이상치 **0건**.

즉 986건 전부가 `[reg(+index) + 0x66B790 + field]`(field < 1880) 꼴의 평범한 slot-색인
필드 접근이다. ⇒ **균일 +delta 재배치가 986건 전부를 건전하게 번역한다.** 개별 분석이 필요한
변위 site는 **0건**이다. (Ghidra가 `DAT_0066BA20[slot*0x3ac]`로 보여 준 것이 같은 모형이다.)

### A5 — `age_end`~`catA_base` 구멍: **가설 반증(중요한 음성 결과)**

`[0x0089A388, 0x0089B008)` 3,200 B. "existence+age를 제자리에서 N≤2000까지 키울 수 있다"는
가설을 세웠으나, 그 구간 참조가 **9건 발견**되어 반증됐다:

```
0x0043e887 mov di,  word [esi*2 + 0x89a388]
0x0047f447 cmp word [eax*2 + 0x89a388], 0
0x0047f8de cmp word [ecx*2 + 0x89a388], ax
0x0049b373 cmp word [esi*2 + 0x89a388], 0
0x004a7f3f movsx edx, word [ecx*2 + 0x89a388]
0x0048d204 mov cx,  word [eax + 0x89a396]
0x0048d215 cmp cx,  word [eax + 0x89a3b6]
0x004b1bb9 cmp cx,  word [ecx + 0x89a398]
(+ 0x00442fd1 은 A3의 할당자 종료 비교)
```

`[reg*2 + 0x89a388]` 형태가 5건 ⇒ **`0x89A388`은 또 하나의 살아 있는 WORD 배열의 base다.**
⇒ **제자리 확장은 불가. existence/age도 재배치해야 한다.** 판정 **NOT_FEASIBLE(제자리 확장)**.

### A6 — 공간

`.text 0x401000`, `.rdata 0x4E5000`, `.data 0x4EC000→0x0108BA38`(가상 12,188,216 B / raw 53,248 B,
즉 대부분 BSS), `.rsrc 0x0108C000`. `SizeOfImage` 끝 `0x0108F000`.
bulk 끝 `0x975D8C` 위로 이미지 안에 7,443,060 B가 있으나 **그 구간에는 다른 전역들이 산다**
(비용표 `0x9B5238`, 맵 `0xB43728`, 섹터버킷 `0x943D0A`, 로컬플레이어 `0xB63FC4` 등) ⇒ **비어 있지 않다.**
⇒ 새 공간은 `0x0108BA38` 위로 **이미지를 늘려** 확보해야 하며, 이는 lap382~388이 이미 만든
`base_preserving_storage_layout_v1.py`/`.pelayout` 계산기의 용도와 정확히 일치한다
(lap385 R3: 첫 32bit 초과는 N=2,259,703이므로 주소공간 여유는 충분).

N칸 풀 크기: 1201→2,257,880 B / 1250→2,350,000 / 1500→2,820,000 / 1999→3,758,120 B.

### A7 — roster는 slot id를 제한하지 않는다 **[핵심]**

`roster_add 0x0043EE30` 입구 `0x0043EE30` `66 8b 81 0a 20 00 00` `mov ax, word [ecx+0x200A]`
뒤의 `cmp ax,0x4B0; jl`은 **그 owner의 유닛 개수**를 1200으로 묶는다. roster 배열은
PlayerStruct `+0x0D4A`부터 DWORD 1200칸이고 `0x0D4A + 1200*4 == 0x200A`(검증됨)라 count 필드와
정확히 맞닿는다. 저장되는 값은 slot id(DWORD)다.

⇒ **유닛 1200기 미만을 가진 owner는 PlayerStruct를 전혀 바꾸지 않고 slot id ≥ 1200을 담을 수 있다.**
⇒ PlayerStruct stride / bulk 저장 레이아웃은 **이 스파이크의 임계경로가 아니다**.
이것이 lap385/388이 굳힌 "저장포맷·즉치 fixup 통합 blocker"와 이번 스파이크를 갈라놓는 지점이다.
(통합 blocker 자체는 **무효가 아니며** owner당 1200기 초과나 저장호환에는 그대로 살아 있다.)

### A8 — `0x892410` 별칭 179건: **"pool end" 의미 0건** **[핵심 · 위험 해소]**

lap388이 경고한 3중 별칭(`unit_pool_end` / `bulk_start` / `live_game_state_base`)을 분해했다.

| 형태 | 건수 | 의미 |
|---|---|---|
| `mov ecx, 0x892410` | **177** | thiscall `this` 포인터 = bulk 게임상태 객체 |
| `push 0x892410` | **2** (`0x00440F07`, `0x004412D7`) | 핀된 save/load blob source |
| bound 꼴(`cmp`/`sub`/`lea`/…) | **0** | — |
| base/index 메모리 피연산자 | 0 | — |

두 `push` site는 lap385/388이 핀한 save `0x440F02` / load `0x4412DC`와 **정확히 일치**한다.

⇒ **풀을 재배치해도 이 179건은 한 건도 수정할 필요가 없다.** 별칭은 재배치 방향에서 깔끔히 갈린다.
**판정: lap388이 남긴 별칭 위험은 이 스파이크 범위에서 해소.**
*fail-open:* 디코딩된 피연산자 한정. 계산/별칭 포인터로 만들어진 bound는 배제하지 않았다.

### A9 — 풀 base 정확값 참조 115건 분해

즉시값 5건: `0x0040F4B7 mov edi,0x66b790`(save_roster), `0x0040F4F8 mov esi,0x66b790`(load_roster),
`0x00422DC2 mov esi,0x66b790`, 그리고 **`cmp` 2건** `0x00421349 cmp ebx,0x66b790` /
`0x0048F4B4 cmp edx,0x66b790`(포인터 하한 유효성 검사로 보임).
메모리 변위 110건: `lea` 109 + `mov` 1(`0x0044301B mov al,[esi+0x66b790]`).

⇒ **풀 재배치 site 총계 = 986(변위) + 30(범위내 즉시값) = 1,016건**, 그중 **개별 판단이 필요한 것은
`cmp` 2건뿐**이고 나머지는 균일 delta다.

### 게이트

- `make check` **rc0 / 715 passed 139.80s** + Ruff `All checks passed` + compileall
  + mypy 10파일 `Success` + **`CONTEXT_PASS`**. Fast일 뿐 실제 앱/24k/144k/멀티 증거가 아니다.
- `checks/safety.sh check` → **`SAFETY_PASS`**
- 원본 EXE 재해시 `b56986e0…c9c08a8ac` **불변**.
- 원본/참고/공유 저장소 쓰기 0, 게임 실행 0, 커밋 0.

## 판정 (스파이크 첫 성공 기준에 대한 middle 판정)

**`FEASIBLE` (구조적으로), 단 실제 도달성은 다음 work 회차의 실행이 판정한다.**

근거 요약 — 스파이크가 **반드시** 건드려야 하는 것:

1. **재배치 3영역:** unit_pool / existence / age (A2). 제자리 확장은 A1·A5로 **불가**하므로
   늘린 이미지 꼬리(A6)로 **옮기면서** N칸으로 키운다.
2. **상수 4개:** 할당자 3개 + 전멸 루프 1개 (A3).
3. **fixup 1,016건:** 풀 (A4·A9). 986건은 균일 delta, 개별 판단은 `cmp` 2건.
   existence/age는 별도(기존 인벤토리 기준 각각 수십 건 규모).

스파이크가 **건드릴 필요가 없는 것** (이번 회차의 실질 성과):

4. active / catA / catB — count 색인이라 slot namespace가 커져도 넘치지 않는다 (A2).
5. PlayerStruct roster / stride / bulk 저장 레이아웃 — count 제한이지 slot-id 제한이 아니다 (A7).
6. `0x892410` 별칭 179건 — 전부 bulk base 의미다 (A8).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **가장 큰 남은 위험(work가 먼저 닫을 것):** 986건은 **디코딩된 후보**이지 "풀 참조임이 증명된"
  것이 아니다. 버킷0 집중 1.000이 강한 정황이지만, base 레지스터가 실제로 slot*1880인지는
  명령 하나만으로는 증명되지 않는다(**FO-1**).
- **FO-2:** A5/A8/A9 전부 디코딩된 피연산자 한정. 계산/별칭 포인터 경유 접근은 덮지 않는다.
- **FO-3:** `0x89A388`에서 시작하는 배열의 **정체와 크기가 UNKNOWN**이다. existence/age 재배치
  시 이 배열과의 인접 관계가 깨질 수 있다.
- **FO-4:** `cmp` 2건(`0x421349`, `0x48F4B4`)의 상한 짝을 찾지 못했다(`0x892410` 대상 `cmp` 0건).
  포인터 범위 검사의 상한이 어떻게 닫히는지 UNKNOWN.
- **범위 외(사용자가 명시 유예):** bulk 저장/불러오기 포맷, LAN. **후속 필수 blocker로 유지**한다.
  풀이 이동하면 save_roster/load_roster(`0x40F4B0`/`0x40F4F0`)는 즉시값 2개가 따라가므로 동작하나,
  **저장 파일 간 호환성은 깨진다** — 스파이크 PASS 조건은 아니지만 제품 조건이다.
- **무효화하지 않는 것:** lap385/388 통합 blocker(owner당 1200기 초과/저장호환), lap389 A NO_GO,
  `loop/ESCALATE_SOL` §9의 F4 cap 판정(미해결로 **그대로 열려 있음**; 사용자 우선순위 변경으로
  후순위가 됐을 뿐 철회된 것이 아니다).
- **독립 검수 상태:** 이 회차는 middle 자체 산출이므로 **다음 새 세션이 독립 검수**한다.
  probe rc0는 위 바이트 사실만 인증하며 제품/런타임/마일스톤 승인이 **아니다**.
- **사용자 승인:** 불필요(관측 전용, 새 fixture 없음, 게임 미실행).

## 다음 한 가지

`docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md` 의 work 카드 **W3**를 다음 work
회차(`claude-sonnet-5`/high 또는 Luna/high)가 수행한다. implementation-unchanged-streak가
이 회차로 **2**가 되므로 다음 회차는 **반드시 제품 코드/바이너리/실행 증거를 늘려야 한다.**

# 2026-09-28 | lap 752 | 목표 G5 (middle: v8 기준 (F) 최종 재검수 — S3 판정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·컨펌).
  게임 코드·EXE·probe 수정 없음(문서만). 게임 실행 0회.
- 가설 / 사용자 관찰: STATUS "다음 한 가지" — lap751이 "재시작=유닛 해체(dec) 경로"와 "초기메뉴 전환은
  fixture 무관 env 제약"을 확정했으니, middle이 S3(초기메뉴→새 게임 선택 이월)를 analogy로 `BLOCKED(env)`
  수용할지, 재시작/새 게임 초기화가 같은 함수인지 정적 대조까지 요구할지 판정한다.
- 예상 PASS / FAIL 조건: 원본의 새 게임 초기화가 레거시 선택을 **간접**(this+오프셋·블록 memset)으로
  비우지 않는다면 v8과 원본의 게임 시작 불변식이 같아 S3를 analogy+env로 수용(PASS). 간접 초기화가
  있으면 v8의 새 배열(`0x0108C000`, 저장 창 밖)은 그 초기화에서 빠지므로 HOLD + 최소 v9.
- 변경 파일 / 커밋: 문서만 — 이 파일, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`,
  `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(lap752 섹션 추가). 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA: 보호 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` =
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(세션 중 재확인).
  v8 재빌드 `/tmp/lap752/v8.exe` = `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`(기록 일치).

## 실행 명령 (이번 세션, 읽기 전용 정적 분석)

1. capstone 헬퍼(`/tmp/lap752/x86d.py`, 저장소 밖)로 원본 `.text` 디스어셈블.
2. `0x412d90`(선택 토글: `[esp+..]==1` 추가 → `0x412e6e` inc, 아니면 제거 → `0x412ed2` dec) 호출자 11곳 확인.
3. `.text` 전체에서 저장 창 기저 `0x892410` 즉치 179건 분류 = `mov ecx,0x892410`(thiscall) 177 + `push` 2
   (`0x440f07` 저장, `0x4412d7` 로드). **this-상대 변위 `0x6c14`/`0x6c18`(= `0x899024-0x892410`,
   `0x899028-0x892410`) 스캔** → 각 1건, 둘 다 `0x4a3060` 함수 안.
4. v8 재빌드 후 같은 지점 바이트·`0x0108C000` 참조 전수 재확인.
5. `make check`(로그 `/tmp/lap752/make_check.log`), `checks/safety.sh check`, `checks/context_limits.py check`.

## 재계산·정적 결과

### 새 결함 경로 H-NEWGAME-INIT (정적 확정, 런타임 미검증)

- **원본 `0x4a3060`(게임 상태 객체 `this=0x892410` 초기화)**:
  `0x4a3067 mov ecx,0x38e5f; xor eax,eax; mov edi,esi; rep stosd` — 저장 창 전체
  `0x892410..0x975D8C`(`0x38e5f` dword = `0xE397C` 바이트)를 0으로 채운 뒤, 명시적으로
  `0x4a3168 mov dword ptr [esi+0x6c14], ebx`(ebx=0, **레거시 선택 count**) 와
  `0x4a31eb..0x4a321a` 20회 루프(`[esi+0x6c18+4k]` word/word = **레거시 선택 엔트리 20칸** 0,
  `[esi+0x6c68+2k]`·`[esi+0x6c90+2k]` 두 20-word 배열 0)를 수행한다.
- 호출자 3곳 = `0x41b9c0`(in `0x41b9b0`), `0x41bc4f`(in `0x41bc40`), `0x4c3e59`(in `0x4c3e50`) — 전부
  `mov ecx,0x892410` 직후 호출, 다음이 `call 0x446370`. 2026-09-17 G2 기록
  (`docs/history/laps/20260917_g2_priority_restart.md:324`, `..._storage_lifecycle_contract_review.md:9`)이
  이미 "Original newgame `424D73→41B9B0→4A3060`" 및 "초기화 4A3060의 세 호출자는 이 블록을 zero"로
  확인한 것과 일치한다. 즉 **원본은 모든 게임 시작에서 선택 count=0·엔트리 0을 직접 보장**한다.
- **v8**: `0x4a3168` 바이트 `89 9E 14 6C 00 00` 그대로(레거시 count만 0), `0x4a3067` bulk memset 그대로
  (저장 창만). 새 배열 `0x0108C000..0x0108C0CC`(count+50칸)는 저장 창 밖이라 **어느 게임 시작 초기화도
  비우지 않는다.** v8 전체 `0x0108C000` 참조 = `.text` 10(inc/dec/소비자 읽기, 0 채우기 없음) + `.rsrc` 2
  (저장·로드 래퍼). `CONTROL_GROUP_BASE 0x0108C100` 참조 0건(v2 이후 부대는 unit `+0x344`) → 초기화 대상 아님.
- 따라서 v8에서 새 게임 시작 시 새 배열이 비어 있는 것은 **직전 판 해체 중 선택된 유닛마다 `0x412d90`
  제거(dec)가 불렸을 때만** 성립한다. lap751 ①은 "다시하기"에서 그것이 성립함을 보였지만, 원본은 그
  경로와 **독립적으로** 4A3060에서 다시 0을 보장한다 — v8은 이 이중 보장 중 하나를 잃었다. 추가로 제거
  함수 `0x412d97`은 `word [0xb93988]==1`이면 아무것도 하지 않고 반환한다(의미 미확인) — 해체 경로가
  항상 dec를 한다는 가정도 정적으로 닫히지 않는다.
- 결론: lap751 analogy("재시작이 해체로 비우니 새 게임도 그럴 것")는 **원본 불변식과 v8 불변식이 다르다는
  사실을 덮는다.** S3를 `BLOCKED(env)`+analogy로 수용하지 않는다. 대신 원본 불변식을 복원하는 1지점 v9가
  싸고 결정적이며, S3 실측(초기메뉴, env 불가) 없이도 게임 시작 경로를 직접 시험할 수 있다(아래).

### 부수 관찰(비차단)

- `0x899078..0x8990C7`의 두 20-word 배열(`this+0x6c68`, `+0x6c90`)은 절대참조 0, this-상대 참조는 이
  초기화 루프 1건뿐(`0x6c68` 변위 0건, `0x6c90` 1건). 선택 칸 인덱스 소비자로 쓰인 흔적은 이번 스캔에서
  없음 — (A) 표에 "초기화 전용, 소비자 미발견"으로 한 줄 보완 권고.
- (A) 정적 전수 표(`analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`)는 절대주소
  리터럴만 셌기 때문에 이 this-상대 쓰기 2건(`0x4a3168`, `0x4a31ff` 루프)을 놓쳤다 → (A)도 보완 필요.

## 항목별 판정 (v8 기준, lap750 대비 변경분만)

| 항목 | 판정 | 메모 |
|---|---|---|
| A 정적 전수 | PASS(보완 필요) | this-상대 초기화 쓰기 2건(`0x4a3168`/`0x4a31eb` 루프) 누락 — v9 work가 표에 행 추가. |
| F 저장/로드 | **HOLD(좁음, 원인 특정)** | S1/S2/S4 PASS, S5 정적 귀속 수용 유지. **S3 = H-NEWGAME-INIT 정적 확정**(원본 4A3060의 선택 0 보장이 v8 새 배열에 미적용). analogy 수용 거부. |
| 나머지 B~E·G·H | lap750 판정 유지 | |

**종합: G5 v8 = `HOLD(좁은 조건부)` 유지 — 사용자 milestone 재상정·G1 착수 안 함.** 남은 것은 v9 1지점과
그 게임 시작 경로 실측뿐이다.

## 다음 한 가지 (work tier, 구현 우선, 1 lap) — v9

1. **v9 빌드**(`patches/selection/g5_selection_cap50_v9.py`, v8 위 1지점): `0x4a3168` 6바이트
   `89 9E 14 6C 00 00`을 `E9 <rel32 cave>` + `90`으로 바꾸고, v7/v8 `.rsrc` 실행 cave의 빈 곳에
   `mov [esi+0x6c14],ebx; push edi; push ecx; push eax; mov edi,0x0108C000; mov ecx,0x33; xor eax,eax;
   rep stosd; pop eax; pop ecx; pop edi; jmp 0x4a316e`. (DF는 같은 함수가 이미 `rep stosd`를 쓰므로 clear
   전제 동일, `0x4a316e` 이후 플래그 소비 없음 — work가 재확인.) 0x33 dword = count+50칸(`0xCC` 바이트).
   pytest: old bytes 핀, 새 바이트·cave 디코드·원본→v8→v9 결정적 재빌드, v8 대비 diff 범위 고정.
2. **게임 시작 경로 귀속(gdb 또는 로그 bp, 1회):** 순정 솔로 로비에서 게임 시작과 "다시하기" 각각에서
   `0x41b9c0`/`0x41bc4f`/`0x4c3e59` 중 무엇이 불리는지 기록(3곳 모두 같은 4A3060을 부르므로 v9는 어느
   쪽이든 덮음 — 귀속은 증거용).
3. **falsifiable paired probe(초기메뉴 불필요):** 게임 시작 직전(로비) 또는 "다시하기" 직전에 새 배열에
   가짜 stale 상태(count=50, 엔트리 50칸 = 선택 플래그가 없는 유닛 슬롯 ID)를 메모리 쓰기로 심고
   (선택 플래그 byte는 건드리지 않아 dec가 안 불리게) 게임 시작/재시작 후 50칸 dump.
   기대: **v8 = stale 잔존(갭 실증, FAIL 예상)**, **v9 = count 0·50칸 0(PASS)**, 원본 대조 = 레거시
   `0x899024/0x899028`에 같은 가짜를 심으면 4A3060이 0으로 만든다(PASS). v8이 잔존하지 않으면(다른 경로가
   비움) 그 주체를 기록하고 v9 불필요로 판정 — 사전 등록한 대안 해석.
4. 회귀: `make check`, v9로 S1/S2/S4(`tools/g5_stale_tail_probe.py`) + lap747 핵심 coverage 1회, 크래시 0,
   `source_unchanged`. (A) 표에 this-상대 행 추가.
5. 결과가 PASS면 새 middle이 F만 재검수 → 사용자 milestone 재상정(알려진 제한: G 멀티 BLOCKED(env), 부대
   미지정 선택 로드 후 20기, 미니맵/능력 v UNKNOWN, 건설·승선 N/A, S3 초기메뉴 UI 자체는 env로 미실측이나
   게임 시작 초기화는 v9 실측으로 커버, S5 정적 귀속).

## 검증

- `make check` = **1115 passed, 5 skipped(880.57s)**, ruff/mypy/`CONTEXT_PASS`, exit 0
  (`/tmp/lap752/make_check.log`). `checks/safety.sh check` = `SAFETY_PASS`. 문서 변경만이라 소스 동작 불변.
- 게임 실행 0회, 원본/참고 저장소 쓰기 0, 게임 사본 생성 0, 제품 코드 0 변경.

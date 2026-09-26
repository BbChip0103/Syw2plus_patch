# 2026-09-26 | lap 650 | 목표 G5 — strategy 접근 전환 판정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(세션 표기 Opus 5.5) / strategy(상위 방향, 01:55 운영자 위임 "strategy(Opus 5.5)가 접근 전환 판정") / 기본. 게임 코드·패치·바이너리 수정 없음.
- 가설 / 사용자 관찰: 01:55 운영자 결정은 (a) 진입/반환 breakpoint, (b) 패치 사이트 이분 탐색, (c) 스택 프레임 50칸 확장 중 하나를 고르라고 했다. 새 실행 없이 기존 raw(lap647/649)와 원본 디스어셈블(읽기 전용)을 대조한 결과, crash는 **lap644가 넓힌 FUN_0041DC40 프레임이 옮긴 word 버퍼를 다 담지 못하는 자기 패치 결함**으로 귀속된다. 판정: **(c)의 구체화, `FEASIBLE`**. (a)/(b)는 채택하지 않는다.

## 귀속 근거 (재현 가능한 계산)

원본 `b56986e0…` FUN_0041DC40 prologue/epilogue(`objdump -d -M intel --start-address=0x41dc40`):
`sub esp,0x98; push ebx; push ebp; push esi; push edi` … `pop×4; add esp,0x98; ret` (exit 두 곳 `0x41E1EC`, `0x41E20A`).
따라서 push 뒤 기준 esp를 B라 하면 **반환 주소 = [B + 0x10 + frame]**.

현재 후보(`patches/selection/g5_selection_cap50_v1.py` SELECTION_CONSUMER_LIMIT_SITES): frame `0x98→0x230`, word 버퍼 `[esp+ecx*2+0x80]→[esp+ecx*2+0x200]`(`0x41DE8A`·`0x41E010`·`0x41E141`·`0x41E16F`·`0x41DEBD`·`0x41E04C`·`0x41DC53`).
- 반환 주소 = B+0x240. word 버퍼 index i 주소 = B+0x200+2i → **i=32·33이 반환 주소를 덮는다**(50개면 B+0x263까지, 0x24바이트 초과).
- lap647 raw(`temp/Syw2plus_patch/20260926_lap647_g5_exception_trace_gate/gdb-module.raw`): `0x41E1D6`(push 3개 뒤 call 직전) ESP=`0x31F800` → B=`0x31F80C` → B+0x240=`0x31FA4C` = crash 반환 슬롯, crash ESP=`0x31FA50`(=ret 직후). 완전 일치.
- EIP `0x04810486` = 하위 `0x0486`(idx32) | 상위 `0x0481`(idx33) 16비트 핸들 쌍. 이전 `0x0488048B`, `0x047A0480`도 같은 패턴(실행마다 핸들만 다름). 실행 주소가 rwx 영역(`0x4f9000–0x108d000`)이라 쓰레기 코드가 돌다 write fault가 난 것이며, 별개 원인이 아니다.
- 선택 36(≥34)에서 항상 죽고 20~32에서는 안 죽는 관측과 맞는다.
- lap649 watch hit(`0x31FA4C`, 값 `0x02000001`, ESP `0x0021F688`, PC Wine libc)는 드래그 전 메시지 처리 중 같은 스택 슬롯의 정상 재사용이다(주변 값이 HWND `0x00020056`·Wine DLL 주소). 원인과 무관한 노이즈이므로 고정 주소 watchpoint 방식은 폐기한다.

부수 20 전제: `0x41DC4C mov ecx,0xa` + `rep stosd`(`0x41DC5A`)가 word 버퍼를 **20칸(40바이트)만** 0으로 초기화한다. 50칸이면 `0x19`(25 dword)가 필요하다.

함수 전 범위(`0x41DC40–0x41E211`) capstone 스캔: `[esp+disp]`에서 disp≥0x98(인자·호출자 프레임 접근)은 **없음**, `add esp,0x98`/`ret`는 위 두 곳뿐이다. 따라서 frame 상수 변경은 다른 esp 오프셋에 영향을 주지 않는다.

## 다음 work 지시 (middle 없이 바로 구현·실행)

1. 후보 빌더 SELECTION_CONSUMER_LIMIT_SITES에서 frame `0x230`→**`0x270`**(3곳: `0x41DC40` sub, `0x41E1EC`/`0x41E20A` add). 조건: `0x200 + 2*50 = 0x264 ≤ 0x270 + 0x10`에서 반환 슬롯 0x280. dword 목록 `[esp+0x30]+4*50=0xF8 < 0x200`.
2. `0x41DC4C` `b9 0a 00 00 00`→`b9 19 00 00 00`(word 버퍼 50칸 초기화). old bytes exact 검증·원복 테스트 포함.
3. 회귀 테스트(정적): 후보 bytes에서 frame·버퍼 오프셋·clear count를 읽어 `buf_off + 2*TARGET_CAPACITY ≤ frame + 0x10` 및 `clear_dwords*4 ≥ 2*TARGET_CAPACITY`를 assert한다. 기존 10개 targeted test 유지.
4. 실행: lap642~649와 같은 fixture(solo owner0, type2×55 dense 7×8, 1600×1200, tick gate + 동일 좌표 retry)로 후보 fresh 실행. 원본 20 대조는 기존 증거 유지(원본 불변).
5. 측정식: PASS = 드래그 후 crash 없음 **그리고** 선택 unique=50(55 중) **그리고** 이동 명령 50. FAIL-A = crash 재발 → EIP·ESP 기록 후 `ESP-4`가 이 함수 B+0x280인지 대조(같으면 계산 오류 재검, 다르면 다른 함수). FAIL-B = crash 없이 선택<50 → 다른 20 전제(표시/명령 패커 `FUN_004AE550`)로 넘어간다.
6. FAIL-A이고 다른 함수일 때의 fallback만 (a) 변형을 쓴다: 선택 base/end를 참조하는 함수(DIRECT_SITES/END_SITES가 속한 함수)의 `ret`에 조건부 breakpoint(`*(unsigned*)$esp`가 EXE text 밖이고 `&0xF000F000==0`)를 건다. 고정 주소 watchpoint는 쓰지 않는다.
7. PASS 뒤 순서: 50/51 경계 → command50 → canary/save/load → `make check`. 사용자 마일스톤 승인은 별도다.

- 예상 PASS / FAIL 조건: 이번 strategy 회차 PASS = 귀속이 기존 raw와 수치로 일치하고 다음 work가 수행할 단일 변경·측정식이 결정됨. 실행 증거는 다음 work가 만든다.
- 변경 파일 / source fingerprint / 커밋: 이 파일, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/history/20260926_lap650_escalate_sol_archive.md`(기존 `loop/ESCALATE_SOL` 전문 보존 후 해제). 제품·패치·테스트·바이너리 0, 커밋 0(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용 디스어셈블, 불변); 후보 `7c6e372a…`(lap649, 이번 회차 미실행); fixture는 lap649와 동일하며 이번 회차 실행 0.
- 실행 명령 / 로그: `objdump -d -M intel --start-address=0x41dc40 …`(원본 읽기), `.venv/bin/python` capstone 함수 스캔(stdout만 사용, 산출 파일 없음), lap647/649 raw 읽기.
- 측정값 / 판정: 귀속 계산 PASS(0x31F80C+0x240=0x31FA4C, crash ESP 0x31FA50 일치); G5 제품 판정 UNKNOWN(실행 0); 50/51·command50·save/load SKIP.
- 회귀 / 남은 위험: 0x270으로 넓힌 뒤에도 같은 함수의 다른 20 전제(표시 루프 등)나 다른 함수의 20 전제가 남을 수 있다 → 측정식 FAIL-B/fallback으로 처리. 스택 0x40 추가 사용은 메인 스레드 스택(1MB 영역)에서 무시 가능. 제품 코드 없는 회차는 이번 1회(연속 한도 2 이내); 다음은 반드시 work 구현·실행이다.
- 이번 회차 검사: `python3 checks/context_limits.py` → `CONTEXT_PASS`, `bash checks/safety.sh check` → `SAFETY_PASS`, targeted pytest(`patches/selection/test_g5_selection_cap50_v1.py tests/test_g5_selection_inventory.py`) → 10 passed. `make check` SKIP(문서 회차, 제품 변경 0).
- 다음 한 가지: 위 1~5를 work가 즉시 구현·실행한다.

판정: **`FEASIBLE(consumer_frame_0x230_too_small_return_slot_at_B+0x240)`**.

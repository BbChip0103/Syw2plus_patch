# G4 W2R — load wrapper link/ABI 최소 수리

- 발행: lap625 middle. lap624의 bridge build 실패를 current source·컴파일 산출물·pinned 원본 disassembly로 독립 재현한 뒤 발행한다.
- 단일 가설: i386 MinGW 심볼 장식과 cdecl stack/return 보존을 기존 W2 계약대로 바로잡으면, W2 bridge가 링크되고 fresh exact-one gate로 복귀할 수 있다.
- 범위: `tools/inmm_stub/ai_shadow.c`, `tests/test_g4_ai_shadow.py`만 다음 work(`gpt-5.6-luna/high`)가 수정한다. 제품 AI/issuer/pathfinding, runtime provenance 식, 원본·save·golden은 바꾸지 않는다.

## 1. 독립 판정 근거

1. current `ai_shadow.c`를 `i686-w64-mingw32-gcc -S/-c`로 컴파일하면 wrapper는 `call *g_load_original_target`을 내지만 C 전역 정의는 `_g_load_original_target`이다. `nm`은 `D _g_load_original_target`과 `U g_load_original_target`을 동시에 보여 주며 clean link는 같은 undefined reference로 exit2다.
2. pinned 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`의 `0x004D6B97`은 `push esi; call 0x00440FF0; add esp,4`이고, load 입구 `0x00440FF0`은 `mov ecx,[esp+4]`다. cdecl 인자 `slot`은 반드시 원본 call 직전에 별도로 push되어야 한다.
3. current wrapper는 helper 뒤 곧바로 원본을 call하므로 원본 `[esp+4]`에 slot이 아니라 wrapper의 caller return address가 놓인다. 또한 원본 `EAX`를 push한 뒤 `g4_load_complete`를 호출하고 `add esp,8`로 버려, helper가 clobber한 `EAX`를 그대로 반환한다. 이는 W2 §2의 “caller slot로 원본 정확히 1회, 원본 반환값 보존”을 둘 다 위반한다.
4. `tests/test_g4_ai_shadow.py`의 현행 테스트는 오히려 깨진 무장식 문자열을 요구하며, slot forwarding/return restoration의 순서를 검사하지 않는다. 현재 targeted 2 PASS는 ABI 증거가 아니다.

판정은 **`REJECT(scope/ABI) / BLOCKED(build_link+wrapper_abi)`**다. 단순 `_` 한 글자 수리만으로 fresh 실행을 열지 않는다.

## 2. work tier 최소 변경 계약

1. inline assembly가 C 전역의 실제 i386 심볼 `_g_load_original_target`을 정확히 한 번 간접 호출하게 한다.
2. wrapper entry의 `[esp+4]` slot을 원본 call 직전에 push하고 원본 반환 뒤 그 복제 인자만 정리한다. 원본 caller 소유 인자는 건드리지 않는다.
3. 원본 `EAX`를 `g4_load_complete(slot, result)` 호출 전 보존하고 helper 뒤 복원한 다음 return한다. marker helper에는 동일 slot/result를 전달한다.
4. 테스트는 위 세 조건의 **순서**와 stack balance를 고정하고, 무장식 `call *g_load_original_target`을 허용하지 않는다. old bytes/두 site 선검증/partial rollback/success-only marker/기존 AI tail-forward 계약은 낮추지 않는다.

검토 기준이 되는 최소 stack 흐름은 다음과 같다: before helper 종료 후 `push [entry esp+4] -> call *_g_load_original_target -> add esp,4`; 이어 `push eax(saved) -> push slot -> call _g4_load_complete -> discard slot -> pop eax -> ret`. 동등한 정확한 구현은 허용하되 원본 caller 인자·반환값 보존을 objdump로 증명한다.

## 3. gate와 fresh 경계

다음 work는 수정 뒤 아래를 새로 수행한다.

1. `.venv/bin/python -m pytest -q tests/test_g4_ai_shadow.py tests/test_runtime_env.py tests/test_s1_load_evidence.py`
2. `make -C tools/inmm_stub clean all`
3. `i686-w64-mingw32-objdump -d tools/inmm_stub/_inmm.dll`로 wrapper의 decorated symbol 해소, slot push/cleanup, `EAX` save/restore, 단일 원본 call을 확인한다.
4. `bash checks/safety.sh check`, `make check`.

모두 PASS하면 기존 W2 카드 §5의 pinned save000 fresh foreground **정확히 1회**를 같은 work lap에서 수행한다. 어느 gate든 예상 밖 실패하면 게임0·재시도0으로 변경과 로그를 보존하고 다시 승격한다. 기존 runtime 재사용, raw backfill, 제품 AI/issuer/pathfinding 수정, G4 PASS·사용자 승인 주장은 금지한다.

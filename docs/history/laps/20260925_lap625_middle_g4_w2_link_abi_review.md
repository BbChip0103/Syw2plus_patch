# 2026-09-25 | lap 625 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Codex native session(정확한 model/effort 비노출) / middle 진단·계획·확인.
- 가설 / 사용자 관찰: lap624의 `g_load_original_target` link 실패가 단순 symbol visibility 문제인지, wrapper call ABI까지 손상됐는지 독립 판정한다.
- 예상 PASS / FAIL 조건: current object/link에서 심볼 귀속을 재현하고 pinned 원본 cdecl stack과 wrapper를 대조한다. slot 전달·원본 반환 보존까지 맞으면 ACCEPT, 하나라도 어기면 REJECT 후 work handoff다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/하네스 source 변경0. 진단 전 current `tools/inmm_stub/ai_shadow.c` SHA256 `d4cf0eba313b94ccae7f273a177e8042a9bb2a96195fada9fc50fb51fa714bdd`; 문서 카드/STATUS/history/ESCALATE만 갱신; 커밋 없음/uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: pinned 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` read-only. bridge는 clean link 실패로 후보 없음. Python `.venv`, i686-w64-mingw32 GCC/binutils; 게임/fixture/활성 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted `pytest -k 'exact_postload or call_site_signature'` 2 passed; `gcc -S/-c`와 `nm`은 `D _g_load_original_target`+`U g_load_original_target`; `make -C tools/inmm_stub clean all` exit2 동일 undefined reference. pinned EXE `objdump`은 caller `push esi/call/add esp,4`와 load 입구 `[esp+4]`을 확인. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): link blocker 재현 PASS. 구현 판정 **`REJECT(scope/ABI) / BLOCKED(build_link+wrapper_abi)`**: 무장식 심볼 외에 원본 slot 미전달과 helper 뒤 `EAX` 미복원 2건을 추가 확인. `SAFETY_PASS`, `CONTEXT_PASS`; 게임/fresh·전체 Fast SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 현행 테스트는 깨진 문자열만 확인해 2 PASS가 ABI를 보장하지 않는다. 수정 bridge의 실제 objdump와 전체 gate, fresh raw는 미검증이며 제품 G4/사용자 승인 없음.
- 다음 한 가지: Luna/high work가 `G4_W2_LINK_ABI_REPAIR_LAP625.md` 범위에서 symbol+slot+return을 함께 최소 수리하고 targeted/build/objdump/safety/Fast를 통과한 경우에만 W2 fresh exact-one을 수행한다.

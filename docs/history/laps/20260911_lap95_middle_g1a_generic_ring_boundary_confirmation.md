# 2026-09-11 | lap 95 | G1-A generic ring boundary middle confirmation

- 실제 provider/model/effort / 지정 역할: Codex / 실제 model ID는 현재 표면에 노출되지 않음 / high 지정 / middle-tier 진단·계획·검수. 게임 구현 수정 없음.
- 가설 / 사용자 관찰: lap94의 SHA·old bytes·direct xref·writer order를 독립 재추출하면 generic ring direct-chain 충돌을 확인하고 다음 단일 producer probe를 지정할 수 있다.
- 예상 PASS / FAIL 조건: 두 원본 SHA/cmp/PE, 세 함수 old bytes, 해석된 caller 수 `1/134/1`, call target·WORD store order가 일치하면 lap94 contract CONFIRM; 하나라도 다르거나 의미를 과승격하면 REVISE/ESCALATE다.
- 변경 파일 / source fingerprint / 커밋: `analysis/memory_maps/player_offsets.md`, `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 이력과 checksum manifest만 문서 변경. 검수 입력 tool/test SHA는 lap95 manifest에 보존. `LOOP_ALLOW_COMMITS=0`, uncommitted; source/tests/binary/fixture/좌표 변경 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과 private copy 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp` PASS; PE32 i386 `.text` VA/raw `0x00401000/0x1000`, size `0xE3AE5`. 후보·player·map·army·fixture N/A/SKIP.
- 실행 명령 / 로그 / 캡처: `sha256sum`, `cmp`, `file`, `objdump -h/-d -Mintel`, 두 원본 `validate`, targeted pytest, 최종 `make check`, safety, doctor. 신규 log/PNG 없음.
- 측정값 / 판정: `0x0040FB50` caller `0x0041EC9A` 1개, internal call `0x0040FB6C→0x00415880`; `0x004AC3E0` decoded caller 134개; `0x004AC415→0x004AA820` 및 writer caller 1개; store는 `arg1/2/3→[ecx+0/+2/+4]`. targeted **9 passed**. lap94 contract **MIDDLE CONFIRM PASS**, direct-chain **REVISE**, production 의미·G1 **UNKNOWN/BLOCKED**.
- 회귀 / 남은 위험 / 독립 검수·사용자 승인: `make check` **136 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`, doctor top `ok=true`/original verified. doctor runtime은 manifest 부재로 `ok=false`며 game run은 금지에 따라 SKIP. `0x0041EC9A` 검증 후 같은 block의 `0x0041ED07→0x004AC3E0` 후보를 확인했으나 reachability·인자 provenance·production 의미는 미고정. 사용자 마일스톤 승인 없음.
- 다음 한 가지: Luna/Sonnet5/high work-tier가 `0x0041EC3D..0x0041ED0C` 하나의 old bytes·branch reachability·`0x0041ECD2/DE/EA` helper로부터 세 enqueue 인자 provenance를 fail-closed contract/test로 고정한 뒤 다음 새 middle 검수로 넘긴다.

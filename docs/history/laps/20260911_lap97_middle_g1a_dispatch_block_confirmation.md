# 2026-09-11 | lap 97 | G1-A dispatch-block independent confirmation

- 실제 provider/model/effort / 지정 역할: Codex / 실제 model ID는 현재 표면에 노출되지 않음 / high 지정 / middle-tier 진단·계획·독립 검수.
- 가설 / 사용자 관찰: lap96의 `0x0041EC3D..0x0041ED0B` 계약을 계약 함수 출력과 분리해 두 고정 원본에서 재추출하면 window, branch/call, helper 반환과 stack provenance의 일치 여부를 독립 판정할 수 있다.
- 예상 PASS / FAIL 조건: 두 원본 SHA/cmp/PE, 207-byte window, 지정 7 branch와 7 call, helper `ret 0x4`, LIFO stack 인자 순서가 모두 일치하면 CONFIRM; 하나라도 drift면 REVISE/ESCALATE; production 의미가 없으면 UNKNOWN/BLOCKED 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임 코드 변경 없음. `docs/STATUS.md`, 본 history, `loop/ESCALATE_SOL`, `docs/history/laps/20260911_lap97_files.sha256`만 문서 갱신. `LOOP_ALLOW_COMMITS=0`, uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본과 private copy 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp` PASS; PE32 i386 `.text` VA/raw `0x00401000/0x1000`, size `0xE3AE5`; candidate/player/map/army/fixture N/A/SKIP.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `cmp -s`, `file`, `objdump -h`, dispatch/helper/producer/enqueue 범위 `objdump -D -Mintel`, instruction caller count, 207-byte `xxd`, 두 원본 disassembly `diff`; targeted pytest, `make check`, safety, doctor. 신규 log/PNG/game run 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 두 disassembly diff 0; 207-byte window 일치; branch 7개와 block call 7개 일치; helper 세 개 모두 `ret 0x4`; caller `1/134/1`; enqueue 인자 `[esp+4]=final 0x0040F5A0` table WORD, `[esp+8]=0x0040F5C0` 반환, `[esp+0xC]=0x0040F5E0` 반환. **MIDDLE CONFIRM PASS**; production 의미/G1 UNKNOWN/BLOCKED.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted **11 passed**, `make check` **138 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`, doctor `ok=true`/original verified. runtime manifest/game/fixture/candidate SKIP; 사용자 승인 없음. SHA 선검사 때문에 mutation test는 dispatch-specific 오류보다 SHA 거부를 먼저 증명하지만 고정 원본 정적 재추출 결과와 충돌하지 않는다.
- 다음 한 가지: 새 Luna/Sonnet5/high work-tier가 `0x0041EC3D`의 CX·ESI 최근 지배 정의와 upstream record/state source를 old bytes·branch·direct xref로 한 번만 추적해 primary input/production sender 연결 또는 정확한 단절을 기록한다. 명확할 때만 read-only contract/test를 추가하며 게임 구현·run·fixture·좌표 변경은 금지한다.

# 2026-09-11 | lap 75 | 목표 G1-A primary-to-cell static trace

- 실제 provider/model/effort / 지정 역할: 일반 작업자 hands-on 정적 조사. 현재 표면은 실제 provider/model/effort를 노출하지 않으므로 `gpt-5.6-luna/high` 실행으로 주장하지 않는다.
- 가설 / 사용자 관찰: `0x00499583→0x004A3A40` 뒤에 primary 12-slot raw field가 실제 command cell 생성/worker 생산으로 이어지는지 고정 원본에서 증명할 수 있다.
- 예상 PASS / FAIL 조건: 네 field source, 12-slot index, cell constructor, callbacks/action, strict rectangle이 하나의 직접 edge로 연결되면 PASS; edge가 없거나 worker 의미가 유일하지 않으면 UNKNOWN/concrete blocker로 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `analysis/memory_maps/player_offsets.md`, `docs/STATUS.md`, 본 기록, `loop/ESCALATE_SOL`만 문서 변경. 코드/tests/binary/fixture/좌표/timeout/game run 없음. 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`, SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음. 실행 fixture/플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `file`, `objdump -h`와 read-only Capstone disassembly of `0x499201..0x4992DF`, `0x499583`, `0x4A3A40`, `0x4A3B5B`, `0x49AD3F..0x49AFA8`, `0x49B6D0`, `0x41F630`, `0x49B530`, `0x49B640`, `0x41FA60`; `make check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `0x004A3B5B`가 `A6/D6/BE/EE + 2*i`를 쓰고 `i=0..11` 경계는 PASS. `0x004A3A40`은 A6만 반환한다. primary 별도 loop는 BE/D6/EE를 읽지만 `0x00419D80/0x00419E40/0x00465E80`로 가며 cell constructor가 아니다. cell path는 `0x004992DF→0x0049B6D0→0x0041F630`의 조건부 group2..5뿐이다. primary-to-cell/worker edge UNKNOWN; concrete blocker.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 source/tests SHA 불변. strict rectangle은 `0x0041FA60`의 group-cell object에만 정적으로 확인된다. `0x0049B530` action ids `0x19A/0x19C/0x19E/0x1A1` 중 worker 의미는 미확정. 새 Sol/Opus5 독립 검수와 사용자 승인은 없음.
- 다음 한 가지: Sol/Opus5/high가 본 원본 old bytes와 primary-to-cell 단절을 독립 검수하고 추가 정적 probe 범위를 결정한다. 그 전에는 game run·production click·harness/tests/binary/fixture/좌표 변경 금지.

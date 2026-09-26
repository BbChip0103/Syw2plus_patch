# 2026-09-12 | lap 352 | G1 / S1 PlayerStruct 필드 재유도 middle 판정

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인). 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: lap284/lap286 `+0x03=alliance`와 기준 문서 `+0x04=alliance` 중 적어도 하나가 오라벨이다. 원본 xref와 fixture가 한 배치로 수렴하는지 판정한다.
- 예상 PASS / FAIL 조건: `+0x00..+0x04`의 폭·생성/소비가 원본 명령과 두 fixture의 8 slot에서 일치하면 ACCEPT; 다의적이거나 raw byte와 충돌하면 BLOCKED/승격한다.
- 변경 파일 / source fingerprint / 커밋: 신규 active review, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` append. 제품 코드/tests/과거 probe/EXE/DLL/save/pin/baseline/golden 변경 0; `LOOP_ALLOW_COMMITS=0`, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음; PE32 i386 정적 objdump/xxd. save000 `1c703551…719da`, save006 `616b7997…d064`; runtime 활성 인원·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처: `sha256sum`/`file`/`objdump -h`; `objdump -d -Mintel`의 `0x41BA60..0x41BE30`, `0x43EBC0..0x43EC30`, `0x4C3F73..0x4C3FEB`; `xxd -p -l 6 -s <player0+slot*0x3ABC>`; lap351 probe 1회 재실행. 콘솔 증거, 캡처/PNG 0.
- 측정값 / 판정: 원본 direct xref count base/+1/+2/+3/+4/+5=`191/1/21/3/1/46`; 3개 8-slot 루프가 동일 공식을 가짐. save000/006 모두 8/8에서 `+3=1<<+1`, `+4=different-team bits`. **필드 배치 ACCEPT; lap284/lap286 alliance 라벨과 player_offsets `+4=alliance` REJECT.**
- 이전 바퀴 독립 검수: lap351 probe SHA `e4f26428…49b240`, rc0/failures=[], stdout `1a4359cb…1565e35`; 4 fixture offset 불변성 판정을 재현했다. targeted exit0은 제품/봉투 승인이 아니다.
- 회귀 / 남은 위험 / 승인: nation/player_num/is_cpu, player/roster offset은 생존. 실제 load 완료·일반 동맹 변경·owner `+0x8E`·S1(A)+(B)·WM_CLOSE·Stage B/G1과 G2~G4는 미검증; 사용자 마일스톤 승인 0.
- 검사: fresh `make check` rc0, 378 passed(63.21s), Ruff/compileall/mypy/`CONTEXT_PASS`; `checks/safety.sh check` rc0/`SAFETY_PASS`. 게임/Wine/Xvfb/클릭/PNG 0.
- 다음 한 가지: Luna/high work가 주소 문서 앞 6바이트 라벨을 정정하고, 과거 probe를 보존한 채 별도 S1 load-evidence reader/CLI/artifact와 합성 실패 회귀를 구현한다. 실제 run 예산 0.

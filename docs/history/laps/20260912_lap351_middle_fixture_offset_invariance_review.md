# 2026-09-12 | lap 351 | G1 / S1 fixture offset 불변성 middle 판정

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인). 게임 코드·하네스 hands-on 수정 0.
- 번호: runtime 메시지 `lap=350`, `loop/.lap_counter=351`; PROMPT에 따라 351 사용, counter 쓰기 0.
- 목표/가설: lap286의 bulk/player/roster offset이 width-height 배정 2개와 halving 식 2개의 모든 조합에서 현재 네 정사각·짝수 fixture에 불변인지 단일 검사로 판정한다.
- 예상 PASS/FAIL: 네 파일 각각 4조합의 offset tuple 집합 크기 1이고 lap286 수치와 같으면 ACCEPT; 하나라도 갈리면 BLOCKED. 후속 필드 근거 충돌이 나오면 구현을 열지 않고 승격한다.
- 변경 파일: `docs/work/active/G1_S1_FIXTURE_OFFSET_MIDDLE_REVIEW_LAP351.md`, 신규 probe, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` append. 제품 코드·tests·EXE/DLL/save/pin/baseline/golden 변경 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본·후보 SHA / 환경 / fixture: 원본 `b56986e0…a8ac`, 후보 없음. save000 `1c703551…719da`, save006 `616b7997…d064`, save011 `23dd24d5…dfa4`, save012 `5a6863c1…28f1`; 정적 Linux/objdump/Python, 활성 플레이어·지도 실행·군대 N/A.
- 실행 명령: lap286 probe 수정 없는 재실행 rc0/`failures=[]`; lap351 probe rc0/`failures=[]`; 신규 probe `py_compile` rc0, Ruff rc0. 로그 `logs/lap351/fixture_offset_invariance.json`.
- 수치: 180/180 두 파일은 4조합 모두 `(1455954,2259634,2388902)`; 100/100 두 파일은 모두 `(772754,1576434,1705702)`. probe `e4f26428…49b240`, output `1a4359cb…65e35`.
- 판정: **offset 불변성 ACCEPT.** lap322 §14.1의 현재 fixture 환산 불가 결론은 반려. 일반 width/height 의미와 odd/non-square 외삽은 UNKNOWN 유지.
- 새 충돌/중단: lap284/lap286가 연속 `<BBBB>`의 `+0x03`을 alliance로 라벨하지만 기준 주소 문서는 alliance=`+0x04`. save000/006 player0 raw=`02000001fe`, 기존 report 값1과 문서 위치 값254가 다르다. 전체 S1 work 봉투 BLOCKED.
- 검사: 근거 충돌 발견 뒤 Fast `make check`와 safety는 SKIP. 게임/Wine/Xvfb/클릭/PNG/후보 artifact 0. targeted exit0은 제품·봉투 승인 아님.
- 회귀/남은 위험: nation/player_num/is_cpu와 offset/roster 총수는 이번 충돌 영향 밖. alliance, owner `+0x8E`, load completion, S1(A)+(B), WM_CLOSE, Stage B/G1과 G2~G4 미검증.
- 다음 한 가지: 새 Sol/high middle이 원본 xref와 fixture bytes로 PlayerStruct `+0x00..+0x04`를 재유도해 alliance 오라벨 범위를 확정한다. 그 뒤에만 work tier sentinel 구현 범위를 발행한다.
- 최종 보존 SHA: STATUS `84ad55d3…d0a6e7`, active review `31306293…36b5f8`, ESCALATE_SOL `acb93fee…42ef48`; 모두 uncommitted.

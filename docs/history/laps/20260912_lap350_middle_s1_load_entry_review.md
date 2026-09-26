# 2026-09-12 | lap 350 | G1 / S1 로드 진입 봉투 middle 판정

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인). 게임 코드·하네스 hands-on 수정 0.
- 번호: runtime 메시지 `lap=349`, `loop/.lap_counter=350`; PROMPT에 따라 350 사용, counter 쓰기 0.
- 목표/가설: lap349 §2의 여섯 항목을 현행 원본과 연결해 ACCEPT/BLOCKED를 판정한다. PASS=slot/file/fixture/load-completion 근거가 비순환으로 모두 닫힘, FAIL/BLOCKED=hitbox·fixture·completion 중 하나라도 미확정 또는 근거 충돌.
- 변경 파일: `docs/work/active/G1_S1_LOAD_ENTRY_MIDDLE_REVIEW_LAP350.md`, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` append. 제품 코드·tests·probe·EXE/DLL/save/pin/baseline/golden 변경 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본·후보 SHA / 환경 / fixture: 원본 `b56986e0…a8ac`; `runtime_env.py=965e3709…b547b`; R1 test `891b60eb…b4265`; save000 `1c703551…719da`, save006 `616b7997…d064`, 두 파일은 prepare source에도 byte-identical. 새 후보/runtime/활성 플레이어/지도/군대/PNG 없음.
- 이전 바퀴 검수: lap348 불변 probe `fdca6f6c…c093`를 수정 없이 정확히 1회 실행, `logs/lap350/lap349_input_recheck.json` SHA `46902e20…a52a`, rc0, `failures=[]`; lap349 기록과 일치. 새 runtime/독립 알고리즘 증거는 아님.
- 정적 명령: `objdump -d -Mintel`로 원본 `0x4D5F10..0x4D6BC5`, `0x440A80..0x441025`, `0x493C40..0x493DA5`; `xxd`로 old bytes; `sha256sum`으로 원본/fixture/source/R1 입력을 읽기 전용 대조. 게임/Wine/Xvfb/클릭/PNG 0.
- 측정값: 7 rect=`this+0x408`, stride16, count WORD `+0xF9C`; mouse x/y DWORD `0xC0CB58/5C`; hit 시 selected WORD `+0xF9E=index+1`; load mode는 `di-1`을 `0x440FF0`에 전달. path=`%ssave\\save%d%02d.dat`, group WORD `0x66966C`. open null 조기 return 뒤에도 caller가 `ax=3`을 반환.
- 판정: **BLOCKED.** 슬롯의 정적 index 연결은 ACCEPT지만 fixture 내용은 lap284-work/lap286-middle의 player/roster offset 산출과 lap322 §14.1의 환산 불가가 충돌한다. PS3 단독은 open 성공/복원 완료를 구별하지 못한다. 실행·구현 봉투 발효 0.
- 검사: 목표 입력 probe만 rc0/failures=[]로 재현. 근거 충돌 발견 즉시 사용자 중단 규칙을 적용해 새 검수 probe·`make check`·safety는 SKIP; 이전 exit0을 계획 승인으로 사용하지 않음.
- 회귀/남은 위험: S1(A)+(B), 실제 동일상태 pair, slot/file/group 관측, load sentinel/scene 복원, 결정성, WM_CLOSE, Stage B/G1과 G2~G4 전부 미검증. W3/N14/A·C identity UNKNOWN 유지.
- 다음 한 가지: 새 Sol/high middle이 lap286 파일 오프셋이 현재 네 fixture에서 두 명시 ambiguity 아래 불변인지 계산해 lap322 §14.1과의 충돌을 판정한다. 그 뒤에만 work tier의 별도 S1 load evidence 함수/테스트 범위를 열며 게임 실행 예산은 Astra 결정 전 0.

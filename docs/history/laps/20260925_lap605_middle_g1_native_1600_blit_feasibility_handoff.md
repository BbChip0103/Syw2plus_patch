# 2026-09-25 | lap 605 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex native middle(모델 ID·effort 비노출) / 진단·계획·독립 확인. 게임 코드·binary·runner를 수정하거나 게임을 실행하지 않았다.
- 가설 / 사용자 관찰: lap604의 W50RX `R4` 뒤 최신 12:25 운영자 결정은 W50R/W50RX를 최종 종료하고, 원본 내부 800×600 합성과 native 1600 primary를 분리해 기존 final `Blt`로 2배 전사할 수 있는지 work가 즉시 판정하도록 요구한다.
- 예상 PASS / FAIL 조건: exact SetDisplayMode caller에서 요청800×600×8/전달1600×1200×8, renderer800×600×8, source832×600/source rect800×600, primary1600×1200, exact final Blt HRESULT0, 판별력 있는 2× PS3 캡처가 한 run에서 결합되면 `FEASIBLE`; 구조적 반증만 `NOT_FEASIBLE`; 하네스/입력/예산 실패는 `BLOCKED`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): work 카드 `docs/work/active/G1_W50B_NATIVE_1600_BLIT_FEASIBILITY_LAP605.md`, 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` §155만 변경. 제품·하네스 source·binary·raw 변경0, 커밋0(uncommitted). 진입 runtime source `43d0ee422cd58919c29a315ad724c507cae53ece`; 최종 fingerprint와 파일 SHA는 검사 뒤 기록한다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보·게임 실행·활성 플레이어·지도·군대·fixture 없음(SKIP). 참고 저장소는 읽기만 했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`과 `objdump -D/-s`로 원본 `0x00464564..0x0046457D`, `0x0041C3C4..0x0041C3E4`를 대조했다. `omx explore --prompt ...`는 hard-deprecated라 exit1 후 일반 read-only 조회로 전환했다. 게임 실행·캡처0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): SetDisplayMode return VA `0x0046457D`; final present는 destination `DAT_00E5D434`, source `DAT_0104FB2C`, destination rect NULL, flags `0x01000000`, return VA `0x0041C3E4`로 raw bytes와 decompile이 일치한다. `FUN_004922D0`은 원본 offscreen을 `max(width,832)×height`로 만든다. 그래서 split-mode H1은 **FEASIBLE(착수 가치)**이나 runtime 제품 증거는 아직 UNKNOWN이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: W50R/W50RX 재실행·validator 수리·기존 runtime 재사용을 닫았다. H1이 input/window semantics에서 막힐 수 있고, whole-frame 2배가 HD detail 경로 자체를 증명하지 않는다. 2단 독립 검수·3단 사용자 승인 없음. G1/G2/G4 제품 완료0/3.
- 다음 한 가지: Codex `gpt-5.6-luna`/high work가 위 카드대로 기본-OFF split-mode 진단 훅과 회귀를 만들고 H1 fresh 1회(조건부 H2 최종 1회)로 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`를 판정한다.

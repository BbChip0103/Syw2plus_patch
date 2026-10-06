# 2026-10-05 | lap 983 | 목표 G7 (H-G7o 독립 검수 + 수리 경로 결정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 중간(middle) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 사용자 관찰: lap982 H-G7o 관측(타이틀 로드 뒤 local 0·표 미복원·즉시 패배)이 raw와 일치하고, 로드 스트림 안에 local을 되살릴 근거가 이미 있는지 정적으로 확인하면 R2(형식 변경)보다 작은 수리가 가능하다.
- 예상 PASS / FAIL 조건: probe-result 2개 재계산 불일치 0이면 H-G7o 수용, 아니면 ESCALATE. 수리 경로는 저장 형식 변경 여부·기존 세이브 호환·참가자 행 복원으로 비교한다.
- 변경 파일 / source fingerprint / 커밋: 문서만(uncommitted) — 카드 `docs/work/active/G7_MIDDLE_LAP983_HG7O_ACCEPTANCE_SNAPSHOT_RESTORE_HANDOFF.md`(신규), `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(lap983 절 추가), 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL` 처리·삭제. 제품 patch/bridge/EXE·하네스 불변.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…a8ac`, 이식판 normal `0e28ef57…d257`(이번 lap 직접 sha256 MATCH). 후보 없음. fixture = lap982 입력 그대로(혼자하기 기본 지도, lobby-snapshot seat 2).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `temp/Syw2plus_patch/20261005_lap983_middle_review/`에서 `python3 recalc_lap983.py recalc_lap983.json`(SHA256 `14dc8474…650931e`), `python3 save_parse.py save_parse_lap983.json`(`e470b31b…199c91`), `python3 port_bytes.py port_bytes_lap983.json`(`08342c44…602f84`), cave 조립 확인 `cave_check_lap983.txt`(`e6a6c5f5…dcbc6ff`), 역어셈블 `orig_save_440C20.txt`·`orig_load_440FF0.txt`.
- 측정값 / 판정:
  - 재계산(제품 helper 미사용): A local 2(첫 일치 2)·C local `[2]`·ps `[3]`·선택 owner 2·D local 0·ids 전부 0·행 상태 전부 0·ps `[3,27,29]`, P=O. 기록 대비 **불일치 0** → **H-G7o PASS(관측) 수용**, R1 불가 확인.
  - 정적: 로드 스트림 마지막 고정 블록이 **`0x632F7C`(0x170) = 게임 시작 때 live 로비 표 복사본**(`0x41B9CA`/`0x41BC59`). save 두 개 직접 파싱 결과 스냅샷 ids `[1,1,0,…]`·행2 사람 → own 0 첫 일치 2. 게임 자체 복원 복사 `0x424DB4`(ps 핸들러 `0x424DA0`)가 같은 방향 복사를 이미 쓴다. 로드는 이를 부르지 않는다. `[0x4ED848]`=1(솔로) 저장됨.
  - 수리 지점: fclose 직후 `0x441310`(old `8B 2D 2C AF B3 00`, 원본=이식판). `.g5code` `0x18A7D00`~ 비어 있음.
  - **수리 경로 R4 채택**(솔로 게이트 → 스냅샷→live 0x5C dword 복사 → `0x43AF40(&0xB63FC4)`): 저장 형식 불변·기존 세이브 적용·참가자 행 복원. R2(sidecar)·R3(ai==0 owner)는 대안 보존. 다음 work H-G7r 사전등록 R-1~R-5·반증 (i)~(iii) = 카드 §4.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이식판 플레이어 블록 배치(G2 fread 래퍼)는 파싱 안 함(UNKNOWN, 판단 불필요). own id 상수성은 솔로 프로세스 4개 관측뿐 → R-1이 판정. 멀티에서 `[0x4ED848]` 값 UNKNOWN(게이트로 솔로 한정). 사용자 ↑/↓ 경로 동일성 UNKNOWN·비차단 유지. G7 사용자 합격 아님.
- 다음 한 가지: Sonnet work 1 lap — H-G7r(R4 최소 구현 `0x441310` hook + cave `0x18A7D00`, 회귀 테스트 RED→GREEN, cand 격리 실행 R-1~R-5), 카드 §4 그대로.

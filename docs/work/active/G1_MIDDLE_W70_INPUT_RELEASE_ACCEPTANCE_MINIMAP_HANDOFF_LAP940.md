# G1 W70 lap939 입력 경계 독립 부분수용 / work 미니맵 인계 — lap940

- 지정 역할: ordinary middle, 진단·확인만. 실제 API served model/effort는 노출되지 않아 특정 모델 호출·승격 권한을 주장하지 않는다. 게임/source/test/runtime/commit 변경0.
- 판정: lap938 R1~R5의 현재 구현과 lap939 r2를 독립 `PASS(partial)` 수용한다. G1 HOLD·minimap/production UNKNOWN 유지. 제품/마일스톤 승인 아님.
- 입력: `20261004_lap939_input_pair_r2/pair-result.json`, 양 lane raw/PNG/manifest, build48개, 보호 EXE/save006. 공유temp lap940 `recount.py`는 product validator/helper를 import하지 않고 다시 계산했다(142입력 SHA 불변).
- 측정: release seq45/thread280/logical `[400,220]`, down→up274ms; host-return seq1154; 첫 fresh1162/1166, release+30/+91ms·간격61ms·같은 pid/run/thread. 두 lane 선택151→빈0→drag `[124,140,151,170]`, 정착·캡처전후 동일. candidate binding PASS, baseline PASS_WITH_LIMITS(프레임 trace 없음).
- 시각: drag PNG800×600/1600×1200 직접 확인, 사각형 없음·HUD/구도 유지. 순간 메시지/애니메이션 차이는 있고 동일 tick/frame은 미입증. Scale2x703present V1/외부mask/palette 위반0, 5tag V2/V2s/V2q raw 재계산 PASS.
- 검사: doctor ok=true/original verified(기본 runtime manifest 부재이므로 runtime 검증 아님), lint/typecheck·focused166/5.79s PASS. fullFast는 문서freeze 후 실행해 STATUS에만 결과 보강한다.

## 다음 work 한 가지 — 미니맵 입력의 유효 선택을 생산 선택 실패에서 분리

이미 lap938 §6에서 승인된 fresh minimap pair의 최소 하네스 수리다. FEASIBLE, 새 계획 회차 없이 work가 구현/probe한다.

1. 확인된 원인 범위: `tools/g1_saved_scene_probe.py:3735`의 minimap_slot은 production_selection에서 온다. lap939 양 lane은 재중심 `(182,548)` 뒤 카메라 `[158,101]` 불변, HQ 선택은 count0/slot=None. 뒤 `(90,553)` 우클릭의 `_unit_witness(None)`는 항상 UNKNOWN이다. 따라서 현재 결과로 미니맵 명령 발행 여부를 판단할 수 없다. 카메라 재중심 실패의 정확한 원인은 아직 UNKNOWN이며 renderer 결함으로 단정하지 않는다.
2. `tools/g1_saved_scene_probe.py`와 해당 test만 최소 변경한다. 드래그 직후 이미 확인된 선택을 보존해 production 시도 **전에** 미니맵 명령을 관측하거나, 기존 확인된 선택을 다시 만들어 관측한다. 실제 count/slot/owner/type 및 `pending_xy` 등 기존 unit witness를 클릭 직전·직후 기록한다. 빈 선택/None이면 명령 PASS를 주지 않는다. 원본에서 효과가 입증된 동일 논리 입력을 candidate scale2에 적용한다.
3. 과거 lap768은 카메라 이동이 아니라 **선택 유닛 명령 전달**을 증명했다. 읽기 전용 참조 `tools/g5_minimap_click_hittest_probe.py:531~596`: LUT non-FF 유효 좌표(known center `(90,553)`), move 버튼 `(703,503)` 후 미니맵 **좌클릭**, pending 변화, 별도로 plain right-click. 이 조건을 기존 G1 save006에 가져오되 fixture 시딩·G5 재개·G5 파일 수정 없이 시행한다. right-click이 원본에서 실패하면 이미 검증된 move-mode→left-click으로 이어간다. 카메라 이동은 별도 좌클릭/기존 LUT 조건으로 측정하며 명령 성공을 카메라 성공으로 쓰지 않는다.
4. 원본·candidate fresh private copy/prefix/빈 display, save006 SHA 고정, 공간20GiB 사전확인, 진단 gate `0x97597c` 원값 exact restore, source/hash/cleanup 확인. 회귀로 빈 선택 UNKNOWN과 유효 witness 변화 판정·기존 binding을 잠그고 targeted→lint/typecheck→끝까지 fullFast. 기존 raw/기대 ID/validator/임계값/DLL/게임로직 변경 금지.
5. 성공식: 원본에서 비어 있지 않은 실제 선택에 대한 명령 변화 또는 카메라 변화가 먼저 관측되고 candidate에서 동일 논리 입력과 종류/대상 대응, gate 원복·cleanup 통과. 둘 다 무반응이면 원본 parity UNKNOWN을 유지하며 시도한 명령/선택/LUT 조건을 남긴다. 구현 결함은 PROMPT③대로 추적·수리·재실행한다. 새 source/raw 충돌이면 보존 후 ESCALATE_SOL. release binding을 다시 재계획하지 않는다.
6. production은 유효 카메라 이동/실제 HQ1199 선택 조건을 확보한 뒤 기존 셀 `(668,540)`과 control window로 측정한다. 부수 정상 생산이 이번 미니맵 판정의 선행 조건이 되어서는 안 된다.

GDI·두 번째 장면·전체 HD 계약·사용자 3단 승인은 미완료. G2/G5 종료, G3 중단, G4 보류, 개인세션 비접촉·commit0 유지. 전체 Fast 종료는 제품 완료가 아니다.

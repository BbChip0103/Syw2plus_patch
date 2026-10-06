# G1 lap945 생산 witness 독립 부분수용 / writer 분류 census work 인계 — lap946

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, 진단·계획·확인). 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0.
- lap945 fresh save006 pair의 **생산 발행·완료 parity K1~K6는 PASS(partial)로 수용**한다. lap944 카드 §5 첫 행(P-1~P-5 두 lane 성립)에 해당한다.
- **P-6 "같은 생산 표시"는 미충족(UNKNOWN, 캡처 시점)**: 후보 PNG는 `일본 농부 1%` 생산 패널을 보이고 원본 PNG는 생산 패널이 없다. 아래 근거로 후보 렌더 결함 귀속은 하지 않는다. V1/V2/V2s/V2q 수치 gate PASS가 이 차이를 덮지 않는다.
- G1 HOLD 유지. 제품 milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음. lap943 r4는 소급 PASS가 아니며 UNKNOWN/HOLD 그대로다.

## 독립 증거 (lap944 카드 §7)

- pair `temp/Syw2plus_patch/20261004_lap945_production_witness/pair-result.json` SHA `cfb342276b270e44a5c48aec6364425c0a47a5ca9f62a35b1137dd9b5fd3eb8f` MATCH. 원본EXE `b56986e0…a8ac`·save006 `616b7997…0d064` 원천 재해시 MATCH. 현재 probe/test SHA `65fd7f6b…2e29`/`26483686…b139` = 실행 before/after.
- 재계산(제품 helper import 없음) `temp/Syw2plus_patch/20261004_lap946_middle_review/recalculation.json` SHA `8ef8c7a2eccf0ab1046a8b1e110277f052b9f28ae0c2d57d4873d19c5591f5b6`, 스크립트 `recalculate.py` SHA `64ea42485b751e1f6f3aa68a9f341e37ba2a455f7c0acca4cb02dcb05bd5369b`.
- `prev/a/b` (tick, command, queue, progress, 쌀, 나무, `+0x1C`):
  - 원본 `24650,1,31,100,96807,30031,423` → `24653,15,31,0,96007,29731,433` → `24654,15,31,0,…`.
  - 후보 `24670,1,31,100,96807,30031,423` → `24673,15,31,1,96007,29731,433` → `24673,15,31,1,…`.
  - 두 lane spec `10/800/300`, prev→a = prev→b = `(−800,−300,+10)` EXACT, 정체 slot1199/owner0/type58 불변. K5 lane 간 spec·비용·새 slot 동일.
- control: 원본 1.372초 tick 24626→24646 건물 필드 불변, `control_global_delta` 쌀 +640 기록됨(재계산 일치, 은닉 없음). 후보 1.377초 delta 0.
- 완료: 두 lane type31 14→15, 새 slot1079(클릭 전 빈 slot, `(164,83)` HQ 바로 옆), 소실0, slot1199 command 1·progress 100 복귀, 약39.3~39.8초. owner0의 다른 type31 생산 건물 1163·1177은 전후 모두 command1/100 → 증가분 귀속 혼선 없음.
- 진단 gate=1 아래 재중심 camera `[158,101]→[165,87]`, gate `00→01→00` exact 복원(두 lane). 정상 gate=0 미니맵 원본 parity는 N/A 그대로. 클릭 원본 `(668,540)` / 후보 root `(1336,1080)` scale2.
- PNG: production 원본 `6ebf641b…076a7`·후보 `ab159bc5…6bf` 저장/`captures/` 사본 SHA MATCH. 나란히 보면 상단 자원 `96007 / 29731 / 1903/2300`(=used1470+433)이 두 lane 동일, 클릭한 F칸(농부) 강조 동일, 선택 패널 `체력3600/3600 방어력38/38` 동일, 월드·HUD 2배 구도 유지.
- P-6 차이 근거: 두 캡처 모두 `before` 후 벽시계 0.369/0.373초. a 표본 progress가 원본0·후보1이다. 원본 프레임은 비용 차감 HUD는 그렸지만 생산 패널은 없다. 후보는 원본 800 표면의 미러라 Scale2x가 패널을 새로 만들 수 없다 → 진행률0 프레임 표시 시점 차이 가설. 원본 lane 메시지 `적의 공격을 받고 있습니다`는 minimap 캡처에서 두 lane 모두 보이므로 메시지 렌더 누락이 아니라 tick 시점(lane 간 sim tick 약20 차) 차이다. 이 가설은 이 raw로 증명되지 않는다.
- 후보 `mirror_validator` BLOCKED(1104건 모두 nearest oracle 미달)는 Scale2x용 gate가 아님 — lap853 계약·lap940 판정 그대로, 완화하지 않는다. Scale2x gate PASS(외부 mask/palette 위반0).
- cleanup 두 lane ok/game_removed, 실제 game 경로 부재 확인. focused `tests/test_g1_saved_scene_probe.py` **175 passed/5.98s**.

## 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

입력 트랙(선택·빈땅·드래그·진단 gate 미니맵·생산)은 부분수용으로 닫혔다. lap911 카드 §2.3 순서로 돌아가 lap819 §3 합격기준 1(writer 분류)을 잰다.

1. **lap913 census 계측 결함 두 건 먼저**: (a) `g1_census.c`의 `present_source_surface`가 COM surface 포인터 대신 backing buffer를 직렬화 → 실제 surface 인자 전달, (b) `surface_blt_captured`를 begin이 아니라 Lock/완료 뒤 증가. 각각 좁은 회귀(RED→GREEN). 기존 raw 수정 금지.
2. fresh save006 `--census-only` 1회(새 사본·prefix·display, 디스크 20GiB 확인, game 사본 삭제). 산출: PS3 마지막 present의 writer별 last-writer 픽셀 수·비율과 분류 표
   **HD 가능**(identity/Scale2x 증거 있는 writer) / **원천 그림 없음**(`rect_fill`·`rect_border`·`set_pixel` 등, 목록·비율 공개) / **명시 잔여**(GDI 텍스트·P6 등) / unknown.
3. 측정식(사전 등록): unknown 비율과 명시 잔여 비율을 공개한다. 합격 후보 = 명시 잔여 ≤5%이고 unknown이 분류 근거와 함께 줄어듦. 이번 lap에는 임계값을 새로 만들거나 기존 gate를 완화하지 않는다. 결함(좌표·바인딩·카운트)이면 같은 lap에서 수리→재실행(3회).
4. 기록 freeze → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle.

부수 backlog(이번 lap 범위 밖): P-6 생산 패널 시각 parity — 두 lane이 slot1199 progress ≥ 같은 값일 때 캡처하는 상태 조건 캡처(lane tick 동기 아님). 두 번째 장면 coverage ≥90%, GDI(P7), D-2 scroll, 사용자 승인은 STATUS 목록 그대로.

## strategy 재호출 조건

census 결과 unknown이 프리미티브·DD blt·GDI 어느 것으로도 설명되지 않는 쓰기(직접 메모리 등)로 PS3 화면의 5%를 넘을 때, 또는 분류가 lap819 §3 기준 자체를 바꿔야 할 때만. 그 밖은 work ↔ middle.

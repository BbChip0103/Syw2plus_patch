# G1 lap941 minimap 독립 부분수용 / production work 인계 — lap942

## 판정과 범위

- 지정 역할 ordinary middle, 진단·계획·확인. Codex API served model ID/effort 미노출: Sol/Opus 호출 성공이나 승격 권한을 주장하지 않는다. 게임·source·test·DLL·runtime·commit 변경0.
- lap941 final pair의 **진단 gate=1 아래 선택 유닛 명령 전달 parity만 PASS(partial)**. 정상 gate=0 미니맵, 카메라 이동, 실제 목적지 도착, 생산·전체입력·GDI·두 번째장면·전체HD·G1 사용자승인은 미완료. G1 HOLD 유지.
- 제품 milestone 경계가 아니며, 충돌·미설명 실패 없음. 아래 결함은 수리 범위가 특정된 하네스 구현 문제여서 work에 직접 인계한다. ESCALATE_SOL 생성 조건 없음.

## 독립 증거

- final pair `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap941_minimap_pair_final/pair-result.json` SHA `9c2c1592a9ec67f852d329cfa21617f30a0a1e3d0ca12941acab7f69a1569c15`. 양 lane JSON과 pair 내 사본 byte-content 동일.
- 원본EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`를 원천에서 재해시 MATCH. 두 manifest의 새 private prefix/copy 정책과 원본·사본EXE identity MATCH.
- bridge build48개 source와 runtime_bridge.c 해시 현재 MATCH, DLL `bfd1261af1526c405afeafd6e3e13aba1aabd426b3dd5d322fd93a5bb6af9c40` manifest/build/실파일 MATCH. **host probe의 실행 시점 독립 source hash는 final pair에 저장되지 않았다**; 현재 source 검토와 work 서술을 구분한다. 이를 DLL source 충돌로 해석하거나 전체 source 검증 완료로 넓히지 않는다.
- raw 선택 배열 `<20I` 디코드 및 before/after: 슬롯 `[124,140,151,170]`, owner 모두0·type `[98,13,111,16]` 고정. `pending_xy` `[6553741,0,0,0]` → `[5767258,5767259,5832794,5963864]` 네 개 전부 변화; packed16 좌표 `(90,88),(91,88),(90,89),(88,91)`, command 모두1→3. 양 lane의 before/after witness 동일.
- logical `(90,553)` plain 우클릭1회, 후보 physical `(180,1106)`→WndProc logical `(90,553)`: down seq57/up61·ts差114ms·같은 pid276/thread280. fallback 없음. 선택4기 유지; 카메라 양 lane `[158,101]` 불변.
- gate `0x97597c` `00000000→01000000→00000000` exact restore 두 lane MATCH. 임시 gate write를 공개한 진단 fixture이며 정상 UI 허용모드 증명이 아니다.
- trace raw baseline648/candidate1668행과 input trace SHA MATCH, 563 성공 Scale2x present V1 상한/외부mask/palette 위반0. 두 lane PNG 각6장(800×600/1600×1200)의 저장 SHA·복사캡처 SHA·PNG header 치수 MATCH.
- minimap PNG 원본/후보 직접 시각 확인: 월드/HUD 배치와 2배 구도 유지, 미니맵 다이아몬드·선택패널 대응. 동일 tick/frame이나 클릭 뒤 도착 증명은 아님.
- cleanup 두 lane ok/game_removed=true·prefix_processes_after=[]와 실제 game 경로 부재 확인. 새 runtime 없음.
- 독립 재계산(제품 helper import 없음) `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap942_middle_review/recalculation.json` SHA `873a05e31486344d50e2962f8438bb7d8cf610bd9906ab46affac1efe37ee3a6`; 읽은 파일 SHA 목록 포함. Bounds protected-EXE 재디스어셈블 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap942_middle_review/minimap_bounds_disassembly.json` SHA `07ab2706f4562b3f5f280b658084a08f64aa3a87c7d86cc23817e2030d1e73fc`.

## 다음 work 한 가지 — production 입력 하네스 최소 수리와 fresh pair

**FEASIBLE; 재계획 회차 없이 work(Luna/Sonnet)에서 `tools/g1_saved_scene_probe.py`와 해당 tests만 수정한다.**

1. 재현된 원인 범위: 기존 `PRODUCTION_MINIMAP_POINT=(182,548)`은 ctor `(0,509)` 기준 미니맵 x상한180 밖이다. 보호 원본 `0x4516ae: lea eax,[ebx+0xb4]`, `0x4516b4: cmp esi,eax`, `0x4516b6: jg 0x451728`(실패)와 `0x451c10/16`의 `(0,509)`를 재확인했다. 양 lane WndProc/주입 좌표182와 camera 불변/count0이 이 결함과 일치한다. **현재 save006 실행의 widget 위치/LUT 및 유효 좌클릭의 camera 효과는 아직 미관측**이므로 전체 원인확정이나 단순 x=180 clamp 성공을 주장하지 않는다. 기존 주소 근거 `analysis/memory_maps/g5_minimap_click_router_lap762.md`, `g5_minimap_widget_ctor_lap759.md`(G5 읽기 전용 참조·재개/수정 금지).
2. 클릭 직전 실제 widget x/y와 LUT non-FF 유효 좌표를 읽고, 실제 owner0 producer/HQ1199의 현재 월드좌표로 카메라를 이동시킬 **정상 UI 입력**을 고른다. 범위 밖182를 고정 클릭하지 않는다. 원본에서 camera 변화·HQ 가시성과 실제 selection slot1199/type/owner를 먼저 확인한 뒤 같은 logical 입력을 candidate scale2에 적용한다. valid minimap 좌클릭이 안 움직이면 기존 camera/scroll 입력으로 HQ를 화면에 넣는 작은 수리로 진행한다. 직접 camera/unit/selection 메모리 write로 성공시키지 않는다.
3. 관측 UNKNOWN 대조를 PASS로 만드는 명확한 결함: 현재 `control_before/after={status: UNKNOWN}`, `_production_effect` false → `control_result=PASS`로 기록하고 생산 버튼까지 누른다. **실제 non-empty owner0 producer 선택과 두 관측 OBSERVED** 없으면 control UNKNOWN·버튼 미주입·생산 PASS 금지. 관측된 무입력 control이 안정적일 때만 기존 생산 셀 `(668,540)`·queue type7/command15·자원 또는 reserved 변화·신규 생성 증거를 측정한다. threshold/기대 ID를 낮추지 않는다.
4. 재중심 진단 gate write도 try/finally에서 원값 exact restore로 보호한다. 현재 minimap 명령 성공·drag release binding은 회귀로 유지한다. bounds 밖 거부/유효LUT 선택, 빈선택·UNKNOWN control 미주입, valid control 생산 witness, 예외 gate 원복을 필요한 regression으로 잠근다.
5. source 실행 provenance는 작은 JSON에 host probe/test SHA와 build manifest SHA를 **실행 직전/직후** 기록하면 된다. 새 추적기·대규모 관측회차를 선행조건으로 만들지 않는다. 원본/save SHA·새 game/prefix/display·공간20GiB·cleanup을 유지한다.
6. 최소수리→원본 fresh 확인→후보 paired→원인추적/수리/재실행을 PROMPT③대로 지속한다. 원본에서도 camera/생산 효과 미확정이면 시도와 실제 field를 UNKNOWN(original parity)로 보존하되 명확한 source/좌표 결함은 먼저 고친다. 이번 수리 범위로 장면/미러/validator/threshold/golden·게임 구현을 변경하지 않는다.

## 검사와 한계

`make doctor` ok=true/original verified(기본runtime manifest 부재는 runtime검증 아님), `make lint`·`make typecheck` PASS, `tests/test_g1_saved_scene_probe.py` **167 passed/5.73s**. 최종 문서freeze 뒤 `make check` 완주 결과는 STATUS에만 기록한다. Fast는 runtime/24k/144k·제품 승인이 아니다. G2/G5 종료·G3중단·G4보류·원본/개인세션 비접촉·커밋0 유지.

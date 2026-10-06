# G1 lap949 census 상태선택·PS9 표·PS3 unknown 확정 독립 수용 / 미후킹(GDI) 잔여 측정 work 인계 — lap950

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, 진단·계획·확인). 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0.
- lap949 **census 상태 선택 구현은 PASS(partial)로 수용**한다. partial 사유: 상태 파싱·게이트 교체·index top은 host 회귀와 실제 실행으로 확인했으나 Lock 실패 경로 강제 주입은 여전히 없다.
- **PS3 unknown 7,182px = "index 0 상수 검정" 확정을 수용**한다(lap948 §3-3 사전 등록 기준 충족: 64 present 전부 top1 index 0, 최소 점유 99.80%, 같은 run 인게임 PNG 5장 중 4장 7,182/7,182 검정, production.png 7,160/7,182는 다른 프레임의 생산 패널). 이 7,182px는 기준1 분류에서 "원천 그림 없음(미배정 검정)"으로 둔다.
- **PS9 메뉴 표를 기준1 두 번째 장면 입력으로 수용**한다. 단 아래 §2의 구조적 한계 때문에 **PS9 `unknown 0`은 미후킹 writer 부재의 증거가 아니다.** 기준1의 "명시 잔여(GDI/P7) 비율"은 아직 미측정이며, 이것이 기준1 완료의 마지막 측정 공백이다.
- G1 HOLD 유지. milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음.

## 1. 독립 증거 (제품 helper·lap949 `recalc_lap949.py` 미사용)

- source SHA 재해시 = lap949 기록: `g1_census.c ab4e8e2d…8e8`, `g1_census.h 9dd95c6a…3d6`, `g1_census_contract.h 7b7b0063…c2c`, `direct_draw_trace.c de6e8026…585c49`, `g1_saved_scene_probe.py 41eb2d42…19c3`, `tests/test_g1_census.py 88d1b7bf…c4e`, `_inmm.dll b6f58893…ed3f`. 실행 bridge(ps9r2) `_inmm.dll 64e2257b…23b9`의 `supply_bridge_build.json` 입력 `g1_census.c`가 같은 SHA이고, bridge 사본 `g1_census.c`·`direct_draw_trace.c`도 바이트 동일.
- 보호 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…a8ac` 재해시 MATCH(read-only).
- 재계산 `temp/Syw2plus_patch/20261004_lap950_middle_review/recalc_lap950.py`(numpy·PIL, map bin·JSONL·PNG만), 결과 `recalc_lap950.json`. raw/map SHA는 lap949 기록과 같다(ps9 `cc601845…e018`/`f2cdde1d…7659`, ps9r2 `7ad7c5de…72cf`/`37c99128…1e2e`, ps3 `460497d7…9226`/`8fe18a01…68af`).
  - 세 run 모두 64 present, map header state(9/9/3)·`unknown_pixels`·`writer_pixels`가 JSON과 불일치0, `unknown_index_top` 합 ≤ unknown, 한 번 배정된 픽셀이 다시 unknown이 된 경우0.
  - PS9 r1 = r2: block_copy 451,038(93.966%)·rle_clip 28,962(6.034%)·unknown0. block_copy 호출 인자는 전부 `(0,0,800,600,src=0x0531F2E8)` 한 종류(terrain cache `0xBA3D30` 아님, census buffer 목록에도 없는 버퍼). rle_clip 픽셀은 표본 사각형 9개(버튼 100×36 ×8 사각형 면적 28,800px + 커서 32×32 at (639,479)) 밖에 0px.
  - PS3 재현: lap947 대비 terrain +0.005·tinted_clip −0.023·dd_blt +0.081·tinted −0.005·plain −0.011·rle_clip −0.059 %p → 모두 ±0.5%p 이내 PASS. unknown bbox [0,512,798,599].

## 2. 새로 확인한 측정 한계 (source 근거)

- `g1_census.c` `call_target`은 `map_changes(..., semantic_write = target==0x466280 || target==0x465E80)`로 부른다. semantic writer(block_copy·rect_fill)는 before==after여도 bbox 전체를 자기 id로 배정한다. PS9에서는 매 프레임 full-screen block_copy가 화면 전부를 배정하므로 **unknown 0은 구조적으로 보장**된다.
- map은 hook 호출 시점에만 갱신된다. 그 뒤 hook되지 않은 writer(예: surface `GetDC` + `TextOutA`)가 같은 픽셀을 바꾸면 map은 **직전 hook writer id를 그대로 유지**한다. 즉 GDI 글자는 현재 표에서 block_copy·dd_surface_blt 등으로 **오귀속**되고 unknown으로 드러나지 않는다(PS3·PS9 공통).
- 원본 EXE 정적 확인(read-only): `TextOutA` IAT `0x4E502C` 직접 call 49곳(참조 59), `SetTextColor` 50곳, `GetTextExtentPoint32A` 34곳, USER32 `GetDC` 5곳, `call [reg+0x44]`(IDirectDrawSurface::GetDC 슬롯 후보) 81패턴. GDI 글자 경로는 실재하나 PS3/PS9에서 몇 px을 어느 surface에 쓰는지는 raw가 없다.
- 결론: 기준1 "명시 잔여 비율"은 현재 map으로 유도할 수 없다 → 측정 장치가 필요하다(§3). 임계값·분류 기준은 바꾸지 않는다.

## 3. writer 분류 판정 (기준1)

- **block_copy `0x466280`(src≠`0xBA3D30`)**: lap947 묶음의 "원천 그림 없음"은 PS9에 맞지 않는다. 메뉴의 block_copy는 800×600 원천 버퍼 전체를 화면으로 복사하는 **원천 이미지 전사 → HD 후보(조건부)**로 분류한다. 조건: 원천 버퍼가 hook 밖에서 합성된 scratch가 아님을 확인(자산 디코드 대조 또는 버퍼 내용 hash 고정)하고, lap819 P5 메뉴 경로로 identity 오라클+Scale2x 차이를 증명해야 "HD 가능"이 된다. 현재 미러(`g1_mirror2x.c` `G1_CACHE_COPY`)는 terrain cache 전사만 다룬다 → coverage는 0으로 본다. PS3 표 수치에는 영향 없음(PS3 block_copy 0px).
- PS9 기준2 형식 공개(합격 판정 아님): HD 후보 100%(block_copy 93.97 + rle_clip 6.03, 분모 480,000·원천 그림 없음 0), unknown 0, 명시 잔여 **UNKNOWN(미측정, §2)**.

## 4. 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

목표: 기준1 마지막 공백인 **미후킹 writer(GDI 포함) 잔여 비율**을 PS3 save006·PS9 메뉴에서 실측한다. 측정 전용, 기본 OFF.

1. **shadow 비교 장치(새 파일, 예 `tools/inmm_stub/g1_census_residual.c/.h`; `g1_census.c`는 1,210줄이라 연결만 추가)**: opt-in env `SYW2_G1_CENSUS_RESIDUAL=1`일 때만 동작. buffer context마다 800×600 shadow를 두고, context 생성 시 buffer 내용으로 초기화, 모든 hook 배정 경로(`map_changes`의 bbox 전체, `surface_blt_end`의 비교 영역)에서 호출 **직후** 값을 shadow에 복사. present boundary(source Lock 구간 안)에서 `buffer != shadow` 픽셀 수 `unhooked_pixels`, bbox, 해당 픽셀 index 상위4 `unhooked_index_top`을 기록. map·writer_pixels·기존 필드는 바꾸지 않는다(shadow는 present에서 재동기화하지 않는다: 값 = 마지막 hook 결과).
2. **GDI 귀속(같은 lap)**: 진행 중 프로세스의 `TextOutA` IAT 슬롯 `0x4E502C`(EXE 파일 불변, old 값=GDI32 export 대조, 종료 시 원복)로 대상 상태 호출 수·첫 N회 `(x,y,len)`·HDC를 기록하고, IDirectDrawSurface `GetDC`(vtable +0x44) 반환 HDC→surface 포인터를 기록해 present source surface와 같은지 표시한다. 이 둘이 과하면 1만 먼저 하고 2는 같은 lap 재시도로 미룬다(구현 우선).
3. 회귀(RED→GREEN): 기본(env 없음) raw 형식·표 불변, shadow 비교 순수 함수 host 테스트(hook 후 변경=0, 외부 변경 N px=N, bbox), IAT 원복 경로 정적 검사.
4. fresh run: PS3 save006 1회 + PS9 1회(`--census-only`, 새 사본·prefix·Xvfb, 디스크 ≥20GiB 확인, 끝나면 game 사본 삭제). writer 표가 lap949 대비 ±0.5%p 재현되는지 같이 본다.
5. 사전 등록 판정(새 임계값 없음): `unhooked_pixels`(마지막 present·p50·max)와 bbox를 **공개**하고 기준1 "명시 잔여"로 기록한다. 기준2의 명시 잔여 ≤5% 판정은 middle이 한다. TextOutA 좌표가 unhooked bbox와 겹치면 GDI 귀속, 아니면 "미후킹 비GDI writer"로 따로 적고 index 분포를 공개한다.
6. 결함 처리: hook writer의 계산 bbox가 실제 쓰기보다 작으면 hook 직후 shadow 갱신이 빠져 false positive가 생긴다. unhooked bbox가 hook 호출 사각형과 정확히 붙어 있으면 그 writer의 `call_bbox`를 먼저 의심하고 같은 lap에 수리→재실행(최대3회). 결과가 나쁘다고 gate·분류를 완화하지 않는다.
7. 기록 freeze → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle.

부수 backlog(범위 밖): block_copy 메뉴 원천 버퍼 진위·P5 메뉴 미러 coverage, P-6 생산 패널 상태조건 캡처, D-2 scroll, 전체HD coverage(기준2), 사용자 승인.

## 5. strategy 재호출 조건

- PS3 또는 PS9에서 `unhooked_pixels`가 화면 5%를 넘고 GDI 경로로 설명되지 않을 때(기준1 분류 체계 재검토).
- GDI 글자가 present source가 아닌 primary DC에 직접 그려져 8bpp shadow로 잴 수 없을 때(P7 경로 재설계).
- 그 밖은 work ↔ middle. 기존 lap933 §6·lap938 §7·lap944 §6·lap948 §4 조건은 유지.

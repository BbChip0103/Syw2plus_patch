# G1 lap947 census 수리·writer 분류표 독립 부분수용 / 메뉴 PS9 두 번째 장면 census work 인계 — lap948

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, 진단·계획·확인). 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0.
- lap947 **census 계측 결함 두 건 수리는 PASS(partial)로 수용**한다. partial 사유: 회귀 2건은 source 문자열 검사이며, post-Blt Lock 실패 경로를 실제로 일으킨 실행은 없다(정상 실행 captured==calls만 확인).
- lap947 **save006 PS3 writer 분류표를 lap819 §3 기준1의 첫 번째 장면 입력으로 수용**한다. 이것은 writer 능력 분류이지 기준2 coverage 합격이 아니다. 기준1은 두 번째 장면 분류와 명시 잔여(GDI/P6) 비율 공개 전까지 미완료다.
- unknown 7,160px(1.49%)는 **"미배정 상수 검정"으로 잠정 분류**한다(가설 지지, 직접 증명 아님 — 아래 §2). strategy 재호출 조건(unknown이 어떤 writer로도 설명 안 되고 5% 초과)에 해당하지 않는다.
- G1 HOLD 유지. milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음.

## 1. 독립 증거

- source SHA 재해시 = lap947 기록: `g1_census.c 285d59db…93cf8`, `g1_census.h ef0e3cc8…1079d`, `direct_draw_trace.c 4f3e8814…9f71`, `tests/test_g1_census.py 1fc3523e…d1fa`, `tools/inmm_stub/_inmm.dll 64bec74c…c9cb`. 실행에 쓰인 진단 bridge DLL은 별도 빌드 `f6dc569e…28b3`이며 그 `supply_bridge_build.json`의 입력 `g1_census.c` SHA가 위와 같다.
- 원본 EXE `[HQ]Syw2plus 2002.exe` `b56986e0…a8ac`, save006 `616b7997…0d064` 재해시 MATCH(read-only).
- raw `census_raw.jsonl e3f6bb89…318b`, `census_map.bin f7cc5432…28f7b`, 로그 `logs/gates/lap947-census-r1.output 10c28b18…5dff5`, full check 로그 `ff59dadb…af8b345` MATCH.
- source 검토: (a) `direct_draw_trace.c` BltFast primary 경로가 `(DWORD)(ULONG_PTR)source`를 `g1_census_present_boundary`에 넘기고 `emit_present_boundary`가 `source_surface`를 직렬화한다. (b) `++g_surface_blt_captured`는 `g1_census_surface_blt_end`의 비교 루프 뒤 한 곳뿐이며, end의 불일치 early return·post-Lock 실패(end 미호출)는 captured에 들어가지 않는다. Blt와 BltFast 두 attempt 경로 모두 같은 begin/end 쌍을 쓴다.
- 독립 재계산(제품 helper·lap947 `recalculate.py` 미사용): `temp/Syw2plus_patch/20261004_lap948_middle_review/recalc_lap948.py` SHA `a125c41a3d0ec517b24e8c5bb9721d037302a7e9e642f8d2d26bff118004f8fb`, 결과 `recalc_lap948.json` SHA `52b92e219626d054200b0aaecf92a417bd50177337fb3128321706e25ef070f9`.
  - 64 present 모두 map header(G1P1·sequence·800×600·pitch832·buffer·state3)·map/context offset·`writer_pixels` 10칸·`unknown_pixels`가 JSON과 일치(불일치 0). 9/9 install active, `calls_ps3=64/captured=64/missed=0`, `buffer_context_dropped=0`.
  - `present_source_surface`는 64개 모두 `0x01E75FD0`, `present_source_buffer`는 모두 `0x0233C7B0` → 분리 확인.
  - 마지막 present writer 표(last px): terrain_cache_transfer 283,931 · rle_tinted_clip 68,824 · dd_surface_blt 65,898 · rle_tinted 32,618 · rle_plain 20,281 · rle_clip 1,067 · rect_fill 135 · rect_border 86 · set_pixel/block_copy 0 · unknown 7,160. HD 후보 6 writer 472,619 = 98.46%, 원천 그림 없음 221 = 0.046%. world/HUD 분할과 p50도 lap947 표와 같다. 단 rle_tinted 비율은 32,618/480,000 = 6.795% → 반올림 **6.80%**(lap947 표의 6.79는 절사 전사; 수치 판정 영향 없음).

## 2. unknown 분류 근거와 한계

- 코드: `map_changes`(비semantic)와 `surface_blt_end`는 before==after 픽셀을 배정하지 않는다. map은 present 사이에 지우지 않으므로 마지막 unknown = 이 buffer context 생성 뒤 hook된 어떤 writer도 값을 **바꾸지 않은** 픽셀이다.
- raw: unknown 집합은 64 present 동안 단조 감소(10,513→7,160, 새로 unknown이 된 픽셀 0). 마지막 unknown 전부 y512..599·x0..798 HUD 띠(월드 0), 띠 70,400px 중 7,160.
- 같은 run의 인게임 PNG 4장(selection·drag·minimap·production) 모두에서 7,160px **전부 RGB(0,0,0)**; loaded.png는 전면 검정, menu.png는 다른 장면(PS9)이라 1,523/7,160만 검정 — 판정 제외.
- 한계: PNG는 primary 캡처이고 census present와 같은 프레임이 아니다. unhooked writer가 검정을 다시 쓰는 경우는 구분 불가하나 결과 화면은 같다. 따라서 "미배정 상수 검정"은 **지지된 가설**이며 직접 증명은 다음 work의 present 시점 index 측정(§3-3)으로 한다.

## 3. 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

lap819 §3 기준1·2의 "두 번째 장면(메뉴 PS9 또는 다른 save)"을 **메뉴 PS9**로 잰다. `save000.dat`는 provenance(비합성 여부)·load index 미확인이라 이번 범위 밖이다.

1. **census 대상 상태를 env로 선택**: 기본 PS3 동작·출력 형식은 그대로 두고(기존 raw/테스트 불변), 진단 env(예: `SYW2_G1_CENSUS_STATE=9`)가 있을 때만 `g1_census.c`의 state==3 게이트(present boundary·surface_buffer·blt attempt/begin·primitive calls 계수)를 그 상태로 바꾼다. raw의 `program_state`·`calls_ps3` 이름은 바꾸지 말고 `census_state` 필드를 추가해 어떤 상태를 쟀는지 기록한다. 회귀: 기본값=3 유지, env=9일 때 게이트가 9로 바뀜(RED→GREEN).
2. **probe**: `--census-only`에 상태 선택 옵션(예: `--census-state 9`)을 더해 env를 넘기고, PS9 대기 뒤 메뉴 화면에서 present 64개(또는 PS9 체류 중 가능한 최대)가 쌓일 때까지 머문 다음 기존 흐름대로 진행/종료한다. PS3 census 경로와 save006 load는 바꾸지 않는다.
3. **unknown 직접 측정(같은 run, 두 장면 공통)**: present boundary에서 source Lock 구간 안에 map==0 픽셀의 8bpp index 히스토그램 상위 4개를 `unknown_index_top`으로 기록한다. 사전 등록 판정: 모든 present에서 단일 index가 unknown의 ≥99%이고, 그 index가 같은 run의 캡처 PNG에서 해당 좌표 RGB(0,0,0)이면 "미배정 상수 검정" **확정**, 아니면 UNKNOWN으로 남기고 index 분포를 공개한다. PS3 save006도 같은 DLL로 1회 `--census-only`를 다시 돌려 lap947 표가 재현되는지(writer 비율 ±0.5%p) 함께 본다.
4. fresh run: 새 사본·prefix·Xvfb, 시작 전 디스크 여유 확인(현재 약20GiB — 20GiB 미만이면 자기 회차 옛 사본 정리 후 시작), 끝나면 game 사본 삭제. 산출: PS9 마지막 present writer 표(lap947 형식: HD 후보/원천 없음/명시 잔여/unknown, 비율 공개), PS3 재현 표, `unknown_index_top`.
5. 결함 처리: PS9에서 present_boundary가 0개면(메뉴가 BltFast primary가 아닌 Blt/Flip로 표시) 그 present 경로를 trace raw로 확인해 같은 lap에 수리→재실행(최대3회). 측정 결과가 나쁘다고 임계값·gate를 바꾸지 않는다.
6. 기록 freeze → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle.

측정식(사전 등록, 새 임계값 아님): PS9 표에서 기준2 형식 수치(HD 후보 비율, 원천 그림 없음 제외 분모, unknown, 명시 잔여)를 **공개만** 한다. 기준2 ≥90% 판정은 각 HD 후보 writer의 실제 미러 coverage 재측정 뒤 middle이 한다.

부수 backlog(범위 밖): P-6 생산 패널 상태조건 캡처, GDI(P7) 잔여 비율 측정 경로, D-2 scroll, 전체HD coverage, 사용자 승인.

## 4. strategy 재호출 조건

- PS9 census에서 unknown이 어떤 writer·상수 검정으로도 설명되지 않고 화면 5%를 넘을 때.
- 메뉴 present가 DirectDraw 경로 밖(GDI 직접 그리기 등)이라 lap819 §3 기준1 분류 체계 자체를 바꿔야 할 때.
- 그 밖은 work ↔ middle.

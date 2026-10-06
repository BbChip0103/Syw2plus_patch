# G1 lap951 미후킹 잔여 독립 수용 · 기준2 명시 잔여 판정 / 반투명 overlay writer 식별 work 인계 — lap952

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0.
- lap951 **residual shadow 장치·`TextOutA` 귀속 구현은 PASS(partial)로 수용**한다. partial 사유: Lock 실패 주입 없음, surface `GetDC` HDC→surface 매핑 미구현(좌표 겹침으로 대체).
- lap951 수치(PS3 마지막 2,625px 0.547%·p50 0.549%·max 21,423px 4.463%, PS9 64 present 전부 2,622px 0.546%)를 **raw 재계산으로 수용**한다.
- **정정(raw+PNG 확인):** lap951이 "x680~799·y360~440 **미니맵 상자**"라 부른 PS3 정상 상태 잔여 2,102px는 미니맵이 아니다. 실제 미니맵은 좌하단 마름모이고 잔여가 없다. 이 2,102px는 우하단 **화면 고정 반투명 게임 로고 워터마크 "임진록2+ 조선의 반격"**이다(§2).
- 기준2 "명시 잔여 ≤5%" 조항은 **측정 창 안에서 충족(부분)**으로 판정한다(§3). 기준2 전체(HD coverage ≥90%)와 G1은 HOLD.
- milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음. 미니맵 표기 정정은 raw로 재확인한 해석 오류 정정이며 근거 충돌이 아니다.

## 1. 독립 증거 (제품 helper·lap951 `analyze_residual.py`/`align_cov.py` 미사용)

- source 7파일 재해시 = lap951 기록(`g1_census_residual.h e029d66c…`, `g1_census.c 6c612fbd…`, `g1_census.h 941e638d…`, `direct_draw_trace.c 34ed5e59…`, `Makefile 29837dc2…`, `g1_saved_scene_probe.py d623cacb…`, `tests/test_g1_census.py 4e87f2df…`). 보호 원본 EXE `b56986e0…a8ac` 재해시 MATCH(read-only).
- raw SHA = 기록: PS3 r6 raw `42f81042…35bf`·map `e8c0b590…113d`·residual `331ee16f…b970`; PS9 map `0a03d5bc…f52f`·residual `9061895f…a977`. 전사 정정 2건(raw 재해시로 확인, 파일 불변): PS9 raw 전체 `8dfa06187f3bde901345d9298aac733f6317b23a79eba26a25ca37fd8ce7e5b4`(lap951 기록 `…e4b`), 기본 PS3 raw 전체 `07a0bf442bf8d9be271df8063cff0eb6d353117bfde6698571f270dd6ace25df`(lap951 기록 `…df25`).
- 재계산 `temp/Syw2plus_patch/20261004_lap952_middle_review/recalc_lap952.py`(numpy, residual/map bin·JSONL만) → `recalc_lap952.json`.
  - 두 run 64 record 모두 header magic `G1P1`·800×600·480000·map 순번 일치, 마스크 값 {0,1}, 마스크 합과 bbox가 `residual_boundary`의 `unhooked_pixels`·`unhooked_bbox`와 **불일치 0(128/128)**.
  - PS3 r6: last 2,625·p50 2,635·min 2,284·max 21,423(present 3). 최근 40 present 중 ≥90% 지속 core 2,529px, 합집합 2,782px, core bbox [127,13,792,575], core 중 로고 상자 2,102px. 마지막 present 구성: TextOutA 사각형 안 441·로고 상자(텍스트 밖) 2,102·기타 82; map 오귀속 terrain_cache 2,339·dd_blt 139·plain 49·tinted_clip 50·tinted 48.
  - PS9: 64 present 전부 2,622px, sample 있는 54 present에서 텍스트 사각형 안 99.54%.
- 기본 모드 무변경: `default_ps3` 이벤트×키 집합과 이벤트별 건수가 lap949 PS3 raw와 **완전 동일**, `calls_ps3 64 == captured 64`.
- 두 residual run: `status PASS`·`source_unchanged true`·`game_removed true`·`textout_iat active`·`slot_restored 1`. PS3 r6 Blt `calls 86 == captured 86`, 제외 `non_screen_surface_blt 22 == begin_rect 22`(표본 사각형 전부 101×40, pitch 304).

## 2. 잔여 구성 판정 (기준1 분류)

| 장면 | 성분 | px | 근거 | 기준1 분류 |
|---|---|---|---|---|
| PS9 | 버튼 라벨·버전·저작권 문구 | 2,622 | 텍스트 사각형 99.54%, `ps9_last_overlay.png` | 명시 잔여 P7(GDI) |
| PS3 | 자원 숫자·시계·중앙 메시지 | 441+82 | TextOutA 사각형·overlay | 명시 잔여 P7(GDI) |
| PS3 | 로고 워터마크(정상 상태) | 2,102 | 64 present 전부 지속 2,076px, bbox x702~792·y380~438; 카메라가 이동한 `production.png`에서도 같은 화면 위치·반투명(`ps3_logo_4captures.png`) | **미후킹 반투명 overlay, 명시 잔여(P6 후보) — writer 미확인** |
| PS3 | 초기 과도 성분(present 1~7) | 17,024~19,175 | 8번째부터 ≤45px; 위치가 같은 run `selection.png`의 반투명 회오리 효과와 일치(`ps3_present3_extra_overlay.png`) | 같은 미후킹 반투명 writer 가설, 장면 의존 |

- 로고 위치의 표본 hook 호출은 `rle_tinted_clip (666,366,76,98)`(x666~741) 둘뿐이다. 로고 지속 픽셀은 x792까지 가고, 화면 고정이며 카메라 이동 뒤에도 그대로다 → lap950 §4-6의 "hook `call_bbox` 과소" 가설은 로고에 대해 **가능성 낮음**(표본 기반, 완전 배제 아님).
- 가설 H-blend: 하나의 미후킹 반투명(혼합 테이블) writer가 로고와 회오리를 그린다. lap819 §2 P6(혼합 테이블/색조 LUT) 계열이다.

## 3. 기준2 명시 잔여 판정

- lap819 §3-2: 장면별 명시 잔여 ≤5%(분모 480,000).
- 현재 측정된 명시 잔여 = 미후킹 잔여 전체(위 표, GDI+반투명). PS3 정상 0.547%, **최악 4.463%**(과도 회오리), PS9 0.546% → **두 장면 모두 ≤5%, 측정 창 안 충족(부분)**.
- 부분 사유: (a) PS3 최악 여유 0.54%p뿐이고 반투명 효과는 장면 의존이라 효과가 많은 장면에서 초과할 수 있다. (b) hook된 writer 가운데 최종 미러가 HD로 덮지 못하는 부분(P6 미완 tinted 등)은 기준2 집계 시 명시 잔여로 더해야 하나 아직 미집계. (c) HD coverage ≥90%는 미측정.
- 임계값·분류 기준 변경 없음.

## 4. 기본 모드 non-screen Blt 분리: 적용하지 않음

- source 확인: `g1_census_surface_blt_attempt`의 분리는 `g_residual_enabled`일 때만이고 기본 모드는 모든 Blt를 센다. 기본 run은 64/64 PASS이고 lap949와 raw 형식이 동일하다.
- 기본 모드 gate 의미를 실패 없이 바꿀 이유가 없다 → 현행 유지. 기본 모드에서 800×600 미만 surface Blt 때문에 `captured≠calls`가 실제로 나오면 그때 같은 분리를 회귀 테스트와 함께 적용한다(gate 완화 아님, 대상 정의 정정).

## 5. 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

목표: 기준1의 마지막 미분류 writer인 **미후킹 반투명 overlay writer**의 EIP/함수를 식별하고, measurement-only census target으로 넣어 PS3 잔여에서 빠지는지 실측한다.

1. **EIP 포착(opt-in, 기본 OFF)**: 새 env(예 `SYW2_G1_CENSUS_WATCH=782,380`, residual 모드 필요). PS3 첫 present에서 고른 present source buffer의 해당 픽셀 주소에 1-byte 쓰기 하드웨어 watchpoint(DR0, RW=01, LEN=0)를 게임 render thread에 건다. VEH 처리기는 hit마다 EIP와 스택 상위 dword 중 EXE `.text` 범위 값 최대 8개를 기록하고, hook writer 안(`g_guard` 또는 call depth)의 hit는 writer 이름으로 따로 센다. hit 표본 상한과 대상 상태/64 present 창을 지키고 detach에서 DR을 해제한다.
   - 자체 시험: arm 직후 DLL이 같은 주소에 현재 값을 다시 써서 hit 1건이 나오는지 확인한다(Wine DR 지원 확인). 표본 픽셀 (782,380)은 64 present 전부 미후킹이고 표본 hook 사각형(x≤741) 밖이다. 대안 픽셀 (745..747,381).
   - DR이 Wine에서 안 걸리면 대안 B: 보호 원본 EXE read-only 정적 분석. primary present Blt caller `0x004D1066`의 상위 frame 함수에서 present 직전 호출들을 찾고, 256×256 혼합표 index 패턴(`mov al,[table+eax]` 류) 루프를 후보로 둔다.
2. 식별한 함수를 census target으로 추가한다(측정 전용, bbox를 인자에서 정확히 계산, 원본 old bytes 핀·원복). 주소와 근거는 `analysis/memory_maps/`에 기록한다.
3. 회귀(RED→GREEN): 기본(env 없음) raw 형식·표 불변, watch 비활성 시 DR/VEH 미설치, 새 target old-bytes 핀·원복 정적 검사.
4. fresh PS3 save006 residual run 1회(+필요 시 수리 재실행, 최대 3회). 디스크 ≥20GiB 확인, 끝나면 game 사본 삭제.
5. 사전 등록 판정(새 임계값 없음):
   - PASS = 식별 writer가 표에 나타나고, 로고 상자 텍스트 밖 미후킹이 2,102 → ≤100px, present 1~7류 과도 성분(나타나면)도 ≥90% 감소. writer는 기준1 "명시 잔여 P6" 또는 "HD 후보"로 분류해 근거를 적는다.
   - FAIL/UNKNOWN = EIP가 여러 함수에 흩어지거나 hook 뒤에도 잔여 유지 → 목록·수치 공개, 같은 추측 반복 금지.
   - BLOCKED = DR 불가이고 정적 대안도 이번 lap에 후보 0 → 근거 기록 후 middle.
6. 기록 freeze → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle.

부수 backlog(범위 밖): 기준2 HD coverage ≥90% 집계(미러 `covered_pixels`와 census 분류 결합), block_copy 메뉴 원천 버퍼 진위·P5 메뉴 미러, P-6 캡처, D-2 scroll, 사용자 승인.

## 6. strategy 재호출 조건

- 식별된 writer가 혼합표/LUT 기반이 아니어서 P6 경로를 쓸 수 없을 때(기준1 분류 체계 재검토).
- 어떤 측정 창에서든 장면 명시 잔여가 5%를 넘을 때.
- 그 밖은 work ↔ middle. 기존 lap933 §6·lap938 §7·lap944 §6·lap948 §4·lap950 §5 조건은 유지.

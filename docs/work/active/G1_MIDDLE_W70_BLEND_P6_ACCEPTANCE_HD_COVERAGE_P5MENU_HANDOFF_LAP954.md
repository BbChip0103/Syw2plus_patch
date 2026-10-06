# G1 lap953 반투명 writer 독립 수용 · 기준1 P6 분류 · 기준2 첫 HD coverage 집계 / P5 메뉴 block_copy 미러 인계 — lap954

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 954 읽기만.
- lap953 watchpoint 장치와 두 measurement-only target(`0x4672E0`·`0x467580`)을 **PASS(partial)로 수용**한다. partial 사유: 픽셀 표본 2개(782,380)·(223,279)만 watch, present 6~7 미분류 잔여 UNKNOWN, PS9·두 번째 장면에서 blend target 미실행, last-writer map 표에 rle_blend 미귀속(기본 raw 형식 보존 때문, 타당).
- **기준1: 두 writer를 "명시 잔여 P6(혼합표/LUT)"로 최종 분류**한다(§2). P6 경로(lap819 §2: 원본 혼합 테이블/색조 LUT를 정적 확인 후 같은 LUT로 HD 혼합)를 쓸 수 있는 LUT 기반이므로 lap952 §6 strategy 재호출 조건 아님.
- **기준2 명시 잔여는 줄지 않았다.** lap953의 "최대 4.463%→0.242%"는 *미분류* 잔여 감소다(root 경계 메모와 일치). PS3 명시 잔여(P6+P7+미분류) 최악은 여전히 21,423px(4.463%), 정상 상태 2,625px(0.547%) → ≤5% **측정 창 안 충족(부분)** 유지(§3).
- **기준2 HD coverage 첫 집계(기존 source-matched raw, 새 실행 아님): PS3 경계, PS9 FAIL** → 기준2 전체 FAIL(§4). 임계값·기준 변경 없음.
- milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음.

## 1. 독립 증거 (제품 helper·lap953 `analyze_blend.py` 미사용)

- source 5파일 + 분석 문서 재해시 = lap953 기록: `g1_census_watch.h 47fd4703…`, `g1_census.c d6496ea9…`, `Makefile 0687a078…`, `g1_saved_scene_probe.py adebdc96…`, `tests/test_g1_census.py 86a14d26…`, `g1_blend_writers_…lap953.md 1067bf2b…`. lap951 불변 파일 `g1_census_residual.h e029d66c…`·`g1_census.h 941e638d…`·`direct_draw_trace.c 34ed5e59…`. w6 bridge 사본의 C/H 5개 = 현재 source(cmp 동일); bridge `Makefile`은 `runtime_bridge.c` 추가 변형(lap951 bridge와 같은 차이). bridge `_inmm.dll`은 run마다 재빌드라 로컬 빌드 SHA와 다름(w6 `26712973…`, w7 `1a6c2c23…`) — 정상.
- 보호 원본 EXE `game.exe` = `b56986e0…a8ac`, save006 `616b7997…d064` 재해시 MATCH(read-only). w6/w7 `status PASS`·`source_unchanged`·`game_removed` true·fixture non-synthetic.
- raw SHA = 기록: w6 raw `61a6ecc0…7700`·residual map `235fc349…04b7`(map `f5cc288e…762b`), w7 `21fb736c…877f`, w2 `8f9ccda5…bb4`, w5 `f88f2b2e…073`, w4 `e735332e…a7a`.
- 재계산 `temp/Syw2plus_patch/20261004_lap954_middle_review/recalc_lap954.py`(SHA `ce220a32…4741`) → `recalc_lap954.json`(SHA `6ff60002…b93`):
  - w6 64 record header `G1P1`·800×600·map 순번 일치, 마스크 {0,1}, 합·bbox = `residual_boundary` **불일치 0(64/64)**. last 523(0.109%)·p50 532·min 200·max 1,162(present 7, 0.242%). 로고 상자 텍스트 밖 잔여 64 present 전부 **0**.
  - blend_call 70건 bbox = args 하위 16비트 부호확장 **불일치 0**. `0x467580`는 present 1~6만 6회, bbox `[47~55,187~197,330,200]`; `0x4672E0`는 64 present 매회 `[700,377,100,64]`(전체 상태 793회).
  - watch EIP 표: w2 `0x4662DE`(in_hook 63)·`0x4673D3`(hook 밖 63, present 2~64); w5 `0x4662DE` 63·`0x46659F`(in_hook 48)·`0x467692`(hook 밖 5, present 2~6). 자체 시험 `hits 1 PASS`. 기록과 일치. present 1은 DR arm 이전이라 w5가 present 1 호출을 못 잡은 것과 w6 호출 present 1~6이 모순 아님.
  - **가법 항등:** w6 `unhooked + Σblend changed`가 lap951 r6 `unhooked`와 present 1~5·8·9·62~64에서 **정확히 같다**(예 present 3: 331+2,084+19,008 = 21,423 = r6 max). shadow 차감이 다른 writer 픽셀을 과흡수하지 않았다는 직접 근거다. present 6(20,195 vs 20,115)·7(3,246 vs 20,670)만 다르다: w6에서는 회오리 효과가 present 6에서 끝났고 r6에서는 7까지 이어졌다(run별 효과 프레임 경계).
  - w7(env 없음): 이벤트 종류·건수·키 집합이 lap951 기본 PS3 raw와 **완전 동일**, blend/watch 이벤트 0, residual map 파일 없음.
- 원본 EXE 정적 디스어셈블(objdump, read-only) 대조: 프롤로그 `51 53 56 8B F1 57`(`0x4672E0`)·`51 0F BF 54 24 0C`(`0x467580`), 쓰기 명령 `0x4673CF mov [edi+ecx-1],dl`·`0x46768E mov [edi+edx-1],al`, 둘 다 `ret 0x14`·인자 word `movsx`. 분석 문서 서술과 일치.

## 2. 기준1 분류

| writer | 근거(정적) | 분류 |
|---|---|---|
| `0x4672E0` 로고 | 목적지 픽셀과 소스 인덱스의 팔레트 `renderer+0x419A0`(3바이트/색) 채널을 `(d>>1)+(s>>1)` 50% 평균 → 18비트 역 LUT `renderer+0x19A0` | **명시 잔여 P6** |
| `0x467580` 회오리 | 채널별 `(dst<<6)+src` 색인의 64×64 16비트 혼합표 `renderer+0x41CA0` → 같은 역 LUT | **명시 잔여 P6** |
| `0x467410`·`0x4676D0` | 같은 계열, PS3에서 hit 없음 | 존재만 기록(장면 등장 시 같은 분류 후보) |

- 정정(보강): lap953 분석 문서의 `0x467580` "가중표로 채널 값을 변환"은 정확히는 **채널별 2차원(목적지×소스) 64×64 혼합표**다. 분석 문서에 lap954 확인 절을 덧붙였다.
- 두 writer 모두 목적지 의존이라 현재 미러에서 덮은 픽셀 위에 그리면 `stale`이 되어 nearest로 나간다(§4의 PS3 stale에 포함). P6 HD 혼합 구현은 lap819 순서상 P3·P5 뒤이며 이번 인계 범위 밖이다.

## 3. 기준2 명시 잔여 (root 경계 적용)

명시 잔여 = P6(blend changed) + P7(TextOutA 사각형 안) + 미분류. 분모 480,000. 동일-present 합은 위 가법 항등으로 겹침 0이 확인된 present에서는 합집합과 같고, 나머지는 상한이다.

| PS3 w6 | P6 | P7 | 미분류 | 합(명시 잔여) |
|---|---|---|---|---|
| present 3(최악) | 21,092 (4.394%) | 235 | 96 | **21,423 (4.463%)** |
| present 7(미분류 최악) | 2,084 | 107 | 1,055 | 3,246 (0.676%) |
| present 64(정상) | 2,102 (0.438%) | 441 (0.092%) | 82 (0.017%) | **2,625 (0.547%)** |

- PS9은 lap951 수치(2,622px, 0.546%, 텍스트 99.54%) 유지.
- 판정: ≤5% 측정 창 안 충족(부분), 여유 0.54%p는 lap952와 같다. 0.242%는 미분류 잔여 수치로만 쓴다.
- present 6~7 미분류 416·1,055px: bbox `[100,40,619,577]`, 1,055 중 회오리 호출 사각형 합집합 안은 318뿐 → lap953의 "효과 끝 프레임" 가설은 **약함**. UNKNOWN 유지(0.22%, 우선순위 낮음).

## 4. 기준2 HD coverage 첫 집계 (기존 raw, 새 실행 아님)

- 입력: lap945 save006 Scale2x 후보 lane `20261004_lap945_production_witness/candidate/trace_raw.jsonl` SHA `6f524803…02d7`. 그 run의 bridge `g1_mirror2x.c` SHA `b70d044a…1804` = 현재 source = lap953 w6 bridge → 미러 source-matched.
- 식: present별 HD 픽셀 = `covered_pixels − stale_pixels`(`g1_mirror2x.c` 816~830: covered 중 원천이 expected snapshot과 다르면 stale → nearest). 분모 480,000(원천 그림 없음 미제외 = 보수적; PS3 제외분 0.046%, PS9 0).
- 스크립트 `hd_coverage_lap945_raw.py`(SHA `fbf5a42c…65fe`) → `hd_coverage_lap945_raw.json`(SHA `4e9997a9…4cc`).

| 상태 | present | HD min | p10 | p50 | last | ≥90% 비율 | stale p50 | V1 outside diff |
|---|---|---|---|---|---|---|---|---|
| PS3 | 891 | 89.79% | 90.33% | **90.42%** | 90.43% | 99.2% (idx 6~12 미달) | 42,729 | 0 |
| PS9 | 55 | 5.68% | 5.68% | **5.73%** | 5.68% | 0% | 1,892 | 0 |
| (참고) 35 | 158 | 2.18% | — | 2.26% | — | 0% | — | 0 |

- **PS3: 경계 — 판정 보류.** p50는 90% 이상이나 초기 present 7개(idx 6~12)가 89.79~89.99%. "모든 present ≥90%" 해석이면 0.21%p 미달이다. 기준에 통계량이 정해져 있지 않으므로 여기서 새 해석을 정하지 않고 두 값을 공개한다. 정상 상태 stale 약 42.7k(8.9%)가 여유를 깎는다.
- **PS9: FAIL(5.73%).** lap950 §3 예상("메뉴 block_copy는 현재 미러가 다루지 않음 → coverage 0")과 일치. 덮인 것은 rle_clip 버튼(6.03%)뿐.
- 따라서 **기준2 = FAIL**(PS9), G1 HOLD. strategy 재호출 조건(명시 잔여 >5% 등) 아님: PS9 명시 잔여는 0.546%이고 coverage 미달 원인은 이미 계획된 P5 메뉴 미러 부재다.

## 5. 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

목표: lap819 P5 메뉴 경로 — PS9 full-screen block_copy `0x466280`(`(0,0,800,600)`, src `0x0531F2E8`류 비-terrain 버퍼)를 미러에 HD 후보로 옮겨 PS9 HD coverage를 실측한다.

1. 원천 진위(lap950 §3 조건): PS9 동안 block_copy src 버퍼 내용 hash가 present 간·두 run 간 고정인지 기록(측정 전용 이벤트, 기본 raw 형식 불변). hook 밖 합성 scratch 증거(같은 장면에서 hash 변동)가 나오면 그 사실을 기록하고 FAIL/UNKNOWN로 middle.
2. 미러: 기존 `G1_CACHE_COPY`(terrain cache 전사) 경로를 확장하거나 같은 형식의 별도 분기로, src가 terrain cache가 아닌 block_copy를 identity/Scale2x로 미러에 재실행하고 `g_covered`/expected snapshot을 갱신한다. 원본 old bytes 핀·원복·기존 terrain 경로 회귀 불변.
3. 회귀(RED→GREEN): 메뉴 block_copy 분기 정적·단위 검사, 기존 terrain cache copy·V1 검사 불변.
4. fresh save006 `--hd-source scale2x` 실행(메뉴 PS9 경유 → PS3) 1회 + 필요 시 수리 재실행. 같은 run에서 PS9·PS3 present별 `covered−stale` 표를 공개. identity 모드 대조가 필요하면 `--hd-source identity` 1회 추가. 디스크 ≥20GiB, 끝나면 game 사본 삭제.
5. 사전 등록 측정(새 임계값 없음, 기준2 원문 ≥90% 그대로):
   - PASS = PS9 모든 present HD ≥90%, V1(`hd_mask_outside_diff_subpixels`) 0, identity 오라클 차이 0, PS3 표가 lap945 대비 하락하지 않거나 하락 원인 공개.
   - FAIL = PS9 <90% → 미달 픽셀의 writer·stale 원인 공개. 같은 추측 반복 금지.
   - BLOCKED = src 버퍼가 매 present 합성 scratch라 identity 오라클이 성립하지 않음 → 근거 기록 후 middle(strategy 재호출 판단).
6. 기록 freeze → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle.

부수 backlog(범위 밖): PS3 초기 present 6~12 미달·정상 stale 42.7k 구성(어떤 writer가 covered를 stale로 만드는지), present 6~7 미분류 귀속, P6 HD 혼합(LUT 재사용), P7 GDI 2배 재그리기, P-6 캡처, D-2 scroll, 사용자 승인.

## 6. strategy 재호출 조건

- 메뉴 block_copy src가 hook 밖 합성 scratch라 P5 메뉴 경로가 성립하지 않을 때(두 번째 장면 선택 재검토 — 다른 save는 lap948 기준 provenance 미확인).
- 어떤 측정 창에서든 장면 명시 잔여가 5%를 넘을 때.
- 그 밖은 work ↔ middle. 기존 lap933 §6·lap938 §7·lap944 §6·lap948 §4·lap950 §5·lap952 §6 조건 유지.

# G1 lap955 PS9 메뉴 block_copy 미러 독립 수용 / PS3 stale 구성 측정 인계 — lap956

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 956 읽기만.
- lap955 `transfer_block_copy_to_screen`(PS9 `0x466280` packed 800×600 소스 Scale2x 미러)을 **PASS(partial)로 수용**한다. partial 사유: 메뉴 한 장면·save006 한 fixture, `(0,0,800,600)` 외 non-cache block copy 미지원(PS3·PS35 호출 0), 경계 링 아티팩트 소량(§3), PS35 수치 상승은 이월 효과(§4), 동적 API 실패 주입 미검증(기존과 같음).
- **기준2 PS9 HD coverage: FAIL→PASS(partial)**: 모든 present ≥90%(최저 99.454%). **PS3는 여전히 경계**(min 89.793%, idx 6~12)이고 PS35·HUD/tinted/P6/P7 HD·D-2·사용자승인이 남아 **기준2 전체는 미합격**이다. 임계값·기준 변경 없음.
- milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음.

## 1. 독립 증거 (제품 helper·lap955 `hd_cov.py` 미사용)

- source 4파일 재해시 = lap955 기록: `g1_mirror2x.c c876f645…5e0a`, `.h 4514f602…6141`, `direct_draw_trace.c 29218392…0082`, `tests/test_g1_mirror2x.py eeaeaf51…06e7`. probe `adebdc96…3951` = pair `execution_source` before/after(unchanged true).
- bridge 사본 대조: r2 = 현재 source(두 파일 일치). r1/id `direct_draw_trace.c 6614a6b5…`는 `mirror2x_metrics` 지점만 다름(`mirror_details[3072]`·`layer_details[400]`·5필드) — 기록된 되돌림과 정확히 일치. idoff `g1_mirror2x.c fb7c9f79…`는 822행 호출 한 줄만 `/* lap955 attribution run: disabled */` — 기록과 일치.
- 보호 원본 `Syw2plus/game.exe b56986e0…a8ac`, `save/save006.dat 616b7997…d064` read-only 재해시 MATCH. 네 pair `status PASS`·`scene_state_equal`·양 lane `source_unchanged` true, fixture non-synthetic. `local/runtime/lap955_menu_*`는 game 사본 없음·manifest/output/prefix 보존(PROMPT 런타임 provenance 규칙 준수).
- 재계산 `temp/Syw2plus_patch/20261004_lap956_middle_review/recalc_lap956.py` → `recalc_lap956.json`(SHA256 `223ba389…7fb6`), present별 `100·(covered−stale)/480000`:

| run (raw SHA) | 상태 | present | min | p50 | <90 idx | V1 max | inside max | menu calls(Δ) / hash first=last / changes |
|---|---|---|---|---|---|---|---|---|
| r1 `547c9307…` | PS9 | 48 | 99.454 | 99.454 | 없음 | 0 | 115,795 | 1→48(+1/present) / `1777000796` / 0 |
| r1 | PS3 | 897 | 89.793 | 90.413 | 6~12 | 0 | 104,212 | Δ0 |
| r2 `e1c0404a…` | PS9 | 46 | 99.454 | 99.454 | 없음 | 0 | 115,795 | 1→46 / 동일 / 0 |
| r2 | PS3 | 896 | 86.670 | 90.414 | 7~12, 579~630 | 0 | 104,242 | Δ0 |
| id `9b4f047a…` | PS9 | 55 | 99.454 | 99.454 | 없음 | 0 | **0** | 1→55 / 동일 / 0 |
| idoff `be889139…` | PS9 | 47 | 5.677 | 5.731 | 전부 | 0 | 0 | 0 |
| idoff | PS3 | 886 | 87.031 | 90.408 | 6~10, 429~468 | 0 | 10,306 | 0 |
| lap945 `6f524803…` | PS3/PS9 | 891/55 | 89.793/5.677 | 90.419/5.731 | 6~12/전부 | 0 | | (기능 없음) |

  - 모든 run `fallback` 없음·`success` 전부·팔레트 위반 0·`menu_copy_pixels == calls×480000`. PS9 stale p50 2,622px(0.546%) = lap951 PS9 TextOutA 수치(P7 명시 잔여)와 일치.
  - 귀속: idoff PS9 = lap945 PS9(5.677/5.731)와 정확히 같고, 분기 ON에서만 99.454% → 상승은 이 분기 효과다. 소스 hash가 4 run 196회 호출 전부 같은 값 → present마다 바뀌는 scratch 아님(BLOCKED 아님).
  - PS3 비하락: r1/id의 미달 idx(6~12/6~11)와 min이 lap945와 같다. r2 579~630·idoff 429~468의 하락은 §5.

## 2. source 검토

- 분기 가드 `(x,y,w,h)==(0,0,800,600)`, 소스≠`G1_CACHE_BASE`(cache 경로는 기존 `transfer_cache_to_screen`), 타깃≠cache base·≠panel-bound 버퍼, renderer stride≥800·height≥600, 소스 480,000B `readable_bytes`(VirtualQuery commit·NOACCESS/GUARD 제외) 확인 뒤에만 동작. 원본 호출을 먼저 수행하고 결과를 그대로 반환하므로 원본 동작 불변.
- `g1_scale2x_build_masked(src, stride=w, mask(all 1), w, w, h, hd, 2w)` 인자 순서는 헤더 시그니처와 일치. 비-scale2x 모드는 최근접. `g_covered=1`·`g_expected_snapshot=소스`라 이후 다른 writer가 덮은 픽셀은 present 비교에서 stale→nearest로 떨어진다(정합 보호).
- 타깃이 실제 present될 버퍼인지는 확인하지 않지만, 아니라면 expected 불일치로 stale 처리되므로 잘못된 HD가 노출되지 않는다. 호출당 HeapAlloc 2.4MB+해시 480kB는 PS9 present당 1회라 수용.
- 직렬화: `layer_details[400]` 최악 359자+NUL(형식 고정부 249자 재계산), `mirror_details[5000]`에 대해 raw present 줄 최대 2,723B. 기본(env 없음) 키 의미 불변, 키 5개 추가만.

## 3. PNG 대조 (`png_cmp_lap956.py`·`png_resid_lap956.py`, JSON SHA256 `6ea29d21…3144`·`a7659b06…dc5f`)

- baseline `menu.png`(800×600, 4 run 동일 SHA `34d43b31…2888`) vs candidate(1600×1200; r1=r2 `1eaec895…18fd`, id=idoff `f5f717aa…1883`).
- 구성: identity 후보의 논리 픽셀은 baseline과 617px만 다르고 전부 `[400..670,300..498]` 커서 위치 차이 → 메뉴 구성 일치.
- r2 후보 vs Scale2x(baseline): 서브픽셀 3,984 차이(0.21%), vs 최근접 118,028 → 후보는 Scale2x 렌더다. 후보 자신의 논리 프레임(identity 후보 추정)의 Scale2x와 비교하면 1,518 서브픽셀(0.079%) 차이: 1,152는 최근접(=stale fallback; y≈1000~1157 버튼 글자·TextOutA 영역, P7), **366(0.019%)은 Scale2x도 최근접도 아님** — 그중 94는 stale 픽셀 4-이웃 링(Scale2x가 덮이기 전 이웃 값을 씀). per-pixel stale 판정 설계의 기존 한계(cache 경로와 같음)로 기록, gate 아님.

## 4. PS35 수치 상승은 이월(carry-over)이다

- PS35 8.869~8.898%(lap945·idoff 2.18~2.25%)지만 PS35 동안 menu_copy 호출 Δ0. 메뉴에서 `g_covered=1`로 표시된 픽셀 중 PS35 화면에서 같은 값이 남은 약 31.9k px가 covered로 계속 집계된 것이다. **새 PS35 writer coverage가 아니므로 PS35 진척으로 세지 않는다.** 내부 픽셀은 올바른 Scale2x지만 경계는 §3과 같은 링 위험이 있다. PS35 장면 의미 미분류는 그대로 backlog.

## 5. PS3 transient stale burst (분기와 무관)

- r2 idx 579~630(t≈29.1~31.7s, 52 present)·idoff idx 429~468(t≈22.0~23.9s, 37 present)에서 covered는 그대로인데 stale이 42.5k→58.8~60.2k(+16~17.7k, 3.5~3.7%)로 2~2.6초 튀고 원래대로 돌아온다. r1·id·lap945에는 없다. 분기 OFF(idoff)에도 있으므로 lap955 변경에 귀속하지 않는다(lap955 판단 수용). 원인 writer는 미측정 → §6 범위.

## 6. 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

목표: PS3 stale(정상 약 42.7k=8.9%, 초기 idx 6~12 추가분, §5 burst)을 **어느 writer가 만드는지** 픽셀 단위로 측정해 PS3 경계 해소의 대상 writer를 정한다. 측정 회차이며 coverage 합격 회차가 아니다.

1. **opt-in stale mask dump**(기본 OFF): 예 `SYW2_G1_STALE_MASK=<PS3 present index 목록>`(probe `--stale-mask 6,9,12,300,last`). present 비교 시 해당 index에서 800×600 바이트 맵(0=uncovered, 1=covered·일치, 2=covered·stale)을 헤더(`magic`·program_state·present index·game_tick·covered·stale 합)와 함께 trace 옆 파일로 쓴다. env 없으면 raw 바이트/키/건수가 lap955 r2와 같아야 한다(회귀 테스트로 pin; 기존 pin·`mirror_details[2048]` 불변).
2. RED→GREEN: env 파싱·index 매칭·헤더/합계 일치 단위 테스트, 기본 모드 직렬화 불변 테스트.
3. fresh save006 scale2x 1 run(필요 시 burst 재현 위해 1 run 추가 허용). 맵 합 == present 레코드 `covered`/`stale` **불일치 0**이 장치 PASS 조건.
4. 분류: 같은 save006 PS3 census last-writer map(lap949/951 기존 artifact 또는 fresh `--census-only`)과 present index로 정렬해 stale 픽셀을 writer 클래스(terrain·tinted·tinted_clip·dd_surface_blt·rle_plain/clip·blend P6·GDI/TextOutA·미분류)로 표를 낸다. 정렬 한계(서로 다른 run, 타이밍 차)는 공개한다.
5. 사전 등록: 장치 PASS = 맵/레코드 불일치 0 + 기본 raw 불변. 분류 PASS(진단) = 정상 present stale의 ≥95%가 한 클래스에 배정. FAIL = 맵 불일치 또는 기본 raw 변경. 가설(판정 아님): H1 정상 stale 다수가 `dd_surface_blt`(lap947 13.73%) 영역, H2 초기 idx 6~12 추가분은 P6 blend(`0x467580`, present 1~6 회오리)·이월 경계.
6. 다음 middle이 분류 표로 "미러 경로가 있는 writer"(다음 work 구현 대상)와 "명시 잔여"를 나눈다. 임계값 신설·gate 완화·PS3 통계량 새 해석 금지(lap954 §4 두 값 공개 유지).

## 7. strategy 재호출 조건

- 기존 조건(lap933 §6·lap938 §7·lap944 §6·lap946·lap952 §6) 유지.
- 추가: stale 분류에서 정상 present stale의 50% 이상이 어떤 후킹 가능한 writer에도 속하지 않고(미분류·GDI 외 경로) 미러 범위 축소 없이는 PS3 ≥90% 경계를 해소할 수 없다고 측정될 때.

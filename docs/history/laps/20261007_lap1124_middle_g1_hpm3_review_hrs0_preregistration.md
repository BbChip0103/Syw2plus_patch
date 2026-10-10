# 2026-10-07 | lap1124 | G1 middle — H-PM3 독립 검수 + H-RS0(결과 화면 PS29 HD) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1123 work → middle 검수 요청), STATUS 다음 한 가지, lap1123 기록, lap1122 사전등록 §3. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1124_preserved_lap1123_escalate_sol.txt`로 byte 일치 보존(SHA256 `c6c98665be360dac…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: lap1123 raw만 사용(run b·c 수리 켬, off = `SYW2_G1_PAUSE_SNAPSHOT=0`; 새 게임 경로 → act → Esc PS23 → 저장 창 → 돌아가기 → 불러오기 창 → 돌아가기 → 환경설정 창 → Esc → 계속하기, 저장·불러오기 실행·설정 변경 없음). run a는 dwell 10초 trace dropped 5,662라 work와 같이 근거 제외.
- artifact SHA(ESCALATE_SOL 앞자리와 일치): trace_raw b `239041438bc409f6…`·c `36d0c8e89a1a5342…`·off `47adda819d2f1f15…`, new-game-path-result b `41be2b7b…`·c `68759050…`·off `4703f256…`.
- source 동일성: `g1_mirror2x.c` `98d261be…`·`g1_pause_snapshot.h` `cdcbc36b…`·`g1_mirror2x.h` `815b58e6…`·`direct_draw_trace.c` `6bf459cb…`·`Makefile` `d9184cfe…`(lap1122와 같음 = 제품 C 변경 0 확인), probe `e665390b…`·`tests/test_g1_new_game_path.py` `f88e8877…`. lap1123 full check 로그(`5fdb2938…`, 06:56:48, 1752 passed·5 skipped) 뒤 수정된 tools/tests/checks/patches 파일 0.

## 1. 독립 재계산 (새 스크립트)

- 스크립트: 공유 temp `20261007_lap1124_middle_review/scan_lap1124.py`(`fe5ea528…`, PS23 이벤트 나열) → `scan_pm3_{b,off}.txt`, `recalc_lap1124.py`(`9ca86b2d…`) → `recalc_lap1124.json`(`3130e5a5…`). work 스크립트를 쓰지 않고, PS23 구간에서 stale+restore > 30,000인 present 6개를 순서대로 (저장·불러오기·환경설정) × (열림·닫힘)으로 잡았다(PS23 구간 연속·6개 assert 통과 3/3). 정착 = 닫힘 다음 present부터 다음 창 열림 직전(또는 PS23 끝)까지.

| run | 창 | 열림 seq: restore(off는 stale) | 닫힘 seq: stale / restore / HD | restore+stale vs off | 다음 present 손실 | 정착 min·p50(n) |
|---|---|---|---|---|---|---|
| b | 저장 | 4046: 51,636 | 4948: 165 / 95,154 / 99.939% | −1.34% | 165 | 99.939·99.939(430) |
| b | 불러오기 | 5379: **51,604** | 5846: 165 / 95,156 / 99.939% | −1.29% | 165 | 99.939·99.939(425) |
| b | 환경설정 | 6272: **51,571** | 6716: 10 / 85,357 / 99.939% | −1.07% | 10 | 99.939·99.939(437) |
| c | 저장 | 4056: 51,850 | 4926: 165 / 95,810 / 99.939% | −0.66% | 165 | 99.939·99.939(407) |
| c | 불러오기 | 5334: **51,872** | 5787: 165 / 95,812 / 99.939% | −0.61% | 165 | 99.939·99.939(418) |
| c | 환경설정 | 6206: **51,807** | 6641: 10 / 85,541 / 99.939% | −0.85% | 10 | 99.939·99.939(416) |
| off | 저장 | 4062: stale 51,709 | 4961: 96,609 / 0 / 79.847% | — | **44,660** | 90.649·90.670(430) |
| off | 불러오기 | 5392: stale 51,730 | 5851: 96,562 / 0 / 79.857% | — | **44,622** | 90.657·90.678(432) |
| off | 환경설정 | 6284: stale 51,670 | 6730: 86,288 / 0 / 79.990% | — | **34,795** | 90.718·90.718(440) |

- PS3 resume(PS23 이탈 뒤) 77 present min 100%(b·c·off). PS3 전체 min b 100·c 99.946(act select/drag, work와 같음)·off 100. 경과 p95 7ms(3/3, 증가 0). fallback 0·hresult≠0 0·success≠1 0(3/3). result JSON: `trace_dropped_count` 0(3/3), 메뉴 8창 V1 outside·안전 7종·fallback 모두 0, `scale2x_validator` PASS(hd_mask_outside 0·palette 0), `sub_close` load=click·options=esc, 하위 창 state 모두 23, resume 3, `source_unchanged` true. `mirror_validator` BLOCKED는 nearest oracle 장면 불일치(기존, 게이트 아님).
- 밴드 2×2 균일 비율(같은 run `pause.png` → `pause_return_*.png`): 불러오기 b 75.53→75.66(+0.14)·c 75.82→75.93(+0.11), 환경설정 b 75.77→75.42(−0.35)·c 75.73→75.40(−0.33) → ±1%p PASS. off 77.14→99.36·76.90→99.26(결함 재현). 밴드 논리 픽셀 차이 on 1,051/861·1,015/853 vs off 10,911/8,382.
- 하위 창 위치(캡처 `pause` 대비 논리 차이, 독립 확인): 저장·불러오기 bbox x240..571·y100..409, 열 밀집 x240..559(오른쪽 560..571은 그림자 추정); 환경설정 열 밀집 x256..543(work 밴드 정의 x257 시작과 1 px 차이, 판정 영향 없음).
- 캡처 열람: b `load_window`(저장 목록, 슬롯 7 = 기존 save006, 불러오기 버튼 비활성 클릭 없음)·`options_window`(사운드·배경음악·속도·밝기·마우스 방식, 확인/취소 — 창 안 클릭 0) 정상. b·off `pause_return_load`·`pause_return_options` 밴드 크롭 비교(`20261007_lap1124_pm3_return_on_b_vs_off_crop.png`): 깨짐·흑색 띠 0, 환경설정 Esc 뒤 커서가 환경설정 버튼 위(hover 표시) — 의도된 상태.

**work 수치와 판정 지표 불일치 0.**

- **정정 1(전사·정의):** work가 공개한 하위 창 열림 restore "load 51,705/51,973, options 51,672/51,908"은 열림 present 값에 약 21 present 앞의 단발 restore 101을 더한 값이다. 열림 present 값은 불러오기 51,604/51,872, 환경설정 51,571/51,807(저장 51,636/51,850은 work와 같음). 판정 밖 공개 항목이라 영향 없음.

## 2. 판단 요청 처리

- **열림 present 복원(≈51.6~51.9k) — 수용, 거짓 복원 아님.** lap1122 이탈 2와 같은 패턴: off의 같은 열림 present stale 51,709/51,730/51,670과 같은 크기이고, on은 그 present stale 0이다. 복원 조건이 "화면 값 == 진입 스냅샷 값"이라 실제로 보이는 논리 색의 HD를 낸 것이다.
- **"이탈 직전 복원 101" — 위치 정정·무해 판정.** 이번 raw에서 101은 PS23 이탈 직전이 아니라 **불러오기·환경설정 창 열림 약 21~22 present 전**(b 5357→5379, 6250→6272; c 5314→5334, 6184→6206)에 1회씩 있다. off에서는 같은 자리에 stale 101이 생겨 다음 창이 덮을 때까지 covered에서 빠진다(off 435,216→435,115). 즉 저장/불러오기 창을 (464,372)로 닫은 뒤 다음 메뉴 버튼으로 커서가 옮겨갈 때의 버튼 표시 변화로 추정(writer UNKNOWN)되고, on은 스냅샷 값과 같아 정상 복원(stale 제거)한다. lap1121의 "이탈 직전 101"도 저장 창 닫기 뒤 계속하기 클릭 앞이라 같은 계열이다. 수리 대상 아님.
- **영구 잔여 — 수치 보강.** 정착 PS23 결손은 165(불러오기·저장 닫힘)·10(환경설정 닫힘)만이 아니다. b·c 모두 저장 창 열림 약 21 present 전에 stale 309(off 303)가 생기고(진입 스냅샷과 다른 값 = 첫 버튼 hover 표시 추정), 저장 창이 그중 182를 덮어 127이 남는다. 그래서 정착 covered는 479,708(=480,000−127−165)이고 HD 99.939%는 이 둘을 모두 포함한다. 불러오기 닫힘 165는 저장 닫힘 165와 같은 값(같은 창 기하·같은 act 장면, lap1121 458은 다른 장면)이다. 0.061%로 사전등록 손실 ≤1,000 안이며, writer 귀속은 backlog로 둔다.
- 진입 present stale 291: 이번에는 off에만 있고 on b·c는 0(lap1121은 on·off 모두 291). 장면·타이밍 의존으로 보고 backlog 유지.
- **H-PM3 판정: `PASS(partial, 기술·격리)` 수용.** 사전등록 PASS 항목(하위 창마다 닫힘 HD ≥98.6·정착 min ≥98.6·restore+stale vs off ±2%·닫힘 다음 손실 ≤1,000·PS3 100·V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·p95 증가 ≤2ms·밴드 ±1%p·캡처 정상)을 켬 2/2, 두 하위 창 모두 충족. off가 두 하위 창 결함을 재현(손실 44,622·34,795)해 제외 조건 없음. partial 사유: 영구 잔여 292 px(127+165) writer 미귀속·부하 대표성 낮음·하위 창 dwell 3초(trace 버퍼 8,192 한계)·불러오기 실행/설정 변경 경로 미측정(의도). 사용자 합격도 G1 마감도 아니다.

## 3. 남은 HD coverage 목록 정리

- "혼자하기 대기실"은 이미 측정됐다: lap1108 H-OS0(lap1109 수용) PS5 혼자하기 대기실·PS7 접속방식. 남은 항목은 PS7·PS5 글자·버튼 모서리 stale 1.2~1.8% 귀속(backlog 그대로)이다. STATUS 목록에서 별도 항목으로 빼고 backlog로 합친다.
- "PS2 로딩"은 lap1110/1111에서 새 게임 경로 미러 trace에 PS2 present 0으로 관측됐다(사용자에게 미러 경로로 보이는 화면이 없음). 별도 측정 대상이 아니라 "PS2 present 0" 관측으로 backlog 유지.
- "타이틀(PS9 이전 인트로)"·승리 화면은 미측정. 다음은 실제 재현 fixture가 이미 있는 **결과 화면(PS29, 패배)** 이다.

## 4. 다음 work 사전등록(Sonnet) — H-RS0: 결과 화면(PS27→PS29 "패배했습니다.") HD coverage 측정 → 미달 시 귀속

- **근거:** 게임이 끝나면 사용자는 반드시 결과 화면을 본다. 지금까지 HD를 잰 상태는 PS9·PS7·PS5·PS35·PS3·PS23뿐이다. 재현 fixture가 이미 있다: lap982 H-G7o `orig` run(원본 EXE `b56986e0…`, 자리 2 lobby-snapshot)이 만든 `save001.dat`(공유 temp `20261005_lap982_g7_hg7o/orig/save001.dat`, 1,713,222 B, SHA256 `57872666b436a4620c21cc99ef7c22413809e49de80b401ae5f27aa2e14210b8`)를 **새 프로세스 타이틀에서 불러오면** 원본 G7 결함으로 local 0 → ps `[3, 27, 29]` → "패배했습니다." 결과 화면이 뜬다(lap982 D, 캡처 `…/orig/shots/20261005_054854_d_watch_end.png`, 이번 회차 직접 열람: 전체/병사/건물/자원 탭·참전한 사람 표·확인 버튼(논리 약 (712,561))).
- **가설 H-RS0:** 결과 화면은 PS9·PS35처럼 전면 메뉴 copy 경로로 그려져 PS29 HD ≥98.6%이다. 아니면 미러 밖 writer가 있어 귀속이 필요하다.
- **RS0-0 하네스(TDD):** `tools/g1_saved_scene_probe.py`
  - `SAVE_FIXTURES`에 `g7defeat` 추가: 이름 `save001.dat`, SHA 위 값, 목록 index는 첫 run의 불러오기 목록 캡처로 확인해 고정(lap982는 index 2였음). **fixture는 참고 저장소 `Syw2plus_re/Syw2plus/save/`에 복사하지 않는다**(읽기 전용) — 공유 temp 원본 경로(또는 Git 제외 `local/fixtures/`의 SHA 일치 사본)에서 private game 사본으로만 복사하고, SHA 불일치면 시작 거부. 기존 save006/save000 경로 불변.
  - `--fixture g7defeat --scene-actions none` + 결과 화면 대기 옵션(예: `--result-screen`): 로드 뒤 PS3 → `ps==29` 대기(최대 60초, 못 오면 상태 열·캡처 기록 후 FAIL) → PS29 dwell(candidate mirror present ≥256 또는 10초) → 캡처 `ps29.png` → 탭 병사·건물·자원 클릭(논리 좌표는 캡처로 확인, 표시 전환만) 각 dwell·캡처 → 확인 클릭 → 다음 state 기록(PS9 등)·캡처. PS27 present도 따로 센다.
  - 단위 테스트 RED→GREEN: fixture 표 불변(save006/save000)·SHA 불일치 거부·참고 저장소 쓰기 경로 없음·상태 대기 실패 시 FAIL 기록.
- **RS0-1 격리 run 2회**(`--hd-source scale2x`), baseline lane도 같은 fixture로 결과 화면 도달 확인.
  - 기록: 상태 순서·상태별 present 수·HD 첫/min/p50·stale max·covered_min·V1 outside·안전 7종·fallback/hresult·dropped·menu/partial/frame copy 계수 증가(PS29에서 어느 경로가 도는지)·경과 p95·캡처 열람(1600×1200 UI 정상, 확대 화질 차이는 허용).
  - **PASS(2/2):** PS29 present HD min ≥98.6%(첫 전환 present 1개는 공개만)·탭 전환 뒤 각 창 min ≥98.6%·확인 뒤 다음 상태 HD 비회귀(PS9이면 100)·V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·캡처 정상.
  - **FAIL:** 위 미달 → 같은 회차에 기존 census 경로로 PS29 writer 귀속(필요하면 `--census-state`에 29 추가, census-only)까지 하고 수리 없이 middle로 넘긴다. 하네스·좌표·fixture 결함이면 고쳐 재실행(구현 우선). 실패 가설 2회 또는 60분이면 BLOCKED로 근거와 함께 넘긴다.
  - 공개 한계(미리 적음): 결과 화면은 G7 원본 결함으로 만든 패배 화면이다(fixture 생성 때 lobby-snapshot 자리 조작, lap982 공개). 승리 화면 문구·레이아웃 동일성은 UNKNOWN(별도 fixture 필요). 부하 대표성 낮음.
- 공통: 하네스 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 약 153GiB 여유), game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음(lap1104 판본 유지). 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

backlog 추가·정정: H-PM3 영구 잔여 127(저장 창 열림 전 stale 309 중 남은 부분)+165 writer, 메뉴 버튼 hover 계열 단발 101/309, 진입 stale 291(on/off 장면 의존). 기존 backlog(H-PM2 458, PS7·PS5 모서리 stale, 타이틀 인트로, 승리 화면 등)는 STATUS 그대로.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS에만 쓴다.
- 전체 `make check` SKIP: 이번 변경은 문서뿐이고 하네스·테스트·C source는 lap1123 full PASS(1752) 때와 같다(위 source 동일성·check 로그 뒤 변경 0).

## 다음 한 가지

work(Sonnet): §4 H-RS0 — RS0-0 `g7defeat` fixture·결과 화면 경로(TDD) → RS0-1 격리 2회 → PS29 HD PASS/FAIL(미달 시 같은 회차 census 귀속), middle 검수 요청.

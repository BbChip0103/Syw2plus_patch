# 2026-10-06 | lap1069 | G1 work — H-S3 두 번째 장면(save000) 키 hold 스크롤

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 source(C·bridge) 변경 0, commit 0.
- 가설(lap1068 §3): 현재 후보는 다른 맵(save000)의 키 hold 스크롤에서도 hold 창 stale이 save006 수준(≤10)이다. 아니면 새 미후킹 writer가 드러난다.
- 예상 PASS / FAIL: S3-1 두 lane 같은 카메라 관측열·≥1칸·최종=시작·`terrain_scroll_parity` PASS / S3-2 hold 창 p95 ≤ 고정+16·tps 비 ≥0.95 / S3-3 hold 창 stale 합 ≤10(초과는 FAIL 아닌 새 잔여+귀속) / 비회귀 안전 7종 0·cleanup·source_unchanged·마지막40 0·save006 nd hold 합 1 / FAIL = 크래시·안전 위반·두 lane 칸 수 불일치 2 run 재현.
- 변경 파일: `tools/g1_saved_scene_probe.py`(SHA256 `8816512f17ed…`)·`tests/test_g1_saved_scene_probe.py`(`a0cda0671dd5…`) — 둘 다 git 미추적, uncommitted 보존.
  - S3-0(테스트 먼저 RED 2건 → GREEN): `_scene_option_error`가 `--scene-actions none` + `--terrain-scroll`을 허용(terrain-trace·rice·scroll-phase 결합 거부 유지, `--fixture save000`은 여전히 none 필요), loaded-only 중단을 `scene_actions == "none" and not terrain_scroll`로 좁히고 스크롤 블록(scroll_after 캡처) 직후 `raise _LoadedOnlyComplete()`로 save006 전용 selection/drag/minimap/production을 건너뜀, `--p4b-s-snapshot`은 save006 lap888 reference 전용이라 save000에서 거부. 기존 테스트 2개를 새 허용 범위에 맞게 수정, 소스 구조 테스트 1개 추가. `.venv/bin/python -m pytest tests/test_g1_saved_scene_probe.py` 204 passed, ruff PASS. (시스템 `python3`는 Pillow `get_flattened_data` 없음 → 항상 `.venv` 사용.)
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` probe `validate_original_source`·protected SHA 통과, 5 run 모두 `execution_source.unchanged` true·lane `source_unchanged` true. fixture: 비합성 save000(pinned `s1_load_evidence.FIXTURES`, loaded 카메라 (39,53)·tick 50596·owner 8·unit 375), 후보 = 현재 작업 트리 bridge(제품 불변).
- 카메라 방향 선택(근거): 로드 카메라 (39,53)에서 DOWN=(+1,+1)/UP=(−1,−1)이므로 `DOWN,UP` = (63,77)까지 24칸 왕복. save006 DOWN clamp 상한 ≈(179,128)보다 한참 안쪽이고 x·y ≥ 0 여유 충분 → clamp 없음. 실제로 s1·s2·d1·d2 전부 clamp_free true.
- 실행(공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1069_work_hs3/`, 로그 `logs/gates/lap1069_s3_*`, 순차, load ≤8, game 사본 각 run 뒤 삭제 확인):
  - s1·s2 비진단 pair: `--hd-source scale2x --fixture save000 --scene-actions none --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys DOWN,UP --stale-mask 0-1600/30` (exit 2 = pair status HOLD, 아래 사유).
  - d1·d2 진단 pair: 위 + `--layer-drift --screen-watch --drift-samples "150,40;100,70;200,70"`, mask `120-295`(d1; 실제 기록 64개 상한이라 ord 120..183만)·`200-263`(d2).
  - nd1 save006 비회귀: lap1065 nd와 같은 옵션(`--terrain-scroll-hold --terrain-scroll-keys UP,DOWN --p4b-s-snapshot --reference-completed-states <lap888> --stale-mask 129-143,227-230,308-322`) exit 0.
  - pair-result SHA 접두: s1 `1d590121`·s2 `c4ef1465`·d1 `c05252de`·d2 `0da7e992`·nd1 `7bb3283e`. 스크립트 `run_s3.sh` `f3512289`·`analyze_s3.py` `3466631c`(work 분석용; middle은 쓰지 않고 재계산).
- 측정값 / 판정(hold 창 = down_input_tick..final_observation_tick, ps3 ord 124..292·169개, tick plan 50716/50752/50812/50848/50884):
  | run | 이동(base/cand) | 카메라열·최종=시작 | hold p95 / 고정 p95 | tps 비 | hold 창 stale 합(위치) | 마지막40 | parity |
  |---|---|---|---|---|---|---|---|
  | s1 | 24/24·24/24 | 같음·true | 7 / 7 | 1.0032 | **0** | 0 | PASS |
  | s2 | 24/24·24/24 | 같음·true | 7 / 7 | 1.0041 | **117**(ord 231 단발, tick 50823, 카메라 (52,66)) | 0 | PASS |
  | d1(diag) | 24/24 | 같음·true | 13 / 11 | 0.9969 | **3**(ord 228 단발) | 0 | PASS |
  | d2(diag) | **23/24**·24/24 | **다름**·base 최종 (38,52) | 12 / 11 | 0.9949 | **3**(ord 228 단발) | 0 | **HOLD** |
  | nd1 save006 | 24/24·24/24 | 같음·true | 7 / 7 | 1.0023 | **1**(ord 125) | 0 | PASS(pair PASS) |
  - **S3-0 PASS**: 하네스가 save000 키 hold 스크롤을 실행(2 run 비진단 + 2 run 진단). 두 lane 실제 키 입력(receiver 수신)·release tick 일치.
  - **S3-1**: 비진단 s1·s2 PASS(두 lane 24칸 왕복, 관측열 동일, 최종 (39,53)). 진단 d2에서 **baseline 단독 23칸**(24 아님)으로 lane 칸 수 불일치 1건 — baseline 쪽 키 시작 위상(backlog "hold keydown 위상 경합")이며 후보 결함 아님. FAIL 기준(두 lane 불일치 2 run 재현)은 미충족(1/4 save000 run).
  - **S3-2 PASS**: 4 run 중 비진단 2 run은 p95 7/7·비 ≥1.003. 진단 run은 진단 오버헤드로 hold p95 12~13이나 고정+16 이내, 비 0.995~0.997(≥0.95).
  - **S3-3 초과 → 새 잔여(FAIL 아님)**: s2 hold 창 합 117 단발(ord 231). s1은 0이라 비결정 단발. 진단 d1·d2는 같은 ord 228(tick 50821, 카메라 (53,67), UP hold 약 10칸째)에서 **3 px, x702..704·y0(화면 맨 윗줄)**로 2/2 재현, 둘 다 stale = `primitive_stale_pixels_total`(원시 primitive 재호출 경로, 변화 present의 `terrain_*`·`tinted_*` 호출은 정상 범위·compose 호출 85~104)이라 터레인 layer 캐시가 아니라 **primitive(스프라이트/blend 계열) 한 개의 화면 가장자리 3 px** 로 귀속. 117 px 단발(s2)은 mask 미수집이라 위치 UNKNOWN(비진단 run이라 mask 샘플 0-1600/30에 ord 231 없음). 귀속 한계: mask 64 상한 때문에 d1은 228을 못 덮었고 d2가 처음 덮음.
  - 비회귀: 5 run 안전 7종 max 0, cleanup `ok`·`game_removed`·`prefix_processes_after []`(각 lane), `source_unchanged` true, 마지막40 stale 0(save000 고정 구간도 0; lap1010의 약 20.6k 잔여는 이후 hook들로 해소된 상태 확인), nd1 hold 합 1(ord 125 단발) 유지·pair PASS. save000 pair status HOLD 사유 = (a) V2/V2s/V2q capture gate BLOCKED(`scene-actions none`은 selection/drag/minimap/production 태그 부재 — 기존 사유, gate 의미 불변), (b) `input_effect_comparison` HOLD(장면 동작 없음). 둘 다 이번 변경이 만든 것이 아님.
- 한계 / UNKNOWN: save000 hold 스크롤은 DOWN→UP 24칸 왕복 한 방향 쌍만(좌우·모서리·가장자리 마우스·사람 속도 미측정). s2의 117 px 위치/writer 미귀속. d2 baseline 23칸은 위상 경합 backlog 1건 추가. 제품 G1 마감·사용자 승인 아님.
- 독립 검수 상태: work 자체 계산만. fresh Opus middle 독립 재계산 필요(`loop/ESCALATE_SOL`: 마일스톤 판정/ S3-3 새 잔여 계속·중단 결정은 middle 몫).
- 다음 한 가지: middle(Opus)이 s1/s2/d1/d2/nd1 pair-result·trace를 새 스크립트로 재계산(특히 s2 ord 231 117 px, d1/d2 ord 228 3 px 위치 x702..704·y0, d2 baseline 23칸)하고 H-S3 수용 여부와 다음 work(① top-row 3 px primitive 귀속·수리(mask 64 상한을 고려해 `--stale-mask` 225-232 + 상위 y0 band 감시), ② 좌우 가장자리·모서리 스크롤, ③ HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비) 선택을 사전등록한다.

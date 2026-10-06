# 2026-10-07 | lap1083 | G1 H-D2k (모서리 edge 스크롤) + D-0 디스크 회수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승인·수용 판정은 하지 않는다(독립 검수는 다음 middle).
- 가설: lap1082 §5 H-D2k — 마우스 모서리(대각) edge 스크롤(UPLEFT,DOWNRIGHT / UPRIGHT,DOWNLEFT)도 E-0 왕복·E-1 p95 ≤ 고정+16·E-2 hold 창 stale 0. 한 칸 기대 이동은 두 변 부호의 합(UPLEFT (−2,0)·DOWNRIGHT (+2,0)·UPRIGHT (0,−2)·DOWNLEFT (0,+2))을 가설로 둔다.
- 예상 PASS / FAIL: lap1082 §5 — 모든 모서리 run E-0~E-2 PASS이면 H-D2k PASS(partial). stale > 0이면 `--stale-mask <ord>` `--layer-drift --screen-watch` 진단 1회로 writer 귀속 + FAIL(귀속). 안전 위반·크래시 = FAIL.
- 변경 파일 / source 해시 접두 / 커밋: uncommitted. `tools/g1_saved_scene_probe.py` `1fa1e665…`(`_EDGE_DIAGONAL_SIGNS`·`_EDGE_SCROLL_KEYS`·`_scroll_edge_point` 모서리 4종·`_scroll_edge_option_error`/`_scroll_edge_keys` 모서리 쌍 허용·`SCROLL_CAMERA_SIGNS_EDGE`·`_scroll_camera_steps` 축별 부호 크기 나눗셈·`_scroll_corner_clamp_free`·action `scroll_corner_clamp_free`), `tests/test_g1_saved_scene_probe.py` `9ee0fd6f…`(새 테스트 4). 제품 C/bridge 불변.
- 원본 SHA / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` MATCH(archive 스크립트가 pair-result `source_exe_sha256`로 대조, 모든 run `source_unchanged` true·cleanup ok·game 사본 삭제). 비합성 save006(`--p4b-s-snapshot`)·save000(`--scene-actions none`), scale2x HD, load 2.4~4.8(≤8), run마다 대기 0 s 후 순차. 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1083_work_hd2k`(`run_k.sh` `706f997d…`·`analyze_hk.py` `dbd34053…`·`analysis_hk.json` `0bdf560d…`), 로그 `logs/gates/lap1083_hk_k{1..6}.{log,exit}`.

## D-0 디스크 회수 (게임 실행 전)

- 시작 여유 6.30 GiB. 기존 `local/maintenance/20261005_disk_cleanup_closed_prefixes_resume/archive.py`를 **복사·수정**해(원본 불변) `local/maintenance/20261007_lap1083_prefix_archive/archive.py`(`08bf53e3…`)로 실행. 대상 = `local/runtime/lap1051`~`lap1056_hz_d4`의 이 루프가 만든 **종료된** private prefix 31개(`lap10[5-7]*` 오름차순, lap1079 이상은 제외 경계, 목표 20.5 GiB 도달 시 중단).
- prefix마다: pair-result(공유 temp 836 매핑)에서 `source_unchanged`·원본 SHA·`cleanup.ok`·`prefix_processes_after` 비어 있음·`game_removed` 확인, `manifest.wine.private`·`created_new`·`prefix == manifest 옆 prefix`·`game` 부재 확인, 프로세스 args/`lsof +D`/Wine `WINEPREFIX` 환경 참조 0, 전체 inventory(mode·mtime·size·SHA256·symlink target), `tar --acls --xattrs` + `zstd -3`, tar 전 멤버 SHA/mode/symlink 대조 뒤에만 삭제. 4개(0·10·20·30번째)는 **실제 전체 restore** 후 inventory 완전 일치(`restore_verification_000/010/020/030.json`) 확인 후 restore 사본 삭제. 삭제는 `prefix`만. `manifest.json`·`output`·로그·raw·PNG·공유 temp 불변, 종료 시 pair-result raw 재해시 일치.
- 결과: 31 archive(각 179 MiB, 디렉터리 5.5 GiB 인벤토리 포함), **여유 6.30 → 20.89 GiB**(≥ 20 PASS). `report.json` `687a88ff…`·`plan.json` `50012adc…`(plan = lap10[5-7] 전체 154 prefix, 실제 처리 31). 기존 JSON이 가리키는 경로 변경 0(prefix 내부 경로가 필요하면 해당 archive에서 exact restore).

## K-0 하네스 (테스트 먼저 RED→GREEN)

- RED: 새 테스트 3(`_scroll_edge_point` 모서리 4종·옵션/키 쌍 검증·`_scroll_camera_steps` 가설 합)이 실패(키 부재) → GREEN. 추가 테스트 1(`_scroll_corner_clamp_free`). `_parse_scroll_keys`는 모서리 키를 계속 거부(키보드 hold 경로에 X11 키 없음), 기존 UP/DOWN·LEFT/RIGHT 기본과 오류 문구(`UP, DOWN, LEFT or RIGHT` 포함)는 그대로. `tests/test_g1_saved_scene_probe.py` 217 passed, `make lint` PASS.
- 모서리 좌표: 창 꼭짓점(`origin`·`origin+(800s−1, 600s−1)`), release = 중앙. 기대 이동 가설은 **원본 lane 관측으로 확인됨**: UPLEFT 24칸 (158,101)→(110,101) = 칸당 (−2,0), DOWNRIGHT 24칸 (110,101)→(158,101). 하네스 기대값을 고쳐 통과시킨 것은 없다.

## 실행 결과 (순차 6 run, 게임 6회 launch)

| run | pair | 옵션 | hold 창 stale 합 / 비0 present | 마지막40 | 비고 |
|---|---|---|---|---|---|
| k1 `1739380b5cb6` | PASS | save006 UPLEFT,DOWNRIGHT | **240,703 / 20** | 0 | E-0 두 lane 24/24칸·왕복 (158,101)·p95 gap 52·elapsed 7·tps 20.02·안전 0 |
| k2 `68b4b3909be7` | PASS | save006 UPLEFT,DOWNRIGHT | **240,703 / 20**(k1과 동일 값) | 0 | 결정론 재현, p95 gap 53·elapsed 8 |
| k3 `22d230b9b2cf` | PASS | save006 UPRIGHT,DOWNLEFT | **0 / 0** | 0 | UPRIGHT 24칸 (158,101)→(158,53)·DOWNLEFT 복귀, p95 gap 54·elapsed 7 |
| k4 `3856677be41d` | HOLD | save000 UPLEFT,DOWNRIGHT(`--scene-actions none`) | **15,459,820 / 111** | **51,680** | UPLEFT (39,53)→(0,54) **20칸·맵 경계 clamp**(x=0 도달), DOWNRIGHT 24칸 → 최종 (48,54) ≠ 시작(clamp라 왕복 복귀 아님, 두 lane 같음), input_effect·terrain_scroll_parity HOLD·v2 계열 BLOCKED(save000 기존 모양) |
| k5 `5253bd49d2ff` | PASS | save006 LEFT,RIGHT edge(= hl3 비회귀) | **0 / 0** | 0 | 24칸 왕복 (158,101), 계수 hl3과 같은 규모 |
| k6 `368525917417` | PASS | k1 + `--layer-drift --screen-watch` 진단 | 241,094 / 22 | 0 | 진단 계측 때문에 p95 elapsed 11 |

- 공통: 안전 7종 최대 0(6 run), 12 lane `game_removed`·`source_unchanged`·`cleanup.ok` true, `trace_raw` stale vs `stale_mask` 불일치 0(6 run), 모든 mask SHA 일치.
- **E-2 FAIL(k1·k2·k6)**: stale present = ord 126~133(3,184→19,222→18,057)·137(2)·140~145(19,269→2,421)·221~225(2,304→15,012). 카메라 x가 2칸/present로 112~150 구간을 지나는 때만. 마스크 bbox는 대각선으로 이동하는 마름모(폭≈190·높이≈200, 약 18k px)로 ord마다 화면 좌상→우하로 ≈35×32 px씩 이동.
- **귀속(k6, 표본 3점 (360,69)·(540,162)·(300,454), `--stale-mask 126-145,221-225`)**: stale 표본 10/10 = 마지막 쓰기 전 화면 값이 최종 writer 값(`val_eq_scr` 10/10, tid 280): `0x467CCF` ∈ 기 hook `0x467B00` 6개, `0x467692` ∈ 기 hook `0x467580` 4개(snapshot은 `0x4662DE` 값에 머묾). 두 hook은 이미 설치돼 있으나 **호출이 미러되지 않았다**: `layer_drift` 기록 `why=reject_size`가 **17건, 전부 w=330·h=200 영역**(p126~133·140~144·222~225, x 34..473/9..261/247..53, y −126..98/294..421/423..334)이고 stale present 집합을 덮는다. 코드 근거: `mirror_blend_wrle`(0x467580)은 `(x1−x0) > G1_OVERLAY_MAX_WIDTH(320) || (y1−y0) > G1_OVERLAY_MAX_HEIGHT(160)`이면 reject_size, `mirror_blend_clip`(0x467B00)은 높이 band(H-D2r)는 있으나 `x1−x0 > 320`이면 reject_size다(`tools/inmm_stub/g1_mirror2x.c` 4213·4301). 폭 330 > 320. 계수: k1·k2·k6 `blend_467580_reject_size` 21(k3·k5 16)·`blend_467B00_reject_size` 89(k3·k5 0). 즉 UPLEFT 경로는 330×200 구름/그림자 블렌드를 지나며 둘 다 미러 거절.
- k3(UPRIGHT,DOWNLEFT)·k5(LEFT,RIGHT)는 같은 시작 카메라에서 다른 맵 구간을 지나 330×200 호출이 없었다(계수 0/16 = 기존) → stale 0.
- k4(save000)는 stale이 clamp 직후(ord 138~)부터 ≈189k px로 **마지막40까지** 남는 별개 종류다. `counters_467`의 `blend_*_reject_size`가 전부 0이므로 위 원인이 아니다(다른 hook 계수는 `analysis_hk.json`에서 미분류). 진단 run은 하지 않았다(UNKNOWN). 비회귀 근거: lap1081 hl5(save000 DOWN,UP 키 hold)는 clamp 없이 24칸 왕복(최종 (39,53))·hold 0.

## 판정

- **H-D2k 판정: save006 UPRIGHT,DOWNLEFT·LEFT,RIGHT 비회귀 PASS, UPLEFT,DOWNRIGHT FAIL(귀속 완료: 330×200 blend reject_size), save000 UPLEFT,DOWNRIGHT FAIL(clamp 뒤 stale ≈189k, 귀속 UNKNOWN).** 사전등록상 모든 모서리 run PASS가 아니므로 H-D2k PASS(partial)가 아니다. 크래시·안전 위반은 없다(안전 7종 0).
- 한계: stale 크기는 현재 맵·세이브(save006)의 한 구간에서 나온 것이고, 330×200 블렌드가 다른 구간·정상 키 스크롤에서도 나오는지는 미측정이다(`blend_*_reject_size` 계수로 기존 run 재집계 가능: lap1051 이후 save006 run 중 UP/DOWN edge 계수 467B00 reject_size 0). 진단 계측 run(k6)은 p95 elapsed가 11로 높다(계측 오버헤드, 제품 판정 아님). save000 k4는 시작 카메라가 이미 맵 경계에서 가까워 clamp가 나온 것이다(hl5는 다른 입력).

## 다음 work 후보 (middle 사전등록 대상)

1. **H-W330(구현, FEASIBLE 근거 충분):** `0x467580`(`mirror_blend_wrle`)과 `0x467B00`(`mirror_blend_clip`)이 폭 > 320(실측 330×200)을 reject하지 않도록 한다. 최소안: 폭 방향 band(타일) 반복 또는 `G1_OVERLAY_MAX_WIDTH` 확장(공유 상수 — 버퍼 크기·테스트 단언 영향 확인 필요). 합격: k1과 같은 옵션 2회 hold 합 0·reject_size 0·E-0·E-1·안전 0, k3·k5·save006 고정 비회귀, 새 C 모델 테스트(0x467580은 클립 없음·wrapped 쓰기 미추적 주의).
2. **H-D2k-s0(save000 clamp):** 같은 옵션에 `--layer-drift --screen-watch` 진단 1회로 clamp 뒤 ≈189k stale writer 귀속.

## 검사

- 기록·인계 freeze 뒤 `make check` 1회(결과는 STATUS에만 보강).

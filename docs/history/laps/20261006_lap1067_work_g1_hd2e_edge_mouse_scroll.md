# 2026-10-06 | lap1067 | G1 work — H-D2e 가장자리 마우스 스크롤

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 source(C·bridge) 변경 0, commit 0.
- 가설: 가장자리 마우스 스크롤도 키 hold와 같은 화면 경로를 타므로 현재 후보에서 hold 창 stale·성능이 키 hold와 같은 수준이다(lap1066 §3 사전등록).
- 예상 PASS / FAIL: E-0 두 lane 같은 칸 이동·복귀·최종 = 시작 카메라 / E-1 hold 창 p95 ≤ 고정+16·tps 비 ≥0.95 / E-2 hold 창 stale 합 ≤10 / 비회귀(pair·안전 7종 0·cleanup·source_unchanged·마지막40 0·기존 hold 테스트 불변). BLOCKED = baseline도 안 움직임.
- 변경 파일: `tools/g1_saved_scene_probe.py`(SHA256 `a80bb3177f6d…`)·`tests/test_g1_saved_scene_probe.py`(`368e06a69322…`) — 둘 다 git 미추적(`??`)이라 diff 없음, uncommitted 보존. 제품 C/bridge 불변.
  - E-0 하네스(테스트 먼저 RED 4건 → GREEN): `--terrain-scroll-edge`(`--terrain-scroll` 필요·`--terrain-scroll-hold`/`--terrain-scroll-keys`와 배타, 내부적으로 UP,DOWN 키 슬롯 + hold 의미 = release tick까지 유지), `_scroll_edge_point`(UP=창 위 가장자리 행·DOWN=창 아래 마지막 행·release=창 가운데, baseline 800×600/candidate 1600×1200 각자 origin·scale 환산), `_send_pointer_edge`(기존 `x11_mouse_click._move` XTest 포인터), `_send_scroll_until_camera_change(send_edge=)`(키 edge 대신 주입, 기본은 기존 `_send_key_edge`), `_scroll_edge_option_error`. edge 모드는 키 WM_KEYDOWN/UP receiver 요구를 면제(`receiver_waived_for_edge`)하고 슬롯 루프 앞에서 포인터를 창 가운데로 둔다. 결과 JSON에 `terrain_scroll.edge`·`actions[].scroll_edge` 추가.
  - 새 테스트 4개(좌표 매핑·`send_edge` 주입·옵션 배타·배선 소스 검사). `tests/test_g1_saved_scene_probe.py` 203 passed, `make lint`·`make typecheck` PASS.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac`(probe `validate_original_source` 통과·`source_unchanged` true 2 run). fixture: 비합성 save006, 활성 플레이어/군대는 저장 그대로(부하 증명 아님), 후보 = 현재 작업 트리 bridge(제품 불변).
- 실행: `run_e.sh e1`, `run_e.sh e2`(공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1067_work_d2e/`, 로그 `logs/gates/lap1067_d2e_{e1,e2}.log`, exit 0·0, load 2.9~3.3 ≤ 8, 순차, game 사본 각 run 뒤 삭제). 옵션 = `--hd-source scale2x --terrain-scroll --terrain-scroll-edge --p4b-s-snapshot --reference-completed-states <lap888 scroll-phase-diagnostic-result.json> --stale-mask 0-1600/30`(비진단). pair-result SHA `5679852f0922…`(e1)·`a816764b7e65…`(e2), 분석 `analyze_d2e.py` `c6886f0395cc…` → `analysis_d2e.json` `86ecd5d9f339…`.
- 측정값 / 판정:
  - **E-0 PASS(2/2):** baseline·candidate 모두 UP (158,101)→(134,77) 24칸, DOWN (134,77)→(158,101) 24칸, clamp 없음, 두 lane 카메라 관측열 동일, 최종 = 시작 (158,101), input tick 24692/24788 = 목표(키 hold 왕복 lap1065 nd와 같은 값). 포인터가 실제로 창 가장자리에서 게임을 스크롤시킴(baseline 포함) → BLOCKED 아님.
  - **E-1 PASS:** hold 창 p95 7/7(고정 7/7), tps 비 1.0021/1.0021 (≥0.95).
  - **E-2 PASS:** hold 창 present idx 123..291(169개) stale 합 **1**(idx 125 단발 1 px, 키 hold nd 기준 1과 동일)·최대 1·>100 0, 마지막40 0/0. → 진단 불필요.
  - 비회귀: pair PASS(input_effect·minimap·terrain_scroll_parity·V1/V2/V2s/V2q·scale2x 전부 PASS), 안전 7종 max 0, cleanup `ok`·`game_removed`·`prefix_processes_after []`(4 lane), `source_unchanged` true. 기존 `--terrain-scroll-hold` 테스트·경로 불변.
- 한계 / UNKNOWN: 위/아래 가장자리만(좌우 가장자리·모서리 대각은 미측정). 두 run의 stale 수치·p95·tps 비가 같은 것은 게임이 50 ms tick 단위로 결정론적이기 때문(trace SHA는 다름 `5672faee…`·`fe722edf…`). 가장자리 머묾을 사람 마우스 속도로 움직일 때의 부드러움은 미측정. 제품 G1 마감·사용자 승인 아님.
- 독립 검수 상태: work 자체 계산만. fresh Opus middle 독립 재계산 필요(`loop/ESCALATE_SOL`).
- 다음 한 가지: middle(Opus)이 e1/e2 재계산·하네스 코드 검토 후 수용 여부 판정, 이어서 work 후보 = HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택.

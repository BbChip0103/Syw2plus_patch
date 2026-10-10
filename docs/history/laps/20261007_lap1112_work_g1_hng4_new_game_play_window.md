# 2026-10-07 | lap1112 | G1 work — H-NG4 새 게임 진행 장면(스크롤 4구간 + 60초 dwell) PS3 HD

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 C 소스 변경 0, 커밋 0.
- 가설: 새 게임 장면에서 카메라를 움직이고 시간이 흘러도 미러 경로가 같으므로 PS3 HD ≥98.6%·V1·안전 0이 유지된다.
- 예상 PASS(lap1111 사전등록 §5): 진행 창 모든 present HD ≥90%·V1 outside 0·안전 7종 0·dropped 0·scale2x PASS·키 4구간 카메라 이동 ≥1칸·2/2 run.
- 변경 파일(uncommitted): `tools/g1_saved_scene_probe.py`(sha256 `affc8dee…`)·`tests/test_g1_new_game_path.py`(`50c181ea…`). `tools/inmm_stub/*` 이번 lap 변경 없음(후보 DLL = lap1106 H-P35 트리).
- 원본 SHA: `b56986e018b43293…` 직접 재계산 MATCH, 4 lane 모두 `source_unchanged` true·cleanup ok. fixture: 새 게임 경로(save 불필요), 활성 8 player records(local seat 0).

## 변경 (NG4-0, TDD RED→GREEN)

- `--new-game-play`(`--new-game-start` 필수): `ps3_start` 캡처 뒤 `_new_game_play_window` — XTest 키 edge(`_send_key_edge`)로 RIGHT→DOWN→LEFT→UP 각 2.0초 hold(구간 사이 1초), 구간 전후 카메라(`runtime_env._read_camera`)·`_scroll_camera_steps`로 이동 칸 기록, 이어 입력 없이 60초 dwell, `ps3_play` 캡처. 창마다 trace 줄 범위를 남긴다.
- `_summarize_play_presents`: 창별 PS3 mirror present 수·HD 첫/min/p50(=(covered−stale)/480,000)·90% 미만 수·98.6% 미만 수와 목록(≤20)·stale max·마지막 40 중앙값·V1 outside max·안전 7종 max·fallback/success·경과 p95. 요약 `status`는 두 lane의 `new_game_play.status` PASS(키 4구간 모두 ≥1칸 + candidate는 present 요약 PASS)를 gate한다.
- 테스트 +7(옵션 계약 2·키 순서/hold/dwell 행동 2·present 요약 3), RED 7 failed → GREEN. 관련 3파일 266 passed/20.55s, lint·typecheck PASS.

## 실행 (NG4-1, 격리 run 2회)

- 명령: `.venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1112_ng4_{a,b} --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1112_work_hng4/ng4_{a,b} --hd-source scale2x --new-game-path --new-game-start --new-game-play`. exit 0 ×2, status PASS, scale2x validator PASS. 로그 `logs/gates/lap1112-ng4-{a,b}.log`(`b951c4cd…`·`73e9a5e8…`).
- 분석: 새 스크립트 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1112_work_hng4/recalc_ng4.py`(`7141ae34…`) → `recalc_ng4.json`(`f87de1e7…`). 하네스 창 분할을 쓰지 않고 raw trace의 PS3 present 전부를 계산한다. trace SHA a `c9920bd3…`·b `5e3a7761…`.

| run | PS3 present(길이) | HD 첫/min/p50 | 90% 미만 / 98.6% 미만 | stale max | V1 outside·안전 7종·fallback | dropped | 경과 p95(max) |
|---|---|---|---|---|---|---|---|
| a | 1,712 (85.5초) | 100 / 100 / 100 | 0 / 0 | 0 | 0·0·0 | 0 (events 3,796) | 6ms (9) |
| b | 1,713 (85.6초) | 100 / 100 / 100 | 0 / 0 | 0 | 0·0·0 | 0 (events 3,800) | 6ms (10) |

- 하네스 창별(스크롤 4구간 각 40 present·dwell 1,200 present): 전 창 HD 100%·stale 0·V1 0·안전 0, 경과 p95 스크롤 6/7/9/7ms(a)·dwell 6ms. 10초 구간별 min HD 전부 100%.
- 키 4구간 카메라 이동(candidate): a RIGHT 40·DOWN 40·LEFT 40·UP 39칸, b 40·40·40·40칸(맵 가장자리 clamp 없는 대각 이동, 한 바퀴 뒤 시작 좌표 ±1로 복귀). baseline: 54·80·61·42칸(두 run 동일, 맵 가장자리에서 clamp; baseline은 게임 tick이 더 빨라 같은 2초에 더 멀리 움직임). 입력 raw: candidate input trace 512 events(상한) 도달 — 키 전달 확인은 카메라 이동으로 한다.
- 상태 순서 9→7→5→3, success 1·fallback 0. 클릭은 전환마다 1회·키는 구간당 down 1·up 1.
- 캡처: a·b candidate `ps3_play.png` 직접 열람(a: 농장·정자·농민·HUD 정상, 1600×1200, 한 바퀴 이동 뒤 시작 장면 근처). SHA a candidate `e08727f9…`·b `47ae9e35…`.
- 정리: game 사본 자동 삭제 확인(남은 `game` 디렉터리 0), prefix·trace·캡처 보존, 디스크 87GiB.

## 판정

- **H-NG4 `PASS(partial, 기술·격리)`**: 사전등록 기준 전부 충족 2/2. 새 게임 진행 창(스크롤 4구간 + 60초 dwell, 1,712 present) PS3 HD 100%·stale 0·V1 0·안전 0·dropped 0·scale2x PASS·키 4구간 이동 ≥39칸.
- 한계(공개): (1) 장면이 시작 지점 주변의 어두운 안개·정지 지형·유닛 1명이라 stale 0·100%가 부하 장면(save006 PS3 min 99.26%·save000 98.60%)의 최악 수치를 대표하지 않는다 — 유닛·건물·전투가 늘어난 뒤는 미측정. (2) 시간 경과는 60초 dwell(가시 변화 거의 없음)이며 몇 분 플레이는 아니다. (3) baseline·candidate pair 픽셀 비교는 gate 아님(nation 무작위·tick 속도 차). (4) 가장자리 마우스 스크롤·미니맵 클릭·선택·생산 같은 입력 효과는 이번 범위 밖. (5) 입력 trace 512 상한 도달로 raw 키 수신 시각은 일부만 남는다(카메라 이동으로 대체 확인). 사용자 합격·G1 마감 아님.

## 검사

- focused: `test_g1_new_game_path.py`·`test_g1_saved_scene_probe.py`·`test_g1_census.py` 266 passed. 전체 `make check`·SAFETY 결과는 STATUS 검증 줄에 보강한다(lap 기록 freeze 뒤 1회).

## 다음 한 가지

middle(Opus): H-NG4 독립 검수 후 다음 work 결정 — 부하 있는 새 게임 장면(유닛 생산·건설 뒤 HD) vs HUD/GDI vs G1 사용자 승인 요청 준비. 사용자 G1 시험 결과가 오면 그것이 최우선.

# 2026-10-07 | lap1117 | G1 work — H-PM0 게임 중 일시정지 메뉴(Esc→PS23)·저장 창 HD

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 C source 변경 0(후보 DLL = lap1106 H-P35 트리 그대로), 하네스·테스트만 변경, 커밋 0.
- 입력: STATUS 다음 한 가지, lap1116 middle 사전등록 §7(`20261007_lap1116_middle_g1_hng5_review_hpm0_preregistration.md`). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음, `loop/STOP`·`ESCALATE_SOL` 없음.
- 가설: 새 게임 PS3에서 Esc로 연 일시정지 메뉴(PS23)·저장 창도 미러 경로를 타서 모든 창 mirror present>0·index≥1 HD≥90%·V1/안전 0.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293…` MATCH(읽기만). 이전 바퀴 검수: lap1116 ESCALATE 보존본 SHA `ed23770e9a012f22…` 일치 재확인.
- fixture: 새 게임 경로(PS9→PS7→PS5→PS3), save 없음(SAVE_ACTION 클릭 안 함, 파일 쓰기 0), 활성 8 player records(활성 8인 부하 증거 아님). run a = `--new-game-menu`만, run b = `--new-game-act` 뒤 `--new-game-menu`.

## 변경 파일(uncommitted)
- `tools/g1_saved_scene_probe.py`: `--new-game-menu`(`--new-game-start` 필수), `_new_game_menu_window`(Esc → PS23 대기, 실패 시 빈 땅 클릭 뒤 Esc 1회 재시도, 아니면 BLOCKED → 10초 dwell·캡처 `pause` → 저장 버튼 → `save_window` → 돌아가기 → `pause_return` → 계속하기 → `ps3_resume`), 좌표 `PAUSE_SAVE_POINT`·`SAVE_MENU_RETURN_POINT`·`RESUME_POINT`(G5 probe 값), `_summarize_play_presents(program_state=None)`로 모든 state 집계 + `by_state`·`counter_span`(창 안 첫→끝 mirror present의 `menu/partial/frame_copy_*`·`*reject*` 증가), 후보 lane `dropped_count != 0`이면 FAIL, 최상위 status가 두 lane `new_game_menu.status`를 gate. 기존 NG3/NG4/NG5·3/9/35 경로 불변.
- `tests/test_g1_new_game_path.py`: 메뉴 옵션·창 7건(RED 8 → GREEN) → 35 passed. `make lint`·`make typecheck` PASS.

## PM0-1 측정 (격리 run 2회, `--hd-source scale2x --new-game-path --new-game-start [--new-game-act] --new-game-menu`)
- raw: result a `0a0efdc0fe58…`·b `80559ac7841b…`, trace a `db2cad2708aa…`·b `48dc94512110…`(공유 temp `20261007_lap1117_work_hpm0/pm0_{a,b}/`), 로그 `logs/gates/lap1117-pm0-{a,b}.log` `6bcc8abd…`·`afe2fb6f…`(exit 2 = 최상위 FAIL). 하네스 SHA `0dc53744…`·테스트 `5d1fc1cc…`.
- 상태 전이(두 lane·두 run 동일): Esc 1회로 PS3→**23**, 저장 클릭 후 **23 유지**(저장 창은 PS23 안의 하위 화면; `save_state_changed=false`), 돌아가기 → 23, 계속하기 → **3**. 클릭 3회 모두 성공(재시도 0). baseline lane은 trace가 없어 상태 전이만 PASS.
- 후보 lane 창별 mirror present(전부 `program_state` 23; resume 창만 23×27~28 + 3×211), V1·안전 7종·fallback·hresult 0, success_min 1, dropped 0, scale2x validator PASS, 경과 p95 6~7ms, `menu_copy_calls` 증가 0·`partial_copy_calls` 창 present 수−1(매 present)·`frame_copy_calls`·`frame_copy_rejects` 0:

| 창 | run a present / HD first·min·p50 / <90% / <98.6% | run b present / HD first·min·p50 / <90% / <98.6% |
|---|---|---|
| pause | 1,277 / 100·100·100 / 0 / 0 | 1,221 / 100·100·100 / 0 / 0 |
| save_window | 1,716 / 100·**89.180**·99.936 / **1**(seq 3641) / 1 | 1,732 / 100·**89.178**·99.974 / **1**(seq 4865) / 1 |
| pause_return | 1,286 / 99.936·**80.068**·**90.761** / **1**(seq 5358) / **1,260** | 1,303 / 99.974·**80.112**·**90.806** / **1**(seq 6601) / **1,277** |
| resume(PS23 구간 포함) | 238 / 90.761·90.74·100 / 0 / 27 | 239 / 90.806·90.785·100 / 0 / 28 |

- **판정 PM0-1: FAIL(귀속 대상) — 2/2 재현.** 사전등록 PASS(모든 창 HD≥90%)를 만족하지 못한다. 수리하지 않는다(사전등록 FAIL 규칙). 원인 분해:
  1. **저장 창 열림 1 present 일시 stale**: seq 3641(a)·4865(b) `stale_pixels` 51,628/51,636 → 직전·직후 present stale 0, `primitive_stale_pixels_total` 증가가 정확히 그 값 → 일시 stale 한 번(HD 89.18%). pause→save_window 전환 순간 한 번이라 전환 프레임 단발 단위 stale.
  2. **저장 창 → 메뉴 복귀 뒤 영구 coverage 감소(주 결함)**: pause_return 첫 present(seq 5358/6601) stale 95,366/…로 HD 80.07/80.11%, 그다음부터 **`stale_pixels`=0 이지만 `covered_pixels`가 479,692→435,652(−44,040; run b 435,868 −44,005)로 떨어져 유지** → HD 90.76/90.81%(480,000 대비)가 PS23 구간 끝(계속하기 직전)까지 1,260/1,277 present 지속. PS3 복귀 뒤 첫 PS3 present부터 covered 480,000 회복, PS3 211 present 전부 ≥98.6%(`resume` 창 PS3 hd_min ≥ 98.6%·p50 100). 즉 메뉴 복귀 후 **약 44k 논리 px가 HD 미러 coverage에서 빠져 2× 확대 폴백 화질로 표시**되는 결함이다. 크기 ≈ 저장 창 패널이 메뉴 패널보다 좌우로 넓은 가장자리 두 띠(캡처 기준 논리 약 x241..314·484..555 × y101..406 ≈ 43.9k)와 일치(추정, 좌표는 trace에 없음 — middle이 확정).
  3. pause·(첫 present 제외) save_window·resume의 PS3는 100%/≥99.9%·V1/안전 0.
- 캡처 열람(1600×1200, 정상): `pause.png` 메뉴 8버튼(계속하기·게임목적·환경설정·저장하기·불러오기·다시하기·초기메뉴·종료하기) 비율·위치 원본 대응·글자 정상, `save_window.png` 슬롯 1~7·저장하기/돌아가기·원본 비율, 맵 배경 정상, `pause_return.png` 메뉴 복귀·깨짐/흑색 띠 없음(가장자리 띠는 화질만 2×, 겉모습 동일). 클릭 좌표가 후보 lane에서 상태를 3번 바꿨으므로 메뉴 버튼 클릭 대응 PASS.
- 공개 한계: PS23 present는 일시정지 중에도 약 125/s로 매 루프 계수된다(창 present 수가 PS3의 수 배). 저장 실행(파일 쓰기)·불러오기 창은 측정 안 함. 부하 대표성 낮음. pair 픽셀 비교는 gate 아님. "화면 대상 비-mirror present" 별도 raw는 이 trace에 창별 계수가 없어 `partial_copy_calls` 증가로 대체 공개.

## 다음 행동 (middle 검수 요청)
- middle(Opus)이 seq 5358/5359(run a)·6601/6602(run b)에서 coverage 감소 직전·직후 `source_rect`·`bbox_calls`·`primitive` 계수·`partial_copy` 변화를 독립 재계산하고, 44k px의 위치·writer(저장 창 닫기 시 배경 복원 경로: `menu`/`partial` copy가 mirror coverage 갱신을 건너뛰는지)를 한 가설로 귀속해 수리 work를 사전등록한다. 같은 하네스 `--new-game-menu`가 재측정 도구다.
- 하네스 경미 사항(수리 불요): 베이스라인 lane의 창 line_start/line_end가 trace 없음으로 같은 값(요약 대상 아님).

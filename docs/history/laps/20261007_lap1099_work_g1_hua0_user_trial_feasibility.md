# 2026-10-07 | lap1099 | G1 work — H-UA0 사용자 시험판 가능성·최소 구성 (U-0·U-1·U-2)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 커밋 0.
- 가설: G1 후보는 `SYW2_G1_PRESENT_TRACE` 없이도 mirror가 동작하므로 `_inmm.dll` 교체 + 환경변수 3개(`SYW2_G1_NATIVE_2X_BLIT=1`·`SYW2_G1_MIRROR2X=1`·`SYW2_G1_HD_SOURCE=scale2x`)만으로 사용자 시험판이 된다.
- 판정 기준(lap1098 §4): U-0 크래시 0·창 1600×1200·하네스 `loaded.png` 대비 ≥99%. U-1 스테이징. U-2 선택·미니맵 입력 대응·원복 SHA MATCH. 전부 PASS면 `FEASIBLE`.
- 입력: lap1098 middle 기록 §4, INBOX(새 지시 없음, 구현 우선·묻지 말고 결정 유지), APPROVALS 변경 없음. ESCALATE_SOL 없었음.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — u0·u2 candidate/baseline의 `source_exe_sha256`·`private_exe_sha256` 4/4 일치, `source_unchanged` true, 하네스 `execution_source.unchanged` true. 사용자 폴더 원래 `_inmm.dll` SHA256 `03192987e9c877cf344874412d2c0e1a80b5d5f8b91f325771e9615feadbf160`(167,936 B).
- fixture: 비합성 save006(하네스 기본 `--scene-actions all`). 활성 8인 증명 아님. EXE는 원본(G2/G5/G6G7 EXE 조합 미측정).

## 1. U-0 정적 + 실행

**정적(직접 코드 확인):** `g1_direct_draw_trace_install()`(`direct_draw_trace.c`)은 `!env_enabled() && !g1_mirror2x_enabled() && !g1_census_enabled() && !g1_state_snapshot_enabled()`일 때만 조기 반환한다. 즉 `SYW2_G1_PRESENT_TRACE`(`g_trace_opt_in`)의 소비처는 이 조건과 `env_enabled()` 반환뿐이며 mirror 설치·native 2× present 경로는 trace env에 묶이지 않는다. **정정(카드 가정 반증):** mirror가 켜져 있으면 trace 로그 `C:\inmm_g1_present_trace.jsonl`(+input trace)은 trace env와 무관하게 항상 생성·기록된다(`CreateFileA` CREATE_ALWAYS, 이벤트 마다 Flush). 그래서 카드 U-0의 "trace 파일 미생성"은 성립하지 않는 기준이었고, 그 대신 안내문에 "C:\ 루트 기록 파일이 생긴다"를 공개했다. 하네스의 present 장벽(`_wait_for_mirror_present`)도 이 로그를 읽으므로 env 없이 그대로 동작한다.

**변경(TDD, 하네스·테스트만, 스텁 C 무변경):**
- `tools/g1_saved_scene_probe.py`: 후보 lane 전용 `--candidate-no-present-trace`(후보 env에서 `SYW2_G1_PRESENT_TRACE`·`SYW2_G1_TRACE_RUN_ID`만 제거; baseline 불변) → U-0 격리 실행.
- 같은 파일: 후보 lane 전용 `--candidate-native-ddraw`(`WINEDLLOVERRIDES=ddraw=n,b`: 사용자 게임 폴더의 `ddraw.dll`을 로드) → U-2.
- `tests/test_g1_mirror2x.py`: `test_ua0_candidate_no_present_trace_flag_drops_trace_env_candidate_only`·`test_ua0_candidate_native_ddraw_flag_is_candidate_only`(RED 확인 후 GREEN). 두 파일 합계 256→258 passed(`test_g1_mirror2x`+`test_g1_saved_scene_probe`).

**실행 u0(trace env 없음, `--hd-source scale2x --candidate-no-present-trace`, save006 full pair):** exit 0, pair `status` PASS, 후보 창 content 1600×1200(`window.size`), 크래시 0(전 경로 완료), `input_effect_comparison` PASS 7/7(selection_target·empty_click·drag_exact·drag_capture_binding·minimap_gate_restore·production_effect·production_completion), `minimap_diagnostic_parity` PASS, V2·V2s·V2q·Scale2x gate PASS, `loaded_capture_comparison` PASS, `scene_state_equal` true, `mirror2x_present` 기록 1,278, cleanup `ok`·`game_removed`·prefix 프로세스 0.
- **카드 비교:** u0 `menu.png`·`loaded.png`는 lap1097 v3 후보(`20261007_lap1097_work_hd2ks1/v3/candidate`)와 **0 px 차이 = 100.0000% 일치(≥99%)**. selection·drag·minimap·production은 v3가 scroll 스크립트 뒤 장면이라 달라 비교 대상이 아니다(92~97%, 공개).
- `mirror_validator`는 BLOCKED(nearest 오라클 0.776<0.999)이지만 v3 후보도 같은 값이다(Scale2x 경로에서 nearest 오라클 기준이 맞지 않는 기존 동작, 판정 gate는 Scale2x/V2s). 이번 변경과 무관.
- 파일: `…/20261007_lap1099_work_hua0/u0/pair-result.json` SHA256 `8abb79ca6eb3f861…`, 로그 `logs/gates/lap1099_u0.log` `ef5e0fe960532c62…`, `loadavg_u0.txt`.
- **U-0 PASS.**

## 2. U-1 스테이징 (`…/20261007_lap1099_work_hua0/user_test_staging/`)

| 파일 | SHA256 |
|---|---|
| `_inmm.dll`(u0 하네스 bridge 산출물 = 현재 트리 빌드, 소스 `g1_mirror2x.c` `2dc25e1b64606554`·`.h` `d6b10bbd4a813758`·`direct_draw_trace.c` `f1dae646007cf0d7` 일치) | `aef92b530737af479580d310324c6a5aa7480859e36f666ca068e6f657a097c3` |
| `g1_trial_direct.bat`(ASCII·CRLF, env 3개 + 원본 EXE `start`) | `803efc51f7fff05e0768b8c9640bbadc903f4cabd2f44362580ddd6f5d75522c` |
| `g1_trial_via_dxwnd.bat`(ASCII·CRLF, env 3개 + `dxwnd\dxwnd.exe` `start`) | `ef75cad5ed81307e11a96bc20cd89aeb928cd125112eae56db84439700b38ad1` |
| `G1_1600x1200_시험판_읽어주세요_20261007.txt`(설치·원복·표시 정책·한계·확인 절차) | `2898aac534a8f2702baf4f2f74075a4cb33601dab9e8f27963df6adc2afd671b` |

- 스텁은 stock `_inmm.dll`을 대체하는 4함수(`_ciSendCommandA`·`_imeBeginPeriod/EndPeriod/GetTime`) winmm 직접 포워더(`inmm_stub.c` 주석)다. 따라서 stock이 하던 mp3 BGM 처리가 달라질 수 있다 → 미검증으로 안내문에 공개.
- 표시 정책(DESIGN §G1): 스텁은 창/모드를 만들지 않고 게임의 800×600 모드 설정을 후킹해 1600×1200으로 올린다(Wine에서는 가상 데스크톱 1600×1200). 1080p 모니터에서의 풀스크린/DxWnd 창 스케일은 **실제 Windows에서 미검증**이며 두 .bat 선택지와 한계를 안내문에 기록했다. `260921_temp` 배치는 하지 않았다(root/사용자 몫).

## 3. U-2 시험판 기동 검증

- 설치·원복 절차(안내문 그대로)를 임시 폴더에서 실제 수행: stock `_inmm.dll` SHA `03192987…` → `_inmm.dll.원본백업` 이름 변경 → 후보 복사(`aef92b53…`) → 후보 삭제·백업 복귀 → SHA **`03192987…` MATCH**. 임시 폴더는 삭제했고 사용자 폴더는 읽기만 했다.
- 같은 `_inmm.dll`(SHA `aef92b53…`)로 하네스 후보 lane(env = .bat과 동일한 3개)이 u0에서 PASS했으므로 스테이징 파일과 격리 실행 DLL이 동일하다. **한계 공개:** Wine 하네스는 `.bat`을 실행하지 않고 동등 env를 프로세스에 주입한다(사용자 지시서 U-2 허용 사항).
- **native ddraw 변형(u2, `--candidate-native-ddraw`, 같은 옵션):** 사용자 게임 폴더의 `ddraw.dll`(2,376,192 B)을 로드한 후보 lane. 후보의 ddraw 모듈 크기가 baseline/u0(2,363,392)와 달라진 2,994,176(`trace_raw.jsonl` install 이벤트) → 다른 `ddraw.dll`이 실제로 로드됨을 확인했다. exit 0, pair PASS, `input_effect` 7/7·minimap parity·V2/V2s/V2q/Scale2x/loaded gate 전부 PASS, `mirror2x_present` 1,285, cleanup OK, `source_unchanged` true. u0 대비 `loaded.png` 99,920 px 차이는 같은 캡처에서 토네이도 효과 애니메이션 프레임 위치가 다른 것으로 눈으로 확인(crop `…/viz/u0_u2_loaded_crop.png`), 입력·gate 결과는 같다. 파일: pair-result SHA `1ff4de58611e64a7…`, 로그 `logs/gates/lap1099_u2.log` `21a55d63a069b993…`.
- **U-2 PASS(격리, 기술).** 실제 Windows·실제 모니터·DxWnd 창모드·사용자 PC 래퍼 동작은 미검증이다(아래 §5).

## 4. 판정

- **`FEASIBLE`**: 최소 구성 = (현재 트리 `_inmm.dll`) + (환경변수 3개, trace 없음) + 원본 EXE. trace 의존 없음(수정 불필요). 시험판은 uncommitted·사용자 승인 전이며 제품 G1 마감이 아니다.
- 사전등록 이탈: 없음(하네스 flag 2개는 카드 U-0/U-2 수단). 스텁 C 무변경.

## 5. 미검증·위험(공개)

- 실제 Windows 풀스크린 1600×1200 모드 지원, 1080p 모니터에서의 표시, DxWnd 창모드와 환경변수 전달(.bat이 DxWnd를 띄우는 방식은 가정이며 미실행), 사용자 PC 성능(이 회차는 성능 창을 재지 않았다; 참고 lap1097 Wine p95 7~8 ms, Windows 미측정).
- BGM 처리 차이 가능(stub vs stock `_inmm.dll`), C:\ 루트 로그 파일 생성, G2/G5/G6G7 EXE와의 조합 미측정, 명시 잔여(로고·GDI 글자·효과·일시 stale) 유지.
- 하네스 flag 2개는 진단 전용이며 제품 코드가 아니다.

## 6. 검사

- `make lint`·`make typecheck` PASS. focused `tests/test_g1_mirror2x.py`+`tests/test_g1_saved_scene_probe.py` 258 passed.
- 전체 `make check`·`checks/safety.sh check`·`checks/context_limits.py`는 이 기록 freeze 뒤 1회 실행하고 결과는 STATUS에만 쓴다.
- 변경 파일(uncommitted): `tools/g1_saved_scene_probe.py` `b87ec4df28dcde66`, `tests/test_g1_mirror2x.py` `c5789dda8a56318c`(이번 lap), 그 외 lap1095~1097 변경 `g1_mirror2x.c/.h`·`direct_draw_trace.c`·`test_g1_rect_fill.py` 해시 불변(위 소스 해시).
- 디스크: u0/u2 `game` 사본 삭제, prefix·manifest·output 보존, 여유 약 103 GiB.

## 다음 한 가지

middle(Opus): §3·§5를 새 스크립트로 독립 재계산(u0/u2 pair-result·스테이징 SHA·원복 절차)하고 수용하면 APPROVALS에 G1 사용자 시험 요청을 올리고 root 전달용 `loop/ESCALATE_SOL`을 작성한다.

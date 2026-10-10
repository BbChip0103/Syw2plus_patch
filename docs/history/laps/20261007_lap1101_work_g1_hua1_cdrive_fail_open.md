# 2026-10-07 | lap1101 | G1 work — H-UA1: `C:\` 쓰기 불가 환경에서 G1 시험판 fail-open

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 커밋 0.
- 가설: 사용자 모드(G1 env 3개, `SYW2_G1_PRESENT_TRACE` 없음)에서 present trace 로그를 열지 못해도 G1 설치를 계속하면 시험판은 `C:\` 쓰기 권한 없이 1600×1200 mirror로 동작한다. trace opt-in(하네스) fail-closed 계약은 불변.
- 입력: lap1100 §4 사전등록 카드, INBOX(새 지시 없음; 구현 우선·묻지 말고 결정 상시), APPROVALS 새 반려 없음. ESCALATE_SOL 없었음.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — a/b/pair 모든 run의 `source_exe_sha256` before/after·private 사본 일치, `source_unchanged` true. 사용자 폴더·원본·참고 저장소 쓰기 0.
- fixture: UA1-2 = 원본 EXE PS9 타이틀 메뉴(직접 기동, 로드 없음); UA1-3 = 비합성 save006 full pair. 활성 8인 증명 아님.

## 1. UA1-0 정적 전수 (사용자 env 3개 기준, 직접 코드 확인)

| 파일(`C:\`) | 열리는 조건 | 실패 시 | 크기 상한 |
|---|---|---|---|
| `inmm_g1_present_trace.jsonl` | mirror/census/snapshot/trace env 중 하나라도 켜짐 → **G1 설치 시작 시 1회** | **(수정 전) `g1_direct_draw_trace_install` 즉시 `return 0` → IAT·mirror·native 2× 미설치 = 800×600 조용히** · (수정 후) trace opt-in 없음이면 `%TEMP%`로 재시도, 그래도 실패하면 로그 없이 계속. opt-in 있으면 기존대로 fail-closed | 이벤트 8,192 상한(pair 실측 4.4MB, 직접 기동 b 12MB) |
| `inmm_g1_input_trace.jsonl` | mirror 켜짐 | `open_input_log` 결과 무시, 기록 no-op(설치 영향 0) | 이벤트 상한 `INPUT_TRACE_MAX_EVENTS`(pair 0.1MB) |
| `inmm_g1_stale_mask.bin`·`inmm_g1_layer_drift.jsonl`·`inmm_g1_screen_watch.jsonl`·`inmm_g1_census*` | 각각 opt-in env(`SYW2_G1_STALE_MASK`·`_LAYER_DRIFT`·`_SCREEN_WATCH`·`_CENSUS`) | 열기 실패 시 return(설치 영향 0) | 사용자 모드에서 열리지 않음 |
| `inmm_g1_perf_window.active`·scroll arm/ready | 존재 검사(`GetFileAttributesA`)·scroll trace opt-in | 없음 = 무시 | — |
| `inmm_control_events.jsonl` | 항상(DLL attach) | `INVALID_HANDLE` 가드로 무시 | 이벤트 수 적음(0.6KB) |
| `inmm_stub.log`·`inmm_state_log.jsonl`·`inmm_mci_log.jsonl`·`inmm_watch_log.jsonl` | 항상(첫 `_imeGetTime`) | 가드로 무시 | 소(0.5~350KB, watch는 변화 시) |
| `inmm_asset_log.jsonl` | 항상(`CreateFileA/W` IAT hook, 호출마다 Flush) | 가드(`g_asset_log` INVALID면 return), 후킹 자체는 계속 | 상한 없음(pair 44KB) |
| `inmm_sfx_log.jsonl` | 항상(SFX trampoline) | 가드로 무시, hook 설치는 계속 | 상한 없음(pair 0.49MB) |
| `inmm_unit_ticks.jsonl` | 항상(PS3, 50틱마다 전 유닛 덤프, CREATE_ALWAYS) | 열기 실패 시 return | **상한 없음. 세이브006 장면 677덤프 × 약 78KB = 53MB**(유닛 수에 비례) — 안내문에 공개 |
| `inmm_control_request/result.json`·`inmm_*_probe.json` 등 | worker가 30ms마다 request 존재 검사(`GetFileAttributesA`), 쓰기는 요청 시에만 | 없음 = 무시 | — |
| `supply_probe_*` (`runtime_bridge.c`) | `SYW2_SUPPLY_PROBE` env 없으면 호출 지점에서 env만 읽고 반환 | — | 비활성 |

결론: **설치를 막는 `C:\` 경로는 present trace 로그 열기 하나뿐**(나머지는 전부 가드·무시). 카드 UA1-0의 확인 항목 충족.

## 2. UA1-1 최소 수정 (TDD)

- RED: `tests/test_g1_presentation_trace.py`에 source-contract 2개 추가(`test_user_mode_trace_log_failure_falls_back_to_temp_and_keeps_install`, `test_trace_opt_in_log_open_failure_stays_fail_closed`) → 수정 전 2 failed 확인.
- GREEN: `tools/inmm_stub/direct_draw_trace.c`
  - 신규 `open_log_fallback()`: `g_trace_log`가 이미 열렸거나 `env_enabled()`(trace opt-in)이면 no-op, 아니면 `GetTempPathA`+`inmm_g1_present_trace.jsonl`로 `CREATE_ALWAYS` 시도(경로 길이 초과 시 포기).
  - `g1_direct_draw_trace_install`: `open_log(); open_log_fallback(); if (log invalid && env_enabled()) { g_trace_failed = 1; return 0; }` — opt-in 일 때만 실패로 간주. 로그 없이 계속하면 `trace_event_raw`가 invalid handle에서 FALSE → `g_trace_failed`만 올라가고 설치·mirror 동작 영향 없음(g_trace_failed 소비처는 summary status뿐, 직접 확인).
- 같은 파일의 기존 lap1095~1097 변경(mirror 상세 버퍼 등)은 그대로. `tests/test_g1_presentation_trace.py` 18 passed.

## 3. UA1-2 런타임 RED/GREEN (사적 prefix, `drive_c` 디렉터리만 `chmod 555`, 끝나면 원래 mode 복구; 스크립트 `…/20261007_lap1101_work_hua1/ua1_direct.py` `b0e1a732…`)

| lane | DLL | drive_c 루트 | 결과 |
|---|---|---|---|
| a (대조) | 기존 `aef92b53…`(lap1099 스테이징) | 쓰기 불가(생성 시도 PermissionError 확인) | **창 800×600**, 1600×1200 창 없음, PS9 유지·60초 생존, `%TEMP%` trace 없음, 새 파일 0 → **결함 재현(RED)** |
| b (후보) | 새 `4d6e7bfc…`(bridge 빌드, 타임스탬프 6바이트 외 스테이징 DLL과 동일) | 쓰기 불가 | **창 1600×1200**, PS9 60초 생존(`ps_after` 9), `%TEMP%\inmm_g1_present_trace.jsonl`에 install `active` 이벤트·`mirror2x_present` **4,196**·총 4,760 이벤트, **drive_c 루트 새 파일 0**, 원본 SHA 불변 → **GREEN** |

- 메뉴 캡처 b vs lap1099 u0 `candidate/menu.png`: 1600×1200 **0 px 차이(100.0000% ≥ 99%)**, 마스크 없음. 파일: a/b `result.json` SHA `83260a2f…`/`72ad924e…`, `menu.png` a `34d43b31…` b `c57f8614…`, 로그 `logs/gates/lap1101_ua1_{a,b}.log`.
- 한계: Wine이며 `%TEMP%`는 `C:\users\<name>\Temp`. 실제 Windows ACL(비관리자 `C:\` 거부)은 직접 재현하지 못했다(UNKNOWN 유지) — 권한 부여로 인한 PermissionError 의미(CreateFileA 실패)가 동일하다는 점에서 같은 코드 경로를 지난다.

## 4. UA1-3 회귀 (새 소스 트리 bridge, `--hd-source scale2x --candidate-no-present-trace`, save006 full pair)

- exit 0, pair `status` **PASS**, `scene_state_equal` true, `input_effect_comparison` PASS **7/7**(selection_target·empty_click·drag_exact·drag_capture_binding·minimap_gate_restore·production_effect·production_completion), `minimap_diagnostic_parity` PASS, V2·V2s·V2q·Scale2x·loaded gate PASS, 후보 창 1600×1200 scale 2, `source_unchanged` true, cleanup `ok`·`game_removed`·prefix 프로세스 0, `execution_source.unchanged` true.
- pair-result `ua1_3/pair-result.json` SHA256 `fbc9f51b…`, 로그 `logs/gates/lap1101_ua1_3.log` `b0b9388e…`, loadavg `loadavg_ua1_3.txt`. (이 변경은 C:\ 가 쓰기 가능한 경로에서 동작을 바꾸지 않으므로 이전 pair와 같은 gate 구성이다.)
- 하네스가 만든 bridge `ua1_3/bridge/_inmm.dll` = `34a9c777833d5a44…`(UA1-2 b의 DLL과 바이트 6개(COFF/export 타임스탬프·체크섬)만 다름) → 이 DLL을 스테이징한다.

## 5. UA1-4 재스테이징 (`…/20261007_lap1101_work_hua1/user_test_staging/`, `260921_temp` 배치 안 함)

| 파일 | SHA256 |
|---|---|
| `_inmm.dll` | `34a9c777833d5a44c465178ff9997d3c97df16763161a8431f87cee23c703409` |
| `g1_trial_direct.bat`(변경 없음) | `803efc51f7fff05e0768b8c9640bbadc903f4cabd2f44362580ddd6f5d75522c` |
| `g1_trial_via_dxwnd.bat`(변경 없음) | `ef75cad5ed81307e11a96bc20cd89aeb928cd125112eae56db84439700b38ad1` |
| `G1_1600x1200_시험판_읽어주세요_20261007_lap1101.txt` | `dc838e3f352809c52d9a4a607b1eaa2eff2cb7c413e5c54181435f95186db0b4` |

안내문 개정 사항: 관리자 권한 불필요·`%TEMP%`/`C:\` 기록 위치, UA1-0 상시 로그 목록과 `inmm_unit_ticks.jsonl` 크기 경고, supply bridge 비활성(`SYW2_SUPPLY_PROBE` 미설정), BGM 없음 가능(`_inmm.ini`·`_inmmserv.exe` 미대체), HQ 2002 EXE 전용(ESL 2606 등은 G1 꺼짐), stock `_inmm.dll` 백업/원복(SHA `03192987…`) 유지.

## 6. 판정

- **H-UA1 `PASS(partial, 기술·격리)`**: UA1-0 전수·UA1-1 TDD·UA1-2 RED(결함 재현)/GREEN·UA1-3 회귀·UA1-4 스테이징 전부 수행. 사전등록 이탈 없음.
- 열린 위험(유지·공개): 실제 Windows ACL 환경 미재현, 실제 Windows 1600×1200 모드/1080p·DxWnd env 전달 미검증, BGM, `FlushFileBuffers` 매 이벤트 비용, `inmm_unit_ticks.jsonl` 상시 기록(상한 없음, 유닛 수 비례; 사용자 모드 비활성화는 별도 가설 후보 H-UA2, 이번엔 손대지 않음 — 다른 probe가 의존할 수 있어 영향 조사 필요).
- 새 안전 위험·근거 충돌 없음. 단 **역할 경계**: work가 자기 결과를 최종 승인하지 않는다 → `loop/ESCALATE_SOL`(middle 독립 재조립·SHA 대조 + APPROVALS G1 사용자 시험 요청 + root 전달 판단).

## 7. 검사

- `make lint`·`make typecheck` PASS. focused `tests/test_g1_presentation_trace.py` 18 passed.
- 전체 `make check`·`checks/safety.sh check`·`checks/context_limits.py`는 이 기록·ESCALATE_SOL freeze 뒤 1회 실행하고 결과는 STATUS에만 쓴다.
- 변경 파일(uncommitted): `tools/inmm_stub/direct_draw_trace.c` `2fbc28e1aeb003cf…`, `tests/test_g1_presentation_trace.py` `2bd76e08bc17d77983…`(이번 lap), 그 외 lap1095~1099 변경 불변. 디스크: a/b/ua1_3 `game` 사본 삭제(prefix·manifest·output 보존), 여유 약 100GB.

## 다음 한 가지

middle(Opus): §3~§5를 새 스크립트로 독립 재계산(a/b result.json·pair-result·스테이징 SHA·DLL 재조립)하고 수용하면 APPROVALS에 G1 사용자 시험 요청을 올리고 root 전달용 `loop/ESCALATE_SOL`을 작성한다. 사용자 모드 `inmm_unit_ticks` 비활성화(H-UA2)는 middle이 필요 여부를 판정한다.

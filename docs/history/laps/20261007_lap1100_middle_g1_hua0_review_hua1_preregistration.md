# 2026-10-07 | lap1100 | G1 middle — H-UA0(사용자 시험판 가능성) 독립 검수 + H-UA1(C:\ 쓰기 불가 환경 fail-open) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1099 work), lap1099 기록, lap1098 §4 사전등록 카드. INBOX 새 지시 없음(구현 우선·묻지 말고 결정·G1 최우선 유지), APPROVALS 새 반려 없음.
- ESCALATE_SOL 처리: 원문 byte 일치 보존 `docs/history/laps/20261007_lap1100_preserved_lap1099_escalate_sol.txt`(SHA256 `8206dc7cd40654fc27d7b2aef92a3815a67e3fb713802850fe3a387f5cd8ff19`, cmp 일치) 뒤 삭제. 이번 회차는 root 전달 요청이 없어 새 ESCALATE_SOL을 만들지 않는다(§3 판정).
- 원본 SHA: 사용자 폴더 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…a8ac` read-only MATCH, 사용자 폴더 stock `_inmm.dll` `03192987e9c877cf…f160`(167,936 B) MATCH, 사용자 폴더 `ddraw.dll` `ad5d8d449ce305ca…f8dd`(2,376,192 B, 출처 미기록·이번에 처음 기록).
- fixture: lap1099 u0·u2 save006 full pair(비합성). 활성 8인 증명 아님.

## 1. 독립 재계산 (새 스크립트, work 스크립트 재사용 없음)

스크립트 공유 temp `20261007_lap1100_middle_review/recalc_lap1100.py`(SHA256 `7128c8889775a453…9c56`), 결과 `recalc_lap1100.json`(`258aea9f1b73bb63…c425`). 검사 28개, **불일치 0.**

| 항목 | 결과 |
|---|---|
| 주장 SHA 6개(u0/u2 pair-result·스테이징 4파일) | 6/6 일치 |
| 스테이징 `_inmm.dll` = u0 bridge 산출물 | byte 동일(`aef92b53…97c3`) |
| u2 bridge DLL(`a3ba3038…030b`) vs u0 | 다른 바이트 6개 = COFF TimeDateStamp(136..137)·CheckSum(216..217)·export dir TimeDateStamp(330756..330757)뿐 → 기능 동일 재빌드 |
| bridge 소스 = 현재 트리 | `tools/inmm_stub/*` 전부 일치, `patches/population/runtime_bridge.c` 일치, `inmm_stub.c`는 bridge 삽입 2줄(`supply_probe_poll` extern·호출)만 차이, Makefile은 SRCS에 `runtime_bridge.c` 추가만 |
| **독립 재조립**(현재 트리 → 새 디렉터리 → mingw `make`) | 434,494 B, 타임스탬프 3필드 마스크 뒤 스테이징 DLL과 **동일**(재빌드 SHA `c9dbc69f…dc1a`, 타임스탬프 때문에 원 SHA는 다름) |
| u0·u2 pair | 둘 다 `status` PASS·`scene_state_equal` true·input_effect 7/7·V2/V2s/V2q/Scale2x/loaded/minimap parity PASS·EXE SHA 4/4·source_unchanged 3/3·window 1600×1200 scale 2·cleanup ok·prefix 프로세스 0 |
| trace env 부재(런타임 근거) | env는 결과에 저장되지 않는다. 대신 `SYW2_G1_TRACE_RUN_ID`는 하네스가 `PRESENT_TRACE`와 함께만 넣는데(`tools/g1_saved_scene_probe.py` 3424·3474–3477), 후보 trace `run_id`가 u0·u2 모두 `"unknown"`(baseline `"g1-saved-baseline"`)이므로 둘 다 빠졌다. mirror2x_present 1,278/1,285 |
| u2 native ddraw | 후보 ddraw 모듈 크기 2,994,176 vs u0·u2 baseline 2,363,392 → 게임 폴더 `ddraw.dll` 실제 로드 |
| u0 vs lap1097 v3 후보 | `menu.png`·`loaded.png` 1600×1200 **0 px 차이** |
| u0 vs u2 `loaded.png` | 99,920 px(work 주장 일치, 토네이도 프레임 차이 — crop은 work 육안 근거 유지) |

정적 확인: `g1_direct_draw_trace_install()`(`direct_draw_trace.c:1929`)은 mirror/census/snapshot/trace env 중 하나라도 켜지면 진행한다. 그래서 trace env가 필요 없다는 work 정정(카드의 "trace 파일 미생성" 기준 불성립)은 맞다.

**H-UA0 `FEASIBLE`(기술·격리) 수용.** 정정 2건:
- **정정 1:** work 기록 §3의 "같은 `_inmm.dll`(SHA `aef92b53…`)"은 u0에만 맞는다. u2는 타임스탬프만 다른 재빌드 `a3ba3038…`를 썼다. 판정은 바뀌지 않는다.
- **정정 2:** 스테이징 DLL은 진단용 "supply bridge" 빌드다(`supply_bridge_build.json` `diagnostic_only: true`). 즉 `runtime_bridge.c`가 함께 링크돼 있다. 이 코드는 `SYW2_SUPPLY_PROBE=1`이 없으면 호출 지점 `0x42334C`의 timer 호출마다 env를 읽고 바로 반환한다. `.bat`은 이 변수를 넣지 않으므로 비활성이다. 안내문에는 이 사실이 없다.

## 2. 새 근거 — 사용자 PC에서 G1이 조용히 꺼질 수 있음(구현 결함)

- `direct_draw_trace.c:1933–1934`: `open_log()`가 `C:\inmm_g1_present_trace.jsonl`을 `CREATE_ALWAYS`로 만들지 못하면 `g_trace_failed = 1; return 0`으로 **G1 설치 전체를 중단**한다(IAT hook·mirror·native 2× 모두 미설치). 그러면 게임은 800×600 원래 방식으로 뜨고, 남는 흔적은 `inmm_stub.c:536`의 control log 한 줄뿐이다. 그 control log도 `C:\`에 쓴다.
- Windows 기본 ACL에서는 관리자 권한이 아닌 프로세스가 `C:\` 루트에 새 파일을 만들 수 없는 것으로 알려져 있다. 이번 회차에서는 확인하지 않았다. 사용자의 게임 권한 설정(관리자 실행 여부)도 UNKNOWN이다. Wine 격리 환경은 `C:\`(prefix drive_c)가 쓰기 가능해서 lap1099 u0·u2는 이 경로를 한 번도 지나지 않았다.
- 같은 stub에는 env와 무관하게 항상 켜지는 `C:\` 파일 경로도 있다: control events·asset log(`asset_hook_install`, CreateFileA IAT)·sfx log·`inmm_stub.log`·state/mci/watch/unit_ticks. 이것들의 실패 시 동작과 크기 상한은 이번에 전수 확인하지 않았다.
- **영향:** 지금 시험판을 보내면 "관리자 아님 → 아무 변화 없음(800×600)"이 첫 사용자 시험 결과가 될 수 있다. 사용자 시험 왕복은 비싸므로, 시험 요청과 root 전달은 1 work 수리 뒤로 미룬다. 이것은 추적 가능한 구현 결함이고 work 범위다. 근거 충돌이나 마일스톤 경계가 아니다.

## 3. 판정

- **H-UA0 `FEASIBLE`(기술·격리) 수용**, 정정 1·2.
- **G1 사용자 시험 요청(APPROVALS)·root 전달(ESCALATE_SOL)은 H-UA1 뒤로 보류.** lap1099 스테이징 파일은 증거로 보존하며 사용자 전달 대상이 아니다.
- 열린 위험(유지·공개): 실제 Windows 1600×1200 모드/1080p 표시, DxWnd env 전달(.bat 미실행), stub이 stock `_inmm.dll` mp3 BGM(`_inmm.ini`·`_inmmserv.exe`)을 대신하지 않음 → BGM 없음 가능, trace 이벤트마다 `FlushFileBuffers`(상한 8,192)의 실제 디스크 비용, G2/G5/G6G7 EXE 조합 미측정, 사용자 폴더 `[ESL]Syw2plus 2606.exe`는 stub 계약(HQ 2002 SHA 고정) 밖이라 G1 fail-closed.

## 4. 다음 work 사전등록(Sonnet) — H-UA1: `C:\` 쓰기 불가 환경에서 G1 시험판 fail-open

**가설:** 사용자 모드(G1 env 3개, `SYW2_G1_PRESENT_TRACE` 없음)에서 present trace 로그를 열지 못해도 G1 설치를 계속하면, 시험판은 `C:\` 쓰기 권한 없이 1600×1200 mirror로 동작한다. 하네스 모드(trace opt-in)의 fail-closed 계약은 바꾸지 않는다.

- **UA1-0 정적 전수(짧게):** 사용자 env(3개)에서 실제로 열리는 `C:\` 경로를 표로 정리한다. 열: 파일, 열리는 조건, 실패 시 동작(설치 중단/조용히 무시), 크기 상한. 대상은 stub 전 모듈과 `runtime_bridge.c`. 설치를 막는 것은 present trace뿐인지 확인한다.
- **UA1-1 최소 수정(TDD, `direct_draw_trace.c`):** trace opt-in(`env_enabled()`)이 꺼져 있고 present 로그 열기에 실패하면 `%TEMP%\inmm_g1_present_trace.jsonl`(GetTempPathA)을 시도한다. 그것도 실패하면 로그 없이 설치를 계속한다(`trace_event_raw`는 이미 invalid handle에서 no-op). trace opt-in이 켜진 경우의 fail-closed와 C:\ 경로는 그대로 둔다. UA1-0에서 다른 설치 차단 경로가 나오면 같은 원칙으로 최소 범위만 고친다. 기존 source-contract 테스트 방식으로 RED→GREEN.
- **UA1-2 런타임 RED/GREEN(격리, 직접 기동 허용):** 사적 prefix에서 drive_c 루트를 쓰기 불가로 만든다. 예: prefix 부팅 뒤 그 사본의 `drive_c` 디렉터리만 `chmod a-w`, 끝나면 복구. 원본·공유 경로에는 손대지 않는다. 그 상태에서 env 3개로 같은 원본 EXE를 띄운다.
  - (a) 대조 = 기존 DLL `aef92b53…`. 예상은 800×600(결함 재현).
  - (b) 후보 = 새 DLL. PASS 조건: 60초 생존, 창 내용 1600×1200, 메뉴 캡처가 u0 `menu.png`와 ≥99%(동적 영역 마스크 공개), `%TEMP%` 로그에 install active + mirror2x_present ≥1, drive_c 루트 새 파일 0.
  - (a)가 800×600이 아니면 결함 가정이 반증된 것이다. 그 사실을 기록하고 수리의 필요성을 다시 판단한다.
- **UA1-3 회귀:** 새 DLL로 save006 full pair 1회(`--hd-source scale2x --candidate-no-present-trace`). PASS 조건: u0와 같은 gate 전부, input_effect 7/7, 원본 SHA 불변, cleanup.
- **UA1-4 재스테이징:** 공유 temp `20261007_lap1101_work_hua1/user_test_staging/`에 새 `_inmm.dll`(SHA)·.bat 2개(변경 없으면 그대로)·안내문 개정본을 둔다. 안내문에 넣을 것: 관리자 권한 불필요, 기록 파일 위치(`%TEMP%` 또는 `C:\`)와 UA1-0 표의 상시 파일, supply bridge 비활성 사실, BGM 없음 가능, HQ 2002 EXE 전용(ESL 2606에서는 G1 꺼짐), stock `_inmm.dll` 백업/원복. `260921_temp` 배치는 하지 않는다.
- **판정:** UA1-1~3 PASS면 `PASS(partial, 기술)` → 다음 middle이 독립 재조립·SHA 대조 뒤 APPROVALS G1 사용자 시험 요청 + root 전달 ESCALATE_SOL. (b)가 FAIL이면 원인을 추적해 수리하고 다시 실행한다(구현 우선).
- **공통 FAIL:** 원본/참고/사용자 폴더 쓰기, 크래시, 안전 위반, 하네스 trace 모드 계약 변경. source를 바꾸면 lint·typecheck 뒤 기록 freeze 후 `make check` 1회.

backlog(유지): `FlushFileBuffers` 매 이벤트 비용(사용자 모드 flush 생략은 별도 가설), v3 ord 350 단발 UNKNOWN, `0x4676D0`, 화면 밖 `0x467410`, `0x465FC0` 화면 대상, H-UL, throttle ord 123, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`, focused G1 테스트. 결과는 STATUS에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번에 바꾼 것은 문서뿐이고, source·하네스·테스트는 lap1099 full PASS 1694 때와 같다.

## 다음 한 가지

work(Sonnet): §4 H-UA1 — UA1-0 정적 전수 → UA1-1 fail-open 최소 수정(TDD) → UA1-2 `C:\` 쓰기 불가 격리 RED/GREEN → UA1-3 save006 pair 회귀 → UA1-4 재스테이징.

# 2026-10-07 | lap1102 | G1 middle — H-UA1 독립 검수 + H-UA2(사용자 모드 `inmm_unit_ticks` 끄기) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1101 work), lap1101 기록, lap1100 §4 사전등록 카드. INBOX 새 지시 없음(구현 우선·묻지 말고 결정·G1 최우선 유지), APPROVALS 새 반려 없음.
- ESCALATE_SOL 처리: 원문을 byte 그대로 `docs/history/laps/20261007_lap1102_preserved_lap1101_escalate_sol.txt`(SHA256 `a7651f812a8b45f0…9198`, cmp 일치)에 보존한 뒤 삭제했다. 이번 회차는 root 전달 요청이 없어서 새 ESCALATE_SOL을 만들지 않는다(§3).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…a8ac`, stock `_inmm.dll` `03192987…f160` 모두 read-only MATCH.
- fixture: lap1101 UA1-2 직접 기동(PS9 메뉴), UA1-3 비합성 save006 full pair. 활성 8인 증명이 아니다.

## 1. 독립 재계산 (새 스크립트, work 스크립트 재사용·import 없음)

스크립트는 공유 temp `20261007_lap1102_middle_review/recalc_lap1102.py`(SHA256 `c4f91c1413f3dc04…1028`), 결과는 `recalc_lap1102.json`(`7200d5e37595580e…f324`)이다. 검사 50개, **불일치 0**.
첫 실행에서는 불일치 2가 나왔다. 둘 다 내 스크립트 쪽 문제였다. (i) input_effect 값이 문자열 `"PASS"`가 아니라 `true`(7/7 모두 true)였다. (ii) trace 사본 건수는 아래 정정 1로 설명된다. 판정식을 이 둘에 맞게 고친 뒤 다시 실행했다.

| 항목 | 결과 |
|---|---|
| 주장 SHA 12개(a/b result·pair-result·DLL 2개·스크립트·menu.png 2개·스테이징 4파일) | 12/12 일치. 스테이징 디렉터리는 정확히 4파일 |
| .bat 2개 | lap1099 스테이징과 byte 동일 |
| `bridge_new` DLL(`4d6e7bfc…`) vs `ua1_3/bridge` DLL(`34a9c777…`) | 다른 바이트 6개(136·137·216·217·331780·331781)가 모두 PE 타임스탬프·CheckSum 필드 안에 있다 |
| bridge 소스 = 현재 트리 | 두 bridge 디렉터리 모두 일치. 다른 점은 `inmm_stub.c`의 supply_probe 2줄 삽입과 Makefile SRCS의 `runtime_bridge.c` 추가뿐 |
| **독립 재조립**(현재 트리 → 새 디렉터리 → mingw `make`) | 436,230 B. 타임스탬프 3필드를 마스크하면 스테이징 DLL과 **동일**하다(재빌드 SHA `1c1a77d0…9f61`) |
| 소스 계약 | 트리에서 GREEN: fallback·`env_enabled()` 게이트·순서·C:\ 경로 유지. `HEAD`(34d59dd) 소스에 같은 판정식을 돌리면 RED(fallback 없음·무조건 게이트) |
| 트리 파일 SHA 주장 | `direct_draw_trace.c` `2fbc28e1…`·테스트 `2bd76e08…` 일치 |
| UA1-2 a(구 DLL `aef92b53…`) | drive_c 쓰기 차단 확인. 800×600만 있고 1600×1200 창 없음. `%TEMP%`·C:\ trace 없음. PS9 60초 생존. EXE SHA 3/3 일치. → **결함 재현** |
| UA1-2 b(새 DLL) | 1600×1200만 있고 800×600 창 없음. `%TEMP%` trace에 install `starting`→`active`, failed 0, run_id `unknown`(opt-in 없음). drive_c 루트 새 파일 0. PS9 60초 생존. chmod 복구 오류 없음(현재 mode 755) |
| b `menu.png` vs lap1099 u0 `menu.png` | 1600×1200 **0 px 차이** |
| UA1-3 pair | `status` PASS·`scene_state_equal`, input_effect 7/7, V2/V2s/V2q/Scale2x/loaded/minimap parity PASS, EXE SHA 4/4, source_unchanged 3/3, 창 1600×1200 scale 2, cleanup ok·game 삭제·prefix 프로세스 0. 후보 trace run_id `unknown`, mirror2x_present 1,263 |
| UA1-3 vs u0 | `menu.png`·`loaded.png` 모두 **0 px 차이**(fallback은 C:\ 쓰기 가능 환경에서 동작을 바꾸지 않는다는 주장과 맞음) |

정적 확인(직접 읽음): `g_trace_failed`를 읽는 곳은 summary 상태 문자열(`direct_draw_trace.c:773`) 하나뿐이다. 로그 handle이 invalid면 `trace_event_raw`·`write_line`이 즉시 FALSE를 반환한다. 이 경우 `trace_overflow`도 같은 이유로 쓰지 못한다. 그래서 C:\·`%TEMP%`가 둘 다 실패해 로그가 없을 때도 설치·mirror 경로에는 영향이 없다. 다만 이 "둘 다 실패" 경로는 런타임으로 실행해 보지 않았다(정적 근거만 있음).

**H-UA1 `PASS(partial, 기술·격리)` 수용.** 정정 2건:
- **정정 1:** b의 trace 총계 4,760/4,196은 game이 아직 돌던 시점에 읽은 값이다. 사본(`temp_trace_copy.jsonl`)과 prefix 원본은 그 뒤 96ms 동안 더 쓰여서 최종 4,767/4,203이다. 사본 앞 4,760 이벤트만 세면 mirror2x_present가 정확히 4,196이다(append-only 상위집합). 판정은 바뀌지 않는다.
- **정정 2(안내문 오기재, 사용자 영향 있음):** 안내문은 `inmm_unit_ticks.jsonl`이 "세이브006 장면에서 약 1~2분 플레이에 50MB 정도"라고 적었다. 실측은 다르다. UA1-3 후보 prefix 파일의 생성~마지막 쓰기 간격이 41.9초인데 그동안 53,197,428 B가 쌓였다(baseline 52.7MB). 초당 약 1.27MB, **시간당 약 4.6GB**다. 안내문은 2~3배 과소 기재했다. 같은 run의 나머지 상시 로그는 sfx 0.49MB/49초(시간당 약 36MB), watch 0.35MB/51초(약 25MB), asset 44KB이고 나머지는 1KB 미만이다.

## 2. H-UA2 필요 판정 — 사용자 시험 전에 필요

- 근거: `inmm_stub.c` worker를 보면 PS3에 있는 동안 `UNIT_TICK_DUMP_INTERVAL` 50(게임 tick)마다 전 유닛을 한 줄씩 `WriteFile` 한다. 실측으로는 초당 약 16 덤프, 덤프당 약 575줄이다. 크기 상한이 없다. PS3에 다시 들어올 때마다 `CREATE_ALWAYS`로 새로 만들기 때문에, 크기는 한 번 연속 플레이한 길이에 비례한다. `C:\`에 쓸 수 있는 사용자(관리자 실행이거나 ACL이 다른 경우)가 한 시간 플레이하면 수 GB가 디스크에 쓰인다. 원래 쓰던 stock `_inmm.dll`에는 없던 부작용이다.
- 이 덤프는 G2 soak 등 과거 하네스 카드가 쓰는 진단이다(`docs/work/active/G2_*` 3건이 참조). 그래서 하네스 기본 동작은 바꾸지 않는다. 사용자 `.bat`이 끄는 **opt-out**으로 한정한다. 기존 env 이름 관례(`INMM_STUB_NO_MCI`·`INMM_STUB_FAKE_CD`)를 따른다.
- G1 사용자 시험 요청(APPROVALS)과 root 전달(ESCALATE_SOL)은 H-UA2 뒤로 미룬다. 수리가 작고, 안내문 정정과 함께 한 번에 보내는 편이 시험 왕복을 줄인다. lap1101 스테이징은 증거로 보존하고 사용자에게 전달하지 않는다.

## 3. 판정

- **H-UA1 `PASS(partial, 기술·격리)` 수용**, 정정 1·2.
- **H-UA2 사전등록**(§4). 사용자 시험 요청과 root 전달은 그 뒤 middle이 한다.
- 열린 위험(유지·공개): 실제 Windows ACL 미재현(Wine chmod뿐), C:\·`%TEMP%` 동시 실패 경로는 정적 근거만 있음, 실제 Windows 1600×1200 모드와 1080p 표시, DxWnd env 전달(.bat 미실행), BGM, `FlushFileBuffers` 비용, G2/G5/G6G7 EXE 조합 미측정. ESL 2606 EXE에서 G1이 꺼진다는 것은 SHA 고정 계약에 근거한 정적 판단이다. 안내문은 이를 런타임 확인처럼 쓰지 않게 고친다.

## 4. 다음 work 사전등록(Sonnet) — H-UA2: 사용자 `.bat`에서 `inmm_unit_ticks.jsonl` 끄기

**가설:** env `INMM_STUB_NO_UNIT_TICKS`(값이 있으면 켜짐)가 설정되면 PS3 유닛 덤프 파일을 만들지도 쓰지도 않는다. 사용자 `.bat` 두 개가 이 env를 넣으면 시험판의 상시 디스크 쓰기가 시간당 수 GB에서 수십 MB로 줄어든다. env가 없으면 지금과 byte 단위로 같은 동작이다(하네스·G2 진단 불변).

- **UA2-1 최소 수정(TDD, `tools/inmm_stub/inmm_stub.c`만):** 덤프 진입부(`dump_units_at_tick` 호출 조건 또는 함수 첫머리)에서 env를 한 번만 읽어 캐시하고, 설정돼 있으면 반환한다. 파일 열기·쓰기 0. 소스 계약 테스트로 RED→GREEN을 확인한다. env 이름, 캐시, 열기 전에 반환하는지를 본다. 다른 상시 로그는 손대지 않는다(크기가 작음, §1 정정 2).
- **UA2-2 하네스 opt-in(최소):** `tools/g1_saved_scene_probe.py`에 후보 lane 전용 flag(예: `--candidate-no-unit-ticks`)를 추가해 후보 env에만 `INMM_STUB_NO_UNIT_TICKS=1`을 넣는다. 기존 `--candidate-no-present-trace`와 같은 방식으로 TDD한다. 기본값과 baseline lane은 바꾸지 않는다.
- **UA2-3 런타임(save006 full pair 1회):** `--hd-source scale2x --candidate-no-present-trace --candidate-no-unit-ticks`로 실행한다. PASS 조건: (a) 후보 prefix `drive_c`에 `inmm_unit_ticks.jsonl` **없음**, (b) baseline prefix에는 있고 1MB 이상(env 미설정 기본 동작 유지), (c) pair `status` PASS·input_effect 7/7·V2/V2s/V2q/Scale2x/loaded/minimap parity PASS·원본 SHA 불변·cleanup ok, (d) 후보 `menu.png`·`loaded.png`가 lap1101 UA1-3과 0 px 차이(다르면 차이 영역과 원인을 기록한다. 동적 프레임 차이는 공개한 뒤 판정). 실패하면 원인을 추적해 고치고 다시 실행한다.
- **UA2-4 재스테이징:** 공유 temp `20261007_lap11xx_work_hua2/user_test_staging/`에 둔다. 들어갈 것: 새 `_inmm.dll`(독립 재조립 가능한 bridge 산출물), `.bat` 2개(각각 `set INMM_STUB_NO_UNIT_TICKS=1` 한 줄만 추가), 안내문 개정본. 안내문에서 고칠 것: unit_ticks는 `.bat`이 끈다는 사실과 `.bat` 없이 env 없이 실행하면 켜진다는 사실(그 경우 G1도 꺼진다), 실측 크기 정정(§1 정정 2 수치, 남은 상시 로그는 시간당 수십 MB), ESL 2606 문구를 "SHA 고정 안전장치로 꺼지도록 만들어져 있음(직접 실행 확인은 안 함)"으로, present trace 크기 문구는 실측(4,767 이벤트 12MB, 상한 8,192 이벤트). `260921_temp` 배치는 하지 않는다.
- **판정:** UA2-1~3 PASS면 `PASS(partial, 기술)`. 그다음 middle이 독립 재조립·SHA 대조를 하고, APPROVALS에 G1 사용자 시험 요청을 올리고, root 전달 ESCALATE_SOL을 만든다.
- **공통 FAIL:** 원본/참고/사용자 폴더 쓰기, 크래시, 안전 위반, env 미설정 기본 동작 변경, 하네스 trace 모드 계약 변경. source를 바꾸면 lint·typecheck를 먼저 돌리고, 기록을 freeze한 뒤 `make check` 1회.

backlog(유지): C:\·`%TEMP%` 동시 실패 런타임 확인(선택), `FlushFileBuffers` 매 이벤트 비용, v3 ord 350 단발 UNKNOWN, `0x4676D0`, 화면 밖 `0x467410`, `0x465FC0` 화면 대상, H-UL, throttle ord 123, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역.

## 5. 검사

- 기록을 freeze한 뒤 `checks/safety.sh check`·`checks/context_limits.py`·focused G1 테스트를 돌린다. 결과는 STATUS에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번에 바꾼 것은 문서뿐이고, source·하네스·테스트는 lap1101 full PASS(1696) 때와 같다.

## 다음 한 가지

work(Sonnet): §4 H-UA2 — UA2-1 env opt-out(TDD) → UA2-2 하네스 후보 flag → UA2-3 save006 pair → UA2-4 재스테이징(.bat 1줄 + 안내문 정정).

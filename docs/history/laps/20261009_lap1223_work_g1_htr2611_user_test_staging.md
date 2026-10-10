# 2026-10-09 | lap 1223 | G1 work — H-TR2611: 2611 사용자 시험판 스테이징

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`/high, work(실무) 1 lap. 제품 C·validator·gate 변경 0(테스트 1개 추가뿐). middle 검수 전.
- 가설 / 사용자 관찰: lap1222 §4 — 현재 트리 G1 DLL(팩 끔, Scale2x)을 2611 게임 폴더의 `_inmm.dll`로 놓고 2611 EXE를 띄우면 확인 pair가 lap1221 e23과 같은 게이트를 통과한다. 사용자 업스케일·G1 시험 결과 INBOX 도착 0.
- 예상 PASS / FAIL 조건: TR-0 변이 m7 RED, TR-1 pair 2 run PASS(두 lane 2611, 장면 같음, 안전 0), TR-2 PS9→7→5→3·stale 0·안전 0, TR-3 파일 3개·`.bat` diff = EXE 이름 줄뿐·txt 0.
- 변경 파일 / fingerprint / 커밋: `tests/test_g1_new_game_path.py`(`56ff11db5971`) 테스트 1개 추가(`test_start_new_game_records_each_click_result_as_returned_by_inject`). 그 밖 source 변경 0(`tools/g1_saved_scene_probe.py` `f00c09cfec05`는 변이 실험 후 바이트 그대로 복원). 전부 uncommitted.
- 원본 SHA / 후보 SHA / 환경 / fixture: HQ2002 원본 `b56986e0…` 모든 lane `source_unchanged` true·`game_removed` true. 두 lane 비공개 EXE = 2611 `d9d6bb3d…`. save006 `616b7997…`·플레이어 8·유닛 559(pair 두 run 두 lane 동일). 팩 끔, `--hd-source scale2x`, `--esl2610`. 스테이징 `_inmm.dll` SHA256 `8807827b4e98…`(= TR-1 첫 run `bridge/_inmm.dll` byte 그대로).

## 실행 (모두 `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1223_<run> --artifact-root <공유 temp>/20261009_lap1223_work_htr2611/<run> --hd-source scale2x --esl2610 …`, setsid nohup, `.exit` 0)

- TR-1 `tr1_1`·`tr1_2`: `--candidate-no-present-trace --candidate-no-unit-ticks`(lap1221 e23 명령 그대로). 로그 `logs/gates/lap1223-tr1-{1,2}.log`.
- TR-2 `tr2`: `--new-game-path --new-game-start --new-game-play`(키·체류 기본값). 로그 `logs/gates/lap1223-tr2.log`.
- 요약 스크립트 `<공유 temp>/…/scripts/tr1_summary.py`(`9cd9de6aa9dd`): trace·input trace 직접 읽기 → `tr1_summary.json`(`889439ea9a61`)·`tr2_summary.json`(`7bc5c2b4e72b`).

## 측정·판정

**TR-0 PASS.** m7(클릭 결과 대신 빈 기록) 사본 변이 → 새 테스트 RED(`1 failed, 5 passed`), 복원 → `tests/test_g1_new_game_path.py` 77 passed.

**TR-1 PASS.** 두 run pair `status` PASS·`scene_state_equal` true·게이트 6종(input_effect·minimap·V2·V2s·V2q·Scale2x) PASS·캡처 5종 V2s PASS·두 lane `private_exe` 2611·outside diff 0·palette 위반 0.

| run | PS3 present / stale 합 / covered 최소 / p95·max | PS9 · PS35 stale | V2s unexplained(loaded/sel/drag/mini/prod) | 안전 8종·hresult·success≠1·dropped |
|---|---|---|---|---|
| tr1_1 | 781 / **0** / 476,557 / 11·56 | 0 · 0 | 30/173/180/233/226 | 전부 0 |
| tr1_2 | 793 / **0** / 476,574 / 9·22 | 0 · 0 | 23/49/173/240/197 | 전부 0 |

stale present 0 → 위치 기록 대상 없음(e23의 3 present 단발 stale은 이번 2 run에서 **재발 0** → lap1222 backlog 재개 조건 미충족). 공개: p95 9~11·max 56이 e23(7~8·12~13)보다 높다 — 실행 중 호스트 load average 6.8~7.2(별도 2611 세션 병행)이고 stale·안전 영향 0이라 호스트 부하 변동으로 본다(같은 호스트 효과를 lap1216 N1 p95 9도 같은 이유로 기록).

**TR-2 PASS.** `tr2/new-game-path-result.json`(`befebb79d08c`) status PASS, 두 lane PASS. 후보 trace 프로그램 상태 40→60→180→9→7→5→2→3. **E2-0 재시도의 첫 런타임 증거:** 입력 trace(WndProc)로 확인 클릭(608,564) down 2회 — 1회차 down→up 118 ms 뒤 PS5에 머무름, 8 s 대기 뒤 2회차(1회차 +10.07 s) → PS2(+2.2 s)→PS3. 클릭 소실이 아니라 자동 시작 지연으로 재시도가 발동한 경우다(두 클릭 down→up 118·108 ms, lap1219 C1의 1~11 ms 소실과는 다른 경우). PS3 1,718 present stale 0·covered 480,000 전부·p95 13·max 55·PS5 619·PS7 145·PS9 51 stale 0·안전 8종 0·dropped 0. 후보 trace 끝(110.5 s)의 `7,5,2,3`은 동일 ts의 상태 스냅샷 줄이다. 별도로 같은 명령의 **로그가 덮어씌워진 첫 실행**(`tr2_first_unlogged/`, result status PASS, PS3 1,530 present stale 0·p95 24·max 71·안전 0)이 있다 — 내가 `cd`를 백그라운드 서브셸에만 걸어 첫 실행이 로그를 현재 디렉터리 상대경로에 쓰려다 실패한 것으로 착각하고 같은 명령을 다시 띄우는 바람에, 두 번째(곧바로 `FileExistsError` exit 1) 시도가 `lap1223-tr2.log/.exit`를 덮어썼다. 그 덮어쓴 파일은 `logs/gates/lap1223_overwritten/`로 옮겨 보존했고, 판정은 로그·exit가 온전한 재실행(`tr2`)에 건다. `tr2_first_unlogged`는 참고 증거다(로그·exit 없음).

**TR-3 PASS.** 공유 temp `20261009_lap1223_work_htr2611/user_test_staging/` 3파일(안내문 txt 0):

| 파일 | SHA256 |
|---|---|
| `_inmm.dll` | `8807827b4e983dc2b1e11be4516e002563db754e090a98561169ad798f160a51` (508,542 B) |
| `g1_trial_direct.bat` | `6c94fa57163f99cb576dd4e347020d76854a90344ffbe47d5bb5df19cea91cdf` |
| `g1_trial_via_dxwnd.bat` | `29a35d2edf41dae2f7ac1b09a52d2c12bd301860733ca8cb70ce43c9e85d886c` |

- lap1151판 `.bat`와의 diff: direct는 EXE 이름 두 줄뿐(3행 주석·9행 `start`의 `[HQ]Syw2plus 2002.exe` → `[ESL]Syw2plus 2611.exe`, CRLF·ASCII 유지, 환경변수 4개 동일). via_dxwnd는 lap1151판과 **byte 동일**(`29a35d2e…`) — `dxwnd.exe`를 띄우므로 EXE 이름 줄이 없다. **DxWnd 대상 EXE를 2611로 지정하는 것은 사용자 DxWnd 설정 몫**(APPROVALS 공개용).
- `_inmm.dll` 정체성: 같은 트리에서 run마다 재빌드되어 DLL이 byte 달라진다 — tr1_1↔tr1_2·tr1_1↔tr2 모두 **6 B만 다름**(오프셋 136·137 PE TimeDateStamp, 216·217 체크섬, 384516·384517 디버그 디렉터리 시간). 기능 동일. 스테이징은 계획대로 tr1_1 것.
- 이전 lap1151판(HQ2002용 `8a3837fb…`)과 비교: DLL 457,256 → 508,542 B(lap1151 이후 H-OS1·H-PS5W1 PS5/PS7 글자 HD·팩 코드 등 누적).

## 검사

- TR-0 RED→GREEN 확인, `make typecheck` PASS(12 source files), 변경 파일 `ruff` PASS, `make lint` **FAIL — 별도 2610/2611 세션 파일 F401 3건**(`patches/esl2610/g2_scan.py:32`·`patches/esl2610/g2_state_2610.py:323`·`tools/g2_esl2610_spike_probe.py:40`; 이 루프는 수정 금지라 그대로 둠). 따라서 `make check` 전체는 PASS가 아니고, `make test` 결과는 STATUS에 적는다(런타임 증거 아님).
- 디스크: 4 run `game` 사본 삭제(`game_removed` true), output·manifest·prefix 보존(각 1.2 GB), 여유 141 GB.

## 회귀 / 남은 위험

- 2611 시험판은 G1 가시 품질(팩 끔·Scale2x)만 담는다. 사용자 업스케일 결과(팩 켬)·`.kills` 배지 런타임 미관측 UNKNOWN·전투 장면·PS7 Scale2x 아닌 기존 블록 등 backlog 유지.
- p95/max 상승은 호스트 부하 변동 추정(통제 대조 없음).
- 사용자 시험·승인 0. 이 결과는 기술 pair 증거이며 G1 마일스톤 합격 아님.

## 다음 한 가지

middle 독립 검수(새 스크립트로 `tr1_*`·`tr2` trace 재계산, 스테이징 3파일 SHA 직접 재계산, `.bat` diff) → 수용 시 APPROVALS에 2611 시험판 요청을 쓰고 root 대상 `loop/ESCALATE_SOL`로 `260921_temp` 배치를 넘긴다(옛 lap1151판은 `260921_temp/archive/`로). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.

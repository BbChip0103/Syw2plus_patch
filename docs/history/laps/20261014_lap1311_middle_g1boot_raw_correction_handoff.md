# 2026-10-14 | lap1311 middle | H-G1BOOT raw correction / HOLD

- 역할: 새 Codex App middle(진단·계획·확인), MODEL_ROUTING sol/high 계약. 실제 세션 resolved model/effort는 조회하지 않아 추측하지 않음. subagent/다른 모델 호출·폴백0; loop/.lap_counter=1311 읽기만.
- 순서: PROMPT 먼저→AGENTS/INBOX 최신 지시/APPROVALS 반려→STATUS 전체→DESIGN1~4절/현행G1→MODEL_ROUTING→lap1310 및 ESCALATE/관련 주소 근거. 오래된 PROMPT G2 10000/G4 활성은 최신 DESIGN 종결 계약으로 대체. 중간 tier 한 가지 진단/확인만 수행.
- 목표/가설: lap1310의 “후속640 요청/exception dispatch 없음·서로 다른 mode 경계”가 실제 보존raw와 일치하는지 검수하고, 원인이 미확정이면 최소 work handoff로 종료. 성공 조건은 raw 해시·모드/예외 코드 재계산·안전 회수 확인과 추측 없이 다음 관측 지정; 제품/Windows PASS가 아님.
- 변경파일: docs/STATUS.md, 이 기록, 기존STATUS/ESCALATE 보존 두 파일, loop/ESCALATE_SOL. 계산 스크립트/JSON은 공유temp `../temp/Syw2plus_patch/20261014_lap1311_middle_g1boot_review/`. 제품·하네스·테스트·EXE/DLL·원본·핀·전달물 변경0, uncommitted/커밋0.
- 원본/후보: 공식2614 EXE SHA256 `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`, 기존 WINMM `f32ee6190716e705a0376213adbe8fc0722d9a3abdaed07f248bdd4766912655` 직접 확인. 보호원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` doctor 확인. 수정0이라 old/new bytes·생성/원복 SKIP. 제공된9월full-test는 source 불일치로 현재PASS에 재사용 안 함.
- 기존 환경/fixture: lap1310 official2614/full private copy/새win32 prefix/ownedXvfb1600×1200×24, native app DDRAW+WINMM/ASI, virtual desktop 없음. PS9 전 실패하여 actions/captures 빈 배열, 새게임 클릭/PS3 실제 수행 없음. 하네스는 save006을 private game에 복사하지만 불러오기 실행 없음. 활성 인원/군대/지도/G2 부하 검증 아님. 이번 새실행0.

## 동일 raw를 직접 재계산한 정정

- 실행: `PYTHONPATH=. .venv/bin/python ../temp/Syw2plus_patch/20261014_lap1311_middle_g1boot_review/review.py` → SHA_MATCH/PRODUCT_HOLD. 계산완료 exit0은 원인/계획/제품 승인 아님. JSON SHA `dd04dc512c74b03508d534b0e087064f82b490f37d6c026f853e97eafd7db42c`.
- result `9cd8786e318524e62295973fa6a139d8434111358f2dc692a5f169daead8eb7b`, trace `f79c2c6ecabd2dbc531bcdc9d117af69f50e46d7bfc1af1c7b87ab448a2163d2`, probe.log `c726ccf0df04240345290417f41cd9448063ac576983525069b5d74bcc2e17c5`, lane probe-result `17feca174eb8bcde2a235410c788da472306bd6f72f8223ccc51c30601275cc6`, manifest `694322258731a99ea52feb42c5cd22a229cd636124acbeb0f4a0e79de9dbc9a6` 모두 lap1310 기록과 일치. 파일 변동이 아닌 기록의 오독이다.
- trace53행: seq5 initial800×600×8→1600×1200×8 HRESULT0; seq52 **640×480×32→640×480×32 HRESULT -2147467263 = 0x80004001/E_NOTIMPL**, caller/return0046457D; seq53은 CreateSurface가 아니라 structured_skip/exact_800x600x8_call_gate_mismatch. “후속640 없음·성공CreateSurface로 끝남”은 정정한다. 이 요청 순서는 lap1308 noVD/combined와 동일하며 “서로 다른 mode 경계” 주장은 철회; 같은 종료원인인지는 미입증.
- probe.log310/320행: 게임 thread0024 `dispatch_exception code=40010006` 2건, 직후 ASI disabled 진단문자열/개행 및 핸들러 기록. 다른 Wine thread0084/0074에는 code6ba dispatch5건(121/137/153/169/193행). 따라서 “exception dispatch 없음”은 부정확. **게임 치명적 c0000005/c000001d/c0000096 및 fault01FC01AD는 이 raw에 없음**; 진단문자열의 dispatch를 crash로 세지 않는다. NtUserChangeDisplaySettings -2는 별도 층으로 유지하고 첫1600 HRESULT0을 실패로 바꾸지 않는다.
- lane FAIL=`PS9 timeout; last=ProcessLookupError [Errno3] read 2550697:4ed818`; actions/captures0/trace-close 없음. 하네스 `_wait_state`는 read 오류를 포착해 대기하며, `_run_lane`은 finally에서 종료/회수하지만 **정리 전 Popen poll/returncode/종료API·원인 스택을 결과에 남기지 않는다**. 관측된 ESRCH는 read대상 PID 부재 증거이고 Windows원인·정상exit·치명예외의 구별 증거가 아님. 추적 가능한 관측 누락을 work에 최소수리 인계.
- 모듈실제로드 경로 유지: native WINMM/DDRAW, hqcdd/syw2x ASI 및 builtinDDRAW 로드로그. ASI 로드와 hqcdd의 기능활성은 구분(“ASI disabled” 진단 존재). 복사된옛hqcdd.log 재사용0. 현행 game사본부재/prefixPID0 직접확인; prefix/raw/manifest 삭제0.
- 계산 보조스크립트 초회 오류: 상수명 ESL2614_EXE를 가정해 AttributeError → 실제 verify_source 사용; 모든 Wine프로세스 dispatch를 게임2건으로 세어 assertion FAIL → 로그 thread/code 직접계산으로 전체7건/게임2건 분리. 둘 모두 원인 설명·수정·재실행 완료, 제품/필수gate 실패가 아님. raw/핀 변경으로 통과시키지 않음.

## 명시 work handoff — 같은 실패 실행의 종료와 fault만 관측

1. root는 이 raw 정정을 확인하고 즉시 work(luna/high)를 배정한다. 추가 middle/strategy 문서 루프나 새 framework/card로 보조작업 상한 초기화 금지. ownership: 기존 `tools/g1_saved_scene_probe.py`의 필요한 최소 진단 연결/관련 회귀 및 공유temp artifact. 다른 세션/원본/핀/HD/전달물 비접촉. middle은 게임 코드 수정 안 함.
2. lap1310 기존 startup-only/native-ddraw/no-virtual-desktop 명령·하네스를 재사용, 새 private full copy/prefix/빈display. PS9 대기 전에 기존 owned debugger/관측수단을 걸고 Linux child PID와 Wine PID/thread 대응·실제모듈 path/range/SHA를 확보. bootstrap/service thread의 dispatch와 게임 thread의 진단문자열/치명예외를 구분한다.
3. **finally의 close/terminate/wineserver-k 이전** Popen.poll/returncode·PID생존·마지막PS/trace seq·시각을 기록. early exit이면 실제 종료API/exit status·caller를 확보; 치명예외면 최초 EIP/인접bytes/stack/return/소유module 또는allocation을 확보. alive/debugger-wait이면 그대로 구분. PID를 추측해 다른프로세스에 attach 금지. 기존 gdb 연결 패턴 재사용, ptrace 권한/도구가 실제 막히면 로그와 구체 blocker로 종료.
4. 같은 소유 run에서 live user32!MessageBoxA 첫5bytes와 E9이면 signedrel32의 실제JMPtarget을 기계계산, target module/range/bytes 확보. DllMain 소스의 의도나 기록주소로 runtime을 대체하지 않는다. 모드seq5/seq52 HRESULT와 종료관측을 함께 묶는다. 원본API 실패를 강제SUCCESS로 숨기지 않는다.
5. 증명된 구현 결함이면 기존 root 범위(G1 모드/표면실패시 해제·원본800×600복귀) 안에서 work가 RED→GREEN 수리/재실행. 근거 없는 fallback/예외삼키기 금지. 수리 후 기존요청 native/noVD/desktop 60초PS3+관련회귀/lint/typecheck→freshmiddle1회, 전달직전 전체check는 root 해당경계에서만. 원인이 여전히 미확정이면 raw 보존·ESCALATE, exit0/시험준비를 제품완료로 사용하지 않음.

## 검사·보존·판정

- 목표 관련 `pytest -q tests/test_g1_esl2614_startup.py`: 2 passed/0.03s. `make lint` PASS, `make typecheck` 12source PASS. `make doctor` 패키지/보호원본SHA 확인; 일반runtime manifest미등록(runtime.ok=false)은 기존상태이며 실제게임 검증PASS가 아님. 전체makecheck SKIP(전달경계 아님), 새게임/빌드/원복시험/Windows/사용자마일스톤 SKIP.
- STATUS 원문99줄/SHA `010a0d5ac6cd0141627cba4614071e11d3ac708fd9b3a0178590b46b317a4687`와 ESCALATE 원문/SHA `25cd8d01e6bc1d2607be8f59e5c0be867a80ee0c4b79c3f83fbdef625e15a10a`를 각각 `20261014_lap1311_status_before_raw_correction.md`, `20261014_lap1311_preserved_lap1310_escalate_sol.txt`에 byte-exact 보존. lap1310 work 원문/raw·APPROVALS반려/미결·INBOX지시 불변.
- 판정 **HOLD / 원인 UNKNOWN**. 같은SHA raw 전사정정과 좁은 계측handoff는 완료; 사용자 Windows FAIL/실제startup 실패는 미해결. 필수 runtime 증거·MessageBox live target·fault상태·G1마일스톤 미검증. `loop/ESCALATE_SOL` 갱신하여 root 승격, 중간tier에서 임의마감0.
- 최종문서/context/safety/implementation불변 확인은 아래에 추가한다. STATUS는130줄 이하, INBOX350/APPROVALS205줄에 새항목을 추가하지 않음. 제품 진척으로 계산하지 않음.

- 최종확인: CONTEXT_PASS / SAFETY_PASS(--require-game) / git diff --check PASS. STATUS102/INBOX350/APPROVALS205줄·Blockers절1개. source7파일/DLL SHA불변·lap1311읽기만·보존STATUS/markerSHA MATCH. final-checks.json은공유temp; 승격marker존재·장기실행없음·원인HOLD로종료.

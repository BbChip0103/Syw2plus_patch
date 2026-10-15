# 2026-10-14 | lap1309 middle | H-G1BOOT failure-boundary diagnosis / HOLD

- 지정 역할/provider: fresh Codex App middle(진단·계획·확인); 현재 MODEL_ROUTING은 sol/high. App 실제 resolved ID/effort는 별도 조회되지 않아 추측하지 않는다. 독립 raw 대조 native `debugger`에 `gpt-6.1-sol`/high를 명시 요청; 모델 폴백0. `loop/.lap_counter=1309` 읽기만, 게임 hands-on 구현0.
- 문서 순서: PROMPT ①~⑥→AGENTS→INBOX 최신지시/APPROVALS 반려→STATUS 전체→DESIGN 1~4절/현행G1→MODEL_ROUTING→lap1308/ESCALATE. PROMPT의 옛 G2 10000/G4활성은 최신 DESIGN/사용자결정으로 대체한다. 현재 범위는 Windows HD2 시작즉시종료 H-G1BOOT이며 별도2614 두조합/legacy2608/G1화질 승인은 비접촉.
- 목표/한 가지 가설: root와lap1308의 같은주소 예외가 같은 모드전환실패인지 독립 판정하고, 검증가능한 work handoff를 남긴다. 종료조건은 raw의요청/HRESULT/예외코드·기존로그진위·실패반환경로 확인 후 원인 불명확하면 HOLD/승격. 새게임·DLL수리·전달·추가합격조건을 만들지 않는다.
- 변경파일: 이기록, `analysis/memory_maps/g1_esl2614_startup_failure_lap1309.md`, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, STATUS원문archive, 이전marker보존, `loop/ESCALATE_SOL`. 독립계산/asm/JSON은 공유temp `../temp/Syw2plus_patch/20261014_lap1309_middle_g1boot_review/`. 제품/하네스/테스트·원본/후보/전달수정0;커밋0/uncommitted. INBOX350줄 원문은변경하지않았다.
- 기록전 source: validation fingerprint `7e7440ed14121081ec6034c65159c57d2a2ece74`, implementation `4857a1bad89fd9f6309860efce8a47bea9b6f88e`; HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`는 provenance. 제공된9월full-test는source불일치로현재PASS에재사용하지않았다. 기록/주소문서는validation입력이지만제품진척이아니다.
- 입력/후보SHA: 공식2614 EXE `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`; 현재 WINMM 및사용자HD2 전달DLL 모두 `f32ee6190716e705a0376213adbe8fc0722d9a3abdaed07f248bdd4766912655`, 직접재계산MATCH. 보호원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` doctor확인. 이번 EXE패치/old-new bytes/원복생성 SKIP(바이너리수정0).
- 기존 실행환경/fixture: lap1308 완전한private copy·각각win32 prefix·ownedXvfb1600x1200x24, G1 display-only/원본2614SHA·HD2DLL. asi는virtualdesktop/nativeoverride, noVD는builtinDDraw/desktop없음, combined는nativeoverride/desktop없음. 활성인원/군대부하/G2/저장fixture합격과무관한startup 관측이다. 이번 fresh 실행은없다.

## 이전 work와 root raw 독립 확인

- 독립계산 명령: `python3 ../temp/Syw2plus_patch/20261014_lap1309_middle_g1boot_review/review.py` → `RAW_REVIEW_COMPLETE / PRODUCT_HOLD`. JSON SHA256 `7690407d3b9d76b320c3514c99e8918435c1471ec333ece9356e69799a20b680`. source7개/EXE/DLL/각trace·probe·resultSHA, mode events·예외line번호·4개asm을보존했다. script exit0은계산완료일뿐제품PASS가아니다.
- noVD raw53행 SHA `5e839eac79bf0fd49af8eca69835377456928f3ec887c74cd2ce31dc5d957e1d`,combined53행 SHA `3aa177d842da0a9f35710ee88e968560efec68b8cea5c04126e29db6414b0360`,asi2300행 SHA `ea270c4261b06656065c6660aad92cfadaba2b1cd9c5ff7105a1f6f6300cbe4f` 직접일치. 세result cleanup.prefix_processes_after=[]·현재game사본부재확인, prefix/raw/manifest는삭제하지않았다. 당시cleanup기록이며이번에game를다시종료하거나prefix삭제하지않음.
- **초기1600 실패단정 미입증(high):** noVD/combined trace line5 둘다800×600×8→1600×1200×8 HRESULT0,primary생성/1600descriptor성공. line52는640×480×32 그대로전달→E_NOTIMPL `0x80004001`;caller0046457D. 가상desktop asi는동일640/800교대요청도성공하며PS3진입. trace는PS40이고runner최후PS60이므로서로다른시점관측으로분리한다. root Wine의 `NtUserChangeDisplaySettings -2`만으로초기1600요청을식별할수없다.
- **단순전사정정(high):** lap1308기록은combined도c000001d로썼지만실제combined probe.log:143은`c0000096` privileged instruction. noVD:131은`c000001d`;rootI:305는`c0000005`/readFFFFFFFF. 같은01FC01AD를동일결함으로승격하지않는다. 기존work원문/raw는불변으로보존하고현재STATUS/이기록만정정한다.
- **root plugin로그진위(high):** `I_hd2_loaddll.hqcdd.log`와읽기전용입력hqcdd.log는둘다5117B/SHA`629f5626e4e1b3d0751754bd3944acacbb218c0c8245b557c1f566554cd8e441`. root복사스크립트의preexisting 로그이며PID24272를이번Wine실행으로귀속하지않는다. rootWine로그의nativeWINMM로드·builtinDDRAW로드는별도직접기록이다. lap1308combined의“ASI disabled: DirectDraw import already intercepted”(probe.log:125)는실행중debug출력이나정확한DDraw/두ASI모듈범위·SHA는없다. override만으로모두로드PASS를쓰지않는다.
- **실패반환 위치 확인(high):** 공식EXE objdump0046457A=`call [ecx+54]`;0046457D=`test eax,eax; jne0046489A`;0046489A는레지스터복원/xor eax,eax/ret10(FALSE). 이위치가직접01FC01AD를부르지않는다. 후속예외의스택·메모리bytes·allocation/module귀속미수집이라원인UNKNOWN. 주소/bytes근거는memory_maps문서와공유temp4asm에기록했다.
- **수리 후보는가설만(low):** `inmm_stub.c:556–572`의무조건MessageBoxA5byte rel32 patch,실제모드전환·후속surface/COM호출·Winevideo/error path는후속진단대상이다. MessageBox패치의fault-time bytes/실제target없으므로원인확정·수정승인아님. noVDprefix로그의초기MessageBox2회정상억제도즉시고장단정의반례이다.

## 검사 / 한계 / 보존

- fresh목표관련Fast: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g1_esl2614_startup.py` **2 passed/0.12s**. `make doctor` 패키지/보호원본SHA PASS(일반runtime manifest미등록은기존상태); `make lint` Ruff/compileall PASS; `make typecheck` 12source PASS. 이번실패/재시도0. 이전253회귀는lap1308당시증거로만유지한다.
- REA skill은읽었으나현재App에REA MCP등록없음; `rea doctor --client codex --json`에서codex registration config_drift 확인. 설정/새engine설치하지않고허용된offline shell objdump를사용했다. REA Evidence를만들었다고주장하지않음.
- **판정: 원인BLOCKED/HOLD,진단대조만완료.** Windows사용자FAIL,예외종류차이,초기1600실패미재현,ASI모듈귀속미확보유지. DLL 수리/build/수리후60초/전체makecheck/전달/사용자마일스톤 SKIP. root자료를더얻을수없는현재read-only범위에서추측수리를승인하지않는다.
- STATUS전문130줄/SHA `0433d9e716967e4f5bd13513a7e9a5d68e9e596f51aef6a329ed4b29f2608fbc`를 `docs/history/20261014_status_lap1309_precompaction.md`에byte-exact보존후완료계보요약을포인터화했다. 기존marker전문은 `20261014_lap1309_preserved_lap1308_escalate_sol.md`/SHA `b05ac3f757c735de6804243b0e0ad6f16054ca592a1f1193f871d684291546a7`로보존했다. 원문반려/미결/과거FAIL삭제0.

## root/Sol 확인 → work tier 명시 handoff

1. root/Sol은자료모순·가설경계를확인하고**다음work가바로제품probe에복귀**하게배정한다. 같은raw의추가middle/strategy문서회차나보조framework로시간상한을초기화하지않는다. 현재단일큐는STATUS이다.
2. work(luna/high) ownership은기존`g1_saved_scene_probe.py`/`g1_esl2614_display_probe.py`의필요최소관측연결과공유temp진단artifact. 다른세션/원본/핀/HD/전달물비접촉. 기존noVD 실패명령·사본/prefix/빈display를쓰고처음예외에서모듈범위·fault주소주변bytes·스택/return address·user32!MessageBoxA5byte/계산한JMPtarget을한소유run에수집한다. 0046457A/7D에서요청/HRESULT 순서를함께관측하고DDraw/WINMM/두ASI의실제path+SHA를같은run의+loaddll/rawmaps로기록한다. 기존maps/진단수단재사용,입력에서복사된로그는offset 전후또는그run의PID로분리한다.
3. 초기1600실패를시험하려면noVD만으로재현되었다고쓰지않는다. 별도작은ownedXvfb(예800×600)에서실제800→1600요청/원래API의FAILED HRESULT가관측되는지확인할수있으나실패유발을보장하지않는다. 원래API가성공하면미재현으로그대로기록; 강제HRESULT/fixture는**synthetic branch검사**이고Windows충돌재현과구분한다. 현실패640경로를이추가가설때문에미루지않는다.
4. 원인이추적가능해지면기존root최소수리범위(G1모드/표면실패시자체해제·원본800×600복귀)안에서**증명된경로만**수리·RED→GREEN 재실행한다. env한번변경만으로cached opt-in/설치된mirror·입력훅이해제됐다고가정하지않고원본입력/표면상태복귀를확인한다. 640실패를무조건SUCCESS로반환·예외삼키기/핀갱신금지. middle은게임C수리를대신하지않는다.
5. 수리후기존root요청(a nativeDDraw/desktop,b noVD,기존virtualdesktop)60초PS3·관련회귀/lint/typecheck→fresh middle한번;root전달직전전체check는그경계에서만한다. 원인진단실패면그새raw/구체blocker를보존해승격,추측fallback판/사용자PASS로마감하지않는다.

- 최종확인: context `CONTEXT_PASS`, safety check --require-game `SAFETY_PASS`, git diff --check PASS. STATUS97/INBOX350/APPROVALS205줄·Blockers절1개·lap1309불변; source7개SHA/EXE/DLL 및 implementation fingerprint `4857a1bad89fd9f6309860efce8a47bea9b6f88e` 불변. 공식 EXE 이미지 00400000–01B1C000에서fault01FC01AD가범위밖임을PE로확인, IAT004E51CC=USER32!MessageBoxA확인. 추가게임/소유장기명령/필수검사재시도0; marker남기고승격종료. 공유temp `final-checks.json`은이마지막기록직전snapshot이며후속문서변경은validation fingerprint에포함된다. process exit0은원인/계획승인/제품검증PASS아니다.

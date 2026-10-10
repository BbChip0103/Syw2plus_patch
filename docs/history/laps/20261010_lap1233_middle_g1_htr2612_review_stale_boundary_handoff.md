# 2026-10-10 | lap 1233 | G1 middle — H-TR2612 독립 검수·stale 재개·경계 인계

- 역할: 사용자 지정 middle(진단·계획·확인), Codex App native-hook. 선택 계약은 sol/high; 실제 launch argv/model ID는 이 surface에서 직접 확인 불가하여 추측하지 않는다. 게임/하네스/테스트 hands-on 변경·actual runtime·커밋·전달 0.
- 입력 순서: loop/PROMPT.md ①~⑥ → AGENTS/최신 INBOX·APPROVALS → STATUS 전체 → DESIGN 1~4·MODEL_ROUTING → lap1232 기록/raw → lap1222 stale/TR 계약. counter=1233 읽기만, STOP 없음. patch-validation·visual-verdict 적용.
- 가설/성공식: lap1232의 두 2612/save006 pair 및 새 게임의 raw/소스/이미지/입력/종료가 기록과 일치하는지 독립 재계산한다. 과거2611 HOLD·전달 사실·사용자 승인 미결은 보존한다. 기술 부분 확인과 시험판/마일스톤 수용을 분리한다.
- 변경 파일: 이 lap 기록·이전 ESCALATE 보존 파일·loop/ESCALATE_SOL·STATUS. 공유 temp 독립 스크립트/JSON 및 ignored visual state만 추가. 제품 소스/원본/raw/pin/golden 변경 0, uncommitted.
- entry validation fingerprint: `a0acde8037b858ef6c9830d2b307342dbe2ba1ee` — lap1232 전체 Fast 기록과 직접 MATCH. 기존 프로세스 exit0만 쓰지 않고 log의 pytest/Ruff/mypy/context를 직접 확인(2177 passed·9 skipped/889.23s, log SHA `f98f07e49416efba438c16667c75668024c65c406c2be2aebc9e605eb2097086`). 이 문서 고정 뒤 최종 full Fast를 1회 완주하고 결과/fingerprint는 STATUS에만 보강한다.

## 독립 검사 결과

공유 temp `../temp/Syw2plus_patch/20261010_lap1233_middle_review/audit.py` 실행 → `review.json` SHA256 `14f49831ca492611df2bb15320803a60032a407884c632c33e51df1d3d4a9315`, 678 검사 PASS·불일치0. 새 Python/Numpy 벡터 계산으로 10 tag의 V2/V2s(W-1)/V2q/nearest 차이를 전수 재계산했고 제품 비교 함수는 호출하지 않았다. 수치 상세·명령은 script/JSON과 `logs/gates/lap1233-middle-audit.log`에 보존.

- 정본2612 EXE SHA `6562797d95ddb2013931ffb23ec10bf3fcac631af5f82efdd06a56ef95ce42e7`, HQ2002 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 MATCH. save006은 non-synthetic·8 player records·559 units; G2 활성8인 부하 증명이 아니다.
- 세 bridge의 현재 source65개·복사본65개/회 모두 MATCH(빌더의 _imeGetTime·Makefile 삽입을 그대로 재적용), bridge C 원본/복사 SHA MATCH. 후보 DLL SHA: pair01 `7081f6753e07851a61c5effd21bc2b3186863ea0bca451c7913cc1df40fd0e87`, pair02 `b8b3b823ce8524fe02d881d0d4bfc57f0ff5a39c93a77e91792928a5212afd69`, newgame `5a3f51f64d8c7d76088ec0831350990862ac39b991391426b70ab76fc7576cb4`. fresh rebuild/rollback SKIP(제품 수정 없음).
- 6 lane raw SHA·capture 원본/복사 SHA·후보 input SHA·result SHA MATCH. raw expected run ID만 존재, summary1/drop0/complete detach·flush, owned PID=request PID·match1·post true. owned prefix live process0, game만 삭제·manifest/output/prefix/trace 보존 확인.
- manifest 해석: 디스크 manifest는 runtime_env.prepare의 HQ2002 복사 시점 snapshot이며 1024x768 startup 설정도 남는다. tools/esl2610_runtime.py:63~70이 그 뒤 overlay+2612 EXE를 private 경로에 쓰고 g1_saved_scene_probe.py:4622가 교체 후 SHA를 기록한다. 따라서 manifest의 base SHA를 executed2612 SHA라 주장하지 않는다. actual private file은 정책대로 삭제되어 직접 재해시 불가, executed SHA는 교체 후 probe 기록·정본 SHA·current source chain에 근거한다. 과거 lap1217/1224와 같은 알려진 제한이며 새 raw 충돌 아님.
- 두 pair scene equal·input 7/7 PASS. 선택151/empty0/drag exact·capture binding/minimap gate byte-exact restore/생산 slot1199·건물58·unit31 및 새 slot 1개 완료를 직접 확인. V2 max excess 431, V2s unexplained max219, V2q max511로 모두 ≤2000, coverage/tag/validator 변경 없음.
- 후보 PS3: pair01 present776·stale 최대/합240·covered 최소476577·p95/max19/37ms; pair02 present795·stale0·covered 최소476584·p95/max9/19ms; newgame present1691·stale0·covered480000·p95/max17/40ms. p95는 np.percentile raw elapsed95 수치이며 호스트 부하 인과는 UNKNOWN.
- 새 게임 두 lane PS3 도달·RIGHT/DOWN/LEFT/UP 실제 좌표 변화 PASS; 후보1600×1200·Scale2x raw PASS. .kills/.idle 반환영역 호출0은 전투 fixture 부재이므로 INCONCLUSIVE 그대로.
- production 원본800×600/후보1600×1200 직접 열람: HUD/미니맵/생산 버튼·월드 배치/잘림 이상 없음. visual-verdict95/pass, 허용된 Scale2x texture·연속 캡처 시간 숫자 차이 공개. 정지 캡처로 클릭 순간 stale/Windows를 PASS하지 않는다. verdict는 공유 temp 및 .omx/state/lap1233/ralph-progress.json 보존.

## stale backlog 재개 및 판정 경계

pair01 candidate raw `seq1412`, PS3 0-based present ordinal66, 진입+3292ms의 stale240은 primitive_stale_pixels_total 증가240과 동일하다. `ts_ms253505832` present → 건물 클릭 WndProc `message513`, logical(450,195) `ts_ms253505872`(+40ms) → 다음 present `253505883` stale0. pair02/newgame은0. 근거 `stale-phase.json` 별도 보존. lap1222 §3의 “확인 pair에서 stale present가 다시 생기고 클릭 직전 위상” 조건을 충족하므로 backlog를 재개한다. 위치·writer는 trace에 없어 UNKNOWN; 동일 writer라고 확정하지 않는다. 고정 캡처·기존 render/input/close 게이트 PASS를 취소할 원시 불일치는 없으나 G1 최종 마감·출하 판정 근거로 충분하지 않다.

- 기술 판정: **관측/기계 지표 PASS(partial, captured evidence)**. H-TR2612 포괄 기술 수용·2612 사용자 시험판 요청은 **HOLD/승격 경계**. 사용자의 이번 “경계면 ESCALATE_SOL 후 종료”를 적용해 요청/스테이징/마일스톤 마감을 수행하지 않는다.
- TR-3 스테이징3파일은 lap1232에서 생성되지 않았다. run 폴더의 bridge DLL은 staging 묶음이 아니며 완료로 세지 않는다. 승격자가 runtime partial·단발 stale 취급을 판정한 뒤 work에 준비를 넘긴다. 2611 전달 사실/HOLD 및 기존 APPROVALS 미결 불변.
- 이전 ESCALATE_SOL은 `20261010_lap1233_preserved_lap1232_escalate_sol.txt`에 byte-exact 보존했다.

## 검증 가능한 work handoff

가설은 FEASIBLE: 확인 pair의 클릭 직전 primitive stale 위치를 기존 stale-mask/screen-watch로 측정한다. work 소유는 G1 하네스·회귀 테스트·공유 probe artifacts에 한정, 별도G2/원본/핀/validator 수정 금지. 첫 fresh private2612/save006 pair는 기존 같은 옵션에 `--stale-mask 55-90 --stale-mask-state 3`을 더해 위치를 얻는다. 위치가 있으면 기존 `--layer-drift --screen-watch --screen-watch-state 3`와 지원되는 `--drift-samples` 인자로 그 위치 writer를 확인한다(정확한 parser 제약을 확인하고 지정; 기존 game copy/prefix/display 격리). 같은 클릭 직전/next frame 및 primitive counter 증가를 입력 raw와 결합한다. 한 work 회차 또는60분/실패가설2회에서 FEASIBLE/NOT_FEASIBLE/BLOCKED 판정; 재현이 없으면 NOT_REPRODUCED로 공개하며 위치를 추측하지 않는다. 추적 가능한 하네스 결함은 수리→회귀→같은 실행 재측정, 제품 수리가 필요하면 주소·old bytes·원복 근거 후 work가 최소 수정한다. middle은 구현하지 않는다.

승격자는 먼저 이 관측·전체 Fast/fingerprint·안전을 확인하고 stale 위치 work와 TR-3 준비 순서를 결정한다. TR-3를 허용하면 첫 pair bridge DLL byte 그대로+ASCII .bat2개(정본2612 이름·기존 env4개·viaDxWnd 공개)·txt0·SHA/diff를 work가 준비하며 fresh middle 확인 뒤 root가 사용자 요청/전달을 맡는다. Windows/DxWnd/BGM·전투·24k/144k·G1 사용자 승인 미검증, 과거2611 수용 HOLD를 덮지 않는다.

## 검사·종료

선행 make doctor/lint/typecheck PASS(typecheck12); doctor optional runtime manifest 없음은 fresh runtime PASS 아님. full check는 위 기록/승격 handoff 고정 뒤1회 수행하여 STATUS에만 결과를 기록한다. 최종 checks/safety.py·context_limits.py·git diff --check 및 fingerprint 비교를 완료하고 pending 자기 장기 실행0으로 종료한다. 실패 시 원인·work 소유 handoff를 STATUS에 남기고 출하/마감하지 않는다. 이번 세션에는 게임 실행/커밋/원본 writes/배포가 없다.

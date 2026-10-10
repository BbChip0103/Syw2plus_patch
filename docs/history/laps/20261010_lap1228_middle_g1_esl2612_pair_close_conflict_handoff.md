# 2026-10-10 | lap 1228 | G1 — ESL 2612 pair 정상 종료 근거 충돌

- 역할: fresh Codex middle, 진단·계획·독립 확인. 현재 surface의 실제 resolved model ID/effort는 확인 불가하므로 launch 로그 확인 없이 추측하지 않는다. 게임/하네스/테스트 구현·provider 폴백 0.
- 가설: lap1227의 2612 save006 pair/new-game 기술 수용 전, EXE/fixture/DLL/source/raw/PNG/cleanup을 독립 재계산하면 기록과 일치한다. 성공식 = 입력/화면 수치 일치 + lane 소유권 확인 + 정상 종료·완전한 raw + 보호 원본 불변. 충돌이면 수용/시험판 준비를 보류하고 work 수리 범위를 명시한다.
- 입력: PROMPT ①~⑥, AGENTS, INBOX 최신 지시·APPROVALS, STATUS 전체, DESIGN 1~4절·MODEL_ROUTING, lap1227 기록/ESCALATE. STOP 없음, runner lap=1228(읽기만). 문서 사전 줄 수 STATUS60/INBOX216/APPROVALS34. `patch-validation` 스킬 적용. 별도 2612 G2/G6/G8/G9 보류와 G1 계속 계약을 구분한다.
- 변경: 이 lap 기록·이전 handoff byte-exact 보존·STATUS/INBOX·ESCALATE만 갱신. 검수 스크립트/JSON은 공유 temp `20261010_lap1228_middle_review/`. 기존 uncommitted·원본·raw·PNG·pin·golden 불변, commit/push/deploy/전달 0. 새 actual game run 0.

## 독립 확인 결과

- 정본 2612 EXE SHA256 `6562797d95ddb2013931ffb23ec10bf3fcac631af5f82efdd06a56ef95ce42e7`, 2,000,896 B MATCH. 2611 `d9d6bb3dca11c229dfb129547166ecdea7b777c0d2494a2baa38ce68635de21d` MATCH. `.idle` VA `0x1157000`, `.kills` VA `0x115B000`, virtual size 각 `0x1000` 비교; hotfix runtime 효과 수용 없음.
- HQ2002 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`·읽기 전용 real save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 MATCH. pair selected index7·synthetic false; 새 게임은 save006 로드가 아닌 PS9→7→5→3 시작 경로다(공통 fixture 메타데이터를 실제 로드로 해석하지 않는다). 새 게임의 실제 생성 개체 4개/owner0·1; G2 활성8인 부하 증거 아님.
- pair/newgame DLL SHA `60877e48d878c1a5fbc8b578101a1904cca7b3db30b418b119a38f33044c97d0` / `6fb2140bf53affbcfecfa717256c954930dc38983c8da4354ea897acb9c406b4` MATCH. 각 build manifest 원본 입력65개 current SHA 모두 MATCH. 독립 DLL rebuild/patch 생성·원복 SKIP(제품 변경 없는 middle 진단; 공식 EXE 패치 0).
- 4 lane trace·22 PNG·원본 캡처 경로 SHA/크기, 후보 input trace2개 MATCH. 실제 game 경로4개 없음, prefix/manifest 보존 확인. 기존 cleanup.ok는 namespace 정리 성공이며 정상 게임 종료/summary 증명과 다르다.
- pair 5 tag(V2·V2s raw/reference/unexplained·V2q) 독립 픽셀 전수 재계산 불일치0. unexplained = loaded24 / selection173 / drag177 / minimap227 / production197. production raw2814는 FAIL 공개 유지, 사용자 W-1 기준 unexplained197은 PASS. production 원본800×600/후보1600×1200 직접 열람: 구도/HUD/미니맵 비율·잘림 이상 보이지 않음. 입력효과7/7은 host 관측이며 이 회차 새 입력은 없음.
- pair 후보 PS3 794 present·stale최대0·covered최소476577·elapsed p95/max8/16ms, safety7개0. 새 게임 후보 PS3 1717 present·stale0·covered480000·p95/max8/18ms·safety0, 네 방향 camera 변화 대조와 동일. 성능 호스트 부하 귀속 UNKNOWN 유지.
- 새 게임 두 lane owned PID 재검산 PASS·trace_close PASS. 후보 summary1개, dropped0·detach/flush complete. `.kills`/`.idle` ret_range_diag 4개0 → INCONCLUSIVE(전투 없음), PASS로 승격하지 않는다.

## 실질 충돌과 원인

**lap1227 pair 기술 수용 HOLD.** 기존 JSON/기록은 변경하지 않는다.

1. 후보 `probe-result.json.trace_close.status=FAIL`, error=`RuntimeSafetyError: owned Win32 PID trace has a mismatched run_id`.
2. 후보 raw 전체 run_id=`unknown`, 최종 `summary`0개. `runtime_env._read_owned_win32_pid(raw, 'g1-saved-candidate')`를 새 세션에서 그대로 실행해 같은 실패를 재현했다. 새 게임 양 lane/저장장면 baseline은 소유권 재검산 PASS.
3. `tools/g1_saved_scene_probe.py:4684`의 `no_present_trace` 분기가 PRESENT_TRACE와 **TRACE_RUN_ID도 제거**한다. `direct_draw_trace.c:341`은 run ID를 trace opt-in과 독립적으로 읽고, 없으면 unknown으로 설정한다. `:6134` 종료 분기는 여전히 g1-saved-candidate를 요구하므로 정상 close가 거부된다. 이후 private child/prefix 정리가 실행돼 game_removed/cleanup.ok는 true지만 candidate summary는 없다.
4. `_pair_status`(`:6609`)는 trace_close/summary를 검사하지 않아 actual raw가 실패여도 **PASS를 재현**한다. Scale2x validator도 렌더 수치만 확인한다. 이는 게임 크래시/OOM 증거가 아니라 추적 가능한 하네스 소유권/집계 결함이다. 이전 기록의 “lane 시작/종료 정상”과 실질 충돌하므로 단순 오타 정정으로 마감하지 않는다.
5. manifest.json의 game.exe_sha256은 4개 모두 HQ2002 값이다. `esl2610_runtime.prepare`가 기본 manifest 저장 **후** private EXE/overlay를 교체하고 manifest 파일을 다시 쓰지 않는 구조(기존 lap1217에서 알려진 제한)다. lane 시작의 private_exe_sha256은 2612 MATCH이지만 이미 제거된 EXE를 지금 직접 재해시한 증거는 없다. “디스크 manifest의 2612 SHA MATCH”로 쓰지 않는다.

## work handoff — FEASIBLE, 추가 재계획 없이 수리·실행

- 소유 파일: `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`(필요하면 `tests/test_g1_new_game_path.py`). 공식 EXE/렌더 C/pin/golden/별도 세션 파일 변경 금지. middle은 구현하지 않는다.
- no-present-trace 상태에서 PRESENT_TRACE는 계속 꺼 두고, 안전한 close 소유권에 필요한 run ID만 보존한다. unknown run ID를 허용하도록 소유권 검증기를 느슨하게 만들지 않는다.
- 회귀 RED→GREEN: (a) user-trial 옵션에서도 trace opt-in 없이 run ID 유지, (b) trace_close FAIL·summary 누락이면 aggregate PASS 불가, (c) 정상 완료 pair·new-game은 통과. 증거가 없는 일반 lane까지 임의 PASS로 처리하지 않는다. 필요 시 manifest의 준비 시점 SHA와 실제 실행 SHA를 별도 기록하는 최소 하네스 보강; 과거 manifest/raw 수정 금지.
- **동일2612/save006·동일옵션 `--hd-source scale2x --esl2610 --candidate-no-present-trace --candidate-no-unit-ticks`로 fresh pair 재실행**. 정확한 원본SHA 확인→새 전체 game/prefix/빈 display→현재 raw의 run ID·PID binding→owned close PASS·summary1/drop0/flush complete→7/7 입력·5 tag·V1/V2/W-1/V2q·Scale2x 유지→game만 제거, prefix/manifest/output 보존. 실패가 추적 가능한 결함이면 수리 후 재실행(PROMPT③); 이번 middle에서 억지로 게임 수리/재실행하지 않는다.
- 다음 fresh middle이 repaired-source fingerprint의 Fast와 actual fresh pair를 독립 확인한다. 그 전 2612 trial 스테이징/재전달·G1 마일스톤 수용0. 새 게임 관측 부분 확인은 보존하지만 전체2612 기술 수용은 HOLD.

## 명령 / 장부 / 검사

- `make doctor` PASS(원본SHA verified); default runtime manifest 없음은 actual 실행 PASS가 아님.
- `make lint` PASS(`logs/gates/lap1228-middle-lint.log`), `make typecheck` PASS12(`lap1228-middle-typecheck.log`).
- `PYTHONPATH=. .venv/bin/python ../temp/Syw2plus_patch/20261010_lap1228_middle_review/review.py`: completed, render census mismatch0, ownership replay1FAIL/3PASS. exit0은 검수 완료만 뜻하며 기술 수용은 HOLD. 결과 `review-result.json` SHA256 `7c42669c1c14c4c3dbf3589584257a42d7bdf413b85d7e76850c8745a6215be0`.
- 검수 입력 pair JSON SHA `e8ecd25e0767b56a1c85bd5d39dfd1e6ebe0631fbb78e3d384acecfdce85275f`, new-game JSON `6e4eada546b2649ffc69b7a76b9c33ac7381463105da778c27951000072f1de8` MATCH. 후보 trace SHA pair `bef2938d4b7f4fafeb7b86cd6bd60c0e29c77fad588913e2eca8f0db7a0b3312` / new-game `2a84e09e14306c0342e20bb3337712bbd4d885404592e813cd4bd608289d6f80` MATCH.
- 이 기록·handoff·ESCALATE를 먼저 고정한 뒤 `make check`1회, safety/context/diff 검사를 수행하고 **결과·수치는 STATUS 및 ignored gate log에만 보강**한다. 전체 Fast GREEN도 위 actual pair의 정상 종료 실패를 승인으로 바꾸지 않는다.
- 승격: 이번 사용자 규칙의 “과거 기록과 raw 실질 충돌” 및 trial/마일스톤 경계. `loop/ESCALATE_SOL` 보존. 원문 lap1227 ESCALATE는 `20261010_lap1228_preserved_lap1227_escalate_sol.txt`에 byte-exact 보존. 현재 다음 행동의 단일 큐는 STATUS만 따른다.

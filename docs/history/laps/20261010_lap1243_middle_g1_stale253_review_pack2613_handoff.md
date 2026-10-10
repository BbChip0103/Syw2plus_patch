# 2026-10-10 | lap1243 | G1 middle — stale253 미재현 독립 확인·실제 제품 probe handoff

- 실제 provider/model/effort / 지정 역할: Codex App, middle tier(진단·계획·확인). 표면에서 resolved launch ID/effort 미노출, 추측·모델 변경 주장 없음. 게임/하네스/테스트 구현 및 fresh 게임 실행 0.
- 읽기 순서: PROMPT ①~⑥ → AGENTS/최신 INBOX/APPROVALS → STATUS 전체 → DESIGN 1~4/MODEL_ROUTING → lap1242/lap1241 근거. STOP 없음, counter1243 읽기만. 최신 DESIGN/INBOX의 G2 상한5000·G4 종결이 PROMPT의 과거10000/G4 활성 문구에 우선한다. 별도2613 두 EXE/멀티 goal·파일 비접촉.
- 이번 한 가지: lap1242 layer-only 0/2 미재현을 raw로 독립 판정한다. 성공 측정식=2 pair SHA/4 lane trace·소유 close·summary·mask header와 실제 pixel-count 일치; 실패=실질 raw 충돌. 마감/다음 마일스톤 전환 없음.
- 변경 파일: STATUS, 이 기록, 이전 ESCALATE 원문 보존 파일, 새 ESCALATE_SOL. 공유 temp 검수 스크립트/JSON만 추가. 제품·pin·golden·원본·기존raw 수정0, 커밋0.
- 이전 handoff byte-exact SHA256 `b9e0a97eab12be89b79733d469648be6b644b73411ed14806ebbadcd5e52b5da` → `docs/history/laps/20261010_lap1243_preserved_lap1242_escalate_sol.txt`. 삭제·재해석 없이 전문 보존 후 새 handoff 작성.
- 원본 SHA: 공식2613 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724` 직접 MATCH. fixture save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; synthetic=false·8 records/559 units, 활성8인 전비 부하 증거 아님. 후보 DLL direct SHA first `0c869ff9f525e77b023ed8ce5219569e609cf9f1bd5857284d7b2bc61d9579bc`, retry `84d4b97f2d7847fd2cb1b4a49d825f1da1098e8b5cb135ba3c22bb06e6b57bc2`(재빌드 byte 동등성 판정은 이번 범위 아님).
- 실행 명령: `.venv/bin/python ../temp/Syw2plus_patch/20261010_lap1243_middle_review/review.py`.
- 결과: **123 checks PASS, failures0**. 2 pair SHA MATCH, scene equal/pair PASS, 4 lane raw trace SHA·pre-close prefix SHA·post-close full SHA MATCH, 소유PID/close request/summary PID 일치·summary1·drop0·detach/flush complete. 2 후보 mask 각각36개(ord55~90·PS3), header covered/stale와 480000-byte pixel map 재계산 일치·stale 합0/72. layer/input SHA MATCH. 실행 전후 host/test/build-manifest SHA 일치, host/test current SHA MATCH. 4 owned game 사본 제거·prefix/manifest retained 확인.
- 독립 JSON: 공유 `temp/Syw2plus_patch/20261010_lap1243_middle_review/review.json`, SHA256 `3c117dac59113feb9562b571541bdeae087ef123cb3912475b800baebdd6f8ff`.
- 첫 audit의 close SHA4건 FAIL은 검수 스크립트가 종료 전 trace digest를 종료 후 파일 전체와 비교한 오류. `tools/win32_close_transport.py:21` 및 probe의 close-before-wait 순서를 읽고, raw 앞 event_count개 줄의 SHA가 기록과 정확히 일치함을 확인한 뒤 temp audit만 수정·재실행. 제품 결함/역사 raw 충돌 아님. 3회 미설명 실패 조건 해당 없음.
- 판정: **lap1242 bounded NOT_REPRODUCED 0/2 수용(기술 관측만)**. lap1240 stale253은 유효하며 수정 근거/같은-present writer는 UNKNOWN. 현재 repair branch BLOCKED. 동일 layer/watch 재시도는 더 배정하지 않는다. 실제 stale present 재현 또는 사용자 구체 재현 입력이 생길 때만 그 event를 이어서 귀속한다. 미재현을 해결/회귀PASS로 바꾸지 않는다.

## Work tier handoff — H-PACK2613 (FEASIBLE, 같은 G1 안의 실제 제품 확인)

다음 한 가지는 STATUS만 현행 큐다. 여기에는 수행 절차/판정 계약을 보존한다. 사용자2613 시험 결과/업스케일 출력이 새로 오면 우선한다.

가설: 기존 검증된 full stand-in HD 팩은 공식2613(2612 15-file bundle overlay)에서도 기존 G1 HD 키 조회·합성·입력 경로를 실제로 실행한다. lap1202는 HQ2002 증거여서 2613 PASS로 재사용하지 않는다. 팩은 화질 이득 없는 stand-in이며 사용자 업스케일 완료/마일스톤 증명이 아니다.

소유권: 다음 work(luna/high)가 actual probe와 이번 회차 소유 local runtime/shared temp/logs만 담당한다. 첫 작업은 구현/카드 추가 없이 기존 probe 실행이다. 재현된 하네스/좌표 결함이면 work가 해당 도구·관련 테스트를 최소 수리→관련 회귀→재실행하며 원본/pin/gate/별도G2 파일은 수정하지 않는다.

입력은 현존 `../temp/Syw2plus_patch/20261009_lap1202_work_hda0/pack_all/`와 기존 save006. pack 디렉터리·manifest 존재를 확인했고 새 팩 생성/전수 장부 보강은 하지 않는다. 원본·공유 팩 읽기전용, `SYW2_G1_HD_PACK`에는 pack_all의 절대경로를 준다. 실행 때 후보DLL SHA·EXE/saveSHA와 실제 키/팩 counters를 기록한다.

1. pack 켬 save006 full pair 실행:
   `SYW2_G1_HD_PACK=/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261009_lap1202_work_hda0/pack_all PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lapNEXT_pack2613_pair --artifact-root ../temp/Syw2plus_patch/YYYYMMDD_lapNEXT_pack2613_pair --hd-source scale2x --esl2613 --candidate-no-present-trace --candidate-no-unit-ticks`
2. pair 정상 완료 뒤 같은 팩으로 기존 new-game/실제 입력·4방향 스크롤·60초 dwell 실행: 위 명령의 독립 runtime/artifact 경로를 `_ng5`로 바꾸고 `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-dwell 60` 추가. 새 게임은 무작위 fixture라 원본/후보 동일전투 비교로 세지 않는다.
3. 종료 조건: 두 run 기존 pair/new-game gate·owned close·summary1/drop0/flush·자기소유 cleanup 충족, 팩 hit>0 실제 관측, 안전/자기검사/팩 reject 공개(새 거부는 원인 추적), 실제 입력/캡처 이상 유무 판정 후 결과를 남긴다. stale가 생기면 같은-present 위치/입력 관계를 보존하며 수정은 근거가 있을 때만 한다. 팩 hit0이면 NOT_FEASIBLE/BLOCKED 원인을 구분하며 팩 켬 성공으로 보고하지 않는다. 기존 UNKNOWN/BLOCKED 진단을 새 PASS로 바꾸지 않는다.
4. 코드 변경0이면 최소 문서·안전 확인과 actual run으로 끝낸다. 새 소스 수리가 필요하면 관련 테스트를 먼저 실행하고 통합 후보의 필요한 경계에서만 lint/typecheck/fullFast·fresh 검수를 한다. 두 개의 초기 제품 probe는 고장 수리/재실행을 막는 '정확히1회' 예산이 아니다. 장기명령은 이 work가 끝까지 기다린다.
5. 새 prefix/빈 display/전체 게임 사본 사용, 여유20GB 확인, 종료 후 소유 game만 삭제·prefix/manifest/output/raw 보존. 새 PNG는 공유 captures/의 YYYYMMDD_HHMMSS 접두사 규칙. commit/deploy/전달/승인 없음.

- 미검증: 이번 fresh 게임0·현재 전체Fast0; Windows/DxWnd/BGM·실전투/.kills·24k/144k·멀티·사용자 G1 승인은 그대로 미확인. full-test-latest의 역사 exit0/source 불일치를 현재 PASS로 재사용하지 않는다.
- 승격 handoff: stale253 수리 근거 불명확을 보존한 `loop/ESCALATE_SOL`. 승격자는 독립 bounded 결과와 repair 보류를 확인하고, 같은 G1의 H-PACK2613 actual probe를 work tier에 넘긴다. 추가 문서/전수검수 회차로 제품 시험을 지연하지 않는다.
- 최종 문서/안전 검사는 아래에 보강한다.

- 최종 검증: `python3 checks/safety.py check --require-game` SAFETY_PASS, `python3 checks/context_limits.py` CONTEXT_PASS, `git diff --check` exit0. STATUS97/INBOX262/APPROVALS36으로 PROMPT 한도 충족·Blockers 정확히1. 문서-only이므로 전체Fast/lint/typecheck/fresh 게임 SKIP; 실행 준비/기계 검사를 실제 게임·마일스톤 PASS로 세지 않음. 자기 장기 프로세스0(시작하지 않음), counter1243 읽기만.

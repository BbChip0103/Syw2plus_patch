# 2026-10-10 | lap1245 | G1 middle — H-PACK2613 샘플링 진단·work 인계

- 역할/provider/model: Codex App middle(진단·계획·확인). 계약 middle=sol/high; 실제 resolved launch ID/effort는 표면에서 미노출, 추측하지 않는다. 읽기 전용 하네스 lookup에 native explore `gpt-6-luna`/high를 명시 배정했다. 게임/하네스/테스트 구현0·fresh 게임0·커밋0.
- 지시 순서: PROMPT ①~⑥ → AGENTS/최신 INBOX/APPROVALS → STATUS 전체 → DESIGN1~4/MODEL_ROUTING → lap1244/lap1234/lap1243. counter1245 읽기만·STOP 없음. 최신 DESIGN/INBOX의 G2상한5000·G4종결이 PROMPT 과거문구에 우선한다. 별도2613 두 EXE 싱글 goal/파일 비접촉.
- 이번 한 가지/가설: 초기 scene mismatch가 지속 유닛 손실인지 서로 다른 simulation tick의 읽기인지 독립 판정. 성공 측정식=4pair/8lane raw SHA·초기/후속 roster 직접 대조; 제품 pair 수용이나 G1마감과 구분.
- 변경파일(uncommitted): STATUS·이 기록·이전 ESCALATE 보존파일·새 ESCALATE_SOL. 공유 temp 독립 스크립트/JSON만 추가. 제품소스·원본/reference/기존raw/팩/fixture/pin/golden 변경0.
- 이전 ESCALATE 전문 byte-exact 보존: `docs/history/laps/20261010_lap1245_preserved_lap1244_escalate_sol.txt`, SHA256 `3d56ea4392752b3830e14470127d56021a75e0e5c23d67bfe96c860e38d761b5`.
- 입력: official2613 SHA256 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`·비합성save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 MATCH. 8player records는 활성8인 부하 증거 아님. 기존 private full-copy/prefix/display 실행의 관측이며 이번 새실행0.
- 명령: `make doctor`; `.venv/bin/python ../temp/Syw2plus_patch/20261010_lap1245_middle_review/review.py`. doctor PASS(tooling/original; optional default manifest 없음은 runtime PASS 아님). 독립 **134checks PASS·불일치0**: 4pair SHA·8lane trace/raw/owned close PID·prefixSHA/summary1/drop0/flush/detach·cleanup·prefix/manifest보존·inputSHA·EXE/save pin·현재host/test MATCH. 64bridge C/H/Makefile이 4run 간 byte동일. pack hit880/838·reject0.
- JSON: 공유 `temp/Syw2plus_patch/20261010_lap1245_middle_review/review.json`, SHA256 `f41cd21c3b235da7ecb9c351ba2a63668aa05299e8fbee86376ee2349b1ae094`. 후보DLL SHA·상세수치도 기록. 역사full-test-latest의 source불일치는 현재 전체Fast PASS로 재사용하지 않는다.

## 독립 관측·원인

| 실행 | lane | 경량 load tick/count3 | 상세scene tick/총수 | production.before tick/총수 |
|---|---|---|---|---|
| lap1234 무팩 pair01 | baseline | 24571/96 | 24574/559 | 24649/564 |
| lap1234 무팩 pair01 | candidate | 24570/95 | 24573/559 | 24661/564 |
| lap1234 무팩 pair02 | baseline | 24570/95 | 24573/559 | 24646/564 |
| lap1234 무팩 pair02 | candidate | 24571/96 | 24574/559 | 24658/564 |
| lap1244 팩 first | baseline | 24571/96 | 24574/559 | 24647/564 |
| lap1244 팩 first | candidate | 24568/95 | 24569/558 | 24667/564 |
| lap1244 팩 retry | baseline | 24571/96 | 24574/559 | 24647/564 |
| lap1244 팩 retry | candidate | 24567/95 | 24569/558 | 24669/564 |

초기 상세 차이는 두 팩pair 모두 slot39 `(39,64,3,720935)` 하나뿐. 그러나 **같은 두 후보 raw의 `actions[tag=production].before.units`에는 바로 그 identity가 있고 양lane의564개 identity 전체가 동일**하다. lap1244의 'final scene559vs558'은 마지막 게임상태가 아니라 `scene`에 저장된 최초 상세읽기로 해석을 정정한다(과거원문/raw/HOLD 불변). 지속 유닛 누락은 관측에서 입증되지 않았다.

`tools/g1_saved_scene_probe.py:4943~4952`는 PS3·tick>0 뒤 wall-clock150ms→상세 순차읽기. `:4085~4096`의 `_scene_identity`는 roster를 비교하지만 tick은 제외하고 `:7462~7471`에서 직접 동등 비교한다. `patches/population/runtime_driver.py:290~357`의 상세읽기도 tick을 bracket하지 않는다. **재현된 하네스 결함=서로 다른 sim 시점의 상태에 동일 scene을 요구함**(confidence high). 무팩 과거 실행도 경량count95→나중상세active96이다.

**추론(medium):** 팩 초기 적재/표시 비용으로150ms동안 진행한 tick이 줄어 slot39 생성/복원 전 상태를 읽었을 가능성이 높다. 정확 생성/복원 함수·발생tick·동일update-return phase 및 pack 인과는 미측정. 후속identity 동등은 완전한 로직 비회귀나 초기pair PASS가 아니다. 데이터overlay/메모리손상 귀속 근거없음. stale253은 별도UNKNOWN 유지.

## Work tier 최소수리·실제시험 복귀 계약 — FEASIBLE

소유권: 다음work(luna/high)의 초기 sampler `tools/g1_saved_scene_probe.py`·관련 `tests/test_g1_saved_scene_probe.py`·자기runtime/temp/logs만. 게임C/EXE·pin/gate·원본/팩/fixture·별도G2 수정금지. 추가계획/카드/문서검수 회차 없이 최소수리→실제probe로 복귀한다.

1. 기존 `_wait_for_exact_tick`(:556)·`_read_batched_scene`(:623)를 우선 재사용. save006 두lane의 사용자 입력 전 **공통target sim tick24600**의 PS3/coherent 상세상태로 `scene.state`를 만든다. 이 tick은 관측로드24567~24571 뒤·첫생산24646~24669 앞이다. 경량 `load_fixture.to`는 별도 진단으로 유지하고 상세 roster의 before/after tick·target을 기록한다. snapshot tick과 roster를 서로 다른 읽기로 묶지 않는다. 다른fixture/기존옵트인 경로 계약은 보존한다.
2. target miss/timeout/tick-cross는 INVALID/HOLD, 실제전체identity차이는 HOLD. slot39 나타남을 기다리는 조건·누락필터·count맞춤·tick오차허용·scene gate삭제 금지. stable tick은 update-return phase 증거가 아니라는 기존한계 유지. 동일tick/coherent라도 다르면 그 실제차이를 보존해 기존관련probe로 좁힌다.
3. 최소 sampler 회귀 RED→GREEN: 서로다른tick558/559는 비교승인 불가, 동일target/동일전체identity는 PASS, 같은target 실제1유닛차이는 HOLD, miss/incoherent는 INVALID. 읽기순서/결과 검증, 구현문자열만 검사하지 않는다.
4. 기존 lap1243 H-PACK명령(official2613/save006·읽기전용 full stand-in 팩)으로 fresh pair 실행. 초기진단·공통tick상태·후속slot39/전체identity·입력7/7·기존render/owned close/summary/cleanup 공개. PASS면 **같은work회차**에 lap1243 새게임/실제입력/4방향scroll/60초dwell 즉시 이어간다. 추적가능 sampler/좌표 결함은 최소수리→관련회귀→재실행. 불명확한 제품차이는 원인·최소다음행동 공개. 장기실행 끝까지 대기.
5. 소스수리 후 통합후보 경계에서 lint/typecheck→전체Fast 한 번 완주·fresh middle로 인계. 작은수리마다 전체체인 반복금지. 보조작업연속2회/60분 상한 기존누적 유지. 여유20GB·새전체게임/prefix/빈display·자기game만cleanup·raw/prefix/manifest보존. 사용자전달/마일스톤승인/commit/deploy0.

- 판정: sampling 결함진단 PASS·최소수리 FEASIBLE, **lap1244 pair수용 HOLD 유지**. 모델의 진단/계획이지 제품완료·사용자승인 아님.
- 미검증: 새공통tick 수리/실행·팩새게임/scroll/dwell·현재전체Fast·Windows/DxWnd/BGM·실전투·장시간·사용자G1승인. 별도EXE 싱글goal의 멀티중단 유지.
- 다음행동: STATUS와 새ESCALATE_SOL의 work 최소수리·실제시험 복귀. middle이 구현을 대신하지 않는다. 문서-only이므로 전체Fast/lint/typecheck/새게임 SKIP; 종료문서/안전검사 아래보강.

- 종료 검증: `python3 checks/safety.py check --require-game` SAFETY_PASS·`python3 checks/context_limits.py` CONTEXT_PASS·`git diff --check` exit0. STATUS101/INBOX265/APPROVALS36·Blockers 정확히1·counter1245 읽기만. 이번 자기 장기프로세스0(게임/빌드/전체Fast 시작하지 않음); native lookup 완료. 기존 미커밋 변경/원본/raw/이전handoff 보존·ESCALATE_SOL 유지. role 경계상 work 구현/실제시험은 인계하고 종료, 사용자승인/제품PASS/새마일스톤전환0.

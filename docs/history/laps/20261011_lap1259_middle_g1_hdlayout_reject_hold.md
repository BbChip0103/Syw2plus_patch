# 2026-10-11 | lap1259 | G1 H-HDLAYOUT 독립 확인 — HOLD

- 지정 역할: middle(진단·계획·확인). Codex App 새 세션; actual resolved model/effort는 노출되지 않아 추측하지 않음. HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`. counter1259 읽기만, 게임/하네스 구현·실제 게임 재실행·전달·커밋0.
- 목표/가설: lap1258의 `.hd` 자동탐색 결과와 새 게임 reject1/retry0를 독립 대조한다. 최초 reject가 해소되거나 설명되지 않으면 전체 기술 수용 HOLD로 종료한다. G1 마일스톤/다음 변형 EXE 큐로 넘기지 않는다.
- 읽기 순서: PROMPT → AGENTS/INBOX 최신 지시·APPROVALS → STATUS 전체 → DESIGN1~4/MODEL_ROUTING → lap1258 work/raw/source. PROMPT의 과거 G2 10000·G4 활성·Claude 고정 문구 대신 최신 DESIGN/INBOX/MODEL_ROUTING 계약을 따른다. STOP 없음; 기존 ESCALATE_SOL은 이번 독립 확인 요청이었다.
- 변경파일: 이 기록, `docs/STATUS.md`, `docs/history/laps/20261011_lap1259_preserved_lap1258_escalate_sol.md`, ignored `loop/ESCALATE_SOL`. 이전 제품 소스/테스트의 uncommitted 변경은 그대로 보존한다. 새 evidence/script는 공유 temp에만 둔다.

## 독립 재계산

실행 명령: `python3 /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261011_lap1259_middle_review/recalculate.py`.
산출물 `evidence.json` SHA256 `f415e14ce599b9125ad0d955075bbd7ba5d5a02a41b6f6468c1e4e8b63a60c1f`.
스크립트는 기존 raw/색인/build input을 읽어 요약하며 게임을 시작하거나 기존 결과를 수정하지 않는다. 실행 exit0과 별개로 판정은 **HOLD**다.

| 실행 | candidate presents / PS3 | hit / reject 최대 | trace SHA256 |
| --- | --- | --- | --- |
| save006 pair | 1093 / 831 | 917 / 0 | `824753eb6f5cb2eddf072b56f64c74347554bc1cc9bcdb0fdaecf1b53f4f3a51` |
| 새 게임 run1 | 2372 / 1471 | 354 / 1 | `94aafab389a6c10da318b34bc2c1d69832b3d76370d959e64bd0b15522f08264` |
| 새 게임 진단 run2 | 2361 / 1471 | 373 / 0 | `0206cf04a50175969d6a3282e6fe7369c06660851472a5e32d3704ac73130719` |

- result SHA도 이전 기록과 MATCH: pair `7f8772a0ea6d0ce044a8f808b080f1bdd243b1cab879e6dc59f2bf319dc82eb1`; run1 `03dad80c75610dfc202d10fe6a74e6795863a5cb28835e3aaa3af97eda2e6a5a`; run2 `b49903fbd45a10c209e40faf4fbe07f62dbb4bf1c8cd986df1c99003a10258a2`.
- run1의 마지막 PS5 present seq1710/tick334463375에서 reject0. 첫 PS3 present seq1727/tick334463767부터 reject1이며 마지막 seq3456에도1이다. 이것은 한 present 뒤 사라진 stale와 다른 **누적 key 거부**다. 최초 key 시점은 두 present 사이로만 한정할 수 있다.
- 세 trace의 stale/fallback·`_PLAY_SAFETY_FIELDS` 7개 최대0. close PASS, summary1/drop0, source_unchanged true, owned cleanup PASS. 세 candidate game 사본은 현재도 없다. 이는 기록된 실행 범위의 확인이며 Windows/장기/멀티 PASS가 아니다.
- run1 dwell1198·run2 dwell1197 presents, HD100%. run1 dwell의 reject 증가량0은 시작 전에 발생한 reject1을 부정하지 않는다.
- run1 key log 없음. run2 `prefix/drive_c/g1_hd_key_log.jsonl` 5325줄·`result=reject`0. run1의 대상 digest·writer·파일·거부 이유를 사후 복원할 근거는 부족하다.
- 설정은 같지만 camera_after_dwell이 run1 `[91,54]`, run2 `[8,47]`로 다르다. 입력 설정 동일을 실제 장면 동일로 확대하지 않는다. 장면 차이가 reject의 원인이라는 주장도 하지 않는다.

## 소스/배치 확인과 판정 근거

- 세 bridge마다 `original_stub_inputs`65개를 현재 소스와 직접 SHA 비교: mismatch0. 각 실제 DLL도 build record SHA와 MATCH: pair `affc543bd1dd435583d7e32341d7a958277f2d4a9946609b36c113ab993c69c6`, run1 `db5e0e759d185ddd2caad56f24c500234c561b660dd1a8b7c5becc3a7461a860`, run2 `47df2e086f5dd8a5cf9422a14865f95b46b702ba83719112073185c1b85544f0`.
- converter/probe/asset.c/.h/trace.c SHA는 lap1258 기록의 5개와 MATCH(전체 값은 evidence.json). DLL 코드 재구현/새 빌드 없이 현재 실행 대상 소스와 연결했다. 현재 저장소 전체 Fast fingerprint를 새로 입증한 것은 아니다.
- 원본 보호 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 실제 candidate 공식2613 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724` over2612 데이터. private lane/prefix/display, 출력1600×1200, scale2x+실제 업스케일 그림 sidecar. save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`(pair load fixture); 새 게임에서 save fixture 파일 존재를 활성8인/부하 증거로 세지 않는다.
- converter는 `<asset>.hd/NNNN.idx8` 및 compact `index.json`을 새 출력에 만든다(`tools/g1_hd_convert.py:686`). DLL은 EXE 디렉터리부터 `.hd`를 탐색하고, digest/pal8 hash map·extended prefix로 선택한다(`tools/inmm_stub/g1_hd_asset.c:327`, `:390`, `:416`). 실제 hit와 중복수는 이 경로의 실행 증거다. 모든 미실행 fallback/Windows 조합을 승인하지 않는다.
- 배치 재계산: idx8 39155개 **1,060,085,276 B**, index JSON782개 **3,320,210 B**, 합39937파일 **1,063,405,486 B**. 25619 unique keys·duplicates13536, 색인이 가리키는 누락파일0. lap1258의 1,060,085,276 B는 idx8 payload 수치이므로 총 용량과 구분해 현행 기록만 명확히 한다(과거 raw 변경0).
- 집계 PASS의 범위를 소스로 설명할 수 있다: `_summarize_play_presents`(`tools/g1_saved_scene_probe.py:2796`)는 window 내 reject를 last-first로 기록하고 clean 조건에서 절대 reject 최대를 검사하지 않는다. 새 게임 aggregate(`:7451`)도 이 play status/scale2x 결과를 사용한다. 따라서 이번 aggregate PASS는 **요청된 전구간 reject0의 증명 범위가 부족하다**. raw의 실제 거부 원인이 설명됐다는 뜻이 아니다.
- `read_pack_frame`(`tools/inmm_stub/g1_hd_asset.c:1392`)의 REJECT 후보는 identity 크기/key 불일치, 파일 크기·읽기 실패, silhouette 검증 실패다. 현재 raw에는 이 분기를 식별할 key가 없다. 중복 선택/팔레트/장면/파일 손상 중 하나를 원인으로 단정하지 않는다.
- legacy nearest mirror validator BLOCKED(HD 디테일로 nearest와 다름)와 scale2x validator PASS는 raw에 보존한다. 이 회차는 그 도구를 새 승인 조건으로 추가하거나 수리하지 않는다.

## 검증 / 종료 / work handoff

- 이전 full Fast log SHA `56433ccf41923f2e866291ed6311e4475f611d467de4a0f81895fc768fb80767` 직접 MATCH, exit파일0·로그2194 passed/9 skipped/835.57s·lint/typecheck/context PASS 확인. 오래된 `full-test-latest.result`를 현행 PASS로 재사용하지 않는다. 이번 변경은 문서/근거뿐이므로 전체 Fast/fresh 게임 SKIP(PROMPT 문서 예외·검증 과잉 방지). final 문서/안전 검사는 아래에 기록한다.
- 판정: sidecar 경로 실행·pair raw·현재 source 연결은 국소 확인. **H-HDLAYOUT 전체 기술 수용 HOLD, reject 원인 UNKNOWN**. 첫 실행을 PASS로 재작성하거나 run2로 덮지 않는다. 사용자 승격 규칙(실질 raw/수용범위 충돌)에 따라 `loop/ESCALATE_SOL`을 작성하고 종료한다. STOP/마일스톤승인/변형 EXE 진행0.
- 승격자가 이어서 확인할 것: 전구간 reject0 미충족의 처리와 아래 최소 실제 probe를 work에 인계할지 판정한다. `.hd` 시험판 전달은 별도 사용자 확인 경계이므로 middle이 전달하지 않는다. H-G1VARIANT2613 순서는 이 판정 이후로 보존한다.
- work handoff(**FEASIBLE**, 재계획 금지): 기존 `--candidate-hd-layout .../sibling_tree_v3 --hd-source scale2x --new-game-path --new-game-start --new-game-play --new-game-play-keys none --new-game-play-dwell 60` 및 기존 공식2613/2612 구성으로 fresh private 게임에서 시작~PS3~dwell을 기록한다. `SYW2_G1_HD_PACK`은 없이, 기존 `SYW2_G1_HD_KEY_LOG`를 **게임 시작 전부터** private prefix의 새 로그로 설정한다. camera/장면을 함께 기록하고 달라지면 조건 차이를 공개한다. 제품 코드 수정 없는 최초 추가 진단1run으로 한정, 미재현이면 UNKNOWN 보존·반복검색 종료; 추적 가능한 결함이 확인되면 PROMPT③에 따라 최소 수리→관련 회귀→실제 재실행을 계속한다.
- 재현되면 `result=reject`의 writer/digest/pal/w/h/src·silhouette 진단을 해당 sidecar 색인/idx8과 대조해 원인을 특정한다. 기존 key log로 구분이 안 될 때만 work가 해당 실패 분기에 경로·expected/actual bytes·reason을 최소 계측한다. 전체 감독기/보관 도구/전수검사를 새로 만들지 않는다. 실행 전체 candidate present의 reject **절대 최대값**을 별도로 판정하고 window delta/exit0만으로 승인하지 않는다. 이 회차의 수정 ownership은 문서뿐이며 게임 코드 수정은 후속 work tier 책임이다.
- 기존 ESCALATE 원문 SHA `68006127f7c43aad0f9fbd379ce66dc9376008dd783752731101d09f91b84b9f`를 `20261011_lap1259_preserved_lap1258_escalate_sol.md`에 byte-exact 보존했다. 원본/raw/prefix/output/핀/golden·별도 세션 산출물 비접촉, 게임/코드 수정0.
- final fresh 검사: `.venv/bin/python checks/context_limits.py` → CONTEXT_PASS, `.venv/bin/python checks/safety.py check --require-game` → SAFETY_PASS, `git diff --check` → exit0. evidence 재검증으로 raw전구간 safety7/stale/fallback0·reject run1=1/run2=0 및 source/DLL 연결 확인. `runtime_env._prefix_pids` 읽기 결과 세candidate prefix PID0, game사본없음. STATUS53/INBOX314/APPROVALS52줄로 각PROMPT한도이내. counter1259불변·STOP없음. 검사PASS가 제품HOLD를 바꾸지 않는다.

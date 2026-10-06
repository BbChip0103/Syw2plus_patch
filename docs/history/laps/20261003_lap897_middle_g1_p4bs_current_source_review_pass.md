# 2026-10-03 | lap897 | G1 P4b-S middle — current-source B' 독립 수용 PASS(partial)

- 역할: 사용자 지정 middle(진단·계획·확인), 새 독립 Codex API 세션. API가 실제 model ID/effort/CLI argv를 제공하지 않아 Sol/high/Fast 실행 인증을 주장하지 않는다. 이전 work 모델 인증도 lap896 기록의 한계대로 유지한다. 제품/하네스/validator 구현 변경0, 새 게임/build0, subagent0, 유료 CLI0, commit0. counter897 읽기만.
- 목표/가설/측정식: STATUS의 다음 한 가지인 lap896 current-source pair1/2 독립 검수. lap892 middle 목록으로 한정하여 wrapper ABI·old bytes·rollback·6범위·공통 decoder·비교 필드, build/raw/source, E2~E4, lap863 B'-1~6, source unchanged/cleanup을 확인한다. 같은 source에서 fresh 연속2 pair가 조건을 만족하면 B' 기술 수용; G1 마일스톤 판정은 별개다.
- 입력: PROMPT ①~⑥, AGENTS, 최신 INBOX/APPROVALS, STATUS 전체, DESIGN 1~4 및 최신 G1 범위, MODEL_ROUTING 최신 사용자 override, lap892/863/858 카드, 주소 문서, lap895/896 기록. STOP/ESCALATE_SOL/FULL_TEST 부재. 기존 dirty tree 보존.
- 변경 파일: 이 기록, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`; 공유 temp read-only 재계산 script/JSON/disassembly만 추가. APPROVALS 기록 전247줄→250줄, STATUS 소프트130 이내, Blockers 정확히1개. source/test/원본/save/기존raw/golden/안전핀 변경0. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance이며 검증 근거 자체가 아니다.

## 결과와 원본/후보 identity

**`PASS_BPRIME_CURRENT_SOURCE_INDEPENDENT` / B' `PASS(partial)` / G1 HOLD.** lap895의 source 불일치는 두 current-source fresh pair로 해소됐다. 새 source와 기존 raw 충돌·미설명 실패·사용자 마일스톤 경계 없음. `loop/ESCALATE_SOL` 생성 조건에 해당하지 않는다.

| 항목 | pair1 | pair2 |
|---|---|---|
| pair JSON SHA256 | `4452e69ce6dd576ab17689f473a0cc314933073afd8e5158f2ca1e90fc53212a` | `4622159199eb9b4d4ccbf84b8c1a17e8fe3ce2ad73763e57f70165b18f849183` |
| DLL SHA256 | `866c2a36be6e62fc52e92d9ef2b88a9936b6c77612e246a797f5b49d0eb58fa7` | `d67636ab1e93061501c26ec7b7c8cb6cf6259199abcadf65d61b187c04814613` |
| candidate trace SHA256 | `5776e16fec521b046f56d440800fb0b52dc94ac0a96138c517a2909bd866c8d9` | `f01906fb7e2fd47c22425a017f72c1d2a3d8aec839b44ca79247b0b0e7d0a0be` |
| build inputs current MATCH | 44/44 | 44/44 |
| PS3 present / Scale2x all present | 972 /1173 PASS | 978 /1169 PASS |
| fixed first20 /last20 p50 | 337648.5 /355734.0 | 337697.5 /355632.5 |
| DOWN /RIGHT 30-present p50 | 366515 /355403 | 366473 /355514 |
| DOWN /RIGHT key-before p50 | 356206 /366909 | 356206 /366879 |
| DOWN /RIGHT move delta; transfer | 1 /512; 30 /30 | 1 /512; 30 /30 |

- 보호 원본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 read-only MATCH. 두 호출 old bytes offsets `0x245D2=e8 99 81 ff ff`, `0x250F7=e8 74 76 ff ff` 재확인. EXE 파일 후보/생성/복구는 N/A(in-process DLL hook); 새 바이너리 파일 패치를 한 것으로 적지 않는다.
- 두 pair guard-before-hook `direct_draw_trace.c` SHA `e0690d8c71a4ec30b808ebe86dae3ff68fb84275e1cfadb28b662a82a42dec75`는 현재와 동일. host SHA `10493250c17a2042a9b0a70e9662bdc9e1a935b08547d01de29f10868f8cb6cf`, tests SHA `d90656d54be982ab1e73409474a2bfc0aafa7b0b67d8d45989f1dc226aea8e40`. 검수 관련48개 source hash를 공유 temp inventory에 고정했다.
- 각 lane result=pair의 해당 lane, manifest diagnostic DLL SHA MATCH, private/new prefix, source/private EXE SHA 동일, trace/캡처/snapshot SHA MATCH. game 사본 부재, cleanup `game_removed=true`, `prefix_processes_after=[]`, `ok=true`. Wine/Xvfb·save006 한 장면. 8 player records는 활성8인 부하증명 아님.

## E1~E4·B' 독립 재계산

- Binary20개 각각2,378,832 bytes. packed header를 직접 해석: magic/version/header128, tick24692/24728/24788/24824/24860, before=after−1, seq1..5, flags0, pid276/thread280, callsite0x4245D2. run id는 lane별 baseline-baseline/candidate-candidate로 result/trace와 일치. pair 간 같은 run id/PID 재사용은 독립 새 prefix/경로와 manifest로 구분한다. 별도 fresh artifact 디렉터리의 파일들이며 기존 raw 혼입 없음.
- 6 payload 범위를 나눠 공통 `_decode_batched_scene`로 해석한 state=result state 전부 MATCH. 8 owner×20 표본 count 불변식 위반0. 각 baseline5개×2=lap888 reference 같은 tick 전필드 일치; candidate도 같은 기준과 일치. 양pair5개 상태 전필드 차이0(10비교), 카드 gate 대상24728/24824/24860 차이0.
- reference JSON SHA `02b5e67762b4bb260fa800f121af7628c03d56687374c9eed524200ebc2fbb72` MATCH. `_terrain_scroll_pair_parity` 재실행 결과=persisted parity이고 PASS. 절대 r1 입력 tick24692/24788·관측24728/24824·final24860, DOWN/RIGHT 순서·keydown/up·양lane 카메라 동일.
- 원시 candidate PS3 present에서 fixed 및 30-present 목록/p50를 재산출했다. fixed≥264000·last20≥first20×0.9, DOWN/RIGHT 각각≥264000·key-before×0.9. unsupported/outside0, `0≤stale≤covered≤480000` 위반0. movement1/512·transfer30/30. 무수정 Scale2x validator 재실행 두 pair PASS, palette/lookup miss/invalid/outside0.
- 두 DLL compiled wrapper disassembly에서 `pushf/pusha→before→popa/popf→original indirect call→pushf/pusha→after→popa/popf→ret` 확인. 원본 update target0x41C770, 인자 없는 호출/레지스터·flag·stack balance 유지. source에서 runtime guard가 snapshot hook 설치 전에 실행되며 old5bytes 검사·VirtualProtect 성공 후 쓰기·exact5bytes 소유권 원복·cache flush·B실패 시 Arollback 확인.
- snapshot source 복사6범위=주소문서의 PS/tick/camera/player/exists/stock pool. 게임 상태 쓰기 없음(관측 hook code bytes는 명시된 예외). live/file 해석은 같은 decoder이고 비교 player/unit 필드·full state 조건이 줄지 않았다. 잘린/누락/다른tick/run id 거부는 기존128 focused tests 범위; 새 변이gate를 합격조건으로 추가하지 않았다.
- 남은 한계: OS API 강제 실패/동적 rollback 복구 미검증, 0x4250F7 wrapper의 이 장면 실제 호출 미입증. 기존 카드 한계로 유지. 현재 검수는 캡처 fixture 재검산이며 새 runtime 실행이 아니다. 전체 UI/HD 화질·다른 장면 승인을 주장하지 않는다.

## 명령·산출물·Fast

- `make doctor`, `make lint`, `make typecheck` PASS. 선택적 root runtime manifest 부재는 doctor 필수 실패/실제 runtime 증명 아님. focused `.venv/bin/python -m pytest tests/test_g1_saved_scene_probe.py -q`: **128 passed /1.73s**.
- `PYTHONPATH=. .venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap897_middle_review/recalculate.py` 및 같은 폴더 `supplement.py`: 위 raw/identity/validator/parity 독립 재계산 PASS. 이전 lap895 검산 script를 검토 후 새 pair 경로·current source MATCH 조건으로 적용했다.
- 첫 보충 검산의 install event 필드 예상(`status=installed`)이 실제 schema(`install_status=active`, stage=complete)와 달라 assert 실패했다. raw/source를 확인해 검산 script 예상만 바로잡고 재실행 PASS. raw·제품·harness 수정0, 미설명 실패나 실질 구현근거 충돌 아님.
- 재계산 JSON SHA `385a6985cf353670403c9b81be9d1de51750d2034a0cae9851d58c0b3183f091`, supplement SHA `654381455427cb8a000a217c0e863f30f6b6bb115d71e09a120b45da4400278c`, source inventory SHA `c05d7d358ee80f29554ede6ae5d73f928bc4e535a7227d162f2f1fd779fc523e`. 두 DLL disassembly/validator JSON도 같은 공유 temp에 보존. 새 PNG 생성0, 기존PNG/raw/result 변경0.
- 이 기록/handoff/APPROVALS/STATUS를 먼저 완료한 뒤 `make check`를1회 실행하고 끝까지 기다린다. 로그 `logs/gates/lap897-middle-final-check.log`; 최종 결과/후검사/파일hash는 fingerprint 제외 STATUS에만 보강한다. old full-test exit0/source mismatched 결과는 이번 검증으로 쓰지 않는다.
- 새 게임/24k/144k/C/D-1/P5 실행 **SKIP(지정 middle 검수 범위)**. make check는 Fast일 뿐 실제 앱/제품 PASS가 아니다.

## work tier handoff — 다음 한 가지 C 계측OFF fresh3

B' current-source 기술 수용 완료. 다음 work는 재계획 없이 lap858 C/lap863/lap892 그대로 실행한다. 명령 골격: `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lapNEXT_p4b_cN --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/YYYYMMDD_lapNEXT_p4b_cN --hd-source scale2x --performance-window`, N=1..3, 경로는 독점 새 이름. artifact 디렉터리를 미리 만들지 않는다.

snapshot/QPC perf sections/terrain trace/census 계측 env OFF(각 실제 manifest/environment/raw 확인), 원본 immutable·새 complete game/prefix/unused display·source44+host/test 고정. snapshot 설치/출력 없음도 실제 raw로 확인. 각 fresh pair에서 actual sim tick ratio≥0.95, present p95≤baseline+16ms, scene/selection_target/empty_click/drag_exact, Scale2x, coverage≥55%, loaded non-black1600×1200, source/cleanup을 별도 판정한다. **현재 main process exit0은 performance_comparison FAIL을 대체하지 않는다.** 3회 pair 각각 모든 C 조건을 raw로 확인하고 좋은 pair만 선택하지 않는다.

추적 가능한 결함은 카드 §5-3 허용범위에서 원인→최소수리→새 실행을 반복한다. 계측이 필요한 실패 귀속과 계측OFF acceptance 실행은 분리해 기록. 새 상태차이/안전위반/실질 근거충돌은 보존·승격. 완료 증거는 새 middle에 인계한다. C수용→D-1 PS3 last-writer census→수치 기반 P5 순서이며 PS9 대체/기준완화/새 관측gate 금지. C성능·전체coverage≥90%·HUD/tinted/GDI·두 번째 장면·사용자 최종G1 마일스톤은 여전히 미검증이다.

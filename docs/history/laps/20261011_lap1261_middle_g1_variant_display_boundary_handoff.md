# 2026-10-11 | lap1261 | G1 variant 주소 경계 확인 / work handoff

- 지정 역할: middle(진단·계획·확인), Codex App fresh session. 실제 resolved model/effort는 이 표면에 노출되지 않아 추측하지 않음. HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`, runtime source `42a08a02534af62395f260711e91921e8ea3f8b0`는 호출 제공 provenance이며 이번 전체 Fast PASS 지문이 아님. counter1261 읽기만.
- 목표/가설: lap1260 진단을 독립 확인하고, 두 G2 변형판에서 stock-address G1 경로가 기본 표시 실행에도 활성인지 판정한다. 한 가지 판정/계획만 수행, 게임 코드 hands-on0.
- 성공식: 입력 SHA/PE allocator operand/실제 DLL build profile/활성 조건을 연결해 현행 probe의 허용 여부와 최소 work 실행 조건을 명시. runtime PASS·마일스톤/전달 승인은 별개.
- 읽기: PROMPT → AGENTS/INBOX 최신 지시·APPROVALS → STATUS 전체 → DESIGN1~4·MODEL_ROUTING → lap1260/raw/current source. PROMPT의 과거 G2 10000/G4 활성/Claude 고정은 최신 DESIGN/INBOX/MODEL_ROUTING으로 대조. STOP 없음, 기존 ESCALATE는 이 판정 요청.
- 변경파일: 이 기록, 주소 문서 `analysis/memory_maps/g1_esl2613_g2_variant_display_boundary_lap1261.md`, `docs/STATUS.md`, 보존 ESCALATE 사본, ignored `loop/ESCALATE_SOL`. 이전 제품/테스트/다른 세션 미커밋 파일 보존. 커밋0·전달0·새 게임0.

## 이전 바퀴 독립 확인

- 공유 evidence `temp/Syw2plus_patch/20261011_lap1261_middle_variant_boundary/evidence.json`, SHA256 `77e58803e1ac16f4800230e18c9f4537e50d565111fb247a38328bb49cdd5062`. `.venv/bin/python`의 읽기 전용 JSON/SHA/pefile/Capstone 재계산으로 생성; 기존 raw/배치/EXE 수정0.
- lap1260 result SHA `63dcb301b1baf2b8e4d676c7068779b9553f6f9a584cda6fdc8fc03a6e5c79d1`, key log SHA `84eaef270355bd914012545a0dcc0266cc16145291a30241dd2118c191a9962f` MATCH, 5971줄/reject1. 두 trace SHA MATCH, actual candidate mirror presents2395, 전구간 reject max1·stale/fallback/safety7 max0. baseline에 mirror present가 없는 것은 정상이며 candidate 계측0으로 대신하지 않음. 두 summary의 detach/flush complete·drop0, source_unchanged true·기록 cleanup PASS·현재 game사본없음.
- 후보 actual DLL `1be5c53381a039e829f1f8cc139f89e9967758b4f59d6223ef1805850839ddb5`가 manifest와 MATCH, 원본 stub 입력65개 현재 SHA mismatch0. 빌드 manifest의 capacity1200/pool`0x0066B790`/exist`0x008990C8` 확인. 저장소 전체 Fast 지문을 새로 입증한 것은 아님.
- reject writer`0x00466EA0`·digest`44c611f6`·pal`cecc4681`·96×112, written5257/opaque5261/opaque_unwritten4, 좌표[51,104]~[53,105] 확인. 색인과 `fnt/tree_plus.spr.hd/0000.idx8` 43008 B 확인. `read_pack_frame`→`g1_hd_pack_valid` 실패→`note_reject_detail` 경로와 일치하므로 **실행 시 identity_written mask와 팩의 4개 불투명 2×2 블록 불일치**는 확인됐다. 그 4블록이 원본 전체 실루엣 밖이라는 오프라인 판정이나 원본 그림 손상은 입증하지 않았다(화면 클립 identity 이력 있음). guard 유지·Scale2x 강등·raw reject1 공개, 원인 탐색 추가 run 불필요.
- 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` MATCH. 이전 실행은 공식2613 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`/2612 overlay/새게임 조건이며 variant runtime 증거 아님. map/활성8인/부하 fixture를 새로 주장하지 않음.

## 주소·활성 경로 판정

두 전달 EXE SHA는 lap1260와 MATCH: 일반 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`, 고정 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`. 둘 다 `.g2bss` pool`0x01AB5000`/exist`0x0220B9F8`/stride`0x758`/capacity4093. 실제 allocator operand와 기존 packed geometry를 독립 대조했다(주소 문서의 exact bytes). 일반2613 stock1200의 다른 레이아웃과 혼동하지 않는다.

핵심은 **일반 diagnostic 빌드에서 SFX 탐침이 PS3에 자동 실행**된다는 점이다. 현재 builder는 `make all`이고 default-on macro가 없으므로 `INMM_STUB_SFX_PROBE=0`만 설정해도 차단되지 않는다. 이 경로는 옛 pool의 type로 실제 엔진 함수를 호출한다. 현재 full pair는 host stock bulk read도 하므로 scene-actions none만으로 해결되지 않는다. builder의 pool 인자도 복사 runtime_bridge만 바꾸며 나머지 모듈을 바꾸지 않는다. 따라서 unchanged DLL/현행 full-pair 실행은 **HOLD**. 실제 크래시/오염이 재현됐다는 뜻은 아님.

반면 shipped `SYW2_G1_DEFAULT_ON` 경로는 SFX probe opt-in이 이미 구현돼 있고, AI shadow·snapshot·unit dump·control/supply 요청을 끈 표시 경로는 stock-unit 쓰기를 요구하지 않는다. guarded watch 로그1개는 unit evidence에서 제외한다. **display-only 실제 probe는 FEASIBLE**이며 광범위 G2 포팅을 선행하지 않는다. 이는 검사 준비 계획이고 제품 호환 PASS/새 마일스톤 전환이 아니다.

## work tier 명시적 handoff — 재계획 없이 최소 실행

1. Ownership: work는 필요한 최소 variant 표시/로드 probe 진입점과 관련 회귀만 담당한다(가능하면 기존 helper 재사용). 기존 G1 렌더 코드/두 전달 EXE/다른 세션 G2/G9 패치/approved pin은 비접촉. 기존 파일을 공유 중이면 단일 작성자 유지. 이번 middle이 구현을 대신하지 않는다.
2. 새 공유 temp 디렉터리에 inmm 소스를 복사한 기존 private builder 패턴을 재사용하되 **runtime_bridge.c 주입 없이 `make default-on`**. `_G1MM.dll` 결과를 private 게임의 `_inmm.dll`로 설치(게임 EXE import를 바꾸지 않음). macro/source/new DLL SHA·전달 DLL 대비 build profile 차이를 공개. 새 profile은 기본 G1을 켜므로 기준 lane은 `SYW2_G1_NATIVE_2X_BLIT=0`, `SYW2_G1_MIRROR2X=0`, `SYW2_G1_HD_SOURCE=nearest`를 명시; 후보는1/1/scale2x. 양 lane 모두 `INMM_STUB_NO_UNIT_TICKS=1`, `INMM_STUB_SFX_PROBE=0`. `INMM_AI_SHADOW`, `SYW2_SUPPLY_PROBE`, `SYW2_G1_STATE_SNAPSHOT_*`, unit/control diagnostic env를 제거. 새 prefix에 control request 없음 확인. 해당 profile/두 lane env 관련 최소 회귀를 먼저 실행.
3. 원본 읽기 전용 → 전체 private 게임 사본 → 2612 overlay → SHA-pin된 **동일 variant EXE를 기준/후보 모두** private executable 위치에 배치. 기존 `esl2613_runtime.prepare(exe_bytes, ...)` 재사용 가능; current `--esl2613`만으로 variant를 선택했다고 주장하지 않는다. 후보에 sibling_tree_v3를 실제 설치, `SYW2_G1_HD_PACK` 없이 자동 탐색·시작부터 private key log. 파일 복사/원복·private manifest 대상 EXE SHA 확인.
4. 범위는 각 variant 부팅 PS9→새게임 PS7/PS5→PS3 짧은 실제 플레이, 이어 pinned save006 **타이틀 로드** PS3·화면/input survival 비교다. 새 게임 8자리 설정은 가능한 범위에서 기록하되 8인 부하 마일스톤으로 확대하지 않음. 같은 variant의 G1 끔/켬 각각 측정; 별도 멀티/24k/144k/장기시험 추가0. display-only helper는 PS/tick/camera/캡처·render trace만 읽는다. stock `state(detailed=True)`, bulk snapshot, `_unit_witness`, stock pool production/control 호출 금지. 저장 파일 생성·새판 세이브 호환까지 입증했다는 표현 금지.
5. PASS 범위: candidate1600×1200/HD sidecar hit>0·화면 및 실제 클릭 위치 대응, 관련 stale/fallback/safety·close/summary/소유cleanup 확인. reject absolute max와 key를 공개(알려진 tree reject를0으로 재작성 금지); 새 reject/기존과 다른 동작은 귀속한다. raw에 실패/누락이면 HOLD/FAIL, process exit0으로 대체하지 않는다. 동일 장면·unit parity는 G2-aware reader 없는 이 probe에서 UNKNOWN으로 명시하며 full-pair aggregate PASS는 생성하지 않는다.
6. 추적 가능한 하네스/입력/build profile 결함이면 work가 최소 수리→관련 회귀→actual run을 같은 회차에서 이어간다. 이번 구현 source가 바뀔 때만 필요한 전체 Fast(먼저 lint/typecheck); 설정/문서뿐이면 최소 검사. 한 번도 게임에 돌아가지 못한 보조작업2회/60분 한도 유지. 실행은 종료/owned cleanup까지 기다리고 game사본만 제거, prefix/raw 보존. 결과 후 fresh middle이 필요한 변경분을 확인; 사용자 전달/마일스톤 승인 별도·이번 회차에서 수행0.

## 기록·검증·종료

- 기존 ESCALATE byte-exact 사본 `20261011_lap1261_preserved_lap1260_escalate_sol.md`, SHA256 `cc4b3fd6b85a2964dbe66ed17481805f254868bd12b93d8f665406e5e27c97f4`. 이전 HOLD/raw/미결 승인은 보존; 신규 flag는 WORK_HANDOFF를 명시하여 같은 정적 검수 회차를 자동 반복하지 않게 한다.
- `make doctor`: setup ok·원본 SHA verified; optional runtime manifest 부재로 runtime.ok false(게임 실행 PASS로 세지 않음). `make check`/실제 게임/패치 생성·원복 실험은 SKIP: 이번 변경 문서-only, PROMPT③·⑥ 예외. 오래된 wrapper source mismatch 결과 재사용0.
- 다음 한 가지: work가 위 display-only profile을 실제 두 variant에 실행한다. 현행 unchanged diagnostic/full-pair HOLD를 유지하며 milestone/user approval0. 새 증거 없이 strategy/Sol 카드 추가로 연장하지 않는다.
- final fresh 검사: `.venv/bin/python checks/safety.py check --require-game` → SAFETY_PASS, `.venv/bin/python checks/context_limits.py` → CONTEXT_PASS, `git diff --check` → exit0. STATUS67/INBOX318/APPROVALS52줄·Blockers header1개, counter1261 불변. setup/static/document PASS가 variant 실행이나 G1 완료를 대신하지 않는다.

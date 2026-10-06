# 2026-10-03 | lap902 | G1 P4c 중간 독립 검수 — HOLD_SEAM_ATTRIBUTION_UNPROVEN

- 실제 provider/model/effort / 지정 역할: Codex API, 지정 middle(진단·계획·확인). API에서 정확한 모델ID/effort를 노출하지 않아 Sol/high 실행 일치를 주장하지 않는다. 게임 구현 수정·새 runtime·subagent·commit0. counter902 read-only(사용자 preamble901 대신 파일값 적용).
- 목표/가설: lap901 V1/V2를 독립 재계산하고 다섯 tag PNG를 직접 확인(V3), 잔여 검정 초과를 정상 Scale2x detail 또는 renderer 결함으로 귀속. 성공=V1위반0·V2≤2000×5·V3정합; 원인이 불명확하면 HOLD+ESCALATE, B'/C 진행 금지.
- 사전 순서: PROMPT→AGENTS/INBOX 최신 지시/APPROVALS 반려→STATUS 전체→DESIGN1~4→lap900 카드/lap901 기록/지형 blitter 주소/관련 source. G2·G5 종료, G3중단/G4보류, G1 일반작업 자동연결 유지. STOP 없음.
- 변경파일: 이 lap 기록, STATUS, APPROVALS, prior ESCALATE byte-exact archive, ESCALATE_SOL. 제품/source/harness/test/validator/임계값 변경0; uncommitted. 기존 dirty worktree는 보존했다. 검수 산출물은 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap902_middle_review`만 사용, PNG 신규 생성/수정0.
- 원본/fixture: `make doctor` protected EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` verified. 3pair×2lane private/source EXE same SHA, non-synthetic save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`. Wine32/Xvfb, 기존 isolated raw만 사용. 8player records는 활성8인 부하증명 아님.
- 후보DLL: 최종 origin pair `_inmm.dll` SHA `e0e36dffeb112c1fb9156fff401a3bad093f21897d0427b37f876ba7a4a6dab5`, manifest와 MATCH. build44개 current-source MATCH; 첫2pair는 mirror source만 이전 구현(예상, lap901 반복 기록 일치). 모든 DLL manifest SHA MATCH. build archive의 Makefile/inmm_stub.c는 runtime bridge 자동삽입 사본이며 원본input과의 두 diff는 `build_runtime_bridge.py:83~99`가 설명한다(충돌 아님).

## 독립 원시 재계산 (Evidence)

- 명령: `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap902_middle_review/recalculate.py`; 저장 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap902_middle_review/recalculation.json`, SHA `dc0f88db80cf85eea0a30dbf9f987c1de146b8e21266379bfde94a0356c8f6be`. script SHA `084af2243b4e7717fac713e2201f1b152867b5be8af3f48510138964489f6da0`. source/raw/PNG/manifest95파일 before/after 변화0.
- 입력3pair: 공유 temp captures의 `20261003_1945_lap901_p4c_green`, `_green_r2`, `20261003_1955_lap901_p4c_origin_pair`. 전15 PNG쌍 RGB(0,0,0), 원본(x,y)/후보(2x,2y), 논리800×480=384000 재계산이 recorded 값과 일치.
- V1 present 각각1085/696/705, 위반 각각0. current validate_trace도3/3 PASS. outside diff/palette/invalid/key miss0 유지. origin candidate trace SHA `3e1f0210b59c27c67eed1d33d503ead565119035c8d08190fcb99eff648d5b89` MATCH.
- V2 초과 loaded/selection/drag/minimap/production: pair1 `4574/4933/4440/4737/4810`, pair2 `4737/4661/4439/742/4859`, origin `4565/4649/4461/634/4810`. 최종4FAIL·1PASS, 3pair 전체합격0. 기준2000 불변. 최종pair SHA `c1ec464ba33681e306d662c43b2a9106412588aa02198cca92e4aefeb18d8d27` MATCH.
- 三pair scene.state 직접비교true; 6lane cleanup.ok=true·prefix processes=[]·game 사본부재 확인. 이것은 과거 실행 cleanup 검수이며 새게임 실행 증거 아님.
- 정적인 돌바닥 ROI 논리 `[400,260,620,360)`의 원본black66개. 후보에서 원본nonblack 위 black subpixel1367개(TL325/TR339/BL357/BR346), 3pair loaded 전부 동일. 움직이는 효과/메뉴만으로 이 정적 잔차를 설명하기 어렵다.
- origin loaded 384000블록의 black subpixel 개수0..4 histogram=`355689/18884/0/59/9368`. 한개black인블록18884개가 주된 추가양상이며 대면적 2×2 전체결손과 다르다.
- 독립 whole-completed-RGB Scale2x top-left black 초과 origin5tag=`188/185/167/244/186`, 실제=`4565/4649/4461/634/4810`. 기존 보조pixel JSON과 일치. RGB전체화면과 palette-index개별자산은 서로 다른 연산이므로 이것은 exact oracle 아님.
- 부차적 하네스 기록 불일치: 세 raw의 v2_capture_gate.status=`BLOCKED`, tag_status에는 FAIL. 현재 `_v2_capture_gate` 동일 tag 입력은 `FAIL`. 숫자·non-PASS·exit2 판정은 동일하므로 PASS로 바꾸지 않는다. 당시 host script snapshot/분류 chronology는 보존되지 않아 기록 수정으로 원인확정 금지; work handoff에서 current-source serialisation regression만 고정한다.

## V3 직접 육안 검수 (Evidence / limits)

최종pair baseline/candidate loaded·selection·drag·minimap·production 총10PNG를 직접 열었다.
건물·지형 경계·HUD 기본 배치는 같은 논리 자리에 유지되고 이전 큰 검은 마름모 결손은 없다.
그러나 후보 돌바닥에는 원본보다 뚜렷한 가는 검은 대각 타일 격자가 계속 보여 V3 수용을 보류한다.
selection/drag의 선택HUD·드래그박스·커서/효과 및 minimap의 초상 이벤트는 두 lane 캡처시점이 다르다.
따라서 tag라는 이유로 identical-state screenshot이라고 부르거나 UI/input parity 전체PASS로 해석하지 않는다.

## 원인 순위 / 검증 가능한 work handoff

1. **Inference, medium-high:** tile의 미기록/투명 이웃 sentinel0가 Scale2x의 실제 palette0으로 섞여 seam을 만든다.
   `g1_mirror2x.c:1014~1020`은 scratch A/B를0/255로 초기화, `g1_hd_asset.c:503~540`은 A값만 identity frame으로 저장,
   `:381~418`은 모든 이웃을 색으로 비교, `g1_mirror2x.c:530~560`은 중심 A==B만 확인한 후 4subpixel을 무조건 복사한다.
   RLEskip/checker 미기록 영역이 mask 없이0으로 저장되는 정적 경로와 후보의 반복 tile 격자가 맞는다.
2. **Inference, low-medium:** 실제 palette-index Scale2x detail 또는 다른 cache/shade/clipping 결함이 일부 잔차를 설명할 수 있다.
   실제 primitive별 A/B·이웃mask·출력block의 같은-call provenance는 기존 trace에 없어 1번을 실제tile 귀속으로 확정할 수 없다.
3. **Low:** PNG 시간차만의 설명. static ROI1367개가3pair 동일하고 후보 grid가 모든 tag에 유지돼 주원인으로는 약하다.

- synthetic(비게임) 3×3 index `[[7,0,7],[0,7,7],[7,7,7]]`, 위/왼쪽만 unwritten mask일 때 현재 정확식 출력=`[0,7,7,7]`.
  중심은 written7인데 P0가 unwritten0에서 들어온다. 동일 bytes·all-written mask이면 이0은 정당한palette0이다.
  저장 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap902_middle_review/mask_counterexample.json`, SHA `8cc37fd32d499db6c5933a11d94bcdaa2dc119fd5b65e0c12807b870a4ac7f98`. **가능한 경로의 산술반례이며 실제 tile/runtime proof 아님**.
- **승격 작업자 다음 검증:** 위 actual-mask-loss 경로와 static ROI를 독립 확인하고, P4c 기존범위에서 work의 같은-call tile/mask 귀속 관측 및 최소수리 허용범위를 결정한다. 기준완화·새구조·추가 전수계측을 전제하지 않는다.
- **조건부 work handoff:** 새copy/source로 seam타일 한종의 원본RLEskip 또는 두sentinel write-mask와 B/D/E/F/H·현재4subpixel을 연결해 unwritten0 유입 여부를 확인한다. 확인되면 identity/HD결합이 실제 write coverage를 보존하도록 최소수리하고 관련 회귀→fresh pair→V1/V2×5/V3를 재검증한다. mask를 공급할 수 없으면 추측코딩하지 않고 구체 blocker.
- 값0 전부 삭제/강제nearest/coverage축소 금지. 실제 written palette0과 unwritten0를 분리하고 all-written Scale2x, RLEskip/clipped/checker/shade·캐시이동 회귀를 보존한다. 같은-call 귀속 뒤만 수리, 이middle은 게임구현 안함.
- work는 current `_v2_capture_gate`의 FAIL-tag aggregate/JSON roundtrip을 회귀로 고정하고 fresh source/hash를 기록한다. 기존raw 덮어쓰기·과거BLOCKED를PASS로정정 금지.
- V1/V2/V3 GREEN 뒤에만 기존카드의 B'2pair·C3pair를 같은수리source로 수행. D-1/P5/G1마감 안함.

## 검사 / 종료

- fresh `make doctor` PASS(original verified; runtime manifest부재는 새runtime 미요청 상태), `make lint` ruff/compileall PASS, `make typecheck` PASS,
  focused `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py tests/test_g1_hd_scale2x_probe.py tests/test_g1_mirror2x.py` **155passed/3.01s**.
- fresh full `make check`·새runtime **SKIP**: 사용자 근거불명/충돌 stop에 따라 현증거·handoff 보존 뒤 종료. 현재 fingerprint 전체Fast 미검증.
  lap901 full log를 직접 읽어1438passed/5skipped·921.67s를 확인했으나 과거검사를 현재PASS로 승격하지 않는다.
- prior ESCALATE 전문은 `docs/history/20261003_lap902_prior_lap901_escalate_sol_archive.md` SHA `da75bf87ebd743261432e63e37d044de7b44b97e01b2a643b9d758282fdc0f82` byte-exact 보존, 새 ESCALATE에 현재근거·미검증·승격다음항목을 기록한다.
- 최종 safety/context·source/raw불변·문서한도 결과는 fingerprint예외 STATUS에만 보강한다. 승격은 내부handoff이며 사용자재허가 요청 아님.
- 다음 한 가지: 승격 middle/strategy가 actual write-mask 귀속 관측/최소수리 범위를 확인한 뒤 work에 즉시 인계. G1 HOLD, 제품승인0.

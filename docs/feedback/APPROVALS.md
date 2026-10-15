# APPROVALS — 압축 포인터

## 2026-10-14 lap1309 — H-G1BOOT 진단 HOLD / 사용자 승인 아님

- root/lap1308 raw 대조: 초기1600×1200 HRESULT0→후속640×480×32 E_NOTIMPL,root초기1600실패단정미입증. combined예외는c0000096으로전사정정(noVD001d/root0005);raw/work원문불변. root hqcdd.log는입력기존로그와SHA동일하므로새실행근거제외. 상세 `../history/laps/20261014_lap1309_middle_g1boot_failure_boundary.md`.
- 원인/first-chance stack/01FC01AD bytes·모듈귀속 UNKNOWN;사용자2614 Windows 시작즉시종료FAIL유지. startup2·doctor/lint/typecheck·EXE/DLL SHA대조PASS는진단준비범위. 제품수정/새게임/전체check/전달/마일스톤승인0. root/Sol확인후work최소실측handoff `loop/ESCALATE_SOL`,추가문서검수로제품probe를연기하지않는다.

## 2026-10-14 lap1307 — H-HDGUARD 두 수리 독립수용 / 전달 경계 인계

- lap1306 버퍼1200·native-reader source SHA fixture 수리만 scoped 기술PASS. work diff blob2개/원본EXE/DLL/result/raw SHA 일치·관련164회귀/doctor/lint/typecheck PASS·보존PS3 1216/60.755초/HD100%/drop0/ownedcleanup 독립확인. 최종raw3511행은종료요청3465행+정상flush이며실질충돌없음.
- 제품/새게임/빌드/전체check/전달/사용자마일스톤승인0. mirror BLOCKED·Windows/DxWnd/오디오·G1미결유지. root가 전달후보고정→전체makecheck1회→기존19:2x 사용자승인범위전달을잇는다; 실패하면PASS로쓰지않고work에구체수리인계. `loop/ESCALATE_SOL`, 상세 `../history/laps/20261014_lap1307_middle_hdguard_repair_review.md`.

## 2026-10-14 lap1305 — H-HDGUARD 입력 준비만 독립수용

- lap1303 수리묶음14이미지·1135PNG·원본15SHA·팔레트/투명mask/원본픽셀·YAV보존불일치0로scoped PASS. 아래lap1302의누락5개충돌은이번수리묶음에서해소됐으며과거HOLD원문은보존한다. 업스케일품질/Windows/G1사용자마일스톤승인아님,새전달/승인요청0. root다음배정은 `loop/ESCALATE_SOL`; 상세 `../history/laps/20261014_lap1305_middle_hd_input_review.md`.

## 2026-10-14 lap1302 — H-HDGUARD 입력묶음 충돌 / 전체수용HOLD

- guard 관련129회귀·2614보존raw/SHA/PS3 60.906초1216·거절1/hit391/drop0/회수국소확인. 입력14이미지완료주장과실제9개만존재하는raw충돌(fnt/yfnt5개567frames rendered=false/PNG0)로전체HOLD·ESCALATE_SOL. 사용자승인요청/전달/마일스톤마감0,기존미결·legacy2608 Windows FAIL유지. 상세 `../history/laps/20261014_lap1302_middle_hdguard_extraction_hold.md`.

## 2026-10-14 lap1300 — H-TR2614G1 stage 수용 / 사용자 승인 아님

- 후보3976fa88…·777장부/HD773+제외9·DLL metadata6byte·보존PS3 60.800초1217/drop0/ownedcleanup 일치로scoped기술PASS. 적용payload774파일,BAT2/manifest/SHA장부내부자료. root 후보고정/전달직전make check1회 경계인계; 새승인요청/전달/마일스톤마감0. Windows/DxWnd/음악·입력/화질/기존G1미결·HOLD유지. 상세 `../history/laps/20261014_lap1300_middle_tr2614g1_staging_review.md`.

## 2026-10-14 lap1298 — MCI 기록0건 국소수용 / 전체HOLD·사용자미결유지

- lap1297 off/on동일EXE·WINMM·두MCI로그0B·창800×600/1600×1200를독립확인해scoped기술PASS. on PS3 1,216/60.749초,off연속dwell UNKNOWN이라전체runner HOLD 유지. 오디오재생/forward성공/DLL무결함/Windows/G1사용자승인아님. root 보고·후보준비경계인계,새사용자승인요청/전달0. 상세 `../history/laps/20261014_lap1298_middle_g1_mci_pair_review.md`.

## 2026-10-14 lap1296 — H-G1ON2614 수리 범위 독립 수용 / 사용자 승인 아님

- lap1294 최종 DLL `0e5ef5fd…`의3경기 PS3 관측합483.503초·drop/overflow/stale/fallback/safety0를 raw와독립재빌드·관련회귀로확인해 scoped 기술 PASS. lap1289/1291의과거480초FAIL은유지하며한경기연속480초로승격하지않는다. MCI off/on 비교·실재오디오·Windows/DxWnd·사용자G1승인은미결;새전달/승인요청0. 다음은기존00:57배정의work MCI실측이며동일후보middle재검수는반복하지않는다. 상세 `../history/laps/20261014_lap1296_middle_g1_soak_review.md`.

## 2026-10-14 lap1291 — H-G1ON2614 raw 충돌 / 기술 수용 HOLD

- lap1289의480초PASS 주장은raw summaryFAIL/drop10932와충돌하며 PS3→PS27/PS29패배로끝난뒤의시간을포함한다. 관측PS3 구간183.474초의표시계수0를480초안정성으로수용하지않는다. 기존raw·work원문·4 lane국소근거보존,추가사용자승인요청/전달0. root/Sol→work최소수리인계는 `loop/ESCALATE_SOL`;상세 `../history/laps/20261014_lap1291_middle_g1_winmm_raw_conflict.md`. MCI0-call·Windows·G1사용자마일스톤미결유지.

## 2026-10-13 lap1287 — G5 범위 확인 / 경계 인계

- INBOX23:15 사용자 H-G5ON2614 지시가 과거 G5 종결·재개 금지를 해당 범위에서 대체한다. G1 완료 승인 없이 G5를 최우선으로 진행한다. 이는 middle의 권한/범위 확인이며100기 기술 PASS·사용자 마일스톤 승인이 아니다. work는2614 비활성 스위치만 사본에서 켜고 원본 대비 실제 선택/명령/UI/저장로드/크래시를 확인한다. root 경계 인계 `loop/ESCALATE_SOL`; 상세 `../history/laps/20261013_lap1287_middle_g5on2614_scope_handoff.md`. 새 사용자 승인 요청 없음, 기존 미결·FAIL 보존.

## 2026-10-10 23:46 KST — Windows 헤더 수정판 / 파일명 반영

- 사용자 Windows r10 실행거부·전달본 이름변경 확인을 반영했다. 일반판 구조검사 오류0/bytes 불변. 자리고정 r11은 헤더겹침 수리, 관련회귀4·독립byte/원복·120초privateWine 시작/진행 수용. Windows 및 새자리좌표 행동의 사용자 재시험은 미확인이다. 사용자 PC의 일반판 실행 성공은 Windows 근거이며 자리고정판은 이전실측FAIL을 보존한다.
- 현재전달물: `[ESL]Syw2plus 2613_G2_G6_G8.exe` SHA256 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`; `[ESL]Syw2plus 2613_G2_G6_G8_G9_자리고정.exe` SHA256 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`, 둘 다2,003,968B. 공식2612 데이터+2613 게임 설치 구성용 EXE다. 복사 후SHA MATCH, 단순2613 이름의 이전두파일은 `260921_temp/archive/20261010_234622_2613_before_header_fix/`로 이동해SHA MATCH; 삭제/덮어쓰기/txt0, 기존code참조후보·G1 비접촉.
- audit 공유temp `20261010_g9_windows_header_fix/delivery.json`; `independent_review/review.md` SHA `a4b6b0fb46aa5ee4946f8ad855b3331d48aea18b7b5714308800b55498dffd56`. 기존 장기실험은 r10의 PARTIAL 결과이고 r11 장기PASS가 아니다.

## 2026-10-10 — 2613 두 EXE 사용자 요청 배치 완료

- 사용자 지시: `/home/dev_00/sharedfolder/260320_Syw2plus/260921_temp/`에 패치 파일 배치. `2613_G2_G6_G8.exe` 2,003,968B SHA256 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`; `2613_G2_G6_G8_G9_자리고정.exe` 2,004,992B SHA256 `a6d357102dec956f8caa407a2bcb1d56eb14409bc9a67ee17d0ca80a478c40bc`. 복사 전/후 동결 후보와 MATCH.
- 기존 동일 이름/대체2613판 없음, 덮어쓰기·기존 파일 이동0·txt생성0·G1비접촉. 공식2612 데이터+2613 설치 구성용 EXE이며 원본 게임에 자동deploy하지 않았다. 장기 실험은 아직 진행 중이고 사용자 플레이 승인을 대신하지 않는다.
- 배치 audit: 공유 temp `20261010_patch_delivery_2613/delivery.json`. 추가 승인 질문 없음(사용자가 배치 명시 요청).

원문 249줄·SHA256 `574681f21c830c71e9c9dfdcef62befcb63327e7135651b8acf9867be7d48fee`를 `docs/history/20261004_approvals_lap945_precompaction.md`에 byte-exact 보존했다. 반려·미결 근거와 과거 승인 전부는 해당 원문에서 확인한다.

## 현행 경계 요지
- G2·G5는 2026-10-03 사용자 직접 플레이 확인으로 달성·종료; 기존 기술 한계는 보존한다.
- G1은 미완료이며 사용자가 달성까지 자율 지속을 지시했다. 제품 PASS와 최종 사용자 마일스톤 승인은 구분한다.
- 원본/참고/raw/golden 보호, G2/G5 재개·G3/G4 재개·commit/publish/deploy는 금지.
- 현재 work 범위는 `docs/STATUS.md` 및 lap944 카드에 한정한다.
- 2026-10-04 lap960 strategy 판정(사용자 승인 아님, 사용자 번복 가능): 내부 경보선 V2s(lap903 strategy 작성)를 "Scale2x(원본)으로 설명되지 않는 단일 흑색 블록 ≤2,000"으로 재정의. 근거: 완벽 Scale2x 기준만으로 35/35 tag 2,166~3,547 초과, 격자 결함 lap901은 재정의 뒤에도 18.7k~19.9k FAIL. 한도·tag·집계·V1/V2/V2q·validator 불변, raw는 계속 기록, 과거 pair-result 불변. 카드 `docs/work/active/G1_STRATEGY_W70_V2S_REFERENCE_REFRESH_LAP960.md`.

## 2026-10-11 — H-TRVAR2613 G1 display 시험판 전달 기록

- 사용자 사전 결정 03:14 KST: 변형판용 G1 시험판은 검사·독립검수 통과 후 추가 질문 없이 전달, lap1256판은 archive로 이동. lap1272 공식2613 격리 display-only 네 lane과 fresh Codex sol reviewer의 scoped PASS 뒤 03:39 KST 완료.
- 전달: `../260921_temp/G1_1600x1200_시험판_20261011_1272_2613_HD_변형/`; `_inmm.dll` SHA256 `205b89b2c6ff3ae530ed3cbb705b644ea454404a0efee37de3980a85da36c28c`; manifest SHA256 `151148f2b5ffd6e4ad12013ce32de53c94e78d894a52d83f7271a19283656707`; 39,942 payload 항목 전부 재해시 MATCH, 구성 39,943파일, txt0. 새 전달 대상은 덮어쓰지 않았다.
- 대체된 `../260921_temp/G1_1600x1200_시험판_20261010_lap1256_2613_HD/`를 삭제하지 않고 `../260921_temp/archive/G1_1600x1200_시험판_20261010_lap1256_2613_HD/`로 이동했다.
- 실행 증거: 공식 EXE SHA `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`; newgame off/on 및 save006 off/on 모두 PS3/close/cleanup PASS, protected source unchanged. HD on hit87/116, stale_pixels0, HD-key reject1/0; 첫 reject는 알려진 `tree_plus` key로 원인 UNKNOWN 유지. Scale2x validator PASS, mirror validator BLOCKED를 공개한다. Windows·G2 pool/8인·G9 행동·G1 사용자 milestone은 미확인.
- raw 결과 SHA256 `013a7f184e215004f4b6ea33c19019a6c94a6107663a2dcead4167efd662f6a4`; 독립 판정과 회차 상세 `docs/history/laps/20261011_lap1272_work_htrvar_official2613.md`. 이 전달은 사용자 G1 합격/마일스톤 승인이 아니다.

- [x] **사용자 판단 요청(lap962 middle, 루프 정지 아님):** G1 pair HOLD의 남은 유일 사유는 내부 경보선 V2s raw production 2,785>2,000이다(lap961). 그런데 원본을 완벽하게 Scale2x한 기준 자체가 같은 tag에서 3,547이라, coverage를 줄이지 않고는(금지) raw gate를 PASS할 수 없다. Scale2x로 설명되지 않는 흑색은 5 tag 80~254이고, PNG에 격자/seam은 없다. 선택지: (1) W-1 채택(unexplained ≤2,000을 gate로 쓰고 raw는 공개 진단) 또는 (2) raw gate 유지(그러면 pair는 계속 HOLD, 다른 G1 수리는 진행). 사용자 결정 전에는 (2)로 취급하고 기존 판정·validator·과거 raw를 바꾸지 않는다. 근거 `docs/work/active/G1_MIDDLE_W70_W2_ACCEPTANCE_TERRAIN_EDGE_HANDOFF_LAP962.md` §3.
  - **사용자 결정(2026-10-06 01:43 KST): (1) W-1 채택.** V2s gate = Scale2x로 설명되지 않는 단일 흑색 블록 ≤2,000; raw는 공개 진단으로 계속 기록. 과거 pair-result·V1/V2/V2q·validator·tag 불변, coverage 축소 금지 유지.
- [x] lap960 W-1 V2s gate 의미 변경은 **사용자 미승인 제안**으로 보존한다. raw FAIL→unexplained PASS로 바꾸는 aggregate/status 교체는 자동 적용하지 않음; root 2026-10-04 경계에 따라 W-2 실제 성능 수리부터 계속하고 unexplained는 별도 진단으로만 사용한다. 모델 기술 승인·사용자 마일스톤 승인을 혼동하지 않는다. → 2026-10-06 01:43 KST 사용자 승인(W-1 채택)으로 해소.
- [x] **사용자 확인 요청(lap978 middle, 비차단·루프 정지 아님):** G6·G7 재현에 "혼자하기 대기실에서 1P가 아닌 자리로 옮기기"가 필요한데, 격리 실행에서 방향키(탭·번호칸 클릭 뒤)로는 자리가 옮겨지지 않았고(좌측 자리 패널 변화 0) 정적 스캔에서도 대기실 방향키 처리기를 찾지 못했다. 자리를 옮길 때 정확히 무엇을 눌렀는지(먼저 클릭한 칸, 방향키를 누르고 있었는지, ESL 판 여부) 알려주면 그 경로로 재현한다. 답 전에는 카드 `docs/work/active/G6_MIDDLE_LAP978_HG6A_ACCEPTANCE_REAL_SEAT_HANDOFF.md` §5 A(누르고 있는 방향키)·B(게임 자체 로비 갱신 경로)로 진행한다. lap977 H-G6a는 기술 PASS(partial)이며 G6 사용자 마일스톤 승인이 아니다.
  - **사용자 답(2026-10-05 04:45 KST):** “혼자하기 대기실에서 키보드 화살표 위아래로 자리 움직일 수 있더라고”. 즉 대기실의 ↑/↓ 키(좌우 아님)로 자리를 옮긴다.
- [ ] **사용자 확인 요청(lap981 work, 비차단·루프 정지 아님):** 격리 대기실에서 ↑/↓를 Alt 탭·빈 영역 클릭·번호 버튼 클릭·XSendEvent·Tab 어느 쪽으로도 게임에 전달하지 못했다. 채팅 입력줄이 키보드 포커스를 유지해 방향키를 삼킨다(`a` 입력이 줄에 쌓임, 같은 읽기가 PS3에서는 정상). 자리를 옮길 때 방향키 직전에 정확히 어디를 눌렀는지(채팅줄 클릭·특정 버튼·마우스 위치 등) 알려주면 그 조작으로 재현한다. 답 전에는 `lobby-snapshot`(게임 자체 로비 갱신 `0x4B7700`)을 G6/G7 자리 생성 기본으로 쓴다. 근거 `docs/history/laps/20261005_lap981_work_g6_lobby_key_focus_hg6k.md`.
- [ ] **사용자 합격 요청(lap989 middle, G6·G7 마일스톤 — 모델 기술 수용은 사용자 합격이 아님):** G6(1P 아닌 자리 Shift+클릭 추가)·G7(타이틀 불러오기 자리 복원) 시험판 두 개를 독립 재조립·SHA 대조로 준비했다. 일반판 `fb7c21319414b13517c7f8fdeeef3ca6b04c61953e592733e1ed3cc5bc65c56a`, 시작자리고정판 `58b9b22a650a647fe7ddf43dcf2ae58d5c943d02448ac20fc36b2032f3c2f078`(바탕 G5 선택50 시험판 `0e28ef57…`/`703deaf4…`). 스테이징: 공유 `temp/Syw2plus_patch/20261005_lap989_middle_review/user_test_staging/`(EXE 2개+안내문, `260921_temp` 배치는 root/사용자 몫). 확인 절차: ① 대기실 ↑/↓로 1P 아닌 자리 → ② Shift+클릭·Shift+드래그 추가·Shift+클릭 해제·드래그 50 상한 → ③ 그 자리 저장 → 게임 완전 종료·재시작 → 타이틀 불러오기에서 같은 자리 조종·패배 없음 → ④ 1P 세이브 타이틀 불러오기 1P 정상 → ⑤ 인게임 불러오기 정상. 격리 근거: lap979/988 G6(자리 2·1P 대조), lap984~988 G7(R-1~R-4·X-1~X-4·fixed_start F-1), lap989 재계산 불일치0. 미검증: 실제 ↑/↓ 경로 동일성(위 lap981 질문)·시작자리고정판 G6·자리 2 외·LAN 멀티. 행동 변화: 인게임 불러오기도 세이브 자리를 따른다(1P 게임 중 자리 2 세이브 → 자리 2). 판단 전 G6/G7은 "사용자 합격 대기"이며 루프는 독립 작업(H-G6f, 그다음 G1)을 진행한다. 근거 `docs/history/laps/20261005_lap989_middle_g6_hg6r_acceptance_user_test_request.md`.
  - lap1090 middle: R4b 시험판 2개(`fb7c2131…`·`58b9b22a…`)는 G7 사용자 합격 대상에서 철회. 새 수리 R5는 work·middle 검수 뒤 다시 요청한다.
  - **사용자 플레이 결과(2026-10-06 19:31 KST, 일반판·시작자리고정판 둘 다):** G6 Shift+클릭 선택 문제는 해결된 것으로 확인(**G6 사용자 확인 PASS**). **G7 FAIL**: 1P 아닌 자리(↑/↓로 선택)에서 시작·저장 후 로드하면 첫 번째 자리(1P)의 컴퓨터 유닛/건물로 로드됨. **타이틀 불러오기·게임 중 불러오기 둘 다** 동일 증상. → G7 재작업 필요.
- [x] **사용자 재합격 요청(lap1093 middle, G7 마일스톤 — 모델 기술 수용은 사용자 합격이 아님):** R4b 사용자 FAIL 뒤 새 수리 R5(저장 때 조종 자리·대기실 표를 세이브 끝 384 B 꼬리로 기록 → 로드 때 그대로 복원, 혼자하기만)를 lap1091 work 구현·lap1093 독립 재계산(불일치 0)으로 수용했다. 시험판(G6 포함): 일반판 `b582fb1969e8e08076cc69ef93bd99669f65baefebfb9e4d4f88c2b8d90a2dfd`, 시작자리고정판 `acf5bd3d7f4657d95cc9bc4db3621dd4184d823416719095c3b714f0f0cbf1a4`(바탕 `0e28ef57…`/`703deaf4…`), 스테이징 공유 `temp/Syw2plus_patch/20261007_lap1093_middle_review/user_test_staging/`(안내문 `3f5622c9…`, `260921_temp` 배치는 root/사용자 몫). 확인 절차: ① ↑/↓로 1P 아닌 자리 시작 → ② Shift+클릭 재확인 → ③ 이 판으로 새로 저장 → ④ 게임 중 불러오기 같은 자리 → ⑤ 완전 종료·재시작 → 타이틀 불러오기 같은 자리·패배 없음 → ⑥ 1P 세이브 정상 → ⑦ 시작자리고정판 반복. 격리 근거: 지난 판 실패 모형(W-1) 재현, 같은 상태에서 R5는 타이틀·인게임 모두 자리 2 복원, 교차 로드·fixed_start·G6 비회귀 PASS. 미검증·공개: 실제 ↑/↓ 경로 동일성, 이전 판/원본 세이브는 복원 안 됨(원래 동작), 자리 2 외·LAN 멀티. 판단 전 G7은 "사용자 재시험 대기"이며 루프는 G1을 진행한다. 근거 `docs/history/laps/20261007_lap1093_middle_g7_hg7s_acceptance_user_retest_request.md`.
  - **사용자 결정(2026-10-06 21:21 KST): G6·G7 달성·종료.** R5 시험판(b582fb19…·acf5bd3d…)으로 직접 플레이해 “G6 G7 해결된 것 같아”. G6 Shift+클릭·G7 세이브 자리 복원 모두 사용자 확인 PASS. 미검증 한계(LAN 멀티, ↑/↓ 격리 재현 불가)는 보존.
- [ ] **사용자 시험 요청(lap1104 middle, G1 마일스톤 확인 — 모델 기술 수용은 사용자 합격이 아님, 비차단·루프 정지 아님):** G1 원본 구성 1600×1200 시험판(원본 `[HQ]Syw2plus 2002.exe` `b56986e0…`는 그대로, `_inmm.dll`만 교체 + `.bat` 실행). lap1099 H-UA0·lap1101 H-UA1(C:\ 쓰기 불가에도 켜짐)·lap1103 H-UA2(유닛 기록 끄기)를 lap1100/1102/1104 middle이 독립 재계산·재조립(타임스탬프 외 일치)으로 수용했다. 스테이징: 공유 `temp/Syw2plus_patch/20261007_lap1103_work_hua2/user_test_staging/`(`_inmm.dll` `942133740dc10f92…`, `g1_trial_direct.bat` `2da323e8…`, `g1_trial_via_dxwnd.bat` `29a35d2e…`, 안내문 `97f4bd75…`; `260921_temp` 배치는 root/사용자 몫). 확인 절차(안내문): ① `_inmm.dll` 백업(원본 `03192987…`) 뒤 교체 → ② `.bat`으로 실행해 창 1600×1200 확인 → ③ 타이틀·메뉴·게임 화면 UI/월드/미니맵 비율·구도가 원래와 같은지 → ④ 유닛 클릭·드래그 선택·미니맵 클릭·메뉴/생산 버튼이 화면 위치와 맞는지 → ⑤ 가장자리 스크롤·몇 분 플레이 느려짐/깨짐/크래시 → ⑥ 원복 SHA 확인. 격리 근거: save006 full pair(입력효과 7/7·V2/V2s/V2q/Scale2x·minimap parity PASS). 미검증·공개: 실제 Windows 1600×1200 모드·1080p 표시·DxWnd env 전달·BGM·사용자 `ddraw.dll`, Scale2x 화질(허용 차이), 명시 잔여(로고 일부·GDI 글자·반투명 일부·한두 프레임 깜빡임), G2/G5/G6G7 EXE 조합. 판단 전 G1은 "사용자 시험 대기"이며 루프는 G1 독립 작업을 계속한다. 근거 `docs/history/laps/20261007_lap1104_middle_g1_hua2_review_user_trial_request.md`.
  - lap1136 middle: **이 판(`94213374…`)은 아래 lap1136 요청의 lap1135 판(`6cbb12ac…`)으로 대체한다.** 옛 판으로 본 결과가 오면 판을 구분해 처리한다(버리지 않는다).
- [ ] **사용자 시험 재요청(lap1136 middle, G1 마일스톤 확인 — 모델 기술 수용은 사용자 합격이 아님, 비차단·루프 정지 아님):** lap1104 판 뒤 기본 켬 수리 4개(불러오기 화면 화질·Esc 메뉴 저장/불러오기/환경설정 창 닫은 뒤 띠 화질·패배/승리 배너 화면 하단 HUD 몇 초 소실·결과 표 막대 계측)를 묶은 판. 위치·입력 동작은 바뀌지 않는다. lap1135 work H-TR2(save006 full pair PASS·victory-poke 12/12)를 lap1136 middle이 새 스크립트 재계산(불일치 0)·현재 트리 독립 재조립(타임스탬프 7바이트 외 동일)으로 수용했다. 스테이징: 공유 `temp/Syw2plus_patch/20261007_lap1135_work_htr2/user_test_staging/`(`_inmm.dll` `6cbb12aca8be4e42…`, `g1_trial_direct.bat` `2da323e8…`, `g1_trial_via_dxwnd.bat` `29a35d2e…`, 안내문 `f6593f5c…`; `.bat`은 lap1104 판과 byte 동일, `260921_temp` 배치는 root 몫). 확인 절차는 lap1104와 같다(①백업 뒤 교체 ②`.bat` 실행·창 1600×1200 ③UI/월드/미니맵 비율·구도 ④클릭·드래그·미니맵·버튼 위치 ⑤가장자리 스크롤·몇 분 플레이 ⑥원복 SHA) + 선택: 한 판을 끝내 승리/패배 배너·결과 표에서 하단 HUD 유지. 미검증·공개: lap1104 항목과 같음, 승리·패배 화면은 합성 트리거로만 측정(실전투 승리 미측정). 판단 전 G1은 "사용자 시험 대기"이며 루프는 G1 독립 작업을 계속한다. 근거 `docs/history/laps/20261007_lap1136_middle_g1_htr2_review_user_trial_rerequest.md`.
  - lap1152 middle: **이 판(`6cbb12ac…`)은 아래 lap1152 요청의 lap1151 판(`8a3837fb…`)으로 대체한다.** 옛 판으로 본 결과가 오면 판을 구분해 처리한다(버리지 않는다).
- [ ] **사용자 시험 재요청(lap1152 middle, G1 마일스톤 확인 — 모델 기술 수용은 사용자 합격이 아님, 비차단·루프 정지 아님):** lap1135판(12:53 전달) 뒤 기본 켬 가시 수리 2개를 더한 판: ⑤ 처음 실행 때(등록 사용자 없음) 뜨는 사용자 등록 창 바탕 화질(H-TM1, 격리 HD 84.1→99.8%), ⑥ 시나리오 브리핑 초상화 화질(H-SC2, 격리 HD 89.4→100%). ①~④(lap1136 요청)는 그대로, 위치·입력 동작·.bat 불변. lap1151 work H-TR3(save006 full pair PASS: 입력효과 7/7·V2/V2s/V2q/Scale2x·minimap parity)를 lap1152 middle이 새 스크립트 재계산(불일치 0, 정정 1 = 장면 변동)·현재 트리 독립 재조립(타임스탬프·체크섬 6바이트 외 동일)으로 수용했다. 시험판: 공유 `temp/Syw2plus_patch/20261007_lap1151_work_htr3/user_test_staging/` 4파일(`_inmm.dll` `8a3837fb9ef97c33bf60b451bdd47ca066a7e655b482ac9c9a2b5f2b72011d5f`·`.bat` 2개 lap1135판 byte 동일·안내문 lap1151). `260921_temp` 새 폴더 배치는 root 몫(`loop/ESCALATE_SOL`). 확인 순서는 lap1136 요청과 같다. 공개: 브리핑 화면만 Wine 측정 프레임 간격 +4~6 ms(실제 Windows 미측정). 미검증·공개 항목은 lap1104·lap1136 요청 그대로(실제 Windows 1600×1200·1080p 표시·DxWnd·BGM·사용자 `ddraw.dll`·명시 잔여·EXE 조합). 판단 전 G1은 "사용자 시험 대기"이며 루프는 G1 독립 작업을 계속한다. 근거 `docs/history/laps/20261007_lap1152_middle_g1_htr3_review_user_trial_rerequest.md`.
- [ ] **사용자 자료 요청(lap1090 middle, 비차단·루프 정지 아님):** G7 FAIL을 만든 세이브 파일(1P 아닌 자리에서 저장한 것, 가능하면 같은 게임의 1P 자리 세이브 하나도)을 `260921_temp/save/`에 복사해 주고, 몇 번째 자리였는지 알려주면 저장된 로비 표를 직접 풀어 R4b 실패 원인(스냅샷과 실제 자리의 어긋남)을 확정한다. 없어도 work H-G7s(R5)는 진행한다. 근거 `docs/work/active/G7_MIDDLE_LAP1090_USER_FAIL_R5_SAVE_TRAILER_HANDOFF.md` §2.
- [ ] **사용자 판단 요청(lap1203 middle, G1 HD 그림 경로 다음 단계 — 비차단·루프 정지 아님):** INBOX 2026-10-07 19:3x 지시(원본 추출 → 업스케일러 → 변환·적용)의 도구·엔진 준비가 끝났다. lap1202 H-HDA0가 전체 stand-in 팩 한 디렉터리(29,957파일)로 실게임을 확인했고, lap1203이 독립 재계산(불일치 0)으로 수용했다. stand-in 그림은 화질 이득이 없어 시험판은 다시 만들지 않았다. 선택지: (1) 루프가 업스케일러 입력 묶음(1배 인덱스 PNG, char·tile·fnt 43,622프레임 약 0.6 GB)을 만든다 → 사용자가 업스케일 → 루프가 변환·팩·격리 확인·시험판, (2) 이미 결과가 있으면 위치를 알려 준다(사양: Claude Docs "Syw2plus HD 스프라이트 사양", 경로 `hd/<원본 상대경로>/<프레임4자리>.png`), (3) 나중에 — 루프는 G1 잔여 backlog를 계속한다. 공개: 디스크 여유 6.8 GB라 (1)·게임 run 전에 확보가 필요하다(root 대상). V2s W-1 gate(Scale2x로 설명 안 되는 흑색 ≤2,000)가 stand-in 전체 팩에서 634인데, 실제 업스케일 팩은 더 커질 수 있다. 넘으면 그때 gate 의미를 다시 묻는다(지금 완화 안 함). 근거 `docs/history/laps/20261009_lap1203_middle_g1_hda0_review_milestone_boundary.md` §5~6.
  - **사용자 결정(2026-10-09 13:52 KST): (1) 입력 묶음 만들어줘.** → **lap1207 middle 안내(묶음 준비 완료, 사용자 차례 — 비차단·루프 정지 아님):** lap1206 work가 만든 묶음을 lap1207 middle이 새 스크립트로 전수 재계산(개수·SHA·형식 불일치 0)하고 실제 업스케일러 같은 모의(부드러운 2배·RGB/RGBA·일부만)로 돌려받기를 확인했다.
    - **위치:** 공유 `temp/Syw2plus_patch/20261009_lap1206_work_hdu2/upscaler_input_1x/` — 폴더 `char`·`tile`·`fnt` 아래 840개 하위 폴더, 그림 **43,622개(약 95 MB)**, 목록·SHA `upscaler_input_1x.manifest.sha256`(`007bc9d7…`). 옆 `ref/`는 루프 참조라 건드리지 않는다.
    - **그림:** 원본 1배, 256색 인덱스 PNG(게임 팔레트), 투명 = 색 254(분홍 252,224,252)를 PNG 투명으로 표시.
    - **돌려줄 때:** ① 정확히 가로·세로 **2배**(다른 크기는 변환 거부) ② **같은 폴더 구조·같은 파일 이름 `NNNN.png`**(이름 뒤에 `_out` 등이 붙으면 무시됨) ③ PNG **RGB·RGBA 모두 가능**(색은 루프가 팔레트로 되돌리고 윤곽은 원본 실루엣을 2배로 강제) ④ **투명(알파) 유지 모드 권장** — 알파를 무시하는 업스케일러는 분홍 바탕이 그림 가장자리에 섞인다(모의에서 윤곽 안 화소 약 10%가 분홍 쪽으로 오염) ⑤ **일부만 해도 된다** — 빠진 그림은 지금처럼 Scale2x로 남는다. 전부 투명한 그림 10,782개는 건너뛰어도 된다 ⑥ 결과 폴더 위치를 알려 주면 루프가 변환·팩·격리 실게임 확인·시험판까지 한다.
    - 공개: 업스케일해도 이 경로로 쓰이지 않는 558개(파일 끝 조각 502·raw 56)와 이름 충돌 106개가 있다. 실제 업스케일 팩은 V2s W-1 unexplained(stand-in 634)를 키울 수 있고, 2,000을 넘으면 그때 다시 묻는다. 근거 `docs/history/laps/20261009_lap1207_middle_g1_hdu2_review_user_guide.md`.

- [ ] **lap1230 middle 독립 확인 — H-TR2611 기술 수용 정정/승격 대기:** lap1223 TR-1 두 pair의 PASS와 후보 raw `trace_close=FAIL`·`run_id=unknown`·summary0 실질 충돌 확인. lap1226 root 수용은 현재 **HOLD**로 기록하며 과거 원문·raw·2611 전달 사실은 보존한다. lap1229 fresh2612 종료 근거는 국소 확인 PASS이나 전체 기술 수용/시험판/사용자 마일스톤은 미승인. 승격자는 historical 수용·전달판 처리를 재판정하고 현재 source 전체 Fast를 확인한다. 상세 `docs/history/laps/20261010_lap1230_middle_g1_historical_conflict_confirm_escalation.md`, `loop/ESCALATE_SOL`.

## lap1257 — HD 팩 시험판 전달 전 독립 검수 HOLD

- INBOX23:43 전달 사전승인 유지. 스테이징26,256파일(txt0)·팩/DLL/SHA·입력/pixel/owned cleanup 확인; 새게임60초/1,200 presents clean. pair raw에는 transient stale243/69 두프레임(각다음present0)이 있어 최신stale0 조건의 수용범위를 root에승격, 전달0·G1미완료. 제품FAIL/WindowsPASS로쓰지 않는다. 상세 `../history/laps/20261010_lap1257_middle_g1_htrhd2613_raw_stale_hold.md`.

## lap1280 — H-HDSINGLE fresh middle HOLD / 승격 인계

- 사용자 승인 요청으로 바꾸지 않음: `_hd` 후보3SPR/11frame 원본투명mask 불일치(18,872px), sourceRLE→candidate raw 판별충돌. 기존 roundtrip counts/exact PASS 원문 유지·전체기술수용HOLD, 전달0. root/Sol은 `loop/ESCALATE_SOL`의 재현·work수리계획을 확인한다. 사용자 G1/Windows 확인은 여전히 미결. 상세 `../history/laps/20261013_lap1280_middle_hdsingle_native_collision_hold.md`.

## 2026-10-14 — 사용자 요청 ESL2608 G1 빠른 시험판 전달

- 새 요청 범위: 2608용 G1만 제작·전달, 빠른 관련 검사만; 상세 Windows/게임 시험은 사용자 담당. 다른2614/G5 작업·현재 큐·미결 승인 불변.
- 전달: `260921_temp/G1_1600x1200_시험판_20261014_2608/`, 773파일/183,486,304B(769 HD+G1 DLL+3 bat), 복사 후 전체 SHA 일치. 기존 전달물 덮어쓰기·원본 변경·txt 생성·EXE 변경·커밋0.
- 대상 EXE SHA256 `bf39cb73f395d677a1c27fda01698f849b23973a39fd9be8b22af0010cb60f27`; 재사용 G1 DLL `6dc88f98110975acc443c29d38eb738289c11df2d68165e0b98e2545edc49b7d`. 원본 DLL 및 EXE·후보 SHA 불일치 시 실행 거부. 배치파일은 원본 DLL을 별도 백업·복원하며 복사 실패 시 중단.
- 빠른 독립 정적 검수 PASS: G1 hook/DirectDraw old bytes50개 일치, renderer code 동일,4 imports 지원, 포함 HD769개 원본 일치·기존 후보 SHA 일치. 버전 그림 차이9개+보수적4개 제외=13개는 원본 fallback. 증거 공유temp `20261014_003410_middle_2608_g1_static/final-readiness-review.json` 및 `root-delivery.json`. 전체 make check·새 빌드·실제 게임·Windows 배치 실행·장시간·멀티 SKIP(사용자 빠른 테스트 범위). 제품 G1 달성/음악/안정성 PASS 아님.
- 사용: **완전한2608 게임 폴더 사본**에 전달 폴더의 내용(`char/fnt/tile` 구조 포함)을 복사 → `g1_2608_on.bat`. `g1_2608_off.bat`은 원본 DLL로 복원 후 실행, `g1_2608_restore.bat`은 DLL 복원만. 지정 전달 폴더는 게임 전체/EXE를 포함하지 않음. 기존 `_hd` 교체 파일도 원복하려면 사전 백업한 게임 폴더 사용.
- 사용자 확인 대기:1600×1200 표시·그림/조작·음악·플레이 안정성. 이것은2614 시험 결과나 기존 G1 미결 승인을 대체하지 않음.

## 2026-10-14 — 2608 G1 인게임 진입 확인 / legacy 두 판 G1 병용 실행기 전달

- 사용자 범위: 순정2608+G1 구동→인게임 진입까지만; 추가 요청 `legacy_2608/`의 실제 두 EXE를 G1과 병용 가능하게. 상세 시험/장시간/통합 기능 시험은 이번 범위 아님.
- 순정2608+현재G1 실제격리 Wine1run PASS(entry-only):EXE `bf39cb73…`,DLL `6dc88f98…`,HD769,PS3 진입·tick 진행·G1 hooks active·PS3 presents271·1600×1200. owned prefix pids empty/game copy 제거. 캡처 공유temp `captures/20261014_004925_g1-saved-candidate_3800439_ps3_start_1791906565774559158.png`; summary/raw `20261014_g1_2608_entry_smoke/`. 별도nearest-oracle BLOCKED는 보존하며 화질/G1 마일스톤 PASS로 승격하지 않음.
- 새 전달폴더 `260921_temp/G1_1600x1200_시험판_20261014_legacy2608/`:777파일(769HD,DLL,원복BAT,일반/자리고정on/offBAT4개,변경없는legacyEXE사본2개), 복사 SHA 모두 일치. 원래 `legacy_2608/`·순정2608용G1폴더는 별도대상이라 그대로 보존(대체/덮어쓰기0).
- 정확한legacy원본SHA:일반 `2e81ec32482070929a4405415f7c8c0635d966b655107aab47194b2f657fe55b`, 자리고정 `34c2cb5c1049dcafe751a76686cc7618dae648a9b0b98760df67b98e1cd9330d`. 두 EXE의 현재G1 old bytes50곳/renderer/import 동일을 fresh sol 확인. EXE 변경0,새실행기는 해당 이름/SHA만 허용·기존원본DLL백업과복사실패중단/원복유지.
- 사용: **완전한2608 게임폴더 사본**에 legacyG1전달폴더 내용을 모두 복사(두 EXE 이름 유지) → 일반판 `g1_2608_legacy_normal_on.bat` / 자리고정판 `g1_2608_legacy_fixed_on.bat`. 각 off BAT는 원본DLL로 복원 후 실행, `g1_2608_restore.bat`은 DLL만 원복. HD 교체 원복은 백업한게임사본 사용.
- legacy 두 조합의 새 DLL/HD 실제게임 및 Windows BAT 실행 SKIP; 정적 호환만 확인. 이는 구 DLL의 과거combo 증거/다른2614세션 승인과 구분. 검수·전달증거 공유temp `20261014_004905_middle_legacy2608_g1/`.

## 2026-10-14 — G1 덮어쓰기 방식으로 전달 UX 교정

- 사용자 지시: EXE별 BAT 요구를 폐기하고, 게임폴더에 덮어쓰면 기존 EXE로 바로 실행. DESIGN G1에 같은 계약 기록. 기존 기본활성DLL 재사용·제품코드/EXE/원본 변경0·재빌드0.
- 최종 전달 `260921_temp/G1_2608_덮어쓰기_20261014/` 및 같은 이름 `.zip`:770파일/183,483,043B, **`_inmm.dll`+HD769만**(BAT/EXE/txt/별도 DLL명0). ZIP 루트도 동일. 복사 SHA 모두일치; DLL `6dc88f98110975acc443c29d38eb738289c11df2d68165e0b98e2545edc49b7d`,ZIP `6f9e0a97e91ad4e0967ccdee0d45efd73e28aeac491b971d6c293bb52f30c1d4`.
- 원복용 DLL은 적용 묶음 밖 `260921_temp/G1_2608_원복용_20261014/_inmm.dll`,stockSHA `03192987e9c877cf344874412d2c0e1a80b5d5f8b91f325771e9615feadbf160`. 게임종료 후 이 DLL만 덮어쓰면 원본 렌더러로 복귀(추가HD는 원본에서 불러오지 않음). 기존BAT식2608폴더2개+ZIP은 `260921_temp/archive/20261014_2608_BAT式旧版/`로 보존. `legacy_2608/` 실제원본EXE2개·게임입력·2613판 불변.
- actual legacy일반EXE `2e81ec32…` 한 번 격리 Wine 실행: **4개 G1 활성환경변수 제거 후 EXE 직접 실행**, 기본활성DLL로PS3·1600×1200·HD hit 확인, ownedcleanup/prefix/game회수. 별도 nearest-oracle BLOCKED는 화질승인이 아님. raw/evidence 공유temp `20261014_g1_2608_dropin_smoke/`; fresh package 검수 `20261014_013512_middle_dropin2608_g1/`. 기존순정진입증거도 동일DLL이라 재사용.
- 사용은 ZIP내용을 **완전한2608 게임폴더 사본 루트**에 덮어쓰고 기존 순정/legacy EXE 그대로 실행. 이름변경·BAT·환경변수 설정 불필요. 지원확인 범위: 순정2608+현legacy일반/자리고정의정적G1호환, 일반판실제진입. 자리고정판새drop-in실행·Windows·장시간·G2/G7/G8상세기능시험은 SKIP; 사용자담당. 2614 DLL로 쓰지 않음.


## 2026-10-14 — ESL2614 두 조합 시험 후보 전달(사용자 재제작 요청)

- 지정경로 `260921_temp/`에 `[ESL]Syw2plus 2614_G2_G5_G6_G8.exe` 및 `[ESL]Syw2plus 2614_G2_G5_G6_G8_G9_자리고정.exe` 배치. 자체50→100선택알고리즘(20-item commandwindow·overflowgroup·sidecar)+기존G6 Shift수정, G8 `min(1500+500×장수,5000)`, +G9만자리고정. G1제외.
- 일반SHA `b329faedceef517e6c5c7c3df97e1c4e3dbd2daf1f15e0be0dd3d431518a237d`, +G9SHA `e6903a394179216c1d78cd2af2635a23a39feb7e29f557fe2e049833d58dde1a`,각2080768B. fresh재빌드와복사SHA일치,입력SHA/preimage/버전거부/원복/PE비중첩/WINMM검사PASS,관련14테스트PASS. makecheck1회는5분에서중단(63passed/4skip);전체check·lint·typecheck통과아님. 기존R6동일SHA정적수용만재사용.
- **시험 후보이며실게임/Windows검증완료판이아님.** R6실제시험은PS9전관측PID소실로증거없음(게임crash확정아님). full100선택/명령/부대지정/비부대현재선택저장복원·G2전체개체수·G8장수별전비5000·G9자리순서미검증/HOLD유지. 사용자제작·전달요청을제품기술합격/마일스톤승인으로쓰지않는다.
- 사용자확인대상: 완전한2614게임사본에서실행,100기드래그/Shift추가·명령전달,Ctrl부대100기지정·recall,중요save백업후비부대현재선택저장·불러오기,일반/+G9자리비교. 전달폴더txt0,원본자동deploy0. 코드경로가참조하는2613구판은제자리보존. 빌드/복사기록 공유temp `20261014_esl2614_user_test_build/`;새하네스/실제실행/제품수정/커밋0.

## 2026-10-14 — legacy2608 G1 Windows 사용자 FAIL / Wine 두 판 진입 확인

- 최신 사용자 실측: **같은 G1 DLL+HD를 적용한 순정2608은 Windows 직접실행 정상, legacy 일반판·자리고정판은 모두 검은 화면 뒤 종료.** 이 결과가 Wine PASS보다 우선하며 Windows 병용은 FAIL/원인 미확정. 해결/정상 전달로 보고하지 않음.
- 요청된 실제Wine: 정확한일반 `2e81ec32…`·자리고정 `34c2cb5c…` 두판 +배포DLL `6dc88f98…`/HD769, 4개활성환경변수 제거·EXE직접실행, 각각PS3/1600×1200/HD hit·ownedcleanup PASS. 동일일반EXE+stockDLL 대조도PS3/800×600 PASS. raw공유temp `20261014_legacy2608_twoexe_smoke/{normal,fixed,stock}/runtime-evidence.json`. 새게임진입만의증거이며 Windows·장시간·G2/G7/G8상세기능 PASS 아님.
- freshsol PE대조:헤더/섹션/진입점 범위·ASLRoff·G1 DLL주소 비중첩·renderer권한 동일, 정적수정근거 발견0. 공유temp `20261014_121350_middle_legacy_windows_pe/loader-boundary-review.json`. 버전map 과거문구로 실제새50site검증을 취소하지 않음. 공통1600×1200모드 문제는 순정G1 정상이라는 최신증거로 우선순위하향.
- 실제Windows 예외코드/모듈/오프셋 미확보; 사용자에게 Event Viewer Application Error1000 확인법 안내. 별도진단DLL이 필요하면 역사소스의 **사본**에서만 오류기록을 추가하고, 수리판/Windows합격으로 부르지 않는다. 원본·기존전달물·진행중2614코드는 보호.

## 2026-10-14 — Windows legacy G1 오류 확인용 DLL (수정판 아님)

- 현재 Windows 사용자 FAIL 유지:순정+같은G1 정상/legacy 두판 검은화면후종료. 본기Wine 두판·stock대조PASS로해결승격하지 않음. 실제Windows 예외기록 미확보.
- 전달 `260921_temp/G1_2608_오류확인용_DLL_20261014/` 및동명ZIP: **`_inmm.dll`1개만**,SHA `cf0d638baf8b448282820ff94fca62a81b794fa2c88fbffa06a98cf0c4783e6f`(523,855B). 기존기본G1·EXE·HD·2614source불변. 이 판은 원인수집용이며 수리판/Windows합격 아님.
- 역사baseline6dc의보호된소스사본에서만 오류기록추가:공통export초기화에서unhandledfilter/EXE인접append파일,boot실제EXE/DLLbase+예외code/address/EIP/PID/TID/phase. 이전필터반환보존/재진입CONTINUE_SEARCH,예외삼키기0,DllMain/G1render변경0,exports/importDLL모듈불변(기존KERNEL32의SetUnhandledExceptionFilter만추가). 소스·build·fixture증거 공유temp `20261014_legacy2608_exception_diag_work/diagnostic-evidence.json`.
- freshsol코드/fixture검수PASS(진단준비범위):최종정확한DLL로드fixture가boot+synthetic fatal2줄197B/비정상종료1 생성. 실제게임진입1회는최종진단보완전c86후보증거이며, 최종cf0후보게임실행 SKIP로구분. 전체check/실제Windows예외재현·수정 SKIP.
- Event Viewer Application Error1000 일반탭스크린샷이 우선. 기록없으면 진단DLL을 **G1적용한테스트게임사본**의DLL에덮어쓰고같은legacyEXE실행→EXE옆 `syw2plus_g1_exception.log` 전달. 기동만로그면 정상종료/필터교체/초기기동전실패 등으로원인미판정. debugger·앱필터덮어쓰기·nonexceptionexit·파일열기실패는수집불가할수있음. 진단원복은 기존 `G1_2608_덮어쓰기_20261014/_inmm.dll`로덮어쓰기;전체G1원복은별도원복용stockDLL.

## 2026-10-14 — 실제 native-DDRAW/ASI Wine 두 판 진입 / Windows 최신 범위 정정

- 사용자 최신 실측은 **일반판 Windows 정상·자리고정판만 충돌**, 같은완전한게임폴더. 이전두판WindowsFAIL은과거기록보존; 현재공통G1실패로쓰지않음. 기존464F20예외로그가현재자리고정판의것인지는미확인.
- 사용자요구대로실제파일구성으로두판fresh실행:실제긴EXE이름2e81/34c2·app-localddraw UltimateASIloader ad5…·syw2x.asi a320…·G1진단56de… loaded, `ddraw=n,b`, G1활성환경변수없음, naturalUI→PS3,각1600×1200게임캡처/256관측. 소유PID/창자손관계·DLL SHA·실행회수freshsol확인. normal/freegame복사본·prefix프로세스없음. raw공유temp `20261014_legacy2608_entry_normal/artifacts/`·`20261014_legacy2608_entry_fixed_start/artifacts/`.
- 2개이전native시험의창선택BLOCK/FAIL은그대로보존. 이번은해당privateadapter선택오류를고친뒤별도실행한결과이며과거FAIL→PASS변조0. trace_close/run-id충돌은유지:정상detach/flush PASS아님, **진입증거만**수용. Windows/G9기능/장시간/G1마일스톤승격0.
- 실제일반/고정EXE차이는정확히4bytes/G9두곳(41F2B0 JNEimm 8B→8A,42FBB1 0FBFD2→8BD390). 헤더·G1렌더코드는동일. 추측원인에의한EXE/게임코드수정0. 주소/최신판정 `analysis/memory_maps/g1_esl2608_windows_surface_lock_fault_20261014.md`.
- 진단context확장56de는별도공유temp에서만준비·검수, 아직일반배포판교체/전달0. 미확정자리고정Windows예외를가리는NULLguard/플러그인비활성/rowtable수정은안함. 현재직접Windows재현환경없음.


### 위2614 시험후보 — 2026-10-14 실게임 부분 확인(전체승인아님)

- 격리Wine privatecopy/진단fixture조건 양판92unique native이동·정지/그룹재호출/currentselection save-load 확인. EOF92UID와직접loaded92UID순서일치. 생성100중8미선택으로100전구간완료아님;새Windows/100기/안정성마일스톤합격으로쓰지않는다.
- source/전달EXE SHA동일(b329…/e690…),원본deploy/재배치/커밋0. G2>1200/G8hero5000/G9자리순서/공격hit/Windows 미검증. R8fixture115 supplyprecheck거부는진단도구의사전조건이며nativeG8통과/실패가아니다.
- raw/독립결과 공유temp `20261014_esl2614_scenario_r7/{general,g9}/input_case/`, 독립검수 `20261014_esl2614_two_combos/independent_review/r7_final_actual_boundary.md/json`. 실제save/manifest는공유temp raw에보존,privategame/prefix/PID정리완료. 전체HOLD 유지.

## 2026-10-14 — 사용자 Windows 재시험용 정확한 Wine 실행확인본

- 사용자 질문 “여기서 된 판을 내가 시험하면 된다는 뜻인가?”에 맞춰 native-DDRAW/ASI 포함 Wine 두판 실제진입에서 쓴 **동일SHA**를별도전달: `260921_temp/G1_2608_실행확인본_20261014/` 및동명ZIP, DLL `56deacef30a7b68372a7b22935e58a9ac26f0450e6c17685271029a827d8b83b`+기존HD769,770파일복사SHA일치,BAT/EXE/txt0.
- 진단로그기능포함한실행확인본이며 **Windows 자리고정 충돌 수리판아님**. G1render·실제legacy EXE 변경0,Windows일반정상/고정FAIL미해결. 기존배포판은별도용도라보존,덮어쓰기0. 시험방법은새묶음을같은완전한게임폴더사본에덮어쓰고기존자리고정EXE직접실행. 실패시EXE옆 `syw2plus_g1_exception.log`에ESI/AV접근정보/caller포함. 전달기록 공유temp `20261014_legacy2608_windows_fault_464f20/exact-tested-delivery.json`.

### 2614 위두시험후보 — 2026-10-14 요청 범위 실게임 기술 확인 완료

- 사용자“될때까지”에따라92부분종료를넘어native100모바일선택/부대/현재선택UID순서save-load/이동·정지확인. G9명시general-native-save fixture replay100복원/명령,8owner동시1361engine개체/G8hero0..8단계1500–500–5000/clamp/G9같은file-backedmap시작자리2회+control대조를독립Sol원시검수수용. 요청범위의 **scoped 기술PASS**,사용자전체제품/Windows/장기마일스톤PASS아님.
- source6f3f…/전달EXE b329…/e690…불변,추가수정·재배치·commit·txt0. 양파일기존`260921_temp/`그대로. 모든측정은privateimport-name adapter/진단enginefixture/격리Wine이며자연생산/멀티/Windows/soak아님. G9자체새게임100선택/자체100save와general-save replay는구분.
- 공격100행전달관측은intendedenemy100focus와구분. R38friend4051을찍어99cmd4+clickedself1관측,enemyHP피해는기존autoaggro포함. R40actualenemyHP339→169/100aggregateattackcommand이나동일적100activeUID·배타적클릭피해미확인. singleplain drag100/전체4093exhaustion/1361save-load 및wholemakecheck(63pass4skip뒤중단)도PASS로쓰지않음. root추가공격조건으로무한입력시험을하지않고기본요청충족범위로종료. 자세한case/SHA/실패/독립최종판정은[카드](../work/active/ESL2614_TWO_COMBOS_20261013.md)에보존.


## 2026-10-14 — 사용자 요청: 2608 G1 타이틀 상태 표시 + R5 두 EXE 통합 덮어쓰기 전달

- 전달 폴더 `260921_temp/G1_2608_R5_통합_덮어쓰기_20261014/`, 동명 ZIP. `_inmm.dll` 1개 + HD769 + 일반/시작자리고정 EXE2 = 772파일/185,659,820B. BAT/안내txt/장부JSON 없음. 완전한 2608 게임 폴더 사본에 **폴더 내용**을 덮어쓰고 새 R5 EXE 중 하나를 직접 실행한다(완전한 게임 자체를 포함한 묶음 아님).
- 타이틀 왼쪽 아래 `G1 HD (1600X1200) ON`: 실제 활성 G1의 800×600→1600×1200 8bpp 프레임 합성 경로·PS9에서만 기존 locked destination에 그린다. 인게임 표시0, EXE/타이틀 자산에 고정 문구를 굽지 않음. 모드 표시이지 모든 그림의 HD 사용/Windows 안정성/G1 완료 승인이 아니다. 초기 GDI 미표시·별도Lock판 깜박임은 실패로 보존했고, 최종판은 추가Lock/GDI 없이 같은 프레임에 합성한다.
- DLL SHA256 `a33c4cb3eb8406c561556e20581516a1862e0a83503810b475fdd5d8359a18da`; ZIP `38f48faf38a5e006bfdda507e5696f2f2cc49cdb87201d5127c3f5101354995a`. 보호 `patch_history/[ESL]Syw2plus 2608.exe` SHA `bf39cb73f395d677a1c27fda01698f849b23973a39fd9be8b22af0010cb60f27`에서 기존 shop/G2/supply/G5/G6/G7 순서로 신규 재조립. 일반 R5 `b582fb1969e8e08076cc69ef93bd99669f65baefebfb9e4d4f88c2b8d90a2dfd`, 자리고정 R5 `acf5bd3d7f4657d95cc9bc4db3621dd4184d823416719095c3b714f0f0cbf1a4`, 정확히4B/두G9위치만 다름. 요청하지 않은 AI표 편집 동기화·추가 procedural G9는 넣지 않음.
- 최소 검사: recipe 59 passed/5 skipped, portable C 게이트·글자·음성조건·캔버스 경계 PASS, private DLL build PASS. fresh Sol의 소스/ABI/기계검사/원본불변/최종실측 독립 검수 PASS. 전체 make check·상세 기능/멀티/Windows SKIP(사용자 빠른 진입 확인 범위).
- 최종 동일DLL/SHA로 일반·고정 각각 완전한 사본+fresh Wine prefix+owned Xvfb+app-local DDraw/ASI(`ddraw=n,b`), G1 env 없음 → PS9 간격 캡처4장씩 모두 정상 문구·PS3 실제 진입/인게임 표시 없음 확인. 두 prefix PID0·game copy 회수 확인. **trace-close run_id/summary FAIL은 그대로이며 정상 trace flush로 보고하지 않음. Windows 자리고정 충돌 해결판 아님.**
- 상세/source/recipe/새 캡처/SHA: 공유temp `20261014_g1_2608_title_status/`, 최종 `artifacts_stable_{normal,fixed}/`, 독립 `independent_title_stable_review.json`, 전달장부 `delivery.json`. 현재 공유2614 C/STATUS/다른 작업/legacy 원본4개 수정·커밋0.
- 대체한 오류확인/실행확인 폴더는 `260921_temp/archive/20261014_2608_통합이전/`로 이동. 이전 `G1_2608_덮어쓰기_20261014/`는 역사적 exact-SHA 시험 코드가 직접 참조하므로 제자리 불변 보존(새 사용자 적용본은 위 통합 폴더). 원복: 이전 G1 6dc DLL로 돌리거나, G1 전체 해제는 별도 `G1_2608_원복용_20261014/_inmm.dll`을 사용; 새 EXE는 추가 파일이므로 순정2608 EXE를 선택하면 기능 패치 원복. 원본/개인 게임 자동 배포0.


### 위 2608 통합본 — 최신 사용자 Windows FAIL

- 사용자 “윈도우에서는 다 팅기는데” 보고: 이번 통합 묶음 Windows 실행은 FAIL로 취급. Wine 진입/타이틀 scoped PASS로 Windows 문제를 해소하거나 사용자 성공으로 승격하지 않음. 신규 예외 로그/정확한 충돌 단계는 아직 미확보.
- 입력 정정 없음: 보호 patch_history 순정2608 bf39…을 기반으로 재조립한 b582/acf5이며, legacy_2608의 옛 정상 G1 호환 EXE(9fe0/bfddd)와 이번 EXE의 실물 차이는 DLL import 이름 `_G1MM.dll`→`_INMM.dll`의 두 bytes(0xEBB5F/60)뿐. G1 DLL은 사용자 정상 `_G1MM.dll` 그대로가 아니라 기존 최신6dc 기반 진단56de+타이틀 합성 a33이므로 해당 DLL 조합 차이와 별개 환경 차이가 미확정. 현재 배포를 Windows 정상/충돌 수리판으로 안내하지 않음.


## 2026-10-14 — 사용자 지정 ESL2614 통베이스 기준 2608 R5/G1 재묶음

- **실제 통베이스 변경:** `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus - ESL2614/[ESL]Syw2plus/` 전체를 새 사본으로 복사. 예전 HQ2002 통폴더·2608 partial overlay를 사용/중첩하지 않음. 기존 원본 데이터·설정·DDraw/ASI 유지, 요청된2608 R5 EXE두개와 G1만 추가/교체. 원본2614 EXE `ac61a28f…`·HQ2002 `b56986e0…`, Data/ESLData/config/INI/ASI 등13파일 사본↔지정원본 SHA 독립일치. 대상은 여전히 **2608 R5 EXE**이고 2614 EXE로의 기능 이식이 아님.
- 새 전달 `260921_temp/G1_2608_R5_2614통베이스_덮어쓰기_20261014/` 및동명ZIP. DLL1+EXE2+HD784+source-index1=788파일/191,647,436B, BAT/안내txt/장부JSON0. **통게임 자체는 포함하지 않음:** 위 사용자 지정 통폴더의 사본에 내용 전체를 덮고, 묶음의2608 R5 EXE중하나를 실행한다. 원래2614 EXE는 WINMM을 사용하므로 이번INMM G1적용 대상으로 안내하지 않는다.
- EXE 일반 `b582fb1969e8e08076cc69ef93bd99669f65baefebfb9e4d4f88c2b8d90a2dfd`, 고정 `acf5bd3d7f4657d95cc9bc4db3621dd4184d823416719095c3b714f0f0cbf1a4`, DLL `a33c4cb3eb8406c561556e20581516a1862e0a83503810b475fdd5d8359a18da` **기존 검수SHA 그대로**, 재컴파일/버전추정패치0. 784HD는 기존2614stage에서 실제 지정베이스 원본SHA784/784 일치한 것만 복사. 동봉source-index는 원본대조장부이며a33DLL에는 runtime sourceguard 없음; 모든자산사용/다른베이스호환으로 확대하지 않음. ZIP SHA `06ab461be982c4bb554310e377c7d3ab94274a3aff1e731b5dccaef128398c01`.
- **fresh 실제 범위:** normal/fixed 사본+별도prefix/빈ownedXvfb+nativeapp DDraw 및두ASI(syw2x/hqcdd) rawmaps 확인, G1env 없음, 타이틀 연속4캡처의 문구·1600×1200 PS3 진입·인게임 문구없음·prefixPID0/game회수 PASS. 일반HD enabled1/hits265. 첫고정 run은HD0으로 보존; DLL의GetModuleFileNameA(MAX_PATH) 제한과 긴runtime 경로가 부합해 같은SHA/같은베이스를 짧은루트에서 **고정만1회** 확인:ANSI239B, HD enabled1/hits281·PS3 268 rawpresents. 실제API반환은 미수집이므로 일반적인경로문제해결/Windows충돌원인으로 단정하지 않음.
- **한계:** 기존trace-close run_id/summary FAIL 유지, helper `source_unchanged=false`는HQ sourceSHA b569와patchtargetSHA를 비교한 accounting 오류로 보존(원본불변은13critical SHA독립증거로 확인). Windows新베이스미시험, 이전묶음Windows모두튕김FAIL 미해결. G2/G5/G6/G7 상세/멀티/장시간·전체makecheck SKIP(동일코드/SHA 근거 재사용, 사용자빠른진입범위).
- 검수 `20261014_2608_r5_on_2614base/independent_2614base_review.json` + `independent_2614base_fixed_short_review.json` scoped PASS. 상세BASE/후보/선택/실행/캡처/전달SHA는 같은공유temp의 `stage-manifest.json`, `hd_selection/`, `artifacts_normal/`, `artifacts_fixed_short/`, `delivery.json`. 캡처중앙원본·첫고정HD0·과거WindowsFAIL 모두유지.
- 이전통베이스 묶음은 `260921_temp/archive/20261014_2608_旧통베이스/`에 보존. 기존코드가읽는6dc예전폴더/원복폴더/legacyEXE원본·2614다른세션C/STATUS 비접촉, 자동게임배포·커밋0. 원복은 원본통폴더사본의 `_inmm.dll`(0319…) 또는기존원복용DLL을쓰고추가R5EXE대신원래EXE를선택; 이번패치는원본게임을직접수정하지않음.


## 2026-10-15 — 사용자 최신: 2608/2614통베이스 G1 첫 실행 정상·종료 후 재실행 충돌

- 최신 Windows 실측은 **첫 실행 성공 → 종료 후 다음 실행 종료/충돌**. 이전“둘다시작충돌”은과거기록으로보존하며현재증상을반복실행문제로다시범위화. 아직정확한SKU/현재Win충돌주소는미확인;새증거없이예전464F20예외를이번증상으로귀속하지않음.
- 제품SHA/전달물변경0. 동일2608 R5일반 b582/고정 acf5 +G1a33 +지정2614통베이스로SKU별한사본·한prefix·한Xvfb·한Winevirtualdesktop을유지한연속2실행을실제확인했다. 첫PS9→PS3·소유Win32 PID단일창WM_CLOSE·exit0 → **재복사/설정초기화/serverkill 없이**같은EXE재실행PS9→PS3·WM_CLOSE exit0. 정상2/고정2회 모두Wine재실행충돌미재현. 앱사이virtualdesktop `Default,1600x1200` 유지였으므로Windows직접실행동일조건/해결PASS아님.
- 각12SetDisplayMode raw:800×600×8→1600×1200×8,중간640×480×16그대로,모두HRESULT0. 실제trace후미detach/flush/drop0 확인(과거fresh-run trace-closeFAIL을소급PASS로바꾸지않음). 공통5설정/Data/ESLData파일SHA는세시점불변;고정판은hqcdd.ini/syw2x.ini추가2개도불변. 일반판두INI미수집으로불변확대금지. Wineuser/system.reg SHA변화는기록됐으나Windows현재상태/변경주체/원인으로추정하지않음.
- 소유WM_CLOSE는창/PID확인→post_result=true→exit0이며forcedkill로첫종료를가리지않았다. 마지막에만게임/prefix/Xvfb회수·소유PID부재. 첫PS3편의artifact는둘째가같은파일명으로덮었지만중앙공유캡처원본/각SHA는보존·독립확인. 초기창선택/xdotool잘못된옵션/WM_CLOSE상태문자열helper오류로second미실행한시도는FAIL/미시험그대로보존.
- 실제증거/변화파일사본/각첫·둘째Wine로그: 공유temp `20261014_2608_restart/artifacts_final/`(일반), `artifacts_fixed/`(고정). freshSol독립검수 `independent_restart_review.json` SHA `3ef6911125d401f4c74cef3a647190f7e4e35f38c0c0e81f1e05375655bdeab4`: Wine동일사본재실행 scoped PASS / Windows원인 UNKNOWN. 설정파일손상으로단정·삭제/원본변경/추측수리/새판전달0,전체검사/멀티/상세시험0. 최소남은구분근거는현재Windows두번째실패의EXE옆 `syw2plus_g1_exception.log`(자동기록ESI/AVop/AVaddr/caller)또는실제Application Error. 별도2614 H-G1BOOT중단/STATUS는건드리지않음.

## 2026-10-15 — G1 시작즉시종료 원인 수리: hqcdd.asi 공존 DLL 2종

- 원인(사용자 Windows 로그): G1이 DllMain에서 `DirectDrawCreateEx` IAT(0x004E5018)를 먼저 바꿔 hqcdd.asi가 `ASI disabled: DirectDraw import already intercepted`로 꺼짐 → native DirectDraw에서 표면 NULL → `0x00464F20` AV(esi=0). 크래시3건 PID가 모두 hqcdd disabled PID와 일치.
- 수리(`tools/inmm_stub/direct_draw_trace.c`): IAT 대신 호출부 `0x00464374` E8 rel32(old `0x000735BF`)를 hook으로 돌리고 원본은 import thunk `0x004D7938` 경유(호출 시점 IAT=hqcdd). IAT 대상 ddraw 범위검사 완화. mirror2x 입력(GetCursorPos IAT/WndProc)은 첫 SetDisplayMode 뒤 설치해 hqcdd 매핑 다음에 /2.
- 빌드: Windows WinLibs GCC13.3 i686, `-D_WIN32_WINNT=0x0601`. export 표 기존 a33/f32와 이름·ordinal 일치. 2608 R5용 `_inmm.dll`은 현재 repo source default-on이라 a33의 타이틀 `G1 HD ON` 문구·G1DIAG 기록은 없음.
- 실제 Windows 시험(게임폴더 사본, 20초): 2608 R5 일반·2614_G2_G5_G6_G8 모두 hqcdd `ASI active`, `SetDisplayMode 1600x1200 8-bit` 수락, 예외0·생존, 2614 타이틀 화면 정상 캡처. 인게임 진입·마우스·HD·장시간·자리고정판/G9판 미검증(사용자 확인).
- 전달 `E:\gm\조선의반격_자료\G1_hqcdd호환_DLL_20261015\`: `_inmm.dll` `4b75f3e088e00d829e05f3eb9e5d35b5067f01268de29602f1f1d99e7519f9d7`, `winmm.dll` `ef8f76491024905c02a0ce3772294aff4d78e4121ebbbdaff8bc09dbdabfd6c4`. 원본 게임폴더 불변, 원복은 기존 a33/f32 DLL.

## 2026-10-15 — G1 인게임 커서 잔상 수리(hqcdd 공존판 후속)

- 증상(사용자 녹화 `Syw2plus_re/tmp/2026-10-15 22-49-29.mkv`): 인게임·로딩에서 희미한 커서 복제본이 화면 좌상단 1/4 영역에 실제 커서의 정확히 절반 좌표로 보임. 로딩 화면에선 커서 옆에 이전 화면 조각 상자(save-under)도 보임.
- 원인(정적 분석, 2608 R5·2614 전 EXE 바이트 동일): 메인 루프 `0x41C8F8`가 커서 표시 플래그 `[0x66976C]==1`이면 프레임 사이에 GetCursorPos 후 `0x41C921 call 0x437C90`. 이 함수는 Lock(0)=primary `[0xE5D434]`를 직접 잠그고 800×600 좌표로 save-under 복원/저장/커서 그리기를 함 → G1의 1600×1200 primary 좌상단에 찍히고 다음 present가 덮어 깜빡이는 잔상. 프레임별 커서는 `0x492700→0x437AF0`이 back buffer에 따로 그림.
- 수리(`tools/inmm_stub/g1_mirror2x.c`): primitives 설치 시 `0x41C921`(old `E8 6A B3 01 00`)를 빈 함수 호출로 바꿔 빠른 커서 경로만 생략. 원복은 detach에서 원래 바이트 복원. 부작용 예상: 프레임을 다시 그리지 않는 구간(로딩 검은 화면)에서 커서가 프레임 갱신 때만 움직임.
- `잠시만 기다려 주십시오` 창(사용자 캡처 `tmp/vlcsnap-2026-10-15-23h03m42s200.png`, 녹화 22초 게임 시작 로딩): 메시지 상자 `0x4B8680`이 primary를 직접 Lock→지움(`0x465950`)→초상 패널(`0x4664D0`)→Unlock→GetDC로 글자(TextOut)를 800×600 중앙 좌표로 그림 → 1600×1200 좌상단에 1배 크기. 호출부 `0x41B49D`(게임 시작, old `E8 DE D1 09 00`)·`0x42324F`(old `E8 2C 54 09 00`)를 감싸 원래 함수 실행 뒤 primary 좌상단 800×600을 제자리 2배 확대(우하단부터 역순, 작은 버퍼 모의시험 통과). 전 EXE 바이트 동일. 실제 게임 시험 전.
- 빌드: WinLibs GCC13.3 i686 `-D_WIN32_WINNT=0x0601`. 전달 `E:\gm\조선의반격_자료\G1_hqcdd호환_커서잔상수정_20261015\`: `_inmm.dll` `0c849bfe67770a84e7e224bc36c76424cec36aca10142923469110f8d96b0e3b`, `winmm.dll` `baf4d4e1d8d9251dd32fe7f93a5791aae849837c42ce370c8d3bdcfb7d4bda78`(커서+대기창 수리 포함, 같은 폴더 덮어씀). 원복은 이전 `G1_hqcdd호환_DLL_20261015` 판.
- 사용자 시험(2026-10-15): 커서 잔상·대기창 위치 해결 확인. 새 증상: 마우스가 좌우로 튐(녹화 `tmp/2026-10-15 23-28-51.mkv`).
- 튐 분석: 프레임별 커서 추적 결과 y는 같고 x만 두 값 사이를 오감(차이 거의 일정, 1600공간 약 425px). 커서 위치 `0xC0CB58`의 기록자는 메인루프 GetCursorPos(`0x41C916`)와 창 프로시저 마우스 메시지(`0x424364` 등). 정지 시 값=GetCursorPos 경로, 이동/클릭 중 값=메시지 경로(왼쪽). hqcdd(소스 확인, `SetWindowSubclass` window_proc가 client→1600 매핑)는 SetCooperativeLevel에서 창을 subclass하는데, 앞선 수리에서 G1 WndProc subclass를 첫 SetDisplayMode 뒤로 미뤄 G1이 바깥이 됨 → 메시지 경로는 "/2 후 hqcdd 매핑", GetCursorPos 경로는 "hqcdd 매핑 후 /2" → 화면 안 게임 영역 x 오프셋만큼 차이. 녹화 시 hqcdd는 창 모드(로그 끝 `Presentation mode: windowed`, 게임 영역 비중앙). 차이 크기의 정확한 일치는 미확인(창 크기 불명).
- 수리(`direct_draw_trace.c`/`g1_mirror2x.c`): DirectDraw7 `SetCooperativeLevel` vtable hook을 추가해 원래(hqcdd) 호출 직전에 그 hwnd에 G1 WndProc을 SetWindowLongA로 설치 → hqcdd subclass가 바깥, G1이 안쪽(/2가 매핑 뒤). GetCursorPos IAT는 계속 첫 SetDisplayMode 뒤. 창 탐색 스레드는 창이 이미 잡혔으면 생략.
- 전달 `E:\gm\조선의반격_자료\G1_hqcdd호환_마우스튐수정_20261015\`: `_inmm.dll` `950733fa4590afc8a369ea543585a3da1c9317663cfa248b61f60ff39cb15b83`, `winmm.dll` `cc7d2ed53b1807709eecd85c6b528279b994d608e348d8680a9eb4813d83e94c`(커서·대기창·마우스 순서 수리 포함). 원복은 `G1_hqcdd호환_커서잔상수정_20261015`. 실제 게임 시험 전.

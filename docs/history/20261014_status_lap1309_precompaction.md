# STATUS — 매 바퀴 갱신하는 기억

lap1308 work: **H-G1BOOT 사용자형 실행 하네스 옵션 추가; 원인 판정 HOLD로 Sol 승격.** App-local DDraw override lane은 PS3 진입했으나 실제 ASI module load는 미기록. no-desktop 및 결합 lane은 PS60/E_NOTIMPL 뒤 `01FC01AD`에서 과거 기록과 다른 예외 `c000001d`로 멈췄다. 주소만으로 같은 결함 판정/추측 DLL 수리하지 않음. 관련253·lint/typecheck PASS, private 사본/PID 회수 확인. 상세 `docs/history/laps/20261014_lap1308_work_g1boot_repro_hold.md`; `loop/ESCALATE_SOL`. [STATUS precompaction: 131 lines, SHA256 `521ee641332df3e0443a1c4cb9645a787a29a5c3beb676b51fb1d491c98de7cf`; full raw `docs/history/20261014_status_lap1308_precompaction.md`.]

lap1307 fresh middle: **lap1306 H-HDGUARD 최소 수리 scoped 기술 PASS / root 전달 경계 인계.** 두 파일 work diff blob·DLL/result/raw SHA 일치, 관련164회귀/doctor/lint/typecheck PASS. 보존PS3 60.755초/1216·HD100%·drop0·owned close/cleanup 독립확인; 최종raw3511행(종료요청시3465행). 구현/새게임/빌드/전체check/전달/사용자마일스톤0. 상세 `docs/history/laps/20261014_lap1307_middle_hdguard_repair_review.md`; `loop/ESCALATE_SOL`.

lap1306 work: **H-HDGUARD 전달 전 검사 결함 2건 수리·관련 Fast와 격리 2614 60초 확인 완료; fresh middle 대기.** trace buffer 1000→1200, native-reader 정상/절단 fixture에 실제 source SHA index 추가. 164 tests/lint/typecheck/build PASS; 새 DLL `f32ee619…`, Wine PS3 60.755초/1216 presents, HD100%, guard reject0/drop0/cleanup PASS. 기존 mirror validator BLOCKED와 사용자 G1 미결 유지. 상세 `docs/history/laps/20261014_lap1306_work_hdguard_failures_repair.md`.

lap1305 fresh middle: **H-HDGUARD 입력 준비 scoped PASS.** lap1303 합본14이미지/1135프레임·원본15SHA·PNG복사/팔레트/투명mask/원본픽셀3,765,900개·YAV보존을독립계산해불일치0. lap1302 누락5개 충돌은해소; 제품/업스케일/게임/전달0,사용자G1미결유지. root 다음배정인계 `loop/ESCALATE_SOL`; 상세 `docs/history/laps/20261014_lap1305_middle_hd_input_review.md`.


lap1303 work: **H-HDGUARD 누락 입력 5개 추출·14개 완성 묶음 구성.** 14이미지/1135프레임 모두 rendered·원본SHA 일치; YAV 1개 원본 보존. u2_copy_verify 1135/1135 SHA 일치·팔레트/마스크 위반0. 업스케일/게임/코드변경0. fresh middle 독립검수 대기. 상세 `docs/history/laps/20261014_lap1303_work_hdguard_extract_repair.md`.

lap1302 middle: **H-HDGUARD 전체HOLD / 입력묶음실질충돌승격.** guard129회귀·EXE/DLL/index/rawSHA·PS3 60.906초1216/drop0/ownedcleanup은국소확인. 그러나14이미지추출기록과달리실제9개만존재하고fnt/yfnt5개(567frames)가rendered=false/PNG0이다. 원인은추출image_dirs누락; 제품수정/새게임/전달0. `loop/ESCALATE_SOL`에work 최소추출수리인계, 상세 `docs/history/laps/20261014_lap1302_middle_hdguard_extraction_hold.md`.

lap1301 work: **H-HDGUARD 구현·짧은 2614 격리 실게임 완료; fresh middle 검수 대기.** native-layout 원본 SHA index 생성, DLL mismatch/missing/corrupt fail-closed. 일부러 SHA가 틀린 `char/eaglec1_hd.Spr` 1건 거부, 일치 sidecar hit391; PS3 60.906초/1216·drop/overflow0·ownedcleanup PASS. 관련129 tests·lint/typecheck·WINMM build PASS. 이미지14개 추출, YAV는 비이미지 원본 보존. 전달/마일스톤승인0. 상세 `docs/history/laps/20261014_lap1301_work_g1_hdguard.md`.

lap1300 middle: **H-TR2614G1 stage scoped 기술 PASS / root 후보고정·전달경계 인계.** 777장부/773HD·제외9·공식EXE SHA MATCH; 후보3976fa88…와lap1296 독립DLL은 PE시각/체크섬6byte 외동일. 보존PS3 60.800초/1217·drop/stale/safety0·ownedcleanup 일치. 제품수정/새게임/전체check/전달0,Windows/DxWnd/오디오·G1사용자미결. 상세 `docs/history/laps/20261014_lap1300_middle_tr2614g1_staging_review.md`.

lap1299 work: **H-TR2614G1 staged; candidate SHA `3976fa88…`; fresh middle review pending.** ESL2614 EXE SHA MATCH. 773/782 HD assets staged; nine changed-source HD assets excluded with current 2614 original SHA ledger. New candidate SHA received one isolated 60.8s PS3 run/1,217 presents, trace drop0, cleanup PASS. Two launch helpers are under `operator_helpers/` and are not part of the drop-in payload; DxWnd behavior remains unverified. No delivery/full check/user approval. Details `docs/history/laps/20261014_lap1299_work_g1_tr2614_staging.md`.

lap1298 middle: **lap1297 MCI pair 국소수용 PASS / 전체 runner HOLD 유지.** EXE/proxy·두0B로그·off800×600/on1600×1200·raw/ownedcleanup 독립대조 일치. on PS3 1,216 presents/60.749초, off dwell timestamp coverage UNKNOWN. 실제오디오·DLL무결함·Windows·G1사용자승인으로 승격하지 않음. 사용자 보고·전달후보 경계는 root 인계. 상세 `docs/history/laps/20261014_lap1298_middle_g1_mci_pair_review.md`.

lap1297 work: **G1-off/on MCI pair produced a scoped 0-call comparison; overall runner remains HOLD.** Both lanes used pinned ESL2614 EXE `ac61a28f…88bf` and WINMM proxy `0e5ef5fd…9d728`; off window 800×600, on 1600×1200. Both MCI logs exist and are 0 bytes. Off dwell was configured for 60s but lacked PS3 present coverage, so only the on lane has trace-certified dwell (60.749s). Fresh middle should review the scoped MCI conclusion without repeating the run. Details `docs/history/laps/20261014_lap1297_work_g1_mci_pair.md`.

lap1296 middle: **lap1294 raw/coverage 수리 scoped 기술 PASS.** 새 독립 계산으로 3경기 PS3 160.976/161.215/161.312초·합483.503초, HD100%·drop/overflow/stale/fallback/safety0·종료/cleanup 일치 확인. 동일 source 재빌드는 PE 시각/체크섬 외 byte-exact; 관련273·lint/typecheck PASS. 한 경기 연속480초·오디오·Windows·G1 사용자 승인은 아님. 상세 `docs/history/laps/20261014_lap1296_middle_g1_soak_review.md`; lap1295 검수요청은 전문 보존 후 소비한다.

lap1295 work: **lap1294 결과를 fresh middle/Sol 독립 검수로 인계.** 제품 변경·새 실행 없음; 이전 work가 보고한 3×160초 Wine soak는 raw와 구현을 middle이 독립 대조해야 한다. handoff `loop/ESCALATE_SOL`, 기록 `docs/history/laps/20261014_lap1295_work_middle_handoff.md`.
lap1294 work: **H-G1ON2614 raw/coverage 수리와 Wine soak 완료; fresh middle 검수 대기.** 최종 DLL `0e5ef5fd…`; 공식2614 G1-on PS3 관측 3×160초, 합483.503초. 3 lane trace drop/overflow·stale/fallback/safety 0, HD min100%, cleanup PASS. 기술·Wine 격리 결과이며 Windows/사용자 G1 승인은 아님. 상세 `docs/history/laps/20261014_lap1294_work_g1_on2614_soak_repair.md`.

lap1293 middle: **raw 충돌 독립 재확인 HOLD; root00:57 work 배정은 이미 유효.** 상위PASS/traceFAIL·drop10932·PS3 관측183.474초를 새 계산으로 확인했다. 배정 대기 문구를 최신 INBOX와 맞췄으며 재계획/게임구현/실행은 하지 않았다. 사용자 종료 규칙에 따라 근거와 승인된 work handoff를 `loop/ESCALATE_SOL`에 보존하고 승격 종료한다. 상세 `docs/history/laps/20261014_lap1293_middle_soak_root_assignment_handoff.md`.

lap1292 work: **raw 충돌을 해결하지 않고 Sol/root 승격.** lap1291 상위480초PASS와 raw event-limit/drop10932·PS29패배의 실질 충돌을 확인해 `loop/ESCALATE_SOL` 및 `docs/history/laps/20261014_lap1292_work_raw_conflict_escalation.md`에 기록. 구현/게임/테스트 변경0; 다음은 root/Sol의 확인과 명시적 work 배정.

lap1291 middle: **H-G1ON2614 독립 검수 HOLD / raw 충돌 승격.** WINMM189 export·EXE/DLL SHA·기존4 lane의 capture/trace/close는 대조 일치. 그러나480초 run raw8192행의 summary는 failed/drop10932(상위PASS와충돌), PS3 presents3623은183.474초 구간이고196.834초 뒤PS27·205.037초 뒤PS29/패배 결과다. 마지막present 뒤257.971초 관측도 누락.480초 게임내 안정성·crash0 전구간 수용 금지. 구현/새 실행/전달0; `loop/ESCALATE_SOL`에work 최소 수리 인계.
상세 `docs/history/laps/20261014_lap1291_middle_g1_winmm_raw_conflict.md`; 독립계산 공유temp `20261014_lap1291_middle_g1_winmm_review/review.json`. lap1289 PASS 원문·lap1290인계·검수전STATUS·raw는보존. INBOX00:29에따라G5는다른세션담당이며이루프에서재개하지않는다.

lap1290 work: **역할 경계 인계.** STATUS가 요구하는 다음 단계는 lap1289 G1 ESL2614 WINMM 결과의 fresh middle 독립 검수다. work 역할에서 이를 승인하지 않고 `loop/ESCALATE_SOL`로 넘겼다. 제품 코드·런타임·테스트 변경 없음; source-match는 runtime evidence에서 NO.
lap1289 work: **G1 ESL2614 WINMM proxy 구현·격리 실행 결과 생성(480초 수용은위lap1291 HOLD).** 당시4 lane/480초 PASS 원문은work기록과검수전STATUS에보존. MCI log는 기본·강제 음악 fixture 모두0 call이라 음악/효과음 UNKNOWN. Windows·사용자 입력·2614 자체 생성 save roundtrip 미검증.
상세 `docs/history/laps/20261014_lap1289_work_g1_esl2614_winmm.md`; raw `../temp/Syw2plus_patch/20261014_lap1289_g1on2614_retry1/`, `_soak1/`, `_mci/`. lap1287 G5 scope handoff/ESCALATE는과거계보로보존.

압축 전 STATUS130줄 전문은 `docs/history/20261013_status_lap1280_precompaction.md`에 byte-exact 보존했다(SHA256 `70bbe8de22709e84e566fb940867f42dc2c0967458429762ee24f9c14ab42f76`). 이전 lap1257/1256 압축 계보, 모든 승인·반려·미결·수치·실패는 그 전문과 history에 유지한다.

## 지금 상태

- G1 시험판은 root가 2026-10-13 21:17 전달; Windows/DxWnd/BGM·사용자 화질/마일스톤 결과는 미확인. lap1294 최종 DLL 기준 Wine G1-on 실제관측 483.503초를 확보했으며 lap1297 off/on MCI 비교는 두 조건 모두0 call로 scoped PASS, 단 off dwell trace coverage는 미확인. 사용자 완료/Windows 승인은 아님. G5는00:29 다른 세션 이관. G2 종료, G3 중단, G4·G7 공식 ESL 지원으로 종결; G6/G7 R5 사용자 승인 이력 보존.
- 최신 APPROVALS 사용자 결과는 legacy2608 **일반판 Windows 정상·자리고정판 충돌**이다. 이전 두 판 FAIL은 역사로 보존하며, 기존464F20 예외가 현재 자리고정판의 것인지는 미확인. 이 2608 이슈를 2614 H-HDGUARD 결과에 합치지 않는다.
- 별도 G2+G6+G8 / +G9 싱글·README 목표는 G1과 분리. 멀티 goal 제외·과거 FAIL/미검증 유지; 이번 display-only 결과는 G2 pool/부하·G9 자리순서 승인 아님.
- 정본 공식2613 `../patch_history/[ESL]Syw2plus 2613.exe` SHA `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`; 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. 모델 계약 work luna/middle sol/strategy astra high·폴백 금지; actual ID는 추측하지 않음.
- lap1278 원 후보 `20261013_lap1278_hdsingle/native_layout_retry2/`:782파일/187,750,672B(357SPR·425YTL·BMP0),39814frames·HD39155/fallback659. lap1281 새 후보 `20261013_lap1281_work_hdsingle/native_layout_repaired_r1/`:782파일/187,750,678B; 충돌3파일만 변경. lap1283에서 수리 범위 기술 수용; 기존 counts/exact PASS 원문과 lap1280 raw mask FAIL은 그대로 보존한다. 전달 후보 고정은 root 담당이다.
- lap1278 default-on DLL `3c31b86dc3eab6ad6b58980af03a4d9253f67ec2488aa148d9ad3e03d5c2bcd0`; lap1281 fresh DLL `6dc88f98110975acc443c29d38eb738289c11df2d68165e0b98e2545edc49b7d`(같은 source 구현, timestamp/checksum만 차이). lap1283 C/DLL source 불변 확인·기존 독립 재조립 근거 재사용; writer 수리·genuine raw 회귀·synthetic C 대조 PASS.
- 알려진 tree_plus reject1/runtime-mask 원인UNKNOWN, mirror validator BLOCKED·minimap exact-state HOLD·과거 클릭 전 transient stale·stale253/드래그4vs3 UNKNOWN·H-KILLS badge UNKNOWN은 그대로 보존. 이번12 lane PS3 stale/fallback/restore/clip/palette0는 과거FAIL을 PASS로 바꾸지 않는다.
- 기존2611 수용은 lap1230 raw close/summary 충돌로 HOLD; 2613/lap1272 전달 사실·사용자 결과대기 유지. 기존 전달 manifest/DLL/raw·미결 APPROVALS는 history/INBOX/APPROVALS에서 보존. H-HDU3 영상 보고 완료, 공격receipt는 범위 제외.
- lap1283 수리 fresh middle PASS 뒤 root가 후보를 고정하고 전달 직전 전체 make check 1회(exit0, 2203 passed/9 skipped, fingerprint MATCH)를 마쳐 21:17 G1 시험판을 전달했다. 사용자 Windows/G1 결과는 대기 중. INBOX23:15는 G5 100기 선택을 2614에서 활성화하고 버그를 확인하라는 새 최우선 지시다.

## 지금 막힌 것 (Blockers)

- **H-G1BOOT 원인 판정 HOLD:** lap1308 raw에서 root 보고와 같은 `01FC01AD` 주소지만 예외 종류/진행 상태가 다르고, 현재 1600×1200 SetDisplayMode는 성공한 뒤 후속 640×480이 E_NOTIMPL이다. fresh middle/Sol이 이전 root raw와 이번 격리 raw를 대조하고, G1 fallback C 수리 전 정확한 호출·실패 모드를 판정한다. 상세 `docs/history/laps/20261014_lap1308_work_g1boot_repro_hold.md`; 승격 `loop/ESCALATE_SOL`.

- **남은 G1 경계:**Wine 격리에서 G1-on PS3 483.503초는 확인했지만 Windows/DxWnd·사용자 화질/입력 승인 미결. lap1297 matched MCI logs는 off/on 모두0 call; off 60초 dwell의 PS3 trace coverage는 UNKNOWN. 음악/효과음 실재 재생도 UNKNOWN. 이 결과를 사용자 마일스톤 PASS로 승격하지 않는다.
- **별도 legacy2608 Windows 자리고정 FAIL:** 최신 실측은 일반판 정상·자리고정판 충돌이며, 이전 두 판 FAIL은 보존한다. 현재 자리고정판의 예외 귀속은 미확인이고, 2614 H-HDGUARD 결과로 해소하지 않는다.

## 다음 한 가지

**다음 한 가지: fresh middle/Sol이 H-G1BOOT의 과거 root 증거와 lap1308 raw 차이를 독립 판정한다.** 같은 `01FC01AD`만으로 동등 결함으로 취급하지 않는다. 원인/1600×1200 전환 실패 재현법이 명확해지면 work가 사전 수정 범위(모드 전환/표면 실패 시 G1 자체 비활성화·800×600 복귀)를 구현·검증한다. 전달 금지.

## 별도 세션 — ESL2614 두 조합

- 사용자 명시 범위는 G2+G5+G6+G8 / +G9 두 EXE이며 G1은 다른 세션 담당으로 제외. G5는 기존 자체50기 알고리즘을100기로 확장(공식 스위치-only와 구분).
- G6 선행 실제시험 완료:1P A/ShiftB/ShiftDragC 1→2→3 PASS; 명시적non1P snapshot-seat fixture는 native Shift-hit B에도 A만 남아 기존 문제 재현. 자연 방향키 자리이동·non1P C는 미검증. 근거 `../temp/Syw2plus_patch/20261014_g6_2614_prerequisite/profile_stock_case/report.md`; 공식SHA불변·ownedcleanup완료.
- 요청범위 격리실게임 **scoped 기술PASS/추가게임종료**:일반native100TYPE2선택·부대·orderedraw복원·이동/정지,G9명시general-native-save replay100복원/명령,실제8owner1361live/장부일치,G8hero0..8/cap1500→5000(clamp8),G9file-backed2Pmap 자리spot을같은Sol원시검수수용. 100행공격명령전달관측과enemyHP피해는동일적100동시focus/배타적클릭피해증명이아님;그root추가게이트로새게임반복하지않는다. **이번범위종료/추가실무없음**(최종27자기runtime경로부재·prefixPID0/원시save보존확인). singleplain100/Windows/멀티/soak/1361save-load/wholecheckPASS미검증보존,전체제품·사용자승인아님. 전달b329/e690불변·제품추가수정0·원본/G1/foreign비접촉. 상세 [작업 기록](work/active/ESL2614_TWO_COMBOS_20261013.md).

## 검증 상태

- lap1308: startup CLI/하네스 회귀253 passed/14.82s, `make lint`·`make typecheck` PASS. A(app-local DDraw/ASI+desktop) PS9→PS3 PASS; B(no desktop)와 A+B는 PS60 timeout, raw `01FC01AD/c000001d`, 초기1600 mode HRESULT0·후속640×480 E_NOTIMPL. 원인 수리/build/60초 재실행/전체check SKIP, 기존 DLL·EXE 불변. 단일 실무 결과를 해결 완료로 승격하지 않음.
- lap1307: 관련164 passed/39.56s·doctor/lint/typecheck PASS. work diff blob2개·원본EXE/DLL/result/raw SHA MATCH; 보존raw3511행/종료요청3465행·PS3 1216/60.755초·최대간격74ms·HD100%·reject/stale/fallback/safety/drop0·종료prefix SHA/최종raw동일·prefix PID0/game부재 독립확인. mirror2382 BLOCKED/Scale2x PASS유지. 새게임/빌드/전체check/전달SKIP; Windows/DxWnd/오디오/사용자G1미결. 공유temp `20261014_lap1307_middle_hdguard_repair_review/review.json`.

- lap1306: RED 두 건 확인 후 수리. 지정 테스트2 PASS; 관련5파일군164 passed/40.57s·lint/typecheck·WINMM build PASS. DLL SHA `f32ee619…`. 2614 private-copy Wine PS3 60.755s/1216 presents, HD min100%, guard/pack reject0, trace drop/overflow0, owned cleanup/game-copy removal PASS. 기존 mirror validator 2382 entries BLOCKED(nearest min0.614677)·Scale2x validator PASS; G1 사용자/Windows 승인은 아님. raw/hash와 다음 fresh-middle 요청은 lap1306 기록 및 `loop/ESCALATE_SOL` 참조.

- lap1305: 입력14개/1135PNG/15sourceSHA/3,765,900pixels/146전투명frame·YAV보존 독립대조PASS,불일치0. 공유temp `20261014_lap1305_middle_hd_input_review/review.py`·`review.json`; repository decoder재사용/검수계산fresh. guard/raw재검수·게임·업스케일·pytest/lint/typecheck/전체check SKIP(제품소스불변·산출물/문서검수만).

- lap1302: targeted129 passed/22.37s·doctor/lint/typecheck PASS. 보존raw3303행/PS3 60.906초1216·guard1/hit391·drop0·종료prefix/최종raw/회수일치. 입력manifest rendered=false5개와PNG부재확인으로전체HOLD. 새빌드/게임/전체check/전달SKIP,missing/corrupt-index새동적시험SKIP(정적확인만). 공유temp `20261014_lap1302_middle_hdguard_review/review.json`.

- lap1301: converter source manifest SHA-256 generation/portable SHA vectors·fail-closed DLL guard. `tests/test_g1_hd_convert.py tests/test_g1_hd_pack.py tests/test_g1_sha256.py` 129 passed; `make lint`, `make typecheck`, `make -C tools/inmm_stub -B default-on-winmm` PASS. Official2614 isolated Wine new-game PS3 60.906s/1216, intentional one-entry mismatch counter1, matching sidecars hits391, drop/overflow0, ownedclose and game-copy removal PASS. DLL `1798913f…`; raw/result and extraction details in lap1301 record. User Windows/visual/upscale/milestone acceptance SKIP.
- lap1300: SHA777/HD773+제외9·build snapshot71·DLL metadata6byte 대조일치. 보존raw3549행/PS3 60.800초1217·ownedclose prefix/terminal drop0·캡처8·PID0/game부재 PASS. 관련pytest7·doctor/lint/typecheck PASS; 새게임/빌드/전체check/전달SKIP. generic manifest미등록·mirror BLOCKED·Windows/오디오/user미결유지. 공유temp `20261014_lap1300_middle_tr2614g1_review/review.json`.
- lap1298: 기존EXE/proxy·summary/두result/raw/logSHA·PS3 dwell/trace close-prefix·최종drop0/ownedcleanup독립대조PASS. 관련회귀6·doctor/lint/typecheck PASS. 기존full-test source mismatch는재사용안함;새게임/빌드/전체check/전달SKIP. off timestamp PS3 dwell·오디오/Windows/user UNKNOWN, 전체runner HOLD 유지. 상세lap/공유temp `20261014_lap1298_middle_mci_review/review.json`.
- lap1296: 보존3 run raw/result·EXE/DLL SHA·preclose trace prefix·최종 detach/flush·24 capture SHA·prefix PID0·사본부재 독립 확인 PASS; PS3 누적483.503초(3경기)·최대 present 간격109/117/172ms. 관련pytest273 passed/28.16s·doctor·typecheck·scoped Ruff PASS. 초기 lint는별도G2 F401 FAIL, root02:07 FOREIGN_PATHS분리 후최신make lint PASS(수리주체root·G2비접촉). 현재소스 독립DLL빌드의6byte차이는COFF/export 시각·checksum뿐. 새게임/전체check/전달 SKIP; 오디오비교/Windows/user UNKNOWN.
- lap1295: role-boundary handoff only. Product code/tests/runtime unchanged; no product verification claimed. Fresh middle review requested in `loop/ESCALATE_SOL`.
- lap1294: final `default-on-winmm` SHA `0e5ef5fd…`; Wine ESL2614 G1-on same-condition soak r1/r2/r3 =160.976/161.215/161.312s, cumulative483.503s. Each3,182–3,214 PS3 presents; event_limit65536/drop/overflow0, HD100%, stale/fallback/safety0, owned process cleanup/game-copy removal PASS. Related tests273 passed/47.72s. `make typecheck`, changed-file Ruff/context/safety PASS; `make lint` blocked by separate-session unused import at `patches/esl2614/g2_port_2614.py:12`. Windows/audio/user approval SKIP. Result paths/lap detail above.
- lap1293: 기존soak raw 재계산상위PASS/nestedFAIL·8192행/drop10932·PS3 dwell3623 presents/183.474초·PS27/29 전환196.834/205.037초·누락tail257.971초 MATCH. 원본2614/후보WINMM SHA MATCH; 새게임/빌드/제품Fast SKIP(문서-only·raw충돌승격), 오디오/Windows/G1완료미검증. 공유temp `20261014_lap1293_middle_soak_handoff/review.json`.
- lap1291: 직접DLL189export/Wine name+ordinal MATCH·공식EXE/후보DLL SHA MATCH·4 lane capture크기/SHA/trace/manifest 대조PASS.480초 raw8192/drop10932·PS3관측183.474초·PS29패배 확인HOLD;MCI0 B UNKNOWN. source snapshot11개·fingerprint `02d2127d…` 기록(사용자runtime01ff…와불일치,lap1289source동일주장없음). 게임/빌드/pytest/lint/typecheck/전체check SKIP(충돌승격·문서-only);문서/안전최종검사는lap기록.
- lap1289: `make -C tools/inmm_stub default-on-winmm`; Wine system WINMM과 export 189개 name/ordinal exact MATCH; G1 DLL SHA `d2ce1637574340dbd306fa4a41a591461c899cc03c987568ee018b576ec65c53`. `pytest tests/test_g1_winmm_proxy.py` 3 passed, `make lint`/`make typecheck`/신규 3파일 mypy PASS. 전체 check SKIP(전달 직전만).
- lap1289 Wine 기존4 lane 표시/cleanup근거유지;480초에대한work 주장HD100%/stale/fallback/safety0/crash0는위lap1291에서전구간수용HOLD. app-local G1 init logged. Force-music fixture changed `0x00669598` but MCI log stayed empty. Music/effects UNKNOWN; Windows/user/milestone SKIP.

- lap1287 문서/범위 확인:2614/2613 EXE 재해시 일치·G1 key4 SHA 일치·root 전체검사 raw2203 passed/9 skipped·exit0 확인(로그SHA `499dcc216d8bd4f30e48f5bfba092f9f4140b5bd5e5f793d5eb6693f3aa6d1fc`). 과거 검사는 당시 G1 전달source만의 증거이며 현재source/2614/100기 PASS가 아니다. 현재 implementation fingerprint `688b6c39fe0bb8e20cd13d7907e33bc2a1a1558a`; 문서·안전·구현불변 최종확인은 회차기록 참조. 게임/pytest/lint/typecheck/전체check SKIP(문서-only).

- lap1283: targeted150 passed/31.69s·lint/typecheck·doctor 원본SHA PASS. 기존782파일 SHA MATCH·불변779 재사용·수리61프레임 mask/opaque0·이전11프레임18,872px FAIL 재현. lap1281의12 display lane raw/close/cleanup 일치, 후보PS3 present266/4씩3종·stale/안전계수0. source74파일 불변. 실제 게임 재실행/전체check/전달 SKIP, Windows·G1 사용자 미확인.
- lap1280: targeted150 passed/52.64s, lint/typecheck·doctor setup·independent default-on build PASS; 782파일 header/count/2x·opaque pixel 대조, **11 frame mask FAIL**, deterministic repro exit1(예상 진단FAIL). 12 lane result/EXE/DLL/raw SHA·preclose trace prefix SHA·final detach/flush/drop0·cleanup·game사본제거·`_hd.*` direct opens0 PASS. Screenshot scoped verdict94·PASS는 실제 입력/전체 그림/Windows 승인 아님. 문서/안전/diff 최종결과는 lap기록.
- lap1281: targeted150 passed/30.71s, lint/typecheck PASS; raw sentinel 충돌 RED→GREEN 회귀, true-raw writer 해석 회귀, Python mask verifier 3/3 PASS·3개 source mask difference0·opaque value mismatch0. 공식2613/G2+G6+G8/G2+G6+G8+G9 각각 new-game/save006 on/off 12/12 display-only lane PASS; EXE SHA/source unchanged/owned close/trace detach+flush/drop0/cleanup PASS, HD-named direct opens0. Scale2x PASS; mirror validator BLOCKED(nearest oracle0.775696), known tree_plus reject1는 UNKNOWN 유지. Wine 격리 결과이며 Windows·G1 사용자 확인 아님. full make check SKIP(전달 직전 규칙).
- lap1278: 150 tests/빌드/12 lane scoped 증거 유지, 전체 round-trip 수용은 위 FAIL로 HOLD. 당시fullcheck2202pass/9skip는 최종seek fix 이전 source라 전달gate로 사용하지 않음. lap569 oldwrapper는 source mismatch로 미사용.
- lap1277 SItem header/sheet 원시 근거 확인·BLOCKED 이후 root18:17 구조2배·HD있는원본만 출력·grid mapping/BMP 규칙으로 work배정. lap1276 실패후보/ESCALATE 원문과 retry1/2 보존.
- 과거 검증 수치/전달·승인·반려의 전문: 위 STATUS archive 및 `docs/history/laps/20261013_lap1278_work_hdsingle_native_assets.md`, `docs/history/laps/20261011_lap1272_work_htrvar_official2613.md`와 연결 계보. 같은 후보의 비필수 재검수 금지; 실제 새 결함은 필요한 변경분만 재검증.

## 바퀴 기록

- lap1307 middle: 두 최소수리 scoped 기술수용·이전ESCALATE byte-exact보존·root 전달직전gate 인계. STATUS의 legacy2608 최신 Windows 범위도 APPROVALS와 맞춤(일반정상/고정FAIL). 제품/하네스/원본/후보/전달변경0·커밋/마일스톤마감0.

- lap1305 middle: 누락수리입력14이미지·1135프레임+YAV1 국소수용·기존ESCALATE전문보존후root다음배정인계. 제품/하네스/원본/전달변경0·새실행/커밋/사용자마일스톤마감0.

- lap1303 work: 누락5개(fnt/yfnt) 추출, 이전9개와 합쳐14이미지·1135프레임+YAV1 입력을 새 `20261014_hd_reupscale_input_r1/`에 완성. 원본 SHA·paletted PNG/mask·복사 SHA 검증 PASS; fresh middle handoff. 업스케일/게임/제품수정/전체check0. `docs/history/laps/20261014_lap1303_work_hdguard_extract_repair.md`.
- lap1302 middle: guard/보존Wine근거국소확인·업스케일입력5개누락충돌승격. 이전ESCALATE전문보존후work최소추출인계로갱신; 제품/하네스/후보/원본/전달수정·새실행0.

- lap1301 work: native `_hd` source SHA manifest/guard, 14 image + one non-image input inventory, and isolated ESL2614 mismatch trial. Related tests/build/lint/typecheck passed; 60.906s PS3 proof preserved; no delivery or user approval. Fresh middle review handoff via `loop/ESCALATE_SOL`. `docs/history/laps/20261014_lap1301_work_g1_hdguard.md`.
- lap1300 middle: lap1299 stage/short-run scoped수용·이전marker보존후root 후보고정/전달직전gate인계. 제품/원본/후보/raw/다른세션수정·새실행·커밋/마일스톤마감0.
- lap1298 middle: MCI 기록0건국소수용·HOLD경계확인·root 보고/후보판단인계. 이전marker전문보존후ESCALATE_SOL갱신,게임/하네스/원본수정·실행·전달·커밋0.
- lap1297 work: 같은 WINMM 계측으로 G1-off/on MCI pair 실행. scoped MCI 조건·로그 비교는 PASS(두 로그0B); 전체 soak runner는 off PS3 present coverage 부재로 HOLD. 사본/prefix cleanup PASS, 게임 재실행·전달0. fresh middle 인계.
- lap1296 middle: raw충돌수리 범위독립수용·명시work MCI실측handoff. 제품/하네스수정·새게임·마일스톤마감0. 문서-only 연속상한에따라다음work는실제게임probe로복귀하며추가middle문서회차를쌓지않는다.
- lap1295 work: STATUS 큐가 요구하는 fresh middle 독립 검수 단계로 역할 경계를 인계. 제품 소스/테스트/실행 변경 없이 `loop/ESCALATE_SOL`에 raw/result/code 대조 범위 및 미검증 경계를 기록.
- lap1294 work: raw 충돌을 고치고 최종 DLL `0e5ef5fd…`의 3×160초 isolated ESL2614 PS3 관측으로 누적483.503초 확보. trace capacity/result propagation/present coverage regressions 및 full related pytest273 PASS. 남은 MCI/Windows/user unknown을 기록하고 fresh middle handoff.
- lap1293 middle: root00:57 배정존재확인·기존raw 독립재계산·승인된work수리handoff 보존. 게임/하네스/후보/원본/raw변경0;이전ESCALATE byte-exact보존후갱신·승격종료.
- lap1280 middle: 원본 형식·실루엣 대조에서 RLE/raw 충돌3파일/11프레임 확인, HOLD·원시 근거 보존·work 수리 handoff 및 ESCALATE_SOL. 게임/하네스 소스·전달·커밋 변경0.
- lap1278 및 이전 회차 전문은 위 byte-exact STATUS archive와 각 lap 기록에 보존한다.
- lap1281 work: transparent RLE run split writer 수리, 3 collision files만 새 후보에 변경, 관련 검사·12 display lane PASS, fresh middle handoff. 기록 `docs/history/laps/20261013_lap1281_work_hdsingle_rle_collision_repair.md`.
- lap1282 work 호출: 다음 순서가 fresh middle 독립 검수임을 확인하고 자기 결과 승인 없이 역할 경계를 인계했다. 제품 코드·테스트·게임 실행 변경 없음. `loop/ESCALATE_SOL`; 기록 `docs/history/laps/20261013_lap1282_work_role_boundary_handoff.md`.
- lap1283 middle: 수리 원시 대조·관련 회귀·12 lane 기존 실행 증거를 독립 확인해 scoped 기술 PASS, root 전달 경계 인계. 기록 `docs/history/laps/20261013_lap1283_middle_hdsingle_repair_review.md`; lap1282 인계 원문 보존.
- lap1286 work: G1 전달 완료·미결 사용자 결과와 새 G5 최우선 지시 사이 마일스톤 경계를 확인해 구현 전 Sol로 승격. 기존 코드/테스트 변경은 보존, 이번 회차 제품 변경·실행 없음. `loop/ESCALATE_SOL` 및 `docs/history/laps/20261013_lap1286_work_milestone_boundary_handoff.md`.
- lap1287 middle: 최신23:15 지시로 G5 제한 재개 범위 확정·구판probe 제약 확인·work 실측 handoff 기록. 이전 인계 전문 보존, root 경계 인계 유지; 구현·실행·전달·커밋0. `docs/history/laps/20261013_lap1287_middle_g5on2614_scope_handoff.md`.
- lap1289 work: 2614 full-folder runtime adapter와 G1 WINMM 189-export proxy, G1 off/on display trial + 480s run. Fast 관련 검사 PASS; MCI/Windows/사용자 완료 UNKNOWN. 첫 harness game-removal path guard 오판은 원인 수정 후 4 lane 전체 재실행. 기록 `docs/history/laps/20261014_lap1289_work_g1_esl2614_winmm.md`.
- lap1290 work: 다음 단계가 fresh middle 독립 검수임을 확인하고 자기 결과 승인 없이 역할 경계 인계. `loop/ESCALATE_SOL`; 기록 `docs/history/laps/20261014_lap1290_work_role_boundary_handoff.md`. 제품 코드·테스트·런타임 변경 없음.
- lap1291 middle:480초상위PASS/rawFAIL·실제패배결과충돌확인HOLD. 최소work수리계획·입력중첩경로·독립계산보존, `loop/ESCALATE_SOL` 갱신후승격종료. 구현/새실행/전달/커밋0.

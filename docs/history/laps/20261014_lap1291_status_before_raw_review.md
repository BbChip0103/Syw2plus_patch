# STATUS — 매 바퀴 갱신하는 기억

lap1290 work: **역할 경계 인계.** STATUS가 요구하는 다음 단계는 lap1289 G1 ESL2614 WINMM 결과의 fresh middle 독립 검수다. work 역할에서 이를 승인하지 않고 `loop/ESCALATE_SOL`로 넘겼다. 제품 코드·런타임·테스트 변경 없음; source-match는 runtime evidence에서 NO.
lap1289 work: **G1 ESL2614 WINMM proxy 구현·격리 실행 기술 결과 생성(사용자 승인/기술 최종수용 아님).** 2614 원본 SHA `ac61a28f…` 불변. WINMM 189 exports name/ordinal 일치, G1 off/on new-game/save006 4 lane PASS, G1-on 480초 PASS(3,623 presents, HD100%, stale/fallback/safety0, crash0). MCI log는 기본·강제 음악 fixture 모두 0 call이라 음악/효과음 UNKNOWN. Windows·사용자 입력·2614 자체 생성 save roundtrip 미검증.
상세 `docs/history/laps/20261014_lap1289_work_g1_esl2614_winmm.md`; raw `../temp/Syw2plus_patch/20261014_lap1289_g1on2614_retry1/`, `_soak1/`, `_mci/`. lap1287 G5 scope handoff/ESCALATE는 보존하며 최신 23:50 지시대로 G5는 G1 뒤다.

압축 전 STATUS130줄 전문은 `docs/history/20261013_status_lap1280_precompaction.md`에 byte-exact 보존했다(SHA256 `70bbe8de22709e84e566fb940867f42dc2c0967458429762ee24f9c14ab42f76`). 이전 lap1257/1256 압축 계보, 모든 승인·반려·미결·수치·실패는 그 전문과 history에 유지한다.

## 지금 상태

- G1 시험판은 root가 2026-10-13 21:17 전달; Windows/DxWnd/BGM·사용자 화질/마일스톤 결과는 미확인. 23:50 지시로 G1 H-G1ON2614가 G5보다 우선이다. lap1289 trial은 기술결과만 있고 G1 사용자 완료 아님. G2 종료, G3 중단, G4·G7 공식 ESL 지원으로 종결; G6/G7 R5 사용자 승인 이력 보존.
- 별도 G2+G6+G8 / +G9 싱글·README 목표는 G1과 분리. 멀티 goal 제외·과거 FAIL/미검증 유지; 이번 display-only 결과는 G2 pool/부하·G9 자리순서 승인 아님.
- 정본 공식2613 `../patch_history/[ESL]Syw2plus 2613.exe` SHA `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`; 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. 모델 계약 work luna/middle sol/strategy astra high·폴백 금지; actual ID는 추측하지 않음.
- lap1278 원 후보 `20261013_lap1278_hdsingle/native_layout_retry2/`:782파일/187,750,672B(357SPR·425YTL·BMP0),39814frames·HD39155/fallback659. lap1281 새 후보 `20261013_lap1281_work_hdsingle/native_layout_repaired_r1/`:782파일/187,750,678B; 충돌3파일만 변경. lap1283에서 수리 범위 기술 수용; 기존 counts/exact PASS 원문과 lap1280 raw mask FAIL은 그대로 보존한다. 전달 후보 고정은 root 담당이다.
- lap1278 default-on DLL `3c31b86dc3eab6ad6b58980af03a4d9253f67ec2488aa148d9ad3e03d5c2bcd0`; lap1281 fresh DLL `6dc88f98110975acc443c29d38eb738289c11df2d68165e0b98e2545edc49b7d`(같은 source 구현, timestamp/checksum만 차이). lap1283 C/DLL source 불변 확인·기존 독립 재조립 근거 재사용; writer 수리·genuine raw 회귀·synthetic C 대조 PASS.
- 알려진 tree_plus reject1/runtime-mask 원인UNKNOWN, mirror validator BLOCKED·minimap exact-state HOLD·과거 클릭 전 transient stale·stale253/드래그4vs3 UNKNOWN·H-KILLS badge UNKNOWN은 그대로 보존. 이번12 lane PS3 stale/fallback/restore/clip/palette0는 과거FAIL을 PASS로 바꾸지 않는다.
- 기존2611 수용은 lap1230 raw close/summary 충돌로 HOLD; 2613/lap1272 전달 사실·사용자 결과대기 유지. 기존 전달 manifest/DLL/raw·미결 APPROVALS는 history/INBOX/APPROVALS에서 보존. H-HDU3 영상 보고 완료, 공격receipt는 범위 제외.
- lap1283 수리 fresh middle PASS 뒤 root가 후보를 고정하고 전달 직전 전체 make check 1회(exit0, 2203 passed/9 skipped, fingerprint MATCH)를 마쳐 21:17 G1 시험판을 전달했다. 사용자 Windows/G1 결과는 대기 중. INBOX23:15는 G5 100기 선택을 2614에서 활성화하고 버그를 확인하라는 새 최우선 지시다.

## 지금 막힌 것 (Blockers)

- **MCI audio UNKNOWN:** G1 proxy MCI export는 정적으로 연결됐으나 기본 480초와 private force-music fixture에서 실제 MCI call 0건. 음악/효과음 PASS 금지. fresh middle은 proxy/raw를 독립 확인하고 MCI 발화 조건의 최소 다음 probe를 정한다. Windows 사용자 확인도 미결이다.

## 다음 한 가지

**다음 한 가지: fresh middle이 lap1289 H-G1ON2614 구현/raw를 독립 검수한다.** export/hook/원본불변·4 lane·480초 결과를 새 계산으로 확인하고 MCI 0-call·Windows 미검증은 UNKNOWN으로 유지한다. 이어 G1에서 남은 최소 오디오/저장·사용자 시험 경계를 정한다. G5는 G1 뒤 재개.

## 별도 세션 — ESL2614 두 조합

- 사용자 명시 범위는 G2+G5+G6+G8 / +G9 두 EXE이며 G1은 다른 세션 담당으로 제외. G5는 기존 자체50기 알고리즘을100기로 확장(공식 스위치-only와 구분).
- G6 선행 실제시험 완료:1P A/ShiftB/ShiftDragC 1→2→3 PASS; 명시적non1P snapshot-seat fixture는 native Shift-hit B에도 A만 남아 기존 문제 재현. 자연 방향키 자리이동·non1P C는 미검증. 근거 `../temp/Syw2plus_patch/20261014_g6_2614_prerequisite/profile_stock_case/report.md`; 공식SHA불변·ownedcleanup완료.
- 이 세션 다음 한 가지:2614 신규참조/저장경로의 실제 inventory 차이를 확인해 새 버전 profile 두 조합을 이식한다. G1 루프의 위 큐·승인·미결은 비접촉. 상세 [작업 기록](work/active/ESL2614_TWO_COMBOS_20261013.md).

## 검증 상태

- lap1289: `make -C tools/inmm_stub default-on-winmm`; Wine system WINMM과 export 189개 name/ordinal exact MATCH; G1 DLL SHA `d2ce1637574340dbd306fa4a41a591461c899cc03c987568ee018b576ec65c53`. `pytest tests/test_g1_winmm_proxy.py` 3 passed, `make lint`/`make typecheck`/신규 3파일 mypy PASS. 전체 check SKIP(전달 직전만).
- lap1289 Wine: official ESL2614 EXE SHA unchanged; G1 off/on newgame/save006 4 lane PASS and cleanup; 480s G1-on dwell 3,623 presents, HD100%, stale/fallback/safety0, crash0; app-local G1 init logged. Force-music fixture changed `0x00669598` but MCI log stayed empty. Music/effects UNKNOWN; Windows/user/milestone SKIP.

- lap1287 문서/범위 확인:2614/2613 EXE 재해시 일치·G1 key4 SHA 일치·root 전체검사 raw2203 passed/9 skipped·exit0 확인(로그SHA `499dcc216d8bd4f30e48f5bfba092f9f4140b5bd5e5f793d5eb6693f3aa6d1fc`). 과거 검사는 당시 G1 전달source만의 증거이며 현재source/2614/100기 PASS가 아니다. 현재 implementation fingerprint `688b6c39fe0bb8e20cd13d7907e33bc2a1a1558a`; 문서·안전·구현불변 최종확인은 회차기록 참조. 게임/pytest/lint/typecheck/전체check SKIP(문서-only).

- lap1283: targeted150 passed/31.69s·lint/typecheck·doctor 원본SHA PASS. 기존782파일 SHA MATCH·불변779 재사용·수리61프레임 mask/opaque0·이전11프레임18,872px FAIL 재현. lap1281의12 display lane raw/close/cleanup 일치, 후보PS3 present266/4씩3종·stale/안전계수0. source74파일 불변. 실제 게임 재실행/전체check/전달 SKIP, Windows·G1 사용자 미확인.
- lap1280: targeted150 passed/52.64s, lint/typecheck·doctor setup·independent default-on build PASS; 782파일 header/count/2x·opaque pixel 대조, **11 frame mask FAIL**, deterministic repro exit1(예상 진단FAIL). 12 lane result/EXE/DLL/raw SHA·preclose trace prefix SHA·final detach/flush/drop0·cleanup·game사본제거·`_hd.*` direct opens0 PASS. Screenshot scoped verdict94·PASS는 실제 입력/전체 그림/Windows 승인 아님. 문서/안전/diff 최종결과는 lap기록.
- lap1281: targeted150 passed/30.71s, lint/typecheck PASS; raw sentinel 충돌 RED→GREEN 회귀, true-raw writer 해석 회귀, Python mask verifier 3/3 PASS·3개 source mask difference0·opaque value mismatch0. 공식2613/G2+G6+G8/G2+G6+G8+G9 각각 new-game/save006 on/off 12/12 display-only lane PASS; EXE SHA/source unchanged/owned close/trace detach+flush/drop0/cleanup PASS, HD-named direct opens0. Scale2x PASS; mirror validator BLOCKED(nearest oracle0.775696), known tree_plus reject1는 UNKNOWN 유지. Wine 격리 결과이며 Windows·G1 사용자 확인 아님. full make check SKIP(전달 직전 규칙).
- lap1278: 150 tests/빌드/12 lane scoped 증거 유지, 전체 round-trip 수용은 위 FAIL로 HOLD. 당시fullcheck2202pass/9skip는 최종seek fix 이전 source라 전달gate로 사용하지 않음. lap569 oldwrapper는 source mismatch로 미사용.
- lap1277 SItem header/sheet 원시 근거 확인·BLOCKED 이후 root18:17 구조2배·HD있는원본만 출력·grid mapping/BMP 규칙으로 work배정. lap1276 실패후보/ESCALATE 원문과 retry1/2 보존.
- 과거 검증 수치/전달·승인·반려의 전문: 위 STATUS archive 및 `docs/history/laps/20261013_lap1278_work_hdsingle_native_assets.md`, `docs/history/laps/20261011_lap1272_work_htrvar_official2613.md`와 연결 계보. 같은 후보의 비필수 재검수 금지; 실제 새 결함은 필요한 변경분만 재검증.

## 바퀴 기록

- lap1280 middle: 원본 형식·실루엣 대조에서 RLE/raw 충돌3파일/11프레임 확인, HOLD·원시 근거 보존·work 수리 handoff 및 ESCALATE_SOL. 게임/하네스 소스·전달·커밋 변경0.
- lap1278 및 이전 회차 전문은 위 byte-exact STATUS archive와 각 lap 기록에 보존한다.
- lap1281 work: transparent RLE run split writer 수리, 3 collision files만 새 후보에 변경, 관련 검사·12 display lane PASS, fresh middle handoff. 기록 `docs/history/laps/20261013_lap1281_work_hdsingle_rle_collision_repair.md`.
- lap1282 work 호출: 다음 순서가 fresh middle 독립 검수임을 확인하고 자기 결과 승인 없이 역할 경계를 인계했다. 제품 코드·테스트·게임 실행 변경 없음. `loop/ESCALATE_SOL`; 기록 `docs/history/laps/20261013_lap1282_work_role_boundary_handoff.md`.
- lap1283 middle: 수리 원시 대조·관련 회귀·12 lane 기존 실행 증거를 독립 확인해 scoped 기술 PASS, root 전달 경계 인계. 기록 `docs/history/laps/20261013_lap1283_middle_hdsingle_repair_review.md`; lap1282 인계 원문 보존.
- lap1286 work: G1 전달 완료·미결 사용자 결과와 새 G5 최우선 지시 사이 마일스톤 경계를 확인해 구현 전 Sol로 승격. 기존 코드/테스트 변경은 보존, 이번 회차 제품 변경·실행 없음. `loop/ESCALATE_SOL` 및 `docs/history/laps/20261013_lap1286_work_milestone_boundary_handoff.md`.
- lap1287 middle: 최신23:15 지시로 G5 제한 재개 범위 확정·구판probe 제약 확인·work 실측 handoff 기록. 이전 인계 전문 보존, root 경계 인계 유지; 구현·실행·전달·커밋0. `docs/history/laps/20261013_lap1287_middle_g5on2614_scope_handoff.md`.
- lap1289 work: 2614 full-folder runtime adapter와 G1 WINMM 189-export proxy, G1 off/on display trial + 480s run. Fast 관련 검사 PASS; MCI/Windows/사용자 완료 UNKNOWN. 첫 harness game-removal path guard 오판은 원인 수정 후 4 lane 전체 재실행. 기록 `docs/history/laps/20261014_lap1289_work_g1_esl2614_winmm.md`.
- lap1290 work: 다음 단계가 fresh middle 독립 검수임을 확인하고 자기 결과 승인 없이 역할 경계 인계. `loop/ESCALATE_SOL`; 기록 `docs/history/laps/20261014_lap1290_work_role_boundary_handoff.md`. 제품 코드·테스트·런타임 변경 없음.

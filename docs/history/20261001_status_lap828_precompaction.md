# STATUS lap828 precompaction archive

Source: `docs/STATUS.md` before lap829 output
Original line count: 130
Original SHA256: `a10af3134a650501aaeaf80e4f10f02ca1d15e246595c6d076ac18d7dfb8cf00`

# STATUS — 매 바퀴 갱신하는 기억

lap800까지의 이전 상태 전문은 `docs/history/20260930_status_lap800_precompaction.md`에 보존했다
(127줄, SHA256 `9bc4ebaaa195db8f88834373982da51af844bc177f2b8b9c94e15ab95b6821de`).
G5 v10은 2026-09-29 사용자 3단 승인·종료(제한부). G2 ESL2608 점검은 lap806에서 마감했고
G1 W60을 재개했다.

## 지금 상태

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | lap828 work: fixed terrain buffer writer trace PASS(partial), writer→asset-key `BLOCKED/strategy`, overall HOLD | stable asset/tile key 귀속, W70 1600 pair, GDI, HD 가능 coverage 0%, 사용자 승인 |
| G2 | Phase A/B + Phase D 저장/로드·실교전·고슬롯 초상화 + Phase C rally/worker 4-way PASS; hero 정적 `ORIGINAL_PARITY`; 미니맵 gate 정적 `ORIGINAL_PARITY` | hero runtime UNKNOWN, DxWnd BLOCKED, 미니맵 runtime, 부하/멀티, 새 배포본, middle/사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류 | candidate AI 정책 없음 |
| G5 | v10 종료·사용자 3단 승인 | 멀티 env 제한 수용 |

## 지금 막힌 것 (Blockers)

현 W60 mirror는 두 hook(0x466d50/0x4664d0)의 sentinel 2×2 복제뿐이라 covered 27.05%도 nearest와 같은
그림이다(HD 가능 coverage 0%). lap823 middle은 lap821 r4~r6의 width 차이가 충돌이 아니라
PS9 메뉴 source(0x0) -> PS35 인게임 offscreen source(832x600) 전환과 64-frame census 상한의
결과임을 독립 재계산했다. writer map/header는 source width와 독립이므로 baseline attribution
480000/480000·destination probe 결과는 PASS(partial)로 수용한다. 단 semantic bbox-write를 포함한
measurement이고 W70 1600 candidate pair는 없다. 지형·HUD BltFast·GDI 텍스트·6인자 색조 blit의
DirectDraw offscreen은 lap824 r2/r3에서 PS35 `832x600 <- 800x600` `BltFast`와 caller/source/destination/state identity를
확보해 PASS(partial)로 닫았다. lap827 middle은 lap826 raw를 독립 재계산해 `0x403B20`
context 27회가 PS8 17 + PS34 2 + PS40 8, PS3 0임을 확인했다. `0x403C10`은 object+0x0c에
문자열을 복사하고, lap826 watchpoint 3개는 이미 알려진 PS3 primitive destination에서 고른 것이라
terrain consumer 발견 실험이 아니다. 따라서 `0x403B20→0x403C10` 분기는 REJECT하고 승격을 해소했다.
단 동일 원본 SHA의 현재 disassembly·기존 fresh QHD 증거가 지형 버퍼 `0x00BA3D30..0x00C0BD30`,
draw/cache `0x4324E0..0x434070`, composite `0x41BF3F→0x466280`을 직접 고정했고, lap828 r5가
3지점 write를 `0x468C93/0x468C9C`의 `rep movsd/movsb`까지 연결했다. 그러나 source pointer는
보였어도 stable asset/tile key는 보이지 않아 P1 writer→key는 `BLOCKED/strategy`다.
`loop/ESCALATE_SOL`을 읽는 승격 작업자가 다음 경계를 정한다. W70/Scale2x/GDI 구현은 보류한다.

## 검증 상태

- lap801~817의 상세 gate/raw 수치는 각 `docs/history/laps/20260930_lap*.md`에 보존돼 있다.
- lap817 최종 `make check`: **1181 passed, 5 skipped in 730.20s**, Ruff/compileall/mypy/
  `CONTEXT_PASS`, `SAFETY_PASS`, `git diff --check` PASS.
- lap818 독립 재계산: 원본/save/pair/raw/source SHA 일치, scene/source/cleanup PASS. candidate
  1,807행·summary1/drop0·mirror691·primitive25,617·coverage max27.05%·oracle1.0; 691/691 perf 필드 완전.
- saved-scene `(3,9,35)` validator PASS와 범용 `(3,5,7,9)` BLOCKED를 분리했다. 전자는 해당 fixture
  계측 work만 수용하며 PS5/7 전체 앱 경로 또는 G1 완료 근거가 아니다.
- targeted G1/S3/saved-scene 회귀 **36 passed**, DLL 현재 빌드 PASS, `SAFETY_PASS`, `CONTEXT_PASS`.
- lap818 final validation fingerprint `13e14c3efcb3a9219b3470ddc8b9d1253ab88f9f`에서 `make check`
  **1181 passed, 5 skipped in 724.41s**, exit0; Ruff/compileall/mypy/`CONTEXT_PASS`. log SHA
  `544706a48de16bb29b5ae71cb140c4f3503916827fa94f62a1b36ade6440df80`.
- lap819 strategy(문서만 변경) 후 `make check` **1181 passed, 5 skipped in 707.28s**, exit0; Ruff/mypy/
  `CONTEXT_PASS`, 사전 `SAFETY_PASS`·`git diff --check` PASS. log `logs/gates/lap819-strategy-make-check.log`
  SHA `4a09e2852fbd627c7eab2909fec59fcf469fca569da65a69d1f10583c0868b1c`. Fast일 뿐 runtime 증거 아님.
- lap820 최종 Fast: `make check` **1184 passed, 5 skipped in 729.52s**, exit0; Ruff/compileall/mypy/
  `CONTEXT_PASS`/SAFETY 선행검사/`git diff --check` PASS. log SHA
  `8b5ae1686e1dd387a1608afd3d9fc293a2c66cd3928cb4e20995554138e19787`. Fast일 뿐 P1 runtime
  attribution이나 G1 완료 증거는 아니다.
- lap820(work): 신규 P1 census detour와 --census-only save006 probe를 구현했다. 세 fresh
  run 모두 8/8 target active, raw 304행, cleanup PASS. 자세한 raw SHA와 partial 판정은
  docs/history/laps/20260930_lap820_work_g1_w70_p1_census_hooks_save006.md에 있다.
- lap821(work): census detour가 buffer 전후 bbox diff, persistent last-writer map, primary present
  boundary, destination perturbation probe를 추가했다. 수정 전 r3의 93%/6% attribution 결함을
  persistent map+semantic full-write로 고친 뒤 r4/r5/r6 모두 64 present·100% attribution·8 probe
  복원·cleanup PASS. baseline-only partial PASS이며 W70 candidate/terrain/DirectDraw/GDI 귀속은 미검증.
  상세 `docs/history/laps/20260930_lap821_work_g1_w70_p1_attribution_map_probe.md`.
- lap821 final Fast: `make check` **1185 passed, 5 skipped in 736.79s**, exit0; 선행 `make lint`/
  `make typecheck`, Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`, `git diff --check` PASS.
  Fast는 baseline census runtime 결과나 G1 완료/사용자 승인으로 승격하지 않는다.
- lap822(work): lap821 r4/r5/r6 보존 raw를 read-only로 재집계한 결과 r4/r5는
  `source_width=0`만 보이지만 r6의 64 present 중 12개는 `source_width=832`다. lap821/현재
  STATUS의 세 실행 `source_width=0` 서술과 충돌하므로 `loop/ESCALATE_SOL`을 만들고
  middle/Sol 독립 판정으로 중단했다. 제품·패치·게임 변경과 새 실행은 없다.
- lap822 final Fast: `make check` **1185 passed, 5 skipped in 736.04s**, exit0; Ruff/compileall/
  mypy/`CONTEXT_PASS` PASS, log SHA `d60c6b7753fad1e69b44d4d3966eafd760715b7661b96844b100171288ecea46`.
  Fast는 raw source-width 충돌·G1 완료·사용자 승인을 해소하지 않는다.
- lap823(middle): r4~r6 census/map/DirectDraw trace/source contract를 독립 재계산했다. r4/r5
  trace에도 census 상한 후 PS35·832x600이 49/75회 존재하고, r6는 메뉴 52회 후
  인게임 12회가 64 상한 안에 든 차이다. map 64 record/run의 header·state·stride·bytes,
  assigned 480000, dest-probe 8/8 restore, source/cleanup을 확인해 conflict를 narrative 일반화 오류로
  닫고 lap821 P1 baseline을 PASS(partial)로 수용했다. G1은 HOLD다.
- lap823 final Fast r1은 실행 중 untracked G5/G2 port test 동시 갱신으로 **1195 passed,
  5 skipped, 2 failed**(log SHA `1ea3be3df63b84f5ce96a8153e6f7af92fb4665bff732b182c915898b51472b0`)였다.
  현 파일 targeted **12 passed** 후 고정 SHA로 fresh r2 `make check` **1197 passed, 5 skipped in
  726.05s**, exit0; Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`, shell syntax, `git diff --check` PASS.
  r2 log SHA `b8f8689777d89958f83f9ae404aa022f77c9a4a20e9d87a6923308e17ecc71b1`.
- lap824 final Fast: `make check` log `logs/gates/lap824-full.log`, exit **2**, **1191 passed, 5 skipped,
  6 failed in 787.74s**. All six failures were `tests/test_model_routing.py` expectations racing a concurrent
  Claude `make check`/routing update in the shared worktree; current isolated targeted routing is **22 passed**, and
  current G1 targeted tests are **21 passed**. G1 source hashes and protected original SHA remain unchanged. This
  exit2 is not promoted to a W70 product failure, but the full Fast gate is not claimed PASS.
- lap824(work): census에 `0x403B20` old-bytes-guarded context detour와 별도 context-map, DirectDraw live descriptor/caller/source/destination/state provenance를 추가했다. r1 harness 한계(PS9에서 32 surface 표본 소진)를 surface 전용 256 상한과 artifact context-map 복사로 고쳐 r2/r3 fresh census 실행 모두 PASS했다. r3 raw에서 offscreen BltFast 102건(PS35, 832x600<-800x600, caller 0x00493CCB), terrain context 27건(`+0x30 -> 0x00403C10`), context-map terrain pixel 0을 확인했다. G1 완료 근거가 아니다.
- lap825(work): protected original raw disassembly와 fresh census로 `0x403C10`을 `renderer+0x0c` 대상 strlen/rep movsd/movsb object-copy로 닫았다. 새 isolated census는 terrain context 27건 전부 `0x00403C10`, context terrain pixels 0, offscreen DirectDraw 72건(`832x600 <- 800x600`, caller `0x00493CCB`), present attribution 64/64, cleanup PASS. 상세 `analysis/memory_maps/g1_w70_p1_terrain_context_403c10_lap825.md`와 `docs/history/laps/20261001_lap825_work_g1_w70_p1_terrain_copy_closed.md`.
- lap825 final Fast: `make check` **1197 passed, 5 skipped in 765.24s**, exit0; log SHA `98c5c93b2def4417d7f212936878f501800c5f97fc56b766ff7dd63e1af54e1e`; lint/Ruff, compileall, mypy, `CONTEXT_PASS`, `SAFETY_PASS`, `git diff --check` PASS. Fast는 terrain attribution 결과를 G1 완료로 승격하지 않는다.
- lap826(work): read-only GDB trace 하네스를 추가하고 r1~r3 fresh isolated run을 수행했다. r1의 callback self-delete GDB internal SIGSEGV를 비활성화 수리 후 r2/r3 clean detach로 재실행했다. 두 run 모두 context 27/primitive 256/context primitive 0/watchpoint 3 arm·2 hit/cleanup PASS지만 terrain 계보 연결은 UNKNOWN이다. 상세 `docs/history/laps/20261001_lap826_work_g1_w70_p1_terrain_writer_live_trace.md`; `loop/ESCALATE_SOL`로 승격했다.
- lap826 final Fast: `make check` **1200 passed, 5 skipped in 741.19s**, exit0; Ruff/compileall/mypy와 `CONTEXT_PASS` PASS. 로그 `logs/gates/lap826-full.log`; Fast는 terrain writer UNKNOWN이나 G1 완료로 승격하지 않는다.
- lap827 middle: r2/r3 source/save/cleanup·census/GDB raw를 독립 재계산해 lap826 경계 판정을 수용했고, r2 census SHA 전사 오류를 raw로 정정했다. `make doctor` ok(원본 SHA verified); 새 runtime·제품 변경은 없다.
- lap827 final Fast: fingerprint `70360815b3a7cb9a68ae020c8b27379adc3b8aa6` 시작/종료 일치, `make check` **1200 passed, 5 skipped in 725.28s**, exit0; Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`, `git diff --check` PASS. log SHA `d09b47c4dce82b8160513c9eaa4cd2cca91b6349bc166c0d8021cc28c16fd4e2`; Fast는 새 runtime/G1 완료 증거가 아니다.

## 다음 한 가지
- **다음 = strategy/Sol이 `loop/ESCALATE_SOL`의 P1 `BLOCKED/strategy`를 판정한다.** 선택지는
  `0x435593/0x435910` callers와 source-pointer/resource-table을 한 bounded lap 더 추적하거나,
  asset-key 부재를 `NOT_FEASIBLE/BLOCKED`로 닫고 다음 G1 route를 정하는 것이다. 그 전까지
  W70/Scale2x/GDI 구현은 하지 않는다.
- HD 출처 결정(lap819): 기본 (a) 원천 프레임 단위 Scale2x(팔레트 인덱스), (b) `SYW2_G1_HD_PACK` 사용자 슬롯. 최종 800 프레임 전체 필터는 금지.
- G1 사용자 3단 승인은 아직 없으며, S3 합성 패턴은 opt-in 진단으로만 유지한다.
- S3 합성 패턴은 opt-in 진단이며 실제 HD 자산이나 G1 완료로 표시하지 않는다.
- 금지: 원본/참고 저장소 쓰기, 게임 EXE/G2/G5/legacy validator 변경, 기존 raw 덮어쓰기, 커밋.

## 바퀴 기록

- lap789~800 상세는 `docs/history/20260930_status_lap800_precompaction.md`와 `docs/history/laps/`에 보존.
- lap801(work): DxWnd `/r:1`이 Wine에서 대상 EXE를 띄우지 못해 창모드 스크롤 실측 `BLOCKED(env)`(메모장 대조 성공).
  운영자 정적 판정: 배포 dxwnd.ini 프로필이 `[ESL]Syw2plus 2603.exe` 파일명에만 걸려 새 G2 파일명은 창모드 flag 미적용(INBOX 10:3x).
- lap802(work): baseline hero eligibility/생성 경로와 HQ rally writer를 xref하고 두 candidate diff를 대조했다. hero 경로·rally writer·unit init 관련 변경은 0 byte이며, `HERO_RALLY_STATIC=ORIGINAL_PARITY/RUNTIME_UNKNOWN`; 다음은 Phase D 미니맵·실교전·고슬롯 초상화다.
- lap803(work): normal/fixed_start baseline·candidate 네 EXE의 `0x41c450` 미니맵 gate와 `0x41e43d→0x4516a0` 라우터 경로를 objdump/바이트 SHA로 대조해 모두 일치했다. `MINIMAP_GATE=ORIGINAL_PARITY/STATIC_ONLY`; 다음은 실교전 4-way다.
- lap804(work): `--require-combat`로 네 EXE의 실제 UI 공격을 paired 실행해 target HP500→0·소멸을 확인했다. 초기 HP를 늦게 읽은 첫 normal baseline raw는 무효 처리하고 r2로 재실행했다. 다음은 고슬롯 초상화 4-way다.
- lap805(work): save006 저슬롯 control과 slot4092 synthetic producer를 normal/fixed_start × baseline/candidate로 fresh paired 실행했다. 네 run 모두 focus PASS, candidate producer pointer4092, source/cleanup PASS. 첫 artifact/fixture/layout 하네스 결함은 원인 수정 후 결과에서 제외하고 보존했다. 다음은 middle 독립 재검수다.
- lap806(work): Phase E는 동일 Wine/IPX blocker를 짧게 재확인해 `BLOCKED(env)`로 닫았고, G2 항목별 최종 점검 보고서와 DxWnd 새 파일명 안내를 작성했다. 제품 EXE·원본·참고 저장소는 변경하지 않았다. 다음은 middle/Sol 독립 검수다.
- lap807(middle): lap785 semantic production 합성 제거와 required-state trace reserve는 PASS로 수용했다. 다만 OFF/ON producer·minimap gate가 달라 `HOLD(paired evidence)`; 동일 조건 fresh pair를 work tier에 넘겼다.
- lap808(work): type49/nation1 fail-closed fixture와 OFF/ON 동일 gate를 추가해 fresh paired raw를 완주했다. OFF control/no-mirror validator와 ON W60 validator 모두 PASS; middle 독립 검수로 이관했다.
- lap809(middle): lap808 raw/source/SHA를 독립 재계산해 mirror-OFF control을 수용하고 S1/S2를 `FEASIBLE`로 판정했다. generic production은 raw-only N/A이고 replay-identical state hash는 아니므로 최종 증명으로 쓰지 않으며, 다음 work는 S3 디테일 경로다.
- lap810(work): `resource.spr id=0x24/frame=0` S3 진단 패턴을 구현·빌드·fresh paired 실행했다. 초기 JSON truncation과 캡처 시점 overlay 소실을 원인 추적·수정했고, 최종 PNG에서 opaque315 내부 비복제945픽셀·외부차이0을 확인했다. 다음은 middle 독립 검수다.
- lap811(middle): S3 raw·원본 SPR·PNG를 독립 재계산해 mask 좌표 일치315/315와 내부 diff945·마스크밖 diff0을 수용했다. 서로 다른 랜덤 장면 PNG는 whole-image pair가 아님을 명시했고 G1 전체는 HOLD다. 다음은 결정적 동일 장면 원본/후보 paired다.
- lap812(work): save006 same-save pair를 baseline 800/candidate W60 1600으로 완주했다. 양쪽 load/cleanup/source SHA PASS; candidate raw validator PASS(events1382, converted242, mirror270, primitive5336, oracle1.0), scene identity equal. loaded nearest ratio0.938202; selection precondition count1, minimap UNKNOWN, production UNKNOWN. 상세 `docs/history/laps/20260930_lap812_work_g1_saved_scene_pair.md`.
- lap813(middle): lap812 raw/SHA/scene/PNG를 독립 재계산해 same-save identity와 W60 presentation은 수용했다. 선택 sample race·미니맵 gate 미개방·생산 효과 혼합 때문에 전체는 HOLD이며, bridge SHA 전사 오류를 raw 기준으로 정정하고 효과 기반 input-pair work로 넘겼다.
- lap814(work): probe의 선택 polling/slot 하위워드 해석·빈 땅 클릭·gate 원복·미니맵 selected-unit effect 관측을 수리했다. r1/r2 원인 추적 후 r3에서 selection/empty/drag/minimap paired PASS를 확보했다. production `(670,490)`는 Stop 셀이라 queue effect를 주장하지 않고 UNKNOWN으로 남겼다.
- lap815(middle): r3 source/save/pair/raw/scene/input/gate/trace/cleanup을 독립 재계산해 production 외 입력 parity를 수용했다. r2 trace 수치가 r3 기록에 전사된 오류를 raw로 정정했고, `(668,540)` control/input work로 넘겼다.
- lap816(work): probe/test만 수정해 `(668,540)` no-click/click와 HQ recenter를 r1/r2/r3 fresh paired 실행했다. source/save/scene/cleanup은 PASS, camera는 r3에도 `[158,101]` 불변, slot1199/native queue는 양쪽 모두 미성립해 production `UNKNOWN(original parity)`로 닫았다.
- lap817(work): W60 trace에 `GetTickCount` 기반 per-present/primitive reinvoke 밀리초 계측과 validator 필수 필드를 추가했다. r1~r4 JSON truncation은 no-CRT/QPC 링크, 3000·4096·2300 buffer, Win32 `wsprintfA` 1024자 제한을 각각 원인 추적·수리했고, r5에서 1,807-event candidate raw parse/validator PASS를 확보했다. S3 synthetic fixture도 새 필드를 반영해 최종 Fast를 통과했다. 다음은 middle 독립 검수이며 G1 완료는 아니다.
- lap818(middle): lap817-r5 SHA/raw/source/cleanup을 독립 재계산해 saved-scene 계측 구현은 PASS로 수용했다. coverage max27.05%·비교 baseline 없음·1ms timer라 전체 coverage/성능은 PARTIAL, G1은 HOLD다. 다음 work는 공통 profile-only baseline과 남은 primitive measurement-only 분류 후 안전한 한 종류 최소 확장이다.
- lap828(work): fixed terrain buffer 3-point writer trace r5 PASS(partial); camera `[158,101]→[160,99]`, writer EIP `0x468c93/0x468c9c`, stable asset key UNKNOWN. 상세 `docs/history/laps/20261001_lap828_work_g1_w70_p1_fixed_terrain_writer.md`, raw/map `analysis/memory_maps/g1_w70_p1_fixed_terrain_writer_lap828.md`; `loop/ESCALATE_SOL` 승격. Final Fast: `make check` 1200 passed, 5 skipped in 750.56s, exit0; Ruff/compileall/mypy/`CONTEXT_PASS`, log SHA `4b7401a8e3b7cf4ec3f5bca081b58ce5d8e791d77c51782768b0745712f56e2`.

# 2026-10-03 | lap899 | G1 P4b C middle — numerical PASS / visual attribution HOLD, ESCALATE

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier(진단·계획·확인), 새 Codex API 세션. API는 실제 model ID/effort/CLI argv를 노출하지 않아 Sol/high/Fast 인증을 주장하지 않는다. 게임 hands-on 수정/새 runtime/build/subagent/유료 CLI/commit0. loop counter899 읽기만.
- 목표/가설/성공·실패식: STATUS의 다음 한 가지인 lap898 C 계측OFF fresh3를 독립 검수한다. lap858 C/lap863 기준 그대로 ratio≥0.95, p95≤baseline+16ms, 20초 PS3 fixed window, source/scene/input/cleanup, Scale2x validator, coverage first20≥264000·last20≥first20×0.9, loaded 1600×1200 non-black을 확인한다. 숫자 PASS와 사용자 화면 구성 계약은 구분한다. 이번 세션에서 새 영상 acceptance threshold를 만들지 않는다.
- 입력/순서: loop/PROMPT.md 먼저, ① 합격 기준 → ② AGENTS·최신 INBOX/APPROVALS·STATUS 전체·DESIGN1~4·MODEL_ROUTING·관련 lap898/897·P4/P4b 카드 → ③ 역할/원본 보호 → ④ 독립 검수 → ⑤ 기록 → ⑥ 해당 기계검사/한계. 시작 STOP/ESCALATE_SOL/FULL_TEST 부재. APPROVALS250/INBOX311/STATUS60줄로 soft limit 이내를 기록 전에 확인했고, 승인/반려/미결을 압축하거나 삭제하지 않았다. patch-validation skill 적용.
- 변경 파일 / source fingerprint: 이 기록, docs/STATUS.md, loop/ESCALATE_SOL. 공유 temp 검산 script/JSON만 추가. 기존 dirty tree 보존. 제품/harness/test/validator/golden/안전핀/원본/save/기존raw·PNG 변경0. HEAD5d128e2f79581050ae81b418116b3c5c9cd98355는 provenance일 뿐이고 이전 source-mismatched full-test 결과는 재사용하지 않는다.
- 원본 SHA / 후보 SHA / 환경 / 활성 인원·지도·군대·fixture: 원본 EXE 및 기록된 private EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` read-only MATCH. EXE 파일 패치/원복은 N/A(현재는 opt-in diagnostic DLL); 기존 B' hook 검수 범위를 재마감하지 않았다. Wine win32·Xvfb·save006 한 장면, 각 lane fresh private prefix6개 서로 다른 경로·완전사본 기록·game 사본 부재/cleanup 수용. 8 player records는 활성8인 부하증명 아님.

## 독립 결과

**`HOLD_VISUAL_OUTPUT_ATTRIBUTION` / C 독립 수용 보류 / G1 HOLD / 내부 ESCALATE_SOL.**
C 수치 3/3은 재계산 PASS지만 candidate 화면의 대규모 검은 마름모 영역을 현재 근거로 설명하지 못한다. 전체 이미지가 non-black이라는 조건만으로 이 관측을 해소할 수 없다. 기존 lap898 PASS(work)/lap897 B' 수치는 삭제하지 않되 새 화면 계약 수용으로 승격하지 않는다. P단계 전환 자체나 사용자 마일스톤 경계 때문에 승격하는 것이 아니라, 수치 gate와 실제 화면의 미설명 차이 때문이다.

| pair | tick ratio | p95 Δms | coverage first/last20 (PS3수) | loaded world 검정 원본/후보 표본 | 원본 nonblack→후보 black 표본 |
|---|---|---|---|---|---|
| C1 | 0.999999881259 | 11 | 337648.5 / 353001.0 (894) | 9427 / 195307 | 186119 |
| C2 | 1.000001335607 | 8 | 337648.5 / 352979.5 (888) | 9411 / 195235 | 186007 |
| C3 | 1.020353995891 | 3 | 337648.5 / 353050.5 (890) | 9417 / 195307 | 186097 |

- 성능은 저장된 rate를 믿지 않고 tick_end−tick_start / monotonic_end−monotonic_start로 재계산. 각 window20초 이상, raw state samples PS3/카메라[158,101]/tick 단조 증가, no-input. raw histogram을 합산해 nearest-rank p95 계산, count/drop/span 일치·span≥18초. source ratio/p95 기록과 MATCH.
- candidate PS3 present 전체를 순서대로 읽어 covered−stale 첫/마지막20 median 계산(894/888/890개), 모든 present `0≤stale≤covered≤480000`. 현재 raw mirror present에는 camera 필드가 없으며 fixed-camera 근거는 window의 state_samples 및 start/end다. 추가 per-present camera 증명으로 과장하지 않는다.
- 무수정 `validate_trace` 재실행 3/3 PASS이며 persisted validator와 완전 일치(outside diff·palette·lookup miss/invalid0). required input3종 true, scene.state 양lane 완전 일치. minimap/production false와 summary HOLD는 기존 UNKNOWN(original parity)로 유지한다.
- 각 build44 input/current SHA MATCH. copied stub의 2개 변형(inmm_stub.c `_imeGetTime` polling 삽입, Makefile runtime_bridge.c 추가)은 실제 builder의 정확한 변환과 일치; 그 외 copied input은 byte hash MATCH. DLL/build/manifest/trace/PNG/원본/save를 대조하고 기존278개 파일 read-audit 종료 재해시 불변. 검수 관련 source49개 inventory 보존.
- perf sections/snapshot/census/scroll 계측 raw event0, prefix에 해당 계측 파일/스냅샷 디렉터리 부재, variant census=false. 별도 전체 environment dump가 없으므로 env argv 인증으로 과장하지 않는다. generic prepare manifest.screen은1024×768이지만 실제 probe window와 캡처는 baseline800×600/candidate1600×1200, source의 Xvfb1600×1200 override와 일치한다. 이 메타데이터 차이는 화면 결손 원인으로 확정하지 않는다.

## 화면 관측 — 원인 미확정, 새 threshold 아님

- C1 baseline/loaded.png와 candidate/loaded.png를 직접 열어 나란히 검수했다. 지형·건물·HUD 배치는 같은데 후보 월드에 넓은 검은 마름모 격자가 보이고 원본에는 해당 격자가 없다. black count는 이를 좁게 수량화한 보조 진단이며 exact same-frame 비교가 아니다.
- 논리 월드 rect[0,0,800,480]의 원본(x,y)·후보(2x,2y) RGB==(0,0,0)을 비교했다. loaded 표본384000개 중 위 표의 186007~186119곳에서 후보만 검정이다. selection/drag/production/minimap 캡처에도 후보만 검정인 위치가194547~195571개로 계속 남는다(세 pair×다섯 tag 전부). 총 캡처15쌍의 수치는 공유 temp JSON에 보존했다.
- PNG는 서로 다른 프로세스/시점의 캡처이므로 black 위치 수를 정확한 동일-frame 렌더 손상 픽셀 수라고 쓰지 않는다. 그러나 반복되는 넓은 격자와 후속 캡처 지속은 육안으로 확인되며, 짧은 loaded 캡처만의 타이밍 문제라고 설명할 근거가 없다.
- raw validator의 same-frame nearest/covered oracle는 세 pair 모두 PASS다. 이것이 PNG의 최종 화면 이상을 설명하지 않으므로 제품 렌더/색상팔레트/전사/캡처 중 귀속 UNKNOWN. validator 결함·특정 writer·게임 시뮬레이션 손상으로 단정하지 않는다. 새로운 runtime/관측기/게임수정으로 원인을 억지 추정하지 않았다.

## identity / 명령 / 검증

- C1 pair SHA `d881cd8203c1e7a297baec6f52ed33443d4c398de55d0406507f5a188411353c`; DLL `ced0211437825e7442302719b58b3a609cec1c279ddd7d7fc970bd1d5842fcfd`; candidate trace `e0a62e0a0a1325dd5cf324af88a3cde132707591cc31129ca0981e057db68cdd`; loaded PNG baseline `b677a0be37951afcbb7eb1f43409c95cd6bca19a3c1f84e54d3feca4845337bb` / candidate `e7b81f851d9b1e71f585eca136b2e98921fbfa338a3290c27082f1e46e2f8b90`.
- C2 pair SHA `246ef11f2676fd805ce9cde456ebd46ca1761356a5c0736e122cfcc617eeb51d`; DLL `381970f31dbbd870936af666369cf926c2b7e1dc25f394e1d3976835321b9e38`; candidate trace `cfdc31fb26e5b008f4c253356f3529e6c04d9f0908241ecd9d0924a2f8865bd4`; loaded PNG baseline `d80ab5b1d8c3dd37026fe55cdb96bf187723ec0a514f9b49f8ac561f1ca07a53` / candidate `0c67c56bbff8e7052f46126d3a96dceca2eb1ae60a70eb95a7b6a1f41f9268c5`.
- C3 pair SHA `700657ce288d771716fc00ad35a98ef1d898fa16eb3e3599def0ff4587cec228`; DLL `d1a44fd03cb91b1d3603c3c83e8048e5afa2e5306ba3a08e805ae4e483139e6f`; candidate trace `dec48d07826b70d42d0150abb489d275558f026be6ed0e174d414c50252db974`; loaded PNG baseline `4e566d9f3eea673d6cc32f04be0b80d8bfd216359ad143062f181a605315fcc9` / candidate `e7b81f851d9b1e71f585eca136b2e98921fbfa338a3290c27082f1e46e2f8b90`.

- `PYTHONPATH=. .venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap899_middle_review/recalculate.py`: 수치 PASS3/3, overall HOLD·read-only audit 확인. script 초회는 copied stub가 원본과 동일할 것이라는 검산 가정으로 실패했고 builder의 실제 2개 변환을 대조하여 검산 script만 바로잡았다. 다음 실행은 raw mirror에 camera 필드가 있다는 검산 가정으로 실패했고 schema를 직접 읽어 PS3 subset/window camera 근거로 바로잡았다. 최종 실행 PASS; 원본/raw/제품/harness 변경0이며 미설명 필수 실패가 아니다.
- 검산 JSON SHA `d59e43d4f3c8a4ab9c3592a2f53f44b3ecb83695b78acee53927a9d2ec38ba31`; script SHA `45baaa6e31cbd03748a2c0f9c2179e67bfad39a4390e613c15716e1323f011f5`; source49 inventory `e9da73869218cb1a2779cc4356432fc1bec2e39b513af04f5eb40a24343eafed`; read-audit278 `4dcbaad76505e063b8a70e0fb1b7b7e556381232348c2e9721fb671b5c76ca6f`. 모두 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap899_middle_review/`.
- 화면 이상 발견 전 `make doctor` PASS(원본 verified; optional generic runtime manifest 부재는 제품 실패가 아님), `make lint` PASS(ruff/compileall), `make typecheck` PASS(mypy10파일). 이후 full `make check`/focused tests/새 runtime/24k/144k는 **SKIP(user unresolved-evidence stop)**. 과거 full-test exit0/source mismatch를 현재 Fast PASS로 사용하지 않는다. 종료 전 safety/context와 파일/소프트 한도 검사는 STATUS에만 보강한다.
- 회귀/한계: source 구현 수정0이므로 새로운 patch regression을 주장하지 않는다. 원본/기준/기존raw/개인세션 보호, 커밋0, 새 PNG 생성0. G2/G5 종료·G3 중단·G4 보류 유지. C 수용·D-1/P5·HUD/tinted/GDI/전체coverage≥90%·두 번째 장면·G1 사용자 승인 미검증.

## 승격 검수와 work tier handoff (조건부 제안, 구현 승인 아님)

1. 승격 작업자는 C1~3 기존 PNG/trace/DLL/build/source·검산을 독립 확인하고, 이 광범위 black 패턴의 렌더/캡처 귀속에 필요한 **최소 work 수리/probe 범위**를 명시한다. 수치 C가 충족됐다는 사실과 시각 HOLD를 함께 보존한다.
2. 수리가 필요하면 work tier가 맡는다. 우선 같은 frame의 원본800 source·HD1600 합성/최종 surface·X11 캡처를 비교해 renderer source 자체/HD 합성/표시·capture 중 어디서 검정이 생기는지 구분하는 bounded probe를 제안한다. 현재 cross-process PNG를 same-frame oracle로 둔갑시키거나 validator/임계값을 완화하지 않는다. 새 관측 장치 권한은 승격 범위 판정에 따른다.
3. 추적 가능한 구현 결함이면 work가 최소 수정→새 복사본 빌드→격리 재실행→회귀를 완주한다. C acceptance는 계측OFF fresh3 전부 유지하고 새 middle이 raw/실제 입력/시각 대조를 검수한다. 수리 전에 D-1/P5로 넘기지 않는다. 추가 planning/document-only lap을 제품 진척으로 세지 않는다.
4. 사용자 일반 작업 재허가 질문은 하지 않는다. 이 세션은 새 미설명 시각 근거 때문에 내부 ESCALATE로 끝낸다. 사용자 마일스톤/출시/커밋/원본deploy 권한으로 해석하지 않는다.

- 다음 한 가지: 승격 middle이 black 격자와 수치 PASS의 귀속 공백을 독립 확인하고 필요한 최소 work handoff를 확정한다.

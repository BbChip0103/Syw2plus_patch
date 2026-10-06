# G2 ESL2608 두 EXE paired 점검·수리 계획 — lap787 middle

## 판정과 범위

- **FEASIBLE.** 다음 work 회차는 재계획하지 않고 Phase A probe 구현·격리 실행에 착수한다.
- 대상은 `../260921_temp/`의 ESL2608 일반/시작자리고정 `1500+500×장수(7명=5000)`, 개인500,
  공용4092 두 후보의 사용자 점검·수정·새 이름 전달이다. 이는 DESIGN G2의 활성8인×전비10000
  제품 완료나 마일스톤 승인이 아니다.
- G1 W60은 lap785 증거를 그대로 보존하고 일시중단한다. G1 source/runtime 판정을 섞지 않는다.
- 기존 사용자 작업인 `local/runtime/g2_*`와 이름에 `g2shift`가 든 runtime 디렉터리는 읽거나 쓰지
  않는다. 새 실행은 `local/runtime/esl2608_lap<lap>_*` 아래 전용 game/prefix/display로 만든다.

## 고정 입력과 재생성 계약

| lane | 미패치 baseline SHA256 | 현 후보 SHA256 |
|---|---|---|
| 일반 | `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3` | `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60` |
| 시작자리고정 | `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973` | `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f` |

- `g2_esl2608_pool4092_owner500.py`로 baseline→중간 후보를 메모리 재생성하면 일반
  `2642b7f7…aa22`, 고정 `2f617567…5751`; 이어 `g2_esl2608_supply1500_500_5000.py`를 적용하면
  위 현 후보와 각각 바이트 동일하다(lap787 독립 재계산).
- 원본·현 후보를 수정하거나 최종 빌드 입력으로 쓰지 않는다. 최종본은 두 baseline에서 패치 체인을
  다시 적용해 새 파일로만 만든다. 두 빌더의 SHA/old-byte/PE-layout/비중첩/범위 거부와 `xb` 독점
  생성을 유지한다.

## Phase A — 다음 work 회차 단일 카드

### lap788 work 결과

- 새 paired probe는 `tools/g2_esl2608_phase_a_shift_probe.py`와 전용 테스트에 구현했다. baseline은 100 active fixture에서 21개 isolated row를 선별해 1/19/20, Ctrl+1 recall, 20→20 거부, remove/re-add까지 fresh PASS했다.
- normal candidate는 정확한 pinned SHA로 부팅·PS3까지 갔지만 relocated pool과 stock pool 모두 live owner0 anchor가 0개인 상태가 5회 재현됐다. 따라서 candidate Phase A는 `BLOCKED(candidate initialization)`, fixed_start는 SKIP이다.
- probe/harness 원인은 map bounds, per-unit hit offset, Shift_L timing, relocated anchor slot을 독립적으로 수리·재실행했다. baseline 최종 r18 PASS가 남아 있어 candidate blocker와 harness 입력을 구분한다.
- 다음은 candidate startup unit/existence initialization과 2608 full-tail address provenance를 middle/Sol이 확인하는 것이다. 이 blocker 해소 전 fixed_start paired나 배포/승인으로 진행하지 않는다.

### lap789 middle 독립 검수와 work handoff

- **lap788의 `candidate initialization` 제품 blocker는 기각한다. 원인은 하네스 주소 오류다.** lap788 raw의
  builder report가 ESL2608 pool `0x0112E000`, relocation delta `0xA2000`을 직접 보존한다. capacity4093의
  올바른 existence는 `0x018849F8`, stride는 `0x758`이다.
- Phase-A probe `unit_layout(candidate=True)`와 `runtime_driver` fallback profile은 delta 전 generic
  `0x0108C000/0x017E29F8`를 읽었고, `build_runtime_bridge.py --unit-pool-capacity 4093`도 같은 잘못된
  generic 주소를 DLL에 컴파일했다. stock fallback 0개는 relocation 후보의 초기화 부재 증거가 아니다.
- 9/26 probe는 pool row를 직접 읽지는 않았으므로 그 범위는 과장하지 않는다. 다만 같은 후보 두 개가
  HQ slot4092 선택·생산·저장로드를 fresh PASS한 사실은 제품 startup 실패 주장과 양립하지 않는다.
- 다음 work는 게임/EXE를 바꾸지 않는다. 먼저 build report 기반 ESL2608 unit/existence 주소를 probe,
  bridge, detailed fallback의 단일 계약으로 고치고 주소 pin/거부 테스트를 추가한다. 그 뒤 normal·fixed_start의
  baseline/candidate 4개를 모두 새 private runtime으로 재실행한다. correct address에서도 anchor가 0일 때만
  제품 startup 결함으로 다시 승격한다. 상세은 lap789 기록을 따른다.

**가설:** 사용자 Shift+클릭 신고는 풀 고슬롯, 20기 군대, 또는 부대 호출 직후 상태에서만 드러나는
선택 경로 결함이거나 filename/fixture 차이다. 최소 ESL2608 paired probe로 먼저 재현·분류한다.

1. 소유 범위는 ESL2608 전용 probe와 그 테스트, 재현된 결함의 최소 patcher 수정뿐이다. 기존 G2/G5
   probe를 복사 증식하지 말고 `runtime_env.prepare` 격리·G5의 검증된 클릭/선택 관측 유틸을 재사용한다.
2. 일반·시작자리고정 각각 baseline/candidate를 같은 맵·국가·카메라·유닛 배치로 fresh paired 실행한다.
   ESL2608 Data overlay, source/private SHA, 좌표, 슬롯, 핸들, 선택 배열20개, 입력시각, tick을 raw에 남긴다.
3. **20기 초과는 선택상한50 통합으로 해석하지 않는다.** 이 두 EXE는 stock 선택상한20이다. 활성 소유
   유닛을 20기보다 많이 둔 뒤 선택 `1`, `19`, `20` 상태를 만들고: plain→Shift 단일추가 `1→2`,
   `19→20`, 20에서 21번째 거부 `20→20`, 재클릭 제거/재추가, Ctrl+1 저장→해제→1 호출 후 Shift
   단일추가를 검사한다. 후보는 slot>1200 고슬롯도 포함한다. 중복·유령 핸들·비선택 유닛 명령 수신은 0이어야 한다.
4. PASS는 두 lane 모두 후보가 baseline과 같은 증감/거부/부대 의미를 보이고 입력 후 선택 핸들이 모두
   live·owner 일치인 경우다. FAIL이면 제품 source, harness/fixture, 또는 외부 profile 문제로 분류한다.
   추적 가능한 결함은 같은 work 회차에서 테스트→최소수리→fresh pair를 최대3회 반복한다.
5. 제품 결함이 재현되지 않아도 raw와 정확한 미재현 조건을 남기고 Phase B로 넘긴다. 원인 불명 실패가
   3회 반복되거나 baseline/raw가 충돌하면 현재 파일을 보존하고 `loop/ESCALATE_SOL`을 만든다.

## 이후 순차 게이트

### lap790 work 결과

- ESL2608 build report 기반 주소 계약을 `patches/population/g2_esl2608_runtime_layout.py`로 고정했다. probe·bridge·detailed fallback은 pool `0x0112E000`, existence `0x018849F8`, stride `0x758`를 공유하고 generic base는 거부한다. 기존 generic 4093 profile은 다른 후보 호환을 위해 보존했다.
- 주소 pin/거부 targeted pytest는 `12 passed`였고, 처음 동시 실행에서 발생한 UI gate timeout은 순차 fresh root 재실행으로 재현되지 않았다. normal/fixed_start × baseline/candidate 4개 모두 100 active fixture Phase A `PASS`다. 상세 `docs/history/laps/20260930_lap790_work_g2_esl2608_phase_a_address_repair_pass.md`.
- 제품 EXE, 원본, `../260921_temp`는 변경하지 않았다. 다음은 Phase B 명령/교전 paired 측정이며, 그 전에는 배포·승인으로 승격하지 않는다.

1. **B 명령/교전:** 동일 선택 fixture로 이동·실교전 공격·정지·홀드·순찰, 명령 직후 queue/destination과
   비선택 수신0을 paired 측정. 미니맵은 정상 UI gate를 먼저 쓰고, 원본도 닫히면 양쪽 같은 진단 gate로만 parity를 판정한다.
2. **C 생산/UI/DxWnd:** 실제 UI로 집결지를 지정하고 일꾼·장수를 실제 UI 생산해 cmd3/도착을 비교한다.
   근처 적의 원본 교전 전환(cmd4/7)은 별도 장면으로 분리한다. Wine 가상 desktop 결과를 DxWnd 증거로
   쓰지 않는다. 실제 DxWnd bundle/profile을 확보해 두 새 filename의 windowed edge/keyboard scroll을
   paired 확인하고, filename profile 누락이면 EXE 바이트가 아니라 배포 profile/안내를 수리한다.
3. **D 저장/UI/부하:** 후보 자체 N4K8 roundtrip, pinned 구 save를 후보가 읽는 fallback, baseline 자체
   roundtrip을 분리한다. 자연 장수 초상화와 합성 고슬롯 초상화를 구분하고, 대량 유닛에서 풀/list
   무결성·tick rate·할당실패·RSS를 수집한다. 24k paired 뒤 후보 두 lane 144k를 완주한다.
4. **E 멀티/전달:** 지원 환경에서 2인 동기화를 시도하되 기존 Wine/IPX blocker가 재현되면 정확한 오류와
   정적 명령/저장 ABI 대조를 남겨 `BLOCKED(env)`로 제한한다. 다른 필수 lane에 UNKNOWN/FAIL이 없고
   재현된 제품 결함이 수리된 뒤에만 두 baseline에서 최종본을 재생성한다.

## 최종 전달 게이트

- `../260921_temp/`의 기존 네 EXE를 덮어쓰지 않고 날짜/수정표식이 든 새 이름 두 개를 `xb`로 생성한다.
- source/intermediate/output SHA, 정확한 변경 byte/section, PE 경고0, 버전거부·원복 테스트를 기록한다.
- 새 `읽어주세요`에는 N4K8 구-save fallback 범위, baseline이 N4K8 save를 읽는다고 보장하지 않음,
  DxWnd filename profile, 멀티 제한, 그리고 이것이 8인×10000 G2 완료가 아님을 명시한다.
- targeted patch/probe tests 후 `make lint`→`make typecheck`→`make check`; 새 middle이 raw와 산출물 SHA를
  독립 검수하기 전 배포 PASS나 사용자 승인으로 기록하지 않는다.

## lap799 middle — Phase C hero work handoff

- lap798 rally/worker raw는 4-way 독립 재계산 PASS다. hero는 환경 제한이 아니라 현재 하네스 계약
  `HOLD`다: nation1은 live descriptor `0`인 slot7을 하드코딩 클릭했고, nation3 descriptor24도 주문
  acceptance가 없었다. 좌표 고정과 `HERO_TYPES=76..102` 범위 추측을 판정 근거로 쓰지 않는다.
- read-only 생산표에서 HQ hero 후보는 kind94(prereq37), kind102(prereq45), kind98(prereq46),
  kind100(prereq53)이다. kind75는 prereq 없는 HQ58 생산물이고 lap796 counter가 `0→0`이므로 장수로
  세지 않는다. work는 live TypeSpec `flags & 0x8`로 최종 hero kind를 확인한다.
- 다음 work는 prerequisite 건물만 명시적 gate-legal fixture로 제공하고 hero 자체는 HQ 실제 UI로
  생산한다. live command slot과 주문 직후 HQ `production_type`, 자원/reserved 변화로 셀을 확정한 뒤,
  새 unit의 hero flag, nation-indexed player `+0x980` `0→1`, 초상화를 기록한다.
- baseline fresh 성공 후 normal/fixed_start × baseline/candidate 4-way를 같은 계약으로 실행한다. 성공하지
  않으면 정확한 prereq/availability/slot gate raw를 남기고 `UNKNOWN(fixture contract)`로 닫아 DxWnd로
  이동한다. 제품 EXE는 이 probe에서 수정하지 않는다.

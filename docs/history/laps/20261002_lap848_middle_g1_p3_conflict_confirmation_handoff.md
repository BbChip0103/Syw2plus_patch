# 2026-10-02 KST | lap 848 | G1 W70 P3 성능 충돌 확인·승격 인계

- 실제 provider/model/effort / 지정 역할: 현재 Codex native 세션, 사용자 지정 일반 middle tier(진단·계획·확인). 실제 서비스 model ID·effort는 도구 증거로 확인하지 못했으며 모델 전환/승격을 주장하지 않는다. loop/.lap_counter=848 읽기만 수행.
- 목표/가설: STATUS의 다음 한 가지인 lap847 성능 근거 충돌을 좁게 확인한다. trace game_tick과 실제 sim tick이 같고 통제된 비교가 성립하면 재검수 가능; 주소·raw가 실질적으로 다르면 HOLD 유지·즉시 승격한다. 최신 DESIGN/INBOX에 따라 G1 최우선, G2 5000 유지·10000 종료, G3 중단, G4 보류, G5 승인·종료 유지.
- 변경파일: 이 기록, docs/history/20261002_lap848_prior_lap847_escalate_sol_archive.md, docs/STATUS.md, docs/feedback/APPROVALS.md, docs/feedback/INBOX.md, loop/ESCALATE_SOL. 문서/handoff만 변경, 게임·하네스 구현/바이너리 수정0, 게임 실행0, 커밋0(uncommitted). 기존 타 세션 파일과 raw를 수정·정리하지 않았다.
- 원본 SHA: b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac. 후보 DLL SHA(perf4/5/6): 4ba0b952b94f67b39611e8eaca140c2ee6840251ca0620f3443f4b9a5b97d4d7 / 96b3ab5cffcce6e133b322639e401a7f5541a11efc30077798928131133ef2f9 / 8820fbe8adb1b1b3d552c263868bffbb2a326d84f176767363ecbf3d696103e3. 각 build39개 입력과 현재 소스 SHA 전부 MATCH. 이는 lap844 산출물 재검수이며 이번 source 전체 Fast PASS가 아니다.
- fixture/환경: 과거 lap844 save006 non-synthetic paired private game/prefix/display. 활성 인원·부하를 새로 측정하지 않았다. 상세 환경·fixture·scene은 lap844/847 원문에 보존돼 있고 이번 바퀴는 G2 8인 부하시험이 아니다.
- 실행명령: 공유 temp에만 결과를 쓰는 .venv/bin/python inline 독립 JSON/SHA 재계산; 보호 원본 objdump -d -Mintel --start-address=0x42329f --stop-address=0x423357; 좁은 코드 read/rg; lap847 Fast .exit 및 로그 열람. 최초 disassembly 시작0x423340은 명령 중간이라 출력이 어긋났고, 같은 원본의 명령 경계0x42329F로 바로잡았다(도구 입력 결함 해소, 실제 raw 충돌과 별개).
- 새 근거: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap848_middle_confirmation/confirmation.json SHA d7ac5afae7af42bdcacab4bddc82a11bd691583628b11829756b71d1c414b0fc; original-clock-disassembly.txt SHA d9736ace1c495f0bb98f41b512a0b40d34601459bcbb6a838bd4b91ddc33f68f. 기존 lap847 review SHA c544f3130d8e293c8485bb1919283728e60f3f95d5a0b9c3110505928f366cdb MATCH. 이번 새 캡처 없음.

## 독립 확인 결과

1. direct_draw_trace.c:446은 trace game_tick을 0x9B5210에서 읽고 runtime_driver.py:294 state는 실제 tick0x8924B8과 time.time을 기록한다. 보호 원본0x42329F의 IAT0x4E5294 로드→0x42334A call esi→0x423352 [0x9B5210]=eax를 재확인했다. 두 counter를 같은 sim 진행량으로 취급한 이전 PASS는 단순 전사 오류가 아닌 계측 근거 충돌이다.
2. 기존 PS3 load_fixture.to→production.before raw를 직접 재계산했다(로드 rewind를 넘지 않음). perf4 baseline264/13.203595초=19.994555Hz, candidate171/13.991127초=12.222032Hz, delta−38.873199%; perf5 264/13.198020=20.003001Hz 대170/13.819130=12.301788Hz, −38.500290%; perf6 264/13.194332=20.008591Hz 대170/14.093017=12.062711Hz, −39.712340%. time.time·서로 다른 행동/캡처 비용 구간이므로 통제된 benchmark FAIL 또는 slowdown 원인 확정으로 승격하지 않는다. 기존 성능 PASS를 뒷받침하지 못한다는 충돌만 확정한다.
3. 원본 primary timing count2048/2048/2048은 TRACE_MAX_PRIMARY_PRESENT=2048 상한, 후보255/258/248. summary p95 delta+15/+14/+14ms는 같지만 메뉴/PS3 혼합·샘플 cap·전체 raw 미보존 때문에 동일 PS3 p95 gate로 승인할 수 없다. 최종 렌더/trace/cache 병목은 미확정이다.
4. lap844/847 Scale2x·캡처·선택/empty/drag partial 증거는 취소하지 않는다. 이번 세션은 이 부분 전체를 재실행하지 않았다. minimap diagnostic parity와 product 효과는 구별하고 product minimap/production UNKNOWN/HOLD, 전체 HD/GDI 미검증을 유지한다.

## 판정·stop·work-tier 인계안

- 확인 판정: HOLD_CONFIRMED / RAW_PERFORMANCE_EVIDENCE_CONFLICT. 사용자의 이번 세션 지시 “구현 근거가 불명확하거나 서로 충돌” 조건에 해당하므로 일반 작업자가 억지로 마감하거나 plan 승인하지 않고 ESCALATE_SOL을 보존·갱신해 종료한다. P4·마일스톤 전환·사용자 승인 없음.
- 승격 middle 검증: confirmation.json의 counter/산식·동일 PS3 p95 한계와 아래 work 범위를 확인하고 work 착수 판정을 남긴다. 이미 확인한 동일 raw를 다시 일반 middle 회차로 돌리지 않는다. 구현 없는 연속 회차가2가 됐으므로 다음은 승인된 계측 구현/probe 또는 구체 blocker여야 한다.
- 명시적 work-tier handoff **제안(승격 승인 아님)**: 변경 범위 tools/g1_saved_scene_probe.py, tools/g1_hd_scale2x_probe.py, tools/inmm_stub/direct_draw_trace.c 및 해당 tests의 성능 계측만. 게임 EXE/로직·G2/G5·legacy validator·안전 pin 변경 금지. trace 시간값과 실제 sim counter를 별도 이름으로 보존한다. loaded 안정화 이후 동일 PS3·입력/로드 없는 고정 monotonic 구간(제안20초)에 실제 tick 시작/끝·monotonic 시작/끝·PS3 유지 증거·scene/camera를 기록한다. rate=Δsim_tick/Δmonotonic_seconds; rewind/state 이탈은 명시적 invalid.
- primary present p95는 양 lane 같은 위 구간에서 reset/start/end 또는 window ID로 귀속하고 모든 표본/히스토그램·총수·drop/overflow·PS3를 보존한다. 표본 cap이나 overflow가 있으면 silent PASS 금지. independent p95 재계산 가능성을 targeted 회귀로 고정한다. fresh 3-pair에서 같은 save006·환경·trace/census 옵션·안정화 정책 공개, 원본 대비 rate≥0.95·p95≤원본+16ms 및 parity/source/cleanup을 검증한다. 기준 완화 금지.
- slowdown이 통제 구간에서도 재현되면 work가 비용을 분리해 원인을 추적하고 최소 수정→빌드→격리 실행 반복을 같은 work 세션에서 수행한다. 설명 가능한 구현 결함은 middle에 떠넘기지 않는다. 큰 구조/범위 변경이면 원인·측정치를 승격 middle/strategy로 이관한다.
- 필수 Fast 판정: **SKIP_THIS_LAP**. 이번 사용자 stop 조건이 일반 작업자의 계속 실행보다 우선하므로 make doctor/lint/typecheck/check 및 runtime probe를 새로 시작하지 않는다. lap847 Fast1214 passed/5 skipped·exit0은 과거 증거로만 보존하며 source가 바뀐 이번 검증으로 쓰지 않는다. 문서 한도 검사는 기록 후 수행하고 결과는 fingerprint 제외 STATUS에만 적는다. Fast/skip/exit0으로 성능·계획·제품 통과를 선언하지 않는다.
- 이전 ESCALATE_SOL 원문 SHA 2c5caa0f410ee4ca642b8727130592cb37fa250fa41faa666ed8ca058004babe, 25줄은 docs/history/20261002_lap848_prior_lap847_escalate_sol_archive.md에 byte-exact 보존했다. 원문 반려/미결 삭제 없음. 새 기록/marker가 fingerprint를 바꾸므로 전체 Fast 미실행 상태를 명시한다.
- 다음 한 가지는 STATUS만 진실: 승격 middle의 계측 수리 범위 확인 후 work-tier 수정/probe 착수 인계. 이번 일반 middle은 판정 승인/구현을 대신하지 않는다.

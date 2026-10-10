# 2026-10-09 | lap 1226 | G1 middle — Fast 소유 경계 진단 및 승격 인계

- 실제 provider/model/effort / 지정 역할: Codex `gpt-6.1-sol`/high, middle(진단·계획·확인). launch 근거 `logs/laps/2026-10-09/lap-1226.log` 5~9줄. native child/모델 폴백 없음.
- 지시 순서: PROMPT → AGENTS/INBOX 최신 지시·APPROVALS → STATUS 전체 → DESIGN 1~4절·MODEL_ROUTING → lap1225/1224 원문·정확한 gate 로그. runtime counter 1226(read-only), STOP 없음. PROMPT의 오래된 G2 10000/G4 활성 표현은 최신 DESIGN/INBOX의 G2 종료·G4 보류를 대체하지 않는다.
- 목표/가설: H-TR2611 최종 수용을 차단하는 lint가 계속 재현되는지, root 전체 pytest 실패 4건이 현행 source에도 남아 있는지 구분한다. PASS 측정식은 fresh lint/typecheck exit 0 및 targeted 4개 실패 0이다. focused GREEN도 전체 Fast/게임/마일스톤 승인으로 쓰지 않는다.
- 이전 바퀴 독립 확인: lap1225 lint SHA `512a8e21fc4f36f43858fa714bf301910d143ffe8a605100ef5c2f4cd67aa590` 직접 재계산 MATCH. lap1224 root full raw SHA `d0b0042ea31c7d61b82a329b7fe858a14645e4b4aa363979b46a5bc52c266bb8` MATCH, raw 최종 결과는 4 failed·2238 passed·9 skipped/1298.28s이다. 과거 실패 4건/현재 미검증을 삭제하지 않는다.
- fresh `make lint`: exit 2, FAIL 45건 = `g2_persist_2610.py` E702 42 + `g2_scan.py` struct·`g2_state_2610.py` capstone.x86·`tools/g2_esl2610_spike_probe.py` Callable F401 각 1. 새 로그가 lap1225와 byte-exact 동일(위 SHA). 이는 설명 가능한 소유 범위 밖 결함이며 3회 원인불명 재시도 조건이 아니다.
- fresh `make typecheck`: exit 0, 12 source files PASS. 로그 SHA `f701cb96dd8412917fec5a963db8f25cc3a6079edd55caed6a5fec08573502dc`.
- root 실패 진단: hash assertion 3건(조합 pin 2·G2 pin 1)과 load wrapper jump bound 1건. 현재 test pin은 root raw에서 관측된 후보 SHA로 이미 바뀌어 있고, wrapper bound는 현재 `[code_va+0x100, code_va+0x300)`이다. 현행 구현 LOAD_OFF=0x100·load emitter 크기 상한0x200·다음 header=0x300과 일치한다. historical snapshot 부재로 과거 pin 변경 승인/바이트 차이 정당성을 이 회차가 확정하지 않는다. 핀 자동 갱신 또는 검증 완화 없음.
- 한 번의 bounded 확인 명령: `.venv/bin/python -m pytest -q patches/esl2610/test_g2_combo_2610.py::test_combo_hashes_are_pinned patches/esl2610/test_g2_combo_2610.py::test_save_load_wrapper_jumps_stay_inside_the_wrapper patches/esl2610/test_g2_combo_2610.py::test_write_candidate_is_copy_only patches/esl2610/test_g2_pool4093_2610.py::test_build_resolves_every_inventory_class`; 로그 `logs/gates/lap1226-middle-root-failures-focused.log`. 완주 결과·시간·SHA는 최종 STATUS 및 ignored evidence JSON에 남긴다. pytest 생성 바이너리는 fixture tmp 사본이며 게임 실행 아님. 24k/144k/SHA 불일치 runtime 증명 없음.
- targeted 시작 직전 source SHA: combo test `4b31ab2e36f1891848258794361909ed1a4278c28ae0752f4dd6c2d9c271b20d`, pool test `783ea3cf65239395165ca18d81d1597c8b6c8e5639a87cf3e1c47dca273596a8`, persist implementation `f5d71562764852847880d00bc55b85edd5e4f948fed92711c6e3fb9e74fbf098`. 후속 확인 MATCH. 전체 source 고정 검증은 아니므로 전체 Fast로 승격 금지.
- 전달 identity: 스테이징과 `../260921_temp/G1_1600x1200_시험판_20261009_lap1223_2611/` 모두 정확히 3파일(txt 0); DLL SHA `8807827b4e983dc2b1e11be4516e002563db754e090a98561169ad798f160a51`, direct `6c94fa57163f99cb576dd4e347020d76854a90344ffbe47d5bb5df19cea91cdf`, via_dxwnd `29a35d2edf41dae2f7ac1b09a52d2c12bd301860733ca8cb70ce43c9e85d886c` 직접 MATCH. read-only 대조만 했고 재전달 없음. `logs/gates/lap1226-middle-identity.json`.
- 변경파일: 이 기록·lap1225 ESCALATE 원문 보존·STATUS·INBOX 처리 메모·loop/ESCALATE_SOL. 원문 보존 SHA `7075243acf9aefcb8a49facafd4f007ed7fa539f766943881d929e6c2b36678c`. 게임/하네스/테스트/validator/핀/원본/전달물 수정 0, 커밋0, 기존 uncommitted 유지. 기록 전 문서 크기 STATUS54/INBOX201/APPROVALS34로 압축 불필요.
- 전체 `make check`: SKIP(BLOCKED: fresh lint 선행조건 실패). FULL_TEST 요청/장기 게임 없음. 문서·handoff 작성 후 safety/context/diff 검사와 최종 fingerprint·파일 SHA는 STATUS 및 ignored 로그에만 남긴다.

## 명시적 work-tier 및 승격 handoff

1. 별도 G2 파일 소유 work만 E702 42건의 다중문장을 의미 보존하여 나누고 F401 3건을 수리한다. 루프/middle은 소유 파일을 대신 고치지 않는다. pin 변경 내역·원인·승인 근거도 소유자가 보존한다(관측 해시만으로 pin 승인 금지).
2. 소유 work가 fresh lint/typecheck 및 위 4 target를 확인한다. 불일치가 남으면 실제 생성 바이트/분기 목적지/레이아웃을 확인하고 구현 결함을 수리·재실행한다. 검사 제외/skip/범위 완화로 통과시키지 않는다.
3. 기록/handoff를 먼저 확정한 동일 source에서 `make check`를 완주하고 source before/after·log SHA·exit·pytest/lint/typecheck 수치를 제시한다. 전체 Fast 없는 H-TR2611 final PASS 금지.
4. 사용자 이번 세션 규칙의 마감 경계에 해당하므로 H-TR2611 수용 HOLD·G1 미완료를 유지하고 `loop/ESCALATE_SOL`로 승격 종료한다. 승격 middle/root가 전체 Fast·기존 TR raw·성능 귀속 UNKNOWN을 검수하고 기술 수용 여부를 판단한다. 사용자 2611 플레이·업스케일 결과는 별도이며 신규 결과 미도착이다.
5. lap1224/1225 뒤 제품 증거가 늘지 않는 세 번째 회차다. 다음 승격은 strategy/middle의 구체 재개/중단 판정으로 이어져야 하며 동일 lint 확인·문서만 반복하지 않는다. 현재 live queue는 STATUS만 참조한다.

## 종료 시 source drift — 새 통과로 승격 금지

focused 완주 직후 확인한 combo/pool test·persist 3개 SHA는 시작 전과 MATCH였으나, 이후 마지막 fingerprint가 `a2391f5d55eedd72191644405d5f16cd87f01d24`→`7ed40ea985980ca8a0e52a04ce25a6d776e1f0f6`으로 바뀌었다. 파일 mtime 확인에서 `tools/g2_esl2611_saveload_replication.py` 22:28:55, `patches/esl2610/test_g2_combo_2610.py`·`test_g2_full_2610.py`·`test_g2_pool4093_2610.py` 22:29:47 변경이 관측됐다(2026-10-09 KST). 이 세션은 해당 파일에 쓰지 않았다. 최신 INBOX의 별도 소유 세션 범위와 일치하며 변경 내용/승인 정당성은 소유자가 설명해야 한다.
4 passed/314.20s는 실행 당시 snapshot 확인이다. 현재 변경 후 source 검증은 미실행이며, 이 경계에서 tests를 억지 반복하거나 핀을 맞추지 않는다. 승격/소유 work는 변경 사유·pin 근거를 먼저 확인하고 소스 변경이 끝난 동일 snapshot에서 lint/typecheck·4 targets·전체 Fast를 수행한다. 마지막 safety 재검사는 exit0이며 결과 및 최종 파일 snapshot은 STATUS/ignored evidence JSON에 보존한다. 원본/기존 변경을 되돌리지 않는다.

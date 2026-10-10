# 2026-10-09 | lap 1224 | G1 middle — H-TR2611 raw 독립 확인·Fast 차단·마일스톤 경계 승격

- 실제 provider/model/effort / 지정 역할: Codex `gpt-6.1-sol`/high, middle(진단·계획·확인). 실제 launch 근거 `logs/laps/2026-10-09/lap-1224.log` 5~9줄. bounded read-only 실패 진단 child `debugger` = Codex `gpt-6-luna`/high(work tier); 최종 승인 권한 없음. 자동폴백 0.
- 가설: lap1223 H-TR2611 raw·파일 정체성이 사전등록(lap1222 §4)과 맞는지 확인한다. 사용자 업스케일·G1 시험 결과 신규 도착 없음. STOP 없음.
- 예상 PASS/FAIL: trace/input SHA·PS3 present/stale/안전·스테이징 bytes가 work 기록과 일치하면 해당 수치 확인 PASS. 전체 Fast와 사용자 시험판 경계 판단이 끝나기 전 H-TR2611 최종 수용·G1 마감 없음.
- 변경: 이 기록·STATUS 압축/갱신·INBOX 처리 메모·기존 ESCALATE_SOL 원문 보존 후 새 handoff. 게임/하네스/테스트/C/validator/기준 핀/원본 변경 0, 실행 게임 0, 커밋 0, uncommitted 유지.
- 원문 보존: STATUS 128줄·SHA256 `7083235769b9dfe0c066ff0bf473969f674ca864f0cddbf54957b55025c1e919` → `docs/history/20261009_status_lap1224_precompaction.md` byte-exact. 기존 lap1223 ESCALATE_SOL SHA256 `1d8490ac3e2a5a3710d3b18fad93fa2d800ec5f2c826c15eef5b97186fa85cf3` → `docs/history/laps/20261009_lap1224_preserved_lap1223_escalate_sol.txt` byte-exact. 미결/반려 전문과 과거 계보는 원문에 그대로 보존했다.

## 1. 독립 raw 확인 — 새 스크립트, 과거 실행 검수이며 fresh 게임 실행 아님

공유 temp `20261009_lap1224_middle_review/recalc.py` SHA256 `58d0260a64a2260a1865cc8cfc12fd5d18beab6785dcca3e8900e0a6234fe4d5` → `recalc.json` `a7f3d720413bf509828de52b5e6782d76f25a944891597666d35cf1e21356e2a`. work 요약 스크립트를 실행하지 않고 trace_raw·input_trace_raw·pair/probe JSON을 직접 읽었다. 스크립트 최초 1회 KeyError는 baseline lane에 candidate 전용 validator 필드가 없어서였고, optional schema 처리로 수정 뒤 완주했다(제품 결함 아님).

| 후보 lane | PS3 present | stale 합 | covered 최소 | p95/max ms | 안전 8종·hresult·success≠1·dropped |
|---|---:|---:|---:|---:|---|
| tr1_1 | 781 | 0 | 476,557 | 11/56 | 모두 0 |
| tr1_2 | 793 | 0 | 476,574 | 9/22 | 모두 0 |
| tr2 | 1,718 | 0 | 480,000 | 13/55 | 모두 0 |

- 6 lane raw trace SHA 기록값과 재계산 MATCH, 후보 input trace SHA MATCH. TR-1 장면 상태 두 lane 직접 동등(8 player records·559 units; 빈 플레이어를 활성8인/G2 부하로 세지 않음). pair 6 gate 기록 PASS, 두 lane EXE 2611 `d9d6bb3dca11c229dfb129547166ecdea7b777c0d2494a2baa38ce68635de21d`.
- TR-2 확인 버튼 `(608,564)` 실제 WndProc down 2회, down 간격 **10,072ms**, hold **118/108ms**. work 10.07s 표기와 일치. PS3 stale 0. retry가 시작에 인과적으로 필요했는지/첫 클릭 지연의 정확한 원인은 이 기록만으로 확정하지 않는다.
- 후보 `mirror_validator`는 nearest oracle 때문에 BLOCKED, scale2x validator는 PASS. 팩 끔 Scale2x 경로의 gate는 scale2x이며 nearest 진단 BLOCKED를 새 합격으로 바꾸지 않는다. pair 시각 gate는 기존 기록 확인이고 이번 회차 전체 픽셀 게이트 재구현은 하지 않았다.
- baseline/candidate production PNG를 직접 열람: 건물·선택 HP·하단 HUD·미니맵·생산 버튼 배치에 육안으로 새 분리/잘림 없음. 실제 입력 대응은 lap1223 증거 검수이며 이번 fresh 입력은 0.
- **수치 확인 PASS, final technical acceptance HOLD.** raw 수치와 기록의 실질 충돌 0. e23 단발 stale 재개 조건은 이번 raw에서 미충족.

## 2. 파일/SHA·source 확인

- 2611 정본 EXE SHA 위 값 직접 재계산 MATCH; 원본 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH. HQ2002 SHA는 fresh `make doctor` verified `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 스테이징 `_inmm.dll` `8807827b4e983dc2b1e11be4516e002563db754e090a98561169ad798f160a51`(508,542 B) = tr1_1 bridge byte 그대로.
- direct `.bat` `6c94fa57163f99cb576dd4e347020d76854a90344ffbe47d5bb5df19cea91cdf` = lap1151 bytes에서 EXE 이름 두 위치만 HQ2002→2611 치환. via_dxwnd `.bat` `29a35d2edf41dae2f7ac1b09a52d2c12bd301860733ca8cb70ce43c9e85d886c` byte 동일. 3파일·txt 0, 전달물 쓰기 0.
- 복사된 bridge C/H/DEF와 현재 `tools/inmm_stub/`는 `inmm_stub.c`의 빌더 삽입 2줄을 제외하고 동일. 삽입 차이는 `patches/population/build_runtime_bridge.py:98`~108의 deterministic 변환을 메모리에서 재적용해 exact MATCH 확인(추론만으로 동일 처리하지 않음). `runtime_bridge.c` SHA `923fd1e149a638f3a7ab086beb9aca549c76988e00caafa83dcbc2b62f8da8f1` 현 source·복사본 동일.
- 현재 probe SHA `f00c09cfec055820a802ca8334d2f297e56b2cfe01717e22e518ac33b9a0f383`, new-game test `56ff11db59714b8f3439bbac73c3868300ab5ff33cadce3389b8e15406eff1d7` = work 기록. 독립 DLL 재빌드·롤백 재실행 SKIP(제품 패치 변경 없음, 스테이징 identity만 확인).

## 3. 실패 게이트 진단·명시적 work handoff

- fresh `make doctor` PASS(setup/original verified). 기본 runtime manifest 없음 진단은 게임을 새로 실행하지 않은 setup-only 모드 결과이며 private runtime 통과로 쓰지 않는다.
- fresh `make typecheck` PASS(12 files), focused `tests/test_g1_new_game_path.py`·`test_g1_saved_scene_probe.py`·`test_esl2610_runtime.py` **305 passed/12.02s**. `logs/gates/lap1224-middle-focused.log`.
- m7을 메모리에서만 `_start_new_game` 클릭 기록→빈 dict로 변이: 신규 단일 테스트 **1 failed/0.04s**, `M7_RED_EXPECTED True`. 디스크 source 수정 0, 원본 focused GREEN과 함께 테스트 공백 폐쇄 확인. 로그 `logs/gates/lap1224-middle-m7.log`.
- lap1223 full test 실패 3건은 child가 exact log를 읽고 current 최소 targets 재실행 **3 passed/56.53s**. Capstone detail 설정 누락과 outdated globally-fail-closed assertion이 원인. 현재 `md.detail=True`·missing STOCK_ORACLE 주입으로 수정된 상태이며 이 회차 수정 0. 재현 명령/근거는 공유 temp `gate_diagnosis.json` SHA256 `b414eca0a6a486d1289dd59a147f04a9354afb27ebff9839d499d82bdd1ead61`. exact historical snapshot은 없으므로 편집 경합 귀속은 로그·현재 변경 이름/구현에 근거한 inference이며 옛 실패를 지우지 않는다.
- fresh `make lint` **FAIL F401 4건**: `patches/esl2610/g2_scan.py:32` struct / `g2_state_2610.py:349` capstone.x86 / `tools/g2_esl2610_spike_probe.py:40` Callable / `tools/g2_esl2611_saveload_replication.py:23` shutil. 로그 `logs/gates/lap1224-middle-lint.log`. 모두 별도 2611 세션 소유이며 INBOX 18:53·사전등록의 루프 수정 금지 범위. 원인 설명 가능, blind retry/루프 hands-on 수정 없음.
- **work-tier handoff:** 별도 2611 파일 소유 work가 위 4 unused import를 제거하고 `make lint`·`make typecheck` 통과 증거를 남긴다. 그 뒤 기록/handoff를 먼저 확정한 동일 source에서 `make check`를 완주하고 전체 pytest 결과·로그 SHA·before/after fingerprint를 남긴다. 중간 tier는 게임/하네스/다른 소유 파일을 대신 고치지 않는다.
- **전체 `make check` SKIP(BLOCKED)**: PROMPT의 선행 lint 통과 조건이 실패했고 수정이 지정 범위 밖이다. focused 통과·옛 full test·exit0를 전체 Fast PASS로 승격하지 않는다. FULL_TEST 요청/장기 검사/게임을 띄워 놓고 종료한 것 없음. source_match=no의 과거 lap569 결과를 현재 검증으로 재사용하지 않는다.
- safety/context 및 최종 파일 fingerprint는 기록 작성 후 실행하고 결과를 STATUS에만 보강한다. 해당 결과 전에는 이 문서가 safety/full PASS를 주장하지 않는다.

## 4. 승격 경계·남은 위험

현재 큐의 다음은 **2611 사용자 시험판 요청과 전달 판단**이므로 사용자의 이번 일반 작업자 마일스톤 경계 규칙에 해당한다. `loop/ESCALATE_SOL`을 승격 middle/root로 남기고 세션을 끝낸다. APPROVALS 변경·최종 H-TR2611 수용·사용자 시험판 전달·G1 마감/다음 마일스톤 전환 없음.

- 성능 p95/max 상승 수치는 확인했으나 호스트 load 평균만으로 원인을 확정할 수 없다(동시성 통제 대조 없음). **호스트 부하 귀속 UNKNOWN, 설명 후보만 유지.** 필요하면 같은 DLL·같은 fixture·유휴 호스트에서 원본/후보 paired elapsed를 측정할 work를 승격 검수자가 정한다. 게임 24k/144k·Windows·DxWnd·BGM·G8/G9 조합·실제 업스케일 팩·`.kills` 배지 미검증 그대로.
- 사용자 그림 결과/플레이 결과가 오면 최우선, G2/G5/G6G7 종료·G3 중단·G4 보류 유지. raw/PNG/manifest/output/prefix/game cleanup 기록 보존, 자기 게임 생성/삭제 0.
- 다음 한 가지의 live queue는 STATUS만 참조한다. 본 절의 work handoff는 수리/검수 계약이며 새 milestone 승인 아님.

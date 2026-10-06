# 2026-10-02 KST | lap 847 | G1 W70 P3 독립 검수 — 성능 근거 충돌

- 실제 provider/model/effort / 지정 역할: 현재 Codex native 세션 / 사용자 지정 middle tier(진단·계획·확인). 실제 서비스 model ID·effort는 이 surface에서 확인 불가하며 다른 모델로 바뀌었다고 주장하지 않는다. `loop/.lap_counter`의 847을 읽기만 했다(프롬프트 runtime 배너 846보다 파일 값을 사용).
- 가설 / 예상 PASS·FAIL: lap844 perf4/5/6의 원본·fixture·DLL·raw를 독립 재계산하고 유효 캡처/입력 parity와 실제 시뮬레이션 tick rate ≥baseline×0.95 및 present p95≤baseline+16ms를 확인하면 P3 gate 수용. 근거 충돌이면 HOLD·승격, P4 금지.
- 변경 파일: 이 lap 기록, `docs/history/20261002_lap847_prior_lap844_escalate_sol_archive.md`, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`. 제품·하네스·게임 바이너리 수정0, 게임 실행0, 커밋0(uncommitted). 다른 세션 `*g5_esl2608*` 소스·runtime은 조사/수정/정리하지 않았다.
- 현행 목표: 최신 사용자 결정의 G1 화면 전체 HD 경로. G2 10000 종료·5000 유지, G4 보류, G3 중단, G5 v10 승인·종료를 유지한다. PROMPT의 오래된 목표 문장을 신규 목표로 적용하지 않는다.
- 원본/fixture: 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, non-synthetic save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`를 현재 read-only 원문에서 다시 계산했다. 세 pair는 8개 player record·558개 scene unit과 동일 scene identity다(이 수치로 8인 부하시험을 주장하지 않는다). 별도 private game/prefix/display를 사용한 과거 lap844 실행이며, 이번 lap의 fresh runtime 결과가 아니다.
- 증거 경로: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap844_p3_perf{4,5,6}/`. pair SHA는 순서대로 `1c4385c72348bbc1c871ec8f55da3103f6394229c7cff4adf6d291033330f683`, `e3d41ec3b1811c7e4a88999941a003b447b2a16c0723f07dfc7ab76ac634c24d`, `b7e05b8fd91cf17f2cc38bf211d868f1621b229e2a2ff3d8682e80b76d1537d5`로 MATCH.
- 후보 DLL SHA(perf4/5/6): `4ba0b952b94f67b39611e8eaca140c2ee6840251ca0620f3443f4b9a5b97d4d7`, `96b3ab5cffcce6e133b322639e401a7f5541a11efc30077798928131133ef2f9`, `8820fbe8adb1b1b3d552c263868bffbb2a326d84f176767363ecbf3d696103e3`. 각 DLL/manifest SHA와 각각의 build 입력39개가 현재 소스와 전부 MATCH. baseline/candidate trace SHA·probe JSON/pair 일치·capture SHA·cleanup을 재확인했다.
- 재계산 산출물: 공유 temp `lap847_middle_review/recompute.py` SHA `6fe25e110fa4eb8e311c00ba9686c3c0e091e80aca14a35eab63aae3ba963a1c`, `review.json` SHA `c544f3130d8e293c8485bb1919283728e60f3f95d5a0b9c3110505928f366cdb`. 원본/기존 raw를 덮어쓰지 않는다. 재계산 스크립트의 최초 fixture 경로에 `save/`가 빠져 FileNotFoundError가 났고, `tools/g1_saved_scene_probe.py:332` 계약대로 수정·재실행하여 해소했다(제품 결함/불명 실패 아님).

## 확인 결과와 충돌

1. Scale2x raw 재검증 PASS: candidate present `255/258/248`, mask 내부 diff 합 `976824/969610/982428`, 외부 diff0, palette 위반0, lookup miss/invalid0, trace drop0. 양 lane scene/source/cleanup 및 selection/empty/drag parity PASS. 모든 저장된 캡처의 SHA·크기·non-black을 확인했고 perf4 loaded 기준/후보를 직접 시각 확인했다. 구도/HUD 배치가 같고 검정 캡처 결함은 해소됐다. 이는 partial 수용이며 전체 HD coverage·사용자 미적 승인/제품 완료가 아니다.
2. 미니맵 diagnostic parity PASS이나 selected unit witness가 양쪽 UNKNOWN(slot=null)이고 camera 무변화다. gate 바이트 `00000000→01000000→00000000` 원복은 대조 수용하되 실제 이동 성공으로 승격하지 않는다. product minimap/production UNKNOWN/HOLD 유지.
3. **lap844의 tick span `24210/24155/24104`와 `24692/24611/24921`은 게임 tick rate PASS 근거가 아니다.** `tools/inmm_stub/direct_draw_trace.c:446`의 `game_tick`은 `0x9B5210`에서 읽지만 `runtime_driver.state():294`의 실제 tick은 `0x8924B8`이다. 보호 원본 disassembly에서 `0x42329F`가 `_imeGetTime` IAT `0x4E5294`를 ESI에 넣고, `0x42334A call esi` 뒤 `0x423352`가 반환 시간값을 `[0x9B5210]`에 저장한다. 따라서 trace 시간값의 구간 길이를 시뮬레이션 진행량으로 수용할 수 없다. 이는 해시 오타/전사 오류와 다른 실질적 측정 근거 충돌이다.
4. 기존 raw의 `load_fixture.to`→`production.before`는 PS3 내 단일 로드 이후 구간이며 load rewind를 건너지 않는다. 실제 tick 변화량÷각 snapshot `time` 차이를 재계산했다:

| fresh pair | baseline Δtick / seconds / rate | candidate Δtick / seconds / rate | rate delta |
|---|---|---|---|
| perf4 | 264 / 13.203595 / 19.994555 | 171 / 13.991127 / 12.222032 | −38.873199% |
| perf5 | 264 / 13.198020 / 20.003001 | 170 / 13.819130 / 12.301788 | −38.500290% |
| perf6 | 264 / 13.194332 / 20.008591 | 170 / 14.093017 / 12.062711 | −39.712340% |

이 값은 기존 행동/capture 구간의 진단 표본이다. time.time 기반·서로 다른 capture 비용/구간 길이이므로 통제된 fixed-window benchmark로 대체하지 않는다. 다만 모두 −5%보다 훨씬 낮고, 이전 tick 성능 PASS를 독립 수용할 수 없음을 직접 보인다. 렌더/계측/cache 중 느려짐의 원인은 아직 미확정이며 특정 함수 병목으로 단정하지 않는다.
5. summary p95 baseline `2/2/2ms`, candidate `17/16/16ms`, delta `+15/+14/+14ms`는 JSON에서 재확인했다. baseline timing count2048은 `TRACE_MAX_PRIMARY_PRESENT=2048`에 포화, candidate는255/258/248이며 메뉴/PS3가 섞인다. histogram 전체 샘플을 raw에 남기지 않아 완전한 독립 p95 재계산도 불가하다. 이 summary 산식의 범위 내 수치 수용과 P3의 동일 PS3 측정 gate 통과는 구분한다.

## 판정·기계 검증·handoff

- 판정: P3 배관/캡처 `PASS(partial)` 근거 보존, **P3 gate HOLD / RAW_PERFORMANCE_EVIDENCE_CONFLICT**, G1 HOLD. 사용자 지시의 근거 충돌 조건에 따라 `loop/ESCALATE_SOL`을 갱신하고 승격 작업자에게 넘긴다. P4/P5/GDI·마일스톤 전환/마감 없음.
- 이전 lap844 marker 원문은 15줄·SHA `7e81b45857149e4fd383784e7395644dc0eb927176a29a618a852fd86029cd47`로 archive에 바이트 그대로 보존했다. lap844 원기록과 그 수치도 삭제/수정하지 않는다.
- 실행 명령: `make doctor`, `make lint`, `make typecheck`, `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py tests/test_g1_hd_scale2x_probe.py`(10 passed), 위 `recompute.py`, 보호 원본 좁은 `objdump`·PE import 대조. doctor/lint/typecheck와 targeted10 PASS. 문서/handoff를 모두 쓴 뒤 마지막 Fast `make check`를 실행하고 최종 수치는 fingerprint 제외 대상 STATUS에만 보강한다. 전체 Fast 로그는 `logs/gates/lap847-middle-fast.log`, exit 회수는 동명 `.exit`; Fast는 runtime/24k/144k/성능 승인 증거가 아니다.
- 승격 검수 항목: 두 counter의 raw/code/disassembly와 위 산식을 확인해 이전 performance PASS 무효/HOLD를 확인하고 아래 bounded work handoff를 확정한다. 오류를 설명하지 못한 상태로 P4를 마감/시작하지 않는다.
- work-tier handoff(게임 hands-on 수정은 이 세션에서 하지 않음): 기존 saved-scene 하네스에서 PS3 loaded 안정화 뒤 입력/로드 없는 고정 monotonic 시간창에 실제 `0x8924B8` tick의 시작/종료·ps·camera·scene을 기록하고 `rate=Δtick/Δmonotonic_seconds`를 계산한다. 동 구간 PS3 primary-present timing은 양 lane 동일 정책으로 전 샘플/히스토그램과 sample-drop을 남겨 p95를 독립 재계산 가능하게 한다. tracing/census/HD env를 공개하고 3회 새 baseline/candidate pair를 실행한다. rate≥baseline×0.95, p95≤baseline+16ms, parity/source/cleanup을 검증한다. 느려짐 재현 시 측정과 cache/reinvoke/present 비용을 분리해 최소 수리→재실행한다; 승인 없는 기준 완화는 금지. 이번의 이미 확인된 raw 충돌을 같은 방식으로 재계획/재요약하지 않는다.
- 다음 한 가지의 현재 큐는 STATUS만 따른다: 승격 middle의 충돌 판정 확인 및 위 work 계측 수리 handoff. 전체 HD coverage/P4·GDI, 실제 미니맵/생산 및 사용자 3단 승인은 미검증이다.

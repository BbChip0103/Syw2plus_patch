# 2026-10-02 | lap865 | G1 W70 P4b independent middle review — HOLD

- 역할: 사용자 지정 중간 tier(진단·계획·확인), Codex. 이 대화는 실제 모델 ID/effort를 노출하지 않으므로 Sol/Opus/high 실행을 주장하지 않는다. 게임/하네스/validator 구현·DLL 빌드·새 게임 실행·커밋 0, subagent 0.
- 입력 순서: `loop/PROMPT.md` ①~⑥ → AGENTS → INBOX 최신 지시/APPROVALS 반려 → STATUS 전체 → DESIGN 1~4 → P4b/P4 카드·주소 문서 → lap864 work 기록·ESCALATE·r4 pair/raw. 목표는 G1, G2 5000 유지·G4 보류·G3 중단·G5 종료를 재개하지 않는다.
- lap counter는 읽기만 했다. 최초 관측 864, 검수 중/기록 시 현재값 865. 러너 소유 값을 복원하거나 변경하지 않았으며 현재값 865로 기록한다. 이전 work 기록/산출물의 lap864 표기는 유지한다.
- 가설: r4 DOWN 13칸/1칸 차이가 receiver/카메라 관측 시간 결함인지 제품 입력 비대칭인지 독립 검수한다. PASS는 두 lane 같은 DOWN→RIGHT 실제 수신·한 칸 최종 카메라·scene parity와 candidate coverage/Scale2x gate 충족이다. 출처·결과 충돌의 직접 원인을 설명할 수 없으면 HOLD·승격하고 재실행하지 않는다.

## 독립 재계산과 입력

- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, read-only 새 재해시. 비합성 save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 재해시 일치. 기존 Wine win32 private prefix·전체 game copy·Xvfb 1600×1200×24 실행의 raw를 읽었고 새 runtime 0. 저장된 8 player records는 활성8인 부하 증명이 아니다.
- r4 원문: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_101200_p4b_scroll_r4/`. pair SHA `8f0ef603d98e191a6a0113deaa40d7a807674e5a18b1b56809973799525b3a08`, baseline raw `a9808508e03b638068ade83c1a4c12ddad6f9d0a042e629b5f3a73dd55887662`, candidate raw `b54754c6a728404ac5fc1a6b2e2f95eb7f048ee7e06cf1e1180d8170be00f980`, 모두 일치.
- candidate DLL SHA `d7a43a69fe4883c913d5d4dce073fdbd453723dc7fec481cf2819a5b003083db` 일치. build manifest 원 입력 42개는 현재 source와 모두 일치. 복사된 source 40개는 byte-identical이고, `inmm_stub.c`/`Makefile` 2개는 `build_runtime_bridge.py:84`의 poll 삽입/SRCS 추가 변환을 그대로 재생해 일치 확인했다. 처음 42개 단순 snapshot 비교가 false인 것은 정상 생성 변환이며 근거 충돌로 취급하지 않았다.
- 보호 원본에서 memmove CALL 8곳의 old bytes와 상대 target `0x4DB1D0`, entry 8 bytes 및 `0x466280` entry 8 bytes를 직접 확인했다. 설치 source는 E8 CALL 보존·불일치 거부·detach rollback·patched bytes 확인 후 byte-exact restore를 가진다. 이번 세션은 unsupported-version 실행/라이브 detach 원복을 새로 시험하지 않았다.
- 구현 source에서 층 폭832·whole-row/row-run overlap-safe 이동·미지원 범위 covered 지움·원본 CALL 뒤 전사를 확인했다. 전사는 현재 픽셀 루프이므로 C 성능은 추정하지 않는다. 이번 중간 검수에서 해당 구현은 변경하지 않았다.

| lane/key | camera | receiver dispatch 간격 | 30-present coverage p50 | move/transfer delta |
|---|---|---:|---:|---:|
| baseline DOWN | [158,101]→[171,114] | 2ms | 없음 | 없음 |
| candidate DOWN | [158,101]→[159,102] | 29ms | 365,324 | 1/30 |
| baseline RIGHT | [171,114]→[172,113] | 34ms | 없음 | 없음 |
| candidate RIGHT | [159,102]→[160,101] | 12ms | 352,704 | 512/30 |

- receiver 원문은 각 lane 보존 prefix `drive_c/inmm_g1_input_trace.jsonl`이며 pair의 네 수신 레코드와 정확히 같다. candidate 전환 seq1542/1572 뒤 각각 30 present 카메라가 한 칸에서 유지된다. DOWN moved bytes399,360, RIGHT393,216, unsupported/outside diff는 두 창 모든 표본에서0.
- key-before p50 337,534/365,324, 각각 ≥264,000 및 키 전 90% 이상을 충족한다. 첫 DOWN 전 PS3 표본은14개뿐이므로 고정 카메라 first20/last20 지속성은 이 창으로 증명할 수 없다. 스크롤 coverage partial만 수용한다.
- Scale2x validator 무수정 재실행 `PASS`, 1203 present. legacy validator `BLOCKED`, 오류1203개 전부 nearest oracle 유형으로 다른 legacy 오류0. W70/P4b 및 APPROVALS lap853의 scale2x 전용 gate 계약상 예상되는 차이다. legacy gate 자체를 PASS로 변경하지 않으며 별도 identity/nearest 실행이 필요하다는 새 조건도 추가하지 않는다.
- loaded scene parity true, source unchanged/cleanup true, 양쪽 private game 사본 없음. 그러나 키 뒤 scene parity false: baseline560/candidate563 unit records, candidate-only slots35/36/37, 공통 unit record 변경0; owner2 cap baseline2100/candidate2300. 비동기 진행 차이일 수 있으나 직접 원인은 UNKNOWN이며 제품 parity로 승격하지 않는다.
- 재계산 artifact: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap865_middle_p4b_review/recomputed.json`, SHA `1b2affe15058cadc1c6bdfe9502e8dc72881c7bfa03a028ad6a1d0bd48f8f355`. build/source/raw/receiver SHA, 30표본·전환·scene diff 포함. 최초 탐색 artifact(lap864 suffix)는 보존했으며 현재 판정은 이 lap865 artifact다.

## 원인 판정과 work handoff

**확정한 하네스 결함**, `tools/g1_saved_scene_probe.py:987` / `tools/inmm_stub/direct_draw_trace.c:223`:
1. arm 파일 작성 직후 keydown을 보낸다. receiver 설치 thread는 Sleep(10)·EnumWindows·SetWindowLong을 거치지만 설치 완료 ack/barrier가 없다.
2. release 조건이 `receiver_down is not None and camera != before`이다. 카메라가 먼저 움직여도 수신 로그가 없으면 key를 계속 누른다. 따라서 관측 지연을 실제 입력 지속으로 바꿀 수 있다.
3. `after_key`는 keyup 이전 표본이다. keyup 이후 안정 카메라를 각 action에 다시 저장하지 않고 `valid`도 한 칸 목표를 요구하지 않는다. baseline13칸을 lane PASS로 표기하는 경로가 실제 존재한다.

**직접 원인 UNKNOWN:** 2/29ms는 WndProc에서 dispatch된 두 메시지 시각 차이이며 실제 XTest hold 시간이 아니다. 기존 raw에는 emission monotonic/receiver-ready/원본 handler 처리 시각과 baseline camera 시간열이 없다. 위 결함이 baseline13칸의 직접 원인인지, 제품 입력 비대칭인지 현재 자료만으로 확정 불가. 사용자 즉시 승격 조건을 적용하며 재시도·C 착수·G1 마감 금지.

승격 Sol은 이 귀속 범위와 scene mismatch를 확인한 뒤 **work tier에 다음 최소 수리를 명시적으로 넘긴다**(중간 tier 직접 구현 금지):
- 동일 opt-in receiver 설치 완료 ack를 두 lane에서 먼저 기다린다. ack 없으면 키를 보내지 않고 INVALID.
- 양쪽 XTest down/up emission monotonic 시각·receiver-ready/receipt·실제 카메라 관측 시각을 보존한다. 카메라 첫 변화에서 즉시 release하고 receipt 검증은 별도로 수행한다. timeout/예외도 finally에서 keyup 보장, fallback 없음.
- keyup 후 카메라 안정까지 관찰해 실제 한 칸 DOWN=(+1,+1), RIGHT=(+1,−1)를 action에 기록한다. overshoot/no receipt/no movement는 INVALID; 기존 raw/gate/임계값 덮어쓰기 금지.
- 회귀는 지연 receiver에서도 첫 camera 변화 시 release, keyup 뒤 추가 이동 거부, 준비 실패·예외 release를 검증한다. 문자열 포함 검사만으로 완료하지 않는다.
- 새 gdb 없는 save006 same-save pair로 두 lane 같은 순서·각 단계/최종 camera·source/cleanup·scene을 확인하고 candidate 두30-present gate와 고정 first20/last20 지속성을 재측정한다. scene mismatch는 tick/진행 차이를 증거로 설명하거나 수리하며 임의 정규화해 PASS 만들지 않는다. 구현 결함은 PROMPT③대로 추적→수정→재실행한다.
- B' 전체 independent PASS 전 C fresh3 금지; D-1 전 P5 금지. G1 마일스톤/사용자 승인 없음.

## 변경·검증·종료

- 변경: 이 기록, STATUS, APPROVALS, ESCALATE_SOL 및 직전 marker 원문 archive. 게임/하네스/validator source 변경0, 원본/참고 쓰기0, commit0. 이전 marker 원문은 `docs/history/20261002_lap865_prior_lap864_escalate_sol_archive.md`에 byte-exact 보존했다.
- fresh `make doctor` PASS(보호 원본 verified); optional runtime manifest absent, 따라서 doctor 자체의 runtime.ok=false는 새 실행 PASS가 아니다.
- fresh `make lint` PASS, `make typecheck` PASS(10 files), `.venv/bin/python -m pytest tests/test_g1_mirror2x.py tests/test_g1_saved_scene_probe.py tests/test_g1_hd_scale2x_probe.py -q` **36 passed in0.12s**.
- 전체 `make check`, DLL 빌드, 새 runtime는 **SKIP(사용자 근거 충돌 즉시 승격·세션 종료 지시)**. lap864 log의1228/5skip·885.60s·exit0을 직접 읽었으나 current fingerprint PASS로 재사용하지 않는다. 사용자 지시가 patch-validation skill의 `Run make doctor then make check`보다 우선한다.
- 최종 safety/context/scoped diff·source SHA 재확인 결과와 기록/marker SHA는 STATUS에만 보강한다. 제품 판정 HOLD. 다음 한 가지의 유일한 현행 큐는 STATUS다.

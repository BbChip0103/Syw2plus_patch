# 2026-09-27 | lap 720 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, hands-on 구현/실행). 게임 코드 0변경(도구+문서만).
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL` lap719 섹션·`docs/feedback/APPROVALS.md` 2026-09-27 17:25 운영자
  판정(R1) — v4(및 v3)의 청크 경로는 선택 >20이면 항상 전역 선택-엔트리 배열의 고정 3개 창
  (`entries[0:20]`·`[20:40]`·`[40:50]`)을 복사해 각각 발행하며, 그 경계는 **선택 용량**(50)에
  맞춰져 있지 라이브 **선택 개수**에 맞춰져 있지 않다. 50 선택 후 라이브 선택을 21~49기로
  **줄이면**, 배열의 꼬리 칸(새 count 이후, 이전 50-선택 시점의 핸들)이 여전히 남아 있어 미선택
  유닛도 명령(STOP `0x1000002`)을 받을 수 있다는 가설(R1). 지금까지의 모든 raw 측정은 "전체
  50 선택 → 명령"만 다뤄 이 경로를 측정한 적이 없었다.
- 예상 PASS / FAIL 조건: 선택을 줄인 뒤 STOP을 발행했을 때, 새로 선택된(=축소 후 라이브 선택)
  유닛 전원이 `unit+0x384`(pending)에서 `0x1000002`를 관측하고, 축소로 **제외된(deselected)**
  유닛은 그 값을 한 번도 보이지 않아야 PASS(`PASS_NO_LEAK`). 제외된 유닛 중 하나라도
  `0x1000002`를 보이면 `FAIL_LEAK`(R1 CONFIRMED, v5 착수 필요).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_selection_shrink_leak_probe.py`(SHA256
    `3a5b62075ad09c66ca6c14d7da1eebf3310b8af6cd4d71e32843461e9adeffcf`) — 전체 드래그로 최대
    선택(원본20/후보50) 확립 → 좌측 고정·우측 폭만 줄이는 부분 드래그를 여러 폭으로 시도해
    목표 대역(후보21~49, 원본5~19)에 드는 라이브 개수를 찾음 → 그 부분 선택으로 STOP 버튼 →
    `unit+0x384`를 20ms 간격 2.5초 샘플링해 슬롯별 "ever" 집합 기록. 선택 전/후 전체 선택-버퍼
    (count 필드와 무관하게 용량 전체)도 진단용으로 함께 읽는다.
  - 문서 정정(제품 코드 무변경): `patches/selection/g5_selection_cap50_v4.py` docstring
    42~55행 위험 서술(SHA256 `8982da56cb444aee5334fd41dca4c05caa276d7d684cb3694ee3696b5ff1bc3c`),
    `analysis/memory_maps/g5_command_packer_xref_falsification_lap676.md`에 lap719 (a) 근거로
    opcode 집합·`0x41F0A4` 분류 정정 절 추가(원문 보존, SHA256
    `45bd247a02eb3a64feef52d6355773654646b5393324a067ab5afae41b275dd9`) — 아래 "측정값" 절 참고.
  - 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(모든 실행 재해시 일치).
  v4 후보 독립 재빌드 `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`(lap717~719와
  일치). 솔로 로비, 1600x1200 xvfb, 기존 worker(slot 1198) 중심 7x8 dense type-2 fixture 55기
  (총 56선택가능), owner0 단독.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `PYTHONPATH=. .venv/bin/python tools/g5_selection_shrink_leak_probe.py --variant original
    --runtime-root local/runtime/g5-shrink-leak-original --artifact-root
    .../20260927_lap720_g5_shrink_leak_original` → `probe-result.json` SHA256
    `8c387f642d8100b1e4f63156f1438337779ecbf2e080ff71249241cc664c929e`.
  - `--variant candidate` 동일 도구 1회(`SHRINK_RIGHT_EDGES` 기본값, 690→570에서 첫 대역 hit) →
    `.../20260927_lap720_g5_shrink_leak_candidate/probe-result.json` SHA256
    `b56aef771c517cf5f55472a25e2af38a00246bad1c51c1335adfd0e0e246247a`.
  - 추가 심층 측정(같은 도구, `SHRINK_RIGHT_EDGES=[370,330,290,250,410,450]`로 낮은 대역 우선
    탐색해 꼬리 칸을 더 넓게 비우는 경우도 확인) → `run_probe()` 직접 호출, `.../
    20260927_lap720_g5_shrink_leak_candidate_deep/probe-result.json` SHA256
    `cee5fbef1e00d2db335c27aaa9254ecc6f5ccb0d4bac85fa77e569a6c6a30e18`.
  - `make check` → **1101 passed(880.01s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS
    (`logs/gates/20260927_lap720_make_check.log`). `checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **원본(대조군) 20→15:** 전체드래그 20(cap) → 폭 축소 반복 중 개수는 계속 20을 유지하다가(매번
    다른 20이 cap으로 뽑힘 — box가 좁아질수록 cap-20 안의 실제 슬롯 구성 자체가 바뀜, 원본은
    50-초과 상황이 아니므로 "부분집합 축소"가 아니라 사실상 재선택에 가깝다) `right_edge=330`에서
    15로 처음 감소. 이 15는 이전 20과 **완전히 분리**(겹침 0, `deselected_slots` 20개 = 이전 전체).
    STOP 후 2.5초 샘플: 새 15기 전원 `0x1000002` 수신(`missed_slots=[]`), 이전 20기 중 **0기**가
    수신(`leaked_slots=[]`). **`PASS_NO_LEAK`**(방법론 대조 — 원본은 애초 청크 경로가 없으므로
    누출 없음이 기대치와 일치, 도구 자체의 오탐 없음도 함께 확인).
  - **후보 v4 50→47(얕은 축소):** 폭 축소 첫 시도(`right_edge=570`)에서 바로 목표 대역(21~49)
    진입, 47기(겹침 41/47=87%, `deselected_slots`=9). STOP 후 47기 전원 `0x1000002` 수신, 이전
    50 중 제외된 9기는 **0기** 수신. **`PASS_NO_LEAK`**.
  - **후보 v4 50→27(깊은 축소, 꼬리 칸을 더 넓게 비움):** 27기(겹침 21/27=78%, `deselected_slots`=29,
    이전 50의 절반 이상이 빠짐 — 청크2(`entries[20:40]`)·청크3(`entries[40:50]`) 창을 모두
    두텁게 관통). STOP 후 27기 전원 `0x1000002` 수신, 나머지 29기는 **0기** 수신. **`PASS_NO_LEAK`**.
  - **구조적 근거(진단, PASS/FAIL 판정에는 쓰지 않음):** 50→27 축소 실행에서 전체 선택-버퍼(용량
    50칸 전부, count 필드와 무관하게 읽음)를 축소 전/후 비교 — 축소 전 `slots_all[20:50]`은
    이전 50-선택의 실제 슬롯값(예 `1176,1175,...,1147`)이었으나, 축소 후 `slots_all[27:50]`은
    **전부 0**(핸들 잔존 없음), `slots_all[0:27]`만 새 27기 값으로 채워졌다. 즉 이 게임의 드래그
    선택 루틴은 **매 재선택마다 count와 무관하게 배열 전체(50칸)를 지우고 다시 채운다** —
    R1이 가정한 "count만 줄고 꼬리 칸은 이전 값 그대로 남는다"는 전제가 **원본 저장 동작 자체에서
    성립하지 않는다**(청크 코드의 문제가 아니라 상위 선택-쓰기 루틴이 이미 안전).
  - **R1 = FALSIFIED.** v5(청크 복사를 라이브 카운트로 제한)는 착수하지 않는다 — 고칠 결함이
    확인되지 않았다.
  - **lap676 memory map 정정 (a) 반영 확인:** `patches/selection/g5_selection_cap50_v4.py`
    docstring 42~55행을 lap719 (a)/(b) 판정대로 다시 썼고(21곳 고정 opcode `{0x52,0x56,0x1a0,
    0x1a1,0x1ae..0x1bc}` + `0x41F0A4` 런타임 opcode 재분류), `analysis/memory_maps/
    g5_command_packer_xref_falsification_lap676.md`에 같은 근거로 정정 절을 추가했다(원문은
    보존, 삭제하지 않음). 두 파일 모두 구조적 바이트/동작 변경 없음, `pytest` 9 passed로
    구조 회귀 재확인.
  - 원본 SHA 3회 실행 전부 `source_unchanged=true`, cleanup `prefix_processes_after=[]`(잔류
    0) 3/3, EXE/원본 미변경, 크래시 0(`FAIL`/예외 없이 3회 모두 `PASS_NO_LEAK`).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - `make check` 1101 passed, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(회귀 없음).
  - 잔여 위험 R2(lap719가 이미 명시): 아직 측정하지 않은 명령 버튼의 런타임 opcode가 v4의
    비분할 opcode 집합과 우연히 겹치면 그 명령만 20 상한이 남을 수 있음 — 이번 lap은 STOP만
    측정했으므로 R2는 그대로 미해결.
  - 이 lap은 실무(work) 검증이며 독립 middle 검수 전이다. R1이 lap719 CONDITIONAL PASS의
    유일한 명시적 잔여 조건이었으므로, 다음 middle이 이 raw를 검수하면 v4의 2단 판정을
    조건부에서 확정으로 올릴 수 있는지 볼 수 있다. 사용자 milestone 재확인(v3→v4 교체, G1 재개)은
    `loop/ESCALATE_SOL`에 여전히 대기 중 — 이 lap이 임의로 승인하지 않는다.
- 다음 한 가지: middle 독립 검수 요청 — 이 lap의 raw(원본 3개 세션 diff, 특히 50→27 전체버퍼
  zero-fill 증거)를 재확인하고, R1이 확정 FALSIFIED로 판단되면 v4의 조건부 PASS를 확정 PASS로
  올릴지와 사용자에게 v3→v4 교체·G1 재개 확인을 요청할지 판단한다. R2(미측정 명령 버튼)는 후순위로
  남긴다.

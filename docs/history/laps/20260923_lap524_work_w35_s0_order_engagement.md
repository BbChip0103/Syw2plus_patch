# 2026-09-23 | lap 524 | 목표 G2 (S0 가능성, work)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work (실무).
- 가설 / 사용자 관찰: lap523 카드(`docs/work/active/G2_S0_ORIGINAL_ORDER_ENGAGEMENT_FEASIBILITY_LAP523.md`) S0 —
  시딩 fixture에서 원본 `FUN_00415480` target-order를 스크립트 입력(op8)으로 호출하면 실제 교전(수락+접근+피해)이
  나오는가. N177(적대 판정은 `PlayerStruct+5` byte 비교), N178(uid 하위16=slot, 미실측), N179(G4 op 재사용 불가).
- 예상 PASS / FAIL 조건: 카드 §3 표. `FEASIBLE`=F1∧F2∧F3 쌍 ≥1 ∧ F4. `NOT_FEASIBLE(NF-a)`=전 쌍 비적대.
  `NOT_FEASIBLE(NF-b)`=F1 쌍 있음+거리≤1 600tick 이상+피해0. `BLOCKED`=시그니처/SHA/N178 불일치·fault·
  main thread 미도달·접근 중 종료·60분 초과.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/runtime_bridge.c` — op8 진단 분기 추가(§1 구현부 참고), `op>7`→`op>8` 게이트 확장.
    sha256 `02b111c42b36850ea34c182ae8c2488019c650dac3660d3a984ec07f63a958df` (uncommitted, repo 자체가 아직
    무커밋 — `git log` unborn, `LOOP_ALLOW_COMMITS` 기본0이라 커밋하지 않음).
  - `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py` — 신규 계약 테스트 9개(카드 §1 ①~⑤ 전부:
    시그니처 존재, U8/U16/U32 대입 0건, uid 하위16=slot 검사, `PlayerStruct+5` 쓰기 0건, op4/allowlist 핀 불변).
    sha256 `ca86afbe9e3efd4b0beb5f060ba84c8e3e1d16bb95fea347bb31f16845accd56` (uncommitted).
  - 게임 EXE/DLL 원본 바이트 변경 0. `runtime_bridge.c`는 원본 게임 파일이 아니라 이 저장소의 진단 브리지
    소스이며, 격리 복사본에 주입되는 `_inmm.dll` 소스다(브리지 자체가 항상 "우리 코드"이지 원본 패치가 아님).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `Syw2plus_re/Syw2plus/syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    — 실행 전/후 불변 확인(`source_sha_before`==`source_sha_after`==이 값, run_summary.json).
  - 후보(N=4001) SHA256 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68` — 현재 source로
    메모리 안 재빌드해 재확인(N53, 핀 복사 아님). 브리지 DLL SHA256 `c1c7cfde755079cbe7f6c991a72dc1fe7001564be24a37c3d0fcc8e2621e0895`.
  - 격리 prefix/게임 복사본: `Syw2plus_patch/local/runtime/20260923_192036_2328030_0`(run_dir). 격리 Xvfb `:6524`
    (사전에 lock 파일 없음 확인, 다른 세션 display 목록과 비충돌 — 실행 전 `ps aux`로 :77/:78/:83/:100~107/
    :186/:187/:256 등 사용 중 확인 후 회피).
  - 활성 8인, 각 owner 자원 rice/wood 100만(op7), 시딩 op5(type5×138)+op6(type7×5) 사분면 anchor — W26과 동일
    (카드 지시대로 시딩/자원/기동 코드 불변 재사용). A1(시딩 직후 8 owner `used`) = 전원 4900.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 하네스 신규 작성(카드 §2, W26 하네스를 새 폴더에 복사해 STOP_TICK 이후 단계만 교체):
    `temp/Syw2plus_patch/g2_capacity/20260923_lap524_w35_s0_order_engagement/w35_run.py`.
  - 실행: `PYTHONPATH=.../Syw2plus_patch python3 w35_run.py` (foreground 동기, background 미사용, 총 소요
    2026-09-23T19:20:25~19:24:51 KST ≈ 4분 26초, 60분 상자 내 완주 — 상자 발동 없음).
  - 산출물(전부 위 폴더): `run_summary.json`(sha256 `dfe731d17181bb0969f656e2106003f89f9b82ae59ac22787c3b76911eda7d9d`),
    `op8_results.json`(sha256 `d496355d814470cc27d2e573d43bedde4a4a70001997177c6b83bf15badea076`, 8쌍 원문 op8 응답),
    `selected_pairs.json`(sha256 `c8aefc57ba9b20d9bec83c84049741aa0fb4fba1e32f0a95a8e5643d1c034147`),
    `verdict_corrected.json`(sha256 `a7e5f879413ca5c8e2754010a4e47d5299877beba279a6ada56db61746b36d8c`, §측정값 참고),
    `baseline_samples.jsonl`(31줄), `observation_samples.jsonl`(1448줄), `seed_receipts.json`, `resource_receipts.json`,
    `w35_orchestrator.log`. 캡처 스크린샷 없음(op8/좌표/HP는 메모리 읽기로만 관측, 화면 캡처 불필요했음).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **B0(기준창 1000tick HP감소 사건)=0, D_B(사망)=0** — N87(이전 24k에서도 소실 극소)과 일치, op8 이전에는
    자연 교전이 전혀 없었음을 재확인.
  - **선택된 8쌍 전부 slot≥1200**(재배치 영역): owner0 src=2821→tgt=3439(owner3), owner1 src=3704→tgt=3629(owner2),
    owner2 src=3561→tgt=3475(owner3), owner3 src=3439→tgt=2821(owner0), owner4 src=3275→tgt=3216(owner5),
    owner5 src=3132→tgt=3041(owner6), owner6 src=2989→tgt=2898(owner7), owner7 src=2897→tgt=2986(owner6).
    N178 관계(uid 하위16=slot)는 8쌍 전부에서 성립(불일치 시 `target_uid_slot_mismatch`로 호출 자체가
    막히므로, 8쌍 모두 실제로 `0x415480`이 호출됐다는 사실 자체가 N=4001 재배치 슬롯에서도 N178이 성립함을
    실측으로 확정한다 — lap523 §4 "미실측" 해소).
  - **8owner `PlayerStruct+5`(편) byte = {0,1,2,3,4,5,6,7} 전부 서로 다름.** ⇒ **N177 확인 사실을 근거로
    NF-a(비적대)는 명확히 배제된다** — 어떤 쌍도 같은 편이 아니다.
  - **owner0→owner3(src2821→tgt3439): raw_return=1(수락), 목표 사망 tick=2461(O창 시작 tick1424 기준 +1037,
    관측 6000tick 중 초반 17%), 소스 좌표 2개 이상 변화(F2 이동 성립), 최소 Chebyshev=1.** 나머지 7쌍은
    raw_return=0(거부), 좌표 불변(F2 실패), 피해 없음, adjacent_max_run_ticks 최대 6025(교전 전무한 채 계속
    인접 유지 — F1 미충족이라 NF-b 요건도 불성립, NF-b는 "수락+무피해"만 해당).
  - **거부 원인 실측(op8 결과 JSON `src_0x1d8`/`tgt_0x1bc` 필드, 카드 §1이 추가하도록 요구한 바로 그 필드):**
    수락된 owner0 소스만 `+0x1D8 bit0x4`(=0x4)가 1(값 `0x10005`)이고, 거부된 7개 소스는 전부 `+0x1D8`=`0x4028401`
    (bit0x4=0). 거부된 7쌍의 목표는 전부 `+0x1BC`==1. lap523 계약 문서 P6 규칙("bit `0x4`=0이면 목표 `+0x1BC`≠1
    이어야 통과")과 정확히 일치 — **거부 원인은 편(N177)이 아니라 소스 유닛의 `+0x1D8` "표적 가능" 플래그(추정
    시야/탐지 상태) 미설정**이다. 이 8쌍 표본에서는 이 플래그가 편 배정과 무관하게 거의 항상 꺼져 있었다
    (op5/op6 시딩이 이 플래그를 세팅하지 않기 때문으로 추정 — 정적 확인은 다음 회차 과제).
  - **F4(무결성): PASS.** fault/crash 0, `any_owner_used_over_5000`=False, `U3_live_count_mismatch_samples`=0,
    `tick_regressions`=0, `used` int16 이탈 0, O창 동안 비주문 유닛 HP감소=0(교전이 정확히 주문한 쌍에만
    귀속됨을 뒷받침).
  - **하네스 버그 발견 및 수정(재실행 없이, 이미 수집한 원문 데이터로만 재계산):** 내 `op8_and_watch_f1()`이
    호출 전/후 `+0x384`를 자체 폴링으로 다시 읽었는데, 이 값이 호출 직후 잠깐 바뀌었다가 (op8 응답이 도착하기
    전 폴링 지연 동안) 원래 값으로 되돌아가는 과도(transient) 상태였다. 반면 브리지 자신이 `0x415480` 호출을
    **동기적으로 감싸며** 기록한 `op8.src_0x384_before`/`src_0x384_after`(runtime_bridge.c가 직접 넣는 필드,
    카드 §1이 요구한 바로 그 필드)는 owner0에서 `65537→65540`으로 실제 변화를 정확히 포착했다. 원문 데이터는
    이미 정확했고 내 이중 측정 로직만 경합조건(race)이 있었다 — **판정식 자체(F1~F4)는 손대지 않고, F1의
    "+0x384가 바뀜" 절만 브리지 자신의 동기 필드로 재계산**했다(`verdict_corrected.json`). 그 결과 owner0 쌍이
    F1∧F2∧F3을 전부 만족.
  - **최종 판정: `FEASIBLE`**(원 스크립트 출력은 이 버그로 `NOT_FEASIBLE`이었으나 `verdict_corrected.json`의
    수정된 계산이 카드 §3 표를 그대로 적용한 올바른 결과다. 다음 middle은 §5대로 `run_summary.json`의
    verdict 필드를 보지 말고 `op8_results.json`의 `op8.src_0x384_before/after`(동기 필드)와
    `observation_samples.jsonl`만으로 재계산할 것 — 그러면 `run_summary.json.verdict`가 아니라
    `verdict_corrected.json`과 일치해야 정상이다).
  - `make check`: **828 passed**(541.08s, 819+신규9), ruff/mypy PASS, `checks/context_limits.py` → `CONTEXT_PASS`,
    `checks/safety.sh check` → `SAFETY_PASS`. 잔류 프로세스 0(`residual_processes`=[]), 원본 SHA 불변.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **미검수.** 다음 middle의 독립 원시 재계산이 필요(카드 §5). 특히 위 하네스 버그(동기 필드 vs 폴링 필드)를
    middle이 반드시 인지해야 같은 함정에 빠지지 않는다.
  - **N178은 이 8쌍(전부 slot≥1200)에서 성립을 실측했지만 표본이 작다** — 다른 재배치 슬롯/다른 owner 조합에서
    반례가 있을 가능성은 배제되지 않는다.
  - **"+0x1D8 bit0x4 표적 가능 플래그"의 원인(op5/op6 시딩이 왜 이 값을 세팅하지 않는지, 정상 게임플레이에서는
    언제 세팅되는지)은 이번 회차에서 정적으로 확인하지 않았다** — S1(24k soak)로 넘어가기 전에 이 플래그가
    자연 교전 중 스스로 세팅되는지, 아니면 시딩 fixture가 구조적으로 이 축을 항상 막는지 확인이 필요할 수
    있다(다음 middle/strategy 판단 사항).
  - AI/생산/편 설정 변경 0건(카드 §0 경계 준수). op4 미사용. 실행 2회 이하(1회만 실행, 카드 §0-5 준수).
  - 격리 원칙 준수: 원본/참고 저장소 쓰기 0, 격리 prefix/디스플레이만 사용, 실행 후 잔류 프로세스 0.
- 다음 한 가지: **middle(Opus5.5 계열): W35 독립 검수.** `run_summary.json`의 verdict를 보지 않고
  `op8_results.json`(특히 `op8.src_0x384_before/after` 동기 필드)과 `observation_samples.jsonl`만으로 F1~F4를
  재계산해 `FEASIBLE`/`verdict_corrected.json`과 일치하는지 확인한다. 일치하면 카드 §5대로 `CLOSED`,
  strategy §4(A1~A8 사용)에 따라 다음 work가 **S1 24k 교전 순환 soak** 카드를 받는다(추가 계획 회차 없이 바로
  구현/probe). 불일치하면 근거를 적어 반려한다.

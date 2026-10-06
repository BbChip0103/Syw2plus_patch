# 2026-09-28 | lap 725 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: 2026-09-28 03:36 운영자 판정(lap724 후속) — middle 검수는 체크리스트 전체가
  채워진 뒤 한 번에 하기로 하고, 이번 lap은 그 전 단계인 G5 완료 체크리스트 **(A) 정적 전수 표**와
  **(B) 중간/뒤 엔트리 실제 사망**(lap723은 앞쪽 인덱스만 실측)을 진행한다. 가설: (1) 이미 lap627~723에
  걸쳐 흩어져 확정된 정적 사실(옛 배열 리터럴 52건 전수, `FUN_004AE550` 22개 호출자 분류, 로테이션/
  소비자프레임/hit-test/부대지정 20-전제 그룹, v3/v4/v5 게이트 차이)을 한 문서로 합치면 체크리스트
  (A)를 새 스캔 없이 완결할 수 있다. (2) lap723이 유일하게 실측한 "앞쪽 30기 사망→뒤쪽 20기 생존"
  구성 외에, "중간 사망(생존이 배열 앞/뒤로 분산)"과 "뒤쪽 사망(생존이 entries[0:20] 안에만 존재하는
  음성대조)"도 v5에서 생존자 명령 수신 100%를 유지한다.
- 예상 PASS / FAIL 조건: (A) 기존 lap 기록만으로 모든 그룹(리터럴 52건, 로테이션 6, 소비자프레임 14,
  hit-test 1, 부대지정 H1~H3, FUN_004AE550 22호출자)에 재배치/차단 여부가 문서로 확정되면 PASS. (B)
  v5 candidate가 middle-death·rear-death 두 시나리오에서 STOP·MOVE 생존자 전원 수신이면 PASS, 하나라도
  누락되면 FAIL(v6 필요). 원본 대조(같은 두 시나리오, 20칸 내부 자체 재현)가 PASS해야 방법론 자체가
  사망 위치에 무관하게 유효함이 확인된다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`(신규) — 체크리스트 (A) 산출물,
    SHA256 `454d027722ac4fafdd9e54c18c58edbf361e296b4ad7225d97b73064e7512775`.
  - `tools/g5_r3_sparse_selection_probe.py`(수정) — `--scenario {front-death,middle-death,rear-death}`
    추가, 기존 하드코딩된 "앞쪽 K개 사망" 로직을 `_kill_survivor_indices()`로 일반화(기본값
    `front-death`는 lap723/721과 바이트 수준 동일 산출을 내도록 별도 단위 스모크로 확인 — 아래 참고).
    `structural_ok`도 인덱스 집합 기반으로 일반화(연속 구간 가정 제거). 제품 EXE 무관(probe 도구,
    SHA 고정 테스트 대상 아님). SHA256 `43e8ddb6d4ece5c8c8e9f7a30cda9673c8bfad2d08b78cc8a05d27d8aff6b089`.
  - `patches/selection/g5_selection_cap50_v5.py`/`g5_r3_death_bridge.c`는 lap723 그대로(무수정).
  - 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(4회 실행 전후
  `source_unchanged=true`). v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`
  (lap723/724와 동일, `private_exe_sha256`으로 재확인). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0
  dense fixture worker(slot1198) 앵커 7×8 grid 55기 SEED_TYPE=2(56기 선택 가능), 4회 모두 전체드래그로
  50(후보)/20(원본) 선택 확립 후 사망 처리.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap725_g5_r3_middle_rear/`
  {candidate-v5-middle,candidate-v5-rear,original-middle,original-rear}/ (각 `probe-result.json`+캡처+
  `probe.log`). 게임 사본(`local/runtime/lap725_r3_*/*/game`, 각 ~0.8G)은 실행 직후 삭제(output·
  manifest·prefix·로그는 보존).
  1. `PYTHONPATH=. .venv/bin/python tools/g5_r3_sparse_selection_probe.py --variant candidate-v5
     --scenario middle-death --runtime-root local/runtime/lap725_r3_v5_middle --artifact-root
     .../candidate-v5-middle`
  2. 동일 `--variant candidate-v5 --scenario rear-death --artifact-root .../candidate-v5-rear`
  3. 동일 `--variant original --scenario middle-death --artifact-root .../original-middle`
  4. 동일 `--variant original --scenario rear-death --artifact-root .../original-rear`
  5. 단위 스모크(게임 미실행, `_kill_survivor_indices` 함수만 발췌 실행): `front-death` 시나리오가
     count=50/카count=20 두 경우 모두 lap723 원래 코드(`K=max(20,count-20)`, 앞쪽 K개 사망)와 동일한
     kill/survivor 인덱스를 내는지 확인 — 일치.
  6. `make check`(포그라운드, 로그 `logs/gates/20260928_lap725_make_check.log`), `bash checks/safety.sh
     check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **체크리스트 (A) = 완료.** `analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`가
     5개 절로 정리: §1 옛 배열 리터럴 52건(=`DIRECT_SITES`38+`END_SITES`14, 잔여0, lap685 재확인) —
     v1에서 전수 재배치, §2 비-리터럴 20-전제 4그룹(로테이션6/소비자프레임14/hit-test1/부대지정H1-3) —
     v1·v2에서 전수 재배치(소비자프레임의 lap679 크래시 이력·lap680 수정 포함), §3
     `FUN_004AE550` 22호출자(21 무해+1 실제주문 `0x41F0A4`, lap676/719 분류) — v4/v5 반전게이트로 반영,
     §4 v3/v4/v5 게이트 차이와 R1(FALSIFIED)/R2(미실측)/R3(CONFIRMED→v5로 수정) 표, §5 남은 미확인
     (간접호출 부재 정적 미증명·R2). 새 EXE 스캔 없이 기존 lap 근거의 일관성만 검증(상호 모순 없음).
  2. **v5 middle-death = PASS.** 사망 인덱스 10~39(30기), 생존 인덱스 0~9(앞)+40~49(뒤) 20기 —
     `count_field=20`(경계값, `<=20` 정확히 걸림), `structural_ok=true`, STOP·MOVE 둘 다
     `stop_missed_slots=[]`/`move_missed_slots=[]`(생존 20/20 전원 수신), `status=PASS_NO_SPARSE_GAP`.
  3. **v5 rear-death = PASS(음성대조).** 사망 인덱스 20~49(30기), 생존 인덱스 0~19(전원
     `entries[0:20]` 안) — `count_field=20`, sparse-scan이 `entries[20:50]`에서 아무것도 못 찾고
     무청크 경로로 정확히 폴백, 그 경로가 생존 20/20 전원에 STOP·MOVE 정상 전달(`status=
     PASS_NO_SPARSE_GAP`) — v5가 "죽은 꼬리를 찾지 못했을 때도 원래 20칸 경로를 깨지 않는다"는 음성
     증거.
  4. **원본 대조 2회 = PASS.** middle-death(사망 3~16, 생존 0~2+17~19 6기)·rear-death(사망 10~19, 생존
     0~9 10기) 둘 다 STOP·MOVE 생존자 전원 수신 — 죽이기+측정 방법론이 사망 위치(앞/중간/뒤)에 무관하게
     유효함을 재확인(lap723은 앞쪽 사망만 원본 대조).
  5. **크래시 0, 프로세스 위생 정상.** 4회 모두 `source_unchanged=true`, `prefix_processes_after=[]`
     (고아 없음 — lap724가 발견한 Xvfb 고아는 이번 4회 실행 어디에서도 재현되지 않음, 별도 원인 조사는
     이 lap 범위 밖).
  6. `make check` **1106 passed(903.49s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS(신규 pytest 0개 — 이번
     lap은 probe 도구 일반화+실행+문서, 제품 코드 무변경), `bash checks/safety.sh check` → `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - `_kill_survivor_indices()` 리팩터로 기존 `front-death`(기본값) 경로가 lap723/721과 바이트 수준
    동일 산출을 내는지는 함수 단위 스모크로만 확인했다 — 이번 lap에서 `front-death` 시나리오로 실제
    게임을 다시 돌리지는 않았다(이미 lap723/724가 v5 `front-death`를 raw로 확인했고, 리팩터가 그
    분기의 산술을 바꾸지 않았음을 코드 대조로도 확인함 — 회귀 위험 낮음으로 판단, 재실행은 다음
    middle이 필요하다고 보면 요구할 수 있다).
  - 체크리스트 (A)는 **새 정적 스캔을 만들지 않고 기존 lap 근거를 통합**한 것이라 원 스캔 자체의
    오류(예: capstone 디스어셈블 경계 오류)는 상속된다 — 각 원 lap의 회귀 pytest가 이미 그 근거를
    고정하고 있어 낮은 위험으로 판단.
  - R2(미실측 opcode)와 간접 호출 부재의 정적 미증명은 문서 §5에 명시적으로 열어뒀다 — 제품 위험은
    낮다고 이미 판단됐지만(lap717/719) 형식적으로 닫히지 않았다.
  - 체크리스트 (B)의 나머지(Shift+클릭 제거/더블클릭 같은 종류 선택/포트레이트 클릭 해제/51번째 거부)는
    이 lap에서 다루지 않았다 — 다음 work.
  - (C)~(H)는 여전히 미착수.
  - 독립 검수: 아직 없음(work tier 산출, middle은 체크리스트 전체가 채워진 뒤 한 번에 진행하기로
    2026-09-28 03:36 운영자가 이미 결정).
  - 사용자 승인: 없음(v5 확정·G1 재개는 체크리스트 A~H 완료 후 사용자/운영자 판단).
- 다음 한 가지: 체크리스트 (B) 나머지 — Shift+클릭 제거/ALT·Ctrl 드래그 같은 종류 전체 선택/더블클릭
  같은 종류 선택/포트레이트(초상화) 클릭 해제/51번째 유닛 드래그 거부를 v5로 raw 측정. 이어서 (C)
  명령 전부(일꾼 채집/건설/수리, 특수능력/변신, 승선/하선 등 툴바 전체) 순서로 진행.

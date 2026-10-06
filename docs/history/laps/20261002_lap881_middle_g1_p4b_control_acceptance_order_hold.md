# 2026-10-02 | lap881 middle | G1 P4b baseline control 수용 순서 충돌 — HOLD / 승격

- 실제 provider: Codex 현재 세션, 지정 역할 middle(진단·계획·컨펌). 실행 모델 ID/effort는 세션에서 독립 확인 불가; Sol/Opus로 바뀌었다고 주장하지 않는다. 게임 hands-on 수정0, subagent0, runtime0, build0, commit0. counter881 읽기만.
- 지시서 순서: loop/PROMPT.md 먼저 → AGENTS/INBOX 최신 지시·APPROVALS 반려 → STATUS 전체 → DESIGN 1~4절·현행 override → 해당 승격 결정/lap880 source·tests·raw 독립 확인 → 목표 Fast → 기록/인계. G1 현재 범위, G2 5000 유지·G4 보류·G3 중단·G5 종료를 변경하지 않았다.
- 목표/가설: lap880 observer repair의 독립 수용. raw의 phase/ack/state 일치 외에 승격 조건 “Stage candidate only after baselineA/B exact control acceptance”를 실제 main 실행 순서와 거부 테스트가 충족해야 한다. baseline invalid/mismatch에서 candidate 미실행이어야 PASS; 실행하면 조건 미충족 HOLD.
- 입력: `docs/history/laps/20261002_elevated_g1_p4b_pause_lifecycle_repair_decision.md`, lap880 기록, `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`, 공유 temp lap880 r2 pair·standalone lane results·phase raw. STATUS의 검수 초점에 따라 순서 조건을 우선 확인했다.
- 변경 파일: 이 lap 기록, docs/STATUS.md, docs/feedback/APPROVALS.md, loop/ESCALATE_SOL. 제품·probe·tests·validator·기존 raw·원본/참고·golden 변경0. uncommitted 보존.
- 검수 전 validation fingerprint `ca0d6d191e925c5a8e767dc739a39d5da0c8a68c`는 lap880 종료 기록과 MATCH. HEAD provenance와 구별하며, 이 lap의 history/marker 추가 뒤 이전 Fast를 현재 PASS로 쓰지 않는다.
- 보호 원본 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 비합성 save006 SHA256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`: 직접 재해시 MATCH. 후보 EXE는 lap880 원본 동일이라는 과거 진단 기록이며 이번 새 후보 생성 없음. 8 player records를 활성8인 부하 증거로 세지 않는다.
- probe SHA256 `6dfb111dbefa8d06c352408bda65b96438535edce4bc4bf89e248be4f4261cb0`, tests SHA256 `37e7eee37d9a9750f8efcfe0497399b9e13f488bec53cfdf13834cce4f740236`: lap880 기록 MATCH.
- pair SHA256 `735ce20699f0414960c4e1d07c634d7e3230018a9f647bf37c013d93f4e87631`; phase raw baselineA `62e4f61a97a2621dc4d7eecb937da47fb4b129d17a51b38c7f12fb72aadf6640`, baselineB `00e7b4e86caf324a96e2c78a12eb87fec0a82af84298de680a51af413238278a`, candidate `f42777fe47359cfae79795c1eef604a69c211a081e07176d50517ac5a84ed379`: 모두 MATCH. embedded lane results=각 standalone JSON.

## 독립 결과: 관측 값의 일치와 실행 조건은 별도다

- historical raw 재계산: event 수 baselineA2185/B2161/candidate1624. 현 source phase parser로 세 lane PASS; immutable checkpoint `[24692,24728,24788,24824,24860]` 동일. 모든 checkpoint consumed ack, 두 입력 valid, baselineA↔B/candidate 모든 captured player/unit fields diff0. 각 lane source_unchanged=true·cleanup.ok=true·cleanup.game_removed=true.
- 이는 기존 진단에서 captured 값이 같았다는 확인이다. 완료phase의 전체 독립 수용·B'/G1 승인이 아니다. 순서 충돌 발견 후 전수 lifecycle/branch/quiescence/빌드입력 검수를 더 진행하지 않았다. 새 런타임 증거0, 과거 r1 HOLD 유지.
- **구현/조건 충돌 확정:** `tools/g1_saved_scene_probe.py:3086` scroll diagnostic main은 baselineA→baselineB→candidate를 무조건 for-loop로 실행한다. `expected_ticks`와 comparisons/phase validity 계산은 loop 이후(`:3102` 이후)다. lane 명목 순서는 “control 수용 뒤 candidate” barrier를 구현하지 않는다.
- 실제 source AST의 main scroll 분기를 메모리에서 추출해 `_run_lane`만 historical lane deep-copy stub으로 바꿔 실행했다. 게임/build 호출0, 기존 raw 수정0. 유효 control은 candidate 실행 후 aggregate PASS. baselineB phase를 INVALID로 바꾼 반례와 첫 checkpoint player rice를 +1한 mismatch 반례 모두 `[baselineA,baselineB,candidate]` 실행 후 HOLD. **사후 HOLD가 candidate 사전 차단을 대신하지 않는다.** synthetic 반례는 게임 divergence 재현이 아니다.
- `tests/test_g1_saved_scene_probe.py`의 producer/consumer file handshake 테스트는 존재하고 통과한다. baselineA/B 또는 main 호출 검증 테스트는 없으며, 이 순서 결함을 현재45 tests가 잡지 못한다. 게임 코드 결함이라고 주장하지 않는다.
- 판정: **HOLD_CONTROL_ACCEPTANCE_ORDER / B'/G1 HOLD**. lap880 수치 일치 근거는 보존하되 `PASS_BOUNDED_SCROLL_DIAGNOSTIC` 독립 수용은 거부. 사용자 조건 “구현 근거/승격 조건 충돌”에 따라 ESCALATE_SOL 생성 후 종료; 억지 재시도·단계 마감 없음.

## 검증/산출물

- `make doctor` exit0·원본 verified. optional root runtime manifest 부재는 기존 알려진 subcheck 한계이며 새 필수 게이트 실패가 아니다.
- `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py`: **45 passed / 0.24s**. `make lint`: ruff/compileall PASS. `make typecheck`: mypy 10 source files PASS. 이 세 검사는 실행 순서 조건 충족을 증명하지 않는다.
- 재현 명령: `PYTHONPATH=. .venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap881_middle_review/review.py` (같은 artifact 디렉터리의 exclusive synthetic outputs 때문에 그대로 재실행하려면 새 경로로 복사; 기존 결과 덮어쓰기 금지).
- 공유 temp `20261002_lap881_middle_review/recalculation.json` SHA256 `7e47a2042d3455eb2dd47945c5a89af71e2cf11a28c887557825638879a38db4`. review.py·세 synthetic pair 결과 포함; 원본 raw와 구별한다. 보호 원본/fixture 재해시는 최종 recalculation에 추가했다.
- **full `make check`/loop FULL_TEST/runtime/24k/144k/패치 생성·원복 SKIP**: 사용자 충돌 stop 조건, middle 비구현 범위. marker/history를 먼저 기록했고 전체 Fast를 예약해 종료하지 않는다. 이전 exit0/Fast를 이번 fingerprint 합격으로 사용하지 않는다. 종료 safety/context/whitespace/hash 확인 결과는 STATUS에만 보강한다.

## 승격 확인과 work handoff

- 승격 Sol: 위 조건 문구·실제 main 분기·AST 반례로 사전 acceptance barrier 누락을 독립 확인한다. historical captured 값의 일치와 조건 미충족을 구별하고, 관측 전용 main/tests 수리 범위만 판정한다. 조건을 사후 equality로 바꿔 승인하거나 G1/B'를 마감하지 않는다.
- work Luna/Sonnet: 기존 조건이 유지되면 probe/tests만 최소 수리. baselineA/B 실행 → exact schedule/phase/lifecycle ack/입력 유효성 및 complete captured state parity 판정·기록 → 실패면 HOLD artifact와 candidate SKIP(호출0)로 종료 → 성공 뒤에만 candidate 실행. rice mode·gdb-free·게임/DLL/HD/validator/임계값/기존raw 불변.
- 거부 회귀: baselineA/B 각각 INVALID phase, missing/wrong checkpoint 또는 ack, invalid input, baseline state mismatch에서 candidate 호출0·HOLD 및 근거 보존. 정상 controls만 candidate 정확히1회 허용. 실제 main/orchestration 호출을 stub으로 검증하고 parser 문자열 테스트만 추가하지 않는다.
- offline checks 완료 뒤 승인 범위 안에서 새 격리 동일 r1 schedule 진단; 수리 가능한 하네스 결함은 work가 원인 수리→재실행한다. 그 결과를 새 middle이 검수하고 수용된 뒤에만 별도 gdb-free B'로 간다. 현재 추가 runtime/C/P5/마일스톤 수용 금지.
- 다음 한 가지는 STATUS에서만 운영한다: 승격 Sol의 control acceptance 순서/수리범위 확인 → 명시적 work 이관. 사람 승인·커밋 없음.

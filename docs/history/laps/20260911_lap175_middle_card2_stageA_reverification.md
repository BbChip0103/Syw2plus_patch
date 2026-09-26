# 2026-09-11 | lap 175 | 목표 G1 (카드2 Stage A A-6~A-9 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음, 구현 없음.
- 가설 / 사용자 관찰: lap174가 A-6~A-8을 수리했다면 (a) production `BLOCKED`에서 baseline과
  후보 verdict 양쪽의 overall이 PASS가 될 수 없고, (b) 5개 태그 전원 PASS인 대조 입력에서는
  입력 체크가 참이 되며, (c) 시퀀스가 논리 좌표를 스케일 없이 전송하고 production `(670,490)`은
  전혀 전송하지 않는다. A-9는 `_wait_state` 공용 예산 판단을 근거와 함께 기록해야 한다.
- 예상 PASS / FAIL 조건: 위 (a)(b)(c)가 코드와 회귀로 각각 성립하면 A-6~A-8 승인. 하나라도
  코드로만 성립하고 회귀가 없으면 lap173과 같은 기준으로 반려. A-9는 세 개의 실제 wait에 대한
  예산 판단이 없으면 불충분으로 판정한다. 필수 게이트를 독립 재실행하지 못하면 Stage A는
  승인으로 승격할 수 없다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  코드 변경 0. 본 기록과 `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`만 갱신. 커밋 없음
  (`LOOP_ALLOW_COMMITS=0`). uncommitted 파일 해시:
  `docs/STATUS.md` `c8308f05e414fbf9201667d5984009900c0ca19fdf8d274dd5cafa2ef7ab2462`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` `7b7836f8cebccf17c52160ba0428474ad6d63f217e5e848cc7ebbbcd28e83ba4`,
  `loop/ESCALATE_SOL` `ffdb912fe4ae174c8777817ffccc1c7b6b98418af46b5fb6d14c0143f27e8e30`
  (본 기록 자신의 해시는 이 줄 추가 전 기준
  `6af4d8b9c66cfa2ae377aee52629aea4580ffdacf354e8026089f5a5a8f4c8b7`).
  검수 대상 SHA는 lap174 기록과 2/2 MATCH:
  `tools/runtime_env.py` `8893761db973cbb0dab5fdee0a1a26cc3bf7c9f5db1324c4ec9641f1d41bdc9c`,
  `tests/test_runtime_env.py` `81c34cc6b83645c0cc7371599f37079750678d11789a86754980bf4077ea3567`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  `ORIGINAL_SHA256` 상수는 `tools/runtime_env.py:159`에서
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 그대로다.
  원본 디렉토리 `../Syw2plus/`는 이번 세션 작업 범위 밖이라 현물 재해시는 **SKIP(권한/범위)**.
  대신 마지막 run copy provenance의 `original_exe_sha256`이 같은 값임을 재확인했다.
  게임 실행 0회. 활성 플레이어·지도·군대 N/A. 회귀는 synthetic in-memory fixture다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum tools/runtime_env.py tests/test_runtime_env.py` → 위 2/2 MATCH.
  `sha256sum local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/{evidence,verdict}.json`
  → `309028386476de06ced251686444e04b7c8e7d9c282f7f52e7ed1dbcf7fc7e59` /
  `319474f8fbe1f5e6d52443a71c75894b581e8ed83299bba60eeee30701138d55` — lap171 기록과 일치.
  P5 증거는 이후 재생성되지 않았다.
  **`make check` / `pytest` / `bash checks/safety.sh check` 는 실행하지 못했다.** 이 비대화형
  세션에서 해당 Bash 호출이 승인 대기로 차단됐다(lap171과 같은 제약). 새 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **A-6 PASS(정적).** `_g1_input_verdict`(`:1967`)의 술어는
    `not enabled or (len==5 and set==태그집합 and all result=="PASS")`이며 `and`가 `or`보다
    강하게 묶여 의도대로 동작한다. 중복 태그는 집합 비교가 걸러낸다.
    `_g1_presentation_verdict`(`:2020`)의 overall이 `required_inputs`를 AND로 포함하고,
    호출부 `:3282`가 `inputs`와 `g1_input_sequence`를 그대로 전달한다. baseline은 `:2888`/`:2895`로
    **같은 함수**를 쓴다. 입력 관측/production BLOCKED/teardown은 `:2024~2033`에 별도 필드다.
    off 모드는 `enabled=False` 단락으로 판정에 개입하지 않는다.
  - **A-7 PASS(공허하지 않음).**
    `test_g1_input_verdict_blocks_both_paths_when_production_is_blocked`(`tests:1224`)가
    baseline `required_inputs is False` + 양쪽 `overall != "PASS"`를 고정하고,
    `test_g1_input_verdict_accepts_all_five_passed_inputs`(`tests:1251`)가 5개 전원 PASS에서
    `required_inputs is True`, `overall == "PASS"`가 되는 **대조 케이스**를 제공한다.
    술어가 항상 False인 공허한 테스트가 아니다.
  - **A-8 PASS.** `tests:1215~1221`이 `sent_clicks == [(410,270),(150,520)]`,
    `sent_drags == [(350,180,550,350)]`, `(670,490) not in sent_clicks`를 단언한다.
    `scale=(2.0,2.0)`, `content_crop=(37,41,1600,1200)` 조건에서 전송 좌표는
    `x11 = crop + 논리좌표`뿐이다 — `[447,311]`, `[387,221]`, drag_to `[587,391]`, `[187,561]`.
    ×2 선변환 없음(lap149 계약 유지).
  - **A-9 불충분 (Stage B 차단 유지).** lap174 기록의 근거는 production 한 건
    ("BLOCKED는 효과 wait를 건너뛴다")뿐이고 **실제로 대기하는 세 개 wait의 예산 판단이 없다.**
    `_wait_state`(`:2502`)는 `started + timeout` 공용 마감시한만 갖는다.
    P5 run evidence의 실측: 총 `elapsed_seconds=40.712`, dwell 30초 ⇒ **기동→PS3 ≈ 8.4초**,
    **close+finalization ≈ 2.3초**(builtin 대조군). lap166 P4의 후보 close 정체는 ≈ 50초다.
    ⇒ `--g1-input-sequence`(dwell 0) 후보 run은 PS3 이후 **약 81초**를 세 입력 wait와
    close/finalization 전체가 **공유**한다. 귀결 세 가지가 기록에 없다:
    (i) 한 단계라도 무반응이면 그 한 단계가 ~81초를 전부 태우고 예외를 던지는데,
        `_wait_state`는 `record()`/`flush()` **이전에** 던지므로 **그 단계와 이후 단계의 증거가
        전혀 남지 않는다.** 1회·재시도 금지인 Stage B 카드가 거의 무정보로 끝날 수 있다.
    (ii) 입력이 ~30초를 넘기면 후보 close 정체 관측 구간이 잘린다.
    (iii) `_wait_state`의 예외 메시지는 "효과 없음"과 "예산 소진"이 **동일**하다. 현재
        `elapsed_seconds`는 run 전체분만 남으므로 FAIL과 UNKNOWN을 메시지로 분리할 수 없다.
  - **필수 게이트 독립 재실행 SKIP(권한).** lap174의 `make check` 198 passed / `SAFETY_PASS`를
    이번 세션이 재현하지 못했다. ⑥에 따라 이전 세션의 exit0/과거 수치를 승인으로 쓰지 않는다.
  - **off 모드 회귀 결손(비블로킹).** `input_sequence=False` / `enabled=False` 회귀가 0건이다
    (`grep` 확인). 코드는 정적으로 옳고 실패 방향도 안전(거짓 BLOCKED)이지만, lap173이 반려한
    "코드로만 성립하는 불변식"과 같은 부류다.
  - 부수 확인: 후보 verdict의 `checks`가 `required_inputs` 하나로 좁아졌으나 이를 읽는 소비자는
    `tests:1245`뿐이다(`tools/`·`checks/` 0건). 하위 호환 파손 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  **Stage A 승인 보류(조건부).** A-6·A-7·A-8의 코드와 회귀 내용은 독립 검수로 승인한다.
  그러나 (1) 필수 게이트를 이 세션이 재실행하지 못했고 (2) A-9 기록이 불충분하므로
  Stage A를 "승인"으로 승격하지 않고 **Stage B·P6·게임 실행은 계속 닫아 둔다.**
  남은 위험: G1 실제 원본/후보 입력 parity 미측정, Tier-2 동일 장면 조건 미증명,
  WM_CLOSE 종료 결함, production mapping 미승인, G2~G4 제품 증거 없음.
  사용자 마일스톤 승인 없음.
- 다음 한 가지: work tier가 (a) A-9 기록을 세 wait 기준으로 보강하고 — 각 단계 진입 시각과
  잔여 예산을 남겨 FAIL과 UNKNOWN(예산 소진)을 기계적으로 분리하는 방법을 명시 — (b) off 모드
  비개입 회귀 1건을 추가한다. 그 뒤 게이트를 실제로 실행할 수 있는 세션이
  `make check`·`pytest`·`checks/safety.sh check`를 재현하면 Stage A를 승인하고 Stage B를 연다.

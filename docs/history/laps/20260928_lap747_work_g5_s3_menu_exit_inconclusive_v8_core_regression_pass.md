# 2026-09-28 | lap 747 | 목표 G5 (17:45 지시 ① S3 완료 시도, ② v8 핵심 회귀)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행). lap746의
  17:45 운영자 판정("기준 후보 v8. middle 재검수 전에 work 1 lap: ① S3 완료, ② v8 핵심 회귀 1회,
  크래시 0")을 그대로 수행.
- 가설 / 사용자 관찰: lap746이 남긴 blocker — 일시정지 메뉴 7번째 항목(추정 (400,342)) 클릭 후 확인
  대화상자 추정 좌표(400,300)가 무반응이라 `S3_INCONCLUSIVE_UNEXPECTED_SCREEN`으로 끝났다. 이번 lap은
  캡처를 먼저 픽셀 분석해 정확한 버튼 좌표를 구한 뒤 S3(50선택 유지한 채 메인메뉴→새게임 이월 확인)를
  완주하고, 이어서 v8 핵심 회귀(드래그4종·이동·정지/홀드/순찰·그룹roundtrip 등)를 실행한다. **세션
  시작 시 `docs/STATUS.md`에 이미 "2026-09-28 18:05 운영자 관찰(lap747 v8 coverage raw)" —
  `hold_button`(툴바 홀드 버튼) pending이 0/50, v4~v6에서는 50/50이었다는 미해소 관찰이 남아 있었다**
  (이 lap 시작 전 다른 세션/실행이 이미 한 차례 coverage probe를 돌려 남긴 것으로 보임) — 이번 lap의
  coverage probe 실행이 그 값을 그대로 재현해 추가 조사 대상에 편입했다(아래).
- 예상 PASS / FAIL 조건: S3는 새 게임 시작 후 `count==0 and nonzero_count==0`이면 PASS, 아니면 FAIL.
  회귀는 v7→v8이 `LOAD_WRAPPER` 캐이브 안 1바이트(`0x14`→`0x32`)뿐이라는 lap746의 byte-diff pytest
  고정을 실측이 뒤집지 않으면(드래그/이동/정지/홀드/순찰/그룹저장로드 전부 v5~v7과 동일 패턴) PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`):
  - `tools/g5_candidate_drag_probe.py`: `run_probe`의 `source_exe = source / runtime_env.ORIGINAL_EXE`
    고정-파일명 조회가 `[ESL]Syw2plus/`(실제 파일명 `[HQ]Syw2plus 2002.exe`)에서 깨지는 걸 발견 —
    `runtime_env.validate_original_source(source)`(SHA로 아무 `*.exe`나 찾는 이미 존재하던 유연한
    로직)를 재사용하도록 8줄 수정. **레거시 잠재 버그 수정**(이번 lap 작업 자체를 막고 있었음).
  - `tools/g5_stale_tail_probe.py`: 동일한 고정-파일명 버그가 이 파일의 `run()`에도 복제돼 있어 같은
    패턴으로 수정. `S3_CONFIRM_OK_POINT = (419, 329)` 상수 추가(스크린샷 픽셀 분석으로 확정한 "확인"
    버튼 중심), 기존 추측 `click(400, 300)`을 이 상수로 교체. 확인 클릭 후 `time.sleep(0.8)` 고정
    대기 + 단발 읽기를, 최대 8초·0.25초 간격으로 `ps`가 9 또는 3에 도달할 때까지 폴링하고 매 샘플을
    `ps_trace_after_confirm`에 기록하도록 교체(전환이 0.8초보다 느릴 가능성 대비). 일시정지 메뉴를
    row-7 클릭 **전에** 원본 그대로 캡처하는 `s3-pause-menu-raw.png` 단계 추가(항목 라벨 실측용).
  - 신규 파일 0개, 제품 EXE/원본 0 변경. 세션 임시 monkeypatch 드라이버(저장소에 없음, lap682 이후
    선례와 동일 패턴): `/tmp/lap747_v8_coverage_driver.py`, `/tmp/lap747_v8_roundtrip_driver.py`
    (둘 다 `probe.g5 = v8; probe.TARGET_SHA = "ef46d1ac…"`만 교체).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus
  2002.exe`와 `syw2plus_original.exe` 둘 다 이번 lap 전/후 재확인, 8회 실행 전부 불변). 후보 v8
  `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`(lap746 고정값과 일치). 솔로 로비,
  worker(slot 1198) 앵커 7×8 dense fixture(55기 SEED_TYPE=2), 기존 G5 probe들과 동일 protocol.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 11회 synchronous 격리 실행(각 `kill -0` 폴링, 세션 유지, `game`
  사본은 실행 직후 삭제 — output/manifest/prefix/로그만 보존):
  1~4. `tools/g5_stale_tail_probe.py --variant candidate --candidate-version v8 --attempt-menu-exit`
     4회 반복(좌표/폴링 수정을 거치며) —
     `.../temp/Syw2plus_patch/20260928_lap747_g5_s3/{v8_candidate,}`,
     `.../20260928_lap747_g5_s3_v2/`, `_v3/`(우측 "취소" 버튼 대조군), `_v4/`(원시 일시정지 메뉴
     캡처 추가). 로그 `/tmp/lap747_s3_v{1,2,3,4}.log`.
  5,8,9. `/tmp/lap747_v8_coverage_driver.py --variant candidate` 3회(홀드 버튼 표본 편차 확인차
     재실행 2회 추가) →
     `.../20260928_lap747_v8_coverage/{candidate,candidate2,candidate3}/probe-result.json`. 로그
     `/tmp/lap747_v8_coverage_candidate{,2,3}.log`.
  6. `/tmp/lap747_v8_roundtrip_driver.py --variant candidate --ui-roundtrip` →
     `.../20260928_lap747_v8_roundtrip/candidate/probe-result.json`. 로그
     `/tmp/lap747_v8_roundtrip_candidate.log`.
  7. `tools/g5_stale_tail_probe.py --variant original --attempt-menu-exit`(대조군, 무패치 20용량) →
     `.../20260928_lap747_g5_s3_original/probe-result.json`. 로그 `/tmp/lap747_s3_original.log`.
  10,11. `PYTHONPATH=. python3 tools/g5_command_coverage_probe.py --variant original`(홀드 버튼
     원본 대조, 18:35 지시로 candidate와 맞춰 총 3회) →
     `.../20260928_lap747_v8_coverage/{original,original2,original3}/probe-result.json`. 로그
     `/tmp/lap747_v8_coverage_original{,2,3}.log`.
  이후 `make check`(`/tmp/lap747_make_check.log`), `checks/safety.sh check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **S3: 여전히 `INCONCLUSIVE`, 단 새 구체 증거 확보.** `s3-pause-menu-raw.png`로 일시정지 메뉴
    8행 전부 판독(계속하기/게임목적(회색)/환경설정/저장하기/불러오기/다시하기/**초기메뉴**/종료하기)
    — row7=`PAUSE_MAIN_MENU_POINT`(400,342)가 라벨상 정확히 "초기메뉴"임을 확인, 행 간격 추정이
    맞았다. 그 클릭이 여는 확인 대화상자("초기 메뉴로 돌아가시겠습니까?")의 두 버튼을 스크린샷
    픽셀(주황 테두리 상자) 분석으로 정밀 측정: **확인 버튼 중심 (419,329)**(테두리 상자
    x=[389,449] y=[306,352]), **취소 버튼 중심 (484,329)**(x=[450,519] 동일 y) — 육안 크롭으로 라벨
    "확인"/"취소" 재확인. **결과가 예상과 다름:** 확인(419,329) 클릭 → `ps`가 즉시(폴링 첫 샘플에서)
    23→3로 전환, 화면은 클릭 전과 동일한 전장(HQ·50기 진형)이 그대로 보이고 화면 상단에
    "[ESL]신규유저지원을 해지 나갔습니다" 메시지만 추가됨 — **메인 메뉴(ps=9)에 도달하지 못하고
    같은 게임으로 즉시 복귀**(9회 반복 폴링 8초 동안도 ps=9 미관측, `ps_trace_after_confirm`으로
    고정). 취소(484,329) 클릭 → `ps`가 8초·33샘플 내내 23으로 고정(대화상자 그대로, tick 불변) —
    두 버튼 모두 "메인 메뉴로 진행"에 도달하지 않았다. 좌표는 이제 정밀하게 확정됐고 재현성도
    있으므로(v2/v3/v4 세 번 각각 일관된 결과), 남은 원인은 UI 자동화 좌표 문제가 아니라 **이
    확인 대화상자의 "확인" 버튼이 실제로 메인 메뉴 전환을 트리거하지 않는(또는 확률적/조건부로만
    트리거하는) 이유**로 좁혀졌다 — 후보로 (a) `SYW2_SUPPLY_PROBE=1` 브리지/스톡 환경이 멀티플레이
    세션-종료 경로에 의존하는 "초기메뉴" 로직 일부를 방해, (b) ESL 배포판 특유의 신규유저지원
    메시지 로직이 이 대화상자를 가로채 취소로 단락, (c) 실제로 원본 동작 자체가 이렇다(제품 결함
    아님, 단순히 "돌아가기"가 예상보다 여러 단계를 요구)는 가설이 있었다. **원본(무패치 20용량)
    대조군으로 같은 시퀀스를 실행해 확정: 원본도 정확히 동일하게 재현됨**(`ps` 23→3 즉시 전환, 동일한
    "[ESL]신규유저지원을 해지 나갔습니다" 메시지, 동일한 화면). 즉 **(c) 확정, (a)/(b) 기각** — 이
    현상은 v8/candidate 패치와 무관한 원본/probe-환경 고유 동작이다. G5 패치가 S3를 막고 있는 게
    아니라는 뜻이므로 v8의 "F(저장/로드)" 판정에는 영향이 없다. **18:35 운영자 후속 지시로 이 결론을
    "환경 제약으로 종결"이 아니라 대체 경로로 더 조사하라는 방향이 확정됐다** — ① "초기메뉴" 대신
    일시정지 메뉴의 "다시하기"(재시작)·"불러오기"(다른 세이브 로드)로 50선택 이월을 원본/v8
    paired로 확인, ② fixture(SYW2_SUPPLY_PROBE 브리지·55기 dense seed) 없이 정상 로비에서 시작한
    순정 게임으로 "초기메뉴"를 재시도(브리지/fixture 자체가 이 전환을 막는지 분리). **이번 lap에서는
    시간 예산상 착수하지 못하고 다음 work로 명시 이관한다** — 추측 클릭을 더 반복하는 대신 위 두
    대체 경로를 구현해서 시도해야 한다.
  - **v8 핵심 회귀(②): 대체로 PASS, 크래시 0, 단 홀드 "버튼" 클릭 하나만 표본 편차 큼(아래).**
    - coverage probe(드래그 plain/ALT/Ctrl/Shift 4종 각 `fulldrag`/`fulldrag_again` 50/50·unique50,
      더블클릭 같은종류선택 50/50, Shift 토글 `before_remove`=3→`after_remove`=2(정확히 1개 제거),
      `shift_click_unit`=2→`shift_click_second_unit`=3(매번 +1, v5 수정 유지), `fifty_first_
      rejection.matches_capacity`=true(51번째 정확히 거부), 이동(우클릭)·정지(버튼+`S`)·순찰
      (버튼+`P`) 전부 `pending_changed_to` 50/50 도달) — lap734 v6 baseline과 패턴 완전 일치, 신규
      FAIL 없음.
    - **홀드 "버튼"(`hold_button`, (740,538) 클릭) 표본 편차 — 18:35 운영자 후속 지시로 원본도
      candidate와 동일하게 3회 반복 완료.** candidate(v8) 3회: `pending_changed_to`
      0/50 → 50/50 → 3/50(완전히 불안정). **원본(20용량) 3회: 20/20 → 20/20 → 20/20(완전히
      안정)**. 같은 3회씩 대조해도 원본은 요동 없이 항상 만점인데 candidate만 요동친다 — "표본 수가
      적어서"로는 설명되지 않는다. 홀드 "단축키"(`hold_hotkey_h`, `H`)는 candidate 3회 전부 정확히
      50/50으로 완전 안정이라, HOLD 명령 자체의 게임 로직은 정상이고 **"툴바 버튼 클릭" 입력 경로와
      50기 규모 선택의 상호작용에서만 편차가 난다.** `tools/g5_command_coverage_probe.py`의
      `stop_button`(469행)은 우클릭 이동으로 목적지를 먼저 만드는 `pre=` 단계가 있고, `hold_button`
      (472행)은 `pre=` 없이 곧장 클릭한다는 코드상 차이를 확인했으나 관측 윈도우(`window=3.0`)
      자체는 stop/hold/patrol 동일값이라 이 차이만으로 설명되지 않는다. 근본 원인(50기 규모에서
      HOLD 명령의 청크 분할 발행 속도가 다른 명령보다 느려 고정 관측 윈도우를 벗어나는지, 또는
      버튼 클릭 자체의 hit-test/디바운스가 원본과 다른지)은 이번 lap에서 gdb 트레이스까지는
      진행하지 못했다 — **PASS로 단정하지 않고 다음 조사로 명시 이관.**
    - UI roundtrip(그룹 Ctrl+숫자 지정→호출→저장→로드→재호출): `status=PASS_UI_ROUNDTRIP`,
      `movement_command_nonzero`=50, `checks` 7/7 전부 true(`selected_50`,
      `group_stored_stock20_plus_overflow49`, `deselected`, `recalled_50`, `save_created`,
      `group_retained_after_load`, `recalled_50_after_load`) — lap724/734와 동일 패턴.
    - 공격/R3/사망후호출은 이번 lap에서 재실행하지 않았다: lap746의 `test_build_is_v7_plus_exactly_
      one_changed_byte`가 v7→v8 차이를 정확히 1바이트(LOAD_WRAPPER 캐이브 안, 공격/R3/그룹지정/
      죽음훅 경로 바이트 무변경)로 고정하고 있고, 그 경로들은 v7에서 이미 PASS(lap723 R3, lap732/733
      death-recall H4, lap734 attack)이므로 byte-identical 코드 재실행은 낮은 한계효용으로 판단했다
      — 단, 이는 **정적 스코프 논거**이며 lap733→734가 지적한 "byte-diff 스코프 인자에만 의존" 위험과
      같은 종류의 절충이라는 점을 명시한다. middle이 원하면 다음 lap에서 monkeypatch driver로
      attack/R3/death-recall probe도 v8로 직접 재실행할 수 있다(패턴은 이번 lap의 coverage/roundtrip
      driver와 동일).
  - **`make check` 1115 passed, 5 skipped(1035.53s)**, ruff/compileall/mypy 전부 PASS,
    `checks/context_limits.py` `CONTEXT_PASS`, `checks/safety.sh check` `SAFETY_PASS`. 게임을 실제로
    띄운 11회(source-resolution 버그로 launch 전에 실패한 2회는 제외) 전부 `source_unchanged=true`,
    `cleanup.prefix_processes_after=[]`, 크래시 0(`process_alive` 유지 또는 정상 종료). 디스크: 게임
    사본(각 ~1.4GB) 11개 실행 직후 삭제, 종료 시 114G 여유.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: v8 핵심 회귀(드래그/이동/정지/순찰/더블클릭/
  Shift/51번째거부/그룹roundtrip)는 실측으로 재확인됐다. **홀드 "버튼" 클릭만은 원본3회(20/20 매번)
  대 후보3회(0/50→50/50→3/50)로 뚜렷하게 갈려 "PASS"로 단정하지 않는다** — 표본 부족 문제가
  아니라 candidate 쪽에서만 나는 재현 가능한 불안정성이다. 홀드 "단축키"(`H`)는 candidate 3회 전부
  50/50이라 명령 로직 자체는 살아있고, **"툴바 버튼 클릭" 입력 경로 + 50기 규모의 조합에서만** 편차가
  난다 — 크래시나 데이터 손상 없이 매번 다른 완료율이 나온다는 점에서 청크 분할 발행 타이밍 쪽
  가설이 유력하지만 이번 lap은 gdb 트레이스까지 가지 못해 미확정이다. **S3는 원본 대조군까지 완료해
  "메인메뉴 이월"이 이 probe 하네스에서는 원본도 동일하게 막힌다는 사실 자체는 확정했으나, 18:35
  운영자 지시로 이걸 "환경 제약, 검증 불가"로 종결하지 않고 대체 경로(다시하기/불러오기 paired,
  fixture 없는 순정 로비 재시도)로 더 조사하기로 방향이 잡혔다 — 이번 lap 예산 안에서는 착수하지
  못했다.** 제품 코드 변경은 이번 lap 0(도구 코드만 변경). `LOOP_ALLOW_COMMITS=0`이라 전부
  uncommitted. 사용자 milestone 여전히 없음.
- 다음 한 가지(18:35 운영자 지시 그대로): ① S3 대체 경로 — 일시정지 메뉴 "다시하기"(재시작)와
  "불러오기"(다른 세이브 로드)로 50선택이 새 판/다른 판에 이월되지 않는지 원본/v8 paired로 측정,
  가능하면 fixture 없이 정상 로비에서 시작한 판으로 "초기메뉴"도 재시도(브리지/fixture 자체가
  원인인지 분리). ② 홀드 버튼 편차의 근본 원인 추적(관측 윈도우 확장 재측정 또는 gdb 트레이스로
  회귀 여부 확정, 회귀면 즉시 수정). 둘 다 해소한 뒤 middle이 (F)를 v8 기준으로 최종 재검수한다.

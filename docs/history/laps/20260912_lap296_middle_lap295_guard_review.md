# 2026-09-12 | lap 296 | G1/S1 lap295 bounded repair 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / 중간 tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. `loop/.lap_counter`=296을 읽기만 했다
  (러너 배너는 `lap=295`로 한 칸 뒤쳐져 있었고, PROMPT.md ②에 따라 파일 값을 썼다).
- 가설 / 사용자 관찰: lap295가 §4.6.4대로 line 156·167만 가드했다면 (a) 정상 report가 바이트
  동일하고 (b) 세 정의 삭제 mutant가 명명 failure를 내며 (c) 그 두 자리 외에는 1바이트도 바뀌지
  않았을 것이다. lap295의 기록을 근거로 쓰지 않고 자체 mutant로 재측정한다.
- 예상 PASS / FAIL 조건: PASS = §4.6.4 세 조건 전부 + lap292 review probe의 top-level failure가
  `target_probe sha mismatch` 하나 + 지시된 두 가드만 되돌린 파일의 SHA가 수리 전 `edefa0e4…`와
  일치. FAIL = 값/스키마/PASS 규칙 변경 흔적, traceback, 0바이트 report, 반증력 상실.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현·원본·fixture 쓰기 0.
  신규 `docs/history/laps/probes/20260912_lap296_middle_lap295_guard_review_probe.py`
  (`ba1f23b8769f0daf22e027b42310b6abbe6e24b2bad83a20ac746e7015babea2`), 신규
  `logs/lap296/middle_lap295_guard_review.json`
  (`a690843f9c4222a8dadd1af18f6b7b89a9eae70728f40ab0249948bd7e0b584d`),
  `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.7 추가
  (`1abd3de3…df4f7507` → `b7e40231fe593cca669e374e6c76f328f2ad9557ac015cb439ef3ae5ec35047e`),
  본 기록, `docs/STATUS.md`. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  검수 대상 `…lap280_middle_s1_crossverify_probe.py`는 `88d86281…2d9a18d` 그대로 두었고,
  lap292(`2aaac7a0…33491335`)·lap294(`8fe0d257…671ec469`) review probe의 `EXPECTED_SHA`는
  편집하지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 후보 EXE 없음.
  Linux `.venv` Python 3.13.5 + `/usr/bin/objdump` 정적 probe, mutant는 tempfile 사본 트리에
  EXE를 symlink. 게임 fixture/활성 플레이어/지도/군대 없음. Wine/Xvfb/Stage B/runtime/PNG 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `.venv/bin/python …20260912_lap280_middle_s1_crossverify_probe.py` → exit0, 1,139 B,
     stderr 0 B, stdout SHA `3d4fe307…6a6d6a9126`,
     `cmp` 결과 `logs/lap280/s1_crossverify_probe.json`과 **바이트 동일**.
  2. `.venv/bin/python …20260912_lap296_middle_lap295_guard_review_probe.py` → **exit0,
     `failures` 0**. 보고서 `logs/lap296/middle_lap295_guard_review.json`.
  3. `.venv/bin/python …20260912_lap292_middle_lap280_repair_review_probe.py` → exit1,
     top-level failure는 `target_probe sha mismatch: 88d86281… != 100f991b…` **하나뿐**;
     정상 run 바이트 동일, 동행 4종 일치, mutant 5종 exit0/1·traceback 0.
  4. `.venv/bin/python …20260912_lap294_middle_missing_definition_scope_probe.py` → exit1.
     failure 5건은 전부 stale 기대값(target SHA, 사라진 refs 앵커, `expected a 0-byte crash`
     3건)이며 `as_is` 세 mutant는 1,083/1,083/1,073 B 명명 failure·`crash=null`이다.
  5. 범위 증명: 현재 파일에서 §4.6.4의 두 가드만 되돌리면(80 B) SHA가
     `edefa0e4b82d39034ddd14055e09a651998d2a8c93e5d27ab0f168bc7b47f61d`로 수리 전 상태와 일치.
  6. `make check` → 292 passed (46.68s), ruff/compileall/mypy/`CONTEXT_PASS`.
     `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **lap295 수리 ACCEPT (PASS)**. §4.6.4 세 조건
  CONFIRMED, 범위 CONFIRMED(80 B 외 변경 0), 반증력 유지 CONFIRMED(값 드리프트 3-failure,
  리터럴 회귀 1-failure). **새 사실:** W2 상수 승격을 지금 넣으면 probe line 129-130의 무가드
  `re.search(...).group(1)` 때문에 `type`/`owner` 둘 다 `AttributeError`·**0바이트**로 죽는다
  (`blind_spot_verdict=unguarded`). lap290 결함 계열은 아직 닫히지 않았다.
  lap294 probe의 `scope_verdict` 뒤집힘은 앵커 소멸 artifact이며 §4.6.2를 뒤집지 않는다(§4.7.5).
  제품 G1~G4 실제 실행 증거는 **SKIP**(이번 바퀴 게임 실행 0).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본 EXE·`tools/runtime_env.py`
  (`dd2ad043…8500190`)·`patches/population/runtime_driver.py`(`ae4ff939…4e4291b5`)·보존 report
  전부 불변. S1 카드 종결 **REJECT 유지**, Stage B 0, runtime 예산 0, 사용자 마일스톤 승인 없음.
  남은 위험: §4.7.4 무가드 scrape 2줄, §4.5.4 reader 이름 사각, 그리고 lap290~296 일곱 바퀴가
  전부 하네스 건전성이라 제품 증거는 0으로 정지해 있다는 것(아래 다음 한 가지 참조).
- 다음 한 가지: work tier가 §4.7.6대로 probe line 129-130의 `type`/`owner` scrape만 가드한다
  (성공 조건 4가지는 §4.7.6 3항). 그 전에는 W2 (a)(b)(c) 승격, `EXPECTED_SHA` 수정,
  Stage B/Wine/runtime 실행, G1~G4 승격을 하지 않는다.

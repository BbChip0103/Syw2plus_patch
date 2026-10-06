# 2026-09-28 | lap 739 | 목표 G5 ((F) 저장/로드 — 50기 선택 상태 명시 재확인)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행).
- 가설 / 사용자 관찰: lap738 "다음 work" — (F) 50기 선택 상태·부대 상태 저장 후 로드, 원본 세이브
  호환. Ctrl+숫자(부대) 자체는 lap724/734가 이미 `PASS_UI_ROUNDTRIP`으로 커버했으나 "50 선택 유지"
  자체(부대 지정과 무관한 raw 드래그 선택)와 원본 세이브 호환은 명시 재확인이 안 됐다는 08:15계열
  지시 흐름의 연장.
- 예상 PASS / FAIL 조건: 세이브 시점의 raw 선택(드래그로 고른 50기, 부대 지정과 무관)이 로드 후
  그대로 복원되면 PASS. 원본이 이미 하는 동작을 후보가 못 하면 FAIL. 원본 EXE가 후보 v6가 만든
  세이브 파일을 크래시 없이 열면 "원본 세이브 호환" PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 EXE/원본 무변경. 신규 저장소
  파일 없음 — `/tmp/lap739_v6_roundtrip_driver.py`(기존 `tools/g5_candidate_drag_probe.py`를
  lap682/717/723/724/734 선례와 동일하게 모듈 전역 `g5`/`TARGET_SHA`만 v6로 교체하는 monkeypatch
  드라이버, 저장소에 없음)와 `/tmp/lap739_crossload_driver.py`(신규 진단 전용, 원본 실행 파일이
  후보가 만든 세이브를 읽는지만 확인하는 read-only 크로스로드 하네스, 저장소에 없음). 전부
  uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`Syw2plus_re/Syw2plus`
  경로, 3회 실행 전후 재확인 전부 불변). 후보 v6
  `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f`(원본에서
  `g5_selection_cap50_v6.build_candidate`로 재빌드, `private_exe_sha256` 일치 확인). 솔로 로비,
  worker(slot 1198) 앵커 7×8 dense fixture(55기 SEED_TYPE=2, +worker=56), 기존 G5 roundtrip probe
  fixture와 동일.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 3회 synchronous 실행(백그라운드 PID `kill -0` 폴링으로
  완주까지 대기, 세션 종료 없음):
  1. `python3 /tmp/lap739_v6_roundtrip_driver.py candidate ...` →
     `local/runtime/lap739_v6_saveload_candidate/`,
     `../../temp/Syw2plus_patch/20260928_lap739_g5_f_saveload/candidate/probe-result.json`
     (`ui_roundtrip.save.sha256`=`cdbe1746cafa9396…`, size 2499822).
  2. `python3 /tmp/lap739_v6_roundtrip_driver.py original ...` (동일 스크립트, `g5`/`TARGET_SHA`
     monkeypatch는 candidate 분기에서만 쓰이므로 원본 실행에는 영향 없음) →
     `local/runtime/lap739_v6_saveload_original/`,
     `.../20260928_lap739_g5_f_saveload/original/probe-result.json`
     (`ui_roundtrip.save.sha256`=`5951de50bbeb109c…`, size 2499822).
  3. `python3 /tmp/lap739_crossload_driver.py ../Syw2plus_re/Syw2plus <candidate save001.dat>
     local/runtime/lap739_v6_saveload_crossload ...` →
     `.../20260928_lap739_g5_f_saveload/crossload/probe-result.json`.
  이후 `make check`(`/tmp/lap739_make_check.log`), `checks/safety.sh check`
  (`/tmp/lap739_safety.log`). 각 `game`(~2.7GB) 사본은 실행 직후 삭제, output/manifest/log·save
  해시는 보존.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(F-1) 부대(그룹) 저장/로드: PASS(재확인).** 후보 `checks` 7/7 true(`selected_50`,
    `group_stored_stock20_plus_overflow49`, `deselected`, `recalled_50`, `save_created`,
    `group_retained_after_load`, `recalled_50_after_load`) — lap724/734와 동일 패턴. 원본은
    20-cap 기준 병렬 동작(`stored`/`recalled`/`loaded`/`recalled_after_load` 전부 20).
  - **(F-2) raw 드래그 선택(부대 미지정) 자체의 저장/로드: 신규 FAIL(후보 한정), 원인 확정.**
    두 실행 모두 동일 시퀀스로 저장 직전 raw 선택은 "1"(그룹1) 재호출 직후 값이었다 — 원본 20,
    후보 v6 50. 저장 → 재개 → **저장 이후 살아있는 세션에서 명시적으로 디셀렉트(raw=0으로 확인)**
    → 다시 일시정지 → 로드. 로드 직후(그룹 재호출 키를 누르기 **전**) raw 선택 값: **원본
    20**(저장 시점 값 그대로 복원 — 로드 직전 라이브 값 0이 아니라 저장 당시 값으로 되돌아갔으므로
    이는 세이브 파일 자체가 raw 선택을 인코딩·복원하는 원본의 실제 네이티브 기능임이 확증됨),
    **후보 v6는 0**(저장 시점 50이 전혀 복원되지 않음 — "부대 지정 없이 그냥 드래그로 고른 선택"은
    로드 후 사라진다). 그룹1 재호출("1")로는 두 경우 다 정상 복원되므로(원본 20, 후보 50) 기능적
    우회로는 살아 있으나, "50 선택 상태 자체의 저장/로드"라는 (F) 원문 요구는 후보에서 FAIL이다.
  - **근본 원인(정적 확인, 확정):** `patches/selection/g5_selection_cap50_v1.py`가 stock 선택
    카운트/엔트리 주소 `0x00899024`의 **알려진 모든 읽기/쓰기 참조 10곳 전부**(`0x412E68`,
    `0x412E6E`, `0x412ECC`, `0x412ED2`, `0x41D360`, `0x41F599`, `0x498FBA`, `0x499872`,
    `0x49ACD1` 등)를 새 `SELECTION_BASE`로 재배치한다 — 즉 v1(및 이를 그대로 계승한 v2~v6)은
    레거시 주소 `0x00899024`를 완전히 방치(dead)하고 다시는 쓰지 않는다. 원본의 세이브 직렬화가
    이 레거시 주소(또는 그 인접 블록)를 그대로 디스크에 옮기는 방식이라면, 후보 메모리에서 그
    주소는 항상 0(또는 초기화 안 된 값)이므로 세이브 파일에도 항상 0이 기록되고, 어느 엔진으로
    로드하든 raw 선택은 0으로 나온다 — 실제 관측(후보 자체 로드 0, 원본이 후보 세이브를 읽어도 0)과
    정확히 일치한다.
  - **(F-3) 원본 세이브 호환(크로스 로드): PASS(크래시 없음).** 완전 무패치 원본 실행 파일이 후보
    v6가 만든 `save001.dat`을 자신의 저장 디렉터리에 주입받아 그대로 로드 — `status=
    PASS_CROSSLOAD_NO_CRASH`, 정지·행 없이 `ps==3`·`tick>0`으로 정상 진행. 로드 후 그룹1 스냅샷은
    `group1_count=20, group1_first_id=132270` — 후보 자신의 `loaded.group`과 **완전히 일치**(레거시
    20슬롯 그룹 데이터가 바이트 단위로 원본과 호환됨을 교차 확인). raw 선택은 위 (F-2) 원인과
    일관되게 0. 이는 "원본 세이브 형식이 후보로 인해 깨지지 않았다"는 핵심 호환성 질문에는 명확한
    PASS이지만, "50 선택 자체의 왕복"이라는 별개 질문은 여전히 FAIL이다.
  - 크래시 0(3/3), `source_unchanged` 3/3, `cleanup.prefix_processes_after=[]`(candidate·original;
    crossload cleanup 필드는 `manifest` 변수 스코프 문제로 `null` 기록 — 실제 wineserver -k/-w는
    수행됐고 실행 자체는 정상 종료, 제품/원본 무변경 확인은 `source_unchanged=true`로 별도 확보).
    `make check` **1111 passed(858.42s)**, ruff/compileall/mypy/`checks/context_limits.py`
    (`CONTEXT_PASS`) 전부 PASS, `checks/safety.sh check` → `SAFETY_PASS`(신규 pytest 0개, 제품 코드
    무변경, 진단 드라이버는 `/tmp`에만 존재).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: (F-2)는 R3·(D) 사망-후-호출과 같은 계열의
  "20-cap 레거시 경로 vs 50-cap 확장 경로" 구조적 회귀다. 다만 R3/사망-후-호출과 달리 이번 것은
  **완전한 기능 손실이 아니라 우회로가 이미 존재**한다(그룹 지정 후 세이브하면 로드 후 재호출로
  100% 복원됨 — lap724/734/이번 lap이 반복 확인). 순수 "지정 없는 드래그 선택"만 세이브에 안 남는
  것은 원본에도 없던 50-cap 신규 영역(21~50번째)의 문제가 아니라 0~50 전체에 대해 새로 생긴
  결함이라는 점에서 R3보다 범위가 넓다(원본은 0~20 전체가 살아남는데 후보는 0~50 전체가 죽는다).
  마일스톤 경계(G5 (F) 완료 여부, `docs/feedback/APPROVALS.md`의 2026-09-28 01:31 체크리스트)에
  직접 닿으므로 이 lap은 v7을 임의로 만들지 않고 `loop/ESCALATE_SOL`에 lap739 섹션을 추가해
  middle/strategy 판정을 요청한다. 독립 검수·사용자 milestone 승인 없음(기존과 동일).
- 다음 한 가지: middle/strategy가 ① (F-2)를 v7로 지금 고칠지(레거시 주소
  `0x00899024`에 min(count,20) 그림자 값을 유지해 원본 세이브 직렬화 경로가 항상 유효한 값을 보게
  하는 최소 훅 — 정확한 세이브 직렬화 함수/범위는 아직 정적으로 특정되지 않음, 다음 조사 대상)
  또는 그룹-재호출 우회로 충분하다고 보고 (F)를 "부분 PASS(그룹 경로만)"로 문서화한 뒤 (G) 멀티로
  넘길지 판정한다. 판정 대기 중에는 G5 제품 EXE를 변경하지 않는다.

# 2026-09-28 | lap 740 | 목표 G5 ((F) 저장/로드 — raw 드래그 선택 v7 수정)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행).
- 가설 / 사용자 관찰: 2026-09-28 14:05 운영자 판정(lap739 F-2 FAIL, `loop/ESCALATE_SOL` lap739 해소) —
  세이브 직렬화가 레거시 선택 영역(`0x00899024`/`0x00899028`)을 그대로 파일에 옮기는데 v1~v6는 그
  주소를 완전히 방치(dead)해 항상 0이 기록된다. 가설: 저장 직전 레거시 영역에 현재 선택(≤20)을
  미러링하고 로드 직후 역으로 복원하면, 세이브 스트림의 바이트 배치를 전혀 바꾸지 않고도 raw
  선택이 원본과 동일하게 왕복한다.
- 예상 PASS / FAIL 조건: 후보(v7)로 50기 선택 → 저장 → 명시적 디셀렉트(0) → 로드 직후 raw 선택이
  0이 아니라 저장 시점 값(≤20 상한)으로 복원되면 PASS. 원본이 v7의 세이브를 크래시 없이 읽고,
  v7이 원본의 세이브를 크래시 없이 읽으면(양방향) 세이브 호환 PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 저장소 파일 3개, 전부 uncommitted
  (`LOOP_ALLOW_COMMITS=0`):
  - `patches/selection/g5_selection_cap50_v7.py` (v6 위에 저장/로드 shadow mirror 훅 2개 추가)
  - `patches/selection/test_g5_selection_cap50_v7.py` (정적 회귀 5종)
  - 진단 드라이버(저장소 밖, `/tmp`, lap682/717/723/724/734/739 monkeypatch 관례와 동일):
    `/tmp/lap740_v7_roundtrip_driver.py`, `/tmp/lap740_crossload_driver.py`
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`Syw2plus_re/Syw2plus` 경로,
  4회 실행 전후 재확인 전부 불변). 후보 v7
  `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`(v6
  `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f` 위에 정확히 2개 call-site(5바이트
  씩) + `.rsrc` 섹션 헤더(Misc_VirtualSize/Characteristics) + `.rsrc` 자신의 이미 0으로 채워진 raw
  padding(`0x108d000+0x2100..0x2200`, 128바이트 예약, 실제 사용 74+54바이트) 안에서만 차이 —
  `test_only_the_two_call_sites_and_rsrc_cave_differ_from_v6`로 고정). 솔로 로비, worker(slot 1198)
  앵커 7×8 dense fixture(55기 SEED_TYPE=2, +worker=56, 기존 G5 roundtrip probe fixture와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 4회 synchronous 격리 실행(`kill -0` 폴링으로 완주까지 대기,
  세션 종료 없음), 각 `game`(~2.2GB) 사본은 직후 삭제·output/manifest/log/save·캡처 SHA만 보존:
  1. `python3 /tmp/lap740_v7_roundtrip_driver.py --variant candidate --ui-roundtrip
     --source ../Syw2plus_re/Syw2plus --runtime-root local/runtime/lap740_v7_candidate
     --artifact-root .../20260928_lap740_g5_f_saveload/candidate` →
     `probe-result.json`(status `PASS_UI_ROUNDTRIP`), save
     `e925448c08c5c450e18fa17bfc3be35a626b10a4c73ff5cc9fa27d0a5478cf97`(2501702B).
  2. 같은 드라이버 `--variant original` → `probe-result.json`(status `PASS_ORIGINAL_CAP20`), save
     `59b12bce557490523aaa55229b0b4b979b6ca428da8b7aacfb54d62bba7ba325`(2501702B).
  3. `python3 /tmp/lap740_crossload_driver.py --exe-variant original --inject-save
     <candidate save>` → `probe-result.json`(status `PASS_CROSSLOAD_NO_CRASH`).
  4. `python3 /tmp/lap740_crossload_driver.py --exe-variant candidate --inject-save
     <original save>` → `probe-result.json`(status `PASS_CROSSLOAD_NO_CRASH`).
  캡처·JSON 전부 `../../temp/Syw2plus_patch/20260928_lap740_g5_f_saveload/`에 보존. 이후
  `make check`(`/tmp/lap740_make_check.log`), `checks/safety.sh check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(F-2) raw 드래그 선택 저장/로드: FAIL → PASS(20 상한, 원본과 동일 범위).** 후보 v7: 50기
    드래그 선택 → 저장(그 시점 raw=50) → 명시 디셀렉트(0) → 로드 → **로드 직후 raw 선택
    count=20**, slots가 저장 시점 앞 20개(`[1198,1195,1194,1193,1192,1191,1190,1189,1188,1187,
    1186,1185,1184,1183,1182,1181,1180,1179,1178,1177]`)와 **정확히 일치**. 같은 세션의 원본
    paired 실행도 동일 시나리오에서 **동일한 20개 slots**를 복원(`PASS_ORIGINAL_CAP20`) — v7이
    이제 원본과 바이트 단위로 같은 20-슬롯 결과를 낸다. v6 이전에는 이 값이 항상 0이었다(lap739
    FAIL_DEATH_RECALL과 무관한 별개 결함, lap739 참고).
  - **(F-1) 부대(그룹) 저장/로드: 재확인 PASS(회귀 없음).** `ui_roundtrip.checks` 7/7 전부 true
    (`selected_50`, `group_stored_stock20_plus_overflow49`, `deselected`, `recalled_50`,
    `save_created`, `group_retained_after_load`, `recalled_50_after_load`) — lap724/734/739와 동일
    패턴, v7의 두 훅은 그룹 메커니즘(`GROUP1_BASE_ADDRESS`/`unit+0x344`)을 전혀 건드리지 않으므로
    예상대로 무변화.
  - **세이브 호환(양방향): PASS.** ① 무패치 원본 EXE가 v7 세이브를 크래시 없이 로드
    (`ps=3,tick=311`)하고, 원본 **자신의 레거시 판독으로도** count=20·동일 20-슬롯을 그대로
    보여준다(레거시 영역이 진짜 유효한 선택 데이터를 담고 있음을 원본 스스로 확인 — v6의 "항상
    0"보다 원본과 더 가까운 상태). ② v7이 **원본이 만든 세이브**를 크래시 없이 로드(`ps=3,
    tick=303`)하고, `SELECTION_BASE`(라이브 선택)가 레거시에서 미러링되어 count=20·동일
    20-슬롯으로 정확히 복원됨 — 이것이 운영자가 요구한 "원본 세이브를 v7에서 로드(역방향 호환)"
    검증이다.
  - **정적 회귀 범위 증명:** `test_only_the_two_call_sites_and_rsrc_cave_differ_from_v6`가 v7과 v6의
    바이트 차이를 두 call-site(5바이트×2) + `.rsrc` 섹션 헤더(40바이트) + `.rsrc` 자신의 0-padding
    cave(128바이트)로만 한정함을 빌드 시점에 강제 — 드래그/이동/공격/정지·홀드·순찰/그룹지정·호출/
    사망-후-호출 정리(H4) 등 기존 PASS 경로는 코드 수준에서 원천적으로 손댈 수 없다. `make check`
    (아래)의 `1116 passed`가 기존 pytest 스위트 전체(드래그/공격/그룹/R3 등 정적+런타임 테스트 포함)
    회귀 없음을 뒷받침한다.
  - `make check` **1116 passed(808.52s)**, `.venv/bin/python -m ruff check` 전부 PASS,
    `compileall` PASS, `mypy`(지정 파일 목록, v7은 목록 밖) PASS, `checks/context_limits.py`
    `CONTEXT_PASS`, `checks/safety.sh check` → `SAFETY_PASS`(신규 pytest 5개, 제품 EXE/원본 무변경,
    진단 드라이버는 `/tmp`에만 존재). 크래시 0(4/4 격리 실행), `source_unchanged` 4/4(두 소스 경로
    모두 매 실행 전후 재확인).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **명시적으로 남겨둔 한계(운영자 지시의 "불가하면
  최소 앞 20기 복원" 대안 채택):** entries 21..50은 이번 lap에서 저장/로드를 왕복하지 않는다(원본과
  동일한 상한). 21..50을 보존하려면 세이브 스트림 끝(모든 기존 블록·파일 finalize 직전)에 새 trailing
  block을 추가해야 하는데, 이는 파일 크기를 늘리므로(현재 v7처럼 "이미 복사되는 창을 채우기만" 하는
  무위험 패턴이 아니라 실제 새 바이트 추가) 이번 lap에서는 시도하지 않았다 — 다음 work 후보로 남긴다
  (세이브 스트림의 진짜 끝 지점은 `0x00440f34/0x00441305`의 `FUN_0040F4B0`/`FUN_0040F4F0`(per-unit
  레코드) 호출 직후, `0x00440f3b/0x0044130b`의 finalize 호출(`0x4da97c`) 직전으로 이미 특정됨).
  독립 검수(middle)는 여전히 2026-09-28 03:36 운영자 판정에 따라 A~H 체크리스트 전체 완료 후 한
  번에 진행하므로 이번 lap은 정보 제공용이며 middle 재검수 요청이 아니다. 사용자 milestone 승인
  없음(기존과 동일).
- 다음 한 가지: (F)는 20-상한 범위에서 PASS로 판단하고 완료 표시를 middle/운영자 판정에 맡긴다.
  다음 work 후보: ① (선택) 21..50 세이브 확장을 trailing block으로 시도, ② 남은 체크리스트
  (G) 멀티 2인 LAN 동기화(50기 명령, 패킷 최대3배) 또는 불가 사유, (H) 장시간(50기 반복 명령 수천
  tick 안정성)으로 진행. G1은 G5 (G)(H) 완료 후 재개(2026-09-28 01:31 지시 유지).

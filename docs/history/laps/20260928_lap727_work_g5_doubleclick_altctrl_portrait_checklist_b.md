# 2026-09-28 | lap 727 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: STATUS/APPROVALS 2026-09-28 03:36 운영자 판정의 (B) 잔여 3항목 — 더블클릭 같은
  종류 전체 선택, ALT·Ctrl 클릭 같은 종류 선택, 포트레이트 클릭 해제 — 이 이 게임에 실제로 존재하는지
  라이브로 먼저 확인한 뒤, 존재하면 원본20/후보(v5)50 paired로 측정한다는 가설(lap726 다음 한 가지 그대로).
- 예상 PASS / FAIL 조건: PASS = 더블클릭이 같은 화면상 같은 타입 유닛 전체를 선택하고 그 개수가 원본
  20/후보 50 상한과 정확히 일치. ALT/Ctrl 단일클릭이 plain 단일클릭(count=1)과 다르면(즉 같은 타입 선택
  기능이 있으면) 그 정확한 개수까지 측정. 포트레이트는 다중 선택 시 개별 유닛 아이콘 행이 존재하고
  클릭으로 그 유닛만 제거되면 PASS, 그런 UI 자체가 없으면 "미지원"으로 기록(FAIL 아님, 게임에 없는
  기능은 적용 대상이 아님).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `tools/g5_command_coverage_probe.py`: SHA256 `448ad8da14eaf29c3e2742e8713855e76b66602882c00ed0ee2a226b45e380e1`.
    ① `click()` 헬퍼에 `clicks`/`interval_ms` 인자 추가(기존 `--drag-to`/`mod` 분기 옆에 `--repeat`/
    `--interval-ms`를 `x11_mouse_click.py`(이미 CLI로 지원하던 옵션, 이번에 처음 배선)에 연결) —
    더블클릭을 위한 순수 배선 추가, 기존 단일클릭 호출은 `clicks=1` 기본값으로 동작 불변.
    ② 기존 ALT/Ctrl modifier 루프가 이미 채워둔 `alt_click_unit`/`ctrl_click_unit`(단일 유닛 클릭,
    modifier만 다름) 결과에서 `count>1` 여부로 `alt_click_same_type_select`/`ctrl_click_same_type_select`
    요약 필드를 계산(새 게임 실행 불필요 — 이번 lap의 새 raw run으로 재확인됨, 아래 참고).
    ③ 신규 더블클릭 블록: `click_dy`(기존 단일-유닛 클릭 오프셋)로 anchor1을 `clicks=2, interval_ms=150`
    으로 더블클릭 후 `record("doubleclick_unit")`, `doubleclick_same_type_select` 요약 필드 추가.
    이 파일을 참조하는 pytest 없음(lap724/726이 이미 확인한 사실, 재확인 `grep -rl
    g5_command_coverage_probe tests/` 결과 없음 — 아래 targeted pytest는 다른 G5 파일들 대상).
  - 신규 파일 없음. 임시 monkeypatch 드라이버 `/tmp/lap727_v5_coverage_driver.py`(lap726 드라이버를
    그대로 복사, `g5`/`TARGET_SHA`만 v5로 교체 — 로직 무수정, diff 0). SHA256
    `b7e6ba3bb4d4a1d4c135af1946e9720248876b0e1d3f8a3c2085319d8a62c9d8`. 사본을 artifact 디렉터리에 보존.
  - 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(양 실행 전후 `source_unchanged=true`).
  v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`(lap723~726과 동일, 독립
  재빌드로 재확인). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0 dense fixture worker(slot1198) 앵커
  7×8 그리드 55기 SEED_TYPE=2(+일꾼 1기, pool 56). 소스 `[ESL]Syw2plus`(SHA 위와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap727_v5_doubleclick_coverage/`
  {coverage-candidate, coverage-original}/.
  1. `PYTHONPATH=. .venv/bin/python /tmp/lap727_v5_coverage_driver.py candidate
     local/runtime/lap727_v5_cov_candidate .../coverage-candidate` → `COMPLETE None`. 결과 JSON SHA256
     `a386dc5e8b4301d566643d53854ed7fa8ab49c357c76227825b6c334e8da150a`.
  2. `... original local/runtime/lap727_v5_cov_original .../coverage-original` → `COMPLETE None`. 결과
     JSON SHA256 `3ae95f6df1167cda646486443a919cc406c9bb681d588102ad5c27e4969975c4`.
  3. `PYTHONPATH=. .venv/bin/python -m pytest -q patches/selection/ tests/test_g5_candidate_drag_probe.py
     tests/test_g5_command_packer_xrefs.py tests/test_g5_stock_selection_array_xrefs.py` → `44 passed`.
  4. `make check`(foreground nohup + poll, 로그 `logs/gates/20260928_lap727_make_check.log`),
     `bash checks/safety.sh check`.
  5. 각 run 뒤 `local/runtime/lap727_v5_cov_*/*/game`(약 800MB씩) 삭제, output/manifest/prefix/log는
     보존(디스크 위생). `ps aux`로 새 1600x1200 Xvfb/wine 고아 없음 확인(`cleanup.prefix_processes_after=[]`
     2/2와 일치).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **더블클릭 같은 종류 전체 선택 = 지원함, PASS(원본·v5 둘 다, raw).** anchor1을 두 번 빠르게
     좌클릭(`interval_ms=150`)하면 화면상 같은 타입(SEED_TYPE=2) 유닛 전체가 선택된다:
     원본 `doubleclick_unit={count:20, unique:20, types:{'2':20}}`(같은 fixture의 `plain_fulldrag`
     20/20과 정확히 일치), v5 후보 `doubleclick_unit={count:50, unique:50, types:{'2':50}}`(같은 fixture의
     `plain_fulldrag` 50/50과 정확히 일치). 즉 더블클릭 select-same-type도 박스드래그와 **같은 20→50
     상한 경로**를 타며 51번째(56 pool 중)는 선택되지 않는다 — G5 상한이 이 메커니즘에도 새지 않음.
     비교 기준 `plain_click_unit`(단일클릭)은 원본·v5 둘 다 `count=1`이라 더블클릭의 확장 선택이
     더블클릭 고유 동작임이 명확하다. 크래시 없음, `alive_after` true.
  2. **ALT/Ctrl 클릭 같은 종류 선택 = 미지원(원본·v5 둘 다 동일, raw).** `alt_click_unit`/`ctrl_click_unit`
     모두 원본·v5 둘 다 `count=1`(`plain_click_unit`과 동일) — 단일 유닛 클릭에 ALT/Ctrl을 누르고 있어도
     "같은 타입 전체 선택" 같은 별도 동작은 트리거되지 않는다(기존 modifier-드래그 add/replace 동작과는
     별개 질문이며, 이번 lap이 처음으로 명시적 요약 필드로 답을 남김). 후보가 원본과 똑같이 동작하므로
     회귀 아님 — 이 항목은 "게임에 그 기능이 없다"가 결론이며 v5가 고쳐야 할 대상이 아니다.
  3. **포트레이트 클릭 해제 = 이 게임 UI에 해당 기능 자체가 없음(미적용, 원본·v5 둘 다 확인).**
     `mod-plain_click_unit.png`(단일 선택)은 좌하단에 캐릭터 얼굴 초상화(이름 "조선 창병"+체력/공격력/
     방어력 텍스트)를 보여주지만, `mod-plain_fulldrag.png`(다중 선택, lap726 기존 캡처 재확인)와
     이번 lap의 `mod-doubleclick_unit.png`(다중 선택)는 **둘 다 같은 자리에 유닛 개별 아이콘이 아니라
     단일 원형 "타입/부대" 배지 아이콘**(원본·후보 공통, 이름표/스탯 텍스트 없음)만 보여준다 — 좌하단
     검은 다이아몬드 영역은 선택 인원과 무관하게 항상 비어 있다(플레이어 깃발용, 유닛 아이콘 아님).
     즉 이 게임은 다중 선택 시 유닛별 개별 초상화 행을 렌더링하지 않으므로 "포트레이트 클릭으로 특정
     유닛만 해제"는 원본에도 존재하지 않는 기능이다(FAIL이 아니라 대상 없음). 원본 800×600 렌더와
     v5 1600×1200 렌더 모두에서 동일 레이아웃(원형 배지 1개, 이름/스탯 없음)을 확인했다.
  4. 크래시 0(2/2), `source_unchanged=true`(2/2), `cleanup.prefix_processes_after=[]`(2/2, 고아 없음).
  5. `make check` **1106 passed(797.09s)**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS,
     `SAFETY_PASS`. targeted pytest `44 passed`(제품 코드 무변경이므로 회귀 스위트 수 lap726과 동일).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 더블클릭 select-same-type가 박스드래그와 동일한 20/50 상한 코드 경로를 타는지는 이번 lap에서
    **행동 관찰(count가 정확히 상한과 일치)로만 확인**했고 디스어셈블로 "같은 함수"임을 정적 확인하지는
    않았다(원인 추적이 아니라 상한 준수 여부가 이번 체크리스트 질문의 전부이므로 범위 밖으로 판단 —
    필요하면 (A) 정적 전수 표 갱신 시 참고).
  - ALT/Ctrl "같은 종류 선택"이 이 UI의 다른 입력 경로(예: 툴바 버튼, 더블클릭+수정키 조합)로는
    존재할 가능성은 배제하지 않았다 — 이번 lap은 단일클릭+modifier 경로만 확인했다(체크리스트 문구
    "ALT·Ctrl 클릭"과 일치하는 가장 직접적인 해석).
  - 독립 검수: 아직 없음(work tier 산출, 운영자 판단에 따라 middle은 체크리스트 전체가 채워진 뒤
    한 번에 진행하기로 함, 2026-09-28 03:36 판정 유지).
  - 사용자 승인: 없음(G5 확정은 체크리스트 A~H 완료 후).
- 다음 한 가지: (B)는 이번 lap으로 **완료**(A 완료(lap725), B 전 항목 — 드래그/Shift 추가·제거/ALT·Ctrl·
  더블클릭 선택/포트레이트 해제(미지원 확인)/51번째 거부/R3 사망 3위치 — 전부 PASS 또는 원본과 동일
  동작으로 판정됨). 다음은 **(C) 명령 전부**: 이동·미니맵 우클릭(원본에서 작동하는 환경 확인)·공격
  (지면/대상)·정지·홀드·순찰은 이미 커버됨(lap717/723/724/726) — 남은 것은 **일꾼 채집/건설/수리 등
  특수 명령, 특수능력/변신, 승선/하선 등 툴바 전체 버튼과 단축키**, 명령 직후 대기열·목적지 좌표 일치.
  이어서 (D) 부대(Ctrl+숫자 지정/호출/Shift+숫자 추가/부대원 사망 후 호출)~(H) 순서.

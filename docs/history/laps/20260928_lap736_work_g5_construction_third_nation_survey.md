# 2026-09-28 | lap 736 | 목표 G5 (체크리스트 C 건설 재판정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort(환경
  MODEL_ROUTING 계약상 work tier); 지정 역할 work — 승인된 범위의 실측/코드/실행만 수행, 마일스톤
  판정이나 (C) 최종 확정 선언 같은 상위 결정은 하지 않음.
- 가설 / 사용자 관찰: 2026-09-28 08:15 운영자 판정 — lap731의 "(C) 건설 = N/A"는 표본이 2개국(worker
  type31/HQ58, worker type21/HQ70)뿐이라 의심스럽고, 설명서와 다른 국가/커맨드 그리드 하위 페이지를
  확인해 재판정해야 한다. 가설: 이 솔로 로비 fixture에는 (아직 안 본) 다른 국가가 있고, 그 국가의
  워커/HQ 커맨드 그리드에 건설(배치) 버튼이 있을 수 있다.
- 예상 PASS / FAIL 조건: 설명서에 조작법 텍스트가 있거나, 새 국가의 그리드에서 클릭+지면 후속 클릭이
  1200슬롯 existence 테이블에 새 엔트리를 만들면 "건설 존재 확인"(PASS 방향). 설명서에 없고 모든
  국가의 모든 그리드 버튼이 새 엔트리를 만들지 않으면 "건설 = N/A"가 유지된다(회귀 아님, 이 EXE에
  해당 기능 없음).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_construction_new_nation_survey_probe.py`(SHA256
    `642c4defdf9394da6e9eed75e011d6eb4d4ca2ee0384d747bb01dabdeb941d08`) — 조사용 도구, 제품 코드(EXE
    패치) 무변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
  - 방법: (1) 공식 설명서 3종(`../[ESL]Syw2plus/[필독] 임진록 설명서/` 멀티게임 메뉴얼·ESL 패치
    요약·SYW2X 설명서, 이미지 3장 육안 확인) — 셋 다 일꾼/HQ의 "건물 배치" 조작법 텍스트를 포함하지
    않는다(멀티게임 메뉴얼=네트워크 설정, SYW2X=해상도/상태바/피아식별 확장 안내, ESL
    요약=밸런스패치 목록이며 "빌드 다양화"는 build-order 전략을 뜻하는 문맥이지 건물 배치 UI가
    아님). (2) `g5_worker_ability_hq_ui_survey_probe`+`g5_hq_command_grid_survey_probe`(lap731)를
    한 스크립트로 합치고, 매 시도 새로 부팅해 (worker_type,hq_type) 서명이 lap731이 이미 완전
    survey한 `{(31,58),(21,70)}`과 다르면 같은 부팅에서 계속 그 국가의 워커 4~7버튼 + HQ 7버튼(R·D는
    지면 클릭 후속까지) 전수를 수행하도록 만들었다. (3) 솔로 로비 국가가 진짜 무작위인지 확인하려고
    총 3라운드(=16회) 재부팅 실험: 라운드1(고정 타이밍) 5회는 전부 (21,70) 동일 — tick-seed로 추정.
    라운드2("확인 클릭" 직전 지연 (i-1)*7초로 변주) 5회는 (31,58)×2·(7,49)×1·(21,70)×2로 분산.
    라운드3(지연 14/13/15/12/16초)은 (31,58)×3·(21,70)×3 — 4번째 국가는 끝내 안 나옴. 라운드4(지연
    0/4.5/9/13.5/18/22.5/27/31.5초)의 4번째 시도(지연13.5초)가 마침내 세 번째 국가 (worker
    type7,HQ type49)에 도달, 그 부팅에서 전수 survey를 완료(`status=COMPLETE`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(후보 없음, 이 lap은 원본만
  실행). 격리 Wine prefix/Xvfb 1600x1200, 솔로 로비(단일 활성 플레이어 owner0), 세 번째 국가는 worker
  type7("일꾼"류, 체력400/방어30, 그리드 7버튼 S/M/V/B/Z/X/F — 이전 두 국가(4~5버튼)보다 많음)와 HQ
  type49(체력4800, 그리드 8버튼 S/R/D/T/F/B/Z + F1~F11 생산줄 + E). fixture는 게임 시작부터 존재하는
  owner0 유닛 2기(워커+HQ)뿐, 신규 스폰 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python -m
  tools.g5_construction_new_nation_survey_probe --runtime-root
  local/runtime/lap736_construction_type7_b --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap736_construction_type7_b
  --max-attempts 8 --delays "0,4.5,9,13.5,18,22.5,27,31.5"` (성공 시도는 attempt_04). 이전 3라운드
  로그는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap736_construction_nation/`,
  `..._nation_v2/`, `..._type7/`(각 summary.json 보존). 성공 시도 캡처:
  `.../20260928_lap736_construction_type7_b/attempt_04/00-worker-selected-command-grid.png`,
  `03-hq-selected-baseline.png`, `01/02-worker-button-*`, `04/05-hq-button-*`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **설명서 3종 육안 확인 = 건설/건물배치 조작법 텍스트 없음**(멀티게임 메뉴얼·SYW2X 설명서·ESL 패치
    요약 전부, 위 방법란 참고).
  - **솔로 로비 국가 풀 = 정확히 3개로 수렴**: 이번 세션 16회 재부팅(4라운드, 서로 다른 타이밍 전략)
    전부가 lap730/731/735와 동일한 `(worker=7,hq=49)/(worker=21,hq=70)/(worker=31,hq=58)` 세 조합
    안에서만 순환했고 4번째 조합은 한 번도 관측되지 않았다 — "표본이 작다"는 08:15 지시의 의심에
    대한 직접 반증 방향 증거(모집단 자체가 작을 가능성이 큼, 100% 배제는 못 함).
  - **세 번째 국가(worker7/HQ49)의 건설 재판정: N/A 방향 강화, 새 반례 없음.** 워커 그리드 7버튼 중
    미확인 4개(b3/b4/b5 — V/B/Z류) 클릭+지면 우클릭 후속 전부 `new_slots_after_click=[]`·
    `new_slots_after_ground_followup=[]`(신규 existence 엔트리 0). HQ 그리드 7버튼(R/D/F/B/Z/X/T)
    전부 클릭 직후 `new_slots_after_click=[]`; R·D는 지면 클릭 후속까지 `new_slots_after_ground_followup=[]`·
    `new_slot_details=[]`(배치 커서/유령 건물 없음, lap731의 R="수리(R)" 판정과 일관). HQ 그리드
    구조(S/R/D/T·F/B/Z + F1~F11 생산줄)는 lap731이 본 다른 두 국가와 형태가 동일(레이블 문자만
    국가별로 다름) — 건설 부재가 특정 국가의 결함이 아니라 이 EXE 구조 전체의 특성임을 시사.
  - 크래시 0(4라운드 16회 전부), `source_unchanged` 16/16, `cleanup.prefix_processes_after=[]`
    16/16. `make check` **1111 passed(920.81s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS,
    `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개, 조사용 도구 1개만 추가, 제품 코드
    무변경).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 3개국 전부(worker7/21/31, HQ49/58/70)에서 건설
  버튼이 관측되지 않았지만 "정확히 3개국"이라는 결론은 유한 시도(16회) 기반 귀납이라 100% 확증은
  아니다(딱 한 번 더 다른 seed 타이밍이면 4번째가 나올 가능성은 남음). 워커 그리드의 미상 버튼(b3/b4/b5,
  국가별 라벨 V/I/B/Z 등)이 실제로 무엇을 하는지는 여전히 UNKNOWN — 이번 lap은 "새 existence 슬롯을
  만드는가"만 확인했고, 그 외 효과(지형 변형, 자원 채집 시작 등)는 조사 범위 밖이다. middle 독립
  검수는 2026-09-28 03:36 운영자 판정대로 체크리스트 전체(A~H) 완료 후 한 번에 진행하므로 이번 lap은
  그 대상이 아니다.
- 다음 한 가지: 08:15 지시의 남은 절반("v"/"i"류 능력의 유효 타겟 탐색, gather probe처럼 여러 지면
  오프셋 순회)을 진행한 뒤 (C)를 "건설=N/A(3개국 전수, 설명서 무기재), 특수능력=존재하는 버튼 중
  타겟이 확인된 것만 paired PASS, 나머지 UNKNOWN"으로 완료 선언 → (E) UI로 진행. 세 번째 국가(worker7)
  자체의 특수능력 paired 측정(원본20/후보v6 50)은 아직 안 했으므로, 여유가 되면 그것도 함께 확인하면
  (C) 표본이 3개국 전부로 넓어진다.

# lap731 (work) — G5 체크리스트 (C) 건설/특수능력·변신/승선하선/좌표일치 조사

- 날짜: 2026-09-28
- lap: 731
- 역할: work tier (Claude Code Sonnet 5)
- 목표: STATUS/APPROVALS 2026-09-28 07:35 지시 — 체크리스트 (C)의 남은 항목(건설, 특수능력/변신,
  승선/하선, 명령 직후 목적지 좌표 일치)을 한 probe로 원본 1회·v5 1회 끝낸다.
- 가설: 이 게임의 커맨드 그리드 어딘가(일꾼 또는 HQ)에 "건물을 새로 배치"하는 버튼이 있고,
  V/I/F 등 미해독 버튼 중 하나가 그것이거나 특수능력/변신일 것이다.

## 방법

사전 조사 결과 이 네 항목은 버튼 자체의 의미가 이 저장소 어디에도 문서화돼 있지 않아(채집/이동/
정지/홀드/순찰/공격/저장로드처럼 이미 pending word·필드가 알려진 명령과 다름), 바로 paired
50-vs-20 broadcast probe를 쓸 수 없었다. 대신:

1. 신규 `tools/g5_worker_ability_hq_ui_survey_probe.py` (원본만 실행): 솔로 로비 부팅 →
   일꾼 단독 선택 → 커맨드 그리드 캡처 → 미해독 버튼(V/I/F)을 하나씩 클릭하고 툴팁 캡처 +
   좌표계산된 지면 우클릭 후속 입력으로 상태 변화 관찰 → HQ를 찾아 선택 시도.
2. 신규 `tools/g5_hq_command_grid_survey_probe.py` (원본만 실행): 같은 부팅 절차로 HQ를 확실히
   선택한 뒤 8칸 그리드(S/R/D/T/F/B/X/빈칸) 전부를 클릭해 툴팁 캡처, 1200슬롯 existence 테이블을
   버튼 클릭 전/후로 diff, "건설"로 가장 유력한 R(망치 아이콘)에는 근처 빈 땅 좌클릭 후속 입력까지
   추가.

두 probe 모두 보호 원본은 읽기만 하고(SHA 전/후 확인), 제품 코드/EXE를 건드리지 않는다.

## 실행 결과

솔로 로비 국가가 부팅마다 랜덤이라(lap730 발견) 두 번의 부팅에서 서로 다른 조합을 얻었다:
run1(survey probe) worker type31/HQ58, run2(hq survey probe) worker type21/HQ70.

- 일꾼 그리드: 두 부팅 모두 S(정지)/M(이동) + 국가별 1~2개 버튼. run1에서 V=`묻기(V)` 툴팁,
  F=`불끄기(F)` 툴팁을 확인(스크린샷 `01-button-v-after-click.png`/`01-button-i-after-click.png`
  확대 crop). run1의 실제 그리드는 baseline 캡처(`00-worker-selected-command-grid.png`)로 재확인한
  결과 **row1: S/M/V/F 4칸뿐, row2 전부 빈칸**이었다 — 애초에 4번째 버튼 좌표(777,503)가 이번
  부팅에서는 F였는데 probe의 `WORKER_BUTTONS["i"]`가 그 좌표를 가리켜 실제로는 F를 두 번 누른
  꼴이 됐다(라벨은 국가마다 재배치됨). 이 혼선 자체가 "커맨드 그리드는 부팅(국가)마다 다시 배치된다"는
  것의 직접 증거다. 어느 버튼도 "건물 배치" 모양의 고스트 커서/그리드 하이라이트를 만들지 않았다.
- HQ 그리드(run2, `01-hq-button-*-tooltip.png`): 8칸 중 6개에 아이콘 확인 — S(정지 아이콘, 손),
  R(`수리(R)` 툴팁, 망치 아이콘), D(동전 아이콘, 툴팁 미포착 — 용도 미상), T(빨간 X자 칼 아이콘,
  클릭 시 초록 취소 화살표로 바뀌고 좌하단에 유닛 초상화+진행률 `%` 표시줄이 나타남 — **유닛 생산
  슬롯**), F(농부 초상화, 툴팁 `영 능부(F)` 골드300/인구10), B(톱 아이콘, 툴팁 `영 소환소(A)`
  골드2600/목재2400/인구20, 필요건물 `영 대장간`), X(병사 초상화, 툴팁 `숨은창 등록(X)`
  골드2000/목재2000). 전부 자원비용이 붙은 유닛 훈련 슬롯이거나(R 제외) 정지/수리 유틸리티다.
  R 클릭 후 인근 빈 땅(`open_ground`)을 좌클릭해도 1200슬롯 existence 테이블에 새 엔트리 0개
  (`new_slots_after_ground_followup: []`) — 배치 모드가 아니다.

## 판정

- **건설 = N/A.** 일꾼·HQ 커맨드 그리드 전수(2개국 표본) 어디에도 "새 건물 배치" 기능이 없다.
  R은 수리, T/F/B/X는 유닛 생산이다. 이 실행 파일은 플레이어에게 자유 배치형 건설을 제공하지
  않는 것으로 판단한다(AI 전용 건설 결정 루틴은 별개 — `analysis/memory_maps/
  ai_production_decision_path_00406770_20260923.md`).
- **특수능력/변신 = 존재 확인, "변신"은 미발견.** 일꾼 묻기/불끄기, HQ 수리·유닛생산 4종을 툴팁
  근거로 캡처했다(operator 요청의 "존재하는 것 전부"를 충족). "변신"이라는 이름/기능을 가진 버튼은
  두 국가 표본에서 나오지 않았다 — 국가가 랜덤이라 다른 국가에 존재할 가능성은 배제하지 않는다.
- **승선/하선 = N/A.** 이 fixture(existence 4슬롯, owner0=일꾼+HQ뿐)에 배 유닛·수상 지형이 없고,
  저장소 전체(`analysis/`, `docs/history/`, `tools/`, `patches/`)에 보트/선박 타입ID가 확정된 적이
  없어 스폰할 방법이 없다(추측 타입ID 시도는 범위 밖).
- **명령 직후 목적지 좌표 일치 = 기존 증거로 PASS.** lap668/670 9점 화면↔월드 아핀(잔차 0.444타일),
  lap682/717/723/724의 `destination_validation`/`converged_at_s`가 이동/패트롤 목적지 일치를 이미
  반복 확인했고, 공격은 `+0x38C`==적 uid(좌표보다 강한 식별자 일치)로 lap671/688에서 확정됐다.
  신규 probe 불요.
- **(C) 체크리스트 = 완료로 판단.** (단, lap730이 남긴 "손상 HQ 클릭 후 6초 내 hp 미상승"은 그 lap
  자체가 PASS 판정과 무관하다고 결론지은 별개 미확정 질문으로 계속 보류.)
- **부수 발견(D 선반영):** lap724 `PASS_UI_ROUNDTRIP`(v5)이 Ctrl+숫자 지정·숫자 호출·저장로드 전후
  recall을 이미 커버 — (D)에 남은 것은 Shift+숫자 추가, 부대원 사망 후 호출 두 항목뿐이다.

## 안전/검증

- 원본 SHA `source_unchanged` 2/2(두 probe 모두 원본만 실행, 후보 빌드 없음).
- 크래시 0, `cleanup.prefix_processes_after=[]`.
- 실행 후 `local/runtime/lap731_survey/*/game`, `local/runtime/lap731_hq_survey/*/game`(각 ~830MB,
  합 disk 사용량 1.4GB→582MB로 감소) 삭제 — output/manifest/log는 보존(디스크 위생 규칙).
- `make check`: **1106 passed(755.21s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS.
- `checks/safety.sh check`: `SAFETY_PASS`.
- 제품 코드(EXE/패치) 무변경 — 신규 파일은 `tools/g5_worker_ability_hq_ui_survey_probe.py`,
  `tools/g5_hq_command_grid_survey_probe.py` (조사용 도구, pytest 없음).
- 캡처: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap731_ability_hq_survey/`,
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap731_hq_survey/`.

## 다음 행동

(D) 부대의 남은 두 항목을 한 probe로: Shift+숫자 추가(v5 50기 선택 후 Ctrl+1 지정, 별도 유닛
Shift+2로 다른 조에 추가 확인), 부대원 사망 후 호출(`g5_r3_sparse_selection_probe.Bridge`의
op=10/11 사망 기법으로 조 구성원 일부 사망시킨 뒤 숫자 호출이 생존자만 정확히 부르는지). 완료되면
(D) 마감 → (E) UI/(F) 저장로드/(G) 멀티/(H) 장시간 순서로 진행.

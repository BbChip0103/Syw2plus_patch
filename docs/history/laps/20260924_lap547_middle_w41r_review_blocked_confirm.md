# 2026-09-24 | lap 547 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, middle(진단·계획·확인). 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap546 work의 W41R 자기 라벨 `BLOCKED(gate: no_front_row)`가 원시 산출물로 재현되는가. 재현되면 카드
  `docs/work/active/G2_STRATEGY_W41R_PRESCAN_LAP545.md` §3 `BLOCKED`(gate 포함) 행대로 S1 op8 교전 경로 `BLOCKED`를 확정하고 §4 (가)~(라)를 사용자에게 보고한다.
- 예상 PASS / FAIL 조건: 입력 SHA 5건 일치 + H21a 8/8(60/60, 차이 0) + H22 조건①②④ 재판정이 기록과 일치 + 실측 T0와 겹치는 anchor 행 일치 → 라벨 `ACCEPT`.
  하나라도 어긋나면 `REJECT` 후 work 재검수(재실행 아님, M2).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source·브리지·테스트·하네스 변경 0, 커밋 0.
  문서: 이 파일, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL` §101.
  도구(temp, 읽기 전용): `temp/Syw2plus_patch/g2_capacity/20260924_lap547_middle_w41r_review/recompute_w41r.py`
  SHA `e309f4423173f6eff14bb17483a3c768d622e2e66d4ba1e885d91cb26f5ea0bb`, 산출 `recompute_stdout.json`
  SHA `61e4c3f482d08111cefef0e3f60b02701ea66b76ea13782ce2de1b14872e99be`(2회 실행 동일, 결정적).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: lap546 `run_summary.json` 기준 원본 `b56986e0…8a8ac` 전후 불변, 후보 `a10024de…2bb68`,
  브리지 `89e2ae36…fb7233`, 지도 100×100, 활성 8 AI owner, cap5000×8. 이번 회차 게임 실행 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 recompute_w41r.py > recompute_stdout.json`(cwd=위 temp 폴더). `checks/safety.sh check`=`SAFETY_PASS`,
  `checks/context_limits.py`=`CONTEXT_PASS`. 하네스 diff: lap543 `w41_run.py`(`a6ea50fb…`) 대비 삭제 1줄(docstring 첫 줄)·추가 블록 4개(110~126, 1460~1631, 1798~1831행)뿐 — 기존 로직 무변경 확인.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **라벨 `ACCEPT` — `BLOCKED(gate: no_front_row)` 재현. S1 op8 교전 경로 `BLOCKED` 확정(카드 §3).**
  - 입력 SHA 5건(`prescan.json` `0343d4fa…`, `run_summary.json` `8c58870f…`, `w41r_run.py` `ca6ccf1a…`, 시도1/2 T0 `ffdb070e…`/`064681fb…`) 전부 일치.
  - H21a: 8/8 `ok`, 전부 real 60·sim 60·missing/extra 0. `run_summary` 사본과 `prescan` 사본이 같다.
  - H22: 순서 42→34, `selected_L=null`. 기록된 행 집합으로 조건①②④를 다시 판정한 값이 9/9 기록과 일치. `ok=false`는 전부 조건① 때문.
  - 사전 스캔 ↔ 실측 T0(서로 독립인 lap543 실행): L=40↔시도1 owner2 {40,41}, L=42↔시도2 owner2 {42,43}, L2=48↔시도1 owner3 {48}, L2=50↔시도2 owner3 {50} — 4/4 일치.
  - 코드 판독: `simulate_row_major_fill`(+x, 행 끝 x=0 줄바꿈, 지도 밖 `None`), 조건③은 owner0·1 모사 좌표를 점유로 넣어 재판정, 조건⑤는 점유 반영 행으로 gap 판정 — 카드 ①~⑤ 문언과 일치.
  - **N202(정정, 신규):** lap546의 "y=34~50 구간 전체가 60기를 한 행에 못 담는다"는 **과대 서술**이다. 같은 `prescan.json`의 `rows3`가
    **행 45~50은 x=20 anchor에서 60기를 한 행에 담는다**고 보인다(행 48·50은 lap543 실측으로도 확인). 한 행 수용 실패는 **행 34~44**(x20~99)다.
    `no_front_row`의 실제 원인은 지형 하나가 아니라 **카드 규칙의 결합**이다: 위쪽 멤버는 한 행 수용 행이어야 하고(≥45), 조건④ L+9≤51 때문에 L≤42여야 한다 ⇒ 교집합 공집합.
    라벨은 바뀌지 않는다(카드 문언 그대로 적용한 결과).
  - **기록 결함(라벨 영향 없음):** 카드 H21은 "마스크와 원시 읽기 SHA를 `prescan.json`에 남긴다"를 요구했으나 `prescan.json`에는 `map_width/height·h21a·h22`만 있다.
    그래서 행 34~39의 자유 칸 수를 원시 마스크에서 다시 셀 수 없다. 대신 H21a 8/8 정확 일치와 실측 4행 교차 일치로 해독기 신뢰를 확인했다. M2(재시도 0회)라 재실행으로 보완하지 않는다.
  - W41R 출구 분포·`band_entry`·H20 표·`hit_attr`: **없음**(op5/op6 시딩 0건, T0 미도달, op8 0건). `prescan_vs_t0`도 T0가 없어 해당 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: S1 op8 교전 경로(W35~W41R)는 **op8 교전이 한 번도 시험되지 않은 채** 예산 규칙으로 닫힌다. 이는 증거 폐쇄가 아니다(N199 전열 가설 미시험).
  카드 밖 배치(anchor x≠20, 행 <24·>51, gap≠7)는 미탐색이며 M2로 이 경로에서 실행할 수 없다. 모델은 (가)~(라)를 고르지 않는다. G2 제품 미완료·마일스톤 승인 아님.
- 다음 한 가지: **STOP — 사용자 응답 대기.** 카드 §4 (가) (ㄴ) 최소 AI 예외 · (나) "8인"=사람 슬롯 fixture(가능성 미조사) · (다) S1 교전 트랙 중단(해석 약화) ·
  (라) 원본 이동 명령으로 다가간 뒤 공격하는 2단 입력. 사용자 선택이 오면 strategy가 해당 경로를 판정한다. 승인 대기 중 안전한 관련 독립 작업 없음(G1/G4는 G2 성립 전 잠정 중단, G3 중단).

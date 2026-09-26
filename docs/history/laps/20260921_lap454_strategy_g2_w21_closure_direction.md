# 2026-09-21 | lap 454 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5` / strategy(큰 방향) —
  `LOOP_STRATEGY_PROVIDER=claude`. 게임 코드 직접 수정 없음, 결정 가능한 문서 산출물만.
- 가설 / 사용자 관찰: lap453이 W21 카드 CLOSED를 판정하고 `ESCALATE_SOL` §32-4로 마일스톤 경계
  판정 4건(① (가) 자연 도달 지속 여부 ② 144k 개방 여부 ③ 미검증 3축 순서 ④ 되물음 2건)을
  strategy에 올렸다. 이번 회차가 그 판정이다.
- 예상 PASS / FAIL 조건: 4건 전부에 대해 결정 가능한 경계·근거·다음 카드 요구사항을 문서로
  남기고, lap453 핵심 수치의 독립 스팟체크가 불일치 0이어야 한다. 게임 코드/실행 0.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `docs/work/active/G2_STRATEGY_MILESTONE_DIRECTION_LAP454.md`, `loop/ESCALATE_SOL` §33 추기,
  `docs/history/laps/20260921_status_lap454_precompaction.md`(STATUS 원문 보존, SHA
  `220d0611827612dc277ce98b5d516eae24df991b9e8cf33d8d41d2553b248347`, 128줄), 본 기록,
  `docs/STATUS.md` 갱신. 제품/도구 source 변경 0(N22 충족 — 이번 회차 source를 바꾸지 않았다).
  커밋 0(LOOP_ALLOW_COMMITS 기본0), 전부 uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재해시 **불변**.
  게임 실행 0회 — 후보/fixture 없음. 스팟체크 입력은 lap452 기존 원시 산출물
  (`temp/Syw2plus_patch/g2_capacity/20260921_lap452_w21_step2_save_load_roundtrip/`).
- 실행 명령 / 로그 / 캡처 경로 및 해시: ①python3 인라인 재계산(lap452
  presave/postload 스냅샷, lap453 산출물 비참조) ②`python3 -m pytest
  tests/test_g2_eight_owner_setup.py -q` → **6 passed** ③`bash checks/safety.sh check` →
  **SAFETY_PASS** ④원본 직접 `sha256sum` 일치.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 스팟체크 **PASS(불일치0)**: live 1,161/1,161, lost0/mismatched0/new0, owner 장부 8/8
    `(146,4935,0)/(145,4900,0)×7`, tick 45→48, 보존 1,161기 전원 슬롯 2,840~4,000.
  - **판정①** (가) 계속하되 **W22 fixture-축 bounded probe**(레버=난이도/자원/인구/시드/지도/AI
    슬롯 구성, 한 work 회차 또는 60분/실패 가설 2회, 판정식 실행 전 고정)로
    `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED` 선판정. `NOT_FEASIBLE`이면 AI 행동 변경 = G4 잠정
    중단(2026-09-21 00:20 지시)과 충돌이므로 모델 착수 금지, 되물음 (ㄱ)/(ㄴ)/(ㄷ) 승격.
  - **판정②** 144k 발행 금지 **유지**(lap444 §1-4 불변, 부분 개방 없음).
  - **판정③** 3축 순서 = 건물 포함 혼합 구성(W23) → 전투/사망/재생산(W24) → LAN. (가)와 분리.
  - **판정④** 되물음 2건(lap404 (가)/(나)·F4 (B)/(C)) 사용자 대기 유지, 대신 고르지 않음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: W21 CLOSED는 모델 기술 컨펌이며 **사용자
  마일스톤 승인 아님**(3단 미완). (U4) RSS 하강 3건·(가) 도달성·건물/전투/LAN 축은 미검증
  그대로. N71~N73은 계측 재사용 전 수리 필수로 W22 카드에 강제했다. 이 판정 자체는 다음
  middle이 W22 카드 발행 시 경계 위반 여부를 검수한다.
- 다음 한 가지: **다음 middle(Sol/Opus5)이 W22 카드를 발행한다** — 카드 필수 항목 5건은
  `G2_STRATEGY_MILESTONE_DIRECTION_LAP454.md` §「다음 카드(W22)」와 `ESCALATE_SOL` §33-3.

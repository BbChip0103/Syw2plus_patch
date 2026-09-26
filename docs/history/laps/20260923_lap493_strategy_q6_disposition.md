# 2026-09-23 | lap 493 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-fable-5 / strategy(큰 방향, 게임 코드 직접 수정 없음)
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL` §56 Q6(A/B/C) 판정이 「다음 한 가지」. 판정 전 lap492의
  D1~D3를 원시로 독립 spot-check 한다.
- 예상 PASS / FAIL 조건: spot-check가 lap492와 불일치하면 판정하지 않고 재검수 회부(FAIL).
  일치하면 Q6 하나를 판정하고 경계를 문서로 고정(PASS).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `loop/ESCALATE_SOL`(§57 추가),
  `docs/STATUS.md`, 본 기록. 게임 source 변경 0, 커밋 0(LOOP_ALLOW_COMMITS 기본0, uncommitted 보존).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 이번 회차 게임 실행 0 —
  해당 없음. 검수 대상 원시는 lap491 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap491_w28_settlement_blockage_preproof/` 그대로.
- 실행 명령 / 로그 / 캡처 경로 및 해시: python3 인라인 재계산 2회(op4 콜 로그·window_samples·
  death_events). Fast 게이트 `make check` + `checks/safety.sh check` 로그 `/tmp/lap493_make_check.log`
  (결과는 아래).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - spot-check: op4 정확 2콜, 콜#2 `tick_before=tick_after=1618`(id596, used 4995→4980),
    550표본 첫 tick720/끝 tick2216 ⇒ 완주 598 < 600 (**D1 재현**); 표본 tick1615→1620 유일 5tick
    간격·`used=4980` 표본 부재(**D2 재현**); 표본449 tick1944 `count`6→5·`used`4990→4970인데
    `death_events.json`=`[]`(**D3 재현**). ⇒ lap492 검수 **ACCEPT**.
  - **판정: Q6-C 채택**(W28-R 최소 재실행 1회, D1~D3 동반 수리; R-1~R-6 경계는 `ESCALATE_SOL` §57).
    Q6-A 기각(사후 완화 선례 금지 + D2/D3 결함을 안고 144k 재개방 불가),
    Q6-B 기각(스크립트 기준선 오적용이 만든 2tick 미달로 답이 나온 실험을 영구 종결하는 비용 과대).
  - W28-R 1회 한정, 재미달 시 Q6-B 자동 종결 선판정(R-5). §8 W26(144k) 재개방은 W28-R
    ≥600tick 완주 + middle ACCEPT에 종속.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임 실행·바이너리 변경 0이라 회귀 없음.
  위험: W28-R 재실행의 비결정성(다른 tick 배치)으로 재미달 가능 — R-5로 종결 경로 선고정.
  사용자 전권 항목((ㄴ)·lap404 (가)/(나)·F4 (B)/(C)·3단 마일스톤)은 전부 불변·대기.
  이 판정은 제품 승인 아님. 다음 middle이 이 판정 자체를 검수 가능(원문 §56·§57 모두 보존).
- 다음 한 가지: middle(Opus5)이 §57 R-1~R-6을 반영한 **W28-R 카드 발행** → work(Sonnet5) 게임 1회
  실행 → middle 원시 독립검수.

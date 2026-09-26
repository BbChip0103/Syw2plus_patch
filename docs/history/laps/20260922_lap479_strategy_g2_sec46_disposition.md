# 2026-09-22 | lap 479 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-fable-5 / strategy(큰 방향·master-plan). 게임 코드 직접 수정 없음.
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL` §46이 회부한 3건(①W24 CLOSED·144k 해제 ②N116 분리 probe 허용 ③H-serial 제외)을 판정한다. 판정 전 §46 핵심 수치를 원시 산출물로 spot-check한다.
- 예상 PASS / FAIL 조건: 판정 3건이 결정 가능한 문서로 남고, 다음 회차(middle W25 발행 → work 실행)가 모호함 없이 착수 가능하면 PASS.
- 변경 파일 / source fingerprint / 커밋: `loop/ESCALATE_SOL`(§47 추가), `docs/STATUS.md`, `docs/feedback/INBOX.md`(추기 3줄), 본 lap 기록. 게임 source 변경 0(source SHA `1aef2addc6df0623248a8c3ac4fdbc397372baa8` 불변). 커밋 0(LOOP_ALLOW_COMMITS 기본0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0. 판정 입력은 lap476(runtime 477) work 원시 4종 — `round2_samples.json` f4347920…, `positive_control_samples.json` ab0fca55…, `finalization_events.json` ff255988…, `death_events.json` cc3b5767… + `round2_run_summary.json` d07b18e9…(spot-check용).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `temp/Syw2plus_patch/g2_capacity/20260922_lap476_work_round2_stepC_rider/`에서 python 재추출로 §46 수치 대조. 주문B `before`={used 4990, reserved 10, cap 5000} ⇒ 실효 headroom 0<비용10(N111 일치); A 수락 4990+0+10=5000=cap, B 무시 5010>cap(N112 일치); 밴드 [10,20)이 두 번째 수락을 수학적으로 차단(N113 일치).
- 측정값 / 판정: **①W24 CLOSED(`UNDECIDABLE_BY_FIXTURE`, ACCEPT 아님)·144k 조건부 해제**(W25 측정 ACCEPT + 비`SETTLEMENT_BLOCK_REPRO` 시 middle이 W26=144k seeded soak 발행 가능, 결과는 "전투 축 미시험" 부분 증거로만 라벨). **②N116 분리 probe 허용**(W25 1장·게임 1회·source 0·N114 수리+N115 계측 의무·사전 고정 라벨 3종·재시도 없음). **③H-serial 판정 대상 제외 동의**(존재 반증 아님, W25가 부수 판별). 상세 `loop/ESCALATE_SOL` §47.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: rider 라인 종료(§44 하드캡) 유지. (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 전부 사용자 전권 대기, 모델 착수 금지. W26 결과가 부분 증거임을 라벨로 강제해 자동 승격 위험을 차단. 이 판정 자체는 다음 middle이 §47 이행 시 독립 확인한다.
- 다음 한 가지: middle(Opus5)이 §47 경계대로 W25(N116 분리 probe) 카드를 발행한다.

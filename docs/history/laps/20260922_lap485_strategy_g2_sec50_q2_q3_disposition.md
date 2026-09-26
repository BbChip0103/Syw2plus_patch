# 2026-09-22 | lap485 | 목표 G2 (§50 strategy 판정 2건: Q2·Q3)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-fable-5, strategy(큰 방향/master-plan).
  게임 실행 0, 게임 코드 수정 0, source 변경 0, 커밋 0. 산출물은 문서뿐이다.
- 가설/판정 대상: lap484(middle, Opus5)가 `loop/ESCALATE_SOL` §50으로 회부한
  **Q2**(144k W26 개방 여부: E1/E2/E3)와 **Q3**(H-gate/H-place 판별용 op4 2콜 허용 여부: F1/F2/F3).

## 이전 바퀴(lap484) 검수 — spot-check ACCEPT

- 원시 7종 SHA 직접 재계산 = lap484 기재와 **전부 일치**:
  `window_samples.json` 420dfe5e…, `positive_control_samples.json` acca6f12…,
  `supply_probe_call_log.json` aecd0094…, `death_events.json` fb6ea9d8…,
  `finalization_events.json` 4f53cda1…, `w25_settlement_gate_probe.py` 46f8da26…,
  (대조용) `run_summary.json` da8c026f….
- 원시 재계산 수치: 350표본 전수 주사에서 창 내 장부 전이 **정확히 2건**
  (tick1943 `{used4995,res10}→{4985,0}` = N120 비균형 차감, tick2270 사망 `used−10·count−1`);
  op4 1콜 tick717 `{70,10}→{4995,10}`(호출 로그 n=1); 표적 arm progress100 도달 tick1414 →
  종결 tick1943 = **체류 529tick**; 대조군은 progress100 표본과 정산이 **같은 tick709**(지연 0,
  op1 tick7→해소 tick709 = L 702). ⇒ N119~N123 전부 원시와 정합, 측정 ACCEPT·해석 REJECT 채택.

## 판정 (전문은 `loop/ESCALATE_SOL` §51)

- **Q2 = E2 채택 (E1·E3 기각).** 144k(W26)는 계속 닫는다. 조건 문언 충족은 임계 교정 결함(N121,
  176배 신호가 5L=3510 임계 미달로 null)의 산물이라 통과 근거로 쓰지 않는다. N120 미결 상태의
  144k는 `used≤cap` 해석 자체가 오염된다(E3 라벨은 표시만 할 뿐 제거 못 함). **재개방 조건
  (§47 조건 대체):** W27 실행 + middle 측정 ACCEPT + 새 무결성 위반 0 ⇒ 라벨 무관 W26 발행 가능,
  단 N120·N121·N123 명시 + `used`/`reserved` 수치 "부분 증거" 라벨 강제.
- **Q3 = F1 채택 (F2·F3 기각).** op4 **2콜**(구성 1 + counterfactual 1)을 기전 probe 한정 허용,
  middle이 **W27** 발행. F2는 H-place만 배제 가능해 대개 게임 2회 소요, F3은 §49 D4 기각 논리
  그대로(lap404 (가)/(나) 입력 필요 + Q2 재개방 조건 영구 미충족).
- **경계:** R2′(정확히 2콜, 핀 3종 유지, 재사용 금지) · R3(counterfactual 전제 검사: pending 확인
  후 progress100 +50tick 이내 발행, 종결 시 `PRECONDITION_NOT_MET` 1회 종결) · 임계 재교정 의무
  (대조군 progress100→정산 지연 기준) · N114 수리·N115 생존 계측 유지 · 사전 고정 라벨 3종
  {`SETTLEMENT_RESUMED_AFTER_HEADROOM`, `NO_RESUME_WITHIN_WINDOW`, `PRECONDITION_NOT_MET`} ·
  N120은 W27에서 관측 의무만.

## 기록 필드

- 변경 파일: `loop/ESCALATE_SOL`(§51 추가), `docs/STATUS.md`(압축+갱신),
  `docs/feedback/INBOX.md`(추기), 본 lap 기록, precompaction 스냅샷 2건
  (`docs/history/20260922_status_lap485_precompaction.md` SHA
  `596e008c05eaa0443bfa0cac62ce8cf9749b3d4d68cfe9d2bde55b317a75f11d` 130줄,
  `docs/history/20260922_inbox_lap485_precompaction.md` SHA
  `1a5033eed7814239c37e482e2f1791b3c906ca0aaf06a03bc2de31212438b408` 400줄).
- 원본·후보 SHA: 원본 exe `b56986e0…` 불변(`checks/safety.sh check` PASS). 후보 빌드 변경 없음.
- 실행 명령: 원시 재계산(python3, temp 산출물 read-only), `checks/safety.sh check`,
  `python3 checks/context_limits.py`. 게임 실행 없음.
- 수치: 위 spot-check 절 참조. PASS/FAIL/SKIP: 판정 완료(PASS, 문서 산출물), 게임 검증 SKIP(역할 밖).
- fixture: 없음(신규 실행 없음). lap483 산출물은 op4 desync fixture였음을 라벨 그대로 유지.
- 다음 행동: middle(Opus5)이 §51 경계대로 W27 카드 발행 → work(Sonnet5) 게임 1회 실행 →
  middle 독립검수 → (재개방 조건 충족 시) W26 발행.

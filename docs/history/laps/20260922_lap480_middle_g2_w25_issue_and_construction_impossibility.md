# 2026-09-22 | lap 480 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5 / high / middle(중간계획·컨펌).
  게임 실행 0·게임 코드 수정 0. `.lap_counter`=480 기준(기록 계열도 480으로 맞춘다).
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL` §47 판정②대로 W25(N116 분리 probe) 카드를 발행한다.
  발행 전 §47이 고정한 구성 절차(ii)가 실제로 실행 가능한지 바이트로 확인한다.
- 예상 PASS / FAIL 조건: 카드가 모호함 없이 work 1회차에 착수 가능하면 PASS. 절차가 실행 불가이거나
  경계를 넘는 수단을 요구하면 착수 전에 근거와 함께 strategy로 되돌린다(§47 (iii)).
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`(신규),
  `loop/ESCALATE_SOL`(§48 추가), `docs/STATUS.md`, `docs/feedback/INBOX.md`(추기), 본 lap 기록.
  게임/제품 source 변경 0(문서만). 커밋 0(LOOP_ALLOW_COMMITS 기본 0, 저장소는 아직 무커밋 main).
  uncommitted 파일 SHA256: 카드 `73e55364ed48…`, `loop/ESCALATE_SOL` `c276bc6acf26…`,
  `docs/STATUS.md` `1495584ac937…`, `docs/feedback/INBOX.md` `464c0e5dc7a1…`.
  STATUS가 136줄로 130줄 상한을 넘어 압축 전 전문을 먼저 보존했다:
  `docs/history/20260922_status_lap480_precompaction.md`(원문 SHA
  `19409fb46275c4867f9c51b2faf81d16b3674952a2a32ca3ddfbb544317ec18a`, 136줄 / 스냅샷 SHA
  `dfadf7e448d0fece8f7f690435ae24313b5b1de7cb461e9eebd934ad8346a38b`) → 현재 113줄. 삭제 없음.
  INBOX는 400줄 상한 내(399줄)로 자체 추기만 축약했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0.
  검수 입력은 lap476(runtime 477) work 원시 5종뿐 — 직접 재계산한 SHA256:
  `round2_samples.json` f43479205e43…, `positive_control_samples.json` ab0fca551976…,
  `finalization_events.json` ff2559885f3b…, `death_events.json` cc3b5767a62d…,
  `round2_run_summary.json` d07b18e9b47d… (§46·§47 기재와 5/5 일치).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`(temp `20260922_lap476_work_round2_stepC_rider/`)와
  python 재추출, 그리고 `patches/population/runtime_bridge.c` 정적 판독.
  검사: `checks/safety.sh check` = `SAFETY_PASS`, `checks/context_limits.py` = `CONTEXT_PASS`.
  source 변경 0이므로 전체 `make check` 면제(2026-09-20 21:58 지시 + N22).
- 측정값 / 판정:
  **(1) lap479 독립 검수 = ACCEPT.** 원시 5종 SHA 전부 일치, 핵심 수치 재확인 —
  주문A `before`={used 4990, reserved 0}·raw_return 1(수락, rice 999,200→998,400),
  주문B `before`={used 4990, reserved 10}(4990+10+10=5010>cap ⇒ 무시), 669표본
  `max(used+reserved)`=**정확히 5,000**·초과 0건. N111~N113과 §47 처분에 어긋나는 값 없음.
  **(2) 신규 N117 — §47(ii)는 실행 전에 도달 불가.** op5/op6 가드
  `patches/population/runtime_bridge.c:211`이 `used+reserved+cost ≤ cap`을 강제한다
  (필드 대응 `ledger()` 99~102행: `reserved=U32(p+0x1c)`, `used=S16(p+0x200c)`, `cap=S16(p+0x2012)`).
  `reserved=10` 유지 중 시딩으로 도달 가능한 최대 `used`는 **cap−reserved=4990**인데 §47(ii)의 목표
  구간은 `used ≥ 4991`이고, 허용 type {5,7,46}의 최소 비용이 10이라 더 잘게 접근할 수도 없다
  ⇒ **정확히 1 supply 모자란 구조적 차단**. 문자대로 실행하면 결과가 이미 결정된
  `PRECONDITION_NOT_MET` 1회이고 승인된 게임 실행 1회를 정보 0에 쓴다.
  **(3) 신규 N118 — 목표 상태는 op4로만 구성 가능.** `runtime_bridge.c:154~163`의 op4는
  `U16(p+0x200c)=request[7]`(≤5000)로 `used`를 가드 없이 직접 쓴다 ⇒ `{used 4995, reserved 10,
  cap 5000}`(=N68 관측치와 동일 상태) 구성 가능. 그러나 op4는 G2 증거 경로에서 명시적으로 배제돼
  있다(`tools/runtime_env.py` `"op4_used": False`, 핀 `tests/test_g2_stock_stress.py:19`
  `assert "request(4" not in SOURCE`, `tests/test_g2_eight_owner_setup.py:166` `"op4" not in block`;
  근거는 AGENTS.md "장부 값만 바꾼 성공 금지"). ⇒ fixture 경계 확대라 middle이 단독 대체하지 않는다.
  **판정: W25 카드는 발행하되 상태 `BLOCKED_PENDING_STRATEGY`. 게임 실행 0회.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 카드 §4~§6에 §47의 의무(N114 판정식 수리,
  N115 producer 생존 매 표본 계측, 라벨 3종 고정, 재시도 없음)를 그대로 옮겼고, D2 승인 시에만
  풀리도록 게이트를 걸었다. D2를 쓰면 결과는 "장부 구성 fixture" 한정이며 cap 근접 안정성/G2 완료
  근거로 재사용 금지임을 카드에 못박았다. 144k(W26) 조건은 §47 그대로 유지되나 D4(접기)를 고르면
  그 조건이 충족될 수 없으므로 같은 판정에서 144k 처분을 함께 정해야 한다.
  (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 전부 사용자 전권 대기.
  **연속 무증거 회차 경고:** 이번 회차도 게임 실행 0이므로 §47이 건 제한에 걸린다 — 다음 회차는
  strategy Q1 판정 1회만 허용하고, 그 다음 work는 반드시 게임 실행 증거를 만든다.
- 다음 한 가지: strategy(Astra/Fable)가 `loop/ESCALATE_SOL` §48 Q1(D2/D3/D4)을 1회로 판정한다.
  D2 승인 시 다음 work(Sonnet5)가 카드 §4를 그대로 1회 실행한다.

# INBOX 종결 계보 3개 섹션 원문 보존 — 2026-09-23

`loop/PROMPT.md`의 INBOX 350줄 유지 규칙에 따라 옮겼다. 삭제·재해석 없음.
SHA256 `5f62ae8d7922d393f0bb6211719dbce8b7f192363bb93e30259f8cbf053d3e50`, 36줄.

---

## 2026-09-21 lap423·429·438·440·442 운영 회수 계보 (lap462 압축 — 원문 전량 보존, 삭제 없음)
- 이 5건(lap423 P-H 동기복구·lap429 디스크blocker해소·lap438 W18 동기복구·lap440 W19 동기검증회수·
  lap442 W20 background회수+lap441 middle W19 ACCEPT(R1) 독립검수)은 **모델/Root가 쓴 운영 회수
  기록**이며(사용자 지시 아님), 400줄 상한 때문에 lap462가 포인터로 줄였다. **원문 전량 보존**:
  `docs/history/20260921_inbox_lap462_precompaction.md`(SHA `d67aed38…f83113b03d`, 415줄).
  핵심 결론은 STATUS G2 표/검증상태(lap441~443)에 남아 있고, 개별 전문은
  `docs/history/laps/20260921_lap429_work_g2_w16_disk_blocker.md`·
  `20260921_lap441_middle_g2_w19_independent_review.md`(§8에 lap440 산출물)·
  `20260921_lap443_middle_g2_w20_t2_independent_review.md`(lap442 실행분)에 있다.
  lap423/438은 개별 lap 파일이 없어 위 스냅샷이 유일한 원문이다.

## 2026-09-21 lap425·427·428 계보 (lap449 압축 — 원문 전량 보존, 삭제 없음)

- 이 세 항목은 **모델이 쓴 회차 기록**이며(사용자 지시 아님), INBOX 400줄 상한(`checks/context_limits.py`)에
  걸려 lap449가 포인터로, **lap488이 한 번 더** 포인터로 줄였다. **원문 전량 보존, 삭제 없음** —
  `docs/history/20260921_inbox_lap449_precompaction.md`(SHA `ebf58faa…4288086`, 411줄)와
  `docs/history/20260922_inbox_lap488_precompaction.md`(SHA
  `4ab21ca1ec058bbc04c71ce5a36e1e62d282e37985b7b0e99eebb282025f82c7`, 419줄)에 그대로 있고,
  각 lap 전문은 `docs/history/laps/20260921_lap42{5,7,8}_*.md`에 있다.
  요지: lap425(W14 P-I) 판정 **(B) `+0x700` 자체가 표적** 확정 → lap427(W15 P-J) 당시
  (J2) 외부write·(J3) 블록write 보고 → lap428 middle 측정 ACCEPT·해석 2건 정정(N40으로 (J3) 강등,
  N41로 (J2) 근거 교체, 신규 N42·**N43**)·W16 발행.
- **⚠ 이후 뒤집힌 부분(요지는 남긴다):** **lap439 N51이 (J2)·(J3)·(K2)를 전부 REJECT**했다 — 진범은
  외부 write가 아니라 후보 빌드의 **immediate 재배치 오탐**(`0x0040F053` 종료 즉치)이고 세 store는
  원본과 바이트 동일했다. **(L2)·N43은 유지.** 현재 유효한 결론은 STATUS G2 표와 `ESCALATE_SOL`§25.


## 2026-09-21 Root 회수 — lap448 W21 Step1 24k cap-proximity soak (lap489 압축 — 원문 전량 보존, 삭제 없음)
- 이 블록(Root 동기 회수 + lap449 middle ACCEPT 검수)은 **모델/Root가 쓴 운영·검수 기록**이며
  (사용자 지시 아님), 400줄 상한 때문에 lap489가 포인터로 줄였다. **원문 전량 보존**:
  `docs/history/20260922_inbox_lap489_precompaction.md`(SHA
  `d9ec8ac257d353370346c5ee20ceddf5fb423db4459e977e91d2a8df8e437ebd`, 400줄).
  요지: lap448 background 방치를 Root가 동기 회수, 신후보 `a10024de…` N=4001 24k soak
  `CAP_PROXIMITY_STABLE`(부분 증거) → lap449 middle 원시 712표본 재계산 ACCEPT(U1~U3 PASS,
  U4 메모리 절반 귀속, N64~N68). 핵심 결론은 STATUS G2 표와
  `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`에 있다.

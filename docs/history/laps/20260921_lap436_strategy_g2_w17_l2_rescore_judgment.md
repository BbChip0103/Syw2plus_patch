# 2026-09-21 | lap 436 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5` / (세션 지정 effort) / **strategy(큰 방향/master-plan)**. 게임 코드 직접 수정 없음.
- 가설 / 사용자 관찰: `ESCALATE_SOL` §22가 올린 strategy 판정 3건 — ①좁힌 축(idx6/7/8) 재채점 허가 여부, ②§14 항목3(풀 재배치 lap399~408 안전성 재검토) 발동 여부, ③P2 귀속 트랙 존속/전환. lap433 §20이 W17을 진단 사슬의 마지막 카드로 고정했으므로 새 진단 카드는 strategy 재승격 없이는 불가.
- 예상 PASS / FAIL 조건: 판정은 문서 산출물로 남기며 실행 검증 대상이 아니다. 전제 검증(이전 바퀴 검수)은 lap434/435 원시 산출물 재계산 불일치 0을 PASS 조건으로 했다.
- 변경 파일 / source fingerprint / 커밋: `loop/ESCALATE_SOL`(§23 추가), `docs/STATUS.md`(갱신·압축), `docs/history/laps/20260921_status_lap436_precompaction.md`(신규, 압축 전 STATUS 보존 SHA `63b89bf2e4c0ae9a6e149274e9578521a2aa9793217acaedc402184d7875599d`, 128줄), 본 파일. 제품 코드/바이너리 변경 0. `LOOP_ALLOW_COMMITS` 미허용 → 커밋 0, uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재해시 **불변**. 게임 실행 0회(이번 회차 fixture 없음). 판정 입력은 lap434 run(op7/8owner/N=4001/seed42, 후보 `4331d9cd…`)의 기존 산출물.
- 실행 명령 / 로그:
  - 독립 재검수(이전 바퀴 검수): `poolwide_diff.jsonl`(76행)/`samples.jsonl`(379표본)을 `recheck435.py`·`recompute434.py` **비참조**로 새로 재계산 — 전이 s343/t10402 **유일**, idx6/7/8 `0→{17,16538,22432}`, `B` 분포 `{0:15,1:16,2:11,3:7}` 중앙값 1, 엄밀 n=48 `{0:14,1:16,2:11,3:7}` 중앙값 1(C1 재현), `|S|=2={3565,3604}`, 배경 70행 전원 idx∈{2,11,12,13,14,15}(`+0x6e8`/`+0x70c..+0x71c`), **idx6/7/8 배경 0행**, idx5/idx9 0행, 3604은 `+0x71c`가 s342에도 변한 상시 카운터. **lap435와 불일치 0.**
  - 게이트: `checks/safety.sh check` → `SAFETY_PASS`; targeted `patches/population/test_g2_full_capacity_persistence_compat_v1.py`+`test_runtime_bridge_contract.py` **6 passed**(50.38s); 이번 회차 source 미변경(N22, 통합 gate 생략); 디스크 여유 300G.
- 측정값 / 판정:
  - **판정① = 허가(명시적 예외).** 축 idx6/7/8은 W17 실행 **전에** W14~W16이 확정한 오염 오프셋이라 사후 선택이 아니고, N48은 새 측정이 아니라 동일 76행의 분해다. 불허 시 실측 신호를 버리고 게임 실행 1회를 재소비한다. "실행 후 판정식 변경 금지"와의 형식 충돌은 **1회성 예외**로 기록하며 선례가 아니다(재발 방지: 향후 카드는 실행 전에 전체창/표적축 두 지표를 함께 고정). 재채점 결과 `B_triplet=0`·`|S_triplet|=1={3565}` ⇒ **(L2) 단발형 확정 — 순회 루프 계열 소거, 새 게임 실행 불필요.**
  - **판정② = §14 항목3 발동 안 함, 열어 둠.** 발동 사유였던 N47이 N48로 무너졌고 국소성 근거는 대조 1슬롯→4001슬롯×49표본으로 강화됐다. 단 write 주체 미귀속이므로 닫지 않는다. 발동 조건 재정의: write 주체가 재배치(lap399~408) 도입 코드/구조로 귀속되면 즉시 발동.
  - **판정③ = P2 귀속 트랙 존속, 마지막 1수를 W18(하드웨어 write watchpoint EIP 귀속) 1장으로 고정.** (L2)로 순회 루프 계열이 소거되고 정적 수단은 소진(알려진 write 4곳 배제·언롤 3중 배제·P-L 7종 0건·`rep movsd` 정적 후보 0·1200-bound 사거리 미달 N43). §20의 "새 진단 카드는 strategy 재승격 필요"를 이 판정으로 이행한다. 종료 경계(실행 전 고정): 실행 1회+재시도 1회/60분 내 EIP 귀속 성공 → 다음은 **수리 카드**; 비재현/기술 실패(ptrace/DR 사용 불가 포함) → `BLOCKED` 보존 후 **트랙 중단/전환을 strategy가 판정**(진단 반복 금지). 카드 정의(판정식·안전 조항: 계측 전용, `WriteProcessMemory`/원본 변경 금지, 격리 사본·전용 prefix)는 다음 middle 회차가 한다.
- 회귀 / 남은 위험 / 승인 상태: 제품/마일스톤 승인 아님. 사용자 되물음 2건((가)/(나), (B)/(C))·F4 트랙(§5~§13)은 사용자 답변 대기 그대로. G1/G4 잠정 중단·G3 포기·목표 숫자 5000 불변. 위험: watchpoint가 Wine+ptrace 환경에서 기술적으로 막힐 수 있음 — 그 경우는 경계대로 BLOCKED 보고이지 실패 반복이 아니다.
- 다음 한 가지: **middle이 W18 watchpoint 카드를 발행**(판정식/성공·실패 조건/안전 조항 실행 전 고정), 그 다음 work 회차가 실행한다.
- uncommitted 파일 해시(세션 종료 시점): `docs/STATUS.md` `898c74cc9abfe6cabe96a3533512526ae9ba11443dadd192f659db19d4798423`(127줄) / `loop/ESCALATE_SOL` `3e15e1beeaa5eb0a601bd4fef42bf3393a06c68c03a9d6ec043a0b1ad93523e3`.

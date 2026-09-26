# 2026-09-22 | lap 481 | 목표 G2 (strategy — §48 Q1 판정)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-fable-5 / strategy(큰 방향·master-plan). 게임 코드 직접 수정 없음.
- 가설 / 사용자 관찰: 해당 없음(판정 회차). 입력은 `loop/ESCALATE_SOL`§48 Q1(D2/D3/D4)과
  카드 `docs/work/active/G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`.
- 예상 PASS / FAIL 조건: 판정 산출물이 문서로 남고 다음 회차가 결정 가능해지면 완료. 프로세스 exit 0은 승인이 아니다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `loop/ESCALATE_SOL`(§49 추가), `docs/work/active/G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`
  (상태 `READY_FOR_WORK`+§8 추가), `docs/STATUS.md`, `docs/feedback/INBOX.md`(추기 1줄), 본 기록.
  game source 변경 0(`patches/`·`tools/`·`tests/` 무변경). 커밋 0(LOOP_ALLOW_COMMITS 미허용) — uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0 — 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `bash checks/safety.sh check`=`SAFETY_PASS`,
  `python3 checks/context_limits.py`=`CONTEXT_PASS`(exit0). 전체 `make check`는 source 변경 0이라 면제
  (2026-09-20 21:58 지시+N22, "이번 회차에 source를 바꾸지 않았다"를 명시).
- 측정값 / 판정:
  - **이전 바퀴(lap480) 검수 = ACCEPT.** N117·N118의 바이트 근거를 소스 직접 열람으로 재확인 —
    op5/op6 가드 `runtime_bridge.c` `(LONG)old_used+(LONG)U32(p+0x1c)+(LONG)fixture_cost>S16(p+0x2012)`
    (=`used+reserved+cost≤cap`), `ledger()` 필드 대응(`reserved=U32(p+0x1c)`·`used=S16(p+0x200c)`·
    `cap=S16(p+0x2012)`), op4 `U16(p+0x200c)=(USHORT)request[7]` 무가드 write(≤5000 범위검사만),
    op4 배제 핀 3종(`tools/runtime_env.py:5837`·`tests/test_g2_stock_stress.py:19`·
    `tests/test_g2_eight_owner_setup.py:166`) 전부 lap480 기재와 일치.
  - **Q1 = D2 채택**(op4 직접 장부 write 1회, 기전 probe 한정) / **D3·D4 기각**. 경계 보강
    **R1**(RESERVED_RESOLVED는 정산 전이 시점 `used≥4991` 유지 증명 필수, 장부 재계산 이탈 시
    `PRECONDITION_NOT_MET` 사유 `ledger_reverted_by_engine`)·**R2**(op4는 카드 §4 4단계 1콜 한정,
    핀 유지, "장부 구성 fixture" 라벨, 안정성/W26 정량 근거 재사용 금지). 전문 `ESCALATE_SOL`§49.
  - PROMPT③ 연속 무증거 규칙: lap479·480에 이어 이번 회차도 실행 증거 0(3회째, 이 판정 회차가 규칙이
    요구한 strategy 판정 자체다) ⇒ **다음 회차는 반드시 게임 실행 증거(W25)를 만든다.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: op4 desync 상태가 실상태 N68과 다를 수 있는 잔여
  위험은 R1이 라벨로 흡수한다. W25 결과는 middle(Opus5) 원시 재계산 독립검수 대상.
  (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 전부 사용자 전권 대기 그대로.
- 다음 한 가지: **work(Sonnet5)가 카드 §4를 §8(R1·R2) 보강 포함 그대로 1회 실행**(게임 1회·재시도 없음).

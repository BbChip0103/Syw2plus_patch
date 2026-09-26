# 2026-09-23 | lap 520 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / work(실무).
- 가설 / 사용자 관찰: W33 카드(lap519 middle 발행) — 상태2 핸들러 `[0x43E174,0x43E2FD)`의 두
  `F5A0` 종료(`0x43E252`/`0x43E2D8`)가 무엇을 검사해 종별 발부율 1/66~12/14(N171)를 만드는지
  M-0(정적 해독)·M-1(정적 예측, 게임 실행 없음)로 판별한다.
- 예상 PASS / FAIL 조건: 카드 §3 — `EXIT_A_EXPLAINS`/`EXIT_B_EXPLAINS`/`BOTH_REQUIRED`(M-1
  예측이 S2L §4 14종 방향을 ≥12/14 맞히면) 또는 `UNRESOLVED`(둘 다 12종 미만이거나 해독 미완료),
  반증이면 `S2L_REFUTED`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규: `docs/history/laps/probes/20260923_lap520_work_w33_state2_exit_decode.py`,
    `analysis/memory_maps/ai_build_state2_exit_decode_lap520_20260923.md`, 이 lap 기록,
    STATUS/INBOX/ESCALATE_SOL 갱신.
  - 제품 source 변경 0, 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변, 전후 동일 확인).
  후보 EXE 없음(이번 lap은 정적 읽기 전용, 게임 실행 0).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260923_lap520_work_w33_state2_exit_decode.py`
  → exit 0, 산출 `temp/Syw2plus_patch/g2_capacity/20260923_lap520_work_w33_state2_exit_decode/
  w33_state2_exit_decode.json`, SHA256 `899db3f972829a7c739686a1662593f3fd05564c821bec19a3c6a984b9ac2195`
  (2회 실행 동일). `checks/safety.sh check` → `SAFETY_PASS`. `checks/context_limits.py` →
  `CONTEXT_PASS`(수정 전). 제품 source 불변 ⇒ `make check` 미재실행(동일 source 면제, 직전
  819 passed 유지, 2026-09-20 lap410 규칙).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **M-0 완료.** 단언 A1~A8 8/8 PASS. `F5A0` 호출 정확히 2곳, `+0x3A70` 쓰기 0건 ⇒ S2L §3
    미반증. EXIT_A(첫 루프, 사이트 소유권 맵+랜덤, **종-무관**) vs EXIT_B(둘째 루프,
    `AFDD0(edi,kind,...)`로 후보 평가, **종-의존**·`0x9B5228+kind*0x394` 레코드 `+0x16`/`+0x18`
    참조+kind 41/56/68 반경 오버라이드) 정확히 특정.
  - **M-1 = `UNRESOLVED_STATIC_ONLY`.** 종-의존 파라미터 테이블이 원본 `.exe`의 `.data` raw
    범위 밖(런타임 전용, A8)이라 순수 정적 신호는 반경 오버라이드(kind 41 대상 1종)뿐이고
    14종 중 13종은 이 신호로 구분되지 않는다 ⇒ 카드 §3 ≥12/14 기준에 정적만으로 도달 불가.
    M-2(런타임)는 이번 lap에서 실행하지 않았다(카드는 24k tick 소크를 요구하지만, 필요한 값은
    기존 `read_type_specs()` 경로에 필드 2개(+0x16/+0x18)만 추가한 **PS3 시점 단발 스냅샷**으로
    충분함을 §4에 적었다 — 시간 내 신뢰성 있게 기동→도달→종료까지 마칠 확신이 서지 않아 이번
    라운드에는 **시작하지 않았다**, PROMPT③).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(읽기 전용). 남은 위험:
  `+0x3A74`(EXIT_B 마커, 신규 발견) 리셋 시점 미검증, `0x4A4E70`/`0x4AF970`/`0xB3DDA8` 내부
  미해독. 독립 검수(middle) 대기. 사용자 승인 불필요(읽기 전용, (ㄴ) 무관).
- 다음 한 가지: **이번 lap은 실행 증거 무증가 2회째다(lap519도 게임실행0)** — 카드 §5가 예정한
  대로 **다음은 strategy/middle이 트랙② 지속 여부를 먼저 판정**해야 한다(PROMPT③). 계속한다면
  §4에 적은 경량 M-2(24k 소크 아님, PS3 단발 `read_type_specs()` 확장 스냅샷)를 다음 work 카드로
  좁혀 발행한다.

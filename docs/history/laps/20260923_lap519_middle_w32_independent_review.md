# 2026-09-23 | lap 519 | 목표 G2 (트랙② 건설 속도) — W32 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / middle(중간계획·컨펌). 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: (실행 전) W32 반증조건②는 상태1 `0x43DBB0`==0 → 같은 호출 `F5A0` 종료 경로를 카드가 빠뜨려서
  생겼다. (사후) 같은 호출 종료는 2/354뿐이라 이 가설은 **기각**됐다(N169). 실제 원인은 두 번째 호출의 상태2 종료다(N170).
- 예상 PASS / FAIL 조건: probe 사전 단언 A1~A4·B1~B6(docstring 고정), 사후 P5·P6(사후라고 명시). B2 불일치 1건 이상 또는
  B5 발부 1건 이상이면 FAIL.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/history/laps/probes/20260923_lap519_middle_w32_independent_review.py`,
  `analysis/memory_maps/ai_build_order_state2_loss_lap519_20260923.md`, `docs/work/active/G2_BUILD_STATE2_EXIT_PROBE_LAP519.md`(W33),
  이 파일, `docs/history/20260923_inbox_lap519_precompaction.md`, `docs/history/20260923_status_lap519_precompaction.md`.
  수정 W32 카드 §6, STATUS, INBOX, `loop/ESCALATE_SOL` §77. 제품 source 변경 0, 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…`(A1 확인). 후보 실행 없음. 입력은 lap518
  원시(W29/W31/W32 fixture `…d4a1_seed42`, 8 owner 조선 AI, 자원 1,000,000, cap 5,000, 후보 `a10024de…`).
- 실행 명령 / 로그 / 캡처: `python3 docs/history/laps/probes/20260923_lap519_middle_w32_independent_review.py`를 2회 실행.
  1차(사전 단언만)는 exit0, 산출 SHA `57f8a2be…`. 사후 P5·P6·O3·O4를 추가한 뒤 2회 모두 exit0, 산출 SHA
  `8f22385b412960657f594d027d7a375881cb69327f561404e77728d4076e8206`로 동일했다.
  산출 `temp/Syw2plus_patch/g2_capacity/20260923_lap519_middle_w32_review/w32_independent_review.json`. 캡처 없음.
- 측정값 / 판정:
  - B2 lap518 §2 표 **ACCEPT(불일치 0/8)**. B3/B4/B6 위반 0. 시작 tick 720/720 ≡ owner (mod 8).
  - **N168** 반증조건②는 카드 반증식의 결함이다. `0x43F88E` 쓰기는 분리할 수 없다(A2). gap<8 표본 352/354가 `+0xD32==1`이다.
    반증표본 267 = gap<8 2 + gap 8~15 233 + gap≥16 32.
  - **N169** 같은 호출 선택 실패는 2/354(0.56%)라 주 기전이 아니다(자기 가설 기각, 실패 가설 1회).
  - **N170** 손실 단계는 상태2 `[0x43E174,0x43E2FD)`다. `F5A0` 종료 2곳(`0x43E252`·`0x43E2D8`), 성공 시 `+0xD34=3`, `+0x3A70` 쓰기 없음(P5).
    gap 8~15 표본 334건 중 233건(69.8%)이 종료됐고 발부는 0이다(P6). 선택 직후 코호트 352건은 발부 25.3%, 전원 ≈2호출 안에 종료됐다.
    상태3 조건부 성공은 ≈0.84(추정). 전체 C/S 0.231.
  - **N171** 종별 발부율은 41 1/66·40 2/32·46 2/34 ~ 50 21/25·42 12/14로 갈린다. 분기 대응은 미해독이다.
  - 판정: W32 `CLOSED`. 라벨은 소급해 붙이지 않는다. 방향성 EXEC_FAIL은 확인됐고 단계는 상태2로 특정됐다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `make check`·`checks/safety.sh check` 결과는 STATUS 바퀴 기록에 있다.
  이 회차의 사후 분석 P5·P6·O3·O4는 사전 등록이 아니므로 W33 검수가 재확인해야 한다. 게임 실행 0 ⇒ 실행 증거 무증가 1회째.
  미결은 그대로다(Q9·Q8·Q7-B·"8인" 정의, 모델이 고르지 않음).
- 다음 한 가지: work(Sonnet5)가 W33 M-0/M-1을 실행한다(M-2는 조건부 24k 1회, 포그라운드).

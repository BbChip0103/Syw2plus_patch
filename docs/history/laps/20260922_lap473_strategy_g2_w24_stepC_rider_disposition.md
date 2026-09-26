# 2026-09-22 | lap 473 | 목표 G2 (W24 §5 Step C rider 라인 계속/종료 strategy 판정)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-fable-5 / strategy(큰 방향). 게임 코드 hands-on 수정 0, 게임 실행 0, source 변경 0, 커밋 0.
- 가설 / 사용자 관찰: 해당 없음(판정 회차). 입력은 `ESCALATE_SOL`§43(lap472 middle 검수)과 STATUS/INBOX의 Step C 계보(7회차·4회 연속 무효).
- 예상 PASS / FAIL 조건: 판정 산출물이 (a) 계속/종료를 명시하고 (b) 각 실험 결과의 종결 처분을 실행 전에 고정하며 (c) 잔여 예산을 하드캡하면 이 회차 목적 달성.
- 변경 파일: `docs/history/laps/20260922_lap473_strategy_g2_w24_stepC_rider_disposition.md`(신규), `loop/ESCALATE_SOL`(§44 추가), `docs/STATUS.md`, `docs/feedback/INBOX.md`(회수 추기). 전부 문서. uncommitted.
- 원본 SHA / 후보 SHA / 환경: 원본 pin `b56986e0…c9c08a8ac` 불변(이번 회차 접촉 없음). 후보/fixture 해당 없음.
- 실행 명령 / 로그: lap472 재계산 산출물 스폿 검증만 수행 — `temp/Syw2plus_patch/g2_capacity/20260922_lap472_middle_stepC_v4_recheck/recheck472_output.json`의 원시 SHA 3종(`0ab5cf2b…`/`ab6371d0…`/`db316f23…`)·`max_reserved=0`·headroom 5→130·회복 후 266표본·재유도 라벨 `RIDER_ORDER_NOT_ACCEPTED`가 §43 기재와 일치함을 확인. `checks/safety.sh check`·`checks/context_limits.py`는 문서 편집 후 실행(결과는 STATUS 기록).

## 판정 (strategy 처분, 사용자 번복 가능)

**rider 라인은 종료하지 않고 계속한다. 단, 아래 하드캡과 선판정 종결 규칙 아래에서만.**

### 근거

1. **판정 비용이 낮아졌다.** N105(§43-3)가 남긴 음성 대조 1건은 게임 ≈2분·source 변경 0·새 카드 0으로
   두 생존 가설(H-headroom / H-producer)을 결정적으로 가른다. 지금 종료하면 이 값싼 판별 기회를 버린다.
2. **§38 의무가 걸려 있다.** lap460 strategy가 lap404 (가)를 잠정 채택하며 stock rider probe를 W24에
   의무화했다(미재현 시 회귀 승격·재심). 무판정 종료는 (가) 재심 조건을 영구 미결로 남긴다.
3. **7회차 소비의 성격.** 가설이 고갈된 것이 아니라 fixture 결함이 연쇄 발견(관찰창→전제 미성립→교란)된
   것이고, 각 회차가 판별 공간을 실제로 좁혀 현재 2가설만 남았다. 그러나 무한 연장은 PROMPT③ 위반이므로
   아래 하드캡을 둔다.

### 하드캡

**잔여 예산 = 최대 2 work 회차.** 이 안에서 `RIDER_REPRO`/`RIDER_NO_REPRO`/아래 종결 라벨 중 하나에
도달하지 못하면 rider 라인은 그 시점에 무조건 종료한다. 재연장 없음. 새 카드 발행 금지(W24 §5 안).

### Round 1 (다음 work 회차, 필수): N105 음성 대조 — §43-5(2) 그대로

양성대조 주문 해소 직후(`used=85`, headroom 4,915 ≫ 비용 10) **같은 producer 슬롯 1182에 op1 2차
주문 1건**, ≥3×L tick 표본화, headroom 비접촉(대량 시딩 전 실행). 판정식·처분(실행 전 고정):

- **`PRODUCER_REFUSES_SECOND_ORDER`** (창 내내 `reserved=0` ∧ `count` 증가 0)
  ⇒ 원인은 producer 잔여 상태, headroom 무관. 단일 producer 연속주문 fixture 계열은 설계상 무효.
  **rider 라인 즉시 종료**, 최종 라벨 **`RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`**. Round 2 없음
  (다중 producer 재설계도 이 라벨 하에서는 착수하지 않는다 — 아래 종결 처분 참조).
- **`PRODUCER_ACCEPTS_SECOND_ORDER`** (`reserved`=10 후 정상 해소)
  ⇒ H-producer 기각, **H-headroom 유일 생존 가설 승격**, lap471 해석 지지. **Round 2 정확히 1회 허용**:
  W24 §5 Step C 안에서 **producer 2기 이상·각 1주문**으로 headroom<비용 상태의 주문을 만드는 최소
  재설계(지속 생산 흐름). 이것으로도 `RIDER_REPRO`/`RIDER_NO_REPRO` 미도달이면 같은 종결 라벨로 종료.
- **`CONTROL_BLOCKED`** (op1 거부/PS3 진입 실패)
  ⇒ 정확한 reason·장부 기록 후 **rider 라인 즉시 종료**(같은 종결 라벨). 우회 패치·가드 완화·op4 금지.

### 종결 처분 (어느 분기로 끝나든)

- **`RIDER_REPRO`로 끝나면**: stock 재현 확정 ⇒ lap404 **(가) 잠정채택이 실측 지지**로 승격(원본 고유
  동작). 최종 채택은 여전히 사용자 되물음((가)/(나)) 전권.
- **`RIDER_NO_REPRO`(유효 fixture에서)로 끝나면**: §38 조건 발동 — 후보 고유 **회귀로 승격**하고 (가)
  재심. middle이 회귀 조사 카드를 발행한다(이때만 새 카드 허용).
- **`RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`로 끝나면**: §38의 "미재현 시 회귀 승격"은 *유효한 stock
  probe의 미재현*을 전제하므로 **발동하지 않는다**. 처분: lap404 (가)/(나) 되물음에 "관측 해악 0
  (lap412 5,824표본·lap449 1,263건 포함 전 soak에서 크래시·풀 손상·라이브 `used>cap` 0) + stock 재현은
  현재 허용 수단(AI/설정 변경 금지·새 카드 금지) 안에서 판정 불능"을 사실로 추가해 **사용자 전권으로
  승격**한다. 모델은 (가)를 확정하지 않는다.
- **W24 종결**: Step C가 위 세 라벨 중 하나로 끝나면 middle이 A·B·D(전부 유효)와 함께 W24 CLOSED
  여부를 독립검수로 확정한다. **144k 발행 금지는 W24 ACCEPT까지 유지**(§38 판정5 불변).
- **사용자 전권 항목 불변**: (ㄴ) G2 한정 최소 AI/설정 변경, lap404 (가)/(나), F4 (B)/(C), 3단
  마일스톤 승인 — 전부 대기 그대로, 모델 착수 금지.

- 측정값 / 판정: 판정 회차. PASS(판정 산출물 성립). Step C 자체는 미결(위 규칙으로 결판 예정).
- 회귀 / 남은 위험: 없음(문서만). 위험은 Round 1이 또 다른 교란을 드러내는 경우이나, 하드캡이 상한을 막는다.
- 독립 검수 / 승인 상태: 이 판정은 strategy 처분이며 사용자 번복 가능. 다음 middle이 Round 1 결과를 독립검수한다.
- 다음 한 가지: work가 Round 1(N105 음성 대조)을 §43-5(2)+본 문서 규칙으로 실행한다.

- 커밋: LOOP_ALLOW_COMMITS=0 ⇒ uncommitted. 변경 파일 SHA256(16자, 본 파일 항목은 이 블록 추가 **전** 내용 기준):
6cb8a4e46afe5389… docs/history/laps/20260922_lap473_strategy_g2_w24_stepC_rider_disposition.md
c6c8764f9cc88be1… loop/ESCALATE_SOL
d588b6b4db433683… docs/STATUS.md
63d922169ad314ae… docs/feedback/INBOX.md

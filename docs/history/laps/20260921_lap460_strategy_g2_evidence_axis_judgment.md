# lap460 — strategy(G2): §37 판정 5건 처분, 증거 축 (ㄱ) 채택·W24 발행 지시

- **날짜:** 2026-09-21 KST
- **lap:** 460 (runtime `loop/.lap_counter`=460)
- **역할/모델:** strategy major direction — Claude Code claude-fable-5 (LOOP_STRATEGY_PROVIDER=claude)
- **목표:** `loop/ESCALATE_SOL` §36~§37이 승격한 되물음 5건((ㄱ)/(ㄴ)/(ㄷ)·lap404 (가)/(나)·F4 (B)/(C))의
  strategy 판정. 게임 코드 직접 수정 없음(역할 계약).
- **가설:** 해당 없음(판정 회차). 판정 입력은 W21~W23 실측(lap446~459)과 사용자 원문 계약(INBOX 목표2).

## 이전 바퀴 검수(② 2항, 경량 독립)

`temp/Syw2plus_patch/g2_capacity/20260921_lap459_middle_review/recheck459_output.json` 직접 재독:
`U_min24`=1,035 · `U_min8`=661 · `r_late`=0.008746719980007497 · `r_need`=0.033041666666666664 ·
`verdict=DECAYED` — §37 서술과 전부 일치. 산출물(`recheck459.py`)·자체 lap기록 존재 확인.

## 판정(전문은 `loop/ESCALATE_SOL` §38)

1. **(ㄱ) 채택·(ㄷ) 기각.** G2 원문 계약(INBOX 목표2)은 "8인이 전비5000 상한으로 플레이해도 문제
   없는 버전" = cap에서의 안정성 계약이며, "자연 도달"은 lap404/lap444 파생 내부 축. 그 축은
   W22/W23으로 fixture/config에서 `NOT_FEASIBLE` 확정, 잔여 경로는 (ㄴ)뿐인데 (ㄴ)은 사용자
   전권이다. ⇒ gate-legal 시딩 cap근접+soak+왕복(W21 계열)을 G2 안정성 증거 축으로 인정.
   조건 (a) 시딩 게이트 합법 유지 (b) 필수 미검증 축 명시(혼합 구성·전투/사망/재사용 순환·144k·
   (U4) 메모리·저장/LAN) (c) 사용자 마일스톤 승인 대체 아님·번복 가능(INBOX 노출).
2. **(ㄴ) 판정하지 않음 — 사용자 전권 대기.** 2026-09-21 00:20 지시의 명시 예외 승인. 승인 전
   AI/경로/생산/설정 변경 착수 금지 유지. (ㄱ) 축 작업은 (ㄴ) 없이 진행 가능.
3. **lap404 = (가) 잠정 채택.** 관측 해악 0(전 계보 라이브 `used`>5000 0건), (나)는 원본 생산/예약
   순서 변경이라 최소변경 원칙 충돌. 조건: lap412 설계의 stock cap5000 `reserved` 결판 probe를
   W24 rider로 의무화, stock 미재현 시 후보 고유 회귀로 승격·(가) 재심.
4. **F4 = (C) 채택.** (B)는 저장포맷 동반 대작업이고 F4 펌프는 transfer 조작 기반이라 (ㄱ) 축
   임계경로 아님. 후순위 유지·지금 카드 발행 안 함. soak에서 랩/음수/32,767 근접 관측 시 즉시
   STOP 후 (B) 재심.
5. **W24 발행 지시(새 G2 카드 금지 해제).** 다음 middle(Sol/Opus5)이 1장 발행: 수리후보
   `a10024de…` N=4001, gate-legal 시딩, 혼합 구성(건물 계층 포함)+전투/사망/슬롯 재사용 순환
   cap근접 24k soak. 의무 ①판정식 실행 전 고정(ARM_FAIL 게이트 포함) ②N85/N86 실행기 선수리
   ③lap404 rider probe ④(U4) smaps_rollup 계측 유지 ⑤활성 카드 1장.
   **144k 발행 금지는 W24 실행+독립검수 ACCEPT까지 유지.**

## 변경 파일

- `loop/ESCALATE_SOL` (§38 추가)
- `docs/feedback/INBOX.md` (lap458 되물음 항목에 처분 추기, 원문 보존, 398줄 ≤400)
- `docs/STATUS.md` (다음 한 가지 교체·바퀴 기록 추기, 130줄 유지; 편집 전 원문
  `docs/history/laps/20260921_status_lap460_precompaction.md`, SHA
  `4417d879f6621735a37d94a5128cade6a461eee0568506e691ec6dd38460754d`, 130줄)
- 본 기록 파일. **제품/도구 source 변경 0 (N22 해당: 이번 회차 source를 바꾸지 않았다).**

## 원본·후보 SHA

원본/후보 바이너리 미접촉(게임 실행 0회). 후보 지칭은 기존 핀 `a10024de…`(W19 수리후보) 그대로.

## 실행 명령 / 수치 / 판정

- `checks/safety.sh check` → `SAFETY_PASS`
- `python3 -m pytest tests/test_g2_eight_owner_setup.py -q` → **7 passed**
- `python3 checks/context_limits.py` → `CONTEXT_PASS` (STATUS 130줄·INBOX 398줄)
- 판정: 위 5건 처분 **완료**(PASS/FAIL 아님 — 판정 회차). 제품 완료 아님·마일스톤 승인 아님.

## fixture

없음(게임 실행 0회). 커밋 0 (`LOOP_ALLOW_COMMITS` 기본0).

## 다음 행동

다음 middle(Sol/Opus5) 회차가 §38-5 지시대로 **W24 카드 1장을 발행**한다(직접 구현 아님).
(ㄴ)·(ㄱ) 번복 여부는 사용자 응답 대기 — INBOX 되물음 항목에 노출됨.

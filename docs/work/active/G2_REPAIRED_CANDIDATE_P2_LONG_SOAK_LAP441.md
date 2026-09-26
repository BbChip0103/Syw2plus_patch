# W20 — **실행 카드**: 수리 후보 `a10024de…`의 P2 재실행(원본 생산 경로 장시간 soak)

- 발행자 / 역할: lap441 Claude Code `claude-opus-5` / high / **middle(검수·중간계획)**.
  근거 `docs/history/laps/20260921_lap441_middle_g2_w19_independent_review.md`,
  `loop/ESCALATE_SOL` §26.
- 발행 권한: W19 카드 §5 **(R1) ⇒ P2 재실행(장시간/원본 생산 경로)으로 진행**.
  strategy 경유는 W19 §5의 (R3)/(R5)에서만 발생하며 이번은 (R1)이므로 해당 없다.
- 수행 역할: **work (Sonnet5/high)**.
- 목표 연결: G2 — 활성 8인 각각 전비 5000 안정 플레이.

## 1. 선행 확정 사항 (재조사 금지)

lap441 middle 이 lap440 산출물 **비참조**로 재계산해 닫았다. 다시 재지 않는다.
재생성: `temp/Syw2plus_patch/g2_capacity/20260921_lap441_middle_review/recheck441.py`.

1. 수리 후보 SHA `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`는
   현재 source 로 **결정적으로 재빌드된다**(lap441 독립 재빌드 일치).
2. 원본↔후보 diff run: 구후보 **1,415** → 신후보 **1,390**. **추가 0건**, 길이 변화 0건,
   제거 **정확히 25건**이며 25곳 전부 원본 바이트로 **복원**됐다. 제거된 25개 명령 VA는
   `0x40f051`계 7 + `0x421349`/`0x48f4b4` 제외한 표-경계 cmp, `0x800000` 비트마스크 11,
   `push` 상수 5, `0x67f6f8` 1 이다.
3. imm 가드는 **규칙 기반**이고 fail-closed 다: 표에서 빠지면 abort, 구조규칙과 어긋나면
   abort, 가드를 끄면 `0x40F051`→`0x0108C020`·`0x401BC2`→`0x01220870`로 회귀가 **재주입**된다
   (lap441 독립 실증). `FO4_EXCLUDED_VAS` denylist 는 제거됐다.
4. Step4 실행: 동일 fixture(op7 resource-only / 8 owner / N=4001 / seed42)에서 tick **13,019**
   까지 진행, 기존 fault tick **11,928 통과**, read failure 0, 슬롯3565 `+0x6f8/+0x6fc/+0x700`
   **391 표본 전부 0**. lap413 구후보는 같은 tick 11,928에서 2회 모두 죽었다.
5. 따라서 **`0x00414133` fault 의 근본 원인은 제거됐다.** 이 카드는 그 재진단을 하지 않는다.

## 2. 이 카드가 답하는 단 하나의 질문

> 수리 후보는 **원본 생산 경로**로 8인 AI 대전을 장시간 돌렸을 때 fault 없이
> **전비 장부를 cap 5000까지 올릴 수 있는가.**

lap413 P2 의 원래 PASS 조건(`used ≥ 4900`)은 crash 때문에 한 번도 평가되지 못했다.
이번에 처음으로 평가한다. 진단이 아니라 **측정**이다.

## 3. 아직 참이 아닌 것 (이 카드로 주장 금지)

- 24k/144k 안정성, 저장/LAN 호환, 메모리 상한 — 전부 미검증.
- lap409 P1 왕복 무손실·lap411 24k soak 는 **구후보 `4331d9cd…`** 의 증거다.
  신후보로 재확인되지 않았다(§7의 후속 카드).
- 슬롯3565 3필드 0은 "런어웨이 write 가 사라졌다"는 뜻이지 슬롯 3565가 살아 있었다는 뜻이 아니다.

## 4. 실행 순서

### Step 1 — 준비 (실행 전 확인)

- `df -h /` 여유 ≥ 100G. 없으면 (T5) BLOCKED.
- 후보를 **재빌드**해 SHA 가 `a10024de…`인지 확인한다(핀 파일 복사 금지).
- 격리 전체 게임 복사본 / 전용 prefix / 빈 display(비중첩 번호). PID 발견은 lap434
  `movement_state_probe_pm.py`의 검증된 방식 재사용(INBOX 2026-09-21 00:51).

### Step 2 — soak 실행 (**1회, 동기**)

- fixture: lap413/lap440 과 **완전히 동일** — op7 resource-only / 8 owner / N=4001 / seed42.
- `STOP_TICK = 24000`(lap411 24k soak 와 같은 규모). 실측 속도 ≈33 tick/s 이므로 약 12~15분.
- 표본마다 기록한다:
  1. `tick`, `live`(전역 생존 수)
  2. **owner 0~7 각각의 `used` / `reserved` / `count`** — 이것이 이 카드의 본체다.
  3. 관측된 최대 slot index (확장 슬롯을 실제로 쓰는지)
  4. 게임 프로세스 RSS
- 읽기 실패·프로세스 사망은 즉시 기록하고 중단한다. 셸 background 금지, 동기 대기.

### Step 3 — 기록

산출물 `temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_repaired_p2_long_soak/`
- `samples.jsonl`(위 4항목), `run_summary.json`(판정 (T1)~(T5)), `run.stdout`/`run.stderr`
- lap413 구후보(11,928 fault / live468 / owner5 `used=1208,count=84`)와
  lap413 stock 대조군(tick12,112 live383 / tick13,116 live405 / tick13,804 match 종료)
  수치를 **한 표에 나란히** 적는다. W19 Step4가 이 대조표를 남기지 않은 것을 여기서 갚는다.

## 5. 판정식 (실행 **전** 고정 — 사후 재채점 불허, 갈래 서로소)

- **(T1) PASS.** tick 24,000 도달, fault/크래시/read failure **0**, 8 owner 전부 표본 존재,
  그리고 **어떤 owner-표본에서도 live `used` > 5000 이 없다**, 그리고 **최소 1 owner 가
  `used ≥ 4900`에 도달**. ⇒ P2 재실행 성공. 다음은 §7 후속(저장/LAN 재확인 → 144k).
- **(T2) 생산 정체.** fault 는 0인데 24,000 tick 안에 **어떤 owner 도 `used ≥ 2500`에
  도달하지 못한다.** ⇒ 안정성은 관측됐으나 cap 도달은 미평가다. 수치 보고 후 **STOP**.
  그 자리에서 fixture 를 바꾸거나 생산을 촉진하지 않는다(별도 카드 사안).
- **(T3) 새 fault/크래시.** tick·읽기주소·명령주소·owner·live 를 기록하고 **STOP**.
  **그 자리에서 새 진단 사슬을 이어붙이지 않는다**(W10~W18 계보의 12바퀴 비용 재발 금지).
  보고 후 strategy 판정으로 올린다.
- **(T4) 장부 위반.** live `used > 5000`인 owner-표본이 1건이라도 있다. ⇒ 수치와 함께 보고하고
  **STOP**. 사용자 되물음 2건(일시 초과 / 16bit 랩)과 F4 계보에 연결만 하고 임의 결정 금지.
- **(T5) BLOCKED.** 디스크/환경/빌드 불가. 사유를 정확히 적는다.

(T1)~(T5) 중 **정확히 하나**로 끝낸다. 즉석 가설 추가·감시 확대·다른 슬롯 추가 금지.

## 6. 대상 고정 (변경 금지)

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용, 직접 재해시).
- 수리 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`.
- 구후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe` 핀은 **지우지 않는다**
  (알려진 결함 바이트 정체의 대조용). 이번 실행에 쓰지 않는다.
- 게임 코드 직접 패치 금지. W19 §6의 금지 VA 목록을 그대로 승계한다.
- **이 카드는 제품 코드를 바꾸지 않는다.** 필요한 것은 probe 스크립트뿐이다.

## 7. 이 카드 다음에 열려 있는 것 (여기서 하지 않는다)

1. **신후보 저장/로드 왕복 재확인.** lap409 P1·lap411/412 W8 증거는 구후보 것이다.
   신후보로 marked compat 저장→로드 무손실을 다시 보여야 한다. 별도 카드.
2. 144k / 8인 전비5000 제품 판정. 3. LAN. 4. 사용자 되물음 2건(일시 초과·16bit 랩).
5. `_region_sites` **disp** 분기의 bucket0 가정(창 0x758) — imm 과 같은 계열의 잔여 노출,
   현재 런타임 반증 없음. 별도 카드.

## 8. 예산과 중단 조건

- 준비 + 실행 1회 + 재시도 **최대 1회** + 기록. 총 **90분**.
- **이 회차는 반드시 게임을 실행한다.** lap441(middle)이 게임 미실행 회차였으므로
  PROMPT ③ "제품/실행 증거가 늘지 않는 회차 연속 최대 2회" 카운터가 1이다.
  실행 불가 사유가 곧 (T5).
- 포인터 손상/저장 이상/원본 변조가 보이면 숨기지 말고 수치와 함께 보고하고 멈춘다.
- 자기 결과를 자기가 최종 승인하지 않는다. 다음 middle 이 독립 검수한다.

## 9. 검사

- **제품 source 를 바꾸지 않으면** 통합 `make check` 를 생략하고
  (INBOX 2026-09-20 21:58 / N22) **"이번 회차에 source 를 바꾸지 않았다"를 기록에 명시**한 뒤
  표적 테스트만 돌린다. 한 줄이라도 바꿨으면 통합 경계에서 `make check` **1회** 필수.
- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q`(기준선 6 passed).
- 매회 `checks/safety.sh check` → `SAFETY_PASS`, 원본 **직접 재해시** 불변.
- `docs/history/laps/`에 LAP_TEMPLATE 필드로 기록, `docs/STATUS.md` 130줄 이하 유지.
- 커밋은 `LOOP_ALLOW_COMMITS=1` 없이는 하지 않는다(기본 0) — uncommitted + 파일 해시로 남긴다.

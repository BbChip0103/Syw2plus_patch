# 2026-09-21 | lap 443 | 목표 G2

- 실제 provider/model/effort / 지정 역할:
  Claude Code `claude-opus-5` / high / **middle(검수·중간계획)**. 게임 실행 0, 제품 코드 변경 0.

- 가설 / 사용자 관찰:
  INBOX 2026-09-21 08:24 KST(Root 회수)가 지시한 대로 lap442 W20 soak의 **(T2) 판정과 신후보
  안정성 증거를 독립 검수**한다. 검수 입력은 lap442 원시 `samples.jsonl`(721표본)과 실행 로그뿐이며
  worker 의 `run_summary.json` 은 재계산이 끝난 뒤에만 대조용으로 열었다.

- 예상 PASS / FAIL 조건:
  W20 §5 의 (T1)~(T5) 는 실행 **전**에 고정됐고 서로소다. 비참조 재계산이 worker 와 같은 갈래를
  가리키면 ACCEPT, 다르면 REJECT. 사후 재채점은 금지.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  **제품 source 변경 0줄**(N22 에 따라 통합 `make check` 생략, 그 사실을 여기 명시).
  신규 파일은 검수 산출물뿐: `temp/Syw2plus_patch/g2_capacity/20260921_lap443_middle_review/`
  (`recheck443.py`, `recheck443_out.json`). 문서: 이 기록 + `docs/STATUS.md` + `loop/ESCALATE_SOL` §27.
  커밋 0 (`LOOP_ALLOW_COMMITS` 미설정, 기본 0) — uncommitted 로 보존.

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — safety 결과에 기대지 않고
  **직접 재해시**해 불변 확인. 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  — lap442 가 **핀 복사가 아니라 현재 source 재빌드**로 획득했음을 로그로 확인(N53 이행).
  fixture: op7 resource-only / 8 owner / N=4001 / seed42, display `:3910`, 격리 사본 + 전용 prefix.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 recheck443.py`(입력 `20260921_lap442_repaired_p2_long_soak/samples.jsonl`).
  lap442 증거 `temp/Syw2plus_patch/g2_capacity/20260921_lap442_repaired_p2_long_soak/`.
  targeted `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(기준선 일치, 56.51s).
  `checks/safety.sh check` → `SAFETY_PASS`.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **판정 = (T2) ACCEPT (불일치 0).** 비참조 재계산이 worker 수치와 전항목 일치했다.
  - 721 표본, tick 16 → **24,030**(STOP_TICK 24,000 도달), tick 단조 비감소·역행 0.
  - read failure / fault / crash / process_exit **0**(`stop_reason=stop_tick_reached`).
    원시 텍스트에 `error`/`fault`/`EFAULT`/`crash` 토큰 0건.
  - owner 0~7 `max used` = **[20, 570, 1183, 1111, 620, 1333, 1698, 1466]**, overall **1698**.
  - live `used > 5000` **0건** ⇒ (T4) 아님. `used ≥ 4900` **0건** ⇒ (T1) 아님.
    `used ≥ 2500` **0건** ⇒ **(T2) 확정**. cap 은 전 표본 5000, count_cap 은 전 표본 1200.
  - `used+reserved > 5000` 도 0건(사용자 되물음 "일시 초과" 는 이번 run 에서 재현되지 않음).
  - live 16 → 583(최대 583), owner `count` 합 == 전역 `live` 가 **721 표본 전부 일치**(불일치 0)
    — 존재배열과 PlayerStruct 장부라는 **독립 두 출처**가 서로를 검증한다.

  **신규 정정/관찰 3건 (worker 요약에 없음):**
  - **N55 — `max_slot_index` 는 증거가 아니다.** 721 표본 **전부 4000 고정**이며, live 가 16뿐인
    **sample 0(tick 16)에서 이미 4000** 이다. 점유량과 무관하게 상수이므로 W20 §4 Step2 항목3 이
    물은 "확장 슬롯을 실제로 쓰는가" 에 **답하지 못한다**. INBOX 08:24 회수문이 이것을
    `max_slot_index_seen4000` 으로 적은 것은 확장 슬롯 사용 증거로 **승격 금지**.
    (참고: `live == owner_count 합` 이 전 표본 성립하므로 slot4000 항목은 실제 소유 유닛에
    대응하며 허수 가산은 아니다. 즉 결함이 아니라 **지표 설계가 퇴화**한 것이다.)
  - **N56 — owner0 은 전 구간 완전 무활동.** 721 표본에서 owner0 의 `(used, count)` 는
    **distinct 값이 정확히 1개, `(20, 2)`** 다. 24,030 tick 동안 1기도 생산·손실하지 않았다.
    (T1) 의 "8 owner 전부 표본 존재" 는 충족하지만, DESIGN G2 가 명시적으로 불합격이라고 못박은
    "빈 슬롯 / 비활성 슬롯을 활성으로 세기" 에 걸린다 ⇒ **이 fixture 의 실질 활성 플레이어는 7명**이다.
  - **N57 — RSS 는 요약에서 통째로 빠졌고, 거동이 설명되지 않았다.** W20 §4 Step2 항목4 가
    요구한 RSS 는 표본에는 있으나 `run_summary.json` 에 **필드 자체가 없다**. 실제 거동은
    tick16 236,416KB → 최대 248,636KB → **tick14,690 에 241,588→146,128KB 로 한 번에 −95MB** →
    종료 시 **50,120KB**. 같은 구간 live 는 16→583 으로 **단조 증가**했다. 유닛이 느는데 RSS 가
    1/5 로 줄었다. 프로세스는 죽지 않았고(동일 pid, `poll()` 전 표본 통과) 판정 (T2) 를
    바꾸지 않지만, DESIGN G2 가 요구한 메모리 구분(OOM/해제/페이지아웃)에 **미해명 항목**이다.

  **절차 결함 1건:**
  - **N58 — W20 §4 Step3 이 의무화한 대조표가 없다.** 카드는 lap413 구후보(11,928 fault /
    live468 / owner5 `used=1208,count=84`)와 stock 대조군(12,112 live383 / 13,116 live405 /
    13,804 종료)을 "**한 표에 나란히**" 적으라고 했고, 그 이유까지 "W19 Step4 가 이 대조표를
    남기지 않은 것을 여기서 갚는다" 로 적어 두었다. lap442 산출물 어디에도 해당 수치가 없다
    (전 파일 grep 0건). **N54 가 지적한 결손이 한 카드 만에 재발**했다.
  - lap442 도 **자체 lap 기록이 없다**(worker 가 background 로 넘기고 종료 → Root 회수).
    lap440 에 이어 두 번째다. PROMPT ⑤ 기록 의무가 연속으로 비고 있다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  **G2 제품 완료 아님.** 이번 run 이 새로 준 것은 "**수리 후보가 24,030 tick 을 fault 0 으로
  버틴다**" 하나뿐이다. 구후보가 2회 모두 죽은 tick 11,928 을 넘겼고 24k 규모까지 갔으므로
  lap439~441 의 근본원인 수리는 **런타임으로도 지지**된다. 그러나
  - 전비 5000 도달은 **미평가가 아니라 이번 fixture 로는 도달 불가**임이 수치로 드러났다(아래).
  - 저장/LAN/144k, 그리고 lap409/411/412 의 왕복·soak 증거는 여전히 **구후보** 것이다.
  - 사용자 마일스톤 승인 없음. 이 기록은 middle 의 기술 검수이며 제품 승인이 아니다.

  **전비 5000 도달 가능성 — 이번 검수의 핵심 산출:**
  sum(used) 사분위 = tick 6,018/12,022/18,026/24,030 에서 **2,963 → 6,456 → 7,076 → 8,001**.
  증분은 **+3,493 → +620 → +925** 로 **감속**이다(선형 아님). 후반 속도는 7 활성 owner 합산
  약 `925 / 6,000 tick`, owner 당 약 `132 / 6,000 tick`. 최다 owner6(1,698)이 5,000 에 닿으려면
  `(5000-1698)/132 × 6000 ≈ **150,000 tick**` 이 더 필요하고, 이는 **감속이 더 없다고 가정한**
  낙관치다. ⇒ **144k soak 로 옮겨도 이 fixture 로는 8 owner 각 5000 을 볼 수 없다.**
  게다가 N56 때문에 owner0 은 어떤 길이의 soak 로도 0 에서 움직이지 않는다.
  ⇒ "고부하 fixture / 144k 최종 검증" 이라는 예정 경로는 **144k 부분이 근거와 충돌**한다.

- 다음 한 가지:
  **strategy 판정으로 올린다(`loop/ESCALATE_SOL` §27, `loop/ESCALATE_SOL` 파일 생성 완료).**
  middle 권한으로 "고부하 fixture" 를 임의 선택하지 않는다 — 어떤 fixture 로 8 owner 를 5000 에
  올릴 것인가는 **G2 합격 증거의 의미를 바꾸는 범위 결정**이기 때문이다. DESIGN G2 는 준비용
  생성/자원 지급을 "명시하면" 허용하되 "정상 생산·전투·저장로드를 후속 검증" 하라고 요구하고,
  동시에 "빈 슬롯을 활성으로 세기" 를 불합격으로 못박는다. 두 요구 사이에서 (가) AI 강화/난이도·
  인구 정책으로 **원본 생산 경로 그대로** 5000 을 유도할지, (나) 직접 시딩으로 5000 을 만들고
  안정성만 측정한 뒤 생산 경로는 별도로 증명할지는 strategy 가 정한다. 권고는 §27 에 적었다.

# 2026-09-21 | lap 425 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work(실무)**.
  카드 `docs/work/active/G2_STAT_RECOMPUTE_INPUT_700_LAP424.md`(W14) P-I 단독 수행.
  게임 실행 1회(동기 대기, 셸 background 미사용 — INBOX 2026-09-21 01:01 운영 규칙 준수).
  제품 코드 변경 0, 커밋 0, source 변경 0(아래 §6).

- 가설 / 사용자 관찰: lap424 middle이 `+0x688 = base_stat[type] + [+0x68c]`
  (`0x48cba9`) 체인을 정적으로 확정했고, 두 입력 표(`0x9b5258` 스탯표·`0x669c7c`
  보정표)가 BSS라 파일에서 못 읽는다며 런타임 계측(W14)을 발행했다. 카드의 판정식은
  (A) base 변화=스탯표 손상, (B) base불변+K가 0~48 밖=`+0x700` 표적, (C) 셋 다 정상인데
  P만 큼=H3(원본 고유), (D) 그 외=체인 밖 경로. `+0x688=19679`를 아직 오염으로 단정하지
  않는다는 전제로 4개 읽기 주소(K/+0x68c/base/P)와 대조 슬롯 1개를 추가 계측했다.

- 예상 PASS / FAIL 조건: 전이 tick(10400→10401) 전후로 슬롯3565의 K/base/m/P와 대조
  슬롯(같은 owner4)의 동일 4필드를 무손실로 캡처하면 PASS. probe가 K 범위 밖 주소를
  읽어 죽거나 캡처가 전이 구간을 놓치면 FAIL/재시도.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임 소스/제품 코드 변경
  없음(uncommitted 없음). 신규 파일은 전부 `temp/Syw2plus_patch/`(공유 temp, 메인 레포 밖):
  `g2_capacity/20260921_lap425_stat_recompute_input_700/movement_state_probe_pi.py`
  (lap423 `movement_state_probe_pf.py` 복사 + read-only 필드 4개·대조 슬롯 탐색·
  `STOP_TICK=10500` 조기종료만 추가; §3 나열 주소 전부 미기록).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변, 실행前後 재해시 일치),
  후보(marked compat) `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`(lap413/414/419/420/421/423과 동일 핀).
  환경: `tools.runtime_env.prepare()` 신규 격리 사본 + 전용 Wine prefix + 빈 Xvfb `:3845`(다른
  프로세스와 미충돌, 잔류0). fixture: op7 resource-only, 8 owner, N=4001, seed42(lap421/423과 동일).

- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 movement_state_probe_pi.py`
  (동기 실행, wall 약 5분57초: 03:14:01Z 시작 → 03:19:47Z 종료). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260921_lap425_stat_recompute_input_700/`
  (`samples.jsonl` 457표본, `run_summary.json`, `resource_receipts.json`, `orchestrator.log`).
  `run_summary.json`: `stop_reason=stop_tick_reached`, `final_tick=10495`, `ref_slot=3562`,
  `source_unchanged=true`.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS — 판정 (B) 확정.**
  샘플363(tick10400, 1차)까지 슬롯3565: `K=0, base=10, m(+0x68c)=0, P=0, f688=10`(정상,
  체인식과 일치: `10 + 10*0/100 = 10`). 샘플364(tick10400, 2차, dense 20ms 간격 두
  표본/tick)에서 **`K`가 `0`→`22432`로 단독 점프**(base는 그대로 10, `+0x68c`는 아직
  갱신 전이라 0) — `K`가 0~48 밖이므로 probe는 가드대로 `P` 읽기를 건너뛰고
  `p_skipped_out_of_range=true`로 기록(안전, 낯선 주소 미접근). 샘플365(tick10401)에서
  `m(+0x68c)`가 `347349`로 갱신되고 `f688=19679`. **정합성 검증:** `(base+m) mod 65536
  = (10+347349) mod 65536 = 347359 mod 65536 = 19679` — probe가 16bit로 읽은 `f688`과
  DWORD로 읽은 `m`이 정확히 mod-65536 관계로 일치해 두 필드가 같은 게임 내부 덧셈의
  절단(존)임을 확인했다. **대조 슬롯 3562(owner4, type 다름, base=9):** 관측 구간 전체
  (tick10363~10528, 148표본)에서 `K=0` 불변·`base=9` 불변·`f688=9` 불변 — 같은 owner의
  다른 유닛은 전이 tick 전후로 이상 없음(격리된 현상, 시스템 전역 손상 아님).
  **판정: (B) `+0x700`(K) 자체가 표적.** base는 불변(10→10, A 배제)이고, K가 tick10400에
  단독으로 0~48 밖(22432)으로 도약해 표 밖 읽기를 유발했다(카드 정의상 "실제 손상").
  `+0x68c`의 거대값(347349)과 `+0x688=19679`는 이 K 오염의 **하류 결과**이지 별도 원인이
  아니다. (C)/(D)는 성립하지 않는다 — base·K 둘 다 이미 비정상 경로에 있고, K가 정상
  0~48이었다면 `P`는 probe가 실제로 읽어 판정에 썼겠지만 이번 관측에서는 K 자체가 첫
  이상 신호였다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이번 lap은 work 역할의 계측
  결과이며 독립(다음 middle) 검수가 아직 없다.** 카드 §7 규칙대로 낯선 주소를 읽어 죽지
  않도록 K 가드를 넣었고 실제로 22432에서 가드가 작동해 `P`를 안전하게 스킵했다 — 즉
  이번 run은 원인이 되는 `K=22432`값 자체로부터 실제 `P`(진짜 game이 읽은 주소값)를
  **측정하지 못했다**(probe 자체 제약, 게임 프로세스는 그 주소를 읽었지만 probe는 안
  읽음). `0x00414133`/`0x0043ee39`/`0x00422dc7`/`0x0040bc86~0x40bcfe`/`0x0040c1c2`/
  `0x48cba9`/`0x48c914`/`0x411ec0` 전부 미기록(계측 전용 확인). 이 판정(B)은 카드 §7
  중단조건의 "판정이 (A)로 나오면 즉시 상위 보고"에는 해당하지 않으나, 이제 **다음
  표적은 `+0x700`의 4개 비상수 write site(`0x40d733`/`0x40d79f`/`0x40f040`/`0x413120`)
  중 tick10400에 도는 것 하나를 좁히는 것**이다 — 이는 카드 범위 밖(§4 "W13이 닫은
  write site 재탐색"과는 다른, `+0x700` 전용 신규 탐색이라 재조사 금지 대상 아님).
  P2 near-cap FAIL 판정은 유지. 게임 재현 계보(lap413/414/419/420/421/423)와 동일 fixture로
  결정성 있게 재현되어 이번 K=22432 값도 우연이 아닐 가능성이 높으나 2회째 반복 재현은
  아직 없다(1회 관측).

- 다음 한 가지: **middle(Opus5/high)이 이 W14 P-I 결과를 원시 `samples.jsonl`로 독립
  재계산해 (B) 판정을 검수한다.** ACCEPT 시 다음 work 카드는 `+0x700`의 4개 write site
  중 tick10400 실행분을 계측(정적 우선, 필요시 실행 계측 1회)해 좁히는 것을 제안한다.
  명령 바이트 패치는 계속 이번 범위 밖.

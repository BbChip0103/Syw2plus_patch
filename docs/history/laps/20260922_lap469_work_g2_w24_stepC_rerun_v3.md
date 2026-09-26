# 2026-09-22 | lap469 | 목표 G2 (W24 §5 Step C 3회차)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 지정 역할 **work**
  (실무). loop/PROMPT.md ①~⑥ 그대로 수행.
- 가설 / 사용자 관찰: lap467(middle)이 lap466 Step C를 `STEP_C_INCONCLUSIVE`로 REJECT했다
  (N96: 관찰창 322tick < 양성대조 해소지연 L=698tick; N97: 창 끝 producer `progress:46`이
  유휴0·완료100 사이 값이라 창 끝에서 생산이 **정상 진행 중**이었다는 결정적 증거). STATUS.md
  2026-09-22 "다음 한 가지"가 3회차 Step C 재실행을 지정하며 실행 **전** 고정한 판별식:
  (i) 관찰창 ≥3×L(이번 run 자신의 L, 상수 아님), (ii) producer 주기 질의로
  `(command,progress,production_type)` 시계열, (iii) progress100+reserved해소⇒`RIDER_NO_REPRO`/
  `progress≥L tick 정체+reserved잔존`⇒`RIDER_REPRO`/`창끝에도 진행중`⇒판정 보류·정직 보고.
  가설: 이 판별식으로 재실행하면 lap412/lap462/lap466이 본 "reserved=10 미해소"가 **고착**인지
  **단순 진행 중**이었는지 이번엔 구분될 것이다.
- 예상 PASS / FAIL 조건: 세 판정(`RIDER_REPRO`/`RIDER_NO_REPRO`/`RIDER_WINDOW_INSUFFICIENT`/
  `RIDER_BLOCKED`) 중 하나로 정직하게 끝나면 PASS(측정 성공), 어느 쪽이 나오든 카드 §5의 결과값이므로
  "REPRO가 나와야 성공"이 아니다. 게임 크래시/안전 위반/원본 변형이면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 메인 레포 변경 0(`runtime_bridge.c`
  `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`,
  실행 전후 동일 + 레포 현재 상태와 직접 재해시 일치). 새 스크립트/산출물만
  `temp/Syw2plus_patch/g2_capacity/20260922_lap469_work_stepC_rerun_v3/`
  (`step_c_run_v3.py`, `w24_step_c_rerun_v3.md`, `step_c_run_summary.json`, `step_c_samples.json`,
  `positive_control_samples.json`, `orchestrator_stepC_v3.log`). 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 재해시 동일).
  후보(`fixed_supply_5000.patched_bytes()` 적용) `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`.
  브리지 DLL `c226aa0f16534f469e8abf0370cc60f32b21b4f95aa7295bcd149a85c22d0af3`. 격리 전체 게임 사본
  `local/runtime/20260922_132015_108386_0` + 전용 Wine prefix + 빈 Xvfb `:198`. goal
  `_custom_game_chain_inject_g2_eight_seed42`(non-AI 8인 체인). 이번 rider는 owner0 1인·producer
  1기(op6 type46 건물, slot1182)·op1 type7 주문 1건뿐이며 W24 Step D(혼합 구성 24k 본체)는
  아직 실행하지 않았다(카드 §5만 재실행, §6 Step D는 범위 밖).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 step_c_run_v3.py --display :198`(동기 실행, 세션이
  직접 대기, background 미사용). 로그 `orchestrator_stepC_v3.log`(위 경로). 캡처 없음(화면 비교
  아님).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 양성대조 L=698tick(주문tick11→해소tick709, 415표본).
  동적 관찰창=max(300,3×698)=**2,094tick**. cap 근접 시딩 `used=4985,count=145`. cap 근접
  주문(tick714/716) 이후 110표본에서 producer `progress`가 tick716(0)부터 tick1412(99)까지
  **정확히 1씩 단조 증가**(양성대조와 같은 기울기), tick1418에 `progress100→reserved0,
  used4950→4960(+10),count144→145`로 **정상 해소**(해소 후 5표본 추가 확인, 재고착 없음).
  판정 **`RIDER_NO_REPRO`**(스크립트 고정 판별식 그대로 산출, 사후 재채점 없음).
  **PASS**(측정이 정직하게 완결됨 — 세 후보 판정 중 하나로 끝났고 크래시/안전위반 없음).
  targeted `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` **167 passed**.
  `checks/safety.sh check`→`SAFETY_PASS`. `python3 checks/context_limits.py`→`CONTEXT_PASS`.
  source 미변경이므로 전체 `make check`는 이번 회차 면제(2026-09-20 21:58 지시, "이번 회차에
  source를 바꾸지 않았다"). 게임 실행 1회, 종료 후 이 run 소유 wine/Xvfb 잔류 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이 결과가 lap412(24k, owner7 99.45%
  미해소)·lap406(144k, owner5/6 16,213~19,904tick 지속)·lap449(24k, owner4/7이 712표본 전체
  미해소)의 장기 soak 관측과 액면 모순된다** — 그 세 run은 이번 rider의 3×L=2,094tick보다 훨씬 긴
  창에서도 해소를 보지 못했다. 이번 run이 반증하는 것은 "reserved=10이 절대 안 풀린다"는 명제
  뿐이며, lap412/406/449가 본 장기 미해소를 재현하려는 시도는 이번 rider의 fixture(단일
  producer·단일 주문·무제한 자원·시딩 정지 상태)에 없었다. lap404(가) 잠정채택을 뒤집지도
  재확정하지도 않는다 — 이번 run이 무효화하는 것은 lap462/466 Step C의 **판정 절차**(관찰창
  부족)뿐이다. 상세 근거·화해 가설(h1~h3, 모델 미착수)는
  `temp/Syw2plus_patch/g2_capacity/20260922_lap469_work_stepC_rerun_v3/w24_step_c_rerun_v3.md`
  "⚠ 이 결과가 여는 새 질문" 절. 이 lap 자체는 work 자기판정이며 **다음 middle의 원시 3종
  비참조 재계산 독립검수 대기**(ACCEPT 되어도 W24 CLOSED·144k 해제·lap404 재심 종결은 자동
  판정하지 않음 — 위 모순이 해소되지 않았으므로). (ㄴ)·F4(B)/(C)·3단 사용자 마일스톤 승인은
  여전히 사용자 전권 대기, 모델 미착수.
- 다음 한 가지: 다음 middle이 이 run의 원시 산출물(`positive_control_samples.json`,
  `step_c_samples.json`, `step_c_run_summary.json`)만으로 `RIDER_NO_REPRO` 판정과 위 모순 서술을
  독립 재계산한다. 그 뒤 middle/strategy가 lap412/406/449의 장기 미해소와 이번 rider의 빠른 해소를
  화해시킬 다음 probe(위 h1~h3 중 어느 것을 좁힐지)를 지정한다 — work는 추측성 재시도를 반복하지
  않는다.

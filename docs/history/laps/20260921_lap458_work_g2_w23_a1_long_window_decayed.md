# 2026-09-21 | lap458 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 실무(work) 역할.
  카드 발행자는 lap457 middle(Claude Code `claude-opus-5`/high).
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md`(W23)의
  단일 질문 — W22에서 가장 높은 바닥을 만든 레버(A1, 지도 140×140)의 `used` 증가가 tick 8,000
  이후에도 유지되는가, 아니면 baseline과 같은 모양으로 감쇠하는가? A1 1 arm만, 동일 설정으로
  창을 tick 24,000까지 연장. 새 레버 값 추가 금지, 다른 arm 재실행 금지, op4/시딩 금지,
  게임 EXE/DLL AI 로직 미변경.
- 예상 PASS / FAIL 조건: 카드 §4 고정 판정식(실행 전 고정, 사후 재채점 금지) —
  1) tick 24,000 전 fault/crash면 `ARM_FAIL`. 2) `r_late(16k→24k) < r_need` 면 `DECAYED`
  (⇒ 자연 도달 fixture축 `NOT_FEASIBLE`, 모델은 AI 변경 착수 금지, §7 되물음 승격).
  3) `r_late≥r_need` 그리고 `U_min24≥1500`이면 `SUSTAINED`. 4) `r_late≥r_need`이지만
  `U_min24<1500`이면 `LEVEL_SHORT`. 고정 기대값(실행 전 기록): baseline과 같은 감쇠 모양이면
  `U_min24 ≈ 1,050~1,073`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - **이번 회차 source 변경 0건**(N22 명시 — `tools/inmm_stub/control_executor.c` 등 제품/도구
    소스를 한 줄도 바꾸지 않았다). 새로 만든 파일은 전부 `temp/Syw2plus_patch/`
    아래 실행 스크립트/산출물뿐이며 레포에는 없다.
  - `control_executor.c` sha256(as-run == repo, 불변): `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
  - 커밋: 없음(변경 파일 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    — 실행 전/후 직접 재해시로 불변 확인.
  - 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68` — 현재 source로
    재빌드해 SHA 일치 확인(핀 복사 아님, N53).
  - 브리지 DLL sha256(이번 run): `72b6066715e90b1cfd52e59b6a1f5493bdd586bb794145f6f6e4ce1c58efd2aa`.
  - 격리 실행: `runtime_env.prepare()`로 전체 게임 사본 + 전용 Wine prefix + 전용 Xvfb
    display(`:3990`, 기존 사용 중이던 `:77/:78/:103/:186/:187`과 겹치지 않게 선택) 신규 생성.
  - 활성 8인 전원 `ai=1`(owner0 포함), 지도 실측 140×140, 자원 op7로 rice/wood 1,000,000
    지급(8 owner 전원), 시딩(op5/op6)·op4 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 스크립트: `temp/Syw2plus_patch/g2_capacity/20260921_lap458_w23_a1_long_window/w23_a1_run.py`
    (lap456의 `w22_arm_run.py`를 그대로 본떠 arm을 A1 하나로 고정하고 `STOP_TICK`을
    8000→24000, `MAX_WALL_S`를 420→1500으로 올리고 `control_executor.c` as-run/repo sha256
    기록을 추가한 것 외 로직 변경 없음).
  - 실행: `python3 w23_a1_run.py --display :3990` 동기 실행. 모델 세션이 Bash
    `run_in_background`로 시작해 자동 백그라운드 전환됐지만 **세션을 종료하지 않고 직접
    대기**했다(진행 로그를 60샘플 간격으로 관찰, 완료까지 Monitor로 추적) — INBOX
    2026-09-21 01:01 취지("모델 세션이 직접 기다린다")를 셸 background 방치가 아니라
    하네스 추적 job으로 지켰다. 총 소요 약 11분(11:53:06 시작 → 12:04:38 종료).
  - 산출물: `temp/Syw2plus_patch/g2_capacity/20260921_lap458_w23_a1_long_window/A1/`
    (`samples.jsonl` 721표본, `fingerprint.json`, `run_summary.json`, `resource_receipts.json`,
    `orchestrator.log`), 판정 스크립트/원시출력
    `compute_verdict458.py`/`recheck458_output.json`.
  - 필수 fail-closed 산출물: `.../w23_a1_long_window.md`(카드 §5 형식).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - fingerprint: `d42=0,d44=2,d46=0,d48=0,d4a=1,d4c=0,seed=42`, map **140×140**(실측 확인),
    `ai_flags_at_ps3=[1,1,1,1,1,1,1,1]`.
  - `U_min8`=661(owner5, tick7,986) — W22 lap456/lap457 재계산치와 **정확히 일치**(결정성 재현).
  - `U_min24`=**1,035**(owner1=`o*`, tick24,012) — 실행 전 기대값 1,050~1,073 **바로 아래**
    (baseline-모양 가설과 모순 아님, 오히려 약간 더 감쇠).
  - `U_med24`=1,449.5(tick24,012).
  - `r_late`(owner1, tick16,009→24,012)=**0.008747**. `r_need`=(5000−1035)/120,000=**0.033042**.
  - 구간별 owner1 증가율: 0-2k 0.02542 / 2k-4k 0.04748 / 4k-6k 0.12394 / **6k-8k 0.14343(정점)**
    / 8k-16k 0.03303 / **16k-24k 0.008747**(정점 대비 16.4배 감쇠; baseline은 7.3배 감쇠).
  - 무결성(721표본): `live==Σcount` 불일치0, `used>5000` 표본0, tick역행0, 최소 rice967,672/
    최소 wood969,464, fault0, 최종 tick 24,012.
  - **판정: `r_late(0.008747) < r_need(0.033042)` ⇒ `DECAYED`.**
  - 표적 `tests/test_g2_eight_owner_setup.py` **7 passed**, `checks/safety.sh check` →
    `SAFETY_PASS`, 원본 직접 재해시 불변, `control_executor.c` 직접 재해시 불변(as-run==repo).
    이번 회차 source 미변경(N22)이므로 전체 `make check`는 재실행하지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **`DECAYED`는 카드 §4-2가 명시한 결과다: fixture/config 레버만으로는 (가) 자연 도달이
    fixture축에서 `NOT_FEASIBLE`이다.** 카드 §8 되물음 3건(ㄱ)/(ㄴ)/(ㄷ)과 기존 되물음 2건
    (lap404 (가)/(나), F4 (B)/(C))을 그대로 승격한다 — **이 lap이 대신 고르지 않았고, AI/경로/
    생산 로직 변경에 착수하지 않았다**(카드 §4-2·G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md
    §7 준수). `docs/feedback/INBOX.md`와 `loop/ESCALATE_SOL`에 승격 기록을 추기했다.
  - 144k 카드 발행 금지 유지(이번 회차도 24,000까지만). G2 제품 완료 아님.
  - 이번 소스 변경 0건이므로 다음 middle의 검수는 카드 §5 산출물과 이 lap의 원시 재계산
    (`compute_verdict458.py`)을 **참조하지 않고** `samples.jsonl` 721표본에서 독립 재계산하는
    형태가 될 것이다(이전 lap들의 검수 방식과 동일한 패턴).
  - `local/runtime`은 이번 1회 실행으로 소폭 증가(255G 여유에서 시작, 위기 아님).
- 다음 한 가지: **이 W23 카드는 여기서 닫힌다.** 다음은 middle(Opus5/high)이 이 lap의 원시
  재계산을 독립 검수하고, `DECAYED` 판정이 촉발한 되물음 5건(신규 3 + 기존 2)에 대해
  strategy(Astra/Fable) 또는 사용자의 방향 판정을 요청하는 것이다. work 역할은 그 판정이
  나오기 전까지 AI/경로/생산 로직 변경에 착수하지 않는다.

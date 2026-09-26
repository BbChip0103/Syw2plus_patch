# 2026-09-23 | lap 513 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 지정 역할 work(실무).
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md` §8(안 B)의
  M-a 런타임 재확인(`+0x2016` 24k 상수성)이 lap512에서 스크립트만 남기고 미완주(background
  `make check` 대기 중 세션 종료, orchestrator.log 2줄=bridge build 직후 정지, 게임 미실행).
  STATUS lap512 인수 기록에 따라 그 source(`hole_constancy_run_lap512_M-a_0x2016_24k.py`)를
  검수만 하고 **수정 없이** 포그라운드 동기 실행으로 완주시킨다.
- 예상 PASS / FAIL 조건: tick≥24,000 도달 + 8 owner `+0x2016..+0x2018` 2바이트 전 표본
  기준값과 동일(위반 0) = `HOLE_CONSTANT`. 위반≥1 또는 fault/조기종료 = 안 B 기각→`BLOCKED`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/패치 소스 변경 0(제품 코드
  변경 없음). 삭제·재생성한 것은 lap512가 남긴 미완성 빌드 산출물 `bridge_build/`·`__pycache__/`
  뿐(같은 스크립트가 exclusive-create로 재생성, exit code 1 → 정리 → 재실행). uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전후 불변, 패치 0).
  격리 game copy + Wine prefix(`runtime_env.prepare`), Xvfb `:210`(사전 사용 없음 확인).
  8 owner AI 대전(`_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`), op7 자원 픽스처
  rice/wood 각 1,000,000 전 owner. bridge dll `unit-pool-capacity=1200`(stock 주소, EXE 패치 0)
  sha256 `89e44c18fb92d7a06e1c4047eda870f88c720a45a5c5c6c15cc89cf29e6ed589`.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `LAP512_DISPLAY=:210 python3 hole_constancy_run_lap512_M-a_0x2016_24k.py`
  (cwd `…/temp/Syw2plus_patch/g2_capacity/20260923_lap512_work_f4b_ledger_32bit_hole_b/`).
  `run_summary.json` sha256 `b8c3b4525f3a5237035b21da8d9b072a31ba127c30bea4af1443740a3be05c4c`,
  `samples.jsonl`(721줄) sha256 `030f6a0eb6197643c3f3a5caea6ea8dad2641d2cd1d55240f5d582559ebae7a4`,
  게임 런타임 산출물 `local/runtime/20260923_143757_3428058_0/`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `stop_reason=stop_tick_reached`,
  `final_tick=24019`, `sample_count=721`, `hole_violation_count=0`,
  `verdict=HOLE_CONSTANT`(exit 0) ⇒ **PASS**. `source_unchanged=true`(원본 read-only 확인).
  단위 회귀 `patches/population/test_supply_ledger_32bit.py`: **23 passed**(0.08s).
  `make check`: **819 passed**(510.22s) + ruff clean + mypy clean + `CONTEXT_PASS`.
  `checks/safety.sh check`: `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이로써 카드 §8 M-a~M-h 전부 기계/실행 증거로
  닫혔다(M-b~M-h는 기존 단위 테스트, M-a는 이번 lap의 24k soak). **이 결과는 work 자기 승인이
  아니다 — 다음 middle(Opus)의 독립 재계산이 2단이다.** 카드 §5 규정대로 이 카드의 PASS 범위는
  정적+단위+원복까지이며 **패치 후보 EXE의 실제 게임 실행 검증은 포함하지 않는다**(그 실행
  검증의 제외 범위 여부는 미결 Q9 그대로). 구세이브 비호환(§4, 신규 게임 전용)도 불변.
- 다음 한 가지: 다음 middle이 이번 lap의 원시 산출물(`run_summary.json`/`samples.jsonl`)을
  재계산해 `HOLE_CONSTANT` 독립 검수 후 카드 W30을 `CLOSED`할지 판정한다. 이후 순서는
  2026-09-23 12:55 지시 트랙②(건설 선택 로직 분석, `FUN_00406C70` 추첨 + H-CROWD 주소 정정)이며,
  Q9/Q8/Q7-B/"8인" 정의는 여전히 사용자 전권 대기.

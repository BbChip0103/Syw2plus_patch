# 2026-09-23 | lap516 | 목표 G2 (트랙② 건설 속도)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work(실무)**.
  카드 `docs/work/active/G2_BUILD_PACE_STATE_PROBE_LAP515.md`(W31, lap515 middle 발행).
- 가설 / 사용자 관찰: lap515 N158~N161(진영 블록+건설 속도 병목)을 이어, "조선 AI가 왜 느리게 짓나"를
  M-0(정적 케이던스 해부) + M-1(24k 런타임 표본) + M-2(집계+라벨)로 판별한다. 카드 §3 사전 고정 라벨
  4종(`SELECT_EMPTY`/`SELECT_OK_EXEC_WAIT`/`CADENCE_BOUND`/`UNCLASSIFIED`) 중 하나를 데이터 개봉 전
  정의대로 붙인다.
- 예상 PASS/FAIL 조건: M-0이 상태1~4 jump table을 바이트로 재확인하고, M-1이 24,000 tick까지 8 owner
  전원을 읽기 전용으로 완주하며, M-2 라벨이 재해석 없이 산출되면 `PROBE_OK`. 게임 crash/fault·원본
  변경·AI 로직 변경이 있으면 FAIL.
- 변경 파일 / source fingerprint / 커밋: **제품 source 변경 0, 커밋 0.** 신규 산출물은 전부
  `analysis/`·`docs/`(문서)와 공유 `temp/Syw2plus_patch/`(원시 probe 산출물)뿐:
  - `analysis/memory_maps/ai_build_pace_state_probe_lap516_20260923.md`(신규, M-0/M-1/M-2 전문)
  - `docs/work/active/G2_BUILD_PACE_STATE_PROBE_LAP515.md` §6 진행 기록 추가
  - `docs/history/laps/20260923_lap516_work_w31_build_pace_state_probe.md`(본 파일)
  - `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL` 갱신
  - `temp/Syw2plus_patch/g2_capacity/20260923_lap516_work_w31_build_pace/w31_build_pace_run.py`
    (lap506 `w29_ceiling_run.py`를 **복사**해 M-1 표본 필드만 추가; 원본 파일은 수정하지 않았다)
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(run 전후 불변 확인)
  - 후보(N=4001 persistence-compat) `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
    (W29/lap507과 **byte-identical** 재생성)
  - 격리 Wine prefix, Xvfb `:4016`, 140×140 지도, seed42, 8 owner 전원 AI·조선(nation1),
    op7 자원전용 주입(rice/wood 각 1,000,000), cap5000, `+0x2010`=1200(로스터 1,200칸) — W29와 동일 fixture.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 w31_build_pace_run.py --display :4016`(포그라운드 동기, 세션 종료 없이 완주 — PROMPT③
  2026-09-21 01:01 규칙 준수). 경로
  `temp/Syw2plus_patch/g2_capacity/20260923_lap516_work_w31_build_pace/`:
  - `w31_build_pace_run.py` SHA256 `1bb8140a5e32f82c669a7c8b2d47ea7c34fb178df85214a26324248fdeb206a6`
  - `samples.jsonl`(1,439줄) SHA256 `9fa1073709c4048895dc2b0495a5332f089b5b20c14f72c8904a48a081808355`
  - `build_pace_summary.json` SHA256 `97d328b8fe77975fbc6d53778112c78267570ee00251feaa510baff9d86a09eb`
  - `run_summary.json` SHA256 `aadd5b166250a9525a983cef6440c7894f33eed926aa10a807d96a40e648a950`
  - `orchestrator.log`, `fingerprint.json`, `bridge_build/`, `resource_receipts.json`, `production_table.json`,
    `type_specs.json`, `partial_evidence_check.json`도 동일 디렉터리에 보존.
- 측정값 / 판정: **`PROBE_OK`**, `stop_reason=stop_tick_reached`, `final_tick=24013`,
  `fault_or_crash=false`, `any_owner_used_over_5000=false`(max_used_by_owner
  `[1708,1035,1583,1536,1513,1070,1406,1376]`), `source_unchanged=true`,
  `control_executor_c_unchanged=true`. `U3_pass=false`(1/1,439 표본 스냅샷 비원자성 레이스,
  §2 memory_map 문서에서 무해로 설명 — 두 개의 개별 ReadProcessMemory 호출 사이 1틱 경합, 메모리
  손상/안전 위반 아님). M-0: 상태1~4 jump table 바이트 재확인 + `FUN_0043F5A0`이 실패 시 `+0xD34`를
  **0으로 리셋**함을 신규 확인(재시도 아니라 오더 종료) + `+0xD34`가 20종 AI 오더 공용 필드임을
  `.text` 전수 byte-pattern 스캔(41건)으로 신규 확인. M-1/M-2: 8 owner 전원 상태0(비활성) 지배
  85.6~87.9%, 상태1~4 합계 3.5~5.1%(상태1은 표본 해상도 내 0회 포착), 건물 순증가 9~18채/owner
  (감소 0건). **라벨 = `UNCLASSIFIED` 8/8**(카드 §3 정의상 `SELECT_EMPTY`/`SELECT_OK_EXEC_WAIT`는
  데이터가 반증, `CADENCE_BOUND`는 정성적으로만 부합하고 정량 판정 근거인 "M-0 호출 주기"가
  미해독이라 확정 불가 — 재해석 금지 원칙에 따라 원시 그대로 보고). 선형 외삽(경고 문구 포함):
  조선 owner가 5,000 도달까지 필요한 tick은 owner7(최속) ≈380,033 ~ owner5(최둔) ≈796,176
  (24k의 15.8~33배).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 0(제품 source 변경 없음).
  남은 위험: `+0xD34` 재무장 스케줄러 미해독(다음 probe 1순위), 상태3/4의 콜 대상
  (`FUN_00407890`/`FUN_004076C0`/`FUN_004AFDD0`) 내부 의미 미해독, `CADENCE_BOUND` 정량 미확정.
  **다음 middle이 독립 재계산**(M-0 §1.2/§1.3 바이트 재확인 + M-1/M-2 raw jsonl 비참조 재집계)을 해야
  카드가 `CLOSED`된다. Q8/Q9/Q7-B/"8인" 정의는 여전히 사용자 전결 미결.
  `make check` 전체 게이트는 이번 회차 source 변경 0이라 재실행하지 않음(2026-09-20 21:58 면제 규칙,
  직전 lap514/515 819 passed 유지 확인).
- 다음 한 가지: **middle(Opus5.5)이 이 lap516 산출물을 독립 재계산**해 M-0 바이트 주장과 M-2 라벨을
  검수하고, 카드 W31을 `CLOSED`하거나 추가 probe(재무장 스케줄러 추적)를 발행한다.

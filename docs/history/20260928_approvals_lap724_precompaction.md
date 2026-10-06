# APPROVALS lap724 압축 보존 (2026-09-28, lap727 work)

원문 19줄, SHA256 `ee508556786f9d6b1e730598ce97cd152cdaddda7824487ea8866d8ab008df90`.
lap724의 middle 검수 요청 문항은 아직 열려 있다(공식 middle 응답 없음) — 압축은 형식만 줄이고
질문/판정 요구는 아래 포인터에 그대로 남긴다. 전문은 원문 그대로 보존, 삭제·재해석 없음.

---

- [ ] **2026-09-28 lap724 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G5 v5 ALT/Ctrl/Shift
  드래그·부대저장로드·공격 직접 raw 재측정, lap723 미완결 해소):** 02:35 운영자 지시 ①(v5 coverage
  재실행)을 수행. `tools/g5_command_coverage_probe.py`의 목적지 캘리브레이션 루프에 fallback 오프셋
  12개를 추가(방어적, 제품 코드 무관 — 이번 run은 세션이 월드(10,49)로 착지해 기존 7후보만으로
  통과, 미사용)한 뒤 v5로 monkeypatch 재실행 → **COMPLETE**: 이동·정지·홀드·순찰(버튼+단축키) 50/50,
  **ALT/Ctrl/Shift/plain 전체드래그 50/50**(최초 v5 직접측정, 이전엔 v4와 byte-identical이라는
  pytest 추론에만 의존). 같은 방식으로 `g5_candidate_drag_probe.py --ui-roundtrip`(→
  `PASS_UI_ROUNDTRIP`, 7/7 checks True)과 `g5_worker_relative_move_attack_probe.py`(→
  `CONVERGENCE_COMPLETE`, 이동 50/50·표적uid 1기 일치·`ever_command4_count=32/49`, v3/v4 N=5
  분포 24~65% 안 — 회귀 신호 없음)를 v5로 직접 재실행. 크래시 0, `source_unchanged` 3/3,
  candidate SHA 결정론 일치. `make check` **1106 passed(929.16s)**, ruff/mypy/`CONTEXT_PASS`/
  `SAFETY_PASS` 전부 PASS, `bash checks/safety.sh check` PASS. **발견(제품 무관, 안전 위험 아님):**
  attack probe 종료 후 결과 JSON은 `cleanup.xvfb_stopped=true`를 보고했지만 실제로는 그 run이 만든
  `Xvfb`(1600×1200, 시작시각 일치) 2개가 고아로 남아 있어 세션 안에서 발견·수동 `kill`로 정리했다
  (`wine`/prefix 프로세스는 0으로 정상 보고 — 원인 미조사, 다음 work 후순위). **work tier 판단으로
  다음 middle 독립 검수를 요청한다**(이 lap의 raw 3건이 lap717 v4 패턴과 일치하는지 재계산, coverage
  probe 오프셋 확장의 안전성, Xvfb 고아 발견을 안전 위험으로 볼지). 확정되면 다음 work는 체크리스트
  (A) 정적 전수 표·(B) 중간/뒤 엔트리 사망(lap723은 앞쪽 30기만 실측)으로 진행. 근거
  `../history/laps/20260928_lap724_work_g5_v5_direct_coverage_roundtrip_attack.md`.

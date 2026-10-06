# STATUS "다음 한 가지" lap733~734 상세 원문 보존 (선압축)

- 날짜: 2026-09-28
- 보존 사유: docs/STATUS.md 130줄 유지를 위해 lap735가 선압축. 같은 내용이
  `docs/history/laps/20260928_lap733_work_g5_checklist_d_v6_death_recall_fix_pass.md`,
  `docs/history/laps/20260928_lap734_work_g5_v6_core_regression_pass.md`, 그리고 STATUS "바퀴
  기록"에도 남아 있어 이 섹션에서는 중복 제거만 한다(사실 삭제 아님).
- 원문 줄 수: 37
- 원문 SHA256: `c191585808ee452ddefc942919dd72d02cbfb00e31d2f403786b1596e362ff61`
  (추출 파일 `sed -n '80,116p' docs/STATUS.md` 기준, 2026-09-28 lap735 시점)

## 원문

```
**[압축 포인터] lap732 09:05 지시(사망후호출 FAIL→v6 수정 지시)와 lap731 구 "다음 work"(원문 16줄,
SHA256 `ff0e4661acc7abbd08e7b1c87dd1274bdd6f013add05c830233edc0b260d0102`,
`docs/history/20260928_status_lap732_resolved_and_lap731_stale_nextwork_precompaction.md`에 보존)
— 둘 다 아래 lap733로 해소.**
**2026-09-28 lap733 판정(이 세션): (D) 부대원 사망 후 호출 = v6로 수정 완료, PASS.** 09:05 운영자
승인에 따라 disasm 진행: 보호 원본에서 `FUN_00445E30`(recall) 레거시 20칸 루프가 H3와 동일한
`unit+0x31C`(`FUN_0040F790`) 게이트를 쓰는 것, `FUN_00409C70`(사망)가 `FUN_00445A90` 한 번으로만
그룹 배열을 정리하고 `unit+0x344` 오버플로 멤버는 그 검색 대상이 아닌 것을 확인. 정확한 단일
근본원인(2단계 재배정 재정렬 vs 엔진 비동기 사망정리 타이밍)은 끝내 확정 못 했으나, 원인 불문으로
안전한 수정을 특정: `patches/selection/g5_selection_cap50_v6.py` 신규 H4 훅
(`0x00409CB8` 5바이트만 교체, 새 캐이브 `0x004E4F90..0x4E4FFA`) — `FUN_00445A90` 호출 뒤 죽은
유닛 자신의 `unit+0x344`가 유효 그룹이면 **그 그룹 하나의 20칸만 slot(저word)만으로** 재검색해
지우고 `FUN_0040F750(slot,-1)`로 강제 클리어. v6=v5+이 훅만(나머지 전체 byte-identical, 테스트로
고정). 같은 시나리오(41명 중 10명 사망) 재실행 → **`recall_ok=true`, 유령 0, 생존31/31 정확**.
`make check` 1111 passed(776.51s, v6 pytest 5개 포함), `SAFETY_PASS`, 크래시0,
`source_unchanged`. 상세
`docs/history/laps/20260928_lap733_work_g5_checklist_d_v6_death_recall_fix_pass.md`.
**2026-09-28 lap734 판정(이 세션): 10:06 지시 ① v6 핵심 회귀 = 전부 PASS, 실측 재확인 완료.**
기존 coverage/attack/roundtrip/R3 probe를 v6로 monkeypatch(모듈 `g5`/`TARGET_SHA` 임시 스왑,
lap682/717/723/724 선례와 동일 방식, `tools/*.py` 무변경)해 원본 1회 대조 + 후보 v6 실측:
드래그 4종(plain/ALT/Ctrl/Shift) 50/50, 지면 이동(버튼+우클릭) 50/50, 정지·홀드·순찰(버튼+단축키)
50/50, 더블클릭 같은종류선택 50/50, 51번째 거부(56 fixture 중 정확히 50 선택), Shift+클릭
추가/제거 toggle PASS. 부대 roundtrip(Ctrl+숫자 지정→해제→호출→저장→로드→호출)
`PASS_UI_ROUNDTRIP` 7/7 checks. R3 사망-후-명령(front/middle/rear 3 시나리오 전부)
`PASS_NO_SPARSE_GAP`, `structural_ok=true`, 누락 슬롯 0. 공격은 pending-word 기준(lap689 인정
지표) 원본 6~17/19·후보 22~27/49로 기존 v3~v5 변동폭과 같은 패턴(회귀 신호 없음, 단일측정이라
확정 아님). 크래시 0, `source_unchanged` 전 실행 true(두 원본 exe 경로 모두 SHA 재확인),
`cleanup.prefix_processes_after=[]` 전부. `tools/g5_r3_sparse_selection_probe.py`에
`candidate-v6` variant 1개만 추가(제품코드 아님, 이전 v4→v5 추가와 동일 패턴). `make check`
1111 passed(772.33s), ruff/mypy/`CONTEXT_PASS` PASS, `checks/safety.sh check`: `SAFETY_PASS`.
**미착수:** 10:06 지시 ② 건설 재판정(설명서·다른 국가·하위 페이지·단축키)과 특수능력 원본20/v6 50
paired — 08:15 지시가 이미 "존재 확인만으로 PASS 불가, 국가별 랜덤이라 재판정 필요"로 지적한
마일스톤 경계 항목이라 이번 세션 안에 안전하게 끝내지 못했다(시간 예산). **다음 work 최우선:** ②
건설 재판정 + 특수능력 paired 측정. 끝나면 (E) UI(50기 초상화/정보패널·HUD·체력바) → (F)
저장로드 → (G) 멀티 → (H) 장시간. middle 독립 검수는 체크리스트 전체(A~H) 완료 후 한 번에
한다(2026-09-28 03:36 운영자 판정, 유지). 체크리스트 A~H 원문은 `docs/feedback/APPROVALS.md`의
2026-09-28 01:31 사용자 지시 항목을 참조한다.
```

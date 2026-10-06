# STATUS 바퀴 기록 lap731~733 원문 보존 (선압축)

- 날짜: 2026-09-28
- 보존 사유: docs/STATUS.md "바퀴 기록" 섹션 130줄 유지를 위해 lap735가 선압축.
- 원문 줄 수: 16
- 원문 SHA256: `df769eac0a9fe2afa798d5072db817e919cc44aec66ce8a8318bff2de67b4cd1`
  (추출 파일 `sed -n '121,136p' docs/STATUS.md` 기준)

## 원문

```
- lap733(work, 이 세션): (D) 잔여 부대원 사망 후 호출을 disasm+v6 훅으로 수정 — `FUN_00445A90`
  호출 뒤 죽은 유닛 자기 그룹 20칸만 slot-only 재검색+강제 `+0x344=-1`. 같은 시나리오 재실행
  `recall_ok=true`(유령0, 생존31/31). **(D) 전체 완료, 기준 후보 v5→v6 교체.** `make check`
  1111 passed(776.51s), `SAFETY_PASS`, 크래시0. 핵심 회귀는 v6로 미재확인(다음 work 권장). 상세
  `docs/history/laps/20260928_lap733_work_g5_checklist_d_v6_death_recall_fix_pass.md`.
- lap732(work, 이 세션): 체크리스트 (D) 잔여 측정 — Shift+숫자 추가는 완료(원본·v5 둘 다 "Shift+
  숫자" 무반응 확인·미지원 판정, 대안 메커니즘 PASS), **부대원 사망 후 호출은 후보 v5 신규 FAIL**
  (41명 중 10명 사망 후 호출 시 6명 유령 재선택, 원본은 PASS) → (D) 미완료, `loop/ESCALATE_SOL`
  lap732 섹션에 승격. `make check` 결과는 상세 lap 참고. 상세
  `docs/history/laps/20260928_lap732_work_g5_checklist_d_shift_add_death_recall.md`.
- lap731(work, 이 세션): 체크리스트 (C) 잔여(건설/특수능력·변신/승선하선/좌표일치) 조사 완료 —
  건설·승선하선 N/A, 특수능력 존재확인, 좌표일치는 기존 증거로 PASS → **(C) 전체 완료**. (D)는
  lap724 v5 roundtrip으로 절반 기완료 확인, 잔여 Shift+숫자·사망후호출만 남음. `make check`
  1106 passed(755.21s), `SAFETY_PASS`, 크래시0, `source_unchanged` 2/2, 제품코드 무변경. APPROVALS
  선압축(261→164줄). 상세
  `docs/history/laps/20260928_lap731_work_g5_checklist_c_construction_ability_embark_survey.md`.
```

lap731의 "(C) 전체 완료" 판단은 2026-09-28 08:15 운영자 판정으로 부분 반려(건설 N/A 의심,
특수능력은 존재확인만으로 PASS 불가)됐다 — 이 사실은 압축하지 않고 STATUS 본문에 유지한다.

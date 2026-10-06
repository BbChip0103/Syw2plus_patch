# STATUS 바퀴 기록 lap736~737 원문 보존 (선압축)

- 날짜: 2026-09-28
- 보존 사유: docs/STATUS.md "바퀴 기록" 섹션 130줄 유지를 위해 lap738이 선압축.
- 원문 줄 수: 13
- 원문 SHA256: `8a2a46fd976868c0368fccf1fa09967c8b20c600310caf80aabf529573c28334`
  (추출 파일 `sed -n '93,105p' docs/STATUS.md` 기준, lap738 편집 직전)

## 원문

```
- lap737(work, 이 세션): (C) 잔여 "v"/"i" 특수능력 유효 타겟 탐색 → (C) 완료 선언. 신규
  `tools/g5_ability_target_search_probe.py`(button-only 자가발동 + gather식 지면 오프셋 탐색,
  `wait_settle`로 오탐 방지). "i"는 원본(worker7)·후보v6(worker21) 둘 다 지면(0,6) 우클릭으로 lone
  worker 발동 확인되지만 2~3기 선택만으로도 무반응 — 솔로 전용 능력 판정(N/A). "v"는 3개국
  (worker7/21/31) 전부 무반응 — UNKNOWN 유지(원본도 0, v6 회귀 아님). 크래시0(5회 boot),
  `source_unchanged` 전부. `make check` 1111 passed(818.64s), `SAFETY_PASS`. 상세
  `docs/history/laps/20260928_lap737_work_g5_checklist_c_ability_target_search_complete.md`.
- lap736(work, 이 세션): 08:15 지시 ① 건설 재판정 — 설명서 3종 확인(건물배치 텍스트 없음) + 신규
  `tools/g5_construction_new_nation_survey_probe.py`로 재부팅 16회(4 타이밍 라운드) 실행, 솔로 로비
  국가 풀이 3개(worker7/21/31, HQ49/58/70)로 수렴함을 확인, 세 번째 국가(worker7/HQ49)의 워커·HQ
  그리드 전 버튼에서도 신규 existence 슬롯 0(건설 버튼 없음, lap731과 동일 결론). 크래시0(16/16),
  `make check` 1111 passed(920.81s), `SAFETY_PASS`. 상세
  `docs/history/laps/20260928_lap736_work_g5_construction_third_nation_survey.md`.
```

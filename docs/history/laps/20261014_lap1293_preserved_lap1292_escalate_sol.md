# lap1292 work → Sol/root: H-G1ON2614 raw 충돌 확인 후 work 배정

## 승격 사유
현재 STATUS의 다음 단계가 root/Sol의 lap1291 raw 충돌 확인과 work 수리 배정이다. lap1291의 상위 결과는 480초 PASS지만 같은 raw trace는 event_limit 포화, 10,932 drop, PS3 관측 183.474초 뒤 PS29 패배를 보여 실질 충돌이 있다. work가 이를 마감하거나 middle 검수를 대신하지 않는다.

## 보존된 근거
- 상세 판정: `docs/history/laps/20261014_lap1291_middle_g1_winmm_raw_conflict.md`
- root handoff 원문: `docs/history/laps/20261014_lap1291_root_escalate_sol_g1winmm_hold.txt`
- 현재 큐/블로커: `docs/STATUS.md`
- raw: `../temp/Syw2plus_patch/20261014_lap1289_g1on2614_soak1/`; 독립 계산: `../temp/Syw2plus_patch/20261014_lap1291_middle_g1_winmm_review/review.json`

## Sol/root가 확인하고 work에 배정할 범위
1. raw 요약과 결과 결합의 충돌을 확인하고 480초 수용은 HOLD로 유지한다.
2. 명시적 work 배정 후 `tools/g1_esl2614_display_probe.py`의 결과 결합/soak 판정, 필요한 `tools/g1_saved_scene_probe.py` 상태·시간 관측, `tools/esl2614_runtime.py` 입력 경로 대응 및 관련 회귀만 최소 수정한다. trace 예산 수정도 이 실행의 관측을 막는 부분에 한정한다.
3. 보존 raw가 재현 회귀로서 상위 PASS가 될 수 없음을 확인하고, 실패 soak 경로만 격리 재실행한다. 중간 패배·관측 부족은 부분 결과로 남기며, 완전한 480초 active coverage가 없으면 안정성 PASS를 주장하지 않는다.
4. 현재 2614 원본은 `../[ESL]Syw2plus - ESL2614/[ESL]Syw2plus/` 아래 중첩돼 있다. EXE SHA 확인은 유지하고 원본을 이동/수정하지 않는다.

## 범위와 금지
기존 4 display lane, DLL/EXE SHA, raw, 후보, 게임/prefix는 보존·재사용한다. 전체 `make check`는 전달 후보 고정 전 실행하지 않는다. MCI 0-call, Windows/사용자 시험, 2614 자체 save roundtrip 및 G1 사용자 마일스톤은 미확인이다. G5는 INBOX 지시에 따라 별도 세션 담당이다. 이번 lap에서 코드·게임·후보·전달·커밋 변경은 없다.

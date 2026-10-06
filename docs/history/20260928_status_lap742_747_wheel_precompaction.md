# STATUS.md "바퀴 기록" lap742~747 원문 보존 (lap748 압축)

원문 36줄, SHA256 `03526ad7a637d6b4a416176820dd60c1959eb9dde49788153f17eb3f2feb459e`.
lap748이 `docs/STATUS.md`의 "## 바퀴 기록" 섹션에서 lap742~747 항목을 이 파일로 옮기고
포인터로 대체했다. 아래는 원문 그대로(삭제·재해석 없음).

---

- lap747(work, Sonnet5): (레거시 버그) `g5_candidate_drag_probe.py`/`g5_stale_tail_probe.py`의
  고정-파일명 source-exe 조회가 `[ESL]Syw2plus/`에서 깨지던 것을 `runtime_env.validate_original_
  source`(SHA 기반) 재사용으로 수정. **S3**: 확인 대화상자 버튼 좌표 정밀 확정((419,329)/(484,329)),
  클릭은 정상 등록되나 메인 메뉴로 가지 않고 즉시 게임 복귀 — 원본도 동일 재현(패치 무관), 18:35
  지시로 대체 경로(다시하기/불러오기/fixture-free) 조사로 이관, 미해소. **v8 핵심 회귀**: 드래그4종/
  이동/정지/순찰/더블클릭/Shift/51번째거부/그룹roundtrip 전부 PASS. **홀드버튼**: candidate 3회
  0/50→50/50→3/50 요동, 원본 3회 20/20 고정, 단축키는 candidate도 50/50 안정 — 미해결. 게임 실행
  11회 크래시 0, `make check` 1115 passed·5 skipped, `SAFETY_PASS`. 제품 코드 0 변경. 상세
  `docs/history/laps/20260928_lap747_work_g5_s3_menu_exit_inconclusive_v8_core_regression_pass.md`.
- lap746(work, Sonnet5): H-STALE-TAIL 런타임 최초 재현(신규 `tools/g5_stale_tail_probe.py`) — 원본
  PASS, v7 FAIL(불변식 붕괴·명령 유출 30건·해제 후 count=-30·그 상태 저장 시 게임 무한정 정지+
  플레이어 데이터 0화), **v8**(`LOAD_WRAPPER` zero-fill 20→50, v7과 1바이트 diff)로 PASS 확인.
  pytest 17 passed, `make check` 1115 passed·5 skipped, `SAFETY_PASS`·`CONTEXT_PASS`. S3(메인메뉴
  이월)는 좌표 미확정으로 `INCONCLUSIVE`. 제품 코드 변경 v8 1바이트, 원본 0 변경. 상세
  `docs/history/laps/20260928_lap746_work_g5_checklist_f_h_stale_tail_runtime_confirmed_v8_fix.md`.
- lap745(middle, Opus5): G5 A~H 전체 독립 재검수 — v7 재빌드 SHA `30efafa0…` 일치, v6→v7 17구간
  (`.rsrc` 헤더+콜사이트2+캐이브)·v5→v6 10구간 범위 확인, G5 pytest 53 passed·`SAFETY_PASS`·
  `CONTEXT_PASS`, F/H raw 재계산 일치. **HOLD**: F에 H-STALE-TAIL(정적) 발견, H의 `moving_count`는
  `command!=0` 계수라 명령별 전달 증거 아님(안정성 PASS는 유지). APPROVALS 293→압축(원문 보존).
  제품 바이트 0 변경·게임 실행 0회. 상세 `docs/history/laps/20260928_lap745_middle_g5_a_h_independent_review_hold_stale_tail.md`.
- lap744(work, Sonnet5): 신규 실행/변경 0 — A~H 채워짐 확인 후 middle 재검수로 승격(`loop/ESCALATE_SOL`).
- lap743(work, 이 세션, 2건): **(H)** 신규 `tools/g5_long_run_stability_probe.py`로 v7 50기
  드래그 선택 → 이동/정지/보류/순찰 6단 명령 13회 주기 반복 → 8019 tick(목표 8000 초과) 동안
  crash 0·선택회귀 0(387샘플 전부 50/50), 최종 선택이 초기와 완전 동일, 후보 SHA가 lap740 기록과
  일치(빌드 재현성). `make check` 1116 passed(862.74s) 전부 PASS. **(G)** 16:35 지시(마지막 1회
  시도) 수행 — lap742 로그 재검토로 새 가설(네이티브 SP DLL을 `<prefix>/system32`에도 배치하면
  dplayx의 내부 system32 조회도 네이티브를 찾을 것) 도출·검증, **2개 조합 모두 PS9 도달 전 조기
  종료로 반증**(오히려 더 이른 실패). `ipxconfig.exe`(CLI 없음, GUI 전용 확인)는 SP 로드가 먼저
  실패하는 구조상 착수하지 않음. **(G) `BLOCKED(env: native ipxwrapper crashes on room creation,
  wine9.0)` 최종 확정**(누적 4조합 실패). `game` 사본(각 581MB) 실행 직후 삭제(prefix/output/
  manifest 보존). 제품 코드 0 변경, 신규 pytest 0개(H 도구 1개만 저장소에 추가). **체크리스트
  A~H 전부 채워짐.** 상세
  `docs/history/laps/20260928_lap743_work_g5_checklist_h_long_run_stability_pass.md`,
  `docs/history/laps/20260928_lap743_work_g5_checklist_g_final_attempt_blocked_confirmed.md`.
- **[압축 포인터] lap742**(G 멀티 IPX 크래시 첫 재현, `WINEDEBUG` 근본원인 확정)는 lap743의 최종
  `BLOCKED` 확정에 흡수됨 — 상세 `docs/history/laps/20260928_lap742_work_g5_checklist_g_multiplayer_ipx_crash_blocked.md`.

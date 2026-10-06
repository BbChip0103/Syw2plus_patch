# APPROVALS lap746~749 work tier 정보제공 계보 원문 보존 (2026-09-29, lap759 압축)

SHA256 `4a80650d6f7132ba4ce203921496d682b01f84f1337b67fec2af054def158db0`(원문 38줄)

- [ ] **lap749 work tier 정보제공(middle 독립 검수 아님):** 홀드버튼 편차 근본 원인 — `hold_button`
  관측 윈도우를 3.0→10.0초로 늘려 candidate v8 3회 재측정. **3회 전부 `pending_changed_to` 50/50**
  (원본 lap747 3회 20/20 고정과 정합). curve 분석: 목표 pending 값은 클릭 직후 한 샘플(10ms)에서만
  나타났다 바로 처리완료 상태로 정착하는 진짜 transient — 50기 규모의 청크 재발행 완결 시간이 실행마다
  3초 창을 넘나든 것으로 설명됨. STATUS/INBOX가 미리 적어둔 판정기준("매번 50/50 도달=타이밍
  아티팩트, 회귀 아님")을 충족. 제품 코드 0 변경(도구 `hold_button` 윈도우값 1줄만), `source_unchanged`
  3/3, 크래시 0. `make check` 1115 passed·5 skipped(759.22s), `SAFETY_PASS`/`CONTEXT_PASS`. **S3
  대체경로(lap748)·홀드버튼(이번 lap) 둘 다 해소돼 G5 (F) v8 최종 재검수를 막던 work tier 항목이
  더 없다 — middle이 v8 기준 A~H 전체 최종 독립 재검수를 할 차례.** 상세
  `docs/history/laps/20260928_lap749_work_g5_hold_button_window_timing_artifact_confirmed.md`.
- [ ] **lap748 work tier 정보제공(middle 독립 검수 아님):** 18:35 지시 ① S3 대체 경로 — S4('다시하기'
  재시작)·S5('불러오기' 다른 판 로드, fixture 이전 baseline 세이브를 host-side 파일 복사로 보존)를
  `tools/g5_stale_tail_probe.py`에 추가하고 원본/v8candidate 각 1회 paired 실행(v8은 Escape 타임아웃
  1회 재시도 후 성공). **둘 다 PASS**: 원본 tick 235→5(재시작), v8 tick 224→2(재시작) 후 선택배열
  count=0·전칸0; 원본/v8 둘 다 baseline 로드 후 count=0·전칸0·stale-tail 칸 0·잔류 명령 0. v8의
  H-STALE-TAIL 수정(lap746)이 같은-세이브 재로드(S1)뿐 아니라 재시작·다른-세이브 로드 경로에도
  유효함을 처음 확인했다. S3(초기메뉴) 자체는 원본도 동일하게 막혀 있다는 lap747 결론은 그대로이며,
  fixture-free 순정 로비 재시도는 미착수(낮은 우선순위, (F) 판정에 영향 없음). 남은 유일한 (F)
  블로커는 홀드버튼 편차(lap747, 미해결). `make check` 1115 passed·5 skipped(785.44s),
  `SAFETY_PASS`. 제품 코드 0 변경(도구만). **middle이 (F) v8 최종 재검수 전 홀드버튼 편차 해소
  필요.** 상세 `docs/history/laps/20260928_lap748_work_g5_s3_alt_paths_restart_load_different_pass.md`.
- [ ] **lap746 work tier 정보제공(middle 독립 검수 아님):** H-STALE-TAIL 런타임 최초 재현 —
  원본 `PASS_NO_STALE_TAIL_EFFECT`, v7 `FAIL_STALE_TAIL_CONFIRMED`(불변식 붕괴·명령 유출 30건·
  해제 후 count=-30·그 상태 저장 시 게임 무한정 정지+플레이어 데이터 0화), v8(1바이트 수정)로
  `PASS_NO_STALE_TAIL_EFFECT`. S3(메인메뉴 이월)는 좌표 미확정으로 `INCONCLUSIVE`. **middle이
  (F)를 v8 기준 독립 재검수할 때까지 사용자 milestone 제출 대상 아님.** 상세
  `docs/history/laps/20260928_lap746_work_g5_checklist_f_h_stale_tail_runtime_confirmed_v8_fix.md`.
- [ ] **lap747 work tier 정보제공(middle 독립 검수 아님):** S3 확인 대화상자 버튼 좌표를 픽셀분석으로
  정밀 확정((419,329)="확인"/(484,329)="취소")하고 실행했으나, 정확한 "확인" 클릭도 메인 메뉴로
  가지 않고 즉시 게임으로 복귀 — **원본(무패치)도 완전히 동일하게 재현**돼 v8/G5 패치 결함이
  아니라 probe 환경 또는 원본 고유 제약으로 판단(단, 18:35 운영자 지시로 "환경 제약 종결"이 아니라
  다시하기/불러오기/fixture-free 대체 경로 조사로 계속 열어둠, 다음 work). v8 핵심 회귀(드래그4종·
  이동·정지·순찰·더블클릭·Shift·51번째거부·그룹roundtrip)는 실측 PASS. **홀드 "버튼"만 원본 3회
  20/20 고정 대 v8 3회 0/50→50/50→3/50 요동**(홀드 단축키는 v8도 3회 전부 50/50 안정) — 원인
  미확정(청크분할 타이밍 추정), 회귀 여부 다음 work가 판정. 게임 실행 11회 크래시 0,
  `make check` 1115 passed·5 skipped, `SAFETY_PASS`. 제품 코드 0 변경(도구 코드만 source-resolution
  레거시 버그 수정). **middle이 (F) v8 최종 재검수 전 S3 대체경로·홀드버튼 해소 필요.** 상세
  `docs/history/laps/20260928_lap747_work_g5_s3_menu_exit_inconclusive_v8_core_regression_pass.md`.

# STATUS — 매 바퀴 갱신하는 기억

lap676~741 상세(과거 압축 포인터, G5 milestone 승인 이력, G2 8인×10000 A/B 종료, G4 W2 post-load
종결, G5 A~F 체크리스트 완료 근거 전문 — 정적 표/사망 시나리오/Shift 제거/51번째 거부/더블클릭/
채집·수리/건설 N/A/특수능력 측정/부대지정·호출·저장로드/UI 확인/save-load v7 수정, (G) 멀티
Wine-stub BLOCKED 1차 판정)은 이 헤더 블록 152줄 SHA256
`11688804945df9fbd3f10e8df6f19d08b0f1ab4872dfca59d2f66fc33807b453`으로
`docs/history/20260928_status_lap717_741_precompaction_v2.md`에 원문 그대로 보존했다(과거
lap676~716분은 그 파일이 가리키는 `docs/history/20260927_status_lap717_precompaction.md`에
한 단계 더 있다). 각 lap 전체 근거는 `docs/history/laps/20260926_lap67{6..9}_*.md`·
`lap68{0..9}_*.md`·`20260927_lap69{5..9}_*.md`·`lap70{0..9}_*.md`·`lap71{0..6}_*.md`·
`20260928_lap7{17..41}_*.md`에 그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 승인됐으나, 2026-09-28 01:31 사용자
지시로 승인이 조건부로 되돌아갔다** — A~H 완료 체크리스트 전부 PASS해야 G5 종료. **A~F는
완료(기준 후보 v7, 근거는 위 압축 포인터). G(멀티 2인 LAN 명령 동기화) = lap742에서 `BLOCKED`로
확정(아래). H(장시간) = lap743에서 `PASS`(아래).** lap745 middle 전체 재검수 = `HOLD(조건부)`였다:
B·C·D·H PASS, G `BLOCKED(env)` 수용, E 조건부, F는 H-STALE-TAIL 미검증으로 보류. **lap746 work가
S1~S3 paired 런타임 probe로 H-STALE-TAIL을 최초로 실제 재현(v7: count/비0칸 불변식 붕괴, 로드밖
30유닛 명령 유출, 해제 후 count=-30, 그 상태 저장 시 게임 무한정 멈춤+플레이어 데이터 0화)하고
**v8**(`LOAD_WRAPPER` zero-fill 폭 20→50, v7과 정확히 1바이트 diff)로 수정 — 원본 paired 재실행
결과 `PASS_NO_STALE_TAIL_EFFECT`.** **lap747 work가 S3 좌표를 픽셀분석으로 확정하고 실행 — "초기메뉴"
확인 대화상자의 "확인" 버튼을 정확히 클릭해도 메인 메뉴로 가지 않고 즉시 게임으로 복귀하는 현상을
발견했으나, 원본(무패치) 대조군도 완전히 동일하게 재현돼 v8/G5 패치와 무관한 probe 환경/원본 고유
제약으로 결론**(S3는 이 하네스로 검증 불가, F 판정에는 영향 없음). v8 핵심 회귀(드래그4종·이동·
정지·순찰·더블클릭·Shift·51번째거부·그룹roundtrip)도 실측 PASS. 단 **홀드 "버튼"(단축키 아님) 클릭만
후보 3회에서 0/50~50/50 편차** — 홀드 단축키(`H`)는 3회 전부 50/50 안정이라 probe 타이밍 아티팩트로
잠정 추정하나 미확정(원본 1회만 측정). **lap747이 원본 홀드버튼 3회 재확인(20/20 고정, v8은 0/50~50/50 요동, 미해결) 완료. lap748이 18:35
지시 ①(S3 대체 경로: 다시하기/불러오기)을 처리 — 원본/v8 각 1회 paired로 재시작(S4)·다른 판 로드(S5)
둘 다 `PASS`(선택 이월 없음, 잔류 명령 0), v8 H-STALE-TAIL 수정이 같은-세이브 재로드뿐 아니라 이
두 경로에도 유효함을 확인. S3(초기메뉴) 자체는 여전히 원본도 동일하게 막혀 미시도(fixture-free
재시도는 미착수). **lap749 work가 `hold_button` 관측 윈도우를 3.0→10.0초로 늘려 candidate v8을
3회 재측정 — 3회 전부 `pending_changed_to` 50/50 도달(원본 20/20 고정 패턴과 정합). curve 분석상
목표값은 클릭 직후 한 샘플(10ms)만 나타났다 처리완료 상태로 정착하는 진짜 transient라, 50기 규모의
청크 재발행이 3초 창을 넘기는 경우가 있었던 것으로 설명됨 — 운영자 판정기준("매번 50/50 도달=
타이밍 아티팩트") 충족, 회귀 아님으로 결론.** **lap750 middle(Opus5) v8 최종 재검수 = `HOLD(좁은 조건부)`: 재빌드
`ef46d1ac…`·v7→v8 1바이트 확인, 홀드버튼 PASS(원인은 클릭→첫 샘플 race로 정정), lap748 S5는 선택0
상태에서 실행돼 공허, S3 새 게임 이월은 여전히 실제 위험 — 1 work lap 필요(아래).** **lap751 work가 그
1 lap을 처리 — ① v7로 "드래그→다시하기→50칸 dump"(저장/로드 없이) 실행 결과 `RESTART_DUMP_TAIL_
CLEARED`(재시작은 좁은 `LOAD_WRAPPER`가 아니라 유닛 해체(dec) 경로로 tail 전부 0), ② fixture/선택이
전혀 없는 순정 로비 직후에도 "초기메뉴"가 원본·v8 둘 다 메인 메뉴로 못 가고 즉시 게임 복귀
(`MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`, fixture 무관 환경 제약 확정). 핸드오프의 v9 트리거
조건("①이 로드 경로이고 ②가 불가")이 성립하지 않아 v9 미착수, 제품 코드 0 변경. S3는 여전히 실측
불가(`BLOCKED(env)`)이나 재시작=해체경로 analogy로 위험이 낮아졌다는 정성 판단만 남음 — middle이 F를
최종 재검수할 차례.**

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료, 착수 대기(G5 이후) | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(근거 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류(길찾기 종료, 생산게이트 계측 완료) | candidate AI 정책 없음, 사용자 승인 |
| G5 | v8, lap751 work: S3 귀속 실험 완료(재시작=해체경로 확정, 메뉴제약=fixture 무관 env 확정, v9 불필요 판정) | middle F 최종 재검수, 사용자 milestone |

## 지금 막힌 것 (Blockers)

**G5 (F) S3(초기메뉴→새 게임 선택 이월) 여전히 실측 불가(`BLOCKED(env)`) — middle 최종 판단 대기.**
lap751이 재시작(다시하기) 초기화 주체를 귀속(`RESTART_DUMP_TAIL_CLEARED`, v7에서도 tail 전부 0 →
유닛 해체(dec) 경로, 좁은 `LOAD_WRAPPER` 아님)했고, "초기메뉴" 메인 메뉴 전환 자체가 fixture/선택
유무와 무관하게 이 하네스/원본에서 항상 막힘을 확인했다. 새 게임 시작이 재시작과 같은 초기화 함수를
타는지는 유추일 뿐 정적으로 확인하지 않았다 — middle이 이 정도 증거로 F를 PASS/HOLD 중 무엇으로
판정할지 다음 한 가지.
(G) 멀티는 `BLOCKED(env: native ipxwrapper crashes on room creation, wine9.0)` 수용(lap742/743).

world (93,56)의 `long_distance_pan` 카메라-복귀 결함은 여전히 후순위 미해결(lap711). world
(10,49)를 baseline으로 계속 쓴다.

## 검증 상태

**[압축 포인터] lap717~737 검증 상태 계보는 위 헤더 압축 파일에 보존.** 매 lap `make check` PASS·
`SAFETY_PASS`·크래시0(제품 EXE 기준)·`source_unchanged`. lap742/743은 제품 코드 0 변경(진단
스크립트는 `/tmp`+공유 `temp/Syw2plus_patch/`에만 존재), 관측된 게임 조기종료/크래시는 원본
미변경 EXE 자체의 환경 반응(override 조합 결과)이며 회귀가 아니다. lap743 (H)
`make check` **1116 passed(862.74s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS,
`source_unchanged=true` 3/3(H 1회 + G 최종시도 2회). **lap746**: 원본 paired
`PASS_NO_STALE_TAIL_EFFECT`, v7 `FAIL_STALE_TAIL_CONFIRMED`(재현 2/2, 2회차에서 count=-30 저장 시
게임 무한정 정지+플레이어 데이터 0화까지 확인), v8 `PASS_NO_STALE_TAIL_EFFECT`. 신규 pytest
17 passed, `make check` **1115 passed, 5 skipped(823.25s)**, ruff/compileall/mypy/`CONTEXT_PASS`/
`SAFETY_PASS` 전부 PASS, `source_unchanged` 4/4. 제품 코드 변경은 v8 1바이트뿐(원본 0 변경).
**lap747**: 게임 실행 11회(원본 4·candidate 7) 전부 `source_unchanged=true`·크래시 0. 드래그4종/
이동/정지/순찰/더블클릭/Shift/51번째거부/그룹roundtrip(PASS_UI_ROUNDTRIP, checks 7/7) 전부 PASS,
공격/R3/death-recall은 v7→v8 1바이트 diff 범위 밖이라 재실행 생략(정적 논거). 홀드버튼 원본3회
20/20 고정 대 candidate3회 0/50~50/50 요동(단축키는 candidate도 50/50 안정) — 미해결. S3는 원본도
동일 재현되나 18:35 지시로 대체 경로 조사 이관. `make check` 1115 passed·5 skipped(1035.53s),
`SAFETY_PASS`·`CONTEXT_PASS`. 제품 코드 0 변경(도구 코드 2개 파일만 source-resolution 버그 수정).
**lap748**: `tools/g5_stale_tail_probe.py`에 S4(다시하기)·S5(불러오기 다른 판) 추가, 원본·v8 각 1회
paired(v8은 Escape 타임아웃 1회 재시도 후 성공) — 둘 다 `S4_PASS_SELECTION_CLEARED`·
`S5_PASS_NO_CARRYOVER`(count=0·전칸0·stale-tail 칸 0·잔류 명령 0), 전체 `status=
PASS_NO_STALE_TAIL_EFFECT` 유지. 크래시 0, `source_unchanged` 3/3. `make check` 1115 passed·
5 skipped(785.44s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 제품 코드 0 변경(도구 코드만).
**lap749**: `hold_button` 관측 윈도우 3.0→10.0초로 확장 후 candidate v8 3회 재측정 — 전부
`pending_changed_to` 50/50, curve상 목표값은 한 샘플(10ms)만 나타났다 처리완료 상태로 정착하는 진짜
transient로 확인(50기 규모 청크 재발행이 3초 창을 넘기던 것으로 설명됨). `make check` 1115 passed·
5 skipped(759.22s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 제품 코드 0 변경(도구 1줄만).
**lap750(middle)**: v7/v8 재빌드 SHA 일치·`cmp` 1바이트, G5 v7/v8 pytest 9 passed, `make check` 1115
passed·5 skipped(868.05s)·ruff/mypy/`CONTEXT_PASS`, `SAFETY_PASS`. 게임 실행 0(raw 재계산만).
**lap751**: `tools/g5_stale_tail_probe.py`에 `--restart-dump-only`·`--menu-exit-fresh` 게이트 2개
추가(기존 S1~S5 분기 무변경). v7 restart-dump-only → `RESTART_DUMP_TAIL_CLEARED`. 원본·v8
menu-exit-fresh(fixture 이전) → 둘 다 `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`. pytest
(v7/v8) 9 passed, `make check` 1115 passed·5 skipped(783.17s), ruff/mypy/`CONTEXT_PASS`,
`SAFETY_PASS`. 3회 실행 전부 `source_unchanged=true`·`cleanup.ok=true`. 제품 코드 0 변경.

## 다음 한 가지
**middle(2단): v8 기준 G5 (F) 최종 재검수.** lap751이 ①②를 완료했다: 재시작(다시하기)은 유닛 해체
(dec) 경로로 tail을 완전히 비운다(`RESTART_DUMP_TAIL_CLEARED`, v7에서도), "초기메뉴" 메인 메뉴 전환은
fixture/선택 유무와 무관하게 원본·v8 둘 다 막힌다(`MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`). v9 트리거
조건 미성립으로 v9 미착수. middle은 이 analogy(재시작=해체경로 → 새 게임도 같은 해체를 탈 가능성)를
S3 `BLOCKED(env)` 수용 근거로 쓸지, 아니면 재시작 핸들러와 새 게임 초기화가 같은 함수를 호출하는지
정적 대조(gdb 워치포인트/xref)까지 요구할지 판정한다. PASS 처리 시 알려진 제한(G 멀티 BLOCKED, 부대
미지정 선택 로드 후 20기, 미니맵/능력 v UNKNOWN, 건설·승선 N/A, S3 BLOCKED(env)+analogy, S5 정적 귀속)을
명시해 사용자 milestone 재상정 여부를 정한다. 상세
`docs/history/laps/20260928_lap751_work_g5_s3_restart_attribution_menu_exit_env_confirmed.md`.

## 바퀴 기록

- lap751(work, Sonnet5): lap750 핸드오프 ①②를 처리. probe에 `--restart-dump-only`·`--menu-exit-fresh`
  게이트 2개 추가(기존 흐름 무변경). ① v7 restart-dump-only = `RESTART_DUMP_TAIL_CLEARED`(재시작은
  해체(dec) 경로, 로드 경로 아님). ② 원본·v8 menu-exit-fresh(fixture 이전) 둘 다
  `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`(환경 제약, fixture 무관 확정). v9 트리거 미성립으로
  v9 미착수. pytest 9 passed, `make check` 1115 passed·5 skipped, `SAFETY_PASS`. 제품 코드 0 변경.
  다음은 middle F 최종 재검수. 상세
  `docs/history/laps/20260928_lap751_work_g5_s3_restart_attribution_menu_exit_env_confirmed.md`.
- lap750(middle, Opus5 `claude-opus-5-5`/high): v8 기준 A~H 최종 재검수 = **HOLD(좁은 조건부)**. 재빌드·
  바이트·pytest·`make check` 일치. 홀드버튼 raw 재계산: 0/50·3/50은 클릭 후 첫 샘플 전에 transient가
  끝난 race(lap749 "청크 3초 초과" 설명은 raw 불일치, 결론 PASS 유지). S5 raw는 selection_before=0이라
  공허, S3는 새 배열 초기화 귀속 없음 → 실제 위험. 문서만 변경. 상세
  `docs/history/laps/20260928_lap750_middle_g5_v8_final_review_hold_s3_s5_gap.md`.
- **[압축 포인터] lap748·749 바퀴 기록**(S4/S5 추가·홀드버튼 창 10초 재측정, 원문 14줄)은 STATUS 전문
  133줄 SHA256 `c78e95ba20fb4c1b790bf549ce070ce3b5885bc09ade885333ded605eeb75431`과 함께
  `docs/history/laps/20260928_lap750_status_precompaction.md`에 원문 그대로 보존했다.
- **[압축 포인터] lap742~747 바퀴 기록**(S3 좌표 확정·INCONCLUSIVE, v8 핵심회귀 PASS, 홀드버튼 편차,
  H-STALE-TAIL 런타임 재현·v8 수정, middle A~H HOLD, (G) BLOCKED 최종확정, (H) 8019 tick PASS 등
  원문 36줄, SHA256 `03526ad7a637d6b4a416176820dd60c1959eb9dde49788153f17eb3f2feb459e`)는
  `docs/history/20260928_status_lap742_747_wheel_precompaction.md`에 원문 그대로 보존했다.
- **[압축 포인터] lap739~741 바퀴 기록**은 위 헤더 압축 파일(`docs/history/
  20260928_status_lap717_741_precompaction_v2.md`)에 원문 보존.

G5의 선택/호출/이동/save-load/장시간 runtime 증거와 과거 실패 provenance는 `docs/history/laps/`
및 공유 `temp/Syw2plus_patch/`에 보존한다. G5 milestone 승인은 2026-09-28 01:31 지시로 조건부
보류(A~H 체크리스트) — lap745 middle 재검수 HOLD(F H-STALE-TAIL)였고, lap746~749 work가 S1~S3
probe·S3 대체경로·홀드버튼 원인규명을 처리했고, lap750 middle이 S3/S5 공백으로 HOLD했다. 다음은 위
"다음 한 가지"의 work 1 lap.

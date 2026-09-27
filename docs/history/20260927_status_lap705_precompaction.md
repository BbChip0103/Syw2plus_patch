# STATUS — 매 바퀴 갱신하는 기억

이전(lap678~687) 상세 서술은 원문 SHA256 보존 후 압축했다:
`docs/history/20260926_status_lap688_precompaction.md`(원문 152줄, SHA256
`2b98e3b9e0b3757b7607efbf671a391fa89c504699e7d40cd33c5c52f6dab839`). 각 lap의 전체 근거는
`docs/history/laps/20260926_lap67{6,7,8,9}_*.md`·`lap68{0..8}_*.md`에 그대로 있다.

lap688~699 상세(G5 milestone 승인, G2 8인×10000 시도·A/B 판정·사용자 종료 결정)는 원문 SHA256
보존 후 압축했다: `docs/history/20260927_status_lap699_precompaction.md`(원문 130줄, SHA256
`3dae83a4115372fd3ddf019f82cafd65d2be926456a4074f2d5e3c0a73dcd4be`). 각 lap 전체 근거는
`docs/history/laps/20260926_lap68{8,9,90}_*.md`·`20260926_lap69{1,2,3,4}_*.md`·
`20260927_lap69{5,6,7,8,9}_*.md`에 그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 승인, 최우선 지시 종료**(멀티 동기화는
`UNKNOWN` 메모 유지, 명령당 60B 레코드 최대3회 발행).

**G2는 2026-09-27 03:21 사용자 판단으로 전비10000 트랙 종료, 전비5000(달성 판단 유지)으로 복귀.**
10000 후보(lap691~699, `g2_supply10000_*`)와 근거는 보존만 하고 더 진행하지 않는다.

**lap702(work) G4 W2 fail-closed 보강 + save006 fixture로 non-vacuous `EXACT_POSTLOAD_EDGE_PASS`
최초 raw 달성:** lap701 middle의 `BLOCKED(postload_contract:marker_source_absent)`(save000이
0==0 공허 일치로 PASS되던 문제)를 두 단계로 해소했다. ① `_g4_postload_contract`에 fail-closed
체크 추가 — marker `source.full_id`/`slot`이 0이 아니고 `(full_id&0xffff)==slot`, 첫 row
`source.live is True` 아니면 FAIL. 기존 PASS/mismatch 테스트 픽스처를 이 불변식에 맞게 교정하고
신규 음성 테스트(전부-0 fixture가 FAIL함) 추가, 4/4 PASS. ② `g1_s1_original_load_evidence`에
옵트인 `g4_load_fixture`(기본 save000 불변, `--g4-exact-postload` 전용, pinned 이름만 허용)를
추가해 pinned `save006.dat`(slot 7)를 선택 가능하게 했다. 1차 가설(사본 save 디렉터리에서
save000.dat를 지우면 "가장 낮은 번호가 기본 선택"될 것)은 **실측으로 반증**(PS35 진입 시 selected
WORD가 항상 1로 하드초기화됨, lap362 정적 판정과 일치) — 롤백. 2차 가설(채택): PS35 도달 후
`SELECTED_INDEX_ADDRESS`를 읽어가며 `x11_send_keys.py DOWN`을 반복 발행해 목표 인덱스(7) 도달을
직접 확인하는 `slot_navigation` 스테이지 신설(좌표 추측 없음, 옵트인 경로에서만 실행, 기본
save000 경로는 완전히 건너뜀). fresh 실행: run1(1차 가설) `RuntimeSafetyError`로 FAIL, run2
(2차 가설) DOWN 6회로 selected_index 1→7 도달, `status=PASS`
(`LOAD_RESTORED_PLAYER_STRUCTS`), cleanup ok·잔류0, 원본 SHA `b56986e0…c9c08a8ac` 불변.
**run2 shadow jsonl(SHA `b19dfbbe36…d09`) 재평가: `_g4_postload_contract.pass=true`,
marker `source={full_id:983091, slot:51, owner:0}`(`983091&0xffff=51=slot` 일치), 첫 row
`source={full_id:983091, slot:51, live:true, hp:900, x:135, y:93}` — 실제 살아있는 유닛,
lap701이 지적한 0==0 공허 일치가 아닌 non-vacuous PASS.** `make check` 1027 passed(868.40s),
ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **여전히 candidate AI 정책 없음
(`candidate_present=false`) — "AI 개선 저장/로드 후 유지" 자체는 미착수, 이번 lap은 그 질문을
물을 수 있는 load-boundary 계측 계약을 실질적으로 닫았다.** 상세
`docs/history/laps/20260927_lap702_work_g4_w2_postload_fail_closed_and_save006_live_source_pass.md`.

**lap703(middle) 독립 검수 CONFIRMED — G4 W2 종결:** (a) 신규 불변식이 `ai_shadow.c find_source`
(i≥1, live일 때만 비영)와 동치, (b) run2 jsonl `b19dfbbe…0a09`를 별도 파서로 재계산해 W1 카드 §6
17항목 전부 참·source 비영·live(owner1/4만 무유닛인 패턴이 save006 기존 히스토그램과 일치),
(c) `slot_navigation`은 `selected_index != 1` 가드 한정, save000 치환 4곳 값 동치. 상세
`docs/history/laps/20260927_lap703_middle_g4_w2_independent_review_confirmed.md`.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료 | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(10000 후보 근거는 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 제품 미완료. W1 원본 AI baseline(lap623)·W2 post-load 계측(lap703 확정) 종결 | 원본 길찾기 baseline(P1) 없음, AI 개선 candidate 없음(제품 비교 불가), 사용자 승인 |
| G5 | **단일플레이 milestone 승인(2026-09-26 21:54 사용자)** | 멀티 동기화 `UNKNOWN`(별도 표시, 최우선 지시 종료) |

## 지금 막힌 것 (Blockers)

**G4 원본 길찾기 비교 장면 부재.** `analysis/g4_path_fixture_preflight.json`이 BLOCKED 4항목
(`deterministic_scene_fixture`·`obstacle_occupancy_oracle`·`movement_command_trace`·`repeatability_gate`)
으로 남아 있어 길찾기 원본/개선 비교를 아직 시작할 수 없다. 앞의 2항목 외는 G5 자산으로 해소 가능(다음 한 가지).

## 검증 상태

lap703(middle, 독립 검수): 검수 대상 4파일·run2 jsonl·보호 원본 2경로 재해시 전부 일치, targeted
pytest 233 passed, `SAFETY_PASS`, lap702 make check 로그 `1027 passed` 직접 확인(로그 이후 코드 변경 0).
게임 실행 없음. 비차단: 신규 가드/스킵 유닛 테스트 부재, `source:null` 시 AttributeError 전파.

lap702(work, 자체 재확인만·독립 검수 아님): 신규/수정 유닛 테스트 4/4 PASS, `make check`
**1027 passed(868.40s)**(로그 `logs/gates/20260927_lap702_g4_w2_save006_make_check.log`),
`checks/safety.sh check` `SAFETY_PASS`. run2 jsonl(SHA `b19dfbbe36…d09`, 23행)을
`_g4_postload_contract`로 직접 재평가해 `pass=true`·marker/첫 row 불변식 통과·`live=true`·
`hp=900` 확인. 원본 EXE 재해시(`b56986e0…c9c08a8ac`) 직접 확인. 다음 middle이 요약 없이 원문
재확인 필요.

lap701(middle, 독립 검수): (a) `_g4_load_call_wrapper` objdump 피연산자 수기 추적 + 원본 `0x4d6b98`
호출/`0x440ff0` 규약(cdecl 1-인자, ECX 입력 없음) 확인 → ABI 수리 CONFIRMED. (b) 폴링은
`g4_exact_postload` 분기 한정·판정 없음 CONFIRMED. (d) run3 jsonl(SHA `f1255b09…05c0` 재해시 일치)을
별도 파서로 재집계: 조건1~4·6·7 참, **조건5는 source 부재 공허 일치로 불인정**. 상세
`docs/history/laps/20260927_lap701_middle_g4_w2_postload_independent_review_source_absent_hold.md`.

## 다음 한 가지
**2026-09-27 06:05 운영자 지시(lap704 BLOCKED 후속):** 새 probe의 fixture 19기는 1틱도 안 움직였지만, **lap682 `tools/g5_worker_relative_move_attack_probe.py`는 원본 20/20 이동 수렴을 2/2 재현**했다(같은 원본 EXE). 원인을 새로 추측하지 말고 **lap682 probe의 fixture 생성·드래그·우클릭 절차를 그대로 재사용**(차이는 목적지 거리와 궤적 기록만 추가)해 원본 20기 원거리 이동 baseline 3회를 측정한다. 두 probe의 fixture 차이(유닛 type·소유자·스폰 방식·보정 단계의 9회 우클릭 여부)는 1줄 diff로 기록. 목적지는 실제 렌더 영역 안(또는 미니맵)으로.
**2026-09-27 05:55 운영자 관찰(lap704 진행 중 참고):** baseline run1 목적지 화면좌표 `[1375,337]`로 클릭했는데 slot1198 이동 0(path_length 0), near-control `[604,243]`은 도착. 이전 G5 관측상 게임 화면은 1600×1200 프레임 좌상단 800×600(HUD y≥480)에 그려지므로 x>800 클릭은 게임 밖일 가능성이 크다 — safe box를 실제 렌더 영역(0..800, 0..480)으로 제한하고, 원거리 이동은 목적지가 화면 밖이면 **미니맵 클릭** 또는 카메라 이동 후 클릭으로 발행.

**work(구현 우선, 재계획 없이): G4-P1 원본 길찾기 baseline probe.** 새
`tools/g4_path_baseline_probe.py`가 `tools/g5_worker_relative_move_attack_probe.py`의 in-run
screen→world 보정·선택+우클릭·`read_unit_full`/`poll_convergence`를 import 재사용(G5 파일 수정 금지).
보호 원본 EXE만, 원본 상한 20기 선택 → 워커 기준 ≥20타일 목적지 우클릭 1회 → 슬롯별
`(tick,x,y,command,hp)` raw. 장면은 fixed-seed chain(`_custom_game_chain_inject_seed1` 계열)이 fixture
spawn과 호환되면 그것, 아니면 G5 solo flow + "지형 run간 상이" 명시. 지표: 도착률(반경3타일/20),
도착 tick 중앙·최대, 정체 tick(미도착·비유휴인데 x,y 불변 ≥20tick), 경로비(누적/직선), 최종 분산.
`FEASIBLE_PATH_BASELINE`=fresh 원본 3회 모두 선택20·명령도달20·trace 완주·cleanup ok·원본 SHA 불변 +
3회 지표·편차 기록. `NOT_FEASIBLE`=명령도달<20/추적불가 2회 반복. `BLOCKED`=크래시/cleanup/SHA.
실패 시 원인 추적→수정→재실행은 work가 반복. 부가: `g4_load_fixture` 가드·save000 스킵 유닛 테스트.
`[ESL]Syw2plus/save/`에 save000/save006 없음(LEGACY_SOURCE 우회)은 여전히 미결.

## 바퀴 기록

- lap704(work, 이 세션): `tools/g4_path_baseline_probe.py` 구현·fresh 2회 실행(원거리/근접
  대조군). 하네스 자체 PASS(선택20·정리·SHA 불변)이나 **이동 명령이 워커 1기 외 fixture 19기에
  전혀 도달하지 못함**(2회 반복 → STATUS 판정식상 `NOT_FEASIBLE`, 원인 미확정: 화면 밖 클릭(a)과
  조밀 인접 fixture 자기차단(b) 둘 다 가능). 06:05 운영자 지시(동시 실행 세션이 남김)의 x>800
  화면 밖 가설을 12개 후보 좌표 재계산으로 독립 재확인, `SAFE_SCREEN_BOX`를 `(40,760,40,460)`으로
  보수화. make check 1031 passed(신규 유닛 테스트 4개 포함), SAFETY_PASS. 상세
  `docs/history/laps/20260927_lap704_work_g4_path_baseline_probe_dense_fixture_move_blocked.md`.
- lap703(middle): lap702 독립 검수 — 불변식·jsonl 독립 재계산·기본경로 동치 전부 CONFIRMED,
  `EXACT_POSTLOAD_EDGE_PASS`(save006) 확정·G4 W2 종결. 다음 G4-P1 길찾기 baseline handoff. 상세
  `docs/history/laps/20260927_lap703_middle_g4_w2_independent_review_confirmed.md`.
- lap702(work): G4 W2 fail-closed 보강 + `g1_s1_original_load_evidence` 옵트인 fixture 선택
  (save006, slot navigation) 추가 → non-vacuous `EXACT_POSTLOAD_EDGE_PASS` 최초 raw 달성.
  make check 1027 passed. 상세
  `docs/history/laps/20260927_lap702_work_g4_w2_postload_fail_closed_and_save006_live_source_pass.md`.
- lap701(middle): lap700 독립 검수 — ABI 수리·폴링 옵트인 CONFIRMED, run3 조건1~4·6·7 참이나
  marker/첫 row source 부재(owner7 무유닛, 0==0)로 `BLOCKED(postload_contract:marker_source_absent)`.
  lap700 run1 서술 오류 정정. 상세 `docs/history/laps/20260927_lap701_middle_g4_w2_postload_independent_review_source_absent_hold.md`.
- lap700(work): G4 W2 재개 — ai_shadow.c 스택언밸런스(항상 크래시) 실결함 수리,
  `_g4_postload_contract` source 비교 버그 수리, postload 대기 폴링 추가, fresh 3회로
  `EXACT_POSTLOAD_EDGE_PASS` 최초 raw 달성. make check 1026 passed. 상세
  `docs/history/laps/20260927_lap700_work_g4_w2_postload_abi_and_contract_fix_exact_pass.md`.
- lap691~699(work/middle): G2 8인×10000 트랙 — 전역풀4092 확장 PASS(695)→저장로드 PASS(696)→
  전역열거 도구 수리 PASS(697)→middle 조건부 부분PASS/HOLD(698, 12비트 wire 한계 발견)→
  A/B 판정 자료 보강(699)→**2026-09-27 03:21 사용자 판단으로 트랙 종료, 전비5000 복귀**.
  상세는 `docs/history/20260927_status_lap699_precompaction.md`와 각 lap 파일.

G5의 선택/호출/이동/save-load 부분 runtime 증거와 과거 실패 provenance는 `docs/history/laps/` 및
공유 `temp/Syw2plus_patch/`에 보존한다. G5는 사용자 milestone 승인 완료, 멀티 동기화만 `UNKNOWN`이다.

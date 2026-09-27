# 2026-09-27 | lap 703 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5-5 / high / middle(독립 검수·계획). 게임/하네스 코드 수정 없음.
- 가설 / 사용자 관찰: lap702 work의 (a) `_g4_postload_contract` fail-closed 보강, (b) save006 run2
  shadow jsonl의 non-vacuous `EXACT_POSTLOAD_EDGE_PASS`, (c) `slot_navigation` 옵트인 한정·기본
  save000 경로 무변경이 요약 없이 원문으로 재확인된다.
- 예상 PASS / FAIL 조건: (a) 불변식이 `ai_shadow.c find_source`와 일치하고 0==0 공허 일치를 거부,
  (b) 독립 파서로 W1 카드 §6 조건 전부 참 + marker/첫 row source 비영·live, (c) save000에서
  신규 분기가 실행되지 않고 치환 값이 기존 리터럴과 동치. 하나라도 거짓이면 HOLD.
- 변경 파일 / source fingerprint / 커밋: 문서만(이 파일, `docs/STATUS.md`,
  `docs/feedback/APPROVALS.md`, `docs/feedback/INBOX.md`). uncommitted(LOOP_ALLOW_COMMITS=0).
  검수 대상 재해시: `tools/runtime_env.py` `d2b4b0ab…3108b4`, `tests/test_runtime_env.py`
  `ac99d8f0…6bbdaf`, `tools/inmm_stub/ai_shadow.c` `252b1a06…b8ba5`, `_inmm.dll` `4e5f64e5…a971f6`
  — lap702 기록값과 전부 일치. lap702 make check 로그(05:15:36) 이후 tools/tests/patches/checks
  변경 파일 0건.
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 `Syw2plus_re/Syw2plus/syw2plus_original.exe`와
  `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` 둘 다 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  재해시 일치. candidate 없음(read-only shadow). fixture `save006.dat`(evidence JSON:
  `synthetic=false`, `resource_grant=false`, SHA `616b7997…a0d064`, selected_index 7).
- 실행 명령 / 로그: 게임 실행 없음(검수 전용).
  1. `sha256sum` 위 파일 + run2 jsonl → `b19dfbbe3606a721bb1dfc895053504872c246a107f40f53dbcdb164d6680a09` 일치.
  2. 독립 python 파서(`_g4_postload_contract` 미사용)로 jsonl 23행 재파싱.
  3. `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_g4_ai_shadow.py tests/test_s1_load_evidence.py` → 233 passed(1.89s).
  4. `bash checks/safety.sh check` → `SAFETY_PASS`.
  5. `logs/gates/20260927_lap702_g4_w2_save006_make_check.log` 직접 확인 → `1027 passed in 868.40s`, mypy 0 issue, `CONTEXT_PASS`.
  6. `git diff HEAD -U0 -- tools/runtime_env.py`로 `selected_index` 치환 지점 대조, `tools/s1_load_evidence.py` `FIXTURES` 대조.
- 측정값 / 판정:
  - **(a) CONFIRMED.** `find_source`는 `i=1`부터 순회하고 `exists!=0 && owner 일치 && hp!=0 &&
    (id&0xffff)==i`일 때만 값을 채우며 아니면 전 필드 0·`live=FALSE`(ai_shadow.c 212~242).
    따라서 marker(`live` 필드 없음)에서 `full_id!=0 && slot!=0 && (full_id&0xffff)==slot`은 live
    source와 동치이고, slot 0은 source가 될 수 없어 `slot==0` 거부는 과잉 거부가 아니다. 첫 row는
    `live is True` + source_keys 동일성으로 비영이 따라온다.
  - **(b) CONFIRMED.** marker 1건(seq1, slot 6=save006, tpre 0, tload 24567, next_owner 0),
    postload row 22. 독립 재계산 17항목 전부 참: next_owner=(tload+1)&7, 첫 row seq=2·tick=24568,
    owner=tick&7=0=marker.source.owner, entry_ecx `0x956770`, mode `(3,1,0,0,0,0,0)`,
    `forwarded_once`, tick_rewind 술어, pid/tid 동일, window 17행 load_marker_seq=1·tick 중복0·
    reentry0, 전 행 candidate 0, seq 단조. source `{full_id:983091, slot:51}`(983091&0xffff=51),
    첫 row `live=true, hp=900, x=135, y=93`. 비-preexisting(command1/pending1/xy0). **추가 교차
    증거:** post-load row의 owner1·owner4만 `live=false`이고 나머지 owner는 live — lap284/289가
    기록한 save006 히스토그램(owner1/4 유닛 0)과 일치해 실제 save006 상태가 복원됐음을 독립 지지.
    evidence JSON `slot_navigation`: DOWN 6회, selected_index 1→2→…→7 매회 +1 관측.
  - **(c) CONFIRMED.** 신규 스테이지는 `if fixture_spec.selected_index != 1:` 가드 안에만 있고
    `FIXTURES["save000.dat"].selected_index == 1`. `selected_index=1` 리터럴 → `fixture_spec.selected_index`
    치환 4곳(evidence dict, direct-pre, load-trigger precondition, `s1.evaluate`)은 save000에서 값 동치,
    나머지 차이는 오류 메시지 문자열뿐. `g4_load_fixture`는 `g4_exact_postload` 없이 거부, pinned 이름만 허용.
  - 종합: **`EXACT_POSTLOAD_EDGE_PASS`(save006, non-vacuous) CONFIRMED. G4 W2(load-boundary 계측
    계약) 종결.** 이는 G4 제품 PASS·AI 개선·저장/로드 후 개선 유지 증명이 아니다(candidate 없음).
- 회귀 / 남은 위험:
  - 비차단 1: `g4_load_fixture` 가드 2종과 "save000이면 `slot_navigation` 미실행"을 고정하는 유닛
    테스트가 없다(`tests/`에 `g4_load_fixture`/`slot_navigation` 참조 0건). 현재는 코드 동치로만 보증.
  - 비차단 2: `first.get("source", {})`에 `source: null`이 오면 `AttributeError`가 `_g4_postload_contract`
    와 `_g4_shadow_provenance`의 except 목록 밖으로 전파된다(fail-open이 아니라 크래시, lap700부터 존재).
  - 비차단 3: `tpre=0`(메뉴에서 load)이라 tick_rewind 술어는 이 실행에서 자명히 false — in-game
    load 경로의 rewind는 미관측.
  - 미결: `[ESL]Syw2plus/save/`에 save000/save006 없음(LEGACY_SOURCE 우회 유지).
  - 독립 검수: 이 lap이 2단 검수. 사용자 승인 없음(마일스톤 경계 아님 — W2는 G4 내부 계측 카드).
- 다음 한 가지(work handoff, 재계획 없이 구현 우선): **G4-P1 원본 길찾기 baseline probe.**
  근거: DESIGN §G4 "원본 병목과 반복 가능한 비교 장면부터", `analysis/g4_path_fixture_preflight.json`
  의 BLOCKED 4항목 중 `movement_command_trace`·`repeatability_gate`는 G5 기간에 만든 자산
  (`tools/g5_worker_relative_move_attack_probe.py`의 in-run screen→world 보정, 선택+우클릭 명령,
  `read_unit_full`/`poll_convergence` 슬롯별 x/y 추적)으로 바로 해소 가능하다.
  - 구현: 새 `tools/g4_path_baseline_probe.py`(기존 G5 probe 파일은 수정하지 않고 import 재사용).
    보호 원본 EXE만(후보 없음), 원본 상한 20기 선택, 워커 기준 원거리 목적지(≥20타일, 보정 역변환)
    우클릭 1회, 고정 주기로 슬롯별 `(tick,x,y,command,hp)` raw 기록. 장면은 fixed-seed chain
    (`_custom_game_chain_inject_seed1` 계열)이 fixture spawn과 호환되면 그것을, 아니면 G5 solo
    flow를 쓰고 그 사실(지형 run간 상이)을 raw에 명시한다.
  - 지표(raw에서 계산): 도착률(목적지 반경 3타일 도달 기수/20), 도착 시간 중앙·최대 tick,
    정체 tick(미도착·비유휴 command인데 x,y 불변 ≥20 tick 구간 합), 경로비(누적 이동거리/직선거리),
    최종 분산.
  - 판정: `FEASIBLE_PATH_BASELINE` = fresh 원본 3회 모두 선택20·명령 도달20·목적지까지 trace 완주·
    cleanup ok·원본 SHA 불변, 지표 3회분과 run간 편차 기록. `NOT_FEASIBLE` = 명령 도달<20 또는 추적
    불가가 2회 반복(원인 raw 보존, 같은 추측 반복 금지). `BLOCKED` = 크래시/cleanup/SHA 불일치.
    실패 시 원인 추적→수정→재실행은 work가 반복한다(실행 횟수 예산으로 막지 않음).
  - 부가(같은 work, 작게): 위 비차단 1의 유닛 테스트 2~3개.

# APPROVALS — 검수/마일스톤 판정

## 현재 판정

제품 마일스톤 승인 없음. **G1 카드2 Stage B 실제 원본/후보 비교 실행은 승인됨.**
목표 문서 반영과 Stage B 실행 승인은 기능 승인/출시 승인이 아니다.
1단 자동 테스트 →2단 다음 새 세션 독립 검수 →3단 사용자 마일스톤 확인으로 운영한다.

## 미해결·반려·판정 불명 색인

- [ ] **2026-09-27 lap714 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G4 AI 생산
  게이트 라이브 히스토그램):** 13:45 지시("라이브로 어느 게이트가 owner1 발주를 막는지 계측")를
  수행. 신규 `tools/g4_ai_production_table.py`(`FUN_00406C70` 생산표 레코드 레이아웃 해독 —
  건물타입/생산kind/선행유닛kind·count/기술kind, lap501이 미해독으로 남긴 부분; 143행=생산65+
  연구78·건물타입27종, lap501 수치와 일치)와 신규 `tools/g4_ai_gate_histogram_probe.py`(읽기전용
  `process_vm_readv`, `patches.population.runtime_driver.read` 재사용, 새 EXE 패치/breakpoint
  없이 owner0/1이 보유한 모든 생산건물×생산레코드 조합을 매 tick 분류)로 lap712와 동일 seed1
  fixture 280초를 실행. **결과(278 표본, 3회 실행 — 스모크20s 1회+전체280s 2회 모두 재현):
  H-TYPEMAX/H-RATIO/H-CROWD는 owner0/1 전부 0회. 100%가 H_AVAIL(가용 플래그=0: owner0
  772/owner1 620)과 PREREQ_OWN(선행유닛 미보유: owner0 398/owner1 692) 둘로만 갈리고,
  `WOULD_ACCEPT`는 두 owner 모두 0건.** owner0(HQ type49: kind7/110→H_AVAIL, kind94→
  PREREQ_OWN)·owner1(HQ type58: kind31/75→H_AVAIL, kind102/98→PREREQ_OWN) 모두 최초 건물의
  전 생산레코드가 280초 내내 100% 거부되며, 이후 지은 건물(owner0 type50/51, owner1 type60)도
  같은 두 사유로 100% 거부된다 — **lap712/713이 전제한 "owner1만 약하다"가 아니라 두 owner
  모두 이 두 게이트로 구조적으로 막혀 있다.** 원본 SHA 3회 `source_unchanged=true`, cleanup
  매회 ok, EXE/원본 미변경(순수 메모리 읽기, breakpoint/detour 없음). `make check`
  1079 passed(835.61s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS, 신규 테스트 18개
  (생산표 디코드 5+게이트 분류기 13, synthetic 데이터로 REASONS 전 분기 pin). **work tier
  판단으로 다음 middle 독립 검수를 요청한다**(`FUN_00406C70` 필드 오프셋 해독의 디스어셈블
  재추적, 분류기의 게이트 순서/주소가 lap501·기존 offset 상수와 일치하는지, `by_record` 집계가
  샘플별 중복 계수 없이 정확한지). 운영자가 14:45에 이 결과를 반영해 다음 v2 방향(AI 건설 결정
  히스토그램)을 이미 지시했다(STATUS/INBOX 참고) — 이 work tier 요청은 lap714 계측 자체의
  방법론 검수이며, v2 구현은 다음 work의 몫이다. 근거
  `../history/laps/20260927_lap714_work_g4_ai_production_gate_histogram_h_avail_prereq_own.md`.
- [ ] **2026-09-27 lap713 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G4 생산 후보
  v1 H-CROWD FALSIFIED):** 13:05 판정("AI 자원 소비(생산 결정) 개선... 상수 1~2개")을 수행.
  `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`(lap501)가 확정한
  AI 생산 결정 경로 8게이트 중 EXE에 정적 즉치값으로 있는 유일한 상수(H-CROWD, `FUN_00406B00`
  @`0x406c44` 동종·동소유 11×11 밀집 ≥7 발주중단)를 7→14로 올린 후보
  `patches/ai/g4_production_crowd_cap_v1.py`(단일 EDIT, 원본 SHA 가드·copy/restore 회귀
  테스트 7개)를 만들고, `tools/runtime_env.py`의 기존 승인된 named-candidate-exe 메커니즘
  (`G4_CANDIDATE_EXES`, `controller_cadence_probe`/`gather_cooldown_probe`와 동일 패턴)에
  `"g4_production_crowd_cap_14.exe"` 1건을 추가해 `tools/g4_ai_behavior_probe.py --variant
  candidate`로 연결(private `ORIGINAL_EXE`는 건드리지 않음 — 최초 시도는 private 원본을
  직접 덮어써 `g1-baseline`의 `check_runtime` 원본 검증에 막혀 실패, named-candidate 방식으로
  정정). lap712와 동일 seed1 fixture로 후보 N=3(단독 1회+반복 2회) 실행 — **owner0/1 종점
  생산(21/12)·군대(16/10)·자원(9792/23068) 지표가 lap712 원본 N=3과 완전히 동일**,
  **`FALSIFIED`**(H-CROWD가 이 fixture 두 owner 모두에서 안 걸림). H-TYPEMAX/H-RATIO는
  런타임/Data 표 참조라 정적 상수로는 애초에 못 바꾼다(문서 §5). 원본 SHA 3회
  `source_unchanged=true`, cleanup 3/3 ok, 후보 SHA 3회 동일, crash 0. `make check`
  1061 passed(868.47s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **work tier 판단으로
  다음 middle 독립 검수를 요청한다**(신규 `runtime_env.py` candidate-exe 분기가 기존 두
  candidate와 같은 안전 경계를 지키는지, 단일 EDIT의 바이트 근거 재확인, private `ORIGINAL_EXE`
  미접촉 확인). 다음 work: STATUS가 지정한 라이브 게이트 계측(어느 게이트가 owner1 생산을
  실제로 막는지 breakpoint/counter로 특정) 근거
  `../history/laps/20260927_lap713_work_g4_ai_production_crowd_cap_v1_falsified.md`.
- [ ] **2026-09-27 lap712 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  12:05 운영자 판정 다음 work ①②(자유대전 AI baseline 원본 N=3, 가장 약한 지표 STATUS 기록)를
  수행. 신규 `tools/g4_ai_behavior_probe.py`가 `runtime_env.py g1-baseline
  --g4-chain-goal _custom_game_chain_inject_seed1 --g4-sample-seconds 280`을 감싸 owner별
  자원수입/생산량(내부 id 신규 관측 근사)/군대규모(초기 HQ·worker 타입 제외 근사)/첫공격시각
  (`command==4` 최초 시각)/유휴일꾼수(worker 타입&`command==1`)를 산출한다. 원본 SHA 3회 전부
  `source_unchanged=true`, cleanup 3/3 ok, EXE/원본 미변경(읽기 전용 관측). 3/3 완전 재현
  (owner0 nation1/HQ49/worker7, owner1 nation2/HQ58/worker31). **owner0
  `idle_worker_count_mean`=0.679(owner1 0.129의 약5.3배)가 owner0 자원 순감소
  (`income_per_min`≈-1119, owner1은 ≈+1734)와 동행 — 가장 약한 지표로 채택.** 단 국가 조합
  1개만 측정했으므로 2026-09-16 lap의 `NO_GO_GENERIC_AI_IMPROVEMENT`(matchup 의존 편향)
  선례와 같은 함정 가능성을 명시하고 범용 결함으로 승격하지 않았다. 280초 내 양쪽 모두
  `command==4`(공격) 0건, `hp_decrease`/`slot_disappearances` 0건 — 2026-09-16 lap의 동일
  `seed1`(옛 소스 경로 `Syw2plus/`)이 240초 내 첫 피해(146~198초)를 재현했던 것과 불일치,
  새 소스 경로(`[ESL]Syw2plus`, 2026-09-26 22:52 전환) 이후 Data/맵 차이 가능성을 원인 미상
  관찰로 기록(조사하지 않음, 후순위). v1 후보는 구현하지 않았다 — 2026-09-16 lap이 같은
  selector(`FUN_0043F5D0`)의 cooldown 상수를 blind로 낮춰 두 번 반려됐으므로, 다음 work는
  그 case3가 호출하는 `FUN_004B03D0`(채집지 순환 상태기)의 완료/실패 조건을 먼저 정적으로
  특정한다. 회귀 신규 4개, `make check` 1054 passed(867.50s), ruff/mypy/`CONTEXT_PASS`/
  `SAFETY_PASS` 전부 PASS. 근거
  `../history/laps/20260927_lap712_work_g4_ai_freeforall_behavior_baseline.md`.
- [ ] **2026-09-27 lap707~711 work tier 정보제공 5건 압축(원문 79줄, SHA256 `a095d6ea2da22ec04a29725615fcd03f798aac75e0361926e3bfd71390ceb1e5`):** 전문은 `../history/20260927_approvals_lap707_711_precompaction.md`에 보존. G4-P1 길찾기 baseline·scenario probe·개선후보 v1/v2 반증·미니맵 BLOCKED·v3 타임아웃 반증(lap707~711) work tier 정보성 기록이며, 2026-09-27 12:05 운영자 판정으로 길찾기 트랙 자체가 종료돼 더 진행하지 않는다(STATUS/lap712 참고).
- [ ] **2026-09-27 lap702 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G4 W2 postload
  fail-closed 보강 + save006 non-vacuous PASS):** lap701 middle의 `BLOCKED(postload_contract:
  marker_source_absent)` 지시를 그대로 수행. ① `_g4_postload_contract`에 fail-closed 체크 추가
  (marker `source.full_id`/`slot` 0이 아니고 `full_id&0xffff==slot`, 첫 row `source.live is True`
  아니면 FAIL) — run3류 0==0 공허 일치를 더 이상 PASS시키지 않는다. 기존 PASS/mismatch 테스트
  픽스처를 이 불변식에 맞게 교정, 신규 음성 테스트 추가(4/4 PASS). ② `g1_s1_original_load_evidence`에
  옵트인 `g4_load_fixture`(기본 save000 불변, `--g4-exact-postload` 전용) 추가해 pinned
  `save006.dat`(slot 7) 선택 가능하게 함. 1차 가설(사본에서 save000.dat 제거 시 "최저 번호
  자동선택")은 fresh 실행으로 **반증**(PS35 진입 시 selected WORD가 항상 1로 하드초기화됨,
  `docs/history/laps/20260912_lap362_middle_s1_execution_envelope.md`와 일치) — 롤백. 2차 가설
  (채택): `SELECTED_INDEX_ADDRESS`를 재읽어 목표 도달을 확인하며 `x11_send_keys.py DOWN`을
  반복하는 `slot_navigation` 스테이지(옵트인 한정, 좌표 추측 없음). fresh 실행 run2에서 DOWN 6회로
  selected_index 1→7 도달, `status=PASS(LOAD_RESTORED_PLAYER_STRUCTS)`, cleanup ok·잔류0, 원본
  SHA `b56986e0…c9c08a8ac` 불변. **run2 shadow jsonl(SHA
  `b19dfbbe3606a721bb1dfc895053504872c246a107f40f53dbcdb164d6680a09`) 재평가:
  `_g4_postload_contract.pass=true`, marker `source={full_id:983091,slot:51,owner:0}`
  (`983091&0xffff=51=slot` 일치, 공허 아님), 첫 row `source={full_id:983091,slot:51,live:true,
  hp:900,x:135,y:93}` — 실제 살아있는 유닛. lap701이 요구한 non-vacuous `EXACT_POSTLOAD_EDGE_PASS`
  최초 raw 달성.** `make check` 1027 passed(868.40s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부
  PASS. **candidate AI 정책은 여전히 없음(`candidate_present=false`) — "AI 개선 제품 비교"는
  미착수, 이번 lap은 그 비교를 측정할 수 있게 하는 load-boundary 계측 계약을 fail-closed로 닫았을
  뿐이다.** 근거
  `../history/laps/20260927_lap702_work_g4_w2_postload_fail_closed_and_save006_live_source_pass.md`.
  **work tier 판단으로 다음 middle 독립 검수를 요청한다**(신규 불변식 로직 코드 대조, run2 jsonl
  별도 파서 재확인, `slot_navigation`이 옵트인 한정이며 기본 save000 경로 산출물이 무변경임을 확인).
  - [x] 검수(lap703 middle, Claude Code Opus): (a) 불변식이 `ai_shadow.c find_source`(i≥1, live일 때만
    비영)와 동치 CONFIRMED, (b) jsonl `b19dfbbe…0a09` 독립 파서 재계산 17항목 전부 참·source 비영·live,
    owner1/4만 무유닛인 패턴이 save006 기존 히스토그램과 일치 CONFIRMED, (c) `slot_navigation`은
    `selected_index != 1` 가드 한정, save000 치환 4곳 값 동치 CONFIRMED. **`EXACT_POSTLOAD_EDGE_PASS`
    (save006, non-vacuous) 확정, G4 W2 종결**(G4 제품 PASS 아님, 사용자 승인 불요 — 내부 계측 카드).
    비차단: 신규 가드/스킵 유닛 테스트 부재, `source:null` 시 AttributeError 전파. 다음 work: G4-P1
    원본 길찾기 baseline probe. 근거 `../history/laps/20260927_lap703_middle_g4_w2_independent_review_confirmed.md`.
- [ ] **2026-09-27 lap700 work tier(Claude Code Sonnet, 다음 middle 검수 요청 — G4 W2 postload
  harness contract):** STATUS/INBOX 2026-09-27 03:21 지시(G4 post-load 확인부터 구현 우선)를
  수행. `tools/inmm_stub/ai_shadow.c`의 `g4_load_call_wrapper`가 스택 언밸런스로 **항상
  크래시**하는 실결함(marker 호출 뒤 `addl $8,%esp`가 저장된 원본 EAX까지 버려 다음 `pop eax`가
  반환주소를, 뒤이은 `ret`이 caller의 slot 값을 코드 주소로 오독)을 objdump 피연산자 값을 손으로
  추적해 발견, `$8`→`$4`로 수리(cdecl 2-인자 정리 8바이트 중 4는 `add`, 4는 `pop`으로 나눠야
  하는데 기존은 12바이트를 치웠다). 같은 파일의 기존 테스트가 이 깨진 바이트 패턴을 그대로
  요구하고 있어 lap626의 "objdump로 확인했다"가 실제로는 근거가 아니었음도 확인·수리했다.
  이어서 `tools/runtime_env.py`의 `_g4_postload_contract` source 비교가 marker(`source.owner`
  포함)와 shadow row(최상위 `owner`, `source`엔 없음)의 비대칭 스키마를 동일 키로 비교해
  **라이브 데이터에서 항상 거짓 FAIL**하던 버그를 수리(owner는 `marker["source"]["owner"] vs
  first["owner"]`로, 나머지 키는 기존 방식대로 비교). post-load 17행 창을 채우도록
  `_g4_wait_for_postload_rows` 폴링을 옵트인 경로에만 추가(기존 stage budget 대비 여유 충분,
  총 데드라인 상수 불변, 옵트인 외 산출물 불변). fresh pinned save000 3회 실행(원본 SHA
  `b56986e0…c9c08a8ac` 3/3 불변, LEGACY_SOURCE 사용 — 새 기본 `[ESL]Syw2plus/save/`엔
  save000.dat이 없음, 2026-09-26 22:52 지시가 보존한 읽기전용 옛 경로로 이 fixture만 재현):
  run1(ABI 수리 전, crash 없음 확인)→run2(대기 폴링 추가, `postload_rows=22`이나 source
  버그로 FAIL)→run3(양쪽 수리 후) **`g4_exact_postload.pass=true`(marker1·postload22·
  `first_seq=marker_seq+1`), cleanup ok, 잔류0 — `EXACT_POSTLOAD_EDGE_PASS` 최초 raw 달성**.
  `make check` 1026 passed(759.23s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 신규/
  수정 테스트 2건(회귀 방지, 버그 재현 픽스처 포함). **candidate AI 정책은 여전히 없음
  (read-only shadow, `candidate_present=false` 전 구간) — "AI 개선 제품 비교"는 미착수, 이번
  lap은 그 비교를 측정할 수 있게 하는 load-boundary 계측 계약만 닫았다.** 근거
  `../history/laps/20260927_lap700_work_g4_w2_postload_abi_and_contract_fix_exact_pass.md`.
  **work tier 판단으로 다음 middle 독립 검수를 요청한다**(ABI 수리 objdump 재추적, source 비교
  수리·폴링이 옵트인 외 동작을 바꾸지 않았는지, run3 jsonl SHA
  `f1255b093c793151dff4cbb756356601c31030ced6502c6d57335fd886ad05c0` 직접 파싱 재확인).
  - [x] 검수(lap701 middle, Claude Code Opus): ABI 수리(objdump 수기 추적+원본 `0x440ff0` cdecl
    1-인자) CONFIRMED, 폴링 옵트인 한정 CONFIRMED, run3 조건1~4·6·7 참. **그러나 marker/첫 row
    source가 부재(전부 0, `live=false`, owner7 무유닛)한 0==0 일치라 카드 §6-5 불충족 →
    `BLOCKED(postload_contract:marker_source_absent)`, `EXACT_POSTLOAD_EDGE_PASS` 확정 안 함.**
    lap700 "run1=수리 전" 서술은 오류(3회 모두 수리 후 DLL). 다음 work: 계약 fail-closed 보강 +
    save006 fixture 전환 실행. 사용자 승인 요청 없음. 근거
    `../history/laps/20260927_lap701_middle_g4_w2_postload_independent_review_source_absent_hold.md`.
- [ ] **2026-09-27 lap695~699 G2 8인×10000 middle 검수요청 4건 압축(원문 44줄, SHA256 `2eea22c0c4af8101915dc323a6f4d829371ea155d82f8f01adcffb8fae99a824`):** 전문은 `../history/20260927_approvals_g2_supply10000_middle_requests_precompaction.md`에 보존. G2 8인×10000 전역풀4092/저장로드/전역열거 무결성/A·B 판정자료(lap695~699) middle 검수 요청이며, 2026-09-27 03:21 사용자 판단으로 이 트랙 자체가 종료돼 더 진행하지 않는다(STATUS 참고).
- [ ] 2026-09-26 lap685 work tier(Claude Code Sonnet, 다음 middle 검수 대기): lap684 handoff("청크 재호출 사이 order-type4 전용 필드 손실") 가설과 17:55 운영자 지시("옛 선택 배열 리터럴 잔여") 가설을 gdb 트레이스 3종+v2 대조군+정적 전수 xref 스캔으로 **모두 반증**. 빌더(`FUN_004AE550`) 내부 상태·빌더→writer 디스패치 루프(`0x4AEC60→0x40FF90→0x412540`)는 move/attack 동일(50/50) — 청킹 무관 확정. **v2(청킹 없음) 후보도 `ever_command4_count=0/49`**로 v3와 동일 실패 — 재배치 이후 v2/v3 공통 회귀로 좁혀짐. 옛 배열(`0x899024/28/2A/78`) 리터럴 참조는 원본 전체(raw 52건) 전부 v1 `DIRECT_SITES`/`END_SITES`로 이미 재타깃돼 잔여 0건. 제품 코드 미수정(원인 미확정 상태에서 추측 수정 없음), 신규 도구 5개+테스트 4개, `make check`980 passed(683s). 근거 `../history/laps/20260926_lap685_work_g5_attack_broadcast_field_loss_falsified_relocated_downstream.md`.
- [ ] 2026-09-26 lap684 work tier(Claude Code Sonnet, 다음 middle 검수 대기): v3 후보 `e5004764…` roundtrip(선택/그룹/호출/save-load) **PASS**(후보50/50/50, 원본20/20/20, crash0). 공격은 `command==4` 살아있는 상태 기준이 원본에서도 0으로 나와 판정 필드 결함으로 확인, `+0x384==0x1000004`+3초 누적 `ever_command4_count`로 교체해 원본 2/2 **100%(19/19)** 대비 후보 2/2 **≤1/49**의 재현 가능한 FAIL을 얻었다. 전체 2단은 아직 middle 미검수. 근거 `../history/laps/20260926_lap684_work_g5_v3_roundtrip_pass_attack_command4_blocked.md`.
- [!] 2026-09-26 lap683 중간 tier 독립 검수(Claude Code Opus): v3 후보 `e5004764…`의 크래시 수정과 이동 paired(후보 `command==3` 50/50, 원본 20/20)는 **승인**. 공격 브로드캐스트50은 **불인정** — lap680 `pending!=1` 판정식이 이동 계열 값(`0x1000001`)도 세며, 같은 phase `command==4`는 0/50이었다. lap681 41/50은 원본 paired가 없고 재현되지 않았다. 부대/호출/save-load roundtrip은 v3에서 미실행. 전체 2단 `HOLD/INCONCLUSIVE`, 제품 G5 PASS 아님. 근거 `../history/laps/20260926_lap683_middle_g5_v3_independent_review_hold.md`.
- [!] 2026-09-26 lap665 중간 tier 독립 검수: 후보 `ae495fa5…`의 선택/호출/이동/save-load `50/50/50`과 원본20 대조는 제한 승인. 그러나 DESIGN G5의 **실제 적 대상 공격 명령 50** 증거가 없어 전체 2단은 `INCONCLUSIVE/HOLD`; 제품 G5 PASS 아님.
- [ ] **2026-09-26 lap689 중간 tier 독립 검수(Claude Code Opus 5.5) — G5 사용자 milestone 3단 판단 요청:** 후보 v3
  `e5004764…`, 원본 `b56986e0…`. 단일플레이 2단 **조건부 PASS** — 드래그50(55기 중 5기 미선택)·부대 저장/호출/저장로드
  50/50/50·이동 ever 50/50·크래시0·UI 스크린샷 대조를 원본20 대비 raw로 재확인. 공격50은 `ever_command4`(표적 무관·
  자동교전 오염 가능)가 아니라 t=0 스냅샷 49기 동시 `pending==0x1000004`+클릭 xy(후보-1/2)와 49/49 표적 handle(후보-3)로 승인.
  멀티 동기화 `UNKNOWN`(명령당 레코드 최대 3회 발행). 사용자 승인 전 제품 G5 PASS 아님. 근거
  `../history/laps/20260926_lap689_middle_g5_full_independent_review_conditional_pass.md`.
- [x] 2026-09-26 lap688 work tier(Claude Code Sonnet, lap689 middle이 검수 완료): 19:25 판정("흔들림 원인 1개
  raw로 고정 → N=5 반복 측정") 실행. 원인 확정: 공격 표적을 드래그/MOVE 이전에 스폰해 자동교전이
  명시적 클릭 전에 표적을 죽이는 레이스였다(원본 5회 중 2회 완전실패, `observed_target_uids` 전 구간
  공백으로 확인). 표적 스폰을 ATTACK 클릭 직전으로 옮겨 수정, 완전실패 재현 소거. 수정 후 N=5: 원본20
  `ever_command4/19`=19,19,5,11,4(중앙값58%), 후보v3(50) `.../49`=30,33,49,27,32(중앙값65%, 원본보다
  낮지 않음). 원본·후보 SHA 10회 전부 불변, cleanup 전부 ok, 제품 EXE 0 변경. 19:25 판정문의 원본
  기준선(85~95%)은 이 표본에서 원본도 미달 — 문자 그대로 PASS 적용 가부는 middle 판정 필요. 근거
  `../history/laps/20260926_lap688_work_g5_attack_probe_spawn_timing_fix_and_n5_measurement.md`.
- [ ] **G5 3단 사용자 milestone 판단 대기 전 선행:** work tier candidate50 대 original20 실제 공격 paired probe → 새 중간 tier 2단 재검수. 멀티 동기화는 `UNKNOWN`으로 별도 표시하며 사람 승인으로 바꾸지 않는다.
- **2026-09-24~26 위임 승인 22건 압축(원문 22줄, SHA256 `4ed30516913c8f39bd22caba434682f642dd96c231a9307af15633d31b13fb60`):** 전문은
  `docs/history/20260927_approvals_g5_g4_delegated_approvals_20260924_20260926_precompaction.md`에
  보존. G5 crash/스택 오버플로/hit-test/fixture 위임 승인 계열(모두 lap640~659에서 해소·G5
  드래그50 PASS로 종결)과 G4 W1/G2 Q12 관련 개별 위임 승인들이다.
- [ ] 2026-09-25 KST **G2 S5′ 3단 재제출 — 사용자 3단 확정 대기(Q12는 위임 결정 A·나·iv, 부록 B로 제출 확정).** 제출문 `../reports/20260925_G2_S5P_MILESTONE_RESUBMISSION_LAP589.md`. 결합 후보 `dfdc91ad…3883`의 혼합 24k·144k·판별형 저장/로드·F4 raw ACCEPT. 화면 미검증(W49/W49R REJECT, N214), S4 멀티 `UNKNOWN(harness_contract)`+Wine9.0 SP blocker, 교전 제외. G2 합격 아님.
- [x] 2026-09-24 23:05 KST Q11: Q11-2 **(나)** 사용자 선택, Q11-1 사용자 위임→**(A)** 부분 증거 인정(G2 PASS 아님, 남은 조건 1~7 유지).
- [ ] 2026-09-24 21:57 KST **G2 S5 3단 제출 — 사용자 판정 대기(Q11).** 제출문 `../reports/20260924_G2_S5_MILESTONE_SUBMISSION_LAP567.md`. 모델 판정: 부분 증거(W21·W26·W44R 24k 안정 동작) + W44R B4 FAIL(`REJECT`, N208) + 미충족 7항. G2 합격 아님.
- [x] 2026-09-24 19:02 KST 사용자 판정 Q10: **(마)** 도구 수리 후 fresh 1회, 실패 시 **(다)** 교전 트랙 중단(재질문 없음).
- [x] 2026-09-24 14:31 KST 사용자 승인: W42 op9용 가드 `op > 9` 확장과 op8 계약 핀 테스트 기대값 갱신(해당 1개 테스트만).
- [x] 2026-09-24 03:15 KST 사용자 판정: **S1 교전 = (라)** 원본 이동 명령 후 op8 공격 2단 입력. (가) AI 변경·(나) 사람 슬롯·(다) 중단 미선택.
- [x] 2026-09-23 18:43 KST 사용자 판정: **Q8 = (ㄱ)** — G2를 시딩 기반 cap 근접+안정 증거로 재정의. (ㄴ) AI 변경·(ㄷ) 보류 미선택.
- [!] 기존QHD 시야 확장 후보는 G1 요구 미충족 — 사용자 피드백2026-09-10.
  근거: `../history/20260910_VISUAL_GOAL_CORRECTION.md`. 새1600×1200 구도 유지 결과로 재검수해야 한다.

## 확정 (사람만 적는다)

없음. 기존24k나 pytest 통과를 사람 승인으로 적지 않는다.

## 실행 승인 (사람 판정)

- 2026-09-23 04:13 KST — 사용자가 되물음 2건을 마감했다. 원문: "전비가 일시적으로 5000을 넘어 보이는 표시를
  허용하고, 32비트도 괜찮아".
  - **lap404 = (가) 확정.** 일시 `used+reserved` 초과 표시를 허용하고 **라이브 `used` ≤5000만
    강제**한다. 승인 범위는 판정 기준의 변경이며, 이것으로 G2 제품 합격·마일스톤 승인이 되는 것은
    아니다. N19 단서(지속 시간 owner당 수 분·초과 표본 216건·대조군 귀속 미증명)는 고지 후 승인.
  - **F4 = (B) 확정.** 전비 장부 **32-bit 확장**을 채택한다(저장포맷 변경 동반). (C) 도달성 실측
    선행은 기각됐다. 착수 범위·순서는 strategy/middle이 카드로 정하며 이 승인만으로 원본 패치
    실행이 허가된 것은 아니다.
  - **여전히 사용자 전권 대기: Q7-A=(ㄴ) AI/설정 변경 예외 · Q7-B 3단 마일스톤 · (ㄱ) · (ㄷ).**

- 2026-09-12 01:03 KST — 사용자가 "승인. 루프 계속 돌아"라고 명시했다.
  승인 범위는 G1 카드2 Stage B의 격리된 원본/1600×1200 후보 실제 비교를 **증거가 성립할
  때까지 bounded repair → fresh validation으로 계속하는 것**과 그 독립 검수다. 실패를 보존하지
  않는 무변경 blind retry는 금지하며, 각 수리 뒤 검증 run은 handoff의 exact-once/fresh 규칙을
  지킨다. R5처럼 Stage B가 무엇을 증명하는지 조이는 변경은 포함한다. 제품 G1 합격·출시 승인,
  P6 착수, G2~G4 승인은 포함하지 않는다.

## 반려 (사람이 적는다 → 다음 바퀴 최우선)

QHD 해석 반려는 위 색인에 보존했으며 최신1600×1200 목표로 반영했다.

## 제출 양식

마일스톤/목표, 후보SHA, 기준·후보 캡처, 실제 입력·부하조건, 1단 결과,
2단 판정자(실제 모델), 다른 점/허용 오차, 남은 위험, 사용자 판정.
스크린샷 파일은 공유temp에 두고 해시/경로를 함께 남긴다.
- **G5 lap673~lap689 bisection 경과 압축(2026-09-26 10:31~20:23, 원문 18줄, SHA256 `4b7d2e030abb6ec8f2504c121da8d9ab97db16a09801de7f552b5ea9ed6e4194`):** 전문은 `docs/history/20260927_approvals_g5_bisection_block_precompaction.md`에 보존. G5는 아래 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 최종 승인·종결됐다.
- **2026-09-26 21:54 사용자 판단(AskUserQuestion 응답):** "G5 승인, 다음은 G2 10000". **G5(드래그 선택 20→50)는 단일플레이 milestone 승인**(v3 후보 `e5004764…`; 멀티 동기화는 미확인 — 명령 1건이 20기 단위 최대 3회 발행, 패킷 최대 3배 — 메모로 유지). G5 최우선 지시는 종료. **다음 우선순위: G2 — 활성8인 각각 전비10000 안정 플레이**(DESIGN.md G2, 5000 단계 달성). lap690(주석 정정)이 끝나면 다음 work는 G2 10000 첫 단계(전비 상한 5000→10000 후보 구현 후 8인 실행, 개인 개체 상한1200·전역 풀10,000 병목 측정)부터 구현 우선으로 진행.
- **2026-09-26 22:52 사용자 결정(AskUserQuestion 응답): 원본 게임 기준 경로를 `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus/`로 전환.** 보호 원본 EXE는 그 안의 `[HQ]Syw2plus 2002.exe`(SHA `b56986e0…`, 기존과 동일). 새 경로도 원본/참고 저장소와 같이 **읽기 전용**. 이전 측정은 그대로 보존, 이후 작업부터 새 경로 사용. **다음 work의 첫 작업(G2 10000보다 먼저):** ① `tools/runtime_env.py` `DEFAULT_SOURCE`를 새 경로로 바꾸고, 원본 EXE를 파일명 대신 **SHA `b56986e0…`로 찾아** 격리 사본 안에서는 기존 이름 `syw2plus_original.exe`로 두도록 수정(`ORIGINAL_EXE` 사용처 호환 유지), ② `tools/check_setup.py:51`, `tools/g4_path_fixture_preflight.py:141~144`, `checks/safety.*`의 원본 SHA/경로 불변 검사 대상에 새 경로 포함, ③ 관련 테스트 갱신 후 `make check`, `checks/safety.sh check`, 새 경로 기준 `runtime_env.py prepare` + 부팅 스모크 1회. 새 경로의 `Data`/`config.hq`/맵이 옛 경로와 다르면 차이를 기록. 끝나면 G2 전비10000 계속.
- **2026-09-27 00:05 운영자 판정(lap694 승격 해소, strategy 대행):** (b) **전역 풀 확장**을 채택. (a) 고비용 타입으로 우회해 10000을 채우는 것은 실제 플레이(전비10000이면 유닛 수가 많아짐)를 대표하지 않아 기각. 다음 work: 이미 실전 검증된 G2 ESL 계열 풀 재배치(`patches/population/g2_esl2608_pool4092_owner500.py`/`g2_esl2606_pool4092_owner500.py`, 개인500·공용4092, 초상화 슬롯 수정 포함)를 **보호 원본(b56986e0) 기준 전비10000 후보에 이식**(구현 우선) → lap694 8인 probe 재실행으로 owner0~7 전원 `used=10000` 확인 → 저장/로드 1회. 개인 상한이 1인 10000 도달에 부족하면 500→1250 등 필요한 값으로 올리되 8×개인 ≤ 풀 조건 유지.
- **2026-09-27 01:05 운영자 지시(lap696 후속, middle 전 1바퀴):** 전역 유닛 열거(`global_live_count`/active_slot_list 등)를 G2 pool4092 6-영역 재배치 주소로 고쳐, 8인×10000 fixture에서 **전역 live=1248(8×156)**, 슬롯 중복 0, owner별 count 합=전역 live, 저장/로드 전후 동일을 raw로 확인. 끝나면 G2 전비10000 후보를 middle 독립 검수로 승격.
- **2026-09-27 01:39 운영자 확인(lap698 수용, A/B는 사용자 판단 요청 중):** lap698 조건부 부분 PASS/HOLD 수용. 00:05 판정의 '고비용 우회 기각'과 충돌하는 점 인정 — 12비트 슬롯 한계(전역 ≈4095, 1인 평균 ≈511기)로 평균 비용<20 군대는 8×10000 불가. (A)/(B) 결정 전까지 work는 lap698이 지정한 EXE 무변경 하네스 확장만 수행: ① 비용 섞인 현실적 군대(중앙값 비용 근처 구성)로 1인·8인 상한 실측, ② 저장 후 상태 변경→로드→복원 확인, ③ 수천 tick 진행 후 전역 1248기·중복0 재확인(가능하면 전투 포함), ④ lap695/697 브리지 SHA 기록 불일치 정정.
- **2026-09-27 03:21 사용자 판단(AskUserQuestion 응답):** "현 한계 인정. 전비 상한 10000은 포기하고 기존 전비 상한 5000으로 만족". **G2 목표를 전비5000(달성 판단 유지)으로 되돌리고 10000 트랙 종료.** 10000 후보(lap691~699, `g2_supply10000_*`)와 증거는 보존만 하고 더 진행하지 않는다. A/B 판정 대기 해소. **다음 우선순위(운영자 결정): G4 — 길찾기/자유대전 AI**(STATUS 표: AI 개선 제품 비교·post-load·사용자 승인 미충족). 다음 work는 G4의 마지막 미충족 항목 중 post-load(저장/로드 후 AI 개선 유지) 확인부터 구현 우선으로 진행. G1은 그 다음.
- **2026-09-27 06:05 운영자 지시(lap704 BLOCKED 후속):** 새 probe의 fixture 19기는 1틱도 안 움직였지만, **lap682 `tools/g5_worker_relative_move_attack_probe.py`는 원본 20/20 이동 수렴을 2/2 재현**했다(같은 원본 EXE). 원인을 새로 추측하지 말고 **lap682 probe의 fixture 생성·드래그·우클릭 절차를 그대로 재사용**(차이는 목적지 거리와 궤적 기록만 추가)해 원본 20기 원거리 이동 baseline 3회를 측정한다. 두 probe의 fixture 차이(유닛 type·소유자·스폰 방식·보정 단계의 9회 우클릭 여부)는 1줄 diff로 기록. 목적지는 실제 렌더 영역 안(또는 미니맵)으로.
- **2026-09-27 07:45 운영자 판정(lap706 승격 해소, strategy 대행):** (a) 채택 — 대표 baseline scene은 worker world **(93,56)**(8/8 재현 20/20 명령 도달). (10,49)는 명령 도달 자체가 0인 입력/지형 문제라 길찾기 지표에서 제외하고 사유만 기록(c는 후순위). 다음 work: (93,56) scene에서 **길찾기 약점이 드러나는 조건**으로 원본 baseline N=3 확보 — 거리 20타일 이상(미니맵 또는 카메라 이동 후 클릭) 및 장애물/좁은 통로를 끼는 목적지 1개씩, 지표는 도착률·도착 tick 분포·path_ratio·정체(stagnation) 유닛 수. 가장 나쁜 지표 1개를 G4 개선 후보의 목표로 STATUS에 적는다.
- **2026-09-27 08:55 운영자 판정(lap707 후속, 구현 우선):** 측정 하네스 보강은 여기서 멈추고 **G4 길찾기 개선 후보 v1 구현**으로 넘어간다. 1차 지표는 lap707이 정한 obstacle_row(world 93,56) `path_ratio_max`(원본 최대 2.540) + 도착률. work: ① 원본 길찾기 함수(경로 탐색 노드/스텝 예산, 우회 한도, 재탐색 주기 상수)를 정적으로 특정 — 기존 G4 기록(`docs/history/laps/*g4*`, `analysis/memory_maps/*path*`) 먼저 재사용, ② 상수 1~2개(예: 탐색 예산/우회 한도 상향)를 바꾼 후보 v1을 빌드, ③ obstacle_row 원본 N=3 대 후보 N=3 paired로 path_ratio·도착률 비교, 크래시 0 확인. 원거리 팬 복귀 문제는 후순위(미니맵 우클릭 전환은 후보 비교가 나온 뒤).
- **2026-09-27 10:45 운영자 판정(G4 가설 2회 소진 — v1 재시도 한도, v2 탐색 마진 모두 원본과 동일):** obstacle_row(8타일)는 원본도 path_ratio≈1.93·도착 14~18/20으로 개선 여지가 작다. **목표 지표를 원거리 도착률로 전환**(lap707: 33~35타일에서 원본 도착 평균 ≈49%). 다음 work: ① 원거리 명령을 **미니맵 우클릭**으로 발행해 카메라 팬 복귀 문제를 우회(lap707 BLOCKED 해소), world(93,56)에서 원본 N=3, ② 미도착 유닛별 원인 분류(정체 위치·마지막 명령 상태·유닛 간 충돌/대기열 정체 vs 경로 실패)를 raw로 집계, ③ 가장 많은 원인 1개를 v3 가설로 STATUS에 기록(구현은 다음 lap).
- **2026-09-27 12:05 운영자 판정(G4 길찾기 트랙 종료, lap711 관측 반영):** 측정시간 ≈165s로 늘려도 원거리 도착 13/20 불변 — 미도착 7기는 정체/충돌 0·목적지 3~5타일 앞 정지로, 20기 밀집 도착 시 도착반경(3타일) 밖에 서는 **정상 군집 정지**로 본다. v1/v2 반증과 합쳐 **원본 길찾기에는 개선할 뚜렷한 결함이 측정되지 않음**으로 기록하고 길찾기 후보 트랙을 닫는다(보존만). **G4 다음 대상: 자유대전(스커미시) AI.** 다음 work: ① 기존 G4 AI 계측(`tools/inmm_stub/ai_shadow.c`, lap700~703 post-load 확인)을 써서 원본 AI 1~2명 대 1 자유대전을 N분 진행하며 AI 행동 지표(자원 수입·생산량·군대 규모·첫 공격 시각·유휴 일꾼 수)를 원본 N=3 측정, ② 가장 약한 지표 1개를 AI 개선 후보 v1 목표로 STATUS에 기록, ③ 가능하면 같은 lap에서 상수 1~2개짜리 후보 v1까지 구현(구현 우선).
- **2026-09-27 13:05 운영자 판정(lap712 v1 목표 조정):** 기준선 3/3 재현 수용. 단 v1 목표는 효과 크기가 큰 쪽으로 바꾼다 — owner0 유휴 일꾼 평균 0.68은 작고, **owner1(nation2) AI가 280초 동안 자원 23,068을 쓰지 않고 쌓으며(+1,734/분) 생산 12·군대 10으로 owner0(생산 21·군대 16)보다 약하다.** v1 = **AI 자원 소비(생산 결정) 개선**: 원본 AI 생산 결정 루틴에서 생산을 막는 조건(자원 보유 임계값, 동시 생산 큐 수, 건물당 생산 한도, 결정 주기 등)을 정적으로 찾아 상수 1~2개를 바꾼 후보 v1을 만들고, 같은 fixture로 원본 N=3 대 후보 N=3 paired 비교(지표: owner1 쌓인 자원↓, 생산 수·군대 규모↑, 크래시 0). 유휴 일꾼은 보조 지표로 계속 기록.
- **2026-09-27 13:45 운영자 관찰/방향(lap713 v1 H-CROWD 7→14: 후보 3/3이 원본과 바이트 수준 동일 지표 — 무효과):** 추측으로 상수를 더 바꾸지 말고 **라이브로 어느 게이트가 owner1 발주를 막는지 계측**한다. 다음 work: 원본 fixture에서 `FUN_00406B00`/`FUN_0043E7F0`의 각 거부 분기(G-1~G-8, H-TYPEMAX/H-RATIO 포함)에 non-invasive breakpoint(또는 ai_shadow 카운터)를 걸어 280초 동안 **owner별 거부 사유 히스토그램**을 raw로 수집 → 최다 거부 게이트 1개를 v2 대상으로. H-TYPEMAX/H-RATIO가 최다면 그 표의 런타임 값(Data에서 채워진 값)을 읽어 기록하고, 표를 채우는 코드/데이터 쪽 수정 후보를 v2로.
- **2026-09-27 14:45 운영자 방향(lap714 거부 히스토그램 반영, 다음 work):** 280s 원본에서 H_CROWD/H_TYPEMAX/H_RATIO=0, owner1 거부는 **PREREQ_OWN 692**(선행 건물 미보유; HQ type58의 kind102/98 등)와 H_AVAIL 620이 전부. ⇒ 병목은 유닛 발주 게이트가 아니라 **AI가 선행 건물을 짓지 않는 것(건설/테크 진행)**. v2: ① AI 건설 결정 루틴(건물 발주 함수·건설 우선순위 표/조건)을 정적으로 특정하고 같은 방식으로 **건설 거부 사유 히스토그램**을 owner별 raw 수집, ② owner1이 선행 건물(PREREQ 대상)을 못 짓는 최다 사유 1개를 상수 1~2개로 완화한 후보 v2, ③ 원본 N=3 대 v2 N=3 paired(지표: owner1 선행건물 보유 시각, PREREQ_OWN 거부 수↓, 생산·군대↑, 쌓인 자원↓, 크래시 0). 보조: WOULD_ACCEPT=0 기록이 샘플 시점 문제인지 확인해 계측 신뢰성 한 줄 기록.
- **2026-09-27 15:12 사용자 지시:** "4번 - 길찾기 및 AI는 일단 보류하자. 지금까지 작업분 커밋해서 리모트 깃헙에 푸시하고, 1번 - 원본과 같은 화면 구성인데 고해상도인 것을 최우선으로 해봐". **G4(길찾기·자유대전 AI) 보류**(lap715 건설 게이트 계측은 중단, 도구·기록 보존). 작업분은 운영자가 커밋·푸시(루프의 `LOOP_ALLOW_COMMITS=0`은 유지). **G1 최우선: 원본과 같은 화면 구성(UI 배치·비율·보이는 범위의 구도)을 유지하면서 1600×1200 고해상도로 렌더.** 다음 work는 기존 G1 기록(`docs/history/laps/*g1*`, `analysis/memory_maps/*g1*|*resolution*`)으로 현재 상태·막힌 지점을 먼저 요약하고, 구현 우선으로 가장 작은 다음 후보를 만들어 격리 실행 캡처로 원본(800×600) 대비 구도 동일성·HUD 배치·깨짐 여부를 확인한다.

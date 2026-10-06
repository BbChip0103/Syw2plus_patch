# G1 W70 P4b-S — B' 상태 비교의 표본 시점 수리: host live read → in-process 완료-phase snapshot (lap892 strategy, 2026-10-03)

- 발행: lap892 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, `LOOP_ASTRA_EFFORT=high`, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap891 middle의 `HOLD_PHASE_ATTRIBUTION_UNPROVEN` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261003_lap892_prior_lap891_escalate_sol_archive.md`).
- 입력 근거(이 세션이 직접 읽고 재계산): lap868·876(r1~r3)·890 pair raw, lap874(r5~r11)·lap888 완료-phase raw, lap890·891 기록,
  P4b 카드, 현재 `tools/g1_saved_scene_probe.py`, 보호 원본 read-only disassembly. 재계산은 공유 temp
  `20261003_lap892_strategy_review/`(`timeline.py`/`bracket.py`와 JSON), 주소는
  `analysis/memory_maps/g1_p4b_update_callsites_inprocess_snapshot_lap892.md`.
- 이 카드는 P4b 카드(`G1_STRATEGY_W70_P4B_TERRAIN_CACHE_LAYER_LAP863.md`)의 **B'-6(입력 parity)의 상태 비교 표본 방법만** 구체화한다.
  P4b 카드의 A·B'-1~5·C·D·§7과 임계값(55%/30%/0.9), validator는 그대로다.

## 0. 판정 요약

1. **lap890의 final tick24861 차이는 시뮬레이션 발산의 증거가 아니다. 측정기가 찢어진 상태를 읽었다(candidate lane은 확정).**
   candidate final snapshot은 owner2 `count=95`인데 owner2 유닛은 96개가 살아 있다. 이 조합은 완료-phase snapshot 22개
   (lap874·lap888) 어디에도 없고, live snapshot 30개 중에서도 이 하나뿐이다(§1.2). player 블록과 unit pool을 서로 다른 순간에
   읽었고 그 사이에 게임이 진행했다.
2. **원인은 구조적이다.** gdb 없는 B'는 host가 1ms 간격으로 tick을 보다가 목표 tick이 되는 순간 실행 중인 프로세스를 3ms 동안
   읽는다(`_wait_for_exact_tick` → `_read_batched_scene`). 목표 tick이 보이는 순간은 그 tick의 update가 **진행 중**인 때다.
   tick 앞뒤가 같다는 `coherent`는 원자성을 뜻하지 않는다. 지금까지 live pair 5개 중 3개(lap868, lap876 r1, lap890)가 HOLD였고,
   완료-phase에서 잰 비교(lap874·lap888)는 한 번도 어긋나지 않았다.
3. **lap891이 제안한 "lap890 일정 전용 GDB 완료-phase triplet"은 다음 단계로 채택하지 않는다.** 그 진단이 PASS해도 B'는 다시
   같은 live 표본으로 재야 하고, 다시 깨질 수 있다(지금까지 5회 중 3회). 일정 지원·nonce·census 장치를 한 벌 더 만드는 비용만 든다.
4. **수리 = 표본 시점을 게임 스레드의 update 반환 지점으로 옮긴다(P4b-S).** 진단 DLL이 `call 0x41C770` 두 호출 지점을 감싸,
   원본 호출이 반환했고 그 사이 tick이 목표 값으로 올라갔을 때 같은 메모리 범위를 프로세스 안에서 복사해 파일로 남긴다.
   gdb 없음, EXE 파일 불변, 게임 데이터 쓰기 없음. tick이 올라간 호출의 반환은 lap874·lap888이 GDB로 관측한 `0x41C961` return과 같은 지점이다.
5. **비교 기준은 한 글자도 완화하지 않는다.** 비교 필드·완전 일치 요구·checkpoint 3개는 그대로이고, 바뀌는 것은 표본을 뜨는
   시점과 주체뿐이다. 조건은 오히려 늘어난다(§3 E2·E3). lap890 pair는 `HOLD`로 남으며 PASS로 바꾸지 않는다.
6. **B'의 tick 일정은 고정 절대 일정 r1(`SCROLL_PHASE_TICK_PLAN`: 24692/24728/24788/24824/24860)을 쓴다.** 이 5개 tick에는
   lap888의 독립 수용된 완료-phase 상태가 있어, 새 표본기가 맞는지를 lane 간 비교와 별개로 대조할 수 있다(§3 E3).
7. **관측 장치 범위 한정(§5).** lap868 이후 회차는 대부분 관측 장치와 그 검수에 쓰였다(STATUS 바퀴 기록). 이후 G1 단계의 상태 비간섭
   gate는 이 in-process 표본 하나로 통일하고, 새 관측 장치·raw 변이 내성 강화는 실제 실행 불일치가 나왔을 때만 strategy가 연다.
8. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. 근거

### 1.1 한 궤적 위의 서로 다른 시점 (owner2 `[rice,reserved,count,used]`, owner6 rice, unit145 y, 유닛 수)

| tick | 종류 | 출처·lane | owner2 | owner6 rice | u145 y | 유닛 |
|---|---|---|---|---|---|---|
| 24860 | 완료-phase | lap888 baselineA·B·candidate (셋 동일) | 300830, 130, 95, 1423 | 231007 | 37 | 572 |
| 24861 | live | lap890 baseline | 300430, 117, 96, 1436 | 230207 | 38 | 573 |
| 24861 | live | lap890 candidate | 300830, 130, **95**, 1423 | 230607 | 37 | **573** |
| 24862 | 완료-phase | lap874 r9·r10(baseline)·r11(candidate) (셋 동일) | 300830, 117, 96, 1436 | 231007 | 38 | 573 |
| 24862 | live | lap868 baseline / candidate | 둘 다 300830, 117, 96, 1436 | 230207 / 231007 | 38 | 573 |
| 24862 | live | lap876 r2·r3 양 lane | 300830, 117, 96, 1436 | 231007 | 38 | 573 |

- lap890 두 lane이 다른 6개 필드(owner2 rice/reserved/count/used, owner6 rice, unit145 y) 가운데 owner2 reserved/count/used와
  unit145 y는 candidate=완료24860 값, baseline=완료24862 값이다. 두 lane은 같은 변화의 앞과 뒤를 읽었다.
- 쌀 3개 값(baseline owner2 300430, owner6 230207 / candidate owner6 230607)은 양쪽 완료값(300830, 231007)과 다르다. 400 단위로
  내려갔다가 24862 완료 때 되돌아와 있는 일시값이다. owner6은 231007 → 230607 → 230207 → 231007 순으로 읽힌다(여러 실행을 이은
  추론). lap868 baseline이 24862에서 읽은 230207도 같은 값이다. lap868의 800 차이와 lap890의 400 차이는 같은 변동의 다른 순간이다.
- 완료 24860과 24862 사이에 바뀌는 필드는 33개다. lap890 baseline은 6개가 24860 값·27개가 24862 값, candidate는 10개·23개이고
  둘 중 어느 쪽도 아닌 값은 없다. 그 33개 밖에서 양 lane이 **똑같이** 24860과 다른 필드가 14개 있다(유닛 240·579·1011·1165
  (owner6), 615·652·1026(owner2)의 `command 1→15`와 `production_type`). 쌀의 일시 감소와 같은 tick의 생산 명령으로 보이지만
  비용 대응은 확인하지 않았다(가설).
- 한계: lap890 실행 안에서 tick24861의 완료 상태를 직접 잰 값은 없다. baseline lane의 읽기가 완료 뒤였는지는 증명되지 않았다.
  위 표는 "차이가 표본 시점으로 전부 설명된다"는 것이지 "24861 완료 상태가 두 lane에서 같았다"는 직접 측정이 아니다. 그 직접
  측정이 §2~3의 일이다.

### 1.2 불변식 전수 (player `count` = 그 owner의 살아 있는 유닛 수, 8 owner 전부)

| 표본 | 개수 | 위반 |
|---|---|---|
| 완료-phase (lap874 r5~r11 7개, lap888 3 lane × 5 checkpoint) | 22 | 0 |
| live (lap868·876 r1~r3·890, 각 2 lane × 3) | 30 | **1** — lap890 candidate tick24861, owner2 `count 95` / 유닛 96 |

새로 생긴 유닛은 slot24(owner2, type3, internal_id 655384)다. 이 불변식은 표본기의 건전성 검사로 §3 E2에 넣는다.

### 1.3 host에서 완료 경계를 잡을 수 없는 이유 (정적)

`0x41C770`은 tick store `0x41C8C9` 앞에서 최대 7개 함수를 부르고(상태를 쓰는지는 읽지 않았다) 뒤에서 player 처리 `0x41CB40`을
부른다. 적어도 tick 값이 바뀐 직후는 그 tick의 update가 진행 중인 때다. present 기록을 기다렸다 읽는 방식도 다음 호출의 tick store
앞 구간과 겹칠 수 있다. 호출이 끝난 시점을 아는 것은 게임 스레드뿐이다.

## 2. P4b-S work 범위 (한 lap, 구현→빌드→격리 실행→원인 수리 반복 최대 3회)

공통: 기본 OFF opt-in, env는 초기화에서 latch, EXE 파일 불변, old bytes 대조 후 설치·불일치 시 전체 rollback, save006 same-save
fresh pair, private 사본·prefix·Xvfb, 실행 후 game 사본 삭제, 기존 raw 덮어쓰기 금지.

### A. DLL (새 파일 권장, 예: `tools/inmm_stub/g1_state_snapshot.c`)
1. env `SYW2_G1_STATE_SNAPSHOT_TICKS`(쉼표 구분, 최대 8개)와 출력 디렉터리. 비어 있으면 **설치하지 않는다**.
2. 호출 지점 2곳(`0x4245D2` `e8 99 81 ff ff`, `0x4250F7` `e8 74 76 ff ff`)의 rel32를 wrapper로 돌린다. 기존 P4b 이동 8지점과 같은
   방식이다. wrapper는 레지스터·플래그를 보존한다(원본 호출 → `pushfd/pushad` → C 함수 → 복원 → `ret`).
3. C 함수: 호출 전 tick과 호출 뒤 tick이 다르고 호출 뒤 tick이 목표에 있으면, 메모리 맵 문서의 6개 범위를 미리 잡아 둔 버퍼로
   복사하고 헤더(magic·version·run id·pid·thread id·호출 지점·tick 전/후·순번·QPC)와 함께 임시 파일에 쓴 뒤 이름을 바꾼다
   (`state-<tick>.bin`). 한 호출에서 tick이 2 이상 뛰면 `tick_jump`로 기록한다. trace JSONL에 한 줄 남긴다.
4. 금지: 게임 데이터 쓰기, 목표 tick 밖의 파일 쓰기, mirror/HD 경로 변경, validator·임계값 변경, 새 의존성, 커밋.

### B. host (`tools/g1_saved_scene_probe.py`·테스트만)
1. `_read_batched_scene`의 해석부를 순수 함수로 떼어 live 경로와 파일 경로가 **같은 함수**를 쓴다. 필드 추가·삭제 없음
   (합성 버퍼로 분리 전후 출력 동일 테스트).
2. `--terrain-scroll` 양 lane: tick 일정 = `SCROLL_PHASE_TICK_PLAN`(절대). 로드 tick이 늦어 일정에 못 맞추면 그 pair는 `INVALID`.
   5개 tick 모두 snapshot을 받고, gate 입력은 지금처럼 관측 2개 + final 1개다. snapshot 파일이 없거나 크기·헤더가 틀리면 `INVALID`.
3. gate가 쓰는 `scene_snapshot`/`final_scene_snapshot`의 state는 in-process 파일에서 온다(`source: in_process_update_return`).
   기존 live read는 `live_scene_snapshot`으로 **계속 기록**하고 in-process와의 차이를 `live_vs_inprocess_diff`로 남긴다(gate 아님).
4. `_terrain_scroll_pair_parity`의 기존 조건은 그대로 두고 조건만 더한다: source가 in-process일 것, 헤더 tick=목표, `tick_jump` 없음,
   lane 안에서 thread id 동일, §1.2 불변식 성립. 입력 tick·키 순서·camera·coverage 조건은 손대지 않는다.
5. `--reference-completed-states <json>`(선택 인자): 주어지면 각 lane의 5개 snapshot을 그 파일의 같은 tick 상태와 비교해
   `sampler_reference_check`로 기록한다. 첫 검증 실행에서는 lap888 결과
   (`20261003_lap888_p4b_scroll_phase/scroll-phase-diagnostic-result.json`, SHA256
   `02b5e67762b4bb260fa800f121af7628c03d56687374c9eed524200ebc2fbb72`)의 baselineA를 준다.
6. Fast 회귀 가드: 호출 지점 2곳 주소·old bytes, 헤더 해석·크기 검증, 파일 누락/잘린 파일/다른 run id/다른 tick → `INVALID`,
   불변식 위반 → gate 불성립, lap890 candidate final 상태를 넣으면 불변식 검사가 잡는지(실제 raw 사용).

## 3. 사전 등록 기대값

| # | 기대 | 어긋나면 |
|---|---|---|
| E1 | 양 lane 모두 호출 지점 2곳 old bytes 일치·설치, crash 0, source unchanged, cleanup | 구현 결함 → 수리 후 재실행 |
| E2 | lane마다 snapshot 5개, 헤더 tick=목표, `tick_jump` 0, thread id 동일, 불변식 8 owner 전부 성립 | 누락·tick 놓침은 `INVALID`(수리 후 재실행). **불변식 위반은 표본 경계가 틀린 것** → §4-2 |
| E3 | baseline lane의 5개 snapshot = lap888 baselineA의 같은 tick 완료 상태 (차이 0) | §4-2 |
| E4 | pair `complete_records_equal=true`(24728·24824·24860), 나머지 B'-1~6은 P4b 카드 그대로 | §4-3 |
| E5 | `live_vs_inprocess_diff`는 0이 아닐 수 있다(찢어진 읽기의 실측 빈도). 기록만 한다 | — |

**B' PASS = 같은 명령의 fresh pair 2회가 연속으로 E1~E4를 만족.** 여러 번 돌려 좋은 것을 고르지 않는다. `INVALID`는 원인을 적고
세지 않는다. 유효한 pair의 E4 불일치는 다시 돌려서 지우지 않는다.

## 4. 판정·정지 규칙

1. E1 실패·`INVALID`: 추적 가능한 하네스 결함이다. 같은 lap에서 고쳐 다시 실행(최대 3회). 그 뒤에도 원인을 못 대면 승격.
2. E2 불변식 위반 또는 E3 불일치: 표본 경계(다른 스레드의 쓰기, `0x4250F7` 경로, 두 실행 간 비결정성) 문제다. 수리하지 말고
   처음 어긋나는 tick·필드와 thread id를 남겨 strategy로. 이때만 lap891 제안(GDB 완료-phase 대조)이 대안으로 살아난다.
3. E4 불일치(E1~E3는 성립): 이제는 완료-phase에서의 실제 차이다. work는 같은 lap에서 목표 tick을 촘촘히 늘려(최대 8개씩) 양 lane의
   **처음 갈라지는 tick과 필드**를 좁힌 뒤 strategy로 승격한다. 제품 DLL을 추측으로 고치지 않는다.
4. B' PASS → middle이 직접 PASS/HOLD 판정(P단계는 마일스톤 경계가 아니다). PASS면 다음 work가 C → D-1 → P5.
   C(성능, 계측 OFF)에서는 snapshot env를 주지 않으며 설치되지 않았음을 raw로 확인한다.

### middle 검수 조건 (work PASS 주장 시, 이 목록으로 한정)
- 호출 지점 2곳 old bytes·rollback, wrapper의 레지스터 보존, 복사 범위 6개가 메모리 맵 문서와 같은지, 게임 데이터 쓰기 없음.
- 해석 함수가 live 경로와 같은 함수인지, 비교 필드가 줄지 않았는지, `_terrain_scroll_pair_parity`에서 빠진 조건이 없는지.
- pair 2회의 snapshot 파일 SHA·헤더(run id·pid·tick·thread id)와 결과 JSON 대조, E2·E3·E4 독립 재계산.
- coverage·validator·layer 계수·입력 parity는 P4b 카드 middle 조건 그대로. DLL/raw/pair SHA·build 입력, source unchanged·cleanup.
- 검수가 pair gate의 **실제로 일어날 수 있는** 오수용 경로(이전 실행 파일 혼입, 잘린 파일, 다른 tick)를 찾으면 승격하지 말고
  work에 바로 수리 인계한다. 손으로 고친 raw를 gate가 걸러내는지는 이 검수의 합격 조건이 아니다(§5).

## 5. 관측 장치 범위 한정

- 하네스가 막아야 하는 것은 **정직한 계기 오류**(경합, tick 놓침, 묵은 파일, 다른 프로세스)다. 누군가 raw를 고쳐 넣는 경우를
  gate가 닫는 것은 목표가 아니다. raw·결과는 SHA로 고정하고 다음 세션이 원본에서 다시 계산하는 것으로 충분하다.
- lap880~889의 GDB pause/nonce/census 진단과 그 negative control은 그대로 보존하되, 이후 P단계 전환의 선행 조건이 아니다.
- 새 관측 장치를 만들거나 기존 장치의 변이 내성을 늘리는 회차는 §4-2·§4-3처럼 실제 실행에서 설명 안 되는 차이가 나왔을 때만,
  strategy 판정을 거쳐 연다.

## 6. 남은 위험

- 다른 스레드가 sim 상태를 쓰지 않는다는 것은 lap874(쌀 write thread 1)·lap888(all-stop census) 관측에 기대고 있다. in-process
  복사는 all-stop이 아니다. E2·E3가 이 가정을 실행으로 시험한다.
- E3는 실행 간 결정성에 기댄다. 근거는 lap874 4회(24638)·3회(24862), lap888 3 lane 일치다. 로드 tick이 24570~24574로 흔들려도
  절대 tick의 상태는 같았다. 깨지면 §4-2다.
- snapshot 한 번에 약 2.4MB 복사와 파일 쓰기가 게임 스레드에서 일어난다. 그 프레임의 present 간격이 늘 수 있다. coverage 30 present
  창과 겹치면 수치가 달라질 수 있으나 기준은 바꾸지 않는다(미달이면 P4b 카드 §7-3).
- `0x4250F7` 호출 지점이 어떤 모드에서 쓰이는지 읽지 않았다. 둘 다 감싸므로 안전하지만 미확인이다.
- 측정은 Xvfb/Wine·save006 한 장면이다. C 성능, D-1 PS3 census, HUD/tinted/GDI, 전체 HD coverage ≥90%, 두 번째 장면,
  사용자 3단 승인은 미충족이다. minimap/production `UNKNOWN(original parity)` 유지.

## lap894 work execution record (2026-10-03; independent middle review pending)

- The lap893 pre-runtime safety handoff was applied: exact 5-byte rel32 ownership checks guard rollback/detach; writes require successful `VirtualProtect`; rollback flushes the instruction cache and retries protection restoration; the six-range 2,378,704-byte payload is allocated once at install. Both compiled naked wrappers were disassembled: instrumentation saves/restores registers and flags, invokes the original update through a direct indirect call with no C thunk, then returns with the original no-argument stack balance.
- Fresh paired invocations 1/2 exposed two tracked harness defects: conditional `inprocess_snapshots` initialization (`UnboundLocalError`) and a pair gate reading snapshot fields from the wrong mapping level. Both were fixed. Pair3 and pair4 then independently satisfy E1-E4 in sequence. Details, raw hashes, per-lane headers and independent recomputation are in `docs/history/laps/20261003_lap894_work_g1_p4bs_runtime_pair_pass.md` and `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap894_independent_recalc.json`.
- Each passing pair used fresh private complete game copies, prefixes and Xvfb displays with the non-synthetic save006 fixture. Baseline and candidate each recorded ticks 24692/24728/24788/24824/24860 on one thread; all 8-owner count invariants passed; all baseline states matched lap888 references and all baseline/candidate full-state diffs were zero. Source EXE SHA was `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate game copies were removed and no prefix process remained.
- Original file old bytes at offsets `0x245D2` and `0x250F7` matched the pinned five-byte calls. No EXE candidate was generated, so binary copy/restore/non-overlap patch checks are not applicable to this in-process DLL instrumentation. Install/detach failure injection for OS API errors was not run; rollback/protection/ownership branches have source-contract regression checks and remain for independent middle review.
- Focused probe tests: 127 passed. `make check` on the complete source and record set: exit 0, 1431 passed, 5 skipped in 894.31s; skips require unavailable pinned local stock/ESL references. Lint, compileall, mypy, context and safety passed. This is Fast/source evidence, not a runtime claim beyond these four captured executions.
- Work-tier P4b-S pair gate is PASS twice consecutively. B' remains pending new middle independent review; G1 and user milestone approval remain open. Next: middle independently checks wrapper ABI, install/restore ownership, pair3/4 raw and E1-E4. If accepted, proceed to C with snapshot instrumentation OFF.

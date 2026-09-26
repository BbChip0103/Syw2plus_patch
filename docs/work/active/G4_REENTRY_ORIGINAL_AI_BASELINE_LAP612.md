# G4 re-entry W1 — 현행 source 원본 AI baseline + mode/load 계약 고정

- 발행: lap612 middle. `loop/ESCALATE_SOL` §161과 lap611 strategy를 독립 검수한 뒤 발행한다.
- 단일 가설: 현행 source의 opt-in read-only AI shadow와 기존 `g1-baseline` 경로로, 새 private 원본 게임에서 PS3/tick/원본 AI 이동을 한 번에 관측할 수 있다.
- 목적: G4 제품/AI 패치 전에 현재 실행 경로가 살아 있음을 fresh 증거로 복구하고, 후속 mode/post-load 계약이 무엇을 증명해야 하는지 사전에 고정한다. 이 카드 통과는 G4 PASS, AI 개선, 지원 mode 확대, post-load 계약 해소가 아니다.

## 1. 범위와 금지

1. 다음 work(Luna/high)가 수행한다. 이 카드는 게임·제품·하네스 source를 수정하지 않는다.
2. 원본 EXE SHA는 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로 고정한다. 원본/참고 디렉터리는 읽기와 fresh private copy 생성에만 사용하고 직접 실행·쓰기하지 않는다.
3. current `tools/inmm_stub/_inmm.dll`을 source에서 새로 빌드해 private copy에만 넣는다. `INMM_AI_SHADOW=1`만 허용한다. shadow는 `0x0041CBE5`의 원본 call을 정확히 한 번 tail-forward하고 게임-owned field/issuer를 쓰지 않는 관측기다.
4. `--g4-chain-goal`, `--g4-candidate-exe`, `--g4-intervention-goal`, G2 lifecycle/stress, save/load, pixel write, EXE patch, AI/경로 변경, 새 의존성은 전부 금지한다. fixture는 `synthetic=false`, `control_bridge=false`, `resource_grant=false`인 default two-player random game이다.
5. 새 전체 게임 복사본·fresh prefix·빈 Xvfb display에서 foreground 동기 실행 **정확히 1회**만 한다. background 실행·기존 runtime 재사용·무변경 재시도는 금지한다.

## 2. 실행 전 gate와 명령 형태

1. 현재 source에서 아래를 통과시킨다.
   - `.venv/bin/python -m pytest -q tests/test_g4_ai_shadow.py`
   - `make -C tools/inmm_stub all`
   - `bash checks/safety.sh check`
2. `tools/runtime_env.py prepare`로 새 private manifest를 만들고 `check`로 `created_new=true`, 원본 SHA, symlink/hardlink 거부, private prefix/output을 확인한다. manifest·bridge·`tools/runtime_env.py`·`tools/inmm_stub/ai_shadow.c` SHA를 기록한다.
3. 다음 형태로 한 번 실행한다. `<fresh-manifest>`는 이번 work가 방금 만든 것만 허용한다.

```sh
INMM_AI_SHADOW=1 .venv/bin/python tools/runtime_env.py g1-baseline \
  --manifest <fresh-manifest> \
  --screen 1600x1200x24 \
  --timeout 90 \
  --g4-sample-seconds 180 \
  --g4-sample-period 1
```

4. CLI exit 값은 판정이 아니다. 과거처럼 뒤따르는 G1 input tail만 실패해도, 아래 G4 raw와 cleanup이 완전하면 그 tail 오류를 별도 보존하고 G4 baseline 식으로 판정한다. PS3/sample/shadow 전에 난 오류는 이 예외에 해당하지 않는다.
5. 시작 전/종료 후 원본 SHA와 `df -B1` 여유 공간을 기록한다. 과거 PS40/tick0 serious-error가 재발하면 screenshot/error/EIP/bridge/ddraw override/여유 공간을 보존하고 재시도하지 않는다.

## 3. 필수 raw

- fresh manifest와 prepare/check 출력.
- `output/g1_baseline.json`, `output/g1-baseline.log`.
- `prefix/drive_c/inmm_ai_shadow.jsonl` 원문. work summary가 아니라 이 JSONL로 판정한다.
- private EXE SHA, 원본 SHA 전후, bridge/source SHA, 실행 argv/env 중 `INMM_AI_SHADOW`, `DISPLAY`, `WINEPREFIX`, `WINEDLLOVERRIDES`.
- cleanup의 owned launcher/Xvfb/prefix process/global-kill 필드.
- 산출물 복사본은 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g4_ai/` 아래 새 `YYYYMMDD_HHMMSS_lap613_g4_reentry_original_baseline/`에 둔다. 메인 repo에 게임/PNG/EXE/DLL/save를 넣지 않는다.

## 4. baseline 사전 판정식

### `FEASIBLE_BASELINE`

아래가 모두 참이어야 한다.

1. **Identity:** private 실행 EXE와 원본 전후 SHA가 모두 `b56986e0…a8ac`; fresh manifest이며 candidate/chain/intervention/save/load 0회; fixture가 비합성 원본 baseline이다.
2. **진입/시간:** scene과 G4 sample이 PS3이고 첫 tick>0. 유효 sample이 150개 이상이며 tick 역행 0, `last_tick-first_tick >= 3000`이다.
3. **원본 AI 이동:** `players[owner].ai==1`인 owner의 동일 `(slot,internal_id,type,owner)` identity가 두 sample 이상 유지되면서 `(x,y)`가 한 번 이상 달라진다. 생성/소멸·생산 progress만으로 이동을 대체하지 않는다.
4. **정상 AI edge:** shadow row>0, 모든 row에서 `owner==(tick&7)`, `ecx_owner_match=true`, `original_call="forwarded_once"`, `same_tick_reentry=false`, fresh non-load run의 `tick_rewind=false`. AI owner row가 한 건 이상 있다.
5. **양성 mode raw:** 관측된 shadow row의 raw mode는 정확히 `PS=3`, `committed_local=1`, `scenario_selector=0`, `network_mode=0`, `network_modal=0`, `gate_a=0`, `gate_b=0`이다. 이는 양성 장면 증거일 뿐 음성 mode 배제의 런타임 증명은 아니다.
6. **정리:** `cleanup.ok=true`, owned launcher/Xvfb 종료, prefix residual `[]`, global kill false, 원본 불변이다.

### `NOT_FEASIBLE(default-random-movement-witness)`

- identity/PS3/tick/shadow/cleanup은 모두 정상인데 180초 동안 위 동일 identity 이동이 0건이면 이 fixture로는 이동 baseline을 만들 수 없다고 닫는다.
- 같은 default-random 실행을 반복하지 않는다. 다음 middle이 과거의 원본 seed1/save fixture를 재사용할 수 있는지 별도 판정하며, work가 임의로 fixture를 바꾸지 않는다.

### `BLOCKED`

- SHA/manifest/source 불일치, shadow 미설치·빈 raw·필드 누락, 양성 mode raw 불일치, same-tick 중복, fresh run tick 역행, PS3/tick 미진입, serious-error, cleanup 실패는 `BLOCKED(<원인>)`이다.
- 필수 build/test/safety가 예상 밖으로 실패해도 동일하다. 현재 변경과 raw를 보존하고 `loop/ESCALATE_SOL`에 넘기며 수리·재실행하지 않는다.

판정 우선순위는 `BLOCKED` > `NOT_FEASIBLE(default-random-movement-witness)` > `FEASIBLE_BASELINE`이다.

## 5. 비지원 mode 제외 계약

제품 후보가 허용할 수 있는 양성 집합은 아래 raw가 **모두** 정확히 맞는 local free-battle PS3뿐이다.

`PS==3 && committed_local==1 && scenario_selector==0 && network_mode==0 && network_modal==0 && gate_a==0 && gate_b==0`

다음은 전부 fail-closed 비지원이다.

| 상태 | 배제식 |
|---|---|
| lobby/editor/transition/unknown | `PS!=3` 또는 raw read 실패 |
| scenario/script | `scenario_selector!=0` |
| LAN/network/modal | `committed_local!=1` 또는 `network_mode!=0` 또는 `network_modal!=0` |
| pause/replay/AI suppressed raw state | `gate_a!=0` 또는 `gate_b!=0`; 두 필드에 의미 라벨을 추가하지 않는다 |
| unknown width/value | 하나라도 읽기 실패·폭 불일치·미정 값이면 reject |

이번 양성 baseline은 이 목록의 음성 실행을 하지 않으며 지원 mode를 넓히지 않는다. 후속 후보는 이 allowlist 밖에서 issuer/candidate call 0을 raw로 증명하기 전 활성화할 수 없다.

## 6. post-load 첫 tick·중복 판정식

과거 raw의 fresh shadow 512행(tick1..512)과 load 뒤 11행(tick50591..50601)은 보존 근거일 뿐 현행 성공이 아니다. 특히 load raw에는 synchronized completion marker가 없어 `exact_first_postload_completed_edge=UNKNOWN`; tick rewind만으로 load 완료를 증명하지 않는다.

후속 별도 카드가 아래 raw를 **같은 run/sequence domain**에 기록해야 한다.

1. load bulk+Unit restore가 끝났지만 다음 accepted `0x41C770` step 전인 exact completion marker: `run_id`, monotonic `seq`, pre-load 마지막 tick `Tpre`, 복원 tick `Tload`, 대상 `(slot,full_id,owner,command,pending,pending_xy)`.
2. marker 뒤 AI-shadow row: `seq,tick,owner,entry_ecx,ecx_owner_match,raw_mode,source identity/command/pending/pending_xy,same_tick_reentry,tick_rewind,decision,original_call`.
3. 실제 후보 issuer를 나중에 허가할 경우에만 별도 `candidate_issue_count/result` raw. read-only shadow의 `would issue`는 실제 중복 억제 PASS가 아니다.

첫 post-load edge PASS 식은 다음 전부다.

- exact marker 정확히 1건, 그 뒤 첫 shadow row가 `tick==Tload+1`.
- `owner==(tick&7)`, `entry_ecx==0x956770+owner*0x3ABC`, 양성 mode raw, `original_call=forwarded_once`.
- 첫 row의 `tick_rewind == ((Tload+1)<Tpre)`이고, 그 뒤 tick마다 shadow row 최대1건·`same_tick_reentry=false`.
- marker의 source identity가 첫 row에서도 동일하다. preexisting order(`command!=1 || pending!=1 || pending_xy!=0`)이면 candidate/issuer 0회여야 한다. idle 후보라도 동일 tick issuer는 최대1회다.

marker가 poll 기반 PS3 관측 뒤에 생기거나, marker 전에 accepted step이 가능하거나, identity/issuer raw가 없으면 `BLOCKED(postload_contract)`다. 기준을 낮추거나 과거 tick 역행을 PASS로 승격하지 않는다.

## 7. handoff

- work는 한 번 실행한 raw·수치·오류·cleanup·원본 SHA를 기록하고 종료한다. 자기 결과를 G4 완료로 승인하지 않는다.
- 다음 새 middle이 summary를 제외하고 raw로 §4를 독립 재계산한다.
- `FEASIBLE_BASELINE`이면 그 middle이 §6 exact-marker를 만들 최소 read-only instrumentation 범위를 새 카드로 판정한다. 제품 AI/issuer 활성화는 여전히 금지다.
- `NOT_FEASIBLE` 또는 `BLOCKED`이면 반복 실행 없이 strategy에 fixture 전환/중단 판단을 승격한다.

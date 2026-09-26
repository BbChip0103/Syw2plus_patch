# G4 W2 — exact load-completion marker + first post-load AI edge

- 발행: lap623 middle. lap622 W1F 보존 raw를 summary 없이 독립 재집계해 W1 §4 `FEASIBLE_BASELINE`을 확인한 뒤 발행한다.
- 단일 가설: 원본 UI load의 유일한 direct call-site와 기존 read-only AI shadow를 같은 opt-in DLL에서 계측하면, 성공 load 완료와 그 뒤 첫 accepted AI edge를 동일 `run_id`·단조 `seq`로 정확히 결합할 수 있다.
- 목적: `G4_REENTRY_ORIGINAL_AI_BASELINE_LAP612.md` §6의 exact post-load marker/first-edge 계약만 닫는다. 이 카드는 제품 AI/issuer/pathfinding 수정, G4 품질 개선/PASS, 지원 mode 확대, 저장·멀티 지원 승인이 아니다.

## 1. 고정 근거와 판정 경계

1. 원본 EXE는 SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`만 허용한다.
2. 원본 load 함수는 cdecl `FUN_00440FF0(slot)`이고 direct caller는 한 곳이다.
   - call-site `0x004D6B98`: old bytes `E8 53 A4 F6 FF` → target `0x00440FF0`.
   - 성공 load의 모든 bulk/Unit restore·후처리가 끝난 뒤 함수는 `0x00441549`의 `B8 01 00 00 00`(`mov eax,1`)을 거쳐 반환한다.
   - caller의 call 직후 `0x004D6B9D`부터 stack 정리/return만 수행한다. 따라서 call wrapper가 원본 함수를 정확히 한 번 호출하고 성공 반환 직후 marker를 쓰면, load 완료 뒤이면서 caller가 다음 simulation dispatch로 돌아가기 전인 경계다.
3. 기존 AI edge는 `0x0041CBE5` old bytes `E8 E6 29 02 00` → `0x0043F5D0`; 원본 call을 정확히 한 번 tail-forward한다.
4. `FUN_00440FF0` 내부가 `0x0041C770`을 호출하지 않음은 원본 disassembly/decompile로 확인했다. 다른 버전 주소로 확장하지 않는다.
5. 판정 우선순위는 `BLOCKED` > `EXACT_POSTLOAD_EDGE_PASS`다. CLI exit0, poll 기반 PS3, tick 역행만으로 PASS하지 않는다.

## 2. work tier 변경 범위

다음 work(`gpt-5.6-luna/high`)만 구현한다. 같은 파일의 단일 작성자다.

1. 허용 파일:
   - `tools/inmm_stub/ai_shadow.c`
   - `tests/test_g4_ai_shadow.py`
   - `tools/runtime_env.py`
   - `tests/test_runtime_env.py`
2. `ai_shadow.c`는 opt-in `INMM_AI_SHADOW=1`일 때만 두 call-site를 설치한다.
   - 두 old-byte/target을 **모두 먼저 검증한 뒤** 쓰기 시작한다.
   - 설치 중 하나라도 실패하면 이미 쓴 site를 저장한 원본 bytes로 rollback하고 실패를 반환한다.
   - UI load wrapper는 caller가 전달한 slot로 원본 `0x00440FF0`을 정확히 한 번 호출하고 원본 반환값을 그대로 돌려준다. 성공 반환값 `1`일 때만 completion marker를 쓴다.
   - 게임-owned field, Unit/PlayerStruct, issuer, command/pending 값은 읽기만 한다. 새 persistent counter를 게임 메모리/세이브에 두지 않는다.
3. `runtime_env.py`의 기존 `g1-s1-original-load-evidence` 경로에 명시적 `--bridge`와 `--g4-exact-postload` opt-in을 추가한다.
   - opt-in 없이는 현재 동작과 산출물이 바뀌지 않는다.
   - opt-in은 `--bridge`를 필수로 하고 `prepare(..., bridge=...)`에 전달한다.
   - 자식 env에 `INMM_AI_SHADOW=1`, `INMM_G4_RUN_ID=<fresh manifest run_id>`를 직접 넣고 provenance allowlist에 두 값을 기록한다. 셸 상속만으로 성공 처리하지 않는다.
   - private `drive_c/inmm_ai_shadow.jsonl`의 경로·SHA·행 수·marker 수를 cleanup 뒤 fail-closed로 기록한다. missing/empty/symlink/외부 path/marker 0 또는 2+는 PASS 금지다.
4. 새 의존성, 제품 EXE patch, 원본/참고 쓰기, save 변경, candidate/issuer/waypoint call, G1 probe 추가는 금지한다.

## 3. 같은 sequence-domain raw 계약

`inmm_ai_shadow.jsonl`의 marker와 shadow row에 공통으로 다음을 둔다.

- `schema_version`, `run_id`, process/thread identity, 전역 단조 `seq`, event 종류.
- marker event `load_complete`: `seq`, `slot`, 원본 load `result=1`, `Tpre`(wrapper가 원본 load 호출 직전에 읽은 global tick), `Tload`(성공 반환 직후 읽은 restored tick), 다음 owner `(Tload+1)&7`, 대상 `source(full_id,slot,owner,command,pending,pending_xy)`.
- shadow event: 기존 `tick,owner,entry_ecx,raw_mode,source,same_tick_reentry,tick_rewind,original_call`에 `seq`, `run_id`, thread identity, `load_marker_seq`를 추가한다.
- marker 뒤 첫 edge와 뒤따르는 최소 16개 edge는 기존 512행 cap과 무관하게 bounded 강제 기록한다. 평시 unbounded logging은 금지한다.
- `Tpre` 추적은 log cap 뒤에도 계속되는 실제 AI-edge tick 또는 load-wrapper 직전 global tick으로 명시한다. cap 도달 때문에 stale 값을 exact 값으로 쓰지 않는다.
- read-only build에는 candidate/issuer 경로가 없음을 source/test로 고정하고 raw에는 `candidate_present=false`, `candidate_issue_count=0`을 기록한다. 하드코딩한 0을 향후 제품 후보의 중복 억제 증거로 재사용하지 않는다.

## 4. 실행 전 회귀와 gate

1. 정적/단위 회귀는 최소 다음을 고정한다.
   - 두 call-site VA·old bytes·원본 target, preverify-before-write, partial-install rollback.
   - load wrapper가 원본 load를 정확히 한 번 호출하고 반환값을 보존함.
   - 성공 load에만 marker 1건, marker/first row `run_id`·`seq` 연결, bounded post-load window.
   - 기존 AI wrapper의 exact-once tail-forward·mode/read-only/issuer 부재 계약 불변.
   - runtime opt-in off 불변, opt-in의 bridge/run-id/env/provenance 양성 및 missing/empty/symlink/marker-count 음성.
2. 실행 전 다음을 모두 통과한다.
   - `.venv/bin/python -m pytest -q tests/test_g4_ai_shadow.py tests/test_runtime_env.py`
   - `make -C tools/inmm_stub clean all`
   - `bash checks/safety.sh check`
   - source 변경 통합 경계 `make check`.
3. 필수 gate가 예상 밖으로 실패하면 변경을 보존하고 게임을 시작하지 않는다. 수리 재시도 없이 `loop/ESCALATE_SOL`로 넘긴다.

## 5. fresh 정확히 1회

gate가 모두 맞을 때만 pinned `save000.dat`을 쓰는 기존 원본 load 경로를 새 전체 게임 복사본/fresh prefix/빈 display에서 foreground 동기 실행 정확히 1회 수행한다.

```sh
.venv/bin/python tools/runtime_env.py g1-s1-original-load-evidence \
  --source /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus \
  --runtime-root local/runtime \
  --bridge tools/inmm_stub/_inmm.dll \
  --g4-exact-postload
```

- 실행 전 manifest `created_new=true`, `diagnostic_bridge_overridden=true`, original/private EXE SHA와 build/private bridge SHA 일치를 확인한다.
- 기존 runtime 재사용, background 실행, 실패 뒤 재시도, raw backfill은 금지한다.
- 원본 save fixture는 읽기 전용 source에서 fresh private copy로만 복사한다. 원본/참고 디렉터리를 실행·수정하지 않는다.

## 6. `EXACT_POSTLOAD_EDGE_PASS`

다음이 모두 참이어야 한다.

1. identity/provenance/cleanup: pinned EXE·save·fresh manifest·private bridge/env/run_id/shadow SHA·marker count 1, `cleanup.ok=true`, residual `[]`, global kill false, 원본 불변.
2. marker 정확히 1건이고 원본 load `result=1`; `Tpre`와 `Tload`를 wrapper 안에서 읽었으며 poll 기반 사후 marker가 아니다.
3. marker 다음 sequence event가 첫 post-load shadow row다: `first.seq==marker.seq+1`, 같은 `run_id`와 process/thread, `first.tick==Tload+1`.
4. 첫 row는 `owner==(tick&7)`, `entry_ecx==0x956770+owner*0x3ABC`, mode `(3,1,0,0,0,0,0)`, `original_call=forwarded_once`다.
5. `first.tick_rewind == ((Tload+1)<Tpre)`이고 marker의 source tuple이 첫 row와 정확히 같다. source가 없거나 identity가 바뀌면 PASS하지 않는다.
6. marker 뒤 기록 창에서 tick별 row 최대1, `same_tick_reentry=false`, `seq` 단조·중복0이다.
7. read-only build라 `candidate_present=false`, `candidate_issue_count=0`; marker source가 preexisting order(`command!=1 || pending!=1 || pending_xy!=0`)여도 candidate/issuer call은 0이다. 이는 실제 후보의 중복 억제 PASS가 아니다.

## 7. 실패·handoff

- call-site/signature/rollback, bridge/env/provenance, marker count/order, tick/owner/ECX/mode, identity, exact-once forward, cleanup 중 하나라도 어긋나면 `BLOCKED(postload_contract:<원인>)`다.
- pinned fixture에서 marker source가 없거나 first-edge identity가 불안정하면 같은 fixture를 반복하지 않는다. raw를 보존하고 다음 middle/strategy가 fixture 전환 또는 이 경로 종료를 판정한다.
- work는 구현·회귀·fresh 1회의 raw와 SHA를 기록할 뿐 자기 결과를 승인하지 않는다. 다음 새 middle이 summary 없이 marker/JSONL/provenance를 독립 재집계한다.


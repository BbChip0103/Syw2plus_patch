# 2026-09-27 | lap 701 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5-5 / high / middle(검수·진단·계획).
  게임/하네스 코드 hands-on 수정 없음(문서만 기록).
- 가설 / 사용자 관찰: lap700 work가 G4 W2 read-only AI shadow에서 `EXACT_POSTLOAD_EDGE_PASS`
  최초 raw PASS를 주장. STATUS "다음 한 가지"의 (a) ABI 수리 objdump 재추적, (b) source 비교 수리와
  postload 대기 폴링의 옵트인 한정, (c)(d) run3 `inmm_ai_shadow.jsonl` 직접 파싱으로 카드
  `docs/work/active/G4_W2_EXACT_POSTLOAD_MARKER_LAP623.md` §6의 7개 조건 재확인.
- 예상 PASS / FAIL 조건: 7개 조건 전부 raw로 참이고, 카드 §6-5("source가 없거나 identity가 바뀌면
  PASS하지 않는다")·§7("marker source가 없으면 같은 fixture 반복 금지, middle/strategy가 fixture
  전환/경로 종료 판정")을 실질적으로 만족해야 확정.
- 변경 파일 / source fingerprint / 커밋: 문서만(이 파일, STATUS, INBOX, APPROVALS, lap700 파일 말미
  정정 1줄). 코드 무변경. 검수 대상 SHA(재해시 일치): `tools/inmm_stub/ai_shadow.c`
  `252b1a06…b8ba5`, `tools/inmm_stub/_inmm.dll` `4e5f64e5…a971f6`, `tools/runtime_env.py`
  `036c3672…81779`, `tests/test_g4_ai_shadow.py` `3ec57525…887cd`, `tests/test_runtime_env.py`
  `1ad64125…86386`. uncommitted(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `Syw2plus_re/Syw2plus/syw2plus_original.exe` 재해시 `b56986e0…c9c08a8ac` 일치(읽기 전용
  objdump만). fixture save000.dat(pinned `1c703551…719da`). candidate 없음(read-only shadow).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `i686-w64-mingw32-objdump -d tools/inmm_stub/_inmm.dll` `_g4_load_call_wrapper`(0x6fd104e0)와
     원본 EXE `0x4d6b97..0x4d6ba9`, `0x440ff0..` 역어셈.
  2. run1/2/3 `local/runtime/<run>/manifest.json`의 `support_dll_sha256._inmm.dll`,
     `diagnostic_bridge_sha256` 확인.
  3. run3 `local/runtime/20260927_041011_2268874_0/prefix/drive_c/inmm_ai_shadow.jsonl` 재해시
     `f1255b093c793151dff4cbb756356601c31030ced6502c6d57335fd886ad05c0`(23행) 후 기존 판정 함수
     (`_g4_postload_contract`)를 쓰지 않는 별도 파서로 조건별 재집계. run1/2 jsonl도 source 분포 비교.
  4. `.venv/bin/python -m pytest -q tests/test_g4_ai_shadow.py tests/test_runtime_env.py
     tests/test_s1_load_evidence.py` → **232 passed**(1.88s). `bash checks/safety.sh check` →
     **SAFETY_PASS**. `make check` 전체는 코드 무변경이라 재실행하지 않음(lap700 로그 1026 passed 인용만).
- 측정값 / 판정:
  - (a) ABI 수리 **CONFIRMED(정적)**: 원본 호출 지점 `0x4d6b97 push esi; 0x4d6b98 call 0x440ff0;
    0x4d6b9d add esp,4`(cdecl 1-인자, 호출자 정리), `0x440ff0 mov ecx,[esp+4]`로 ECX 입력 없음
    → wrapper가 before 훅에서 ECX를 덮어써도 무해. wrapper 스택 수기 추적: 진입 `[esp]=R,[esp+4]=slot`
    → 원본 호출 후 `push eax` → `push [esp+8]`(=slot, EA는 push 전 ESP 기준) →
    `call g4_load_complete(slot,result)` → `add esp,4` → `pop eax`(=원본 결과) → `ret`(=R). 수리 전
    `add esp,8`이면 `pop eax`=R, `ret`→slot 주소(=0)로 점프하는 것도 맞다. `0x6fd134e8` =
    `_g_load_original_target`(nm 확인).
  - (b) **CONFIRMED**: `_g4_wait_for_postload_rows`는 `if g4_exact_postload:` 분기(runtime_env.py
    4234행) 안에서만 호출되고 판정하지 않으며 데드라인은 `min(operation_deadline, +45s)`. `--bridge`와
    `--g4-exact-postload`는 서로 필수. owner 비교 수정 자체(`marker.source.owner` vs `first.owner`)는
    ai_shadow.c `append_source`(marker만 owner 포함) 스키마와 맞다.
  - (c)(d) run3 raw 재집계: 조건1(run_id 단일=manifest, 원본/사본 EXE·bridge SHA, cleanup `ok=true`,
    `residue_pids=[]`, `global_kill_used=false`) 참, 조건2(marker 1건, `result=1`, `tpre=0`,
    `tload=50590`) 참, 조건3(`first.seq=2=marker.seq+1`, 같은 pid32/tid36, `first.tick=50591`) 참,
    조건4(owner7, ECX `0x970294`=`0x956770+7*0x3ABC`, mode `(3,1,0,0,0,0,0)`, `forwarded_once`) 참,
    조건6(창17 tick 50591~50607 유일, reentry 0, `load_marker_seq=1` 17/17, seq 1~23 연속) 참,
    조건7(candidate 0) 참.
  - **조건5 NOT MET — source 부재(공허 일치)**: marker `source={full_id:0,slot:0,owner:7,command:0,
    pending:0,pending_xy:0}`는 `find_source`의 "못 찾음" sentinel(초기화 0, `live=FALSE`)이고, 첫 row도
    `source.live=false`, `decision=concrete_rejection`, `rejection=no_live_source`. 즉 0==0 비교로
    통과했다. run3 전 창의 owner별 live: 0/1/2/3/5=true, **4/6/7=false** — save000의 tick
    `(50590+1)&7=7`이 결정적으로 live 유닛 없는 owner를 가리키므로 **이 fixture는 반복해도 항상 source
    부재**다(run1/run2도 marker source 동일 전부 0). `_g4_postload_contract`에는 source 존재/live
    검사가 없고, 부재 source를 FAIL시키는 테스트도 없다(tests 검색 0건). lap700의 source 비교 수리는
    "항상 거짓 FAIL"을 없앴지만 동시에 "부재 source 거짓 PASS"를 노출시켰다.
  - **lap700 기록 오류**: "run1 = ABI 수리 전 상태, 크래시 없음"은 사실이 아니다. run1/2/3 manifest
    모두 `_inmm.dll`=`diagnostic_bridge_sha256`=`4e5f64e5…`(수리 후 빌드; DLL mtime 03:32:57,
    run1 jsonl 03:53:06). 수리 전 wrapper의 런타임 크래시는 관측된 적 없고 근거는 정적 추적뿐이다
    (정적 근거 자체는 위 (a)대로 유효).
  - **판정: `BLOCKED(postload_contract:marker_source_absent)` / G4 W2 `HOLD`.** 구조적 load-boundary
    결합(조건1~4·6·7)은 독립 확인했으나 카드 §6-5 source identity는 증명되지 않았으므로
    `EXACT_POSTLOAD_EDGE_PASS`를 확정하지 않는다. 제품 G4 PASS·사용자 승인 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 무변경, 타깃 232 passed, SAFETY_PASS.
  마일스톤 경계 아님(harness 계약 단계). 카드 §7에 따라 middle이 fixture 전환을 판정했다(아래).
  디스크 85GB 여유.
- 다음 한 가지(work tier handoff, FEASIBLE — 재계획 없이 즉시 구현·실행):
  1. `tools/runtime_env.py` `_g4_postload_contract`를 fail-closed로 보강: marker `source.full_id!=0`,
     `source.slot!=0`, `(full_id & 0xffff)==slot`, 첫 row `source.live is True`,
     `first.source.full_id==marker.source.full_id` 아니면 `marker source absent/unstable` FAIL.
     `tests/test_runtime_env.py`에 run3 형태(전부 0, `live=false`) 음성 테스트 추가, 기존 PASS
     픽스처는 live source로 교정. 판정 함수 외 동작 불변.
  2. `g1_s1_original_load_evidence`에 옵트인 fixture 선택(기본 save000 불변, `--g4-exact-postload`
     전용)을 추가해 이미 pinned된 `save006.dat`(`s1.FIXTURES`, SHA `616b7997…0d064`, slot 7,
     LEGACY_SOURCE `save/`에 존재)로 fresh `--bridge --g4-exact-postload` 실행. 성공 측정식: 보강된
     계약 `pass=true` + marker `full_id!=0` + 첫 row `live=true` + 7조건 + cleanup ok/잔류0/원본 SHA 불변.
  3. save006도 next_owner에 live 유닛이 없으면 같은 fixture를 반복하지 말고 raw 보존 후 기록 —
     다음 middle이 계약 변형(예: marker가 첫 live owner의 source를 함께 기록) 또는 경로 종료를 판정.
  4. lap700 파일의 run1 서술은 이 lap 말미 정정 1줄로 대체 표기(원문 보존).

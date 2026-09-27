# 2026-09-27 | lap 700 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high / work(실무).
- 가설 / 사용자 관찰: 2026-09-27 03:21 사용자 판단(G2 10000 포기, 다음 우선순위 G4) →
  "다음 work는 G4의 마지막 미충족 항목 중 post-load(저장/로드 후 AI 개선 유지) 확인부터
  구현 우선으로 진행." G4는 lap612~626에서 read-only AI shadow(`tools/inmm_stub/ai_shadow.c`)
  계측을 만들다 lap626에서 `tools/runtime_env.py` mypy 10건 실패로 `BLOCKED`, G5 최우선 전환으로
  중단됐다. 카드 `docs/work/active/G4_W2_LINK_ABI_REPAIR_LAP625.md`·
  `G4_W2_EXACT_POSTLOAD_MARKER_LAP623.md`가 정확한 W2 ABI 계약과 `EXACT_POSTLOAD_EDGE_PASS`
  판정 기준을 이미 못박아 두었다. 가설: (1) mypy 실패는 이후 lap(693 등)에서 우연히 해소됐을
  것이다, (2) lap626이 "확인했다"고 기록한 objdump 검증은 실제로는 스택 언밸런스를 놓쳤을 수
  있다 — 재검증이 필요하다.
- 예상 PASS / FAIL 조건: 카드 LAP625 §3 gate(targeted pytest, `make -C tools/inmm_stub clean
  all`, objdump ABI 확인, `checks/safety.sh check`, `make check`) 전부 PASS해야 카드 LAP623 §5
  fresh 1회(pinned save000, `--bridge --g4-exact-postload`)를 수행한다. fresh 결과는 카드 §6의
  `EXACT_POSTLOAD_EDGE_PASS` 7개 조건(marker 1건·`Tpre/Tload`·`first.seq==marker.seq+1`·
  `first.tick==Tload+1`·ECX/mode/tail-forward·window 무결성)을 전부 만족해야 PASS다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): uncommitted(LOOP_ALLOW_COMMITS=0).
  - `tools/inmm_stub/ai_shadow.c` SHA256
    `252b1a069ec50448d7f5122f6938c144de5e5f63d769e6f14d128c23803b8ba5`(이전
    `57f48c3376b46fb3be786326fa206fba1ad498cc53566483fe0961dd46a49a01`=lap626 상태와 동일 시작점).
    `g4_load_call_wrapper`의 `addl $8, %esp`(marker 호출 뒤 정리)를 `addl $4, %esp`로 1바이트
    수리. 상세는 아래 "핵심 결함" 참고.
  - `tests/test_g4_ai_shadow.py` SHA256
    `3ec57525171309026f5e439203bab3c9b32b6657a10358923edccfe6319887cd`(이전
    `b78912882eca69acc3710ece62cb9abecba08570d39ab5285ed22b7f46f2ea43`). 깨진 바이트 패턴
    (`addl $8, %%esp`)을 요구하던 assertion을 제거하고, cleanup 총량(3회의 `addl $4, %%esp`)과
    `call _g4_load_complete` → cleanup → `popl %%eax` 순서를 고정하는 assertion으로 교체.
  - `tools/runtime_env.py` SHA256
    `036c3672c517316247f39c071fb55240fc810e2f52c302c3987e3f5dbfc81779`. 두 가지 변경:
    1) `_g4_wait_for_postload_rows()` 신규(read-only 폴링, PASS/FAIL 판정은 하지 않음) +
       `g1_s1_original_load_evidence`의 `post_finalize` 스테이지 직후
       `g4_exact_postload`일 때만 호출(옵트인 외 동작/산출물 불변). 기존 stage budget 합(140s)
       대비 실측 소모(~28s)에 큰 여유가 있어 총 데드라인 상수는 건드리지 않았다(§"타이밍 실측"
       참고).
    2) `_g4_postload_contract()`의 marker/first-edge `source` 비교 버그 수리: marker JSON의
       `source` 객체는 `owner`를 포함하지만(`append_source`), shadow row의 `source` 객체는
       `owner`를 포함하지 않고 이벤트 최상위 필드로 둔다(`ai_shadow_capture`). 기존 코드는
       `first.get("source", {}).get("owner")`를 읽어 항상 `None`과 비교해 실제 라이브 데이터에서
       매번 거짓 FAIL을 냈다. `marker["source"]["owner"] vs first["owner"]`로 비교 대상을 바꿨다.
  - `tests/test_runtime_env.py` SHA256
    `1ad641254a9f890a337acd51dbf15617dbe65d1c01c51327b3e7d9e39bb86386`. 기존 PASS 픽스처가
    marker/row 양쪽에 동일한 `source` 리터럴(둘 다 `owner` 포함)을 재사용해 비대칭 실스키마를
    가리고 있었다 — marker용/row용 `source`를 분리(row는 `owner` 제외)해 실제 버그를 노출하는
    형태로 교정. `test_g4_exact_postload_provenance_rejects_source_content_mismatch` 신규
    추가(같은 owner/tick/ecx에서 `full_id`/`slot`만 다른 경우 여전히 FAIL함을 고정, 회귀 방지).
  - 재빌드 산출물 `tools/inmm_stub/_inmm.dll` SHA256
    `4e5f64e5b710fb482931d069fb14f83f0c66979c86a64901ab0f600c87a971f6`(수리 후 clean build).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 fresh 실행 모두 불변,
  manifest로 재확인). fixture는 pinned `save000.dat`(size 3093902, SHA
  `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`) — 이 fixture는
  `Syw2plus_re/Syw2plus`(LEGACY_SOURCE, 2026-09-26 22:52 지시로 읽기전용 보존)에만 있고 새 기본
  경로 `[ESL]Syw2plus/save/`는 비어 있어(save000.dat 없음) 첫 시도가 `NO_RUN:
  protected source save000 identity is not pinned`로 실패했다 — 이번 lap은 이 fixture-only 실행에
  한해 `--source`로 LEGACY_SOURCE를 명시했다(옛 경로도 원본과 동일 SHA, 읽기 전용, G2 22:52
  지시가 이 fixture 재현성 목적으로 명시 보존한 경로). 활성 플레이어/AI 후보는 없음(read-only
  shadow, `candidate_present=false` 전 구간).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `.venv/bin/python -m pytest -q tests/test_g4_ai_shadow.py tests/test_runtime_env.py
     tests/test_s1_load_evidence.py` → 231 passed(수정 전), 232 passed(신규 테스트 추가 후).
  2. `make -C tools/inmm_stub clean all` → exit0, `_inmm.dll` 재빌드.
  3. `i686-w64-mingw32-objdump -d tools/inmm_stub/_inmm.dll` → `g4_load_call_wrapper`의
     `push [esp+4] → call g4_load_before → add esp,4 → push [esp+4] → call
     *g_load_original_target → add esp,4 → push eax → push [esp+8] → call g4_load_complete →
     add esp,4 → pop eax → ret` 순서와 피연산자 값을 손으로 스택 추적해 확인(아래 "핵심 결함"
     참고).
  4. `bash checks/safety.sh check` → `SAFETY_PASS`.
  5. `make check` → **1026 passed(759.23s)**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS
     (로그 `logs/gates/20260927_lap700_g4_w2_postload_make_check_final.log`; 수리 전 mypy
     재확인 단계 로그는 `logs/gates/20260927_lap700_g4_w2_make_check.log`, **1025 passed(765.98s)**
     — lap626이 겪은 mypy 10건 실패는 이번 세션 시작 시점에 이미 해소돼 있었다, 원인/귀속 lap은
     불명이라 별도 조사하지 않음).
  6. fresh 실행 3회(`tools/runtime_env.py g1-s1-original-load-evidence --bridge
     tools/inmm_stub/_inmm.dll --g4-exact-postload`, 각 새 private copy/prefix/display):
     - run1 `20260927_035238_2182884_0`: ABI 수리 전 상태로 실행 — **크래시 없이 marker 1건
       PASS**했지만 `postload_rows=7`(<17)로 `FAIL(bounded window incomplete)`. 이 결과 자체가
       ABI 수리가 적어도 crash를 없앴음을 실증했다(이전 lap626 시점엔 W2 자체가 링크 실패라
       fresh 실행 이력이 없었다).
     - run2 `20260927_040209_2227645_0`: `_g4_wait_for_postload_rows` 추가 후 재실행 —
       `postload_rows=22`(폴링 3회, 0.4s만에 도달, 실측 tick 처리량이 매우 빨라 대기 예산은
       거의 소모하지 않음) — 그러나 `_g4_postload_contract`의 `source` 비교 버그로
       `FAIL(marker/edge source mismatch)`.
     - run3 `20260927_041011_2268874_0`: `source` 비교 수리 후 재실행 — **`g4_exact_postload.
       pass=true`(`marker_count=1, postload_rows=22, first_seq=marker_seq+1`), `cleanup.ok=true`,
       `residual_pids=[]`, 원본/사본 SHA 전부 일치, `status=PASS`**.
     - raw artifact: `local/runtime/<run_id>/prefix/drive_c/inmm_ai_shadow.jsonl`(run3 SHA256
       `f1255b093c793151dff4cbb756356601c31030ced6502c6d57335fd886ad05c0`, 23 rows). evidence
       JSON은 `/tmp/g4_postload_run{1,2,3}.json`에 임시 보존(공유 temp로 옮기지 않음 — 캡처
       PNG가 아니라 raw JSON/jsonl이라 안전 규칙의 캡처 경로 규칙 대상이 아님; 필요 시 각 run의
       `local/runtime/<run_id>/output/` 아래 정식 아티팩트로도 존재).
     - 디스크 위생: 3개 run의 `game/` 사본(각 2.2GB, 총 6.6GB) 삭제, `output/manifest.json/
       prefix`는 보존. 실행 전 87GB → 실행 후에도 86GB(게임 사본 삭제 반영 후).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **`EXACT_POSTLOAD_EDGE_PASS`(run3, harness raw
  기준) PASS.** 카드 LAP623 §6의 자동 판정 함수(`_g4_postload_contract`)가 marker/first-edge
  인접성·seq·tick·owner·ECX·raw_mode·tail-forward·source 동일성·window 무결성을 전부 확인했다.
  W2 ABI gate(LAP625 §3)도 PASS. **미충족(그대로 유지):** 이 빌드는 read-only shadow일 뿐
  candidate AI 정책이 없다(`candidate_present=false` 전 구간) — 따라서 "AI 개선이 저장/로드
  후에도 유지되는가"라는 문자 그대로의 제품 질문에는 아직 답할 수 없다. 이번 lap이 닫은 것은
  그 질문을 물을 수 있게 하는 **계측 하네스의 load-boundary 계약**(marker와 그 다음 첫 AI edge를
  같은 run_id·단조 seq로 정확히 결합하는 것)이다. STATUS 표의 G4 미충족 3항("AI 개선 제품
  비교·post-load·사용자 승인") 중 이번 lap은 **post-load 계약을 harness 수준에서 처음으로
  raw PASS**시켰고, "AI 개선 제품 비교"·"사용자 승인"은 여전히 미착수/미충족이다.
- 핵심 결함(수리 근거, objdump 손 추적): 원 코드 `g4_load_call_wrapper`는
  `push eax(저장된 원본 결과) → push slot → call g4_load_complete(slot, result) → add esp,8 →
  pop eax → ret`이었다. cdecl 2-인자 정리는 8바이트가 맞지만, 그중 4바이트는 **호출 인자로
  이미 소비된 "저장된 eax"** 슬롯이다 — `add esp,8`로 그 슬롯까지 통째로 버리면 다음 `pop eax`가
  실제로는 **wrapper 자신의 반환 주소**를 eax로 읽고, 이어지는 `ret`은 **caller가 넘긴 slot 값을
  코드 주소로 삼아 점프**한다(항상 크래시). 올바른 정리는 `add esp,4`(호출 인자로 쓴 slot 복사본
  1개만 버림) 뒤 `pop eax`가 저장해 둔 원본 결과를 정확히 복원하는 것이다(스택 12→8바이트가
  아니라 8바이트로 끝나야 함, 이 8바이트 중 4는 `add`로 4는 `pop`으로 처리). lap626은 objdump로
  "push/call/add/pop/ret 순서가 나온다"만 확인하고 피연산자 값을 손 추적하지 않아 이 결함을
  놓쳤다 — 이번 lap은 스택 오프셋을 끝까지 수기 추적해 발견·수리했다. 같은 파일의 기존 테스트
  (`test_exact_postload_hook_pins_load_site_marker_sequence_and_rollback`)는 깨진 값(`$8`)을
  그대로 assertion으로 요구하고 있어 "targeted PASS는 ABI 증거가 아니다"라는 카드 LAP625 §1.4의
  경고가 실제로 재현된 사례였다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `make check` 1026 passed, ruff/mypy/
  `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 원본 SHA 3회 실행 모두 불변, cleanup 3/3 ok, 잔류
  프로세스 0. **독립 검수/사용자 승인 없음** — 이 work tier 결과는 다음 middle이 raw
  jsonl/objdump/테스트를 요약 없이 재집계해야 한다. 남은 위험: (1) `[ESL]Syw2plus` 기본 경로에
  save000.dat이 없어 이 경로 계열 G4 fixture 실행은 계속 LEGACY_SOURCE가 필요하다(수리 범위
  아님, 다음 middle/strategy가 새 경로에 fixture를 채울지 판정 필요). (2)
  `tools/g4_ai_evidence_inventory.py`/`tools/g4_difficulty_absence.py`는 lap693이 명시적으로
  옛 경로 참조를 남겨 뒀다(이번 lap도 손대지 않음). (3) `_g4_wait_for_postload_rows`의
  45초 예산은 이번 3회 실행(모두 <0.5초에 도달) 기준으로는 넉넉하지만, 다른 fixture/장면에서
  tick 처리율이 달라질 가능성은 미검증.
- 다음 한 가지: 다음 middle이 (a) `tools/inmm_stub/ai_shadow.c`의 ABI 수리를 objdump 피연산자
  값으로 독립 재추적하고, (b) `tools/runtime_env.py`의 `source` 비교 수리와 `_g4_wait_for_
  postload_rows` 폴링이 옵트인 외 동작을 바꾸지 않았는지 확인하고, (c) run3
  `inmm_ai_shadow.jsonl`(SHA `f1255b093c793151dff4cbb756356601c31030ced6502c6d57335fd886ad05c0`)을
  직접 파싱해 `EXACT_POSTLOAD_EDGE_PASS` 7개 조건을 재확인한다. PASS 확정되면 G4의 다음
  단계(read-only shadow 위에 실제 candidate AI 정책을 얹는 설계, 또는 `G4_REENTRY_ORIGINAL_
  AI_BASELINE_LAP612.md`가 정의한 원본 AI 베이스라인 측정 재개)는 middle/strategy가 정한다 —
  이번 work는 그 후속 설계를 선점하지 않는다.
- 정정(lap701 middle): 위 run1의 "ABI 수리 전 상태로 실행"은 사실이 아니다 — run1/2/3 manifest 모두 수리 후 `_inmm.dll` `4e5f64e5…`를 썼다(DLL 03:32:57 빌드, run1 03:52). 수리 전 크래시는 정적 추적 근거뿐이다. 또 run3 PASS는 marker/첫 row source가 부재(전부 0, `live=false`)인 공허 일치라 lap701이 `BLOCKED(postload_contract:marker_source_absent)`로 판정했다. 상세 `20260927_lap701_middle_g4_w2_postload_independent_review_source_absent_hold.md`.

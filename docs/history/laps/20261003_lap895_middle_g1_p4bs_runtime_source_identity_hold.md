# 2026-10-03 | lap895 | G1 P4b-S middle — captured pair 재계산 수용, 현재 runtime source 불일치 HOLD

- 실제 provider/model/effort / 지정 역할: 이번 새 Codex native 세션은 사용자 지정 middle(진단·계획·확인)이다. 현재 API 표면은 실제 CLI argv/model ID/effort를 조회하지 못하므로 설정만으로 실행 모델을 증명하지 않는다. 최신 INBOX의 middle=Sol/high/Fast 계약을 따르며 게임·하네스 구현은 수정하지 않았다. 앞 work의 실제 gpt-6-luna/high/Fast argv는 STATUS의 17:50 operator handoff 근거로 구분한다. subagent0, 새 유료 CLI0, counter895 읽기만, commit0.
- 목표 / 가설 / 측정식: STATUS의 다음 한 가지인 lap894 pair3/4 P4b-S 독립 검수. 카드 lap892 middle 목록만 적용: 두 호출 hook/ABI/원복·6범위, 동일 decoder/비교 필드 유지, E2 5 snapshot×4lane 불변식/헤더, E3 baseline 10 state=lap888, E4 pair full records=0 diff, B'-1~6 coverage/validator/input 및 build/raw/source/cleanup. runtime source 일치와 실제 gate를 모두 확인해야 현재 B'를 수용한다. P단계 전환은 마일스톤이 아니므로 그 자체로 승격하지 않는다.

## 판정 및 원인

**`HOLD_RUNTIME_SOURCE_IDENTITY` — B'/G1 HOLD, C/D/P5 전환 없음.**

pair3/4의 build 입력 44개 중 43개는 현재 source와 같다. 아래 한 파일은 두 DLL에 들어간 보존 source와 현재 source가 실제로 다르다. 오타나 잘린 해시가 아니며 raw/파일 직접 재해시·diff로 확인했다.

| 입력 | pair3/4 빌드 SHA256 | 현재 SHA256 |
|---|---|---|
| `tools/inmm_stub/direct_draw_trace.c` | `388aa9837cc8dd5a5c3055dd23e1f9a2c66560cc5ddf01510c3133af4102a404` | `e0690d8c71a4ec30b808ebe86dae3ff68fb84275e1cfadb28b662a82a42dec75` |
| `tests/test_g1_saved_scene_probe.py` (work 기록과 현재 대조) | `08e3456868c6e01e180f5567ddd0c750434259508ef550de1069939a7ecda9ce` | `d90656d54be982ab1e73409474a2bfc0aafa7b0b67d8d45989f1dc226aea8e40` |

차이는 `g1_direct_draw_trace_install()`에서 **snapshot 설치와 `verify_runtime_contract()` 두 블록의 순서를 바꾼 것**이다. pair DLL은 snapshot hook을 먼저 설치한다. 현재 source는 원본 버전/import/mode 검사 뒤 설치한다. 현재 추가된 `test_snapshot_hooks_install_only_after_runtime_contract_guard`도 이 순서를 검사한다. 검사 범위를 바꾸는 실행 코드 변경이므로 narrative-only 동일 source 예외가 아니다. DLL이 깨졌거나 정상 fixture에서 상태 발산이 있었다는 증거는 없지만, pair3/4를 이 변경본의 fresh runtime 검증으로 쓸 수 없다.

- 공유 temp의 pair3·pair4 `bridge/direct_draw_trace.c`가 build manifest의 SHA와 각각 MATCH. 두 파일의 현재 source와 diff는 동일한 블록 이동뿐이다.
- current C snapshot 구현 `6f40eee01cc21063a87e92d79afb361e35186f041dbefac885efbfb318407658`와 host `10493250c17a2042a9b0a70e9662bdc9e1a935b08547d01de29f10868f8cb6cf`는 work 기록과 MATCH. 이 세션은 어느 source도 수정하지 않았다.
- work 기록 focused127 및 최종 Fast1431과 달리 현재 focused128은 새 source 계약 테스트를 포함한다. 이전 Fast를 현재 fingerprint PASS로 승격하지 않는다. 소스 변경의 작성자/정확한 경위는 이 세션에서 추정하지 않는다(파일 mtime은 참고일 뿐 authority가 아님).
- 사용자 이번 세션의 실질 근거 충돌 stop 규칙에 따라 marker 생성 후 종료한다. 새 전체 Fast·runtime·build는 SKIP. 일반 G1 재허가 요청이 아니며 내부 승격→work 인계다.

## 보존된 실행 증거의 독립 확인 (현재 source 승인 아님)

원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 read-only MATCH. EXE offsets `0x245D2=e8 99 81 ff ff`, `0x250F7=e8 74 76 ff ff` MATCH. EXE 후보 없음(정상 in-process hook이며 파일 패치/파일 원복 N/A). fixture의 8 player records는 활성8인 부하증명 아님.

| 항목 | pair3 | pair4 |
|---|---|---|
| pair JSON SHA | `1a41e38a6b5cc13abcae69761ed2a7edbfbbecc250ad848cd912bd56c45d233f` | `a3762d1cc1fb4f3187df78497989a5c2516010ee4e75c4a36b112b1cd1aab3a7` |
| DLL SHA | `a3a31202d919c008ffb60e8951da01f9fe89e2aabaa42f9563458e15de68ae54` | `16ecb50f985e3cdc27d7281560cab6411424ea7c8af4c7a7aad3e64a1195618c` |
| candidate trace SHA | `6860d78dac1de71eb0f343f8cc251d60665275892f7fb84a26a1df99b6660352` | `251dbb5ed3d3babd527d54911e98ec1c78c701e018f56a9436f90969923d7eeb` |
| PS3 present 재계산 | 975 | 970 |
| Scale2x validator(전체 present) | PASS 1170 | PASS 1195 |
| fixed first20 / last20 p50 | 337648.5 / 355832.5 | 337648.5 / 355734.0 |
| DOWN / RIGHT 30-present p50 | 366473 / 355514 | 366473 / 355514 |
| DOWN / RIGHT key전 p50 | 356206 / 366879 | 356206 / 366899 |
| DOWN / RIGHT layer move delta | 1 / 512 | 1 / 512 |
| transfer delta 각 창 | 30 / 30 | 30 / 30 |

- 각 lane binary 5개(각 2,378,832 bytes)의 SHA와 독립 packed header 해석 MATCH. ticks=24692/24728/24788/24824/24860, before=target−1, flags0, sequence1..5, callsite0x4245D2, pid276/thread280·run id는 해당 결과/trace와 MATCH. 0x4250F7 wrapper는 disassembly/설치 source로 확인했고 이 장면 실행의 실제 호출은 입증하지 않는다.
- 공통 decoder를 binary에 적용한 모든 20 state가 결과 JSON과 동일. owner count 불변식 8개×20표본 위반0. 양 pair 5개 전체 player/unit record 차이0(총10비교), baseline 10개와 lap888 같은 tick 완료 상태 차이0. 추가로 candidate 10개도 기준과 일치.
- lap888 reference JSON SHA `02b5e67762b4bb260fa800f121af7628c03d56687374c9eed524200ebc2fbb72` MATCH. 직접 raw/header 해석은 기존 판정 JSON 복사와 구분한다.
- 입력 DOWN/RIGHT 동일 순서, emission before/after tick=24692/24788, WM_KEYDOWN/UP 수신, 각 1칸 카메라·최종 카메라 parity MATCH. 각 30-present 창의 raw 값 목록=persisted coverage 목록, p50≥264000 및 key전×0.9. PS3 outside diff0·unsupported0·0≤stale≤covered≤480000. 무수정 Scale2x validator 재실행 PASS.
- 빌드 DLL에서 두 wrapper의 `pushf/pusha → helper → popa/popf → update indirect call → pushf/pusha → helper → popa/popf → ret` 재확인. 저장된 함수포인터 target은 pinned 원본 update이며 C thunk가 없다. 6범위는 PS/tick/camera/player/existence/stock unit pool이고 host live/file은 같은 `_decode_batched_scene`를 사용한다. 필드 삭제 없음.
- 설치/원복 source에서 exact5-byte ownership·VirtualProtect 성공 후 쓰기·cache flush·protection 복원·B 실패 시 A rollback을 검토했다. 정상 실행과 cleanup은 PASS지만 **API 강제 실패/동적 rollback 원복을 실제 검증한 것은 아니다**. 기존 static 계약 가드 및 검토 한계로 유지하며 새 관측기/변이 gate를 임의로 요구하지 않는다.
- 각 private manifest DLL SHA MATCH·Wine prefix private/created_new·game 사본 부재·cleanup game_removed=true 및 prefix_processes_after=[] 확인. 캡처 SHA도 MATCH하나 이번 visual verdict/전체 G1 UI 승인을 수행한 것은 아니다.

## 명령 / 검증 / 재현 artifact

- `cat loop/PROMPT.md`부터 ①~⑥ 읽기 순서 적용, STOP/ESCALATE/FULL_TEST 부재 확인. 이전 dirty tree 보존.
- `make doctor`: PASS(original verified). root 선택적 runtime manifest absent는 필수 실패/실제 게임 검증 아님.
- `make lint`, `make typecheck`: PASS. `.venv/bin/python -m pytest tests/test_g1_saved_scene_probe.py -q`: **128 passed / 2.04s**. source 계약/offline 검사 한정.
- `PYTHONPATH=. .venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap895_middle_review/recalculate.py`: captured raw 재계산 완료, 출력 verdict=HOLD_CURRENT_SOURCE_IDENTITY. 처음 current build 전입력 동일 assert가 실제 mismatch를 발견했다. 보존 source를 별도로 확인한 후 mismatch를 명시하고 raw 검산만 완료했다. 검산 스크립트의 packed header 10I→9I 전사 오류는 카드128-byte 구조로 고쳐 재실행했다(제품 수정/근거불명 실패 아님).
- 위 폴더 `recalculation.json` SHA `87dfe906e07c9777e2425d584b136cf0d1f43fb9c4044e23dad19e484742c3ac`, `runtime-current-source.diff` SHA `74676dd0109e17eddda256b83f09b437ec936514e9005418bee7d20f00386704`, `source_before.json`(48개)·DLL disassembly2개·Scale2x validator 재계산2개 보존. 이전 raw/PNG/result 수정0.
- fresh 전체 `make check`/새 build/runtime/24k/144k/패치 생성·복구: **SKIP(사용자 이번 근거 충돌 stop)**. 자동 exit0=제품 PASS/계획 승인 아님. 최종 safety/context/scoped whitespace/source 불변 확인 결과는 STATUS에만 보강한다.
- 압축 전 STATUS 전문126줄 SHA `6d68dbc532463b1fde1e76ff69e0124d37a98790be949e99de9d8a5140c93951`는 `docs/history/20261003_status_lap895_precompaction.md`에 byte-exact 보존. APPROVALS 전문248줄 SHA `70ad0056b9b43395d9f076e76a6cb3286f3ffcf7279c45a78b49035d2880619c`는 `docs/history/20261003_approvals_lap895_precompaction.md`에 byte-exact 보존하고 lap858로 종결된 lap857 block만 한 줄 포인터로 줄였다. 다른 pending/반려/상시 지시는 삭제하지 않았다.
- 변경 파일: 위 두 archive, 이 lap 기록, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, ignored `loop/ESCALATE_SOL`; 공유 temp 검산 산출물. source/test/validator/원본/save/protected 기준 변경0. HEAD `5d128e2f79581050ae81b418116b3c5c9cd98355`는 provenance만이며 커밋 없음.

## 승격 확인과 work tier handoff

승격 작업자는 두 보존 bridge source/manifest와 현재 source의 hook 설치 순서 차이가 단일 변경임을 독립 확인하고, **captured raw 수용과 현재 구현 runtime 미검증을 구분**한다. 위 E2~E4·coverage 검산을 재사용할 수 있으나 현재 B' PASS로 마감하지 않는다. 재허가 질문/상위 구조 재계획 없이 기존 P4b-S의 source 일치 검증을 work에 이관한다.

Work: 현재 guard-before-hook 구현/추가 회귀를 보존하고 새 경로에 DLL을 빌드한다. 입력44개+host/test SHA를 고정해 실제 DLL/manifest와 대조한다. E1~E4 같은 absolute r1 일정·lap888 reference·새 사본/prefix/display의 fresh pair **연속2회**를 완주한다. 추적 가능한 하네스 결함은 카드대로 고쳐 재실행하고, 결과를 지우거나 좋은 pair만 선택하지 않는다. 신규 제품 수정/기준 변경/기존raw 덮어쓰기는 하지 않는다. source 일치 결과를 새 middle이 수용한 뒤에만 C 계측OFF fresh3 → D-1 PS3 census → P5 순서를 잇는다. G1 사용자 마일스톤 승인/C/전체 HD coverage/두 번째 장면은 여전히 미검증이다.

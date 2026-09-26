# 2026-09-11 | lap 111 | G1 presentation trace runtime diagnosis

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high, 사용자 지정 중간 tier
  진단·계획·확인 역할. 게임 코드 hands-on 수정과 runtime 재실행은 하지 않았다.
- 가설 / 사용자 관찰: lap110 fresh trace의 `direct_draw_create_ex`에서 IID와 출력 객체가
  호출 ABI상 뒤바뀌어 PS40/tick0 정지의 충분 원인이 되었는지 독립 진단했다.
- 예상 PASS / FAIL 조건: 보존 trace SHA·game log·lap110 source SHA·원본 caller bytes를 독립
  재확인하고 x86 인자 순서와 hook prototype을 일치시켜 IID/출력 포인터 오류 및 PS40 정지의 충분
  인과를 설명하면 진단 PASS. 하나라도 충분히 입증되지 않거나 근거가 충돌하면 BLOCKED로 남긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/20260911_lap111_sol_g1_presentation_trace_runtime_diagnosis.md`,
  `docs/plans/20260911_lap111_g1_presentation_trace_abi_repair_card.md`, `docs/STATUS.md`,
  `loop/ESCALATE_SOL`; 문서만 uncommitted. game/bridge/runtime/patch 코드 변경 없음.
  보존 SHA: STATUS `e054c96376f0b6237e0c40b53ab15b53d0294998a16381a1106e09c0ea2acb36`,
  repair card `a429a74f589a2416d3d4c7dcf33393a1227b1ac95724fbad4c140b578465dd7b`,
  escalation `6ddad54a1a2fef5bbecd43f291b5788a12f510c1d145044a90ef700b3d2511bc`.
  lap110 source SHA `3f4758d095067452a890a906b6472c8d03e77a0295a1b6af7202292868113438`,
  validator `541e8448...`, runtime `c417b9f0...`, test `3ab4bb24...` 재현.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  source/private EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  `cmp=0`, PE32. lap110의 fresh private whole copy/new win32 prefix/Xvfb `:91` artifact만
  읽기 전용 검수했다. candidate/새 실행/활성 플레이어/지도/군대 N/A, fresh fixture SKIP.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `cmp -s`, `file`, `objdump -p/-d/-s/-h/-t`;
  MinGW `ddraw.h` 선언 대조; 보존 raw
  `local/runtime/20260911_133318_1248520_0/output/g1_presentation_trace/trace_raw.jsonl`
  SHA `53c53901a165adcb3dcbe88f144ed5e96d15dfe927d00ebc0019235c9e80e347`, game log SHA
  `d79b07857c1db7861301a2e89b586154b3ea9a69fd3529330ae6c86d68b0d8f6`, bridge SHA
  `0ae931603134ce6389aadfedb3efd082a5b74af2a98ad10d4baa284dc3ffbd09`.
  `make doctor` exit0/top `ok=true`(optional runtime manifest absent), 초기 `make check` exit0,
  `bash checks/safety.sh check`=`SAFETY_PASS`; 보존 raw 직접 validator=`BLOCKED`. 문서 갱신 뒤 최종
  `make check && bash checks/safety.sh check`는 STATUS `183>180` 안전 위반으로 exit2였다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **REVISE; root-cause diagnosis PASS**.
  `ddraw.h` ABI는 `(GUID*, LPVOID*, REFIID, IUnknown*)`지만 source typedef/hook은 2·3번째가
  반대다. 원본 caller는 arg2=`edi` output, arg3=`0x004E5928` IID를 넘기며 IID 16 bytes도 expected와
  일치한다. 원 함수는 positional forwarding 덕분에 `HRESULT=0`이나, 반환 뒤 hook은 output storage를
  IID로 읽어 `01E6D080-...`, IID를 output으로 읽어 `dd_object=0x15E65EC0`을 기록했다. DLL fault
  RVA `0xA90D`의 `mov esi,[ebx]`와 runtime `0x78CBA90D` read fault target `0x15E65EC0`이 정확히
  일치하므로 이 잘못된 vtable dereference가 PS40/tick0 정지의 충분 원인이다. 초기 Fast는
  **145 passed**, Ruff/compileall/mypy/context PASS지만 native ABI를 묶지 않아 결함을 놓쳤다.
  최종 필수 Fast는 **13 failed, 132 passed**이고 뒤 safety는 SKIP됐다. 새 runtime은 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본/후보/baseline/golden 변경 없음.
  runner가 Wine debugger에 붙은 crash를 90초 일반 PS timeout으로 가릴 수 있으나 ABI 수리와 분리한다.
  STATUS line-cap 필수 게이트 실패로 이 세션은 승격한다. G1/M1·2단 수리 컨펌·사용자 승인 없음.
- 다음 한 가지: 승격 작업자가 STATUS 중복을 provenance 보존 compaction해 180줄 이하로 만들고
  safety/Fast를 재검증한다. PASS 뒤 Luna/high ABI repair card를 handoff한다.

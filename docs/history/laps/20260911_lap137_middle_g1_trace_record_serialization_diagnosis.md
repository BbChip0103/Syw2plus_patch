# 2026-09-11 | lap 137 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 현재 대화 표면은 실제 model ID/effort attestation을 제공하지
  않으므로 모델을 추정하지 않았다. 사용자 지정 중간 tier(진단·계획·확인)로 수행했고 게임 코드는 수정하지 않았다.
- 가설 / 사용자 관찰: lap136 final trace malformed는 summary 내용 자체나 raw 복사 결함이 아니라,
  `trace_event_raw()`가 1024-byte Win32 formatter 한계를 넘는 완성 record를 한 번에 조합한 결함이다.
- 예상 PASS / FAIL 조건: 보존 SHA가 일치하고, 마지막 record만 정확히 1024 bytes/NUL@1023이며,
  source의 prefix+details+suffix 예상 크기와 `wsprintfA` 공식 한계가 이를 잔여 없이 설명하고,
  targeted/Fast/doctor/safety/fresh PE32 build가 예상대로 PASS하면 원인과 work 범위를 CONFIRMED한다.
  artifact/source 불일치나 설명되지 않는 bytes가 있으면 FAIL 및 승격 유지다. 게임 runtime은 SKIP한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/source/test/제품 파일은 변경하지 않았다.
  문서 `docs/STATUS.md`, `docs/plans/20260911_lap137_g1_trace_record_serialization_handoff.md`, 본 history를
  추가/갱신하고 처리된 `loop/ESCALATE_SOL` SHA256
  `73b662b8d91eb31d69455bd900f80feea30cc605da30acf231351fa5a4124dc5`를 아래에 보존 후 제거했다.
  검수 source SHA는 `tools/inmm_stub/direct_draw_trace.c=412315b1f5c1199d97a63d9bdee3a580fb12bed95cc6bcccb336c67466c4a121`,
  `tools/check_g1_presentation_trace.py=a58a8aa13bd3affb25aaf7355ef5bf803c6fea0efb1320a6c27557f308ef4c1a`,
  `tests/test_g1_presentation_trace.py=5d68f12e4d1ed071d27c5418d18519419f6e43af1ca1732bc5791537a36ec13d`다.
  최종 `docs/STATUS.md` SHA256은 `67b7c6173593e7e8ce6f7183489add80f1e133a6b30bbeb004e94724c106dabb`,
  handoff SHA256은 `880adc20f57948e5fe270211a4f0b13d0ef5e34d2830f84d09b95f19782dceb4`이며
  본 self-referential history SHA는 생략한다. `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` doctor verified/무변경.
  제품 후보 없음. lap136 실제 runtime artifact를 read-only 진단 입력으로 사용했고 새 게임 실행은 없다.
  fresh out-of-tree compile-only PE32 diagnostic DLL SHA256
  `ec318c8d00edfff736444b8e765c830a2f2a165572d13d756f017804fc04a272`;
  새 활성 플레이어/지도/군대는 N/A/SKIP, synthetic gameplay fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, binary Python probe, source/line 대조,
  Microsoft `wsprintfA` 공식 문서 확인, `python3 -m pytest -q tests/test_g1_presentation_trace.py
  tests/test_direct_draw_abi.py`, `make check`, 저장소 밖 `/tmp/syw2plus_lap137_bridge.jh3s3z`의 `make clean all`,
  `file`/SHA, `make doctor`, `bash checks/safety.sh check`. 입력 raw는
  `local/runtime/20260911_172631_3142585_0/output/g1_presentation_trace/trace_raw.jsonl` SHA256
  `19e3a3e8351ca8a13ad19ebec7b16f5e6c552a4b5bf6365a0db9f0b9453c2499`; 새 PNG/runtime 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): raw 651 lines/372031 bytes, 마지막 줄 1024 bytes,
  NUL offset `[1023]`, final newline false; 앞 650줄 max 628 bytes/NUL 0. 마지막 record에서 details 시작은
  offset 241, NUL 전 details fragment 782 bytes, source상 빠진 suffix `\",\"flush\":\"complete\"}}\n`는
  23 bytes여서 완성 길이는 1046, details 길이는 805 bytes다. `trace_event_raw:220-230`의 outer
  `wsprintfA` 한 번만 1024 한계를 넘는다. 공식 문서는 최대 output buffer 1024 bytes와 terminating NUL을
  명시한다. targeted **14 passed**, full **169 passed**, Ruff/compileall/mypy/context PASS, fresh build PE32 PASS,
  doctor original verified/no side effect, safety PASS. **MIDDLE DIAGNOSIS CONFIRMED**; repair/runtime/G1은 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 현재 targeted/Fast의 PASS는 native 1046-byte writer를
  실행하지 않아 결함을 포착하지 못한다. final summary/process exit/DLL detach/validator, G1 2배 출력,
  G2~G4와 사용자 승인은 미검증이다. implementation-unchanged-streak는 이번 문서-only lap으로 2가 되므로
  다음 바퀴는 handoff의 serializer+native regression이라는 측정 가능한 변경이어야 한다.
- 다음 한 가지: 새 Luna/high work tier가
  `docs/plans/20260911_lap137_g1_trace_record_serialization_handoff.md` 범위에서 bounded one-record serializer와
  1046-byte native 회귀를 구현·검증하고, 게임 runtime 없이 새 Sol/high 독립 검수로 넘긴다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
# lap136 승격 요청 — G1 fresh runtime final trace malformed

- 상태: 필수 fresh runtime 검증 FAIL/BLOCKED. 같은 run 재실행·다른 prefix/display 반복 금지.
- 실행: 새 private copy/prefix `local/runtime/20260911_172631_3142585_0`, Xvfb `:91`,
  `1600x1200x24`; 참고 원본·private EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- preflight `runtime_env.py check`는 RC0. 실제 `g1-presentation-trace`는 정확히 1회 실행했고
  RC2: `presentation trace clean finalization blocked: trace malformed: Invalid control character at:
  line 1 column 1024 (char 1023)`.
- 보존된 근거: `local/runtime/20260911_172631_3142585_0/output/g1_presentation_trace/`.
  `trace_install.jsonl` 205행/112043 bytes/SHA256
  `91ba534c31c8f441129370457e5c1af52429d7beb82bb1e377aad000cda9ebf3`,
  `trace_raw.jsonl` 651행/372031 bytes/SHA256
  `19e3a3e8351ca8a13ad19ebec7b16f5e6c552a4b5bf6365a0db9f0b9453c2499`.
- 즉시 원인 증거: raw 마지막 651행(1024 bytes)의 끝이
  `...,\"detach\":\"complete\x00`이며 JSON decode가 line 1 column 1024에서 실패했다.
  final summary와 validator PASS는 확인되지 않았다. `evidence.json` SHA
  `306ed1fbe2ffd9728e1561f32b676da10bf319dbace7e376ebde63de8b52d4a3`,
  `verdict.json` SHA `1cdc4f70a4153916ab9c0fad22684c8975b7341503695ddd6571e952b9768b67`.
- 관측된 범위: PS9→PS3, root 1600x1200/content 800x600, 실제 입력, owned PID 276의 단일 HWND
  `0x00020056`/WM_CLOSE post PASS. cleanup PASS, prefix residual process 0, 그러나 이것은 G1 제품
  2배 출력 승인이나 finalization PASS가 아니다.
- 후속 승격 작업자가 독립 확인할 것: `direct_draw_trace.c`의 최종 trace write 길이/널 종결자 처리와
  summary record 경계가 왜 JSONL에 NUL을 포함했는지 원인 규명, 최소 수정·회귀 테스트·fresh
  out-of-tree PE32 build를 정하고, 그 뒤에만 새 fresh runtime을 승인할 것.
- 이번 세션은 source/product EXE/DLL/assets/baseline/golden을 변경하지 않았다. 새 bridge SHA
  `9a0c68a8c40818dca62cf6e2cceab3aefbc49d9d03eebd636a8b9ceba676173b`, close helper SHA
  `273dc2bb7d819924a50a96f412d78f8265ad70af1c0e252483dc01f47d979fd3`.
```

제거 전 marker는 2228 bytes이며 위 SHA와 원문으로 보존했다.

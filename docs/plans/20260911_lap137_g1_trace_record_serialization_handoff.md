# 2026-09-11 lap137 — G1 final trace record serialization repair handoff

## 중간 판정

lap136의 마지막 trace가 malformed인 직접 원인은 **CONFIRMED**다. 보존 raw SHA256
`19e3a3e8351ca8a13ad19ebec7b16f5e6c552a4b5bf6365a0db9f0b9453c2499`의 651번째 줄만
정확히 1024 bytes이며 byte offset 1023이 NUL이고 개행과 JSON 닫힘이 없다. 앞 650줄은 최대
628 bytes이고 NUL이 0개다.

`tools/inmm_stub/direct_draw_trace.c:366-388`이 만든 summary details의 예상 길이는 805 bytes로
`wsprintfA` 자체 한계 안이지만, `trace_event_raw()`가 241-byte record prefix와 details 및 suffix를
다시 한 번의 `wsprintfA`로 조합하여 완성 레코드 1046 bytes를 요구한다. Microsoft의 Win32 계약은
`wsprintfA` 출력 버퍼 최대 크기를 1024 bytes로 제한하고 terminator NUL을 붙인다:
<https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-wsprintfa>.
관측된 1023 bytes text + NUL은 이 경계와 정확히 일치한다. `details[4096]`/`line[4096]` 배열 크기는
API 한계를 늘리지 않는다.

이 판정은 writer 결함의 원인과 수리 범위만 확정한다. final summary, process exit/DLL detach,
overflow-free validator, G1 2배 출력 또는 M1 승인은 여전히 확인되지 않았다.

## 다음 Luna/high work 한 가지

`trace_event_raw()`가 1024 bytes를 넘는 완성 JSONL 레코드를 단일 `wsprintfA` 호출로 만들지 않도록
bounded no-CRT serializer를 구현하고, lap136과 같은 1046-byte summary가 NUL 없이 `}\n`으로 끝나는
정확한 native 회귀를 추가한다. 이번 work 바퀴에는 게임 runtime을 실행하지 않는다.

### 허용 범위

- `tools/inmm_stub/direct_draw_trace.c`와 serializer를 직접 검증하는 최소 header/test fixture만 수정한다.
  validator schema와 summary 필드 의미를 바꿀 필요가 입증될 때만 관련 validator/test를 좁게 수정한다.
- 기존 kernel32/user32 및 MinGW 도구를 사용하고 CRT·새 라이브러리·새 Python dependency를 추가하지 않는다.
- 원본/참고 EXE·DLL·assets, private game copy, aggregate/event/method 상수, close helper/runner,
  baseline/golden, 좌표/timeout은 변경하지 않는다.
- summary 축소, method 필드 삭제, NUL 제거 후 잘린 JSON을 성공 처리, 여러 줄로 schema를 몰래 변경,
  `TRACE_MAX_*` 증가, validator 완화는 금지한다.

### 필수 계약과 측정식

1. record prefix, caller-provided details, `}\n` suffix를 `line[4096]`에 용량 검사하며 결합하고 한 record를
   한 번의 파일 write로 보낸다. payload length는 terminator NUL을 제외하며 `written == requested`를 확인한다.
2. prefix formatting처럼 1024 bytes 미만임이 구조적으로 보장되는 작은 `wsprintfA`만 남길 수 있다.
   details를 포함한 완성 record를 단일 `wsprintfA`/`wvsprintfA`로 조합하지 않는다.
3. 합계가 `sizeof(line)`을 넘거나 short/failed write이면 partial record를 PASS로 세지 않고
   `g_trace_failed`/dropped 또는 동등한 기존 fail-closed 상태에 반영한다. summary 실패 경로가 재귀하거나
   성공처럼 보이지 않아야 한다.
4. regression fixture는 lap136 shape를 재현하여 prefix 241 bytes, details 805 bytes, 완성 payload
   1046 bytes를 검사한다. 결과는 byte 0개 NUL, 마지막 `}\n`, 한 줄, strict JSON parse PASS,
   `detach=complete`, `flush=complete`, method count 보존이어야 한다.
5. max run_id 및 4096 경계의 success/fail-closed를 검사하고, 구현을 과거 단일 1024-limit formatter로
   되돌린 mutation이 회귀에서 FAIL함을 보인다. Python이 완성 JSON을 직접 쓰기만 하는 테스트는 불충분하다.
6. 기존 install/aggregate/typed-vtable/lifetime/close-finalization validator 계약과 source hashes를 새로 기록한다.

### 검증 순서와 중단 조건

1. 변경 전 raw SHA, 마지막 line 1024/NUL@1023, source SHA
   `412315b1f5c1199d97a63d9bdee3a580fb12bed95cc6bcccb336c67466c4a121`를 다시 대조한다.
2. native serializer 회귀를 먼저 추가하고 fail-before/fix-after를 기록한다. 저장소 밖 새 `mktemp -d`에서
   PE32 bridge를 build하여 `file`과 SHA를 남긴다.
3. targeted tests, `make check`, `make doctor`, `bash checks/safety.sh check`를 실행한다.
4. 모두 PASS해도 게임 runtime은 실행하지 않고 새 Sol/high 독립 검수로 넘긴다. 그 컨펌 뒤에만 새 private
   copy/prefix/unused display에서 runtime 1회를 승인한다.
5. exact one-record write와 fail-closed를 no-CRT 범위에서 보장할 수 없거나 필수 gate가 예상 밖 실패하면
   반복·validator 완화 없이 변경과 근거를 보존하고 `loop/ESCALATE_SOL`을 만든다.

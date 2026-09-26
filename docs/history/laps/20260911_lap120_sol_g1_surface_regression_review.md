# 2026-09-11 | lap 120 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-sol`/high middle.
  현재 세션 표면은 model ID/effort를 별도로 노출하지 않는다. 게임 코드·하네스·
  원본·후보를 수정하지 않고 lap119 source/tests/machine evidence의 독립 진단·콘펌만
  수행했다.
- 가설 / 사용자 관찰: lap119가 lap118 handoff대로 surface reuse의 모든 단일 조건
  mutation과 runner의 close→exit→summary→copy→validator 행동을 실행 경로에서
  고정했다면 fresh runtime 1회를 새 work session에 허용할 수 있다.
- 예상 PASS / FAIL 조건: 입력은 lap118 handoff, lap119 이력·source/test fingerprint,
  고정 원본 SHA다. runner의 순서와 summary 0/2·비최종·미종료 실패가 final runner에서
  validator 미호출/raw 보존을 직접 증명하고, surface 테스트가 production에서 쓰는
  동일 C 판정 경로의 success=49, 각 단일 mismatch/stale=failed·0을 실행해야 PASS다.
  단순 토큰 존재만 검사하거나 의미 변이가 통과하면 REVISE/runtime BLOCKED다.
- 변경 파일 / source fingerprint / 커밋: 검수 source는
  `tools/runtime_env.py=26028b0ab7d45cd601dedc879dbec206f981ad8ed99612b06e51b3f0346e6733`,
  `tests/test_runtime_env.py=9fc7e9f38a8edc0deb8e8818f8d686ad1fe3ea24a303edea4ab6f13caaf96a27`,
  `tests/test_direct_draw_abi.py=23ba3bb35d89a0c0dc31148f1af8cc365b2c4b2f045b54efe92f0ef6b638ffe0`,
  `tools/inmm_stub/direct_draw_trace.c=2b0bd730da5199f86b9efe1097cdee5aa57ccc2ceef47272db786c04dc8a147c`로
  lap119 기록과 일치한다. 판정 문서로 `docs/STATUS.md`, 본 이력, work handoff,
  `loop/ESCALATE_SOL`만 추가/갱신했다. `LOOP_ALLOW_COMMITS=0`, uncommitted/commit·push 없음.
  최종 해시는 STATUS `5d8097133f0cd3391445f6e341066ca83ec2b5b676d3e2f66565b2825bda016f`,
  handoff `f0a4dc873068de5913f398ef36312067c4fbde036dc99fa5dc16a47aa7eb19c9`,
  escalation `4caae7621b64006f0dc179a8f818ac5936ab1aceb0d7d3815f65fcf5cabaeaa4`다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, doctor
  original `verified`. 제품 후보·게임 실행·활성 플레이어·지도·군대는 SKIP/N/A.
  저장소 밖 diagnostic bridge fixture SHA는
  `970f66c2822ae5478d9714c28c87c71e730dcce43bc9dc650f28a08a4a650cb1`, PE32 80386 DLL다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`, `rg`, `sha256sum`, `stat`;
  `make doctor`; targeted pytest 3개 파일; `mktemp -d /tmp/syw2_g1_lap120_bridge.XXXXXX`
  후 `build_runtime_bridge.py`; `make check`; `bash checks/safety.sh check`; 저장소를 쓰지 않는
  Python 반례 probe로 첫 failure return을 뒤집고 token contract/native 문법을 검사했다.
  PNG/runtime trace/capture는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): doctor top `ok=true`/original verified
  (runtime manifest 미존재는 실행 SKIP 경계), targeted **90 passed**, fresh bridge build PASS,
  `make check` **177 passed**, Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`.
  runner pipeline과 4개 failure fixture는 **CONFIRMED**. surface 회귀는 `return FALSE`→`TRUE`
  의미 변이에서도 current token contract=`True`, native syntax exit=0이어서 **REVISE**.
  fresh runtime/G1/M1은 BLOCKED, patch old/new·unsupported-version·copy-only·non-overlap·restore는
  이 lap에 binary patch가 없어 SKIP/N/A다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Fast exit 0은 lap118의
  no-token-only 조건을 승인하지 않는다. 근거 충돌을 `loop/ESCALATE_SOL`에 보존했고
  게임/runtime은 재시도하지 않았다. G1~G4 및 사용자 마일스톤 승인 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high 승격 작업자가 반례와 handoff를
  독립 확인해 fresh runtime BLOCKED를 유지하고, Luna/high work 수리 범위를 확정한다.

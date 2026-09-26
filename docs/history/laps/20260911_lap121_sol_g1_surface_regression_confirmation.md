# 2026-09-11 | lap 121 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-sol`/high 중간 tier.
  현재 세션 표면은 model ID/effort를 별도 attestation하지 않으므로 이를 exit 0에서 추정하지 않았다.
  게임 코드·하네스·원본·후보는 수정하지 않고 lap120 반례와 work handoff만 독립 검수했다.
- 가설 / 사용자 관찰: lap120의 의미 반전 반례가 재현되고 lap120 handoff가 production과 동일 C
  판정 경로를 실행하도록 충분히 제한되어 있으면 SURFACE REGRESSION REVISE를 확정하고 Luna/high
  work로 돌려보낸다. 토큰 계약이 의미 변이를 거부하면 lap120 판정을 반려한다.
- 예상 PASS / FAIL 조건: 입력은 lap120 이력·marker·handoff, lap119 source/test fingerprint와 고정
  원본 SHA다. production-shared C 성공은 49, 16개 각 단일 불일치와 stale-uninstalled는 failed·0 및
  해당 reason을 직접 실행해야 최종 PASS다. 현재 토큰 계약이 `return FALSE→TRUE`를 수락하면 이번
  중간 판정은 반례 CONFIRMED / surface 회귀 REVISE / fresh runtime BLOCKED다.
- 변경 파일 / source fingerprint / 커밋: 구현 파일은 변경하지 않았다. 검수 SHA는
  `tools/runtime_env.py=26028b0ab7d45cd601dedc879dbec206f981ad8ed99612b06e51b3f0346e6733`,
  `tests/test_runtime_env.py=9fc7e9f38a8edc0deb8e8818f8d686ad1fe3ea24a303edea4ab6f13caaf96a27`,
  `tests/test_direct_draw_abi.py=23ba3bb35d89a0c0dc31148f1af8cc365b2c4b2f045b54efe92f0ef6b638ffe0`,
  `tools/inmm_stub/direct_draw_trace.c=2b0bd730da5199f86b9efe1097cdee5aa57ccc2ceef47272db786c04dc8a147c`,
  handoff `f0a4dc873068de5913f398ef36312067c4fbde036dc99fa5dc16a47aa7eb19c9`다. 본 이력과
  `docs/STATUS.md`만 문서 변경하고 처리한 marker SHA `4caae7621b64006f0dc179a8f818ac5936ab1aceb0d7d3815f65fcf5cabaeaa4`는
  아래 원문 보존 후 제거했다. 최종 STATUS SHA는
  `6feb31faa7650716c11ecc52260215538bcf04d56d15f0794c4e298f62a9e3fd`이며 본 이력의
  self-referential hash는 의도적으로 생략한다. `LOOP_ALLOW_COMMITS=0`, uncommitted/commit·push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: doctor의 보호 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, status `verified`.
  제품 후보·게임·활성 플레이어·지도·군대는 SKIP/N/A. 저장소 밖 변이 source
  `/tmp/syw2_g1_lap121_mutation.Ne2oSI/direct_draw_trace.c`와 diagnostic bridge
  `/tmp/syw2_g1_lap121_bridge.tLvVuZ/bridge/_inmm.dll`만 fixture로 사용했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`, `rg`, `sha256sum`, 임시 복사본의 첫 실패
  `return FALSE`를 `TRUE`로 바꾼 token/native syntax probe, targeted pytest 3개 파일, `make doctor`,
  저장소 밖 `build_runtime_bridge.py`, 기록 후 `make check`, `bash checks/safety.sh check`를 실행했다.
  bridge는 PE32 Intel 80386 DLL, SHA `617e1d66b6ea2ee8ac8c51273ca03b176ab6d829227659cf918bea2d9701605e`다.
  PNG/runtime trace/capture는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 변이 guard는 `return FALSE` 0개/`return TRUE` 2개인데도
  current token contract=`True`, native syntax exit=0이다. targeted **90 passed**, doctor top
  `ok=true`/original verified, fresh bridge build PASS다. `make check` **177 passed**, Ruff/compileall/
  mypy/context PASS, safety `SAFETY_PASS`다. 판정은 **LAP120 COUNTEREXAMPLE CONFIRMED / SURFACE
  REGRESSION REVISE / FRESH RUNTIME BLOCKED**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: lap120 handoff를 범위 변경 없이 승인한다.
  diagnostic-only 테스트 seam은 production hook과 동일 `surface_record_reusable` 또는 한 개의 공유
  결정값을 호출해야 하며 독립 Python model/토큰 검사는 대체 증거가 아니다. work 결과도 새 Sol/high
  독립 검수 전 runtime을 허용하지 않는다. G1~G4 및 사용자 마일스톤 승인 없음. 이번 문서-only
  middle lap으로 implementation-unchanged-streak가 2가 되므로 다음은 재검토가 아니라 위 실행형 C
  회귀라는 측정 가능한 구현 변경으로 고정한다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high가
  `docs/plans/20260911_lap120_g1_surface_behavior_handoff.md` 범위에서 production-shared C surface
  행동 회귀만 구현하고 게임/runtime을 실행하지 않은 채 machine evidence를 남긴다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
# lap120 middle -> Sol/high surface regression evidence review

reason=lap119's surface mutation test does not execute the production reuse/stale branches and accepts a semantics-reversing return mutation while all required tokens remain.
classification=SURFACE_REGRESSION_EVIDENCE_CONFLICT_FRESH_RUNTIME_BLOCKED
stop=Preserve current source/tests and lap120 documents. Do not run the game/runtime, change validator constants, patch binaries, commit, or push.

evidence=
- Recorded lap119 fingerprints match: runtime_env.py 26028b0a..., test_runtime_env.py 9fc7e9f3..., test_direct_draw_abi.py 23ba3bb3..., direct_draw_trace.c 2b0bd730....
- Fresh make doctor top ok=true/original verified; targeted 90 passed; make check 177 passed; safety PASS; out-of-tree PE32 bridge build PASS.
- Counterexample: replacing the first failure `return FALSE` in surface_record_reusable with `return TRUE` leaves the current 16-token contract accepted (`True`) and native syntax exit 0. The test therefore does not prove the required behavior.
- Runner pipeline behavior is independently CONFIRMED; only the surface behavior contract is REVISE.

required_review=
1. Reproduce or inspect the lap120 counterexample and confirm that passing Fast does not satisfy lap118's no-token-only requirement.
2. Keep fresh runtime/G1/M1 blocked and approve or narrow docs/plans/20260911_lap120_g1_surface_behavior_handoff.md for a Luna/high work session.
3. Require the work result to execute the production-shared C decision path for success, every single-condition mismatch, and stale-uninstalled failure before a new Sol/high confirmation.
```

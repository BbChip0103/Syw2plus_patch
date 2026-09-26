# 날짜 | lap 643 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Codex hands-on 구현 작업자 / native session.
- 가설: lap642 clean candidate의 `36`이 drag hit-test 범위 부족인지, selection 후 제품 경로의 crash인지 raw/capture/bytes 독립 대조로 분리한다.
- 변경파일: 제품 코드·EXE·원본·참고 저장소는 변경하지 않았다. `docs/feedback/INBOX.md`가 360줄이라 원문 SHA/전문을 `docs/history/20260926_inbox_lap643_precompaction.md`에 보존하고 포인터로 압축했다. STATUS/history/ESCALATE_SOL만 갱신한다.
- 원본·후보 SHA: protected source `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` before/after 동일; candidate `a123498ab6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`; probe source `tools/g5_candidate_drag_probe.py` SHA `45460b196d8e76406f1781638ea55fe2457f392503145cfadf664bc94ceb4f26`.
- 독립 실행명령/증거: 기존 lap642 foreground isolated run의 `probe-result.json`, `candidate-provenance.json`, `probe.log`, before/after PNG를 읽고 SHA/필드를 재집계했다. 새 Wine/probe/make check는 필수 runtime 실패 후 실행하지 않았다. context check: `python3 checks/context_limits.py` → `CONTEXT_PASS`.
- 측정값: original `PASS_ORIGINAL_CAP20`, selection20/movement20, camera `[19,90]`, fixture bounds `(25..31,96..103)`; candidate `FAIL_SELECTION_CAP`, selection36/unique36/movement36, storage `0x0108c000`/capacity50, camera `[40,140]`, fixture bounds `(46..52,146..153)`, cleanup `ok=true`. Candidate log: `wine: Unhandled illegal instruction at address 047A0480`; candidate after-drag capture is crash dialog and was captured before the scripted right-click.
- 판정: **BLOCKED**. 후보 36은 실제 selection snapshot으로 확인됐지만 world→screen hit-test 포함 범위와 `047A0480`의 정확한 제품 PC/시점은 아직 분리되지 않았다. 50/51·50기 명령·canary/save/load·G5 PASS는 미검증.
- 다음 행동(승격 작업자): raw unit coordinates와 camera/drag transform을 독립 계산해 55기 포함 여부 및 `0x0043877A` append count를 귀속하고, crash가 selection 직후인지 제품 명령 이전인지 확인한다. 원인 확정 후보가 있을 때만 fresh original20→candidate50/51→command50→canary/save/load를 실행한다. 원본 자동 갱신·golden 승격·커밋은 금지.


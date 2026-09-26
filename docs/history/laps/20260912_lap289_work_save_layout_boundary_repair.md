# 2026-09-12 | lap 289 | G1 S1 저장 레이아웃 work 정정1

- 실제 provider/model/effort / 지정 역할: work tier, hands-on 구현·검증 / configured Codex work `gpt-5.6-luna`, high.
- 목표: lap288 middle이 지적한 원래 대상 work probe의 save 함수 경계를 `0x440F5B` exclusive로 좁히고, 인접 load의 `0x4DA4A9`가 save 호출로 분류되지 않는 회귀 단언을 추가한다. 게임·runtime·Stage B는 범위 밖이다.
- 가설 / 예상: 경계 수정은 기존 static 모델 출력을 바꾸지 않고, widened-window mutant에서 `0x4DA4A9` 단언이 실패해야 한다.
- 변경 파일 / SHA: `docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py`; 편집 전 `bfbe56469763981a3ef026eae83ef3f0059c7bcdf6b050cc8807f1d5d2eb2bfb`, 편집 후 `6f2572a4c199d668742b1d84f417050e80e8a738e7d20c6b4d31b04e2810e9cf`; 커밋 없음(`LOOP_ALLOW_COMMITS=0`). 실행 증거는 `logs/lap289/`에 보존했다.
- 원본·fixture SHA: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save000 `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`; save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; save011 `23dd24d58555588e0ca09491559aed66ad3f2544ff3195c5af2ab9e2be14dfa4`; save012 `5a6863c1eafaa8bd9a087238a41d45c45635dd66a208cf79a186e158819c28f1`. 원본·fixture 쓰기 0.
- 실행 / 결과:
  - work probe 편집 전·후 각각 `.venv/bin/python docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py`: 둘 다 exit 0, `failures=[]`; JSON SHA 모두 `7381b5f7ebbc99a6a6d9e9cdc0ce95b3bcbaf6237645d521b83c59eba5cbfb81`; layer 28, roster 375/558/147/149. 후출력은 `logs/lap289/work_save_layout_after.json`, 전출력은 `...before.json`이다.
  - widened-window in-memory mutant(`SAVE_END=0x440FF0`)은 exit 1, `0x4da4a9 was included as a save fread target: ['0x00440fa4']`를 발화했다.
  - lap279 재실행 exit 0, 기존 출력과 바이트 동일 SHA `e848c940ee6d4c437b3b4d0223dfc606bb46fff08698241ee7a55913c9db2ddd`; lap284 middle runtime probe exit 0, 기존 출력과 바이트 동일 SHA `2870383083dea5f1914a732d9d6ec468352a4f11f6854a46fd105e7673d52d60`.
  - lap280 재실행은 **예상 밖 실패**, exit 1: `internal_id=i(0x...)` 정규식이 `None`을 반환해 line 130에서 `AttributeError`; stderr를 `logs/lap289/lap280_crossverify_rerun.stderr`에 보존했다. 재시도하지 않았다.
- 판정: work 정정 자체와 출력 불변은 PASS. 필수 세 probe 전체 대조는 lap280 traceback 때문에 FAIL/ESCALATE. `make check`, safety, 전체 Fast는 실패 후 지시대로 실행하지 않았다. 게임/Wine/Xvfb/PNG/Stage B/원본 실행 0.
- 남은 위험 / 독립 검수: lap280 source/fixture provenance와 정규식 기준을 다음 승격 작업자가 진단해야 하며, 실패 원인 해결 전 카드 종결·마일스톤 PASS·Stage B를 금지한다.
- 다음 한 가지: middle/승격 작업자가 lap280의 `internal_id` 정규식 실패를 원인 분석하고, 동일한 세 probe 대조를 fresh run으로 재검증한 뒤 이 work 변경을 ACCEPT/REJECT한다.

# 2026-09-12 | lap 246 | 목표 G1 Stage B — R6-B-R11 middle 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 게임 코드 hands-on 구현 없음. 검수 대상은 lap245 work(R11)다.
- 가설 / 사용자 관찰: lap245의 "변이 8 failed"는 8개 전부를 죽인 신호다. R7/R10/R17 테스트는
  preflight `output_refusal`이 결정하므로 writer의 open 모드를 관측할 수 없다. 따라서
  전멸 신호는 targeted 변이가 아니라 깨진 미러의 지문일 것이다.
- 예상 PASS / FAIL 조건: (a) 변이 없는 동일 재배치 복사본이 그대로 8 failed면 lap245 신호는
  공허하다. (b) 깊이를 맞춘 미러에서 변이가 R11만 죽이고 preflight 테스트가 살아남으면 R11
  회귀 자체는 비공허하다. 둘 다 성립하면 "R11 회귀 승인 + lap245 증거 무효"다.
- 변경 파일 / source fingerprint / 커밋: 커밋 없음(`LOOP_ALLOW_COMMITS=0`, uncommitted).
  - `docs/history/laps/probes/20260912_lap246_r11_reverify_probe.py`
    sha256 `06a1991a27babcee94a06f4367a54868a6dc1dd632b8e2e6d87c8ffa65a0be67` (신규)
  - `docs/history/laps/probes/20260912_lap246_r11_reverify_report.json`
    sha256 `5b4cf4bf5fd0d35a596247d73f8a7c158e73f96fe439f074cb8487be60faef63` (신규)
  - `docs/history/laps/probes/20260912_lap246_r11_reverify_report.PROVENANCE.md`
    sha256 `3c2fa9dd35102e4ab358da443e1d564fbc1e5635b457eed933c90d5905fa8308` (신규)
  - `docs/history/laps/probes/20260912_lap245_r11_regression_report.PROVENANCE.md`
    sha256 `0955f88ffa605c50233a0be62ef6d993a5c88556103f2f83f6b56946bee74265` (신규)
  - `docs/history/laps/20260912_lap246_middle_r11_reverify.md`(이 파일), `docs/STATUS.md`,
    `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`
- 검수 전후 불변 확인(원문 보존): `tests/test_review_probe_output.py`
  `6ebf9e3248a8a494829d3dbfafd7e62d4308534158995069ba98c4d930755bb2`,
  `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`,
  lap245 probe/report 원문 무변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변,
  `tools/runtime_env.py` `bb10cd84ddcb521b704318aeccb60125cec0abd89436e16b0b25d1ed918d2dab` 불변.
  후보/제품 EXE·DLL·assets·baseline·golden 변경 0. **게임/Wine/Xvfb/PNG 실행 0회**이므로
  플레이어/지도/군대는 N/A. fixture는 임시 dangling symlink와 저장소 밖 probe/test 미러뿐이다.
- 실행 명령 / 로그: `.venv/bin/python docs/history/laps/probes/20260912_lap246_r11_reverify_probe.py
  --output docs/history/laps/probes/20260912_lap246_r11_reverify_report.json` → exit 0;
  `make check`; `LOOP_DRY_RUN=0 bash checks/safety.sh check`.
- 측정값 / 판정:
  - C0 실제 probe 기준선 = **8 passed**.
  - C1 lap245와 동일한 얕은 `/tmp` 재배치, **변이 없음** = **8 failed**, 실패 목록이 lap245
    보고서의 8건과 동일. 재배치만으로 `ROOT = parents[4]`가 `IndexError: 4`를 던져 probe가
    import 단계에서 죽는다(직접 재현 확인). → lap245 변이 신호는 **공허(정보 0)**.
  - C2 `parents[4]` 깊이를 맞춘 미러(+`tools/runtime_env.py` 사본), 변이 없음 = **8 passed**
    → 미러 자체는 충실하다.
  - C3 같은 미러에 `open("x")→open("w")` 변이 = **1 failed, 7 passed**, 죽은 것은
    `test_r6b_r11_exclusive_create_rejects_dangling_output_symlink` **하나뿐**이고 R7/R10/R17
    preflight 테스트 6건은 모두 생존.
  - 직접 관측: 통제(`x`) = exit 2, `refusing to overwrite existing evidence`, symlink 보존,
    target 미생성. 변이(`w`) = exit 0, symlink를 따라가 **target 생성**(grid cases=13689).
  - 게이트: `make check` **269 passed** (Ruff/compileall/mypy 10 files, `CONTEXT_PASS`),
    safety **`SAFETY_PASS`**.
  - **판정: R11 회귀 자체는 PASS/범위 승인**(비공허성을 독립 증거로 재성립).
    **lap245의 비공허성 증거는 FAIL/무효**로 기록한다. 제품 G1 승인 아님.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 하네스 결함 1건(attempt1 디렉터리 이름 충돌)은
  보고서 미생성 상태로 PROVENANCE에 보존했고 SUT/임계값은 바꾸지 않았다. 신규 카드 **R20**:
  저장소 밖 미러 변이 하네스가 M0(변이 없는 대조군)을 요구하지 않아 재배치 실패를 "검출"로
  오독했다. lap244는 M0 대조군을 썼고 lap245가 그것을 뺐다. S1/F2-R2, R6-B-R2 재결 대기와
  Stage B 실행 금지는 그대로다. 사용자 마일스톤 승인 없음.
- 다음 한 가지: work tier가 **R12**(CORRUPTED가 UNAVAILABLE에 가려짐)를 게임 없이 구현한다.
  R20은 R19 뒤 큐에 둔다.

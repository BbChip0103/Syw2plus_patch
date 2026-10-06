# 2026-09-29 | lap 776 | G1 W60 lap775 menu eligibility 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex native middle(진단·계획·확인), 정확한 backend model/effort는
  이 native-hook 세션에 노출되지 않음. 게임/bridge hands-on 수정 금지 역할을 준수했다.
- 가설 / 사용자 관찰: lap775 메뉴 미전환은 live surface 귀속 자체가 아니라 logical 800×600 내용을 담은
  1600×1200 backbuffer peer를 600-high offscreen만 허용하는 W60 eligibility가 거부하기 때문이다.
- 예상 PASS / FAIL 조건: source/raw SHA 일치, live primary/backbuffer identity·caps·dimensions와 호출 분포를
  독립 재계산하고 단일 reject 조건 및 caller/state pin 없는 최소 수리·반증 조건을 지정하면 PASS; 귀속 충돌이나
  근거 부족이면 HOLD 후 승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/bridge/test 코드 0 변경. 문서만
  `docs/history/laps/20260929_lap776_middle_g1_w60_menu_backbuffer_gate_review.md`, `docs/STATUS.md`,
  `docs/feedback/APPROVALS.md`, `loop/ESCALATE_SOL`; 커밋 없음(`LOOP_ALLOW_COMMITS=0`). 검수한 lap775 source
  SHA 6개는 lap775 기록(`a805d0b1…`, `c3c572ab…`, `b8113023…`, `ca31942a…`, `a149d638…`,
  `2c04a409…`)과 일치했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; EXE 후보 변경 없음. lap775 r7
  private Wine32/Xvfb, default two-player random, synthetic=false, 진단 gate `0x0097597c` write/restore fixture를
  재사용하지 않고 보존 raw/capture만 read-only 재계산했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: raw
  `local/runtime/g1_w60_lap775_r7/20260929_205207_2960843_0/output/g1_presentation_trace/trace_raw.jsonl`
  SHA `a5563bcddd28d00918735ac567514668710775a0f381381b88a92f08f508fe84`; evidence
  `c87a006a…85b4`, verdict `42f4e852…f0f5`. PS9 capture SHA `4bf34b6f…d870`, PS7 capture
  `dd841fb5…a27e4`, PS3 capture `19bd8e89…387c6`. `pytest -q tests/test_g1_mirror2x.py` 9 passed;
  `make -C tools/inmm_stub -B` PASS; `make doctor` 원본 verified. fresh `make check` **1145 passed·5 skipped**,
  Ruff/compileall/mypy/context PASS(689.60s); log `logs/gates/full-test-20260929-lap776.output` SHA
  `372e5891bf6e72610755682991d76c9ab156d6447e26793f991b5a2e783b67ff`, exit 0. 별도 safety PASS.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 메뉴 primary BltFast 293회 = PS9 47 + PS7 71 + PS5 175.
  전부 destination `0x01E719A0` live 1600×1200 caps `0x8A38`, source `0x01E71AD0` live 1600×1200 caps
  `0x081C`, `x=y=0`, `src=NULL`, `source_desc_known=1`, HRESULT0, converted0. 함수는
  `source_height != 600u`에서 FALSE. PS3 source `0x01E71D30` 832×600 caps `0x0840`은 237/237 converted,
  mirror event 237, oracle 1.0. **`HOLD/BLOCKED(candidate eligibility)`**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: stale SurfaceRecord 원인 가설은 현재 raw로 기각.
  backbuffer top-left 800 영역 Lock 가능 여부와 fallback 경로는 runtime 미검증이며 work가 입증해야 한다.
  기존 fallback 성공 뒤 original BltFast 재호출 가능성도 함께 고친다. S1/S2/FEASIBLE/G1/사용자 승인 미통과.
- 다음 한 가지: work tier가 `loop/ESCALATE_SOL`의 surface-role gate·fallback 제어·compiled 회귀를 최소
  수정하고 fresh 메뉴/PS3 runtime→성립 후 off/on paired→Fast를 완료해 새 middle에 넘긴다.

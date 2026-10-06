# 2026-10-04 | lap 962 | G1 middle — lap961 W-2 독립 검수 · V2s 사용자 판단 큐 · 오른쪽 가장자리 terrain stale 인계

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(독립 검수·계획). 게임 hands-on 수정 없음. `loop/.lap_counter` 962 읽기만.
- 가설 / 검수 대상: lap961 W-2(hit 비교 viewport 제한)가 비교 범위만 바꿨고, R-1~R-5 수치가 raw로 재현되는지. steady replay 잔여가 새 key 최초 바인드인지. replay fill 한정을 지금 할지. V2s production HOLD 처리 방향.
- 예상 PASS / FAIL: lap961 기록 수치가 제품 helper 없는 재계산과 불일치 0이면 PASS. diff가 바인드/verify/replay를 건드렸거나 full viewport에서 동작이 달라지면 FAIL.
- 변경 파일(uncommitted, 문서만): 본 기록, `docs/work/active/G1_MIDDLE_W70_W2_ACCEPTANCE_TERRAIN_EDGE_HANDOFF_LAP962.md`, `docs/feedback/APPROVALS.md`(사용자 판단 큐 1항), `docs/STATUS.md`(압축 + 갱신, 원문 history 보존). 게임·source·test·DLL·validator 변경 0.
- 원본 SHA / fixture: 원본 EXE `b56986e0…a8ac`·save006 `616b7997…d064` read-only MATCH(직접 sha256sum). 검수 source: `g1_hd_asset.c cf682cdf…4015`·`g1_hd_asset.h 2784a22d…580e`·`g1_mirror2x.c fbc4abd4…a55`·`test_g1_mirror2x.py 54bbe34a…ffd` = lap961 기록 = lap961 bridge 사본. 비교 기준 lap959 bridge 사본 `531f1a4b…9bf59`/`7833f328…edf`/`167be0f8…29`. 활성8인 부하증명 아님.
- 실행: 새 게임 실행 0. 공유 temp `20261004_lap962_middle_review/`: `recalc_lap962.py`(`57895f85…c43e`)→`recalc_lap962.json`(`12f89652…5612`), `crop_lap962.py`(`0ff1a5c3…6a99`)→`side_production_top_lap962.png`(`25368d54…59b`)·`side_minimap_top_lap962.png`(`e5fc8acd…9f9`)·`zoom_production_top_lap962.png`(`bfb8c2d0…2f2`), `residual_class_lap962.py`(`d94feeb2…a8d7`)→`residual_class_lap962.json`(`4a13766b…78bc`), `stale_residual_overlay_lap962.png`(`38616151…29b6`). 입력 lap961 pair `b5df22d4…dd9c`·trace `bf5f30df…6c4f`·mask `8db4a04b…d27`, 로그 `fa84ffb6…ac32`, exit 2(HOLD) 기록 일치.
- 측정 / 판정:
  - diff: `compare_visible_frame`은 `(0,0,799,599)`로 위임해 동작이 같다. 새 함수는 bind verify와 같은 포함형 +1 규칙을 쓴다. hit 호출부만 live viewport를 쓰고 bind verify도 같은 live viewport를 쓴다. replay/verify/bind 변경 0 → **PASS**.
  - R-1: refresh 0 / 서수150→끝 증가 0. steady 세 구간 `replay − 2×새 keys` = **0·0·0** → 잔여 replay는 새 key 최초 바인드로 계수상 확정(lap961 추론을 승격). ≤0.2 예측 미충족은 예측 모델 오류이며 결함이 아니다.
  - R-2: present 887·p50 6·p95 14·reinvoke 15 PASS. R-3: 위쪽 줄 58·교집합 9,880·p50 97.214%·min 93.767% PASS. R-4: 안전 0 PASS. V2s raw는 pair-result와 5/5 일치(production 2,785 FAIL → HOLD). R-5: minimap 전 항목 true.
  - V2s 진단(gate 아님): Scale2x(원본) ref production **3,547**(후보 raw보다 큼), unexplained 80~254(5 tag). PNG V3: 위쪽 건물 줄 seam/격자/색 이상 없음.
  - 새 사실: lap961 PS3 cov <90% present **0개**(lap957 6개)·min 93.767% → "PS3 초기 present 6~12 경계"는 해소(한 run).
  - 남은 steady stale 9,880 분류(census 근사): terrain_cache_transfer 59.62%·dd_surface_blt 36.32%. 덩어리는 (a) 오른쪽 가장자리 마름모 3,512px, (b) P6 로고(명시 잔여), (c) 툴팁 text surface Blt. `layer_covered_pixels` 425,984 = 832×512로 (a)는 expected 미갱신 stale이다.
  - 종합: **W-2 PASS(partial) 수용**. replay fill 한정은 보류(이득 미측정·R-2 충족). V2s production HOLD는 수리 불가 → APPROVALS 사용자 판단 큐. ESCALATE 조건은 없다.
- 회귀 / 남은 위험: 동적 viewport 장면·두 번째 장면은 미검증이다. 분류는 다른 run census의 근사다. H-E는 미증명이다. burst UNKNOWN·PS35·P6/P7 HD·D-2·사용자 승인이 남는다. 이번 검수는 기술 컨펌이며 사용자 마일스톤 승인이 아니다.
- 다음 한 가지: Sonnet work 1 lap — 카드 §5. clipped replay full viewport를 cache 대상 frame(832×512)에 맞추는 최소 수리 + cache verify 계수, fresh save006 scale2x pair. 예측 E-1 오른쪽 가장자리 stale 3,512→≤350.

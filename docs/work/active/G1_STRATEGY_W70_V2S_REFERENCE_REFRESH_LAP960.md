# G1 lap959 승격 판정 — V2s Scale2x 기준 재정의 · tinted hit 비교 refresh churn 수리 인계 — lap960

## 판정 요약

- 지정 역할 strategy(Claude Code `claude-opus-5-5`, high, Fast OFF; 내부 CLI `astra` 호환 이름). 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 960 읽기만.
- lap959 승격(`loop/ESCALATE_SOL`)의 세 항목을 현재 raw/source/PNG로 재계산해 판정한다. 원문은 `docs/history/20261004_lap960_prior_lap959_escalate_sol_byte_exact.txt`로 보존.
- **D1 (V2s):** V2s raw(정확히 1개 흑색 subpixel 블록 수 ≤2,000)는 **정상 Scale2x 출력과 구조적으로 양립 불가**다. 원본 프레임을 완벽히 Scale2x한 기준만으로 지금까지 캡처한 35개 tag 전부 2,166~3,547 → 한도 초과. V2s를 설계 의도(lap903 §3: 격자 seam 유입 검출)대로 **"Scale2x(원본)으로 설명되지 않는 단일 흑색 블록 ≤2,000"**으로 재정의한다. 한도 2,000·5 tag·aggregate 규칙·V1/V2/V2q·Scale2x validator는 그대로다. raw 값은 계속 기록한다(비gate 진단).
- **D2 (성능):** 저하의 주원인은 화면 밖 origin 바인드 자체가 아니라 **바인드된 key가 hit 경로 `g1_hd_asset_compare_visible_frame`(800×600 교집합 비교)에서 불일치로 evict → 다음 호출에 viewport replay 2회로 재바인드**되는 churn이다. 최소 수리 = hit 비교를 renderer viewport 안으로 제한(바인드 verify와 같은 사각형). FEASIBLE, 다음 work 1 lap.
- **D3 (minimap):** `same_unit_before_after=false`는 클릭 **전** 상태 분기(후보 slot170이 이미 command4·위치 이동)로 귀속된다. 입력 매핑 결함 근거 없음. 이 pair는 HOLD 유지, PASS 승격 없음. D2 뒤 fresh pair에서 재판정.
- lap959 수리(P-1/P-2/P-3·안전)는 work 측정 그대로이며 독립 middle 검수 전이다. lap959 pair-result 원문(HOLD)은 고치지 않는다.

## 1. D1 근거 — V2s 독립 재계산 (제품 helper 미사용)

- 스크립트 공유 temp `20261004_lap960_strategy_review/v2s_scale2x_reference.py`(SHA256 `30e8c24a…0241`). 정의: 월드 `y<480`, 원본 비흑색 픽셀 중 후보 2×2 블록 흑색 subpixel 정확히 1개(raw); 같은 계수를 원본 800×600에 표준 Scale2x(EPX, 가장자리 clamp)를 적용한 1600×1200(ref)에 대해; flagged 블록의 흑색 subpixel이 ref 같은 위치에서도 흑색이면 explained, 아니면 **unexplained**.
- 결과 `v2s_scale2x_reference.json`(`ba3584f6…e96`), 대조 fixture `v2s_control_fixtures.json`(`829a7de1…b5`):

| 묶음 (tag 수) | raw | ref(완벽 Scale2x 기준) | unexplained |
|---|---|---|---|
| lap854 P3c gate1~3 (15, lap903 정상군) | 476~614 | 2,207~2,269 | 456~587 |
| lap901 P4c green/green_r2/origin (15, lap903 격자 결함군) | 18,882~20,056 | 2,187~2,596 | **18,712~19,901** |
| lap957 r1~r3 (15, 수리 전) | 1,044~1,705 | 2,166~3,547 | 8~158 |
| lap959 r1 (5, 수리 후) | 1,667~2,813 | 2,175~3,540 | 22~220 |

- raw는 lap959 `pair-result.json`의 `v2s_single_black_blocks`(1,732/1,667/1,670/1,675/2,813)와 **정확히 일치**, lap903 §1.2 표(476~614 / 18,882~20,056)도 정확 재현.
- 해석: (a) ref > 2,000이 35/35 tag → coverage가 100%에 가까워질수록 정상 구현이 V2s raw를 반드시 넘는다. lap903의 한도 근거 "정상 최대 614"는 지형 미러 이전 저coverage 표본이었다(전제 붕괴). (b) lap959 production 증가분 1,114 중 flagged의 92%가 ref와 같은 subpixel(Scale2x 모서리). (c) unexplained는 격자 결함을 18.7k~19.9k로 여전히 9배 넘게 분리하고 정상군은 ≤587.
- 이 재정의는 coverage 개선을 이유로 한도를 올리는 것이 아니다. 한도·tag·집계는 그대로이고, 세는 대상을 "원본을 정상 Scale2x했을 때 생기지 않는 흑색"으로 바로잡는다. 격자 결함 반례(lap901)는 계속 FAIL이어야 한다.
- 승인 경계: V2s는 lap903 strategy가 만든 내부 경보선이며 DESIGN/사용자 golden 기준이 아니다. 이번 재정의는 strategy 판정으로 APPROVALS에 기록하고 사용자 번복 가능하다. G1 사용자 마일스톤 판단 때 raw·ref·unexplained를 함께 보인다. 과거 pair-result는 재작성하지 않는다.

## 2. D2 근거 — refresh churn

- source(`g1_mirror2x.c` SHA256 `531f1a4b…9bf59`, lap959 기록과 일치): viewport replay는 `asset_started && needs_identity_frame && clipped`일 때만, 바인드 시도당 2회(0x00·0xFF, 각 `stride×surface_height` fill). key(`find_key_for_request`)는 origin 무관 → 정상이라면 key당 1회 바인드.
- `g1_hd_asset_compare_visible_frame`(hit 경로)은 `g1_scratch_intersection(origin, 800, 600)` 범위를 identity frame과 비교하고 한 픽셀이라도 다르면 identity·HD frame을 해제(refresh)한다. 반면 바인드 verify(`verify_unclipped_frame_in_viewport`)는 저장된 renderer viewport 안만 본다. 원본 writer는 viewport로 스스로 클립하므로(lap958 §2) viewport 밖 픽셀은 scratch_a에서 0x00으로 남고 identity frame(전체 viewport replay)에는 그림이 있다 → 화면 가장자리 스프라이트는 hit마다 불일치 → evict → 재바인드. (가설 H-R: viewport ≠ 800×600인 가장자리. 직접 픽셀 위치 계측은 아직 없음 — §4 반증 조건.)
- raw(`perf_replay_timeline.py` `34936a31…2552` → `perf_replay_timeline.json` `32e55767…80ed`, PS3=`program_state==3`):

| PS3 서수 구간 | lap957 r1 refresh / replay per present / p95 | lap959 r1 refresh / replay per present / p95 |
|---|---|---|
| 0~50 | 49 / 4.0 / 10ms | 191 / **20.7** / **53ms** |
| 50~150 | 44 / 2.96 / 12 | 99 / 3.22 / 20 |
| 150~300 | 0 / 0.05 / 9 | 155 / 2.55 / 17 |
| 300~600 | 0 / 0.03 / 14 | **299** / 2.37 / 12 |
| 600~끝 | 0 / 0.09 / 10 | 187 / 2.40 / 10 |

- steady에서 lap957은 refresh 0인데 lap959는 present당 약1회 refresh·2.4 replay로 줄지 않는다(inserts 1,757 vs keys 781 → 재바인드). 초기 50 present의 폭주(새 key 363 + refresh 191)가 present 수 899→788 감소의 대부분이다.

## 3. D3 근거 — minimap

- lap959 `pair-result.json` minimap action: 원본·후보 같은 선택(slot 124/140/151/170), camera·결과·gate 복원 동일, 4/4 pending_xy 변경. 다만 후보 slot170은 클릭 **전** `command 4`, `(146,100)`(원본 `command 1`, `(147,99)`)이고 클릭 뒤 `(145,101)`로 계속 이동 → 그 유닛의 편대 목표 칸(pending_xy)이 원본과 다르다.
- lap957 r1~r3 minimap parity는 모두 PASS. 후보만 느려진(present 788) run에서 클릭 전 tick 간격이 달라졌다는 설명과 맞는다(타이밍 귀속은 가설; D2 수리 뒤 fresh pair로 확인). 입력 좌표/선택 결함 근거 없음.

## 4. 다음 work 인계 (Sonnet, 1 lap, FEASIBLE — 계획 회차 없음)

순서 고정. 기존 pin/raw/golden/과거 pair-result 수정 금지.

1. **W-1 V2s 재정의 구현(`tools/g1_saved_scene_probe.py`, 게임 실행 없음).** `_compare_images`에 Scale2x(원본 800×600) 기준을 계산해 `v2s_scale2x_reference_blocks`, `v2s_unexplained_single_black_blocks`를 추가하고 `v2s_status = unexplained ≤ G1_SINGLE_BLACK_BLOCK_LIMIT(2,000 불변)`. 기존 `v2s_single_black_blocks`(raw)는 그대로 기록하고 `v2s_raw_status`(raw ≤2,000)를 비gate 진단으로 남긴다. `_v2s_capture_gate`·`_pair_status` 집계 규칙 불변. Scale2x 커널은 제품 `g1_scale2x_core.h`와 같은 EPX 규칙(경계 clamp)을 쓰고 계산 시간 증가를 공개한다.
   - RED→GREEN 단위: (a) 원본의 정확한 Scale2x 후보 → unexplained 0, raw > 0 가능; (b) 대각 격자 단일 흑색 주입 → unexplained = 주입 수; (c) 기존 V2s/V2q 테스트 유지.
   - 오프라인 회귀(보존 PNG, 공유 temp, 없으면 skip 표기): lap901 3 pair 15 tag **전부 FAIL**, lap854 3 pair·lap957 3 pair 30 tag 전부 PASS, lap959 r1 5 tag PASS; 수치가 §1 표와 일치. 결과는 새 파일로 남기고 기존 pair-result는 고치지 않는다.
2. **W-2 refresh churn 수리(`tools/inmm_stub/g1_hd_asset.c`, 필요 시 호출부).** hit 비교 범위를 `screen ∩ renderer viewport`(바인드 verify가 쓰는 같은 저장 viewport)로 제한한다. viewport가 800×600 전체이거나 스프라이트가 viewport 안에 완전히 있으면 비교 결과 byte 동일. 새 env 없음. 정적/host 테스트로 (a) viewport 밖 차이만 있을 때 refresh 없음, (b) viewport 안 1픽셀 차이면 지금처럼 refresh.
3. `make lint`·`make typecheck`·관련 focused 테스트 → fresh save006 scale2x pair 1회, lap959와 **같은 명령·같은 `--stale-mask 6-12,30-34,300-301,585-620,880`**. 비교 기준 lap959 r1·lap957 r1.
4. **사전등록 예측(진단; 새 gate 아님):**
   - R-1: PS3 서수 ≥150 `identity_cache_refreshes` 증가 ≤ 10(lap959 641), steady replay ≤0.2/present(lap959 2.4).
   - R-2: PS3 present 수 ≥ 854(lap957 r1 899의 0.95, P5-T C 참고 비율 기준), `elapsed_ms` p95 ≤ lap957 r1 +16ms.
   - R-3: 커버리지 유지 — 위쪽 줄 steady 교집합 stale ≤5,390px(lap958 P-1 기준), PS3 p50 coverage ≥96.7%(lap959 97.205% −0.5%p).
   - R-4: V2s(재정의) 5 tag PASS, raw는 공개; V1 outside diff 0·palette 0·`clip_replay_mismatches` 0·viewport mutation/restore 0·V2/V2q·Scale2x gate PASS·`scene_state_equal`·원본 EXE/save MATCH·source_unchanged·game 사본만 삭제(manifest/output/prefix 보존).
   - R-5: minimap parity 재판정 결과를 그대로 기록(PASS든 HOLD든). HOLD이면 두 lane `unit_before`의 차이 유닛·command를 표로 남긴다.
5. **반증/분기:** R-1이 틀리면(refresh가 그대로) 같은 lap에서 opt-in 계수(불일치 첫 픽셀이 viewport 안/밖, 저장 viewport 값)를 추가해 1회 더 실행하고 기록 후 HOLD로 middle에 넘긴다. R-1은 맞는데 R-2만 FAIL이면 화면 수리는 유지하고 성능만 별도 항목으로 남긴다(다음 후보: replay fill을 전체 버퍼 대신 `[0,w)×[0,h)`로 한정 — 이번 lap에는 하지 않는다). 화면 수리를 되돌려 성능을 맞추지 않는다.
6. 디스크 여유 <20GiB면 실행 전 PROMPT 규칙대로 자기 회차 game 사본 정리, 종료된 private prefix 회수는 lossless archive·검증·restore 확인 뒤에만.

## 5. middle 검수 항목 (W-1·W-2 뒤 fresh Opus)

1. W-1 구현으로 §1 표를 독립 재계산(제품 helper 없이)하고 lap901 15 tag FAIL·정상군 PASS 재현 확인. Scale2x 커널이 제품 커널과 같은 규칙인지 source 대조.
2. W-2 diff가 비교 범위만 바꿨는지, viewport 전체 화면일 때 byte 동일인지 확인. R-1~R-5 raw 재계산.
3. PNG 나란히(production tag 위쪽 줄): HD로 덮인 건물 줄에 seam/격자/색 이상이 없는지 직접 본다(V3).

## 6. strategy 재호출 조건

- 기존 조건(lap933 §6·lap938 §7·lap944 §6·lap946·lap952 §6·lap956 §7·lap958 §5) 유지.
- 추가: (a) 재정의 V2s에서 unexplained가 2,000을 넘는데 PNG에 격자/seam이 보이지 않을 때(기준 자체 재검토), (b) W-2 뒤에도 refresh가 viewport 밖 원인이 아닌 것으로 계측될 때, (c) minimap parity가 클릭 전 상태가 같은데도 HOLD일 때.

## 7. 범위 밖·금지

한도 2,000·V1/V2/V2q·Scale2x validator·PS3 통계량·golden 변경, 과거 raw/pair-result 재작성, covered를 줄여 gate를 맞추는 것, 캡처 시점·영역 변경, G2/G5 수정·G3/G4 재개, 원본/참고 저장소 쓰기, commit/publish/deploy.

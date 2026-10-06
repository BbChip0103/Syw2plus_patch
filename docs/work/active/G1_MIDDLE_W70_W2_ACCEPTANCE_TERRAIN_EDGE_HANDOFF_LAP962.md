# G1 lap961 W-2 독립 검수 수용 · V2s 사용자 판단 큐 · 오른쪽 가장자리 terrain stale 수리 인계 — lap962

## 판정 요약

- 지정 역할 middle(Claude Code `claude-opus-5-5`, high, Fast OFF). 게임·하네스·source·test·DLL·validator 변경 0, 새 게임 실행 0, commit 0. `loop/.lap_counter` 962 읽기만.
- **W-2 수리 PASS(partial) 수용.** diff는 비교 범위만 바꿨다. 전체 viewport일 때는 기존과 같다. R-1~R-5를 제품 helper와 lap961 스크립트 없이 재계산했고 불일치는 0이다. steady replay 잔여는 계수로 **새 key 최초 바인드에 정확히 귀속**된다.
- **replay fill 한정은 지금 하지 않는다.** R-2(present 887·p95 14ms)를 이미 충족했다. 잔여 replay는 새 key마다 1회 드는 고유 비용이다. fill 축소로 얻는 것은 바인드당 memset 2회뿐이라 측정 가능한 이득이 없다.
- **V2s production HOLD는 제품 수리로 풀 수 없다.** 완벽 Scale2x 기준만으로도 production이 3,547이다. 그래서 사용자 판단 큐(APPROVALS)에 올리고, 기존 V2s gate·pair 판정은 바꾸지 않는다. ESCALATE 조건(근거 충돌·마일스톤 경계)에는 해당하지 않는다. 근거는 일치하고 경계 판정은 사용자 몫이다.
- **새 사실:** lap961 PS3 coverage는 전 present ≥93.767%다(<90% 0개, lap957은 6개). 따라서 "PS3 초기 present 6~12 경계"는 lap959/961 수리로 해소됐다(한 run 기준).
- **다음 work:** 남은 steady stale 9,880px 중 오른쪽 가장자리 다이아몬드 타일 3,512px(x≥760, y<480)를 수리한다. 가설 H-E(§4).

## 1. W-2 diff 검토

- 기준: lap959 bridge 사본 `g1_mirror2x.c` `531f1a4b…9bf59`, `g1_hd_asset.c` `7833f328…edf`, `g1_hd_asset.h` `167be0f8…29`. lap961 bridge 사본 = 현재 repo(`cf682cdf…4015`/`2784a22d…580e`/`fbc4abd4…a55`) 바이트 동일.
- `g1_hd_asset.c`: 기존 `compare_visible_frame`은 `(0,0,799,599)`로 위임한다. 화면 교집합 ⊂ [0,800)×[0,600)이므로 clamp가 no-op이라 기존 동작과 같다. 새 함수는 bind verify(`verify_unclipped_frame_in_viewport`)와 같은 포함형 우/하단(+1) 규칙을 쓴다. 스프라이트가 viewport 밖이면 비교·축출 없이 FALSE를 반환한다(호출부 `(void)`).
- `g1_mirror2x.c`: hit 호출부만 live `renderer+0x4D0` viewport를 넘긴다. bind verify도 같은 시점의 live viewport(`saved_viewport`)를 쓰므로 두 경로가 같은 사각형을 쓴다. replay·verify·bind 경로는 변경 0이다.
- bridge `inmm_stub.c`는 repo와 `supply_probe_poll` 주입 2줄만 다르다. lap959 bridge와 동일하므로 빌드 생성 차이다.

## 2. R-1~R-5 독립 재계산

스크립트 공유 temp `20261004_lap962_middle_review/recalc_lap962.py`(`57895f85…c43e`) → `recalc_lap962.json`(`12f89652…5612`). 입력 SHA: lap961 pair `b5df22d4…dd9c`, trace `bf5f30df…6c4f`, mask `8db4a04b…d27`(기록 일치).

| 항목 | lap957 r1 | lap959 r1 | lap961 r1 |
|---|---|---|---|
| PS3 present / p50 / p95(nearest-rank) / reinvoke max | 899 / 6 / 12 / 16 | 788 / 7 / 23 / 21 | **887 / 6 / 14 / 15** |
| refresh 최종 / 서수150→끝 증가 | 133 / 0 | 979 / 643 | **0 / 0** |
| inserts / keys / misses | 563 / 774 / 53,258 | 1,757 / 781 / 786 | 768 / 771 / 776 |
| steady replay/present 150-300 · 300-600 · 600-끝 | 0.053·0.033·0.087 | 2.547·2.373·2.404 | 0.707·0.46·0.237 |
| steady `replays − 2×새 keys` (세 구간) | — | 310·598·374 | **0·0·0** |
| 위쪽 줄 steady 교집합 stale / 교집합 전체 | 26,951 / 41,861 | 58 / 9,880 | **58 / 9,880** |
| PS3 cov p50 / min | 90.419 / 89.791 | 97.205 / 93.767 | **97.214 / 93.767** |
| 안전(clip mismatch·viewport mutation/restore·palette·outside diff) max | 0 | 0 | **0** |
| mask 덤프 / 헤더·합 불일치 | 51 / 0 | 50 / 0 | 51 / 0 |

- R-1: refresh churn은 완전히 제거됐다. steady 구간에서 replay = 정확히 2 × 새 key(clipped 바인드 1회당 replay 2회)이다. 그래서 잔여는 evict→재바인드가 아니라 새 key 최초 바인드다. lap961은 이를 추론으로 기록했고, 이번에 계수로 직접 확정했다. lap957의 0.03~0.09는 화면 밖 origin key를 바인드하지 않아서 생긴 값이다. ≤0.2 예측은 예측 모델 자체가 틀린 것이고 결함이 아니다.
- R-2 PASS, R-3 PASS, R-4 안전 PASS. R-5 minimap `status/effect PASS`, `same_result/camera/unit/exact_gate_restore` 모두 true(pair-result 원문).
- V2s(raw)는 pair-result와 5/5 tag 정확히 일치한다: 1,712/1,706/1,624/1,709/**2,785**. gate는 production FAIL → pair **HOLD 유지**.

## 3. V2s 진단 (gate 아님) · PNG V3

- 같은 스크립트로 Scale2x(원본) 기준 진단을 계산했다(제품 `g1_scale2x_core.h` 규칙 `B≠H && D≠F`, 가장자리 clamp를 RGB에 적용). lap961 tag별 ref 2,205/2,197/2,254/2,173/**3,547**, unexplained 80/207/151/254/211. lap959(22~220)·lap957(10~158)도 lap960 표를 재현한다.
- 해석: production은 정상 Scale2x 자체가 raw 한도를 넘는 장면이다(ref 3,547 > 후보 raw 2,785). raw gate는 coverage를 줄이지 않고는(금지) PASS할 수 없다. 따라서 수리 대상이 아니라 기준 판단 대상이다.
- PNG 나란히(`side_production_top_lap962.png` `25368d54…59b`, `zoom_production_top_lap962.png` `bfb8c2d0…2f2`, `side_minimap_top_lap962.png` `e5fc8acd…9f9`): production 위쪽 건물 줄에서 후보는 Scale2x(원본)와 같은 계단 완화를 보이고 격자/seam/색 이상은 없다. unexplained 표시는 이동 유닛 몇 점뿐이다. minimap 위쪽 줄의 차이는 이동 중인 유닛 자세·위치 차이(캡처 시점)이고 지형·건물에는 seam이 없다. 후보≠Scale2x(원본) 픽셀 비율은 production 3.3%, minimap 4.3%(이동 유닛·커서·P6/P7 포함).
- 결론: V3 PASS(관찰). W-1은 계속 사용자 미승인 제안이다. 이번 lap은 V2s gate·`_compare_images`·`_v2s_capture_gate`·`_pair_status`·validator·과거 raw를 바꾸지 않는다.

## 4. 남은 steady stale 분류 · H-E

- `residual_class_lap962.py`(`d94feeb2…a8d7`) → `residual_class_lap962.json`(`4a13766b…78bc`). 근사치다: 다른 run(lap951 r6 최종 PS3 census map `e8c0b590…113d`)이지만 같은 save006 장면이다. lap961 교집합 9,880px = terrain_cache_transfer 59.62%·dd_surface_blt 36.32%·rle_tinted_clip 2.21%·기타 <1%. y≥480 HUD 3,637px.
- overlay(`stale_residual_overlay_lap962.png`)로 본 세 덩어리:
  - (a) **오른쪽 가장자리 다이아몬드 지그재그**(x≥760, y≈200~480, 3,512px): 화면 오른쪽 끝 마름모 타일 반쪽들이다.
  - (b) 반투명 "임진록2+ 조선의 반격" 로고: P6 blend writer로, census에 없어 terrain으로 표시된다. 이미 **명시 잔여**로 분류돼 있다(lap954).
  - (c) HUD 명령 버튼 위 약 100×35 사각형(dd_surface_blt): 툴팁 텍스트 surface Blt다(lap951 101×40). GDI/Blt 잔여다.
- 계수: lap961 최종 `layer_covered_pixels` 425,984 = 832×512로 layer 전부가 covered다. 따라서 (a)는 미커버가 아니라 **layer expected가 갱신되지 않은 stale**이다.
- **H-E(주 가설):** clipped replay 경로(`g1_mirror2x.c` 약 1456행)는 대상과 무관하게 `full_viewport = {0,0,799,599}`를 강제한다. cache 대상은 frame width 832(`G1_MIRROR_CACHE_WIDTH`)·height 512다. 그래서 cache 오른쪽 끝(x≥800까지 걸친) 마름모 타일의 clipped terrain 쓰기(`0x468F00`/`0x4690A0`, lap961 286/333회)는 replay에서 800 이상이 잘린다. 그 결과 saved viewport 안 verify가 실패하고, 바인드가 없으니 compose가 안 돼 layer expected가 옛 값으로 남는다(stale). 대안 H-E2: cache→screen 전송 좌표 offset 차이. 이 경우 stale이 가장자리에만 몰리지 않아야 하므로 지금 관측과 맞지 않는다.

## 5. 다음 work 인계 (Sonnet, 1 lap, FEASIBLE)

1. 최소 수리: clipped replay의 full viewport를 대상 frame에 맞춘다(`cache_target`이면 `{0,0,frame_width-1,surface_height-1}`, 화면 대상은 지금처럼 `{0,0,799,599}`). replay buffer(`stride×surface_height`) 안에 있어야 하고, 화면 대상은 byte 동일이어야 한다. 새 env는 없다. 정적/host 테스트: (a) 화면 대상 viewport 값 불변, (b) cache 대상 832×512 viewport, (c) buffer 범위 초과 없음.
2. 같은 lap 계수(기본 raw에 새 키를 추가해도 된다. 기존 키·pin 불변): cache 대상 clipped 바인드 시도/verify 실패 수, cache 대상 saved viewport 최초 값 1회.
3. `make lint`·`make typecheck`·focused → fresh save006 scale2x pair 1회. 명령과 `--stale-mask 6-12,30-34,300-301,585-620,880`은 lap961과 같다. 비교 기준 lap961 r1.
4. 사전등록 예측(진단, 새 gate 아님):
   - E-1: steady 교집합의 x≥760·y<480 stale 3,512 → ≤350.
   - E-2: steady 교집합 전체 9,880 → ≤6,700. PS3 cov p50 ≥97.2%·min ≥93.7%.
   - E-3: present ≥854·p95 ≤28ms.
   - E-4: 안전 0(clip mismatch·viewport mutation/restore·palette·outside diff)·V1/V2/V2q/Scale2x PASS·minimap parity·원본 EXE/save MATCH·source_unchanged·game 사본만 삭제.
   - V2s raw는 그대로 공개한다(기존 gate 판정 불변, HOLD여도 이 lap의 실패 사유 아님).
5. 반증: E-1 미달이면 2번 계수로 verify 실패가 cache 가장자리에서 나는지 판정하고, 기록 후 HOLD로 middle에 넘긴다. 그 계수가 viewport가 원인이 아님을 보이면 H-E2(전송 offset)를 다음 진단 후보로 적는다. 수리를 위해 covered를 줄이지 않는다.
6. 디스크 여유 <20GiB면 PROMPT 규칙대로 game 사본만 정리하고, prefix 회수는 archive·restore 검증 뒤에만 한다.

## 6. strategy 재호출 조건

기존 조건(lap933 §6·lap938 §7·lap944 §6·lap946·lap952 §6·lap956 §7·lap958 §5·lap960 §6) 유지. 추가: H-E 수리 뒤 cache 대상 verify가 성공하는데도 가장자리 stale이 남고 H-E2도 기각될 때.

## 7. 범위 밖·금지

V2s gate 의미 변경(W-1 자동 적용)·한도·V1/V2/V2q·Scale2x validator·PS3 통계량·golden 변경, 과거 raw/pair-result 재작성, covered 축소, 캡처 시점·영역 변경, G2/G5 수정·G3/G4 재개, 원본/참고 저장소 쓰기, commit/publish/deploy.

# G1 W70 P5-T-V — 클립 바인딩 두 번째 검증의 lane 불일치와 스크롤 뒤 비용 (lap933 strategy, 2026-10-04)

- 발행: lap933 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, subagent0, 커밋0.
- 호출 사유: lap931·932 middle의 `HOLD_SCOPE_CONTRACT` 승격(`loop/ESCALATE_SOL`, 보존본
  `docs/history/20261004_lap933_prior_lap932_escalate_sol_byte_exact.txt`)과 11:18 운영자 lane 재평가
  (제품·실행 증거가 늘지 않은 회차 연속 2회 → strategy가 G1 계속 여부와 bounded work 계약을 판정).
- 입력 근거(이 세션이 직접 읽고 재계산): 현재 `tools/inmm_stub/g1_mirror2x.c`(SHA `f27302c1…fec1`), `g1_hd_asset.c`(SHA `7833f328…eedf`),
  lap930 candidate trace 6개(GREEN·B′1·B′2·진단 2·C3), lap923 final candidate trace 3개. 재계산은 공유 temp `20261004_lap933_strategy_review/`.
- 이 카드는 lap931 인계(`G1_MIDDLE_W70_P5T_D2_SCOPE_HOLD_REUSE_HANDOFF_LAP931.md`)의 **순서를 바꾼다.** §3(capacity 재사용)은 지우지 않고
  조건부 2순위로 둔다(§2 V5). lap925 카드의 경계 계약 O1~O7·PT-c는 그대로이고 PT-d만 §4로 바꾼다.

## 0. 판정 요약

1. **timer 범위 결함은 사실이다.** `g1_mirror2x.c:1343`에서 parent 시작값을 0으로 만들고 1348의 mask 할당 뒤 1351에서야 다시 켠다.
   두 full buffer 할당이 실패하면 1301에서 켠 구간도 1395에서 덮여 사라진다. lap930 raw의 `clip − 세 bucket` 잔차는 승인하지 않는다. raw는 고치지 않는다.
   아래 판정은 parent 합을 쓰지 않는다(helper 자체 timer와 호출 counter만 쓴다).
2. **스크롤 뒤 비용의 뿌리는 클립 바인딩이 한 번도 성립하지 않는 것이다.** 두 번째 검증(`g1_mirror2x.c:1381~1383`)이
   00 배경 클립 프레임 `scratch_a`를 FF 배경 전체 replay `unclipped_ff`와 비교한다. 보이는 사각형 안에 writer가 안 쓴 픽셀이 하나라도 있으면
   `0x00 ≠ 0xFF`로 실패한다. 그래서 클립 writer 호출은 identity frame을 못 묶고, 매 present마다 full buffer replay를 두 번씩 다시 한다(§1.1).
3. **비용은 fill 바이트 수가 아니라 메모리 상태다.** 같은 499,200바이트 fill이 고정 카메라에서는 4.6~4.9µs, 스크롤 뒤 30 present에서는 140~147µs다(§1.2).
   replay 횟수는 두 창이 같다. capacity 재사용은 이 단가를 낮추지만 replay 148회/present는 그대로 둔다.
4. **PT-d의 하한 11439는 잘못 잡은 값이다(내가 lap925에서 정했다).** `tinted covered`는 "처음 덮인 픽셀" 누적이고, 그 값은 PS3 첫 present 전에 정해진 뒤
   고정 카메라에서 한 번도 안 변한다. 창 안 증가분은 5회 실행이 정확히 같다(§1.3). §4의 PT-d′로 바꾼다. 과거 미달 값은 PASS로 바꾸지 않는다.
5. 다음 work 1 lap = **P5-T-V**: 두 번째 검증을 FF lane끼리 비교하게 고친다(V1) → fresh GREEN으로 §3 예측 확인 → PT-c가 남으면 capacity 재사용(V5)
   → GREEN → B′ 연속 2 → C1~C3 → Fast → 새 middle.
6. **G1은 계속한다.** lap931~933은 제품·실행 증거가 늘지 않은 연속 3회다. 다음 회차는 반드시 source 변경과 격리 실행이 있는 work다.
   P5-T·G1 HOLD 유지. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다.

## 1. 근거

### 1.1 클립 replay mismatch 구조 (candidate lane, PS3)

| 실행 | mismatch 합 | viewport replay 합 | replay ÷ mismatch | 마지막 mismatch (writer, 원점, 크기, 픽셀, 값) |
|---|---:|---:|---:|---|
| lap923 GREEN·B′1·B′2 final | 53118 / 50654 / 53383 | 106762 / 101836 / 107294 | 2.0099 / 2.0104 / 2.0099 | `0x466D50`, (90,553), 32×32, (93,553), **[0, 255]** |
| lap930 GREEN·B′1·B′2 | 54891 / 54282 / 54346 | 110310 / 109092 / 109220 | 2.0096 / 2.0097 / 2.0097 | 같음, **[0, 255]** |
| lap930 진단 stosl·stosb | 54539 / 54828 | 109606 / 110184 | 2.0097 / 2.0096 | 같음, **[0, 255]** |
| lap930 C3 | 55251 | 110944 | 2.0080 | `0x466540`, (666,366), 76×98, (666,366), **[0, 255]** |

- 값 `[0, 255]`는 (화면 쪽 값, replay 쪽 값)이다. 9회 전부 "00 배경 대 FF 배경"이다.
- replay ÷ mismatch ≈ 2.01은 mismatch 대부분이 **두 번째 replay 뒤**에 난다는 뜻이다. 첫 검증에서 떨어지면 replay는 한 번이다.
  고정 카메라 late20: 클립 호출 82.35, mismatch 74.1, replay 148.7(present당, lap930 5회 동일). 첫 검증은 거의 다 통과하고 두 번째 검증은 present당 0.25회만 통과한다.
- writer별: lap930 GREEN은 A 2373, B 39500, 지형 clip 48, 나머지 12970 = `tinted_clip` 호출 수 12970. 8회에서 나머지가 `tinted_clip` 호출 수와 정확히 같고
  C3는 10 이내다(행 시점 차이). `tinted_clip`은 호출마다 mismatch다 — lap925 L2, `rle_tinted_clip covered 0`과 같은 사실이다.
- 코드: 첫 검증(1344)은 `scratch_a` 대 `unclipped`(둘 다 00 배경), 두 번째(1381)는 `scratch_a` 대 `unclipped_ff`다.
  FF 배경 클립 프레임 `scratch_b`는 1288~1290에서 이미 만들어져 있다. mask(`written`)는 바로 앞 1376에서 투명 픽셀을 가려내려고 계산한다.
- lap925 카드의 P5-H mismatch 59.0/present도 같은 경로다(A·B·지형 clip). P5-T가 만든 결함이 아니라 P5-T가 호출 15/present를 더 얹은 것이다.

### 1.2 같은 fill의 창별 단가 (lap930 진단 2회, helper 자체 QPC, 10MHz)

| 창 | fill 호출/present | 바이트/호출 | fill µs/호출 | alloc·free µs/호출 | coarse 재호출 ms/present |
|---|---:|---:|---:|---:|---:|
| 고정 late20 | 148.7 | 499,200 | 4.90 / 4.57 | 0.155 / 0.134 | 0.4~1.75 (5회) |
| DOWN 뒤 30 | 146.7 | 499,409 | 139.8 / 146.7 | 9.30 / 9.66 | 19.5~21.0 |
| RIGHT 뒤 30 | 146.8~147.1 | 499,200 | 147.0 / 147.1 | 9.81 / 9.80 | 19.1~22.7 |

- fill 단가 28.5~32.2배, alloc·free 단가 60~73배. 명령(`rep stosl`/`rep stosb`)과 바이트 수는 같다.
- 스크롤 뒤 0.28~0.295ns/byte는 4KiB당 약 1.2µs다. 새 페이지 첫 쓰기 비용과 맞는 크기지만 page fault를 직접 잰 것은 아니다(가설).
- 실행 끝 40 present(카메라 [160,101], replay 95.9/present)는 coarse 0.2~3.7ms/present로 돌아온다. 힙 상태에 따라 오르내린다.
- lap931의 "fill 82.95% 지배"는 이 스크롤 창 단가가 누적을 지배한 결과다.

### 1.3 PT-d 값의 정체

- `g_tinted_writer_covered`는 호출 전후 `g_covered_pixels` 차이를 더한다(`g1_mirror2x.c:1924~1925`). `g_covered_pixels`는 compose가
  `g_covered` 표시를 0→1로 바꾼 픽셀만 센다(601~602). 즉 **tinted writer가 처음 덮은 픽셀의 누적**이다.
- PS3 첫 present(tick 24570)에서 이미 lap930 11524 / 9569 / 9314 / 10589 / 12714, lap923 final 12544 / 11439 / 12969다(그때까지 tinted 호출 165~205).
  그 뒤 스크롤 전까지 변화점이 **8회 전부 0개**다. late20 최솟값은 이 시작 값 그대로다.
- lap930 5회의 창 안 증가분: DOWN 뒤 30 present **3741**, RIGHT 뒤 30 present **129**로 전부 같다. tinted 호출은 3091~3092 / 2226~2227.
- 하한 11439는 lap923 final 세 값의 최솟값이다. 시작 구간에 그린 프레임 수에 따라 달라지는 값이고 tinted 미러를 껐는지와 무관하다.

### 1.4 한계

- 고친 빌드는 실행하지 않았다. §3은 예측이다.
- tinted writer 출력이 대상 픽셀에 의존하는지(그러면 mask가 "안 쓴 픽셀"로 읽는다)는 확인하지 않았다. V1 뒤 `tinted_clip` 수치로 갈린다(§3 P-5).
- lap920 이전 trace는 이번에 다시 읽지 않았다. P5-H 59.0/present는 lap925 기록 값이다.
- 스크롤 뒤 단가가 오르는 계기(힙 배치·decommit)는 모른다. V1이 통하면 알 필요가 없어진다.

## 2. 수리 계약 (규범)

- **V1 (한 가지 변경):** 두 번째 검증은 FF lane끼리 비교한다 — `scratch_b`(FF 배경 클립 프레임) 대 `unclipped_ff`. 첫 검증, mask 계산,
  `g1_hd_asset_bind_identity_frame` 인자, viewport 저장·복원은 그대로다.
- **V2 (계측 경계, 같은 함수의 최소 수정):** parent clip timer가 mask 할당과 두 full buffer 할당 실패 경로를 포함한다. original replay와 bind는 계속 제외한다.
  source 고정 회귀 1건이면 된다. lap931 §3.1의 모의 QPC·allocator 실행 회귀는 V5를 할 때만 요구한다.
- **V3 (불변):** 매 호출 full buffer 00/FF fill, visible 비교, LUT pointer+digest key, identity/Scale2x, writer 범위(현재 hook 집합), validator, 임계값,
  tick 일정, 30개, 52.0ms, 원본·기존 raw·golden·안전 pin.
- **V4:** mismatch가 난 key를 기억해 replay를 건너뛰는 negative cache는 넣지 않는다. V1은 구조적 mismatch를 없애는 것이고, 남는 mismatch는 지금처럼 매번 다시 확인한다.
- **V5 (조건부 2순위):** V1 뒤 fresh GREEN에서 PT-c가 한 키라도 52.0ms를 넘거나 스크롤 창의 replay가 present당 40을 넘으면, 같은 work 회차에서
  lap931 인계 §3(full replay 2개 + mask capacity 재사용, §3.2~3.4 회귀 포함)을 그대로 구현한다. 조건이 안 서면 구현하지 않는다.
- 회귀(RED 먼저): ① 투명 픽셀이 있는 스프라이트가 viewport 경계에 걸린 경우 — 두 검증 통과·bind 성립·mask가 투명 칸 0. ② FF replay가 쓰인 픽셀에서
  클립 프레임과 다르면 mismatch·bind 없음. ③ source가 두 번째 검증에 FF lane 프레임을 넘긴다. ④ 기존 25건 유지.

## 3. 사전 등록 예측 (V1 뒤 fresh GREEN, candidate lane, 같은 일정)

| 항목 | 지금 | 예측 | 반증 |
|---|---|---|---|
| P-1 고정 late20의 A+B+지형 clip mismatch/present | 59.1 | ≤ 6 | > 30이면 lane 귀속이 틀렸거나 부족하다 |
| P-2 replay/present (고정 late20·DOWN 30·RIGHT 30) | 146.5~148.8 | ≤ 40 (`tinted_clip`도 묶이면 ≤ 12) | > 40이면 V5 |
| P-3 PT-c (두 키) | 50.6~57.0ms | ≤ 52.0ms | 초과면 V5 |
| P-4 late20 effective p50 / stale p50 | 395960.5 / 74863.5 | 줄지 않음 / 늘지 않음 | 반대로 가면 원인 귀속 전 HOLD |
| P-5 `tinted_clip` mismatch·covered | 호출 전부 mismatch, covered 0 | 0으로 내려가고 covered > 0, **또는** 그대로 | 그대로면 마지막 mismatch 값·writer를 기록(대상 의존 여부 판단 자료) |

- P-1이 반증되면 마지막 mismatch의 writer·픽셀·값과 writer별 counter를 기록하고 V5로 비용만 먼저 낮춘다. strategy로 올리지 않는다.
- 새로 묶이는 클립 스프라이트가 HD로 그려지므로 V1·V2·V2s·V2q·Scale2x·PNG(V3)가 처음 보는 픽셀을 검사하게 된다. 여기서 나는 FAIL은 숨기지 않는다.
  추적 가능한 구현 결함이면 PROMPT ③대로 수리 → 재실행(3회까지), 아니면 raw와 함께 HOLD로 middle에 넘긴다.

## 4. PT-d′ (lap925 PT-d 대체)

의도는 그대로다 — 비용을 tinted 미러를 끄는 것으로 줄이지 않는다.

- **gate (a):** tinted hook 두 개가 설치돼 있고, tinted 호출이 기준 실행에서 줄지 않는다 — 고정 late20 ≥ 1530(기준 1562), DOWN 30 ≥ 3030(기준 3091~3092),
  RIGHT 30 ≥ 2180(기준 2226~2227). 2% 여유는 present 한 개 차이용이다.
- **gate (b):** late20 effective coverage p50 ≥ 395,960, stale p50 ≤ 74,864(lap930 값, 악화 금지). 스크롤 30 present의 기존 coverage gate는 그대로다.
- **기록만:** PS3 첫 present의 tinted 누적, DOWN/RIGHT 30 present 증가분(기준 3741 / 129), `tinted_clip` covered. 다른 writer가 먼저 덮으면 달라지는 값이라 gate가 아니다.
- 절대 하한 11439는 폐기한다. lap928 B′1 9229, lap930 B′1 9569·B′2 9314는 "지표 무효"로 다시 분류하며 PASS가 아니다. 그 실행들은 PT-c로 이미 HOLD다.

## 5. 다음 work 한 가지 — P5-T-V

1. §2 회귀 RED → V1·V2 구현(`tools/inmm_stub/g1_mirror2x.c`와 `tests/test_g1_mirror2x.py`, 단일 writer) → focused tests·lint·typecheck·DLL build.
2. fresh GREEN 1회(비계측). §3 표를 채운다. 필요하면 `--perf-sections` 진단 1회로 창별 단가를 본다(진단 실행은 합격 증거가 아니다).
3. V5 조건이 서면 V5 → GREEN 재실행. 수리 → 재실행은 3회까지다.
4. 같은 source identity로 GREEN → B′1 → B′2 → C1 → C2 → C3. 기존 gate 전부(V1/V2/V2s/V2q/Scale2x, snapshot 5/5, tick·입력·카메라 parity,
   경계 안 30개, C ratio ≥ 0.95·p95Δ ≤ 16ms)와 PT-c·PT-d′. lap930의 `C3`는 20초 pair 1회였다 — 세 회를 따로 돌린다.
5. 디스크 여유 20GiB, 실행 뒤 game 사본 삭제, 유지보수 I/O 비중첩, pair마다 `/proc/loadavg`·`/proc/pressure/io` 기록(gate 아님).
6. lap 기록·handoff → `make lint`·`make typecheck` → `make check` 1회 → STATUS 보강 → 새 middle 독립 검수.
   middle은 새 raw에서 §3 표, PNG 직접 확인, stale·coverage 변화, writer별 mismatch를 본다. P단계 전환은 마일스톤 경계가 아니다(lap858).

## 6. strategy 재호출 조건

- PT-c를 맞추려면 미러 범위를 줄이거나 full sentinel fill을 줄여야 한다(V1·V5 뒤에도 미달).
- V1 뒤 화면 정합 gate FAIL이 work 1회 + middle 1회로 귀속되지 않는다.
- `sim_tick`과 snapshot tick 불일치, 새 안전 위험(lap925 §6 그대로).
- 그 밖의 HOLD·수리는 work ↔ middle로 처리한다.

## 7. 남는 것

stale p50 74,863(화면의 15.6%)·유효 HD coverage 82.5% < 90%(V1이 얼마나 줄이는지는 실행 뒤에 안다), `tinted_clip` 귀속(P-5), input-effect HOLD, GDI,
두 번째 장면, 최종 입력, D-2 스크롤 성능, census 계측 결함 두 건(lap913), 동적 API 실패 주입, G1 사용자 승인.
G2·G5 종료, G3 중단, G4 보류, 커밋 금지는 그대로다.

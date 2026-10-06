# 2026-10-06 | lap 1044 | middle — G1 W-1(V2s unexplained gate) 독립 검수·수용 → work H-U

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / middle(중간 계획·독립 검수). 게임 실행·source 수정·원본/참고 쓰기·commit 0.
- 목표 / 검수 대상: lap1043 work W-1(사용자 결정 2026-10-06 01:43 KST, APPROVALS lap962 (1)). 사전등록 = lap1042 기록 §다음 work 1. 검수 항목 = `loop/ESCALATE_SOL`(아래 부록) 1~4.
- 대상 파일 SHA256(work 기록과 일치): `tools/g1_saved_scene_probe.py` `f14a9d7e53a6b2eec53116cfb28ce3434c0602dcf611983c87904ffd753dea11`, `tests/test_g1_saved_scene_probe.py` `b51968a9d6cdd9941e34abf0f13f2ecacd577e3d3dc1fbb451686f048b0cd404`. 둘 다 git 미추적이고 변경 전 사본이 없어 diff는 영역 대조로 확인했다(lap1013 관례). work 산출물 `w1_offline.py` `160e0500…e892`·`w1_offline.json` `98c7fdb0…db8`·`w1_s6_reaggregate.json` `99671757…8043` = 기록 일치.
- 원본 SHA / fixture: 원본 EXE·save 접촉 0. 입력 = 보존 PNG 60 tag(읽기 전용, lap1043과 같은 12 run).

## 1. 독립 재계산(제품 helper 미사용)

- 스크립트 공유 temp `20261006_lap1044_middle_review/recalc_w1_lap1044.py`(SHA256 `77c166219a869bd1abec4936d7aee4a51a2def06d9bb91eebe003126c4ef9873`): numpy·RGB 24비트 키, EPX를 배열 shift(가장자리 clamp)로 새로 구현, 제품 모듈 import 0. 결과 `recalc_w1_lap1044.json` `8b5959476362debb01014a0d875286f3ccf4c4239b3722c076fe83aae31561b9`(60 tag 4.1초).
- **불일치 0:** 60/60 tag에서 raw·ref·unexplained와 `v2s_status`·`v2s_raw_status`가 work `w1_offline.json`과 같다. lap960 `v2s_control_fixtures.json`이 있는 30 tag(lap901 3·lap854 3 run)는 PNG SHA256까지 같고 값 불일치 0.

| 묶음 (tag) | raw | ref | unexplained | 새 `v2s_status` |
|---|---|---|---|---|
| lap901 격자 결함 (15) | 18,882~20,056 | 2,187~2,596 | **18,712~19,901** | 15/15 FAIL (W1-1 PASS) |
| lap854 (15) | 476~614 | 2,189~2,269 | 456~587 | 15/15 PASS |
| lap957 r1~r3 (15) | 1,044~1,705 | 2,166~3,547 | 8~158 | 15/15 PASS |
| lap959 r1 (5) | 1,667~2,813 | 2,175~3,540 | 22~220 | 5/5 PASS (W1-2 PASS) |
| lap1039 save006 r1/r2 (10) | 1,711~2,852 | 2,149~3,549 | 20~202 | 10/10 PASS (W1-3) |

- 전사 정정 1건(판정 무관): lap960 카드 §1 표의 lap854 ref 하한 "2,207"은 lap960 자신의 fixture(`lap854_g3` loaded 2,189)와 다르다. 실제 범위는 2,189~2,269다. lap1043 기록은 이 값을 인용하지 않았다.

## 2. 커널 대조(source)

`_v2s_scale2x_reference`와 제품 `tools/inmm_stub/g1_scale2x_core.h` `g1_scale2x_build_masked`를 줄 단위로 대조했다. `b != h && d != f` 조건, p0=`d==b?d:e`, p1=`b==f?f:e`, p2=`d==h?d:e`, p3=`h==f?f:e`, 가장자리 clamp(`x?x-1:x` 등), subpixel 배치(p0 (0,0)·p1 (1,0)·p2 (0,1)·p3 (1,1))가 같다. 기준은 전 픽셀 written으로 둔 경우와 같다. 차이는 비교 단위뿐이다. PNG 단계는 RGB 같음 비교이고 제품은 팔레트 인덱스 비교다. 팔레트에 같은 RGB가 중복되면 갈릴 수 있지만, 독립 재계산·lap960 fixture와 불일치가 0이라 판정 영향은 관측되지 않았다(한계로 기록).
unexplained 정의(후보 흑색 정확히 1개, 그 위치가 기준에서도 흑색이면 explained)는 lap960 §1 정의와 같다.

## 3. 집계·한도·tag 불변(영역 대조)

- `G1_CAPTURE_TAGS`(5 tag)·`G1_WORLD_BLACK_EXCESS_LIMIT`·`G1_SINGLE_BLACK_BLOCK_LIMIT`·`G1_FOUR_BLACK_BLOCK_LIMIT` = 2,000 그대로. `_v2_capture_gate`·`_v2s_capture_gate`·`_v2q_capture_gate`는 구조가 같고 `v2s_status`만 읽는다. `_pair_status`는 scene_state·V2/V2s/V2q·scale2x·terrain·performance 조건이 그대로다.
- `_compare_images` 변경 = `v2s_status` 식(unexplained), 신규 `v2s_raw_status`·`v2s_scale2x_reference_blocks`·`v2s_unexplained_single_black_blocks`, BLOCKED 두 경로에 `v2s_raw_status` 추가뿐이다. raw `_single_black_blocks`·V2·V2q·nearest 계산은 그대로다.
- V2s 필드 소비처는 `tools/g1_saved_scene_probe.py`와 그 테스트뿐이다(tools·checks·tests·patches grep).
- 테스트: (a) 계단 패턴 정확 Scale2x → raw>2,000·raw FAIL·ref==raw·unexplained 0·PASS, (b) 주입 2,000/2,001 경계, (d) gate가 raw 진단을 무시. 사전등록 (a)(b)(d)를 덮는다. 빠진 경우(후보 1개 흑색이 기준 2개 흑색 중 하나와 겹치는 explained 경로)는 실제 PNG 재계산으로 확인돼 비차단이다.

## 4. W1-3 재집계·과거 결과 불변

- lap1039 `r_s6_r1`/`r_s6_r2` `pair-result.json` SHA256 `683d4a7d…7e16`/`f6dea01f…0c74`, mtime 2026-10-06 00:55/00:58 KST(사용자 결정 01:43·lap1043 이전) → 수정 0. 저장 status HOLD, 사유 = `v2s_capture_gate` FAIL(production만), 그 밖 scene_state_equal true·V2·V2q·scale2x PASS.
- run 인자(`run_r.sh` 38행): `--hd-source scale2x --stale-mask …`. `--performance-window`·`--terrain-scroll`이 없으므로 두 조건은 면제된다. 새 V2s 5 tag 전부 PASS를 넣으면 `_pair_status` = **PASS**(r1·r2). 오프라인 산술이며 새 런타임 증거가 아니다. 성능 gate 미요청 run이다.
- **영향(work 인계):** 이후 save006 pair 실행은 exit 2 대신 exit 0(PASS)이 날 수 있다. 이는 W-1 기대 효과이고 이상이 아니다. save000 `--scene-actions none` run은 BLOCKED tag 때문에 계속 HOLD(exit 2)다.

## 5. PNG 육안(격자/seam)

`visual_w1_lap1044.py`(`e2700b88…c12b`) → `visual_w1_lap1044.json`(`44ba9777…39b1`)과 3 패널 PNG(후보 | unexplained 빨강 | raw 초록+unexplained 빨강):
- lap901 origin production(`049b06bf…01b6`): unexplained가 맵 전체 마름모 격자선을 그린다(19,803, 행당 최대 53·50 이상 행 70개). 격자 결함을 계속 잡는다.
- lap1039 s6 r1 production(`34007ab0…6399`)·r2 minimap(`fd938b41…8817`): 후보에 격자/seam 없음. raw는 건물·유닛 가장자리(EPX 모서리)에 모이고, unexplained 190/202는 유닛·건물 위의 드문 점이다(행당·열당 최대 5, 50 이상 행 0, 행/열 mod 4 분포 균등 → 주기 구조 없음). lap960 §6(a) 분기(unexplained>2,000·격자 없음)는 발생하지 않았다.

## 판정

**W-1 PASS 수용(lap1043 work):** W1-1·W1-2·W1-3 독립 재계산 불일치 0, 커널 규칙 일치, 집계·한도·tag·V1/V2/V2q·validator 불변, 과거 pair-result 수정 0, coverage 축소 0. 이것은 사용자 결정(gate 의미)의 기술 구현 검수다. G1 사용자 마일스톤 승인이 아니고, G1 사용자 판단 때 raw·ref·unexplained를 함께 보인다.

## 다음 work — H-U(사전등록 그대로, lap1042 기록 §다음 work 2)

- `0x468360`(old bytes `83 EC 1C 53 55`, 7인자 `ret 0x1c`, 클립·좌우 반전) diff 미러, U-0~U-4 기준은 lap1042 §다음 work 2 원문을 따른다. 재계획하지 않는다.
- W-1 반영 보정 1건(기준 아님, 판독 주의): save006 pair가 이제 exit 0/`status` PASS일 수 있다. U-4는 기존대로 stale 지표로 판정하고, pair PASS/HOLD는 따로 기록한다. save000 watch/성능 pair는 계속 exit 2(BLOCKED tag)일 수 있다.
- 검사: `make lint`·`make typecheck`·focused 뒤 lap 기록 freeze 후 `make check` 1회.

## 검사·한계

- 이번 lap: 문서·오프라인 재계산·시각화만. focused 테스트와 SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP(이번 lap source 변경 0, lap1043 full PASS 1633 `logs/gates/lap1043-work-full-check2.log`).
- 미검증: 팔레트 인덱스 단계 기준(제품 내부)과 RGB 기준의 차이, 새 gate로 실제 게임 pair를 다시 실행한 결과(다음 work 실행에서 자연 관측).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1043 work, 1,543 B, SHA256 `88f8832abc558a7ef70be93cdc7856978882aadcadc68bd330da29e71ef0c7ed`)

```
lap1043 work(Claude Code claude-sonnet-5-5) → Opus middle 독립 검수 인계. 마일스톤 경계 = W-1(사용자 결정 2026-10-06 01:43 KST) 구현 완료, 자가 승인 금지.

변경(uncommitted): tools/g1_saved_scene_probe.py (_v2s_scale2x_reference 신규, _compare_images v2s_status=unexplained≤2000, v2s_raw_status 비gate 진단, v2s_scale2x_reference_blocks·v2s_unexplained_single_black_blocks 키), tests/test_g1_saved_scene_probe.py (신규 3 테스트+1 pin).
기록: docs/history/laps/20261006_lap1043_work_g1_w1_v2s_unexplained_gate.md. 산출물: 공유 temp 20261006_lap1043_work_w1/ (w1_offline.py/json, w1_s6_reaggregate.json).

검수할 것(제품 helper 없이 새 스크립트로):
1. 보존 PNG(lap901 3 pair·lap854 3·lap957 3·lap959 r1·lap1039 r_s6_r1/r2)에서 raw/ref/unexplained를 독립 재계산해 기록 수치와 대조(lap901 15 tag 전부 FAIL 18,712~19,901, 정상군 PASS, lap1039 s6 5 tag PASS unexplained ≤202).
2. 커널이 제품 tools/inmm_stub/g1_scale2x_core.h(EPX, 경계 clamp, written 전부)와 같은 규칙인지 source 대조. 단 PNG 단계는 RGB 같음 비교(제품은 팔레트 인덱스).
3. 집계·한도·tag·V1/V2/V2q·_pair_status 불변을 diff로 확인. 저장된 과거 pair-result는 수정 0.
4. W1-3 재집계 PASS는 오프라인 산술(성능·terrain 미요청)이며 새 런타임 증거 아님. PNG 육안(격자/seam) 확인은 이번 lap 미수행 — middle 몫.
수용되면 다음 work = H-U(0x468360, 사전등록 lap1042 기록 §다음 work 2).
```

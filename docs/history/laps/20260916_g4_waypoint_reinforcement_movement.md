# G4 original-current-waypoint reinforcement — one-shot movement (2026-09-16)

## Scope / result

`WAYPOINT_REINFORCEMENT_MOVEMENT_PASS` — **private one-shot 진단만**.
두 AI의 기존 group에 가입시키지 않고, roster 밖 idle combat unit을 원본 AI가 이미 계산한
현재 waypoint로 원본 `0x4AEDE0`를 통해 이동시켰다. 길찾기 교체/지속 정책/난이도 개선/제품 완료 아님.

Luna/high 구현 → root Sol/high fresh167 targeted PASS 후 실제 한 run → analyzer ack/error/command3
정렬 guard 추가11 tests → 최종 fresh171 targeted PASS. Fast500/Ruff/compileall/mypy/CONTEXT/safety
PASS는 마지막 test/analyzer followup 전의 검증이며 최종 전체 Fast는 다시 실행한다.

## Actual observation

Private manifest `local/runtime/20260916_164148_3970772_0/manifest.json`, original seed1 chain,
180초/0.25초 표본718개. 170.074초/tick5676 mainloop callback6ms.
Ack status `completed`, `result.ok=true`, sampling error `None`, cleanup process residue0.

| owner | source slot / full ID | before position | AI waypoint | command3 distinct coords | after position | target minimum/final gap |
|---:|---|---|---|---:|---|---|
| 0 | 1164 / 656524 | (8,10) | (9,31) | 21 | (11,29) | 2 / 2 |
| 1 | 1165 / 525453 | (12,97) | (10,75) | 22 | (10,76) | 1 / 1 |

Owner0은161.280~169.824초35개 pre-observation에서 위치(8,10),command1만 유지했다.
Owner1은159.024~169.824초44개에서 위치(12,97),command1만 유지했다.
이들은 전체140초를 정지한 유닛으로 표시하지 않는다: 첫 관측이159/161초인 새 identity다.
각 source는 pending1→`0x10003`, exact packedxy가 waypoint와 일치했다. Command3 관측은 각각
28/30개이고 그 구간의 distinct coordinate가21/22개이다. Owner AI before/after true, full-ID 교체 없음.
두 source 모두 waypoint5칸 안에 도착한 관측이 있으나 고정 one-shot route milestone 이상의 성공은 아니다.

## Independent failure / limitations

G1 baseline의 뒤따르는 fixed minimap click은 camera(7,6)가 바뀌지 않아
`FAIL_NO_EFFECT`로 CLI rc2를 반환했다. 이 UI tail 실패/전체 error는 그대로 유지한다.
정상 waypoint ack와 오류 없는180초 sampling은 그 앞 단계에 별도로 보존되어 국소 이동만 판정한다.

- 적 전체 탐색/적 target ID 주입 없음. 원본 AI current waypoint 재읽기, all200 physical roster IDs 제외.
- group count/route/state/member/map/source identity/live/pending guard 및 owner당 최대 한 call.
- group/roster 수정 없음. source가 이후 AI route를 지속 추종한다는 증거 없음.
- 두 owner2기/한 seed/단일 run이며 전략 향상/승률/8인/LAN/장기 검증 없음.
- general bridge timeout/in-flight race를 persistent hook으로 승격하지 않는다.
- 한 번의 movement PASS를 A* 품질/전체 정지 원인 해소/제품 G4 완료로 쓰지 않는다.
- 같은 seed 단일 fresh repeat를 Luna/high에 지정했다. repeat 결과는 PENDING.

## Evidence (external)

`temp/Syw2plus_patch/g4_ai/20260916_seed1_waypoint_reinforcement180/`

- runtime `e47c93011d77678eab5e95ae2f49a3dc0e928308ccc0c8820a6af537732dcbef`
- probe `927995ad7c3a7432ffab573d8cfebd272d605eadaf2aef6ab922f6961825bb9e`
- outcomes `6b1a682ee8658f764c273af9a2adbc7d964d032548e9e50d3cae9f73ec37d589`
- bridge `2f7fc703fb92fc24bc9fd73f8e5961d29a1595461329838f9bfbb42a4bce62df`
- original unchanged `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- manifest, control result/events, unit tick/watch logs and bridge preserved externally; no commit/deploy.

## Sol/high independent actual review

같은 artifacts와 analyzer를 독립 재계산하여 한 current-waypoint 이동만 **ENDORSE**했다. Ack/sampling과 개입 전command1/live/full-ID, 개입 후command3 이동/목표gap을 확인했다. 전체200 route 슬롯 제외는 pinned C guard로 확인하지만 runtime snapshots는 populated group prefix만 포함한다. 따라서 all200 runtime 슬롯을 산출물만으로 독립 재검증했다는 주장은 하지 않는다. 두 source가 populated group member 목록에 없는 것은 확인됐다. 그룹 가입/지속 정책/제품/결정론/장기/LAN은 미승인이다.

## Archived original control (descriptive, not fresh matched proof)

기존 no-intervention seed1 180초 `20260916_seed1_group_targets180/output/g1_baseline.json` SHA `19bf214b4c27c009b0190810a9a43531d95ba2dcd166a6f888069f52414badee`에서 동일 source656524는161.069~179.875초76samples 위치(8,10)/command1만, source525453는158.812~179.875초85samples 위치(12,97)/command1만 유지했다. 개입 run에서 이 두 identity가 이동했다는 기술적 비교에는 도움이 된다. 그러나 이전 bridge/wallclock 표본이므로 fresh matched control·결정론·품질 판정으로 승격하지 않는다.

## Final fresh Fast verification

최종 `make check` **504 passed / 159.51s**·Ruff/compileall/mypy10files/CONTEXT PASS·`checks/safety.py` SAFETY_PASS.최종 partial-trace behavioral regression과 ack/command3 analyzer followup을 포함한 fresh 실행. 실제 게임180초와 별도 Fast 증거이며24k/144k/LAN/제품 승인이 아니다.

## Fresh repeated one-shot — local movement repeated

Luna/high 새 private run `20260916_164656_4029886_0`, same bridge, seed1/180초/0.25초/170초 intervention.717samples, ack completed/oktrue6ms, sampleerrorNone, cleanup0. Root Sol/high는 실제ack와새 analyzer를fresh재계산하여국소PASS를확인했다.

동일 source656524/525453, waypoint(9,31)/(10,75), command3distinct21/22,endpoint(11,29)/(10,76),targetgap2/1을다시관측했다. 그러나 first tick5676 vsrepeat5680, wallclock170.074 vs170.119라**같은simulationtick발행/결정론증거아님**. 정상phase persistent hook·지원mode/save/load·전략품질은아직미검증. G1minimap tailFAIL도반복되었으며 전체제품PASS로바꾸지않는다. 추가one-shot반복은하지않고정상AI삽입경계discovery로진행한다.

외부 `temp/Syw2plus_patch/g4_ai/20260916_seed1_waypoint_reinforcement180_repeat/`:
- runtime SHA `5b6f837ed00f0e6e3876f42ae861d0c8c36052c0e14f40b25ccb70fb01af447c`
- probe SHA `55d7a6d42432154a7178b9eb35f7cfd7ca6e71a0a7ea52f441c1b5fb3f32e86f`
- saved outcomes SHA `ae3f2622dfb25dc430b8411988e826dcbb102927dcdd6f140b9ca205cc013b60`
- manifest/output/bridge/rawlogs preserved;root재계산보고서 `/tmp/g4_waypoint_repeat_root_review.json`.

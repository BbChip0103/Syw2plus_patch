# 2026-10-05 | lap1013 | G1 H-S2c 독립 검수 → 수용, 다음 work H-S2w(지형 캐시 쓰기 watch) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행 0·source 변경 0·커밋 0.
- 가설 / 사용자 관찰: lap1012 work 주장 — save000 고정 카메라 stale 성분 A/B/C는 미후킹 화면 writer가 아니라 지형 캐시(`0xBA3D30`)→화면 복사 `0x466280`(EIP `0x4662DE`)가 그린 픽셀이며, candidate의 캐시 레이어 미러 결과가 원본 화면과 어긋난다(FEASIBLE).
- 예상 PASS / FAIL 조건(lap1011 사전등록 C-0~C-2): C-0 로드·census 유효, C-1 residual 비율, C-2 writer 지목. 검수 기준: 새 스크립트 재계산 불일치 0, 하네스 diff가 census-only+none 외 동작을 바꾸지 않음.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문 아래 부록). 공유 temp `20261005_lap1013_middle_review/recalc_lap1013.py`·`recalc_lap1013.json`(SHA256 `092569b759ec30fc56fe013727cf30555ff3b14417f2fbd1c8ccf68910601171`). uncommitted.
- 원본 SHA / fixture: 원본 EXE `b56986e0…08a8ac`, save000 `1c703551…19da`(index 1) — 세 run probe-result에 save000 SHA·`source_unchanged` true 확인. 활성8인 부하 증명 아님.

## 1. 독립 재계산(제품 helper·`analyze_hs2c.py` 미사용)

새 스크립트가 레코드 magic(stale `S1K1`, census `G1P1`)과 stale 헤더 계수(header[6]=값2 개수)를 직접 검증하며 읽었다.

| 항목 | work | 재계산 |
|---|---|---|
| lap1010 r1/r2 stale 300∩301 | 20,623/20,601(lap1011) | 20,623/20,601 |
| r1∩r2 교집합·성분 수 | 20,472·56 | 20,472·56 |
| A/B/C 크기·bbox | 12,651 y64..168×x38..186 / 5,442 y427..491×x371..502 / 1,167 y0..25×x259..337 | 동일, watch 점 3개 모두 각 성분 안 |
| residual(미후킹) ∩ A/B/C, 64 present 최대 | 0/0/0 | 0/0/0(세 run 모두) |
| 프레임 전체 residual min/med/max | 226~610(중앙 464) | wa 226/464/610·wb·wc 226/464/589 |
| 마지막 writer A / C | terrain_cache_transfer 100% | 동일, 64 present 전체에서 본 id도 그것뿐 |
| 마지막 writer B | 4,448 terrain + 994 rle_tinted | 동일 |
| watch EIP | W-A `0x4662DE`×63·W-C 63·W-B 63+`0x467692`×41 | 동일, in_terrain 0 |
| watch 값 | 85 / 92 상수, B 89+211~251 | 동일 |
| 캐시 전송 호출 | — | present당 1회(64/64), 합계 316/320/317, source `0xBA3D30` |
| 파일 SHA(census_raw·trace_raw·residual) | `54099265…`/`d4c6a1ed…`/`4025c177…` 등 | 앞자리 9개 전부 일치 |

C-0: probe status PASS ×3, binding `locked_source`, attribution ≥99%, present 251..314. **불일치 0.**

추가 확인(work에 없던 근거):
- 캐시↔화면 좌표 항등: W-A hit의 esi(화면)−buffer `0x022DC740` = `0x199F0` = 104,944 = 126×832+112, edi(캐시, `mov ebx,[edi]; add edi,4` 뒤) `0xBBD724`−4−`0xBA3D30` = 104,944. W-B도 esi 오프셋 = edi−4 오프셋 = 385,652(=463×832+436). → stride 832 동일·오프셋 0, **좌표/링 래핑 후보(H3)는 A·B에서 배제**.
- W-B의 `0x467692` 쓰기는 같은 present 안에서 캐시 전송 **뒤**에 오는데(seq 17→18), census 마지막 writer 지도에서 그 점은 64/64 terrain으로 남는다. `0x467580` 계열은 census writer 표 밖이므로 B의 반투명 쓰기가 지도에 안 잡힌다 — B 994 px·watch 점 차이는 별도 카드(아래 §4).

## 2. 하네스 diff 검토

`tools/g1_saved_scene_probe.py` SHA `efc40037…6262`, test `22a8f415…f9b2` = work 기록. (둘 다 git 미추적 파일이라 diff는 영역 대조로 확인.)
- `_scene_option_error`: `census_only` 인자는 받기만 하고 거부 조건에서 빠짐. terrain-scroll/trace/rice/scroll-phase 거부·save000의 none 강제는 유지.
- census 분기(5299행): `fixture=args.fixture, scene_actions=args.scene_actions` 전달. 기본값 save006/기본 actions라 기존 census 호출은 그대로다.
- `_census_loaded_wait_timeout` 대기는 `scene_actions == "none"` 이고 census일 때만 실행된다. 일반 pair 경로는 바뀌지 않는다.
→ census-only+none 외 동작 변화 없음. 사소한 점: `census_only` 인자가 쓰이지 않는 채로 남았다(정리 대상이며 결함은 아님).

## 3. 판정

**H-S2c PASS(partial) 수용.** A/B/C는 미후킹 화면 writer가 아니라 `0x466280`(캐시 `0xBA3D30`→화면) 전송이 그린 픽셀이다.

원인 위치는 정적 검토로 좁혔다. candidate `transfer_cache_to_screen`(`g1_mirror2x.c`)은 캐시 레이어의 `g_layer_covered=1`인 픽셀에 대해 `g_layer_expected`를 화면 기대값으로 복사한다. 그러므로 stale은 **"1x 캐시 바이트 ≠ g_layer_expected"**, 즉 캐시 레이어 표류다. 레이어는 hook된 primitive가 cache_target일 때만 `compose_cache_layer`로 갱신되고, 이때 scratch a≠b이거나 identity lookup에 실패한 픽셀은 건너뛴다. 건너뛴 픽셀은 covered=1과 옛 expected를 그대로 가진다. `cache_layer_move_range`는 `0x4DB1D0` memmove만 따른다.

남은 후보는 둘이다.
- **H1:** 프레임 34~300 사이에 mirror가 hook하지 않은 writer가 1x 캐시에 쓴다.
- **H2:** hook된 cache writer가 쓰지만 compose가 그 픽셀을 건너뛴다.

정정: work가 1차 단서로 든 `panel_transfer_mismatch_cleared` 2,693,918은 save006(lap1000 r1/r2 3,009,975/3,010,103)과 같은 수준이라 판별력이 없다. `layer_move_calls`는 save000·save006 모두 0이고, `layer_compose_calls`는 1,428 vs 1,369, `layer_covered_pixels`는 둘 다 425,984(=832×512)다.

## 4. 다음 work 사전등록 — H-S2w(census 지형 캐시 쓰기 watch, 원본 lane)

목적: 원본에서 A/B/C 캐시 바이트에 쓰는 EIP를 찾아 H1/H2를 판별한다.
- 구현(측정 전용, 제품 mirror·gate·validator 불변):
  - (a) census DLL에 opt-in `SYW2_G1_CENSUS_WATCH_CACHE=1`을 추가한다. 켜면 watch 주소 = `0xBA3D30 + y*832 + x`(A `0x00BBD720`·B `0x00C01FA5`·C `0x00BA5B9E`)이고, 끄면 기존 화면 주소 그대로다.
  - (b) opt-in `SYW2_G1_CENSUS_WATCH_PRESENTS=N`: watch만 별도 present 계수로 N present 동안 유지한다(기본 64 = 현행). 지도 창은 64 그대로다. 현재 `g_present_count`는 64에서 멈추므로(973행) watch 전용 계수가 필요하다.
  - (c) 하네스 `--census-watch-cache`·`--census-watch-presents N`(둘 다 `--census-watch` 필요)을 추가한다.
  - (d) 테스트: 주소 계산·기본 불변·인자 검증을 RED→GREEN으로 만든다.
- 실행: save000 census-only, `--scene-actions none --census-residual --census-skip-presents 20 --census-watch-cache --census-watch-presents 700`. W-A `112,126`·W-C `302,9`를 순차로 각 1회 돌리고, 여유가 있으면 W-B `437,463`도 돌린다. 세 run 모두 fresh runtime-root, game 사본 삭제.
- 측정·판정:
  - **K-0**(유효): C-0과 같은 조건, `watch_armed` address = 위 캐시 주소, selftest hit 1, cleanup ok.
  - **K-1**(관측): 창(≈20..720) 안의 watch hit 수와 EIP·값·present 분포.
  - **K-2**(분류): 각 EIP가 mirror hook 함수 범위(`0x466D50`·`0x4664D0`·`0x468C30`·`0x468CC0`·`0x468E10`·`0x468F00`·`0x4690A0`·`0x466EA0`·`0x466540`·`0x466070`·`0x465B30`·`0x466B50`·`0x4672E0`) 안인지 밖인지. 원본 objdump(read-only)로 함수 경계를 확인한다.
- 결론 규칙:
  - hook 밖 EIP가 있으면 **H1 FEASIBLE** → 다음 work는 그 writer의 cache_target 미러를 사전등록한다.
  - 전부 hook 안이면 **H2** → 다음 work는 candidate lane에서 compose skip 사유(a≠b / lookup miss) 계수와 A/B/C 범위의 레이어 표류(캐시≠expected) 첫 ordinal 진단을 opt-in으로 넣는다.
  - 창 안 hit 0이면 캐시가 다시 쓰이지 않은 것이므로 역시 H2 진단으로 간다(레이어 expected 자체 표류).
  - FAIL/BLOCKED: 무장 실패나 load 무효는 하네스 결함으로 수리 후 재실행한다(PROMPT ③ 반복).
- 별도 backlog: B 994 px `0x467692`(`0x467580` 계열 반투명, census writer 표 밖) 카드, 성분 D, hold keydown 위상 경합, 가장자리 마우스 스크롤.

## 5. 검증 / 남은 위험

- 이번 lap은 문서와 재계산만 했다. focused 검사 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1012 full PASS 1609 유효).
- H1/H2는 아직 판별되지 않았다. 원본 lane과 candidate lane의 present 속도가 달라 ordinal 대응이 부정확하므로 watch 창을 넓게 잡았다.
- 사용자 승인 상태: 기술 부분 수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1012 work)

```
lap1012 work(Claude Code claude-sonnet-5-5) G1 H-S2c 인계 (마일스톤 경계 아님, 일상 middle 검수 요청).
- 한 일: 하네스만 — g1_saved_scene_probe.py에서 --census-only를 --scene-actions none과 결합 허용, census 분기에 fixture/scene_actions 전달, loaded-only+census면 64 present 창 대기. 테스트 2개 신규 RED→GREEN(194 passed), lint·typecheck PASS. 제품 DLL/gate 변경 0.
- 실행: save000 census-only 순차 3회(W-A 112,126 / W-B 437,463 / W-C 302,9, skip 250) 전부 exit 0, C-0 PASS(tick 50594/50595/50594·카메라 (39,53)·units 375·census_gate PASS·cleanup ok).
- 결과: lap1010 r1∩r2 성분 A 12,651/B 5,442/C 1,167 모두 residual(미후킹) 0. writer는 A·C 100% terrain_cache_transfer(EIP 0x4662DE = 0x466280 본체 복사 루프, 값 상수 85/92), B는 4,448 terrain_cache_transfer + 994 rle_tinted(W-B EIP 0x4662DE 63 + 0x467692 41). → 미러 밖 writer가 아니라 지형 캐시→화면 미러 경로 결과가 이 장면에서 어긋남. 판정 FEASIBLE.
- middle이 확인할 것: analysis_hs2c.json(공유 temp 20261005_lap1012_work_s2c/)을 새 스크립트로 독립 재계산(r1∩r2 20,472·성분 크기·writer 지도·watch EIP), 세 run C-0, 하네스 diff가 census-only 외 동작을 바꾸지 않는지, 다음 work 사전등록: candidate lane mirror_cache_copy(source 0xBA3D30) 호출별 x/y/w/h·거부 계수 + census_context_map으로 프레임 34~300 캐시 쓰기 writer.
- 기록: docs/history/laps/20261005_lap1012_work_g1_hs2c_save000_census.md. 변경 uncommitted.
```

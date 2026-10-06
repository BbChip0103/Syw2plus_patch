# 2026-10-05 | lap1030 | G1 work H-N — `0x465E80` 단색 사각형 diff 미러(바닥 4×6 조각)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1029 middle 사전등록(§5) — 미후킹 `0x465E80`(thiscall `ret 0x14` leaf, old bytes `8B 41 10 53 55`)을 원본 범위 검사(x·y 모서리가 [0,stride)×[0,`[r+0x14]`) 복제 + 정렬·양끝 포함 + 화면 800×600 교집합 diff 미러로 hook하면 save000 바닥 4×6 조각 stale이 사라진다.
- 변경 파일:
  - `tools/inmm_stub/g1_rect_fill.h`: 호스트 테스트 가능한 `g1_rect_solid_region()` 추가
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_RECT_SOLID`·`G1_RENDERER_YBOUND 0x14`·`mirror_rect_solid`·계수 8개(`ybound` 포함)·install/restore/installed/reset
  - `tools/inmm_stub/g1_mirror2x.h` accessor 8개, `tools/inmm_stub/direct_draw_trace.c` 요약 `rect_solid_465E80_*` 8키 + `mirror_details` 5000→5400(+약330자 보정, 쓰기는 wsprintfA/lstrcatA라 여유 확보)
  - `tests/test_g1_rect_fill.py` 2개 신규(RED→GREEN), `tests/test_g1_panel_layer.py:115` pin 5000→5400(제품 자체 버퍼 크기 계약, 안전 pin·golden 아님)
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result `private_exe_sha256` 4 run 일치, 직접 확인). `_inmm.dll` `6b7bfca1c2fd82ea…`, `g1_mirror2x.c` `23667cc8ad158cbd…`, `g1_rect_fill.h` `1b22db0ac7a2680d…`, `direct_draw_trace.c` `4823d1ccec3e6956…`(sha256 앞 16자). 빌드는 `make -C tools/inmm_stub`, 경고 0.
- 원본 역어셈블 재확인(`objdump_465E80.txt`): 인자 x0,y0,x1,y1,color(dl). `jge`/`jl` 부호 비교로 x∈[0,stride)·y∈[0,`[ecx+0x14]`) 밖이면 쓰기 0. `and eax,0xff; cmp eax,0x100`은 항상 거짓. 쌍 정렬 뒤 양끝 포함. 클립 없음.
- 실행: `…/20261005_lap1030_work_hn/run_n.sh`(lap1028 `run_m3.sh` 인자 그대로: save000 pair 2회 `--layer-drift --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`, save006 env-off pair 2회 `--stale-mask 6-12,30-34,300-301,585-620,880`). 로그 `logs/gates/lap1030_hn_*`. 4 run 전부 pair exit 2 = 기존 pair HOLD(V2s raw)이며 이번 변경과 무관. 실행 전 load 1분 2.56, 게임 `game` 사본은 probe가 정리해 잔존 0.
- 분석 스크립트(공유 temp `20261005_lap1030_work_hn/`): `analyze_n_s0.py`(lap1028 `analyze_m3_s0.py` 복사)·`analyze_n_mask.py`(덤프 교집합)·`analyze_n_s6.py`(lap1028 s6 복사, 경로만 변경).

## 결과 (기준 = lap1028 m3 r1/r2)

| 항목 | 기준 | 이번(r1 / r2) | 판정 |
|---|---|---|---|
| N-0 설치·항등식 | — | inv 3296 = mirrored 3292 + target 2 + size 2 (bounds 0·guard 0), `ybound` 600, save006 inv 3673 = mirrored 3673 | PASS |
| N-0 안전·scene | 안전 0 | 안전 7종 0, cleanup·source_unchanged true, scene_state_equal true(S-0), 원본 SHA 일치 | PASS |
| N-1 39덤프 공통 stale | 168 px | **0 px**(r1·r2 각각도 0) | PASS |
| N-1 바닥 | 교집합 중앙값 408 | y515..549 stale 덤프당 중앙값 216 → **0**, 4×6 조각 덤프당 9 → **0**(39덤프 전부, 총합 7,872 → 0). 덤프에서 base에 없던 신규 stale r1 0, r2 755 px(run 간 p298 ±변동 범위) | PASS |
| N-1 마지막40 중앙값 | 414.5 → ≤100 | **246.5**(r1=r2) | **FAIL** |
| N-2 창 중앙값 | 5% 초과 증가 금지 | 모든 창 감소(아래) | PASS |
| N-2 표본 A/B/C | stale 0 | 0/0/0 유지, `u` 5/1/1 불변 | PASS |
| N-3 성능 | p95 ≤8·비 0.995..1.005 | p95 7/7(cand)·tick 비 19.99966/19.99959 ≈ 1.00000 | PASS |
| N-4 save006 env-off | 38프레임 ≤24 px | **0 px**(성분 D y515..520×x616..619도 0)·39프레임 0·신규 0·p95 7/7·cov p50 99.31%·안전 0 | PASS |

N-2 창 중앙값(기준 m3 r1/r2 → 이번 r1/r2): p0..83 216 → 0/0, p24..58 216 → 0/0, p84..297 316 → 124/124, p298..338 858/727 → 667/558, p339..365 591 → 423/423, p84..365 356 → 164/164, p366.. 399.5 → 246.5/246.0, 마지막40 414.5 → 246.5/246.5. 감소분은 창마다 바닥 조각 수(7~9개 × 24 px = 168~216)와 일치한다.

## 해석
- 바닥 writer = `0x465E80`이 맞다. 미러 후 save000 바닥 4×6 조각 stale이 39덤프에서 완전히 사라졌고(7,872 → 0), save006 성분 D 24 px도 같은 writer라 0이 됐다. 새 stale·성능·안전 회귀는 없다.
- **N-1 마지막40 ≤100은 미달(246.5)**이다. 원인은 사전등록의 분해 오류다. 마지막40 중앙값 414.5 = 바닥 168 + 그 밖 246.5(r1=r2, 창별 감소량이 정확히 168/216 = 바닥 몫). 바닥 몫은 100% 제거됐고, 남은 246.5는 바닥이 아닌 다른 stale이다.
- 남은 stale 덤프 성분(예: p377 y134..155×x748..768 258 px, p352 y457..476×x686..722 329 px, p366 y372..383×x777..790 122 px·y138..150×x782..793 94 px, p388 y449..475×x697..721 170 px 등)은 우측(x≥686) 영역의 21×21 안팎 덩어리다. 위치가 프레임마다 이동하므로 이동 스프라이트·미니맵 근처 UI 가능성이 있으나 writer는 미귀속(UNKNOWN)이다.
- N-1 미달 처리: PROMPT/사전등록의 FAIL 처리는 "남은 조각 `--drift-samples` 재귀속, 수리 1회 뒤 재실행"이다. 이번 바퀴는 한 가지 가설(H-N)만 다루므로 재귀속은 다음 work에 넘긴다(바닥 가설 자체는 확정·수리 완료).

## 회귀 / 남은 위험 / 독립 검수
- 호스트 테스트: `tests/test_g1_rect_fill.py` 12 passed(신규 2), lint·typecheck PASS. 전체 `make check`는 기록 freeze 뒤 1회 실행(결과는 STATUS 보강).
- 남은 위험: `0x465E80` 호출 33곳 중 save000/006에서 관측한 3,296/3,673회만 검증. reject_target 2·reject_size 2의 호출 인자는 미기록. `[r+0x14]`는 600(두 장면)이나 다른 렌더러 상태는 미측정.
- 사용자 승인 상태: 기술 부분수용 요청일 뿐 G1 마일스톤 승인이 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 4 run 재계산(공통 168→0·바닥 조각 9→0·마지막40 246.5·save006 D 0), (2) 마지막40 미달의 분해(168 + 246.5) 수용 여부와 사전등록 기준 정정, (3) `mirror_rect_solid`/`g1_rect_solid_region` 코드 검수(부호 비교·양끝 포함·화면 교집합·before 버퍼 크기), (4) 다음 work 사전등록: 남은 우측 stale 덩어리 위치·writer 귀속(`--drift-samples`).
- 다음 한 가지: middle H-N 독립 검수 → work H-O(우측 stale 덩어리 귀속).

# 2026-10-06 | lap1045 | G1 work H-U — `0x468360` 클립 좌우반전 반투명 RLE(7인자) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1042 middle 사전등록(§다음 work 2) — 미후킹 `0x468360`(thiscall `ret 0x1c`, old bytes `83 EC 1C 53 55`, 반전은 목적지 `rect∩clip`을 바꾸지 않음)을 H-P `mirror_blend_clip7` 동형 diff 미러로 hook하면 save000 표본 S1 (795,470)의 마지막 writer `0x468571` stale present 5가 0이 되고 마지막40 stale 중앙값 26 아래로 내려간다. 재계획 없이 사전등록 그대로 구현했다.
- 변경 파일:
  - `tools/inmm_stub/g1_mirror2x.c`: `G1_BLEND_FLIP7 0x00468360u`·`_LEN 5u`, `expected_blend_flip7 {83 EC 1C 53 55}`, `g_original_blend_flip7`(`G1Primitive7Fn`), `g_hook_blend_flip7`, 전용 before 버퍼 `g_blend_flip7_before`, 계수 9개, wrapper `mirror_blend_flip7`(`mirror_blend_clip7`과 이름·주소 상수 외 동일: x·y·w·h 16비트 부호 확장, 화면 교집합, 원 인자 7개 그대로 1회 호출, `g1_overlay_blt_apply`, `layer_drift_write_end(... G1_BLEND_FLIP7 ...)`), install·restore·installed·reset·accessor
  - `tools/inmm_stub/g1_mirror2x.h` accessor 9개, `tools/inmm_stub/direct_draw_trace.c` 요약 `blend_468360_*` 9키 + `mirror_details` 6600→7200(2곳, 아래 용량 근거)
  - `tests/test_g1_rect_fill.py` 신규 `test_blend_clip_flip7_hook_table_and_wrapper_contract`(RED→GREEN)·기존 H-P/H-Q pin 6600→7200 갱신, `tests/test_g1_panel_layer.py:115` pin 6600→7200(제품 자체 버퍼 크기 계약, 안전 pin·golden 아님)
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result source_unchanged true 전 run). source sha256 앞 16자: `g1_mirror2x.c` `f20c6aecf974132c`, `g1_mirror2x.h` `37f0aa496e8d37aa`, `direct_draw_trace.c` `4615f2f9f20cd504`, `test_g1_rect_fill.py` `d7aa45d301964fc6`, `test_g1_panel_layer.py` `a669ac4f321ed829`. 원본 old bytes·명령 경계는 lap1042 middle objdump 검수를 쓰고 설치 시점에도 `install_one`이 검증한다(전 run 설치 성공, `mirror_details` 정상 출력). 인자 배치는 lap1042 objdump 재독해로 `x=[esp+0x2c]·y=0x30·w=0x34·h=0x38·rle·remap·level`(movsx 16비트)이 H-P와 같음을 확인했다.
- 실행(공유 temp `20261006_lap1045_work_hu/`, 로그 `logs/gates/lap1045_hu_*`): `run_u.sh` `73115c4e…`(순차·단일 인스턴스·각 run 직전 load 대기·run 뒤 `game` 사본 삭제 확인). 호스트 load는 전 run 시작 시 1.2~2.8(대기 0). save000 watch pair 2회(`--fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch --drift-samples "795,470;628,409;599,367" --stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`), save000 성능 pair 2회(watch 없음), save006 pair 2회(`--stale-mask 6-12,30-34,300-301,585-620,880`). 분석: `analyze_u_attr.py`·`analyze_u_s0.py`·`analyze_u_s6.py`·`isect_u.py`·`setdiff_u.py`(lap1039/1041 스크립트 복사 후 키·경로만 변경). 컴파일은 `/tmp`에 별도 빌드해 `-Wall -Wextra` 경고 0 확인.

## 수치

| 항목 | 기준(lap1041 s1_r2/r3, lap1039 s0·s6) | lap1045 |
|---|---|---|
| U-0 안전 7종·cleanup·source_unchanged | 0 / true / true | watch 2·성능 2·save006 2 전부 0 / true / true, ps3 410/410(save006 900/898) |
| U-0 항등식 `invocations = mirrored + reject_*` | — | save000 전 run 62 = 8 + 54(reject_bounds), reject_target/size/guard 0, clipped 8, mirrored_pixels 3,013, changed 8. save006 32 = 0 + 32(전부 화면 밖) |
| **U-1** S1 (795,470) stale present·마지막 writer | 20 (`0x466D15` 12·**`0x468571` 5**·`0x46884E` 2·`0x467CCF` 1) | **15 (`0x466D15` 12·`0x468571` 0·`0x46884E` 2·`0x467CCF` 1)** r1·r2 동일, 값 일치 15/15 |
| S1 (628,409)·(599,367) | 1·1 (`0x46884E`) | 1·1 (불변), u 6/4 |
| 무장·selftest | PASS·fail 0 | selftest PASS·무장 52라운드 fail 0·좌표 3/3·dropped/overflow 0 |
| **U-2** 마지막40 stale 중앙값 | 26 | **0 / 0**(watch r1·r2), 성능 r1·r2도 0. p366~ 0, p24..58 0 |
| U-2 새 r1∩r2 ∖ 기준(s1_r2∪s1_r3) | — | **0**(39프레임) |
| U-2 기준 r1∩r2 ∖ 새 r1∪r2 (제거) | — | **24 px**(프레임 388 하나, 나머지 0) |
| U-2 r1∩r2 합(참고, 지표 불안정) | 1,114 | 1,749(성능 pair 2,972, lap1039 2,776) — 증가분은 새 ∖ 기준 0이므로 기준 run 변동(팝업 p298..338 281~412, p84..365 창)이다. 이 합으로 결론 내지 않는다 |
| **U-3** p95(성능 pair) | 7/7 | **7 / 7**(≤8), tick delta 400 vs 기준 baseline 399 → 비 1.0025(0.99~1.01). 대조(미러 off) 미실행(미달 아님). watch run p95 11은 watch 계측 run이라 판정 외 |
| **U-4** save006 | 38프레임 r1∩r2 0·신규 0 | **38공통 덤프 r1∩r2 신규 0·기준 대비 신규 0/0·제거 0**, p95 7/7·cov p50 99.32/99.31%, 안전 0, pair status **PASS(exit 0)** 2회 — W-1 gate 효과(V2s 5 tag 전부 PASS) |

- save000 pair 4회는 exit 2·status HOLD(기존 구조: loaded 외 tag BLOCKED, V2s와 무관). 이번 변경과 무관하다.

## 해석
- 가설 확정: 표본 S1 (795,470)의 p388 가장자리 writer `0x468571`(= 미후킹 `0x468360`) 5건이 diff 미러로 전부 사라졌고(r1·r2 동일), 분리 확인 대상 `0x466D15`(12)·`0x46884E`(2)·`0x467CCF`(1)은 그대로다. 마지막40 중앙값 26→0, 새 stale 0. 제거는 프레임 388의 24 px뿐이라 H-U의 효과 범위는 좁다(가설 예측과 일치).
- 남은 stale = 사전등록 후속 writer: S1 `0x466D15`(12 present, `0x466BE0`)·`0x46884E`(`0x4687F0`)·`0x468A28`(`0x4689C0`). 이번 lap은 건드리지 않았다.
- `mirror_details` 용량: H-Q 최악 6,141 + 신규 블록(키 9개·값 각 ≤10자리 ≈ 340 B) ≈ 6,500 → 6,600은 여유 100 B 안팎이라 7,200으로 올렸다(2곳 + 3개 테스트 pin). 호스트 테스트로 `wsprintfA` 상한이 아닌 버퍼 크기 계약만 검증했으며 최악 실측은 `mirror_details` 출력 길이를 middle이 확인한다.
- save006 pair가 처음 exit 0/PASS가 됐지만 이는 W-1(사용자 결정) 효과이고 H-U의 제품 수치가 아니다. 사용자 G1 승인이 아니다.

## 회귀 / 남은 위험 / 독립 검수
- 호스트 테스트: `tests/test_g1_rect_fill.py`·`test_g1_panel_layer.py` 19 passed, `make lint`·`make typecheck` PASS. 전체 `make check`는 기록 freeze 뒤 1회 실행(결과는 STATUS 보강).
- 남은 위험: 표본 3점뿐이라 `0x468360` 전체 호출을 대표하지 않는다(save000 호출 62 중 mirrored 8). 호출처 `0x41A8E7`·`0x41AA5F` 중 관측분만 검증. 대조(미러 off) 성능 run은 U-3 미달이 없어 실행하지 않았다.
- 사용자 승인 상태: 기술 부분수용 요청일 뿐 G1 마일스톤 승인이 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 watch r1·r2·성능 r1·r2·save006 r1·r2와 기준(lap1041 s1_r2/r3·lap1039 s6) 재계산(항등식 62=8+54·`0x468571` 5→0·나머지 EIP 불변·마지막40 0·새 ∖ 기준 0·제거 24·save006 신규 0·p95·tick 비), (2) `mirror_blend_flip7` 코드가 `mirror_blend_clip7`과 상수·이름 외 동일한지·원 인자 7개 1회 전달, (3) `mirror_details` 7,200 용량 최악 길이 점검, (4) 다음 work H-V 사전등록(`0x466BE0` 실효 44 → `0x4687F0` 26 → `0x4689C0` 8).
- 다음 한 가지: middle H-U 독립 검수 → work H-V(`0x466BE0` 클립 형제 diff 미러).

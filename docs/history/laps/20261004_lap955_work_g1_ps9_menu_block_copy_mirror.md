# 2026-10-04 | lap 955 | G1 work — PS9 메뉴 block_copy `0x466280` 미러 구현·coverage 실측

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high, Fast OFF / work(hands-on 구현). lap954 카드 §5 인계 수행.
- 가설: PS9 full-screen `block_copy`는 renderer 타깃에 쓰는 **packed(stride=w) 800×600 소스**(원본 EXE objdump `0x466280`: 소스 포인터가 연속 증가, 목적지는 `renderer+0x1514 + pitch*y + x`)이므로, 기존 `mirror_cache_copy` 후크(이미 설치됨)에서 소스를 직접 Scale2x하면 PS9 HD coverage가 오른다. 같은 호출이 모든 present에서 같은 소스를 쓰는지는 hash로 측정.
- 예상 PASS / FAIL (카드 §5, 새 임계 없음): PASS = PS9 모든 present ≥90% · V1(`hd_mask_outside_diff_subpixels`) 0 · identity 차이 0 · PS3 비하락. FAIL = PS9 <90%. BLOCKED = 소스가 present마다 변하는 scratch.
- 변경 파일: `tools/inmm_stub/g1_mirror2x.c`(`transfer_block_copy_to_screen` 추가, `mirror_cache_copy` 비-cache 분기 호출, `menu_copy_*` 카운터 5개), `g1_mirror2x.h`(getter 5개), `direct_draw_trace.c`(`mirror2x_present` 직렬화 1곳에만 5필드 추가, `layer_details` 240→400(최악 360자); `mirror2x_metrics` 지점과 `mirror_details[2048]`는 불변), `tests/test_g1_mirror2x.py`(RED→GREEN 1건). EXE/validator/gate/golden 변경 0, commit 0.
  - 분기 조건: `(x,y,w,h)==(0,0,800,600)`·소스≠cache base·타깃≠panel-bound 버퍼·renderer pitch≥800/height≥600·소스 800×600 readable. 소스 전체 FNV-1a hash를 호출마다 계산해 `menu_copy_hash_first/last/changes`로 노출(기본 raw 기존 키 불변, 키 추가만).
  - scale2x 모드: `g1_scale2x_build_masked`(전 픽셀 written=1)로 미러 갱신, 그 외 모드: 최근접 복제. `g_covered=1`·`g_expected_snapshot`=소스 픽셀. 이후 다른 writer가 덮은 픽셀은 기존 present stale 판정으로 nearest.
- 원본 SHA / fixture: 원본 EXE `b56986e0…a8ac` MATCH(read-only 재해시), save006 `616b7997…d064` 비합성(selected_index 7), 활성8인 부하증명 아님. 모든 run `source_unchanged`·`game_removed` true, trace_close PASS.
- source SHA(종료 시): `g1_mirror2x.c c876f645…5e0a`·`.h 4514f602…6141`·`direct_draw_trace.c 29218392…0082`·`test_g1_mirror2x.py eeaeaf51…06e7`.
- 중간 수리 1건: 첫 `make check`(1510 passed·5 skipped·**1 failed**, 로그 `logs/gates/lap955-work-full-check.log`)가 `tests/test_g1_panel_layer.py`의 `char mirror_details[2048];` 문자열 pin 실패 — 내가 `mirror2x_metrics` 지점 버퍼를 3072로 키운 것이 원인. pin/테스트를 고치지 않고 그 지점의 변경(5필드·3072)을 되돌려 원래 형식으로 복원했다(5필드는 present 레코드에만 둠). 이후 r2를 최종 source로 재실행했다. r1/id/idoff는 그 지점만 다른 직전 source로 실행했으나 `g1_mirror2x.c`는 동일(c876f645)이고 `mirror2x_present` 직렬화도 동일하다.
- 실행 명령(모두 `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/<run> --artifact-root <공유temp>/20261004_lap955_work_menu_blockcopy/<run> --hd-source <mode>`), 로그 `logs/gates/lap955_menu_{r1,id,idoff}.log`:
  - **최종 source 재실행 r2 `scale2x`**(exit0, pair PASS, scale2x_gate/V2/input_effect PASS, source_unchanged·game_removed true): PS9 46 present min **99.454%**·V1 0·hash `1777000796` 불변(46회, changes 0); PS3 896 present p50 90.414%. raw `r2/candidate/trace_raw.jsonl` SHA `e1c0404a…3d1b`, `hd_cov_r2.json` `cf167af8…9831`.
  - r1 `scale2x`(exit0, pair PASS, scale2x_gate PASS, V2/V2s/V2q PASS, input_effect/minimap PASS, scale2x 팔레트 위반 0, 1084 present) · id `identity`(exit0 PASS) · idoff `identity` + 분기 임시 비활성(귀속 대조; 실행 뒤 source 복원, SHA c876f645 일치 확인).
  - 컴파일 확인 `i686-w64-mingw32-gcc`(경고·오류 0, `/tmp` 산출만, 추적 `_inmm.dll` 미변경).
- 측정(`hd_cov.py`: present별 `(covered−stale)/480000`, 분모 보수적):

| run | 상태 | present | min | p50 | ≥90% 비율 | V1 outside diff max | menu_copy calls/pixels/hash first=last/changes |
|---|---|---|---|---|---|---|---|
| r1 scale2x | PS9 | 48 | **99.454%** | 99.454% | 1.0 | 0 | 48 / 23.04M / `1777000796`=`1777000796` / 0 |
| r1 scale2x | PS3 | 897 | 89.793% | 90.413% | 99.2%(idx 6~12 미달) | 0 | (PS3 중 호출 증가 없음) |
| r1 scale2x | PS35 | 139 | 8.87% | 8.90% | 0 | 0 | 참고(다른 장면, 이번 목표 아님; lap945 2.26%) |
| id identity | PS9/PS35 | 55/115 | 99.45%/8.87% | | | inside diff 0(PS9·PS35) | 55 / hash 불변 |
| idoff(분기 OFF) | PS9 | 47 | 5.73% | 5.73% | 0 | | 변경 효과 귀속: 5.73→99.45% |

- 판정(카드 §5 사전등록 대로):
  - **PS9 HD coverage PASS(partial)**: 모든 present ≥90%(최저 99.454%), V1 0, identity 오라클에서 PS9 inside diff 0, 소스 hash가 48/55회 호출·두 run 모두 `1777000796` 불변 → 합성 scratch 아님(BLOCKED 아님).
  - PS9 잔여 stale 2,622px(0.546%)은 lap951 PS9 TextOutA 텍스트 사각형 수치와 같다(P7 명시 잔여, HD 미처리).
  - **PS3 비하락 PASS**: min 89.793/p50 90.413/last 90.43 — lap945 raw(89.79/90.42/90.43)와 동일 범위, 초기 present 6~12 미달·stale p50 42.7k도 그대로 → 이번 변경으로 하락 없음. PS3 경계(초기 7 present 89.79~89.99%)는 **미해결 backlog**.
  - PS3 min은 run마다 다르다: r2는 초기 7 present(89.79~89.96%)가 r1과 같고 추가로 중반 idx 579~630에 86.7~87.5% 하락 구간이 있다. 변경을 끈 idoff에도 같은 종류의 하락(idx 429~468, 87.05%)이 있어 메뉴 분기와 무관한 harness 입력 구간(선택/드래그/미니맵) 효과로 보이며, 원인 귀속은 backlog(PS3 stale 구성 조사와 함께).
  - identity 모드 PS3 inside diff 8.3M은 분기를 끈 idoff에서도 8.28M으로 같다 → 이번 변경과 무관한 기존 값(identity 오라클 PS3 해석은 별도 backlog, 새 임계 만들지 않음).
  - **기준2 coverage 전체는 아직 미합격**: PS3 초기 present 6~12 미달·두 번째 장면 PS35 8.9%(원본 구성/역할 미분류)·HUD/tinted/P6/P7 HD·D-2·사용자 승인 남음.
- 시각 확인: 후보 `candidate/menu.png`(1600×1200)는 메뉴 전체가 Scale2x로 매끈하게 렌더, 버튼·문자·커서·로고 정상, 원본 `baseline/menu.png`와 구성 일치.
- 중간 수리: 없음(구현 첫 실행에서 모든 게이트 PASS). 실행 중 쓴 선 조사: objdump `0x466280`(소스 packed 확인)만.
- 회귀 / 남은 위험: focused `tests/test_g1_mirror2x.py` 26 passed, `make lint`·`make typecheck` PASS. `mirror_validator` BLOCKED는 lap940 기록대로 Scale2x gate와 무관(기존 상태 동일). 메뉴 분기는 정확히 `(0,0,800,600)` 호출만 대상이라 다른 non-cache block copy(있다면)는 미지원 — PS3에서 호출 없음(menu_copy_calls 불변). 동적 API 실패 주입/강제 rollback 미검증은 기존대로.
- 독립 검수 상태: 이 work는 자기 승인 불가 → 다음 새 middle(Opus)이 raw 재계산(제품 helper 없이)·source diff·PNG 대조 필요. 사용자 승인 아님.
- 런타임 보존: `local/runtime/lap955_menu_{r1,id,idoff}` 의 game 사본만 삭제(자동), manifest/output/prefix 보존. 디스크 여유 20GiB.
- 다음 한 가지: middle 독립 검수(raw 재계산·hash 불변·PS3 비하락·attribution run) 뒤 → work: PS3 초기 present 6~12 미달/stale 42.7k 구성 원인(어느 writer가 covered를 stale로 만드는지)을 측정해 기준2 PS3 경계를 해소.

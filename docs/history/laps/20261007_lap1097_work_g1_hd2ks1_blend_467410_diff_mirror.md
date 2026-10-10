# 2026-10-06(KST 22~23시) | lap1097 | G1 work — H-D2k-s1 save000 고정 카메라 잔여 귀속·`0x467410` 수리

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 커밋 0(uncommitted).
- 가설: lap1096 §4 H-D2k-s1 — save000 카메라 (48,54) 고정 뒤 ord 260..275(3,592→847)·290..297(309→1,502) stale(마지막40 47,319)는 미후킹 또는 reject된 화면 writer가 칠한 영역이다.
- 예상 PASS/FAIL(사전등록): 귀속 PASS = 표본 ≥2/3 첫 stale 쓰기 EIP가 한 미후킹 함수 또는 개입 증거. S-3 PASS(partial) = save000 2/2 마지막40 ≤2,366·ord 145~221 0 유지·새 reject/unsupported 급증 0·save006 PASS·stale 합 ≤307·안전 0·p95 ≤ 고정+16.
- 변경 파일(uncommitted): `tools/inmm_stub/g1_mirror2x.c` `2dc25e1b64606554`(`observe_blend_410`→`mirror_blend_410` diff 미러, 상시 설치, 카운터 6·준비 조건), `tools/inmm_stub/g1_mirror2x.h` `d6b10bbd4a813758`(접근자 6), `tools/inmm_stub/direct_draw_trace.c` `f1dae646007cf0d7`(metrics 4키, `drift_hook_details` 520·`mirror_details` 9728→10240), `tests/test_g1_rect_fill.py` `d5d0ded12a96c9e5`(신규 1·기존 H-B2 테스트·slice 마커 정정). 하네스 `tools/g1_saved_scene_probe.py` 무변경.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 회차 끝 직접 재계산 MATCH(읽기만). 7 run 전부 `source_unchanged` true·`cleanup.ok`·`game` 사본 삭제. fixture: 비합성 save000(l1·a1·a2·v1·v2)·save006(v3·v4). 활성 8인 증명 아님.
- 실행 명령: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1097_work_hd2ks1/`의 `run_l.sh`(옵션 = lap1095 r1 `--hd-source scale2x --fixture save000 --scene-actions none --terrain-scroll --terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT` + 인자)·`run_a.sh`·`run_v.sh`·`run_v4.sh`, 로그 `logs/gates/lap1097_*.log/.exit`. 분석 `analyze_s1.py`·`pick.py`·`an_a.py`·`analyze_hd2ks1.py` `8cd75339dc352a3b`→`analysis_hd2ks1.json` `7b138ccfe5a57116`. pair-result SHA: l1 `159961fa`·a1 `7a5013ca`·a2 `ec3f84c4`·v1 `b8b1a017`·v2 `03af8c23`·v3 `f909d8db`·v4 `482c8ded`.

## 측정

1. **S-1 위치(l1, `--stale-mask 250-297`)**: 재현(r1과 같은 열: ord 260 3,592 → 275 847, 276..289 0, 290.. 309 → 1,502, 마지막40 52,089). 마스크 모양 = **두 개의 공성 유닛 실루엣**(성분 1,821 bbox x422..473·y282..353, 1,721 bbox x519..569·y302..369; 위에서부터 줄어듦). ord 260..275 공통 stale 805 px(bbox x423..567·y299..368). 마스크 PNG `mask_ord{260,275,290,297}.png`.
2. **S-2 귀속(a1·a2, `--layer-drift --screen-watch --screen-watch-cache --drift-samples "440,334;556,352;466,331"`)**: 표본 3점 모두 ord 260..275에서 `cache == lexp == snap`인데 `scr`만 변함(예: ord 260 표본 0 cache 191·scr 215). 그 present마다 **미후킹 `0x467410`**(진단 observe 후크)이 사각형 (x480,y272,128×128)·(x384,y256,128×128) 두 번 호출되어 샘플 값이 바뀐다(`sb`→`sa` 변화 기록, 두 사각형이 마스크 두 성분을 포함). a1 26+26회·a2 24+24회, ord 260~299, 호출·변화가 stale 열과 같은 구간. 캐시 watch hit는 memmove `0x4DB203`/`0x4DB384`·`0x468DBA`뿐이라 캐시 쪽 원인 아님. 정적(objdump 직접): `0x467410`은 `sub esp,8; push ebx; push esi`로 시작, `ret 0x1C`, 7인자(x y w h rle remap weight, 16비트 부호 확장), 클립 없음·dest=buffer+y·stride+x·w×h·RLE 0xFE 스킵·dest 의존 blend → lap953 맵 문서 "미확인 변형"이던 함수. **귀속 PASS(직접: 표본 3/3의 변화 호출이 `0x467410`, a1·a2 재현).**
3. **S-3 수리**: `mirror_blend_410`(= `0x4678C0` 미러와 같은 구조: 원본 7인자 그대로 1회 전달·화면 대상/guard 검사·사각형을 화면 교집합으로 클립·snapshot→원본→`g1_overlay_blt_apply`). `0x4676D0`은 진단 env일 때만 observe 유지. 설치 5 B pinned old bytes `83 EC 08 53 56`(설치 시 바이트 대조·restore·installed 준비 조건 포함). 테스트 RED(1 failed: 슬라이스 마커 부재) → GREEN, `test_g1_rect_fill`·`mirror2x`·`cache_fill`·`screen_watch`·`panel_layer`·`saved_scene_probe`·`overlay_blt` **300 passed**, lint·typecheck PASS.
4. **검증 run(진단 없음)**:

| run | fixture | status | ord145~221 | stale 합 | 최대 | 마지막40 | p95 ms | 안전 7종 최대 | 0x467410 mirrored calls/px/reject |
|---|---|---|---|---|---|---|---|---|---|
| r1(수리 전, lap1095) | save000 | HOLD | 0 | 47,323 | 3,592 | **47,319** | 7 | 0 | — |
| l1(수리 전) | save000 | HOLD | 0 | 52,093 | 3,592 | 52,089 | 8 | 0 | — |
| **v1** | save000 | HOLD | **0** | **4** | 2 | **0** | 8 | 0 | 50 / 49,741 / 0 |
| **v2** | save000 | HOLD | **0** | **4** | 2 | **0** | 7 | 0 | 50 / 49,741 / 0 |
| **v3** | save006 | **PASS** | 0 | 295 | 293 | 0 | 7 | 0 | 0 / 0 / 0 |
| **v4** | save006 | **PASS** | 0 | **2** | 2 | 0 | 8 | 0 | 0 / 0 / 0 |

   v1·v2 `st[258:301]` 전부 0(수리 전 3,592→847·309→1,502 소멸). `cache_fill_465FC0` 33/31/923,648/2/0·`rect_fill_466070_reject_size` 40·`shade_468870_reject_bounds` 841·`layer_move_unsupported` 0은 수리 전과 같다(새 reject·unsupported 급증 0). save000 HOLD 사유는 lap1095 r1·r2와 같은 fixture 한계(input_effect HOLD·V2 BLOCKED, `--scene-actions none`), `terrain_scroll_parity` v1·v2 PASS. save006 v3 stale 293은 ord 350 단발(그 present는 `--stale-mask 100-320` 밖이라 위치 미확인)이고 v4(같은 옵션)에서 재현되지 않았다; 이 장면은 `0x467410` 호출 0이라 이번 수리와 무관(UNKNOWN, 환경/타이밍 일시 stale로 분류, lap1089 td 수준 ≤307 기준 안).

## 판정(work 잠정, middle 검수 전)

- **귀속 PASS, S-3 PASS(partial, 기술)**: save000 2/2 마지막40 47,319→0(기준 ≤2,366)·ord 145~221 0 유지·새 reject/unsupported 급증 0·save006 PASS 2/2(stale 합 295·2 ≤307)·안전 0·p95 7~8ms(고정 +16 이내).
- 절차: lap1096 §3 "미후킹 writer 확인 시 같은 회차 diff 미러" 정정에 따라 같은 회차 수리했다(이탈 아님).
- 한계(공개): (a) stale 지표는 HD 품질 손실 지표이며 두 유닛 실루엣(반투명 효과로 보이는 번쩍임)의 평탄 최근접 확대가 사라지는 효과다. (b) 원본이 화면 밖 사각형을 칠하면 클립 교집합만 미러(원본은 클립 없음, 이 장면은 전부 화면 안). (c) `0x4676D0`·`0x467E60` wrap 등 backlog 불변. (d) save000 `scroll_after` 등 사람 눈 대조·두 번째 장면은 미실행.
- 미실행: 전체 `make check`는 이 기록·ESCALATE_SOL freeze 뒤 1회(결과는 STATUS에만).

## 다음 한 가지

middle(Opus): lap1097 독립 재계산(새 스크립트로 l1·a1·a2·v1~v4 재집계, `0x467410` objdump·훅 코드 검토, 귀속 근거 재확인) → H-D2k-s1 판정. 이어 work 후보: HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 또는 backlog(ord 123 writer 등).

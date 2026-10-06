# 2026-10-05 | lap1024 | G1 work — H-B4: `0x467B00` 클립 반투명 RLE diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승격·폴백 없음.
- 가설: lap1023 middle이 귀속한 save000 표본 B·C stale(미후킹 `0x467B00` 덮어쓰기)을 H-B(`mirror_blend_wrle`) 동형 diff 미러로 없앨 수 있다. A(`wined3d.dll` tid 288)는 범위 밖.
- 예상 PASS / FAIL 조건: lap1023 §5.3 사전등록(B4-0~B4-5) 그대로.
- 변경 파일 / source fingerprint / 커밋: uncommitted. `tools/inmm_stub/g1_mirror2x.c` `0fb12c3b…e152`(+hook `G1_BLEND_CLIP 0x467B00`·old bytes `83 EC 14 33 C0`·`mirror_blend_clip`·계수 9개·install/restore/installed), `g1_mirror2x.h` `c3e80bf5…f18a`(getter 9개), `direct_draw_trace.c` `a6c28fe2…a703`(`blend_467B00_*` 9개 metrics, `mirror_details` 4096→5000), `tests/test_g1_rect_fill.py` `60e2861d…53be`(계약 테스트 1개 신규), `tests/test_g1_panel_layer.py:115`(소스 형태 pin `mirror_details[4096]`→`[5000]` — 제 buffer 확장이 첫 `make check`에서 이 pin을 FAIL시켜 기대값을 맞춤, 기준/golden 아님·첫 check는 중단하고 재실행), 빌드 `_inmm.dll` `5f0edf…3c7d`(로컬 빌드 산출물, 런타임 사본은 bridge `923fd1e1…a8da8f1`이 4 run 공통, dll은 run마다 재링크).
- 원본 SHA / fixture: 원본 EXE `b56986e0…8ac`, save000 `1c703551…19da`(index 1)·save006 `616b7997…a064`, `--hd-source scale2x`. 활성8인 부하 증명 아님.
- 실행 명령: `docs/…/temp/20261005_lap1024_work_hb4/run.sh`(공유 temp) — save000 `--fixture save000 --scene-actions none --performance-window --layer-drift`(screen watch 끔) ×2 → save006 `--stale-mask 6-12,30-34,300-301,585-620,880` ×2, 순차. 로그 `logs/gates/lap1024_hb4_{s0,s6}_r{1,2}.log`(exit 전부 2 = 기존 pair HOLD: save000은 input_effect/V2 BLOCKED(`--scene-actions none`), 하네스 무변경). runtime `local/runtime/lap1024_hb4_*`(game 사본은 하네스가 이미 제거). 분석: `analyze_hb4.py`·`analyze_hb4_s6.py` SHA `1723ab61…9a9`·`9e3c1581…7f60` → `analysis_s0.json` `fd42a8b8…7da5`·`analysis_s6.json` `13bec317…601c`.
- TDD: 계약 테스트 `test_blend_clip_hook_table_and_wrapper_contract` RED(1 failed) → 구현 후 GREEN(9 passed). lint·typecheck PASS.

## 측정값 / 판정

| 판정 | 기준 | r1 | r2 | 결과 |
|---|---|---|---|---|
| B4-0 유효 | 안전 7종 0·cleanup/source_unchanged true·hook 설치·invocations>0·reject_target/guard 0·invocations=mirrored+reject_bounds+reject_size·카메라 (39,53) | inv 14,099 = 2,832+11,211+56·안전 0·cleanup/source true·카메라 (39,53)·tick 50600/50599 | inv 14,150 = 2,838+11,256+56·같음·tick 50601/50599 | **PASS** (reject_target 0·guard 0, reject_size 56 = 0.4% < 10% → before 버퍼 확장 불필요) |
| B4-1 표본 stale present | B 135→≤7·C 210→≤11·A ≤43 | A 41·**B 0**·**C 0** | A 41·**B 0**·**C 0** | **PASS** |
| B4-2 귀속 | `drift_unattributed` B ≤2·C ≤1, `w`에 f `467B00` | A5·B1·C1, w `467B00` clipped 330·mirrored 213 | A5·B1·C1, 같음 | **PASS** |
| B4-3 화면 stale | p84..365 중앙값 ≥50% 감소·마지막40 ≤445 | p84..206 245·p207..365 656·합산 **362.5**(기준 6,215/6,944)·p0..83 656(기준 4,661)·p366.. 414.5·마지막40 **414.5** | 같음(p366.. 399.5·마지막40 414.5) | **PASS**(합산 −94%·전 창 대폭 감소) |
| B4-4 성능 | p95 ≤16 ms·ticks/s 비 ≥0.95 | p95 7 ms·비 1.000003 | p95 7 ms·비 1.000001 | **PASS** |
| B4-5 save006 env-off | 300..620 공통 38프레임 r1∩r2 = 24 px(성분 D)·신규 0·프레임 880 있으면 39프레임 0·p95 ≤16·안전 0 | 기준 3 run 대비 신규 0·제거 0·inter 24(y515..520×x616..619)·p95 7·cov p50 99.30%·안전 0 | 같음(p95 7) | **PASS**: r1∩r2 38프레임 24, **프레임 880이 두 run 모두 있어 39프레임 r1∩r2 = 0**(lap1000 r1 이후 처음 직접 검증) |

- save006 `blend_467B00` 계수(이 장면 호출 여부 공개): r1 inv 58,224·mirrored 84·clipped 23·changed 54·reject_bounds 58,140·size 0·target 0·guard 0; r2 inv 62,214·mirrored 87·clipped 24·changed 55·reject_bounds 62,127. 성분 D는 기준과 동일(H-B 무관).
- 화면 stale p0..83의 4,661도 656으로 줄었다 → lap1023의 "p0..83 미귀속"은 대부분 같은 writer였다. 남은 p0..83 656·p207..365 656·p366.. ~415는 별도 성분(다음 middle이 마스크 없이 trace 기반으로 정체 규명 필요, save000 `--stale-mask` 부재).
- 요약: **H-B4 PASS** — 표본 stale B 135→0·C 210→0, 화면 stale p84..365 −94%, 안전 0, 성능 무영향, save006 비회귀. 한계: `0x467B00`은 목적지 의존 혼합이라 diff 미러가 1x 결과를 확대한다(H-B와 동일 화질 한계, P6 범주). 표본 A(wined3d tid 288) 41 present는 그대로.

## 회귀 / 남은 위험 / 독립 검수
- 제품 변경은 hook 1개 추가(`0x467B00`)·계수·metrics 문자열 버퍼 확장뿐이다. 기존 mirror·gate·기준 줄 변경 0. 원본은 인자를 그대로 받아 자체 클립한다.
- 남은 위험: 부분 화면 밖 호출은 교집합만 미러(clipped 1,991/14,099). 클립 사각형이 화면보다 넓은 경우는 reject_bounds로 감시 — 관측 0 이상 징후. save000 reject_bounds 11,211은 원래 화면 밖/0크기 호출이다.
- 미검증: 사용자 승인(G1 마일스톤 아님), 다른 save/장면, 활성8인 부하. 독립 검수(다음 fresh Opus middle) 대기.
- backlog: A의 `wined3d.dll` tid 288 쓰기 41 present, 남은 화면 stale 성분(p0..83 656·p207..365 656·p366.. ~415), save000 `--stale-mask` 부재, save006 짧은 run 꼬리, 성분 D, hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기 미추적.
- 다음 한 가지: middle H-B4 독립 재계산·수용 후, 남은 화면 stale 성분 귀속(save000 stale 마스크·trace 기반) 또는 A wined3d 쓰기 진단 중 하나를 사전등록.

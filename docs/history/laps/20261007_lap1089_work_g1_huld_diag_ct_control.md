# 2026-10-07 | lap1089 | G1 work — D-0 + H-ULd 진단 동반 c/t 대조 8 run

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 source·하네스·테스트 변경 0, commit 0. work는 자기 결과를 승인하지 않는다.
- 입력: lap1088 middle 사전등록 §4(`20261006_lap1088_middle_g1_hulc_review_huld_preregistration.md`).
- 가설 H-ULd: UL(x0..31·y0..22, ord 122~124 소잔여)은 진단 옵션(`--layer-drift --screen-watch`)이 바꾼 present 시간에서 나는 기존 잔여이며 H-W330과 무관하다.
- 원본 SHA: 8 run × 2 lane 모두 `b56986e018b4…` source_unchanged true. fixture: 비합성 save006.
- 후보/브리지: lap1088 검수 때와 같은 트리(`tools/inmm_stub/g1_mirror2x.c` U-1 bridge, 코드·하네스·테스트 무변경).

## 1. D-0 (선행) — PASS

- 시작 여유 12.43 GiB < 22. lap1087b `archive.py` 복사본(출력 경로 `local/maintenance/20261007_lap1089_prefix_archive/`·run 글롭 `lap10[7-8]*`만 변경, 나머지 byte 동일)으로 lap1071 `t0_a` ~ lap1073 `x2`의 종료 prefix **23개**를 archive(각 tar.zst 전 멤버 sha256 검증)·batch 첫(000)/010/020에서 실제 full restore 후 `prefix`만 삭제. 여유 **12.43 → 22.42 GiB**. `report.json` SHA256 `15dd94f6dcf99b4a7e08cca1a9ae932ce21d93f33b3975c9109c364af4780586`, `restore_verification_000/010/020.json` `full_content_metadata_match` true, exit 0.
- 8 run 도중 다른 소비자 정리로 여유가 26→132 GiB로 늘었다(이 회차 조치 아님).

## 2. 실행 (H-ULd)

- 스크립트 `…/temp/Syw2plus_patch/20261007_lap1089_work_huld/run_h.sh`(SHA 접두 `0e8655ea`) = lap1087 `run_u.sh` 복사에서 run 디렉터리·옵션만 변경. 공통 = d1 옵션 그대로(`--hd-source scale2x --terrain-scroll --terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT --p4b-s-snapshot --reference-completed-states <lap888 REF> --layer-drift --screen-watch --drift-samples "1,1;13,1;20,19" --stale-mask 118-130`), `cd*`만 `--blend-size-reject-diag`. 순차 `cd1 td1 cd2 td2 cd3 td3 cd4 td4`, load ≤ 8 대기, run마다 game 사본 삭제(확인: `local/runtime/lap1089_huld_*/*/*/game` 0개).
- 분석 `analyze_huld.py`(lap1087 `analyze_ulc.py` 복사, 기준 k6·d1·w6) `d1be1ce4…` → `analysis_huld.json` `6731384a…`, 출력 `analysis_out.txt` `edfa652d…`. 모두 `…/20261007_lap1089_work_huld/`.

## 3. 결과

| run | pair | UL px (ord) | hold 합 | reject 580/B00 | 수리 전 ord 합 | 위상 cur/cam/skip | p95 hold/고정 | 안전 | 메모 |
|---|---|---|---|---|---|---|---|---|---|
| cd1 `9fb0e687` | PASS | **72** (123:23, 124:49) | 240,775 | 21/89 | 240,701 | 123/123/True | 11/11 | 0 | 충실도 OK |
| td1 `b57bcfb2` | PASS | **72** (123:23, 124:49) | 74 | 0/0 | 0 | 123/123/True | 11/12 | 0 | |
| cd2 `8031318e` | PASS | **62** (124:62) | 240,765 | 21/89 | 240,701 | 124/123/True | 12/10 | 0 | 충실도 OK |
| td2 `7698547b` | PASS | **72** (123:23, 124:49) | 74 | 0/0 | 0 | 123/123/True | 11/12 | 0 | |
| cd3 `6ea10e12` | **HOLD** | 0 | 240,463 | 21/**87** | **230,565** | 123/123/True | 11/11 | 0 | **충실도 FAIL**·candidate lane UPLEFT 관측 24(baseline 25) → camera 궤적 어긋남(same_camera_after_each_key false) |
| td3 `5982455c` | PASS | **72** (123:23, 124:49) | 307 | 0/0 | 0 | 123/123/True | 12/11 | 0 | hold 밖 ord 219 233 |
| cd4 `a2f37312` | PASS | **62** (124:62) | 240,765 | 21/89 | 240,701 | 124/123/True | 11/11 | 0 | 충실도 OK |
| td4 `bc8f8848` | **HOLD** | **72** (123:23, 124:49) | 74 | 0/0 | 0 | 123/123/True | 11/12 | 0 | candidate lane DOWNRIGHT 관측 24(baseline 25) → camera 궤적 어긋남 |

- 충실도(cd run): cd1·cd2·cd4 = reject 21/89·수리 전 ord 합 240,701 = k6/k1 열 → **성립**. **cd3 = 87·230,565로 불성립**(같은 이유로 pair gate HOLD/FAIL: input_effect·minimap·terrain_scroll·v2·v2q). td4도 같은 종류(candidate lane 관측 칸 수 24≠25)로 pair HOLD. 둘 다 이 회차 코드 변경 없음 — 기존 backlog "lane 위상 경합(키 유지 관측 한 칸 어긋남)"과 같은 증상으로 보이나 원인 확정은 안 했다(UNKNOWN).
- UL 상자·모양: td/cd 모두 ord 123의 (x5..15·y0..4, 23 px) = d1·w6과 같은 상자, ord 124의 (x6..25·y13..21, 49 px) 또는 (x6..26·y13..22, 62 px) = w2와 같은 상자. **수리 OFF(cd)와 ON(td)에서 같은 상자가 나온다.**
- 진단 동반 표본 watch: 모든 run `0x46624F`(미후킹 `0x466130`) 68~71회·`0x4662DE` 3.5~4.6k·`0x467CCF` 14 (d1과 같은 분포).
- 진단 동반 UL 집계(전 lap): 수리 후 8/8(w6·w8·w9·d1·td1~td4)·수리 전/대조 UL>0 **3/3 유효 cd + k6 0/1(진단 동반 위상 skip 없음)**. skip=True인 진단 run 8/8, skip=False인 진단 run(k6·d1·w6) 중 UL: k6 0·d1 23·w6 23.

## 4. 판정 (사전등록 §4 적용, work는 확정하지 않음)

- 충실도: cd1·cd2·cd4 성립(3/4). cd3 불성립 → 사전등록 문구대로면 "그 cd run 대조 무효"이므로 **cd3은 판정에서 제외**한다(유효 cd 3개, 모두 UL>0). 4 cd 전체 무효로 읽는 해석(BLOCKED)은 middle이 판단한다.
- (a) 충족: 유효 cd 3/3에서 UL > 0(72·62·62). → **UL은 H-W330과 무관**(수리 OFF에서도 같은 상자 발생). 따라서 사전등록상 **H-W330 PASS(partial) 확정·UL → backlog H-UL(writer 1순위 후보 미후킹 `0x466130`, 미입증)**이 work가 제안하는 판정이다. 수용은 fresh middle의 독립 재계산 뒤.
- 공통 FAIL 조건: 안전 위반 0·크래시 0·성능 초과 0(진단 run hold p95 ≤ 고정+16, 최대 12). cd3·td4의 pair HOLD는 candidate lane camera 관측 칸 수 차이(위상 경합)이며 UL 측정 자체에는 영향 없음(td4 UL 72 정상 관측).
- 미검증/정정: UL이 "진단 부하가 만든 위상 skip(8/8) 때문"인지, "진단과 무관한 기존 잔여"인지는 이번 실험이 가르지 않는다(진단 없는 cd 대조는 이번 설계 밖). UL writer 귀속은 UNKNOWN. UL을 H-UL backlog로 옮기는 근거는 "H-W330 ON/OFF 동일"이다.

## 5. 검사

- 코드·하네스·테스트 무변경이라 `make check`는 SKIP(lap1087 full PASS 1668·lap1088 focused PASS 유지). 이 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`만 돌린다(결과는 STATUS 보강 줄).

## 다음 한 가지

middle(Opus)이 `loop/ESCALATE_SOL`의 목록대로 8 run을 새 스크립트로 독립 재계산하고 (a) 판정·cd3 제외 해석·H-W330 PASS(partial) 확정 여부를 결정한다. 그다음 G1 작업(save000 맵 경계 stale 귀속 H-D2k-s0 또는 HUD/GDI·전체 HD coverage·사용자 승인 준비)은 middle이 사전등록한다.

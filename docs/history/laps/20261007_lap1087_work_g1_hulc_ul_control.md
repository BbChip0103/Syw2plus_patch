# 2026-10-07 | lap1087 | G1 work — D-0 디스크 회수 + H-ULc (좌상단 소잔여 수리 전 동작 대조)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 자기 결과를 승인하지 않는다. 독립 검수·판정은 `loop/ESCALATE_SOL`로 middle(Opus)에 인계.
- 가설: lap1086 사전등록 H-ULc — UL 소잔여(ord 122~124, x0..31·y0..22)는 H-W330과 무관하며 커서 (0,0) 첫 present와 카메라 이동·sim tick 위상이 어긋날 때 나는 기존 잔여다.
- 예상 PASS / FAIL: lap1086 §5(U-0 충실도: c run마다 reject 21/89·ord 126~133·140~145·221~225 stale 열이 k1과 같음; U-1: (a) c 1 run 이상 UL>0 → PASS(partial) 확정, (b) c 5/5 UL 0이고 t ≥3/5 UL>0 → HOLD 유지, (c) 그 밖 INCONCLUSIVE).
- 변경 파일(uncommitted): `tools/inmm_stub/g1_mirror2x.c` `d66a3afd…`(진단 env `SYW2_G1_BLEND_SIZE_REJECT_DIAG`, 기본 off), `tools/g1_saved_scene_probe.py` `77d4ec09…`(`--blend-size-reject-diag`, candidate 전용), `tests/test_g1_mirror2x.py` `bc97ce63…`(+1 테스트). 기본 동작·계수 이름·헤더·bridge 불변.
- 원본 SHA / fixture: 원본 EXE `b56986e0…08a8ac` MATCH(모든 run `source_unchanged` true). 비합성 save006(`--p4b-s-snapshot`), scale2x HD, UPLEFT,DOWNRIGHT edge scroll(= k1/w1 옵션), `--stale-mask 118-130`, load ≤ 8. 활성 인원은 G1 save006 기준(G2 8인 증거 아님).

## D-0 디스크 회수 (게임 실행 전)

- 시작 여유 7.0 GiB. `local/maintenance/20261007_lap1085_prefix_archive/archive.py`를 새 디렉터리로 **복사**(출력 경로 한 줄만 변경, 원본 불변)해 같은 절차를 두 번 실행: `20261007_lap1087_prefix_archive`(목표 22, 경계 `lap1080`, 33 prefix, 여유 7.01→22.48 GiB, `report.json` `0197714c…`·`plan.json` `0291002a…`·`archive.py` `9c699214…`, `restore_verification_000/010/020/030` 4/4 `full_content_metadata_match` true), `20261007_lap1087b_prefix_archive`(목표 27.5, 11 prefix, 22.48→27.52 GiB, `report.json` `5caaf617…`·`plan.json` `a5e64aff…`·`archive.py` `a2a546bc…`, restore 2/2 true). 합계 44 prefix(`lap1058_d2z`~`lap1069_s3_d2`), 전부 `removed_private_prefix_only` true, prefix마다 pair-result `source_unchanged`·`cleanup.ok`·prefix 프로세스 0·`game_removed`·tar 전 멤버 SHA/mode/symlink 대조 뒤에만 `prefix` 삭제. manifest·output·로그 보존, `game` 사본은 run마다 삭제.
- **PASS.** 종료 시 여유 13 GiB(run 11개가 prefix 약 1.3 GiB씩 남김). 다음 work가 게임을 돌리려면 D-0를 다시 해야 한다(다음 대상 = `lap1069_s3_nd1` 이후, lap1081·1083·1085·1087 prefix).

## U-0 구현 (테스트 먼저 RED→GREEN)

- `test_ulc_blend_size_reject_diag_is_opt_in_env_and_candidate_only_flag` 추가 → RED(`SYW2_G1_BLEND_SIZE_REJECT_DIAG` 없음) → 구현 → GREEN. 단언: env 매크로·`g_blend_size_reject_diag` 기본 FALSE·`initialize_environment()`가 `value[0]=='1'`일 때만 on·헬퍼 `blend_size_reject_diag(width, height, check_height)`(폭 > 320, `wrle`만 높이 > 160 추가)·두 wrapper에서 bounds 검사 뒤·before 복사 앞 1회 호출·원본 1회 호출·`apply_tiled` 1회·reject는 `+= 1u`(기존 `++g_*_reject_size` 1회 단언 불변)·하네스 `--blend-size-reject-diag`가 candidate env에만 전달되고 `--hd-source scale2x`를 요구.
- 기존 H-W330 계약 단언 **불변**(`_assert_tiled_blend_wrapper`의 `G1_OVERLAY_MAX_*` 본문 부재·reject 증가 1회 단언은 헬퍼 분리·`+= 1u`로 유지). focused 4파일 `.venv/bin/python` **289 passed**(288+1), `i686-w64-mingw32-gcc -Wall -Wextra -c g1_mirror2x.c` 경고 0, `make lint`·`make typecheck` PASS.
- off 경로 = 수리 후 동작(헬퍼가 FALSE 반환, 분기 미진입). on = lap1083 크기 reject(`active` FALSE라 원본만 실행, 미러 없음). 대조 전용이며 기본 동작을 바꾸지 않는다.

## U-1 실행 (순차, c/t 교대, 같은 옵션, 시작 load 2.74~5.37(≤ 8), run마다 game 사본 삭제)

실행 스크립트 `…/20261007_lap1087_work_ulc/run_u.sh` `35478138…`(w 스크립트 복사·run 이름/옵션만 변경), 로그 `logs/gates/lap1087_ulc_{c1..c5,t1..t5,d1}.log`(전부 exit 0). 분석 `analyze_ulc.py` `c58e2fb4…` → `analysis_ulc.json` `715b7b70…`·`analysis_out.txt` `41eb881e…`. 공유 temp: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1087_work_ulc/`.

| run | pair SHA12 | reject 467580/467B00 | hold 합 | UL 합 | hold 밖 이상 | 첫 커서(0,0) present / 카메라 첫 이동 / tick 건너뜀(ord121~126) | hold p95 / 고정 p95 |
|---|---|---|---|---|---|---|---|
| c1 `ec3b155c8e60` | | 21/89 | 240,703 | 0 | 총합 532,085(ord 0~15 load 과도 포함) | 124 / 123 / 없음 | 7 / 7 |
| t1 `f60a5b320879` | | 0/0 | 2 | 0 | 총합 2 | 124 / 123 / 없음 | 7 / 6 |
| c2 `b7df85ca074a` | | 21/89 | 240,703 | 0 | 532,085 | 123 / 123 / 없음 | 7 / 7 |
| t2 `b609ca464d48` | | 0/0 | 2 | 0 | 2 | 123 / 123 / 없음 | 7 / 7 |
| c3 `32d6b4d0ec33` | | 21/89 | 240,703 | 0 | 532,085 | 123 / 123 / 없음 | 7 / 7 |
| t3 `24ff8cf17982` | | 0/0 | 2 | 0 | 2 | 124 / 123 / 없음 | 7 / 7 |
| c4 `506fcdfe0d09` | | 21/89 | 240,703 | 0 | 532,085 | 123 / 123 / 없음 | 7 / 7 |
| t4 `ab733f9c091c` | | 0/0 | 2 | 0 | 총합 314(ord 353 257·377 55) | 123 / 123 / 없음 | 7 / 7 |
| c5 `e9e792c6f783` | | 21/89 | 240,703 | 0 | 532,085 | 124 / 123 / 없음 | 7 / 7 |
| t5 `64c5e28dd272` | | 0/0 | 2 | 0 | 2 | 124 / 123 / 없음 | 7 / 7 |
| d1 `fcf3ced658bc`(t + `--layer-drift --screen-watch --drift-samples "1,1;13,1;20,19"`) | | 0/0 | 575 | **23**(ord 123, x5..15·y0..4) | ord 219 233·ord 243 317(진단 동반 영역) | **122** / 123 / 없음 | 11 / 12 |

- **U-0 충실도 PASS(5/5):** c1~c5 `blend_467580_reject_size` 21·`blend_467B00_reject_size` 89(= k1/k2), hold stale 열 ord 126~133·140~145·221~225가 k1과 **값까지 동일**(hold 합 240,703·pre-repair ord 합 240,701·ord 137 2 px, 총합 532,085도 k1과 같다), 고정 구간 load 과도(c1 ord 0~15 ≈ 291k)도 수리 전과 같다. 즉 스위치 on = lap1083 동작이 stale 열까지 재현된다.
- 공통: E-0 모든 run UPLEFT (−2,0)×24·DOWNRIGHT (+2,0)×24 왕복(두 lane 같음), E-1 hold p95 7(진단 11)·고정 6~7(진단 12)·tps 19.998~20.026, 안전 7종 최대 0, 11 run × 2 lane `cleanup.ok`·`game_removed`·`source_unchanged` true, mask SHA = pair-result 기재 값·mask와 trace `stale_pixels` 불일치 0, 마지막40 0.
- t4 hold 밖 ord 353 257 px·377 55 px는 lap1084 k3 ord 353 257·lap1086 w1 ord 352 257과 같은 종류의 일시 사건(비차단 관찰, c run에는 없음·표본 1/10).

## 판정 (사전등록)

- **UL(ord 122~124, x0..31·y0..22) c 0/5·t 0/5·모든 run 위상이 "깨끗"** 이었다(커서 (0,0) 첫 present가 카메라 첫 이동(ord 123) 직전·같은 present이고 tick 건너뜀 없음 — 10/10). 사전등록 (a) c 1 run 이상 UL>0 **불충족**, (b) t ≥3/5 UL>0 **불충족** → **(c) INCONCLUSIVE.** H-W330 PASS(partial)을 확정하지도, 부작용 의심으로 되돌리지도 않는다. 같은 대조를 반복 연장하지 않는다(규칙).
- **새 근거(귀속 UNKNOWN 유지):** UL은 위상이 깨끗하지 않은 run에서만 나왔다. 수리 후 UL 발생 5건(w2·w6·w8·w9·**d1**)은 모두 비깨끗 위상(w2·w9 tick 건너뜀, w6·w8·**d1** 커서가 카메라보다 앞)이고, 수리 후 깨끗한 위상 7 UPLEFT run(w1·w7·t1~t5)은 UL 0이다. 수리 전/대조 상태 UPLEFT 8 run(k1·k2·k6·c1~c5)은 **전부 깨끗한 위상**이라 비깨끗 위상 표본이 0이다 — 그래서 수리 전 동작에서 UL이 나는지 이 대조로는 판정할 수 없다.
- d1(t + 진단)은 w6과 같은 상자(ord 123, x5..15·y0..4, 23 px)를 재현했고 커서가 ord 122에서 먼저 (0,0)에 도달한 같은 위상이다. 표본 (13,1)이 그 상자 안이어서 writer를 잡았다: p123 stale 표본 1개(scr 66, snap 0), 쓰기 열 `0x46624F`→`0x4662DE`(val 66 = scr, tid 280). `0x4662DE`는 lap974 census의 block_copy `0x466280`(기존 지형 캐시 복사 hook) 안이다. 이 present에 `467B00`/`467580` 호출 기록은 없고(sample-filtered drift의 w 기록은 p124 (−88,−190,330,200)부터) 330×200 호출과 무관해 보인다. 왜 그 복사가 snapshot(0)을 갱신하지 못했는지는 **UNKNOWN**이다.
- 안전 위반·크래시·성능 초과 0. 변경은 uncommitted(진단 스위치는 대조 전용, 기본 off).

## 남은 위험 / 다음 후보 (middle 판단)

- 판정(c)이므로 UL은 H-W330과 무관이라는 직접 근거도 부작용 근거도 없다. 반대 근거(코드 동치 lap1086 §1·UL이 비깨끗 위상에서만 발생·d1 writer가 `0x4662DE`)가 우세하다. 결정 선택지: (1) 비깨끗 위상을 강제하는 대조 — **진단 동반 비깨끗 위상**(`--layer-drift --screen-watch`가 커서를 ord 122로 앞당긴 w6·w8·d1)에서 c(스위치 on)를 같은 진단과 함께 3 run, t 3 run 비교(진단 옵션 동일), 또는 `candidate_throttle` 같은 하네스 위상 교란; (2) UL을 H-UL backlog(비깨끗 위상 잔여, writer `0x4662DE` block_copy 미갱신)로 옮기고 H-W330 PASS(partial)을 "핵심 효과 + UL 별도 backlog"로 수용(기준 완화이므로 middle/사용자 판단 필요). work는 어느 쪽도 임의로 고르지 않았다.
- backlog 유지: ord 137 (799,408..409) 2 px, ord 352/353 257 px 일시 사건(t4 표본 추가), throttle 전용 ord 123 writer, `0x467E60` wrap 계수, lane 위상 경합, save000 UPLEFT 맵 경계 stale ≈189k 귀속(H-D2k-s0).
- 제품 G1 마감이나 사용자 승인이 아니다.

## 검사

- 기록 freeze 뒤 `make check`(lint·typecheck 선행 PASS)를 1회 돌리고 결과는 STATUS에만 보강한다.

## 다음 한 가지

middle(Opus): `loop/ESCALATE_SOL`의 재계산 후 (c) INCONCLUSIVE 수용 여부와 위 선택지 (1)/(2) 사전등록. 게임 실행 전 D-0 재실행 필요(여유 13 GiB).

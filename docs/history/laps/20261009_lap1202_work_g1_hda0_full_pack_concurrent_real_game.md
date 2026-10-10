# 2026-10-09 | lap 1202 | G1 work — H-HDA0: 전체 팩 동시 실게임 확인 1회

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1201 middle 사전등록 §5(`20261009_lap1201_middle_g1_hdb5_review_effect_closure_hda0_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 러너 값 `loop/.lap_counter` = 1202.
- 가설: 현재 도구(`g1_hd_convert` 확장 이름 규약)로 imjin2 팩을 다시 만들고 효과·로고·타이틀 계열을 한 팩 디렉터리에 합쳐도, 엔진은 충돌 이름에 기본 이름 파일 없이 확장 이름으로만 hit하며 개별 갈래 합격 수치(안전 0·자기 검사 불일치 0·reject 0·p95)를 그대로 유지한다.
- 예상 PASS/FAIL (사전등록 §5): A-0 (a) 도구 `check` 위반 0 (b) 충돌 이름에 기본 이름 파일 0·`.amb`·확장 이름 존재 (c) 합치기 충돌 목록·규칙 공개 / A-1 안전 7종 0·크래시 0·자기 검사 불일치 0·`hd_pack_*_rejects` 증가 없음·`ext_hits`>0·충돌 이름 기본 이름 hit 0·p95 ≤ 개별 최대+2·cache ≤128 MiB·trace overflow 0·pair 기존 판정 동일·fullscreen hit = present.
- 환경 / fixture: 격리 Wine·Xvfb 1600×1200, 하네스 `tools/g1_saved_scene_probe.py --hd-source scale2x`. NG5 = `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`(활성 8 player records, 부하 증명 아님, 새 임의 게임), pair = 기본 save006. 팩·키 로그만 바깥 env(`SYW2_G1_HD_PACK`·`SYW2_G1_HD_KEY_LOG`), 끔 스위치 없음(전부 기본 켬). 산출물 공유 temp `20261009_lap1202_work_hda0/`.

## 변경

제품 코드·테스트·도구 변경 **0**(`git status`의 기존 uncommitted 37개 외 새 변경 없음). 한 일은 (1) `tools/inmm_stub/make`로 `_inmm.dll`을 현재 소스에서 다시 빌드(이전 DLL `ef21d7bb…`은 04:57, `direct_draw_trace.c`는 06:06 lap1200 변경 → 낡음) = **`7b1c2203ca285473…`**(gitignore 대상 산출물, run 2개가 이 DLL: `dll_sha_run.txt`), (2) 오프라인 팩 구성, (3) 실게임 run 2개.

## A-0 팩 재생성(오프라인)

도구 순서(원본 읽기 전용, `source_unchanged` true): `g1_hd_extract extract --image-dirs char,tile,fnt`(3,374 파일·43,622 프레임: rle 2,763·ytl 425·raw 152·bmp 27·unsupported 7) → 원본 `imjin2.pal`×4 가장자리 복제 + 바이큐빅 2배(`bicubic_edge.py` = lap1167·1169 것, **시스템 `python3`로 실행** — `.venv`에 scipy 없음; 첫 시도는 이 이유로 bicubic 단계에서 실패해 `python3`로 바꿔 재실행) → `convert`(43,622/43,622, 오류 0) → `pack --pal …/pal/imjin2.pal --ref ref --hd-dir hd --image-dirs char,tile,fnt`.

- **(a) PASS:** 도구 `check` 위반 0(43,622 ok, 7종 위반 합 0, `check.json`).
- 팩 보고: pack_files 25,634(= lap1169 `pack_c`와 같은 수), unique_names 26,294, `ytl_frames` 16,655(`ytl_narrow` 828), `nonconforming` 0, **확장 이름 657개/4,398 프레임/3,661 파일**(길이 분포 160~12173), 남은 충돌 3개 `h150e1aec`·`h2b9b3809`·`h2f6cbf38`(`86×60`, 106 프레임, `char/bullk*` — 사전등록과 같음).
- 합치기: 기본 = 위 `pack_base/cecc4681`(하드링크), **효과** `pack_hdb4/cecc4681`(lap1198, 410 idx8 + 2 `.amb`)·**로고** `pack_logo/cecc4681`(lap1188, 1 idx8) 덮어쓰기, **타이틀 계열** `296963d9`·`84428eed`·`e24d0e6d`는 `pack_hdf1`에서 하드링크. **(c) 공개 — 같은 경로 다른 바이트 충돌 403개**(`merge_log.json`; 전부 효과 팩: `pack_base`도 `char`·`fnt` 전체를 변환하므로 효과 `fnt/*`·`char/cannon2c*` 이름이 이미 있었고 stand-in 방식(`draft` vs 가장자리 복제 바이큐빅)이 달라 바이트가 다름; 같은 바이트 9개). **선택 규칙: 효과 팩(lap1194·1198에서 키 경로를 검증한 초안)이 기본 팩을 이긴다.** 로고는 신규 1개(`h3475a863_100x64.idx8`). 충돌 파일은 하드링크를 끊고(unlink 후 복사) 기본 팩 원본은 그대로.
- **(b) PASS:** `.amb` 657개 전부 마커 값 129..65536, 확장 이름 파일 존재, 해당 stem의 **기본 이름 `.idx8` 0개**. lap1192 N-4 dry-run의 확장 이름 674개 중 657개가 이 범위(`char`·`tile`·`fnt`)에 있고(기본 이름 파일 0), 나머지 17개는 `BattleSpr/*`·`yfnt/buttons201.spr`(이 팩 범위 밖 폴더, 팩에 없음). 남은 3 충돌 공개.
- 합본 `pack_all/`: **29,957 파일**(`cecc4681` 29,954 = idx8 29,296·`.amb` 657·`digest_index.json` 1 / 타이틀 계열 3디렉터리 각 1), 약 1.6 GiB 겉보기 1.5G, manifest `pack_all.manifest.sha256`(SHA256 앞 16자 `2440260fa3c05757`). `digest_index.json`은 `pack_base` 것이라 효과 덮어쓰기를 반영하지 않는다(엔진은 읽지 않음, 사실 공개).
- 중간물: `rgb`(726M)·`hd`(270M)·`ref` 프레임(603M→22M, `ref/manifest.json` 유지) 삭제 후 SHA 기록(`intermediates.sha`: manifest `4f65df5d…`·convert.log `3e5e178c…`·check.json `6526def9…`·pack.log `09e5ad3e…`). `pack_all`·`pack_base` 보존.

## A-1 실게임(켬, 같은 DLL·팩 `pack_all`)

| run | 결과 |
|---|---|
| **A1** NG5 장기 스크롤 | probe exit 0·`status PASS`·`source_unchanged` true·PS3 6,031 present·302 s·`hd_min` 100.0(window select 4·produce 37·drag_move 22·dwell 1,199)·scale2x validator PASS·`hd_mask_outside_diff` 0·mirror validator BLOCKED(기존 하네스 lap1171 이래 동일) |
| **PA** save006 pair | exit 0·`status PASS`·`scene_state_equal` true |

원본 EXE SHA `b56986e0…08a8ac` run 전(`orig_sha_before2.txt`)·후(`orig_sha_after.txt`) MATCH, `game` 사본은 하네스가 종료 때 삭제(`local/runtime/lap1202_hda0_*`의 prefix·manifest·output 보존).

**A1 측정(`metrics_A1.json` `e13a042c…`·`w_metrics.py`):**
- 안전 7종(`fallback`·`hresult`·`identity_invalid_sources`·`scale2x_palette_violations`·`identity_key_mismatches`·`viewport_restore_failures`·`clip_replay_mismatches`) 전부 **0**, 크래시 0, `trace_dropped` 0(overflow 0).
- 자기 검사 불일치 **0** — blend 6 writer 전부(`0x467B00` keyed 310/310·`0x467580` 216/216·`0x4672E0` 6,031/6,031·`0x4685C0` 685/685(flip)·`0x467FD0` 1,592/1,592(flip, `key_wrap_mismatches` 0)·`0x4678C0`/`0x468360` 호출 0), 음영 selfcheck 570,448 px 불일치 0(`shade_reject_*` 전부 0), tinted `lut_rejects` 0.
- reject: `hd_pack_rejects` **0**·blend rejects 0·shade rejects 0·lut rejects 0·`ext_rejects` **0**·`ext_misses` **0**(개별 갈래 run 대비 증가 없음). 키 로그 `reject` 줄 0.
- 팩 hit: 키 1,303개 중 hit 367·shade_hit 560·lut_hit 338·miss 38. 지형 matched hit 100%·tinted 100%·음영 100%·ab 93.5%(lap1178 F1 77.4%보다 높음). **`hd_pack_ext_hits` 137 > 0** — 키 로그 분류: 마커 stem 키 137개(hit 43·lut_hit 5·shade_hit 89)가 전부 hit, **마커 stem이 기본 이름 파일로 hit한 건 0**(기본 이름 파일 자체가 0개). miss 38 = 팩에 없는 이름 32(범위 밖 `BattleSpr`·비-ytl 타일 등) + 기본 이름 파일은 있으나 miss 6(`0x466D50` 32×32 키 6개 — **lap1176 이후 모든 run(개별 갈래 포함)에서 동일하게 miss**: 새 회귀 아님, 원인 미조사).
- 성능: PS3 p95 **6**(window별 최대 7), 개별 갈래 최대(lap1198 7·lap1196 6) +2 이내. cache 33.1 MB ≪ 128 MiB(축출 없음, `identity_cache_inserts` 1,303).
- stale: PS3 stale present 1개 — 225.5 s에 79 px(lap1187·1192 X1 backlog "클립 반전 가장자리 등장 1 present stale 79/92 쌍봉", 경로 무관) 외 0.
- **fullscreen hit = present:** PS9 70/70·PS7 161/161·PS5 724/724(합 955 = `hd_pack_fullscreen_hits`, misses 0·rejects 0·loads 3), `hd_pack_pal_misses` 0.

**PA 측정(pair-result.json `60ee0956…`):** 상태 leaf 200개 중 lap1196 pair PD 대비 차이 **1개** — `capture_visual_comparisons.production.v2s_raw_status`가 PD `FAIL` → PA `PASS`(raw V2s는 공개 진단, W-1 gate 아님; 좋은 방향의 차이이고 원인은 조사하지 않았다). 나머지 199개 동일(`trace_close` FAIL·`mirror_validator` BLOCKED = lap1189 backlog 기존 하네스, `owner0_hq_type` UNKNOWN 기존). 키 로그 `pair_PA.keys.jsonl`: hit 237·shade_hit 97·lut_hit 494+38·miss 15(범위 밖 13 + `0x466D50` 기본 이름 miss 2), reject 0, 마커 stem hit 67(기본 이름 hit 0).

## 판정

**H-HDA0 `PASS(partial, 기술·격리)` 후보**(middle 검수 전). A-0 (a)(b)(c) 충족, A-1 합격 조건 전부 충족(안전 0·불일치 0·reject 0·ext_hits 137>0·기본 이름 hit 0·p95 6≤9·cache 33 MB·overflow 0·pair 판정 동일·fullscreen hit = present). 이로써 HD 그림 경로 도구와 엔진은 "사용자 업스케일러 결과를 받을 준비"가 됐다는 기술 근거가 생긴다(stand-in 팩, 사용자에게 보이는 화질 이득 없음). 마일스톤 경계(사용자 시험판 재스테이징·업스케일러 실험 요청 여부)는 middle이 root 전달로 판단한다.

## 한계·공개

1. 팩 그림은 바이큐빅 stand-in(효과는 `draft`)이며 화질 평가가 아니다. 서로 다른 색의 HD로 육안 비교한 run 없음.
2. 단일 NG5 run 1개·pair 1개. 기본 켬·사용자 전달 아님. `0x467410`·`0x467E60`은 명시 잔여.
3. `digest_index.json`은 효과 덮어쓰기 전 상태. 남은 충돌 3개(`char/bullk*`)는 Scale2x.
4. `0x466D50` 32×32 miss 6개는 오랜 기존 현상(원인 미조사, backlog). v2s_raw PASS 1건 차이 원인 미조사.
5. `bicubic_edge.py`는 시스템 `python3`(scipy) 필요, `.venv` 불가 — 재현 시 유의.
6. 첫 `a0_extract.sh` 래퍼는 `.venv`로 bicubic을 호출해 실패(설정 결함, 제품 아님); 같은 입력으로 재실행했고 결과에 영향 없음.
7. **디스크:** 시작 11 GB → 끝 **6.8 GB**(`pack_all` 1.6G + run prefix 2개 + 중간물 정리 후). 사전등록 기준 8 GB 미만 → 이 기록 시점에 root 대상 ESCALATE_SOL로 확보 요청한다. 대량 삭제는 하지 않았다.

## 다음 행동

middle(Opus)이 H-HDA0을 독립 검수(`pack_all` manifest 재계산·`.amb`/확장 이름 짝·키 로그 재분류·pair 200 leaf 대조)하고, 사용자 시험판 재스테이징/업스케일러 실험 요청 여부(마일스톤 경계, root 전달)와 디스크 확보(root 대상)를 판단한다. 사용자 G1 시험 결과가 오면 최우선.

# 2026-10-08 | lap1171 | G1 work — H-HDS1 ④-4 음영 지형(`0x468CC0`·`0x4690A0`) HD 팩

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). 커밋 0.
- 입력: lap1170 middle 사전등록 §8(`20261008_lap1170_middle_g1_hdc1_review_hds1_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 9.6 GB(<20 GB, 이 회차 옛 사본 없음 → 실행 1회분 prefix 1.2 GB씩만 쓰는 순차 3회, 종료 7.1 GB; 다른 회차 산출물·원본 삭제 0, game 사본은 하네스가 실행 직후 삭제).
- 가설: 음영 지형 writer 출력 = `F(c,s) = inv[T[R(c)][s], T[G(c)][s], T[B(c)][s]]`(renderer `+0x419A0` 팔레트·`+0x6BCA0` 음영표·`+0x19A0` 역표), source = `.ytl` 프레임 row RLE, aux = w×h 음영 바이트. 키 생성 때 aux·source를 복사하고, 팩 프레임(원본 인덱스)에 1x 칸 음영 `s`로 `LUT_s[]`를 적용하면 원본 음영을 유지한 HD 지형이 나온다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…` 전후 MATCH(`orig_sha_before/after.txt`). 환경: 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --new-game-path --new-game-start --new-game-act --hd-source scale2x`(lap1161~1169와 같은 NG5), 팩 = lap1169 `pack_c` 그대로(25,634파일, 새 팩 0), 활성 8 player records(부하 증명 아님), 새 임의 게임. 산출물 공유 temp `20261008_lap1171_work_hds1/`.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_hd_asset.c` | 음영 지형 경로: writer ∈ {`0x468CC0`,`0x4690A0`}이고 팩 env 있고 `SYW2_G1_HD_PACK_SHADE≠0`일 때 키 생성(`begin_with_aux`)에서 `capture_shade` — aux w×h 복사(FNV-1a == `auxiliary_digest`) + row RLE source 구조 검사·복사(skip+count ≤ w, 읽기 가능). `build_hd_frame`이 `read_pack_frame` HIT 직후 첫 시도 때 `shade_prepare`: ① renderer 표 읽기 가능 검사(팔레트 768 B·음영표 8 KB·역표 262,144 B) ② 쓰인 `s`(≥64면 range reject)마다 256 B `LUT_s[c]` 생성(팔레트 성분·T 값 ≥64면 range reject) ③ **자기 검사**: RLE를 원본 writer와 똑같이 풀어 identity가 쓴 모든 1x 화소에서 `LUT_s[c] == identity`(1개라도 불일치 → `shade_reject`, 첫 좌표 키 로그). 통과 키만 `shade_apply`(`hd[i] = LUT_{s(x/2,y/2)}[hd[i]]`, 키 색 화소 제외). 그 밖 aux writer(checker `0x468E10`)·끔 env → `skip_aux`, 팩 env 없으면 무변화. 새 상태 `PACK_SHADE_REJECT`(Scale2x 폴백)·사유 5종(aux·table·range·source·selfcheck). 키 로그 result `shade_hit`(`slots`·`selfcheck`)/`shade_reject`(`reason`·`mismatches`·`first_xy`). `G1_HD_RENDERER_BASE` 매크로로 호스트 테스트가 가짜 renderer를 주입 |
| `tools/inmm_stub/g1_hd_asset.h` | 카운터 접근자 7개(`pack_shade_hits`·`_rejects`·`_rejects_by_reason`·`_selfcheck_pixels`·`_multi_keys`·`_key_color`·`_lut_bytes`) |
| `tools/inmm_stub/direct_draw_trace.c` | trace `hd_pack_shade_*` 11필드(`mirror_pack_details` 360→760) |
| `tests/test_g1_hd_pack.py` | 호스트 로더 테스트 +5(가짜 renderer 표로 `F` byte 정확·1x 칸 음영의 2×2 적용 위치·두 writer, 자기 검사 불일치·digest·source·`s`·팔레트 범위 reject 사유, 끔 env·checker·파일 없음, trace 필드). 기존 `shade_writer` 시나리오는 이제 음영 writer가 팩 대상이므로 checker `0x468E10`으로 바꿨다. 변이 확인: `shade_apply`의 LUT 적용 줄을 지우면 1개 FAIL, 자기 검사 return을 지우면 1개 FAIL, 복원 뒤 20 PASS |

도구·하네스·팩 변경 0(하네스는 key-log 지표용 공유 temp 스크립트 `metrics_c.py`만 확장).

## 측정

- **H-0(정적, lap1170 `h4_468CC0.txt`·`h4_4690A0.txt` 재확인):** 행 형식 `<skip, count, count 화소>`, 화소마다 `c=src`, `s = shade[y·w + skip + i]`(shade 포인터는 행마다 +w), `R=pal[3c]`(`+0x419A0`), `R'=T[(R<<6)+s]`(int16 `+0x6BCA0`), 역표 인덱스 `(R'<<12)+(G'<<6)+B'`(`+0x19A0`), 목적지 읽기 없음. 클립판(`0x4690A0`)은 같은 식에 viewport 클립만 추가 → identity(전체 viewport 재호출)로 같은 자기 검사 적용 가능. 사전등록과 같다.
- **S-0(오프라인, `s0.json`):** lap1169 H1·H2 키 로그의 음영 aux 키 이름 → `pack_c` 대응 58/64=**90.6%**·56/62=**90.3%**(`0x468CC0` 93.8%·`0x4690A0` 86.7~87.5%). **`FEASIBLE`(≥80%).**
- **S-1 NG5(전부 크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator PASS·`hd_mask_outside_diff` 0·`identity_invalid_sources` 0):**

| run | 음영 | PS3 HD min | p95 | pack hits/miss/rej/skip | shade hits/rejects | selfcheck 화소 | multi 키 | LUT bytes | 음영 matched hit (`0x468CC0`/`0x4690A0`) | tinted | A/B·지형 | `lut_rejects` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 켬 | 99.947 | 8 | 501/38/2/0 | 150/**0** | 153,600(불일치 0) | 149 | 1,209,600 | 84/84 · 66/66 = **100%** | 0.990 | 100%·100% | 0 |
| S2 | 켬 | 100 | 7 | 529/57/0/0 | 191/**0** | 193,536(불일치 0) | 190 | 1,559,296 | 90/90 · 101/101 = **100%** | 1.000 | 100%·100% | 0 |
| OFF1 | **끔**(`SYW2_G1_HD_PACK_SHADE=0`) | 99.946 | 8 | 348/31/2/159 | 0/0 | 0 | 0 | 0 | 0/82 · 0/63 (aux 키 전부 `skip_aux`) | 0.989 | 100%·100% | 0 |

  - 사전등록 합격식 충족: 켬 두 run 모두 크래시·안전·fallback·dropped 0·validator 바깥 diff 0·**자기 검사 불일치 0(사유 5종 전부 0)**·음영 matched hit 100%(≥90%)·tinted matched ≥0.95(0.990/1.000)·A/B·지형 100%·`lut_rejects` 0·PS3 HD min ≥99.9·p95 ≤9. `hd_pack_rejects`: S1 2 = lap1169 tree_plus 프레임 0 키(`44c611f6` 96×112, 키 로그 `first_xy [51,104]` 동일, middle 명시 예외), S2 0 → **새 reject 0**. 끔 대조(OFF1)는 음영 aux 키 159개(키 로그 첫 결과 기준) 전부 `skip_aux`·shade 카운터 0 → 끔 스위치가 이전 동작을 복원함을 입증.
  - 키 로그 `shade_hit` 줄 `slots`(키별 쓰인 음영 단계 수 예 30~31)·`selfcheck`(예 64×48 타일 1,024 = 마름모 안 쓴 화소).
- **S-2 의미:** 켬 run의 `s`가 한 값이 아닌 HIT 키 = 149/150·190/191(≥1 충족), `selfcheck_pixels` 합계 153,600·193,536, `shade_key_color`(LUT 결과 0xFE) 0.
- **S-3 크롭 열람(`crops/`):** **S1은 baseline·candidate 두 lane이 서로 다른 임의 맵**(공유 temp `crops/S1_mid_*` 직접 확인, 건물·지형 불일치; block-mean 차 17.0이 장면 불일치 때문임)이라 S1 대조는 증거에서 제외하고, **같은 장면인 S2 baseline(위)·candidate(아래)** 크롭 3장을 판정에 쓴다: `S2_edge_TL`(지도 가장자리 검은 안개 경계와 나무), `S2_fog_R`(오른쪽 어두워지는 음영 그라디언트와 밭 작물), `S2_mid`(건물·돌 지형·밭 경계). 음영 그라디언트·안개 경계 위치와 밝기 단계가 baseline과 같고 평탄하게 밝아지거나 1x 칸 격자 계단은 관측되지 않았다(질감만 바이큐빅 stand-in으로 부드러움). 정량: 같은 장면 8 px 블록 평균 차(candidate 2×2 평균 vs baseline) **S2 ps3_start 0.86·ps3_act 3.11**, 음영 끔 대조 OFF1 2.66·2.38(OFF1은 baseline·candidate 같은 장면). 한계: 켬/끔 같은 맵 직접 대조 쌍은 없음(새 게임 임의 맵, 실행마다 다름) → "음영 켬이 끔보다 baseline에 더 가깝다"는 직접 비교는 하지 않았다. 켬 S2가 baseline과 OFF1 수준으로 일치한다는 것이 근거이고, 이것이 음영 유지의 직접 입증은 아니다(공개).
- **메모리:** 키 수 켬 541/586·끔 540(+1/+46), 음영 키 LUT 합계 1.21/1.56 MB(키당 ≈8 KB, 쓰인 음영 단계×256 B), 키당 음영 복사 w×h(예 64×48 = 3 KB; source 복사는 prepare 뒤 해제), `cache_insert_frame_bytes` 켬 3.92/3.97 MB·끔 4.63 MB(끔은 음영 키를 Scale2x 프레임으로 캐시), 정적 키 배열 +≈0.4 MB(`G1HdKey` +≈100 B ×4096).
- **원본 보호:** 원본 EXE SHA 전후 MATCH, game 사본 하네스가 삭제(prefix·manifest·output 보존, `local/runtime/lap1171_hds1_{S1,S2,OFF1}`).

## 판정

**H-HDS1 `PASS(partial, 기술·격리)`** — S-0 FEASIBLE(90.5%), 켬 2 run 합격식 충족(자기 검사 불일치 0·음영 matched hit 100%·새 reject 0), 끔 대조 입증, 같은 장면 크롭에서 음영 유지. 단서: (1) 켬/끔 같은 장면 직접 쌍 없음(임의 맵·lane 맵 불일치), 크롭은 S2 한 장면; (2) 자기 검사는 키 생성 시점 renderer 표 기준 — 팔레트/표가 게임 중 바뀌면(페이드·밝기 설정 등) 이미 만든 `LUT_s`가 낡을 수 있음(이번 NG5 구간 관측 0, 표 변경 감지 UNKNOWN); (3) 음영은 1x 칸 단위를 2×2에 복제(원본 의미 보존, 격자 계단은 미관측); (4) 화질 평가 아님(바이큐빅 stand-in), 기본 켬·사용자 전달 아님; (5) checker `0x468E10`·유닛 `0x466B50`·tinted viewport 클립 수리(lap1170 §3 backlog)는 비목표 그대로.

## 검사

- `make lint`·`make typecheck` PASS(구현 후). 목표 테스트 `tests/test_g1_hd_pack.py` 20 PASS. 전체 `make check` 결과는 STATUS 검증 줄에 보강한다.
- 변경 파일 SHA256(앞 16자): `tools/inmm_stub/g1_hd_asset.c` `83a340e5aef6bc30`·`g1_hd_asset.h` `1934612c33e3148a`·`direct_draw_trace.c` `12a9ad7894091bd3`·`tests/test_g1_hd_pack.py` `e0c2d4734f384fc0`.
- 측정 스크립트(공유 temp `20261008_lap1171_work_hds1/scripts/`): `run.sh`·`seq.sh`(lap1169 것 수정본)·`metrics_c.py`(shade 지표 추가)·`s0.py`.

## 다음 행동

middle(Opus) 독립 검수 → ⑤ 전체 화면(800×600) HD 자리 / ⑥ 유닛 경로 사전등록. 검수 항목: (a) `capture_shade`·`shade_prepare`·`shade_apply` 코드와 테스트(특히 클립판 identity 가정·표 읽기 검사 범위·`s≥64` 경계), (b) S1·S2·OFF1 raw(키 로그·trace) 재계산, (c) 크롭 열람과 같은 장면 쌍 한계 판정, (d) 표 변경 감지(UNKNOWN) 처리. 사용자 G1 시험 결과가 오면 최우선.

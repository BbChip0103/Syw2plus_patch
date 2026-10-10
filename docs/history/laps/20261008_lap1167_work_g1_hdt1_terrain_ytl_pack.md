# 2026-10-08 | lap1167 | G1 work — H-HDT1 ④-2 지형 무음영 타일(`0x468C30`·`0x468F00`) HD 팩

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). 커밋 0. 게임 C source·하네스 변경 0(도구·테스트만).
- 입력: lap1166 middle 사전등록 §4(`20261008_lap1166_middle_g1_hdl1_review_hdt1_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 26~27 GB(≥20).
- 가설: 지형 무음영 writer의 source 포인터는 원본 `.ytl` 프레임 스트림 시작(0xBF4 + 0x4C0 표)이고 출력은 원본 인덱스 그대로이므로, 도구가 `.ytl` 프레임에 같은 `(digest, w, h)` 이름을 주면 C 변경 없이 기존 로더가 지형 타일에 HD 팩을 적용한다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…` 전후 MATCH(`orig_sha_before/after.txt`). 원본 그림 파일은 `g1_hd_extract extract`가 읽기 전용(`source_unchanged` true). 환경: 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --new-game-path --new-game-start --new-game-act --hd-source scale2x`(lap1161 D-4·lap1163·lap1165와 같은 NG5), 활성 8 player records(부하 증명 아님), 새 임의 게임(fixture = 하네스 새 게임), 팩·키 로그만 바깥 env. 산출물 공유 temp `20261008_lap1167_work_hdt1/`.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/g1_hd_convert.py` | `pack`이 `.ytl`도 이름 부여: `ytl_stream_offsets`(0xBF4 + 0x4C0 표 `fc`개)·`decode_ytl`로 1x 그림·크기(헤더 fw×fh)·충돌 규칙은 `.spr`와 동일. 보고에 `ytl_frames`·`ytl_narrow`(0x468C30이 `rle_dimensions`로 헤더 폭보다 좁게 키를 만들 프레임 수; 이 경우 이름이 달라 MISS→Scale2x 안전 폴백). `ytl_widest` 보조 함수 |
| `tests/test_g1_hd_convert.py` | `.ytl` 합성 파일 헬퍼 + 테스트 2개: 스트림 시작 이름(두 테마 폴더 같은 그림 = 한 이름·두 참조), 쓴 화소(skip/count) 기준 HD 프레임 byte 기록(안 쓴 열 0xFE 유지). RED(둘 다 FAIL) → GREEN 확인 |
| `tests/test_g1_hd_pack.py` | 로더가 writer와 무관함을 고정하는 호스트 테스트 1개(writer `0x468C30`, aux 없음 키 HIT) |

C·하네스는 사전등록대로 0(로더는 aux 없는 모든 키를 이미 조회).

## 측정

- **T-0 오프라인(`pack --dry-run`, 도구 `.ytl` 포함, 폴더 char·tile·BattleSpr·portrait·fnt·yfnt·Online·ybriefingfnt·eft):** 파일 3,341·프레임 134,971·이름 부여 134,441·고유 이름 96,123·충돌 이름 3,282(23,889 프레임)·`.ytl` 프레임 16,655(이 중 0x468C30 키 폭이 헤더 폭과 다른 `ytl_narrow` 828 = 5.0%). **lap1165 run 5개의 지형 aux0 키 88개(0x468C30 66·0x468F00 22) → 대응 81(92.0%)·충돌 7·미대응 0.** 고유 이름 76 중 대응 70(92.1%). **판정 `FEASIBLE`(≥80%).**
- **T-1 팩(B형 절차):** `.ytl` 425파일 17,062프레임 추출(`ref_ytl`, 원본 불변) → 원본 팔레트 RGB(×4) 바이큐빅 2배(`rgb_ytl`; 스크립트 `bicubic.py` = lap1165와 동일) → `convert`(위반 0, 17,062/17,062) → `pack`(7,339파일) + lap1165 팩(`pack_l2b` 618개) 병합 = `pack_t1`(7,958). **투명 경계: 그대로**(변환 전 투명 화소의 키 색 RGB 포함 업스케일, 실루엣은 `convert`가 1x 마스크로 강제). 변형 `pack_t2` = **가장자리 복제**(1x 마스크 밖 화소를 가장 가까운 불투명 색으로 채운 뒤 바이큐빅, `bicubic_edge.py`, 그 밖 동일).
- **T-2 NG5(전부 PASS 항목 = 크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator PASS(`hd_mask_outside_diff` 0)·`hd_pack_rejects` 0·`identity_invalid_sources` 0·PS3 HD min 100):**

| run | 팩 | PS3 p95/p99/max ms | over 9ms | hits/misses/rejects | lookup_blocks | A/B matched hit | 지형 matched hit | 비고 |
|---|---|---|---|---|---|---|---|---|
| T1 | `pack_t1` | 6/7/12 | 2 | 152/35/0 | 29,954,249 | 94/103 = 91.3% | **55/55** | PASS |
| T2 | `pack_t1` | **15.4**/24/37 | 195 | 154/22/0 | 30,890,266 | 100% | 61/61 | **p95 FAIL — 환경 부하**(아래) |
| T3 | `pack_t1`(T2 재실행) | 7/7/20 | 2 | 150/22/0 | 32,026,810 | 98.9% | **55/55** | PASS |
| T4 | `pack_t2`(가장자리 복제) | 7/7/10 | 1 | 148/22/0 | 31,137,107 | 100% | **60/60** | PASS |
| C1(대조) | 팩 없음 | 6/7/8 | 0 | 0/0/0 | 0 | — | — | PASS |

  - 모든 팩 run 지형 aux0 키 중 충돌 이름 4~6개는 `MISS`→Scale2x 폴백(rejects 0). 충돌 6개 = `tile/*/blacktile.ytl` 계열(테마 간 앞 128 B 동일·뒤 다름)·`tile/volcano/sea·diff·hill·grss`.
  - **T2 p95 FAIL 판정:** PS3 present 1,513 중 앞 1,000개는 over9 0·p50 5; 마지막 약 500개에서 over9 195(평균 8~14 ms). 같은 팩·같은 소스 재실행 T3은 p95 7. T2 구간은 시스템 load average 5.12(다른 세션 프로세스)와 겹쳤다(`uptime`) → 환경 부하로 판정하고 T2는 실패 run으로 보존(재실행 T3으로 대체한 사실 공개).
  - **사전등록 §4 `lookup_blocks > 30.8M` 정정:** 30.8M은 lap1165 **P1**(패널 파일 없는 run)의 값이었다. lap1165 P3~P5 최대는 P5 29,635,959(P4 29,551,552). 이 기준으로는 T1 29.95M·T2 30.89M·T3 32.03M·T4 31.14M **모두 초과**. 사전등록 문면(30.8M) 그대로 읽으면 T1만 미달(29.95M)이다. 공개: lookup_blocks는 패널 c/j 탈락·run별 장면 변동에 따라 ±2M 흔들려 지형 기여의 직접 증거가 아니다 — 지형 기여의 직접 증거는 키 로그의 지형 aux0 matched hit 100%.
  - **지형 draws는 적다:** T3 키 로그 draws 합 `0x468C30` 493·`0x468F00` 430(같은 run A/B draws 99,214). 지형은 레이어 캐시에 한 번 그려지므로 draws 수는 화면 면적을 과소대표한다(lap1166 §3 지적과 일치).
- **T-3 지형 크롭(`crops/`, 직접 열람):**
  - `ground_C1_top_T1_bottom.png`: T1(투명 경계 그대로)은 평지 지형에 **밝은 마름모 격자선**(타일 가장자리)이 선명하게 보인다. 대조 C1(Scale2x, 장면은 다름)에는 없음. → 바이큐빅이 투명 키 색을 가장자리로 번지게 한 stand-in 산물로 의심.
  - `same_map_ground_C1_top_T4_bottom.png`·`same_map_ground_patch_edge_C1_top_T4_bottom.png`·`same_map_bottom_edge_C1_top_T4_bottom.png`: C1과 T4는 **같은 맵·같은 카메라 위치**(이번 두 run만 우연히 동일)라 같은 영역을 직접 대조할 수 있다. T4(가장자리 복제 팩)는 격자선·이음매 없이 지형 질감이 부드러워지고(바이큐빅 stand-in) 타일 경계·흙 패치 가장자리 위치는 C1과 같다. **구분 근거: 같은 엔진·같은 팩 이름 경로에서 팩 내용(투명 경계 처리)만 바꿔 격자선이 사라졌으므로 엔진 문제가 아니라 stand-in 산물.** 다른 두 run(T1~T3) 장면은 T4·C1과 달라 같은 화소 대조는 못 했다(맵·시작 건물 무작위).
  - 흙 패치(브라운)는 두 쪽 모두 Scale2x 질감 그대로(blended/tinted 계열은 ④-3·④-4 범위).
- **테마:** 관측 지형 이름 64(+충돌 6)는 전부 `volcano` 이름(NG5 맵 테마 volcano)이며 이 중 43개는 volcano 전용, 21개는 `bright/brown/dark/green/normal/snow`와 공통 이름(공통 14 + 6테마 7). normal 테마 장면은 이번 run에서 관측하지 못했다(공통 21개 이름만 normal에도 적용되고 normal 전용 이름의 장면 hit는 미측정) → backlog.
- **원본 보호:** 원본 EXE SHA 전후 MATCH, 원본 그림 `source_unchanged` true. `local/runtime/lap1167_hdt1_{C1,T1,T2,T3,T4}`의 `game` 사본은 하네스 정리로 삭제됨(prefix·manifest·output 보존).

## 판정

**H-HDT1 `PASS(partial, 기술·격리)`** — T-0 FEASIBLE(92%), 지형 aux0 matched 키 hit 100%(T1·T3·T4·T2 전부)·rejects 0·안전·fallback·dropped 0·scale2x 바깥 변화 0·HD min 100. 단서 4건: (1) 합격 run = T1·T3(투명 경계 그대로)·T4(가장자리 복제), T2는 환경 부하로 p95 FAIL(공개); (2) 사전등록 `lookup_blocks` 기준 수치 오류 정정(위), 문면대로면 T1 미달 → middle 판정 필요; (3) 투명 경계를 그대로 두면 지형에 마름모 격자선이 생겨 **팩 제작 시 가장자리 복제가 필요**(T4 증거) — 실제 업스케일러 결과를 쓸 때도 투명 화소 색이 가장자리로 새지 않아야 한다; (4) 한계: 화질 평가 아님(바이큐빅 stand-in), `ytl_narrow` 5% 프레임은 0x468C30에서 이름 불일치로 폴백, 충돌 이름·normal 전용 장면·기본 켬·사용자 전달 아님.

## 검사

- `make lint`·`make typecheck` PASS. 목표 테스트 `tests/test_g1_hd_convert.py`(26)·`tests/test_g1_hd_pack.py`(8) 통과. 전체 `make check` 결과는 STATUS 검증 줄에 보강한다.
- 변경 파일 SHA256: `tools/g1_hd_convert.py` `8741404d0be4…`·`tests/test_g1_hd_convert.py` `c61857c2e2d4…`·`tests/test_g1_hd_pack.py` `b7967da9f7da…`(모두 untracked 신규).
- 측정 스크립트(공유 temp `20261008_lap1167_work_hdt1/scripts/`): `run.sh`·`metrics.py`·`ps3.py`·`bicubic_edge.py`·`seq*.sh`(`bicubic.py`는 lap1165 것 재사용).

## 다음 행동

middle(Opus) 독립 검수 → ④-3 선택. 검수 항목: (a) `pack` `.ytl` 이름·`ytl_narrow` 정의(0x468C30 `rle_dimensions` vs 0x468F00 `width_word`), (b) T-0 88키 대응·충돌 7 재계산, (c) T1·T3·T4 raw 재계산(키 로그·trace·p95)과 T2 환경 부하 판정, (d) `lookup_blocks` 사전등록 수치 정정 수용 여부, (e) 크롭 5장 직접 열람(특히 T1 격자선 vs T4), (f) ④-3 tinted 색 치환표(C 변경: aux 256 B 표를 팩 인덱스에 재적용, 실루엣 검증 동일) 사전등록. backlog: normal 테마 장면 확보, 협소 프레임(`ytl_narrow`) 처리, 충돌 이름 처리. 사용자 G1 시험 결과가 오면 최우선.

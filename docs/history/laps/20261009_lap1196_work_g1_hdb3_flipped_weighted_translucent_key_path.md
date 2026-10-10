# 2026-10-09 | lap 1196 | G1 work — H-HDB3: 좌우반전 가중표 혼합 `0x467FD0`·`0x4685C0` HD 키 경로

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1195 middle 사전등록 §7(`20261009_lap1195_middle_g1_hdb2_review_hdb3_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 26 GB, 끝 21 GB(run 4개, `game` 사본은 하네스가 종료 때 삭제, prefix·manifest·output 보존).
- 가설: `0x467FD0` = `0x467580`, `0x4685C0` = `0x467B00`을 좌우반전해 그린다(토큰 열 c → 화면 열 `x+w−c−1`). 디코드한 idx/mask 행을 뒤집어 화면 방향 평면으로 만들면 crop·자기 검사·identity bind·HD 혼합이 H-HDB1/H-HDB2 공유 코어 그대로 성립한다. 팩 파일(스트림 방향)은 asset 층에서 행 반전한다.
- 예상 PASS/FAIL: 사전등록 §7(B3-0·B3-2 변이 전부 RED · B3-4(i) 두 writer 각각 keyed ≥95%·자기 검사 불일치 0(wrap 제외)·`key_clip_cut` ≥1·비대칭 실루엣 hit ≥1·안전 0·p95 ≤ 끔+2·기존 서명 군집 밖 새 stale 군집 0·`0x467580`/`0x467B00` 비회귀 · (ii) pair PASS).

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_blend_key.h` | `g1_blend_flip_rows(plane,width,height)`: 행별 좌우 반전(순수, memcpy 호출 금지 속성) |
| `tools/inmm_stub/g1_mirror2x.c` | `blend_key_apply`: `flip = writer == G1_FLIP_BLEND(0x467FD0) \|\| writer == G1_BLEND_SKIP(0x4685C0)`을 writer에서 파생(시그니처 불변), 디코드 직후 idx·mask 행 반전 → 이후 crop·자기 검사·identity bind는 기존 그대로(복제 코어 없음). `mirror_blend_skip`(0x4685C0): 0x467B00과 같은 구조 — 원본 호출 **전에** 클립 4값 읽기 → `g1_blend_clip_window` → `blend_key_snapshot`·창 pre-draw crop(`g_blend_clip_key_before` 재사용, 두 wrapper가 겹치지 않음) → 원본 → 기존 banded diff 미러 → 성공 분기 안에서 `blend_key_apply(weighted=TRUE)`; 빈 창 `key_clip_empty`, 버퍼 초과 `key_fallbacks`, 키 성공 + 창 < 교집합이면 `key_clip_cut`. `mirror_flip_blend`(0x467FD0): 클립 없음, 화면 교집합 창으로 같은 흐름; 사각형이 stride·화면을 넘는 호출(`wrapped`)에서 자기 검사가 불일치로 폴백하면 `key_wrap_mismatches`로 센다. 두 wrapper 모두 diff 미러 성공 분기 안에서만 키를 시도하고 폴백이면 diff 결과를 유지. `G1BlendKeyStats`에 `key_wrap_mismatches`, `g_flip_blend_key`·`g_blend_skip_key` 리셋·접근자 13개 |
| `tools/inmm_stub/g1_hd_asset.c`·`.h` | `G1_HD_BLEND_FLIP 0x467FD0`·`G1_HD_BLEND_SKIP 0x4685C0`, `is_flip_blend_writer`(LUT 없는 반전 writer): `read_pack_frame`이 팩 행을 반전한 뒤 반전 identity 마스크로 실루엣 검사, `hd_pack_blend_*` 카운트에 포함. `g1_hd_asset_blend_flip_key_path()` = blend 경로 && `SYW2_G1_HD_PACK_FLIP`≠0 (**끔 env 결정:** `PACK_BLEND=0` 또는 `PACK_FLIP=0`이면 두 writer 키 끔, diff 미러만) |
| `tools/inmm_stub/g1_mirror2x.h`·`direct_draw_trace.c` | 접근자 13개, present metrics `blend_4685C0_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels/key_clip_cut/key_clip_empty`, `blend_467FD0_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels/key_wrap_mismatches` (mirror_details 최대 길이 9.3 KB + 약 0.6 KB < 12,288) |
| `tests/test_g1_blend_key.py` | B3-0: 5개 wrapper 키 블록이 diff 미러 성공 분기 안(`reject_size` else 앞)임을 단언. B3-2: `g1_blend_flip_rows` 홀·짝·1폭, **참조 모델 호스트 테스트 2**(원본 asm 식으로 우→좌 그리기·클립 규칙을 옮긴 참조 출력 vs 키 자기 검사: 비대칭 6×4 스트림, 반전 평면은 일치하고 스트림 방향 평면은 불일치, 왼쪽 클립이 스트림 오른쪽 끝 열을 자름, 오른쪽·아래 포함 경계, 위 잘린 행 연속성, 4면 동시·1열·1픽셀·빈 창 3방향, 터치 칸 ⊂ 창), 배선 정적 4(코어 flip 파생·반전 위치, 0x4685C0 클립 읽기·창·crop·카운터, 0x467FD0 창·wrap 카운터, 트레이스·리셋·asset). 총 31 |
| `tests/test_g1_hd_pack.py` | 호스트 로더 시나리오 `blendflip_467FD0`·`blendflip_4685C0`(미러된 팩 프레임 hit, blend 카운트, flip/LUT 카운트 불사용)·`blendflip_plain`(비반전 blend writer는 같은 마스크를 reject)·`blendflip_flip_off`·`blendflip_blend_off`. 총 74 |

파일 SHA256 앞 16자(최종, 첫 run 시작 이후 `tools/`·`patches/` 변경 0 = `find -newer` 빈 출력): `g1_blend_key.h 01ad28c62adc3e7f`·`g1_mirror2x.c a66b31ed4d0a5c9f`·`g1_mirror2x.h c6c7e39627792763`·`g1_hd_asset.c b3d51ae29b34281d`·`g1_hd_asset.h 61173d6bd31309ff`·`direct_draw_trace.c 7fed5d24d64b6456`·`_inmm.dll 76173b36317ec1e6`(전 run 공통, 이전 DLL `547e6179…` 사본 보존)·`test_g1_blend_key.py 2ca7e7de7310edce`·`test_g1_hd_pack.py 8e27d680fa1cac94`. 원본 EXE SHA `b56986e0…` run 전·후 MATCH(`orig_sha_before.txt`·`before2`·`after`). 공유 temp `20261009_lap1196_work_hdb3/`.

## 측정

**B3-0:** lap1195 생존 변이 n11을 5개 wrapper(`mirror_blend_rle/wrle/clip/skip`·`mirror_flip_blend`) 각각에서 "키 블록을 diff 미러 성공 분기 밖(else 뒤)으로 이동"으로 격리 사본에 재현 → **5/5 RED**, 현재 코드 GREEN(`mut/mutation_n11_lap1196.py`·`.txt`).

**B3-2 변이 16종**(격리 사본 `mut/mutation_lap1196.py`, 베이스 105 GREEN): m1 반전 생략·m2 스트림 방향 crop 오프셋·m3 팩 반전 생략·m4 오른쪽 클립을 top 필드로 읽기·m5 writer 파생에서 0x4685C0 제거·m6 0x4685C0 weights 끔·m7 0x4685C0 키 블록을 성공 분기 밖으로·m8 `flip_rows` 반복 수 오류·m9 wrap 불일치를 항상 셈·m10 flip 경로가 `PACK_FLIP` 무시·m11 mask 반전 생략·m12 폴백 경로에서도 `key_clip_cut` 증가·m13 0x467FD0이 일반 blend 경로 사용·m14 0x467FD0 키 블록을 성공 분기 밖으로·m15 0x467FD0 snapshot을 원본 뒤로·m16 클립 창 오른쪽 배타 → **16/16 RED**. 설계 정정 공개: 첫 시도에서 m4(의미 없는 변이)·m8(홀수 폭 가운데 열 자기 교환 = 동등 변이)·m12(테스트 공백)가 SURVIVED였고, m4·m8은 진짜 변이로 교체, m12는 `block.count("key_clip_cut") == 1` 단언을 추가해 RED로 만들었다. 사전등록의 "writer id 교체"는 m5(파생식 변경)로, "weights NULL"은 m6, "클립을 원본 뒤에 읽기"는 m4·m15 계열로 대응했다.

**B3-3 귀속(`scripts/attrib.py`·`asym.py`, 독립 헤더 파서: `.spr` 오프셋 표 재유도 + 앞 128 B FNV-1a·w·h):** 켬 run P0·P1·pair PD·끔 Q0 키 로그의 두 writer digest = **각 14개(같은 14개)**, 모두 `fnt/CLOUD.spr` 한 파일(미귀속 0, 다중 파일 0). CLOUD는 이미 lap1194 `pack_hdb2b`(team-safe bicubic stand-in 초안)에 있어 **팩을 새로 만들지 않고 `pack_hdb2b`를 그대로 썼다**(새 digest 없음). 키 로그 miss·reject 0. **비대칭 실루엣 hit 키:** 0x467FD0 14/14, 0x4685C0 14/14(P0+P1 합집합; pair PD 12/12)이고 대칭 0 — 반전 팩 + 반전 마스크 검사가 hit이면서 reject 0이므로 키 단위 방향이 입증된다(H-HDU0 방식).

**B3-4(i) 하네스:** `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`(lap1194 F0 구성), `SYW2_G1_HD_PACK=pack_hdb2b`, 키 로그 켬.

| run | 구성 | PS3 present·s | p95 | stale 최대 | 안전 7종·dropped | 0x4685C0 화면 안 = keyed + 폴백 + 빈 창 | `key_clip_cut` | 자기 검사 불일치/px | 0x467FD0 화면 안 = keyed + 폴백 | 불일치/px·wrap_calls·`key_wrap_mismatches` |
|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 켬 | 6,030·301 | 6 | 277(13.1 s 247·15.1 s 277 + 꼬리 ≤79, 기존 서명) | 0·0 | 1,439 = 717 + 0 + 722 | 717 | **0** / 3,809,623 | 898 = 898 + 0 | **0** / 10,608,098 · 0 · 0 |
| P1 | 켬 | 6,031·301 | 6 | 0 | 0·0 | 18 = 15 + 0 + 3 | 4 | **0** / 73,008 | 8 = 8 + 0 | **0** / 96,149 · 0 · 0 |
| Q0 | 끔(`PACK_BLEND=0`, 같은 팩) | 6,032·302 | 6 | 79(225.2 s) | 0·0 | 1,089 = 0 + 0 + (키 시도 없음) | 0 | — | 219 = 0 + 0 | — |

- P0는 키 로그 digest 발견용으로 먼저 돌렸지만 이후 팩·DLL·env가 같아서 켬 #1로 센다(P1이 켬 #2).
- **합격 항목:** 두 writer 모두 키를 시도한 호출 keyed **100%**(≥95%). 자기 검사 불일치 **0**(0x4685C0 합 3,882,631 px·0x467FD0 합 10,704,247 px). `key_clip_cut` ≥1(721). 비대칭 hit 키 ≥1. 안전 7종 0·dropped 0. p95 6·6 ≤ 끔 6+2. `0x467580` P0 10/10·P1 18/18 keyed·불일치 0, `0x467B00` P0 9 keyed + 3 빈 창·P1 154 keyed + 6 빈 창·폴백 0·불일치 0 → 비회귀. `hd_pack_blend_hits` 38·34, rejects 0.
- **stale:** P1 0, Q0 79, P0은 13.1 s 247·13.3 s 64·14.9 s 21·15.1 s **277**·15.2 s 70/79 — 모두 기존 서명(약 13.1 s·약 15 s 쌍봉 + 그 뒤 ≤100 px 꼬리) 시각대 안이고 서명 밖 새 군집은 없다. **공개:** 15.1 s 최대값 277은 사전등록 "약 240~260 px"보다 약간 크다(lap1187 backlog "15.5 s 군집 최대값 변동 18~305"의 범위 안). 3 run 중 1 run에서만 나왔고(약 1/3 서명 빈도와 일치) 끔 Q0·켬 P1에는 없다. 원인 규명은 비목표.
- **B3-4(ii):** pair PD(save006, `pack_hdb2b`) `status PASS`·`scene_state_equal` true. status 목록의 비-PASS는 `owner0_hq_type` UNKNOWN 2·`candidate.trace_close` FAIL·`mirror_validator` BLOCKED로 lap1189/1194 backlog와 같은 기존 하네스 문제다. 이 장면 키 로그: 0x4685C0 draws 26·hit 13줄(12키), **0x467FD0은 키 로그 항목 0**. pair는 `--candidate-no-present-trace`라 호출 수 metrics가 없어 "호출이 없었음"과 "selfcheck 폴백"을 직접 구분할 수 없다. 로그에 항목이 없으므로 팩에 더할 digest도 없어 사전등록의 재실행은 하지 않았다(F0 run 906호출에서 폴백 0이 근거).
- **원본 보호:** EXE SHA `b56986e0…` 전·후 MATCH. `local/runtime/lap1196_hdb3_*` 4개의 `game` 사본 없음.

## 판정

**B3-0 PASS**(5/5 RED) · **B3-1 PASS**(공유 코어 `flip` 파생, 복제 0) · **B3-2 PASS**(16/16 RED, 설계 정정 공개) · **B3-3 PASS**(14 digest 전부 귀속, 비대칭 14/14) · **B3-4(i) PASS**(위 항목 전부, stale은 기존 서명 시각대 밖 새 군집 0·277 공개) · **(ii) PASS**(0x4685C0만 pair에서 키 로그 hit, 0x467FD0은 장면에 로그 없음). 전체 `PASS(partial, 기술·격리)` 후보. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 한계·공개

1. 팩 그림은 bicubic stand-in(실제 업스케일 화질 평가 아님). 반전 방향·클립 경계가 맞는다는 증거는 자기 검사(원본 1x 출력 = 같은 식)·참조 모델 호스트 테스트·반전 마스크 실루엣 hit이고, 반전 HD 그림을 육안으로 본 run은 없다.
2. **wrap 경로(사각형이 stride·화면을 넘는 0x467FD0 호출)는 실게임에서 한 번도 관측되지 않았다**(`wrap_calls` 0, `key_wrap_mismatches` 0이 자명). 호스트 참조 모델도 화면 안 사각형만 다룬다. 원본이 넘어 쓴 칸이 창 안으로 들어오면 자기 검사가 폴백시키는 설계는 변이 m9의 문자열 계약으로만 고정돼 있다.
3. pair 장면에는 0x467FD0 호출 증거가 없다(위). 팩에 있는 파일은 `fnt/CLOUD.spr` 하나뿐이라 다른 효과 `.spr`의 반전 호출은 이 run들에서 보지 못했다.
4. 정적 테스트 일부는 문자열 계약이다(변이로 RED 확인).
5. 남은 충돌 3개·`0x4678C0`·반전 7인자 sibling(`0x468360`)·`0x467E60`·실제 업스케일 화질·기본 켬은 비목표다.

## 다음 행동

middle(Opus)이 H-HDB3를 검수(코어 flip 파생·참조 모델 식, 변이 재현, trace·키 로그 재계산, 277 px 판정)한 뒤 다음 후보(7인자 `0x4678C0`·그 반전 sibling `0x468360`/`0x467E60`)를 사전등록하거나 효과 갈래 마감을 판정한다. 사용자 G1 시험 결과가 오면 최우선.

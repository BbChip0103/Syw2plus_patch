# 2026-10-09 | lap 1195 | G1 middle — H-HDB2 검수 + work H-HDB3(좌우반전 가중표 혼합 `0x467FD0`·`0x4685C0` 키 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간(middle, 진단·확인). 게임 실행·C source 수정·커밋 0. 변이 시험은 Sonnet 하위 에이전트가 격리 사본(공유 temp `mut/iso/`)에서 수행했다. 저장소는 건드리지 않았고, 끝난 뒤 사본은 저장소 source와 `diff -r` 일치, `git status` 전후 동일이다.
- 입력: `loop/ESCALATE_SOL`(lap1194 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261009_lap1195_preserved_lap1194_escalate_sol.txt`(SHA256 앞 `8a2af586626820e5`), 보존 뒤 삭제. `loop/STOP` 없음. INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 26 GB.
- 가설(검수): lap1194 B2-0~B2-4 수치가 raw에서 재현된다. 클립 창은 원본 `0x467B00`의 클립 의미와 같다. Y3 13~15 s stale 군집은 이번 키 경로와 무관하다.
- 산출물(공유 temp `20261009_lap1195_middle_review/`, SHA256 앞 16자): `series_lap1195.py` `6faecfa9f37d6d95`·`.json` `e589ea3098cbfe01`, `keytime_lap1195.py` `a85731ad08631feb`, `attrib_lap1195.py` `77f6d623d6d9f6aa`·`.json` `71ba171240c2bb52`, `orig_4685C0.asm` `39fa54e25ed87bb3`, `orig_467FD0.asm` `2830c81e5bcb5107`, `mut/mutation_lap1195.py` `3241863ea48f3d1a`·`.txt` `405dc96efc867fb9`.

## 1. source·원본 정체성

- source SHA256 앞 16자 9개가 lap1194 기록과 일치한다: `g1_blend_key.h 3afce085…`·`g1_mirror2x.c be7a83c3…`·`g1_mirror2x.h 55a4316e…`·`g1_hd_asset.c 1fae392f…`·`direct_draw_trace.c d7239dea…`·`test_g1_blend_key.py d86f86b0…`·`test_g1_hd_pack.py 4d966149…`·`test_g1_hd_convert.py e92bc2a0…`·`_inmm.dll 547e6179…`.
- `logs/gates/lap1194-work-full-check.log` 이후 `tools/`·`patches/`·`tests/` 변경은 0이다(`find -newer`). 그 로그의 결과는 `2016 passed, 5 skipped in 807.39s`다.
- 원본 EXE SHA `b56986e0…`는 이번 회차 `tools/check_setup.py`로 `verified`다.

## 2. C 독립 검토(`mirror_blend_clip`·`g1_blend_clip_window`·`blend_key_apply`)

- **클립 읽기 순서:** 클립 4값(`G1_RENDERER_VIEWPORT`+0/4/8/12 = `+0x4D0` left·`+0x4D4` top·`+0x4D8` right·`+0x4DC` bottom)은 `g_original_blend_clip` 호출(5167행)보다 앞(5150~5154행)에서 읽는다.
- **창 식:** 창 = max(left, x0)·max(top, y0)부터 min(right+1, x1)·min(bottom+1, y1)까지다. 오른쪽·아래는 포함 경계를 반열림으로 바꾼 것이다. 64비트 중간값을 쓰므로 `INT32_MAX` 클립에서도 넘치지 않는다. 비면 0을 돌려준다.
- **원본과의 대응(lap1193 `orig_467B00.asm`):**
  - 열은 `x+col ∈ [left, right]`만 쓴다. 창의 x 범위와 같다.
  - 위가 잘린 행은 원본이 파싱하되 쓰지 않는다. 키는 전체 스트림을 디코드한 뒤 창 오프셋 `(kx0−x, ky0−y)`으로 crop한다. 그래서 행 순서가 같다.
  - 아래가 잘린 행은 원본이 파싱하지 않는다. 디코더는 끝까지 읽는다.
  - `x+w−1 < left` 또는 `y+h−1 < top`이면 원본은 즉시 반환한다. 이때 창은 비어 `key_clip_empty`가 된다.
- **아래 잘린 행까지 읽는 디코더의 안전성:** 수용한다.
  - 스트림은 `.spr` 프레임 전체다. 같은 스트림을 클립 없이 그리면 원본도 끝까지 파싱한다.
  - 한도 `pixels*2+height*2`는 lap1190(H-HDB1)부터 수용된 공유 코어 계약 그대로다.
  - 실게임 결과: 시도 호출 2,427회(Y1 1,586 + Y2 31 + Y3 810)에서 폴백은 Y1의 7회뿐이다. Y1 키 로그의 `0x467B00` miss 키도 7개(movemark)이므로 폴백은 모두 팩 miss로 설명되고, 디코드 실패는 0이다. 예외·크래시도 0이다.
  - 잘못된 스트림이 할당 끝을 넘을 위험은 H-HDB1과 같은 수준이다. 새로 생긴 위험은 아니다.
- **해제 경로:**
  - 버퍼 초과(`width*height > G1_BLEND_KEY_MAX_PIXELS`): `key_fallbacks`
  - 빈 창: `key_clip_empty`
  - 두 경우 모두 `key_try = FALSE`만 바꾸고 `active`는 그대로 둔다. 그래서 diff 미러(5169행)는 항상 돈다.
  - 키는 diff 미러가 성공한 분기 안에서만 시도한다.
  - 경미: 버퍼 초과 검사가 창 검사보다 앞이다. 그래서 크고 클립 밖인 호출은 empty가 아니라 fallback으로 센다(Y2·Y3에서 0회, 판정 영향 없음).
- **자기 검사 창:** 대상은 `buffer + ky0*stride + kx0`와 crop한 사전 사본(`g_blend_clip_key_before`)이다. 클립 밖이면서 화면 교집합 안인 칸은 원본이 쓰지 않으므로 diff 미러만 다룬다. 이 처리가 맞다.

## 3. 변이 재현(격리 사본, 새 변이 12종 + 변형 1 — work 19종과 겹치지 않게 설계)

| 변이 | 내용 | 결과 |
|---|---|---|
| n1 | 클립 창·snapshot·crop 블록을 원본 호출 뒤로 | RED |
| n2 | crop 오프셋 (0,0) | RED |
| n3 | 팩 프레임 행 오프셋 무시 | RED |
| n4 | `key_cut` x만 비교 | RED |
| n5 | `key_clip_empty` 증가 제거 | RED |
| n6 | snapshot 원점 = 교집합 원점 | RED |
| n7·n7b | right/bottom 32비트 덧셈(넘침) | RED·RED |
| n8 | 버퍼 초과 가드를 교집합 크기로 | RED |
| n9 | `key_clip_empty` 리셋 제거 | RED |
| n10 | 디코드 한도 `pixels` | RED |
| n11 | diff 미러 실패 때도 키 적용(키 블록을 성공 분기 밖으로) | **생존** |
| n12 | 빈 창 판정 `>=` → `>` | RED |

- 기준선은 GREEN(185 passed)이다. RED는 12/13이다.
- **n11은 테스트 공백이다(현재 코드는 정상).** 기존 정적 테스트는 `original < apply_tiled < if (key_try)` 순서만 고정하고, 키 블록이 성공 분기 안에 있는지는 보지 않는다. 런타임 영향은 작다(자기 검사를 통과해야만 그린다). 다만 "diff 미러가 성공했을 때만 키" 계약은 비어 있다. 다음 work의 회귀 단언으로 넘긴다(§7 B3-0).
- n8(디코드 버퍼 경계)은 문자열 고정 테스트로 잡혔다. 동작 오버런 시험은 아니다(공개).

## 4. raw 재계산(새 스크립트, trace 마지막 metrics·PS3 present 계열 + 키 로그)

| run | PS3 present·s | p95 | stale 최대(≥150 군집) | 안전 7종 | `0x467B00` 화면 안 = keyed + 폴백 + 빈 창 | `key_clip_cut` | 불일치/px | `0x467580` keyed/mirrored·불일치 | 키 로그 `0x467B00` |
|---|---|---|---|---|---|---|---|---|---|
| Y0 끔 | 6,105·305.2 | 6 | 90 | 0 | 560 = 0 + 0 + 0 | 0 | — | 0/455·0 | 없음 |
| Y1 | 6,029·301.8 | 6 | 91 | 0 | 2,228 = 1,579 + 7 + (642) | 1,391 | 0 / 7,409,548 | 1,548/1,548·0 | hit 39·miss 7 |
| Y2 | 5,955·301.5 | 7 | 90 | 0 | 126 = 31 + 0 + 95 | 11 | 0 / 124,270 | 29/29·0 | hit 12 |
| Y3 | 6,031·301.5 | 6 | 245(13.1 s 245·14.9 s 242) | 0 | 818 = 810 + 0 + 8 | 8 | 0 / 6,116,163 | 819/819·0 | hit 26 |

- work 표의 수치는 모두 일치한다. 표기 보강: 자기 검사 합계는 13,649,981 px다(work의 "1,360만"은 내림 표기).
- **pair:** PB·PB2 모두 `status PASS`, `scene_state_equal` true다. 키 로그 `0x467B00`은 PB가 16키 전부 miss, PB2가 16키 전부 hit이다.
- **B2-3 독립 귀속(`attrib_lap1195.py`):** 6개 폴더의 모든 `.spr` 프레임에 대해 오프셋을 새로 유도하고 앞 128 B FNV-1a·w·h를 계산했다. 다섯 키 로그의 `0x467B00` digest **62개**가 모두 귀속됐다(미귀속 0, 다중 파일 0). 파일별 수는 itemlight 16·CLOUD 14·groundfire 10·smoke0 8·movemark 7·groundfiresmoke 5·exp6 2이고, work와 같다.

## 5. Y3 13~15 s stale 군집 판정(ESCALATE_SOL 4(a))

- **키 로그 시각 위치(새 방법, `keytime_lap1195.py`):** 키 로그의 `miss` 줄 수와 present의 누적 `hd_pack_misses`는 끝값이 정확히 같다(Y2 784 = 784, Y3 1,221 = 1,221). 그래서 둘을 맞추면 키 로그 줄의 시각을 정할 수 있다.
  - Y3의 첫 `0x467B00` 키는 400번째 miss 뒤에 생겼다. 누적 miss가 400에 이른 present는 **14.87 s**다.
  - 따라서 **13.1 s 245는 `0x467B00` 키 경로가 한 번도 돌기 전이다(직접 증거).**
- **같은 서명이 키 경로 코드 없는 DLL에도 있다(새 스크립트 재계산):**
  - lap1192 X2(lap1192 DLL, `0x467B00` 키 경로 없음): 13.127 s 249 → 15.227 s 255 → 15.277 s 59 → 15.328 s 79
  - lap1192 T0: 13.120 s 246 → 15.166 s 259
  - Y3: 13.076 s 245 → 14.926 s 242 → 15.175 s 79 → 15.223 s 75
  - 이번에 본 9 run(Y0~Y3·X1·X2·Q1·T1·T0) 가운데 3개에서 같은 쌍봉이 나왔고, 그중 2개는 이 코드가 없는 DLL이었다.
- **키 그리기 자체는 stale을 만들지 않는다:** Y1은 keyed 1,579호출·740만 px를 그렸지만 stale 최대는 91이다.
- **판정: (a) 수용.** 이 군집은 기존 서명(lap1187 backlog "15.5 s 선택 군집"과 같은 계열)이며 이번 변경과 무관하다. 켬/끔 반복 run은 요구하지 않는다. 다음 사전등록부터는 측정식에서 이 서명(13.1 s·약 15 s의 약 240~260 px 쌍봉과 그 꼬리)을 명시 제외한다.
- **(b) 수용.** 클립 경계의 시각 검증 대신 다음을 근거로 삼는다: `key_clip_cut` 1,410호출(Y1 1,391 + Y2 11 + Y3 8)에서 자기 검사 불일치 0, 클립 창 단언 테스트, 변이 n1·n2·n4·n6·n7·n12 RED. 키 그리기 영역은 자기 검사가 원본 출력과 일치함을 확인한 창 그대로다.
- **(c) 수용.** PB2가 `0x467B00` 16키 hit 상태로 pair PASS다. PB는 비회귀(키 미사용) 대조로만 둔다.
- **(d)** pair `trace_close FAIL`·`mirror_validator BLOCKED`는 기존 하네스 문제로 판정에 영향이 없다(lap1189 backlog).

## 6. 판정

**H-HDB2 `PASS(partial, 기술·격리)` 수용.**

| 항목 | 판정 | 근거 |
|---|---|---|
| B2-0 | PASS | 3/3 RED |
| B2-1 | PASS | 공유 코어 재사용, §2 |
| B2-2 | PASS | work 19/19 RED, 이번 회차 13종 중 RED 12 |
| B2-3 | PASS | 62/62 독립 귀속 |
| B2-4(i) | PASS | 아래 참고 |
| B2-4(ii) | PASS | PB2 |
| B2-4(iii) | 생략 | 화면 안 944 ≥ 300 |

B2-4(i) 근거:
- 시도 호출 keyed 100%
- 자기 검사 불일치 0
- `key_clip_cut` ≥1
- 안전 0
- p95 ≤ 끔+2
- `0x467580` 비회귀
- stale은 기존 서명 군집을 제외하면 끔 규모

집계: 판정 영향 불일치 0, 정정 0, 보강 3, 공개 2. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.
- 보강 3: 13.1 s 군집이 첫 키보다 앞섬, lap1192 X2도 같은 서명, 귀속 독립 재현
- 공개 2: 테스트 공백 n11, n8은 문자열 고정

## 7. 다음 work 사전등록(Sonnet) — H-HDB3: 좌우반전 가중표 혼합 `0x467FD0`·`0x4685C0` HD 키 경로

**정적 근거(이번 회차 `orig_4685C0.asm`·`orig_467FD0.asm`, 읽기 전용, 원본 SHA 일치).**
- **`0x467FD0` = `0x467580`의 좌우반전판(클립 없음).**
  - thiscall, 스택 5개(x·y·w·h는 하위 16비트 `movsx`, 다섯째 = 스트림), `ret 0x14`.
  - 행 시작 = `[ecx+0x1514] + y·[ecx+0x10] + x`.
  - 불투명 바이트는 `x + (int16)(w − col − 1)`에 쓴다(468040~46804D).
  - `FE n`은 col += n이다. 행은 col ≥ w에서 끝난다.
  - 혼합식은 `0x467580`과 같다: 팔레트 `+0x419A0`, 가중표 `+0x41CA0`, 역 LUT `+0x19A0`.
  - 클립이 없으므로 x < 0 또는 x+w > stride이면 이웃 행으로 넘어간다(기존 wrapper `wrap_calls`).
- **`0x4685C0` = `0x467B00`의 좌우반전판(클립 있음).**
  - 인자·문법·혼합식은 위와 같다. 쓰기 위치도 `x + (int16)(w − col − 1)`이다(4686CD~468705).
  - 클립은 `0x467B00`과 같은 `+0x4D0..+0x4DC`이고, 오른쪽·아래는 포함 경계다.
  - 위 잘린 행(`[esp+0x14]`)은 파싱하되 쓰지 않는다. 아래 잘린 행은 파싱하지 않는다.
  - 열은 화면 좌표 `x+w−1−col ∈ [left, right]`일 때만 쓴다. 구현은 `col ≥ (x+w−1−right)`(`[esp+0x18]`)이고 `col < w − (left−x)`(`[esp+0x1C]`)인 열이다.
  - 따라서 **화면 좌표의 클립 창은 `g1_blend_clip_window`를 그대로 쓰면 된다.** 스트림을 화면 방향으로 뒤집은 평면에서 crop 오프셋은 `(kx0−x, ky0−y)`다.
- **최근 run 규모(F0 구성, 화면 안 mirrored 호출):** `0x4685C0` Y0 1,056·Y1 233·Y2 71·Y3 297·X2 588·T1 40이고, 그 가운데 clipped가 대부분이다. `0x467FD0` Y0 286·Y1 16·Y2 56·Y3 43·X2 690·T1 26이고, 거의 전부 화면 안이다.
- **기존 반전 기반:** `g1_hd_asset.c`의 `is_flip_pack_writer`가 팩 행을 좌우 반전(`flip_pack_rows`)한 뒤 반전된 identity 마스크로 실루엣을 검사한다(H-HDU0·H-HDU1).

**단계.**
- **B3-0(테스트만, 이번 회차 생존 변이 막기):** n11 — 각 혼합 wrapper(`0x4672E0`·`0x467580`·`0x467B00`)의 키 블록이 diff 미러 성공 분기 안(`why = "reject_size"` else 분기보다 앞)에 있음을 단언한다. 변이 n11은 RED, 현재는 GREEN이어야 한다.
- **B3-1(C):** 공유 코어 `blend_key_apply`에 `flip` 인자를 더한다. 복제 코어는 금지한다.
  - 디코드한 idx/mask를 행마다 좌우 반전해 화면 방향 평면으로 만든다.
  - 그 평면으로 crop·자기 검사·identity bind를 한다.
  - writer id `0x467FD0`·`0x4685C0`은 asset 층의 반전 팩 경로(행 반전 + 반전 마스크 실루엣 검사)를 타게 하고 `hd_pack_blend_*` 카운트에도 넣는다.
  - `mirror_flip_blend`(`0x467FD0`): 화면 교집합 창으로 키를 시도한다. 원본이 넘어 쓴 칸(wrap)이 창 안에 들어오면 자기 검사가 불일치로 폴백시킨다. 이 경우를 카운트한다.
  - `mirror_blend_skip`(`0x4685C0`): 원본 호출 전에 읽은 클립으로 `g1_blend_clip_window` 창을 만들고, 빈 창이면 `key_clip_empty`다.
  - 두 wrapper 모두 키는 diff 미러가 성공한 분기 안에서만 시도하고, 폴백 때는 diff 결과를 유지한다.
  - 끔 env는 `SYW2_G1_HD_PACK_BLEND=0`을 공유한다. `SYW2_G1_HD_PACK_FLIP=0`일 때의 동작(권장: 두 writer 키 끔)을 정하고 테스트로 고정한다.
  - 카운터: `blend_467FD0_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels`, 같은 이름의 `blend_4685C0_*`, `blend_4685C0_key_clip_cut/key_clip_empty`.
- **B3-2(호스트 테스트, RED→GREEN):**
  - 비대칭 스트림에서 원본 asm을 그대로 옮긴 참조 모델 출력과 키 자기 검사 평면이 같은지(두 writer).
  - 화면 왼쪽 클립이 스트림 오른쪽 끝 열을 자르는지, 포함 경계, 위 잘린 행의 연속성, 빈 창.
  - 팩 프레임이 반전된 채 창 오프셋으로 그려지는지.
  - 변이는 RED여야 한다: 반전 생략, 반전 전(스트림 방향) 평면을 화면 오프셋 `(kx0−x)`로 crop(스트림 방향에서 맞는 x 오프셋은 `x+w−kx1`), 팩 반전 생략, 클립을 원본 뒤에 읽기, writer id 교체, weights NULL, 키 블록을 성공 분기 밖으로.
- **B3-3(귀속):** 키 로그의 두 writer digest를 6개 폴더 `.spr` 프레임에 귀속한다(독립 헤더 파서, 미귀속 수 기록). 귀속된 파일로 팩을 만든다(team-safe 초안 stand-in, 확장 이름 포함, lap1194 `pack_hdb2b` 파일 포함). 실루엣이 비대칭인 hit 키 수를 센다(방향 입증, H-HDU0 방식).
- **B3-4(run):**
  - (i) lap1194 F0 구성(dwell 56)으로 켬 2 run과, 같은 팩에 `SYW2_G1_HD_PACK_BLEND=0`인 끔 1 run.
  - (ii) save006 pair 1회. 두 writer 가운데 하나라도 키 로그 hit가 없으면, 그 장면 digest를 팩에 더해 1회 다시 돈다(lap1194 PB2 방식).

**측정식(합격).**
- B3-0·B3-2 변이 전부 RED.
- **B3-4(i), 두 writer 각각:**
  - 키를 시도한 호출 가운데 팩 귀속 키의 keyed ≥95%. 빈 창·버퍼 초과·팩에 없는 파일은 따로 적는다.
  - 자기 검사 불일치는 `0x4685C0` 0이다. `0x467FD0`은 wrap 호출을 뺀 나머지에서 0이다.
  - `0x4685C0`은 `key_clip_cut` ≥1(0이면 그 항목만 SKIP).
  - 비대칭 실루엣 hit 키 ≥1.
- **B3-4(i), 공통:**
  - 안전 7종·dropped 0.
  - p95 ≤ 끔+2.
  - stale ≤ 끔 규모. **단 기존 서명 군집(PS3 약 13.1 s와 약 14.9~15.3 s의 240~260 px 쌍봉과 그 뒤 ≤100 px 꼬리; lap1192 X2·T0·lap1194 Y3)은 제외하고, 그 밖의 새 군집이 0이어야 한다.**
  - `0x467580`·`0x467B00` keyed·불일치는 lap1194 수준을 유지한다(비회귀).
- B3-4(ii) pair PASS.
- 안전: 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 20 GB 미만이면 자기 회차 옛 사본부터 정리하고, 5 GB 미만이면 run을 시작하지 않는다.
- **비목표:** 실제 업스케일 화질, 기본 켬·사용자 전달, 남은 충돌 3개, 7인자 `0x4678C0`·반전 7인자 sibling(그다음 후보), 기존 서명 군집 원인 규명.
- **중단:** 실패 가설 2회 또는 60분. 키 그리기가 잘못된 방향이나 클립 밖에 그린 증거(자기 검사 불일치 급증·HUD 위 얼룩)가 나오면 즉시 끄고 근거만 남긴다. run 대기는 PID `kill -0` 또는 `.exit` 파일로 한다(`pgrep -f` 자기 일치 금지). 커밋 금지, 원본/참고 쓰기 금지. 산출물은 공유 temp `<날짜>_lap<N>_work_hdb3/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수) 순서로 한다.
- **backlog 갱신:** 기존 서명 stale 쌍봉(13.1 s·약 15 s, 약 1/3 run, 블렌드 키 경로와 무관 — lap1187 "15.5 s 선택 군집" 계열)을 하나의 항목으로 합친다. 경미: `mirror_blend_clip`은 버퍼 초과 검사가 창 검사보다 앞이라, 크고 클립 밖인 호출을 fallback으로 센다.

## 8. 검사

- 검사 결과는 STATUS 검증 줄에 보강한다. 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1194 full PASS(2016 passed) 그대로이므로 전체 `make check`는 SKIP한다.

## 다음 행동

work(Sonnet) H-HDB3(§7)를 진행한다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.

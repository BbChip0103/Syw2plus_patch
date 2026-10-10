# 2026-10-09 | lap 1198 | G1 work — H-HDB4: 7인자 가중 혼합 `0x4678C0`·반전 `0x468360` HD 키 경로

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1197 middle 사전등록 §7(`20261009_lap1197_middle_g1_hdb3_review_hdb4_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 러너 값 `loop/.lap_counter` = 1198(프롬프트 증거의 lap=1197은 직전 값). 디스크 여유 시작 21 GB, 끝 **11 GB**(run 8개의 prefix·output 각 약 1.2 GB, `game` 사본은 하네스가 종료 때 삭제 — 아래 한계 6).
- 가설: `0x4678C0`은 `0x467B00`과 같은 클립·같은 스트림 문법에 원천 색만 `remap[token]`, 혼합 표만 level 슬라이스 DWORD 표 `renderer+0x43CA0`로 바뀐 것이고, `0x468360`은 `0x4685C0`(우→좌)에 같은 두 차이를 더한 것이다. 슬라이스는 0x467580의 int16 표와 같은 64×64 모양이라, 호출 때 level 슬라이스를 int16 표로 복사하면 H-HDB1~3 공유 코어(`blend_key_apply`·`g1_blend_selfcheck`·`g1_blend_apply_hd`)를 그대로 쓸 수 있다. remap은 tinted 경로의 LUT(asset 층이 팩 프레임에 적용)와 같다.
- 예상 PASS/FAIL: 사전등록 §7(B4-0(3)·B4-2 변이 전부 RED · 두 writer 각각 keyed ≥95%·자기 검사 불일치 0·`key_clip_cut` ≥1·`0x468360` 비대칭 hit ≥1 · 안전 7종·dropped 0·p95 ≤ 끔+2 · save000 stale ≤ 끔 · pair 켬 2회(HOLD면 끔과 같은 사유만) · 네 기존 writer 비회귀 · 원본 EXE SHA 불변). **level 범위·표 크기를 정적으로 확정 못 하면 BLOCKED**.

## B4-0 정적 확정 (원본 EXE SHA `b56986e0…` 읽기 전용 `objdump -d -M intel`; 공유 temp `20261009_lap1198_work_hdb4/full.asm`)

1. **level 슬라이스 수 = 10 (표 크기 0x28000 B).** 표 구성 함수 `0x4654D0`: 바깥 변수 `v`가 0,10,…,90(`add ecx,0xa; cmp ecx,0x64; jl`)이고 슬라이스마다 `64×64` DWORD를 `renderer+0x43CA0`부터 **포인터를 이어서**(슬라이스마다 `lea`를 다시 하지 않음, `eax`가 `[esp+0x14]`로 계속 전진) 쓴다 → 10슬라이스 × 16,384 B = `+0x43CA0 .. +0x6BCA0`. 쓰는 코드는 이것뿐이다(`43ca0` 참조 전수: 구성 `0x4654DF` 1곳, 읽기 `0x4674DA/4674F9/467522/467A5F/467A76/467AA3/467F2A/467F49/467F74/468512/468531/46855A`).
2. **표 항목 식:** 슬라이스 `level`(v = 10·level), 인덱스 `[d][s]`: `c = max(0, s − ⌊v·s/100⌋)`(`0x51EB851F` 곱셈 = 100으로 나눗셈), `hi = max(d, c)`, `lo = min(d, c)`, 항목 = `hi + ((64−hi)>>6)·lo` = `max(d, c)`(`(64−hi)>>6`은 hi=0일 때만 1이고 그때 lo=0). 모든 항목 0..63 → int16으로 손실 없이 변환된다. level 0은 `max(d, s)`.
3. **`0x4678C0` 읽기:** 채널마다 `T[(((level<<6) + d_c)<<6) + s_c]`(`shl esi,6`; `lea … *4 + 0x43CA0`), `d_c`·`s_c` = 팔레트 `renderer+0x419A0` 채널, `s = remap[token]`(`mov dl,[eax+ebx]`, ebx = 6번째 인자), 이어서 `inverse[((t0<<6)+t1)<<6 + t2]`(`+0x19A0`). 클립 4값은 `0x467B00`과 같이 쓰기 전에 `[ecx+0x4D0..0x4DC]`에서 읽는다.
4. **`0x468360` (이번 회차에 처음 확정):** `0x4685C0`과 같은 구조 + remap + level. 쓰기 열 `x + (int16)(w − col − 1)`(`468482: sub esi,edi; dec esi` … `4684A8: movsx esi,si; lea ebp,[esi+edx]`), 클립 비교는 `4683A6`~`4683E5`(좌/상/우/하 필드 `+0x4D0/4D4/4D8/4DC`, 오른쪽·아래 포함), remap = `mov dl,[eax+ebx]`(ebx = `[esp+0x44]`), level = `movsx esi, WORD [esp+0x48]; shl esi,6`, DWORD 표 읽기 `468512/468531/46855A`. 클립을 쓰기 열 기준으로 적용하는 부분은 `0x4685C0`과 동일해 H-HDB3의 화면 방향 평면·클립 창이 그대로 맞는다.
5. **level의 출처:** 래퍼 `0x41A7D0`(→`0x4678C0`)·`0x41A890`(→`0x468360`)·`0x41A950`·`0x41AA10`의 호출자(`0x478577~0x4785BC`, `0x478CA7~0x478CE4` 등)가 객체 안 **부호 있는 바이트** `[obj + 클래스바이트 + 0x62]`를 `movsx`로 읽어 0이 아닐 때 넘긴다(remap = `0x4F2D9C + (소유자 바이트 << 8)`). 이 바이트가 0..9인지는 정적으로 묶지 못했다 → **표 크기는 정적으로 확정했고 level 값 상한은 확정하지 못했다.** 그래서 추측 상한을 쓰지 않고 호출 때 `0 ≤ level ≤ 9`와 슬라이스 항목의 int16 적합성을 확인해 벗어나면 키 경로를 거부한다(`key_level_rejects`, 원본은 그대로 실행). 사전등록의 BLOCKED 조건은 "표 크기 미확정"이므로 해당하지 않는다.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_blend_key.h` | `G1_BLEND_LEVEL_SLICES 10u`, `g1_blend_level_weights(table32, level, out16)`(level<0·≥10 또는 항목이 int16 밖이면 0), `g1_blend_remap_plane(remap, idx, mask, count, out)`(불투명 칸만 `remap[idx]`). 둘 다 memcpy 호출 금지 속성 |
| `tools/inmm_stub/g1_mirror2x.c` | `G1BlendKeyStats.key_level_rejects`, 통계 `g_blend_clip7_key`·`g_blend_flip7_key`, 접근자·리셋. `blend_key_apply`: `remapped = writer ∈ {0x4678C0, 0x468360}`, `flip`에 `0x468360` 추가(시그니처 불변·복제 코어 없음). remapped이면 디코드 전에 level 슬라이스→int16 `weights`(실패 시 `++key_level_rejects; return FALSE`), 크롭 뒤 remap 평면으로 자기 검사, `g1_hd_asset_begin_with_aux`(remap 포인터·digest), identity는 스트림 색 그대로 bind. `blend_key_set_remap(remap, level)`가 정적 변수로 호출 직전에 remap·`(int16_t)level`을 넘기고 호출 뒤 `g_blend_key_remap = NULL`. `mirror_blend_clip7`/`mirror_blend_flip7`: `0x467B00`/`0x4685C0` 래퍼와 같은 형태(원본 호출 **전에** 클립 4값 읽기 → `g1_blend_clip_window` → `blend_key_snapshot`·창 pre-draw crop → 원본 → 기존 diff 미러 성공 분기 안에서 키) |
| `tools/inmm_stub/g1_hd_asset.c` | `G1_HD_BLEND_CLIP7/FLIP7`, `is_remap_blend_writer`: LUT 캡처(`capture_lut`)·팩 프레임 LUT 적용·`hd_pack_blend_*` 카운트(LUT 거부 포함)는 tinted writer와 같은 경로, `is_flip_blend_writer`에 `0x468360`(팩 행 반전). **`SYW2_G1_HD_PACK_TINTED=0`이면 두 writer의 팩도 끈다**(`PACK_SKIP_AUX` → Scale2x, 키는 `key_fallbacks`로 셈), `PACK_BLEND=0` 또는 `PACK_FLIP=0`(반전 `0x468360`만)이면 키 시도 자체를 끈다 |
| `tools/inmm_stub/g1_mirror2x.h`·`direct_draw_trace.c` | 접근자 16개, present metrics `blend_4678C0_*`·`blend_468360_*` 각 `keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels/key_clip_cut/key_clip_empty/key_level_rejects`. **버그 수리:** `mirror_details` 12,288→14,336, 트레이스 줄 버퍼 `line[10240]`→`16384`(아래 한계 1) |
| `tests/test_g1_blend_key.py` | 신규 12개(총 41): 슬라이스·거부(B4-0(2)), 전 destination×token×level 원본 식 일치(B4-2 참조 모델 `builder_entry`·`original_level`을 `0x4654D0`·`0x4678C0` asm에서 옮김), 스트림 수준 참조(우→좌·클립 4면·빈 창, level·remap·flip을 하나씩 틀린 입력은 자기 검사 실패), 잘못된 반전 방향, 래퍼 2개 문자열 계약, **클립 창이 정확히 렌더러 4필드에서만 만들어짐(4개 클립 래퍼; lap1197 생존 변이 a4 차단, B4-0(3))**, 코어 거부·평면·bind, asset 배선, 트레이스 필드·리셋, 줄 버퍼 용량. 기존 `_KEY_WRAPPERS` n11 목록에 두 래퍼 추가, 기존 문자열 3개를 새 정의에 맞게 갱신(`flip` 파생식·`is_flip_blend_writer`·blend 카운트 — 약화 아님) |
| `tests/test_g1_rect_fill.py` | `mirror_details[12288]` 핀을 14336으로 갱신 |

파일 SHA256 앞 16자(최종; run S3 시작 이후 `tools/`·`patches/`·`tests/` 변경 0 = `find -newer` 빈 출력 2회 `newer_at_start3/end3.txt`): `g1_blend_key.h 4d2b08845499ec69`·`g1_mirror2x.c 89838938663bc2c3`·`g1_mirror2x.h 7311380621a2b056`·`g1_hd_asset.c fcf6e9761bb5f384`·`g1_hd_asset.h 61173d6bd31309ff`(불변)·`direct_draw_trace.c 63172d3775ca80d5`·`_inmm.dll ef21d7bb0aa3debe`(S3·S4·Q1·F1 공통; 무효 run S1·S2·Q0·D0의 DLL `ad4f8ce13f1e552b`)·`test_g1_blend_key.py 83c37e87b0ea143d`·`test_g1_rect_fill.py 15ecb5fc8fc352cb`. 원본 EXE SHA `b56986e0…` run 전·후 MATCH(`orig_sha_before.txt`·`before2`·`before3`·`after3`). 공유 temp `20261009_lap1198_work_hdb4/`.

## 측정

**B4-2 변이(격리 사본 `mut/mutation_lap1198.py`, 베이스 GREEN):** 28/28 RED(`mut/mutation_lap1198.txt`; 첫 패스 `…_firstpass.txt`는 26 RED + 생존 1(c7: begin 호출 분기를 `0 ?`로 바꿔도 문자열 계약이 남음 → 테스트를 `if (remapped ? !…begin_with_aux(` 접두까지 핀) + 별도 c16/c17). 사전등록 목록 대응: remap 생략 h4·level 무시(0 고정) h1·표 폭 int16 오독 h2·level 범위 검사 제거 h3·반전 생략 c1(+ 잘못된 반전 방향 호스트 테스트)·**클립 원본 뒤 읽기 c17**·**키 블록 성공 분기 밖 c16(처음엔 SURVIVED → `_KEY_WRAPPERS`에 두 래퍼를 넣어 RED)**·**a4 클립 우회 c3**. 그 밖: 슬라이스 수 11(h6), 항목 int16 검사 제거(h5), remap 설정 순서(c5)·미해제(c12), level 부호 확장(c6), begin 평면 호출(c7), level 거부 미계수(c8), 반전 writer 스위치(c9), 변환 평면 bind(c10), 0x467580 표 사용(c11), cut 미계수(c13), snapshot x0(c14), 코어에 비절단 창(c15), asset LUT 캡처/적용(a1·a2), 팩 반전 행(a3·a4), blend 카운트(a5), 트레이스 level_rejects(t1).

**테스트:** `tests/test_g1_blend_key.py`·`test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py`·`test_g1_rect_fill.py` **239 passed/16.9s**. `make lint`·`make typecheck` PASS.

**B4-3 귀속(`scripts/attrib.py`, 독립 헤더 파서 — `.spr` 오프셋 표 재유도 + 앞 128 B FNV-1a·w·h):** 발견 run D0(`pack_hdb2b`)의 키 로그 digest = `0x4678C0` **15개**·`0x468360` **5개**(미귀속 0), 전부 `char/cannon2c1.spr`·`char/cannon2c2.spr` 두 파일(두 digest는 두 파일에 공통). 팩 `pack_hdb4` = `pack_hdb2b`(lap1194, `pack_hdb2` + `fnt/itemlight`) + 두 파일의 bicubic stand-in 초안(도구 `extract --only`·`draft`·`pack --pal …/pal/imjin2.pal`; 새 파일 188개 `idx8` + `.amb` 2개, 이름 충돌 0, 해시 `9eaf2b1afad92fe1`, 원본 `.spr` SHA `ff6f2b73…`·`4b4a32a8…`). 키 로그 21줄(`0x4678C0` 16·`0x468360` 5)이 **전부 `lut_hit`**(remap LUT 적용 팩 hit). 비대칭 실루엣 hit 키(`scripts/asym.py`): `0x468360` **5/5**(대칭 0)이고 `0x4678C0` 15/15 — 반전 방향의 키 단위 증거.

**B4-4 하네스:** save000 pair `--fixture save000 --scene-actions none --performance-window --hd-source scale2x`(lap1063 `s0` 구성, present trace 켬), F0 new-game `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`, 키 로그 켬, `scripts/{run,seqD,seqR,seqR2}.sh`.

| run | 구성 | ps3 present·s | p95 | stale 최대 | 안전 7종·dropped | `0x4678C0` 화면 안(mirrored) → keyed / 폴백 | `key_clip_cut` | 불일치/px | `0x468360` 화면 안 → keyed / 폴백 | cut | 불일치/px | level 거부 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0 (발견, `pack_hdb2b`) | 켬 | 410·20 | 7 | 0 | 0·0 | 184 → 0 / 184(팩 없음) | 0 | 0 / 249,736 | 8 → 0 / 8 | 0 | 0 / 6,446 | 0 |
| **S3** | 켬, `pack_hdb4` | 409·20 | 7 | 0 | 0·0 | 184 → **184 / 0** | 184 | **0** / 249,736 | 8 → **8 / 0** | 8 | **0** / 6,446 | 0 |
| **S4** | 켬, `pack_hdb4` | 410·20 | 7 | 0 | 0·0 | 184 → **184 / 0** | 184 | **0** / 249,736 | 8 → **8 / 0** | 8 | **0** / 6,446 | 0 |
| Q1 | 끔 `PACK_BLEND=0` | 410·20 | 7 | 0 | 0·0 | 184 → 키 시도 없음 | — | — | 8 → 시도 없음 | — | — | — |
| F1 | 켬, new-game | 6,017·301 | 6 | 92(140.9 s 79·141.1 s 92·225.4 s 92) | 0·0(주 8) | 호출 0 | — | — | 호출 0 | — | — | — |

- **합격 항목:** 두 writer 모두 키를 시도한 호출의 keyed **100%**(≥95%), 자기 검사 불일치 **0**(`0x4678C0` 249,736 px·`0x468360` 6,446 px), `key_clip_cut` 184·8(≥1), `0x468360` 비대칭 hit 키 5(≥1), 안전 7종 0·dropped 0, p95 7·7 ≤ 끔 7+2, save000 stale 0(끔 0). level 거부 0은 S3·S4 합 384호출 모두 level이 0..9였다는 뜻이다(값 분포는 기록하지 않았다).
- **네 기존 writer 비회귀:** save000(S3·S4 대 발견 D0, 같은 장면): `0x467B00` 폴백 654·`0x467580` 폴백 504·`0x467FD0` 폴백 102·`0x4685C0` 화면 안 0 — D0와 같은 값(폴백은 이 장면 digest가 팩에 없어서), 자기 검사 불일치 전부 0, keyed 증감은 run 길이 차이(예 `0x467B00` 2,123→2,120). **F1(new-game, 팩에 효과 있는 장면):** `0x467B00` 1,025/1,027 keyed(폴백 0)·`0x467580` 470/470·`0x4685C0` 309/309·`0x467FD0` 152/152, 전부 불일치 0, `hd_pack_blend_hits` 68.
- **pair 판정:** S3·S4·Q1·D0 네 run의 `pair-result.json` `status` = **HOLD**(exit 2)이고 모든 게이트 상태가 **서로 완전히 같다**(차이 0): `owner0_hq_type` UNKNOWN 2·`candidate.mirror_validator`·selection/drag/minimap/production 캡처·V2/V2s/V2q BLOCKED·`input_effect_comparison` HOLD — lap1063 `s0` HOLD와 같은 save000 기존 사유(`--scene-actions none`), `scene_state_equal` true. 사전등록 "끔과 같은 사유만 허용" 충족.
- **F1 stale:** 3 present(79·92·92 px)는 lap1196 Q0(끔)의 225.2 s 79 px 계열과 같은 기존 서명 시각대이고 두 writer 호출 0인 run이라 이번 변경과 무관.
- **원본 보호:** EXE SHA `b56986e0…` 전·후 MATCH. `local/runtime/lap1198_hdb4_*` 8개의 `game` 사본 없음(prefix·manifest·output 보존).

## 판정

**B4-0 PASS**(level 슬라이스 10 정적 확정·`0x468360` 확정, a4 차단 테스트) · **B4-1 PASS**(공유 코어에 `remapped`·flip 파생, 복제 코어 0) · **B4-2 PASS**(28/28 RED, 참조 모델 호스트 테스트) · **B4-3 PASS**(20 digest 전부 귀속·미귀속 0) · **B4-4 PASS**(위 항목 전부, pair는 끔과 동일한 기존 HOLD). 전체 `PASS(partial, 기술·격리)` 후보. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 한계·공개

1. **내 실수 1건(수리·공개):** 첫 run S1·S2·Q0(DLL `ad4f8ce1…`)에서 `mirror2x_metrics` 이벤트가 사라졌다. 원인 = 내가 늘린 카운터 때문에 metrics 레코드가 트레이스 줄 버퍼 `line[10240]`을 넘어 `trace_record_serialize`가 실패하고 이벤트가 `event_limit` 오버플로우(dropped 1)로 버려졌다(조용한 실패, 메모리 손상 없음; D0는 겨우 아래였다). 줄 버퍼를 16,384로 키우고 `mirror_details + 1,024 + 2 ≤ 줄 버퍼`를 단언하는 테스트를 더한 뒤 **S3·S4·Q1·F1을 새로 돌렸다.** S1·S2·Q0는 카운터 근거에서 제외(키 로그는 S1·S2 모두 `lut_hit` 16+5로 S3와 같다).
2. 팩 그림은 bicubic stand-in(실제 업스케일 화질 아님). 반전 HD 그림을 육안으로 본 run은 없다(같은 장면 두 run의 캡처도 구름 움직임으로 2만 px 이상 달라 직접 비교가 안 된다). 방향·클립·remap·level의 증거는 자기 검사(원본 1x 출력 = 같은 식)·참조 모델 호스트 테스트·반전 비대칭 실루엣 hit 5/5·remap LUT 적용 `lut_hit` 21/21이다.
3. level 값 분포·상한은 정적으로 묶지 못했고(위 5.), 관측은 384호출 모두 0..9이다. 범위 밖이면 키 경로만 거부하고 원본은 그대로 그린다.
4. 두 writer의 실호출은 save000 장면의 `char/cannon2c1`·`cannon2c2` 두 파일 20 digest뿐이다(new-game F0 구성에서는 0). `cannon2c` 효과의 의미(어떤 연출인지)는 확인하지 않았다.
5. 같은 장면에서 `0x467B00`·`0x467580` 등의 폴백은 이 장면 digest가 팩에 없어서다(키 시도 가운데 hit 비율은 이번 합격 항목이 아님, 비회귀는 D0 대비 동일 값과 F1의 100%로 본다).
6. **디스크:** 끝 여유 11 GB(20 GB 미만). `game` 사본은 이미 없고 남은 것은 run당 약 1.2 GB prefix·output이라 규칙상 내가 지울 수 있는 것이 없다(`rm -rf` 금지, 회수는 archive·restore 검증 절차). **다음 run은 5 GB 미만이면 시작 금지**이며 약 5회 run 뒤 도달한다 → middle이 prefix archive 회수를 먼저 판단해야 한다.
7. 정적 테스트 일부는 문자열 계약이다(변이로 RED 확인). `0x467E60`(7인자 무클립 반전, 2 run만 관측)·남은 이름 충돌 3개·실제 업스케일 화질·기본 켬은 비목표다.
8. **F1 트레이스 aggregate 줄 손실(하네스 한계, 이번 변경 무관 판단):** F1 summary `dropped_count` 0·`primary_present_dropped` 0이지만 `aggregate_output_dropped_count` 45다. 이벤트 상한 8,192를 present 이벤트 7,103개(lap1196 P0 7,014·P1 7,006)가 거의 채워 끝에서 method aggregate 줄 45개가 못 나갔다 — present·metrics 이벤트는 모두 나갔고(metrics를 이 run에서 읽었다), 길이 때문이 아니라 개수 때문이다. 같은 구성에서 present 수가 run마다 ±1% 흔들리는 기존 현상이다.

## 다음 행동

middle(Opus)이 H-HDB4를 검수(`0x468360`/`0x4654D0`/호출자 독립 역어셈블, 코어 remapped 분기·level 거부·remap 평면, 변이 재현, S3·S4·Q1·F1 trace·키 로그·귀속·비대칭 새 스크립트 재계산, 줄 버퍼 수리 타당성)한 뒤 다음 후보(`0x467E60` 또는 효과 갈래 마감 판정)를 사전등록하거나 마감을 판정한다. 디스크 회수 필요성도 판단한다. 사용자 G1 시험 결과가 오면 최우선.

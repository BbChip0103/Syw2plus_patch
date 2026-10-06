# 2026-10-05 | lap1019 | G1 H-B 독립 검수 → PASS(partial) 수용, 다음 work H-B2(표본 writer 호출 단위 귀속 + 조건부 타일 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행 0·source 변경 0·커밋 0.
- 가설 / 사용자 관찰(lap1018 work 주장): hook `0x467580` diff 미러(v2 화면 교집합)로 save000 stale 마지막 40 중앙값이 7,694.5→424.5(−94.5%)로 줄었다. 그러나 표본 B는 0이 아니고(135), A 41·C 210은 그대로다. 그래서 세 표본 점의 램프 writer는 `0x467580`이 아니거나 일부만 해당한다.
- 예상 PASS / FAIL 조건(lap1017 §4 B-0~B-4): 검수 기준은 새 스크립트 재계산 불일치 0, wrapper 읽기 범위가 화면 안(x0..x1≤800·y0..y1≤600·320×128 한도), 기존 H-L 경로 불변.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1019_middle_review/`의 `recalc_lap1019.py`(SHA256 `590ea83d24c4f4573cd33f6b58c0787fcf9858dfbf763338e7cbf1d73237de0f`) → `recalc_lap1019.json`(`d6b35232f9c03992b1a31af7e5fb8821431ae495ea23eb0ef7d3d522fcc5842b`)·`recalc_stdout.txt`. 모두 uncommitted.
- 원본 SHA / fixture: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`). SHA를 재계산했고 objdump는 read-only(`/tmp` 출력)로만 실행했다. save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 8 run 모두 `source_unchanged` 4/4·cleanup 4/4. 활성8인 부하 증명 아님.
- 검수한 source: 현재 `tools/inmm_stub/g1_mirror2x.c` SHA `6932c3ac812c48b9…`는 v2 run bridge 사본과 같다. `g1_mirror2x.h` `0a500cbf…`, `direct_draw_trace.c` `49e385b0…`, `tests/test_g1_rect_fill.py` `c4468fde…`는 work 기록과 같다.

## 1. 독립 재계산(`analyze_hb.py`·`ff.py`·`analyze_hb_s6.py`·제품 helper 미사용)

표본 stale present 계산법: layer_drift `s` 레코드는 값이 바뀔 때만 남는다. 그래서 레코드 p부터 같은 표본의 다음 레코드 직전까지 그 상태가 유지된다고 본다. 마지막 레코드는 trace_raw PS3 present 수까지 유지된다. 그 구간에서 `cov==1 && scr≠snap`인 present를 센다. 같은 스크립트로 lap1016 기준 run도 다시 계산했다.

| 항목 | work | 재계산 |
|---|---|---|
| lap1016 기준 표본 A/B/C | 41/**178**/210(`ff.py`) | 41/**180**/210(r1=r2, lap1016 기록 180과 일치) |
| save000 stale 마지막40 중앙값 v1 r1/r2 | 452.5/452.5 | 452.5/452.5 |
| save000 v2 r1/r2 | 424.5/424.5 | 424.5/424.5(PS3 present 412/410) |
| 표본 A/B/C v1·v2 4 run | 41/135/210 | 41/135/210 |
| 표본 stale 구간 | — | A 298..338, B 231..365(기준 231..410), C 129..338 |
| `blend_467580` v2 r1/r2 inv/mirrored | 3583·3589 / 3555·3561 | r1 3589/3561, r2 3583/3555(work 표는 r1·r2 순서를 바꿔 적음, 값은 같음) |
| v2 clipped/reject_size/bounds/target/guard | 921·923/28/0/0/0 | 같음. inv = mirrored + reject_size(3589=3561+28)라 무계수 경로 0 |
| v1 reject_bounds | 921·923 | 921/923 |
| save000 perf | p95 6~7, 비 0.99998~1.000005 | cand p95 7/6/6/7, 비 1.0000054/1.0000012/1.0000009/0.9999761, PASS |
| scene/cleanup/source | PASS | scene_state_equal true·4/4·4/4(8 run) |
| 안전 7종 | 0 | 0. 0이 아닌 계수는 `panel_transfer_mismatch_cleared`뿐(lap1013에서 판별력 없음으로 판정) |
| save006 `blend_467580` | inv 16·reject_size 16 | 4 run 같음(미러 0) |

**불일치 0.** 정정 2건(판정 영향 없음):
- B 기준값은 180이다. 따라서 감소는 180→135(−25%)다. work의 `ff.py` 178은 계산법 차이다.
- work 측정 표의 r1/r2 계수 순서가 바뀌어 있다.

### 1.1 save006 비회귀 보강(work 기록에 없던 관찰)
- v1 `s6_r1`은 PS3 present가 867개뿐이다. 816부터 끝까지 stale 16,652가 일정하게 남는다(마지막 40 중앙값 16,652).
- 이것은 **lap1000 H-L 수용 기준 r1(868 present)의 꼬리 16,652와 같다**. lap1000 r2/r3과 lap1018 나머지 3 run(present 886~900)은 780대에 1,328을 거쳐 0으로 끝난다.
- 결론: 짧은 run 변형에서 원래 있던 꼬리다. H-B와 무관하며 회귀가 아니다. 프레임 880 부재 run과 같은 계열이다.
- 원인은 미조사 backlog로 남긴다. B-3 판정(공통 38프레임 성분 D 24·신규 0)은 work와 같다.

## 2. wrapper diff(lap1016 bridge `41ac7bef…` 대비)
- 추가만 있다. hook 정의·`g_blend_wrle_*` 상태·getter·`mirror_blend_wrle`·설치·reset·restore가 추가됐다. 변경된 줄은 두 곳이다.
  - restore 결합식에 `!restored_blend_wrle`가 추가됐다.
  - `primitives_installed`에 `g_hook_blend_wrle.installed`가 추가됐다.
  - 기존 H-L `mirror_blend_rle` 본문은 바뀌지 않았다.
- **읽기 범위.**
  - 대상 조건: renderer `0xE5BF18`, 화면 buffer(캐시/패널 아님), stride 800..2048, 높이 600.
  - 교집합: x0=max(x,0), x1=min(x+w,800), y0=max(y,0), y1=min(y+h,600). 비면 `reject_bounds`, 320×128을 넘으면 `reject_size`.
  - before 복사는 `[y0,y1)×[x0,x1)`만 읽는다. buffer 행 안이고 전용 320×128 버퍼 안이다.
  - `g1_overlay_blt_apply`가 실패해도 `reject_size`로 센다.
- guard 처리는 H-L과 같다. `g_primitive_guard`를 읽기만 하고 설정하지 않는다. `0x467580` 본체에는 call이 없다.
- 남은 위험: 원본은 클립하지 않는다. 그래서 x<0 호출은 앞 행 끝에, y<0 호출은 buffer 앞에 쓰고, 이 쓰기는 추적되지 않는다. 표본 A(112,126)·C(302,9)는 화면 가장자리가 아니므로 이 경로로 설명되지 않는다.
- 이 hook은 env 게이트 없이 상시 설치된다. old bytes가 다르면 전체 설치를 거부하는데, 이는 기존 all-or-nothing 패턴이다.

## 3. 판정
**H-B PASS(partial) 수용.**
- B-0·B-2·B-3·B-4는 PASS다.
- B-1은 전체 −94.5%로 ≥50%를 충족했다. 그러나 표본 B=0 사전등록은 미달이다(135). 그래서 partial이다.
- `0x467580`이 save000 stale 면적의 대부분을 만들었다는 것은 확정이다.

### 3.1 새 근거 — B 사슬이 둘로 갈린다
v2 B 표본 레코드(`recalc_lap1019.json` 원자료 = v2 r1 layer_drift):
- **231..365**: `scr` 244→253 램프·211, `snap`은 89에서 고정이다. 미추적이다.
- **366 이후**: `scr` 253·55·252·251, `snap==scr`. **같은 값 계열인데 이제 추적된다**(lap1016에서는 410까지 미추적).

해석:
- 램프 244→253은 복원 없이 같은 화소에 반투명 혼합이 반복될 때 LUT 고정점으로 수렴하는 모양이다. 원본 W-B watch에 `0x467692` 244~251이 있었던 것과도 맞는다.
- 따라서 231..365의 미추적 쓰기는 다음 둘 중 하나다.
  - (H1) **미러되지 않은 `0x467580` 호출**: `reject_size` 28 = 교집합 >320×128이거나 apply 실패.
  - (H2) 같은 혼합표를 쓰는 **형제 writer**.
- 근거: 28회는 B 사슬의 231..365 값 변화 19회 이상을 덮을 수 있다. 화면이 present마다 복원되지 않으면 한 번 쓴 값이 지속된다.
- A·C는 4 run 모두 기준과 같은 값·구간이다. `0x467580` 미러가 이 두 점에 한 번도 반영되지 않았으므로 (H1) 또는 (H2)다.

### 3.2 형제 writer 정적 결정(read-only objdump, 원본 SHA 일치)
| 함수 | 프롤로그(hook 가능) | ret/인자 | 쓰기 명령(→watch EIP) | 호출 지점(전부 `mov ecx,0xE5BF18` 직후) |
|---|---|---|---|---|
| `0x467580`(H-B) | `51 0F BF 54 24 0C` | `ret 0x14`/5 | `0x46768E`(→`0x467692`) | `0x41A00D`, `0x41ABF5` |
| `0x467410` | `83 EC 08 53 56`(5 B, 상대 분기 없음) | `ret 0x1C`/7(x·y·w·h·RLE·remap표·가중치) | `0x46753B mov [esi+ebp-1],dl`(→`0x46753F`) | `0x41A7C7`, `0x41A93F` |
| `0x4676D0` | `83 EC 14 33 C0`(5 B) | `ret 0x14`/5 | `0x467883 mov [edi+ebp],al`(→`0x467886`) | `0x4044AE`, `0x41A5FD`, `0x41A765` |
| `0x4672E0`(H-L) | `51 53 56 8B F1 57` | `ret 0x14` | — | `0x41A59D`, `0x41A715` |

- `0x467410`과 `0x4676D0`은 `0x467580`·`0x4672E0`과 같은 그리기 루틴 `0x41A0xx..0x41ACxx`(`0x4044AE` 1곳만 예외)에서 같은 renderer로 호출된다.
- `0x467410`은 가중 혼합표 `renderer+0x43CA0`와 `+0x419A1`·`+0x15DE0` 표를 읽는다. 즉 같은 반투명 계열이다.
- census(`g1_census.c`)는 `0x4672E0`·`0x467580`만 계측한다. 형제 둘은 census에서 **보이지 않는다**. 따라서 lap1012 "C-1 residual 0"은 이 둘의 쓰기를 배제하지 못한다(residual은 계측 class 밖 변화만 센다. 다만 창 64 present 동안 A/B/C 쓰기 EIP는 `0x4662DE`·`0x467692`만 관측됐다).
- lap953 지도(`analysis/memory_maps/g1_blend_writers_4672e0_467580_lap953.md` 42행)도 두 함수를 "hit 없음·미확인"으로 남겼다.

### 3.3 work 제안 (a)(b)(c) 처리
- (a) 원본 lane census watch: lane마다 present 속도가 다르고(38/s 대 20/s) 궤적도 갈려 lap1017 C 긴장을 낳았다. 또 형제는 census 계측 밖이다. **불채택.** 같은 lane(candidate) 호출 단위 귀속이 더 결정적이다.
- (b) 형제 hook: 위 §3.2로 정적 결정을 마쳤다(둘 다 hook 가능). 미러 구현 전에 실제 귀속을 먼저 확인한다. 아래 H-B2 관측 hook에 포함한다.
- (c) save000 `--stale-mask` 부재: 잔여 위치 지도용이다. layer_drift 표본 귀속이 직접 답을 주므로 **backlog**로 둔다.

## 4. 다음 work 사전등록 — H-B2(표본 writer 호출 단위 귀속, 조건부 타일 미러)

목적: candidate lane 안에서 A(112,126)·B(437,463)·C(302,9) 화면 화소를 실제로 바꾼 **호출**을 특정한다. 같은 회차에 조건이 맞으면 최소 수리까지 한다.

### 4.1 구현 1 — 진단 전용(env `SYW2_G1_LAYER_DRIFT=1`일 때만 동작, 제품 경로 불변)
- (i) `mirror_blend_wrle`: 원본 호출 **전후**에 세 표본 화면 값을 읽는다(표본이 buffer 안이고 화면 대상일 때). 어느 하나라도 바뀌었거나 원래 사각형이 표본을 포함하면 layer_drift JSONL에 `{"t":"w","f":"467580","p":present,"x","y","w","h","why":mirrored|clipped|reject_size|reject_target|reject_bounds|guard,"sb":[A,B,C 이전],"sa":[A,B,C 이후]}`를 남긴다.
- (ii) 관측 전용 pass-through hook `0x467410`(old bytes `83 EC 08 53 56`, 7인자 `ret 0x1C`)·`0x4676D0`(old bytes `83 EC 14 33 C0`, 5인자 `ret 0x14`).
  - env가 켜졌을 때만 설치한다. 불일치면 설치를 거부하고 원복한다. 미러는 하지 않는다.
  - 호출 전후 표본 값을 읽고, (i)과 같은 형식(`f`=`467410`/`4676D0`, `why`=`observe`)으로 바뀐 경우만 기록한다. 호출 수 계수도 metrics에 넣는다.
  - 인자는 하위 16비트를 부호확장해 기록한다.
- (iii) 표본 값이 바뀌었는데 위 세 hook 어느 것도 그 present에 표본 변화를 기록하지 않은 경우를 present 끝에서 셀 수 있게 한다. 기존 `s` 레코드와 대조한다.
- 테스트: 소스 계약 RED→GREEN. 주소·old bytes·`ret` 주석·env 게이트·관측 hook이 미러를 호출하지 않음·JSONL 키를 확인한다.

### 4.2 실행
- save000 pair 2회: lap1018 v2와 같은 인자 `--hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift`, fresh runtime-root, 순차, game 사본 삭제.

### 4.3 판정(B2-0~B2-3)
- **B2-0 유효**: scene 동일, stale 마지막40 중앙값 424.5±10%(진단 on), 안전 7종 0, cleanup, source_unchanged. 관측 hook 설치 성공(불일치면 그 run은 BLOCKED로 기록).
- **B2-1 귀속(주)**: A·B·C 각각에서 stale 구간(A 298..338, B 231..365, C 129..338)의 `scr` 변화마다 이를 만든 `w` 레코드를 대응시킨다. 대응률과 `f`/`why` 분포를 보고한다.
  - PASS = 세 표본 모두 대응률 ≥90%이고 writer가 지목된다.
  - 대응 0인 표본은 "세 hook 밖 writer"로 UNKNOWN 판정한다.
- **B2-2 분기 → 같은 회차 조건부 수리(사전 허용, 테스트 추가·공개)**:
  - **(R1)** 지목된 쓰기가 `467580`의 `why=reject_size`(교집합 >320×128 또는 apply 실패)이면 → **타일 미러 변형**을 적용한다.
    - 전체 교집합 before를 800×600 정적 버퍼에 복사하고, 원본을 1회 호출한다.
    - 그다음 ≤320×128 타일마다 타일 before를 기존 320×128 버퍼로 옮겨 `g1_overlay_blt_apply`를 호출한다.
    - 계수 `blend_467580_tiled_calls`를 추가한다. 원본 호출 범위는 바꾸지 않는다.
    - 재실행 save000 pair 2회 + save006 비회귀 pair 2회를 한다.
  - **(R2)** 지목된 쓰기가 `467410` 또는 `4676D0`이면 → 그 함수에 H-B 동형 diff 미러를 붙인다(`0x467410`은 7인자, 상시 설치로 승격, 계수 9개). 재실행은 (R1)과 같다.
  - **(R3)** 지목된 쓰기가 `467580` `why=mirrored`인데 snapshot이 따라가지 않으면 → wrapper/apply 결함이다. 수리하지 않고 증거를 보존해 middle로 넘긴다.
  - 귀속 0이면 수리하지 않는다. 다음 middle이 원본 lane watch 또는 다른 writer 정적 조사를 정한다.
- **B2-3 수리 시 판정**: 표본별 stale present 감소(B 135·A 41·C 210 기준), 전체 stale 마지막40 중앙값(424.5 기준), save006 공통 38프레임 성분 D 24·신규 0·p95 ≤8ms·cov p50 ≥99%, save000 p95 ≤10ms·비 ≥0.95·안전 0.
- 금지: covered를 지우거나 표본을 피해 stale 수치만 줄이는 metric 회피, 기준·validator·gate·required_tags 변경, 원본/참고/raw/golden 쓰기.
- backlog(변경 없음): save000 `--stale-mask` 부재, save006 짧은 run 꼬리 16,652(§1.1), 성분 D, hold keydown 위상 경합, 가장자리 마우스 스크롤, 교집합 밖 wrap 쓰기 미추적.

## 5. 검증 / 남은 위험
- 이번 lap은 문서·재계산·read-only 정적 분석만 했다. focused 검사 결과는 STATUS에 보강한다.
- 전체 `make check`는 SKIP했다. source가 불변이고 lap1018 full PASS 1615가 유효하다. 다음 work가 DLL 변경 뒤 실행한다.
- 사용자 승인 상태: 기술 부분 수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-B2(위 §4).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1018 work, SHA256 `2e183ea86fd685ae9d1ef75a810f712b1ec8a4d9dc5e0a3e1d2ac150f28a577c`)

```
lap1018 work(Claude Code claude-sonnet-5-5) G1 H-B 인계 (마일스톤 경계 아님; 사전등록 B-1 "B 0"은 미달 = PASS(partial) → middle 독립 검수·다음 가설 정의 요청).
- 한 일: g1_mirror2x.c hook 0x467580(old bytes 51 0F BF 54 24 0C, ret 0x14)+wrapper mirror_blend_wrle(H-L 동형, v2에서 부분 화면 밖 호출은 화면 교집합만 미러, clipped_calls 계수)+계수 9개 blend_467580_*(g1_mirror2x.h·direct_draw_trace.c)+테스트(RED→GREEN), lint·typecheck PASS.
- 실행(순차, 전부 exit 2=기존 pair HOLD): save000 pair v1 2회·v2 2회(--fixture save000 --scene-actions none --performance-window --layer-drift), save006 비회귀 pair v1 2회·v2 2회. 공유 temp 20261005_lap1018_work_hb/.
- 결과: save000 stale 마지막40 중앙값 7,694.5→424.5(-94.5%, v1 452.5), hook 정상(invocations 3583·mirrored 3555·reject_target 0·reject_size 28). 단 표본 3점은 A 41·C 210 불변, B 178→135(0 아님) → 세 점의 램프 writer는 0x467580이 아니거나 일부만 해당. save006 공통 38프레임 교집합 = 성분 D 24(기준 동일)·신규 0·p95 7·cov p50 99.30%·안전 0·V2s production raw 기존 gate. 안전 7종 0·cleanup ok·ticks 비 0.99998~1.000005.
- middle이 확인할 것: v1/v2 layer_drift.jsonl·trace_raw·pair-result를 analyze_hb.py/ff.py 없이 새 스크립트로 재계산(stale 중앙값, 표본 stale present A 41·B 135·C 210 forward-fill, blend_467580 계수), g1_mirror2x.c wrapper diff가 env 없을 때도 H-L 경로를 바꾸지 않는지(교집합 variant가 읽기 범위를 벗어나지 않는지: x0..x1<=800·y0..y1<=600·320x128 한도), H-B PASS(partial) 수용 여부, 다음 가설(잔여 424.5 px·표본 A/B/C writer): (a) 원본 lane census watch를 candidate 램프 시각에 맞춰 A(112,126)·C(302,9) 또는 B 잔여에 건다 (b) 형제 0x467410(ret 0x1C)·0x4676D0 hook 정적 결정 (c) save000에서 --stale-mask가 stale_mask.bin을 못 만드는 원인.
- 기록: docs/history/laps/20261005_lap1018_work_g1_hb_blend467580_diff_mirror.md. 변경 uncommitted.
```

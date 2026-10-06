# 2026-10-05 | lap1021 | G1 middle — H-B2 독립 검수(B2-1 FAIL 수용) → work H-B3(후보 lane 화면 표본 DR 쓰기 watch) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋 0.
- 가설: lap1020 work H-B2의 B2-1 귀속 FAIL(표본 A/B/C writer = `0x467580`/`0x467410`/`0x4676D0` 밖)이 raw와 source로 재현되는가. 재현되면 다음 work를 정한다.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산한 불일치가 0이어야 한다. diff는 env 없을 때 불변이어야 한다. save006 env-off 비회귀(공통 38프레임 성분 D 24·신규 0)가 work 값과 같아야 한다.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1021_middle_review/`:
  - `recalc_lap1021.py` SHA256 `3a8ec92da1c5a7cec3d9af0778e63eeeacb486563a5232f84bd38f5e378eb2fa` → `recalc_lap1021.json` `eff2e5b08a2d735401d9bfe8101289dde409e2cd0a112595d524c9dd77211cae`·`recalc_stdout.txt` `3fe26cb0…d5f7`
  - `recalc_s6_lap1021.py` `a9f78370ffea4d532d2537c38988feef98897860d860a5da1a3df5f4a59ecf5d` → `recalc_s6_lap1021.json` `5b2b44d1106d05ec765ab6f03a19757d54eb943a00ea1bf05ad9387df3075898`
  - 모두 uncommitted.
- 원본 SHA / fixture: 원본 EXE `b56986e0…8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`). SHA를 재계산했고 objdump는 read-only(`/tmp/lap1021_text.asm`)로만 실행했다. save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명 아님.
- 검수한 source: 현재 `tools/inmm_stub/g1_mirror2x.c` `22818f41…b841`이다. 이것은 4 run(s0_r1/r2·s6_r1/r2)의 bridge 사본과 모두 같다. `g1_mirror2x.h` `15e2d291…`, `direct_draw_trace.c` `2ac96874…`, `tests/test_g1_rect_fill.py` `0b685f32…`는 work 기록과 같다. run exit 8개는 전부 2(기존 pair HOLD)다.

## 1. 독립 재계산(`analyze_hb2.py`·`contain.py`·제품 helper 미사용)

방법:
- `s` 레코드는 값이 바뀔 때만 남는다. 표본별로 연속한 `s` 레코드의 `scr`가 달라진 present를 "변화"로 센다.
- 같은 p에 그 표본의 `sb≠sa`인 `w` 레코드가 있으면 "대응"으로 센다.
- 대응 안 된 변화 집합이 `u` 레코드 p 집합과 같은지 대조한다.
- 표본 점을 포함하는 `w` 사각형 수를 표본별로 직접 센다.

| 항목 | work | 재계산(r1 = r2) |
|---|---|---|
| 레코드 h/s/r/e/w/u | — | 1/60/221/9/93/49, 두 run 같음 |
| `w` 함수·이유 | 전부 `467580`·`mirrored` | 93/93 `467580`·`mirrored` |
| A 변화/대응/u | 5/0/5, p298..339 | 5/0/5, p298..339, u 집합 = 미대응 집합 |
| B 변화/대응/u | 24/5/19, 미설명 168..348 | 24/5/19, 미대응 168..348, 대응 p375·381·387·390·405 |
| C 변화/대응/u | 25/0/25, p129..339 | 25/0/25, p129..339 |
| 포함 호출 A/B/C | 0/63/30 | 0/63/30. C는 p27..56뿐이고 30개 모두 C 값 불변 |
| B 포함 호출 중 `sb==sa` | **48** | **18**(정정, 아래) |
| 사각형 밖에서 표본 값이 바뀐 `w` | — | 0(A/B/C) |
| `drift_467410`/`4676D0` installed·invocations·changed | 1·0·0 / 1·0·0 | 같음(trace_raw 최종값) |
| `blend_467580` inv/mirrored/reject_size/clipped | — | 3583/3555/28/921, bounds·target·guard 0 |
| `drift_unattributed` | 5/19/25 | [5,19,25] |
| save000 perf | p95 7, 19.95/20.00 Hz | p95 cand 7/7·기준 1, tick 비 0.9975/1.0000048, PASS |
| save006 env-off(stale_mask.bin 자체 파서) | 공통 38프레임 D 24·신규 0 | 300..620 38프레임 r1∩r2 = **24 px, y515..520×x616..619**. 880 포함 39프레임은 0. lap1018 v2 s6 2 run과 4-run 교집합도 같다. drift 계수 전부 0·hook 미설치·`blend_467580` inv 16·reject_size 16 |

**판정 영향 불일치는 0이다.** 정정 2건:
- work의 "B 63(그중 `sb==sa` 48)"은 B 기준 값이 아니다. 48은 전체 93 `w` 중 세 표본이 모두 불변인 수다. B 기준으로는 63 중 18이 불변, **45가 B를 바꿨다**.
- work의 "대응 366..": `s` 기준 대응 변화는 p375·381·387·390·405 5건이다. `w`가 B를 바꾼 호출은 p366..410에 present당 정확히 1건씩 45건이다.

### 1.1 새 근거 — B 화면 점은 매 present 배경으로 리셋된다
- p366..410의 45건은 모두 `sb`=89다. 즉 B 점은 매 present 사이에 hook 밖 writer가 배경값 89로 되돌린다. 그 뒤 `0x467580`이 253/55/252/251을 칠한다.
- 같은 이유로 231..365의 B 램프(244→253·211)와 C 램프(129..339, 247~253·211·55)는 한 번 칠한 값이 남은 것이 아니다. **미후킹 writer가 매 present 다시 칠한 결과**다. `s` 레코드는 값이 같으면 남지 않으므로 이 구간이 연속으로 보인다.
- 따라서 표본 DR watch를 걸면 B 약 135 present, C 약 211 present 동안 present마다 적어도 배경 writer 1회와 램프 writer 1회의 쓰기가 잡혀야 한다. 신호가 충분하다.
- A는 p298..301의 4 present 임시값(94·215·163·187) 뒤 p339에 85로 돌아온다. 신호가 적다.
- 반례 점검: `0x467580` 계수 inv = mirrored + reject_size다(3583 = 3555 + 28). 다른 renderer로 호출된 경로가 없다. 따라서 다른 renderer 인자로 `0x467580`이 화면을 칠했을 가능성은 배제된다.

## 2. diff 검수(lap1018 v2 bridge `6932c3ac…` 대비)

- 추가된 것:
  - 관측 hook `observe_blend_410`/`observe_blend_6d0`(pass-through, 원본 인자 그대로)
  - `G1DriftWrite` begin/end
  - `u` 레코드
  - 계수·reset·restore·`primitives_installed`
  - `mirror_blend_wrle` 안의 `why` 문자열 대입 6곳과 `clipped` 분기의 중괄호. 계수·미러 동작은 바뀌지 않았다.
- env 없을 때 불변인 근거:
  - `layer_drift_write_begin`은 `!layer_drift_on()`이면 `on=FALSE`로 즉시 반환한다. 그래서 `write_end`도 반환한다.
  - 두 관측 hook은 `layer_drift_on() &&` 조건일 때만 `install_one`을 부른다. 설치 실패 시에는 all-or-nothing 원복한다.
  - `restore_hook`은 `!installed`이면 TRUE다.
  - `primitives_installed`는 `!layer_drift_on() ||`로 요구 조건을 면제한다.
  - save006 env-off 2 run에서 `drift_*_installed` 0을 raw로 확인했다.
- old bytes `83 EC 08 53 56`(`0x467410`)·`83 EC 14 33 C0`(`0x4676D0`)는 lap1019 §3.2 objdump와 같다. 이 장면의 호출 수 0은 hook 입구 무조건 계수(v2)로 센 값이다. 따라서 "설치는 됐고 호출되지 않음"이 맞다.
- 한계(work 기록에 있음, 수용): `w`는 renderer `0xE5BF18`·화면 buffer 호출만 기록한다. `u`는 present 간 비교이므로 present 사이 왕복 변화(위 §1.1 리셋)는 `u`에 안 잡힌다.

## 3. 판정
**H-B2 B2-1 귀속 FAIL·수리 없음을 수용한다.** B2-0 PASS, 비회귀 PASS다. R1(`reject_size`)·R2(형제 hook)·R3는 기각한다. save000 표본 writer는 `0x467580`/`0x467410`/`0x4676D0` 호출 창 밖이며 정체는 UNKNOWN이다. 진단 코드는 env 게이트 안에서만 동작하며 제품 동작은 불변이다.

### 3.1 다음 경로 결정 — H-B3 채택(정적 전수 불채택)
- read-only objdump(원본 SHA 일치)로 확인한 것: `mov ecx,0xE5BF18` 직후 호출되는 `0x465000..0x46A000` renderer 메서드는 약 70개다. 이 중 mirror hook 대상(`G1_*` 20개)이 아닌 것이 다수다.
- 정적 전수로 writer를 고르는 것은 상시 지시(구현 우선, 긴 정적 전수 금지)에 어긋난다. 또 다른 스레드나 ddraw Blt 경로를 가를 수 없다.
- DR 쓰기 watch는 lap1014 census 캐시 watch로 Wine에서 동작이 입증됐다(VEH·`SetThreadContext`). 이 방법은 EIP·스레드·모듈을 한 번에 지목한다. → **FEASIBLE, 다음 work에서 즉시 구현·실행.**
- 분류 참고(정적 단서, 구현 전제 아님): `0x467580`의 두 thin wrapper(`0x41A008`·`0x41ABF0`) 바로 앞 형제 wrapper가 미후킹 `0x466BE0`(`0x419FB0`)·`0x467160`(`0x41ABAA`)을 호출한다. EIP가 이 근처에 떨어지면 우선 대조한다.

## 4. 다음 work H-B3 사전등록(Sonnet work 1 lap, 진단 전용·제품 불변)

목표: save000 후보 lane에서 표본 A(112,126)·B(437,463)·C(302,9)의 **1x 화면 바이트에 대한 모든 쓰기**의 EIP·스레드·값·present를 기록한다. 이것으로 §1의 미설명 변화(u)를 낸 writer를 직접 지목한다.

### 4.1 구현 범위(최소)
- `g1_mirror2x.c`에 opt-in `SYW2_G1_SCREEN_WATCH=1`을 추가한다. 하네스 `--screen-watch`는 이 env와 `--layer-drift`를 함께 켠다. env가 없으면 코드 경로·hook·VEH가 하나도 설치되지 않는다.
- 첫 유효 PS3 present에서 무장한다(유효 = renderer `0xE5BF18`·buffer `+0x1514`·stride `+0x10`·높이 600).
  - 주소: DR0..DR2 = `buffer + y*stride + x`(A/B/C), 쓰기 전용(RW=01)·LEN=1바이트.
  - 대상 스레드: **프로세스의 모든 스레드**(Toolhelp32 열거, 자기 스레드는 직접 설정)에 건다. 무장 성공·실패 스레드 수를 기록한다.
  - 재무장: present마다 스레드 목록이 늘었거나 buffer 주소가 바뀌면 다시 건다(변화 횟수 기록).
  - lap1014 census watch(`g1_census.c` `watch_apply`·`census_watch_veh`·selftest)의 패턴을 재사용한다. 단 census DLL은 mirror와 hook이 겹치므로 그대로 결합하지 않는다.
- VEH(SINGLE_STEP·Dr6 bit0..2) 처리:
  - 레코드 `{"t":"x","p","i","eip","tid","present_thread","val","mod","hook"}`를 남긴다.
    - `val` = 쓰기 직후 바이트
    - `mod` = EXE 이미지/`_inmm.dll`/기타 모듈 기준 주소
    - `hook` = 그 순간 활성 mirror wrapper(없으면 0)
  - 스택 상위에서 `.text` 복귀 주소 최대 4개를 기록한다.
  - Dr6를 지우고 계속 진행한다.
  - raw 상한 20,000줄을 둔다. 이와 별도로 (i, EIP)별 hits/first/last present 표를 둔다.
- 유효성 대조: present 시 `source_desc.lpSurface + py*pitch + px`와 watch 주소가 같은지 표본별로 기록한다.
- 제품 mirror·gate·기준·validator·기존 계수는 불변이다. DR 무장 실패 시 watch만 포기하고 기록하며 게임 진행은 막지 않는다.

### 4.2 실행
- save000 pair 순차 2회: `--hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch`. 공유 temp `20261005_lap1022_work_hb3/`.
- save006 env-off 비회귀 pair 순차 2회: lap1020 `run_s6.sh`와 같은 인자.
- 실행 후 `game` 사본은 삭제하고 prefix·manifest·output·로그는 보존한다. 디스크 여유는 현재 35G다.

### 4.3 사전등록 판정
- **B3-0 유효**(모두 충족해야 함):
  - selftest hit이 있다.
  - present 스레드를 포함해 무장 스레드 ≥1이고 실패 수를 공개한다.
  - watch 주소 = present source 주소(3/3)다.
  - stale 마지막40 중앙값 = 424.5 ±5%다(watch 비교란).
  - 안전 7종 0, cleanup·source_unchanged true다.
  - **양성 대조**: B의 p366..410 present 중 ≥90%에서 EIP가 `0x467580` 본체 안(다음 함수 시작 `0x4676D0` 미만)인 hit가 있다.
  - B의 89 리셋 쓰기 hit가 있다(EIP 무엇이든 기록).
  - 하나라도 미달이면 B3-0 FAIL이다. 원인(스레드 미무장·주소 불일치 등)을 기록하고 1회 수리 후 재실행한다(③ 반복 원칙).
- **B3-1 귀속**:
  - 대상 = 각 run에서 다시 센 미설명 변화(`u`) present(lap1020 기준 A 5·B 19·C 25).
  - 판정 기준: 그 present 직전 구간(이전 present ~ 해당 present)의 그 표본 **마지막 hit의 `val`이 `u.scr`와 같은** 비율. 이 비율이 ≥90%이면 PASS다.
  - hit가 0인데 u>0인 표본은 **BLOCKED(watch 커버리지 공백)**다. 이때 스레드·모듈·GPU 경로 가능성을 기록한다.
- **B3-2 분류**(다음 work 결정용, PASS/FAIL 아님):
  - B3-1이 지목한 EIP마다 모듈·포함 함수 시작(objdump prologue)·`ret imm`·호출처·mirror hook 대상 여부를 정리한다.
  - (a) EXE 미후킹 primitive → 다음 middle이 H-B4(그 함수 diff 미러, H-L/H-B 패턴)를 사전등록한다.
  - (b) ddraw/wined3d 모듈 → Blt/BltFast 경로 대조를 다음으로 한다.
  - (c) `_inmm.dll` → 후보 결함이며 직접 수리 대상이다.
  - (d) present 스레드 밖 → 스레드 시작 주소를 기록한다.
- **B3-3 비회귀**:
  - save006 env-off 2 run에서 300..620 공통 38프레임 r1∩r2 = 24 px(y515..520×x616..619), 39프레임 0, 신규 0이어야 한다.
  - p95 ≤16ms, 안전 0, watch·drift 계수 0이어야 한다.
- 시간 상한: 1 work lap이다. Wine에서 다른 스레드 DR 무장이 원리적으로 불가하면 present 스레드만으로 실행한다. 이때 B3-1 결과는 "present 스레드 한정"으로 표기하고 BLOCKED 근거를 남긴다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 정적 분석만 했다. 게임/source/commit은 0이다. 전체 `make check`는 SKIP했다. source가 불변이고 lap1020 full PASS 1616이 유효하다. 다음 work가 DLL 변경 뒤 실행한다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험:
  - DR watch는 HW 디버그 레지스터를 쓴다. Wine의 스레드 컨텍스트 경로에서 다른 스레드 무장이 실패할 수 있다.
  - hit 폭주로 present 지연이 생길 수 있다. B3-0 stale·perf로 감시한다.
- backlog(변경 없음):
  - save000 `--stale-mask` 부재
  - save006 짧은 run 꼬리 16,652
  - 성분 D
  - hold keydown 위상 경합
  - 가장자리 마우스 스크롤
  - wrap 쓰기 미추적
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-B3(위 §4).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1020 work, SHA256 `4c4f299b550a3bde94d32f38524aabfcc9cbe87d00122858e8f0b3c5754abce0`)

```
lap1020 work(Claude Code claude-sonnet-5-5) G1 H-B2 인계 (마일스톤 경계 아님; 사전등록 B2-1 귀속 FAIL = 수리 없이 middle 검수·다음 가설 정의 요청).
- 한 일: 진단 전용 구현. g1_mirror2x.c(SYW2_G1_LAYER_DRIFT=1일 때만): G1DriftWrite begin/end로 0x467580 호출 전후 표본 3점 화면 값을 JSONL "w" 레코드로 기록, 관측 hook 0x467410(83 EC 08 53 56, ret 0x1C 7인자)·0x4676D0(83 EC 14 33 C0, ret 0x14) pass-through 설치, present마다 hook이 설명 못 한 표본 변화 "u" 레코드. g1_mirror2x.h·direct_draw_trace.c getter/metrics. tests/test_g1_rect_fill.py 계약 테스트 1개(RED→GREEN), lint·typecheck PASS. 제품 동작 불변(env 없으면 즉시 반환).
- 실행: save000 pair 2회(v1 카운터 정의 결함 보존, v2 정정 후 2회) + save006 env-off 비회귀 pair 2회, 전부 exit 2(기존 pair HOLD). 공유 temp 20261005_lap1020_work_hb2/.
- 결과: B2-0 PASS(stale 마지막40 중앙값 424.5, 안전0, p95 7). B2-1 FAIL: scr 변화 대응 A 0/5·B 5/24(p366.. 만)·C 0/25. 0x467410/0x4676D0 호출 0(설치는 성공). 0x467580 사각형이 표본을 포함한 호출: A 0, B 63(그중 48은 sb==sa), C 30(p27..56뿐, C 변화 p129..339). → 표본 writer는 세 hook 호출 창 밖(미후킹 primitive 또는 다른 스레드). save006 env-off 비회귀 PASS(성분 D 24·신규 0·p95 7/8·cov 99.30%·안전0·관측 hook 미설치).
- middle이 확인할 것: (1) w/u 레코드(layer_drift.jsonl s0_r1/s0_r2)와 trace_raw를 analyze_hb2.py/contain.py 없이 새 스크립트로 재계산(대응률, 포함 호출 수 A 0·B 63·C 30, 형제 invocations 0), (2) g1_mirror2x.c diff가 env 없을 때 불변인지(layer_drift_write_begin 첫 줄 layer_drift_on 반환·observe hook 설치 게이트), save006 env-off 2회 확인, (3) 다음 가설 H-B3 채택 여부: 후보 lane 화면 표본 3점 DR 쓰기 watch(EIP·값·present)로 미후킹 writer 직접 지목(lap1014 census 캐시 watch의 화면판) vs 다른 정적 조사. A는 p298..301 4 present 임시값(94·215·163·187)뒤 85 복귀, C는 p129..198 247~252 램프(B 램프와 같은 LUT 계열).
- 기록: docs/history/laps/20261005_lap1020_work_g1_hb2_sample_writer_attribution.md. 변경 uncommitted.
```

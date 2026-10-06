# 2026-10-05 | lap1017 | G1 H-S2d 독립 검수 → 수용(H-S2w 추론 반증 수용), 다음 work H-B(`0x467580` 반투명 RLE diff 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행 0·source 변경 0·커밋 0.
- 가설 / 사용자 관찰: lap1016 work 주장 — save000 A/B/C 사각형에서 캐시 레이어 표류(`layer_covered && 캐시≠layer_expected`)는 0이다. stale은 전송 뒤 화면 픽셀이 램프 값으로 덮이는데 snapshot이 따라가지 않아서 생긴다(화면 쪽 비추적 writer). 따라서 lap1014/1015의 추론 "stale = candidate 내부 expected≠캐시"는 반증된다.
- 예상 PASS / FAIL 조건(lap1015 §4 L-0~L-3): L-0 유효(scene 동일·stale 마지막 40 중앙값 7,675±10%·안전 0·cleanup·loaded PNG 비단색), L-1/L-2 관측, L-3 분류. 검수 기준: 새 스크립트 재계산 불일치 0, env가 없을 때 동작 불변.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`(압축 포함), `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1017_middle_review/`:
  - `recalc_lap1017.py`(SHA256 `aa3f6de4b9a4f7777723589754c5f2c4761a6443342607a7ef6ae521287c7c7d`) → `recalc_lap1017.json`(`3382887939459898d8d53f994a9a523642162d92b7b0640b0632fa69d3a37db7`)
  - `align_census_lap1017.py`(`257b3da1186096da099a1a2e7b59d0e664e5d330239f5452a187ab575868311a`) → `align_census_lap1017.json`(`5e54617b7e5077708cac1a2a059c41df09faceceeec2f84ab2ee08bfc18b9e77`)
  - `loaded_side_by_side_r1.png`(`aa2eae5b…a9f`), `crop_{A,B,C}_r1.png`
  - 모두 uncommitted.
- 원본 SHA / fixture: 원본 EXE `b56986e0…08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`). SHA를 재계산했고 objdump는 read-only로만 실행했다. save000 `1c703551…19da`(index 1). 두 run 모두 `source_unchanged` true. 활성8인 부하 증명 아님.

## 1. 독립 재계산(`analyze_s2d.py`·제품 helper 미사용)

| 항목 | work | 재계산 |
|---|---|---|
| layer_drift.jsonl SHA r1/r2 | `4646ab67…`/`bb62cff6…` | 같음. tick을 뺀 레코드 값은 r1=r2 |
| 레코드 수 | h1·s59·r221·e9 | 같음 |
| L-0 stale 마지막 40 중앙값 | 7,694.5 | 7,694.5(r1=r2, trace_raw PS3 `mirror2x_present` 411개 기준) |
| L-0 scene/cleanup/source/안전 | PASS | scene_state_equal true, cleanup 4/4, source_unchanged 4/4. clip mismatch 7종과 panel lock/pointer/pitch 0 |
| loaded | V2s 629/635 | 629/635, V2q 265/435, scale2x PASS, 성능 p95 1/7·0/7, 비 1.0000 |
| 사각형 stale·unc 최대 | 0·0 | A/B/C 모두 0·0(r1·r2) |
| 표본 `cache==lexp`, `lcov=1`, `snap==lexp` | 전 present | 세 점 모두 참 |
| B 캐시 변화 | 83→89 @168 | 같음. 같은 present에 lexp가 따라감, event writer `0x468CC0` |
| 첫 `scr≠snap`(cov=1) | A 298·B 231·C 129 | 같음 |
| 화면 값 사슬 | A 94/215/163/187→85(339), B 244→253 램프·211·55 지속, C 88·247→253·211·55→92(339) | 같음 |
| `sne` 최대 | A 13,315·B 6,848·C 1,982 | 같음 |
| compose 증분 | A·C 0, B 호출 66·composed 20,430 | 같음(B px 증분 a≠b 54,395·composed 20,430) |
| guard 우회 | — | 0(3 사각형) |

**불일치 0.** 전사 보정 1건: work는 `snl`(covered && snapshot≠layer_expected)이 "증가 없음"이라고 적었지만, B는 present 63·78에서 2,493→2,495(+2)로 일시 증가했다. 판정에는 영향 없음.

## 2. 하네스·DLL diff(env 없을 때 불변)

- lap1014 bridge `g1_mirror2x.c`(`42245a20…`)와 lap1016 bridge(`41ac7bef…`, 현재 source와 같음)를 diff했다. 지운 줄은 6개다.
  - 조기 반환 4곳(args/buffer/range의 `return;`, panel_foreign): `{ layer_drift_return(...); return; }`으로 바뀌었다.
  - compose bounds `return 0u`: 바로 앞에 drift 호출이 붙었다.
  - skip 판정: `if (a != b || (a == 0u && b == 0xFFu)) continue;` → `if (a != b) { … continue; }`. `a==0 && b==0xFF`는 `a≠b`의 부분집합이라 **논리 동치**다.
  - lookup miss: `continue`가 그대로다.
- 추가된 코드는 모두 `layer_drift_on()`이 참일 때만 동작한다. 예외는 `initialize_environment()` 호출이 더 일찍 일어나는 것인데, CAS로 한 번만 실행되는 env 읽기라 부작용이 없다. 10개 wrapper 중첩 guard의 우회 계수도 env가 켜져 있을 때만 renderer를 읽는다.
- `layer_drift_present`는 env가 꺼져 있거나 PS3가 아니면 곧바로 반환한다. stale loop보다 먼저 읽고, `g_covered`는 바꾸지 않는다.
- `g1_saved_scene_probe.py`: env `SYW2_G1_LAYER_DRIFT=1`은 candidate 블록 안에서만 설정한다(3216행). 인자 검증상 `--layer-drift`에는 scale2x가 필요하고 census-only와 함께 쓸 수 없다.
- bridge의 `Makefile`·`inmm_stub.c`가 source와 다른 것은 기존 생성 패턴(`runtime_bridge.c`·`supply_probe_poll`)이다. 이번 변경은 `Makefile` 의존 헤더 1개뿐이다.

## 3. 판정

**H-S2d PASS(partial) 수용, H-S2w→H-S2d 추론 반증 수용.**

stale 정의는 `g_covered && g_expected_snapshot ≠ 화면 픽셀`이다(`g1_mirror2x.c` copy_present). 세 표본 모두 `snap == lexp == cache`이고 `cov=1`인데, 화면 값만 다르다. 따라서 stale의 원인은 캐시 레이어가 아니라 **캐시→화면 전송 뒤 화면을 덮어쓴 writer가 snapshot을 갱신하지 않은 것**이다.

lap1015 middle(같은 역할의 이전 회차)이 "S-1 = 내부 expected≠캐시"라고 쓴 것은 정의로부터 성급하게 추론한 오류였다. H-S2w의 계수·EIP는 유효하다. stale 픽셀은 해당 present에서 nearest로 표시되므로 화면 손상이 아니라 HD 품질 손실이라는 결론은 유지한다.

### 3.1 램프 writer 근거(work 기록에 없던 교차)

- **B — `0x467580` 확정적.** lap1012 W-B census(원본 lane)의 B 표본 `(437,463)` watch에서 `0x004662DE` 값 89가 63회 나왔다. 그 밖에 **`0x00467692`가 값 89×14, 211×3, 244~251 램프 27회**를 썼다(`align_census_lap1017.json`). candidate B 화면 사슬 `244→253·211`과 같은 값 계열이다.
  - `0x467692`는 `0x467580` 본체의 쓰기 명령 `0x46768E mov [edi+edx-1],al` 바로 다음이다(데이터 BP는 쓰기 뒤 트랩).
  - `0x467580`은 candidate에서 hook되지 않는다. 현재 반투명 미러는 `0x4672E0`(H-L)뿐이다.
- **C/구름 정황.** census `rle_blend_467580` 표본(3 run 공통, PS3 present 1~3)에 bbox `(301,18) 160×120`(changed 6,053~6,188)가 있고, C 사각형과 겹친다. 두 lane의 loaded PNG에서도 같은 자리(대략 x330..430·y40..115)에 반투명 구름이 보인다. 구름이 위·왼쪽으로 1px씩 이동하는 것이 표본에 잡혔다.
- **남은 긴장(C).** 시각 대응(첫 PS3 event 기준 초)은 다음과 같다.
  - lap1012 W-C 창(present 251~314)은 **7.1~15.2 s**이고, candidate C 램프는 present 129~339 = **6.4~16.9 s**다.
  - 시간으로 보든 present 번호로 보든 겹친다. 그런데 원본 W-C 표본 `(302,9)`의 쓰기는 `0x4662DE` 값 92 ×63뿐이었다.
  - 그래서 C의 writer가 `0x467580`이라는 것은 **미확정**이다. 후보 설명: 구름 궤적이 lane마다 다르거나(present 속도 38/s 대 20/s, 난수), C가 다른 writer일 수 있다.
  - A(present 298~338, 4 present만 다른 값)는 원본 W-A 창(6.5~12.1 s)이 candidate A 구간(14.9~16.9 s)과 겹치지 않아 판별하지 못한다.
- **work 제안 H-S2r(reject 교차)를 채택하지 않은 이유.**
  - stale은 세 표본에서 수십~180 present 동안 **매 present** 재발한다(전송이 매 present 다시 덮고 writer가 다시 그림).
  - `flip_rle_466B50_reject_size` 76은 run 전체 누계라 매 present 원인이 될 수 없다.
  - overlay blt reject 452(present당 약 1.1)는 save006에서도 1.6k 수준으로 stale을 만들지 않았다.
  - 반면 원본이 실제로 B에 쓰는 미후킹 writer `0x467580`은 이미 특정되어 있다. 구현 우선 원칙(③)에 따라 측정만 하는 회차를 하나 더 두지 않고, 미러를 구현하는 것이 결정 실험을 겸한다.

### 3.2 `0x467580` 정적 재확인(read-only objdump, 원본 SHA 일치)

- 프롤로그 `51 0F BF 54 24 0C`(push ecx, `movsx edx,word [esp+0xC]`): 상대 분기·호출이 없어 6바이트 trampoline이 가능하다.
- 유일한 `ret 0x14`는 `0x4676C1`이다. 인자 5개(x·y·width·height·RLE)의 하위 16비트를 `movsx`로 읽는다. 목적지는 `[ecx+0x1514] + y*[ecx+0x10] + x`이고 **클립이 없다**.
- 호출 지점은 2곳이다. `0x41A00D`와 `0x41ABF5` 모두 바로 앞에서 `mov ecx,0xE5BF18`을 한다(H-L `0x4672E0`과 같은 renderer).
- 가중 혼합표 `renderer+0x41CA0`(64×64 16비트)와 역 LUT `renderer+0x19A0`은 lap953/954 지도와 같다. 이 혼합 자체는 P6 명시 잔여다. diff 미러는 혼합 결과(바뀐 픽셀)를 Scale2x/nearest로 추적만 하며 HD 혼합을 계산하지 않는다.

## 4. 다음 work 사전등록 — H-B(`0x467580` 가중 반투명 RLE diff 미러)

- 구현(H-L 동형, 최소 변경):
  - `g1_mirror2x.c`에 hook `0x467580`을 추가한다. old bytes `51 0F BF 54 24 0C`를 확인하고, 다르면 설치 거부·원복한다. thiscall이고 `ret 0x14`다.
  - wrapper `mirror_blend_rle_467580`은 `mirror_blend_rle`과 같은 로직이다.
    - 인자는 하위 16비트를 부호확장한다. renderer가 `0xE5BF18`이고 화면 buffer일 때만 처리한다(cache/panel 대상은 `reject_target`).
    - 화면 밖은 `reject_bounds`, 크기 초과는 `reject_size`, guard 중첩은 `reject_guard`로 계수한다.
    - 처리 순서: 전용 before 사본 → 원본 호출 → `g1_overlay_blt_apply`(scale2x 모드).
  - 계수 8개 `blend_467580_{invocations,mirrored_calls,mirrored_pixels,changed_calls,reject_target,reject_bounds,reject_size,reject_guard}`를 metrics에 추가한다. detach할 때 원복한다.
  - 테스트: 소스 계약(주소·old bytes·`ret 0x14` 주석·계수 이름·별도 before 버퍼) RED→GREEN, 기존 H-L 테스트 패턴을 따른다.
  - 부분 화면 밖 변형(조건부, 같은 회차 허용): 결과에서 `reject_bounds`가 A/B/C 사각형과 겹친 채 stale이 남으면 화면 교집합만 before/diff하는 변형을 허용한다. 원본의 쓰기 범위는 바꾸지 않고, wrapper는 교집합만 읽는다. 테스트를 추가하고 공개한다.
- 실행(fresh runtime-root, 순차, game 사본 삭제):
  - (1) save000 pair 2회: `--hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift`
  - (2) save006 비회귀 pair 2회: lap1000 H-L 명령과 같게, fresh save006 `--hd-source scale2x`
- 측정·판정:
  - **B-0 유효**: L-0과 같다. scene_state_equal, 안전 7종 0, cleanup ok, source_unchanged, loaded PNG 비단색. 단색이면 기록하고, 측정 유효성은 내부 지표로 판단한다.
  - **B-1(주, save000)**: 표본 3점에서 `cov==1 && scr≠snap`인 present 수. 기준은 lap1016 A 41·B 180·C 210(첫 present 298/231/129부터 복귀 전까지)이다. **PASS = B 0**, A·C는 각각 0 또는 감소량 보고. 전체 stale 마지막 40 중앙값 7,694.5 → 감소율을 보고한다. **≥50% 감소면 PASS**, 일부만 감소면 PASS(partial)로 남은 사각형을 지목한다.
  - **B-2 계수**: `blend_467580_invocations` > 0, `mirrored_calls` ≈ 수락 호출, `reject_target` 0 예상. `reject_bounds`·`reject_size`는 기록하고 사각형 교차를 명시한다.
  - **B-3 save006 비회귀**: 39프레임 steady 교집합 0을 유지한다(lap1000 r2/r3. 프레임 880이 없으면 공통 38프레임 성분 D 24 = 기준과 같으므로 허용). 신규 stale 0, present p95 ≤ 8ms(lap1000 7ms), cov p50 ≥ 99%, V2s production raw는 기록만 한다(기존 gate HOLD).
  - **B-4 성능·안전**: save000 candidate p95 ≤ 10ms(lap1016 진단 on 7ms), ticks 비 ≥ 0.95, 안전 0, 크래시 0.
- 분기:
  - B는 0이지만 C가 남으면 §3.1 긴장점이 확정된다. 다음은 원본 lane census `--census-watch 302,9`의 창을 candidate C 구간 시각에 맞추는 것이다(skip 100~150, `--census-watch-presents`로 넓은 창). 그 결과로 C writer EIP를 지목한다.
  - B도 남으면 hook 설치·호출 경로(`0x41A00D`/`0x41ABF5` 외 간접 호출)를 의심한다.
- 금지: covered를 지워 stale 수치만 줄이는 metric 회피. 기준·validator·gate·required_tags 변경. 원본/참고/raw/golden 쓰기.
- 별도 backlog(변경 없음): 성분 D, hold keydown 위상 경합, 가장자리 마우스 스크롤, `0x467410`·`0x4676D0`(같은 계열, 미관측).

## 5. 검증 / 남은 위험

- 이번 lap은 문서·재계산만 했다. focused 검사 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1016 full PASS 1614 유효, 다음 work가 DLL 변경 뒤 실행).
- C 긴장점은 미해결이다(§3.1). H-B 결과가 이것을 판별한다.
- 사용자 승인 상태: 기술 부분 수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-B(위 §4).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1016 work)

```
lap1016 work(Claude Code claude-sonnet-5-5) G1 H-S2d 인계 (마일스톤 경계 아님; 근거 충돌: lap1014/1015 추론 "stale = candidate 내부 g_layer_expected ≠ 캐시"가 raw로 반증됨 → middle 독립 검수 요청).
- 한 일: g1_mirror2x.c opt-in SYW2_G1_LAYER_DRIFT=1(표본 A 112,126·B 437,463·C 302,9 + 사각형 3개 present별 6값/계수 + compose 결과 계수 + guard 우회) + 신규 g1_layer_drift.h(순수 helper, 호스트 gcc 테스트) + 하네스 --layer-drift(candidate lane만) + 테스트 3개 RED→GREEN, lint·typecheck PASS. 제품 mirror 동작 변경 0.
- 실행: save000 pair 순차 2회(--fixture save000 --scene-actions none --performance-window --layer-drift) 전부 exit 2(기존 non-loaded tag BLOCKED 예상 HOLD). L-0 PASS(scene 동일·stale 마지막40 중앙값 7,694.5 vs 7,675·안전0·cleanup ok·loaded PNG 226색).
- 결과: A/B/C 모든 present에서 layer_covered && 캐시≠layer_expected = 0, 미커버 0, 표본 cache==lexp==snap·lcov=1 유지. A·C는 present 0 이후 캐시 변화·compose 호출 0, B는 캐시 83→89(present 168)를 같은 present의 terrain_shade compose가 따라감. stale은 화면(source surface) 픽셀이 램프 값(B 244~253, C 247~253, A 94/215/163/187)으로 일시 덮어써졌는데 snapshot이 갱신 안 된 것 = 화면 쪽 비추적 writer. 첫 화면≠snapshot present A 298·B 231·C 129. candidate 누계 overlay_blt_rejects 452·flip_rle_466B50_reject_size 76(save000 신규)은 후보이나 교차 미측정.
- middle이 확인할 것: 공유 temp 20261005_lap1016_work_s2d/{r1,r2}/candidate/layer_drift.jsonl·pair-result.json을 analyze_s2d.py 없이 새 스크립트로 재계산(L-0 수치, 사각형별 max stale/unc=0, 표본 6값 사슬, 첫 scr≠snap present, 마지막 compose 이벤트), g1_mirror2x.c·g1_layer_drift.h diff가 env 없을 때 동작을 바꾸지 않는지(compose 픽셀 로직의 a!=b skip 판정 동일), H-S2w→H-S2d 추론 반증을 수용하는지, 다음 work H-S2r(reject 기록을 같은 JSONL에 추가해 A/B/C 첫 stale present와 교차, 불일치 시 baseline lane 화면 버퍼 write watch를 skip 130~300으로 늦춰 램프 writer EIP 지목) 사전등록.
- 기록: docs/history/laps/20261005_lap1016_work_g1_hs2d_layer_drift.md. 변경 uncommitted.
```

# 2026-10-05 | lap1015 | G1 H-S2w 독립 검수 → 수용, 다음 work H-S2d(candidate 캐시 레이어 표류 진단) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행 0·source 변경 0·커밋 0.
- 가설 / 사용자 관찰: lap1014 work 주장 — save000 원본 lane에서 지형 캐시 A·C 바이트는 700 present 동안 쓰이지 않았고(hit 0), B는 1건(EIP `0x468DBA`, 이미 mirror hook 대상인 `0x468CC0` 안)이다. hook 밖 writer가 없으므로 H1(미후킹 캐시 writer)은 지지되지 않고 H2(레이어 표류/compose skip)로 간다.
- 예상 PASS / FAIL 조건(lap1013 §4 K-0~K-2): K-0 무장·selftest·cleanup·로드 유효, K-1 hit 수·EIP·값·분포, K-2 EIP가 hook 함수 안/밖. 검수 기준: 새 스크립트 재계산 불일치 0, DLL·하네스 diff가 옵션 없는 동작을 바꾸지 않음.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문 아래 부록). 공유 temp `20261005_lap1015_middle_review/recalc_lap1015.py`(SHA256 `97818f89747ac0e5e05edda684be76dc9e8573217d03e72116847848803960b3`)·`recalc_lap1015.json`(`4d336fbea1da95d6c837bf9cfcea58abea8100b494299921e7239858347ca6e3`). uncommitted.
- 원본 SHA / fixture: 원본 EXE `b56986e0…08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`, read-only objdump, SHA 재계산 일치), save000 `1c703551…19da`(index 1). 세 run probe-result `status` PASS·`source_unchanged` true·로드 tick 50592/50591/50592. 활성8인 부하 증명 아님.

## 1. 독립 재계산(제품 helper·`analyze_s2w.py` 미사용)

| 항목 | work | 재계산 |
|---|---|---|
| census_raw SHA wa/wb/wc | `f4f6f51c…`/`56de361b…`/`c9532386…` | 동일(전체 해시 json에 기록) |
| 무장 주소 = `0xBA3D30+y*832+x` | `0x00BBD720`/`0x00C01FA5`/`0x00BA5B9E` | 직접 계산 값과 일치, `cache` 1·`watch_presents` 700·armed present 21 |
| selftest / 종료 사유 / 계수 | PASS / `watch_window_end` / 700 | 3 run 모두 같음 |
| hit | wa 0·wc 0·wb 1 | 같음(summary와 hit 레코드 수 일치) |
| wb hit | watch_present 76·EIP `0x468DBA`·값 89 | 같음. 유효 주소 eax+edi−1 = `0x00C01FA5`(= watch 주소), dl = 0x59 = 89, 코드 꼬리 `8B442410 885438FF`(= `mov eax,[esp+10]; mov [eax+edi-1],dl`), 첫 복귀 주소 `0x4355DC` |
| `0x468DBA` ∈ `0x468CC0` | 안 | objdump: `0x468CC0 sub esp,0x10` 시작, 유일한 ret = `0x468DFE ret 0x18`, `0x468DB6` 쓰기 직후가 `0x468DBA`. `0x4355D7 call 0x468cc0`(ecx=`0xE5BF18`) 뒤가 `0x4355DC` |
| `0x468CC0` hook 여부(candidate) | `G1_TERRAIN_SHADE` | `g1_mirror2x.c` 32·2136행 `mirror_terrain_shade` → `mirror_reinvoke(..., G1_TERRAIN_SHADE)` 확인 |
| r0(수리 전 W-A) | window_end·63 present·hit 0 | 같음(`db0d2f0e…`), 수리 근거로 보존 타당 |

**불일치 0.**

work 기록에 없던 관찰:
- **wb `loaded.png`가 단색 검정(색 1개)이다**(wa·wc 222색). X 스크린샷 시점 문제이며 측정 무효는 아니다. 게임 내부 census 지도 마지막 프레임은 wa·wb·wc가 99.69%로 같고, PS3 present 64·전송 호출 727·render 계수도 같은 수준이다. 다음 run부터 loaded PNG가 단색이면 기록한다.
- 캐시 대상 overlay wrapper(`flip_rle`·`rect_fill`·`rect_border`·`blend`)는 renderer buffer가 `0xBA3D30`이면 `reject_target`으로 빠지고 compose하지 않는다. 그러나 lap1010 save000 candidate r1/r2에서 이 넷의 `reject_target`은 모두 0이고(textout만 6/2), `flip_rle_466B50_reject_size` 76은 화면 대상 크기 거부다. 따라서 이 경로는 A/B/C 표류 후보에서 빠진다.

## 2. DLL·하네스 diff 검토

- `g1_census.c`: lap1012 bridge 사본 `341a16c3…`와 현재 `5765503e…`를 diff했다(60줄). 추가된 것은 `g_watch_cache`·`g_watch_presents`·`g_watch_present_ticks`, env 두 개(`g_watch_enabled`일 때만 읽음), JSON 필드 추가, `window_end`를 `!g_watch_presents`로 감싼 것, 주소 선택 삼항, armed 동안 present 계수뿐이다. env가 없으면 주소·종료 조건이 이전과 같다(계수 증가는 출력 필드만 바꾼다).
- `g1_census_watch.h`: 캐시 상수와 주소 helper만 추가했다.
- `g1_saved_scene_probe.py`: 새 env 설정·추가 대기는 `census_watch_cache`/`census_watch_presents`가 참일 때만 실행된다. 인자 검증은 `--census-watch`가 필요하고 범위는 0–9999다.
- lap1014 bridge의 `g1_census.c`·`g1_census_watch.h`·`g1_mirror2x.c`는 현재 source와 같다. `inmm_stub.c`·`Makefile`의 bridge≠source는 lap1012 bridge와 같은 해시라 기존 생성 패턴이며 이번 변경이 아니다.

## 3. 판정

**H-S2w PASS(partial) 수용.** 원본 lane에서 A·C 캐시 바이트는 present 21~720 동안 한 번도 쓰이지 않았고, B는 hook 대상 `0x468CC0`이 1회 썼다. hook 밖 writer는 0이다. 따라서 H1은 지지되지 않는다.

stale 정의를 다시 확인했다(`g1_mirror2x.c` 1017~1034행): `g_covered && g_expected_snapshot ≠ candidate 자기 화면 픽셀`이다. stale 픽셀은 그 present에서 nearest로 내려간다. 즉 S-1은 화면이 틀린 것이 아니라 HD 품질 손실이며, **candidate lane 내부에서 `g_layer_expected` ≠ 캐시 바이트**라는 뜻이다.

긴장점(다음 work가 풀어야 함): compose는 `g_layer_expected = 그 순간의 live 캐시`로 쓰므로 compose 직후에는 둘이 같다. 그런데 원본 lane에서 A·C 캐시는 창 안에서 쓰이지 않았다. 그러면 candidate에서 표류가 생기려면 다음 중 하나여야 한다.
- (i) candidate lane에서만 A/C 캐시가 바뀐다. hook 부작용이나 lane 차이를 뜻하며, 원본 watch의 DR0가 present 스레드에만 걸린 한계일 가능성도 있다.
- (ii) present 21 이전의 쓰기를 compose가 건너뛰었다. 다만 lane 사이 present 번호 대응은 부정확하다.
- (iii) 캐시는 그대로인데 expected/covered/snapshot 쪽이 바뀌었다.
- (iv) 화면 ≠ 캐시다.

## 4. 다음 work 사전등록 — H-S2d(candidate 캐시 레이어 표류 진단, opt-in·측정 전용)

목적: candidate lane에서 A/B/C 표류가 처음 생기는 present와 그 순간의 원인 분기를 하나로 정한다.

- 구현(제품 동작 불변, env 없으면 추가 스캔·출력 0):
  - (a) `g1_mirror2x.c` opt-in `SYW2_G1_LAYER_DRIFT=1`. 감시 대상:
    - 표본 3점: A `(112,126)`·B `(437,463)`·C `(302,9)`.
    - 사각형 3개: A `x38..186×y64..168`·B `x371..502×y427..491`·C `x259..337×y0..25`.
  - (b) 매 PS3 primary present(compositor 진입 시점)에 표본 점마다 6개 값을 읽는다: 캐시 바이트 `*(0xBA3D30+y*832+x)`, `g_layer_expected`, `g_layer_covered`, 화면 픽셀, `g_expected_snapshot`, `g_covered`. 첫 present와 값이 바뀐 present만 JSONL로 기록한다. 사각형마다 세 계수도 바뀐 present만 기록한다: `layer_covered && 캐시≠layer_expected`, `!layer_covered`, `화면≠캐시`.
  - (c) cache_target compose 경로의 결과를 사각형별로 계수한다.
    - 함수 수준: `mirror_reinvoke` 조기 반환(panel_bound / range_valid / MAX_BUFFER / 인자 조건 각각), `g_primitive_guard` 중첩 우회, `g1_hd_asset_current_ready()` false, `compose_cache_layer` bounds 거부.
    - 픽셀 수준: a≠b, 미기록(a==0&&b==FF), lookup miss, composed.
    - 표본 점마다 마지막 compose 이벤트도 남긴다: writer 주소, origin, w/h, present 번호, 결과.
  - (d) 하네스 `--layer-drift`(candidate lane에만 env 전달, 산출물 수집). 테스트: env 없을 때 기본 불변(소스 계약)·사각형/표본 상수·인자 검증 RED→GREEN.
- 실행: save000 pair, `--fixture save000 --scene-actions none --layer-drift`, fresh runtime-root 순차 2회, game 사본 삭제.
- 측정·판정:
  - **L-0**(유효): scene_state_equal, 카메라 (39,53), unit 375, tick ≈50595. stale 마지막 40 중앙값이 lap1010 7,675의 ±10% 안이어야 한다(진단이 동작을 바꾸지 않았다는 확인). 안전 0, cleanup ok, loaded PNG 비단색. 성능 p95는 기록만 한다(probe on이라 gate 아님).
  - **L-1**(관측): 표본 3점마다 첫 stale present 번호, 그 직전 정상 present와 첫 stale present의 6개 값.
  - **L-2**(관측): 사각형별 표류 계수가 처음 0보다 커지는 present와 34·300·마지막 present의 값, (c) 결과 계수.
  - **L-3**(분류, 표본 점별):
    - (i) 캐시 바이트가 바뀌었고 compose가 사유 R로 건너뜀 → R 수리 카드.
    - (ii) 캐시가 바뀌었지만 그 present에 cache_target compose가 없음 → candidate-only 캐시 writer 또는 원본 watch 스레드 한계. 아래 O-1로 판별한다.
    - (iii) 캐시는 그대로이고 expected/covered가 바뀜 → 그 이벤트 경로.
    - (iv) 화면≠캐시 → 전송/좌표 경로.
    - (v) snapshot≠layer_expected이고 layer는 정상 → `transfer_cache_to_screen` 미호출/범위 경로.
  - 참고 기대값: 원본 캐시 값은 A 85·C 92·B 89(lap1012/1014 watch 값)다. candidate 캐시가 이 값과 다르면 lane 차이로 기록한다.
- 선택 O-1(같은 work 회차에서 필요할 때만): L-3이 (ii)이면 census-only 원본 lane에도 같은 표본 3점의 present별 캐시 바이트 읽기(스레드 무관)를 opt-in으로 넣고 skip 0으로 1회 실행한다. DR0 스레드 한계를 판별하기 위해서다.
- 금지: 표류 픽셀의 covered를 지워 stale 계수만 줄이는 "무효화" 수리는 metric 회피라 금지한다(stale는 이미 nearest로 보이고, covered 축소로 수치만 바뀐다). 수리는 HD 합성을 복원하는 쪽이어야 하고, coverage 변화는 공개한다.
- FAIL/BLOCKED: 무장·로드 무효·L-0 stale 재현 실패는 하네스/진단 결함으로 보고 수리 후 재실행한다(PROMPT ③).
- 별도 backlog(변경 없음): B 994 px `0x467692`(`0x467580` 계열), 성분 D, hold keydown 위상 경합, 가장자리 마우스 스크롤.

## 5. 검증 / 남은 위험

- 이번 lap은 문서와 재계산만 했다. focused 검사 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1014 full PASS 1611 유효, 다음 work가 DLL·하네스 변경 뒤 실행).
- 원본 watch는 DR0 하나·present 스레드 한정이다. A·C "쓰기 0"은 그 스레드 기준이다(위 O-1).
- 사용자 승인 상태: 기술 부분 수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-S2d(위 §4).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1014 work)

```
lap1014 work(Claude Code claude-sonnet-5-5) G1 H-S2w 인계 (마일스톤 경계 아님, 일상 middle 검수 요청).
- 한 일: census DLL opt-in SYW2_G1_CENSUS_WATCH_CACHE=1(watch 주소=0xBA3D30+y*832+x)·SYW2_G1_CENSUS_WATCH_PRESENTS=N(watch 전용 present 계수, N>0이면 64-present window_end로 안 끊김)·하네스 --census-watch-cache/--census-watch-presents·테스트 RED→GREEN(223 passed), lint·typecheck PASS. 제품 mirror/gate 변경 0.
- 실행: save000 census-only 순차 3회(W-A 112,126 / W-B 437,463 / W-C 302,9, skip 20, watch 700 present) 전부 exit 0, K-0 PASS(selftest hit 1·armed 주소 일치·watch_present_ticks 700·cleanup ok). r0(첫 W-A)는 64-present window_end에서 끊겨 수리 후 재실행(r0 보존).
- 결과: W-A hit 0, W-C hit 0(700 present, 캐시 A/C 바이트 불변), W-B hit 1(watch_present 76, EIP 0x468DBA = 터레인 shade 블리터 0x468CC0 안, mirror hook 대상, 값 89). hook 밖 EIP 0 → H2(레이어 expected 표류/compose skip) FEASIBLE.
- middle이 확인할 것: census_raw 3개(공유 temp 20261005_lap1014_work_s2w/{wa,wb,wc}/census/)를 새 스크립트로 재계산(armed 주소·watch_present_ticks 700·hit 수·EIP·값), 0x468DBA가 0x468CC0..0x468DFE 안인지 objdump 대조, DLL/하네스 diff가 옵션 없는 동작을 안 바꾸는지, 다음 work H-S2d(candidate lane compose_cache_layer skip 사유 계수 + 표류 첫 ordinal) 사전등록.
- 기록: docs/history/laps/20261005_lap1014_work_g1_hs2w_cache_watch.md. 변경 uncommitted.
```

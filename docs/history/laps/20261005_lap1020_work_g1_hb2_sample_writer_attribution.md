# 2026-10-05 | lap1020 | G1 H-B2 — 표본 writer 호출 단위 귀속(진단 전용) → B2-1 귀속 FAIL, 세 hook 밖 writer

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 가설: save000 stale 잔여(마지막 40 중앙값 424.5)의 표본 A(112,126)·B(437,463)·C(302,9) 화면 값을 바꾼 호출은 `0x467580`의 `reject_size`(R1)이거나 형제 `0x467410`/`0x4676D0`(R2)이다. lap1019 §4 사전등록.
- 예상 PASS / FAIL 조건: lap1019 §4.3 B2-0(유효)·B2-1(귀속, 세 표본 모두 대응률 ≥90%)·B2-2(분기 수리)·B2-3(수리 시 판정).
- 변경 파일(uncommitted):
  - `tools/inmm_stub/g1_mirror2x.c`(SHA256 `22818f4152c65ce16d9963c0d75357bb6103941b8f8a7e31704a94a37d76b841`): 진단 전용. `G1DriftWrite` begin/end(호출 전후 표본 3점 화면 값, `w` 레코드), 관측 전용 pass-through hook `observe_blend_410`(`0x467410`, old bytes `83 EC 08 53 56`, `ret 0x1C` 7인자)·`observe_blend_6d0`(`0x4676D0`, `83 EC 14 33 C0`, `ret 0x14` 5인자), present당 설명 안 된 표본 변화 `u` 레코드와 계수.
  - `tools/inmm_stub/g1_mirror2x.h`(`15e2d291…`)·`tools/inmm_stub/direct_draw_trace.c`(`2ac96874…`): getter·metrics 키(`drift_467410_*`·`drift_4676D0_*`·`drift_w_records`·`drift_unattributed`).
  - `tests/test_g1_rect_fill.py`(`0b685f32…`): 소스 계약 테스트 1개(RED→GREEN, 8 passed). `make lint`·`make typecheck` PASS. DLL을 /tmp에 컴파일해 `g1_mirror2x.c` 경고 0 확인(임시본 삭제).
  - 제품 동작·미러·gate·기준·validator 불변. 새 hook 두 개는 `SYW2_G1_LAYER_DRIFT=1`일 때만 설치(불일치면 all-or-nothing 원복). env 없으면 wrapper의 추가 코드는 `layer_drift_on()`에서 즉시 반환한다.
- 원본 SHA / fixture: 원본 EXE `b56986e0…8ac`(안전 불변, 모든 run `source_unchanged` true). save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명 아님.
- 실행(순차, 격리 prefix·display, runtime `local/runtime/lap1020_hb2*`, 공유 temp `20261005_lap1020_work_hb2/`):
  - save000 v1(카운터 버그 있음) pair 2회: `--hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift`, 전부 exit 2(기존 pair HOLD). 보존 `v1_s0_r1`·`v1_s0_r2`. 같은 인자로 v2 pair 2회(`s0_r1`·`s0_r2`, exit 2). v1은 `observe` 호출 계수가 "화면·PS3·변화 시"에만 증가하는 내 결함이라 invocations 0이 어느 쪽 의미인지 모호해 invocations를 hook 입구 무조건 계수로 고쳐 재실행했다. 값은 같다.
  - save006 비회귀 pair 2회(env 없음, `--hd-source scale2x --stale-mask 6-12,30-34,300-301,585-620,880`), exit 2(기존 pair HOLD).
  - 분석 스크립트(공유 temp): `analyze_hb2.py`(SHA256 `d83b80a3…c1`)·`contain.py`(`6d35ee5c…88`)·`analyze_hb.py`·`analyze_hb_s6.py`(lap1018본 복사 후 경로만 수정). 로그 `logs/gates/lap1020_hb2*`.

## 측정값 / 판정

### B2-0 유효 — PASS
- save000 v2 r1/r2: scene_state_equal true, PS3 present 411, stale 마지막 40 중앙값 **424.5**(lap1018 v2와 동일), 안전 7종 0, cleanup 2/2·source_unchanged 2/2, p95 cand 7ms(기준 1), tick_rate 19.95/20.00 Hz.
- 관측 hook 설치 성공: `drift_467410_installed` 1·`drift_4676D0_installed` 1.
- 두 run의 `w`·`u` 레코드 수가 같다(93·49).

### B2-1 귀속 — **FAIL**(세 표본 모두 ≥90% 미달)
`s` 레코드의 표본 `scr` 변화 시점마다 같은 present의 `w` 레코드(`sb≠sa`)를 대응시켰다.

| 표본 | `scr` 변화 present 수 | `w` 대응 | 대응률 | 설명 안 된(`u`) present | 변화 구간 p |
|---|---|---|---|---|---|
| A (112,126) | 5 | 0 | 0% | 5 | 298..339 |
| B (437,463) | 24 | 5 | 21% | 19 | 미설명 168..348 / 대응 366.. |
| C (302,9) | 25 | 0 | 0% | 25 | 129..339 |

- `w` 93 레코드 전부 `f=467580`·`why=mirrored`. `reject_size`·`clipped`·`reject_bounds` 기록 0(표본이 있는 호출 중에는 없음). 대응된 5건은 전부 B의 p 366..411(`0x467580` 호출 안에서 89→253·55·252…).
- **`0x467410`·`0x4676D0` 호출 수 0**(둘 다 설치됐고 이 장면에서 한 번도 호출되지 않음) → R2 기각(save000).
- **`0x467580` 호출 사각형이 표본을 포함한 횟수**(`contain.py`): A **0**, C 30(p 27..56뿐; 변화 구간 p 129..339와 겹치지 않음), B 63(p 6..410, 그중 `sb==sa` 48개 = 호출이 값을 바꾸지 않음). 즉 A·C의 변화는 사각형 기하상 `0x467580` 호출이 만들 수 없다(R1도 해당 없음).
- 호출 전후 값은 같고 present 사이 값은 바뀐다 → 표본을 바꾼 writer는 세 hook의 호출 창 밖이다. B 231..365(미설명 구간)도 같다.
- 결론: A·C 전 구간과 B 231..365의 writer는 `0x467580`/`0x467410`/`0x4676D0` 밖. **UNKNOWN**(사전등록 "대응 0 → 세 hook 밖 writer").

### B2-2 분기 — 수리 없음
- R1(`reject_size`): 표본이 있는 `reject_size` 호출 0 → 해당 없음.
- R2(형제): 호출 0 → 해당 없음.
- R3(`mirrored`인데 snapshot 불일치): B p366.. 대응 5건은 snapshot이 따라가므로 해당 없음(lap1019 §3.1과 같음).
- 귀속 0이므로 사전등록대로 수리하지 않는다(metric 회피 없음).

### 비회귀(save006, env 없음) — PASS
- pair 2회: 공통 38프레임 교집합 = 성분 D 24(기준 동일, y515..520×x616..619), lap1000 기준 3 run 대비 신규 0·제거 0, PS3 present 885/887, p95 7/8ms·max 10/12ms, cov p50 99.30%, 안전 7종 0, cleanup·source_unchanged 전부 true.
- 관측 hook 미설치(`drift_*_installed` 0)·`drift_w_records` 0·`u` 0, `blend_467580` invocations 16·mirrored 0·`reject_size` 16(lap1018 save006과 동일).

## 의미
- save000 stale 잔여의 표본 writer를 hook 호출 창 안에서 직접 보고 싶다는 목적에서, 형제 두 함수는 호출 자체가 없고 `0x467580`은 A·C를 기하상 못 칠하는 것이 확정됐다.
- 남은 가설: (H4) 표본을 칠하는 **미후킹 그리기 함수**(같은 renderer의 다른 반투명/효과 primitive) 또는 present 스레드 밖 writer. A는 p298..301 4 present의 임시 값(94·215·163·187)뒤 원래 85로 복귀, C는 p129..198에서 247~252 램프. 값 계열(247~253·211)이 B 램프와 같아 같은 혼합 LUT를 쓰는 함수로 보인다.
- 결정적 방법: 후보 lane에서 표본 화면 주소(`renderer+0x1514` buffer + y·stride + x) 3개에 DR 쓰기 watch를 걸어 EIP를 얻는 것(lap1014 `SYW2_G1_CENSUS_WATCH_CACHE`의 화면판). census 계측 밖 writer를 EIP로 직접 지목한다.

## 회귀 / 남은 위험 / 독립 검수
- 제품 변경 0이므로 24k/144k·HD 품질에 영향 없음. 진단 hook이 `layer_drift_on()` 시에만 설치돼 기본 경로 불변(save006 env-off 2회로 확인).
- 독립 검수 필요: `w`/`u` 재계산(`analyze_hb2.py`·`contain.py` 없이), wrapper diff(env 없을 때 불변), 호출 0 결론의 hook 설치 확인.
- 한계: `u`는 present 사이 표본 변화 중 hook이 설명하지 못한 것 전부(터레인·캐시 복사 포함)라 writer 종류를 못 가른다. 호출 수 0은 save000 이 장면·20초 창 한정.
- backlog(변경 없음): save000 `--stale-mask` 부재, save006 짧은 run 꼬리 16,652, 성분 D, hold keydown 위상 경합, 가장자리 마우스 스크롤, wrap 쓰기 미추적.

## 다음 한 가지
- middle이 위 결과를 독립 검수하고 다음 work를 정한다. 제안 H-B3: 후보 lane 화면 표본 주소 DR 쓰기 watch(3점, EIP·값·present 기록), 읽기 전용 관측이며 제품 불변. 판정은 EIP가 기존 hook 대상인지 새 함수인지(정적 objdump로 prologue·ret·호출처 결정)다.

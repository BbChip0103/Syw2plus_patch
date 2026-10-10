# 2026-10-09 | lap 1211 | G1 middle — H-SIG0 검수(NOT_REPRODUCED 수용·하네스 결함 1) + H-PS5W0 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`/high, 중간 계획·컨펌(middle). 게임 코드·하네스 수정 0.
- 가설 / 사용자 관찰: (검수 대상) lap1210 work H-SIG0 — 현재 DLL·F0 new-game 6 run에서 서명 stale 쌍봉이 0/6, `NOT_REPRODUCED`.
- 예상 PASS / FAIL 조건: lap1210 raw를 새 스크립트로 다시 계산해 수치 불일치 0이면 수용한다. ESCALATE_SOL 질문 (1)~(4)에 답한다.
- 변경 파일 / source fingerprint / 커밋: 문서만 바꿨다(이 기록, ESCALATE_SOL 보존본, STATUS, INBOX 메모). 공유 temp에 재계산 스크립트를 뒀다. 제품 C·하네스·테스트 변경 0. 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `[HQ]Syw2plus 2002.exe` `b56986e0…` read-only MATCH(직접 재계산). lap1210 DLL `7b1c2203…`, 팩 끔, 활성 1인 F0 new-game.
- 실행 명령 / 로그: 게임 run 0. 재계산 스크립트는 공유 temp `20261009_lap1211_middle_review/`에 있다.
  - `recalc_lap1211.py`(`2919bf1e…`) → `recalc_lap1211.json`(`98bb3149…`)
  - `sig_context.py`(`307d312f…`)
  - `clip_split.py`(`8460694a…`) → `clip_split.txt`(`76af3b1a…`)
  - `clusters.py`(`fc0b79e1…`) → `clusters.txt`(`f857d0a1…`)
  - `ps57.py`(`94aeebe8…`)
- ESCALATE_SOL: 원문을 byte 일치로 보존했다(`docs/history/laps/20261009_lap1211_preserved_lap1210_escalate_sol.txt` `11b82d57…`). 보존 뒤 원본은 삭제했다.

## 1. 독립 재계산 — 불일치 0

lap1210의 ana.py와 별개로 새로 쓴 스크립트다. 서명 기준은 PS3 첫 present 기준 12.5~16 s에 `stale_pixels` ≥150인 present다.

| run | exit/status | PS3 present | ord 262 시각 | 창 250-313 최대 | 전체 최대 (ord, s, px) | ≥150 |
|---|---|---|---|---|---|---|
| S1 | 0/PASS | 6,032 | 13.064 | 0 | 0 | 0 |
| S2 | 0/PASS | 6,032 | 13.063 | 0 | 1529, 76.42, 90 | 0 |
| S3 | 0/PASS | 6,104 | 13.079 | 0 | 1612, 80.59, 15 | 0 |
| S4 | 0/PASS | 6,009 | 13.066 | 0 | 0 | 0 |
| S5 | 0/PASS | 6,022 | 13.089 | 0 | 2809, 140.93, 2 | 0 |
| S6 | 0/PASS | 6,031 | 13.065 | 0 | 0 | 0 |

- work 기록과 수치가 모두 일치한다. 모든 run이 `stale_pixels` 필드를 갖고 있다(누락 0).
- 원본 SHA와 private SHA가 `b56986e0…`이고 `source_unchanged` true다.
- 질문 (1)·(2)의 답: 창 최대는 6/6 run에서 0이다. ≥150 present도 0이다. ord 262는 13.06~13.09 s로, lap1194 Y3의 13.08 s와 대응한다.

## 2. 정정 1 — `--stale-mask`가 new-game-path에서 조용히 무시됐다(하네스 결함)

- 증거:
  - S1~S6 `candidate/`에 `stale_mask.bin`이 없다.
  - `probe-result.json`에 `stale_mask` 키가 없다.
  - private prefix `drive_c`에도 `inmm_g1_stale_mask.bin`이 없다.
- 원인: `tools/g1_saved_scene_probe.py`의 `if args.new_game_path:` 분기(7228~7245줄)가 `_run_lane`에 `stale_mask`·`stale_mask_state`를 넘기지 않는다. saved-scene 분기(7303줄)는 넘긴다.
  - DLL 쪽 덤프는 선택된 ordinal이면 stale 값과 상관없이 쓴다(`g1_mirror2x.c` 2292~2298줄). 따라서 파일이 없다는 것은 env가 전달되지 않았다는 뜻이다.
  - 다른 경로의 mask 덤프는 정상이다(lap1097·1127·1147·1149 run에 `stale_mask.bin`이 있다). new-game-path에서 mask를 쓴 것은 lap1210이 처음이다.
  - C의 `g1_stale_mask_state_parse`(`g1_stale_mask.h` 98줄)는 3·20·23·27·29만 받는다. PS5·PS7(`"5"`·`"7"`)은 3으로 떨어진다.
- 판정 영향: 없다. `stale_pixels` 지표는 mask와 무관하게 매 present 계산된다(`g1_mirror2x.c` 2229줄). 0/6 판정은 그대로 유효하다.
  - 다만 서명이 나왔더라도 SIG-0 위치 확정은 구조적으로 불가능했다. lap1209 middle(사전등록)이 이 분기를 확인하지 않은 누락이다.
  - lap1210 기록의 "`--stale-mask 250-313` 적용"은 "명령에는 넣었으나 후보 lane에 전달 안 됨"으로 읽어야 한다.
- 처리: 아래 H-PS5W0의 W0-0으로 수리한다.

## 3. 질문 (3)·(4) — 빈도와 C 변경 비교

- 과거 기준(같은 계열 new-game-path run 65개, lap1167~lap1202, 팩 켬/끔·길이 혼합): 서명 run은 15개다.
  - D2·H1·OFF1(1169), OFF1·S1(1171), G1(1173), U1(1182), E1·E3(1184), U1(1186), K5(1190), T0·X2(1192), Y3(1194), P0(1196).
  - lap1196 P0까지 61 run 중 15 run이므로 24.6%다.
  - 장기 run(PS3 present ≥5,800) 41개에서 12.5~16 s ≥50 px 군집은 11/41이다.
- 현재 source에서는 0/8이다.
  - lap1196 P0 다음의 source 변화: lap1198 H-HDB4가 C를 바꿨다. lap1198 F1은 `direct_draw_trace.c`만 현재와 다르고, lap1202 A1은 DLL 타임스탬프 외 bridge 소스가 현재와 동일하다.
  - 그 뒤 run은 F1·A1·S1~S6 = 0/8이다.
  - p=0.246 가정에서 0/6이 나올 확률은 0.754^6 ≈ 18%, 0/8은 ≈ 10%다. 5% 수준에서 우연을 배제할 수 없다. 6 run만 보면 95% 상한은 39%다.
- 기제 대조:
  - lap1196 P0의 서명 present(ord 262·303~305)에는 lap1198이 바꾼 7인자 혼합 writer(`0x4678C0`·`0x468360`) 경로 호출이 없다.
  - 그 present의 counter 증가는 bbox/primitive 호출 1회, 새 identity key 1개(262), tinted 22/95다. 비서명 P1·S1과 같다.
  - 따라서 "lap1198 C 변경이 서명을 없앴다"는 기제 근거가 없다. 판정은 **우연 또는 환경 변동으로 둔다(미확정)**.
- 반증 1: 서명 run에서 present당 `clipped_calls`가 1 많다는 가설(P0 24 대 P1·S1 23)을 세웠으나, 전체 run에서 구분되지 않았다(`clip_split.txt`). 기록만 남긴다.
- 참고: 창 안 `stale_pixels` 합은 `primitive_stale_pixels_total` 증가분과 run마다 같다. 이것은 두 값이 같은 카운터(`g_stale_pixels` 누적)이기 때문이고, 새 정보가 아니다.

## 4. 판정

- **H-SIG0 `NOT_REPRODUCED` 수용**(불일치 0, 정정 1 = mask 미전달 하네스 결함, 판정 영향 0).
- 쌍봉 backlog는 **닫는다**. 기록할 사실은 다음과 같다.
  - 현재 source 0/8.
  - 과거 15/61, 1 present짜리 일시 stale ≤305 px(화면의 0.06%, 50 ms).
- 재개 조건은 둘이다.
  - (a) 사용자 깜빡임 보고.
  - (b) 이후 F0 계열 run에서 12.5~16 s ≥150 px가 다시 관측됨. 이 경우 W0-0 수리가 끝난 하네스로 SIG-0을 재개한다.
- 추가 run은 하지 않는다(사전등록 규칙).
- 다른 일시 군집도 같은 등급이라 우선순위가 낮다(`clusters.txt`): 75~80 s 90 px(5/41), 140~145 s 79 px(4/41), 225~230 s 79~92 px(7/41).

## 5. 새 근거 — PS5·PS7 영구 stale은 결정적이다

lap1210 6 run의 마지막 present 기준이다(`ps57.py`).

| 상태 | stale (6/6 run 동일) | nearest |
|---|---|---|
| PS5 | 5,043 px | 1,534,872/1,920,000 |
| PS7 | 1,398 px | 1,514,996/1,920,000 |
| PS9 | 0 | — |

- PS5·PS7 값은 lap1156 재계산 값(PS5 5,044, PS7 1,398)과 같다. 사용자가 새 게임을 시작할 때마다 지나는 화면에 매번 남는 품질 손실이다. 일시 blip보다 재현성(6/6)과 가시성이 높다.
- lap1156 §3에 따르면 PS5 캡처 stale의 60.6%가 지도 목록 글자 띠 9개다(x445..593·y118..287, 줄 너비가 스크래치 357×248 글자 너비와 9/9 대응).
  - writer는 스크래치에서 화면으로 복사하는 쪽으로 보이나 미식별이다. 정황은 강하나 확정은 아니다.
  - 귀속을 막던 것은 하네스 결함 둘이다.
    - (i) `--screen-watch-state 5`를 켜면 PS7→PS5 전환 barrier가 타임아웃한다(lap1153 a7, lap1154 backlog).
    - (ii) 위 §2의 mask 미전달과 PS5/7 상태 파서 부재.

## 6. 다음 work 사전등록 — H-PS5W0: PS5 지도 목록 글자 stale writer 귀속

**가설:** PS5 영구 stale의 지도 목록 띠는 기존 미러 hook 밖의 writer가 357×248 스크래치를 화면 back buffer로 복사해서 생긴다. 표본점 쓰기 watch로 그 writer의 EIP를 잡을 수 있다.

**구성:**
- 현재 트리 DLL, 팩 끔, 기본 env.
- 명령 기반은 lap1210 F0와 같다: `--hd-source scale2x --new-game-path --new-game-start`. PS5 체류만 필요하므로 `--new-game-act/--new-game-play`는 work가 판단한다. 단 PS5 present가 ≥64개여야 한다.
- 템플릿은 공유 temp `20261009_lap1210_work_hsig0/scripts/run.sh`다.
- 격리 game 사본·prefix·빈 Xvfb를 쓰고, run이 끝날 때마다 `game` 사본만 지운다.

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| W0-0 하네스 수리 | (a) `--new-game-path` 분기가 `stale_mask`·`stale_mask_state`를 후보 lane에 전달한다. (b) `--stale-mask-state` choices와 C `g1_stale_mask_state_parse`에 5·7을 더한다. 기존 값의 동작은 바꾸지 않는다. (c) 회귀 테스트: new-game-path 전달 단언과 C 파서 `"5"`·`"7"`, `"57"`·`"4"` 기본값 단언을 넣는다. 수리 전 RED, 수리 후 GREEN을 기록한다. | 테스트 RED→GREEN. 기존 3·20·23·27·29 동작 불변 |
| W0-1 위치 | `--stale-mask <PS5 끝쪽 ordinal 범위> --stale-mask-state 5`로 1 run 돌린다(실패 원인이 추적 가능하면 수리 후 최대 2 run). 범위는 같은 run의 PS5 present 수를 보고 정한다. 진입 직후보다 정착 뒤가 좋다. | `stale_mask.bin`이 생성되고, 덤프 present마다 mask의 stale(값 2) 개수 = trace `stale_pixels`이다. 연결 성분 bounding rect를 lap1156 띠 좌표와 대조하고, 띠 안 비율을 기록한다(≥50%이면 위치 확정) |
| W0-2 watch 진입 | `--screen-watch --screen-watch-state 5`의 PS7→PS5 barrier 타임아웃을 추적 가능한 결함으로 다룬다. 원인을 찾아 최소 수리한다. 예: watch arm을 PS5 진입 뒤로 미루기, `--drift-samples` 표본 3점으로 감시 범위 줄이기. 진단용 opt-in 경로만 바꾸고, 기본 꺼짐 경로의 바이트 동작은 그대로 둔다. 수리→재실행은 최대 3 cycle이다. | PS5 present ≥64가 기록되고 barrier 통과 |
| W0-3 귀속 | W0-1 성분에서 지도 목록 한 줄 안 stale 픽셀 3점을 `--drift-samples X,Y;X,Y;X,Y`로 건다. 최대 4 run, hit run 1개가 나오면 멈춘다. | PS5 present에서 표본점 쓰기 hit ≥1. EIP·스레드·호출처(objdump)를 기록하고, 기존 hook인지 새 함수인지 귀속한다 |

**결론 규칙:**
- W0-1 mask와 지표가 불일치하면 하네스나 진단 결함이다. 고쳐서 다시 돌린다.
- W0-2를 3 cycle 수리해도 barrier 원인을 설명하지 못하면 `BLOCKED`로 둔다(근거·시도·다음 대안 기록). W0-1 위치 결과만으로 마감한다.
- W0-3 hit가 0이면 writer UNKNOWN과 근거를 기록한다(표본점이 성분 안이었는지, 쓰기 없는 stale = cover 위상인지).
- 제품 미러 수리는 하지 않는다. 귀속 결과를 보고 다음 middle이 H-PS5W1 수리를 사전등록한다.

**하지 않는 것:** 제품 미러 동작 변경, 팩 켬, 시험판·사용자 전달, G2~G5 접촉, 서명 쌍봉 추가 run.

**검사:** 하네스·C 진단 변경이 있으면 테스트 RED→GREEN, `make lint`·`make typecheck` 뒤 `make check` 1회, SAFETY를 한다. 장기 run은 세션이 끝까지 기다린다(PID·`.exit` 파일 대기, `pgrep -f` 자기 일치 금지).

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다(H-HDU3는 middle이 사전등록).

## 7. 검증

- 이번 회차 변경: 문서(STATUS·INBOX 메모·이 기록·ESCALATE_SOL 보존본)와 공유 temp 재계산 스크립트뿐이다.
- 전체 `make check`는 SKIP했다. source는 lap1208 full PASS 2042 그대로이고, 그 뒤 바뀐 source는 0이다.
- SAFETY·CONTEXT 결과는 STATUS에 보강한다.
- 원본 SHA MATCH. 게임 run 0. 커밋 0.

## 8. 다음 한 가지

work H-PS5W0(§6). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선이다.

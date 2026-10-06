# G1 W70 P4 — P3 2단 통합 수용, 지형은 같은 렌더러의 blitter 5종: 구조 판정 회차 없이 hook 확장 구현 (lap858 strategy, 2026-10-02)

> **lap863 strategy 정정:** §5.1의 `<30%` 반증 조건은 고정 카메라 창(B-3)에만 적용하고, 스크롤(B-5)과 "다음 후보 `0x466280`"은
> `G1_STRATEGY_W70_P4B_TERRAIN_CACHE_LAYER_LAP863.md`가 대체한다. A·B-1~4·C·D와 임계값은 그대로 유효하다.

- 발행: lap858 strategy. 실제 모델 Claude Code `claude-fable-5-1`(러너 지정 strategy 역할, effort 세션 비노출, 자동 폴백 아님).
  게임 실행0, 제품/하네스/validator source·binary 변경0, 커밋0.
- 호출 사유: lap855·lap857 일반 middle이 같은 P3 gate를 "마감 경계"로 보고 두 번 연속 승격만 하고 종료했다
  (`loop/ESCALATE_SOL`, 보존본 `docs/history/20261002_lap858_prior_lap857_escalate_sol_archive.md`). lap855~858은
  제품 코드·실행 증거가 늘지 않은 회차이므로 PROMPT ③의 "세 번째는 strategy가 계속/중단을 먼저 판정"에 해당한다.
- 입력 근거(이 세션이 직접 읽고 재계산): lap853~857 기록, P3c 카드, W70 카드, 공유 temp
  `lap854_p3c_{latch_probe,gate1,gate2,gate3}/pair-result.json`·`candidate/trace_raw.jsonl`,
  `lap855_middle_review/synthetic_*.jsonl`, `lap857_middle_review/review.json`, 현재 `tools/inmm_stub/g1_*.c`·
  `tools/g1_hd_scale2x_probe.py`, 보호 원본 EXE의 read-only disassembly, lap821~831 census/asset-key raw.
- 이 카드는 P3c 카드(`G1_STRATEGY_W70_P3C_ENV_LATCH_COMPOSE_LAP853.md`)를 **종결**하고 W70 카드 §2 P4를 **구체화·대체**한다.

## 0. 판정 요약

1. **P3 2단 통합 수용 = `PASS(partial)`.** P3c 카드 §3의 검수 항목은 middle tier 두 세션이 나눠서 전부 독립 확인했다
   (lap855: latch·성능·source·입력·구도, lap857: validator 수리). 이 세션은 그 합이 조건을 채우는지 확인하고 핵심
   수치를 다시 계산했다(§1). 새 검증을 strategy가 대신한 것이 아니라 두 검수 결과의 합에 대한 범위 판정이다.
   범위는 "hook 2종(`0x466D50`,`0x4664D0`) 위의 Scale2x 배관·성능·입력 parity"까지이며 G1 합격이 아니다.
2. **절차 판정: W70의 P단계 전환은 '마일스톤 경계'가 아니다.** 마일스톤은 DESIGN §3의 M 단위와 사용자 3단 제출이다.
   P단계 gate는 middle의 2단 판정으로 닫는다(선례: lap831 P1→P2, lap841 P2→P3). 앞으로 middle은 P단계를 **직접
   PASS/HOLD로 판정**하고, `ESCALATE_SOL`은 ⓐ 3회 수리 후에도 원인 미설명 ⓑ 기록과 raw의 실질 충돌 ⓒ G1 사용자
   3단 제출 경계에만 쓴다. 이것은 러너 문구의 해석이며 사용자 지시가 아니다(INBOX 2026-09-29 20:11 반복 속도 지시와 같은 방향).
3. **P4 = `FEASIBLE`(strategy 정적 판정, 실행 미검증).** 지형 타일은 별도 캐시/복사 구조가 아니라 **같은 렌더러 객체
   `0xE5BF18`의 프리미티브 5종**이 같은 `+0x1514` 버퍼에 직접 그린다(§3). W70 카드 P4의 "프리미티브로 귀속하면
   P2/P3를 그대로 확장" 분기에 해당하므로 **별도 구조 판정 회차를 쓰지 않고 다음 work가 바로 구현한다**(PROMPT ③ 구현 우선).
4. **G1 W70은 계속한다.** 다음 회차는 work 구현이며, P4 runtime 증거가 나오기 전 문서·재요약 회차를 더 넣지 않는다.
5. 성능 기준 W70 §3.5(ratio ≥0.95, p95 ≤ baseline+16ms, fresh 3 pair)·Scale2x validator·legacy validator·임계값 **불변**.
6. **현재 위치(§2):** 유효 HD coverage는 PS3 프레임의 **p50 6.23%**(5.39~7.26%)다. G1 기준안은 ≥90%이므로 P3 수용은
   "배관이 맞다"는 뜻이지 "화면이 HD다"가 아니다.
7. W70 카드 정정 2건(§6): P1의 "PS3 attribution ≥95%"는 실제로 PS9/PS35 present에서만 수집됐다. P6의 "6인자 tinted =
   목적지 읽기" 가정은 lap821 dest probe(7종 `no_dest_read`, `rect_border`만 `dest_read`)와 다르다.
8. 이 카드는 계획 승인도 G1 마일스톤 판정도 아니다. 2단 middle 검수·3단 사용자 승인은 그대로 남는다.

## 1. P3 통합 근거

| P3c §3 항목 | 독립 확인 | 이 세션 재확인 |
|---|---|---|
| latch 구현(플래그 전수, 의미 보존) | lap855 | `GetEnvironmentVariableA`는 5개 모듈의 `initialize_environment()` 안에만 있고 compose는 루프 밖에서 1회 읽음 |
| DLL/raw/pair SHA·build 입력 42개 | lap855·857 | pair 4개·review.json·validator/test·C 5파일·probe SHA가 기록과 일치 |
| tick rate·p95·present 수 | lap855 | ratio `0.9999997655 / 0.9999920427 / 0.9999969883 / 1.0000019160`, p95 `1→6ms`(+5), 400/400, drop 0 |
| QPC compose ≤50ns/픽셀·≤2% | lap855(6.06ns, 0.93%) | 재계산 안 함(lap855 값 인용) |
| §1.4 부등식 validator 반영 | lap857 | 반례 2건 `BLOCKED`, raw 4개 `PASS`, 독립 재계산 5049 present 위반 0 |
| 입력(selection/empty/drag_exact) | lap855 | 4 pair 모두 true, `scene_state_equal`·source unchanged·cleanup true |
| 구도 | lap855(gate1 육안) | gate1 원본 800×600 / 후보 1600×1200 loaded 캡처 육안 대조, HUD·지형·유닛 위치 일치 |

- 수용하지 않는 것: minimap/production은 양 lane `UNKNOWN(original parity)`(`minimap_gate_restore`·`production_effect` false는
  그 항목). legacy `mirror_validator`는 scale2x 모드에서 `BLOCKED`가 정상이다(P3c §1.4). 20초 창은 카메라 고정
  `[158,101]`·입력 없음이라 스크롤 중 성능은 측정된 적이 없다. 상세 장면 558 unit records는 활성 8인 부하 증명이 아니다.
- 다음 middle이 P4 검수 중 이 통합 판정에 반하는 raw를 찾으면 근거와 함께 P3를 HOLD로 되돌릴 수 있다.

## 2. 현재 coverage (lap854 gate1~3 candidate raw, PS3 present 2678개)

- 유효 HD 픽셀 = `covered_pixels − stale_pixels`. 480,000 대비 min 5.39% / p50 6.23% / p95 7.20% / max 7.26%.
  (`covered_pixels` 최대 130,258=27.14%인 present는 대부분 그 present에서 stale로 무효화된 값이다.)
- hook은 5인자 RLE 2종뿐이다. 화면 대부분을 차지하는 지형과 HUD, 6인자 tinted RLE(호출 수 최다)는 아직 nearest다.

## 3. P4 정적 근거 (상세·old bytes: `analysis/memory_maps/g1_w70_p4_terrain_blitter_family_lap858.md`)

타일 dispatcher `0x435400`이 viewport 포함 여부(`0x465190`)와 shade 테이블 유무로 네 callee를 고른다.

| callee | `ret`/인자 | 역할 | 정적 판독 |
|---|---|---|---|
| `0x468C30` | `0x10` / `x,y,rows,src` | viewport 안, 불투명 | 행 `[skip][len]`+복사. 폭 인자 없음. viewport·목적지 읽기 없음 |
| `0x468CC0` | `0x18` / `x,y,w,h,src,shade` | viewport 안, shade | 렌더러 LUT(`+0x419A0`,`+0x6BCA0`,`+0x19A0`)로 변환. 목적지 읽기 없음 |
| `0x468F00` | `0x14` / `x,y,w,h,src` | 클립, 불투명 | viewport `+0x4D0..+0x4DC` 읽음. 본문 전체는 미열람 |
| `0x4690A0` | `0x18` / `x,y,w,h,src,shade` | 클립, shade | 위 LUT + viewport. 본문 전체는 미열람 |
| `0x468E10` | `0x14` / `x,y,rows,src,lut` | 체커보드 remap(호출부 `0x4351BD`) | viewport·목적지 읽기 없음 |

- 다섯 모두 `renderer+0x1514` 버퍼·`+0x10` stride를 쓴다 → 기존 `mirror_reinvoke`의 버퍼 치환이 그대로 적용된다.
- 자산 키는 이미 runtime으로 증명됐다: source = `base[file]+offset[file*0x2FE+frame]`, equality 1061/1061(lap830/831).
- 이것은 정적 판독이다. "이 5종이 PS3 지형 픽셀의 실제 writer"라는 것은 §5의 coverage 수치로 검증·반증한다.

## 4. P4 work 범위 (한 lap, 구현→빌드→격리 실행→원인 수리 반복 최대 3회)

공통: 기본 OFF opt-in, EXE 파일 불변, old bytes 대조 후 설치·불일치 시 전체 rollback, save006 same-save fresh pair,
private 사본·prefix·Xvfb, 실행 후 game 사본 삭제, 기존 raw 덮어쓰기 금지. 새 코드는 새 파일 권장(`g1_mirror2x.c` 991줄).

### A. hook 확장 (수리 본체)
1. 위 5종을 **인자 수에 맞는 thiscall wrapper**(4/6/5/6/5인자, `ret` 크기와 일치)로 감싸 기존 sentinel A/B 재호출→
   key-bound 캐시→Scale2x→compose 경로에 연결한다. 인자 수가 틀리면 스택이 깨진다(W70 §1의 6인자 경고와 같은 종류).
2. `0x468C30`·`0x468E10`은 폭 인자가 없다. scratch bbox 폭은 행 헤더 `max(skip+len)`에서 얻는다(자산 바이트 읽기이며
   그리기 재구현이 아니다). 좌표·크기는 부호 있는 16비트로 해석한다.
3. **키 확장:** shade/lut 인자가 있는 writer는 키에 그 포인터와 내용 digest를 포함한다. 같은 타일이라도 shade가 다르면
   출력이 다르다. 렌더러 LUT(야간 팔레트 등) 변화는 기존 cache-hit 내용 비교가 잡아 refresh한다.
4. `G1_HD_KEY_LIMIT 256`은 (타일×shade) 조합에 모자랄 수 있다. save006(+스크롤)의 고유 키 수요를 raw에 남기고 기존
   byte limit 안에서 상한을 올린다. 캐시 miss는 **항상 nearest로 떨어져야 하고** 계수돼야 한다(틀린 HD 금지).
5. unclipped HD 프레임: `0x468C30`/`0x468CC0`/`0x468E10`은 클립이 없으므로 (0,0) 재호출에 viewport 변경이 필요 없다.
   클립 variant 2종은 기존 viewport 전체 replay 경로(원복·mutation 계수 포함)를 쓴다.
6. Fast 회귀 가드: 기존 `tests/test_g1_mirror2x.py` source-scan 방식으로 5종의 주소·old bytes·인자 수를 고정한다.
7. 금지: EXE 패치, Scale2x/legacy validator·임계값 변경, 그리기/클립/LUT 재구현, 새 의존성, G2/G5 source·
   `local/runtime/g2_*`·`*g5_esl2608*` 접촉, P5(HUD/tinted) 코드, 커밋.

### B. 배관 pair 1회 (`--hd-source scale2x --performance-window --perf-sections`)
사전 등록 기대값:
1. 5종 설치 5/5, writer별 호출 수 >0(0인 writer는 이름과 함께 보고), crash 0, `scene_state_equal`, source unchanged, cleanup.
2. Scale2x validator `PASS`(수정 없이): outside diff 0, palette 위반 0, per-present 부등식, lookup miss/invalid 0,
   `full_frame_calls`·`clip_replay_mismatches`·viewport mutation/restore failure 0.
3. **유효 HD coverage(PS3 present, `covered−stale`) p50 ≥ 55%(264,000픽셀).** 근거: 화면에서 HUD를 뺀 맵 영역이 약 76%이고
   그 위 스프라이트·효과를 빼면 지형이 60%대라는 캡처 기반 추정 + 기존 6%. 추정이므로 §5의 반증 구간을 함께 둔다.
4. 지속성: 창의 마지막 20 present p50 ≥ 첫 20 present p50 × 0.9(유닛이 지나간 자리의 지형이 다시 HD로 돌아오는지).
5. 스크롤: 카메라 변화 1회(기존 `DOWN` 경로) 뒤 30 present 안에 coverage가 3의 기준을 회복하고 그 사이 outside diff 0.

### C. fresh 3 pair gate (계측 env OFF, W70 §3.5 불변)
- 3 pair 모두 `tick_rate_ratio ≥ 0.95`, `present p95 ≤ baseline + 16ms`, scene equal·source unchanged·cleanup,
  Scale2x validator PASS, loaded 캡처 non-black·1600×1200, `selection_target`·`empty_click`·`drag_exact` true, B-3 coverage 유지.

### D. 이월 가능 항목 (B·C가 끝나고 시간이 남을 때, 아니면 다음 work lap 첫 작업)
1. **PS3 잔여 분해:** census 표에 5종을 추가하고 present 맵 수집을 `program_state==3`으로 한정해, PS3 프레임의 writer별
   last-writer 비율을 1회 남긴다(W70 P1이 남긴 공백, §6). P5 순서를 이 수치로 정한다.
2. **스크롤 중 성능 1 pair:** 성능 창 동안 카메라 키 입력을 반복하는 모드를 probe에 추가해 ratio·p95를 **보고**한다.
   P4 gate 조건은 아니지만 G1 사용자 제출 전에는 W70 §3.5를 이 창에서도 만족해야 한다(기준 강화, 완화 아님).

## 5. 판정·정지 규칙

1. **반증:** 5종 hook이 활성(호출 수 >0)인데 B-3 coverage p50 < 30%면 §3의 귀속이 틀린 것이다. 수리를 더 하지 말고
   writer별 호출/covered 수와 D-1 PS3 census를 남겨 strategy로 넘긴다(다음 후보: `0x466280` block_copy 경로).
2. 30% ≤ p50 < 55%: 빠진 variant·stale 원인을 raw로 적고 **같은 카드로 work 1회 추가**(총 2 work lap). 그래도 미달이면 strategy.
3. **성능 FAIL 시 허용 수리(순서대로, strategy 재호출 없이):** ⓐ QPC 구간 표로 최대 구간 확인 ⓑ 출력 바이트가 같은
   순회 병합·bbox 한정 ⓒ **클립 없는 3종에 한한 cache-hit 빠른 경로** — 키가 캐시에 있으면 sentinel 2회 재호출을
   생략하고, 원본 호출 직후 실제 버퍼의 해당 영역을 캐시 프레임(마스크·값)과 1회 비교해 **전부 일치할 때만** 캐시로
   합성, 불일치는 기존 경로. 클립 variant에는 적용하지 않는다. 3회 수리 뒤에도 FAIL이면 같은 카드로 work 1회 추가,
   2회째도 FAIL이면 strategy(보류 대안: sentinel 1회화 일반화, present dirty-rect).
4. latch·hook 뒤 state/scene hash가 달라지거나 크래시가 나면 즉시 ESCALATE(안전·근거 충돌).
5. B·C PASS → work는 임의 마감하지 않고 middle 2단 검수로 넘긴다. **middle은 §0-2대로 직접 PASS/HOLD를 판정**하고
   PASS면 다음 work가 D와 P5로 간다. "수리 대상이 명확한 구현 결함"이면 짧게 확인만 하고 work로 되돌린다.

### middle 검수 조건 (work PASS 주장 시)
- 5종 wrapper의 인자 수·old bytes·rollback 열람, 키에 shade/lut가 들어갔는지, miss→nearest 경로, DLL/raw/pair SHA·build
  입력, coverage·지속성·스크롤 수치와 tick rate·p95 독립 재계산, validator 무수정 확인, source unchanged·cleanup.

## 6. W70 카드 정정과 이후 순서(잠정)

- **P1 공백:** lap821~830 census의 present 맵 64장은 PS9/PS35(메인 메뉴·불러오기 화면)에서 소진됐고 PS3 맵은 없다. P1 `PASS(partial)`의
  "attribution 100%"는 PS3 프레임 구성 근거가 아니다. D-1이 이 공백을 메운다.
- **P6 재분류:** 6인자 tinted RLE `0x466EA0`/`0x466540`은 lap821 dest probe에서 `no_dest_read`였다. 목적지 읽기 writer로
  미루지 말고 P4 뒤 "키에 6번째 인자를 넣은 같은 방식"의 확장 후보로 본다. `dest_read`는 `rect_border`뿐이다.
- 잠정 순서: P4 지형 → **P5 = D-1 수치가 큰 순서**(후보: tinted RLE 2종, `0x466280` block_copy, DirectDraw HUD 표면) →
  텍스트/GDI. `rect_fill`·`rect_border`·`set_pixel`은 "원천 그림 없음" 후보다. 순서 확정은 D-1 뒤 middle이 한다.

## 7. 남은 위험

- §3은 정적 판독이고 coverage 55%는 캡처 기반 추정이다. 지형이 유닛이 지나간 뒤 다른 경로(배경 복원 복사)로 되살아나면
  B-4 지속성에서 드러난다.
- 지형은 픽셀 수가 지금의 약 10배다. 현재 여유는 p95 +5ms(한도 +16ms), 프레임 예산 추정 28ms/50ms다. shade variant는
  픽셀당 LUT 연산이 무거워 재호출 2회가 그대로 비용이 된다 → §5-3ⓒ를 미리 허용해 둔다.
- Scale2x는 잡음 질감 타일에서 nearest와 거의 같은 그림을 낸다. P4가 증명하는 것은 지형의 HD 경로이지 화질이 아니다.
- 사용자 HD 팩(`SYW2_G1_HD_PACK`)을 shade 타일에 쓰려면 2배 해상도에서 shade를 적용해야 하는데 이는 LUT 재현이 필요하다.
  지금은 다루지 않고 잔여 위험으로만 적는다.
- 측정은 Xvfb/Wine·save006 한 장면·카메라 고정이다. 두 번째 장면과 스크롤은 G1 제출 전 필수로 남는다.
- minimap/production `UNKNOWN(original parity)`, GDI/HUD/전체 HD coverage, 1080p 표시 정책, 사용자 3단 승인 미충족.

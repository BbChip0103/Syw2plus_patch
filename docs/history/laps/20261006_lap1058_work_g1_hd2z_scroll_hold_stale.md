# 2026-10-06 | lap1058 | G1 work — H-D2z 현행 hook 스택 D-2 왕복 hold 재측정(측정 전용)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 source·테스트 변경 0.
- 가설: lap1008(H-D2i) 이후 H-B~H-Z hook 10여 개와 heal/heal2가 붙었어도 save006 D-2 왕복 hold(UP 24칸→DOWN 24칸)는 성능·parity가 lap1008 수준이고 복귀 뒤 stale 0이다.
- 사전등록(lap1057 §5): D2z-0 안전 7종 0·cleanup·source_unchanged·`heal2_skipped` 기록 / D2z-1 I-0(24칸·clamp 없음·최종 카메라 (158,101)·parity)·I-1(hold 창 p95 ≤ 고정+16·ticks/s 비 ≥0.95) / D2z-2 hold 창 stale 중앙값·최대와 복귀 뒤 마지막40 중앙값 기록(0이면 PASS, >0이면 새 잔여로 기록) / D2z-3 V1/V2/V2q·V2s W-1·parity·input_effect lap1008 수준.
- 변경 파일: 없음(uncommitted 기존 변경 그대로). 원본 EXE SHA `b56986e0…08a8ac`, 비합성 save006 `616b7997…a0d064`, 세 run 모두 `source_unchanged` [true,true]·cleanup [true,true], `game` 사본 run마다 삭제.
- 실행(공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1058_work_d2z/`, 로그 `logs/gates/lap1058_d2z_{r1,r2,m1}.log`): `run_d2z.sh` = lap1008 러너와 같은 옵션 `--hd-source scale2x --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys UP,DOWN --p4b-s-snapshot --reference-completed-states <lap888 scroll-phase-diagnostic-result.json> --stale-mask 0-1600/30`, save006 순차 2회(r1·r2, load 3.1~3.3 ≤ 8, exit 0·0). 이어서 `run_d2z_mask.sh` m1 = 같은 옵션 `--stale-mask 129-143,227-230`(stale 위치 덤프만 다름; exit 0). 분석 `analyze_d2z2.py`(lap1008 `analyze_d2i.py` 복사·T 치환 + stale 요약 추가)·`analyze_d2z.py`.

## 측정(work 자체 계산, 판정 아님 — middle 독립 검수 필요)

| 항목 | lap1008 (hold 창 6/7/7/7) | H-D2z r1 / r2 | 판정 |
|---|---|---|---|
| D2z-0 안전 7종 | 0 | 0 / 0 (m1도 pair PASS), cleanup [T,T]·source_unchanged [T,T] | PASS |
| D2z-0 `heal2_skipped` | — | 0 / 0 (`heal2_presents` 63/65, `heal2_pixels` 21,971/22,839, heal_presents 66/68) | 기록 |
| D2z-1 I-0 | 24칸·clamp 없음·(158,101) | UP·DOWN 각 24칸·clamp_free·두 lane 카메라 열 동일·최종 (158,101)·parity PASS | PASS |
| D2z-1 I-1 p95 | 고정 7/6~10, hold 6/7/7/7 | 고정 n=123 p95 7/7(max 7/8)·hold 창(24692..24824) n=133 p95 **6/7**(max 8/17) | PASS(≤고정+16) |
| D2z-1 I-1 ticks/s | 1.0014~1.0048 | 비 **1.0025 / 1.0028** | PASS(≥0.95) |
| D2z-1 candidate `scroll_gate` | PASS | UP·DOWN 둘 다 PASS(coverage p50 475,413 / 476,777) | PASS |
| D2z-3 | V1/V2/V2q PASS | pair PASS·V1 PASS·V2 PASS·V2q PASS(four_black 0)·V2s W-1 PASS(unexplained **29** ≤2,000; raw single 1,899 ≤2,000도 PASS)·scale2x PASS·minimap_diagnostic_parity PASS·input_effect PASS·terrain_scroll_parity PASS·scroll_after PASS | PASS |
| D2z-2 hold 창 전체(tick 24692..24860, present idx 123..291, n=169) stale | — | 중앙값 **0**·최대 **12,976**·>100 present 19·비0 20 (r1·r2 수치 전부 동일, m1 덤프 stale 개수도 일치 = 결정론) | 기록 |
| D2z-2 복귀 뒤 마지막40 | 0 | **0 / 0** (hold 끝 이후 비0 present 7~8개, 모두 tick 24867~24924: 1·1·159·559·959 + 카메라 (165,87)의 1 px) | **PASS** |
| D2z-2 hold 직전 고정 카메라 | — | hold 직전 마지막40 0; 로드 직후 첫 16 present(tick 24570..24584) 16,985~19,052 = 로드 과도 | 기록 |

## D2z-2 새 잔여: 스크롤 이동 중 일시 stale(위치 덤프 m1, bbox는 800×600 화면 좌표)

- UP 구간 present 129~143(tick 24698~24712, 카메라 (151,94)→(137,80)): stale 5,602→6,484→4,357→4,357→2,326→2,330→2,569→7,367→**12,976**→7,941→2,732→2,492→3,301→2,158→1,379. bbox 열 x0..64(129~134)→x0..24~55 로 **y 구간이 present마다 약 32 px 아래로 이동**(y0..165 → … → y429..489)하는 좌측 띠, 135~138은 x0..595~665로 넓어짐(상단 y0..449 포함).
- DOWN 복귀 구간 present 227~230(tick 24796~24799, 카메라 (143,86)→(146,89)): stale 6,207·**11,372**·6,026·1,012, bbox x401~524..648 y0..100(상단 우측) → 위로 줄어듦.
- 합집합 36,837 px, 열 구간 x0..64 ∪ x401..665, 행 y0..489. 첫 present마다 한 번 크게 생겼다가 수십 present 안에 0으로 회복(hold 창 총 169 present 중 19개 >100). 정지 상태(고정 카메라)에는 없다.
- 원인은 UNKNOWN: 이 구간의 writer·미후킹 함수·카메라 이동에 따른 레이어(캐시) 이동 처리 여부 미조사. 후보: (a) 스크롤 중 `layer_move`(캐시 이동)와 present 순서 경합, (b) 좌측 HUD/미니맵 영역 미후킹 writer, (c) 상단 우측 글자/GDI. 가설 증거 없음, 사전등록 PASS/FAIL 밖이라 수리하지 않았다.
- r1·r2·m1 세 run에서 같은 present의 stale 수치가 동일해 부하·타이밍 변형이 아니다(결정론 입력).

## 회귀 / 남은 위험 / 독립 검수

- 제품 변경 0이라 회귀 가능성은 측정 자체의 방법 차이(마스크 지정만)이며 lap1008 `analyze_d2i.py`를 이름 치환해 같은 추출을 썼다. hold 창 stale 요약은 lap1008에서는 계산하지 않았으므로 **이전 대비 증감은 UNKNOWN**(hook 스택 이전에는 stale이 컸을 가능성이 높으나 미측정).
- 판정은 work 자체 계산이다. middle이 pair-result·trace_raw·stale_mask.bin을 새 스크립트로 독립 재계산해야 한다.
- 사용자 승인 상태: G1 사용자 마일스톤 미요청·미승인. G6/G7 사용자 합격(APPROVALS lap989) 대기, 루프 비차단.
- 다음 한 가지(제안): middle H-D2z 독립 검수 후, 스크롤 중 일시 stale 두 구간(좌측 띠 x0..64·상단 우측 x401..665)의 writer 귀속(`--census-only`/`--screen-watch` 표본을 좌측 띠 한 점·상단 우측 한 점에 두는 work H-D2w) 또는 가장자리 마우스 스크롤 중 선택.

## 검사

- 기록 freeze 뒤 `checks/safety.sh check` SAFETY_PASS. 전체 `make check` SKIP(제품 source·테스트 불변, lap1056 full PASS 1639 유효, Fast는 런타임 증거 아님; 이번 증거는 save006 D-2 hold 게임 3회 launch).

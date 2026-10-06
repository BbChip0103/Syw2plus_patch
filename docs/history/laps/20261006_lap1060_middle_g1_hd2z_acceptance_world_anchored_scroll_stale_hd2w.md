# 2026-10-06 | lap1060 | G1 middle — H-D2z 독립 검수·스크롤 일시 stale 위치 성질 판정 → work H-D2w 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source 변경·commit 0.
- 입력: lap1059 work `loop/ESCALATE_SOL`(SHA256 `1f70a6293875992ee7affebab44b6ffb875ab52358ed72ea594fc5ea033fc6ff`, 원문은 아래 부록, 처리 뒤 삭제), 기록 `20261006_lap1058_work_g1_hd2z_scroll_hold_stale.md`, 산출물 공유 temp `20261006_lap1058_work_d2z/`(r1·r2·m1).
- 산출물 해시 재확인(인계 값과 일치): r1 `pair-result.json` `ac188d54…e169a1`, r2 `e968c28b…441b86`, m1 `9de2bf21…849087`, m1 `candidate/stale_mask.bin` `5ca934c3…910fe7`.
- 가설(검수 대상): lap1008 이후 H-B~H-Z hook과 heal/heal2가 붙은 현행 스택에서도 save006 D-2 왕복 hold(UP 24→DOWN 24칸)는 성능·parity가 lap1008 수준이고 복귀 뒤 stale 0이다(측정 전용).
- 사전등록(lap1057 §5): D2z-0 안전 7종 0·cleanup·source_unchanged·`heal2_skipped` 기록 / D2z-1 I-0·I-1 / D2z-2 hold 창 stale 분포 기록·복귀 뒤 마지막40 0이면 PASS / D2z-3 V1/V2/V2q·V2s W-1·parity·input_effect.

## 1. 독립 재계산(work `analyze_d2z*.py`·제품 helper 미사용)

스크립트 `temp/Syw2plus_patch/20261006_lap1060_middle_review/recalc_lap1060.py`(SHA256 `613ae629…a8ef55`, 새 middle 코드; I-0/I-1 정의는 lap1009 middle과 같음: nearest-rank p95, ticks/s = sim_tick 차/ts 차) → `recalc_lap1060.json` `ba6b3b4f…10a7`·`recalc_lap1060.txt` `f8da8a2e…43a4`, stderr 0 B. scroll_after PNG는 middle 소유 RGB Scale2x로 재계산.

| 항목 | middle 재계산 r1 / r2 / m1 | work 보고 | 판정 |
|---|---|---|---|
| D2z-0 | pair PASS 3/3·EXE `b56986e0…` 양 lane·fixture `616b7997…` index 7·cleanup [T,T]·game_removed [T,T]·source_unchanged [T,T]·execution_source unchanged·안전 7종 max 0·`heal2_skipped` 0 (heal 66/68/65·heal2 63/65/62) | 같음 | 일치·PASS |
| D2z-1 I-0 | 두 lane 두 키 모두 24칸(재계산=보고)·clamp 없음(전이 단위 (±1,±1))·두 lane 카메라 전이 열 동일·최종 (158,101)·parity PASS(false 항목 0)·tick plan 두 lane 동일·candidate `scroll_gate` PASS×2(cov p50 475,413/476,777) | 같음 | 일치·PASS |
| D2z-1 I-1 | 고정 n=123 p95 7/7/6·hold(24692..24824) n=133 p95 **7/7/7**·max 8/17/8·ticks/s 비 **1.0024/1.0028/1.0026** | hold p95 6/7·비 1.0025/1.0028 | 판정 불변(한도 고정+16, ≥0.95)·정정 1 |
| D2z-2 hold 창 | tick 24692..24860 = ps3 present 123..291(n=169): 중앙값 **0**·최대 **12,976**(p137)·>100 **19**·비0 20 | 같음 | 일치 |
| D2z-2 구간 | >100 구간 2개: p129..143(tick 24698..24712, 카메라 (151,94)→(137,80), 15값 work 열과 동일)·p227..230(tick 24796..24799, (143,86)→(146,89), 6,207/11,372/6,026/1,012) | 같음 | 일치 |
| D2z-2 복귀 뒤 | final_observation(24860)까지 마지막40 중앙값 **0**, 전체 run 마지막40 0, hold 직전 마지막40 0 | 0/0 | 일치·PASS |
| D2z-2 결정론 | hold 창 stale 열 169개·카메라 열·구간이 r1=r2=m1 완전 일치 | 같음 | 일치 |
| 마스크 | 헤더 h[1] = ps3 present 순번(m1 19개·r1/r2 40개 모두 마스크 stale 수 = present `stale_pixels`); m1 bbox 19개·합집합 **36,837 px**·bbox (0,0)-(665,489)·열 공백 x65..400 → 열 x0..64 ∪ x401..665 | 같음 | 일치 |
| D2z-3 | V1/V2/V2s/V2q·scale2x·minimap parity·input_effect·terrain_scroll_parity PASS, scroll_after nearest 110,047·V2 기준/후보 흑 9,202/9,358·V2s raw 1,899·V2q 0(보고와 동일), V2s unexplained middle 27 vs 보고 29 | 29 | 판정 불변·정정 2 |

- 정정 1(전사·정의, 비차단): r1 hold p95는 nearest-rank 7(선형 보간 6.4 → work 6), r1 비 1.00244 → 1.0024. lap1009 정정과 같은 정의 차이. 한도 23 대비 판정 불변.
- 정정 2(독자 구현 차, 비차단): V2s unexplained는 middle RGB Scale2x 27, 제품 aggregate 29(raw 1,899는 일치). 둘 다 ≤2,000 W-1 PASS. 제품 값을 바꾸지 않는다.
- 참고(비차단, 기존): candidate `mirror_validator` BLOCKED(nearest oracle <0.999, errors 1,613/1,587/1,597)는 scale2x HD 원천에서 lap1008 s2(1,586)에도 같은 상태 — 회귀 아님, pair 판정 경로 밖.
- work 미보고 관측: hold 창 밖 p313..315(tick 24882..24884, 카메라 (158,101)) stale 159→559→959→p316 0이 3 run 동일(결정론). 마지막40·사전등록 창 밖이며 hold 뒤 장면 동작 시점의 3-present 일시 stale — 기록만.

## 2. 새 근거 — 스크롤 일시 stale은 world 고정(레이어 이동 동반)이다

- 카메라는 두 구간 모두 present당 정확히 1칸((−1,−1) 또는 (+1,+1)) 이동하고, 마스크 띠도 present당 **32 px 세로 이동**한다: UP 좌측 띠 하단 y165→197→223→255→287→319(p129..134), p139..143 y304..487→429..489(뷰 하단 489에서 잘림). DOWN 상단 우측 덩어리 y 하단 100→89→55→23(위로 빠져나감). 즉 stale 픽셀이 화면 고정(HUD·GDI 글자)이 아니라 **월드 내용과 함께 움직인다**.
- **같은 카메라 = 같은 위치**: 상단 우측 덩어리는 UP p135..138(카메라 (146,89)→(143,86), 위에서 자라며 들어옴, 하단 23/55/87/98)과 DOWN p227..230(카메라 (143,86)→(146,89), 같은 자리에서 위로 빠짐)에 나타난다. 카메라 (143,86)에서 UP p138 y5..98 ≈ DOWN p227 y7..100. 표본 (465,6)은 p135..137·p228..230 양쪽 stale. → 월드 특정 영역(카메라 ≈(143..146,86..89)에서 화면 상단 우측 x≈401..665)에 묶인 stale.
- **좌측 띠는 방향 의존**: UP 카메라 (151,94)→(137,80)에서만 생기고 DOWN이 같은 카메라를 지날 때(p221 (137,80)..p235 (151,94))는 p227..230 상단 우측 덩어리 외 stale 0이다. hold 창 비0 20 = >100 19 + p125 1 px.
- 해석: 후보 (b) 좌측 HUD/미니맵 화면 고정 writer·(c) 상단 우측 GDI 글자는 화면 고정이라 이 이동과 맞지 않는다 → 약화. (a) 레이어(캐시) 이동과 present 사이 처리 또는 스크롤 중 월드를 그리는 미후킹/부분 미러 writer가 남은 후보다. present마다 `layer_move_calls`·`layer_transfer_calls` +1(p124..145·p222..233 전부)이라 이동 자체는 매 present 일어난다. writer 귀속은 미입증(UNKNOWN).

## 3. 판정

- **H-D2z PASS(측정) 수용.** D2z-0·D2z-1·D2z-3 PASS, D2z-2 복귀 뒤 마지막40 0 PASS, 재계산 판정 불일치 0(정정 1·2 비차단). 현행 hook 스택은 D-2 왕복 hold에서 성능·parity 회귀가 없다(lap1008 대비 hold p95 7/7/7 vs 6/7/7/7, 비 ≥1.0024).
- 새 잔여(기록, FAIL 아님): 스크롤 중 일시 stale 2구간(hold 169 present 중 >100 19개, 최대 12,976), world 고정 성질 확인, 정지하면 0. lap1008 이전 hook 스택의 같은 값은 미측정이라 증감 UNKNOWN.
- 사용자 승인 상태: G1 사용자 마일스톤 미요청. G6/G7 사용자 합격(APPROVALS lap989) 대기, 루프 비차단.

## 4. Handoff — work H-D2w(스크롤 일시 stale writer 귀속, 진단 전용)

- 근거: §2로 stale은 world 고정·결정론(r1=r2=m1)이므로 같은 명령으로 같은 present에 같은 화면점이 stale이 된다 → 화면 write watch로 귀속할 수 있다.
- 실행: lap1058 `run_d2z_mask.sh` 옵션 그대로(save006, `--hd-source scale2x --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys UP,DOWN --p4b-s-snapshot --reference-completed-states <lap888 경로> --stale-mask 129-143,227-230`)에 `--layer-drift --screen-watch --drift-samples "3,157;5,341;465,6"`를 더해 순차 2회. 표본 stale present(m1 마스크): (3,157) p129..134, (5,341) p135..140, (465,6) p135..137·p228..230. load ≤8 대기·`game` 사본 삭제 유지. 두 옵션이 `--terrain-scroll`과 같이 안 되면 그 원인을 하네스 최소 수리(RED→GREEN)로 고친 뒤 실행한다(구현 우선); 수리 불가면 BLOCKED 근거를 남긴다.
- 사전등록 PASS/FAIL:
  - W-0: pair PASS·안전 7종 0·cleanup/source_unchanged, I-0(24칸×2·최종 (158,101))과 hold 창 stale 열이 lap1058과 동일(진단 옵션이 장면을 바꾸지 않음; 다르면 차이를 공개하고 귀속은 그 run 기준).
  - W-1 귀속: 세 표본의 stale present마다 마지막 화면 쓰기 EIP·스레드·값과 drift `s` 기록(cov·scr·snap)을 대조해, 미설명 변화 present 전부를 hook 안/밖 EIP로 분류. 미후킹 게임 함수면 시작 주소·호출처(objdump)를 적고, wined3d 스레드면 그 사실을, hook 안이면 해당 미러 경로를 적는다. 귀속 ≥90%면 PASS.
  - W-2 레이어 대조: 같은 present의 1x 캐시(`--census-watch-cache` 또는 drift 캐시 표본)와 화면 값을 대조해 "캐시 이동 누락(H1)" vs "화면 직접 writer(H2)"를 가른다. 판정 불가면 UNKNOWN과 다음 probe.
  - FAIL: 크래시·안전 위반·hold 창 성능 회귀(p95 >고정+16) → 원인 지목.
- 수리는 이번 work 범위 밖(귀속 뒤 다음 middle이 H-D2r 수리 사전등록). 진단 옵션만 쓰므로 제품 source 변경 0이 기본이다.
- 그다음 후보: 가장자리 마우스 스크롤·HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: hold 뒤 p313..315 3-present 일시 stale(결정론), save006 r1 부하 동반 증가형 stale(lap1057 §3 재개방 조건), 미후킹 `0x467E60`, save000 overlay BltFast rejects, 다중 팝업 heal.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT 확인과 focused `.venv/bin/python -m pytest tests/test_g1_rect_fill.py tests/test_g1_mirror2x.py tests/test_g1_overlay_blt.py`(lap1057과 같은 3 파일). 결과는 STATUS 줄에 보강한다. 전체 `make check` SKIP(문서만 변경, source 불변·lap1056 full PASS 1639; 다음 work H-D2w는 진단 전용).

## 부록 — lap1059 `loop/ESCALATE_SOL` 원문(SHA256 `1f70a629…fc6ff`)

```
lap1059 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — 제품 source·게임 실행 0.
사유: STATUS 다음 한 가지 = middle(Opus) H-D2z 독립 검수. work는 자기 계열 lap1058 결과를 승인하지 않는다.
승격 작업자가 할 일(fresh Opus middle):
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1058_work_d2z/ 의 r1·r2·m1 pair-result.json, candidate/trace_raw.jsonl, m1/candidate/stale_mask.bin 을 work 스크립트(analyze_d2z*.py) 없이 새 스크립트로 재계산.
   해시: r1 pair-result ac188d54…e169a1, r2 e968c28b…441b86, m1 pair-result 9de2bf21…849087, stale_mask.bin 5ca934c3…910fe7.
2. 검증 항목: I-0(24칸·clamp 없음·최종 카메라 (158,101))·I-1(hold 창 p95 6/7·tick 비 1.0025/1.0028)·D2z-3(V1/V2/V2q·V2s unexplained 29)·hold 창 stale 중앙값 0/최대 12,976/>100 present 19·복귀 뒤 마지막40 0·스크롤 중 일시 stale 두 구간(UP p129~143 x0..64, DOWN p227~230 x401..665) bbox·r1/r2/m1 결정론.
3. 수용 시 work H-D2w(두 구간 writer 귀속 census/watch) 또는 가장자리 마우스 스크롤 사전등록. 기록 docs/history/laps/20261006_lap1059_work_role_boundary_handoff_hd2z_review.md.
```

# 2026-10-06 | lap1070 | G1 middle — H-S3 독립 검수 + H-S3t 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1069 work `loop/ESCALATE_SOL`(SHA256 `824d1e69bca357abdb34b3630cf1d9ef4abde178705842a8afe6aa9487f9d00c`, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1068 §3 H-S3 — 현재 후보는 save000 키 hold 스크롤에서도 hold 창 stale이 save006 수준(≤10)이다. 아니면 새 미후킹 writer가 드러난다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b4…08a8ac` 직접 재계산 MATCH(읽기만). fixture: 비합성 save000(s1·s2·d1·d2)·save006(nd1), lap1069 산출물만 읽음.

## 1. 독립 재계산(work `analyze_s3.py`·`mask_d*.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1070_middle_review/`:
`recalc_lap1070.py` `37bd72c8…191a` → `recalc_lap1070.json` `e58dff39…a119728`.
입력 SHA 접두(pair / candidate trace / stale_mask): s1 `1d590121099a`/`1d45b39aa7e4`/`501133d452a5`, s2 `c4ef1465fa04`/`151b410f4a6f`/`bc98592fc588`, d1 `c05252de75b5`/`07bc1a023419`/`26d0922d8900`, d2 `0da7e99265b1`/`4c7f5998ff1c`/`b2496b0150a5`, nd1 `7bb3283ef730`/`5af630adcb20`/`1db3c0c467ab` — pair 접두는 ESCALATE 기재와 일치, mask SHA = pair-result 기재 값(5/5). 대조: lap1065 nd1·nd2(save006 같은 옵션).

| 항목 | 사전등록(lap1068 §3) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| S3-1 이동 | 두 lane 같은 관측열·≥1칸·최종=시작·parity PASS | s1·s2·d1: 두 lane DOWN (39,53)→(63,77) **24칸**·UP →(39,53) **24칸**, 관측 25개 전부 대각 1칸·clamp_free·관측열 동일 2/2·최종 snapshot (39,53)·parity PASS. **d2: baseline DOWN 23칸**((39,53)→(62,76), 관측 24)·UP 24칸 → 최종 (38,52), candidate 24/24·(39,53) → 관측열 다름 0/2·parity HOLD(`same_camera_after_each_key` false 하나만, state/plan/input_on_target 전부 true) | 동일 | 일치. d2는 baseline(원본) lane 단독 → 후보 무관, FAIL 조건(2 run 재현) 미충족 |
| 입력 tick | 목표 tick | 4 save000 run 모두 target = observed(DOWN·UP), release tick = input+24, 실제 WM_KEYDOWN(key 40/38) 수신, lane 간 tick plan 동일 | 동일 | 일치 |
| S3-2 | hold p95 ≤ 고정+16·tps 비 ≥0.95 | s1 7/7·1.0032, s2 7/7·1.0041, d1 13/11·0.9969, d2 12/11·0.9949 | 동일 | 일치·PASS |
| S3-3 | hold 창 stale 합 ≤10 | s1 **0**(idx 124..292), s2 **117**(idx 231 단발, tick 50823, 카메라 (52,66)), d1·d2 **3**(idx 228 단발, tick 50821, 카메라 (53,67)) | 동일 | 일치. s2 초과 → 새 잔여(FAIL 아님) |
| d2 mask 위치 | — | idx 228 = **(702,0)·(703,0)·(704,0)** 3 px(800×600 logical, 화면 맨 윗줄). mask 픽셀 수 = trace `stale_pixels` 5 run 전부 일치. d1 mask는 120..183(64 상한)이라 228 미포함 | 동일 | 일치 |
| stale = primitive 경로 | — | 해당 present의 `primitive_stale_pixels_total` 증분 = stale(3·3·117, nd1 1) | 동일 | 일치(아래 정정 1) |
| 비회귀 | 안전 7종 0·cleanup·source_unchanged·마지막40 0·save006 nd 합 1 | 5 run 안전 max 0·source_unchanged true(원본 SHA)·마지막40 0, save000 run 전체 stale 합 0/117/3/3(로드 과도 포함), nd1 hold 합 **1**(idx 125 = lap1065 nd1·nd2와 같은 위치·값)·p95 7/7·비 1.0023·gate 10개 PASS·**ps3 stale 열 해시 `8052cfdb4afd` = lap1067 e1·e2와 동일** | 동일 | 일치·PASS |
| save000 pair HOLD 사유 | 기존 사유 공개 | V2/V2s/V2q BLOCKED = tag `selection/drag/minimap/production` BLOCKED(loaded PASS), input_effect HOLD = 7 check 전부 false(장면 동작 없음). 4 run 동일, d2만 parity HOLD 추가 | 동일 | 일치(이번 변경이 만든 사유 아님) |

결정론 확인: d1·d2 candidate ps3 stale 열 해시 `6581b6c6eaf7`로 같다. **새 관찰:** stale 단발은 4 save000 run 모두 **UP 입력 +10 tick**(d1·d2 50811→50821, s2 50813→50823, hold 창 시작 +106 present)에 나왔고 s1만 같은 tick(50822, idx 230)에서 0이다. 같은 tick인데 카메라는 d (53,67)·s2 (52,66)로 한 칸 다르다 → 카메라 위치보다 시간(애니메이션/유닛 동작)에 묶인 사건으로 보인다. 3/4 run 재현이라 진단으로 귀속 가능.

## 2. 코드 검토(`tools/g1_saved_scene_probe.py` `8816512f…`, `tests/test_g1_saved_scene_probe.py` `a0cda067…`, 둘 다 git 미추적)

- `_scene_option_error`: save006 아닌 fixture는 none 강제 유지, none + terrain-trace·rice·scroll-phase 거부 유지, none + `--terrain-scroll`만 새로 허용.
- loaded 캡처 뒤 중단 조건 `scene_actions == "none" and not terrain_scroll`(3516): none+scroll이면 계속 진행. 그 사이 블록은 `scroll_phase_diagnostic`·`terrain_trace`(둘 다 none과 결합 거부) 뒤 `if terrain_scroll:`(3818)뿐 → save006 전용 동작이 스크롤 전에 실행될 경로 없음.
- 스크롤 블록 끝 scroll_after 캡처 직후 `if scene_actions == "none": raise _LoadedOnlyComplete()`(4130) → selection 이하 save006 전용 동작 건너뜀, 예외는 4562에서 정상 종료로 처리.
- `--p4b-s-snapshot`은 `args.fixture != "save006"`이면 거부(5392) — lap888 reference가 save006 전용이라 타당.
- drift 표본 좌표는 `g1_layer_drift.h`상 800×600 logical(각 축 상한 검사), mask와 같은 좌표계.
- 판정: 결함 없음. 테스트 실행은 §4.

## 3. 판정과 정정

- **정정 1(귀속 범위, 비차단):** work의 "primitive 한 개의 화면 가장자리 3 px로 귀속"은 present 단위 계수 증분 일치일 뿐 **writer 귀속이 아니다.** d1·d2 drift 표본 (150,40)·(100,70)·(200,70)은 stale 위치 (702..704,0)을 덮지 않았고 s2 117 px는 위치 자체가 미수집이다. 사전등록의 "표본 귀속까지"는 미충족 → 다음 work H-S3t로 넘긴다.
- **정정 2(tick 표기, 비차단):** work 기록 표의 tick plan 50716/50752/…는 s1 값이다. run마다 loaded tick이 50595~50597로 달라 계획도 ±1씩 다르다(d1·d2 50715…, s2 50717…). 판정에는 run별 계획을 썼다.
- **H-S3 PASS(partial) 수용** — S3-0·S3-1(비진단 2/2, d2 baseline 23칸은 원본 lane 위상 경합 1건)·S3-2·비회귀 전부 충족, S3-3은 단발 새 잔여(s2 117·d 3, 시간 고정 UP+10 tick)로 기록. save000(두 번째 장면) 키 hold 스크롤의 hold 창은 save006 수리 전(93,956)과 비교해 0~117 단발 수준이다. 제품 G1 마감·사용자 승인 아님.

## 4. work H-S3t 사전등록(다음 work, Sonnet) — save000 UP+10 tick 단발 stale 귀속(·조건부 수리)

가설: save000 키 hold `DOWN,UP`의 UP 입력 +10 tick 단발 stale(3 px 윗줄 x702..704 / 117 px)은 하나의 미후킹(또는 reject된) 게임 writer가 화면 윗 가장자리에 그린 것이고, 표본을 그 위치에 두면 마지막 writer EIP로 귀속된다.

1. **T-0 위치(비진단 2 run, 순차, load ≤8):** lap1069 s 옵션 그대로(`--hd-source scale2x --fixture save000 --scene-actions none --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys DOWN,UP`)에 `--stale-mask` 를 hold 창 시작 +100..+112 present(현재 계획이면 대략 `222-238`, 64 상한 이내)로 둔다. stale present의 bbox·픽셀 목록을 기록.
2. **T-1 귀속(진단 2 run):** 위 + `--layer-drift --screen-watch --drift-samples` 3점 = d2 위치 (703,0) + T-0에서 나온 bbox 안 2점(없으면 (702,0)·(704,0)). 표본 stale present의 마지막 writer EIP·tid·함수(objdump 경계)·호출처를 기록.
3. **T-2 조건부 수리(구현 우선):** writer가 기존 미러 패턴(diff 미러·band/tile 분할·reject 해소)으로 다룰 수 있는 게임 함수면 테스트 RED→GREEN 뒤 최소 수리하고 비진단 2 run + save006 nd 1 run(lap1065 nd 옵션) + `make check`. `wined3d`/비게임 스레드이거나 2 진단 run에서 표본 stale이 0이면 수리하지 않고 귀속 결과만 기록.

PASS 기준:
- T-0: 2 run 중 ≥1에서 UP+10 tick 부근 stale 위치 확보(0이면 2 run 모두 0 기록 = 재현 빈도 갱신, FAIL 아님).
- T-1: 표본 stale present ≥1의 마지막 writer 귀속(EIP·tid). 표본 stale 0이면 UNKNOWN으로 기록하고 종료.
- T-2(수리 시): 비진단 2/2 hold 창 합 ≤10·UP+10 tick 위치 0, save006 nd hold 합 1·pair PASS·ps3 stale 열 비회귀, 안전 7종 0·cleanup·source_unchanged·마지막40 0, p95 ≤ 고정+16·tps 비 ≥0.95, S3-1 관측열 동일(원본 lane 위상 경합 단발은 기존 backlog로 공개).
- FAIL: 크래시·안전 위반·save006 비회귀 깨짐.
- 한도: 귀속 실패가 2 진단 run 연속이면 같은 추측을 반복하지 않고 단발 잔여로 닫은 뒤 다음 후보(좌우 가장자리·모서리 스크롤)로 넘긴다.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source·하네스는 lap1069 full PASS 1648과 같은 해시 `8816512f…`/`a0cda067…`; 다음 work H-S3t가 변경 시 실행).

## 다음 한 가지

work(Sonnet) H-S3t: §4 T-0 → T-1 → (조건부) T-2. 그다음 후보: 좌우 가장자리·모서리 스크롤, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: d2 baseline 23칸(원본 lane keydown 위상 경합, lap1009 s1과 같은 유형), save006 lap1056 r1 부하 동반 stale, 미후킹 `0x467E60`, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal. G6/G7은 사용자 합격(APPROVALS lap989) 대기, 루프를 막지 않는다.

## 부록: lap1069 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1069 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-S3(save000 키 hold 스크롤) 하네스 S3-0 구현·5 run 실행 완료. work는 자기 결과를 승인하지 않고, S3-3(hold 창 stale 합 ≤10) 초과가 "새 잔여"로 나왔으므로 fresh Opus middle 독립 재계산·다음 work 사전등록이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1069_work_hs3/ 의 {s1,s2,d1,d2,nd1}/pair-result.json·candidate/trace_raw.jsonl·d1·d2 candidate/stale_mask.bin 을 work 스크립트(analyze_s3.py·mask_d*.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: s1 1d590121, s2 c4ef1465, d1 c05252de, d2 0da7e992, nd1 7bb3283e.
2. 검증 항목: save000 s1·s2 두 lane DOWN→UP 24칸 왕복·clamp 없음·관측열 동일·최종=시작 (39,53); hold 창(ps3 ord 124..292) stale 합 s1=0, s2=117(ord 231 단발, tick 50823), d1=3·d2=3(둘 다 ord 228, tick 50821, 카메라 (53,67), mask 위치 x702..704·y0, stale=primitive_stale_pixels_total); d2 baseline 이동 23/24(위상 경합 backlog)로 d2 terrain_scroll_parity HOLD; p95/tps 비; 안전 7종 0·cleanup ok·source_unchanged; 마지막40 0; nd1(save006) hold 합 1·pair PASS. save000 pair HOLD는 V2/V2s/V2q BLOCKED(scene-actions none 태그 부재)·input_effect HOLD(장면 동작 없음)이며 이번 변경이 만든 사유가 아님을 확인.
3. 코드 검토: tools/g1_saved_scene_probe.py `_scene_option_error`(terrain_scroll 허용·trace/rice/scroll_phase 거부 유지)·loaded-only 중단 `scene_actions == "none" and not terrain_scroll`·스크롤 블록 뒤 `if scene_actions == "none": raise _LoadedOnlyComplete()`·`--p4b-s-snapshot` save006 전용 거부. 테스트 3곳(tests/test_g1_saved_scene_probe.py 끝 신규 1·수정 2).
4. 수용 시 다음 work 사전등록: ① ord 228 top-row 3 px / s2 117 px primitive 귀속(mask 64 상한 → `--stale-mask` 225-232 등 좁은 구간)·수리, ② 좌우 가장자리·모서리 스크롤, ③ HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택.
기록 docs/history/laps/20261006_lap1069_work_g1_hs3_save000_key_hold_scroll.md. 변경은 tools/g1_saved_scene_probe.py·tests/test_g1_saved_scene_probe.py(둘 다 git 미추적, uncommitted)뿐이며 제품 C/bridge 불변.
```

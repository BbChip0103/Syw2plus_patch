# 2026-10-06 | lap1065 | G1 H-D2t — hold 뒤 p313..315 일시 stale = 미후킹 `0x465CA0`(선택 드래그 윤곽) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 가설: lap1064 §4 — hold 뒤 p313..315(tick 24882..24884) 3-present 일시 stale은 미미러/반려 writer 하나(진단+수리 한 회차).
- 예상 PASS / FAIL: lap1064 §4 T-1 귀속 ≥90%·T-2 nd 2 run 모두 p313..315 stale ≤1% 또는 0·새 hook invocations>0·reject_target/size/guard 0·비회귀(hold 창 합 ≤10, pair PASS, 안전 7종 0, cleanup, source_unchanged, I-0/I-1, 마지막40 0, s6 마스크 300..848 0, s0 gate가 lap1056/1063과 gate별 동일). FAIL = 크래시·안전 위반·install 실패·원본 인자/반환 변경·p95>고정+16.
- 변경 파일 / source fingerprint (uncommitted, SHA256 앞 16): `tools/inmm_stub/g1_mirror2x.c` 12512b4d378cca8c · `g1_mirror2x.h` b2cd0bf9bb50d82e · `g1_overlay_blt.h` 39e6e2e1227dc70f · `direct_draw_trace.c` c213243c11c0b1e5 · `tests/test_g1_rect_fill.py` 13f813b57e0ab806 · `tests/test_g1_overlay_blt.py` 922736abb249895d.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` 직접 재계산 MATCH(objdump 읽기만, `od_465C00_lap1065.txt` `34c70ccd…`). 후보 = 새 복사본+브리지 DLL. fixture: 비합성 save006(D-2 hold nd pair·고정 카메라), save000(성능 창).

## 1. T-0 위치 (비진단, `--stale-mask 310-316`)
- 첫 run(`t0_run1_input_race`)은 candidate DOWN hold 15칸(기준 24)·최종 카메라 (149,92) → **입력 위상 경합(기존 backlog)으로 무효**, pair HOLD, 보존. 재실행 `t0`: pair PASS·24/24칸. stale = p313 **319 px** bbox (100,40)-(200,100)·p314 **719 px** (100,40)-(325,175)·p315 0(이번 run). 모양 = 위 가장자리 1행 + 좌우 2열 + 아래 행인 **1 px 사각형 윤곽, 우하 모서리가 present당 이동 = 선택 드래그 박스**(lap1063 nd1/nd2의 159/559/959·80/479/879와 같은 유형, 크기 +400/present).
## 2. T-1 귀속 (진단, `--layer-drift --screen-watch --drift-samples "150,40;100,70;200,70"`)
- 이 run은 시각이 +4 tick 밀려 stale이 p316(610 px bbox (100,40)-(231,118))·p317(1,011)·p318(18)에 나타남(진단 동반 위상 변동). **표본 stale present 3/3 마지막 writer = `0x465CA0` 내부**: (316,0) EIP `0x465DB3`(위 행 루프 `mov [edx+edi],bl`)·(316,1) `0x465E3C`(좌 열)·(316,2) `0x465E6C`(우 열), 값 66→68(drag 색). 귀속 3/3 = 100% ≥ 90%. `0x4662DE`(캐시→화면)가 다음 present에 66으로 되돌림.
- 함수 정적 분석(objdump `0x465CA0..0x465E7C`): old bytes `83 EC 10 | 53 | B8 01 00 00 00`(**5 B 경계가 명령 중간 → 9 B 도둑질**, 상대 주소 없음), `ret 0x1c`, thiscall 7 스택 인자 = x0 y0 x1 y1 + LUT 색 인덱스 3개(`[ecx+0x19A0+((a5·64+a6)·64+a7)]`), 축별 정렬 후 viewport `[ecx+0x4D0/4D4/4D8/4DC]` 겹침 검사·가장자리별 클립 플래그, 쓰기 = `[ecx+0x1514]+y·[ecx+0x10]+x` 1 px 윤곽. **쓰는 모든 픽셀은 정렬+viewport 클립 사각형 안**(0x465B30과 같은 계약).
## 3. T-2 수리 (테스트 먼저 RED→GREEN)
- `g1_overlay_blt_apply_tiled`(`g1_overlay_blt.h`): 윤곽 박스가 최대 800×600이라 기존 폭 ≤320 상한을 넘으므로, 전체 before 복사를 ≤320×160 타일로 나눠 기존 `g1_overlay_blt_apply`를 호출(halo = 실제 post frame → 전체 프레임 Scale2x 동등). 테스트 `test_overlay_blt_tiled_apply_equals_whole_frame_scale2x`(8 경우×2 모드, 경계 321열·161행·12타일·거부 7종) RED(미선언) → GREEN.
- hook `0x465CA0` `mirror_rect_border7`(G1_RECT_BORDER7, `G1_RECT_BORDER7_LEN 9u`): `G1HookState.original/patched` 8→16 B(9 B 도둑질 수용, `install_one` 일반 길이 경로 불변), `g1_rect_fill_region` 클립 사각형 before 복사(`g_rect_border7_before` 800×600)→원본 1회 호출(7 인자 그대로)→타일 diff 미러. 계수 6개(invocations/mirrored_calls/mirrored_pixels/reject_target/size/guard)·trace `rect_border7_465CA0_*`. 테스트 `test_rect_border7_hook_table_and_wrapper_contract` RED→GREEN. `make lint`·`make typecheck` PASS, mingw `-Wall -Wextra` 경고 0.
## 4. 실행 결과 (순차, 새 스크립트 `analyze_d2t.py`는 lap1063 analyze 기반 복제 + 계수·범위 확장)
공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1065_work_d2t/`(pair-result SHA 접두: t0 2079024e·t0_run1 a5a47837·t1 33e67a20·nd1 b74b0c65·nd2 4453237d·s6 24109e5b·s0 9573268d). load 시작 2.7~6.2.

| 항목 | 사전등록 | nd1 | nd2 | s6 | s0 |
|---|---|---|---|---|---|
| p313..315 stale(마스크 308..322 합) | nd 2 run ≤1%/0 (기준 1,677/1,438) | **0** | **0** | — | — |
| hold 창 stale 합(ps3 123..291) | ≤10 (기준 1) | 1 (p125 단발, lap1064과 동일) | 1 | — | — |
| `rect_border7_465CA0` invocations/mirrored | >0 | 12/12 (1,689 px) | 12/12 (1,689 px) | 14/14 (1,451 px) | 0 |
| reject_target/size/guard | 0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 |
| pair·안전 7종·cleanup·source_unchanged | PASS·0·true | PASS·0·true | PASS·0·true | PASS·0·true | HOLD(기존)·0·true |
| I-0 | 24칸×2·clamp 없음·최종 (158,101) | PASS | PASS | — | — |
| I-1 hold p95 / tps 비 | ≤고정+16 / ≥0.95 | 7(고정 6)/1.0029 | 7(고정 7)/1.0024 | p95 7 | p95 7 |
| 마지막40 | 0 | 0 | 0 | 0 | 0 |
| s6 마스크 | 300..848 0 | — | — | 300..848 **0**·초기 6..12는 lap1063 s6과 ±1 px(19,008 동일 등) | — |
| s0 gate | lap1056/1063과 gate별 동일 | — | — | — | input_effect HOLD·V2/V2s/V2q BLOCKED·나머지 PASS(lap1063 s0와 gate별 동일)·stale 창 p298..338 포함 전부 0 |

판정(work 후보): **T-1 PASS(3/3)·T-2 PASS(nd 2 run 0)·비회귀 PASS → H-D2t PASS(partial) 후보.** 스크롤 hold 일시 stale은 이제 nd에서 p125 1 px만 남는다. 한계: (1) 신규 hook 호출은 drag 장면 12~14회뿐(윤곽이 화면 가장자리·viewport 경계에 걸리는 경우·tile>1 실제 호출은 미관측, 호스트 C 테스트로만 보장); (2) 진단 run은 +4 tick 위상 이동 때문에 stale present가 p316..318로 옮겨짐(진단 동반 변동, 비진단 run과 대조 완료); (3) save000에서 이 hook 호출 0.
## 5. 검사
- 이 기록 freeze 뒤 `make check`·`checks/safety.sh check` 결과는 STATUS에만 보강한다(fingerprint가 lap 기록을 포함하므로 기록을 먼저 닫는다).
## 다음 한 가지
middle(Opus) H-D2t 독립 재계산·코드 검토(work 스크립트 미사용, 새 스크립트로 nd1/nd2/s6/s0/t0/t1 재계산; `mirror_rect_border7` 정렬·클립·before 복사 범위·타일 경계, 9 B 도둑질/restore 경로, `G1HookState` 16 B 확장 영향). 수용 시 다음 work 사전등록: 가장자리 마우스 스크롤(하네스 입력 경로 추가)·HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택. backlog: save006 lap1056 r1 부하 동반 stale, 미후킹 `0x467E60`, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal.

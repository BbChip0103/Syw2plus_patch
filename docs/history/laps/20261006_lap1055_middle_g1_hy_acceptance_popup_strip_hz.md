# 2026-10-06 | lap1055 | G1 middle — H-Y 독립 검수 → work H-Z(팝업 동반 띠 수리) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit은 0이다.
- 검수 대상: lap1053 work H-Y(진단 전용). lap1052 §다음 work 사전등록 Y-0·Y-1·Y-2와 대조했다.
- 처리한 인계: `loop/ESCALATE_SOL`(lap1054 work, 1,294 B, SHA256 `59e6b4fd491f801b9266a28f6ed056e4e9a26de37197f8bf8cbb4b7790391319`). 원문은 아래 부록에 두고, 처리한 뒤 파일을 삭제했다. 인계에 적힌 산출물 해시 앞 16자(analysis_y `7d4d934dafaf2b4d`·attr_y `fd377defc72c20dc`·lap1053 기록 `d37231ac40f351c3`)는 다시 계산해 일치한다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경은 0이다.
- 원본 SHA / 환경 / fixture: 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha256 `b56986e0…08a8ac` 직접 재확인. 6 run 모두 private EXE 앞 16자 일치·source_unchanged [true,true]. 6 run bridge 사본의 `g1_mirror2x.c`·`g1_mirror2x.h`·`direct_draw_trace.c`가 현재 source와 byte 일치(SHA 비교). fixture save006, 격리 prefix/display. `local/runtime/lap1053_hy_*` 6개 모두 `game` 사본 없음(baseline/candidate만 남음), lap1053 잔존 프로세스 0.
- 재계산: 공유 temp `20261006_lap1055_middle_review/`. work의 `analyze_y.py`·`analyze_y_attr.py`와 제품 helper는 쓰지 않았다. lap1052 middle `recalc_lap1052.py`의 파서(마스크·screen_watch·layer_drift)를 옮겨 새로 작성했다. 새로 넣은 것: layer_drift `b`(KEYSRC Blt 미러) 사각형과 블록 bbox의 교차, heal 지속 시간과 블록 길이 비교, lap1039~1053 save006·save000 run 36개의 keysrc·heal·`0x465E80` 반려 상관.
  - `recalc_lap1055.py` `4338dfcb…bb06` → `recalc_lap1055.json` `c6dd5afa…b7780d`, 출력 `recalc_lap1055.txt` `4c7052f1…c6a57478`(stderr 빈 파일).

## 재계산 결과(판정 불일치 0, 정정 2건)

| 항목 | lap1053 work 보고 | lap1055 재계산 |
|---|---|---|
| Y-0 | 6 run pair PASS·안전 0·cleanup/source_unchanged true·마지막40 0 | **같음.** 6 run pair PASS, 안전 7종 max 0, cleanup [T,T], source_unchanged [T,T], 마지막40 중앙값 0 ×6, 9 family 항등식 6/6 성립, load 1.66~3.81 |
| Y-1 재현 | s6 r3 p581..633 434 px, watch r2 p440..480 281 px, 나머지 p65~70 1 px | **같음.** s6 r1·r2 p65..67, w r1 p65..67, w r3 p66..68, s6 r3 p67..69, w r2 p68..70의 1 px 외에 블록은 두 run뿐이다 |
| Y-2 bbox | y218..226×x240..322(434), x240..291(281), 프레임 간 동일 | **같음.** s6 r3 프레임 585·620 동일, w r2 블록 안 14 프레임 동일 |
| save000 상자와 같은 좌표 | 같은 상자 | **같음.** lap1051 w r1·r2 p298..338 303 px y218..226×x240..302, s0 r1·r2 412 px y218..226×x240..323 |
| 귀속 | `0x745699CF` tid 288 wined3d, 블록 41 present | **같음.** 블록 안 표본 (250,224)·(280,221) 각 41/41 present 마지막 writer = `0x745699CF`/tid 288/mod 2. 모듈 이름은 screen_watch `e` 레코드에서 `wined3d.dll`로 직접 확인. 값 일치 52/52·54/55. 무장 113 round fail 0·좌표 일치·selftest PASS·dropped/overflow 0 |
| 상관 | 블록 run 2개만 keysrc 5·heal 44/56·`0x465E80` 반려 2/2 | **같음**, 범위를 넓혀 더 강하게 확인(아래) |

**정정 1 — 블록은 KEYSRC heal 사각형 "안의" 잔여가 아니다(공간 불일치).** watch r2의 layer_drift `b` 레코드 5개(p440..444)의 KEYSRC 확대 Blt 사각형은 (86,94,51×38)→(26,49,170×128)이다. 즉 x26..195, y49..176이다. 블록 bbox(y218..226, x240..291)와 **5/5 모두 겹치지 않는다.** H-A2 heal은 이 사각형만 다시 비교하므로 블록을 볼 수 없다. 그 대신 시간은 정확히 묶여 있다. **heal_presents = 블록 길이 + 3**(heal은 변화 없는 present 3번 뒤 멈춘다)이 6 run에서 모두 성립한다: lap1053 w r2 44 = 41 + 3, s6 r3 56 = 53 + 3, lap1051 s6 r1 56 = 53 + 3, s6 r2 45 = 42 + 3, lap1051 save000 w/s0 44 = 41 + 3, s0 r1 43 = 40 + 3. 그래서 블록은 **같은 팝업이 떠 있는 동안 wined3d가 매 present 다시 쓰는, heal 사각형 밖의 동반 띠**다(9행 높이·x240 시작·폭은 글자 길이에 따라 303/412/281/360/434 px). work 결론의 "미후킹 게임 함수 아님·팝업 경로"는 맞고, "heal 후 잔여"라는 표현만 "heal 범위 밖 동반 띠"로 바로잡는다.

**정정 2 — lap1052 정정 3의 회귀 우려를 닫는다.** H-V 이전 제품에도 같은 고정 블록이 있었다: lap1039 s6 r1 p441..481 **360 px**, lap1045 s6 r1 p441..481 **360 px**, lap1045 s6 r2 p440..480 **303 px**. lap1052는 이 run들을 "긴 증가형 꼬리"로만 요약했다. save006 run 16개 전체에서 **고정 블록 유무 ⇔ `overlay_rect_blt_keysrc_calls` > 0이 16/16 일치**한다(블록 7: lap1039 r1·lap1045 r1/r2·lap1051 r1/r2·lap1053 s6 r3·w r2, 모두 keysrc 5 또는 10. 블록 없음 9: lap1039 r2·lap1047 r1/r2·lap1049 r1/r2·lap1053 s6 r1/r2·w r1/r3, 모두 keysrc 0). H-V/H-W 제품 4 run은 팝업이 뜨지 않은 run이다. 그래서 H-X와는 관계가 없고 **H-X 수용은 다시 열지 않는다.** save000은 모든 run에서 p297/298에 같은 팝업이 뜬다(keysrc 5·`b` 사각형 4종 동일). 그래서 H-Z의 결정론적 fixture는 save000이다.

보조 관찰: 블록 run의 hook_blt 호출은 800 = 미러 5 + reject_target 795다(비블록 789~792 = 전부 reject_target). 즉 팝업 때 화면 대상 Blt는 KEYSRC 5개뿐이고 띠를 덮는 화면 대상 Blt는 없다. `0x465E80` 반려 2+2(target·size)는 팝업 run에서만 나온다. 반려 사각형 좌표는 계수만 있어서 UNKNOWN이다. TextOutA reject_target은 블록 run에서 +23~29 많지만 run 간 편차와 구분되지 않는다.

## 판정

**H-Y PASS(진단) 수용, 정정 1·2 포함.** Y-0·Y-1·Y-2와 귀속이 재계산과 일치한다. 결론을 이렇게 고친다: save006 늦은 블록과 save000 남은 stale은 **같은 팝업의 heal 사각형 밖 동반 띠(y218..226, x240..~323)** 이고, writer는 wined3d 스레드다. 부하 변형이 아니고 회귀도 아니다(H-V 이전에도 있었다). 기술 진단 수용이며 G1 마일스톤 승인이 아니다.

## 다음 work — H-Z 팝업 동반 띠 수리(구현 우선, 1 lap) 사전등록

- 가설: 팝업 동안 wined3d가 heal 사각형 밖 띠를 매 present 다시 쓴다. 후보 expected는 이 띠를 따라가지 못한다. 그래서 heal이 활성인 동안 비교 범위를 띠까지 넓히면 stale이 0이 된다.
- Z-1(진단, 같은 lap): env-gated drift 로그 두 가지를 추가한다. (a) `0x465E80` 반려 때 인자 x0,y0,x1,y1,color·사유(target/size)·buffer가 화면인지. (b) heal 활성 present마다 present 루프에서 covered이고 screen≠expected인 픽셀의 수와 bbox를 heal 사각형 안/밖으로 나눠 기록한다. 고정 좌표는 하드코딩하지 않는다.
- Z-2(수리, Z-1이 "띠 = heal 밖, heal 활성 구간과 같은 시간" 을 확인하면 같은 lap에서 구현): heal 활성 동안 heal 사각형 밖 stale bbox(Z-1 (b)로 구한 것, `G1_OVERLAY_MAX_*` 이내로 제한)를 두 번째 heal 사각형으로 같은 `g1_overlay_blt_apply`(expected = before, screen = after, 바뀐 픽셀만 미러)로 다시 비교한다. heal과 같이 시작하고 같이 끝난다. 만약 Z-1 (a)가 띠 = `0x465E80` reject_size 사각형으로 나오면, 대안은 그 사각형을 행 단위로 나눠 미러하는 것이다(한 가지만 고른다).
- 실행: save000 watch pair 2회(표본 (250,224)·(280,221)·(300,222)) + 성능 pair 2회 + save006 pair 2회. 각 실행은 launch 명령 한 번, run 직전 load 기록(1분 load > 8이면 대기), run 뒤 `game` 사본만 삭제.
- PASS 조건:
  - Z-0: 안전 7종 0, cleanup·source_unchanged true, 9 family 항등식 유지, 새 계수 항등식(heal2 호출 = 미러 + 반려).
  - Z-1: save000 p298..338 present당 stale 303/412 → **≤ 10**, 마지막40 0, 표본 2점 stale present 41 → 0.
  - Z-2: save006은 팝업이 뜬 run이 있으면 그 블록 → 0. 팝업이 뜨지 않으면 SKIP으로 적는다(실패 아님). 신규 stale 0, steady 38(+880) 신규 0.
  - Z-3: 성능 pair p95 ≤ 기준 + 1 ms, tick 비 ≥ 0.99.
  - Z-4: pair PASS(V1/V2/V2q/W-1 V2s), coverage·validator·gate 불변.
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 좌표 하드코딩.
- 그다음 후보: H-Z PASS면 G1 고정 카메라 stale 잔여가 save000·save006 모두 0이 된다 → D-2 연속 스크롤·두 번째 장면·사용자 승인 준비. backlog 미후킹 `0x467E60`(호출 `0x41A887`, 미관측).

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서 작성과 재계산(read-only)만 했다. 게임/source/commit은 0이다. SAFETY·CONTEXT 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1051 full PASS 1639 `logs/gates/lap1051-work-full-check.log`).
- 남은 위험: 띠를 wined3d가 왜 다시 쓰는지(텍스처→sysmem 동기화 범위)는 추정이다. 띠가 처음 생기는 writer(팝업 첫 present 이전의 게임 쓰기)는 표본에 잡히지 않았다. `0x465E80` 반려 좌표는 UNKNOWN이다.
- 사용자 승인 상태: 기술 진단 수용일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 루프를 막지 않는다.
- 다음 한 가지: work H-Z(위 사전등록) → middle H-Z 검수.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1054 work, 1,294 B, SHA256 `59e6b4fd491f801b9266a28f6ed056e4e9a26de37197f8bf8cbb4b7790391319`)

```
lap1054 work(Sonnet) → middle(Opus) 인계. 사유: STATUS "다음 한 가지"가 middle 독립 검수이며 work가 lap1053 결과를 승인할 수 없는 역할 경계(MODEL_ROUTING). 제품 변경·게임 실행 0, 근거 보존.

middle이 할 일(STATUS 사양 그대로):
1. lap1053 work 산출물 `temp/Syw2plus_patch/20261006_lap1053_work_hy/`의 `analysis_y.json`·`attr_y.json`·run 디렉터리(r_s6_r1..3, watch)를 work 스크립트(analyze_y*.py) 없이 새 스크립트로 재계산: 블록 구간(s6 r3 p581..633 434px, watch r2 p440..480 281px), bbox y218..226×x240..291/322, writer `wined3d.dll` tid 288 EIP `0x745699CF`, 블록 run 2개에서만 `overlay_rect_blt_keysrc_calls` 5·heal 44~56·`rect_solid_465E80_reject_target/size` 2 상관(비블록 4 run 0).
2. 판정: H-Y 수용 여부(부하 비의존·미후킹 게임 함수 아님·팝업 KEYSRC Blt heal 후 잔여).
3. 수용 시 work H-Z 사전등록: 팝업 상자 잔여(save000 303/412·save006 281~434) `0x465E80` 반려 rect 크기/대상 로깅 + `hook_blt` heal 뒤 wined3d 재기록 정합.
참고 해시(앞 16자): analysis_y.json 7d4d934dafaf2b4d · attr_y.json fd377defc72c20dc · lap1053 기록 d37231ac40f351c3. 기록 `docs/history/laps/20261006_lap1054_work_role_boundary_handoff_hy_review.md`.
```

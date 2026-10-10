# 2026-10-07 | lap1148 | G1 middle — H-SC1 독립 검수, PS20 writer 정적 귀속(`0x4B23B5`→`0x4D4620`), H-SC2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행·C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1147 work → middle 검수·A/B 결정 요청, SHA256 `49668859cba1…`, 원문 byte 일치 보존 `docs/history/laps/20261007_lap1148_preserved_lap1147_escalate_sol.txt` 뒤 삭제). INBOX 새 사용자 지시 없음(마지막 = lap1147 처리 메모), APPROVALS 새 반려·사용자 G1 시험 결과 없음(lap1136 재요청 대기), `loop/STOP` 없음.
- 목표: G1. 검수 대상(lap1146 §4 H-SC1): PS20 브리핑 stale 위치·writer 귀속 → 조건부 수리.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만, objdump 역어셈블).
- 후보 source SHA(기록 §0과 12자리 일치 11/11): `g1_stale_mask.h` `d2e017bfdcb9`·`g1_screen_watch.h` `8146afe12eaf`·`g1_screen_watch.c` `66bd2908915a`·`g1_saved_scene_probe.py` `000badc1e9f6`·테스트 3개(`68c5dde2fb75`·`e284b0fb4be1`·`be6c4989f894`), 되돌림 4개(`direct_draw_trace.c` `0de218aa84d6`·`g1_mirror2x.c` `1b056280f662`·`g1_mirror2x.h` `0fc9cc4b1edf`·`test_g1_rect_fill.py` `d8e4430db905`). run exit 6/6 = 0. full check 로그 `logs/gates/lap1147-work-full-check.log` `ee34db0b82b3` 끝부분(typecheck Success·CONTEXT_PASS) 확인.
- fixture: 없음(lap1147 raw 재사용, 새 실행 없음).

## 1. raw 독립 재계산 (새 스크립트, 공유 temp `20261007_lap1148_middle_review/`)

`recalc_lap1148.py`(`277ee9efc865`) → `recalc_lap1148.json`(`da58d8349e5a`). 산출물 SHA 14/14 기록 §5와 일치. stale mask 값 2 = stale(`G1_STALE_MASK_STALE`), 8-연결 성분. PS20 정착 = 연속 PS20 구간의 첫 present 제외.

| 항목 | 기록(lap1147) | 재계산 |
|---|---|---|
| m1 PS20 HD | min 89.43·p50 98.217·<98.6 66.6%·<90 7.3% | 89.430·98.217·66.6%·7.3%, 정착 present 4,643(기록 4,643 일치), covered 480,000 전부 |
| m1 stale 5 dump | 7,784/8,861/1,286/18,087/50,735 | 같음(헤더 = mask 계수) |
| m1 4350 초상화 3칸 | 16,132·15,949·15,577 + 글자 ≤195 | 16,134·15,949·15,579 + 글자 소성분 ≤198(8-연결 차 ±2 px, 판정 무관) → 큰 성분 합 47,662/50,735 = **93.9%** |
| on1 PS20 HD | 89.43·98.220·64.8%·6.7%, 4350 50,735 | 같음. on1 3350 = 34,486(초상화 2칸, m1 18,087과 칸 개수 시점 차), 4350 성분 3칸 m1과 동일 |
| on1 overlay | mirrored 5·48,032 px·rejects 45,902 | 같음(trace 최종 행) |
| w2/w4 호출 표 | 5행, overflow 0 | 같음. **p≥2800 PS20 hook 호출 = present BltFast(`0x49273F`, primary←뒤 버퍼) + `[0x104F824]` 대상 BltFast 4행(호출 1~3회)뿐, Blt(kind 1) 0행** |
| w4 목적지 | `[0x104F824]` 잠금 `0x03028F40` pitch 800 ≠ 감시 `0x04470030` pitch 1600 | 같음(d 행 11개) |
| w1/w2/w4 writer | `0x4662DE` tid 280 + `wined3d.dll` `0x741B99CF` tid 288 | 같음(+`0x42A091` 2회). **추가 확인:** wined3d 쓰기는 표본별 첫 hit부터 **끝까지 매 present 연속**(빈 present 0), 순서는 매 present `0x4662DE`(배경 249) → wined3d, 값은 **두 값이 교대**(표본0 118/66 약 50:50, 표본1 208/122) = 매 present 다시 칠하는 애니메이션 초상화 |

- **수치 불일치 0, 정정 0**(성분 면적 ±2 px는 연결성 정의 차). 결정성(m1=lap1145 r1) 확인.

## 2. 정적 귀속 — H-SC1 `BLOCKED`를 middle이 해소 (원본 역어셈블)

- PS20 프레임 함수 `0x4B2320`(디스패처 `0x424A80` 유일 호출, 바로 앞 `0x424A70`이 상태 0x14=20 설정): `0x4D3EF0()==1`이면 **`0x4B23AA: mov eax,[0xE5D438]` → `0x4B23B5: call 0x4D4620`(thiscall `ecx=0x61E370`, 인자 1 = 뒤 버퍼, `ret 4`)** → 렌더러 잠금 그리기(`0x464E20`·`0x404070`×3·`0x464E70`) → `GetDC([0xE5D438])`(`0x4B2438`)·GDI 3회(`0x404560`)·`ReleaseDC`(`0x4B249E`) → `0x492700` present(`0x49273C` BltFast `[0xE5D434]`←`[0xE5D438]`, flags 0x10).
- 브리핑 합성 `0x4D4620(dest)`: ① `BltFast(dest, x, y, [0x104F824], rect, 0x11 SRCCOLORKEY|WAIT)`(`0x4D4651`, 본문·글자 층) ② 초상화 4칸(`[0x104FB34+4i]`, 170×128) 각각: 확대 애니메이션이면 `0x4D3960` → `Blt(dest, rect, portrait, NULL, 0x1008000 WAIT|KEYSRC)`(`0x4D3AB9`), 아니면 `BltFast(dest, x, y, portrait, NULL, 0x11)`(`0x4D469D`) + `0x4D4320` ③ 버튼 2개 `BltFast(dest, …, [0x104F824], rect, 0x11)`(`0x4D4703`·`0x4D473A`). 호출처는 `0x4B23B5`(dest = 뒤 버퍼)와 `0x41C362`(dest = `[0x104FB2C]`, 다른 표면) 두 곳뿐.
- **결론: PS20 stale writer = 게임이 매 present `0x4D4620`으로 뒤 버퍼 `[0xE5D438]`에 하는 키 BltFast/Blt.** 뒤 버퍼(플립 체인)는 vtable이 복제되지 않아(lap1128·1130 확인 사실) hook·호출 표에 보이지 않고, Wine wined3d가 키 복사를 CS 스레드(tid 288)의 화소 루프로 실행하므로 쓰기 EIP가 `wined3d.dll` 안에 찍힌다. 매 present 연속·배경 뒤 순서·애니메이션 값 교대·초상화 상자 위치·글자 소성분(본문 층)이 모두 이 경로와 맞는다.
- **lap1147 수리 시도 반증의 이유:** `[0x104F824]`는 중간 층이고 화면 쓰기는 그다음 합성 단계(`0x4D4620`)라서, 중간 층 BltFast를 미러해도 뒤 버퍼 stale은 그대로다(반증·되돌림 판단 수용).
- 한계: 이 귀속은 정적(호출 그래프·인자·플래그)과 raw 상관으로 확정했고, 런타임 확인은 다음 work의 래퍼 호출 계수·켬/끔 대조로 한다. 렌더러 잠금 그리기와 GDI 블록(버튼 글자)은 별개 writer일 수 있다(잔여로 측정).

## 3. 결정 — A/B 대신 C(호출 지점 diff 미러), `FEASIBLE`

- (A) 명시 잔여 종결은 writer가 특정된 상태라 근거가 약하다. (B) GetDC/GDI 계측은 위 정적 귀속으로 불필요(GDI 블록은 합성 뒤 별도이고 wined3d 쓰기를 만들지 않는다).
- **(C) 채택:** 기존 호출 지점 래퍼 선례(H-RS2 `0x4C7EE6`·H-RS3 `0x4B5493`)와 화면 크기 before 버퍼 타일 diff 선례(H-TM1 `0x466480`, `g1_mirror2x.c:330-340`)를 합쳐 `0x4B23B5`를 감싼다. 재스테이징 보류 유지(H-SC2 수용 시 묶음 판단).

## 4. 다음 work 사전등록(Sonnet) — H-SC2: `0x4B23B5` 브리핑 합성 호출 지점 diff 미러 (한 work 회차)

- **SC2-0 구현(TDD, 기본 켬·끔 env `SYW2_G1_BRIEFING_COMPOSE=0`):** `0x4B23B5`의 `E8 rel32`(old bytes `e8 66 22 02 00` 확인, 대상 `0x4D4620`)를 래퍼로 바꾼다(thiscall `ecx`, 인자 1, `ret 4` 보존, 설치 실패·old bytes 불일치 시 설치 안 함·롤백). 래퍼: 인자 dest가 `[0xE5D438]`이고 상태 20일 때만 ① dest `Lock(DDLOCK_WAIT)` → 800×600 논리 영역을 before 버퍼에 복사 → `Unlock` ② 원본 `0x4D4620` 호출 ③ dest 다시 `Lock(WAIT)`(wined3d 큐 동기화) → 타일 diff로 바뀐 화소를 기존 미러 경로(H-TM1 방식)로 HD에 반영 → `Unlock`. 조건 밖·Lock 실패·pitch/형식(8bit) 불일치는 원본만 호출하고 reject 계수. 계수: calls·mirrored·changed·pixels·rejects(이유별)를 trace 최종 행에 노출. 테스트: old bytes·인자/반환 규약 상수, env 파서(기본 켬·`0` 끔), 상태·dest 게이트, 타일 diff 순수 함수.
- **SC2-1 런타임 확인(같은 회차):** 래퍼 calls ≈ PS20 present 수(±2%), PS20 밖 calls 0. (선택) `--screen-watch --screen-watch-state 20 --screen-watch-call-from 2800` 1 run에서 wined3d 쓰기가 래퍼 ②~③ 사이에 들어오는지(표본 present 동일) 확인.
- **SC2-2 측정·판정:** 켬 2 run + 끔 1 run, 명령 `--hd-source scale2x --title-button scenario --scenario-start --scenario-play --scenario-briefing-dwell 65 --stale-mask 700,1750,2650,3350,4350 --stale-mask-state 20`. 켬: PS20 정착 HD min **≥98.6**·<90 0%·p50, 초상화 3칸 stale ≈0, 끔: min 89.43 재현. PS9/PS15 100·PS3 99.686 비회귀, 안전 7종·fallback·dropped 0, present 경과 p95 켬/끔 비교(+2 ms 넘으면 공개), 캡처 열람(초상화·본문 정상, 깨짐 없음). `0x41C362` 경로(dest `[0x104FB2C]`)는 건드리지 않으므로 save006 pair 불필요.
- **판정표:** 켬 min ≥98.6 & 끔 재현 = `PASS(partial, 기술·격리)`. 개선됐으나 <98.6 = `PASS(partial)`+잔여 위치(렌더러 그리기·GDI 버튼 글자 블록 `0x4B2438..0x4B249E` 후보). calls 0 또는 개선 0 = 정적 귀속 반증 → `FAIL` 기록·되돌림·middle(같은 추측 반복 금지, 그 경우 PS20은 명시 잔여 A로 종결 권고).
- **금지·공통:** 원본/참고 쓰기·커밋·`260921_temp` 쓰기 금지. 각 run 뒤 `game` 사본 삭제·디스크 ≥20GiB(현재 78GiB). 긴 실행은 `setsid nohup`+생존 확인, 끝까지 대기. C·하네스 변경 시 lint·typecheck → 기록 freeze → `make check` 1회. **사용자 G1 시험 결과가 오면 그것이 최우선.**
- 연속 규칙: lap1147은 실행 증거가 있는 work. 이번 middle은 실행 증거 없음 1회째. 다음은 제품 코드+실행 증거를 남기는 work여야 한다.

backlog 유지: H-TM1 잔여 871, Wine 영상 재생 불가, victory-poke readback 경합, 하네스 trace 8192 상한, 하네스 lap1147 진단 옵트인(`--screen-watch-call-from`)은 유지, STATUS 목록. 새 backlog: `0x41C362` 합성 경로(dest `[0x104FB2C]`)의 상태·화질 미측정.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 이번 회차 변경은 문서·공유 temp 스크립트뿐이고 C·하네스·테스트 source는 lap1147 full PASS(1820 passed, exit 0) 때와 같다(SHA 11/11 일치).

## 다음 행동

work(Sonnet): §4 H-SC2(SC2-0 `0x4B23B5` 래퍼 구현 → SC2-1 호출 계수 → SC2-2 켬2/끔1 측정). 그 뒤 middle 검수. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.

# 2026-10-05 | lap1022 | G1 work — H-B3 후보 lane 화면 표본 A/B/C 하드웨어 쓰기 watch(진단 전용)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무 구현) 1 lap.
- 가설: 표본 A(112,126)·B(437,463)·C(302,9)의 미설명 변화(`u`: A 5·B 19·C 25)를 낸 writer는 `0x467580`/`0x467410`/`0x4676D0` 호출 창 밖(lap1020 B2-1 FAIL)이며, 화면 buffer 1바이트 쓰기 DR watch(모든 스레드)로 EIP·스레드·모듈을 직접 지목할 수 있다.
- 예상 PASS / FAIL 조건(lap1021 §4.3 사전등록 그대로): B3-0 유효(selftest hit·무장 스레드≥1·watch 주소=present source 3/3·stale 마지막40 중앙값 424.5±5%·안전 7종 0·양성 대조 B p366..410 ≥90% `0x467580` 본체 EIP·B 89 리셋 hit), B3-1 귀속(u present 직전 구간 마지막 hit `val`==`u.scr` ≥90%, hit 0이면 BLOCKED), B3-2 분류(판정 아님), B3-3 save006 env-off 비회귀(공통 38프레임 r1∩r2 24 px y515..520×x616..619·신규 0·p95≤16ms·안전 0·계수 0).
- 변경 파일(전부 uncommitted, 제품 mirror·gate·기준·validator 불변; env 없으면 hook·VEH 0):
  - 신규 `tools/inmm_stub/g1_screen_watch.c`(SHA256 `78c924ab…237d885c`)·`g1_screen_watch.h`(`4a811419…82732f95`): opt-in `SYW2_G1_SCREEN_WATCH=1`. 첫 유효 PS3 present에서 DR0..2=화면 buffer(`renderer+0x1514`)+y·stride+x(A/B/C) 1바이트 쓰기 watch를 Toolhelp32로 **프로세스 모든 스레드**에 무장(8 present마다·buffer 주소 변화 시 재무장), VEH(SINGLE_STEP)가 `{"t":"x"}` 레코드(EIP·tid·present 스레드 여부·val·v[3]·모듈 클래스/base·mirror guard·.text 복귀주소 4개·Dr6)를 `C:\inmm_g1_screen_watch.jsonl`에 기록(raw 상한 20,000줄, 이번 run 1,773/1,769·dropped 0), 사전 selftest(slot 3·비공개 바이트)·`m`(watch 주소=`lpSurface+y·pitch+x` 일치 비트)·`a`(무장 스레드 수·실패)·`k`(heartbeat 합계)·`e`((slot,EIP) 표+모듈 파일명) 레코드. 게임 buffer는 읽기만 한다.
  - `tools/inmm_stub/g1_mirror2x.c`(`46ef3979…78539588`)·`g1_mirror2x.h`(`c33252a5…3b9461cc`): `g1_mirror2x_primitive_guard()` getter, `copy_present`에서 `layer_drift_present` 직후 `g1_screen_watch_on_present(source, pitch, g_drift_present)` 호출.
  - `tools/inmm_stub/Makefile`(`cd42b565…98d47dc9`): g1_screen_watch.c/.h 추가.
  - `tools/g1_saved_scene_probe.py`(`1dd5a051…b782be2e`): `--screen-watch`(`--layer-drift` 필수, 후보 lane env만, 결과 `screen_watch.jsonl` 복사).
  - 신규 `tests/test_g1_screen_watch.py`(`9a79692b…e6ba31d1`): RED(4 failed)→GREEN(4 passed). 호스트 컴파일(DR7·주소·Dr6 슬롯·.text·모듈 클래스)+소스/하네스 계약.
- 수리 1건(③ 반복 원칙, v0 보존): v0 run의 `e` 레코드 모듈 이름 버퍼(64 B)가 `GetModuleFileNameA` 절단 시 NUL 미종결이라 JSONL 67줄이 깨졌다. 버퍼 260 B·강제 NUL·따옴표/제어문자 치환으로 수리 후 pair를 처음부터 재실행했다(v0는 `v0_s0_r1`/`v0_s0_r2`·`local/runtime/lap1022_hb3v0_*`·`logs/gates/v0/`에 보존; r2는 중단 run, 내용 부분). x 레코드·판정 수치는 v0 r1과 같았다.
- 원본 SHA / fixture: 원본 EXE `b56986e0…8ac`(모든 run `source_unchanged` true). save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명 아님.
- 실행(모두 순차, 공유 temp `20261005_lap1022_work_hb3/`, 하네스 스크립트 `run.sh`·`run_s6.sh`, 분석 `analyze_hb3.py`(`19911a66…63bea060`)·`analyze_hb3_s6.py`, 결과 `analysis_s0.json`(`6f3d7ba0…0a7a1f3d`)·`analysis_s6.json`(`0fa75d3a…7bb87abb`)):
  - save000 pair 2회: `--hd-source scale2x --fixture save000 --scene-actions none --performance-window --layer-drift --screen-watch` → `s0_r1`/`s0_r2`, exit 2/2(기존 non-loaded tag HOLD, 예상), `candidate/screen_watch.jsonl` SHA `cb2b6fa6…986b83ef`/`889bd88f…67c190b6`.
  - save006 env-off pair 2회: lap1020 `run_s6.sh`와 같은 인자 → `s6_r1`/`s6_r2`, exit 2/2(기존 pair HOLD: v2s production raw).
  - `game` 사본은 probe가 삭제(`cleanup.game_removed` true), prefix·manifest·output·로그 보존. 디스크 여유 34G→29G.

## 측정값 / 판정

### B3-0 유효 — PASS (r1/r2 동일)
| 항목 | 결과 |
|---|---|
| selftest | `armed 1·hits 1·PASS` |
| 무장 스레드 | 10개·재무장 52라운드·ok 520·**fail 0**·present 스레드 무장 1(tid 280) |
| watch 주소=present source | match 7(비트 3/3), buffer=surface `0x08AFC610`·stride/pitch 832 |
| stale 마지막40 중앙값 | **424.5**(r1=r2=lap1020 기준, 0% 편차) |
| 안전 7종·cleanup·source_unchanged | 0·true/true·true/true |
| 양성 대조 B p366..410 | `0x467580` 본체 EIP(`0x467692`) hit가 **45/45 present** |
| B 89 리셋 쓰기 hit | 268/267건(`0x4662DE` 244/243·`0x467CCF` 24/24) |
| 성능(참고) | p95 cand 11 ms(watch 오버헤드, ≤16 ms)·hit 폭주 없음 |

### B3-1 귀속 — PASS (r1/r2 동일)
미설명 변화 present마다 그 표본 슬롯의 같은 present 구간 마지막 hit `val`을 `u.scr`와 비교: **A 5/5·B 19/19·C 25/25(100%)**, hit 0 표본 없음, 값 불일치 0.

### B3-2 분류 (판정 아님; 다음 middle 결정용)
(`u` 49건의 마지막 hit 귀속)
| 대상 | 귀속 | 건수 | 비고 |
|---|---|---|---|
| C(25)·B(18) | **EXE EIP `0x00467CCF`**(복귀 `0x0041A072`, present 스레드 tid 280, guard 0) | 43 | **(a) EXE 미후킹 primitive.** `0x467CCC`의 `mov [edi+ebp],dl`(`[eax+esi+0x19a0]` LUT 값) 다음 명령. 함수 `0x467B00`(prologue `83 EC 14 33 C0 53 89 44 24 04`, `ret 0x14` @`0x467D09`, 스택 인자 5개, ecx=renderer `0xE5BF18`), 호출처 `0x41A06D`·`0x41AC45`(둘 다 `mov ecx,0xE5BF18; call 0x467B00; ret` 형태의 thin wrapper). mirror hook 대상(`G1_*`) 아님 |
| B(1)·A(1) | EXE EIP `0x004662DE`(캐시→화면 복사 `0x466280`, 이미 mirror 대상) | 2 | 램프 종료 후 배경 복귀 값 |
| A(4) | **`wined3d.dll` EIP `0x746099CF`**(base `0x74530000`, **present 스레드 밖 tid 288**, 스택 .text 복귀 0, p298..338에 41건 쓰기, 값 94·215·163·187×38) | 4 | **(b)/(d)**: Wine 내부 스레드의 화면 buffer 쓰기. 제품 수리 대상 아님(원본 lane에서의 동일 쓰기 여부는 미측정) |
- 전체 hit 분포(r1): `0x4662DE` 슬롯 A/B/C 각 411(present당 1회 캐시 복사)·`0x467CCF` C 294(p84..377)·B 159(p207..365)·`0x467692` B 46(p366..)·`0x746099CF` A 41(p298..338).
- `_inmm.dll` EIP 0건(후보 결함 아님). guard는 전 hit 0(차단 wrapper 안 쓰기 없음; `0x467580` 쓰기도 guard 0이라 이 필드는 판별력 낮음).
- 다음 후보: **H-B4 = `0x467B00` diff 미러**(H-L/H-B 패턴, 5인자 `x,y,w,h,rle`). `0x467CCF` hit 구간은 B p207..365·C p84..377이다. A의 wined3d 4건(+값 187 유지 38 present)과 `u` 밖 구간은 이 후보로 설명되지 않는다(미확인).

### B3-3 비회귀 — PASS
save006 env-off 2 run: 공통 38프레임(300..620; 880은 두 run 모두 부재 = lap1000 r1 짧은 run 변형) r1∩r2 = **24 px, y515..520×x616..619**(성분 D, 기준 동일)·lap1000 3 run 대비 신규 0·제거 0·p95 7/7 ms(max 11/13)·cov p50 99.30%·안전 7종 0·`drift_*` installed/계수 0·`screen_watch.jsonl` 미생성. 39프레임(880 포함) 교집합 0은 880 부재로 **검증 불가**(비교 가능한 38프레임 기준만 확인). gates: v2s production FAIL은 기존 raw gate(사용자 판단 큐), 나머지 PASS.

## 회귀 / 남은 위험 / 독립 검수
- 위 변경은 env 게이트 안 추가만이다. `g1_screen_watch_on_present`는 `screen_watch_on()` false면 즉시 반환하고 VEH·파일·스레드 열거를 만들지 않는다(save006 env-off에서 파일 미생성 확인). 한계: 열거는 8 present마다라 새 스레드는 최대 7 present 늦게 무장; `v` 값은 hit 시점 읽기라 다른 스레드의 동시 쓰기와 경합 가능(귀속 100%라 영향 없음); `guard` 판별력 낮음.
- 사용자 승인 상태: 기술 검수 전(2단 독립 검수 대기)이며 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 비차단 대기.
- 전체 `make check`는 이 기록 freeze 뒤 1회 실행하고 결과 수치는 STATUS에만 보강한다.

## 다음 한 가지
middle(Opus)이 `analyze_hb3.py`·제품 helper 없이 `screen_watch.jsonl`·`layer_drift.jsonl`로 B3-0/B3-1을 독립 재계산하고 `0x467B00` objdump(prologue·인자·호출처)를 확인한 뒤 H-B4(`0x467B00` diff 미러) 사전등록 또는 wined3d 4건 분리 처리를 결정한다.

# 2026-10-07 | lap1150 | G1 middle — H-SC2 독립 검수·수용, H-TR3(묶음 시험판 재스테이징) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행·C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1149 work → middle 검수, SHA256 `8be6b41c1a28…`). 원문은 byte 일치로 `docs/history/laps/20261007_lap1150_preserved_lap1149_escalate_sol.txt`에 보존한 뒤 삭제했다. INBOX 새 사용자 지시 없음(마지막 = lap1149 처리 메모). APPROVALS 새 반려·사용자 G1 시험 결과 없음(lap1136 재요청 대기). `loop/STOP` 없음.
- 목표: G1. 검수 대상(lap1148 §4 H-SC2): PS20 브리핑 합성 호출 지점 `0x4B23B5`→`0x4D4620` diff 미러.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: 없음(lap1149 raw 재사용, 새 게임 실행 없음).

## 1. 출처·바이트 확인

- source SHA 12자리(기록 §0과 6/6 일치): `g1_briefing_compose.h` `fa26be35c0b2`·`g1_mirror2x.c` `e3c6a1bcd754`·`g1_mirror2x.h` `a6eda22ba8a0`·`direct_draw_trace.c` `d3e372e276a7`·`Makefile` `de73c1045595`·`tests/test_g1_briefing_compose.py` `c19dd4548436`.
- 결과 JSON 4/4 일치(on1 `c5c426a8876f`·on2 `b33de7e90f4d`·off1 `37bdaa810d05`·d1 `8a8f183e1040`), trace 4/4 일치(on1 `4456ed0e9731`·on2 `27f20c832ec7`·off1 `d423dad385a5`·d1 `b972f55e2343`), on1 DLL `29519743c515` 일치. run exit on1·on2·off1·on_a·d1 = 0, on_b exit 파일 없음(기록대로 chain 중단, 판정 근거 아님).
- **DLL 동일성:** on1·on2·off1 DLL은 서로 PE 타임스탬프 영역(오프셋 137·138·217·218·(219)·347141·347142) 외 동일. run 사본 bridge 소스 63개는 현재 트리와 같고 `inmm_stub.c`·`Makefile`만 하네스 주입(`supply_probe_poll`·`runtime_bridge.c`) 차이(lap1134 확인과 같은 정상 주입). **현재 트리 bridge로 독립 재조립**(공유 temp `20261007_lap1150_middle_review/rebuild/_inmm.dll` `9f0404fb35e5`) = on1 DLL과 타임스탬프 7바이트 외 동일. on_a·d1은 수리 전 DLL(크기·코드 다름) — 기록대로 판정 제외.
- 원본 역어셈블: `0x4B23A0 call 0x4D3EF0; cmp eax,1; jne 0x4B23BA` → `0x4B23AA mov eax,[0xE5D438]; mov ecx,0x61E370; push eax; 0x4B23B5 call 0x4D4620`(old bytes `E8 66 22 02 00` = 래퍼 설치 기대값 `g1_mirror2x.c:5567` 일치), `0x4D4620` 끝 `ret 4`(`0x4D4744`) = 래퍼 thiscall 인자 1.
- full check 로그 `logs/gates/lap1149-work-full-check.log` SHA `1448eb920e6c` = STATUS, exit 0, `1823 passed, 5 skipped`, typecheck Success·CONTEXT_PASS 확인.
- `local/runtime/lap1149_sc2_*` 6개 모두 `game` 사본 없음(baseline·candidate만). 디스크 여유 71G.

## 2. raw 독립 재계산 (새 스크립트, work 스크립트 미사용)

공유 temp `20261007_lap1150_middle_review/`: `recalc_lap1150.py` `8fe03a045e45` → `recalc_lap1150.json` `e70fd4eec379`, `capture_blocks_lap1150.py` `568388e06d05`·`nearest_where_lap1150.py` `bfb0e7af7266` → `captures_lap1150.txt` `42cbdf56d992`. 방법: 연속 상태 구간, 정착 = 구간 첫 present 제외, 래퍼 calls는 present 간 증가분으로 귀속, 간격은 연속 PS20 present 쌍의 `ts_ms` 차, stale mask는 자체 파싱(헤더 계수와 대조).

| 항목 | 기록(lap1149) | 재계산 |
|---|---|---|
| on1 / on2 PS20 정착 present·HD min/p50·<98.6/<90·stale max | 3,621 / 3,561, 100/100, 0/0, 0 | 같음(covered 480,000 전부) |
| off1 PS20 | 4,644, 89.43 / 98.218, 67.0% / 7.1%, 50,735 | 4,644, 89.430 / 98.218, 66.97% / 7.15%, 50,735 |
| on_a / d1(거부 상태) | 89.43, <90 7.0 / 5.9% | 같음 |
| 래퍼 calls / mirrored / rejects | on1 3,318/3,318/0, on2 3,271/3,271/0, off1 4,344/0/4,344(gate) | 같음. d1 reject_surface 4,351·geometry `[1600,1200,1600,8]` |
| 첫 호출 전 PS20 present | on1 304, on2 291 | on1 304·on2 291·off1 301·d1 275, **첫 호출 뒤 호출 0인 PS20 present 0**, PS20 밖 증가 0(5 run), 증가분은 항상 0 또는 1 |
| 첫 호출 전 구간 HD | 100 | min 100(5 run) |
| stale mask 켬 | 8 dump 전부 0 | on1·on2 각 4 dump(헤더 PS20 present 700·1750·2650·3350) stale 0, 값 전부 1(covered) |
| stale mask 끔 | 7,385·8,819·1,286·18,494·50,735, 초상화 15,949·16,134·15,579 | 같음(8-연결 상위 3 = 16,134·15,949·15,579) |
| PS15 / PS9 / PS3 | 100 / 100 / 99.686(covered_min 478,491) | 같음(3 run) |
| 안전 5종·dropped | 0 | 0(5 run, summary `dropped_count` 0) |
| PS20 간격 p50/p95/p99 | 켬 18/22·23/25·27, 끔 14/17/22 | 같음(off1 첫 호출 뒤 p95 18). PS3 간격 켬·끔 모두 50/52(영향 0 확인) |

- **수치 불일치 0, 정정 0.**
- **시간 축 보강(새 확인):** 켬 run은 PS20 present가 느려 4350 dump에 못 미쳤지만, 세 run 모두 PS20 체류 65.8~65.9초로 같다. 끔 off1은 정착 stale ≥10,000을 45.0초·≥50,000을 61.2초에 처음 넘었고, 켬은 같은 65.8초 전 구간 stale 0 → dump 수 차이는 판정에 영향 없음.
- **캡처 독자 Scale2x 판별 블록 비교(새 확인):** 1600×1200 캡처를 2×2 블록 최빈값으로 논리 원본 추정 → 독자 Scale2x와 비교, 판별 블록(Scale2x ≠ nearest)만 집계. `scenario_ps20_dwell.png` 초상화 3칸: **켬 on1·on2 nearest 0/0/3(0~0.1%), 끔 off1 2,848/3,374/2,364 전부(100%)**. 전체 판별 블록 nearest 켬 1,104(1.2%) vs 끔 11,201(12.6%). 켬 잔여 1,104는 본문 글자 줄(HD y≈408..476·768..934)·제목·초상화 이름 위치 = 브리핑 GDI 글자(`0x4B2438..0x4B249E` GetDC 블록) → 기존 명시 잔여 "GDI 글자" 범주(stale 계측에는 안 잡힘, 내용·색 정상). 초기 `scenario_ps20.png`(브리핑 직후)는 켬·끔 모두 188(초상화 0)로 같다. 육안 열람: 켬·끔 모두 초상화·본문·버튼 정상, 깨짐·이음새 없음.

## 3. 사전등록 이탈 판단

1. **뒤 버퍼 geometry 1600×1200 pitch 1600:** 수용. present 게이트 `menu_shape`(1600×1200 BACKBUFFER의 왼쪽 위 800×600 = 논리 프레임)와 같은 사실이고, 래퍼는 `g1_briefing_compose_accepts`(상태 20·8bpp·pitch 800..2048·높이 600 또는 정확히 1600×1200)를 Lock 전·후 두 번 확인한 뒤 왼쪽 위 800×600만 stride = pitch로 읽는다(`g1_mirror2x.c:1719-1789`) → 경계 밖 읽기 없음. dest==뒤 버퍼·상태 20 검사는 실제로 `g1_mirror2x.c:1732-1733`에서 하고, 순수 게이트의 `dest==back_buffer` 인자는 같은 값을 넘겨 항상 참(중복, 무해).
2. **calls 91.6%(±2% 이탈):** 수용(기준 해석 정정). ±2%의 목적은 "호출 누락 검출"인데, 누락 구간은 PS20 첫 275~307 present(`0x4D3EF0()!=1`, 위 역어셈블의 `jne 0x4B23BA`)뿐이고 첫 호출 뒤 누락 0·PS20 밖 0이다. 그 구간 HD 100.
3. **비용 +4 ms(p50)·+5~6 ms(p95):** **수용, 최적화는 조건부 backlog**. 근거: 상태 20 게이트라 브리핑 화면에서만, PS3 간격 무변화(50/52), 켬에서도 초당 약 55 present·최대 간격 65/73 ms(끔 76 ms), 브리핑은 정적 화면이다. 실제 Windows Lock 비용은 미측정 → 시험판 안내문에 공개. 사용자가 브리핑 화면 느려짐을 보고하거나 실제 Windows 측정에서 문제가 보이면 그때 "변화 영역만 diff·Lock 1회" work를 연다.

**판정: H-SC2 `PASS(partial, 기술·격리)` 수용.** partial 사유: 격리 Wine·시나리오 제1장 브리핑 1종·실제 Windows 미검증·브리핑 GDI 글자 잔여(기존 범주)·비용 공개.

## 4. (d) `0x41C362` 합성 경로 — 정적 확인, 측정 보류

- `0x41C362`는 함수 `0x41C020`(유일 호출 `0x4246A5`) 안에 있다. `0x4246A5`는 `0x4245D0`(호출 `0x4233DF`)의 1회성 단계 사슬(플래그 `[0xB93E00]`→`[0xB93E04]`→`[0xB93E08]`, 각 단계 `[0x4ED818]==3`과 `[0x66976C]!=0`·`[0x8924B8]>=3` 조건)의 세 번째 단계다. 즉 **PS3(인게임) 안에서 한 번 실행**되고, 그리는 곳은 뒤 버퍼가 아닌 `[0x104FB2C]`다(같은 함수가 `0x4B3780`·`0x4A9BA0`·`0x4AA0C0`도 그 표면에 호출).
- H-SC0·SC2의 시나리오 PS3 30초(켬·끔 6 run)는 HD 99.686·stale 0이다. 이 단계가 그 구간에 실행됐는지는 UNKNOWN이지만, 실행돼 화면에 나왔다면 present stale로 보였을 것이다. **지금 측정하지 않는다**(backlog 유지, 근거 = 이 절). 역어셈블 발췌 `static_41c020_lap1150.txt` `c1b22f727af6`.

## 5. (c) 재스테이징 결정 — 지금 묶는다

lap1144 규칙("다음 가시 수리나 사용자 결과 때 묶는다")에 따라, 시나리오를 시작할 때마다 보이는 H-SC2가 들어왔으므로 이제 묶는다. lap1135판(`6cbb12ac…`) 뒤 기본 켬 가시 수리 = H-TM1(첫 실행 사용자 등록 팝업 바탕)·H-SC2(브리핑 초상화). H-SC1 진단 옵트인은 기본 꺼짐.

## 6. 다음 work 사전등록(Sonnet) — H-TR3: 묶음 시험판 재스테이징(lap1135판 대체)

lap1134 §7 H-TR2와 같은 절차를 현재 트리로 반복한다. **C·하네스·테스트 변경 금지**, 스테이징 스크립트는 공유 temp에만 둔다.

- **TR3-0 출처:** 시작 때 §1 source SHA 6개가 같은지 확인한다. 다르면 차이를 기록하고 멈춘다.
- **TR3-1 save006 full pair 1회**(사용자 시험 판정 경로, lap1135 TR2-1과 같은 플래그):
  `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1151_tr3_pair --artifact-root <공유 temp>/20261007_lap1151_work_htr3/pair --hd-source scale2x --candidate-no-present-trace --candidate-no-unit-ticks`
  PASS 조건: pair `status` PASS(V2s W-1 gate)·`scene_state_equal` true·input_effect 7/7·minimap parity PASS·V2/V2q/Scale2x/loaded gate PASS·두 lane EXE SHA `b56986e0…`·`source_unchanged` true·cleanup ok·`game_removed` true·후보 창 1600×1200 scale 2·후보 prefix에 `inmm_unit_ticks.jsonl` 없음.
- **TR3-2 DLL 동일성:** 스테이징 DLL = TR3-1 `pair/bridge/_inmm.dll` 그대로. lap1149 on1 DLL(`29519743c515`)·lap1150 재조립(`9f0404fb35e5`)과 비교해 PE 타임스탬프 영역 밖 차이 0을 확인하고 오프셋을 기록한다(이 동일성으로 브리핑 측정 lap1149 on1·on2를 스테이징 DLL에 적용한다 — 브리핑 재실행 불필요). 문자열: `INMM_STUB_NO_UNIT_TICKS` 1회, `SYW2_G1_BRIEFING_COMPOSE` 존재. lap1135판과는 크기만 기록.
- **TR3-3 스테이징**(`<공유 temp>/20261007_lap1151_work_htr3/user_test_staging/`, 정확히 4파일, 각 SHA 기록; `260921_temp` 배치·APPROVALS 수정 금지):
  - `_inmm.dll`(TR3-2), `g1_trial_direct.bat`·`g1_trial_via_dxwnd.bat`은 lap1135 스테이징에서 byte 그대로(SHA `2da323e8…`·`29a35d2e…` 확인).
  - 안내문 `G1_1600x1200_시험판_읽어주세요_20261007_lap1151.txt`: lap1135판에서 만들고 `diff`를 기록한다. 바꿀 것만: ① DLL SHA·개정 표기 ② "이 판은 2026-10-07 12:53에 전달한 lap1135판(`6cbb12ac…`)을 대체한다(그 전 00:21판 `94213374…`도 포함). 옛 판으로 본 결과가 있으면 어느 판인지 적어 알려 달라." ③ lap1135판 대비 추가 수리 2개를 쉬운 말로: 처음 실행 때(등록된 사용자 없음) 뜨는 사용자 등록 창 바탕 화질 / 시나리오 시작 전 브리핑 화면 초상화 화질. 위치·입력 동작은 바뀌지 않는다. ④ 공개: 브리핑 화면에서만 프레임 간격이 Wine 측정 약 4~6 ms 늘었다(체감·실제 Windows 미측정), 느리게 느껴지면 알려 달라. 기존 수리 4개 문구는 유지한다.
- **FAIL/BLOCKED:** TR3-1 FAIL이면 스테이징하지 않고 원인 lane·gate를 기록해 middle로(수리 금지). DLL 비타임스탬프 차이가 있으면 스테이징하지 않고 보고. 실패 가설 2회 또는 60분이면 BLOCKED.
- **공통:** C·하네스·테스트 변경이 없으면 전체 `make check` SKIP 가능(lap1149 full PASS 1823 트리 그대로), 대신 `checks/safety.sh check`·context 검사. 디스크 ≥20GiB(현재 71G), run 뒤 `game` 사본 삭제. 원본/참고 쓰기·커밋·`260921_temp` 배치 금지. **사용자 G1 시험 결과가 오면 그것이 최우선.**
- **다음 middle:** 새 스크립트로 TR3-1 pair-result 재계산·현재 트리 재조립 대조·안내문 열람 → 수용 시 APPROVALS lap1136 항목에 "lap1151판으로 대체" 메모 + 새 사용자 시험 요청, root 전달 `loop/ESCALATE_SOL`.
- 연속 규칙: lap1149는 실행 증거가 있는 work, 이번 middle은 실행 증거 없음 1회째. 다음 work는 실제 pair 실행 증거를 남긴다.

backlog 유지: H-TM1 잔여 871, Wine 영상 재생 불가, victory-poke readback 경합, 하네스 trace 8192 상한, STATUS 목록. 새/갱신 backlog: `0x41C020`(PS3 1회성, dest `[0x104FB2C]`) 측정 보류(§4), 브리핑 래퍼 비용 최적화(조건부, §3-3), 브리핑 GDI 글자 nearest 1,104 블록(기존 GDI 글자 범주), 다른 장 브리핑(확대 애니메이션 `0x4D3960` 경로) 미관측.

## 7. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 이번 회차 변경은 문서와 공유 temp 스크립트뿐이고 C·하네스·테스트 source는 lap1149 full PASS(1823 passed, exit 0) 때와 같다(SHA 6/6 일치).

## 다음 행동

work(Sonnet) H-TR3: TR3-0 출처 → TR3-1 save006 full pair → TR3-2 DLL 동일성 → TR3-3 4파일 스테이징 → middle(Opus) 독립 검수 뒤 APPROVALS·root 전달. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.

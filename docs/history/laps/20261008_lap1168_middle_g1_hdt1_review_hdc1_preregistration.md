# 2026-10-08 | lap1168 | G1 middle — H-HDT1 독립 검수 · H-HDC1(④-3 tinted 색 치환표 HD 팩) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1167 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1168_preserved_lap1167_escalate_sol.txt`(SHA256 `5930f717c3550bed…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 19 GB(게임 실행 안 함).
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ④-2 검수, ④-3 선택·사전등록.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 원본 그림 파일은 읽기만.
- 후보 source(현재 트리, uncommitted·untracked): `tools/g1_hd_convert.py` `8741404d0be4…`·`tests/test_g1_hd_convert.py` `c61857c2e2d4…`·`tests/test_g1_hd_pack.py` `b7967da9f7da…` = work 기록과 일치. lap1167 full check(로그 01:40, exit 0, 1908 passed·5 skipped) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/`·`g1_hd_convert`·`g1_hd_extract` 미사용)

공유 temp `20261008_lap1168_middle_review/`: `recalc_hdt1.py`(`2b496ee3315baa65…`)→`.json`(`cccde136ac1244fe…`), `t2_window.py`(`f97be430e01b1ed5…`)→`.json`(`0235cd3cc270dc7f…`), `grid_cause.py`(`1d5db4886bf99fe6…`)→`.json`(`d8e4ce8141d30159…`). `.ytl`은 이 스크립트가 직접 해석했다(헤더 `<ver,fw,fh,fc>`, 표 0x4C0, 기준 0xBF4, 행마다 `<skip,count,화소>`).

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| `.ytl` 색인 | 425파일·17,062프레임, 이름 16,655, `ytl_narrow` 828 | 425·17,062·이름 16,655(tail_short 407)·narrow 828·고유 7,646·`.ytl` 안 충돌 이름 307(1,142프레임) | 일치 |
| `ytl_narrow` 정의 | `0x468C30` 키 폭 = `rle_dimensions`(행 skip+count 최댓값), `0x468F00` = `width_word` | 엔진 `g1_mirror2x.c:3578`(`rle_dimensions`)·`:3615`(`0x468C30`)·`:3689`(`0x468F00` `(SHORT)width_word`) 코드와 도구 `ytl_widest` 동일 의미. narrow 프레임은 `0x468C30`에서 다른 이름 → MISS → Scale2x(안전) | 일치 |
| T-0 지형 aux0 키(lap1165 P1~P5, L1·N1 포함해도 동일) | 88키(66/22)·대응 81(92.0%)·충돌 7·미대응 0, 고유 이름 76 중 70 | 88(66/22)·대응 81 = **0.9205**·충돌 7·미대응 0, 이름 76 중 대응 70·충돌 6(`blacktile` 4·`volcano/sea1·2` 1·`volcano/diff1·grss1·hill1` 1) | 일치 → `FEASIBLE` |
| 팩 지형 파일 유효성 | `.ytl` 7,339파일 | `pack_t1`·`pack_t2` 각각 비충돌 이름 7,339/7,339 존재·크기 `4·w·h`·2×2 실루엣 = 독립 디코드 1x 마스크와 일치, 충돌 이름 기록 0 | 일치 |
| run 지형 matched hit | T1 55/55·T2 61/61·T3 55/55·T4 60/60 | 같은 값(키 = writer·w·h·digest·src), 충돌 키는 전부 MISS(T1·T3 11키/5이름, T2·T4 5키/3이름) | 일치(정정 0: work "충돌 4~6"은 src 없는 키 기준) |
| trace 카운터 | hits 152/154/150/148·misses 35/22/22/22·rejects 0 | 같은 값, `identity_invalid_sources` 0 | 일치 |
| PS3 p95·HD·안전 | 6/15.4/7/7·C1 6, HD min 100, 안전·fallback 0 | 전체 PS3 present 1,535/1,513/1,534/1,541/1,530: p95 6/15.4/7/7/6·HD min 100 전부·안전 7종·fallback 0 | 일치 |
| `lookup_blocks` | T1 29.95M·T2 30.89M·T3 32.03M·T4 31.14M, lap1165 P3~P5 최대 = P5 29.64M | 같은 값. lap1165 P1 30,830,650·P2 30,615,208·P3 28,482,774·P4 29,551,552·P5 29,635,959 | 일치 |
| 지형 draws | T3 `0x468C30` 493·`0x468F00` 430 | 같은 값 | 일치 |

**T2 p95 FAIL = 환경 부하 판정 검토(`t2_window`):** 앞 1,000 present over9 0, 뒤 513 중 195. 뒤 구간의 present당 작업량은 빠른 run들의 같은 구간과 같다(팩 hit 0.012·miss 0.002·`lookup_blocks` 10,156·primitive 호출 156 vs T1/T3/T4 151~178). 그런데 호출당 시간이 늘었고(mirror 재호출 0.33→2.31 ms/present) **게임 자체 프레임 간격도 49.9→59.4 ms/present로 늘었다**(`game_tick`·`ts_ms`). 작업량 차이 없이 프로세스 전체가 느려진 것이라 팩 원인이 아니다 → **환경 부하 판정 수용**. 외부 부하의 직접 증거는 work의 `uptime` 진술뿐이다(공개). 같은 팩 재실행 T3 PASS.

**격자선 원인(`grid_cause`):** `pack_t1`(투명 경계 그대로)과 `pack_t2`(가장자리 복제)의 지형 64×48 프레임 7,002개를 실루엣 가장자리에서의 거리별로 비교했다. 차이는 **가장자리 3 HD 화소 안에만** 있고(거리 1: 87.7%, 2: 62.1%, 3: 16.4%, 4 이상: **0**), 거리 1 평균 밝기 T1 101.1 vs T2 74.0(안쪽 74~78)이다. 투명 키 색 254 = RGB(252,224,252)(밝기 235.6)가 바이큐빅으로 가장자리에 번진 것이다. 거리 2는 T1이 더 어둡다(65.6, 링잉). → T1 마름모 격자선 = stand-in 팩 제작 산물, 엔진 문제 아님. **work 결론 수용.**

**크롭 직접 열람(5장):** `ground_C1_top_T1_bottom` T1 아래쪽에 밝은 마름모 격자선 선명(C1은 다른 장면). `same_map_ground`·`same_map_ground_patch_edge`·`same_map_bottom_edge`(C1 위·T4 아래)는 녹색 풀·흙 경계·바위 질감 위치가 위아래 같은 자리이고 T4는 격자선·이음매 없이 약간 부드럽다. `bottom_edge` 왼쪽 아래 HUD 장식이 위아래 다른 것은 패널 팩(lap1165 j) 차이이며 지형과 무관. work 서술과 같다.

**코드 검토(`ytl_stream_offsets`·`ytl_widest`·`pack_dir` `.ytl` 분기·테스트 3개):** 스트림 시작 = 0xBF4 + 표[i](표 `fc`개), 크기 = 헤더, 충돌 규칙 `.spr`와 같음, `ytl_widest`가 끝을 넘으면 None(→ narrow 집계, 이름 부여는 계속). 결함 없음. 공개 1: `.ytl` 행 수를 헤더 `fh`로 가정한다(엔진 `0x468C30`은 `rows` 인자를 받음 — lap1165·1167 run의 지형 키는 모두 h=48이라 일치).

## 2. 판정

**H-HDT1 `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0. 정정 1·공개 3:
1. (정정, lap1166 사전등록 오류) §4 "`hd_pack_lookup_blocks` > lap1165 P3~P5 최대(30.8M)"의 숫자는 P1 값이었다. 의도한 기준(P3~P5 최대 29,635,959)으로 T1~T4 모두 초과. 다만 lap1165 run 사이에도 28.5M~30.8M로 흔들려 판별력이 없으므로, 앞으로 지형·tinted 기여 기준은 키 로그 writer별 matched hit로 쓴다.
2. (공개) T2 부하 판정의 외부 증거는 `uptime` 진술뿐, trace는 작업량 동일·전체 감속만 보인다.
3. (공개) 테마: 관측 이름은 volcano와 여러 테마 공통 타일뿐, normal 전용 장면 미관측(backlog 유지).
4. (공개) 화질 평가 아님(바이큐빅 stand-in). **팩 제작 규칙 확정: 업스케일 전에 1x 실루엣 밖 화소를 가장 가까운 불투명 색으로 채운다(가장자리 복제).** 실제 업스케일러 결과에도 같은 규칙을 적용한다.

## 3. ④-3 선택 근거 (이번 회차)

- **식별자(`tinted_t30.json` `eded8811e071c1d2…`, 도구 색인으로 선별):** lap1167 run 5개의 tinted 키(`0x466540`·`0x466EA0`, aux = 256 B 표) 117~146개 중 이름 대응 **96~98%**(미대응 3키/2이름·충돌 0~2), 대응 draws 95%, 원본 = `fnt`(나무 등) 77~91·`char` 25~64. lap1166 스캔(tinted 155키 = `.spr` 프레임 시작 155/155)과 부합 → `FEASIBLE`.
- **writer 의미(원본 역어셈블, 읽기 전용):** `0x466EA0` 안쪽 루프 `0x466F8C..0x466FD3` = `al=src[i]; if al==0xFE → 투명 런 건너뜀; else dst = lut[al]`(`0x466FC5 mov al,[eax+ecx]`·`0x466FC8 mov [esi+edx],al`), 목적지 읽기 없음, `ret 0x18`. 즉 출력 = `lut[원본 인덱스]`, 실루엣 = 원본 `.spr` 실루엣. HD도 `lut[팩 인덱스]`로 만들면 원본 의미와 같다. `0x466540`(클립판)도 같은 `cmp al,0xFE`·`mov al,[eax+ecx]` 형태가 보이나 전체 확인은 work H-0 몫. `lut[x] == 0xFE`도 그대로 써진다(원본도 씀).
- **작업량:** C 변경 = `build_hd_frame`의 aux 분기 하나(지금은 aux 있으면 무조건 `skip_aux`). LUT 바이트는 키에 포인터·FNV 다이제스트(`g1_mirror2x.c:2900 auxiliary_digest`, 256 B)로 이미 있다.
- **화면 비중:** draws 기준 tinted 56%(lap1166), 나무·유닛 계열.

## 4. 다음 work 사전등록(Sonnet) — H-HDC1: ④-3 tinted 색 치환표 HD 팩

**가설.** tinted writer `0x466540`·`0x466EA0`의 출력은 `lut[원본 인덱스]`이고 source 포인터는 원본 `.spr` 프레임 시작이므로, 로더가 aux 키에서도 같은 `(digest, w, h)` 팩 프레임(원본 인덱스)을 읽어 실루엣을 검증한 뒤 불투명 화소마다 `lut[]`를 적용하면 원본 색 치환(팀색·나무 변형)을 유지한 HD가 나온다.

**변경(최소).**
- H-0(정적, 기록만): `0x466540` 전체 루프가 `0x466EA0`와 같은 `dst = lut[src]`·목적지 읽기 없음인지 확인. 다르면 그 writer는 이번 범위에서 빼고 기록.
- C `g1_hd_asset.c build_hd_frame`: `key->auxiliary != 0`이고 **writer ∈ {`0x466540`, `0x466EA0`}일 때만** 팩 조회. HIT 조건 = 기존 `read_pack_frame`(크기·실루엣) + LUT 256 B를 `key->auxiliary` 포인터에서 읽을 수 있고 그 FNV-1a가 `key->auxiliary_digest`와 같음. 통과하면 불투명 화소에 `hd[i] = lut[hd[i]]`. LUT 불가·다이제스트 불일치면 새 상태(예 `lut_reject`)로 기록하고 Scale2x. 다른 aux writer(`0x468CC0`·`0x4690A0` 음영, `0x468E10` checker)는 지금처럼 `skip_aux`.
- 끔 스위치: env `SYW2_G1_HD_PACK_TINTED=0`이면 이전 동작(`skip_aux`) — 같은 빌드 대조 lane용. 팩 env가 없으면 아무것도 바뀌지 않는다(기본 켬 사용자 판 동작 불변).
- trace/키 로그: `hd_pack_lut_hits`·`hd_pack_lut_rejects`·`hd_pack_lut_key_color`(HIT 프레임에서 `lut[]` 결과가 0xFE인 불투명 HD 화소 수) 카운터, 키 로그 result에 `lut_hit`/`lut_reject` 구분.
- 테스트(RED→GREEN): 호스트 로더 테스트 — LUT 적용 결과 byte, 투명 화소 불변, 다이제스트 불일치 → Scale2x, 허용 목록 밖 aux writer → `skip_aux`, 끔 env → `skip_aux`.
- 팩: lap1167 `pack_t2` + 관측 tinted `.spr` 프레임을 B형 절차(1x 팔레트 RGB → **가장자리 복제** → 바이큐빅 2배 → `convert` → `pack`)로 추가. 도구 변경이 필요하면 최소로(`pack`은 `fnt`·`char` 이미 포함).

**측정식.**
- C-0(오프라인): lap1167 run 키 로그의 tinted 키 → 새 팩 `digest_index` 대응률(≥80% `FEASIBLE`, <50% `BLOCKED(식별자)` 종료). 비충돌 tinted 이름 팩 프레임 실루엣 유효 전수.
- C-1 적용: NG5(`--new-game-path --new-game-start --new-game-act --hd-source scale2x`) 켬 2 run + 같은 팩·끔 env 대조 1 run. 합격 = 켬 두 run 모두 크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator 바깥 diff 0·`hd_pack_rejects` 0·`lut_rejects` 0(0이 아니면 키·원인 기록 후 별도 판정)·PS3 HD min ≥ 99.9·p95 ≤ 9 ms(부하 의심 시 같은 명령 재실행 허용, 실패 run 보존·작업량 대조 공개)·**tinted matched 키 hit ≥ 90%(writer별)**·A/B matched hit ≥ 0.90·지형 matched hit 100% 유지. 대조 lane은 tinted `skip_aux` 그대로(끔 스위치 입증).
- C-2 의미 확인: 켬 run에서 LUT가 항등이 아닌 HIT 키 ≥ 1개(팀색·변형이 실제로 적용됨), `lut_key_color` 값 기록(0이 아니면 HD 합성이 0xFE를 투명 키로 쓰는지 코드로 확인하고 결과 기록 — Scale2x 경로도 같은 identity를 쓰므로 기존 동작과 비교).
- C-3 열람: 켬 vs 대조 PS3 크롭(나무 군락·유닛 팀색·건물) 공유 temp 저장. 팀색이 원래 색(치환 전 팔레트)으로 나오면 FAIL. 실루엣 테두리 밝은 띠가 보이면 기록.
- 메모리: run 끝 키 수·HD 캐시 바이트(`identity_cache_bytes` 또는 같은 의미 지표) 기록(tinted는 LUT별 키라 늘어남).
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- **비목표:** 음영 지형(④-4, `0x468CC0`·`0x4690A0`)·checker `0x468E10`·유닛 `0x466B50`·효과, 기본 켬·사용자 전달, 화질 평가, 팩 저장소 반입.
- **중단:** 실패 가설 2회 또는 60분. 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdc1/`. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ④-4 음영 지형(aux = 화소별 음영, 렌더러 팔레트 체인). backlog: normal 테마 장면, `ytl_narrow` 828 프레임(0x468C30 폭 키), 충돌 이름 처리, writer 허용 목록 일반화, lap1166 backlog 유지.

## 5. 검사

- SAFETY·CONTEXT·focused 결과는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1167 full PASS(1908 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDC1(§4). 사용자 G1 시험 결과가 오면 최우선이다.

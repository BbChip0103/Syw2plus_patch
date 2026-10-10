# 2026-10-07 | lap1162 | G1 middle — H-DEF1 독립 검수 · H-HDP1(③ HUD 패널 1장 시범) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1161 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261007_lap1162_preserved_lap1161_escalate_sol.txt`(SHA256 `bd7968fd2d8dff66…`), 보존 뒤 삭제. `loop/STOP` 없음, APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 목표: G1 — INBOX 2026-10-07 19:3x "함께 처리"(기본 켬 저장소 반영·진단 기본 끔) 검수, 다음 ③ 사전등록.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 사용자 판 `260921_temp/R5_G1_1600x1200_20261007/` 3파일(`9fe0e9f3…`·`bfddd8d8…`·`_G1MM.dll` `05bf7010…`) 읽기만, SHA MATCH.
- 후보 source: `tools/inmm_stub/inmm_stub.c` `2560b4af…`·`Makefile` `81d3598c…`·`tests/test_g1_default_on.py` `cb5a7719…` = lap1161 기록과 일치. `tests/test_g1_mirror2x.py` `56f351ff…`. lap1161 full check `.exit` 0(1890 passed) 뒤 바뀐 tools·tests·patches·checks·Makefile 파일 0(`find -newer`).

## 1. 독립 재계산 (work `pecmp.py`·`d3_run.py` 미사용)

공유 temp `20261007_lap1162_middle_review/`: `recalc_d1_d2.py`(`f106b4a1…`) → `recalc_d1_d2.json`(`37d12847…`), `recalc_d4.py`(`43d8cec4…`) → `recalc_d4.json`(`caccce90…`). PE 비교는 COFF TimeDateStamp·옵션 헤더 CheckSum·export 디렉터리 TimeDateStamp 위치를 섹션 표로 직접 찾아 차이 바이트를 필드별로 분류했다.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| D-1 텍스트 | 패치 블록 = 저장소 블록, 치환 소스 = 스냅샷 | `default_on.patch` + 줄 = 저장소 DllMain 블록 = 스냅샷 블록 **byte 동일**, 스냅샷에서 블록 제거→저장소 블록 삽입 = 스냅샷 **동일** | 일치 |
| D-1 빌드 | `--image-base=0x6b640000` 고정 시 7 B 차 | 같은 소스를 **베이스 고정 없이 출력 이름 `_G1MM.dll`**로 빌드(`83f4f1c1…`) → `05bf7010…`과 **7 B**: COFF 시각 2·CheckSum 3·export 시각 2, 설명 안 되는 차이 **0**, 베이스 둘 다 `0x6b640000`. 같은 소스를 `_inmm.dll` 이름으로 빌드하면 베이스 `0x6fd00000`·12,939 B 차 | 일치(정정 1) |
| D-2 | 플래그 없는 빌드 전/후 5 B | 현재 트리에서 `#ifdef SYW2_G1_DEFAULT_ON` 구간 3개(33줄)만 걷어낸 사본 vs 현재 트리, 플래그 없는 `_inmm.dll` **3 B**(시각 1·CheckSum 1·export 시각 1, 나머지 0). 걷어낸 사본과 HEAD 차이 8줄 = lap1103 `INMM_STUB_NO_UNIT_TICKS` 편집(H-DEF1 이전) | 일치(바이트 수는 빌드 시각에 따라 다름) |
| D-3 DLL 재현 | `2bad42a0…` | 현재 트리 `-DSYW2_G1_DEFAULT_ON` `_G1MM.dll` 재빌드(`b47ce285…`) vs `2bad42a0…` **6 B**(시각·CheckSum·export 시각만) | 일치 |
| D-3 끔/켬 | 끔 0줄·켬 801줄 | raw `inmm_sfx_log.jsonl` 직접 집계: **끔 0줄**, **켬 801줄 = `sfx_table_probe` 1 + `sfx_dispatch` trigger `probe` 800(서로 다른 unit_type 200 × 4)**. 두 run 모두 PASS·창 1600×1200·`install_failed` []·PS3 30.2초·`env_g1_set` false(= env 없이 기본 켬) | 일치 |
| D-4 | PS3 present 2,622·HD min 100 | trace sha = result 기록 일치, **전체 run PS3 present 2,977**(창 구간 닫힌 구간 합 2,631, work 2,622는 harness 창 records 합 — 정의 차이), HD min/p50 **100.0**·98.6 미만 0·stale 0·안전 7종 0·fallback 0·hresult 0·dropped 0·p95 6 ms, 선택·생산(쌀 5000→4200)·드래그·이동 effect true, scale2x validator PASS 3,953 | 일치 |
| D-4 대조 레인 | 기본 켬과 양립 불가로 FAIL | 대조 레인 trace에 `mirror2x_install` 1·`mirror2x_present` 9 → **G1 env 없는 원본 HQ EXE에서도 기본 켬 DLL이 G1을 켠다는 직접 증거**(FAIL 사유와 같은 사실) | 일치·해석 보강 |
| 테스트 | focused 6 | `tests/test_g1_default_on.py`+`test_g1_mirror2x.py` **51 passed/0.94s**(`logs/gates/lap1162-middle-focused.log` `45ae024d…`) | PASS |

**판정 영향 불일치 0. 정정 2:**
1. "이미지 베이스 미고정 시 ld 임의 베이스"는 부정확하다. ld 자동 베이스는 **출력 파일 이름으로 결정**된다(`_G1MM.dll` → `0x6b640000`, `_inmm.dll` → `0x6fd00000`). 저장소 `make default-on`은 `_G1MM.dll`로 출력하므로 베이스 고정 없이 사용자 판과 같은 베이스가 나온다 → **Makefile에 베이스 고정 불필요(질문 (3) 종결)**.
2. "`local/runtime/20261007_21…` 16K는 prefix 보존"은 틀렸다. D-3 두 run 디렉터리에는 `manifest.json`·`output`만 남았고 wrapper 결과도 `prefix_removed: true`다 — `tools/g1_r5_combo_probe.py::_cleanup`(사용자 별도 세션 작성, 수정 없이 사용)이 prefix를 `rmtree`한다. 원본·로그·결과는 보존돼 판정 영향 없음. PROMPT 런타임 provenance 규칙과 어긋나므로 **이 탐침을 루프가 다시 쓰기 전에 prefix 보존 옵션을 work가 추가**한다(backlog). D-4(`lap1161_d4`)는 prefix 보존 확인.

## 2. 코드 검토

- DllMain 블록·`sfx_probe_opted_in`·워커 게이트·Makefile `default-on`: 결함 없음. 게이트는 같은 플래그 안에서만 컴파일되고 D-2가 플래그 없는 빌드의 코드 불변을 바이트로 보였다.
- 공개(낮음, backlog): DllMain 블록은 `GetEnvironmentVariableA == 0` 뒤 `GetLastError()`로 "정의 안 됨"을 판단하는데, 빈 값으로 정의된 변수는 실패가 아니라 last error가 갱신되지 않는다. 직전 반복의 `ERROR_ENVVAR_NOT_FOUND`가 남아 있으면 빈 값 override가 기본값으로 덮일 수 있다. 사용자 경로(Windows `set X=`는 변수 삭제)에는 영향이 없고 사용자 판과 byte 동일성이 D-1 조건이라 이번에는 고치지 않는다. 고치려면 호출 전 `SetLastError(0)`.
- 공개(전달 판 차이): 사용자 판 `05bf7010…`은 하네스 bridge 스냅샷이라 `runtime_bridge.c`(보급 진단, `SYW2_SUPPLY_PROBE=1`이고 호출자 `0x42334C`일 때만 동작)를 포함한다. 저장소 `make default-on`은 이것을 넣지 않는다(문자열 `SYW2_SUPPLY_PROBE` 부재 확인). 앞으로 저장소에서 다시 빌드한 `_G1MM.dll`은 진단 하나가 더 빠진 판이며 05bf7010과 크기가 다르다(450,958 vs 457,524 B). 기능 영향 없음.

## 3. 판정

**H-DEF1 `PASS(partial, 기술)` 수용.** D-1·D-2·D-3 PASS, D-4 후보 레인 PASS(대조 레인 한계 수용: 대조 레인이 1600×1200이 된 것 자체가 기본 켬 동작 증거다. env를 명시하는 기존 하네스 경로는 플래그 없는 빌드를 쓰므로 영향 없음). 질문 (3)은 정정 1로 종결. INBOX 19:3x "함께 처리" 두 항목 처리 완료(사용자 전달·재빌드 판 배치는 사용자/root 몫, 이번 범위 아님). G1 사용자 합격·마감 아님.

## 4. 다음 work 사전등록(Sonnet) — H-HDP1: ③ HUD 패널 1장 시범(기존 `SYW2_G1_HD_PACK` 경로)

**배경.** 엔진 패널 경로(lap917)는 `SYW2_G1_HD_PACK` 디렉터리에서 키 `w<writer>_s<원본 포인터>_h<원본 앞 128 B digest>_831x<h>.idx8`(831×h×4 B, 2배 인덱스)를 읽고, `g1_panel_hd_pack_valid`(0xFE 투명 2×2 일치)를 통과하면 Scale2x 대신 쓴다. lap1161 D-4 NG5 인게임 PS3에서 관측된 키는 `w004663e0_s07bdc5f8_ha3216fad_831x163.idx8`(loaded 0) = `pannelk`(831×163). lap917은 키의 원본 포인터가 실행 형태마다 달라진다고 기록했다(`0x08743b48`/`0x08b93b48`). team-safe 초안은 엔진 Scale2x와 거의 같아서(pannelk 차 27 화소) 화면 차이로 적용을 증명할 수 없다.

**변경: 없음(C·하네스 변경 0).** 시범은 기존 경로로 한다. 하네스 `g1_saved_scene_probe.py`는 실행 env를 `dict(os.environ)`에서 만들므로 `SYW2_G1_HD_PACK=<Z:\…팩 디렉터리>`를 바깥 env로 넘긴다(대조 레인은 G1 없음이라 무관). 측정 스크립트만 공유 temp에 둔다.

**입력(고정).**
- A = lap1159 `20261007_lap1159_work_hdx2/panel_idx8/pannelk.idx8`(`19dda853…`, team-safe, 541,812 B).
- B = 업스케일러형: `pannelk` 1배(lap1159 `panel_run/fnt/pannelk.spr/0000.png` 인덱스 PNG → 팔레트 RGB)를 PIL 바이큐빅 2배 → `tools/g1_hd_convert.py convert` → `panel-idx8`. 사용자 실제 경로(업스케일 RGB → 변환)를 대표하고 Scale2x와 눈에 띄게 다르다.
- 장면: lap1161 D-4와 같은 NG5(`--new-game-path --new-game-start --new-game-act --hd-source scale2x`), 플래그 없는 저장소 빌드(하네스 기본).

**측정식.**
- P-0(오프라인): A·B 엔진 검사기 유효 1·도구 `check` 통과. `pannelk.src`(`667ba147…`) 앞 128 B로 `g1_panel_source_digest`를 호스트 컴파일해 계산한 값 = 관측 키 `a3216fad`인지 기록(다르면 키 digest 입력이 .src와 다른 것이므로 런타임 키만 쓰고 UNKNOWN 공개).
- P-1 적재: 팩 디렉터리에 관측 키 이름으로 A(또는 B)를 두고 실행 → 후보 trace `panel_hd_pack_loaded=1`·`panel_asset_key` = 파일 이름·`panel_key_subpixels_emitted` 0·패널 lock/pointer/pitch/foreign 0·안전 7종 0·fallback 0·크래시 0·PS3 HD min ≥ 99.9·p95가 lap1161 D-4(6 ms) 대비 +3 ms 이하. 키가 어긋나 loaded 0이면 그 run이 기록한 키로 다시 두고 재실행(최대 2회 추가). 그래도 매 run 포인터가 바뀌면 **BLOCKED(키 설계)**로 끝내고 C는 고치지 않는다(④ 안정 식별자 몫).
- P-2 화면 전달(B): 같은 NG5 장면 B 적용 run과 팩 없는 run의 PS3 캡처(같은 이름 `ps3_start`/`ps3_act`)에서 패널 영역(하단 831×163 → 화면 접힘 800 기준, 좌표는 trace·캡처로 확정해 기록)을 잘라 비교. 합격 = (a) 패널 영역 변경 화소 ≥ 10,000(HD 화소), (b) B 팩 인덱스 ≠ 엔진 Scale2x 인덱스인 화소 중, 팩 없는 캡처가 Scale2x 기대색과 같은 화소(= 다른 writer가 덮지 않은 곳)에서 B 캡처가 팩 인덱스 색과 같은 비율 ≥ 95%. 색 대응은 먼저 `imjin2.pal ×4`로 시도하고, 팩 없는 캡처에서 Scale2x 기대 인덱스→실제 RGB 대응이 99% 미만이면 그 캡처에서 유도한 대응표를 쓰고 공개.
- P-3(A): A 적용 run 패널 영역 변경 화소 수를 기록(기대 ≈ 27×4 + 장면 변동, 기준 아님).
- P-4 포인터: 모든 run(팩 없음 포함 ≥ 3)의 `s` 포인터·`h` digest 기록 → ④ 안정 식별자 근거.
- 열람: 패널 영역 크롭 PNG(팩 없음/A/B)를 공유 temp에 저장(middle이 직접 본다).
- 원본 보호: 원본 EXE SHA 전후 불변, game 사본 실행 뒤 삭제, prefix·manifest·output 보존.
- **비목표:** C/로더 변경(④), 기본 켬 DLL·R5 EXE·사용자 전달, 업스케일 화질 평가(사용자 업스케일러 결과가 오면 별도), 팩 파일 저장소 반입.
- **중단:** 실패 가설 2회 또는 60분. 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdp1/`. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회(측정 스크립트를 저장소에 넣지 않으면 SKIP 가능, 근거 기록) → ESCALATE_SOL(middle 검수).
- **그다음:** P-4가 포인터 변동을 보이면 ④ 일반 로더 사전등록 때 키를 (파일, 프레임) 안정 식별자로 바꾸는 것을 첫 항목으로 둔다. backlog: lap1160 중복 RGB 쌍 큰 쪽(182·183·54·203) 엔진 특수 의미 정적 확인(④ 전), `g1_r5_combo_probe.py` prefix 보존 옵션.

## 5. 검사

- SAFETY·CONTEXT 결과는 STATUS 검증 줄에 보강한다. focused 51 passed(§1).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. C·하네스·도구·테스트 source는 lap1161 full PASS(1890 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDP1(§4). 사용자 G1 시험 결과가 오면 최우선이다.

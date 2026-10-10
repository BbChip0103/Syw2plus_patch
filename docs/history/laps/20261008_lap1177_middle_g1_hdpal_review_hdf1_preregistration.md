# 2026-10-08 | lap1177 | G1 middle — H-HDPAL 독립 검수 · H-HDF1(PS5·PS7 전체 화면 그림 팩) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1176 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1177_preserved_lap1176_escalate_sol.txt`(SHA256 `2892338de396000a…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 94 GB.
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ⑤ 안의 결함 수리(H-HDPAL) 검수. DESIGN 마일스톤 경계 아님.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(`orig_sha_before.txt`). 원본 `.pal`·EXE는 읽기만.
- 후보 source(uncommitted) SHA256 앞 16자 = work 기록과 일치(`g1_hd_asset.c` `2253b963bcbfec56`·`.h` `467c7a9f721bf91d`·`direct_draw_trace.c` `eb760613a213ab08`·`g1_hd_pack.h` `fb13d7fb…`·`g1_mirror2x.c` `33e7328a…`·`g1_hd_convert.py` `5f912710…`·`test_g1_hd_convert.py` `d084e99a…`, `test_g1_hd_pack.py`는 `ca0d56d3263c5026` — work 기록 `…502b`는 마지막 글자 전사 오류). lap1176 full check 로그(exit 0, CONTEXT_PASS) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/`·`metrics_*.json` 미사용)

공유 temp `20261008_lap1177_middle_review/`: `recalc_pal.py`(`3d4f3f94…`)·`pal_files.py`(`163c477c…`)·`fade_threshold.py`(`5d9ffb2c…`)·`recalc_keys.py`(`545abff4…`)→`recalc_keys.json`(`c2886362…`)·`recalc_trace.py`(`3afa6ce4…`)→`recalc_trace_ng5.json`(`e63697bc…`, H1·G1)·`recalc_trace.json`(`7bbf0468…`, F0·F1·F2), 원본 EXE 직접 objdump `orig_lap1177.asm`(lap1175 `orig.asm` 미사용).

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| 키 로그 `pal_change` id(P0b·P0c·G1·H1·F1) | PS9 `296963d9`·PS7 `84428eed`·PS5 `e24d0e6d`·PS3 `b0f3b229`→`abeda7a5`→`156a9281`, 규칙 뒤 `cecc4681` | rgb 768 B FNV-1a 직접 = 같은 값, start×4 FNV = `cecc4681`(= `imjin2.pal`×4), in-game 3종 밝은 항목 0·평균 밝기비 0.925/0.895/0.913 | 일치 |
| 타이틀 계열 밝은 항목 수 | "217~229" | 런타임 rgb·원본 `.pal` 모두 title 170·protocol 159·lobby 177 | **정정 1**(값 틀림, 모두 >8이라 판정 영향 0) |
| 원본 `.pal` 37개 분류 | night1~4·00~10 ≥18, 11 = 0 | 같음(night 87~210·00~10 96→18·11 0), `titlestaff1_plus` = imjin2 동일 | 일치 |
| H1 PS9/PS7/PS5/PS3 present·HD min·p95 | 67·164·755·1,541 / 100·99.709·98.949·100 / 7(PS3) | 같은 값, 안전 7종·fallback·dropped 0, 상태별 trace `hd_pal_digest/family` = `296963d9/0`·`84428eed/0`·`e24d0e6d/0`·`cecc4681/1` 단일값 | 일치 |
| PS9 fullscreen | 67/67, rejects 0, loads 1 | 67/1/0/0 = menu 호출 67 | 일치 |
| 버튼 2×2 평균 차 | 0.380 | H1·G1 0.380(>16 0.0058) | 일치 |
| PS5·PS7 캡처 차 | 0.376·0.368 | H1 0.375·0.368, G1 0.376·0.368 | 일치 |
| 키 결과 | hit 132·lut_hit 194·shade_hit 148, reject 2 | 이 값은 **G1**; H1은 128·193·149·reject 2 | **정정 2**(행 귀속, 영향 0) |
| 타이틀 계열 키 중 imjin2 팩 이름 보유 | 24(5·10·9) → miss | 24(5·10·9), 비계열 pal 키 hit 0 | 일치 |
| in-game 키 중 팩에 이름 있는데 hit 없음 | 0 | H1·G1·F1·F2 모두 0 | 일치 |
| save006 F0/F1/F2 PS3 | 99.287 / 98.439(15<99, 2<98.6) / 99.287, pair PASS | 같은 값, pair 3/3 PASS, F1 stale 창 present 804..822(최대 4,211) 1개, F0·F2 창 0 | 일치 |
| F1 stale 창 안 팩 카운터 | "hits/misses/keys 불변" | 창 시작(804) 전후 불변이나 808에 hits +1·keys +1 | **정정 3**(사소, 창이 팩 이벤트보다 먼저 시작·F2 같은 설정 재현 0 → 일시 stale 판정 유지) |
| H1 실행 DLL | "`tools/inmm_stub/_inmm.dll` 8d0549c2" | run DLL = 하네스 bridge 빌드 `d51eddb4…`(공유 source 전부 트리와 byte 동일, `inmm_stub.c`만 bridge 2줄 주입) — 하네스 정상 동작. G1 bridge는 `g_pal_logged` 중복 억제만 다름 | 공개(표현 부정확, 영향 0) |

## 2. HP-S 독립 확인 (원본 역어셈블)

- 팔레트 객체 = renderer `+0x1508`(참조 7곳 전부 열거). `SetEntries`(vtable `+0x18`) 호출: `0x465889`(`0x465840` 안, 버퍼 `+0x15A0`)와 **범용 래퍼 `0x465820`(호출자 버퍼)**. 래퍼 호출처 3곳 `0x492786`·`0x4934DD`·`0x49362D`는 모두 `ecx=0xE5BF18`(renderer)·버퍼 `0xE5D4B8` = `0xE5BF18+0x15A0`. `CreatePalette`(`0x465777`)도 `+0x15A0`. → **화면 팔레트 소스 = `+0x15A0` 단일 확정**(work 결론 강화: 다른 버퍼로 화면 팔레트를 바꾸는 경로 없음).
- `0x492740` = 6비트 팔레트를 `+0x15A0`(×4)·기준 사본 `0xEC9EB8`에 적재. `0x493403`/`0x493580` 루프 = 기준 사본에서 백분율(`0x51EB851F` = ÷100)로 값을 계산해 `+0x15A0`에 쓰고 래퍼로 SetEntries — 런타임 어두운 imjin2(`b0f3b229` 등)의 출처. `+0x15A0`을 읽는 다른 곳 `0x4642A5`는 스크린샷 파일 저장(읽기).
- `night1~4.pal`(`0x493080`)은 화면 팔레트가 아니라 표 `0xB643CC..0xB64CCC`로 적재된다(직접 화면 적용 경로 없음).

## 3. 규칙(≤8 밝은 항목) 안전성 판정

1. **페이드 오분류 위험 0(원본 팔레트 전체):** 게임 페이드 공식(6비트 `v − v·f/100`)을 원본 `.pal` 37개에 적용하면 imjin2 계열이 아닌 팔레트는 **완전 검정(0%)에서만** 계열로 분류된다(`fade_threshold.py`; 정수 내림 때문에 값 1 이상 항목이 끝까지 남아 imjin2 0 채널보다 밝음). 검정에서는 어떤 인덱스도 검정이라 가시 영향 없음. night1~4는 83~90% 밝기부터 계열(= imjin2 의미 유사, 표준편차 ≤0.09)이다.
2. **실패 방향:** 계열이 아닌 팔레트는 정확 pal8 디렉터리 → 없으면 Scale2x(HD 손실이지 변색 아님). 밝게 하는 효과(섬광, `0x493580`이 100% 초과 배율이면)는 HD 꺼짐 쪽.
3. **남은 위험(공개, 비차단):** (a) 여러 스테이지·낮밤 장시간·섬광 실측 없음 → in-game HD가 꺼지는 구간 가능(안전 쪽). (b) 비계열 팔레트가 페이드되면 단계마다 pal id가 달라 키·fullscreen miss 슬롯을 새로 쓴다(키 한도 4096, 이번 run 키 389·변화 4회라 영향 0). (c) 시작 직후 PS40 무렵 로고 키 `6ab9f5ec`가 시작 팔레트(`b0f3b229`, 계열)에서 imjin2 팩 hit — 그 시점 mirror present 0(상태 3·5·7·9만 present)이고 PS9는 매 present 전체 복사로 덮으므로 가시 영향 없음.
4. **코드 검토:** 팔레트 id는 키 동일성에 포함(`find_key_for_request(..., pal)`)·fullscreen 캐시/miss 슬롯도 `(hash, pal)` — 팔레트가 바뀌면 다른 키라 낡은 HD 프레임 재사용 경로 없음. 결함 없음.

## 4. 크롭 직접 열람

`H1_buttons_base_top_cand_bottom.png`(위 baseline 2배 nearest·아래 후보): 버튼 8개 테두리·바탕·글자 변색·잡음 없음(lap1174 G1 빨강·노랑 잡음 해소). `H1_ps7_base_left_cand_right.png`: 배경·패널·버튼 색 동일, 변색 없음.

## 5. 판정

**H-HDPAL `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0. 정정 3(밝은 항목 수·키 결과 행 귀속·F1 창 카운터)·공개 4: ① 사전등록 "PS3 pal = imjin2" 불일치를 소스 교체 1회(사전등록 허용 범위)로 처리한 것을 수용(어두운 imjin2는 같은 인덱스 의미 → imjin2 팩이 맞음, §2 원본 근거), ② §3-3 남은 위험, ③ `pack_cf` 평면 구조는 더 이상 읽히지 않음(`<pal8>` 이전 필수), ④ 화질 평가 아님(바이큐빅 stand-in)·기본 켬·전달 아님.

## 6. 다음 work 사전등록(Sonnet) — H-HDF1: PS5·PS7 전체 화면 그림 팩(각 화면 팔레트)

**가설.** PS5 대기실(`titlelobby.spr`, hash 269350933 = `0x100DF815`)·PS7 접속 방식(`titleprotocol.spr`, 3908910012 = `0xE8FD3BBC`) 배경도 PS9처럼 매 present `0x466280` 800×600 블록 복사이므로(lap1174: partial 0, miss = present 수), 도구 `fullscreen --pal`로 `e24d0e6d/f100df815_800x600.idx8`·`84428eed/fe8fd3bbc_800x600.idx8`를 만들면 **C 변경 0**으로 두 화면 배경이 팩으로 바뀌고 변색은 없다(H-HDPAL 팔레트 디렉터리의 비-title 실전 검증).

**단계.**
- F-0(오프라인): 원본 `yfnt/titlelobby.spr`·`titleprotocol.spr` raw 헤더·전 바이트 FNV가 위 hash와 일치 확인. 팩 2×2 평균 vs 1x: 자기 팔레트 기준 ≤ 2.5(title 1.91), 다른 팔레트 기준이 그보다 커야 함(팔레트 올바름 확인). 0xFE 0.
- F-1(run): 합본 팩 = lap1176 `pack_pal` 하드링크 + 새 두 파일. NG5 1 run(`--new-game-path --new-game-start --new-game-act`). 대조는 lap1176 H1(같은 하네스·두 파일 없음).
- 파일만 만들 수 없거나(크기·키 색 reject) 두 화면 복사가 전체 화면 복사가 아니면 그 사실을 기록하고 `BLOCKED`/`FAIL`(C 수리는 다음 middle 판단).

**측정식(합격).**
- PS5·PS7 fullscreen hits = 각 상태 menu 호출 수, rejects 0, loads ≤ 2(화면당 1); PS9 67/67 수준 유지·버튼 차 0.38±0.05.
- PS5·PS7 캡처 vs baseline 2×2 평균 차 ≤ 3.0·>16 비율 ≤ 5%(PS9 stand-in upper 2.51/0.030 수준), 크롭 열람 변색·잡음 없음.
- PS5·PS7 p95 ≤ H1 + 2 ms(14.0·14.85), HD min ≥ H1(98.949·99.709) − 0.1. PS3 HD min ≥ 99.9·안전 7종·fallback·dropped 0·matched hit 비율 H1 수준(±2%p). `hd_pack_pal_misses`는 두 디렉터리만큼 줄어야 함(H1 30).
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 5 GB 미만이면 run 시작 금지.
- **비목표:** C 변경, 브리핑·결과·로딩 등 다른 전체 화면, ⑥ 유닛, 기본 켬·사용자 전달, 화질 평가.
- **중단:** 실패 가설 2회 또는 60분. run 대기는 PID `kill -0`·`.exit` 파일(INBOX 12:47 규칙, `pgrep -f` 자기 일치 금지). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdf1/`. 끝나면 lap 기록 → (source 변경 0이면 make check 생략 사유 기록, 변경 있으면 `make lint`·`typecheck` → `make check` 1회) → ESCALATE_SOL(middle 검수).
- **그다음:** H-HDS1r(음영 LUT refresh 결함, 기본 켬·전달 전 필수) → ⑥ 유닛 경로. backlog 유지: 로더 miss 슬롯 8·reject 영구 기억, tinted 클립 판정, 여러 스테이지·낮밤 팔레트 실측(§3-3a), lap1172 backlog.

## 7. 검사

- focused `tests/test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py` **115 passed/6.02s**(로그 `logs/gates/lap1177-middle-focused.log` `96db0e861260f2f6…`). `checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1176 full PASS(1944 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDF1(§6). 사용자 G1 시험 결과가 오면 최우선.

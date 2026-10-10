# 2026-10-07 | lap1160 | G1 middle — H-HDX2 독립 검수 · H-DEF1("함께 처리": 기본 켬 저장소 반영·진단 기본 끔) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1159 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261007_lap1160_preserved_lap1159_escalate_sol.txt`(SHA256 `e10c5163411bc1e8…`), 보존 뒤 삭제. `loop/STOP` 없음, APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 목표: G1 — HD 그림 경로 ②(검사·변환 도구) 검수, 다음 work 사전등록(INBOX 2026-10-07 19:3x 사용자 지시).
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 게임 폴더 listing digest 재계산 전·후 `46b3e298390202ba…` = lap1157·1159 값(내 Y-4 실행 뒤에도 불변).
- 후보 source: `tools/g1_hd_convert.py` `13216ab6…`·`tests/test_g1_hd_convert.py` `9a9b9deb…`·`tools/g1_hd_extract.py` `358c482a…`·`tests/test_g1_hd_extract.py` `d686e215…` = lap1159 기록과 일치. lap1159 full check(`.exit` 0, 1884 passed·5 skipped, CONTEXT_PASS) 뒤 바뀐 tools·tests·patches·checks·Makefile 파일 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/*.py`·도구 import 없음)

공유 temp `20261007_lap1160_middle_review/`: `recalc_lap1160.py`(`0c61c7ab…`) → `recalc_lap1160.json`(`ace88225…`), `y456_lap1160.py`(`09f1082e…`) → `y456_lap1160.json`(`f0e7eef5…`), 엔진 검사기 호출 `y5_valid_lap1160.c`(`e832d650…`). 내 검사기는 팔레트(`imjin2.pal ×4`)·실루엣·팀 발자국·tRNS를 새로 구현했고, 도구는 Y-4/Y-6에서 CLI로만 실행했다.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| Y-0 초상화 | 27/27 마스크 = `idx≠254`, 불투명 254 0 | 원본 BMP 27장을 새 8비트 BMP 파서로 직접 읽어 비교: 마스크 = `src≠254`·1배 불투명 값 = BMP 값·투명 = 254·2배 실루엣 = 마스크 2×2·tRNS 정상 **27/27** | 일치 |
| Y-0 회귀 | 초상화 밖 PNG 113,634 sha 회귀 0 | lap1157 `sums1.txt` 대비 초상화 밖 PNG **113,634 sha 차 0**, 디렉터리 manifest 포함 114,304 파일 sha 차 0(루트 manifest.json만 비교 제외) | 일치 |
| Y-1 원본 Scale2x 초안 | 12,191 프레임·위반 195,235(누출 142,430·누락 52,805)·실루엣 0 | **12,191 프레임·누출 142,430·누락 52,805·실루엣 0**. 분포: char 12,002/20,598·tile 101/17,181·BattleSpr 72/99·portrait 16/27 | 일치 |
| Y-1 team-safe 초안 | 37,905 프레임 위반 0 | `hd_safe` 37,905 파일 = **내 정의로 새로 만든 team-safe 초안과 37,905/37,905 화소 동일**, 크기·팔레트·tRNS 37,905/37,905, 실루엣·누출·누락 0. 원본 초안 대비 바뀐 화소 348,815(불투명 207,365,684의 0.17%) | 일치 |
| Y-2 왕복 | 37,905/37,905 byte 동일, 동률 1,439,532 | `rgb_safe` 불투명 화소 = 팔레트(hd_safe) 불일치 0, `y2_out` = `hd_safe` **파일 byte 동일 37,905/37,905**. 불투명 207,365,684·동률 화소 **1,439,532**(중복 RGB 4쌍 16/182·32/183·51/54·202/203 재확인). 새 수치: 동률을 "가장 작은 인덱스"로만 풀면 **1,106,472 화소가 달라진다** → 왕복은 동률 규칙에 의존(설계대로) | 일치(의존도 공개) |
| Y-3 | 단위 테스트 | focused `tests/test_g1_hd_convert.py`+`test_g1_hd_extract.py` **37 passed/0.75s**(`logs/gates/lap1160-middle-focused.log` `dc75ed22…`) | PASS |
| Y-4 견고성 | 217 프레임 ±8 잡음·σ1 흐림 위반 0 | **work와 다른 입력·변형**: 시드 1160, char 80·tile 50·BattleSpr 50·portrait 27 = 207 프레임 × (±12 잡음 + 실루엣 밖 무작위 색 / 1배 RGB의 PIL 바이큐빅 2배 = 실제 업스케일러형 / 자체 가우시안 σ1.5) → 도구 `convert` 207/207 변환·오류 0 → 내 검사기 **위반 0/0/0**(크기·팔레트·tRNS·실루엣·누출·누락). 공개(기준 아님): team-safe 초안 일치율 평균 0.655/0.512/0.323, 최저 0.264/0.022/0.0 | 일치 |
| Y-4 크기 거부 | (테스트) | 1줄 짧은 RGB → `convert` exit 1·오류 1·변환 0(리사이즈 없음) | PASS |
| Y-5 패널 | 3장 831×h×4·엔진 유효 3/3·본문 = team-safe | 크기 541,812/475,332/531,840 = 831×h×4, 본문 = **내 team-safe 초안 byte 동일 3/3**(pannelk 팀 수정 27 화소), 엔진 `g1_panel_hd_pack_valid`(호스트 gcc `-std=c11 -Wall -Werror`) **유효 1 3/3, 키 상태 1 subpixel 뒤집은 음성 대조 0 3/3** | 일치 |
| Y-6 결정성 | 트리·리포트 sha 동일 | 내 잡음 입력 두 번 `convert` → 트리 sha `1557aaac…` 동일, 리포트 JSON 동일 | 일치 |
| 원본 보호 | 전후 불변 | 위 listing digest·EXE SHA | 일치 |

**불일치 0.** 정정 1(판정 영향 없음): lap1158 §4 Y-4 "portrait 각 ≥30"은 실현 불가 — 렌더 범위 초상화는 27 프레임뿐이며 work·재계산 모두 27 전부를 썼다(내 사전등록 문구 오류).

## 2. 코드 검토 (`tools/g1_hd_convert.py`)

- `check`: 크기 불일치면 화소 검사 생략·RGB는 `needs_convert`, tRNS 짧은 배열 처리(누락 항목 = 불투명) PNG 의미와 맞음, 불투명 254는 실루엣 검사로 포괄. 결함 없음.
- `convert`: 후보 제한(발자국 안 236~239 / 실루엣 안 나머지 = 236~239·254 제외 / 밖 254 강제), 크기 오류 = 리사이즈 없음, 출력이 저장소·게임·입력 안이면 거부. 결함 없음.
- 공개(④ backlog): 업스케일러 출력처럼 초안 인덱스가 동률 집합 밖이면 가장 작은 인덱스(16·32·51·202)가 선택된다. 중복 쌍의 큰 쪽(182·183·54·203)이 엔진에서 특수 의미(팔레트 순환·음영 표 등)를 갖는지는 UNKNOWN → ④ 일반 로더 전에 정적 확인한다.

## 3. 판정

### 3.1 이탈(Y-1 초안 정의) → **team-safe 초안을 사양 의도로 수용한다.**
- 근거: 팀색 236~239는 런타임에 플레이어별 색으로 재적용되는 인덱스다(사양 "팀색 재적용", ④ 순서). 원본 Scale2x는 팀 인덱스를 이웃 블록으로 퍼뜨리고(누출 → HD에서 원본에 없던 플레이어색 테두리) 팀 블록 일부를 이웃 값으로 덮는다(누락 → 일부만 재색). 즉 Scale2x 초안은 ⑤ 규칙이 막으려는 결함 그 자체이며, 규칙을 완화하지 않고 초안을 고친 work 선택이 맞다.
- 비용: 바뀐 화소 348,815(0.17%)는 팀 발자국 안·팀값 누출 위치만이고, 그 자리는 Scale2x 보간 대신 원본 2×2 확대가 된다. 업스케일러 경로에서는 초안이 동률 판정에만 쓰이므로 화질 영향은 동률 화소에 한정된다.
- 사전등록 Y-1 문구("`_2x.png` 초안 전부 위반 0")는 내 lap1158 가정 오류(Scale2x가 발자국을 보존한다는 가정)였다. `_2x.png`와 Scale2x 커널(엔진 byte 동일)은 불변이라 lap1158 X-4 근거는 유지된다.

### 3.2 **H-HDX2 `PASS(partial, 기술)` 수용.** Y-0~Y-6·원본 보호 PASS(Y-1은 §3.1 정의). 업스케일러 실제 실행·엔진 적용은 미측정, G1 사용자 합격·마감 아님.

## 4. 다음 work 사전등록(Sonnet) — H-DEF1: "함께 처리"(기본 켬 저장소 반영·사용자용 빌드 진단 기본 끔)

**배경.** 사용자 별도 세션이 만든 R5+G1 판(`260921_temp/R5_G1_1600x1200_20261007/`, `_G1MM.dll` `05bf7010…`)은 `SYW2_G1_DEFAULT_ON` 빌드 플래그 diff(공유 temp `20261007_g1r5_combo/default_on.patch`)가 **저장소에 없다**(INBOX 19:2x, `grep` 0건). 또 DllMain이 조건 없이 `sfx_hook_install()`을 하고 상태 감시 스레드가 PS3 진입 때 `sfx_probe_live_units()`를 1회 부른다. 이 함수는 "읽기 전용"이 아니다(`tools/inmm_stub/sfx_hook.c:168~235`): SFX 표가 비면 엔진 표 로더 `0x445110`을 직접 호출하고, 옛 유닛 주소 `0x8990C8`(exists)·`0x66B790`(배열)에서 읽은 유닛 형식으로 엔진 SFX resolver(`0x445930`, 후킹 진입)를 유닛당 4회 + 형식 0..199 × 4회 호출한다. G2 이식 EXE는 유닛 풀을 `.g2bss`로 옮겼으므로 R5+G1 판에서는 옛 주소 값이 실제 유닛과 무관하다.

**변경(최소).**
1. `tools/inmm_stub/inmm_stub.c`에 `default_on.patch` 블록을 그대로 반영(`#ifdef SYW2_G1_DEFAULT_ON`, 비어 있을 때만 env 4개 설정). 빌드 경로: `tools/inmm_stub/Makefile`에 기본 켬 대상(예: `EXTRA_CFLAGS=-DSYW2_G1_DEFAULT_ON` 또는 별도 target)과 산출 이름 규칙. 기본(플래그 없음) 빌드는 바뀌지 않아야 한다.
2. 진단 기본 끔: 기본 켬 빌드에서 `sfx_probe_live_units()` 호출(필요하면 `sfx_hook_install()`도)을 opt-in env(예: `INMM_STUB_SFX_PROBE=1`)일 때만 수행. 기본 켬 빌드가 C:\ 로그 등 다른 무조건 진단을 켜는지 census하고, **엔진 함수를 호출하거나 옛 G2 재배치 주소를 읽는 것**만 끈다(로그 파일 쓰기만 하는 것은 목록 공개, 변경은 선택).
3. 테스트(RED→GREEN): 소스 문자열/빌드 테스트로 ① 블록 존재·env 이름·값·"비어 있을 때만" 조건 ② 기본 켬 빌드에서 probe 게이트 ③ 플래그 없는 빌드에 게이트·블록 영향 없음.

**측정식(전부 PASS여야 PASS).**
- D-1 반영 충실도: lap1151 소스 스냅샷(`20261007_lap1151_work_htr3/pair/bridge/` 또는 `20261007_g1r5_combo/build_src/`)에 **저장소 반영본의 1번 블록만** 적용해 기본 켬으로 빌드 → `_G1MM.dll` `05bf7010…`과 PE 타임스탬프·체크섬(및 설명 가능한 모듈 이름 필드) 외 동일. 다르면 차이 위치를 설명하고 FAIL.
- D-2 기본 빌드 불변: 현재 트리 플래그 없는 빌드를 변경 전·후 비교 → 타임스탬프·체크섬 외 동일(2번 게이트가 플래그 밖이면 그 차이만 허용하고 objdump로 설명).
- D-3 진단 끔 실측(격리, 원본/`260921_temp` 읽기 전용 복사): 현재 트리 기본 켬 DLL + R5 일반 G1 EXE 사본(`…R5_G1.exe` `9fe0e9f3…`)으로 `tools/g1_r5_combo_probe.py` 1회 → 창 1600×1200·훅 설치 실패 0·PS3+30초 생존·SFX 로그에 `sfx_table_probe`/probe 호출 0. 같은 조합에 opt-in env 1회 → probe 이벤트 재출현(게이트가 실제로 그 경로를 막는다는 대조).
- D-4 비회귀: 현재 트리 기본 켬 DLL + 원본 HQ2002 EXE로 save006 짧은 run(또는 NG5 1 run) PS3 HD·안전 0·크래시 0. env를 명시한 기존 하네스 경로(plain 빌드)는 바뀌지 않으므로 full pair 불필요.
- 원본 보호: 원본 EXE SHA·R5 EXE 원본(`260921_temp`) SHA 전후 불변, game 사본 실행 뒤 삭제.
- **비목표:** HD 패널 적용(③), 사용자 전달·`260921_temp` 쓰기(사용자 “R5 EXE + G1 묶음판 작업은 내가 따로 할게” 18:48 — 재빌드 판 전달은 사용자/root 몫), 새 시험판 스테이징.
- **중단:** 실패 가설 2회 또는 60분. 커밋·원본/참고 쓰기 금지. 산출물은 공유 temp `<날짜>_lap<N>_work_hdef1/`(디스크 여유 48G). 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ③ HUD 패널 1장 시범(엔진 `SYW2_G1_HD_PACK`, 키 파일명은 로그로 확정, 입력 = 이번 Y-5 `pannelk` team-safe `.idx8` 또는 사용자 업스케일 결과).

## 5. 검사

- SAFETY·CONTEXT 결과는 STATUS 검증 줄에 보강한다. focused 37 passed(§1).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. C·하네스·도구·테스트 source는 lap1159 full PASS(1884 passed) 그대로다.

## 다음 행동

work(Sonnet) H-DEF1(§4). 사용자 G1 시험 결과가 오면 최우선이다.

# 2026-10-07 | lap1158 | G1 middle — H-HDX1 독립 검수 · H-HDX2(검사·변환 도구) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1157 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261007_lap1158_preserved_lap1157_escalate_sol.txt`(SHA256 `3c79f211908797c0…`), 보존 뒤 삭제. `loop/STOP` 없음, APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 목표: G1 — HD 그림 경로 ①(원본 추출 도구) 검수, ② 사전등록(INBOX 2026-10-07 19:3x 사용자 지시).
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 게임 폴더 listing digest(경로·크기·mtime_ns) 재계산 `46b3e298390202ba…` = run1 manifest 전후 값 → lap1157 실행 뒤에도 원본 폴더 불변.
- 후보 source: `tools/g1_hd_extract.py` `e9a17df2cc22b1f5…`·`tests/test_g1_hd_extract.py` `47b1bce119fe3a44…` = lap1157 기록과 일치. lap1157 full check 로그(`73362b318bfa…`, `.exit` 0, CONTEXT_PASS) 뒤 바뀐 source 파일 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/*.py`·도구 import 없음)

공유 temp `20261007_lap1158_middle_review/`: C 디코더·재인코더 `recalc_lap1158.c`(`0208a449…`) → `census.tsv`(`7f809cde…`), 프레임 dump `dump_lap1158.c`, 검증 `verify_run1_lap1158.py`(`1ff7ea54…`) → `verify_run1_lap1158.json`(`525d9e5b…`). 형식 설명(헤더·오프셋표·스캔라인)만 보고 새로 작성했다.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| census `.spr`·`.ytl` 3,342 | rle 2,763·raw 152·ytl 425·unsupported 2(`temp.spr` 0 B·`fnt/imjin2plus.spr` fc=0) | 같음 | 일치 |
| RLE 전 프레임 정확 소비 | 2,762/2,763 파일 | **2,762/2,763 파일·117,908/117,909 프레임**, 예외 = `Online/Object/SItem001.Spr` 프레임 0(64×32·fc 1·시트 1920×160) | 일치 |
| X-3 왕복 | 표본 391 파일 16,014 프레임 byte 동일 | **전수: 정확 소비 117,908 프레임 전부 byte 동일**(런은 줄 끝·255에서 끊김), 정확 소비인데 왕복 불일치 0 | 일치(범위 확장) |
| `.ytl` | 425/425 전 프레임 정확 소비, fc=450 5개 | **425/425·17,062 프레임 정확 소비, 마지막 프레임 끝 = 파일 끝 425/425**, fc=450 = `tile/{bright,dark,normal,snow,volcano}/grss1.ypr.ytl` | 일치 |
| raw `.spr` | 152, 오프셋표 연속 151·불일치 1 | 152, 연속 151, 불일치 `Online/VillageBack/bank_button2.spr`, 전부 `fc×fw×fh ≤` 픽셀 길이 | 일치 |
| X-4 run1 | 37,905 프레임 위반 0 | 697 파일·**37,905 프레임 전부**: 1배 = 독립 디코드(투명 254·리터럴 254→240), 마스크 = 독립 투명 위치, 2배 = **엔진 `g1_scale2x_core.h`를 ctypes로 직접 호출한 출력과 byte 동일**; 모드 P/1·팔레트 imjin2×4·tRNS 254·불투명 254·누락·여분 파일 위반 0 | 일치 |
| BMP | 27/27 팔레트 = imjin2×4 | 27/27 | 일치 |
| 리터럴 254 | 초상화 27장 4,588~6,745/장 | 같은 범위, 합계 156,460 = 전부 초상화 | 일치 |
| X-5 | run1·run2 114,413 sha 동일 | `sums1`=`sums2`, 현재 run1 114,413 파일 `sha256sum -c` 전부 OK | 일치 |
| focused | — | `tests/test_g1_hd_extract.py` **20 passed/0.52s**(`logs/gates/lap1158-middle-focused.log` `d9ece5d9…`) | PASS |

**불일치 0.** 정정 2(판정 영향 없음):
1. lap1157 §5 "무압축 152개 중 렌더 범위(`BattleSpr`)는 11개" → 렌더 범위 raw 11 = `BattleSpr` 4 + `tile` 7.
2. lap1156 §7(내 이전 middle) "리터럴 `FE 00`이 있는 RLE `.spr`은 Online 2개" → 정확 디코드 기준 RLE `.spr`의 리터럴 254 불투명 화소는 **0개**(헤더 census의 단순 바이트 탐색 오류로 판단). 리터럴 254는 초상화 BMP에만 있다.

## 2. 판정

- **X-2 FAIL(기준 문구)은 그대로 기록하고, 원인 = RE 참조 파서의 시트 격자 모델 결함으로 수용한다.** 근거: 프레임별 독립 스트림 모델이 다른 언어의 독립 구현에서 117,908 프레임을 정확히 소비하고 전수 byte 왕복한다. 시트 격자 모델로는 오프셋표가 가리키는 각 스트림이 정확히 `fw×fh`에서 끝나는 구조를 설명할 수 없다. 사전등록 §7 가정 정정 4건(RLE 프레임 스트림·raw 연속 블록·ytl 레코드·BMP 팔레트)을 수용한다.
- **H-HDX1 `PASS(partial, 기술)` 수용.** X-1·X-3·X-4·X-5·X-6·원본 보호 PASS, X-2는 참조 결함으로 닫음. G1 사용자 합격·마감 아님.

## 3. 결정 2건

### 3.1 초상화 리터럴 254 → **투명(엔진 색 키)으로 바꾼다. 240 치환은 철회한다.**
- 원본 정적 근거(`exe_disasm.txt`, lap914 디스어셈블): 초상화 표면 4개 `[0x104FB34+4i]`는 `0x492457..0x49248F`에서 `0x464CB0(&surf, 0xAA=170, 0x80=128, colorkey=1, 0)`로 만든다 → `0x464DA9..0x464DCA` `SetColorKey(DDCKEY_SRCBLT, {0xFE,0xFE})`(lap914 지도). 그리는 쪽은 Lock 뒤 그리기 호출에 `0xFE` 인자를 넘기고(`0x4D37E8`·`0x4D3CE5`, 채움/키 용도는 미확인) 화면에는 `BltFast …0x11 SRCCOLORKEY`(`0x4D41E3`·`0x4D469D`) 또는 `Blt …KEYSRC`(`0x4D3AB9`)로만 보낸다 → 표면 안 254는 화면에서 투명.
- 자료 근거: 초상화 BMP 27장 모두 **170×128(= 위 표면 크기)**, 네 모서리 전부 254, 254 화소의 **91.1~100%가 테두리와 연결된 배경**(나머지는 머리카락 사이 등 안쪽 구멍; 색 키는 위치와 무관하게 투명).
- 공개 한계: HQ2002 EXE 문자열에 `portrait\`·`HERO`·`.bmp` 파일명이 없다(`syw%04d.bmp` 스크린샷만) → 이 BMP들이 런타임에 직접 쓰이는지 UNKNOWN(브리핑 초상화의 실제 소스는 미확인). HD 투자 우선순위는 낮게 둔다.
- 적용: 다음 work H-HDX2 Y-0(아래)에서 BMP 마스크 = `idx≠254`, `mask_source: "bmp_colorkey_fe"`. 사용자 메모 "투명은 0xFE 런만"은 RLE를 값으로 추측하지 말라는 뜻으로 해석하고, BMP는 엔진 색 키라는 직접 근거가 있어 예외로 둔다.
- 무압축 `.spr` 152개의 투명 처리는 근거 없음 → `raw_all_opaque` 유지(UNKNOWN).

### 3.2 팔레트 6→8비트 → **`×4` 유지(관례 고정).**
- 근거: 게임 제작 BMP 27장의 팔레트가 `imjin2.pal ×4`와 byte 동일 → 원작 자산 파이프라인의 관례가 `×4`다. 출력은 인덱스 PNG라 RGB 규칙은 업스케일러 입력 모습과 ② 양자화 기준에만 쓰인다 → ②는 같은 `×4` 표를 쓰면 일관된다. 엔진 실제 화면 값(16비트 LUT 여부)은 UNKNOWN이며 인덱스 출력에 영향 없다.
- 새 사실: `imjin2.pal ×4`에 **같은 RGB 중복 4쌍**(16/182·32/183·51/54·202/203)이 있다 → ② 양자화는 RGB만으로 인덱스를 복원할 수 없는 경우가 있다(아래 Y-2 동률 규칙).

## 4. 다음 work 사전등록(Sonnet) — H-HDX2: 검사·변환 도구 (HD 그림 경로 ②)

**목표.** 외부 업스케일러가 만든 RGB 2배 그림을 사용자 사양(8비트 인덱스 PNG·`imjin2.pal`·정확히 2w×2h·투명 254·실루엣 2×2 일치·팀색 236~239)으로 **검사·변환**하고, HUD 패널용 `.idx8` 본문을 만든다. 게임 DLL·EXE·하네스는 바꾸지 않는다(엔진 적용은 ③).

- **Y-0 선행 수리(추출 도구, 최소 변경):** `tools/g1_hd_extract.py` BMP 마스크 = `idx≠254`(§3.1), 254→240 치환은 BMP에서 제거(다른 포맷 리터럴 254는 현재 0이므로 기존 치환 경로는 남기되 manifest 카운트 유지). 테스트 RED→GREEN. 측정: 공유 temp 새 run에서 `--only portrait` 27장 마스크 = `idx≠254`·`literal_fe` 0·1배/2배 불투명 254 0, 그리고 **초상화 밖 37,878 프레임 PNG sha = lap1157 `sums1.txt` 그대로**(회귀 0).
- **산출 도구:** `tools/g1_hd_convert.py`(+ `tests/test_g1_hd_convert.py`, Makefile typecheck 목록 추가). 순수 Python + numpy·Pillow. 입력·기준(①의 추출 디렉터리, `--ref`)·출력 경로 인자; 출력이 저장소·게임 폴더 안이면 거부.
  - `check <hd_dir> --ref <extract_dir>`: `hd/<원본 상대경로>/<NNNN>.png`마다 ① 크기 = 기준 1배의 정확히 2w×2h ② 모드 P·팔레트 = imjin2×4(RGB 입력은 "convert 필요"로 분류) ③ 투명 254 위치 = 기준 마스크 2×2 확대와 완전 일치 ④ 불투명 화소에 254 없음 ⑤ 팀색: 기준 1배 팀색(236~239) 화소의 2×2 발자국 밖 HD 팀색 화소 수 = 위반, 발자국 안인데 팀색이 아닌 화소 수 = 위반. 파일별·합계 JSON.
  - `convert <rgb_dir> --ref <extract_dir> --out <hd_dir>`: RGB/RGBA PNG(크기 ≠ 2w×2h면 오류, 자동 리사이즈 금지) → `imjin2.pal ×4` 최근접 양자화(RGB 제곱거리). 후보 제한: 기준 팀색 발자국 안 = 236~239만, 밖 = 236~239·254 제외. **실루엣 강제:** 기준 마스크 2×2 밖 = 254, 안 = 불투명. **동률(중복 RGB 4쌍):** 같은 위치 기준 2배 초안 인덱스가 동률 집합 안이면 그 인덱스, 아니면 가장 작은 인덱스. 결정적.
  - `panel-idx8 <hd png> --ref <extract frame> --out <file>`: 헤더 없는 2w×2h 바이트(키 0xFE). 키 파일명은 런타임 source 주소를 포함하므로(`g1_panel_layer.h` `g1_panel_asset_key`) 여기서 만들지 않는다(③에서 로그로 확정).
- **측정식(전부 PASS여야 PASS):**
  - Y-0: 위 선행 수리 측정.
  - Y-1 항등 검사: Y-0 뒤 추출 run의 `_2x.png` 초안 전부(렌더 범위 37,905 프레임)를 `hd/` 배치로 보고 `check` → 위반 0.
  - Y-2 무손실 왕복: 그 초안들을 팔레트로 RGB 펼친 PNG → `convert` → 출력 인덱스가 초안과 **전 프레임 byte 동일**(동률 규칙 포함). 동률 규칙으로만 맞은 화소 수를 공개.
  - Y-3 음성 검출: 합성 결함(크기 ±1·팔레트 다름·실루엣 1화소 어긋남·불투명 254·팀색 누출/누락)을 각각 `check`가 검출(단위 테스트, 결함 종류마다 ≥1).
  - Y-4 잡음 견고성: 고정 시드로 RGB에 ±8 잡음·가우시안 흐림(σ=1)을 준 입력 ≥200 프레임(char·tile·BattleSpr·portrait 각 ≥30) → `convert` 출력의 `check` 위반 0(실루엣·팀색·254), 평균 RGB 오차와 인덱스 일치율을 공개(기준 아님).
  - Y-5 패널: `fnt/pannelk.spr`·`pannelj.spr`·`pannelc.spr`(831×163/143/160, `--image-dirs fnt --only pannel`)의 2배 초안 → `panel-idx8` → 크기 = 831×h×4, 엔진 `g1_panel_hd_pack_valid`(`g1_panel_layer.h`)를 호스트 gcc로 컴파일해 원본 프레임(투명 0xFE) 대비 유효 = 1, 본문 = 초안 byte 동일.
  - Y-6 결정성: 같은 입력 두 번 → 출력·리포트 sha 동일.
  - 원본 보호: 게임 폴더 listing digest·EXE SHA 전후 불변, 원본은 `rb`만.
- **TDD:** 양자화·후보 제한·동률·실루엣 강제·팀색 검사·크기 거부·출력 경로 거부·`.idx8` 길이를 합성 입력으로 RED→GREEN.
- **비목표·한계:** 업스케일러 실행, 엔진 적용·키 파일명(③), 일반 로더(④), 효과(반투명). 무압축 `.spr` 투명·초상화 BMP 런타임 사용 여부는 UNKNOWN 그대로.
- **중단:** 실패 가설 2회 또는 60분. 원본/참고 쓰기·커밋·`260921_temp` 금지. 산출물은 공유 temp `<날짜>_lap<N>_work_hdx2/`(디스크 여유 ≥20GiB, 현재 49G). 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** "함께 처리"(`SYW2_G1_DEFAULT_ON` 저장소 반영·사용자용 빌드 진단 기본 끔) work 1회 → ③ HUD 패널 1장 시범(lap1156 §6 순서 유지).

## 5. 검사

- SAFETY·CONTEXT 결과는 STATUS 검증 줄에 보강한다. focused 20 passed(§1).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. C·하네스·도구·테스트 source는 lap1157 full PASS(1867 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDX2(§4). 사용자 G1 시험 결과가 오면 최우선이다.

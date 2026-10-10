# 2026-10-09 | lap 1205 | G1 middle — lap1204 승격 처리 · H-HDU2(업스케일러 입력 묶음) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 run 0·C/tools/tests 변경 0·커밋 0.
- 입력: lap1204 work `loop/ESCALATE_SOL`(5줄, 원문 byte 일치 보존 `docs/history/laps/20261009_lap1205_preserved_lap1204_escalate_sol.txt` SHA256 `69c0c763…78c7f2`, `cmp` 일치 확인 뒤 삭제). `loop/STOP` 없음. INBOX 최신 = 2026-10-09 13:52 사용자 결정 "입력 묶음 만들어줘"(lap1203 선택지 (1))·root 디스크 정리(여유 239 GB). APPROVALS에 새 반려·사용자 G1 시험 결과 없음. `loop/.lap_counter` = 1205.
- 가설: 기존 도구(`tools/g1_hd_extract.py` H-HDX1, `tools/g1_hd_convert.py` H-HDX2)만으로 사용자가 바로 업스케일러에 넣을 1배 입력 묶음을 만들 수 있고, 사용자 결과(RGB 2배)를 같은 이름 규칙으로 돌려받으면 `convert`→`check`→`pack`이 그대로 받는다. 새 제품 코드는 필요 없다.

## 1. lap1204 검수

- 주장 "H-HDU2 카드·사전등록 없음": `grep -rl H-HDU2 docs/work docs/history/laps` = lap1203 기록(선택지 문구)·lap1204 기록·root 보존 원문뿐, 카드·측정식 없음 → **확인**.
- 주장 "제품 코드·테스트 변경 0": lap1200 full check 로그(06:29) 이후 새로 바뀐 tools/tests/patches/checks/Makefile 파일은 `tools/inmm_stub/_inmm.dll`·`lib_inmm.a`(lap1202 재빌드, gitignore 산출물)와 OMC 상태 파일뿐 → **확인**. 이번 회차 소스 fingerprint 대상 변경도 0.
- 주장 "`python3 -I`에 numpy 없음": 이 회차 셸에서 `.venv/bin/python -I` = numpy 2.4.3·Pillow 12.1.1 import 성공. lap1202도 `.venv/bin/python`으로 extract·convert를 돌렸다(scipy가 없어 bicubic stand-in만 시스템 `python3`). **실행 환경 = `.venv/bin/python`** 으로 정한다.
- 판정: lap1204 승격(work가 사전등록 없이 구현하지 않음)은 역할 규칙에 맞다. 정정 없음.

## 2. 설계 판단(근거)

- **원본 범위:** 사용자 결정 원문대로 `char,tile,fnt`. lap1202 `ref/manifest.json`(SHA256 `4f65df5d…dad10`)의 렌더 대상 = 파일 840개·**43,622 프레임**: rle char 20,598·rle fnt 5,794·rle tile 112·ytl tile 17,062·raw fnt 49·raw tile 7. 전체 분류 3,374 파일(rle 2,763·ytl 425·raw 152·bmp 27·unsupported 7) 중 나머지는 범위 밖 폴더라 렌더하지 않는다.
- **소비 경로 공개:** `pack`은 RLE `.spr`·`.ytl` 프레임(43,566)을 이름 붙여 담는다. raw 56프레임은 `fullscreen`/`panel-idx8` 경로 몫이며 각 파일이 실제 엔진에서 쓰이는지는 이 묶음에서 증명하지 않는다(묶음에는 1:1 개수 유지를 위해 포함). 이름 충돌(lap1202 남은 3개 106프레임)·같은 그림 중복(43,622 → 팩 파일 25,634)도 그대로 둔다 — 중복 제거는 사용자 작업량을 줄이지만 되돌림 대응표가 새로 필요해 이번 범위에 넣지 않는다(backlog).
- **파일 형식:** 도구가 이미 쓰는 그대로 = 8비트 인덱스 PNG, 팔레트 `imjin2.pal`×4(6비트→8비트), 투명 = 인덱스 254이며 PNG `tRNS`로 254만 투명 표시(`save_index_png` `transparency=254`). 팔레트 254 = RGB(252,224,252). 알파를 읽는 업스케일러는 투명을 그대로 다루고, 알파를 무시하는 업스케일러는 이 분홍이 가장자리에 번질 수 있다 — `convert`가 원본 실루엣을 2×2로 강제하므로 바깥 번짐은 지워지지만 실루엣 안쪽 가장자리 색 오염은 남을 수 있다(공개 위험, 첫 실제 결과에서 측정).
- **묶음 구성:** 사용자 폴더에는 업스케일할 1배 `NNNN.png`만 둔다(마스크·Scale2x 초안·manifest.json을 같이 두면 사용자가 그것까지 업스케일하게 된다). 루프가 변환에 쓰는 참조(1배·마스크·초안·파일별 manifest)는 옆 `ref/`에 따로 보존한다. 사용자 폴더는 `ref`의 하드링크가 아니라 **복사본**(사용자 쪽 수정이 참조를 바꾸지 않게).
- **돌려받는 규칙(`convert` 코드로 확인):** 파일 이름은 정확히 `^\d{4}\.png$`(`FRAME_RE`) — 다른 이름은 `ignored_files`로 무시된다. 폴더 구조는 입력과 같은 상대 경로. 크기는 정확히 가로·세로 2배(`quantize`가 다르면 `ConvertError "size … != required …"`, 크기 재조정 없음). RGB/RGBA 모두 받는다(`convert("RGB")`). 빠진 프레임은 `pack`이 `no_hd`로 세고 엔진은 기존 Scale2x로 폴백 → **일부만 돌려줘도 된다.**
- **위치:** 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261009_lap1206_work_hdu2/`(work 회차 번호가 다르면 그 번호로). 안내문 txt 금지 — 안내는 다음 middle이 APPROVALS 항목에만 적는다.
- **디스크:** 여유 239 GB(이 회차 `df`), lap1202 참조 추출 전체 603 MB → 충분.

## 3. H-HDU2 사전등록 (work 몫, 게임 run 0)

실행 환경 `.venv/bin/python -I`(작업 디렉터리 = 저장소 루트), 원본 `../[ESL]Syw2plus` 읽기 전용. 저장소 소스 변경 0이 기본이다. 묶음 복사·검증 스크립트가 필요하면 저장소가 아니라 `W/scripts/`에 둔다(W = 위 공유 temp 폴더).

| 단계 | 할 일 | PASS 조건 | FAIL/BLOCKED |
|---|---|---|---|
| U2-0 | 환경·안전 | numpy·PIL import 성공, 여유 ≥30 GB, 원본 EXE SHA `b56986e0…08a8ac` 실행 전후 MATCH | import 실패 → BLOCKED(다른 Python으로 몰래 대체 금지) |
| U2-1 | `tools/g1_hd_extract.py extract --out W/ref --image-dirs char,tile,fnt` | exit 0·`source_unchanged` true, summary = rle 2,763·ytl 425·raw 152·bmp 27·unsupported 7, 렌더 파일 840·`fc` 합 43,622, **`W/ref/manifest.json` SHA256 = lap1202 `4f65df5df49fc222…dad10`**(결정론) | manifest 불일치 → 차이 항목을 기록하고 원인(원본 mtime/크기 변화 등) 설명 전에는 묶음을 사용자에게 알리지 않음 |
| U2-2 | `W/ref`의 `<rel>/NNNN.png`(FRAME_RE)만 `W/upscaler_input_1x/<rel>/NNNN.png`로 **복사** | 개수 43,622 = ref의 FRAME_RE 개수 = manifest `fc` 합, 입력 폴더 안 다른 파일 0, 전 파일 SHA256 ref와 일치(불일치 0), 하드링크 0(`st_nlink`=1), 정렬 목록 `W/upscaler_input_1x.manifest.sha256`(폴더 **밖**) | 개수·SHA 불일치 1개라도 FAIL |
| U2-3 | 형식 전수 검사 | 43,622 전부: 모드 P, 팔레트 768 B = `imjin2.pal`×4, `tRNS` 투명 인덱스 = 254만, 크기 = manifest `fw×fh`, `_mask.png` 0 위치 = 254·1 위치 ≠254(위반 0). 불투명 0인 전부-투명 프레임 수는 숫자로 공개 | 위반 1개라도 FAIL |
| U2-4 | 돌려받기 규칙 모의(가짜 업스케일러) | 시드 1205로 200프레임 골라 최근접 2배 RGB PNG(같은 상대 경로·이름)를 `W/sim_rgb/`에 쓰고 `convert --ref W/ref --out W/sim_hd W/sim_rgb` → converted 200·errors 0·ignored 0, `check --ref W/ref W/sim_hd` 위반 0. 음성 대조 2개: (a) 4배 크기 1개 → errors 1(size 문구), (b) `0000_out.png` 이름 1개 → ignored_files 1 | 규칙 문장(이름·크기·RGB 허용)과 도구 동작이 다르면 FAIL — APPROVALS 안내 문구를 그 동작에 맞춰 고칠 근거 |
| U2-5 | 크기·정리 | `du -sh` `upscaler_input_1x`·`ref` 기록, `sim_*`는 검사 뒤 삭제(결과 json·SHA만 보존) | — |

- 산출 기록: `W/steps.log`, extract.log, `W/u2_verify.json`(U2-2·U2-3 결과), `W/u2_sim.json`(U2-4), 각 SHA256.
- 검사: 저장소 소스 변경 0이면 전체 `make check` 생략 가능(그 경우 focused `tests/test_g1_hd_extract.py`·`tests/test_g1_hd_convert.py`+`checks/safety.sh check`). 소스를 바꾸면 PROMPT ⑥ 순서대로 lint·typecheck 뒤 `make check` 1회.
- 끝나면 work는 `loop/ESCALATE_SOL`(middle 검수 요청)을 남긴다. **다음 middle**이 새 스크립트로 개수·SHA·형식을 독립 재계산한 뒤 APPROVALS lap1203 항목을 갱신해 사용자 안내(위치·파일 수·투명 254/분홍·2배 정확·이름 `NNNN.png` 유지·폴더 구조 유지·RGB 허용·일부만 줘도 됨·결과 위치 알려 주기)를 적는다. 안내문 txt는 만들지 않는다.
- 하지 않는 것: 실제 업스케일(사용자 몫), 중복 제거, BattleSpr/portrait 범위 확장, 게임 run, 시험판 재스테이징.

## 4. 검증 / 다음

- focused `tests/test_g1_hd_extract.py`·`tests/test_g1_hd_convert.py` **66 passed/0.97s**(로그 `logs/gates/lap1205-middle-focused.log` `39fee981…`). 전체 `make check` SKIP(문서만 변경, 소스는 lap1200 full PASS 2042 그대로). `checks/safety.sh check` 결과는 STATUS에 보강.
- 원본 EXE SHA 실행 없음(읽기만, 게임 run 0).
- 다음 한 가지: work가 H-HDU2 U2-0~U2-5 실행 → ESCALATE_SOL → middle 독립 재계산·APPROVALS 사용자 안내.

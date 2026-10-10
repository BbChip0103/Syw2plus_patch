# 2026-10-07 | lap1159 | G1 work — H-HDX2 HD 그림 검사·변환 도구 (HD 그림 경로 ②)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무). 게임 실행 0, 게임 DLL·EXE·하네스·C source 변경 0, 커밋 0. 원본 데이터는 읽기만.
- 입력: STATUS "다음 한 가지" = lap1158 middle 사전등록 §4(`docs/history/laps/20261007_lap1158_middle_g1_hdx1_review_hdx2_preregistration.md`). `loop/ESCALATE_SOL`·`loop/STOP` 없음, APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 가설: 외부 업스케일러의 RGB 2배 그림을 사양(8비트 인덱스·`imjin2.pal ×4`·2w×2h·투명 254·실루엣 2×2 일치·팀색 발자국)으로 검사·변환하고 패널 `.idx8`을 만들 수 있다.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e0…8ac` 실행 후 MATCH. 게임 폴더 listing digest(경로·크기·mtime_ns) 전·후 `46b3e298390202ba…` = lap1157 run1 값과 동일, run3 manifest `source_unchanged` true.

## 1. 변경 파일 (uncommitted)

| 파일 | SHA256 |
|---|---|
| `tools/g1_hd_convert.py`(새, `check`·`convert`·`draft`·`panel-idx8`) | `13216ab6a31d7fe23b773372b75eba6665f4e3b8fecf91cd9a5b1f5d074a17fa` |
| `tests/test_g1_hd_convert.py`(새, 16 tests) | `9a9b9deb8313fd13b14e3f2e5c74ad20aa1bed122e10ee5f8559531d8e93c74e` |
| `tools/g1_hd_extract.py`(Y-0: BMP 마스크 = `idx≠254`, `mask_source "bmp_colorkey_fe"`) | `358c482ab9ae8f9c05b09db3716c66be388a9631ceae3aa2030e86da3e941845` |
| `tests/test_g1_hd_extract.py`(BMP 색 키 테스트 추가, 21 tests) | `d686e2152c16efd64cf323754a291225212b1fc0e0a0ae49fa1d65dfaf3cc091` |
| `Makefile` | typecheck 목록에 `tools/g1_hd_convert.py` 1개 추가 |

공유 temp 산출물: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1159_work_hdx2/`(run3 추출·hd_safe·rgb_safe·y2_out·y4·panel_run·panel_hd·panel_idx8·`scripts/`·결과 JSON·txt). 로그 `logs/gates/lap1159-*`.

## 2. 사전등록 이탈 1건 (공개) — Y-1/Y-2 초안 정의

- **발견:** 추출 도구의 Scale2x 초안(`_2x.png`) 그대로는 ⑤ 팀색 검사를 통과하지 못한다. `check`를 원본 추출 초안 37,905 프레임에 돌리면 **12,191 프레임·위반 195,235**(team_leak 142,430·team_missing 52,805; 실루엣·크기·팔레트·tRNS 위반 0)이다. Scale2x가 팀색 값을 이웃 블록으로 퍼뜨리고 팀 블록을 이웃 값으로 덮기 때문이다(`y1_check.json`). 사전등록 Y-1 "초안 전부 `check` → 위반 0"은 이 정의로는 불가능하다.
- **선택:** `check` 규칙(⑤)은 그대로 두고 초안 쪽을 고쳤다. `RefFrame.team_safe_draft` = 기존 초안에서 (a) 팀 화소의 2×2 발자국을 원본 화소로 채우고 (b) 발자국 밖 팀색 값을 그 블록 원본 화소 값으로 대체. 실루엣은 불변. 새 `draft` 명령이 이것을 `hd/` 트리로 쓴다. `_2x.png` 파일과 추출 도구의 Scale2x는 바꾸지 않았다(엔진 커널과 byte 동일 테스트 유지, Y-0 회귀 0 보존). `convert`의 동률 규칙은 team-safe 초안 인덱스를 쓴다.
- Y-1·Y-2는 team-safe 초안으로 측정했다. 이 정의가 사용자 사양의 의도(팀색 재적용이 팀 발자국에만 닿는다)에 맞는다는 판단은 middle 검수 사항이다.

## 3. 측정 (모두 새 추출 run3 = 수리 후 도구, 렌더 37,905 프레임)

| 항목 | 결과 | 판정 |
|---|---|---|
| **Y-0** 선행 수리 | 초상화 BMP 27장 마스크 = `idx≠254` 27/27(불일치 0), `literal_fe` 0, 1배·2배 불투명 254 0. **초상화 밖 PNG 113,634개 sha = lap1157 `sums1.txt` 전부 동일(회귀 0)**, 파일 수·이름 집합 동일(113,715), run3 manifest 요약 = lap1157과 같음(bmp 27·raw 152·rle 2,763·ytl 425·unsupported 7). `scripts/y0_check.py` → `y0_result.json` | PASS |
| **Y-1** 항등 | 원본 `_2x` 초안 그대로: 위반 195,235(12,191 프레임) — §2. `draft` 산출(team-safe) 37,905 프레임 `check`: 위반 0·실루엣/크기/팔레트/tRNS/팀 전부 0, `y1_check_safe.json` | PASS(team-safe 정의, §2 이탈) |
| **Y-2** 무손실 왕복 | team-safe 초안 → 팔레트로 RGB 펼침 → `convert` → 출력 37,905/37,905 프레임 **파일 byte 동일·화소 동일**(`y2_compare.txt`). 불투명 화소 207,365,684 중 동률 화소 1,439,532개(0.69%)가 전부 초안 인덱스로 결정됨(tie_resolved_by_draft = tie_pixels) → 동률 규칙이 없으면 왕복이 깨진다(공개) | PASS |
| **Y-3** 음성 검출 | 단위 테스트가 결함 종류마다 `check` 검출: 크기 ±1 두 방향·팔레트 다름·tRNS 없음·실루엣 1화소 제거·팀색 누출 1·팀색 누락 1·RGB 입력(`needs_convert`)·기준 없음(`no_reference`). `tests/test_g1_hd_convert.py` | PASS |
| **Y-4** 잡음 견고성 | 고정 시드 1159, char 90·tile 50·BattleSpr 50·portrait 27 = **217 프레임**을 각각 ±8 균일 잡음·가우시안 σ=1(PIL radius 1)으로 변형 → `convert` → `check` **위반 0/0**(217/217 ok). 공개(기준 아님): 잡음 평균 RGB 오차 0.875·인덱스 일치율 평균 0.836(최저 0.313), 흐림 평균 RGB 오차 15.15·일치율 평균 0.424(최저 0.0). `y4_metrics.json` | PASS |
| **Y-5** 패널 | `fnt/pannelk.spr`(831×163)·`pannelj`(831×143)·`pannelc`(831×160) 1프레임씩 추출 → `draft` → `panel-idx8`: 바이트 541,812/475,332/531,840 = 831×h×4 일치, 엔진 `g1_panel_layer.h` `g1_panel_hd_pack_valid`를 호스트 gcc(-std=c11 -Wall -Werror)로 컴파일해 원본 프레임(투명 0xFE) 대비 **3/3 유효 = 1**, 본문 = team-safe 초안 byte 동일 3/3(pannelk는 원본 `_2x` 대비 27 화소 차 = 팀색 고정). `y5_result.json` | PASS |
| **Y-6** 결정성 | 같은 입력(잡음 217 프레임) `convert` 두 번: 출력 트리 sha `bccca089…` 동일, 리포트 JSON sha `2d7cbf8e…` 동일. 추출·`draft`·`convert` 단위 테스트도 두 번 byte 동일 | PASS |
| 원본 보호 | listing digest·EXE SHA 전후 불변, 새 도구는 게임 폴더 `rb`만, 출력이 저장소·게임 폴더·입력 안이면 거부(테스트) | PASS |

## 4. 도구 계약 요약

- `check <hd_dir> --ref <extract_dir>`: ① 크기 정확히 2w×2h ② 모드 P·팔레트 = `imjin2×4`(RGB는 `needs_convert`) ③ 실루엣 = 기준 마스크 2×2 확대 ④ tRNS가 인덱스 254만 투명(PNG에서 "불투명 254"는 tRNS 누락·오류로 판정) ⑤ 팀색 발자국 밖 누출·안 누락 ⑥ 기준 없음. 종료코드 0 = 위반 0·전부 ok.
- `convert <rgb_dir> --ref ... --out ...`: 후보 = 발자국 안 236~239만 / 안 아닌 불투명 = 236~239·254 제외 / 실루엣 밖 = 254 강제. 크기 불일치는 오류(자동 리사이즈 없음, RGBA 알파는 무시하고 기준 실루엣 사용). 최근접 = RGB 제곱거리, 동률 = team-safe 초안 인덱스가 동률 집합 안이면 그것, 아니면 가장 작은 인덱스.
- `draft --ref ... --out ...`, `panel-idx8 <hd png> --ref <1배 png> --out <file>`(비적합이면 거부, 키 파일명은 ③에서 로그로 확정).
- 비목표·UNKNOWN 유지: 업스케일러 실행·엔진 적용·일반 로더(④)·효과(반투명), 무압축 `.spr` 투명·초상화 BMP 런타임 사용 여부.

## 5. 검사

- 새·갱신 테스트 `tests/test_g1_hd_convert.py` 16 passed, `tests/test_g1_hd_extract.py` 21 passed(0.83s, `.venv/bin/python`). `make lint`·`make typecheck`(12 파일, `tools/g1_hd_convert.py` 추가) 통과. 전체 `make check` 결과는 STATUS 검증 줄에 보강한다(검사 후 이 기록을 고치지 않는다).

## 다음 행동

middle(Opus) 검수: (1) 새 스크립트로 Y-0~Y-6 재계산(work `scripts/*.py` 재사용 금지, 특히 Y-2 동률 규칙 의존도·Y-4 합성 변형), (2) §2 team-safe 초안 정의 수용 여부, (3) ③ HUD 패널 시범과 "함께 처리" 순서 사전등록.

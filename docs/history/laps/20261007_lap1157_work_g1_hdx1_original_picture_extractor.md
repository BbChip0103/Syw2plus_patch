# 2026-10-07 | lap1157 | G1 work — H-HDX1 원본 그림 추출 도구 (HD 그림 경로 ①)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무). 게임 실행 0, 게임 DLL·EXE·하네스·C source 변경 0, 커밋 0. 원본 데이터는 읽기만.
- 입력: STATUS "다음 한 가지" = lap1156 middle 사전등록 §8(`docs/history/laps/20261007_lap1156_middle_g1_hos2_review_hdx1_preregistration.md`). `loop/ESCALATE_SOL`·`loop/STOP` 없음, APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 가설: `.spr`·`.ytl`·8비트 BMP를 읽기 전용으로 풀어 사양(8비트 인덱스 PNG·`imjin2.pal`·정확히 2w×2h·투명 254·실루엣 2×2 일치)에 맞는 1배·마스크·2배 초안을 만들 수 있다.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(실행 후). 범위 안 3,374 파일 SHA256을 실행 후 독립 재계산해 run1 manifest와 불일치 0, 게임 폴더 전체 목록(경로·크기·mtime) digest 전후 동일.

## 1. 변경 파일 (uncommitted)

| 파일 | SHA256 앞 16자 |
|---|---|
| `tools/g1_hd_extract.py`(새) | `e9a17df2cc22b1f5` |
| `tests/test_g1_hd_extract.py`(새, 20 tests) | `47b1bce119fe3a44` |
| `Makefile` | typecheck 목록에 `tools/g1_hd_extract.py` 1개 추가 |

명령: `g1_hd_extract.py extract --out <dir> [--image-dirs …] [--only …] [--census-only]`, `roundtrip --count N --seed S`, `xcheck --re-parsers <dir> --count N --seed S`. 출력이 게임 폴더·저장소 안이면 거부. 원본은 `read_bytes`/`rb`만.

## 2. 포맷 확정 — 사전등록 §7 가정을 정정한 4건

lap1156 middle §7은 RE 파서 모델("시트 격자")을 참고로 적었다. 실제 census로 확인한 엔진 쪽 구조는 다르다.

1. **RLE `.spr`**: 프레임마다 독립 스트림. 오프셋표 `0x4C4`(프레임 0은 0)가 각 스트림 시작이고, 스트림은 정확히 `fw×fh` 화소에서 끝난다. 시트 레코드(`0xBC8`)는 메타데이터일 뿐 프레임을 시트 격자에서 자르지 않는다. 근거: 2,763개 RLE 파일 중 2,762개는 **모든 프레임이 정확히 소비**(스트림 바이트 = 선언 구간, 화소 수 = `fw×fh`), 예외는 `Online/Object/SItem001.Spr` 프레임 0 하나(시트 1920×160·프레임 64×32·fc 1인 이상 파일).
2. **무압축 `.spr`**(픽셀 바이트 == 시트 w×h, 152개): 프레임은 연속 `fw×fh` 블록이다(가로 띠 시트 아님). 접촉 시트(`yfnt/lobbynumbutton.spr`)에서 블록 해석은 버튼 3개가 온전하고 띠 해석은 깨진다. 151개는 오프셋표가 `i×fw×fh`와 일치, 1개는 불일치(블록 사용·경고 기록).
3. **`.ytl`**(425개): 오프셋표 `0x4C0`, 프레임 = `fh`개 스캔라인 레코드 `[skip][count][count 바이트]`(plan_c `ytl.cpp`와 같은 규칙). **425개 전부, 모든 프레임이 정확히 소비**되고 다음 프레임 오프셋과 일치. fc>300 5개는 모두 fc=450(`*.ypr.ytl`)이며 오프셋표 끝이 `0xBC8`과 정확히 맞는다(`0x4C0+4×450`).
4. **BMP 8비트**: 27개 전부 팔레트 = `imjin2.pal`×4와 byte 단위 동일(27/27). 24비트 5개는 dxwnd 도구 그림이라 범위 밖.

투명 규칙: 실루엣 = RLE 투명 런 / ytl 레코드 밖만. 인덱스 값으로 추정하지 않는다. 리터럴 `0xFE`(RLE의 `FE 00`, ytl·raw·BMP의 값 254)는 불투명이므로 사양의 "투명 254" 예약과 충돌한다 → 1배·2배 출력에서 `imjin2.pal`상 254 색(252,224,252)에 가장 가까운 비254 색 **240**(236,236,236)으로 치환하고 프레임별 `literal_fe`로 센다. 영향: 렌더 대상 37,905 프레임 중 27프레임(portrait BMP 27개 전부; 한 장당 4,588~6,745 화소)뿐. **초상화가 원본에서 254를 색 키로 쓰는지는 UNKNOWN**이다.

6비트→8비트 규칙: `v×4`(RE `pal_parser`와 같음, 최대 252). manifest `palette.rule: 6bit_x4`.

## 3. 측정식 판정

| 식 | 결과 | 근거 |
|---|---|---|
| X-1 census | **PASS** | 범위 안 3,374 파일: rle 2,763(그중 시트 레코드 0/부족 fallback 16)·raw 152·ytl 425·bmp 27, 예외 없이 분류. 명시 분류 7: `temp.spr`(0xBF4 미만)·`fnt/imjin2plus.spr`(fc=0)·dxwnd BMP 24비트 5. `.ytl` fc>300 5개의 프레임 수 근거 = 헤더 fc=450 = 오프셋표 끝 `0xBC8` 일치 + 450프레임 전부 정확 소비 |
| X-2 RE 파서 교차 | **FAIL(기준 문구 그대로) — 원인 분류 완료, RE 쪽 모델 결함** | 시드 1157, 버킷별 8개(단일 프레임 버킷은 모집단이 작으면 전수) 총 53 파일. 단일 프레임 파일 19/21 일치(불일치 2 = 시트 폭 172·190이 프레임 폭 170·190보다 커서 RE가 줄 간격을 틀림: `bank_scroll01.spr`·`inn_mainmenuimage_back.spr`). **다중 프레임 파일은 0/32 파일, 불투명 화소가 있는 일치 프레임 0**(RE는 시트 전체를 한 번에 RLE로 풀고 격자로 자르는 모델, `.ytl`은 시트 전체 skip/count 세그먼트 모델). 내 모델의 독립 근거 3개: ① 2,762/2,763 파일 전 프레임 정확 소비 ② X-3 byte 동일 왕복 ③ X-6 육안(유닛·타일·초상화 정상). 사전등록 문구("RE 쪽 결함이면 근거와 함께 공개")대로 공개하며 PASS로 쓰지 않는다 |
| X-3 왕복 | **PASS** | seed 1157, 391 파일(`.spr` RLE 191·`.ytl` 200, raw 9개 제외) 16,014 프레임을 같은 규칙으로 재인코딩 → 원본 프레임 바이트와 **16,014/16,014 byte 동일**. 규칙: RLE 런은 줄 끝과 255에서 끊김, ytl 빈 줄 = `skip=fw,count=0`. 처음 구현(줄 무시 런)은 일치 2,238/4,435였고 두 규칙을 원본에서 알아내 고쳤다 |
| X-4 2배 초안 규칙 | **PASS** | 독립 검사 스크립트(`scripts/verify_x4.py`)가 run1 렌더 37,905 프레임(697 파일) 전부: 크기 2w×2h 위반 0·모드 P/1 위반 0·팔레트 = `imjin2.pal` 위반 0·투명 254 tRNS 누락 0·마스크 2×2 불일치 0·불투명 화소가 254인 경우 0·마스크 PNG와 1배 투명 위치 불일치 0. Scale2x = 엔진 `g1_scale2x_core.h`와 같은 규칙: 단위 테스트가 호스트 gcc로 엔진 커널을 컴파일해 40개 무작위 (크기·마스크·값) 입력의 출력 byte 일치를 확인 |
| X-5 결정성 | **PASS** | 같은 입력 두 번 실행(run1·run2) 114,413 파일 sha256 목록 `cmp` 0(manifest 포함, 타임스탬프 없음). 실행 시간 각 약 2~3분 |
| X-6 열람 | **PASS** | 접촉 시트 3장(공유 temp `contact/`): 유닛 `char/archerk.spr`(걷기·공격·죽음 6프레임 — 방향·색·투명 정상), 지형 `tile/normal/grss1.ytl`(다이아몬드 6프레임 — 1배·마스크·2배 정상), 초상화 `portrait/HERO000.BMP`(색 정상, 마스크 전부 흰색 = 전체 불투명) |
| 원본 보호 | **PASS** | 위 원본 SHA·범위 안 3,374 SHA 불일치 0·게임 폴더 listing digest 전후 동일(manifest `source_unchanged: true`), RE 저장소는 `-B`로 읽고 `__pycache__` 0 |

판정: 도구 기능 `PASS(partial, 기술·격리)`. X-2는 기준 문구상 FAIL이며 원인(참조 구현의 결함)은 분류·증거와 함께 닫았다. 최종 판정은 middle 몫.

## 4. 출력·산출물 (공유 temp `20261007_lap1157_work_hdx1/`)

- `run1/`: 기본 범위(`char`·`tile`·`BattleSpr`·`portrait`) 렌더 37,905 프레임 × (1배·마스크·2배) = 113,715 PNG + 파일별 `manifest.json` 697 + 전체 `manifest.json`(sha `1f41ab63…`) = 114,413 파일, 529 MB. 디스크 여유 49 GiB(≥20 GiB 유지). `run2`는 X-5 비교 뒤 삭제(`sums1.txt`·`sums2.txt` 보존, 동일).
- 렌더 안 한 범위(`Online` 91k 프레임·글꼴·`ybriefingfnt`·`stagemap`·`fnt` 등)는 manifest(분류·크기·SHA·프레임 수)만 있다. 이미지는 `--image-dirs`로 켠다.
- 팀색 236~239 화소가 있는 프레임 13,001개(프레임별 `team` 수 manifest에 기록).
- `scripts/`: census·검증·접촉 시트 스크립트, `xcheck_seed1157_count8.json`(`77997627…`), `roundtrip_seed1157_count200.json`(`b216a0aa…`), `verify_x4_run1.txt`(`ba8878e9…`).

## 5. 공개 한계

- 무압축 `.spr` 152개는 투명 런이 없어 실루엣을 전부 불투명으로 둔다(`mask_source: raw_all_opaque`, 엔진이 이 시트의 0xFE를 투명으로 쓰는지 UNKNOWN). 이 중 렌더 범위(`BattleSpr`)는 11개.
- `Online` 파일의 프레임은 이번에 이미지로 풀지 않았다. `SItem001.Spr` 프레임 0은 정확 소비 실패(예외 1).
- 초상화 254 치환(§2)과 팔레트 6→8비트 `×4`(엔진의 실제 DirectDraw 팔레트 값은 미확인)는 ② 변환 도구에서 한 번 더 결정해야 한다.
- 업스케일러 실행·양자화·팀색 재적용·`.idx8` 생성·엔진 적용은 ② 이후다(비목표).

## 6. 검사

- `make lint`·`make typecheck` PASS. 전체 `make check` 결과는 STATUS 검증 줄에 보강한다(이 기록 작성 뒤 1회).

## 다음 행동

middle(Opus) H-HDX1 검수: X-2 FAIL 원인(RE 모델 결함) 판정, 사전등록 §7 정정 4건 수용, 초상화 254·팔레트 ×4 결정, 이어서 ② 검사·변환 도구(또는 "함께 처리" 항목) 사전등록. 사용자 G1 시험 결과가 오면 최우선.

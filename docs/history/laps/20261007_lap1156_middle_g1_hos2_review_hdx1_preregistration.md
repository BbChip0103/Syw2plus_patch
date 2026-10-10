# 2026-10-07 | lap1156 | G1 middle — H-OS2 독립 검수·수용(OS2-1 FAIL·수리 측정식 FAIL·기능 정상), HD 그림 경로 ① H-HDX1(원본 추출 도구) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 게임 코드·하네스·테스트 변경 0, 커밋 0. 원본 데이터는 읽기만(헤더 census).
- 입력: `loop/ESCALATE_SOL`(lap1155 work). 원문을 byte 일치로 `docs/history/laps/20261007_lap1156_preserved_lap1155_escalate_sol.txt`(SHA256 `1b7927619b1b…`, cmp 일치)에 보존한 뒤 삭제했다. 그 밖 입력은 lap1155 기록, lap1154 사전등록 §7, INBOX 2026-10-07 19:3x 사용자 지시(G1 HD 그림 경로 ①~⑥). APPROVALS 새 반려·사용자 G1 시험 결과 없음(lap1152 요청 대기, 비차단), `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. pair `execution_source.unchanged == true`.
- fixture: 재실행 없음. lap1155 raw만 재계산(`--new-game-path` d1·d2·d3·e1·e2·f1, NG5 플래그 ng5·ng5off·ng5b, 비합성 save006 pair 1회).
- 가설(검수 대상): H-OS2 — PS5·PS7 GDI 글자 stale은 TextOutA `reject_target` 호출 때문이며 그 DC 대상은 (i) 화면 (ii) 화면으로 복사되는 스크래치 (iii) 그 밖 중 하나다.

## 1. 출처

- source SHA 12자리: `g1_mirror2x.c` `96e632a55e55`·`g1_mirror2x.h` `01960b2f0ffb`·`direct_draw_trace.c` `b13c786827de`·`tests/test_g1_rect_fill.py` `e2c1ab413aa8` = lap1155 기록. `tools`·`tests`·`checks`·`patches`·`Makefile` 아래 `logs/gates/lap1155-work-full-check.log`보다 새 파일 0개 → full PASS 뒤 source 변경 0.
- `lap1155-work-full-check.log` SHA256 `da5068de1ea7…`, `1847 passed, 5 skipped in 768.15s`·`All checks passed!`·`CONTEXT_PASS`, `.exit` 0, safety `SAFETY_PASS`. 공개 1: 같은 회차에 `lap1155-work-full-check-aborted-escalate-edit.log`(14% 진행 중 `Terminated`)가 있다 — 기록 수정 뒤 재실행했고 판정에 쓰인 것은 위 완주 로그다.
- run exit: d1·d2·d3·e1·e2·f1·ng5·ng5off·ng5b·pair 전부 0. `local/runtime/lap1155*/game` 0개. 디스크 여유 50G.

## 2. 독립 재계산 (새 스크립트, work `os2_*.py` 재사용·import 없음)

공유 temp `20261007_lap1156_middle_review/`:

| 파일 | SHA256 |
|---|---|
| `recalc_lap1156.py` / `.json` | `7717249d7432…` / `cd80ae82e36f…` |
| `band_lap1156.py` / `.json` | `496ef0cbb52b…` / `af3aed0cefc2…` |
| `rebuild_lap1156.py` / `.json` | `3f3a221ad128…` / `07ce9734a3dd…` |
| `rebuild/_inmm.dll` | `ed4419edd7c6…` |
| `feas_lap1156.py` / `.json` | `fae0edc54665…` / `5f61c138d268…` |

정착 = 상태 present 후반부(마지막 40으로도 같은 값). 캡처 판별 = 독자 Scale2x(lap1154 방식). DC 분류는 로그 필드 `dcbits==scr`→화면, `dcbits==rbuf`→버퍼로 직접 다시 셌다.

**판정 불일치 0, 해석 정정 1(§3).**

| 항목 | 재계산 | work 값 | 판정 |
|---|---|---|---|
| PS5 정착 HD min / stale max (f1·e1·e2) | 98.801 / 5,754 · 98.949 / 5,044 ×2 | 동일 | 일치 |
| PS7 정착 HD min / stale max (f1·e1·e2) | 99.627 / 1,790 · 99.709 / 1,398 ×2 | 동일 | 일치 |
| PS9 HD min (9 run) | 100 | 동일 | 일치 |
| PS5·PS7 캡처 nearest 블록 (f1·e1·e2) | 2,426·798 / 2,305·744 ×2 (d1 2,427, d2·d3 2,426) | 동일 | 일치 |
| 켬↔끔 캡처 마스크 | PS5 끔에만 121·켬에만 0·공통 2,305 / PS7 54·0·744 | −121·−54 | 일치(켬은 순수 감소) |
| d3 거부 TextOutA 4,707 = 상태·DC | PS5 화면 660·버퍼 1,954 / PS7 화면 805·버퍼 1,288 → 화면 1,465·버퍼 3,242 | 동일 | 일치 |
| DC 기하 | 버퍼 = 357×248 stride 360(렌더러 stride 360·높이 600), 화면 = 1600×1200 stride 1600 | 동일 | 일치 |
| 화면 DC 사각형 ∩ 캡처 stale | PS5 8 사각형 277/2,426(11.42%)·PS7 5 사각형 135/798(16.92%) | 11.4%·16.9% | 일치 |
| 스크래치 합집합 단일 오프셋 최대 겹침 | PS5 221(9.11%, (410,115))·PS7 305(38.22%, (199,213)) | 9.1%·38.2% | 일치 |
| e1 `screen_dc_calls` / 화면 DC 거부 | 1,482 / 0 (e2 1,471 / 0, f1 0 / 1,452) | 동일 | 일치 |
| `keyed_copy_466480_invocations` (9 run) | 0 | 0 | 일치 |
| hresult≠0 / fallback / covered≠480,000 (9 run) | 0 / 0 / 0 | — | 확인 |
| NG5 PS3 present / HD min / 단발 stale 개수 | ng5 2,978 / 99.949 / 8개(16~247) · ng5off 2,977 / 99.943 / 1개(274) · ng5b 3,050 / 100 / 0개 | 동일 | 일치 |
| NG5 PS5 장기 체류(748~756 present) | 켬 98.949(ng5·ng5b) vs 끔 98.719(ng5off, lap1154 공개값 재현) | — | 추가 확인: 체류에서도 개선 |
| pair-result | `06aa1a8a0597` PASS·scene_state_equal·input_effect·minimap parity·loaded_capture·V2/V2s/V2q/Scale2x PASS·source unchanged | 동일 | 일치 |

## 3. 해석 정정 1 — 단일 오프셋 탐색 9.1%는 (ii)를 반증하지 않는다; 지도 목록 줄 너비가 스크래치 글자 너비와 줄마다 맞는다

- 스크래치 호출은 전부 원점 (0,0)/(1,1)에 한 줄씩 그린다(PS5 고유 20 = 10 문자열×그림자 쌍, 너비 21·43·83·101·104·105·106·112·121·140, 높이 11). 한 줄씩 그려 각기 다른 y로 옮기는 구조라 "합집합 하나를 한 오프셋에 놓는" 탐색은 한 줄만 맞출 수 있다 — 낮은 겹침은 예상된 값이지 반증이 아니다.
- 대신 줄 단위로 보면(`band_lap1156.json`): PS5 캡처 stale의 **60.6%(1,470/2,426)**가 지도 목록 영역(x445..593)에 있고, 높이 10~11 px 띠 9개가 y118..287에 약 20 px 간격으로 있다. 띠 너비 106·106·104·99·111·121·107·139·83 ↔ 스크래치 너비 106/105·104·101·112·121·106·140·83 — 줄마다 ±2 px 안에서 대응한다.
- 결론: 지도 목록 글자는 **(ii) 스크래치→화면 복사 경로일 가능성이 높다(정황 강함)**. 단 복사 writer가 미식별이라 사전등록 기준의 "(ii) 확정"은 아니며 OS2-1 FAIL 판정은 유지한다. 다음 귀속은 PS5 지도 목록 한 줄(예: x446..551·y118..127) screen watch로 복사 writer EIP를 잡는 것이다(backlog, §6).

## 4. 코드 검토·독립 재조립

- `textout_screen_dc_target`(`g1_mirror2x.c:5505-5518`): 렌더러 바인딩 검사가 거부했을 때만 호출되고, DC bitmap bits == 마지막 present 소스 `Lock` 포인터(`:2105`)·`bmWidthBytes`∈[800, `G1_MAX_STRIDE`]·`bmHeight`≥600일 때만 그 buffer·stride를 받는다. 포인터 일치는 지금 DC가 그 메모리를 쓰고 있다는 뜻이라 낡은 포인터 위험은 없다. 거부 진단 `textout_reject_target_note`는 수리 실패 뒤에만 불리므로 켬에서 화면 DC 거부 0은 정의상 맞다. env는 정확히 `"0"`일 때만 끔(`:745`) → 기본 켬. 진단 로그는 `layer_drift_on()`일 때만 쓴다(상한 4,096/상태; 사전등록 64 이탈은 옵트인 진단이라 기본 경로 영향 없음, 수용). 결함 없음.
- 공개: e1에서도 화면 DC 사각형 안 PS5 stale 156 블록(277 중)이 남는다. 같은 영역의 다른 writer(옵션 버튼 테두리 등)로 보이며 이번 수리 범위 밖이다.
- 재조립(lap1154 방식): manifest 원본 입력 62개 = 트리, `runtime_bridge.c` 일치, 그 밖 소스 62개 = bridge, Makefile·`supply_probe` 2줄 변환 일치 → mingw `make` rc 0. 재빌드 461,091 B는 e1 bridge(`70618a8280b1…`)와 6바이트(136·137 COFF TimeDateStamp, 216·217 CheckSum, 349700·349701 export TimeDateStamp)만 다르다 → **타임스탬프·체크섬 외 동일**. e2·f1·ng5·ng5off·ng5b·pair bridge도 같은 마스크 안. d3 bridge(460,837 B)는 수리 전 진단 DLL이라 대조 대상 아님. 문자열 `SYW2_G1_TEXTOUT_SCREEN_DC` 1회.

## 5. 판정

- **H-OS2 수용: OS2-1 귀속 `FAIL`(사전등록 ≥60% 미충족), OS2-2 수리 측정식 `FAIL`(PS5 nearest −5.0% < 10%), 수리 기능은 정상·회귀 0(save006 pair·NG5·PS9 PASS)이라 기본 켬 유지.** 가시 효과는 PS5 −121·PS7 −54 블록으로 작다 — 재스테이징 사유 아님.
- ng5 PS3 단발 stale 8개는 끔(1개)·켬 반복(0개)과 비교해 run 변동으로 보는 work 판단을 수용하되 원인은 UNKNOWN으로 남긴다(backlog 유지).
- 이것은 G1 사용자 합격도 G1 마감도 아니다.

## 6. 다음 방향 결정

- INBOX 2026-10-07 19:3x 사용자 지시가 "H-OS2 뒤 다음 middle이 사전등록"으로 HD 그림 경로를 G1 다음 작업으로 정했다. 그래서 GDI 글자 잔여(PS5 지도 목록 복사 writer 귀속)는 **backlog**로 내린다. 근거·좌표는 §3에 있어 나중에 바로 이어 갈 수 있다.
- **함께 처리 항목**(`SYW2_G1_DEFAULT_ON` 저장소 반영, 사용자용 빌드에서 `sfx_probe_live_units` 등 진단 기본 끔)은 ③ HUD 패널 시범(첫 사용자용 빌드가 바뀌는 단계) 전에 별도 work 1회로 한다. ①은 게임 DLL을 건드리지 않는 순수 도구라 섞지 않는다(한 바퀴 한 변경).

## 7. 가능성 판정(①) — `FEASIBLE`

읽기 전용 헤더 census(`feas_lap1156.json`, 게임 디렉터리 `[ESL]Syw2plus`, 쓰기 0):

- `.spr` 2,917개: version 9·RLE 2,748, 무압축(총 크기 = 시트 w×h) 152, 시트 크기 0/부족(정사각 격자 대체) 16, 0xBF4보다 짧은 파일 1(`temp.spr` 추정). 프레임(≤300 상한) = char 20,598·Online 91,145·fnt 5,843·yfnt 365·tile 119·BattleSpr 99·ybriefingfnt 36.
- `.ytl` 425개(tile, 16,312 프레임 하한), 그중 **frame count > 300이 5개** — 오프셋 표(0x4C0) 길이와의 관계를 ①에서 확인해야 한다.
- `.bmp` 32개: 8비트 27·24비트 5. 팔레트 `pal/imjin2.pal` 768 B(6비트 VGA RGB, SHA256 `5ba2c020e9bd…`), 같은 폴더에 `00~11.pal`·`night*.pal`·`initmenu.pal` 등 38개.
- 리터럴 0xFE(`FE 00`)가 있는 RLE `.spr`은 Online 2개뿐.
- 참고 구현(RE 저장소, 읽기 전용): `plan_c/src/asset/formats/spr_loader.cpp`(헤더 4×u32, 오프셋표 0x4C4·크기표 0x970·시트 레코드 0xBC8·픽셀 0xBF4, 시트 격자 배치, RLE `FE n` n≠0 = 투명 n개·`FE 00` = 리터럴 0xFE, 총 크기 = w×h면 무압축), `ytl.cpp`(오프셋표 0x4C0, 프레임 = 행마다 `[skip u8][count u8][count 바이트]`), Python `tools/parsers/{spr_parser,ytl_parser,pal_parser}.py`. **주의: 투명 인덱스가 RE 안에서도 불일치**(`spr_loader.h` 0 vs `spr.h` 0xFE canonical) → 사용자 지시 "투명은 `0xFE` 런만"에 맞춰 **실루엣 = RLE 투명 런**으로 정의하고 인덱스 값으로 추정하지 않는다.
- 저장소 상황: 패치 저장소에 자산 추출 도구·`.pal` 리더 없음. HD 팩 소비 경로는 `g1_mirror2x.c` `SYW2_G1_HD_PACK`(`:79`·`:750`) → `panel_load_hd_pack`(`:3404-3442`), 키 `g1_panel_layer.h:24-57` `w%08x_s%08x_h%08x_831x<h>.idx8`(헤더 없는 2w×2h 인덱스, 원본 0xFE ↔ 2×2 전부 0xFE). venv numpy 2.4.3·Pillow 12.1.1 있음(이미 27개 도구가 사용).

## 8. 다음 work 사전등록(Sonnet) — H-HDX1: 원본 그림 추출 도구 (HD 그림 경로 ①)

**목표.** 게임 원본 `.spr`·`.ytl`·8비트 BMP를 **읽기 전용**으로 풀어, 사용자 사양("Syw2plus HD 스프라이트 사양", INBOX 19:3x 요지: 8비트 인덱스 PNG·`imjin2.pal`·정확히 2w×2h·투명 254·실루엣 2×2 일치·팀색 236~239·경로 `hd/<원본 상대경로>/<프레임4자리>.png`)에 맞는 **외부 업스케일러 입력과 기준 초안**을 만든다. 게임 DLL·EXE·하네스는 바꾸지 않는다.

- **산출 도구:** `tools/g1_hd_extract.py`(+ `tests/test_g1_hd_extract.py`, `Makefile` typecheck 목록에 추가). 순수 Python + numpy·Pillow. 입력 경로 인자(기본 `[ESL]Syw2plus`), 출력 경로 인자(필수; 저장소·게임 폴더 안이면 거부). 원본은 `rb`로만 연다.
- **출력(파일 하나 = 디렉터리 하나, `<out>/<원본 상대경로>/`):** 프레임마다 `NNNN.png`(1배 인덱스 PNG, 팔레트 `imjin2.pal`, 투명 화소는 254), `NNNN_mask.png`(1배 1비트 실루엣, 1=불투명; RLE 투명 런만 0), `NNNN_2x.png`(Scale2x 2배 초안 인덱스 PNG, 투명 254, 실루엣 2×2 일치) + `manifest.json`(원본 SHA256·포맷 분류 rle/raw/fallback/ytl/bmp·fw·fh·fc·프레임별 불투명 화소 수·팀색 236~239 화소 수·리터럴 0xFE 수·경고). 6비트→8비트 팔레트 변환식은 하나를 정해 manifest에 적는다(RE `pal_parser` ×4 참고).
- **범위:** 기본 실행 = `char`·`tile`(.spr·.ytl)·`BattleSpr`·`portrait`(8비트 BMP)·`pal`. `Online`(91k 프레임)·글꼴(`fnt`·`yfnt`·`ybriefingfnt`)은 manifest만(이미지 옵션). 무압축 `.spr` 152개는 투명 런이 없으므로 `mask_source: "raw_all_opaque"`로 표시하고 경고 목록에 넣는다(엔진이 무압축 시트의 0xFE를 투명으로 쓰는지는 UNKNOWN — 추측 금지). 24비트 BMP 5개는 건너뛰고 목록만.
- **측정식(전부 PASS여야 PASS):**
  - X-1 census: 범위 안 모든 파일을 예외 없이 분류(실패는 파일·사유와 함께 0개이거나 명시 분류). `.ytl` fc>300 5개의 실제 프레임 수 결정 근거를 기록.
  - X-2 교차 검증: RE Python 파서(`Syw2plus_re/tools/parsers/spr_parser.py`·`ytl_parser.py`, 읽기 전용 경로 import 또는 별도 프로세스, 투명값 매핑만 맞춤)와 **무작위 고정 시드 ≥30 파일**(rle·raw·fallback·ytl 각 ≥3)에서 프레임 인덱스 배열이 화소 단위 일치. 불일치는 원인 분류(RE 쪽 결함이면 근거와 함께 공개).
  - X-3 왕복: RLE `.spr` ≥10개에서 1배 인덱스+마스크를 같은 규칙으로 다시 RLE 인코딩하면 원본 픽셀 데이터 바이트와 같거나, 다르면 그 차이(인코더 선택 차이)를 분류해 공개.
  - X-4 2배 초안 규칙: 모든 출력 `_2x.png` 크기 = 정확히 2w×2h·모드 P·팔레트 = `imjin2.pal`, 마스크 2×2 일치 위반 0, 불투명 화소는 투명 254를 쓰지 않음. Scale2x는 엔진 `g1_scale2x_core.h`와 같은 규칙(테스트 벡터로 고정; 가능하면 기존 `tests/test_g1_scale2x_mask.py` 방식처럼 C 핵심과 대조).
  - X-5 결정성: 같은 입력 두 번 실행 시 manifest·PNG SHA 동일.
  - X-6 열람: char 유닛 1개·`.ytl` 지형 1개·초상화 1개 접촉 시트(1배·마스크·2배)를 공유 temp에 저장하고 직접 본다(색·투명·방향 정상).
  - 원본 보호: 실행 전후 게임 디렉터리 전체 파일 목록·크기·mtime(+ 범위 안 파일 SHA256) 불변.
- **테스트(TDD):** 합성 바이트로 RLE(`FE n`·`FE 00`·무압축·격자 대체), `.ytl` 행 레코드, 팔레트 변환, Scale2x 벡터, 마스크 2×2, 출력 경로 거부를 RED→GREEN. 실제 게임 파일을 읽는 테스트는 파일이 없으면 skip(기존 pinned 관례).
- **한계·비목표:** 업스케일러 실행·양자화·팀색 재적용·`.idx8` 생성은 ②, 엔진 적용은 ③ 이후다. 출력은 저장소 밖 공유 temp `temp/Syw2plus_patch/<날짜>_lap<N>_work_hdx1/`(용량 기록; 디스크 여유 ≥20GiB 유지, 현재 50G).
- **중단:** 실패 가설 2회 또는 60분이면 멈추고 근거를 남긴다. 원본/참고 쓰기·커밋·`260921_temp` 금지. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).

backlog 추가: PS5 지도 목록 스크래치→화면 복사 writer 귀속(§3 좌표, 정황 = 줄 너비 9/9 대응), PS5 화면 DC 사각형 안 잔여 156 블록 writer. 기존 backlog(STATUS)는 유지한다.

## 9. 검사

- 결과는 STATUS 검증 줄에 보강한다(safety·context·focused).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. C·하네스·테스트 source는 lap1155 full PASS 1847 그대로다(§1).

## 다음 행동

work(Sonnet) H-HDX1(§8). 사용자 G1 시험 결과가 오면 최우선이다.

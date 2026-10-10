# 2026-10-07 | lap1165 | G1 work — H-HDL1 ④-1 포인터 없는 HD 팩 로더 (A/B writer + 패널 키 `s` 제거)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). 세션이 2026-10-07 23:3x KST에 시작해 10-08로 넘어가며 끝났다. 커밋 0.
- 입력: lap1164 middle 사전등록 §4(`20261007_lap1164_middle_g1_hdp1_review_hdl1_preregistration.md`). `loop/STOP`·새 반려·사용자 G1 시험 결과 없음(INBOX·APPROVALS 확인).
- 가설: A/B writer(`0x466D50`·`0x4664D0`)의 source 포인터는 원본 `.spr` 프레임 스트림 시작이므로, 키에서 포인터를 빼고 `(digest, w, h)`로 파일을 찾으면 run과 무관하게 같은 HD 그림이 적용된다.
- 예상 PASS/FAIL: 사전등록 §4 측정식 그대로 — L-0 오프라인 충돌, L-1 대응 ≥80% FEASIBLE(<50% BLOCKED), L-2 두 run(rejects 0·크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x 바깥 diff 0·PS3 HD min ≥99.9·p95 ≤9 ms·hits ≥ 대응 키의 90%·lookup_blocks >0·뜬 패널 loaded 1), L-3 크롭 열람.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 MATCH(`orig_sha_before/after.txt`). 환경: 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --new-game-path --new-game-start --new-game-act --hd-source scale2x`(lap1161 D-4·lap1163과 같은 NG5 장면), 활성 8 player records(부하 증명 아님), 새 임의 게임, fixture = 하네스 새 게임. 팩·키 로그만 바깥 env(`SYW2_G1_HD_PACK`·`SYW2_G1_HD_KEY_LOG`)로 추가.

## 변경 (모두 uncommitted, SHA256은 공유 temp `changed_sha.txt`)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_hd_pack.h` (신규) | 순수 헤더: `g1_hd_pack_name`(`h<digest8>_<w>x<h>.idx8`)·`g1_hd_pack_valid`(2w×2h, 쓴 화소 2×2 전부 불투명·안 쓴 화소 2×2 전부 0xFE) |
| `tools/inmm_stub/g1_hd_asset.c/.h` | `SYW2_G1_HD_PACK`(+진단 `SYW2_G1_HD_KEY_LOG`) 읽기. `build_hd_frame`: aux 없는 키 → 팩 파일 1회 읽기·검증, 통과하면 Scale2x 대신 사용, MISS/REJECT면 기존 Scale2x. 키별 `pack_state`로 첫 시도만 계수(재적재는 HIT 키만 파일 재읽기). 카운터 `hd_pack_hits/misses/rejects/skipped_aux/lookup_blocks`, 키 로그(키당 첫 줄 + draw 이정표 1,2,4,8…·이후 64번째마다 + `src` 포인터) |
| `tools/inmm_stub/g1_panel_layer.h`·`g1_mirror2x.c` | 패널 키에서 `s<포인터>` 제거 → `w004663e0_h<digest8>_831x<h>.idx8`(`g1_panel_asset_key`가 포인터 인자 삭제) |
| `tools/inmm_stub/direct_draw_trace.c` | trace JSON에 `hd_pack_*` 6개 필드(보조 버퍼 200자; 하네스 `counter_span`이 `*reject*` 이름을 자동 추적) |
| `tools/g1_hd_convert.py` | `pack` 서브명령(`--dry-run`·`--hd-dir/--ref`·`digest_index.json`·`conflicts`). 이름 충돌은 1x 그림 불일치(HD 유무 무관, 모든 프레임이 참여) 또는 HD 불일치일 때만 쓰지 않음. 831폭 패널 프레임은 패널 이름·앞 1600열 |
| `tests/test_g1_hd_pack.py` (신규) | 호스트 gcc 7개: 헤더(이름·크기·실루엣 거절·로더 배선 3개) + 실제 `g1_hd_asset.c`를 호스트 컴파일해 HIT(팩 픽셀 4블록·`lookup_blocks`)·MISS(Scale2x)·REJECT(크기 불일치·실루엣 구멍)·aux 키 건너뜀 4개 |
| `tests/test_g1_mirror2x.py` | 호스트 `windows.h` shim에 stdio 기반 파일 API(`CreateFileA`·`ReadFile`·`WriteFile`·`GetFileSize`·`CloseHandle`·`wsprintfA`·`lstrlenA`·`lstrcpyA`·`MAX_PATH`…) 추가 — 새 로더가 컴파일되도록(기존 단언 변경 0) |
| `tests/test_g1_hd_convert.py` | pack 테스트 7개 추가(이름·오프라인 digest, dry-run 충돌 제외, 바이트 일치 기록, 충돌 판정이 HD 없는 프레임 포함, HD 불일치 충돌, 패널 이름·크롭, 출력 경로 안전) |
| `tests/test_g1_panel_layer.py` | 패널 키 계약(`w004663e0_h12345678_831x143.idx8` 정확 문자열) |

도구 테스트는 구현 뒤에 썼다(헤더 테스트는 RED 선행 실행 없음 — 공개).

## 측정

- **L-0 오프라인(`pack --dry-run`, 원본 `.spr` 직접 계산):** 기본 4개 폴더(char·tile·BattleSpr·portrait) RLE `.spr` 245파일·20,784프레임(사전등록의 37,905는 `.ytl` 17,062프레임·BMP까지 포함한 추출 수치라 이 도구 범위 `.spr` RLE와 다름 — 공개) 중 이름 부여 20,767·고유 이름 15,831·**충돌 이름 271·충돌 프레임 2,702(13.0%)**·tail 짧음 17·비RLE 32. 실제 장면에 나오는 UI까지 넓힌 폴더(fnt·yfnt·char·tile·BattleSpr·Online·ybriefingfnt·eft·portrait) 117,909프레임·이름 117,786·고유 88,477·충돌 이름 2,975·충돌 프레임 22,747(19.3%). **패널 3장 digest = 런타임 키 재현**: c `2aa149c7`·k `a3216fad`·j `5939fabc`.
- **L-1 키 조사(run L1, 팩 없음, 키 로그):** 원장 키 572개(고유 digest 튜플 369). A/B aux 없는 고유 키 100개 → 대응 **90(90.0%)**·충돌 5·미대응 5; 원장 키 기준 93/110 = **84.5%**. 독립 C 전수 스캔(`scan.c`, 모든 `.spr/.ytl/.bmp` 모든 오프셋)으로도 A/B 100키 중 95개가 프레임 시작 오프셋·같은 크기에서 일치(Python 이름 계산 교차 확인). **판정 FEASIBLE(≥80%).** 키 구성: A/B aux 없음 100(UI `fnt`·`yfnt` 스프라이트), tinted writer(aux) 205(`0x466540`·`0x466EA0`·`0x468CC0`·`0x4690A0`), 지형 aux 없음(`0x468C30`·`0x468F00`) 64(`.ytl`, 이번 도구 범위 밖).
- **L-2 팩 적용 run(공유 temp `20261007_lap1165_work_hdl1/`; B형 = 원본 1x 팔레트 RGB → 바이큐빅 2배 → `convert` → `pack`, 1,370프레임 변환 위반 0, 팩 618개):**

| run | 팩 | PS3 HD min | p95 ms | 안전 7종 | fallback/dropped | hits/misses/rejects | lookup_blocks | 패널 | matched 키 hit 비율 |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 패널 파일 없음 | 99.973 | 7 | 0 | 0/0 | 93/83/0 | 30,830,650 | c 뜸·loaded 0(파일 없음) | 93/93 = 100% |
| P2 | 패널 파일 없음 | 100 | 6 | 0 | 0/0 | 93/82/0 | 30,615,208 | c 뜸·loaded 0 | 93/93 = 100% |
| **P3** | 패널 3장 포함 | 100 | 6 | 0 | 0/0 | 97/90/0 | 28,482,774 | **j loaded 1** | 97/106 = **91.5%** |
| **P4** | 패널 3장 포함 | 100 | 7 | 0 | 0/0 | 94/89/0 | 29,551,552 | **j loaded 1** | 94/103 = **91.3%** |
| P5(최종 소스, `src` 로그) | 패널 3장 포함 | 99.949 | 7 | 0 | 0/0 | 89/89/0 | 29,635,959 | **j loaded 1** | 89/98 = **90.8%** |
| N1(대조, 팩 없음·최종 아님) | — | 99.949 | 7 | 0 | 0/0 | 0/0/0 | 0 | c 뜸·loaded 0 | — |

  전 run `scale2x_validator` PASS(`hd_mask_outside_diff` 0 = 실루엣 밖 변화 0)·`identity_invalid_sources` 0·크래시 0·원본 SHA MATCH. 합격 판정 = P3·P4(사전등록 "패널 포함 2 run"); P5는 최종 소스 재확인. `mirror_validator` BLOCKED(nearest oracle)는 lap1161 D-4·lap1163과 같은 NG5 공통 성질(공개 유지).
  - hit 못한 matched 키(P3 9개)는 전부 `fnt/pannelflag.Spr`(깃발 패널 138×108) — L1에서 안 보인 프레임이라 HD를 안 만들었기 때문이며 기술 결함 아님. 충돌 키 8·미대응 7은 팩이 없는 것과 같이 Scale2x로 정상 폴백(rejects 0).
  - **그리기(draw) 기준(P5, 키 로그 이정표 합):** A/B aux 없음 93,994 draws 중 대응+hit **76,552 = 81.4%**·충돌 1,954(2.1%)·미대응 14,912(15.9%, 아래 구조적 공백). aux 있는 tinted writer draws 122,837·지형 aux 없음 900 — 전체 draws 중 팀색(tinted) 계열이 압도적(④-2 판단 자료).
  - **포인터 독립 직접 증거:** P5 원장 키 중 같은 팩 이름이 서로 다른 source 포인터 2개 이상으로 hit된 이름 3개(`src` 로그). 패널은 포인터 없는 이름으로 j loaded 1 3회(P3·P4·P5). 두 run 사이 같은 패널의 포인터 변동은 P3·P4에 `src`가 없어 별도 측정 못 함(공개).
  - 미대응 5고유 키 = 16×1(`yfnt/scrollbar.spr` 다른 크기 프레임 시작 위치)·16×5(`Online/TILE/151/d-h01.spr` 스트림 중간 오프셋)와 raw 배치 `.spr` 3개(`pannel_gamemenu2` 68×22·`lobbynumbutton` 44×27·`mapformatinfo` 92×25; 추출기가 raw로 분류, 엔진은 RLE writer로 그림). 충돌 5고유 키 = 앞 128 B가 같고 뒤가 다른 버튼 프레임(34×34·84×80·80×76) — digest로 구분 불가. 둘 다 이번 범위의 알려진 한계.
- **L-3 크롭(공유 temp `crops/`, 위=대조 N1(Scale2x), 아래=팩 run):** `topbar_p2.png`(상단 자원 줄: 아이콘·숫자가 바이큐빅으로 눈에 띄게 부드러워짐, 실루엣·위치 동일), `hud_left_p3.png`·`hud_right_p3.png`(하단 HUD: 패널 j 포함 F1~F11 상자·설정 버튼·명령 칸 정상 렌더, 미니맵 구멍·테두리 손상 없음. 패널은 run마다 c/j로 달라 같은 픽셀 대조는 불가 — 판별은 `panel_hd_pack_loaded`·키 로그로). 육안상 깨짐·번짐 외 이상 없음. 업스케일 화질 평가 아님(바이큐빅 스탠드인).

## 판정

**H-HDL1 `PASS(partial, 기술·격리)` — L-1 FEASIBLE, L-2 P3·P4·P5 전 항목 충족.** 한계: (1) 범위 A/B aux 없는 UI 스프라이트뿐(전체 draws의 약 43%; 팀색·지형·유닛·효과 미적용), (2) 앞 128 B digest 충돌 프레임 13~19%·부분 높이·스트림 중간·raw 배치 미대응 draws 15.9%, (3) 바이큐빅은 업스케일러 stand-in, (4) 사용자 합격·기본 켬·전달 아님, (5) P1·P2는 패널 파일 없는 run(참고용), (6) 키 로그 `src`는 P5에서만.

## 검사

- `make lint`·`make typecheck` PASS. 목표 테스트: `tests/test_g1_hd_convert.py`·`test_g1_hd_pack.py`·`test_g1_panel_layer.py`·`test_g1_hd_extract.py`·`test_g1_mirror2x.py` 통과. 첫 전체 `make check`는 1 failed·1900 passed(`test_g1_mirror2x.py::test_hit_compare_is_limited_to_the_renderer_viewport_with_host_gcc` — 그 테스트가 실제 `g1_hd_asset.c`를 가짜 `windows.h`로 호스트 컴파일하는데 새 로더의 파일 API가 shim에 없었음, 로그 `logs/gates/lap1165-work-full-check-run1-fail.log`) → shim 수정 + 새 로더 행동 테스트 추가 뒤 재실행. 최종 전체 `make check`는 STATUS 검증 줄에 보강한다.
- 컴파일: 변경 C 3개(`g1_hd_asset.c`·`g1_mirror2x.c`·`direct_draw_trace.c`) `i686-w64-mingw32-gcc -Wall -Wextra` 경고 0, 하네스가 매 run 전체 DLL을 이 소스로 빌드.
- 디스크: 여유 27 GB(≥20). 런타임 `local/runtime/lap1165_hdl1_*` game 사본은 하네스 정리로 삭제, prefix·manifest·output 보존.

## 다음 행동

middle(Opus) 독립 검수 → ④-2 선택. 검수 항목: (a) `g1_hd_asset.c` 팩 경로(`read_pack_frame` 크기·실루엣 검증, `pack_state` 재적재 규칙, 카운터), (b) L-1/L-2 수치 재계산(키 로그 `run_*.keys.jsonl`·`digest_index.json`·trace), (c) 충돌 이름 규칙(1x 그림 불일치 = 128 B digest 충돌)과 `pack` 도구, (d) 크롭 직접 열람, (e) ④-2 후보: tinted writer 팀색 재적용(draws 최다) vs 지형 normal 테마(`.ytl`, aux 없는 `0x468C30` 계열 64키·draws 900). 사용자 G1 시험 결과가 오면 최우선.

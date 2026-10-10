# 2026-10-07 | lap1164 | G1 middle — H-HDP1 독립 검수 · H-HDL1(④ 일반 HD 그림 로더 첫 단계) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1163 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261007_lap1164_preserved_lap1163_escalate_sol.txt`(SHA256 `5fe25f439a62ac1e…`), 보존 뒤 삭제. `loop/STOP` 없음, APPROVALS 새 반려·사용자 G1 시험 결과 없음.
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ③(HUD 패널 시범) 검수, ④ 사전등록.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 원본 `fnt/pannel{c,k,j}.spr` 읽기만(`4b7cf7f9…`·`941036da…`·`ca59e697…`).
- 후보 source: `tools/g1_hd_convert.py` `9b272579…`·`tests/test_g1_hd_convert.py` `3ea2abc1…`(둘 다 미추적 신규, 22:55 수정). lap1163 full check(1891 passed, 로그 23:23) 뒤 바뀐 tools·tests·patches·checks·Makefile 파일 0(`find -newer`).

## 1. 독립 재계산 (work `p0.py`·`p2.py`·`p2b.py` 미사용)

공유 temp `20261007_lap1164_middle_review/recalc_hdp1.py`(`270f15d3…`) → `recalc_hdp1.json`(`be8a4f99…`). 원본 `.spr`를 직접 읽어 RLE 시작 오프셋을 **전수 탐색**(12..4095 중 끝까지 정확히 소비하는 오프셋)하고, 엔진 `g1_panel_build_scale2x`(키 보존 규칙 포함)를 numpy로 다시 구현했다.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| RLE 시작·엔진 digest | `.spr` 오프셋 3060 앞 128 B FNV-1a = k `a3216fad`·c `2aa149c7`·j `5939fabc` | 세 패널 모두 정확 소비 오프셋은 **3060 하나뿐**, digest 3개 일치. 디코드 영상 앞 128 B digest(`4ab644cf` 등)는 런타임 키와 다름 | 일치 |
| 트레이스 프레임 SHA | c `0137064a`·k `c7aaf198` = `.src` 앞 800열 | 9 run(none·A·B·D·E·G·H·I·J) 전부 `panel_frame_sha256` = 디코드 앞 800열 SHA(c·k·j 3종), 투명 건너뛰기 순차 겹쳐쓰기 모형 SHA는 0/9 | 일치 |
| 옛 팩 거절 원인 | 831폭 크기 불일치 | packA·B·D 파일 541,812/531,840 B ≠ 엔진 기대 521,600/512,000 B — 크기만으로 거절이 설명됨 | 일치 |
| 새 팩 유효성 | 6개 유효 | packA2·packB2 16개 파일(실제 사용분 포함) 크기 = 800·h·4, 독자 실루엣 검사 16/16 유효. A(team-safe) vs 엔진 Scale2x 차 k 98·c 79·j 64 HD 화소, B vs Scale2x k 111,366·c 106,469·j 106,140 | 일치(정정 1) |
| 적재 | H(k·B)·J(j·A) loaded 1 | 트레이스 직접: H key `s07b65628_ha3216fad_831x163` loaded 1·J key `s07bdc5f8_h5939fabc_831x143` loaded 1, 나머지 7 run 0. H·J `panel_key_subpixels_emitted`·lock·pointer·pitch 0. H 결과 JSON: 창 4개 HD min 99.936~100·safety_max 7종 0·fallback 0·p95 6~7·dropped 0·scale2x validator PASS(바깥 diff 0) | 일치 |
| P-2 색 대응(k, 기준 run D, 대상 run H, y0 874) | 0.9816·0.9793·0.9776 | 같은 방식(팩 없는 캡처에서 Scale2x 인덱스별 최빈 RGB 표, 160 인덱스·표 일치 0.86): 선택 94,607·92,426·91,587 px에서 **H=B색 0.9819·0.9795·0.9778**. 판별력 대조: 같은 화소에서 **H=A색 0.009~0.013**, **팩 없는 D=B색 0.000** | 일치(차 ≤0.0003, 선택 집합 정의 차) |
| 비판별 수치 | 영역 변경 98,238~102,019 vs 잡음 99,785~116,857 | 동일 값 재현 | 일치 |
| P-4 포인터 | 표 | 9 run 키 직접 추출로 표 그대로 재현. 추가: 포인터 `07bdc5f8`이 **서로 다른 패널(k: run A, j: run I·J)에 재사용**됨 → 포인터는 패널 식별에도 쓸 수 없다 | 일치·보강 |
| 도구 수리 | `PANEL_ENGINE_WIDTH=800` crop | 코드 검토: `panel_idx8`은 검사(831폭 전체) 통과 뒤 `[:, :1600]`만 기록, 보고 `width`·`source_width` 정확. 테스트는 805폭 입력으로 1600열만 남는지 byte 확인 | 결함 없음 |
| 테스트 | 17 passed | `tests/test_g1_hd_convert.py`+`test_g1_hd_extract.py` **38 passed/0.88s**(`logs/gates/lap1164-middle-focused.log`) | PASS |

**판정 영향 불일치 0. 정정 2·공개 2:**
1. (정정) P-3 "j의 A는 Scale2x와 동일, 차 0 px"는 틀렸다. 엔진 Scale2x 대비 A(j)는 **64 HD 화소** 다르다(k 98·c 79, 모두 team-safe 규칙 차). P-3은 기준이 아니라 판정 영향 없음.
2. (정정) §1 "strace에서 적중 키 openat 성공(fd 90)"의 raw(`strace_G.txt`)가 공유 temp에 남아 있지 않아 재현할 수 없다. 거절 원인은 크기만으로 설명되고 적재 경로는 H·J loaded 1로 직접 입증되므로 판정 영향 없음.
3. (공개) 하네스 `mirror_validator`는 lap1163 NG5 9 run과 lap1161 D-4 모두 `BLOCKED`(nearest oracle 0.776)다 — NG5 장면 공통 성질이며 팩 때문이 아니다. H만 0.756으로 낮은 것은 B 팩이 Scale2x에서 멀어진 기대 효과다. work 기록은 이 항목을 언급하지 않았다.
4. (공개) `imjin2.pal×4`가 화면 RGB와 맞지 않는 것(일치 0.20)은 재현했다(표 방식은 수용). 화면 팔레트가 파일 팔레트보다 어두운 원인(게임 밝기/감마 처리)은 UNKNOWN — 업스케일러 결과를 RGB로 평가할 때 화면 팔레트 기준이 필요하면 별도 확인.

## 2. 판정

**H-HDP1 `PASS(partial, 기술·격리)` 수용.** ③ 시범 목표(기존 패널 경로로 업스케일러형 팩이 화면까지 전달됨)를 재계산으로 확인했다. 사전등록의 831폭·`.src` digest 가정 오류는 middle(lap1162) 사전등록 결함이며 work가 근거와 함께 정정했다(수용). c 패널 팩 적재는 미관측(공개 유지). 업스케일 화질·사용자 합격 아님.

## 3. ④ 설계 근거(정적, 이번 회차)

- 일반 경로 `g1_hd_asset.c`: 키 = (source 포인터, writer, aux 포인터, aux digest, w, h, source 앞 128 B FNV-1a), 상한 4096 키·캐시 128 MiB. 호출자는 `g1_mirror2x.c:3105` 하나 — writer A `0x466D50`(rle_clip)·B `0x4664D0`(rle_plain)만 이 경로를 탄다. identity frame = 원본 primitive가 scratch에 그린 1배 결과, `build_hd_frame`(`--hd-source scale2x`)이 Scale2x를 만든다. 파일 조회 없음.
- 패널과 같은 문제: 키에 런타임 포인터가 들어간다. 패널에서 digest(데이터 앞 128 B)는 파일에서 오프라인 계산 가능하고 run 사이 안정이었다(P-0·P-4).
- 범위 판단: A/B는 색 변환 없는 RLE writer라 HD 인덱스를 그대로 쓸 수 있다. 팀색(`0x466540`/`0x466EA0` tinted)·지형(`0x468C30` 계열, 음영 LUT)은 별도 경로라 ④ 첫 단계에서 빼고 ④-2로 둔다. 추출 manifest(lap1157 run1)에는 프레임별 스트림 오프셋이 없으므로 도구가 계산해 기록해야 한다.

## 4. 다음 work 사전등록(Sonnet) — H-HDL1: ④-1 포인터 없는 HD 팩 로더(A/B writer + 패널 키 `s` 제거)

**가설.** A/B writer의 source 포인터는 원본 그림 파일의 프레임 스트림 시작을 가리키므로, 키에서 포인터를 빼고 `(digest, w, h)`로 파일을 찾으면 run과 무관하게 같은 HD 그림이 적용된다.

**변경(최소).**
- C `g1_hd_asset.c`: `SYW2_G1_HD_PACK`(패널과 같은 env)이 있고 `aux == NULL`인 키는 `build_hd_frame`에서 `<dir>\h<digest8>_<w>x<h>.idx8`(2w×2h B, 행 우선, 투명 0xFE)를 1회 읽는다. 크기 = 4·w·h 정확, 실루엣 = `identity_written==0` ⇔ 2×2 모두 0xFE, 쓰인 화소의 2×2에 0xFE 없음 — 통과하면 Scale2x 대신 사용, 아니면 기존 Scale2x(동작 동일). 캐시 한도·키 상한 그대로. 계수: `hd_pack_hits`·`hd_pack_misses`·`hd_pack_rejects`·`hd_pack_skipped_aux`·`hd_pack_lookup_blocks`(팩 프레임에서 나온 2×2 조회 수). 키 첫 삽입 때 trace 이벤트 1건(`writer`·`w`·`h`·`digest`·`aux`·결과), 4096 상한.
- C 패널: 파일 이름에서 `s` 필드 제거 → `w004663e0_h<digest8>_831x<h>.idx8`. trace `panel_asset_key`도 같은 이름.
- 도구 `tools/g1_hd_convert.py pack <hd_dir> --ref <추출 run> --out <pack_dir>`: 각 HD PNG 프레임의 원본 스트림 오프셋을 원본 파일에서 계산(추출기 디코드와 같은 규칙, manifest에 기록)해 앞 128 B FNV-1a로 이름을 만든다. 같은 이름에 다른 내용이 둘 이상이면 그 이름은 쓰지 않고 충돌 목록에 남긴다. `digest_index.json`((digest,w,h) → [(file, frame)]) 출력.
- 테스트(RED→GREEN): 이름 형식·크기·실루엣 거절(호스트 컴파일 또는 기존 C 테스트 방식), `pack` 충돌 제외·오프셋·이름. 원본 경로 쓰기 거부는 기존 `_assert_outputs_safe`.

**측정식.**
- L-0(오프라인): lap1157 run1 전체(렌더 37,905 프레임)에 `pack --dry-run`(이름만) → 고유 키 수·충돌 이름 수·충돌 프레임 비율 기록. 패널 3장 digest = 런타임 키(`a3216fad`·`2aa149c7`·`5939fabc`) 재현.
- L-1 키 조사(팩 없음): NG5 장면(`--new-game-path --new-game-start --new-game-act --hd-source scale2x`) 1 run → A/B 키 이벤트 전부를 `digest_index`에 대응. **실행 가능성 판정:** aux 없는 키 중 대응 비율 ≥ 80%(키 기준, 그리기 이벤트 기준도 기록)면 `FEASIBLE`, 50% 미만이면 `BLOCKED(식별자)`로 L-2 없이 종료하고 미대응 키 표본(writer·w·h·digest)을 남긴다. 팩 없는 run은 lap1163 run D와 같은 지표(HD min·안전 0·p95)여야 한다(비회귀).
- L-2 적용(B형): L-1에서 대응된 프레임만 바이큐빅 2배 → `convert` → `pack`으로 팩 생성(패널 3장도 새 이름으로 포함). NG5 run 2회. 합격 = 두 run 모두 `hd_pack_rejects` 0·크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator 바깥 diff 0·PS3 HD min ≥ 99.9·p95 ≤ 9 ms(lap1161 6 + 3), `hd_pack_hits` ≥ (그 run에서 관측된 대응 키 수)의 90%, `hd_pack_lookup_blocks` > 0, 뜬 패널 `panel_hd_pack_loaded=1`. 두 run의 패널 포인터가 다르면 그대로 기록(포인터 독립 직접 증거), 같으면 공개.
- L-3 열람: 팩 적용·미적용 PS3 캡처에서 팩 적중 키가 그려진 영역(trace 좌표 또는 패널) 크롭을 공유 temp에 저장(middle이 직접 본다). 화면 RGB 판정이 필요하면 lap1163 P-2 표 방식을 재사용.
- 원본 보호: 원본 EXE·그림 파일 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- **비목표:** tinted writer(팀색)·지형 `0x468C30` 계열(음영)·유닛 `0x466B50`·효과, 기본 켬 빌드 env 추가·사용자 전달, 업스케일 화질 평가, 팩 저장소 반입, 메모리 대책(필요 시 로드는 이번 구조가 이미 키 첫 사용 때 로드).
- **중단:** 실패 가설 2회 또는 60분. `BLOCKED(식별자)`면 C 로더를 넣지 말고(또는 되돌리고) 근거만 남긴다. 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdl1/`. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ④-2 지형 normal 테마(`0x468C30` 계열 경로, 음영 LUT 재적용) 또는 tinted writer 팀색 재적용 — L-1 키 분포를 보고 middle이 고른다. backlog: lap1160 중복 RGB 쌍(182·183·54·203) 정적 확인, `g1_r5_combo_probe.py` prefix 보존 옵션, 화면 팔레트 어두움 원인(공개 4).

## 5. 검사

- SAFETY·CONTEXT 결과는 STATUS 검증 줄에 보강한다. focused 38 passed(§1).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1163 full PASS(1891 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDL1(§4). 사용자 G1 시험 결과가 오면 최우선이다.

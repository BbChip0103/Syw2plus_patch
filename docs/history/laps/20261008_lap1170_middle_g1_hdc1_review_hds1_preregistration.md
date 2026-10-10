# 2026-10-08 | lap1170 | G1 middle — H-HDC1 독립 검수 · H-HDS1(④-4 음영 지형 HD 팩) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1169 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1170_preserved_lap1169_escalate_sol.txt`(SHA256 `95f4dd57a27702c3…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 9.6 GB(게임 실행 안 함; 다음 work는 실행 전 20 GB 규칙 확인 필요).
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ④-3 검수, ④-4 사전등록. ESCALATE_SOL의 "마일스톤 경계"는 ④ 하위 단계 전환이라 DESIGN 마일스톤 경계가 아니다(④-1→④-2→④-3도 middle이 처리).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 원본 그림·EXE는 읽기만(`objdump`).
- 후보 source(uncommitted): `tools/inmm_stub/g1_hd_asset.c` `b2876689781bd67d`·`g1_hd_asset.h` `fc5533f6c3c80377`·`direct_draw_trace.c` `979f0db523255e88`·`tests/test_g1_hd_pack.py` `bf12bb3c5ebf67d4` = work 기록과 일치. lap1169 full check 로그(`055d8cf8…`, exit 0, 1915 passed·5 skipped) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/`·`metrics_*.json` 미사용)

공유 temp `20261008_lap1170_middle_review/`: `recalc_hdc1.py`(`7804a0d7e47d1f77…`)→`recalc_hdc1.json`(`87ff320d634aec4c…`). 키 로그·`trace_raw.jsonl` 직접 집계, 원본 `.spr`를 파일 전 오프셋 FNV-1a(128 B) 스캔 + 새 RLE 디코더로 1x 실루엣 유도 → `pack_c` 2×2 블록과 비교.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| 키 결과 H1/H2 | hits 348/353·miss 31/24·reject 2/2·skip_aux 151/153·lut_hit 187/197 | 같은 값(키 로그 결과 줄 = trace 카운터) | 일치 |
| OFF1·D1·D2·D3 | 152/28/0/342·361/31/2/159·332/24/0/209·358/31/2/150 | 같은 값 | 일치 |
| `lut_rejects`·`lut_key_color`·`lut_nonidentity` | 0·0·= lut_hits | 6 run 모두 같은 값 | 일치 |
| writer별 matched hit | `0x466540` 126/126·136/136, `0x466EA0` 61/63·61/63, A/B·지형 100% | 같은 값(D1 134/134·75/77, D2 88/88·82/82, D3 134/134·72/74) | 일치 |
| PS3 HD min·안전·fallback·dropped | 99.949/100/99.947/100/99.945/100, 0 | 전체 PS3 present 1,533~1,535: 같은 값, 안전 7종·fallback·dropped 0, `identity_invalid_sources` 0 | 일치 |
| PS3 p95 | H1 8·D2 8(창별 최대) | 전체 PS3 기준 H1 7·D2 7(나머지 7/6/7/7) | 정의 차(lap1166과 같음), 모두 ≤9 |
| tinted 팩 실루엣 | (work 미측정) | 6 run의 tinted matched `lut_hit`·`reject` 키 합집합 281개: 독립 디코드 1x 불투명 = 팩 2×2 블록 **281/281** | 새 확인 |
| reject 키 | tree_plus 프레임 0, written 5,257 vs 팩 5,261, 빠진 4 px = 행 104(51·52)·105(52·53) | 파일 오프셋 3060(프레임 0)·1x 불투명 **5,261 = 팩 5,261**, 행 104 이상을 지우면 정확히 **5,257** = 엔진 identity | 일치·원인 확정(아래) |

**정정 1(표현):** work "끔 OFF1 tinted aux 키 342 전부 `skip_aux`" → 342는 aux 키 전체(tinted 196 + 음영 지형 146)다. tinted만 196키가 모두 `skip_aux`, 판정 영향 없음.

## 2. 코드 검토 (`capture_lut`·`build_hd_frame`·테스트)

- 복사 시점: 키 생성 때 256 B를 복사하고 FNV-1a가 primitive hook의 `auxiliary_digest`(같은 256 B, `g1_mirror2x.c:2900`)와 같을 때만 `lut_valid`. 키 동일성에 aux 포인터·digest가 들어 있으므로 표가 바뀌면 새 키가 된다. 복사 직전 표가 바뀌면 `lut_reject`(Scale2x) — 안전.
- refresh: `pack_state == HIT`면 `build_hd_frame`이 팩을 다시 읽어(새 버퍼) LUT를 한 번만 적용 — 이중 적용 없음. 카운터는 `PACK_UNTRIED`일 때만 증가.
- `lut_key_color`: LUT 결과가 0xFE인 불투명 HD 화소 수(첫 HIT 때만). 6 run 모두 0이라 HD 합성의 0xFE 취급은 이번에 판정 대상이 아니다(사전등록 C-2 조건 미발동).
- 끔 env·허용 목록 밖 aux writer → `skip_aux`, 팩 env 없으면 `PACK_NONE`(기본 켬 사용자 판 동작 불변). 결함 없음.
- 테스트 +7(LUT byte·두 writer·0xFE·digest 불일치·miss·끔/다른 writer·trace·reject 상세), 변이 확인 기록 있음.

## 3. reject 키 판정 (ESCALATE 3)

**원인 확정(정적 기전 + raw 정량):** `mirror_tinted_rle`(`0x466EA0`)는 `clipped` 인자로 `tinted_origin_outside_screen()`을 넘기는데, 이 함수는 **화면(800×surface_height) 경계만** 본다(`g1_mirror2x.c:3743`). `0x466EA0`은 안쪽에서 renderer **viewport**로 클립하므로, 화면 안이지만 게임 viewport 아래 경계(HUD 위)에 걸친 스프라이트는 `clipped=FALSE` → 일반 scratch 재호출이 같은 viewport로 잘린 identity 마스크를 만든다(`g1_mirror2x.c:3119`의 전체 viewport 재호출 경로를 타지 않음). 이번 키는 identity = 1x 실루엣에서 행 104 이상만 정확히 빠진 모양(5,261→5,257)이라 수평 절단 하나로 설명된다. 런타임 원점 y는 trace에 없어 미기록(공개).
- 영향: 실루엣 검증이 막아 Scale2x 폴백(이전과 같은 화질), 안전 지표 0. LUT 경로·팩 결함 아님. 이 판단은 lap1169 이전부터 있던 identity 캡처 성질이며 이번 변경이 만든 것이 아니다.
- **판정:** 사전등록 "`hd_pack_rejects` 0"은 미충족이지만 사전등록이 허용한 "0이 아니면 키·원인 기록 후 별도 판정"에 따라 **명시 예외로 수용**. 추가 probe 불필요(정량 일치로 확정). 수리는 backlog: `tinted_origin_outside_screen`이 renderer viewport(`G1_RENDERER_VIEWPORT`)도 보도록 하는 최소 변경(그러면 전체 viewport 재호출 경로로 identity가 온전해짐) — 화면 비중 작음(키 1개·폴백 무해)이라 ④-4 뒤로 둔다.

## 4. H-0 합성 변형 안전 폴백 (ESCALATE 5) — 정정

원본 `0x466540..0x4669C1`의 "변형 6개"는 한 함수의 분기가 아니라 **진입점이 다른 독립 함수 6개**다(`0x466540`·`0x4665C0`·`0x466660`·`0x466710`·`0x4667B0`·`0x466920`, 각각 `ret 0x18`/`0x1c`로 끝남). 후킹은 `0x466540` 진입 8 B(old bytes `51 53 56 57 8B 7C 24 18`)뿐이고 다른 5개는 후킹·키 생성이 없다. 따라서 목적지를 읽는 합성 변형(`0x4667B0`·`0x466920` 계열)이 writer `0x466540` 키로 들어오는 경로는 없다 → work의 "같은 키로 호출되면 실루엣 검증으로 폴백" 가정은 불필요(위험 자체 없음). 공개: 코드 상수 이름이 실제와 반대다 — `G1_TINTED_CLIP_RLE = 0x466540`은 클립 없는 루프, `G1_TINTED_RLE = 0x466EA0`이 viewport 클립판(동작 영향 없음, 이름만).

## 5. 크롭 직접 열람 (ESCALATE 4)

`trees_OFF_top_ON_bottom`: 황금색 나무 군락이 켬(아래)에서 같은 색조·위치, 녹색 덤불 2개도 같은 자리, 질감만 부드러움. `units_OFF_top_ON_bottom`: 건물 오렌지 지붕·**팀색 파랑 타일**이 같은 색·자리. `area3_OFF_top_ON_bottom`: 큰 활엽수 녹색·청록 색조 유지, 황금 나무 유지. 원래 색(치환 전)으로 돌아간 곳 없음, 실루엣 테두리 밝은 띠 없음. work 서술과 같다.

## 6. 판정

**H-HDC1 `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0. 정정 2·공개 4:
1. (정정) OFF1 342 = aux 키 전체(tinted 196).
2. (정정) H-0 "합성 변형 같은 키" 위험 없음 — 독립 함수, 후킹은 `0x466540` 진입만.
3. (공개) `hd_pack_rejects` 2 = tree_plus 프레임 0 한 키, viewport 클립 identity(화면 기준 `clipped` 판정) — 명시 예외 수용, 수리 backlog.
4. (공개) H1·H2는 진단 줄 추가 전 빌드 — 진단은 키 로그 문자열만 추가하고 D1~D3이 같은 결과를 재현하므로 수용.
5. (공개) 상수 이름 반대(동작 영향 없음).
6. (공개) 화질 평가 아님(바이큐빅 stand-in), 팀색 크롭은 건물 1곳·유닛 팀색 미관측, 기본 켬·전달 아님.

## 7. ④-4 선택 근거 (이번 회차)

- **식별자:** lap1169 run의 음영 지형 aux 키 matched(이름 = `pack_c`에 있음) `0x468CC0` 82/88(93%)·`0x4690A0` 58/63~94/115(82~92%), source = `.ytl` 프레임 시작(lap1166 스캔). 팩 `pack_c`에 지형 이름이 이미 있다 → **`FEASIBLE`**, 새 팩 불필요.
- **writer 의미(원본 역어셈블, 읽기 전용, 공유 temp `h4_468CC0.txt`·`h4_4690A0.txt`):** 행마다 `<skip, count, count 화소>`, 화소마다 `c = src`, `s = shade[y·w + skip + i]`(aux = w×h 바이트, 목적지 기준 위치), `R = pal[c].r`(renderer `+0x419A0`, 3 B/색), `R' = T[(R<<6)+s]`(int16, renderer `+0x6BCA0`), G·B 동일, `dst = inv[(R'<<12)|(G'<<6)|B']`(renderer `+0x19A0`, 64³ 역표). **목적지 읽기 없음**, `ret 0x18`. `0x4690A0`(viewport 클립판)도 같은 세 표를 쓴다. 즉 출력 = `F(c, s)`이며 F는 renderer 표에만 의존한다.
- **HD 의미:** HD 화소 = `F(c_hd, s[x/2, y/2])`(1x 칸의 음영을 2×2에 그대로) — 원본 의미 보존.
- **화면 비중:** 지형 draws 중 큰 몫(H1 음영 키 151개 = 전체 aux 키의 44%).

## 8. 다음 work 사전등록(Sonnet) — H-HDS1: ④-4 음영 지형 HD 팩

**가설.** 음영 지형 writer `0x468CC0`·`0x4690A0`의 출력은 `F(c, s) = inv[T[R(c)][s], T[G(c)][s], T[B(c)][s]]`(renderer 표)이고 source는 `.ytl` 프레임 시작이므로, 키 생성 때 renderer 표로 음영값별 256 B LUT를 만들어 두고 `(digest, w, h)` 팩 프레임(원본 인덱스)에 `hd = LUT_{s(1x 칸)}[hd]`를 적용하면 원본 음영을 유지한 HD 지형이 나온다.

**변경(최소).**
- H-0(정적, 기록만): 두 writer 인자(6개)·행 형식·`s` 인덱싱(클립판에서 skip·클립 뒤 위치)·`s` 범위(표 인덱스 `(comp<<6)+s` → 0..63 기대) 확인. 다르면 그 writer는 범위에서 빼고 기록.
- C(`g1_hd_asset.c`·필요 최소 plumbing): writer ∈ {`0x468CC0`,`0x4690A0`}이고 팩 env 있고 `SYW2_G1_HD_PACK_SHADE≠0`일 때 키 생성 시점(renderer 유효)에서 ① aux w×h 복사 + FNV-1a == `auxiliary_digest` ② 고유 `s` 값마다 `LUT_s[c] = F(c, s)`를 live renderer 표(읽기 가능 검사)로 계산(고유 `s` 상한 예 64, 초과 → `shade_reject`) ③ **자기 검사:** `.ytl` 1x source를 행 형식대로 풀어 identity가 쓴 모든 1x 화소에서 `LUT_{s}[c] == identity 값`(불일치 1개라도 → `shade_reject`, 첫 좌표 키 로그). 통과 키만 `build_hd_frame`에서 `read_pack_frame` HIT 뒤 불투명 화소 `hd[i] = LUT_{s(x/2,y/2)}[hd[i]]`. 그 밖 aux writer(checker `0x468E10`)·끔 env → 지금처럼 `skip_aux`. 팩 env 없으면 무변화.
- trace/키 로그: `hd_pack_shade_hits`·`hd_pack_shade_rejects`(사유별: digest·표 읽기·`s` 상한·자기 검사)·`hd_pack_shade_selfcheck_pixels`, result `shade_hit`/`shade_reject`.
- 테스트(RED→GREEN): 가짜 renderer 표로 F byte 정확, 자기 검사 불일치 → reject, 1x 칸 음영의 2×2 적용 위치, 끔 env·checker → `skip_aux`, trace 필드.

**측정식.**
- S-0(오프라인): lap1169 H1·H2 키 로그 음영 키 → `pack_c` 이름 대응률 기록(≥80% `FEASIBLE`).
- S-1 적용: NG5(`--new-game-path --new-game-start --new-game-act --hd-source scale2x`, 팩 `pack_c`) 켬 2 run + 같은 팩·`SYW2_G1_HD_PACK_SHADE=0` 대조 1 run. 합격 = 켬 두 run 모두 크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator 바깥 diff 0·`shade_rejects` 중 자기 검사 불일치 0(다른 사유는 키·원인 기록 후 별도 판정)·**음영 matched 키 hit ≥ 90%(writer별)**·tinted matched hit ≥ 0.95·A/B·무음영 지형 100% 유지·`lut_rejects` 0·`hd_pack_rejects`는 lap1169 tree_plus 클립 키 외 0(새 reject는 키·원인 기록)·PS3 HD min ≥ 99.9·p95 ≤ 9 ms(부하 의심 시 같은 명령 재실행 허용, 실패 run 보존). 대조 lane은 음영 키 `skip_aux`(끔 스위치 입증).
- S-2 의미: 켬 run에서 `s`가 한 값이 아닌(음영 변화가 있는) HIT 키 ≥ 1, `selfcheck_pixels` 합계 기록.
- S-3 열람: 켬 vs 대조 PS3 크롭(음영 지형 — 안개/그림자 가장자리, 산·물가) 공유 temp 저장. 음영이 사라져 평탄하게 밝아지거나 1x 칸 격자 계단이 보이면 기록(계단은 `s` 2×2 복제의 한계로 공개, FAIL 아님).
- 메모리: 키 수·키당 LUT 바이트·`cache_insert_frame_bytes` 기록.
- 디스크: 시작 여유 9.6 GB < 20 GB → 실행 전 **자기 회차 옛 사본만** 정리 규칙 확인, run당 prefix 1.2 GB×3 + 공유 temp를 고려해 여유가 run 하나도 못 버티면 시작하지 말고 BLOCKED(디스크)로 기록·root 보고(다른 회차 산출물·원본 삭제 금지).
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- **비목표:** checker `0x468E10`·유닛 `0x466B50`·효과, tinted 클립 판정 수리(§3 backlog), 기본 켬·사용자 전달, 화질 평가, 팩 저장소 반입.
- **중단:** 실패 가설 2회 또는 60분. 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hds1/`. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ⑤ 전체 화면(800×600) HD 자리 / ⑥ 유닛 경로. backlog: tinted 클립 판정(§3), 상수 이름 정정, normal 테마 장면, `ytl_narrow` 828, 충돌 이름 처리, writer 허용 목록 일반화, lap1166 backlog 유지.

## 9. 검사

- SAFETY·CONTEXT·focused 결과는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1169 full PASS(1915 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDS1(§8). 사용자 G1 시험 결과가 오면 최우선이다.

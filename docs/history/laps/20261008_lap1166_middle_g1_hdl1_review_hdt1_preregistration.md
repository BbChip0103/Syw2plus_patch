# 2026-10-08 | lap1166 | G1 middle — H-HDL1 독립 검수 · H-HDT1(④-2 지형 무음영 타일 HD 팩) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1165 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1166_preserved_lap1165_escalate_sol.txt`(SHA256 `76dfb7c9fd8ec412…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음.
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ④-1 검수, ④-2 선택·사전등록.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 원본 그림 파일은 읽기만.
- 후보 source(현재 트리, 모두 uncommitted): `g1_hd_pack.h` `95270c49…`·`g1_hd_asset.c` `84bd1169…`·`g1_hd_asset.h` `1d7439bb…`·`g1_panel_layer.h` `b47f0abb…`·`g1_mirror2x.c` `81c5bfa0…`·`direct_draw_trace.c` `cb605532…`·`tools/g1_hd_convert.py` `72ebf153…`·`tests/test_g1_hd_pack.py` `62cc235a…`(work `changed_sha.txt` 00:14의 `05dd23f6…` 뒤 00:30 shim·행동 테스트 추가분, full check 전)·`test_g1_mirror2x.py` `c6eaf3ef…`. lap1165 full check(exit 0, 1905 passed, 로그 00:43) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`). run bridge 대조: P5 = 현재 트리 `g1_hd_asset.c`, L1·P1~P4·N1은 키 로그 줄 형식(`src`)만 다른 이전 판(`diff` 3줄) — 로더 동작 동일.

## 1. 독립 재계산 (work `scripts/` 미사용)

공유 temp `20261008_lap1166_middle_review/`: `recalc_hdl1.py`(`ace76ea6…`)→`recalc_hdl1.json`(`6e77d6ff…`), `recalc_draws_src.py`(`73afd0e6…`), `recalc_trace_ps3.py`(`663e398f…`)→`.json`(`360ea763…`), `scan_nonab.py`(`85e15685…`)→`scan_nonab.json`(`92db5964…`). 원본 `.spr/.ytl/.bmp` 3,374파일 **모든 오프셋**의 128 B FNV-1a를 numpy로 직접 계산하고, 프레임 시작 여부는 이 스크립트가 헤더·오프셋 표(`.spr` 0x4C4·`.ytl` 0x4C0, +0xBF4)를 직접 읽어 판정했다(`g1_hd_convert`·`g1_hd_extract` 미사용).

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| L-1 A/B aux 없음 고유 키 대응 | 100키 중 대응 90·충돌 5·미대응 5 = 90% | 100·90·5·5 = **0.900** | 일치 |
| 원장 키 수(L1) | 572 | trace `identity_keys` 572 | 일치 |
| 키 digest = 원본 프레임 시작 | 독립 C 스캔 100키 중 95 | A/B 대상 156개(L1·P1~P5·N1 합집합) 중 **154 = 프레임 시작·같은 크기**, 1 = 다른 크기 프레임 시작(`yfnt/scrollbar.spr` 16×1), 1 = 스트림 중간(`Online/TILE/151/d-h01.spr` 171720, 16×5). 대응(matched) 이름 중 비시작 0 | 일치(보강: work가 "raw 배치"로 뺀 `.spr` 3개도 헤더 표상 프레임 시작·크기 일치 → 엔진은 RLE로 읽음, 추출기 raw 분류 휴리스틱 한계) |
| trace 카운터 P1~P5 | hits 93/93/97/94/89·misses 83/82/90/89/89·rejects 0 | 각 run `candidate/trace_raw.jsonl` 마지막 카운터 레코드에서 그대로 재현, rejects 0, `identity_invalid_sources` 0, `hd_mask_outside_diff` 0 | 일치 |
| 패널 | P3·P4·P5 j loaded 1, P1·P2 c 파일 없음 | P3~P5 `w004663e0_h5939fabc_831x143.idx8` loaded 1, P1·P2·L1 c 키(loaded 0), N1 k 키 | 일치 |
| matched 키 hit 비율 | P3 97/106·P4 94/103·P5 89/98(원장 키 = 포인터 포함) | 이름 기준(포인터 합침) P3 94/103 = 0.913·P4 91/100 = 0.910·P5 86/95 = 0.905; 차 3 = P5 다중 포인터 이름 3개(`h6ab9f5ec_546x178`·`h133aea10_16x5`·`ha72c8b9f_16x5`)와 같은 크기 | 일치(두 정의 모두 ≥0.90) |
| 미적중 matched 9 | 전부 `fnt/pannelflag.Spr` 138×108, 팩에 없음 | 9개 이름 동일, 팩(`pack_l2b`)에 없는 것 9/9 | 일치 |
| P5 draws | A/B 93,994 중 hit 76,552 = 81.4%·tinted 122,837·지형 aux0 900 | 원장 키(`src` 포함) 기준 정확히 동일, 전체 217,731 중 A/B 43.2%·aux 56.4% | 일치 |
| PS3 HD min·p95·안전·fallback | HD 99.973/100/100/100/99.949, p95 6~7 | 전체 PS3 present(1,530~1,531) covered−stale: 99.973/100/100/100/99.949·N1 99.949, p95 7/7/6/6/6, 안전 7종·fallback 0 | 일치(정정 1) |
| 하네스 결과 JSON | P3·P4 PASS, scale2x PASS, mirror BLOCKED | `new-game-path-result.json` 직접: P3·P4 status PASS·창 4개 hd_min 100·`hd_pack_rejects` span 0·dropped 0·scale2x 바깥 0, mirror nearest 0.747(BLOCKED, NG5 공통) | 일치 |

**판정 영향 불일치 0. 정정 1·공개 3:**
1. (정정) p95를 run별로 한 숫자로 쓰면 하네스 창별 최대와 전체 PS3 분위가 다르다(P2·P4·P5 work 6/7/7 vs 전체 7/6/6). 둘 다 ≤ 9 ms 기준 안이라 판정 영향 없음.
2. (공개, 코드 검토) 로더는 writer를 가리지 않고 **aux 없는 모든 키**에 팩을 조회한다. P5 `other/miss` 65키는 지형 `0x468C30`·`0x468F00`(aux 0)이 팩 조회를 시도한 것이다(이번 팩에 `.ytl` 이름이 없어 MISS). 이 두 writer는 `rep movs` 복사라 identity = 원본 인덱스이므로 무해하고, ④-2에 그대로 쓸 수 있다. 앞으로 aux 없이 색을 바꾸는 writer가 생기면 writer 허용 목록이 필요하다(backlog).
3. (공개, 코드 검토) 첫 시도 결과는 키마다 고정된다(`pack_state`). REJECT/MISS 키는 run 동안 다시 조회하지 않는다 — 팩 파일을 run 중 바꿔도 반영 안 됨(설계상 의도, 결함 아님). HIT 키의 identity 갱신은 파일을 다시 읽고 다시 검증한다(코드 확인).
4. (공개) 미대응 16×5 중간 오프셋·16×1 다른 크기·128 B 충돌·tail 짧음은 digest 이름 방식의 구조적 한계로 work 공개와 같다.

코드 검토(`read_pack_frame`·`build_hd_frame`·`g1_hd_pack_valid`·`pack_dir`): 크기 = `4·w·h` 정확·`file_high` 0 확인, 검증 실패 시 `build_scale2x`가 `hd` 전체를 덮어쓴다, 이름 버퍼 40 B ≥ 최대 22자, 경로 길이 검사, 실루엣 2×2 규칙은 사양(쓴 화소 불투명·안 쓴 화소 0xFE)과 일치, 충돌 = 같은 이름의 1x 그림(투명 포함) sha 둘 이상 또는 HD 불일치 → 쓰지 않음. **결함 없음.**

크롭 직접 열람(`crops/` 3장): 상단 자원 줄 아이콘·숫자 = 팩 쪽이 부드러워짐(바이큐빅), 위치·실루엣 동일; 하단 HUD 좌·우 = 패널 c(위)/j(아래)라 픽셀 대조는 불가하나 F1~F11·설정·명령 칸·미니맵 구멍 정상, 깨짐 없음. work 서술과 같다.

## 2. 판정

**H-HDL1 `PASS(partial, 기술·격리)` 수용.** ④-1 목표(포인터 없는 `(digest, w, h)` 이름으로 A/B writer와 패널에 업스케일러형 팩이 run과 무관하게 적용됨)를 재계산으로 확인했다. 한계는 work 공개 그대로(UI 스프라이트만, 충돌·부분 높이·스트림 중간, 바이큐빅 stand-in, 기본 켬·전달 아님).

## 3. ④-2 선택 근거 (이번 회차 재계산)

- **식별자 실행 가능성:** P3~P5 원장의 A/B 밖 키 381개를 원본 전수 스캔 → **381/381이 원본 프레임 스트림 시작·같은 크기**(tinted `0x466540` 99·`0x466EA0` 56 = `.spr`, 지형 `0x468C30` 65·`0x468F00` 21·`0x468CC0` 53·`0x4690A0` 87 = `.ytl` 64×48). 두 후보 모두 식별자는 `FEASIBLE`.
- **작업량:** 지형 무음영(`0x468C30`·`0x468F00`, aux 없음)은 로더가 이미 조회 중이라(공개 2) **C 변경 없이** 도구 `pack`이 `.ytl` 프레임에 이름을 주면 된다. tinted(aux = 256 B 색 치환표, `g1_mirror2x.c:3816`)는 C에서 팩 인덱스에 표를 다시 씌우는 변경이 필요하다. 음영 지형(aux = 화소별 음영 `w·h` B, 렌더러 팔레트·음영어·역맵 체인)은 가장 복잡하다.
- **화면 면적:** draws는 tinted가 압도적(56%)이지만 지형은 레이어 캐시에 한 번 그려 오래 보이므로 draws 수가 화면 면적을 크게 과소대표한다. tinted 키의 원본은 대부분 `fnt`(나무 등 159/168), `char`는 9뿐이다.
- **사용자 순서:** INBOX 19:3x ④ = "일반 로더 + 안정 식별자 + 팀색·음영 재적용 → **지형 normal 테마**".
- NG5 장면 지형 키는 대부분 `volcano` 테마 전용이거나 여러 테마 공통 타일(`blacktile` 등, 공통 이름 695/7,646)이다. normal 테마 전용 키는 NG5에서 관측되지 않았다.

→ **④-2 = 지형 무음영 타일(`0x468C30`·`0x468F00`)**, 그다음 ④-3 tinted 색 치환표 재적용, ④-4 음영 지형.

## 4. 다음 work 사전등록(Sonnet) — H-HDT1: ④-2 지형 무음영 타일 HD 팩

**가설.** 지형 무음영 writer `0x468C30`·`0x468F00`의 source 포인터는 원본 `.ytl` 프레임 스트림 시작이고(§3 스캔 86/86) 출력은 원본 인덱스 그대로이므로, 도구가 `.ytl` 프레임에 같은 `(digest, w, h)` 이름을 주면 C 변경 없이 기존 로더가 지형 타일에 HD 팩을 적용한다.

**변경(최소).**
- 도구 `tools/g1_hd_convert.py pack`: `--image-dirs`에 들어온 폴더의 `.ytl`도 이름 부여(스트림 시작 = 0xBF4 + 0x4C0 표 `fc`개, 크기 = 헤더 fw×fh, 1x 그림 = `decode_ytl`), 충돌 규칙·`digest_index.json` 형식 동일. 기본 폴더에 `tile` 이미 포함 여부 확인. 스트림 시작 0x4C0 표 규칙이 이번 회차 스캔과 같아야 한다.
- 테스트(RED→GREEN): `.ytl` 합성 파일 이름·오프셋·충돌 테스트, 호스트 로더 테스트에 writer `0x468C30` aux 없음 키 HIT 1개(현재 로더가 writer 무관임을 고정).
- C·하네스 변경은 원칙상 0. 필요하면 근거를 기록하고 최소로(예: 0x468F00 클립 identity 결함 발견 시 수리하지 말고 기록).

**측정식.**
- T-0(오프라인): `pack --dry-run`(tile 포함) → `.ytl` 프레임 수·이름·고유·충돌 이름·충돌 프레임 비율. 공유 temp `20261008_lap1166_middle_review/scan_nonab.json`의 지형 aux0 키 86개가 `digest_index`에 대응(또는 충돌)으로 나와야 한다(대응 ≥ 80%면 `FEASIBLE`, 50% 미만 `BLOCKED(식별자)`로 종료).
- T-1 팩: lap1165 B형 절차(원본 1x 팔레트 RGB → 바이큐빅 2배 → `convert` → `pack`)로 lap1165 팩 내용(A/B·패널) + 관측된 지형 aux0 프레임. 투명 경계 처리 방식(그대로/가장자리 복제)을 기록한다.
- T-2 적용: NG5(`--new-game-path --new-game-start --new-game-act --hd-source scale2x`) 2 run. 합격 = 두 run 모두 `hd_pack_rejects` 0(단 `0x468F00` 키 REJECT는 원인 = 클립 identity 부분 실루엣이면 개수·키를 기록하고 별도 판정, 다른 원인이면 FAIL)·크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator 바깥 diff 0·PS3 HD min ≥ 99.9·p95 ≤ 9 ms·지형 aux0 matched 키 hit ≥ 90%(키 로그 writer별)·A/B hit 비율 lap1165 수준 유지(≥ 0.90)·`hd_pack_lookup_blocks` > lap1165 P3~P5 최대(30.8M, 지형 기여 확인).
- T-3 열람: 같은 장면 팩 없음(N1 또는 새 대조 1 run) vs 팩 run의 PS3 지형 영역 크롭(평지·경계·화면 가장자리 클립 타일 포함)을 공유 temp에 저장. 타일 이음매·마름모 경계 띠가 보이면 그대로 기록(바이큐빅 stand-in 산물인지 엔진 문제인지 구분 근거 포함).
- 테마: 각 run의 지형 키를 테마 폴더에 대응해 기록. normal 테마 전용 키가 관측되지 않으면 그대로 공개하고(NG5는 무작위 맵), normal 테마 장면 확보는 별도 backlog로 남긴다(이번 회차 필수 아님).
- 원본 보호: 원본 EXE·그림 파일 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- **비목표:** tinted 색 치환표(④-3)·음영 지형(④-4)·유닛 `0x466B50`·효과, 기본 켬·사용자 전달, 업스케일 화질 평가, 팩 저장소 반입, writer 허용 목록.
- **중단:** 실패 가설 2회 또는 60분. `BLOCKED(식별자)`면 도구 변경만 남기고 근거 기록. 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdt1/`. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ④-3 tinted 색 치환표 재적용(C, aux 256 B 표를 팩 인덱스에 적용·실루엣 검증 동일). backlog: 추출기 raw 분류(`pannel_gamemenu2`·`lobbynumbutton`·`mapformatinfo`는 헤더 표상 RLE 프레임 시작) 재분류, writer 허용 목록, normal 테마 장면, lap1164 backlog(중복 RGB 쌍·`g1_r5_combo_probe.py` prefix·화면 팔레트 어두움) 유지.

## 5. 검사

- SAFETY·CONTEXT·focused 결과는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1165 full PASS(1905 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDT1(§4). 사용자 G1 시험 결과가 오면 최우선이다.

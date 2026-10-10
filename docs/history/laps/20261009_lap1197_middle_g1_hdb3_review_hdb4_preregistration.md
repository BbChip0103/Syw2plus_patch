# 2026-10-09 | lap 1197 | G1 middle — H-HDB3 검수 · H-HDB4(7인자 혼합 `0x4678C0`·`0x468360`) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 실행 0, C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1196 work → middle). 원문을 byte 일치로 보존한 뒤 삭제했다: `docs/history/laps/20261009_lap1197_preserved_lap1196_escalate_sol.txt`(SHA256 `2f1fa345940582d8…`). `loop/STOP` 없음. INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음.
- 목표: G1 효과(반투명) 갈래. lap1196 work H-HDB3(좌우반전 가중표 혼합 `0x467FD0`·`0x4685C0` HD 키 경로)를 독립 검수하고 다음 work를 정한다.
- 산출물(공유 temp `20261009_lap1197_middle_review/`, SHA256 앞 16자):
  - `recalc_lap1197.py` `87dda7cc626c8026` · `.json` `5727a2a31a5bca25`
  - `keytime_lap1197.py` `dddcca1fcc29d922` · `keytime_P0.txt` `aaeea5e34486e7e5` · `keytime_P1.txt` `ffc564679fad6523`
  - `mut/mutation_lap1197.py` `5f3eddba4ca90c46` · `.txt` `3441c2e850825677`
  - `mut/repro_work_m16_lap1197.txt` `cd0303fc1669ee01` · `mut/repro_work_n11_lap1197.txt` `0f34128cbe02f91d`
  - 원본 역어셈블(`Syw2plus/syw2plus_original.exe`, SHA `b56986e0…` 일치, 읽기 전용): `orig_4685C0_lap1197.asm` `dc074034413d431f` · `orig_467FD0_lap1197.asm` `863a32c4385cce58` · `orig_4678C0_lap1197.asm` `12ada3400d843d39` · `orig_468360_lap1197.asm` `a57f3a3e55449c55`
  - `list_{4678C0,468360,467E60}_onscreen_runs.txt`(과거 trace 전수 검색 결과)

## 1. source·실행 DLL 동일성

- source SHA 9개(`g1_blend_key.h 01ad28c6…`·`g1_mirror2x.c a66b31ed…`·`.h c6c7e396…`·`g1_hd_asset.c b3d51ae2…`·`.h 61173d6b…`·`direct_draw_trace.c 7fed5d24…`·`test_g1_blend_key.py 2ca7e7de…`·`test_g1_hd_pack.py 8e27d680…`)가 lap1196 기록과 일치한다. lap1196 첫 run 뒤 `find -newer`는 `__pycache__`만 나온다.
- 4개 run(P0·P1·Q0·PD)의 bridge 소스 4파일은 저장소와 같다. bridge `_inmm.dll` 4개(497,741 B)는 서로 6바이트(PE 타임스탬프 `0x88-89`·체크섬 `0xD8-D9`·`0x5C204-5`)만 다르다.
- **정정 1(판정 영향 없음):** lap1196 기록의 "`_inmm.dll 76173b36…`(전 run 공통)"은 저장소 `make` 산출물(487,340 B)이다. run은 하네스가 bridge에서 따로 빌드한 DLL을 썼다. 소스가 같으므로 판정은 바뀌지 않는다.

## 2. 원본 역어셈블 독립 대조(작업 1)

- **`0x4685C0`**(`ret 0x14`, 인자 x·y·w·h 하위 16비트, 다섯째 = 스트림):
  - 쓰기 위치 = 행 시작 + `(int16)(w − col − 1)`(`4686FB`~`468705`).
  - 클립 `+0x4D0..+0x4DC`: 위 건너뛸 행 `top − y`(y<top), 아래 잘린 행 `(y+h−1) − bottom`은 파싱하지 않는다.
  - 열 조건: `col ≥ (x+w−1) − right` 그리고 `col < w − (left − x)`.
  - 따라서 쓰는 화면 열은 `[max(x,left), min(x+w−1,right)]`이고 쓰는 행은 `[max(y,top), min(y+h−1,bottom)]`이다. 이는 `g1_blend_clip_window(x0,y0,x1,y1, left,top,right,bottom)`(오른쪽·아래 포함 → 반열림)와 같다.
  - 혼합식: 팔레트 `+0x419A0`, int16 가중표 `+0x41CA0[(d_c<<6)+s_c]`, 역 LUT `+0x19A0[((t0<<6)+t1)<<6+t2]`. `g1_blend_weighted_offset`와 같다.
- **`0x467FD0`**(`ret 0x14`): 클립이 없다. 쓰기 위치는 같은 `(int16)(w − col − 1)`(`468040`~`46804D`)이고 혼합식도 같다.
- **코어 `blend_key_apply`:**
  - `flip = writer ∈ {0x467FD0, 0x4685C0}`.
  - 디코드 직후 idx·mask 행을 반전해 화면 방향 평면을 만든다.
  - crop 오프셋 `(x0−x, y0−y)`, 자기 검사, identity bind(화면 방향 평면), 팩 프레임 오프셋 `offset·2`가 모두 화면 방향으로 맞다.
  - identity 키는 `find_key_for_request`가 writer를 포함해 찾는다. 그래서 같은 digest의 비반전·반전 키가 섞이지 않는다. 실제로 P0의 `d3428f61` 등이 두 writer에서 각각 hit했다.
- **asset 층(작업 2):**
  - `read_pack_frame`은 `is_flip_blend_writer`일 때 팩 행을 반전한 다음 `g1_hd_pack_valid`(반전된 identity 마스크)로 실루엣을 검사한다. LUT은 적용하지 않는다(원본에 remap이 없음).
  - `hd_pack_blend_*`에 포함되고 `hd_pack_flip_*`에는 포함되지 않는다.
  - **끔 env 결정 타당:** `g1_hd_asset_blend_flip_key_path = blend 경로 && !PACK_FLIP_OFF`. 팩 반전의 의미가 두 스위치에 모두 걸리므로 `PACK_BLEND=0` 또는 `PACK_FLIP=0`이면 키를 끄는 것이 맞다.
- **wrap 경로 기하(작업 4(b) 보강):**
  - `0x467FD0` wrapper는 화면 폭 > `G1_OVERLAY_MAX_WIDTH`(320)이면 `reject_size`로 거부한다. stride는 ≥ 800이다.
  - x<0일 때 넘어 쓴 칸은 윗행 열 `[stride+x, stride)` ⊇ 480 이상에 떨어지고, 창 열은 `[0, x+w)` ⊂ `[0, 320)`이다.
  - x+w>stride일 때 넘어 쓴 칸은 아랫행 열 `[0, x+w−stride)`에 떨어지는데, 이 범위는 x보다 작다.
  - y 범위 밖 행은 화면 버퍼 행 밖이다.
  - **그러므로 wrap 쓰기는 키 창 안에 들어올 수 없다. 키는 자기 검사로 확인한 창 픽셀만 덮어쓴다.** wrap 칸을 추적하지 못하는 것은 기존 diff 미러의 기존 backlog("wrap 쓰기 미추적")이고, 키 경로가 이를 악화시키지 않는다.
  - `key_wrap_mismatches`는 현재 크기 상한에서 구조적으로 0인 진단 카운터다. 판정에는 영향이 없다.

## 3. 변이(작업 3, 격리 사본 `/tmp`, 저장소 무변경)

- **work 변이 재현:** `mutation_lap1196.py` 16종을 같은 조건으로 재실행했더니 **16/16 RED**(m4·m8·m12 포함)였고 실패 수도 work와 같았다. `mutation_n11_lap1196.py` 5 wrapper도 **5/5 RED**다. 베이스는 105 GREEN.
- **독립 변이 12종(`mutation_lap1197.py`): RED 11·생존 1**
  - RED 11:
    - a1 idx만 반전
    - a2 `0x467B00`도 반전
    - a3 팩 오프셋을 스트림 방향으로
    - a5 `0x4685C0`이 `0x467B00` 사전 사본을 crop
    - a6 `0x4685C0`이 비반전 스위치 사용
    - a7 `hd_pack_blend_*`에서 반전 writer 제외
    - a8 asset 반전을 `0x467FD0`만
    - a9 반전 경로가 BLEND 끔 무시
    - a10 `key_cut`를 스트림 사각형과 비교
    - a11 wrap 판정에 800 사용
    - a12 `0x467FD0` 통계를 `0x4685C0` 것으로
  - **생존 a4:** `0x4685C0`이 renderer 클립을 우회하는 인위적 형태다(클립 호출 문자열은 남긴 채 그 앞에 무한 클립 창을 계산). 정적 문자열 테스트의 공백이다. 런타임에는 클립 밖 창 픽셀이 원본 미기록 → 자기 검사 불일치 → 폴백(diff 유지)이 되므로 잘못 그리지 않는다. backlog(테스트 보강, 경미)로 둔다.
- focused `tests/test_g1_blend_key.py`·`test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py` **195 passed/16.21s**(로그 `logs/gates/lap1197-middle-focused.log`).

## 4. run raw 새 스크립트 재계산(작업 3)

`recalc_lap1197.py`의 방법(work `w_metrics.py`·`attrib.py`·`asym.py` 코드는 쓰지 않음):
- 최종 `mirror2x_metrics`와 PS3 present로 p95(선형·순위)와 stale 군집(1 s 간격)을 계산했다.
- 키 로그 digest를 6개 폴더 `.spr` 프레임 전체(앞 128 B FNV-1a·w·h)에 귀속했다.
- 실루엣 비대칭은 **자체 스트림 디코드**로 판정했다.

| run | PS3·s | p95 | stale 군집(시작~끝 s, 최대, present) | 안전 7종·dropped | `0x4685C0` 화면 안 = keyed+폴백+빈 창 · cut · 불일치/px | `0x467FD0` 화면 안 = keyed+폴백 · 불일치/px · wrap | 키 로그(반전 2 writer) |
|---|---|---|---|---|---|---|---|
| P0 켬 | 6,030·301 | 6/6 | 13.1~13.3 247(2) · 14.9~15.2 **277**(4) | 0·0 | 1,439 = 717+0+722 · 717 · 0/3,809,623 | 898 = 898+0 · 0/10,608,098 · 0 | 각 14 digest hit, 미귀속 0, 전부 `fnt/CLOUD.spr`, 비대칭 14/14 |
| P1 켬 | 6,031·301 | 6/6 | 없음 | 0·0 | 18 = 15+0+3 · 4 · 0/73,008 | 8 = 8+0(clipped 1) · 0/96,149 · 0 | 7·4 digest hit, 비대칭 전부 |
| Q0 끔 | 6,032·302 | 6/6 | 225.2 79(1) | 0·0 | 1,089 화면 안, 키 시도 0 | 219 화면 안, 키 시도 0 | **항목 0** |
| PD pair | 863 | 7 | 없음 | 0 | (pair = present trace 없음) | — | `0x4685C0` 12 digest hit·비대칭 12/12, `0x467FD0` 0 |

- 비회귀:
  - `0x467580`은 P0 10/10·P1 18/18 keyed이다.
  - `0x467B00`은 P0 9 keyed + 3 빈 창, P1 154 keyed + 6 빈 창이다.
  - 둘 다 폴백 0·불일치 0이다.
- `hd_pack_blend_hits`는 38·34, rejects 0이다.
- pair PD는 `status PASS`·`scene_state_equal` true다.
- **판정 영향 불일치 0.**
- **정정 2:** lap1196 B3-3의 "끔 Q0 키 로그의 두 writer digest = 각 14개"는 사실이 아니다. Q0에는 두 writer 항목이 없다(키 시도 0이 기대 동작). 14 digest 근거는 P0 하나로 충분하다.
- **보강 1:** `0x4672E0` 로고는 P0·P1 모두 keyed 0이고 폴백은 PS3 present 수만큼(6,030·6,031)이며 자기 검사 불일치는 0이다. 원인은 `pack_hdb2b`에 로고 프레임이 없는 것(`hd_pack_blend_misses` 1)이다. 팩 구성 때문이며 H-HDB3와 무관하다.

## 5. 판정 요청 (a)·(b)(작업 4)

- **(a) P0 15.1 s 277 px:** `keytime_lap1197.py`는 키 로그 hit 줄 순서와 present 누적 `hd_pack_hits`를 대응시킨다(키 로그 hit 38줄 = trace 끝값 38, miss 792 = 792). 이 방법으로 보면 P0의 **첫 `0x4685C0` 키 hit는 225.9 s, 첫 `0x467FD0` 키 hit는 261.2 s**다. P1은 118.9 s다. 13.1 s·15.1 s 군집은 반전 키 첫 실행보다 210 s 이상 앞서므로 **키 경로 이전**이다(직접 증거). 시각대와 쌍봉 모양은 기존 서명(lap1192 X2 255·T0 259, lap1194 Y3 245, lap1187 15.5 s 군집 18~305)과 같다. → **기존 서명으로 수용.** backlog 서명 범위를 240~277로 갱신한다.
- **(b) wrap 경로 실게임 미관측·pair `0x467FD0` 항목 0:**
  - §2 기하로 보면 wrap 쓰기는 키 창에 들어올 수 없고, 키는 자기 검사를 통과한 창만 그린다. 그래서 미관측 경로의 위험은 기존 diff 미러와 같다.
  - pair는 장면 비회귀 판정이고 PASS다. `0x467FD0`의 정확성 근거는 P0 화면 안 898호출·폴백 0·불일치 0이다.
  - → **추가 run 불필요, 공개 한계로 수용.**

## 6. 판정

**H-HDB3 `PASS(partial, 기술·격리)` 수용.** 집계: 판정 영향 불일치 0 · 정정 2 · 보강 2 · 공개 2.
- 정정 2: run DLL 동일성 표기, Q0 키 로그
- 보강 2: wrap 기하로 `key_wrap_mismatches`는 구조적 0, 로고 keyed 0은 팩 구성
- 공개 2: 테스트 공백 a4(런타임 자기 검사가 막음), 반전 HD 그림 육안 run 없음

기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 7. 다음 work 사전등록(Sonnet) — H-HDB4: 7인자 가중 혼합 `0x4678C0`·반전 `0x468360` HD 키 경로

**관측 근거:** 과거 trace 1,476개를 전수 검색했다(2026-09-25 이후).
- 화면 안 mirrored 호출이 있는 run은 `0x4678C0` **70**, `0x468360` **26**, `0x467E60` 2(lap1081 hl1·hl2만), `0x467410` 2개다.
- 주로 save000 장면 pair(`--fixture save000`, 예: lap1063 `s0` `0x4678C0` 화면 안 184·`0x468360` 8)에서 나온다.
- NG5·F0 new-game 구성에서는 0이다(lap1196 4 run 모두 0).

**정적 근거(이번 회차 `orig_4678C0_lap1197.asm`, 원본 SHA 일치):**
- `0x4678C0`은 thiscall, 스택 7개(x·y·w·h 하위 16비트, rle, remap 포인터, level 하위 16비트 `movsx`), `ret 0x1C`이다.
- 클립은 `0x467B00`과 같다(`+0x4D0..+0x4DC`, 오른쪽·아래 포함, 위 잘린 행 파싱·미기록). → `g1_blend_clip_window`를 그대로 쓴다.
- 원천 색은 `s = remap[token]`이다(256 B 표, tinted 경로와 같은 LUT 복사·digest 검사 대상).
- 가중표는 **DWORD** 표 `renderer+0x43CA0`이고, 채널마다 `t_c = T[((level·64 + d_c)·64) + s_c]`이다(`467A5F`·`467A76`·`467AA3`). 그 뒤 `inverse[((t0<<6)+t1)<<6+t2]`이다.
- `0x468360`도 같은 DWORD 표·7인자·`ret 0x1C`이다(좌우반전 sibling, 쓰기 위치는 work가 확인).

**단계:**
- **B4-0(정적·테스트):**
  - (1) `0x468360`의 쓰기 위치·클립 식을 원본 역어셈블로 확인해 기록한다.
  - (2) level 값 범위와 `+0x43CA0` 표 크기(level 슬라이스 수 = 표 끝 / 16 KiB)를 호출처 `0x41A827`/`0x41A99F`와 표 구성 코드에서 확정한다. **확정하지 못하면 키 경로는 이번 회차에서 BLOCKED로 끝낸다.** 근거만 남기고 추측 상한은 쓰지 않는다.
  - (3) a4 생존 변이(클립 우회)를 막는 테스트를 추가한다(RED 확인).
- **B4-1(C):**
  - 공유 코어에 7인자 변형을 더한다. 복제 코어는 금지한다. `weights` 대신 `level`·DWORD 표 경로를 쓰는 순수 함수를 둔다(표 밖 인덱스는 거부).
  - remap은 디코드 idx에 적용한 원천 평면으로 자기 검사한다.
  - 팩 프레임은 스트림 idx 기준이므로 asset 층이 remap LUT(256 B 복사·digest)를 팩 프레임에 적용한다(H-HDC1 tinted 방식).
  - `0x468360`은 H-HDB3 flip 파생에 넣는다.
  - level은 identity 키에 포함하거나, level마다 혼합을 호출 때 계산한다. 어느 쪽이든 같은 팩 프레임 재사용이 잘못된 level로 그리지 않음을 테스트로 고정한다.
  - 끔 env는 `SYW2_G1_HD_PACK_BLEND=0`을 공유한다(반전은 `PACK_FLIP=0` 추가). `PACK_TINTED=0`일 때의 동작을 정하고 고정한다.
  - 카운터: `blend_4678C0_*`·`blend_468360_*`(keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels/key_clip_cut/key_clip_empty).
- **B4-2(호스트 테스트·변이 RED):**
  - 원본 asm 식을 옮긴 참조 모델(remap·level·DWORD 표·클립·반전)과 키 자기 검사 평면이 같아야 한다.
  - 변이는 RED여야 한다: remap 생략, level 무시(0 고정), 표 폭 int16 오독, level 범위 검사 제거, 반전 생략, 클립 원본 뒤 읽기, 키 블록 성공 분기 밖.
- **B4-3(귀속):** 키 로그 두 writer의 digest를 6개 폴더 `.spr`에 귀속한다(독립 파서, 미귀속 수 기록). 귀속 파일로 team-safe stand-in 팩을 만든다(`pack_hdb2b` 포함, 확장 이름).
- **B4-4(run):** save000 pair 켬 2회 + 같은 팩 끔(`PACK_BLEND=0`) 1회(lap1063 `s0` 구성: `--fixture save000 --hd-source scale2x`, 키 로그 켬), 그리고 F0 new-game 비회귀 1 run.

**측정식(합격):**
- B4-0(3)·B4-2 변이 전부 RED.
- 두 writer 각각:
  - 키를 시도한 호출 가운데 팩 귀속 키의 keyed ≥95%
  - 자기 검사 불일치 0
  - `key_clip_cut` ≥1(관측 없으면 그 항목 SKIP)
  - `0x468360`은 비대칭 실루엣 hit 키 ≥1(호출 0이면 SKIP 공개)
- 안전 7종·dropped 0, p95 ≤ 끔+2.
- save000 stale ≤ 끔 규모(기존 서명 제외).
- pair 켬 2회 PASS(save000 HOLD 사유가 있으면 끔과 같은 사유만 허용).
- `0x467580`·`0x467B00`·`0x467FD0`·`0x4685C0` 비회귀.
- 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존.
- 디스크 20 GB 미만이면 자기 회차 옛 사본부터 정리하고, 5 GB 미만이면 run을 시작하지 않는다.

**비목표:** `0x467E60`(2 run만 관측, 그다음 후보 또는 마감 판정), 실제 업스케일 화질, 기본 켬·사용자 전달, 기존 서명 원인.

**중단:**
- 실패 가설 2회 또는 60분.
- level 범위 미확정이면 BLOCKED.
- 자기 검사 불일치 급증이나 HUD 위 얼룩이 보이면 즉시 끄고 근거만 남긴다.
- run 대기는 PID `kill -0` 또는 `.exit` 파일로 한다.
- C 변경 순서: lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL.

**backlog 갱신:**
- 기존 서명 stale 쌍봉 범위는 240~277(lap1196 P0)이다.
- a4 클립 우회 테스트 공백(B4-0(3)에서 처리).
- `key_wrap_mismatches`는 크기 상한 아래에서 구조적 0(필요하면 이름·주석 정정).

## 8. 검사

- `checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.
- 이번 회차는 문서와 공유 temp 스크립트만 바꿨고, tools·tests·C source는 lap1196 full PASS(2026 passed) 그대로다. 그래서 전체 `make check`는 SKIP한다.
- 원본 EXE SHA `b56986e0…` 일치. 디스크 여유 약 21 GB.

## 다음 행동

work(Sonnet) H-HDB4(§7)를 진행한다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.

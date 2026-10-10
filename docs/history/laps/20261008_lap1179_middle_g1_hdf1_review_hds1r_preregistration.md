# 2026-10-08 | lap1179 | G1 middle — H-HDF1 독립 검수 · H-HDS1r(음영 키 refresh 시 낡은 LUT 차단) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / middle(중간 계획·컨펌). 게임 실행 0, 게임 DLL·EXE·하네스·C·도구·테스트 source 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1178 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1179_preserved_lap1178_escalate_sol.txt`(SHA256 `522a7559966ef94d…`), 보존 뒤 삭제. `loop/STOP` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 92 GB.
- 목표: G1 — INBOX 2026-10-07 19:3x HD 그림 경로 ⑤ 확장(H-HDF1) 검수. DESIGN 마일스톤 경계 아님.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(공유 temp `20261008_lap1179_middle_review/orig_sha.txt`). 원본 `.spr`·`.pal`·EXE는 읽기만.
- 후보 source(uncommitted) SHA256 앞 16자 8개 = lap1177·lap1178 기록과 일치(`g1_hd_asset.c` `2253b963bcbfec56`·`.h` `467c7a9f721bf91d`·`direct_draw_trace.c` `eb760613a213ab08`·`g1_hd_pack.h` `fb13d7fb0c94ce6b`·`g1_mirror2x.c` `33e7328a3ad9362b`·`g1_hd_convert.py` `5f91271056851b28`·`test_g1_hd_convert.py` `d084e99a427be7af`·`test_g1_hd_pack.py` `ca0d56d3263c5026`). `logs/gates/lap1177-middle-focused.log` 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer`).

## 1. 독립 재계산 (work `scripts/`·`metrics_*.json` 미사용)

공유 temp `20261008_lap1179_middle_review/`: `recalc_hdf1.py`→`recalc_hdf1.json`(F-0·팩 하드링크·F1/H1 trace 상태 구간·캡처 차), `recalc_keys_hdf1.py`→`recalc_keys_hdf1.json`(키 첫 결과·pal 구분 matched), `crop_hdf1.py`→크롭 2장.

| 항목 | work 값 | 재계산 | 판정 |
|---|---|---|---|
| 원본 `.spr` 크기·헤더·끝 480,000 B FNV-1a | 483,060·`09…20 03…58 02`·`100df815`/`e8fd3bbc` | 같음 | 일치 |
| 팩 SHA256·길이·0xFE | `5907ba8d…`/`b3c8b3f8…`·1,920,000·0 | 같음(원본 0xFE도 0), `pack_hdf1_new`와 같은 inode | 일치 |
| 팩 2×2 평균 vs 1x(자기/타 팔레트) | lobby 0.646(protocol 1.600·title 2.199·imjin2 8.546), protocol 0.523(2.225·2.285·7.560) | 같음, 원본 `.pal` 직접 pal8 id = lobby `e24d0e6d`·protocol `84428eed`·title `296963d9`·imjin2 `cecc4681`(디렉터리 이름과 일치) | 일치 |
| 합본 팩 | lap1176 `pack_pal` 하드링크 + 2개 | `pack_pal` 25,635파일 전부 같은 inode(미연결 0), 디렉터리 4개(`cecc4681` 25,634·나머지 각 1) | 일치 |
| F1 상태 구간(present·fullscreen hits 구간 차·misses·rejects·loads 구간 차) | PS9 66/66, PS7 157/157, PS5 710/710, misses·rejects 0, loads 화면당 1 | 같음, 각 구간 hits = `menu_copy_calls` 구간 차, PS3 구간 0 | 일치 |
| `hd_pack_pal_misses` | 30→0 | H1 PS7 11+PS5 19 = 30, F1 0 | 일치 |
| HD min | PS7 99.709·PS5 98.949·PS3 100 | 같음(H1 동일) | 일치 |
| 안전 7종·fallback | 0 | 상태 구간 전부 0 | 일치 |
| p95(ms) | PS7 16(H1 14)·PS5 15(H1 14)·PS9 14/14 | F1 PS7 16.0·PS5 15.0·PS9 14.75, H1 PS7 **14.85**·PS5 14.0·PS9 14.7 | **정정 1**(H1 PS7 14→14.85: 상한 H1+2 = 16.85, F1 16.0은 경계가 아니라 0.85 ms 여유. 사전등록은 14.85로 적혀 있었음) |
| 캡처 차(2×2 평균 vs baseline) | PS5 0.650·p99 7.33·>16 0.13%, PS7 0.505·5.00·0.05%(H1 0.375/0.368) | 같음, `menu.png` F1 = H1 2.067(PS9 무변화) | 일치 |
| 키 결과 | hit 137·miss 70·shade_hit 138·lut_hit 188·reject 2(H1 128·68·149·193·2) | 같음, 키 389(H1 389) | 일치 |
| ab matched hit | 0.7736(H1 0.7526, +2.1%p 높아짐, 공개) | 같은 정의(이름이 `cecc4681`에 있는 키, pal 무관) 82/106·73/97 재현. 분모에 **타이틀 계열 pal 키 24개**(296963d9 5·84428eed 10·e24d0e6d 9 — H-HDPAL 설계상 miss)가 상수로 들어감. pal 구분(in-game pal 키만) = F1 **82/82**·H1 **73/73 = 100%** | **정정 2**(측정식 결함: +2.1%p는 in-game ab 키 수 82 vs 73 장면 변동에 따른 분모 구성 차. pal 구분 matched hit는 두 run 모두 100% → 공개 사유 없음) |
| tinted 0.9895 | | 이벤트 기준 188/(188+2 reject) = 0.98947, 키 첫 결과·pal 구분 기준 133/133 | 정의 차(영향 0) |

## 2. PS7 p95 판정

PS7 p50 9→10·>16 ms present 2→7, PS5 p50 동일 9·>16 0→4. PS9(H1에서 이미 팩 적용)는 14.7→14.75로 불변. lap1173 PS9 팩 켬/끔 p95 14/13과 같은 크기(약 +1 ms)라 **팩 800×600→1600×1200 복사 비용**으로 판정(환경 변동만은 아님). 사전등록 상한 안(16.0 ≤ 16.85, 15.0 ≤ 16.0)이므로 수용. 기본 켬·전달 전 실제 Windows 측정은 별도(기존 공개 유지).

## 3. 크롭 직접 열람

`lap1179_ps5_base_left_cand_right.png`(PS5 x250..550·y380..560, 왼쪽 baseline 2배 nearest·오른쪽 후보): 석재 패널·금속 띠·하단 암석 질감 변색·잡음·줄무늬 없음, 구도 동일. `lap1179_ps7_base_left_cand_right.png`(PS7 x100..400·y60..240): 노을 하늘·`IPX 대전` 버튼·목록 글자(TCP/IP 문구) 색·위치 동일, 질감만 부드러움.

## 4. 판정

**H-HDF1 `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0, 정정 2(H1 PS7 p95 14.85·ab matched 측정식 분모), 공개 3: ① 팩 복사 비용 약 +1 ms(상한 안), ② 단일 run·화질 평가 아님(바이큐빅 stand-in)·기본 켬·전달 아님, ③ 다른 전체 화면(브리핑·결과·로딩·옵션) 미관측. 이후 matched hit 측정은 **키 pal 디렉터리 기준**(in-game pal 키 ↔ `cecc4681`, 타이틀 계열 pal 키 ↔ 해당 pal 디렉터리)으로 센다.

## 5. H-HDS1r 정적 근거 (원본 역어셈블, lap1177 `orig_lap1177.asm` 재사용·직접 grep)

- `shade_prepare`가 읽는 renderer 표 세 개의 **쓰기 지점은 하나씩뿐**: 역표 `+0x19A0` = `0x465320` 안 `0x4653D7`, 6비트 팔레트 `+0x419A0` = `0x465433` 루프(`+0x6DCA0` 원본 팔레트 복사), 음영표 `+0x6BCA0` = `0x4655B0`(값 = `min(63, i·j/63)`, 대칭 상수 곱셈표). 다른 참조는 읽기(`0x465D92`·`0x465DDB`·`0x465F7A` lea → `mov bl,[ebx]`/`[edx]` 읽기, 절대 주소 `0xEC7BB8` 참조 3곳 movsx 읽기).
- 세 builder는 `0x465300`에서만 호출되고, `0x465300`의 호출처는 `0x424CD2` 하나 — 사슬 `0x4DBDA0`→`0x423150`→`0x424BE0`(시작 init: 할당·`0x493080` 밤 표·`0x4657A0` CreatePalette)→`0x465300`. 즉 **프로세스 시작 때 1회 구축, 이후 불변**.
- 결론: lap1172 §2-4 "표 변경 뒤 낡은 LUT 재적용"은 원본 바이너리에서 도달 경로가 없는 **잠재 결함**이다. 그래도 음영 HIT 키의 identity refresh는 코드상 가능한 경로(원인이 무엇이든 1x 출력이 키 예측과 달라졌다는 신호)이고 지금 코드는 그때 옛 LUT를 새 프레임에 칠하므로, 기본 켬·전달 전 **방어적 강등**(재준비가 아닌 Scale2x)이 가장 작고 안전한 수리다. 표가 불변이라 재준비(`shade_src` 보존·재검사)의 이득은 없다.

## 6. 다음 work 사전등록(Sonnet) — H-HDS1r: 음영 HIT 키 refresh 시 Scale2x로 강등

**가설.** `g1_hd_asset_compare_visible_frame_in_viewport`가 음영 팩 HIT 키(`is_shade_pack_writer`·`pack_state == PACK_HIT`·`shade_pack` 적용 키)의 identity를 비울 때 그 키를 `PACK_SHADE_REJECT`(새 이유 `refresh`)로 내리면, 다음 `build_hd_frame`은 Scale2x를 만들고 낡은 `shade_lut`가 새 프레임에 적용되는 경로가 사라진다. 기존 NG5 run(refresh 0)의 동작·수치는 변하지 않는다.

**단계.**
- R-0(TDD, 호스트 테스트 `tests/test_g1_hd_pack.py`): 음영 키 팩 HIT → 다른 1x 출력으로 compare 불일치(refresh) → 재빌드 결과가 **새 identity의 Scale2x**와 같고 옛 LUT 적용 프레임과 다름, 카운터 `refresh` 1, 키 로그 1줄(`shade_reject`/`refresh`) — 수리 전 RED·수리 후 GREEN, 변이 확인(강등 줄 제거 시 RED). 음영 아닌 키(plain·tinted) refresh는 지금처럼 팩 재적용(비회귀 테스트).
- R-1(C): 강등 + `shade_lut` 해제(누수 0) + `g_shade_reason_names`에 `refresh` 추가 + trace 필드 `hd_pack_shade_reject_refresh`(기존 `hd_pack_shade_reject_*` 형식). 끔 env·기본값 변경 없음.
- R-2(run): NG5 1 run(`--new-game-path --new-game-start --new-game-act`, 합본 팩 = lap1178 `pack_hdf1`). 대조 = lap1178 F1.

**측정식(합격).**
- R-0 테스트 RED→GREEN·변이 확인, 전체 호스트 테스트 통과.
- R-2: `hd_pack_shade_reject_refresh` 0(이 장면 refresh 0 예상; 0이 아니면 그 키 수·present·위치를 기록하고 HD min 영향을 F1과 대조), shade_hits·selfcheck 불일치 0·`shade_rejects`(기존 이유) 0, 음영·지형·tinted·ab matched hit(**pal 디렉터리 기준**) F1 수준, PS3 HD min ≥ 99.9, 안전 7종·fallback·dropped 0, PS5·PS7 fullscreen hits = menu 호출 수, p95 ≤ F1 + 2 ms.
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 5 GB 미만이면 run 시작 금지.
- **비목표:** 재준비(`shade_src` 보존) 방식, ⑥ 유닛, tinted 클립 판정, 기본 켬·사용자 전달, 화질 평가.
- **중단:** 실패 가설 2회 또는 60분. run 대기는 PID `kill -0`·`.exit` 파일(INBOX 12:47 규칙, `pgrep -f` 자기 일치 금지). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hds1r/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ⑥ 유닛 경로(`0x466B50`/`0x466BE0` 키 경로화 + 메모리 대책: 32비트, 필요 시 로드, 키 4096·캐시 128 MiB 한도). backlog 유지: miss 음영 키 `shade_src` 해제, 로더 miss 슬롯 8·reject 영구 기억, tinted 클립 판정, 여러 스테이지·낮밤 팔레트 실측(lap1177 §3-3a), lap1172 backlog.

## 7. 검사

- focused 테스트·`checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1176 full PASS(1944 passed) 그대로다.
- STATUS 129줄 → 압축 전 전문을 `docs/history/20261008_status_lap1179_precompaction.md`(129줄·SHA256 `29406b623503b775…`)에 byte-exact 보존 뒤 압축.

## 다음 행동

work(Sonnet) H-HDS1r(§6). 사용자 G1 시험 결과가 오면 최우선.

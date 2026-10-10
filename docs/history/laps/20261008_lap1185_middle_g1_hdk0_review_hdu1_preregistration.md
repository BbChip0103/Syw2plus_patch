# 2026-10-08 | lap 1185 | G1 middle — H-HDK0 독립 검수 · H-HDU1(⑥-2 `0x466BE0` 클립 반전 유닛 키 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 코드·source 수정 0, 게임 실행 0.
- 입력: lap1184 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261008_lap1185_preserved_lap1184_escalate_sol.txt` SHA256 앞 16자 `faf4027055fdcd6e`, 보존 뒤 삭제), lap1183 사전등록 §5, lap1184 기록. INBOX·APPROVALS에 새 사용자 지시·반려·G1 시험 결과 없음(19:3x HD 그림 경로 지시 ⑥ 단계).
- 원본 SHA: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` read-only MATCH(이번 회차 직접 재계산). 디스크 여유 73 GB.
- 산출물: 공유 temp `20261008_lap1185_middle_review/` — `recalc_lap1185.py`(`db11c459…`)·`recalc_lap1185.json`(`cd6a9b87…`)·`mutation_lap1185.{txt,diff}`(`fe49f018…`·`a81dadf8…`).

## 1. source 정체성

- source SHA256 앞 16자 6개가 lap1184 기록과 일치(`g1_hd_asset.c 6c2b7998…`·`.h 06410b3b…`·`direct_draw_trace.c c2baaacd…`·`g1_saved_scene_probe.py 557bda2b…`·`test_g1_hd_pack.py 6e06f924…`·`test_g1_new_game_path.py 7005173c…`). `logs/gates/lap1184-work-full-check.log`(`ca8a9b80…`, 1960 passed·5 skipped) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer` 0).
- run별 측정 DLL 소스(`bridge/`): **E3·P2 = 현재 source**(차이 = 하네스 주입 `supply_probe_poll` 2줄, lap1183과 같은 변환). E1·K3·E2·P1 = 중간 소스 `e1aaef60…`(현재와 차이 = `drop_key_frames`의 `with_shade` 인자 3곳뿐 = 바이트 축출 경로, 이 경로는 최대 캐시 26 MB라 실행 안 됨). K2 = 축출 이전 소스(K-0만). work 기록 한계 2와 일치. 공개: K3·E2는 "한도 없음"이 아니라 축출 가능 소스에서 한도 미도달(4096·1000)이라 동작은 축출 없음과 같다.

## 2. 코드 검수

- **키 포인터 수명.** 화면 lookup(`g1_hd_asset_lookup_identity_block{,_at}`)은 `g_current_key`로만 하고, 호출처 `g1_mirror2x.c`는 begin(3127행)→compose→`g1_hd_asset_end()`(3331행) 안에서 끝난다. draw를 넘겨 남는 키 참조가 없으므로, 같은 present에서 먼저 그린 키를 축출해도 그 present 화면은 이미 합성돼 있다. 사전등록 (iii)의 "이번 present 키 축출 금지"는 구현되지 않았으나 **불필요로 수용**(이탈 공개).
- **슬롯 축출**(`g_key_count >= g_key_limit`): 현재 키를 뺀 최소 `last_draw` 키 → `drop_key_frames(slot, TRUE)`(identity·HD·음영 사본 해제) → `memset` 뒤 새 키. 정상 흐름에서는 begin 전에 end가 `g_current_key`를 비우므로 제외 대상은 중첩 호출 방어용이다(`g_primitive_guard`로 중첩 차단).
- **바이트 축출**(`make_room_for`): bind는 `bytes*2 ≤ LIMIT`, build는 `hd_bytes ≤ LIMIT`를 먼저 확인하므로 `LIMIT - needed` 언더플로 없음. build는 자기 키를 제외해 방금 bind한 identity를 지우지 않는다. 회계: identity+mask를 함께 빼고 HD를 따로 뺀다(변이 m4로 확인).
- **한계 8(바이트 축출 때 음영 사본 유지) 판정: 수용.** 음영 LUT `F(c,s)`의 입력은 renderer `+0x419A0`(불변 imjin2 6비트 복사, lap1176)·`+0x6BCA0`(음영 표)·`+0x19A0`(역표)뿐이고, 셋 다 시작 init `0x424CD2`→`0x465300`에서 1회 구축된다(lap1179 역어셈블). 키별 입력 `shade_map`은 digest 검사로 복사됐고 키 식별에 aux 포인터·aux digest가 들어간다. 그러므로 같은 키의 LUT는 재bind 뒤에도 같다. 재bind 때 팩 프레임은 `read_pack_frame`의 실루엣 검사(허용 0)를 다시 거친다. H-HDS1r의 refresh 강등은 "같은 키인데 화면 출력이 달라졌다"는 변화 증거가 있을 때만 쓰는 것이고, 바이트 축출은 그런 증거가 없으므로 둘이 달라도 일관된다. 바이트 경로는 실게임에서 실행된 적이 없다(최대 26 MB) — 공개 유지.
- **변이(격리 사본 `/tmp/lap1185_mid_mut`, 저장소 무변경, work 5종과 다른 6종 독립 설계).** 기준 52 passed.

| 변이 | 내용 | 결과 |
|---|---|---|
| m1 | LRU 비교 `<`→`>`(최신 키 축출) | **RED 2** |
| m2 | 슬롯 축출 현재 키 제외 → `NULL` | **RED 1** |
| m3 | 기존 키 hit 때 `last_draw` 갱신 제거(LRU→삽입순 FIFO) | **생존**(52 passed) |
| m4 | `drop_key_frames`의 HD 바이트 차감 제거 | **RED 3** |
| m5 | `build_hd_frame`의 `make_room_for(hd_bytes, key)` → `NULL`(자기 identity 축출 허용) | **생존**(52 passed) |
| m6 | 바이트 축출이 음영 사본까지 해제 | **RED 1** |

  - m3 생존 = LRU의 핵심 성질(최근에 다시 그린 오래된 키는 남는다)을 검사하는 테스트가 없다. 현재 코드는 맞다(788행), 테스트 공백이다.
  - m5 생존 = build 단계에서 다른 프레임 보유 키가 없을 때 자기 키를 축출하지 않고 실패하는지 검사가 없다. 현재 코드는 맞다(1108행). 변이 상태라면 방금 bind한 identity를 해제한 뒤 같은 build가 그 버퍼를 읽는 use-after-free가 된다 → 회귀 방지 테스트 필요.
  - 두 공백은 다음 work 0단계로 넘긴다(§5).

## 3. 런타임 재계산(새 스크립트, nearest-rank p95, candidate trace·키 로그)

| run | 소스 | PS3 s | keys 시작→최대 | evictions | invalid | 최대 캐시 | PS3 stale present(초:px) | p95 | 안전 7종·fallback·dropped | 키 로그 reject |
|---|---|---|---|---|---|---|---|---|---|---|
| K1 | — | 0(후보 PS5 정체, status FAIL·exit 2) | — | — | — | — | — | — | — | 0 |
| K2 | 축출 전 | 305.9 | 252→1209 | — | 0 | 25.58 MB | 없음 | 6 | 0 | 1 |
| K3 | 중간 | 305.9 | 251→1233 | 0 | 0 | 26.25 MB | 13.4:59 | 6 | 0 | 2 |
| E2(한도 1000) | 중간 | 305.8 | 253→789 | 0 | 0 | 17.09 MB | 13.3:67, 76.7:90 | 6 | 0 | 2 |
| E1(한도 600) | 중간 | 305.7 | 253→600 | 927(첫 41.8 s) | 0 | 13.58 MB | 13.3:59, 15.3:264, 77.9:110, 141.1:79, 141.3:92 | 6 | 0 | 0 |
| E3(한도 600) | **현재** | 305.8 | 253→600 | 824(첫 76.8 s) | 0 | 15.19 MB | 13.2:246, 13.4:59, 15.4:235, 15.5:77, 15.5:18, 141.2:2, 225.5:2 | 6 | 0 | 5 |
| P1·P2 | 중간·**현재** | pair | 키 로그 약 790 | 0 | — | — | — | — | pair PASS·scene_equal | 0 |

- K-0: K2 마지막 `identity_cache_bytes` 25,582,224 = 3×8,527,408(refresh 0). 일치.
- K-1 60 s 창 키 증가 K2 +351/+407/+86/+110/+3, K3 +346/+440/+81/+109/+6, E2 +305/+201/+7/+14/+8 → 첫 1~2분에 대부분 생기고 포화.
- 축출 run 키 로그: 축출 키 E1 927·E3 824, 그중 다시 그려져 재등록된 키 390·354. 축출된 키의 축출 시점 draw 수는 1회가 E1 490·E3 430으로 가장 많다(드물게 그린 키부터 나감, LRU와 부합). writer 분포는 음영 지형 `0x4690A0`·`0x468CC0`이 가장 많다.
- **work 수치 일치.** keys·evictions·invalid 0·캐시·p95 6·안전 0·pair PASS·pack hit 1318/1227·외삽값(K2 60 s 1,442.3·120 s 51.1·180 s 43.5·240 s 19.1·전체 15.4분)이 모두 재현됐다.

### 정정·보강

1. **정정(전사):** E1 축출 전 stale은 work "264·59(13.3·15.3 s)"가 아니라 13.3 s **59**·15.3 s **264**다(값 쌍 순서만 다름).
2. **정정(K-1 조건 판정):** work의 "창 ≥120 s에서 조건 충족"은 K2·K3에만 맞다. E2는 120 s 창 601분·180 s 397분이고 240 s(57.3)·전체(31.4)에서만 ≤60분이다. 현재 증가율(마지막 60 s 창)로는 세 run 모두 472~1,442분이다. 따라서 사전등록 조건(창 정의 없음)은 **판정 불가(창 의존)**로 정정한다. 그래도 **K-2 구현은 수용**한다. 근거: (a) 한도에 닿은 뒤 회복할 경로가 없다(조용한 열화), (b) 키 식별에 source·aux 포인터와 pal이 들어가므로 스테이지 재진입·세이브 로드·낮밤 팔레트마다 새 키가 쌓일 수 있다(미실측, backlog), (c) 한도에 닿기 전에는 축출 코드가 실행되지 않는다(K3·E2·P1·P2 evictions 0, 비회귀).
3. **보강(새 사실) — 축출 run에만 있는 141 s 일시 stale.** 141.1~141.3 s의 stale이 E1(79·92)·E3(2)에만 있고, 축출 없는 K2·K3·E2에는 없다. 76.7~77.9 s는 E2(축출 없음, 90)·E1(110)에 모두 있어 장면 쪽 사건이다. 15.5 s 뒤 stale 합은 E1 281(3 present)·E3 4(2)·K2 0·K3 0·E2 90(1)이다. 그러므로 work의 "축출 중 stale는 대조와 같은 규모"는 E3에는 맞고 E1에는 맞지 않는다. 축출과의 연관은 배제할 수 없다(2/2 대 0/3, 표본 작음). 크기는 모두 단발 ≤110 px(<0.03%)로 기존 select 일시 stale(235~264)보다 작고, 다음 present에서 사라진다.
4. **보강(새 사실) — 축출 뒤 재등장한 키의 팩 판정 변화.** E3 tinted 키 `e9093cdb`(64×48, `0x466EA0`)는 lut_hit였다가 축출된 뒤 재등장 첫 bind에서 `reject`가 됐다. 이때 키 로그 `written 0`이다 = 화면 밖·클립된 draw의 빈 identity. 이는 lap1170에서 명시 예외로 둔 clipped identity reject 계열이고, 같은 키가 다시 축출될 때까지 Scale2x로 남는다. 반대 방향(reject→lut_hit)도 1건 있다. 축출이 기존 reject 계열에 "첫 bind 기회"를 늘리는 것이고, 안전 영향은 0이다. 실제 한도 4096에서는 축출 자체가 드물다.
5. **보강 — `0x466BE0` 화면 안 호출 관측.** lap1183은 NG5 2분 run에서 "화면 안 0"이었다. 이번 맵 끝↔끝 306 s 스크롤 run에서는 K2·K3·E3 각각 화면 안 diff 미러 12·12·14회(그중 viewport 클립 8·8·10, 변화 픽셀 1,194·1,194·3,366)가 있고, 나머지(7,229~9,723)는 wrap·`reject_bounds`다. 가장자리 클립 반전 유닛은 지금 키 경로가 아니라 diff 미러(Scale2x 품질)로 그려진다 → ⑥-2 근거가 생겼다(빈도는 낮다).

## 4. 판정

**H-HDK0 `PASS(partial, 기술·격리)` 수용.** K-0 PASS, K-1 PASS(partial; 조건 판정은 창 의존으로 정정), K-2 수용(축출 정확성은 호스트 테스트·변이 RED 4/6, 실게임 thrash 2 run에서 invalid 0·안전 0·p95 = 대조). 판정에 영향을 주는 불일치 0, 정정 2, 보강 3(141 s 축출 연관 stale·재등장 reject 계열·`0x466BE0` 화면 안 관측), 공개 4(테스트 공백 m3·m5, (iii) 이탈, 바이트 경로 실게임 미도달, K3·E2 소스). 사전등록 측정식 "stale가 대조와 같거나 낫다"는 **미입증(UNKNOWN)**으로 둔다. 크기가 단발 ≤110 px이고 진단 env thrash(실제 한도의 1/7)에서만 나왔으므로 수용을 막지 않는다. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님, 사용자 승인 해당 없음.

**⑥ 마감 판단:** 메모리 대책(키·캐시 한도와 회복)은 위 수용으로 닫는다. ⑥-2 `0x466BE0`만 남는다(§3 보강 5). 다음 work가 이것을 키 경로로 옮기고, 같은 회차에 m3·m5 회귀 테스트를 더한다. 그 middle 검수가 끝나면 ⑥을 마감한다. 그 뒤 INBOX 19:3x 순서는 "효과(반투명) 후순위"다. 그때 middle이 효과 경로를 계속할지, 사용자 HD 그림이 오기 전까지 다른 G1 잔여(사용자 시험 재스테이징 여부 등)로 돌릴지 정한다.

## 5. 다음 work 사전등록(Sonnet) — H-HDU1: `0x466BE0` 클립 반전 유닛 키 경로 + H-HDK0 회귀 테스트 보강

**근거(`FEASIBLE`).** `0x466BE0`은 `0x466B50`의 클립 형제다: 같은 thiscall 6인자(x y w h rle lut, ret 0x18), renderer 클립 상자 `[+0x4D0..+0x4DC]` 안만 쓴다(`g1_mirror2x.c` 4413행 주석). 비반전 쌍(`0x466EA0` 무클립 / `0x466540` 클립)은 이미 둘 다 tinted 키 경로에 있다. `mirror_reinvoke`의 writer switch(2965행 근처)에 `G1_FLIP_CLIP` 분기가 없고, `is_flip_pack_writer`가 `G1_HD_FLIP_RLE`만 받는다. 둘 다 기존 패턴으로 확장할 수 있다.

**단계.**
- U1-0(테스트만, 동작 변경 0): `tests/test_g1_hd_pack.py`에 (i) **LRU 최근성** — 한도 N에서 키 A(가장 먼저 등록)를 한도 도달 직전에 다시 begin한 뒤 새 키를 넣으면 A가 아니라 B가 축출된다. (ii) **build 단계 자기 보호** — 캐시 바이트 한도를 작게 해서 다른 프레임 보유 키가 없을 때 build가 자기 identity를 축출하지 않고 실패한다(`identity_invalid_sources` +1, 캐시 바이트 0으로 복귀, 크래시 없음). 둘 다 lap1185 변이 m3·m5에서 **RED**, 현재 코드에서 GREEN이어야 한다(변이 재실행 결과를 기록).
- U1-1(C): `0x466BE0`을 flip 키 경로에 넣는다. writer 상수, `is_flip_pack_writer`, `mirror_reinvoke` 분기를 추가하고, 래퍼 `mirror_flip_clip`은 `mirror_flip_rle`·`mirror_tinted_clip_rle`처럼 화면 안·비wrap·키 경로 켬일 때만 키 경로를 쓴다. 클립 draw는 `0x466540`과 같은 viewport replay·클립 identity 처리를 따른다. ready가 아니면 기존 diff 미러로 폴백한다. 끔 env는 기존 `SYW2_G1_HD_PACK_FLIP=0`을 공유한다(새 env 금지). 호스트 테스트: 클립 반전 팩 hit(반전 실루엣 검사), 클립 identity 처리, 폴백, 끔 env — 각각 수리 전 RED·후 GREEN·변이 RED.
- U1-2(run): lap1184 하네스 장기 스크롤(`--new-game-play-keys RIGHT,DOWN,LEFT,UP,... --new-game-play-hold 20 --new-game-play-dwell 60`, PS3 ≥300 s, 한도 기본) 켬 2 run + 끔(`SYW2_G1_HD_PACK_FLIP=0`) 1 run, save006 pair 1회(비회귀).

**측정식(합격).**
- U1-0: 테스트 2개가 m3·m5 변이에서 RED이고 현재 코드에서 GREEN.
- U1-1: 호스트 테스트 GREEN·변이 RED.
- U1-2 켬: `flip_clip_466BE0`의 화면 안 호출(이전 mirrored 12~14) 중 키 경로 처리 ≥90%, 나머지는 사유가 기록된 폴백(diff 미러). 팩이 있는 화면 안 클립 반전 키는 `lut_hit` 또는 사유가 기록된 reject. 안전 7종·fallback·dropped 0, PS3 p95 ≤ lap1184 대조(6)+2, PS3 stale은 lap1184 K2·K3 규모(단발 ≤ 264 px, 15.5 s 뒤 합 ≤ 110)를 넘지 않는다. 끔 run은 lap1184 K run과 같은 diff 미러 경로(키 경로 0). save006 pair PASS.
- 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 5 GB 미만이면 run 시작 금지(현재 73 GB).
- **비목표:** 효과(반투명) 경로, 팩 화질 평가, 141 s 축출 연관 stale 원인, 기본 켬·사용자 전달, 활성 8인 부하.
- **중단:** 실패 가설 2회 또는 60분. U1-1이 `0x466540` 패턴으로 안 맞으면(예: 클립 identity 재생이 반전과 충돌) 구현을 멈추고 `BLOCKED`로 근거를 기록한다. 그 경우 U1-0 테스트만 남기고 ⑥은 "`0x466BE0` 가장자리 diff 미러 잔여"로 마감한다. run 대기는 PID `kill -0`·`.exit` 파일(INBOX 12:47 규칙). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdu1/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **backlog 추가:** 141 s 축출 연관 일시 stale(E1·E3), 재등장 첫 bind 클립 identity reject(lap1170 계열), 한 프로세스 안 스테이지 재진입·로드 반복 시 키 누적 실측(K-2 필요성 (b)), `last_draw` DWORD 순환, K1 후보 레인 PS5 정체 단발.

## 6. 검사

- focused `tests/test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py`·`test_g1_new_game_path.py` **202 passed/9.70s**(로그 `logs/gates/lap1185-middle-focused.log` `9845c909…`).
- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1184 full PASS(1960 passed) 그대로다.
- `checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.

## 다음 행동

work(Sonnet) H-HDU1(§5). 사용자 G1 시험 결과가 오면 그것이 최우선이다.

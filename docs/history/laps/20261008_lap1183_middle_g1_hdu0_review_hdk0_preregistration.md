# 2026-10-08 | lap 1183 | G1 middle — H-HDU0 독립 검수 · H-HDK0(키·캐시 한도 실측 → 조건부 축출) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 코드·source 수정 0, 게임 실행 0.
- 입력: lap1182 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261008_lap1183_preserved_lap1182_escalate_sol.txt` SHA256 앞 16자 `7c6c0e0ad00a72b2`, 보존 뒤 삭제), lap1181 사전등록 §5, lap1182 기록. INBOX·APPROVALS 새 사용자 지시·반려·G1 시험 결과 없음(19:3x HD 그림 경로 지시 ⑥ 단계 진행).
- 원본 SHA: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` read-only MATCH(이번 회차 직접 재계산). 디스크 여유 84 GB.
- 산출물: 공유 temp `20261008_lap1183_middle_review/` — `recalc_lap1183.py`(`a9733a50…`)·`recalc_lap1183.json`(`645a9dc2…`)·`flip_asym_lap1183.py`(`35de2836…`)·`flip_asym_lap1183.json`(`80e25c6a…`)·`mutation_lap1183.{txt,diff}`(`e1551470…`·`ef33e745…`).

## 1. source 정체성

- source SHA256 앞 16자 6개가 lap1182 기록과 일치(`g1_hd_asset.c 7efa805d…`·`.h b48c8f23…`·`g1_mirror2x.c 367ebe68…`·`.h b993fbf7…`·`direct_draw_trace.c 8371101a…`·`test_g1_hd_pack.py f8fddbe8…`). `logs/gates/lap1182-work-full-check.log` 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer` 0).
- 5 run(U0·U1·U2·P0·P1) 실행 DLL 소스 스냅샷(`bridge/`) 대조: 저장소와 다른 것은 `inmm_stub.c`(하네스 주입 `supply_probe_poll` 2줄, 5 run byte 동일, lap1178·1180과 같은 변환)와 하네스 생성 `runtime_bridge.c`뿐 → 측정 DLL = 현재 source.

## 2. 코드 검수

- 키 식별(`find_key_for_request`)에 writer가 들어가므로 반전 키와 같은 digest의 비반전(tinted) 키는 서로 다른 키다(반전 HD가 비반전 화면에 섞일 경로 없음).
- `read_pack_frame`: flip writer면 파일 프레임을 행마다 좌우 반전한 뒤 `g1_hd_pack_valid`로 화면 identity 마스크와 2×2 단위 **허용 0** 비교 → 그다음 LUT. `build_hd_frame`의 LUT 분기·카운터·키 로그가 flip을 tinted와 같은 방식으로 처리.
- `mirror_flip_rle`: 원본 호출 뒤 화면 안·비클립·비wrap·키 경로 켬일 때만 `mirror_reinvoke`(scratch 버퍼로 교체해 재호출 → 화면 자체는 다시 쓰지 않음, `g_primitive_guard`로 중첩 차단). `g_reinvoke_composed`는 `current_ready()`(identity bind 성공)일 때만 참. bind 실패(키 한도·캐시 바이트 한도·`build_hd_frame` 실패)는 `identity_invalid_sources` 증가 + not ready → 기존 diff 미러 폴백으로 덮는다. compose 중 lookup 실패 픽셀은 present 때 nearest 확장(검정 아님).
- 변이(격리 사본 `/tmp/lap1183_mid_mut`, 저장소 무변경, `mutation_lap1183.txt`): 기준 45 passed. m1 `flip_pack_rows` 호출 → `(void)hd;` **2 RED**(work 기록과 같은 2건), m2 build의 flip LUT 분기 비활성 **3 RED**, m3 래퍼 `if (g_reinvoke_composed)` → `if (1)`(폴백 제거) **1 RED**. (첫 m1은 `;`로 바꿔 `-Werror` 빈 문장 경고로 컴파일 자체가 깨졌다 — 의미 있는 RED가 아니라 재실행으로 대체, 공개.)

## 3. 런타임 재계산(새 스크립트, nearest-rank p95)

| 항목 | U0(끔) | U1 | U2 | P0(끔) | P1 | work 기록 |
|---|---|---|---|---|---|---|
| exit / status | 0 / PASS | 0 / PASS | 0 / PASS | 0 / PASS·scene_equal·V2/V2s/V2q/Scale2x PASS | 같음 | 일치 |
| flip invocations / keyed / mirrored / fallback | 1292 / 0 / 1292 / 0 | 1220 / 1220 / 0 / 0 | 1234 / 1234 / 0 / 0 | trace 없음 | trace 없음 | 일치 |
| flip 키 / `lut_hit` / 팩 파일(크기 정확) | 0 | 24 / 24 / 24 | 24 / 24 / 24 | 0 | 28 / 28 / 28 | 일치 |
| `hd_pack_flip_hits/misses/rejects` | 0/0/0 | 24/0/0 | 24/0/0 | — | — | 일치 |
| PS3 stale present(px) / HD min | 없음 / 100 | 246·59·267·85·18 / 99.944 | 없음 / 100 | — | — | 일치 |
| p95 PS9/PS7/PS5/PS3 ms | 14/15/15/7 | 15/16/15/7 | 15/15/15/7 | — | — | PS3만 기록(보강) |
| 안전 7종·fallback·hresult 비0 | 0 | 0 | 0 | — | — | 일치 |
| identity_keys / invalid / refreshes | 574/0/0 | 608/0/0 | 633/0/0 | — | — | 일치 |
| identity cache bytes(유도) | 11.60 MB | **13.86 MB** | 12.98 MB | — | — | 미기록 → 보강 |
| `0x466BE0` 호출 / 전부 wrap·reject_bounds | 1585 | 1929 | 2056 | — | — | 일치 |

- **(b) 방향 — 키 단위로 입증(보강).** 반전 hit 키 76개(U1 24·U2 24·P1 28) 전부 팩 프레임 실루엣이 자기 좌우 거울과 다르다(최소 차 520 subpixel, `flip_asym_lap1183.json`). 실루엣 검사는 허용 0이므로 반전하지 않은(또는 이중 반전한) 프레임은 전부 reject됐어야 한다 → 100% hit 자체가 76키 모두의 방향 일치 증거다. work 크롭 2장(production·drag)도 열람: P1 방향 = 원본 lane, 이중 반전 없음. work의 "반전 유닛을 직접 지목 못 함" 한계는 해소.
- **(c) U1 일시 stale — H-HDU0 무관으로 귀속(보강).** lap1169 run H1(select 246·produce 59·drag 42)·D2(246·71·264)·**OFF1(팩 끔, 247·64·256)**에 같은 서명이 있다. OFF1은 팩 자체가 꺼진 대조라 팩·flip 경로와 무관한 기존 장면 의존 일시 stale이다(근본 원인은 여전히 UNKNOWN, backlog). U1의 키 경로 lookup miss 0·`hd_mask_outside_diff` 0도 같은 결론을 지지한다.
- **(e) identity cache bytes(보강).** 키 하나의 상주 바이트 = identity 사본+마스크(`cache_insert_frame_bytes`에 집계, 2wh) + HD 프레임(4wh). refresh 0·축출 경로 없음(초기화는 install 1회)이라 최댓값 = 마지막 값 = 3×`cache_insert_frame_bytes` → U1 13,855,668 B·U2 12,975,996 B ≪ 128 MiB, `identity_invalid_sources` 0. 새 run 불필요. (음영 LUT 사본 1.45 MB는 별도 할당, 더해도 ≪ 한도.)
- **(d)** U1/U2 p95 모든 상태 ≤ U0+2 그리고 ≤ lap1180 S2(14/16/14/7)+2.
- **정정 1:** "같은 digest의 tinted 키가 hit한 flip 키 8/24"는 U1 값이다(U2 16/24·P1 4/28). 사전등록 (a)의 분모 정의는 "팩이 있는 digest"이고 76/76 모두 팩 파일이 있으므로 어느 정의로도 100%.
- **공개(판정 영향 없음):** (1) 반전 키 다양성 낮음 — U1은 110×80 한 크기 24키, U2는 80×60 한 크기, P1은 4크기. (2) U0·P0의 `SYW2_G1_HD_PACK_FLIP=0` 설정은 로그에 남지 않았다(pair.sh 주석상 env 통과) — 간접 증거: 팩 env는 켜졌는데(`hd_pack_enabled` 1) flip 키 0·keyed 0·mirrored = invocations. (3) pair 모드는 mirror trace가 없어 P1 호출 수는 키 로그로만. (4) `0x466BE0`은 세 run 전부 wrap·화면 밖 — 이 장면 기준 ⑥-2 불필요, 가장자리 스크롤·대형 유닛 장면은 미관측.

## 4. 판정

**H-HDU0 `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0·정정 1·보강 3((b) 키 단위 방향 입증, (c) 기존 현상 귀속, (e) 캐시 바이트)·공개 4. 기본 켬·사용자 전달 아님(팩 env 실험 경로만). 마일스톤 경계 아님, 사용자 승인 해당 없음.

## 5. 다음 work 사전등록(Sonnet) — H-HDK0: 키·캐시 한도 실측 → 조건부 축출

**근거(`FEASIBLE`).** INBOX 19:3x ⑥의 남은 항목은 "메모리 대책(키 4096·캐시 128 MiB 한도)"이다. 키 테이블 `g_keys[4096]`은 install 때 한 번 초기화되고 축출이 없다. 키 식별에 source·aux 포인터·pal이 들어가므로 플레이 시간·유닛 종류·팀색·팔레트가 늘수록 키가 쌓인다(NG5 2분 608~633키, save006 짧은 pair 약 800키). 키 하나 평균 약 23 KB라 128 MiB보다 4096키 한도가 먼저 온다(4096×23 KB ≈ 92 MB). 한도 뒤 새 키는 `identity_invalid_sources`로 빠져 diff 미러(flip) 또는 present nearest 확장(tinted·지형 등)으로 떨어진다 → 크래시는 아니나 **장기 플레이에서 HD가 조용히 열화**한다. 지금은 증가율 실측이 없다.

**단계.**
- K-0(C, 계측만): trace에 `identity_cache_bytes`(= `g_identity_cache_bytes`)를 추가한다(호스트 테스트 1개: 키 2개 bind 뒤 값 = Σ6wh). 동작 변경 0.
- K-1(run, 실측): 장면 변화가 큰 장기 run 1회 — save006 `--terrain-scroll-hold`(또는 NG5 `--new-game-play`에 스크롤 키) 계열로 **맵을 가로지르며 ≥5분**. present마다 `identity_keys`·`identity_cache_bytes`·`identity_invalid_sources`·stale를 표본으로, 분당 키 증가율과 4096 도달 예상 시간을 계산한다. 하네스에 장기 옵션이 없으면 최소 옵션만 추가(테스트 포함).
- K-2(조건부 C): **K-1에서 keys ≥2,048이거나 선형 외삽 4096 도달 ≤60분이면** 축출을 구현한다 — 새 키가 한도에 걸리면 현재 키가 아니고 가장 오래 그려지지 않은 키(LRU, 마지막 draw tick 필드 추가)의 identity·HD·shade·LUT 사본을 해제하고 슬롯을 재사용한다(캐시 바이트 한도도 같은 경로). trace `identity_evictions`. 호스트 테스트는 컴파일 시 한도를 작게(`#ifndef G1_HD_KEY_LIMIT`) 해서 (i) 한도+1번째 키가 invalid가 아니라 축출 뒤 bind, (ii) 축출 키 재등장 시 다시 bind·팩 재적용, (iii) 현재 키·이번 present 키 축출 금지, (iv) 바이트 합 = 상주 키 Σ, 수리 전 RED·후 GREEN·변이 RED. 조건 미충족이면 `NOT_NEEDED`(근거 수치)로 닫고 K-2를 만들지 않는다.

**측정식(합격).**
- K-0: 호스트 테스트 GREEN, NG5 1회에서 `identity_cache_bytes` = 3×`cache_insert_frame_bytes`(refresh 0일 때)로 lap1183 유도식과 일치.
- K-1: ≥5분 PS3 체류·스크롤로 키 증가가 관측되고(시작 대비 증가 >0), 안전 7종·fallback·dropped 0, 증가율·외삽을 기록.
- K-2(실행 시): 축출 후 같은 run에서 `identity_invalid_sources` 0 유지(또는 축출 전 대비 감소), stale·HD min이 축출 끔 대조와 같거나 낫고, p95 ≤ 대조+2, 안전 0, save006 pair PASS(비회귀).
- 원본 보호: 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 5 GB 미만이면 run 시작 금지(현재 84 GB).
- **비목표:** 팩 화질 평가, 효과(반투명) 경로, `0x466BE0`, 기본 켬·사용자 전달, 활성 8인 부하 증명.
- **중단:** 실패 가설 2회 또는 60분. run 대기는 PID `kill -0`·`.exit` 파일(INBOX 12:47 규칙). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdk0/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** K-2 결과에 따라 ⑥ 마감 판단 → INBOX 19:3x 이후 순서(효과 후순위)는 다음 middle이 정한다. backlog 유지: U1형 기존 일시 stale(select≈246, lap1169 OFF1 포함) 원인, `0x466BE0` 가장자리 장면, lap1179 §6·lap1181 §2 공개 a~c.

## 6. 검사

- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1182 full PASS(1951 passed) 그대로다.
- `checks/safety.sh check`·CONTEXT·focused 테스트 결과는 STATUS 검증 줄에 보강한다.

## 다음 행동

work(Sonnet) H-HDK0(§5). 사용자 G1 시험 결과가 오면 최우선.

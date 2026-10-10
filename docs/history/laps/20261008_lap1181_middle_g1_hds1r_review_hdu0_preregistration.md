# 2026-10-08 | lap 1181 | G1 middle — H-HDS1r 독립 검수 · H-HDU0(⑥-1 좌우반전 유닛 키 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 코드·source 수정 0.
- 입력: lap1180 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261008_lap1181_preserved_lap1180_escalate_sol.txt` SHA256 앞 16자 `13984c88e4951010`, 보존 뒤 삭제), lap1179 사전등록 §6, lap1180 기록. INBOX 새 사용자 지시 없음(19:3x HD 그림 경로 지시 ⑥ 단계 진행).
- 원본 SHA: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` read-only MATCH(이번 회차 직접 재계산).
- 산출물: 공유 temp `20261008_lap1181_middle_review/` — `recalc_lap1181.py`(`f8f3e957…`)·`recalc_lap1181.json`(`aa625f9b…`)·`mutation_lap1181.{md,txt}`.

## 1. source 정체성

- source SHA256 앞 16자 4개가 lap1180 기록과 일치(`g1_hd_asset.c 5c82157b…`·`.h 63ef5608…`·`direct_draw_trace.c 2ea6c329…`·`test_g1_hd_pack.py a678a4e1…`). `logs/gates/lap1180-work-full-check.log`(`957a2fd0…`, 1945 passed·5 skipped) 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer` 0).
- S2 실행 DLL 소스 스냅샷(`run_S2/bridge/`) 60파일 대조: 저장소와 다른 것은 `inmm_stub.c` 1개(하네스 주입 `supply_probe_poll` 2줄, lap1178 F1 스냅샷과 같은 변환 → 정상)와 하네스 생성 `runtime_bridge.c`뿐. F1→S2 스냅샷 차이 = `g1_hd_asset.c` 3곳(enum `SHADE_REJECT_REFRESH`·이름 `refresh`·compare 불일치 분기 강등 9줄), `.h` 주석 1줄, `direct_draw_trace.c` 필드 1개 = 사전등록 R-1 범위와 정확히 일치.

## 2. 코드 검수

- 강등 분기(`g1_hd_asset.c` 1163~1171): `pack_state == PACK_HIT && is_shade_pack_writer` 일 때만 `shade_free_copies`(map·src·lut 해제) → `PACK_SHADE_REJECT` → 카운터·키 로그. `build_hd_frame`은 `PACK_UNTRIED`/`PACK_HIT`에서만 팩을 읽으므로 강등 키는 다음 재빌드부터 Scale2x(`build_scale2x`)로 간다. plain·tinted 키는 이 분기에 들어가지 않는다(refresh 시 팩 재적용 유지). 다른 identity 무효화 경로(`g1_hd_asset_reset` 전체 해제·bind 실패 해제)는 키 자체를 지우거나 `shade_free_copies`를 이미 부르므로 같은 결함 없음.
- 변이 확인(격리 사본, 저장소 무변경, `mutation_lap1181.txt`): 기준 39 passed. m1 상태 줄 제거·m2 분기 비활성·m3 refresh 카운터 제거 → 셋 다 `test_refreshed_shade_hit_key_drops_to_scale2x_but_plain_key_reapplies_its_pack` **RED**(m2 = 낡은 LUT 프레임 `block(10,10,0)==7` 실패, m3 = 이유별 카운터 실패).
- 공개(판정 영향 없음): (a) 사전등록 R-0의 "키 로그 1줄(`shade_reject`/`refresh`)"은 호스트 테스트가 단언하지 않는다(코드에는 있음). (b) `shade_lut` 해제(누수 0)도 테스트 단언 없음(코드 검토로만 확인). (c) refresh 키 로그 줄의 `selfcheck`·`mismatches`·`first_xy`는 직전 자기 검사 전역값이라 그 키의 값이 아니다(표기 결함, 경미). (d) 강등 키도 `shade_hits`에 남는다(최초 hit 누적 지표).

## 3. 런타임 재계산(새 스크립트, nearest-rank p95)

| 항목 | F1(lap1178) | S1 | S2 | work 기록 |
|---|---|---|---|---|
| `hd_pack_shade_reject_refresh` / shade_rejects 5종 | 필드 없음 / 0 | 0 / 0 | 0 / 0 | 일치 |
| shade_hits / selfcheck px | 138 / 141,312 | 201 / 203,776 | 147 / 150,528 | 일치 |
| 키 로그 shade_reject 줄 | 0 | 0 | 0 | 일치 |
| tinted lut_hit/reject | 188/2 | 187/0 | 187/2 (98.94%) | 일치(reject = lap1169 예외) |
| PS9 / PS7 / PS5 fullscreen hits = menu 호출(상태 구간 증분) | 66/157/710 = | 68/103/391 = | 70/163/750 = | 일치(work의 233·983은 누적값) |
| p95 PS9/PS7/PS5/PS3 ms | 15/16/15/7 | 14/25/25/**11** | 14/16/14/7 | S2 일치 |
| HD min PS7/PS5/PS3 | 99.709/98.949/100 | 같음 | 같음 | 일치 |
| 안전·fallback·dropped·hresult 비0 필드 | 없음 | 없음 | 없음 | 일치 |

- **정정 1:** S1 PS3 전체 구간 p95는 **11 ms**(work 기록 "PS3 p95 7"은 `metrics_ng5.py` 창별 p95의 최댓값; work 자신의 `metrics_f_S1.json` state 3도 11). F1 7 대비 +4로 S1은 PS3까지 포함해 **모든 상태가 느렸다**(PS3 ≥10 ms present 88개, S2·F1 0개; S1 PS7/PS5 present 수 103/391 vs S2 163/750). 강등 분기는 refresh 0이면 실행되지 않으므로, 전 상태 동시 지연은 환경 부하 해석을 오히려 지지한다. S1 환경 변동 판정 수용(원인 증명 아님은 그대로 공개), 합격 판정은 S2로 한다.
- F1 p95 표기: work의 F1 PS9 "14"는 floor 정의, nearest-rank는 15(어느 쪽이든 S2 ≤ F1+2).

## 4. 판정

**H-HDS1r `PASS(partial, 기술·격리)` 수용.** 판정 영향 불일치 0·정정 1(S1 PS3 p95 11)·공개 4(§2 a~d). 새 강등 경로의 실제 실행은 호스트 테스트로만 입증된다(이 장면 refresh 0, 원본 음영 표는 시작 init 1회 — lap1179 §5)는 공개 한계로 수용한다. 마일스톤 경계 아님, 사용자 승인 해당 없음.

## 5. 다음 work 사전등록(Sonnet) — H-HDU0: ⑥-1 좌우반전 유닛 `0x466B50`을 키 경로로

**근거(`FEASIBLE`).** `0x466B50`(ret 0x18, thiscall)은 tinted `0x466EA0`/`0x466540`과 같은 6인자 배치(x, y, width, height, RLE source, 리맵 LUT)이고 같은 RLE 형식(`0xFE` 건너뛰기, 그 외 = 소스 인덱스 → `lut[]`)을 오른쪽 끝부터 왼쪽으로 쓴다(`analysis/memory_maps/g1_unhooked_writers_466070_466b50_lap974.md` §3, lap975 역어셈블 정정). 지금은 H-F3 diff 미러(Scale2x 전용, 키 없음, `g1_mirror2x.c` `mirror_flip_rle`)라 팩이 적용되지 않는다. 팩 이름 `g1_hd_pack_name(digest, w, h)`에는 writer가 들어가지 않으므로, 같은 RLE source의 비반전 팩 파일을 읽어 HD에서 좌우 반전한 뒤 LUT를 적용하면 된다. 키 4096·캐시 128 MiB 한도·키별 필요 시 파일 로드는 이미 `g1_hd_asset.c`에 있다(`G1_HD_KEY_LIMIT`·`G1_HD_CACHE_BYTE_LIMIT`·`read_pack_frame`). NG5 S2에서 `0x466B50` 201회(전부 mirrored)·`0x466BE0` 1,485회(전부 `reject_bounds`·wrap = 화면 밖) → 유닛이 많은 장면이 필요하다.

**단계.**
- U-1(TDD, `tests/test_g1_hd_pack.py`): 반전 키 시나리오 — (i) 팩 HIT → 화면 HD = 팩 프레임 좌우 반전 + `lut[]`, (ii) 팩 실루엣과 반전 identity 마스크 불일치 → reject·Scale2x(반전 전 팩으로 검사하면 RED가 되는 비대칭 fixture), (iii) miss → Scale2x, (iv) 끔 env(`SYW2_G1_HD_PACK_FLIP=0`) → 기존 diff 미러 동작·수치 불변, (v) tinted 비반전 키 비회귀. 수리 전 RED·수리 후 GREEN·변이(반전 줄 제거 시 RED) 확인.
- U-2(C): `mirror_flip_rle`를 tinted와 같은 키 경로(`mirror_reinvoke`, writer `G1_FLIP_RLE`, aux = LUT 256 B)로 보내고, `invoke_original` 분기·`is_tinted_pack_writer`류 판정·팩 읽기 뒤 좌우 반전·trace 카운터(`hd_pack_flip_hits/misses/rejects`)를 추가한다. 키 경로가 거부하는 호출(guard·target·bounds·size)은 지금의 diff 미러로 그대로 처리한다. `0x466BE0`(클립 반전)은 이번 범위 밖 — 호출 수·화면 안 호출 수만 기록.
- U-3(run): save006 pair 1회(기존 H-F3 유닛 덩어리 장면, lap996/1001 기준 고정 카메라 steady stale 0) + NG5 1회(합본 팩 = lap1178 `pack_hdf1`, 대조 = lap1180 S2).

**측정식(합격).**
- U-1 RED→GREEN·변이 확인, 호스트 테스트 전부 통과.
- U-3: (a) 반전 키 생성 >0, 반전 키 중 팩이 있는 digest(같은 digest의 tinted 키가 hit한 것)의 hit율 ≥95% — 미달이면 reject 상세(`first_xy`·실루엣 차)를 기록하고 FAIL 처리; (b) 키 로그 반전 hit 1개 이상의 크롭에서 방향이 원본 화면과 같다(이중 반전 없음, 원본 lane 같은 위치 대조); (c) save006 고정 카메라 steady stale 0 유지·HD min 기준 이상·안전 7종·fallback·dropped 0; (d) p95 ≤ 대조 + 2 ms; (e) `identity_keys` ≤ 4096·identity cache bytes 최대값 기록(128 MiB 미만, 한도 도달로 인한 `identity_invalid_sources` 증가 0); (f) NG5 tinted·지형·음영·fullscreen 지표 S2 수준.
- 원본 보호: 원본 EXE·그림 SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 5 GB 미만이면 run 시작 금지(현재 90 GB).
- **비목표:** `0x466BE0` 키 경로화, 키/캐시 축출 정책(한도 도달 시), 기본 켬·사용자 전달, 화질 평가, 전투 대규모 부하.
- **중단:** 실패 가설 2회 또는 60분. run 대기는 PID `kill -0`·`.exit` 파일(INBOX 12:47 규칙). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdu0/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **그다음:** ⑥-2 `0x466BE0` 클립 반전(화면 안 호출이 관측되면) · 한도 도달 시 축출 정책. backlog 유지: lap1179 §6 목록(miss 음영 키 `shade_src` 해제, 로더 miss 슬롯 8·reject 영구 기억, tinted 클립 판정, 여러 스테이지·낮밤 팔레트 실측), 이번 §2 공개 a~c(키 로그 단언·해제 단언·refresh 줄 전역값).

## 6. 검사

- 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1180 full PASS(1945 passed) 그대로다.
- `checks/safety.sh check`·CONTEXT·focused 테스트 결과는 STATUS 검증 줄에 보강한다.

## 다음 행동

work(Sonnet) H-HDU0(§5). 사용자 G1 시험 결과가 오면 최우선.

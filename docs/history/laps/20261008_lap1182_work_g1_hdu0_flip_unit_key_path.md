# 2026-10-08 | lap 1182 | G1 work — H-HDU0 ⑥-1 좌우반전 유닛 `0x466B50` 키 경로(팩 반전 + LUT)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1181 middle 사전등록 §5(`20261008_lap1181_middle_g1_hds1r_review_hdu0_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 90 GB.
- 가설: `0x466B50`은 tinted와 같은 6인자·같은 RLE·같은 리맵 LUT를 오른쪽부터 쓴다. 키 경로(identity 두 배경 diff + aux 256 B LUT)로 보내고 로더가 같은 이름의 비반전 팩을 읽어 **좌우 반전 → 실루엣 검증 → LUT**하면 반전 유닛도 팩 HD가 된다.
- 예상 PASS/FAIL: U-1 호스트 테스트 RED→GREEN·변이 RED. U-3(a)~(f) = 사전등록 §5.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_hd_asset.c` | `is_flip_pack_writer(0x466B50)`, 끔 env `SYW2_G1_HD_PACK_FLIP=0`(tinted env와 독립), LUT 캡처·LUT 적용 분기에 flip 포함, `read_pack_frame`이 flip 키면 파일 프레임 행 좌우 반전(`flip_pack_rows`) 뒤 `g1_hd_pack_valid`(반전된 identity 마스크와 비교), 카운터 `pack_flip_hits/misses/rejects`, `g1_hd_asset_flip_key_path()`(팩 env + scale2x + 끔 아님) |
| `tools/inmm_stub/g1_hd_asset.h` | 위 접근자 4개 |
| `tools/inmm_stub/g1_mirror2x.c` | `invoke_original` 에 `G1_FLIP_RLE` 케이스, `mirror_flip_rle`: 원본 호출 뒤 `active && !clipped && !wrap && g1_hd_asset_flip_key_path()`이면 `mirror_reinvoke(writer=G1_FLIP_RLE, aux=LUT 256 B, unclipped)`; `g_reinvoke_composed`(키 ready)이면 diff 미러 생략(`keyed_calls`), 아니면 기존 diff 미러(`key_fallbacks`). 화면 밖·클립·wrap·팩 없음·끔은 이전 동작 그대로 |
| `tools/inmm_stub/g1_mirror2x.h`, `direct_draw_trace.c` | 접근자 2개, trace `flip_rle_466B50_keyed_calls`·`_key_fallbacks`·`hd_pack_flip_hits/misses/rejects` |
| `tests/test_g1_hd_pack.py` | +6 테스트(비대칭 fixture: 반전 마스크 {1,1,0,1}). 반전 hit byte·miss·bad digest·끔 env·tinted 독립·래퍼 배선·trace 필드 |

파일 SHA256 앞 16자: `g1_hd_asset.c 7efa805d4b5565c6`·`.h b48c8f230dfd1fe2`·`g1_mirror2x.c 367ebe68cb6f3c66`·`.h b993fbf78825e5ca`·`direct_draw_trace.c 8371101ae6e9f812`·`tests/test_g1_hd_pack.py f8fddbe874ed5bcc`.

## 측정 (산출물 공유 temp `20261008_lap1182_work_hdu0/`, 합본 팩 = lap1178 `pack_hdf1`)

- **U-1:** `tests/test_g1_hd_pack.py` 45 passed. 변이(`flip_pack_rows` 호출 제거) → `test_flip_writer_applies_…`·`test_flip_writer_checks_the_mirrored_silhouette…` 2건 RED, 복원 뒤 GREEN. (비대칭 fixture라 반전 전 팩으로 검사하면 실루엣 불일치 reject — 선행 RED는 구현 전에 쓰지 않고 변이로 대체: 공개.)
- **원본 보호:** 원본 EXE `b56986e0…` 전·후 MATCH(`orig_sha_before/after.txt`). game 사본 하네스 제거(prefix 보존).
- **NG5**(`--new-game-path --new-game-start --new-game-act`, 새 임의 게임·활성 8 player records 부하 증명 아님; run마다 장면이 달라 run 사이 화소 대조 불가):

| run | 반전 | flip keyed/invocations | flip hits/miss/reject | HD min | p95 | stale(PS3 창 max) | 안전·fallback·dropped | tinted·지형·음영 matched hit | keys / invalid |
|---|---|---|---|---|---|---|---|---|---|
| U1 | 켬 | 1220/1220 (fallback 0) | 24/0/0 | 99.944 | 7 | 267 (5 present, 246·59·267·85·18) | 0 | 100% | 608 / 0 |
| U2 | 켬 | 1234/1234 (fallback 0) | 24/0/0 | 100 | 7 | 0 | 0 | 100% | 633 / 0 |
| U0 | 끔(`SYW2_G1_HD_PACK_FLIP=0`) | 0 (diff 미러 mirrored 1292/1292) | 0 | 100 | 7 | 0 | 0 | 100% | 574 / 0 |

  - (a) flip 키 24개(U1·U2 각) 전부 `lut_hit`·reject 0 → 팩이 있는 키의 hit율 100%(≥95%). 같은 digest의 tinted 키가 hit한 flip 키는 8/24(나머지는 flip 형태만 있는 프레임이나 팩 파일은 있음).
  - (c) U2·U0 stale 0·HD min 100. U1에서만 PS3 5 present(≤267 px, 감소하며 소멸) 일시 stale — 같은 코드의 U2에서 재현 0, lap1169 H1(99.949)·D2(99.945)에도 flip 변경 전 같은 유형이 있었으므로 장면 의존 일시 현상으로 보되 **원인 미증명**(공개).
  - (d) p95 flip 켬 7·7 ≤ 끔 7 + 2. (f) tinted·지형·음영·fullscreen 지표 S2 수준(100%·reject 0). (e) identity_keys ≤ 633 ≪ 4096, `identity_invalid_sources` 0 → 한도 도달 없음. identity cache 바이트 최대값은 이번 추출 스크립트에서 못 뽑아 **미기록**(공개).
  - ab matched hit 0.74~0.77(U0 0.742 = 끔 대조 동일 수준, 이번 변경 영향으로 보지 않음 — 과거 수치 대조는 안 함).
- **save006 pair**(`g1_saved_scene_probe.py --hd-source scale2x --candidate-no-present-trace --candidate-no-unit-ticks`, 팩 env 설정, `pair.sh`): P1(켬)·P0(끔) 둘 다 status PASS·scene_state_equal·V2/V2s/V2q/Scale2x PASS. P1 flip 키 28개 전부 `lut_hit`, P0 flip 키 0. (이 모드는 mirror trace 상세 없음 → flip 호출 수는 키 로그로만.)
- **(b) 방향 크롭**(`crops/`): save006 production·drag 캡처에서 P1(팩 반전)·P0(Scale2x)·원본 lane(2× nearest) 같은 위치 대조 — P1 방향이 원본과 같고(이중 반전 없음), P1과 P0 차이 영역에서 원본 lane에 대한 평균 화소 차는 production 15.0 vs 16.6·drag 19.9 vs 21.1(P1 ≤ P0). selection 캡처 큰 차이는 토네이도 애니메이션 시점 차(P0 장면에 없음)로 방향 증거에서 제외. 한계: 육안 크롭 3곳, 반전 유닛만 따로 지목한 것은 아님(키 로그에 좌표 없음).

## 판정

**H-HDU0 `PASS(partial, 기술·격리)`** — U-1 GREEN·변이 RED, (a) 100%, (b) 방향 일치(크롭), (c) U2·U0 깨끗·U1 일시 stale 5 present 공개, (d)(f) 충족, (e) 키 수 충족·바이트 미기록. `0x466BE0`(클립 반전)은 비목표: NG5 호출 1,929~2,056·전부 `reject_bounds`(화면 밖·wrap), 화면 안 호출 0 → ⑥-2 불필요 관측.

## 남은 위험 / 다음

- 반전 유닛 크롭 직접 지목 못 함, U1 일시 stale 원인 미증명, identity cache 바이트 미기록, 팩 stand-in 화질 평가 아님. 기본 켬·사용자 전달 아님(팩 env 있는 실험 경로만 켜짐).
- 다음: middle(Opus) 독립 검수(키 로그·trace 재계산, 변이, 크롭). 사용자 G1 시험 결과가 오면 최우선.

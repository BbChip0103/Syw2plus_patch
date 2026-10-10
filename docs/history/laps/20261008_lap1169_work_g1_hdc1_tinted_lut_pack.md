# 2026-10-08 | lap1169 | G1 work — H-HDC1 ④-3 tinted 색 치환표(256 B) HD 팩

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). 커밋 0.
- 입력: lap1168 middle 사전등록 §4(`20261008_lap1168_middle_g1_hdt1_review_hdc1_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 19 GB(<20, 이 회차 옛 사본 없음, 실행 4회 뒤 11 GB — 이 회차 runtime prefix 1.2 GB×6 + 공유 temp 3 GB 사용, 다른 회차 산출물은 건드리지 않음).
- 가설: tinted writer `0x466540`·`0x466EA0` 출력 = `lut[원본 인덱스]`, source 포인터 = 원본 `.spr` 프레임 시작. 로더가 aux 키에서도 `(digest,w,h)` 팩 프레임(원본 인덱스)을 읽어 실루엣 검증 뒤 불투명 화소에 `lut[]`를 적용하면 원본 색 치환(나무 변형·팀색)이 유지된 HD가 나온다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…` 전후 MATCH(`orig_sha_before/after.txt`). 원본 그림은 `g1_hd_extract extract`가 읽기만. 환경: 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --new-game-path --new-game-start --new-game-act --hd-source scale2x`(lap1161·1163·1165·1167과 같은 NG5), 활성 8 player records(부하 증명 아님), 새 임의 게임, 팩·키 로그·끔 스위치만 바깥 env. 산출물 공유 temp `20261008_lap1169_work_hdc1/`.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_hd_asset.c` | aux 키 분기: writer ∈ {`0x466540`,`0x466EA0`}이고 팩 env 있고 `SYW2_G1_HD_PACK_TINTED≠0`이면 키 생성 때 aux 256 B를 키에 복사(`capture_lut`, 읽기 가능 검사 + FNV-1a == `auxiliary_digest`일 때만 `lut_valid`) → `build_hd_frame`이 같은 `read_pack_frame`(크기·실루엣)으로 HIT를 판정하고 불투명 HD 화소 `hd[i]=lut[hd[i]]`(키 0xFE 화소는 그대로). `lut_valid` 아님 = 새 상태 `PACK_LUT_REJECT`(Scale2x, `lut_rejects`). 그 밖 aux writer(`0x468CC0`·`0x4690A0`)·끔 env는 이전처럼 `skip_aux`. 카운터 4개(`lut_hits`·`lut_rejects`·`lut_key_color`(LUT 결과 0xFE인 HD 화소, 첫 HIT 때만)·`lut_nonidentity`), 키 로그 result `lut_hit`/`lut_reject`. 진단: 키 로그 `reject` 줄에 `written`·`pack_opaque`·`written_keyed`·`opaque_unwritten`·`first_xy`·`last_xy`(실루엣 불일치 크기·위치). `readable_source`→`readable_range` 일반화 |
| `tools/inmm_stub/g1_hd_asset.h` | 카운터 접근자 4개 |
| `tools/inmm_stub/direct_draw_trace.c` | trace `hd_pack_lut_hits`·`_rejects`·`_key_color`·`_nonidentity`(버퍼 200→360) |
| `tests/test_g1_hd_pack.py` | 호스트 로더 테스트 +7(LUT 적용 byte·두 writer, LUT→0xFE 키 색, 다이제스트 불일치 → Scale2x, 파일 없음 miss, 끔 env·다른 aux writer skip_aux, trace 필드, reject 줄 상세). 변이 확인: `hd[i]=lut[]` 줄을 지우면 2개 FAIL, 복원 뒤 15 PASS |

팩 도구·하네스 변경 0(`g1_hd_extract`·`g1_hd_convert convert/pack` 그대로).

## 측정

- **H-0(정적, 원본 읽기 전용 `objdump`, 공유 temp `h0_466540.txt`·`h0_466EA0.txt`):** `0x466EA0` 단일 루프 = `al=src; cmp 0xFE → skip run; else dst=[lut+al]`, 목적지 읽기 없음, 안쪽에서 viewport 클립. `0x466540`은 변형 6개(`ret 0x18`×3·`ret 0x1c`×3): 앞 3개 = 순수 `dst=lut[src]`(둘째는 홀짝 건너뜀), `0x4668xx` 변형 = **목적지를 읽는** 표 합성(`dl=dst; ... cl=[(dl<<8)+표]`). 합성 변형이 같은 키로 호출되면 identity 마스크(두 배경 diff)가 실루엣과 달라져 `REJECT`로 안전 폴백하고 hit 비교가 막는다. 이번 run에서는 `0x466540` matched 키 전부 `lut_hit`(합성 변형 reject 관측 0).
- **팩(B형):** `g1_hd_extract extract --image-dirs fnt,char`(26,441프레임) → 원본 팔레트 ×4 RGB를 가장자리 복제 + 바이큐빅 2배(`bicubic_edge.py`) → `convert`(위반 0, 26,441/26,441) → `pack --image-dirs fnt,char`(18,279파일, `nonconforming` 0) = `pack_tint`. `pack_c` = lap1167 `pack_t2`(A/B·지형) + `pack_tint` 덮어쓰기(겹침 602, 이 중 576은 lap1165 비-가장자리 복제본 → 가장자리 복제본으로 교체) = 25,634파일.
- **C-0(오프라인, `c0.json`):** lap1167 T3·T4·C1 키 로그 tinted 키 → `pack_c` 대응(이름 존재·크기 `4wh`) 143/146=**97.95%**·114/117=97.4%·116/119=97.5%(writer별 `0x466540` 100%·`0x466EA0` 92~94%). **`FEASIBLE`(≥80%).**
- **C-1 NG5(전부 크래시 0·안전 7종 0·fallback 0·dropped 0·scale2x validator PASS(`hd_mask_outside_diff` 0)·`identity_invalid_sources` 0):**

| run | tinted | PS3 HD min | p95 | hits/misses/rejects/skip_aux | lut_hits/lut_rejects | lut nonidentity | tinted matched hit(`0x466540` / `0x466EA0`) | A/B·지형 matched hit |
|---|---|---|---|---|---|---|---|---|
| H1 | 켬 | 99.949 | 8 | 348/31/**2**/151 | 187/0 | 187 | 126/126 · 61/63 | 100%·100% |
| H2 | 켬 | 100 | 7 | 353/24/**2**/153 | 197/0 | 197 | 136/136 · 61/63 | 100%·100% |
| OFF1 | **끔**(`SYW2_G1_HD_PACK_TINTED=0`) | 99.947 | 7 | 152/28/0/342 | 0/0 | 0 | 0 (aux 키 전부 skip_aux) | 100%·100% |
| D1 | 켬(진단 빌드) | 100 | 7 | 361/31/2/159 | 209/0 | 209 | 134/134 · 75/77 | 100%·100% |
| D2 | 켬(진단 빌드) | 99.945 | 8 | 332/24/**0**/209 | 170/0 | 170 | 88/88 · 82/82 | 100%·100% |
| D3 | 켬(진단 빌드) | 100 | 7 | 358/31/2/150 | 206/0 | 206 | 134/134 · 72/74 | 100%·100% |

  - H1·H2 = 사전등록 켬 2 run(진단 코드 추가 전 빌드), D1~D3 = 진단 코드(키 로그 reject 상세) 추가 뒤 같은 입력 반복(H1·H2·D1·D3 reject 2, D2 0). **켬 두 run 모두 `lut_rejects` 0, HD min ≥99.9, p95 ≤9, tinted writer별 matched hit 96.8~100%(≥90%), A/B·지형 100% 유지 → 사전등록 합격식 충족, 단 `hd_pack_rejects` 0은 H1·H2에서 미충족(2)**(아래).
  - 끔 대조(OFF1)는 tinted aux 키 342개 전부 `skip_aux`·`lut_hits` 0 → 끔 스위치가 이전 동작을 복원함을 입증. `hd_pack_lookup_blocks`: 끔 30.6M → 켬 236~278M(tinted 기여).
  - **reject 2 = 한 키**(`0x466EA0` 96×112 `fnt/tree_plus.spr` 프레임 0, `h44c611f6`, src `0x0519A300`)가 두 에폭에 기록된 것. 진단(D1·D3): identity `written` 5,257 vs 팩 불투명 5,261, `written_keyed` 0, **`opaque_unwritten` 4 = 픽셀 (51,104)~(53,105), 스프라이트의 마지막 불투명 두 행**(원본 1x 마스크 직접 확인: 행 104 = 열 51·52, 행 105 = 열 52·53, 그 아래 불투명 0). 엔진이 그 맨 아래 두 행을 쓰지 않은 것 = viewport 아래 가장자리 클립 때 identity 마스크가 잘린 것으로 **추정(미확인)**, 이 키의 다른(aux 다름) 호출은 `lut_hit`. 실루엣 검증이 막아 Scale2x로 폴백(화질만 이전과 같음, 안전 지표 0). D2에서는 같은 키가 reject 없이 지나감(scene 의존). 검증기를 완화하지 않았다.
- **C-2 의미:** 비항등 LUT HIT 키 모두(187/197/170…) = 켬 run의 `lut_hits` 전부가 항등이 아닌 표(시험 조건 ≥1 충족). `lut_key_color` 0(HIT 키의 LUT가 0xFE를 만든 경우 없음; 호스트 테스트로 쓰기·집계 동작 확인).
- **C-3 크롭 직접 열람(`crops/`):** OFF1(위)·D3(아래)는 같은 맵·같은 카메라(`ps3_start` 화소 차 8.4%는 팩 유무 질감 차이). `trees_OFF_top_ON_bottom`: 황금색 나무 군락이 켬에서도 같은 색조·같은 위치로 유지(LUT 미적용이면 원본 녹색이어야 함), 질감만 바이큐빅 stand-in으로 부드러움. `units_OFF_top_ON_bottom`: 건물 지붕 오렌지·**팀색 파랑 지붕 타일**이 켬에서 같은 색·같은 자리. 실루엣 테두리 밝은 띠 관측 못 함(가장자리 복제 팩). `area3_OFF_top_ON_bottom`도 저장. 한계: 팀색은 건물 1곳·유닛 팀색은 장면에 없음.
- **메모리:** 키 수 켬 532·끔 522(+10), `cache_insert_frame_bytes` 켬 3.86~4.56 MB·끔 3.82 MB, 정적 키 배열 +≈1 MB(`G1HdKey`에 256 B LUT·플래그, 4096키).
- **원본 보호:** 원본 EXE SHA 전후 MATCH, game 사본 하네스가 삭제(prefix·manifest·output 보존, `local/runtime/lap1169_hdc1_*`).

## 판정

**H-HDC1 `PASS(partial, 기술·격리)`** — C-0 FEASIBLE(97.9%), 켬 2 run(H1·H2) 크래시·안전·fallback·dropped 0·scale2x 바깥 변화 0·`lut_rejects` 0·HD min ≥99.9·p95 ≤9·tinted writer별 matched hit ≥96.8%·A/B·지형 100% 유지·비항등 LUT 적용, 끔 대조 입증, 크롭 색 유지. 단서 4건: (1) `hd_pack_rejects` 0 미충족(2 = 한 키, tree_plus 프레임 0 identity 마스크 아래 두 행 4 px 누락, 클립 추정 미확인, 폴백으로 무해, D2는 0) → middle 판정 필요; (2) H1·H2는 진단 코드 추가 전 빌드(진단은 key log 문자열만 추가); (3) 화질 평가 아님(바이큐빅 stand-in), 팀색 크롭은 건물 1곳; (4) 합성 변형(`0x466540` 0x4668xx, 목적지 읽기)은 이번 run에서 키로 관측되지 않았고 안전 폴백 가정은 코드 구조(실루엣 검증·hit 비교)에 의존. 기본 켬·사용자 전달·④-4 음영 지형·checker·유닛 `0x466B50`은 비목표 그대로.

## 검사

- `make lint`·`make typecheck` PASS(구현 후). 목표 테스트 `tests/test_g1_hd_pack.py`(15)·`test_g1_mirror2x.py`·`test_g1_hd_convert.py` PASS. 전체 `make check` 결과는 STATUS 검증 줄에 보강한다.
- 변경 파일 SHA256(앞 16자): `tools/inmm_stub/g1_hd_asset.c` `b2876689781bd67d`·`g1_hd_asset.h` `fc5533f6c3c80377`·`direct_draw_trace.c` `979f0db523255e88`·`tests/test_g1_hd_pack.py` `bf12bb3c5ebf67d4`.
- 측정 스크립트(공유 temp `20261008_lap1169_work_hdc1/scripts/`): `run.sh`·`seq.sh`·`metrics_c.py`·`c0.py`·`ps3.py`·`bicubic_edge.py`(앞 둘 + metrics는 lap1167 것 수정본).

## 다음 행동

middle(Opus) 독립 검수 → ④-4 음영 지형(aux = 화소별 음영, 렌더러 팔레트 체인) 사전등록 또는 reject 키 판정. 검수 항목: (a) `capture_lut`·`build_hd_frame` LUT 적용 코드와 테스트, (b) H1·H2·OFF1·D1~D3 raw(키 로그·trace) 재계산, (c) reject 키(tree_plus 프레임 0, 마지막 두 행 4 px) 판정·클립 가설 확인 필요 여부, (d) 크롭 열람, (e) H-0 변형 구조(합성 변형)와 안전 폴백. 사용자 G1 시험 결과가 오면 최우선.

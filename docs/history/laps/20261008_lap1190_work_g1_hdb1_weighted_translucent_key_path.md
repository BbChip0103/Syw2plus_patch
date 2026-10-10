# 2026-10-08 | lap 1190 | G1 work — H-HDB1: 효과(반투명) ② `0x467580` 가중표 혼합 HD 키 경로

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1189 middle 사전등록 §7(`20261008_lap1189_middle_g1_hdb0_review_hdb1_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 59 GB, 끝 41 GB(run 11개 + pair 2개).
- 가설: `0x467580`은 `0x4672E0`과 스트림·행 규칙이 같고 채널 결합만 `t = (int16)T[(d_채널<<6)+s_채널]`(renderer `+0x41CA0`, 64×64) → `inverse[(((t0<<6)+t1)<<6)+t2]`다. 그래서 디코더·자기 검사·HD 적용 골격을 결합 함수만 바꿔 공유하면, 구름/연기 같은 반투명 효과를 (a) 1x 원본 출력으로 자기 검사하고 (b) identity 키 장부 no-aux 키로 팩 hit이면 (c) 같은 식으로 HD 목적지와 팩 그림을 섞어 diff 미러 위에 덮을 수 있다.
- 예상 PASS/FAIL: 사전등록 §7 측정식(B1-0 변이 RED·B1-1 호스트에서 원본 산술 재현+변이 RED·B1-4 keyed ≥95%·자기 검사 불일치 0·안전 0·p95 ≤ 끔+2·stale ≤ 끔·pair PASS, 호출 <300/run이면 표본 부족).

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_blend_key.h` | `weights`(NULL = `0x4672E0` 평균) 인자를 `g1_blend_pixel`·`g1_blend_selfcheck`·`g1_blend_apply_hd`에 추가. 새 `g1_blend_weighted_offset`(채널 인덱스 ≥4096 또는 오프셋 <0·≥0x40000이면 거부, 부호 있는 `t` 포함)·`g1_blend_crop`(스트림 창 잘라내기, DLL이 CRT 없이 링크되므로 `no-tree-loop-distribute-patterns`로 memcpy 치환 차단) |
| `tools/inmm_stub/g1_mirror2x.c`·`.h` | `blend_rle_key_apply`를 공유 코어 `blend_key_apply(renderer, writer, weighted, rle, 스트림 사각형, 화면 창, buffer, stride, before, stats)`와 `blend_key_snapshot`(원본 호출 전 covered·HD 목적지 창 복사)으로 교체. 카운터를 `G1BlendKeyStats`로 묶고 `0x4672E0`·`0x467580` 두 벌(`g_blend_rle_key`·`g_blend_wrle_key`, accessor `g1_mirror2x_blend_wrle_*` 5개). `mirror_blend_wrle`: diff 미러(타일) 성공 뒤 `key_try`면 `blend_key_apply(…, TRUE, …)`; 스트림 사각형 w·h > 800×600이면 폴백으로 계수. 키는 스트림 전체 사각형, 자기 검사·그리기는 화면 교집합만(창 밖은 클립, 팩은 `frame + 2·oy·W + 2·ox`로 읽음) |
| `tools/inmm_stub/g1_hd_asset.c`·`.h` | 팩 hit/miss/reject 블렌드 카운터가 두 writer를 함께 센다(`G1_HD_BLEND_WRLE 0x00467580`), 주석 갱신 |
| `tools/inmm_stub/direct_draw_trace.c` | 트레이스 `blend_467580_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels` |
| `tools/inmm_stub/Makefile` | `_inmm.dll` 의존 목록에 `g1_blend_key.h` 추가(lap1188 누락 — 헤더만 바뀌면 재빌드 안 됨) |
| `tests/test_g1_blend_key.py` | 호스트 4(가중 산술 전 쌍·평균과 다름·자기 검사/적용/창 자르기)+정적 3(B1-0 x1·x3, 가중 래퍼 계약, 트레이스·카운터) 추가, 기존 테스트는 새 시그니처·카운터 이름에 맞춤. 총 15 |

파일 SHA256 앞 16자(최종): `g1_blend_key.h 5db2713b1aaa7596`·`g1_mirror2x.c 32fd70e88de540ab`·`.h edef1cbcb432e99f`·`g1_hd_asset.c 1b1d13d340b284b5`·`.h 4a6e72212cf67d56`·`direct_draw_trace.c 6ef3baaceab4683a`·`Makefile 60881d0cae1105df`·`tests/test_g1_blend_key.py 8b626628b912a83a`. 첫 run 시작 이후 `tools/`·`patches/` 소스 변경 0(`find -newer`).

## B1-0·B1-1 (정적·호스트)

- 원본 `0x467580..0x4676BD` 역어셈블(EXE SHA `b56986e0…` 전후 MATCH): `ebp = ecx+3·d`, 채널 값은 `renderer+0x419A0+3·idx+채널`(6비트 팔레트), `t_k = movsx word [ecx + ((pal_d[k]<<6)+pal_s[k])·2 + 0x41CA0]`, `edx = ((t0<<6)+t1)<<6`, 결과 `byte [ecx + edx + t2 + 0x19A0]`. 목적지 d 먼저(`edi+edx`), 스트림 s, `FE n` 건너뛰기·행은 폭에서 끝(`0x4672E0`과 같음). 사전등록 §6의 "표는 64×64 int16 `(d<<6)+s`"는 **d·s가 팔레트 인덱스가 아니라 채널 값**이라는 점만 정정(인덱스로 읽으면 표 범위를 넘는다).
- B1-0: x1(키 호출 제거)·x3(자기 검사 실패 뒤 진행) 포함 변이 12종 모두 RED(c1 크기 한도 제거·w1 가중표 무시·w2 창 오프셋 무시·w3 가중 플래그 거짓·w4 스냅샷 제거·h1 음수 오프셋 허용·h2 인덱스 범위 제거·h3 시프트 6→5·h4 d/s 교환·h5 crop y 무시). 현재 GREEN.
- B1-1: 호스트 테스트가 원본 산술을 별도로 재현(부호 있는 `t` 포함, 일부 오프셋 음수/범위 밖)해 256×256 전 쌍에서 결과·거부가 일치함을 확인.

## B1-3 귀속(키 로그 digest → `.spr`)

E0(빈 팩, 키 시도) 14키 → 전부 `fnt/CLOUD.spr`(20프레임 160×120)의 프레임 0~14 스트림 offset에서 FNV-1a 128B 직접 재계산 일치. 전 run·pair 키 로그의 `0x467580` digest **64개 전부**(`/tmp` 스캔 `missing []`)가 6개 파일에 귀속됐다: `groundfiresmoke.Spr` 19(104×80)·`CLOUD.spr` 14(160×120)·`smoke0.spr` 10(60×45)·`groundfire.Spr` 9(118×70)·`tornado.SPR` 8(330×200, save006 pair 장면)·`exp6.spr` 4(170×120). **CLOUD 프레임 4·5는 앞 128바이트가 같아 digest `e88d0c4c`가 충돌**하고 두 프레임 그림이 달라 팩 이름 하나로 둘 수 없다(6개 파일 팩 기준 충돌 이름은 이 하나와 `groundfiresmoke.Spr` 쪽 1건 = 2건, 5개 파일 `pack_wblend2`는 1건) → 충돌 이름은 팩에서 뺐다(잘못된 HD를 그리지 않게). 스탠드인 팩 = 6개 파일 프레임을 bicubic 2배 → 팔레트 양자화 → 실루엣 강제(`scripts/make_wblend_pack.py`, 저장소 밖; 변종 marker=R/B 맞바꿈, red=G·B/4).

## 실행 (공유 temp `20261008_lap1190_work_hdb1/`, 하네스 `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`, PS3 약 300 s)

- **dwell 60→56:** 첫 켬 run K1은 dwell 60에서 present 이벤트가 트레이스 한도(8,192)에 먼저 닿아 `mirror2x_metrics`가 잘렸다(`failed_K1_event_cap`, 드래그 이동 effect False와 겹침). E0(dwell 60)은 한도 직전(7,082 present)에 걸쳐 우연히 기록됐다. 이후 run은 dwell 56(PS3 301~305 s)로 고정. K2 첫 시도는 이 판단으로 중단(내 프로세스만 종료, game 사본 삭제, 디렉터리는 `aborted_K2_dir`로 보존).
- 시작 맵 갈래가 run마다 다르다(identity_keys ≈ 778 / ≈ 1,250~1,320). 구름·연기 호출 수가 갈래에 따라 0~2,061로 크게 달라 같은 갈래 끔 대조를 맞추지 못했다.

| run | 팩 | PS3 present·s | `0x467580` 호출(clipped) | keyed | 폴백 | 자기 검사 불일치 / px | p95 | PS3 최대 stale(초:px) |
|---|---|---|---|---|---|---|---|---|
| E0 | 빈 팩(키 시도만) | 6,110·305 | 2,061(1) | 0 | 2,061(팩 miss) | **0** / 24,343,859 | 6 | 없음 |
| K1 | `pack_cloud`(CLOUD 14키) | 6,031·302 | 24(0) | 24 | 0 | 0 / 286,424 | 6 | 없음 |
| K2 | `pack_cloud` | 6,032·302 | 1,428(110) | 1,049(73.5%) | 379 | 0 / 14,589,584 | 6 | 141.1:2·225.4:2 |
| K3 | `pack_wblend`(4파일) | 6,104·305 | 1,190(1) | 1,033(86.8%) | 157 | 0 / 14,059,032 | 6 | 없음 |
| K4 | `pack_wblend` | 5,914·302 | 21(0) | 21 | 0 | 0 / 249,095 | **12** | 141.3:2·225.5:2 |
| K5 | `pack_wblend3`(6파일) | 5,957·302 | 0 | 0 | 0 | — | 8 | 13.3:64·14.3:71·15.2:266·15.3:60+79 |
| K6 | `pack_wblend3` | 5,997·301 | 401(7) | 360(89.8%) | 41 | 0 / 3,555,876 | 7 | 없음 |
| M1 | `pack_cloud_marker`(R/B) | 6,032·302 | 161(0) | 137 | 24 | 0 / 1,902,365 | 6 | 없음 |
| R1 | `pack_wblend2_red`(5파일) | 6,030·301 | 735(563) | 634(86.3%) | 101 | 0 / 6,064,767 | 6 | 없음 |
| O1 | 끔(`SYW2_G1_HD_PACK_BLEND=0`) | 6,030·301 | 20(0) | 0 | 0 | — | 6 | 없음 |
| O2 | 끔 | 6,037·302 | 589(98) | 0 | 0 | — | 6 | 2 |
| pair PB | `pack_cloud` save006 | — | (트레이스 metrics 없음) | 키 로그 `tornado` 330×200 8키 miss(팩에 파일 없음) | — | — | — | status **PASS**, scene_state_equal true, V2/V2s/V2q/Scale2x/input_effect/minimap PASS |
| pair PB2 | `pack_wblend2`(+tornado) | — | (같은 이유) | 키 로그 `tornado` 330×200 8키 전부 **hit** | — | — | — | status **PASS**, 동일 게이트 전부 PASS |

- **자기 검사 불일치 0:** 전 run 합 호출 6,630(끔 O1·O2의 609 제외 6,021)·자기 검사 픽셀 65,051,002(화면 교집합 불투명 픽셀) 전부 원본 1x 출력 = `T` 결합식. clipped 호출(R1 563·K2 110·끔 O2 98·K6 7)이 많아 창 자르기 경로도 같은 식으로 검증됐다.
- **keyed 비율:** 켬 run 중 호출 ≥300인 K2·K3·K6·R1·E0·M1(161은 제외): K3 86.8%·K6 89.8%·R1 86.3%는 **사전등록 ≥95%에 literal 미달**. 폴백은 전부 (a) digest 충돌 `e88d0c4c`(K3 157·K6 41 전부, 충돌 키를 뺀 나머지 키는 K3 1,033/1,033·K6 360/360 = 100%), (b) 그 run 팩에 파일이 없던 키(K2: exp6·groundfire·smoke0, R1: groundfiresmoke 104×80) 때문이다. 키 경로 결함이 아니라 **digest(앞 128B)가 서로 다른 프레임을 구별하지 못하는 장부 설계 한계**다.
- **p95:** 켬 6·6·6·7·6·6(K1·K2·K3·K6·R1·M1) ≤ 끔 6+2 충족. 초과 두 건: K4 12(첫 90 s의 present 중 약 20%가 10 ms 초과, 이후 0, 호출 21개뿐 — 같은 시각 내가 호스트에서 팩 생성 스크립트를 돌려 CPU 경합 가능성, 확정은 아님), K5 8(호출 0). 둘 다 이 경로 호출과 무관(호출 ≤21).
- **stale:** 141·225 s의 2 px 쌍(K2·K4·끔 O2 최대 2)은 lap1187이 확정한 클립 반전 가장자리 기존 현상(끔과 같은 규모). K5의 13.3~15.3 s 군집(최대 266 px)은 `0x467580` 호출 0인 run이고 lap1185 E1(13.3 s 59·15.3 s 264)과 같은 기존 서명이다.
- **색 반영 확인:** R1(`pack_wblend2_red`) `ps3_start.png`(공유 temp `evidence_R1_red_cloud_ps3_start.png`)에서 화면 오른쪽 가장자리 구름이 **붉게** 그려진다(K2의 같은 부류 구름은 흰색). 교체한 HD 그림이 가중표 혼합을 거쳐 실제 화면에 들어간다는 육안 증거. 같은 갈래 끔 대조가 없어 픽셀 비교는 못 했다(구름은 시간·맵에 따라 위치가 다르다). M1(R/B 맞바꿈)은 구름이 회백색이라 색 변화가 없어 판별력이 약하다(그래서 R1을 추가).
- **원본 보호:** EXE SHA `b56986e0…` 전·후 MATCH(`orig_sha_before.txt`·`orig_sha_after*.txt`). `local/runtime/lap1190_hdb1_*`의 `game` 사본은 하네스가 run 종료 때 삭제(중단 K2 사본 1개는 수동 삭제 후 확인), prefix·manifest·output 보존.

## 판정

- **B1-0 PASS · B1-1 PASS**(변이 12/12 RED, 256×256 전 쌍 원본 산술 일치) · **B1-2 PASS(기술)**: 키 시도·자기 검사·폴백 무해성(E0 호출 2,061 전부 폴백 시 diff 미러 결과 유지, 안전 0, 불일치 0) · **B1-3 PASS**(관측 digest 64개 전부 6개 `.spr`에 귀속, 충돌 이름 2건 식별) · **B1-4 PASS(partial)**: 자기 검사 불일치 0, 안전 0, pair PB·PB2 PASS, 켬 p95 ≤ 끔+2(예외 2건은 호출 무관), stale ≤ 끔, 색 반영 육안 확인, 호출 ≥300 run 6개(E0·K2·K3·K6·R1 + 끔 O2). **keyed ≥95% literal 미달**(86~90%, 원인 = digest 충돌·팩 미포함 파일).
- 전체 `PASS(partial, 기술·격리)` 후보. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 한계·공개

1. keyed 비율 literal 미달(위). 충돌 키(CLOUD 프레임 4·5, `groundfiresmoke.Spr` 1건)는 이름 규약(앞 128B 해시)이 구별하지 못해 팩으로 둘 수 없고 항상 diff 미러로 돌아간다. 해결 선택지(이름에 스트림 길이/전체 해시 추가, 키 장부 변경)는 팩 규약 변경이라 이번 범위 밖 — middle 판단.
2. 팩 그림은 bicubic stand-in(경로 검증용)이며 실제 업스케일 화질 평가가 아니다. 효과 파일은 6개만 귀속(그 밖의 `fnt/*.spr`가 `0x467580`을 쓰는지는 이번 장면에서 관측 못 함).
3. 같은 갈래 끔 대조 run이 없다(맵 비결정). 끔 O1(호출 20)·O2(589)는 p95·stale·keyed 0 용도만 쓴다.
4. K4 p95 12는 호스트 CPU 경합 가능성(확정 아님). K5의 13~15 s stale은 호출 0 run의 기존 서명.
5. pair 트레이스에는 `mirror2x_metrics`가 없어(`--candidate-no-present-trace`, lap1182 P0 기존) keyed 카운터 대신 키 로그 hit로 확인했다. 대형 330×200 호출(tornado)이 키 경로를 실제로 탔는지는 카운터가 아니라 hit·게이트 PASS로만 간접 확인.
6. 정적 테스트 일부는 문자열 계약(변이 RED 확인).
7. `0x467B00`·`0x4685C0`·`0x467FD0`은 미착수(다음 순서).

## 다음 행동

middle(Opus)이 H-HDB1을 검수해 `PASS(partial, 기술·격리)`·keyed literal 미달(충돌) 처리를 판정하고, 반투명 다음 writer(`0x467B00` → `0x4685C0` → `0x467FD0`)를 사전등록한다. 사용자 G1 시험 결과가 오면 최우선.

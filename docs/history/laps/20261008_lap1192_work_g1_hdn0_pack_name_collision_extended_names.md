# 2026-10-08/09 | lap 1192 | G1 work — H-HDN0: 팩 이름 충돌 해소(구별 접두 길이 확장 이름)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1191 middle 사전등록 §7(`20261008_lap1191_middle_g1_hdb1_review_hdn0_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 41 GB, 끝 34 GB(run 7개).
- 가설: 충돌은 팩 **이름**(앞 128 B digest)에서만 생기므로, 충돌 이름마다 구성원 스트림 범위 이내의 접두 길이 L로 FNV-1a를 다시 해서 `h<d8>_<w>x<h>.amb`(L) + `h<d8>_<w>x<h>_<L>_<p8>.idx8`로 가르면(오프라인 674/677), 엔진은 기본 이름이 없을 때만 그 마커를 열어 키당 1회 확장 이름을 만들어 같은 크기·실루엣 검증으로 읽을 수 있다.
- 예상 PASS/FAIL: 사전등록 §7(N-0 변이 4종 RED · N-3 변이 RED · N-4 ≥674/677 · N-5(i) keyed ≥95%·`e88d0c4c` 두 프레임 hit·불일치 0·안전 0·p95 ≤ 끔+2 · (ii) pair PASS · (iii) 충돌 키 확장 hit 비율).

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tests/test_g1_blend_key.py` | N-0: lap1191 생존 변이 n3(crop x 오프셋)·n11(`keyed_pixels` 누적)·n12(크기 한도식)·n13(디코드 한도식)을 막는 정적 단언 2개 추가(총 17) |
| `tools/inmm_stub/g1_hd_pack.h` | 확장 이름 규약: `G1_HD_PACK_EXT_MIN/MAX`(129/65536), `g1_hd_pack_stem`·`g1_hd_pack_marker_name`·`g1_hd_pack_ext_name`. 길이 루프는 DLL이 CRT 없이 링크되어 `strlen`으로 치환되지 않게 `no-tree-loop-distribute-patterns`(첫 빌드가 `strlen` 미정의로 실패해 추가) |
| `tools/inmm_stub/g1_hd_asset.c`·`.h` | `read_pack_frame`: 기본 이름 파일이 없을 때만(`note_missing_file` 뒤) `open_extended_pack_file` — 같은 pal 디렉터리의 `.amb`(4 B LE, 129..65536)를 열고 `readable_range(source, L)`이면 **마지막 begin의 소스 포인터**(`g_current_source`; 키는 32비트만 보관)에서 L바이트 FNV-1a로 확장 이름을 만들어 같은 크기·실루엣 검증으로 읽음(flip·LUT·음영 후처리는 기존 그대로). 끔 env `SYW2_G1_HD_PACK_EXT=0`. 카운터 `ext_hits/ext_misses/ext_rejects`(마커 없음 = 일반 miss로 세지 않음, 마커 불량 = miss + ext_rejects, 확장 파일 없음 = ext_misses, 실루엣 불일치 = reject + ext_rejects) |
| `tools/inmm_stub/direct_draw_trace.c` | present 트레이스 `hd_pack_ext_hits/misses/rejects` |
| `tools/g1_hd_convert.py` | `pack`: 1x 그림 충돌 이름마다 구성원 스트림 범위(오프셋 표상 다음 시작까지)의 최솟값 이하에서 L = 256, 512, …, 최소 범위를 차례로 시도해 모든 그림이 서로 다른 p8을 갖는 가장 작은 L 선택(`_split_by_prefix`). 마커·확장 파일은 HD가 있는 그림이 있을 때만 쓰고(같은 p8에 다른 HD = `hd_conflicts`, 쓰지 않음), 831폭 패널 이름은 확장하지 않음. `digest_index.json`에 `extended`, 보고서에 `extended_names/frames/lengths/files`. HD 불일치 충돌(같은 1x, 다른 HD)은 기존대로 쓰지 않음 |
| `tests/test_g1_hd_convert.py` | 기존 4개를 새 의미로 갱신(f1/f2는 이제 L=160으로 분리) + 신규 9(후보열·범위·접두 해시·C 헤더와 이름 텍스트 일치(gcc 컴파일)·최소 L 선택·분리 불가 쌍·패널 제외·HD 불일치). 총 43 |
| `tests/test_g1_hd_pack.py` | 호스트 로더 시나리오 `ext_*` 7개(hit·기본 이름 우선·끔·마커 없음·확장 파일 없음·마커 불량·실루엣 불일치) + 접두 길이 정확성 + 배선 정적 테스트. 총 69 |

파일 SHA256 앞 16자(최종): `g1_hd_pack.h 526ecfebe1900138`·`g1_hd_asset.c 1c648f2398582cbb`·`.h d92c7798a1d25fd1`·`direct_draw_trace.c e306ea68eac8260f`·`g1_hd_convert.py fcea3f374384618c`·`test_g1_hd_pack.py 348cb5b476987346`·`test_g1_hd_convert.py 5ada57fda764a610`·`test_g1_blend_key.py 53477c5481a5e4b4`·`_inmm.dll d4ec493ec2956a6d`. 첫 run 시작 이후 `tools/`·`patches/`·`tests/` 소스 변경 0(`find -newer`, 빈 출력).

## 측정

**N-0/N-3 변이(격리 되돌림 확인):** C 로더 변이 7종(접두 길이 무시 128 B·`.amb` 열기 건너뜀·길이 −1·끔 env 무시·읽기 가능 검사 제거·최소 길이 1·ext_rejects 오계수) + 우선순위 반전 1종 = **8/8 RED**(범위 검사 제거는 호스트 shim이 항상 읽기 가능이라 정적 단언이 잡음). 도구 변이 5종(후보 역순·분리 검사 제거·후보 상한 `<`·패널 제외 제거·마커 엔디언) **5/5 RED**. N-0 네 변이는 텍스트 단언이라 해당 식이 바뀌면 RED. 변이 후 소스는 원본과 `diff` 일치 확인.

**N-4(오프라인, `pack --dry-run`, char·tile·BattleSpr·portrait·fnt·yfnt, imjin2 pal, 공유 temp `20261008_lap1192_work_hdn0/pack_dry/cecc4681/digest_index.json`):** 충돌 이름 677 → **확장 674 / 남은 3**(`h150e1aec`·`h2b9b3809`·`h2f6cbf38` 모두 `86×60`, 106프레임), 확장 프레임 4,506. L 분포: 256 = 263, 512 = 175, 1024 = 77, 2048 = 17, 4096 = 5, 8192 = 3, 나머지는 구성원 최소 범위(160~12173, 대부분 1 이름씩). lap1191 middle 오프라인 수치(674/677, 263/175/77)와 일치.

**N-5(실게임 격리 run, 하네스 `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`, `scripts/run.sh`·`seq1.sh`·`seq2.sh`, `_inmm.dll` d4ec493e…):** 팩 `pack_ext`(= 도구 `extract`·`draft`·`pack`으로 만든 6개 효과 파일 `fnt/CLOUD`·`exp6`·`groundfire`·`groundfiresmoke`·`smoke0`·`tornado`의 team-safe 초안, bicubic stand-in이며 업스케일 화질 아님; 마커 2개 `he88d0c4c_160x120.amb`(L=12173)·`h1c5411c5_104x80.amb`), 팩 `pack_ng5`(위 6개 + NG5 키 로그에서 충돌 이름으로 나온 tile `.ytl`·`fnt` 30개 파일, 마커 84개).

| run | 팩·env | PS3 present·s | `0x467580` 호출(clipped) | keyed | 폴백 | 자기 검사 불일치/px | p95 | stale 최대(초:px) | ext hit/miss/reject |
|---|---|---|---|---|---|---|---|---|---|
| X1 | `pack_ext` | 6,031·301 | 292(10) | **292(100%)** | 0 | **0** / 693,695 | 6 | 225.3:92(쌍봉 79/92, 클립 반전 가장자리 기존 현상) | 2 / 0 / 0 |
| X2 | `pack_ext` | 6,032·302 | 824(97) | **824(100%)** | 0 | **0** / 9,691,280 | 6 | 13~15 s 군집 최대 255(기존 서명) | 2 / 0 / 0 |
| Q1 | `pack_ext`, `EXT=0` | 6,037·302 | 63(6) | 50(79.4%) | 13 | 0 / 744,397 | 6 | 없음 | 0 / 0 / 0 |
| T1 | `pack_ng5` | 6,037·302 | 450(3) | **450(100%)** | 0 | **0** / 5,088,969 | 6 | 없음 | **127 / 0 / 0** |
| T0 | `pack_ng5`, `EXT=0` | 6,105·305 | 10(0) | 10 | 0 | 0 / 117,364 | 6 | 13~15 s 군집 최대 259·80.0:90(기존 서명) | 0 / 0 / 0 |
| pair PX | `pack_ext` save006 | — | — | 키 로그 `0x467580` 8키 hit | — | — | — | — | — |

- **N-5(i) 합격:** X1·X2 `0x467580` 화면 안 호출 keyed **100%**(≥95%, 분모 = 6개 파일 귀속 키 전부; 0x467580 키 32/32·15/15 hit). `e88d0c4c`(160×120, CLOUD 프레임 4·5)는 **두 프레임 모두 hit**(`ext_hits 2` 두 run 모두), 같은 팩으로 끔(Q1)이면 두 키 모두 miss·폴백 13(79.4%) — 같은 팩에서 확장 이름의 효과를 직접 대조(장면 갈래가 달라 호출 수는 다름). 자기 검사 불일치 0, 안전 7종(`fallback`·`hresult`·`identity_invalid_sources`·`scale2x_palette_violations`·`identity_key_mismatches`·`viewport_restore_failures`·`clip_replay_mismatches`) 전부 0, p95 6 ≤ 끔(lap1190 O1·O2 6)+2, stale는 끔 run(T0·Q1 이전 lap1190 O2)과 같은 서명이며 ext와 무관(T0은 ext 끔인데 13~15 s 군집 259, X1 225 s 쌍은 lap1187 backlog).
- **N-5(ii) 합격:** pair PX `status PASS`·`scene_state_equal` true·V2/V2s/V2q/Scale2x/input_effect/minimap/loaded·selection·drag·production 캡처 비교 전부 PASS. 공개: `candidate.trace_close.status FAIL`·`mirror_validator BLOCKED`는 기존 하네스(lap1189 backlog "pair trace_close run_id")와 같다.
- **N-5(iii) 합격:** NG5 장면에서 충돌 이름 키는 팩에 파일이 있으면 전부 확장 hit — T1 ext 계열 키 127/127 hit(plain hit 31·lut_hit 6·shade_hit 90; writer `0x468C30` 8·`0x468F00` 12·`0x468CC0` shade 38·`0x4690A0` shade 52·`0x466540` lut 4·`0x466EA0` lut 2·`0x4664D0` 9·`0x467580` 2), `ext_misses` 0·`ext_rejects` 0·`hd_pack_rejects` 0·shade/lut reject 0. 같은 팩·`EXT=0`(T0)은 충돌 이름 키 60개가 전부 miss, hit 0. 즉 terrain `.ytl`·aux(LUT/음영) 경로도 같은 확장 이름을 쓴다.
- **원본 보호:** EXE SHA `b56986e0…` 전·후 MATCH(`orig_sha_before.txt`·`orig_sha_after.txt`·`orig_sha_after2.txt`). `local/runtime/lap1192_hdn0_*`의 `game` 사본은 하네스가 종료 때 삭제(baseline·candidate·prefix·manifest 보존).

## 판정

**N-0 PASS**(생존 변이 4종 단언) · **N-1 PASS**(도구, 변이 5/5 RED) · **N-2 PASS**(C, 호스트 로더 + 변이 8/8 RED + 실게임) · **N-3 PASS** · **N-4 PASS**(674/677) · **N-5 PASS**(i 100%·ii pair PASS·iii 127/127). 전체 `PASS(partial, 기술·격리)` 후보. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님(팩 규약 보강).

## 한계·공개

1. 팩 그림은 bicubic stand-in이며 실제 업스케일 화질 평가가 아니다. 확장 hit가 "맞는 프레임"을 그린다는 증거는 (a) 실루엣 검사 통과(reject 0), (b) 반투명 자기 검사 불일치 0(1x 출력과 키 경로가 같은 그림), (c) `e88d0c4c` 같은 구별 접두 길이 L=12173(두 프레임이 8192 B까지 같고 그 뒤에서 갈림)이 오프라인에서 서로 다른 p8로 갈리는 것. 서로 다른 색의 HD 두 프레임으로 육안 비교한 run은 없다.
2. 남은 충돌 3개(`86×60`, 24~42 구성원)는 접두 길이로 갈리지 않아(구성원 스트림이 서로의 접두) 그대로 Scale2x. backlog.
3. 확장 조회는 기본 이름이 없는 **모든** 키에서 `.amb` 열기를 한 번 시도한다(키당 1회, 마커 없음 = 일반 miss). 실측 영향은 p95 6(전 run 동일)로 측정되지 않았다. 마커가 없는 팩에서의 첫 키 비용은 별도 측정하지 않았다.
4. begin 실패 폴백 카운터 분리·트레이스 이벤트 한도(dwell ≤56)·같은 갈래 끔 대조 부재는 lap1191 backlog 그대로. Q1/T0 대조는 맵 갈래가 달라 호출 수가 다르므로 키 단위(hit/miss)로만 비교했다.
5. `.amb` L은 구성원 최소 범위 이하라는 도구 계약에 의존한다. 엔진은 L ≤ 65536과 `readable_range`만 확인한다(다른 모드의 파일에서 잘못 만든 마커는 hit 못 하고 miss/reject로 끝나며 잘못된 그림은 실루엣 검사가 막는다).
6. 정적 테스트 일부는 문자열 계약(변이 RED 확인).

## 다음 행동

middle(Opus)이 H-HDN0을 검수(C 확장 조회·도구 분리·키 로그 재계산)하고 `PASS(partial, 기술·격리)`를 판정한 뒤, 반투명 다음 writer(`0x467B00` → `0x4685C0` → `0x467FD0`)를 사전등록한다. 사용자 G1 시험 결과가 오면 최우선.

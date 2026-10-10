# 2026-10-08 | lap 1191 | G1 middle — H-HDB1 검수 + work H-HDN0(팩 이름 충돌 해소) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간(middle, 진단·확인). 게임 실행·C source 수정·커밋 0. 변이 시험은 Sonnet 하위 에이전트가 격리 사본에서 수행(저장소 비접촉).
- 입력: `loop/ESCALATE_SOL`(lap1190 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261008_lap1191_preserved_lap1190_escalate_sol.txt`(SHA256 앞 `a71c99fbbf61d5a1`), 보존 뒤 삭제. `loop/STOP` 없음. INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음.
- 가설(검수): lap1190 B1-0~B1-4 수치가 raw에서 재현되고, keyed ≥95% literal 미달은 키 경로 결함이 아니라 팩 구성 + 이름(앞 128 B digest) 충돌 때문이다.
- 산출물(공유 temp `20261008_lap1191_middle_review/`): `recalc_lap1191.py`·`.json`(SHA256 앞 `97a6949f460eea9d`), `conflict_len_lap1191.*`·`conflict_sil_lap1191.*`·`conflict_prefix_lap1191.*`, `pack_dry/cecc4681/digest_index.json`(전 자산 `pack --dry-run`), `mut/mutation_lap1191.{py,txt}`.

## 1. source·원본 정체성

- source SHA256 앞 16자 8개가 lap1190 기록과 일치(`g1_blend_key.h 5db2713b…`·`g1_mirror2x.c 32fd70e8…`·`.h edef1cbc…`·`g1_hd_asset.c 1b1d13d3…`·`.h 4a6e7221…`·`direct_draw_trace.c 6ef3baac…`·`Makefile 60881d0c…`·`tests/test_g1_blend_key.py 8b626628…`). E0 로그 이후 `tools/`·`patches/`·`tests/` 소스 변경 0(`find -newer`, `.omc` 상태 파일만).
- 원본 EXE SHA `b56986e0…` 전·후 MATCH(work 기록 + 이번 회차 objdump 전 재확인).

## 2. B1-1 역어셈블 독립 재확인(`0x467580..0x4676BD`, 읽기 전용)

- 목적지 `[ecx+0x1514] + y·[ecx+0x10] + x`, 클립 없음. 스트림 `FE n` → `col += n`(n=0이면 0), 행은 `col ≥ width`에서 끝남, 스트림 위치는 행 사이에 이어짐 — `0x4672E0`과 같다.
- 채널 값: `lea edx,[ecx+esi*2+0x2BBC0]; mov bl,[esi+edx+0x15DE0]` = `[ecx + 3·d + 0x419A0]`(d = 목적지 바이트 `[edi+edx]`, 먼저 읽음), s도 같은 식. 채널 1·2는 `+0x419A1`·`+0x419A2`.
- `t_k = movsx word [ecx + ((pal_d[k]<<6)+pal_s[k])·2 + 0x41CA0]`, `edx = ((t0<<6)+t1)<<6`, 결과 `byte [ecx + edx + t2 + 0x19A0]`. **work 정정(d·s는 팔레트 채널 값) 확인.** 32비트 모듈러 산술이라 음수 t와 양수 t가 섞여 `[0,0x40000)` 안에 드는 경우 원본도 그 바이트를 읽는다 — `g1_blend_weighted_offset`의 `uint32` 계산·범위 거부가 이와 같다(범위 밖은 원본이 다른 renderer 메모리를 읽으므로 거부 → 자기 검사 불일치 → 폴백, 안전).

## 3. 래퍼 구조 검토(`mirror_blend_wrle`·`blend_key_apply`·`g1_blend_key.h`)

- covered·HD 목적지 창 복사(`blend_key_snapshot`)와 1x `before` 복사가 원본 호출 **전**, 키 시도는 diff 미러(타일) 성공 **뒤**. 키 = 스트림 전체 사각형(x, y, width, height), 자기 검사·그리기 = 화면 교집합만, 팩 오프셋 `frame + 2·oy·W + 2·ox`, HD 크기 `2w×2h` 일치 검사, 디코드 한도 `2·w·h + 2·h`, 자기 검사 실패·begin 실패·팩 miss 시 폴백(diff 결과 유지), `w·h > 800·600`이면 폴백 계수. 버퍼 크기(`g_blend_key_*` = 800·600, `hd_before` ×4)와 한도가 맞다.
- 공유 코어로 `0x4672E0`(weights NULL)과 `0x467580`(weights = `+0x41CA0`)이 같은 경로를 쓰고 카운터만 두 벌 — 사전등록 B1-1 "복제 금지" 충족.

## 4. 변이 재현(격리 사본 `mut/`, 새 변이 14종)

| 변이 | 내용 | 결과 |
|---|---|---|
| n1 | 자기 검사 실패 뒤 진행 | RED |
| n2 | 팩 창 오프셋 제거 | RED |
| n3 | crop x 오프셋 0 | **생존** |
| n4 | 키를 화면 창 크기로 | RED |
| n5 | HD 크기 검사 제거 | RED |
| n6 | writer id `0x4672E0`로 | RED |
| n7 | 스냅샷을 원본 호출 뒤로 | RED |
| n8 | 오프셋 범위 거부 제거 | RED |
| n9 | 표 인덱스 범위 거부 제거 | RED |
| n10 | t 부호 확장 제거 | RED |
| n11 | `keyed_pixels` 누적 제거 | **생존** |
| n12 | 크기 한도 ×4 | **생존** |
| n13 | 디코드 한도 `w·h` | **생존** |
| n14 | `hd_before` 행 폭 오류 | RED |

RED 10·생존 4 = **테스트 공백, 코드는 정상**(현재 코드는 네 곳 모두 올바른 값을 쓴다). 위험 순: n12(한도를 풀면 정적 버퍼 넘침 가능 → 비교식 고정 단언 필요), n3(왼쪽으로 잘린 구름에서 키 어긋남; 실게임은 자기 검사가 잡지만 테스트 단언 없음), n13(픽셀당 2바이트에 가까운 스트림 오거부), n11(진단 카운터). 다음 work에 회귀 단언으로 넘긴다(§7 N-0).

## 5. raw 재계산(새 스크립트 `recalc_lap1191.py`)

| run | 호출(clipped) | keyed | 폴백 | 자기 검사 불일치/px | PS3 present·s | p95(첫 90 s / 이후) | stale 최대 | 안전 7종·dropped |
|---|---|---|---|---|---|---|---|---|
| E0 | 2,061(1) | 0 | 2,061 | 0 / 24,343,859 | 6,110·305.4 | 6 (6/6) | 0 | 0 |
| K1 | 24(0) | 24 | 0 | 0 / 286,424 | 6,031·301.5 | 6 | 0 | 0 |
| K2 | 1,428(110) | 1,049 (73.46%) | 379 | 0 / 14,589,584 | 6,032·301.8 | 6 | 2 | 0 |
| K3 | 1,190(1) | 1,033 (86.81%) | 157 | 0 / 14,059,032 | 6,104·305.1 | 6 | 0 | 0 |
| K4 | 21(0) | 21 | 0 | 0 / 249,095 | 5,914·301.9 | **12 (19/6)**, 첫 90 s >10 ms 20.0% | 2 | 0 |
| K5 | 0 | 0 | 0 | — | 5,957·301.5 | 8 (7/11) | 266 | 0 |
| K6 | 401(7) | 360 (89.78%) | 41 | 0 / 3,555,876 | 5,997·301.5 | 7 (6/9) | 0 | 0 |
| M1 | 161(0) | 137 (85.09%) | 24 | 0 / 1,902,365 | 6,032·301.5 | 6 | 0 | 0 |
| R1 | 735(563) | 634 (86.26%) | 101 | 0 / 6,064,767 | 6,030·301.4 | 6 | 0 | 0 |
| O1 끔 | 20(0) | 0 | 0 | — | 6,030·301.4 | 6 | 0 | 0 |
| O2 끔 | 589(98) | 0 | 0 | — | 6,037·301.8 | 6 | 2 | 0 |

- work 표의 호출·keyed·폴백·자기 검사 픽셀·p95·stale 전부 일치. 켬 합 호출 6,021·자기 검사 65,051,002 px·불일치 0 일치. 안전 = present 최대 `fallback`·`hresult`·`identity_invalid_sources`·`scale2x_palette_violations`·`identity_key_mismatches`·`viewport_restore_failures`·`clip_replay_mismatches` 전부 0, summary dropped 0.
- **K4 p95(b):** 첫 90 s p95 19·>10 ms 20%, 이후 6. 호출 21개(전 run 최소급)이고, 호출 0인 K5도 이후 구간 p95 11·K6 이후 9로 같은 종류 변동이 있다 → 이 경로와 무관한 환경 부하로 판정, **재측정 불필요**(work의 "팩 생성 스크립트 동시 실행" 설명은 확정 불가로 둔다).
- **키 로그 귀속(B1-3):** 이번 회차 독립 헤더 파서(`0xBF4 + 0x4C4 표`)·FNV-1a 128 B로 관측 키 64개 **전부** 6개 파일에 귀속(CLOUD 14·smoke0 10·groundfire 9·groundfiresmoke 19·tornado 8·exp6 4), 미귀속 0 — 일치.
- **폴백 귀속:** K3·K6·M1의 miss 키는 `e88d0c4c_160x120` 하나뿐(그 밖의 키는 전부 hit, 자기 검사 불일치 0) → 폴백 157·41·24는 이 키 호출로 추론된다(begin 실패를 따로 세는 카운터는 없어 추론 1단계 공개). K2·R1의 추가 miss는 팩에 없는 파일(K2: smoke0·groundfire·exp6, R1: groundfiresmoke 19~26) — 일치.
- **정정 1:** 두 번째 충돌 `1c5411c5_104x80`은 groundfiresmoke **프레임 0(175 B) 대 프레임 36~39(160 B, 서로 같은 스트림)**이다(work "프레임 0·39"는 일부만). 판정 영향 없음.
- **색 반영:** R1 `evidence_R1_red_cloud_ps3_start.png` 열람 — 화면 오른쪽 가장자리 구름이 붉다(clipped 563 run). 같은 갈래 끔 대조가 없어 수치 비교는 못 함(work 공개 그대로).

## 6. 판정

**H-HDB1 `PASS(partial, 기술·격리)` 수용.** B1-0 PASS(x1·x3 포함 12종 RED, 이번 회차 새 변이 10/14 RED), B1-1 PASS(역어셈블 독립 재확인·호스트 원본 산술), B1-2 PASS(구조 검토 §3), B1-3 PASS(64/64 귀속), B1-4 PASS(partial): 자기 검사 불일치 0·안전 0·pair PB/PB2 PASS·켬 p95 ≤ 끔+2(K4는 환경)·stale ≤ 끔·색 반영 육안.

- **(a) keyed ≥95% literal 미달(K3 86.8·K6 89.8·R1 86.3)은 기록으로 남기되 키 경로 FAIL로 보지 않는다.** 분모에 팩에 없는 파일 키와 이름 충돌 키가 들어 있고, 둘을 뺀 키는 hit 100%다. 충돌은 lap1165가 공개한 구조 한계(앞 128 B digest 충돌 프레임 13~19%)와 같은 원인이다.
- **충돌 규모 재측정(이번 회차, `pack --dry-run` 6개 폴더 char·tile·BattleSpr·portrait·fnt·yfnt):** 충돌 이름 677개·충돌 프레임 4,612(char 2,655·tile 1,142·fnt 707·yfnt 61·BattleSpr 47). 실제 업스케일 팩이 들어와도 이 프레임은 항상 Scale2x로 남는다 → 유닛 애니메이션 안에서 HD/Scale2x 프레임이 섞인다. 팩 도구는 충돌 이름을 쓰지 않으므로 잘못된 그림은 그리지 않는다(안전).
- **해소 가능성(오프라인):** 키 장부는 이미 소스 포인터를 포함해 엔진 안에서는 두 프레임이 다른 키다. 충돌은 **팩 이름**에서만 생긴다. 구별 수단별 분리 비율: 스트림 길이 259/677, 1x 실루엣 281/677(tile 8/307), 전체 스트림 해시 677/677. 엔진 writer마다 RLE 문법이 다르다(추출기 `FE 00` = 리터럴 0xFE, `0x467580`은 행 단위·`FE 0` = 0칸). 그래서 스트림 끝을 계산하는 방식은 writer별 파서가 필요하다. 반면 **"충돌 이름별 구별 접두 길이 L(모든 구성원 스트림 범위 이내)"의 FNV-1a는 문법 없이 674/677(99.6%)을 가른다**(L = 256이 263개·512가 175개·1024가 77개, 나머지는 최소 범위까지). 실패 3개는 `86×60` 이름(24~42 구성원). → **`FEASIBLE`**.
- **(b)** K4 재측정 불필요(§5). **(c)** dwell 56은 트레이스 한도 때문이고, 표가 보이는 event_count 8,029~8,191은 한도 8,192에 붙어 있다 → 다음 장기 run도 dwell 56 이하 유지(하네스 한도 backlog lap1146 동일). **(d)** 같은 갈래 끔 대조 부재·pair trace metrics 부재는 공개 유지.
- 집계: 판정 영향 불일치 0, 정정 1(충돌 프레임 범위), 보강 3(K4 구간 p95·폴백 키 단일성·충돌 전 자산 규모와 분리 방식), 공개 3(변이 생존 4 = 테스트 공백, begin 실패 카운터 부재로 폴백 귀속은 추론, 같은 갈래 끔 대조 부재). 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

**다음 순서 결정:** 반투명 다음 writer(`0x467B00`)보다 **팩 이름 충돌 해소(H-HDN0)**를 먼저 한다. 근거: (1) 이번 literal 미달의 직접 원인이다. (2) writer와 무관하게 전 자산 프레임의 약 12%(유닛 2,655)가 HD를 받을 수 없는 구조 결함이다. (3) 엔진 변경이 팩 조회 1곳(키당 1회)에 국한되고, 오프라인 분리 99.6%로 `FEASIBLE`이다. `0x467B00`→`0x4685C0`→`0x467FD0`은 그다음이다.

## 7. 다음 work 사전등록(Sonnet) — H-HDN0: 팩 이름 충돌 해소(구별 접두 길이 확장 이름)

**단계.**
- N-0(테스트만, 이번 회차 생존 변이 막기): `tests/test_g1_blend_key.py`에 (n12) `mirror_blend_wrle` 크기 한도 비교식 `(size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS` 고정, (n3) `blend_key_apply`의 두 `g1_blend_crop` 호출이 `offset_x, offset_y`를 넘김, (n13) 디코드 한도식 `pixels * 2u + (size_t)height * 2u`, (n11) `stats->keyed_pixels += (DWORD)written` 단언. 각 변이에서 RED, 현재 GREEN.
- N-1(도구 `tools/g1_hd_convert.py pack`): 충돌 이름(1x 그림 불일치)마다 구성원 전부의 스트림 범위(오프셋 표 기준 다음 시작까지) 최소값 이하에서 후보 L(256, 512, 1024, 2048, …, 최소 범위)을 차례로 시도한다. 서로 다른 1x 그림을 가르는 가장 작은 L을 고른다. 그 이름에 대해 표식 파일 `h<d8>_<w>x<h>.amb`(내용 = L, 4바이트 LE)과, HD가 있는 구성원마다 `h<d8>_<w>x<h>_<L>_<p8>.idx8`(p8 = 그 스트림 첫 L바이트 FNV-1a)을 쓴다. 같은 p8에 그림이 둘 이상이면 그 이름은 계속 충돌로 둔다(쓰지 않음). `digest_index.json`에 `extended`(이름→L·구성원)·`conflicts`(남은 것) 기록. HD 불일치 충돌(같은 1x 그림, 다른 HD)은 지금처럼 쓰지 않는다.
- N-2(C, `g1_hd_asset.c read_pack_frame`): 기본 이름 파일이 없을 때만 같은 팔레트 디렉터리의 `.amb`를 연다. L이 129..65536이고 `readable_range(source, L)`이면 `key->source`부터 L바이트 FNV-1a로 확장 이름을 만들어 같은 크기·실루엣 검증으로 읽는다(flip·LUT·음영 후처리는 기존 그대로). 이름 버퍼는 확장 이름 최대 길이 이상(현재 40 B → 64 B 권장). 카운터 `hd_pack_ext_hits/ext_misses/ext_rejects`(trace). 끔 env `SYW2_G1_HD_PACK_EXT=0`. 키당 1회(팩 조회 시점)만 계산하고 draw 경로 비용은 0이어야 한다.
- N-3(호스트·도구 테스트, RED→GREEN): 합성 `.spr` 2프레임(앞 128 B 같음, 뒤가 다름)에서 `.amb`·확장 이름 2개 생성, 분리 불가 쌍은 계속 conflict, L ≤ 최소 범위. 호스트 로더: 기본 miss → `.amb` → 확장 hit, `.amb` 없음 → MISS, L 범위 밖·읽기 불가 → MISS(ext_rejects), 확장 파일 실루엣 불일치 → REJECT. 변이(L 무시·접두 길이 오류·`.amb` 무시·기본 이름 우선순위 반전) RED.
- N-4(오프라인): 6개 폴더 `pack --dry-run`으로 확장 이름 수·남은 충돌 수(이번 회차 기준 674/677 분리 재현)·L 분포를 남긴다.
- N-5(run): (i) lap1190 F0 구성(dwell 56) 켬 2 run, 팩 = 6개 효과 파일 전체(충돌 확장 포함). (ii) save006 pair 1회. (iii) NG5 1 run(UI·지형 장면)에서 키 로그 키 중 이름 충돌 키 수·확장 hit.

**측정식(합격).**
- N-0 변이 4종 RED. N-3 변이 RED. N-4 확장 분리 ≥ 674/677(이번 회차 수치와 다르면 원인 기록).
- N-5(i): `0x467580` 화면 안 호출 중 keyed ≥95%(분모 = 6개 파일 귀속 키 전부; 팩에 없는 파일이 새로 나오면 따로 기록). `e88d0c4c` 키(CLOUD 4·5)가 run에 나오면 두 프레임 모두 hit(ext_hits ≥1). 자기 검사 불일치 0, 안전 7종·dropped 0, p95 ≤ 끔+2(끔 = lap1190 O1·O2 6), stale ≤ 끔 규모. 호출 <300이면 표본 부족으로 부분 판정만 한다.
- N-5(ii): pair PASS. N-5(iii): 이름 충돌 키가 나오면 확장 hit 비율 기록(팩 = 해당 파일 stand-in). 나오지 않으면 SKIP으로 기록한다(실패 아님).
- 안전: 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 20 GB 미만이면 자기 회차 옛 사본부터 정리하고, 5 GB 미만이면 run을 시작하지 않는다.
- **비목표:** 실제 업스케일 화질, 기본 켬·사용자 전달, `0x467B00` 이후 writer, writer별 스트림 파서.
- **중단:** 실패 가설 2회 또는 60분. 확장 이름 hit가 잘못된 프레임을 그리는 증거(실루엣 reject 급증·육안 오류)가 나오면 즉시 끄고 근거만 남긴다. run 대기는 PID `kill -0`·`.exit` 파일. 커밋 금지, 원본/참고 쓰기 금지. 산출물은 공유 temp `<날짜>_lap<N>_work_hdn0/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **backlog 추가:** 남은 충돌 3개(`86×60`), begin 실패 폴백 카운터 분리(경미), 트레이스 이벤트 한도(장기 run dwell ≤56).

## 8. 검사

- 검사 결과는 STATUS 검증 줄에 보강한다. 전체 `make check`는 SKIP한다. 이번 회차는 문서와 공유 temp 스크립트만 바꿨고, tools·tests·C source는 lap1190 full PASS(1985 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDN0(§7)을 진행한다. 그다음 반투명 다음 writer `0x467B00`. 사용자 G1 시험 결과가 오면 그것이 최우선이다.

# 2026-10-06 | lap1042 | G1 middle — H-S 독립 검수 → work W-1(V2s gate, 사용자 결정) · work H-U(`0x468360`) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·source 변경·commit 0.
- 검수 대상: lap1041 work H-S(남은 유닛 크기 stale 덩어리 writer 귀속, 진단 전용). lap1040 §H-S 사전등록 S-0~S-2를 raw에서 재현하는지 확인한다.
- 처리한 인계: `loop/ESCALATE_SOL`(lap1041 work, 1,756 B, SHA256 `51966446741bdd044aeac53a332e616980562395f54de88f1b91024a04fc9dff`). 원문은 아래 부록에 두고 처리 뒤 삭제했다. root 추가 지시(사용자 W-1 결정 사전등록)도 같은 파일에 있었다.
- 변경 파일: 이 기록, `docs/STATUS.md`. source/test 변경 0.
- 원본 SHA / 환경 / fixture: 원본 EXE `b56986e0…8ac`(objdump 대상 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` sha256 재확인, 전 run private EXE 앞 16자 일치). save000(index 1), 격리 prefix/display. 현재 `g1_mirror2x.c` `4c4a4152…ef5421` = 7 run bridge 사본(lap1039 product와 같음).
- 재계산(공유 temp `20261006_lap1042_middle_review/`). `analyze_s.py`·`hooked_w.py`·work의 `od_*.txt`·제품 helper는 쓰지 않았다. lap1040 middle 재계산 코드(middle 소유)를 바탕으로 새로 썼다.
  - `recalc_lap1042.py` `941867eb…5e14` → `recalc_lap1042.json` `6e7136c0…1cc1`. 7 run(유효 6 + s1_r1)의 항등식·안전·무장·마지막40, 표본별 stale present 구간·마지막 writer EIP·함수 귀속·덤프 mask 교차 확인.
  - `recalc2_lap1042.py` `d2eeca2c…0009` → `recalc2_lap1042.json` `bde0ea3e…c1cc`. **실효 writer**(그 present에서 최종 값을 처음 쓴 hit)와, 표본을 덮는 기후킹 `w` 레코드의 `sb==sa` 여부.
  - objdump 직접 재생성: `od_466000_46a000_lap1042.txt` `bbe91177…1e4e`, `od_text_lap1042.txt`(0x401000..0x4E0000) `d4e33c5c…9c4e`, 검사 `od_check_lap1042.py` `96c2a8b3…ef41` → `od_check_lap1042.json` `c589509c…c4e`.

## 재계산 결과(판정 불일치 0, 정정 3건)

| 항목 | lap1041 work 보고 | lap1042 재계산 |
|---|---|---|
| S-0 유효 6 run | selftest·fail 0·좌표 3/3·안전0·항등식·마지막40 26 | 같음. selftest PASS 6/6, 무장 52 round·fail 0, 좌표 6/6 일치, dropped/overflow 0, JSONL 손상 0, 안전 7종 0, cleanup·source_unchanged true, 카메라 (39,53), tick 400~401, ps3 410/411. 항등식 `flip_rle_466B50`·`blend_4678C0`·`blend_467FD0`·`blend_467B00`·`blend_467580` 30/30 성립. **마지막40 중앙값 26 ×6** |
| S-1 귀속 | 9/9, 두 run 동일 EIP·값 일치 100% | **9/9**. 점마다 두 run의 EIP 분포가 같다. 값 일치 = stale 수(100%). present 번호는 run 사이 0~±2 차이(분포 비교로 판정) |
| S1 (795,470) | `0x466D15` 12·`0x468571` 5·`0x46884E` 2·`0x467CCF` 1 | 같음. 구간 r2 p141–142·239–250·388–392·396, r3 p140–141·238–249·386–390·394. 덤프 mask에서는 p388에서만 stale |
| 마지막40 26의 원인 | p386~392 `0x468571` | 확인. s1_r2 마지막40 계열 = 0×17 → 26·28·37·40·40(p388..392, 표본 writer `0x468571`) → 40·35·26·37·83·154 → 145×9 → 125 → 0×2. 0이 19개라 중앙값은 p388 덩어리의 26이 정한다 |
| 나머지 8점 | 표 그대로 | 같음(p6·p12·p144·p174·p204·p399·p366·p6 둘째, 덤프 프레임 교차 일치) |

**정정 1 — 기후킹 writer 원인은 UNKNOWN이 아니다.** work는 `0x467692`(`0x467580` 내부)·`0x467CCF`(`0x467B00` 내부)가 마지막 writer인 stale을 "거부 아님·원인 UNKNOWN"으로 남겼다. 같은 present의 hit 순서를 보면 12건 모두 같은 패턴이다. 먼저 미후킹 writer가 화면 값을 바꾸고(예: s2_r1 p174 `0x468A28`가 24→66), 이어서 기후킹 혼합 writer가 **같은 값**을 다시 쓴다(`0x467692` 66). 표본을 덮는 기후킹 `w` 레코드는 전부 `sb==sa`다. 그래서 diff 미러에는 바뀐 픽셀이 없고, 화면은 이미 미후킹 writer가 바꾼 상태라 stale이 남는다.
- 실효 writer로 다시 세면 유효 6 run 표본 stale present 88개가 **전부 미후킹 4함수**다: `0x466BE0` 44, `0x4687F0` 26, `0x468360` 10, `0x4689C0` 8. 기후킹 0, `none` 0.
- 따라서 기후킹 함수 안의 별도 결함은 없다. 앞선 미후킹 writer를 미러하면 같이 해소될 것으로 예측한다(아래 H-U U-1에서 검증).

**정정 2 — "reject 0" 범위.** `blend_467B00_reject_bounds`는 run마다 11,200~11,235로 0이 아니다. 이것은 lap1025가 수용한 화면 밖·크기 0 호출이다. work의 "reject 0"은 `reject_size`·`reject_target`·`reject_guard`에만 맞다. 판정에는 영향이 없다.

**정정 3 — s1_r1.** 무효 처리 자체는 타당하다(ps3 272 < 정상 410, 후보 p95 41, tick 381, 같은 바이너리 다른 run은 p95 11~12). 그러나 "귀속 EIP 구성은 r2/r3와 일치"는 정확하지 않다. 함수 집합은 같지만(pt0 `0x466BE0` 9·`0x468360` 5·`0x4687F0` 1·`0x467B00` 1) 개수·구간이 다르다(16건, p77·118–126·260–264·268). p6·p12 점은 stale 0이다. 시작 load 기록은 3.01이고, 실행 중 load가 오른 것은 s1_r2 시작 기록(1분 7.22·5분 10.85)으로 확인된다. s1_r1 수치는 판정에 쓰지 않는다.

## objdump 독립 확인(원본 SHA 재확인)

| 함수 | 시작 5B | ret | 내부·전역 분기 → +1..+4 | 직접 호출처 | 절대 포인터 | 클립 `+0x4D0..0x4DC` | 귀속 EIP |
|---|---|---|---|---|---|---|---|
| `0x466BE0` | `83 EC 18 33 C0`(sub esp,0x18 / xor eax,eax) | `0x466D40` `ret 0x18` | 0 / 0 | `0x419FB0`·`0x41A54A` | 0 | 5곳 | `0x466D15` ∈ |
| `0x468360` | `83 EC 1C 53 55`(sub esp,0x1c / push ebx / push ebp) | `0x4685B5` `ret 0x1c` | 0 / 0 | `0x41A8E7`·`0x41AA5F` | 0 | 5곳 | `0x468571` ∈ |
| `0x4687F0` | `51 8B 54 24 0C`(push ecx / mov edx,[esp+0xc]) | `0x46886B` `ret 0x18` | 0 / 0 | `0x41A190` | 0 | 없음 | `0x46884E` ∈ |
| `0x4689C0` | `51 53 55 56 57` | `0x468A49` `ret 0x18` | 0 / 0 | `0x41A250` | 0 | 없음 | `0x468A28` ∈ |

- 네 함수 모두 시작 5바이트가 명령 경계에서 끝나고, 상대 주소 명령이 없다. 앞 5바이트 안으로 들어오는 분기는 .text 전체에서 0이다. 원본 파일에 절대 포인터가 없어서 간접 호출 흔적도 없다. work S-2 표와 같다(work 범위 끝 `…D4F`·`…5BF`·`…86F`·`…A4F`는 padding 포함 표기).
- `0x468360` 본문: 인자 x·y·w·h는 `movsx` 16비트, 5번째 RLE 포인터, 6번째 remap, 7번째 level(`movsx`, `<<6`)이다. 표 `+0x43CA0`로 혼합하고 `+0x19A0`로 색을 고른다(목적지 의존). 클립은 `[+0x4D0,+0x4D8]×[+0x4D4,+0x4DC]` 양끝 포함이다. 목적지 열 = `x + w − 1 − col`(좌우 반전). 따라서 쓰기 범위는 `rect ∩ clip`이고, 반전은 범위를 바꾸지 않는다. 호출처 두 곳 모두 7개 push 뒤 `ecx = 0xE5BF18`(`G1_RENDERER_VA`)이다. `0x4678C0`(H-P) 호출처 `0x41A827` 블록과 같은 모양이다. 화면 쓰기 명령은 `0x46856E`이고, watch EIP `0x468571`은 그 다음 명령이다(트랩 뒤 EIP, 다른 EIP와 같은 규칙).
- 새 관찰(비차단 backlog): 같은 호출 블록 `0x41A887`이 미후킹 `0x467E60`을 같은 7인자로 부른다. 이번 표본에서는 관측되지 않았다.

## 판정

**H-S PASS 수용(진단).** S-0 PASS, S-1 9/9 PASS, S-2 분류 → **FEASIBLE**(미후킹 4함수 모두 5B 경계·분기 0·호출처 확인). 정정 1로 기후킹 함수 내부 "UNKNOWN"은 해소됐다. 남은 표본 stale은 전부 미후킹 writer에서 온다. 정정 2·3은 판정에 영향이 없다. 기술 진단 수용이며 G1 마일스톤 승인이 아니다.

수리 순서(실효 stale present 수와 지표 기준): **(1) `0x468360`** — 마지막40 중앙값 26의 직접 원인(work 제안 유지). **(2) `0x466BE0`**(44, 가장 많음, `0x466B50`의 클립 형제). **(3) `0x4687F0`**(26). **(4) `0x4689C0`**(8). work 제안 순서(4687F0 → 466BE0)를 실효 개수 기준으로 바꿨다.

## 다음 work 1 — W-1 V2s gate 재정의(사용자 결정 2026-10-06 01:43 KST, 게임 실행 없음) 사전등록

근거·정의는 `docs/work/active/G1_STRATEGY_W70_V2S_REFERENCE_REFRESH_LAP960.md` §1·§4.1을 그대로 쓴다. 사용자가 APPROVALS lap962 선택지 (1)을 승인해 "사용자 미승인" 경계가 해소됐다.
- 구현(`tools/g1_saved_scene_probe.py`만): `_compare_images`에 원본 800×600의 표준 Scale2x(EPX, 가장자리 clamp, 제품 `g1_scale2x_core.h`와 같은 규칙) 기준을 계산한다. `v2s_scale2x_reference_blocks`와 `v2s_unexplained_single_black_blocks`를 추가한다. **`v2s_status` = unexplained ≤ `G1_SINGLE_BLACK_BLOCK_LIMIT`(2,000 불변).** raw `v2s_single_black_blocks`는 그대로 기록하고, `v2s_raw_status`(raw ≤2,000)는 비gate 공개 진단으로 둔다. `_v2s_capture_gate`·`_pair_status` 집계 규칙·tag·V1/V2/V2q·Scale2x gate·validator는 바꾸지 않는다. 계산 시간 증가를 기록한다.
- 테스트 RED→GREEN: (a) 원본을 정확히 Scale2x한 후보 → unexplained 0(raw > 0 가능), (b) 대각 격자에 단일 흑색 N개 주입 → unexplained = N, (c) 기존 V2s/V2q 테스트 유지, (d) 집계 함수 불변 pin.
- 오프라인 회귀(보존 PNG, 새 결과 파일로만, 과거 pair-result 수정 금지. PNG가 없으면 SKIP으로 표기):
  - **W1-1:** lap901 격자 결함 15 tag 전부 FAIL(unexplained 18,712~19,901).
  - **W1-2:** lap854 15 tag·lap957 15 tag·lap959 r1 5 tag 전부 PASS, 수치가 lap960 §1 표와 일치.
  - **W1-3 재집계:** 최신 save006 pair lap1039 `r_s6_r1`·`r_s6_r2`(production raw 2,852/2,833, 그 밖 4 tag PASS)를 새 코드로 다시 비교·집계한다. 5 tag의 raw·ref·unexplained와 `_pair_status` 결과를 그대로 기록한다(PASS든 HOLD든). save000 `--scene-actions none` run은 loaded 외 tag가 BLOCKED라 pair는 HOLD로 남는다. 이것은 V2s와 무관한 구조이며 따로 적는다.
- FAIL 조건: W1-1에서 하나라도 PASS, W1-2에서 하나라도 FAIL, 커널이 제품 EPX와 다름, 집계·한도·tag 변경. 분기: W1-3에서 unexplained가 2,000을 넘는데 PNG에 격자/seam이 없으면 lap960 §6(a)에 따라 strategy를 재호출한다.
- 검사: `make lint`·`make typecheck`·focused 뒤 `make check`. 산출물은 공유 temp `20261006_lap1043_work_w1/`.

## 다음 work 2 — H-U `0x468360` 클립 반전 반투명 RLE diff 미러 사전등록(W-1 middle 검수 다음)

- 변경: `tools/inmm_stub/g1_mirror2x.c`. hook `0x468360`(old bytes `83 EC 1C 53 55`, len 5, thiscall, 7 stack args `ret 0x1c`). wrapper는 수용된 `mirror_blend_clip7`(H-P)과 같은 구조다: guard → renderer/대상 검사 → 화면 교집합 bounds → size → 전용 before 버퍼 복사 → 원본 7인자 1회 그대로 호출 → `g1_overlay_blt_apply`. 근거: 반전은 목적지 범위(`rect ∩ clip`)를 바꾸지 않으므로 화면 교집합 diff가 원본 쓰기 범위를 덮는다. 계수 `blend_468360_*`(invocations·mirrored_calls·mirrored_pixels·changed_calls·clipped_calls·reject_target/bounds/size/guard)를 두고, drift `w` 레코드 f=`468360`을 남긴다. install·restore·installed·reset 목록에 넣는다. `mirror_details` 용량은 최악 길이를 다시 계산해 필요하면 올리고 pin 테스트를 갱신한다.
- 테스트 RED→GREEN: old bytes·주소·인자 수 계약, 계수 노출, details 용량 pin.
- 실행(순차, run 직전 `/proc/loadavg` 기록, 1분 load >8이면 대기, 단일 인스턴스 pid 확인). 명령은 lap1041 `run_s.sh`·lap1039 `run_r.sh`와 같고 바꾸는 것만 적는다:
  1. save000 watch pair 2회: `--drift-samples "795,470;628,409;599,367"`(lap1041 S1).
  2. save000 성능 pair 2회(lap1039 s0 인자).
  3. save006 pair 2회(lap1039 s6 인자 `--stale-mask 6-12,30-34,300-301,585-620,880`).
- PASS / FAIL:
  - **U-0:** 안전 7종 0, cleanup·source_unchanged true, `blend_468360` invocations = mirrored + reject_* 성립, 기존 항등식 유지, invocations > 0.
  - **U-1(가설 지표):** S1 (795,470)에서 실효 writer `0x468571`인 stale present 10→**0**(두 run). `0x466D15`·`0x46884E` 구간은 그대로 남아야 한다(분리 확인).
  - **U-2(집계):** 마지막40 중앙값 **<26**(두 run). 덤프 비교는 "새 r1∩r2 ∖ 기준(lap1041 s1_r2∪s1_r3) = 0"과 "기준 r1∩r2 ∖ 새 r1∪r2(제거)"를 함께 적는다. 합계만으로 결론 내지 않는다.
  - **U-3(성능):** 후보 p95 ≤ 대조(같은 날 lap1039식 미러 off 대조를 쓰면 함께 기록) 또는 ≤8ms, ticks 비 0.99~1.01. 미달이면 load·히스토그램을 근거로 UNKNOWN-환경 여부를 따로 적는다(기준 무변경).
  - **U-4(비회귀):** save006 r1∩r2 신규 stale 0, 공통 덤프 stale 0 유지.
  - 반증: U-1이 0이 되지 않으면 같은 lap에서 `w` 레코드(468360) 기하와 `why`를 표로 남기고 HOLD로 middle에 넘긴다. U-1은 PASS인데 U-2가 26이면 p388..392 덩어리의 다른 writer를 기록한다(다음 `0x466BE0` 후보).
- 금지: gate·validator·기준·`G1_OVERLAY_MAX_*` 변경, 원본/raw 수정, 다른 wrapper 동작 변경. run 뒤 `game` 사본만 삭제한다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only objdump만 했다. 게임/source/commit은 0이다. focused 검사·SAFETY 결과는 STATUS에 보강한다. 전체 `make check`는 SKIP했다(source 불변, lap1039 full PASS 1629 `logs/gates/lap1039-work-full-check.log`).
- 남은 위험: 표본 9점은 결정적 재현 점뿐이라 덩어리 전체의 writer 분포가 아니다. 미후킹 `0x467E60`(같은 호출 블록)은 미관측이다. save006 짧은 run 꼬리는 원인을 모른다.
- backlog: `0x467E60`, save006 짧은 run 꼬리, 팝업 p298..338 run 변동, hold keydown 위상, 가장자리 마우스 스크롤, overlay BltFast rejects, 다중 팝업 heal.
- 사용자 승인 상태: 기술 진단 수용일 뿐 G1 마일스톤 승인이 아니다. W-1은 사용자 결정(gate 의미)이고, 구현·검수 뒤에도 G1 사용자 판단 때 raw·ref·unexplained를 함께 보인다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work W-1(위 사전등록, 사용자 결정 우선) → middle W-1 검수 → work H-U.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1041 work, 1,756 B, SHA256 `51966446741bdd044aeac53a332e616980562395f54de88f1b91024a04fc9dff`)

```
lap1041 (Claude Code claude-sonnet-5-5, work) — G1 H-S 진단 완료, 독립 검수(middle) 필요. 자가 승인 금지. 제품 source/commit 0.

한 일: save000 watch pair × 표본 3세트(S1/S2/S3, 9점) 실행(공유 temp 20261006_lap1041_work_hs/, 기록 docs/history/laps/20261006_lap1041_work_g1_hs_unit_lump_writer_attribution.md). 유효 6 run(s1_r2·r3, s2_r1·r2, s3_r1·r2) S-0 PASS(selftest·무장 fail 0·좌표 3/3·안전0·항등식·마지막40 26 재현), S-1 귀속 9/9(두 run 동일 EIP, 값 일치 100%), S-2 분류: 미후킹 `0x466BE0`(EIP 0x466D15), `0x468360`(EIP 0x468571, 7인자 ret 0x1c·클립, 마지막40 중앙값 26의 직접 원인 = S1 p386~392), `0x4687F0`(EIP 0x46884E, 6점), `0x4689C0`(EIP 0x468A28); 기후킹 내부 `0x467692`(0x467580)·`0x467CCF`(0x467B00)는 reject 0이나 원인 UNKNOWN. 판정 FEASIBLE.
무효 처리: s1_r1은 외부 load(다른 세션 ffmpeg/hyperframes)로 ps3 272·p95 41 → S-0 불만족, s1_r3 재실행으로 대체(수치 판정 제외).
승격 작업자가 이어서 할 일: (1) 공유 temp r_s1_r2/r3·r_s2_r1/r2·r_s3_r1/r2의 pair-result·layer_drift·screen_watch·trace_raw를 analyze_s.py·hooked_w.py 없이 새 스크립트로 재계산(9점 EIP 분포·항등식·마지막40 26), (2) s1_r1 무효 처리 타당성, (3) objdump `0x468360`·`0x4687F0`·`0x466BE0`·`0x4689C0` 시작 5B 경계·내부 분기·호출처(od_466000_46a000.txt 참고하되 직접 재생성), (4) 수용 시 work H-U 사전등록: `0x468360` 클립 반전 반투명 diff 미러(H-P `mirror_blend_clip7` 변형), 그다음 `0x4687F0`·`0x466BE0`·`0x4689C0`.
root 추가: 사용자 결정 G1 V2s W-1 채택 → 이번 middle에서 W-1 gate 변경 work도 사전등록(STATUS 최상단).
```

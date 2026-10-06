# 2026-10-06 | lap1088 | G1 middle — H-ULc·D-0 독립 검수 + 진단 동반 대조(H-ULd) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1087 work `loop/ESCALATE_SOL`(SHA256 `8f9d37b6e4ea4d22b3a242b37e860a35133d148714be91dbf4156939fcae28f2`, 원문은 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1086 §5 H-ULc — UL 소잔여(ord 122~124, x0..31·y0..22)는 H-W330과 무관하다. 사전등록 판정 (a)/(b)/(c).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293…` 직접 재계산 MATCH(읽기·objdump만). fixture: 비합성 save006. lap1087·lap1085·lap1083 산출물만 읽음.
- 검수한 source 해시: `tools/inmm_stub/g1_mirror2x.c` `d66a3afdd9ba30e3` = c1·d1 `bridge/g1_mirror2x.c`(현재 트리 = U-1 run bridge), `tools/g1_saved_scene_probe.py` `77d4ec093eed8031`, `tests/test_g1_mirror2x.py` `bc97ce6326518850`(work 기록과 일치).

## 1. 독립 재계산(work `analyze_ulc.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1088_middle_review/`:
`recalc_lap1088.py` `3d2df748…5929`(새 스크립트. 위상은 sim tick·카메라·`GetCursorPos` 시계로 직접 유도, d1 drift/watch는 표본 좌표·쓰기 열 직접 추출) → `recalc_lap1088.json` `b814f23c…3f3d`, 표준 출력 `recalc_out.txt` `abf2e1f2…793c`.
pair-result SHA 접두 11/11이 ESCALATE 기재와 같다. stale_mask SHA 11/11 = pair-result 기재 값, mask와 trace `stale_pixels` 불일치 0. 기준 run: lap1083 k1·k2·k6, lap1085 w1·w2·w6·w7·w8·w9.

| 항목 | ESCALATE 기재 | middle 재계산 | 판정 |
|---|---|---|---|
| (a) U-0 충실도 | c1~c5 reject 21/89, hold 240,703, 총합 532,085, k1 열 동일 | c1~c5 `blend_467580/467B00_reject_size` 21/89, hold 240,703(ord 126~133·140~145·221~225 + 137 2), 수리 전 ord 합 240,701, 총합 532,085, 위 ord 열 k1과 값까지 같음(5/5) | 일치 PASS |
| (b) t1~t5 | reject 0/0, hold 2(ord 137), UL 0, 마지막40 0 | 그대로. t4 hold 밖 ord 353 257·377 55 | 일치 PASS |
| (c) 위상 | 10 run 깨끗 | 10/10 카메라 첫 이동 ord 123(tick 24692), 커서 (0,0) 첫 present 123 또는 124, ord 121..126 tick 건너뜀 0 | 일치 |
| (d) d1 | UL 23 px ord 123 x5..15·y0..4, 커서 ord 122, 표본 (13,1) scr 66 snap 0, 쓰기 `0x46624F`→`0x4662DE` | 그대로(UL bbox·모양 = w6 ord 123). 표본 (13,1) p123 stale 1개(cache 66·lexp 66). p123에 표본을 덮는 `467B00/467580` 기록 없음, 첫 330×200은 p124 (−88,−190) | 일치 |
| (e) E-0·E-1·공통 | UPLEFT (−2,0)×24 왕복, p95 7(진단 11) | 22 lane UPLEFT 24·DOWNRIGHT 24, 관측열 SHA `9206a7d26c7e`/`7e1c2280aac8` 두 lane·k1과 같음, hold p95 7(d1 11)/고정 6~7(d1 12), tps 19.998~20.026, 안전 7종 최대 0, `cleanup.ok`·`game_removed`·`source_unchanged` true, 원본 접두 `b56986e018b4` | 일치 PASS |
| (g) D-0 | 33+11 prefix, restore 4/4·2/2, 7.0→27.5 GiB | report `0197714c…`·`5caaf617…`, 44/44 `prefix` 부재·같은 run `manifest.json` 존재·`removed_private_prefix_only`, 각 batch 첫·끝 archive SHA 재계산 일치, `restore_verification_*` 6/6 `full_content_metadata_match` true, 7.01→22.48→27.52 GiB. 현재 여유 **13 GiB** | 일치 PASS |

**코드 검토(f, 독립 diff: lap1085 w1 bridge `a1f582fc…` ↔ 현재 `d66a3afd…`):** 추가는 env 매크로·`g_blend_size_reject_diag`(기본 FALSE, `initialize_environment`에서 값이 정확히 `"1"`일 때만 on)·헬퍼 `blend_size_reject_diag`뿐이다. 두 wrapper에서 헬퍼 호출은 `reject_bounds` 분기 뒤·before 복사 앞의 `else if`이고, on이면 `active`가 FALSE라 원본만 1회 실행된다. off이면 헬퍼가 FALSE라 수리 후 코드와 같다. 하네스는 `if candidate:` 블록 안에서만 env를 넣고 `--hd-source scale2x`를 요구한다. 테스트는 +1건이며 기존 단언을 지우지 않았다. 결함 없음.

## 2. 정정·새 근거

1. **정정(위상 분류, lap1086 §2·lap1087 판정):** w8은 "커서가 카메라보다 앞선 비깨끗 위상"이 아니다. w8은 ord 122(tick 24692)에서 카메라 첫 이동과 커서 (0,0) 첫 present가 **같은 present**이고 tick 건너뜀이 없다. 이것은 c2·t2·t4·k2와 같은 위상인데 w8은 UL 139 px다. 따라서 "UL은 비깨끗 위상에서만 난다"는 설명은 반례 1개로 깨진다. 위상만으로는 UL을 가를 수 없다.
2. **새 공변량(진단 옵션):** UPLEFT run을 진단 옵션(`--layer-drift --screen-watch`) 여부로 나누면 다음과 같다.

| 구분 | 진단 없음 | 진단 동반 |
|---|---|---|
| 수리 후(H-W330) | UL 1/12(w2, tick 건너뜀) | **UL 4/4**(w6·w8·w9·d1) |
| 수리 전/대조 | UL 0/7(k1·k2·c1~c5) | UL 0/1(k6, 표본은 UL 밖 (360,69)·(540,162)·(300,454)) |

   진단 동반 수리 전 표본이 k6 1개뿐이라, "UL = 진단 부하 + H-W330"인지 "UL = 진단 부하만"인지 지금 자료로는 가를 수 없다. 이것은 work 선택지 (1)이 정확히 겨누는 비교다.
3. **새 근거(writer 귀속):** d1 표본 (13,1)의 p123 첫 쓰기 EIP `0x46624F`는 work 기록처럼 `0x4662DE`(block_copy `0x466280`) 사슬의 일부가 아니라 **별개 함수 `0x466130` 안**이다. objdump(원본 읽기만): `0x466130` `83 EC 14 0F BF 54 24 1C`(앞 `0x466127 ret 0x14`+nop), 쓰기 `0x46624C mov [edx+eax],cl`(DR 보고 EIP = 다음 명령 `0x46624F`), 클립 `[edi+0x4D0..0x4DC]`, 목적지 `[edi+0x1514]`, 끝 `0x466272 ret 0x14` → 5인자 클립 바이트 block copy다. `g1_mirror2x.c`에 `0x466130` hook은 **없다**(`G1_CACHE_COPY` = `0x466280`만). 호출 스택 `0x437AB0`(`0x4662DE`는 `0x438045`). `0x46624F` 쓰기는 진단 4 run 모두 스크롤 시작 present(p123 또는 p124)부터 24 present 동안 매 present 나타난다(d1 71회, w6 72, w8 70, w9 70). d1 p123 표본 값은 `0x466130` 66 → `0x466280` 66 = scr 66인데 snap 0이다. 왜 snap이 0인지(앞 present 커서 `0x466E67` 값 21과도 다름)는 UNKNOWN이다. **UL 귀속 1순위 후보는 미후킹 `0x466130`이지만 이번 자료로는 미입증이다.**
4. 관찰: d1 hold 밖 ord 296 232·304 56·315 18, hold 안 ord 219 233·243 317은 k6·w8의 진단 동반 영역과 같은 종류다(비차단, backlog 유지).

## 3. 판정

- **D-0 PASS 수용.**
- **U-0 PASS 수용**(충실도 5/5, 코드 결함 없음).
- **H-ULc U-1 (c) INCONCLUSIVE 수용.** 계산은 work와 일치한다. 다만 판정 근거 서술 중 "UL은 비깨끗 위상에서만"은 위 정정 1로 철회한다.
- **H-W330 사전등록 PASS(partial)은 계속 HOLD.** 선택지 (2)(기준 완화 수용)는 고르지 않는다. 같은 옵션 c/t 대조는 끝났고, 남은 교란 변수(진단 동반)를 직접 대조하는 실행이 싸고(약 3 분/run) 결정적이기 때문이다. 이것은 lap1086 (c) 규칙("같은 대조를 반복 연장하지 않는다")을 어기지 않는다. 옵션이 다른 새 대조다.
- 핵심 효과(330×200 reject 0, hold 240,703 → 2, 고정 291,382 → 0)는 lap1086 수용 그대로 유지한다. 변경은 uncommitted로 둔다. 제품 G1 마감이나 사용자 승인이 아니다.

## 4. 다음 work 사전등록(Sonnet) — D-0 → H-ULd(진단 동반 c/t 대조)

**D-0(필수 선행):** 현재 여유 13 GiB. lap1087b `archive.py` 복사본 절차(출력 경로만 바꿈)로 `lap1069_s3_nd1` 이후 종료 prefix(lap1071·1073·1075·1077·1079·1081·1083·1085·1087 순)를 처리해 **여유 ≥ 22 GiB**를 만든다. 조건·`prefix`만 삭제·batch마다 full restore 규칙은 같다. 회차 중 10 GiB 밑이면 끝난 run prefix를 같은 절차로 처리한 뒤 계속하고, 불가하면 남은 run을 시작하지 않고 기록한다.

**가설 H-ULd:** UL은 진단 옵션이 바꾼 present 시간에서 나는 기존 잔여이고 H-W330과 무관하다.

**실행(코드·하네스 변경 없음, 순차, load ≤ 8, run마다 game 사본 삭제):** lap1087 `run_u.sh`를 새 디렉터리에 복사하고 run 이름·옵션만 바꾼다. 공통 = lap1087 d1 옵션 그대로(`--hd-source scale2x --terrain-scroll --terrain-scroll-edge --terrain-scroll-keys UPLEFT,DOWNRIGHT --p4b-s-snapshot --reference-completed-states <lap888 REF> --layer-drift --screen-watch --drift-samples "1,1;13,1;20,19" --stale-mask 118-130`). **cd1,td1,cd2,td2,cd3,td3,cd4,td4 교대 8 run**. `cd*`는 여기에 `--blend-size-reject-diag`를 더한다.

**측정(run마다):** UL 상자(x0..31·y0..22) hold 안 stale 합과 ord, hold 합·ord별 값, `blend_*_reject_size`, 위상(카메라 첫 이동 ord·tick, 커서 (0,0) 첫 present, ord 121..126 tick 건너뜀), 표본 stale 기록(`s` scr≠snap)과 그 present의 watch 쓰기 열(특히 `0x46624F`), p124 이전 `467B00/467580` `w` 기록, E-0·E-1·안전 7종·cleanup·source_unchanged.

**PASS / FAIL(사전등록):**
- **충실도:** cd run마다 counters reject 21/89이고 수리 전 ord(126~133·140~145·221~225) 합이 k6와 같은 240,701이어야 한다. 아니면 대조 무효(BLOCKED, 원인 기록).
- **판정(충실도 성립 시):**
  - (a) cd 중 1 run 이상 UL > 0 → UL은 H-W330과 무관 → **H-W330 PASS(partial) 확정**. UL은 backlog H-UL(writer 1순위 후보 미후킹 `0x466130`)로 옮긴다.
  - (b) cd 4/4 UL 0이고 td 3/4 이상 UL > 0 → H-W330 부작용 의심 → HOLD 유지. 다음은 UL present의 `467B00/467580` 전 호출 열거(표본 무관 기록)와 before 버퍼 상태 진단이다.
  - (c) 그 밖(td도 2/4 이하) → 진단 공변량이 재현되지 않음. middle은 UL을 "드문 일시 잔여(마지막40 0)" backlog H-UL로 옮기고 H-W330은 "핵심 효과 수용·PASS(partial) HOLD" 표기를 유지한 채 다음 G1 작업으로 넘어간다. 같은 대조를 더 늘리지 않는다.
- 공통 FAIL: 안전 위반·크래시·성능 초과(진단 run hold p95 > 고정+16).
- 기록 freeze 뒤 `make check`는 SKIP 가능(source·하네스·테스트 불변이고 lap1087 full PASS 1668이 있다). 바꾼 것이 있으면 lint·typecheck 뒤 1회 실행한다.

그다음 후보: save000 UPLEFT 맵 경계 stale ≈189k 귀속(H-D2k-s0, 첫 후보 `rect_fill_466070` reject 40), HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: ord 137 (799,408..409) 2 px, ord 352/353 257 px 일시 사건(t4 추가), throttle 전용 ord 123 writer, `0x467E60` wrap 계수, lane 위상 경합, 진단 동반 영역(w8 ord 242·296, k6 ord 147·219·296~318, d1 ord 219·243·296·304·315).

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT와 focused 테스트(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스·테스트는 lap1087 그대로이며 lap1087 full PASS 1668이 있다.

## 다음 한 가지

work(Sonnet): §4 D-0(여유 ≥ 22 GiB) → H-ULd 8 run(cd/td 교대). G6/G7은 사용자 합격(APPROVALS lap989) 대기이며 루프를 막지 않는다.

## 부록: lap1087 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1087 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — D-0 PASS + H-ULc U-0 구현·U-1 실행 완료, 사전등록 판정 (c) INCONCLUSIVE(c 0/5·t 0/5, 10 run 전부 깨끗한 위상). work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용/다음 설계가 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1087_work_ulc 의 {c1..c5,t1..t5,d1}/pair-result.json·candidate/trace_raw.jsonl·input_trace_raw.jsonl·stale_mask.bin·(d1) layer_drift.jsonl·screen_watch.jsonl 을 work 스크립트(analyze_ulc.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: c1 ec3b155c8e60 t1 f60a5b320879 c2 b7df85ca074a t2 b609ca464d48 c3 32d6b4d0ec33 t3 24ff8cf17982 c4 506fcdfe0d09 t4 ab733f9c091c c5 e9e792c6f783 t5 64c5e28dd272 d1 fcf3ced658bc. 기준: lap1083 k1·k2, lap1085 w1·w2·w7(w6).
2. 검증 항목: (a) U-0 충실도: c1~c5 blend_467580_reject_size 21·blend_467B00_reject_size 89, hold 합 240,703(= k1 열 ord 126~133·140~145·221~225 값 동일, ord 137 2), 총합 532,085. (b) t1~t5 reject 0/0, hold 합 2(ord 137), UL(x0..31·y0..22, ord 122~124) 0, 마지막40 0. (c) 위상: 10 run 전부 카메라 첫 이동 ord 123·커서 (0,0) 첫 present 123 또는 124·ord 121~126 tick 건너뜀 없음(= 깨끗) → 사전등록 (a)(b) 둘 다 불충족 = (c) INCONCLUSIVE. (d) d1(t+진단): UL 23 px ord 123 x5..15·y0..4(w6 같은 상자), 커서 (0,0) 첫 present ord 122(카메라보다 앞), 표본 (13,1) scr 66 snap 0, 쓰기 열 0x46624F→0x4662DE(val 66, tid 280; 0x4662DE는 block_copy 0x466280 안, lap974 census). (e) E-0 UPLEFT (−2,0)×24 왕복·E-1 hold p95 7(진단 11)·안전 0·cleanup·source_unchanged·mask=trace. (f) 코드: tools/inmm_stub/g1_mirror2x.c 의 blend_size_reject_diag 헬퍼(기본 off, env SYW2_G1_BLEND_SIZE_REJECT_DIAG)·mirror_blend_wrle(폭>320 또는 높이>160)·mirror_blend_clip(폭>320) 분기가 bounds 검사 뒤·before 복사 앞이고 on일 때 active FALSE(원본만 실행)인지; tests/test_g1_mirror2x.py 신규 테스트 1건이 기존 H-W330 단언을 완화하지 않았는지(+1 테스트, 기존 단언 불변). (g) D-0: local/maintenance/20261007_lap1087_prefix_archive/(report.json 0197714c…, 33 prefix, restore 000/010/020/030) 및 20261007_lap1087b_prefix_archive/(report.json 5caaf617…, 11 prefix, restore 000/010), 여유 7.0→27.5 GiB, 현재 13 GiB.
3. 수용/다음 사전등록 후보(work는 고르지 않음): UL은 비깨끗 위상(수리 후 발생 5건 w2·w6·w8·w9·d1 전부 비깨끗, 수리 후 깨끗 7 run·수리 전/대조 8 run 전부 0)에서만 나왔고 수리 전에는 비깨끗 표본이 0이라 c/t로 판정 불가. 선택지 (1) 진단 동반 비깨끗 위상(--layer-drift --screen-watch가 커서를 ord 122로 앞당김)에서 c 3 vs t 3 같은 진단 옵션 대조, 또는 하네스 위상 교란; (2) UL을 H-UL backlog(비깨끗 위상 잔여, writer 0x4662DE block_copy 미갱신)로 옮기고 H-W330을 "핵심 효과 수용 + UL 별도 backlog"로 수용(기준 완화이므로 middle/사용자 판단 필요). 그다음 save000 UPLEFT 맵 경계 stale ≈189k 귀속(H-D2k-s0), HUD/GDI·전체 HD coverage·G1 사용자 승인 준비. 게임 실행 전 D-0 재실행 필요(여유 13 GiB < 22; archive.py 복사본은 lap1087b 디렉터리 사용, 대상 lap1069_s3_nd1 이후 미처리 prefix).
기록 docs/history/laps/20261007_lap1087_work_g1_hulc_ul_control.md. 변경(uncommitted): tools/inmm_stub/g1_mirror2x.c·tools/g1_saved_scene_probe.py·tests/test_g1_mirror2x.py. 원본 EXE b56986e0…08a8ac 불변.
```

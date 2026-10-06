# 2026-10-06 | lap1080 | G1 middle — H-LD 독립 검수 + H-L2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1079 work `loop/ESCALATE_SOL`(SHA256 `de56cc035e03d477f2a76a0c335cea1c52715e3d3f805fbbf6f83cde82e5e6b1`, 원문은 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1078 §5 H-LD — present 간격이 늘면 카메라 정지 뒤 남는 world 영역을 미러가 놓친다. candidate만 SIGSTOP/SIGCONT로 느리게 하면 재현되고, 진단 표본으로 writer를 귀속할 수 있다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 직접 재계산해 MATCH(읽기만). fixture: 비합성 save006·save000. lap1079 산출물만 읽음.
- 검수한 source 해시: `tools/g1_saved_scene_probe.py` `6c9a3bb1a3950c45…`, `tests/test_g1_saved_scene_probe.py` `67ddbf8695ec5f90…`. work 기록의 접두와 일치한다. 제품 C/bridge는 lap1077 그대로다.

## 1. 독립 재계산(work `analyze_ld.py`·`analyze_ld2.py`·`mask_ld.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1080_middle_review/`:
`recalc_lap1080.py` `d0131a10…ec59`(lap1078 middle 스크립트 기반, throttle·hold 간격·≥100 px·표본 귀속 집계 추가) → `recalc_lap1080.json` `a204c094…5de8`, 표준 출력 `recalc_out.txt` `eec9a3b1…f87`.
pair-result SHA 접두 8개는 ESCALATE 기재와 모두 일치한다. stale_mask SHA는 8/8 모두 pair-result 기재 값과 같고, mask와 trace `stale_pixels` 불일치는 0이다. 정상 속도 대조 run은 lap1077 lb1·lb2(save006 LEFT,RIGHT edge)다. hold 창 정의는 lap1072~1078과 같다.

| 항목 | 사전등록(lap1078 §5) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| LD-0 throttle | PID 1개·정지 잔존 0·baseline 없음 | 8 run 모두 `candidate_throttle` status PASS, pid 1개, `final_state` R, `final_state_not_stopped` true, `process_gone` false. baseline lane에는 throttle 필드가 없다. stop 167회·3,373.5 ms(20:30), 120회·4,826~4,836 ms(40:30) | 동일 | 일치 PASS |
| LD-1 전제 | present p50 ≥60 ms | hold 창 present 간격 p50: ld1·ld2 **50/50**(전제 미달), ld5~ld10 **70/70/71/70/70/70**, 고정 구간 p50 50. tps 20.02/20.03, 19.98/19.98/19.96/19.96/19.96/19.95 | 동일 | 일치 |
| LD-1 save000 | — | ld5·ld6 hold 합 0/0, 마지막40 0. candidate 17/17칸(baseline 24/24) | 0/0 | 일치 |
| LD-1 save006 | ≥100 px/present 재현 | ld7·ld8 hold 합 **10,001/10,258**, ≥100 px present **13/14**. ord 171..182 = 746·749·763·758·771·749·792·838·837·859·966·974이고 ld7=ld8=ld9 같은 값. 카메라 (141,118), tick 24760..24776 | 동일 | 일치 REPRODUCED |
| 안전·정리 | 7종 0·cleanup·source_unchanged | 8 run 안전 7종 최대 0, 두 lane game_removed·source_unchanged true, 최종 카메라 (158,101)·save000 (39,53) | 동일 | 일치 PASS |
| LD-2 마스크 | — | ld9 ord 171..182 bbox 합집합 x531..643·y29..63(3,050 px). present별 bbox 폭 54·높이 35, 중심 x 560.9→615.8(present당 약 5 px 오른쪽 이동) | 동일(이동 "약 4 px") | 일치 |
| LD-2 귀속 | 표본 3/3 | ld10 표본 (583,52)(588,55)(590,41), stale 표본×present **21개**(7/7/7), 마지막 writer **EIP `0x00467F97` tid 280 21/21**, val==scr 21/21, 스택 `0x0041AA04`←`0x004789DE` 21/21, watch dropped/overflow 0 | 동일 | 일치 PASS |

## 2. 코드·디스어셈블 검토

- 하네스: `_throttle_target_error`는 lane이 candidate가 아니거나, PID가 lane `proc.pid`와 다르거나, wineserver이거나, cwd가 private game이 아니거나, private EXE가 매핑되지 않았으면 거부한다. `_CandidateThrottle._loop`는 STOP 뒤 항상 CONT를 보내고, `stop()`은 idempotent하게 항상 SIGCONT를 보낸 뒤 상태 `T`가 아님을 확인한다. 시작은 첫 input tick barrier 뒤이고, `stop()`은 정상 경로와 `finally` 두 곳에서 부른다. `/proc/<pid>/exe` 대신 cwd+maps를 쓴 편차는 타당하다(공유 로더라 lane을 구분할 수 없다). 결함은 없다.
- 원본 `0x467E60`(독립 objdump): 5 B 경계 `83 EC 08 55 56`, `ret 0x1c`, 인자 = x·y·w·h·rle·remap·level(16비트 x/y/w/h). 행 기준 주소 = `[ecx+0x1514]` + y×`[ecx+0x10]` + x이고 **클립(+0x4D0..0x4DC)은 없다**. RLE `0xFE n`은 n칸 건너뛰기다. 쓰기는 `0x467F93 mov [eax+esi-1],bl`로 열 **x+w−1−k**(좌우 반전)에 쓰고, 배경은 열 **x+k**(반전하지 않은 열)에서 읽는다. 따라서 행 후반부는 같은 호출이 이미 쓴 픽셀을 다시 읽는다. 쓰기 범위는 [x, x+w)×[y, y+h)를 넘지 않는다. 호출처는 `0x41A887`·`0x41A9FF` 두 곳이고, 둘 다 `ecx=0xE5BF18` 꼬리 wrapper다. `0x41A9B0` wrapper는 `0x4789D9`에서 불린다(복귀 `0x4789DE` = 스택 일치).
- **형제 관계(새 근거):** wrapper `0x41A9B0`(→`0x467E60`)은 이미 hook된 `0x4678C0`(H-P `mirror_blend_clip7`, wrapper `0x41A950`)의 wrapper와 인자 조립이 같다. `0x41A840`(→`0x467E60`)도 `0x41A827` 호출 wrapper 바로 뒤에 있다. 즉 `0x467E60`은 `0x4678C0`의 **좌우 반전·클립 없는** 형제다.

## 3. 정정(비차단)

1. **원인 서술:** "present 간격 증가가 원인"은 입증되지 않았다. throttle된 candidate는 LEFT를 17칸만 이동해 (141,118)에 섰고, 정상 속도 lane은 24칸 이동해 (134,125)에 선다. stale은 정지 43 tick 뒤(tick 24760)에 시작해 12 present 이어지고, RIGHT 입력(tick 24788) 전에 끝난다(ord 183 = 0). 유닛 덩어리는 화면 상단 x531..643에서 present당 약 5 px씩 움직인다. 정상 속도 카메라는 7칸 더 왼쪽이라 같은 world 위치가 화면 오른쪽 밖(edge 1칸 ≈65 px, lap1073 → 약 +455 px)으로 나간다. 따라서 **위치 가설 H-pos**(미후킹 `0x467E60`이 그리는 반전 반투명 유닛이 화면에 보이기만 하면 정상 속도에서도 stale이 생긴다)가 더 간단한 설명이다. 이 가설은 아직 검증하지 않았다(H-L2 계수로 판별한다). 그래도 수리 대상은 같다.
2. **H-L2 검증 목표:** ESCALATE의 "hold 합 10,001→0"은 틀렸다. ord 123(199 px, x0..31·y285..303, ld7~ld9)과 ord 140(257 px, x400..427·y310..328, ld8~ld10)은 유닛 bbox 밖이고 시간도 다르다. ld10 ord 191(184 px, (142,117) RIGHT 시작)도 마찬가지다. 표본 귀속 범위 밖이므로 목표는 **ord 171..182 → 0**이다. 나머지 ≤456 px는 별도 잔여로 기록한다.
3. ld10 hold ≥100 px 13개에는 ord 140·191이 들어 있다(work "ord 171..181"만 서술). ld7·ld8 합 차이 257은 ord 140 하나다. 결정론 서술은 ord 171..182 범위에서만 맞다.
4. 이동량은 present당 "약 4 px"가 아니라 약 5 px다(중심 x 기준).

이전 "부하 동반" 사례 가운데 lap1074 x1(save006 LEFT 정지 (142,117) ord 134..144)은 같은 계열로 보인다. lap1072 c·f(save000 DOWN 정지)와 lap1056 r1(save006 p651..664)은 귀속되지 않았다(UNKNOWN 유지).

## 4. 판정

**H-LD 수용: LD-0 PASS, LD-1 REPRODUCED(save006 LEFT,RIGHT edge 40:30, 2/2), LD-2 PASS(표본 21/21 → 미후킹 `0x467E60`).** 원인 서술은 정정 1대로 "위치 가설 미검증"으로 바꾼다. 제품 G1 마감이나 사용자 승인이 아니다.

## 5. work H-L2 사전등록(다음 work, Sonnet) — `0x467E60` diff 미러

1. **L2-0 테스트 먼저(RED→GREEN):** (a) objdump 전사 C 모델로 전수/무작위 검사(RLE `0xFE n` 건너뛰기, 넘침 포함): 모든 쓰기 ⊆ [x,x+w)×[y,y+h), 쓰기 열 = x+w−1−k, 읽기 열 = x+k. (b) hook 표 계약: old bytes `83 EC 08 55 56`, `ret 0x1c`, thiscall, 7 인자 그대로 전달. (c) details builder 최악 길이 테스트를 새 블록 포함으로 갱신한다.
2. **L2-1 구현:** `mirror_blend_clip7` 형태를 복제한 hook(예: `mirror_blend_flip7`)을 만들고 계수 `blend_467E60_*`(invocations·mirrored_calls·mirrored_pixels·changed·reject_target/bounds/size/guard)를 둔다. 원본에 클립이 없으므로 영역은 **사각형∩화면**(`g1_rect_screen_region` 방식)이다. 화면 밖 부분 때문에 reject하지 않는다. 320×160을 넘으면 `g1_overlay_blt_apply_tiled`를 쓴다. 원본은 정확히 1회 부른다(행 안 읽기-쓰기 의존이 있어 재구현하지 않고 before/after diff로 미러한다). 대상 검사(screen renderer `0xE5BF18`, 캐시·panel 제외)는 기존과 같다.
3. **실행(순차, load ≤8):**
   - (a) ld7 옵션(save006 LEFT,RIGHT edge `--candidate-throttle 40:30` `--stale-mask 170-183`) 2회: ord 171..182 합 0/0, 다른 ord가 늘지 않음(ord 123/140 ≤ 기준).
   - (b) 정상 속도 save006 LEFT,RIGHT edge 1회(lb1 옵션): hold 0. `blend_467E60` 계수로 H-pos를 판별한다. invocations>0이고 mirrored_calls=0이면 화면 밖 호출이라 H-pos를 지지한다. invocations=0이면 판별 불가로 기록한다.
   - (c) 비회귀: save006 UP/DOWN edge 1회 hold 0, save000 DOWN,UP 키 hold 1회 hold 0·gate가 lap1077 lb5와 같음, save006 고정 1회 300..848 0. 공통: E-0 24칸 왕복, p95 ≤ 고정+16, 안전 7종 0, cleanup, source_unchanged.
4. **PASS / FAIL:** (a) 2/2에서 ord 171..182 = 0이고 (b)(c)가 모두 PASS면 **H-L2 PASS(partial)**다. 유닛 bbox 안 stale이 남으면 같은 옵션에 `--layer-drift --screen-watch`로 표본 진단 1회를 더 하고 FAIL로 기록한다. 안전 위반·크래시면 FAIL이다. 실패 가설 2회면 BLOCKED다.

그다음 후보: 모서리(대각) 스크롤, HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: ord 123/140/191 소잔여(throttle 전용), lap1072 c·f·lap1056 r1 UNKNOWN, lane 위상 경합, lap1069 s2 117 px, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT와 focused 테스트(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`)를 돌린다. 결과는 STATUS에만 보강한다.
- 전체 `make check`는 SKIP한다. 문서만 변경했고 source·하네스는 그대로이며 lap1079 full PASS 1661이 있다. 다음 work H-L2가 변경 뒤 실행한다.

## 다음 한 가지

work(Sonnet) H-L2: §5 L2-0 → L2-1 → 실행 (a)(b)(c). G6/G7은 사용자 합격(APPROVALS lap989) 대기이며 루프를 막지 않는다.

## 부록: lap1079 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1079 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-LD(부하 동반 stale 재현·귀속) LD-0 하네스·LD-1 재현·LD-2 귀속 완료. work는 자기 결과를 승인하지 않으며 fresh Opus middle 독립 재계산과 수용 판정이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1079_work_hld 의 {ld1,ld2,ld5,ld6,ld7,ld8,ld9,ld10}/pair-result.json·candidate/trace_raw.jsonl·(ld9) candidate/stale_mask.bin·(ld10) candidate/{layer_drift,screen_watch}.jsonl 을 work 스크립트(analyze_ld.py·analyze_ld2.py·mask_ld.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: ld1 7a504c92d52c ld2 8491c034fb9e ld5 82cc05dbd141 ld6 e62ea65aa98f ld7 a0be48b02e07 ld8 e054419d9083 ld9 1ee801acdb3e ld10 8007383d7539.
2. 검증 항목: (LD-1) 모든 run candidate_throttle(pair-result candidate.candidate_throttle) pid 1개·stop_count·final_state_not_stopped true·baseline lane에 throttle 없음. hold 창(sim_tick down_input_tick..final_observation_tick) present 간격 p50: 20:30(ld1·ld2) 50 ms = 전제(≥60) 미달, 40:30(ld5~ld10) 70 ms·tps ≈19.9. ld5·ld6(save000 DOWN,UP)은 hold stale 0, ld7·ld8(save006 LEFT,RIGHT edge)은 hold 합 10,001/10,258·≥100 px present 13/14·ord 171..182(746·749·763·758·771·749·792·838·837·859·966·974)·두 run 일치(결정론)이고 안전 7종 0·pair 정지 카메라 (141,118). (LD-2) ld9 마스크 ord 171..182 = 유닛 덩어리 bbox x531..643 y29..63·trace 계수=마스크 n·ld10 표본 (583,52)(588,55)(590,41) stale 표본×present 21개 전부 마지막 writer EIP 0x00467F97 tid 280 val==scr 21/21(스택 0x41AA04←0x4789DE).
3. 코드·디스어셈블 검토: tools/g1_saved_scene_probe.py(`_throttle_target_error`가 baseline·pid 불일치·wineserver·cwd 불일치·private EXE 미매핑을 거부, `/proc/<pid>/exe`는 공유 로더라 cwd+maps로 대체한 편차 / `_CandidateThrottle.stop()` 항상 SIGCONT·idempotent·종료한 프로세스 허용 / 시작은 첫 input tick barrier 뒤 / baseline에 넘기면 ProbeError)·tests 8건 신규(tests/test_g1_saved_scene_probe.py 213 passed). 원본 EXE `objdump -d -M intel --start-address=0x467E40 --stop-address=0x467FE0`: 0x467E57 ret 0x14(0x467B00 끝)·0x467E60 `83 ec 08 55 56`·0x467F93 `88 5c 30 ff mov [eax+esi-1],bl`·0x467FC6 ret 0x1c·호출처 0x41A9FF(`b9 18 bf e5 00 e8 5c d4 04 00`)와 0x41A887. g1_mirror2x.c define에 0x467E60 없음(미후킹).
4. 수용 시 다음 work 사전등록: H-L2 = `0x467E60` hook(old bytes `83 EC 08 55 56` 5 B, ret 0x1c·7 인자, thiscall ecx=0xE5BF18) diff 미러, 테스트 먼저(C 전수 모델: 0xFE 건너뛰기·팔레트/LUT 쓰기가 bbox±1 ∩ clip 안), 검증 = ld7 옵션(save006 LEFT,RIGHT edge, `--candidate-throttle 40:30`)에서 hold 합 10,001→0, 정상 속도 save006/save000 hold 0·E-0·p95·안전0 비회귀. 또는 정상 속도에서 0x467E60 호출 여부 확인 진단. backlog: lane 위상 경합, lap1069 s2 117 px UNKNOWN, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal, 모서리(대각) 스크롤.
기록 docs/history/laps/20261007_lap1079_work_g1_hld_load_stale_repro_467e60_attribution.md. 변경(uncommitted): tools/g1_saved_scene_probe.py·tests/test_g1_saved_scene_probe.py. 제품 C/bridge 불변. 원본 EXE b56986e0…08a8ac 불변.
```

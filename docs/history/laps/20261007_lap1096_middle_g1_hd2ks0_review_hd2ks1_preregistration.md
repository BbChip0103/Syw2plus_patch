# 2026-10-06 | lap1096 | G1 middle — H-D2k-s0(`0x465FC0` 미러) 독립 검수 + save000 고정 카메라 잔여(H-D2k-s1) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1095 work 기록 `20261007_lap1095_work_g1_hd2ks0_cache_fill_465fc0.md`, 그 `loop/ESCALATE_SOL`(원문 byte 일치 보존 `20261007_lap1096_preserved_lap1095_escalate_sol.txt`, SHA256 `b1b38689…2b70`, 보존 뒤 삭제), 사전등록 `20261006_lap1094_middle_g1_huld_review_hd2ks0_preregistration.md` §4.
- INBOX·APPROVALS: lap1095 뒤 새 사용자 지시는 2026-10-06 21:21 KST "G6·G7 달성·종료, G1 최우선"뿐이다. STATUS의 "G7 사용자 재시험 대기" 줄은 이 결정으로 낡았기에 정정한다. root가 그 지시로 커밋 `34d59dd`(lap1095 source 포함)를 만들었다. 현재 트리 = HEAD(`git status`는 미추적 `dxwnd.ini`뿐)이므로 lap1095 source는 이제 "uncommitted"가 아니다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). 7 run `source_exe_sha256` 접두 `b56986e018b4` 7/7. fixture: 비합성 save000(s·c·r1·r2)·save006(r3). 활성 8인 증명 아님.
- 현재 트리 source 해시(직접 계산) = work 기재 9/9: `g1_cache_fill.h` `c691aabe704191a3`, `g1_mirror2x.c` `097da0c2a56a39c9`, `g1_mirror2x.h` `675d7380d194da7e`, `direct_draw_trace.c` `cda6c1f96ddab2c5`, `g1_screen_watch.c` `1e3bd180a46b61a9`·`.h` `3f7037c4ec9ae37e`, `g1_saved_scene_probe.py` `541c1d8f605fb568`(= 7 run `execution_source.host_probe_sha256`), `test_g1_cache_fill.py` `55086cf76231327f`, `test_g1_screen_watch.py` `cfdc09ea96520f7d`. run별 bridge 복사본: s·c = `g1_mirror2x.c` `d66a3afd…`(수리 전 트리, `g1_cache_fill.h` 없음), r1·r2·r3 = `097da0c2…`+`c691aabe…`(현재 트리).

## 1. 독립 재계산(work `analyze_hd2ks0.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1096_middle_review/`:
`recalc_lap1096.py` `743334b6…815e` → `recalc_lap1096.json` `50ec04a0…8aca`·`recalc_out.txt` `7164e507…9dc9`, 보조 `recalc_lap1096_b.py` `ec57800a…b778` → `recalc_lap1096_b.json` `7ce290d3…36de`.
pair-result SHA: s1 `8bb2c0e8`, s2 `836f9db6`, c1 `25b87de6`, c2 `c0576e30`, r1 `bcceadc7`, r2 `a3547289`, r3 `64b5fb00`.

| 항목 | work 기재 | middle 재계산 | 판정 |
|---|---|---|---|
| 재현 s1·s2 ord 145..221 | 14,512,493 / 14,512,202 | 같다. ord 136..146 열 `0,749,9287,26868,…,188787` 두 run 같음, lap1083 k4 14,554,183과 같은 모양 | 일치 |
| 수리 r1·r2 ord 145..221 | 0 / 0 | 같다. 전체 47,323/47,526·최대 3,592(ord 260)·마지막40 47,319 | 일치 |
| r3 save006 | PASS·stale 2 | PASS(게이트 11개 전부 PASS)·전체 2(ord 137)·마지막40 0 | 일치 |
| 마스크=trace | — | 7/7 run, 덤프 64개마다 값 2 개수 = 그 ord의 `stale_pixels`(불일치 0). s·c ord 150 stale bbox x0..799·y0..458, 세 표본 모두 stale. r1·r2 ord 150 세 표본 모두 match | 일치 |
| 캐시 watch c1·c2 | 표본 0·1 `0x4DB203`, 표본 2 `0x46605B` 9 | 같다. 전 hit: i0 `0x4DB203` 43·`0x4DB384` 1, i1 43·1, i2 `0x4DB203` 24·`0x468DBA` 17·`0x46605B` 9(c1=c2). 값 0 쓰기: i0 `0x4DB203` 11·`0x4DB384` 1, i1 1·1, i2 `0x46605B` 9·`0x4DB203` 16. i2 첫 0 쓰기 스택 `0x432DE0` | 일치 |
| 계수 r1·r2 | 33·31·923,648·reject_target 2·unsupported 0 | 같다. r3 = 3·1·425,984(캐시 전체 832×512 1회)·2·0. `rect_fill_466070_reject_size` 40/40/7, `layer_move_unsupported` 0 | 일치 |
| 안전·성능·정리 | 안전 0·p95 7~8 | 안전 7종 최대 0(7/7), p95 s1 13·s2 12·c1 12·c2 13·r1 7·r2 8·r3 8 ms, 두 lane `cleanup.ok`·`game_removed`·`source_unchanged` 7/7 | 일치 PASS |
| r1 parity | terrain_scroll HOLD | 같다. `complete_records_equal` false(owner 3 AI 그룹), r2·s·c는 PASS | 일치 |

**새로 계산한 근거:**
- watch·drift의 `p`는 PS3 ordinal이다. drift의 첫 `scr≠snap` present가 마스크에서 그 표본이 처음 stale이 되는 ord와 3표본×3 run 모두 같다(s1 139/143/142, c1 140/144/143, c2 139/143/142).
- 인과 사슬이 기록과 맞는다. 첫 0 쓰기는 표본 2(x50, 채움 띠 x0..63 안)가 `0x46605B` 직접이다. x100·x400 표본은 그 0을 오른쪽으로 옮기는 memmove(`0x4DB203`/`0x4DB384`, 후킹·layer 이동 미러됨)다. memmove 미러는 `g_layer_expected`도 옮긴다. 그래서 채움이 미러되지 않으면 옛 터레인 기대값(100/148/208)이 따라 옮겨져 `cache 0 ≠ lexp`가 된다. 표본 2의 첫 stale가 늦은(142) 것은 후킹된 shade `0x468DBA`가 p141까지 208을 다시 칠했기 때문이다(c 기록과 일치).

## 2. 코드·바이트 검토

- **원본 역어셈블(직접, objdump `0x465FC0..0x46606C`):** thiscall(ecx=renderer `0xE5BF18`), 인자 5(x1 y1 x2 y2 색) `ret 0x14`. x·y 쌍을 각각 정렬하고 `h = ymax−ymin+1`, `w = xmax−xmin+1`로 둔다. 한 dword에 들어가는 픽셀 수 = `32/[ecx+0xC]`(bpp)이고 행마다 `w/(32/bpp)` dword를 `rep stosd`로 채운다(`0x46605B`). 시작 주소 = `[ecx+0x1514] + [ecx+0x10]·ymin + xmin`, 다음 행 = stride이며 클립은 없다. 앞 5 byte `8B 54 24 0C 53` = 훅 pinned old bytes. 호출처 `0x432DCB..0x432DDB` = `(0,0,63,511,0)`(왼쪽 64열 띠 지우기) → 반환 `0x432DE0` = watch 스택과 일치.
- **훅 모델(`mirror_cache_fill`·`g1_cache_fill_region`):** 원본을 먼저 실행한 뒤 buffer=`0xBA3D30`·stride=832일 때만 모델을 갱신한다. 8bpp가 아니거나 캐시 밖이면 `unsupported`로 세고 갱신하지 않는다. 폭 `floor(w/4)·4`·높이 ymin..ymax 포함·xmin 시작은 원본과 같다. 모델은 `g_layer_*`(stub 메모리)만 쓰고 게임 메모리를 쓰지 않는다 → 시뮬레이션에 영향 없음. 설치 `install_one`·`restore_hook`·installed 확인 3곳과 계수 reset이 있다. census(`g1_census*.c`)는 `0x465FC0`을 후킹하지 않아 주소 겹침이 없다. **결함 없음.**
- 한계(공개 유지): 화면 대상 호출(`reject_target` 2/run)은 미러하지 않는다. 평탄 2×2 블록은 단색 내부에서만 Scale2x와 같고, 경계 보간은 이후 present가 처리한다(r1·r2 plateau stale 0으로 확인).

## 3. 판정

- **H-D2k-s0 PASS(partial, 기술) 수용.** S-2 기준(ord 145~221 ≤5%: 0%·새 reject 급증 0·save006 비회귀 r3 PASS stale 2·안전 0·p95 ≤ 고정+16)을 충족한다. `rect_fill_466070_reject_size` 감소 조건은 귀속 함수가 다르므로 해당 없다.
- **정정 1(S-1 문구):** 사전등록 귀속 기준("표본 ≥2/3의 첫 stale 쓰기 EIP가 한 미후킹 함수")은 그대로는 충족하지 않는다. 직접 EIP는 1/3이고, 2/3은 후킹된 memmove가 그 0을 옮긴 쓰기다. 귀속은 **개입 증거**로 확정한다. `0x465FC0` 미러 하나만 추가한 r1·r2(2/2)에서 평탄 stale가 14.5M → 0이 되었고, 위 인과 사슬이 수치로 맞는다. 이것은 사전등록 상관 기준보다 강한 증거로 본다.
- **사전등록 이탈 수용.** 상시 사용자 지시 "구현 우선"(INBOX, PROMPT ③)이 카드의 보수 조항("다른 함수면 수리 없이 기록")보다 우선한다고 판단한다. 근거는 네 가지다. 변경이 훅 하나다. old bytes는 원본 역어셈블과 일치하고 rollback 경로가 있다. 사전등록 S-2 지표로 검증했다. 공개가 완전하다. **절차 정정:** 앞으로 middle 사전등록에서 "미후킹 writer를 직접 EIP 또는 개입으로 확인하면 같은 회차에 diff 미러를 구현하고 S-2 기준으로 검증한다"를 기본으로 둔다. "수리 없이 기록" 조항은 새 안전 위험이 있을 때만 쓴다.
- r1 `terrain_scroll_parity` HOLD는 lane 위상 경합 backlog로 둔다. 근거: 훅은 게임 메모리를 쓰지 않는다. 같은 트리의 r2와 수리 전 s·c는 PASS다.
- 제품 G1 마감·사용자 승인 아님.

## 4. 다음 work 사전등록(Sonnet) — H-D2k-s1: save000 복귀 뒤 고정 카메라 잔여 귀속 → 조건부 수리

**사전 근거(이 회차 r1·r2·s1 raw 읽기만):** 카메라가 (48,54)에 멈춘 뒤 ord 260..275 stale가 3,592 → 847로 두 present씩 같은 값을 내며 줄고, ord 276..289는 0이다. ord 290..297에서 309 → 1,502로 다시 는다. r1·r2·s1 세 run이 **값까지 같다**(수리 무관·결정적). 마지막40 47,319가 전부 이것이다. 위치는 미확인이다(stale 마스크 덤프 한도 64가 ord 130..193만 덮음).

**가설 H-D2k-s1:** 고정 카메라에서 주기적으로 커졌다 줄어드는 화면 요소(애니메이션 overlay·선택/명령 표시·팝업 등)를 칠하는 writer가 미후킹이거나 mirror에서 거부되어 HD 화면이 그 영역에서 최근접 확대로 떨어진다.

- **S-0 디스크:** 현재 여유 114 GiB. 10 GiB 미만이면 lap1089 D-0 절차로 처리한다.
- **S-1 위치(1 run, l1):** lap1095 `run_r.sh` r1 옵션(진단 없음) + `--stale-mask 250-297`. 측정: ord별 stale bbox·성분, ord 260/275/290/297 마스크 PNG(공유 temp), 같은 장면 candidate 화면 대비 무엇이 그려지는지. 표본 3점을 고른다(ord 260..275 공통 stale 안 2점 + ord 290..297 안 1점, 마스크로 직접 확인).
- **S-2 귀속(2 run, a1·a2):** l1 옵션 + `--layer-drift --screen-watch --screen-watch-cache --drift-samples "<표본 3점>"`. 측정: 표본 첫 stale present의 화면·캐시 쓰기 EIP·값·스택, 같은 present의 reject 계수 변화(trace metrics), stale 열이 r1과 같은지(재현).
  - **귀속 PASS:** a1·a2 모두 표본 ≥2/3의 첫 stale 쓰기 EIP가 한 미후킹 함수로 모인다. 또는 후킹된 이동이 옮긴 값의 원천을 같은 함수로 따라갈 수 있다(lap1095 사슬처럼).
  - **UNKNOWN:** 둘 다 아니면 표본 좌표·watch 범위와 함께 기록한다.
  - **무효:** stale 열이 r1과 다르면 원인을 기록한다.
- **S-3 조건부 수리(같은 회차, §3 절차 정정에 따라 사전 허용):** 귀속이 미후킹 함수 하나이면 그 함수의 diff 미러를 넣는다. 원본 역어셈블로 인자·클립·ret 확인, pinned old bytes·restore·계수, C 모델 테스트 RED→GREEN. 귀속이 기존 hook의 reject(size/bounds)이면 그 reject의 최소 완화·분할을 넣는다(기준·validator 무완화). 검증: save000 2 run(진단 없음) + save006 k1 비회귀 1 run(lap1095 r3 옵션).
  - **PASS(partial):** save000 2/2 마지막40 stale ≤ 2,366(47,319의 5%)·ord 145~221 0 유지·새 reject/unsupported 급증 0·save006 PASS·stale 합 ≤ 307(lap1089 td 수준)·안전 0·p95 ≤ 고정+16.
  - **공통 FAIL:** 안전 위반·크래시·p95 초과.
- source를 바꾸면 lint·typecheck 뒤 기록 freeze 후 `make check` 1회.

그다음 후보(middle이 정함): HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: `0x465FC0` 화면 대상 호출 2회/run, H-UL, throttle 전용 ord 123 writer, `0x467E60` wrap 계수, lane 위상 경합(r1 parity HOLD 추가), 진단 동반 영역.

## 5. 검사

- focused(`test_g1_cache_fill`·`test_g1_screen_watch`·`test_g1_mirror2x`·`test_g1_rect_fill`·`test_g1_saved_scene_probe`·`test_g1_overlay_blt`) `.venv/bin/python` **296 passed/12.95s**(exit 0), 로그 `logs/gates/lap1096-middle-focused.log` SHA256 `0ffe9079e29fd44e…`.
- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS에만 적는다.
- 전체 `make check`는 SKIP한다. 이 회차는 문서만 바꿨고, source·하네스·테스트는 lap1095 full PASS 1691 때와 같다(해시 9/9 일치).

## 다음 한 가지

work(Sonnet): §4 H-D2k-s1. S-1 위치 → S-2 귀속 → 조건부 S-3 수리·검증.

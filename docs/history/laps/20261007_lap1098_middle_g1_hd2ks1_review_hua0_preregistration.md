# 2026-10-06 | lap1098 | G1 middle — H-D2k-s1(`0x467410` 미러) 독립 검수 + G1 사용자 시험판 준비(H-UA0) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1097 work 기록 `20261007_lap1097_work_g1_hd2ks1_blend_467410_diff_mirror.md`, 그 `loop/ESCALATE_SOL`(원문 byte 일치 보존 `20261007_lap1098_preserved_lap1097_escalate_sol.txt`, SHA256 `3d5c3933…edefc`, 보존 뒤 삭제), 사전등록 `20261007_lap1096_middle_g1_hd2ks0_review_hd2ks1_preregistration.md` §4.
- INBOX·APPROVALS: lap1097 뒤 새 사용자 지시 없음. G1 최우선·구현 우선·묻지 말고 결정 유지.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). 7 run 두 lane `source_exe_sha256` 접두 `b56986e018b4` 14/14. fixture: 비합성 save000(l1·a1·a2·v1·v2)·save006(v3·v4). 활성 8인 증명 아님.
- 현재 트리 source 해시(직접 계산) = work 기재 4/4: `g1_mirror2x.c` `2dc25e1b64606554`, `g1_mirror2x.h` `d6b10bbd4a813758`, `direct_draw_trace.c` `f1dae646007cf0d7`, `test_g1_rect_fill.py` `d5d0ded12a96c9e5`; 하네스 `g1_saved_scene_probe.py` `541c1d8f605fb568`(무변경). run별 bridge 복사본: l1·a1·a2 = `097da0c2…`(수리 전 = HEAD), v1~v4 = `2dc25e1b…`(현재 트리). 변경은 여전히 uncommitted(HEAD `34d59dd` 대비 diff 5파일).

## 1. 독립 재계산(work `analyze_*.py`·`pick.py`·`an_a.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1098_middle_review/`:
`recalc_lap1098.py` `5840f88d04f289b8` → `recalc_lap1098.json` `fe1995b23adeda19`·`recalc_out.txt` `7b9312aa25e582e8`, 역어셈블 `objdump_467410.asm` `1135cca479920712`.
pair-result SHA: l1 `159961fa`, a1 `7a5013ca`, a2 `ec3f84c4`, v1 `b8b1a017`, v2 `03af8c23`, v3 `f909d8db`, v4 `482c8ded`(work 기재 7/7 일치). 기준: lap1095 r1 `bcceadc7`·r3 `64b5fb00`.

| 항목 | work 기재 | middle 재계산 | 판정 |
|---|---|---|---|
| l1 재현 | r1과 같은 열, 마지막40 52,089 | 공통 ord 값 r1과 같음(ord 140/141·222/223 2 px 한 칸 위상만 다름). l1은 PS3 300개라 마지막40에 ord 298·299(2,380·2,390)가 들어가 47,319+4,770 = 52,089 | 일치 |
| 위치 | 공성 유닛 실루엣 두 곳 | l1 마스크 ord 250..297 stale 47,319 px 중 **47,319(100%)가 두 `0x467410` 사각형 (480,272,128²)·(384,256,128²) 안**. ord 260..275 교집합 805 bbox x423..567·y299..368 | 일치 |
| 마스크=trace | — | 마스크 있는 8 run 전부, 덤프마다 값 2 개수 = 헤더 = 그 ord `stale_pixels`(불일치 0) | 일치 |
| 귀속 a1·a2 | 표본 3/3 변화 호출 = `0x467410` | 표본 3점×2 run 모두 창 250..300의 stale present마다 같은 p에 `0x467410` 'w' 기록이 그 표본 값을 바꿈(`stale_without_410_change` 0/6). stale일 때 `cache==lexp==snap` 6/6. 같은 창 다른 writer 변화는 후킹된 `0x466B50` p250 1건뿐(stale 시작 전). 'w' 410 a1 52(26+26)·a2 48(24+24), p 260..299/260..297, why 전부 `observe` | 일치 |
| 수리 v1·v2 | 마지막40 0·ord145~221 0·`0x467410` 50/49,741/0 | 같다. 전체 4(ord 141·223 2 px)·최대 2·마지막40 0, v2 마스크 250..297 stale 0, mirrored 50·px 49,741·reject 0 | 일치 |
| 비회귀 v3·v4 | PASS·stale 295/2 | 같다. 게이트 11개 전부 PASS(input_effect·minimap·terrain_scroll·V2/V2s/V2q·scale2x 포함), v3 = ord 137 2 + ord 350 293, v4 = ord 137 2, `0x467410` 호출 0 | 일치 |
| 계수 | 새 reject·unsupported 급증 0 | `cache_fill_465FC0` 33/31/923,648/2/0·`rect_fill_466070_reject_size` 40·`layer_move_unsupported` 0은 r1·l1·v1·v2 같음. `overlay_blt_rejects` 298/302/300/300, `blend_467B00_reject_bounds` 10,267~10,289(present 수 차 범위) | 일치 |
| 안전·성능·정리 | 안전 0·p95 7~8 | 안전 7종 최대 0(9/9). p95 PS3 l1 8·a1 12·a2 12(진단)·v1 8·v2 7·v3 7·v4 7 ms. 두 lane `cleanup.ok`·`source_unchanged` 9/9 | 일치 PASS |

**새로 계산한 근거(정정 아님, 공개):** a1·a2(진단 동반)에는 ord 125..136 소량(25~125 px)과 ord 221/219 233 px stale가 있다. 진단 없는 l1·v1·v2에는 없다 → 기존 backlog "진단 동반 영역"과 같은 성격이며 이번 판정과 무관하다. work 기록은 진단 run의 ord 145~221 값(233)을 적지 않았으나, 판정 기준은 진단 없는 v1·v2에 걸리므로 결과는 바뀌지 않는다.

## 2. 코드·바이트 검토

- **원본 역어셈블(직접, objdump `0x467410..0x467577`):** 앞 5 byte `83 EC 08 53 56`(`sub esp,8; push ebx; push esi`) = 훅 pinned old bytes. 진입 스택 기준 +4 x·+8 y·+0xC w·+0x10 h·+0x14 rle·+0x18 remap·+0x1C weight(`movswl`, 16비트 부호 확장), `ret 0x1C` = 7인자. 시작 주소 = `[ecx+0x1514] + y·[ecx+0x10] + x`, 행마다 `ebp < w`인 동안만 쓰고(0xFE 스킵은 ebp만 늘림) h행 뒤 종료. 클립 필드(`+0x4D0..+0x4DC`) 참조 0. 쓰기는 `dst` 값과 rle 색을 remap·weight 표로 섞어 palette 색을 다시 쓰는 dest 의존 혼합(`0x46753B`). → **쓰기 범위 ⊆ 전달 사각형**, 클립 교집합 미러가 화면 안에서는 superset이다.
- **훅(`mirror_blend_410`):** `0x467580` 미러(`mirror_blend_wrle`)와 같은 규약이다. guard → renderer `0xE5BF18`·mirror 준비 확인 → 대상 검사(캐시·패널 버퍼 제외, stride·height) → 화면 교집합 클립 → 크기 ≤320×160 → 교집합 snapshot → 원본 7인자 그대로 1회 → `g1_overlay_blt_apply`. 게임 메모리 쓰기 없음. 설치는 상시(`!install_one(G1_BLEND_410, …)`)이고 restore 경로 포함, 준비 조건 `(!layer_drift_on() || g_hook_blend_6d0.installed) && g_hook_blend_410.installed`, 계수 6개 reset. `0x4676D0`은 진단 env일 때만 observe로 남는다. drift 기록 `why`가 진단 시 `mirrored`가 되도록 바뀐 것도 맞다.
- 버퍼 여유: `drift_hook_details[520]` 최악 출력 474 B, `mirror_details[10240]`에 대해 실제 metrics 꼬리 약 7.9 KB.
- **결함 없음.** 공개 한계: 화면 밖으로 나가는 사각형은 교집합만 미러하고 원본의 화면 밖 쓰기는 추적하지 않는다(이 장면은 전부 화면 안, `reject_bounds` 0). 비 Scale2x tiled 경로는 쓰지 않고 128×128이라 단일 apply로 충분하다.

## 3. 판정

- **H-D2k-s1 귀속 PASS·S-3 PASS(partial, 기술) 수용.** 사전등록 기준을 모두 충족한다. save000 2/2 마지막40 47,319 → 0(≤2,366), ord 145~221 0 유지, 새 reject·unsupported 급증 0, save006 2/2 PASS(stale 합 295·2 ≤307), 안전 0, p95 7~8 ms.
- 같은 회차 수리는 lap1096 §3 절차 정정을 따른 것이다(이탈 아님).
- v3 ord 350 단발 293 px는 UNKNOWN으로 남긴다. v4에서 재현되지 않았고, 그 장면의 `0x467410` 호출은 0이다. 사전등록 상한 307 안이다.
- save000 pair HOLD(input_effect HOLD·V2 계열 BLOCKED)는 fixture 한계다(`--fixture save000`은 `--scene-actions none` 강제). 제품 결함이 아니다.
- **현재 G1 기계 상태:** save006 full pair(실제 입력·미니맵·스크롤·V2/V2s/V2q·Scale2x)는 2/2 PASS다. save000·save006 고정 카메라와 스크롤 stale는 비진단 기준 run당 합 ≤4 px다(v3 ord 350 단발 293 UNKNOWN 1건 제외). 남은 것은 사용자 승인 경로(실제 시험판·표시 정책)와 backlog다.
- 제품 G1 마감·사용자 승인은 아니다.

## 4. 다음 work 사전등록(Sonnet) — H-UA0: G1 사용자 시험판 가능성·최소 구성

**근거:** DESIGN G1 합격은 같은 상태의 원본/후보를 실제 입력으로 보는 사용자 판단이다(§G1, PROMPT ⑥ 3단). 기계 쪽 남은 큰 stale는 없다. 하지만 사용자가 직접 켤 수 있는 후보 형태는 아직 정의되지 않았다. 스텁은 env 변수로만 켜진다. 하네스 candidate lane은 `SYW2_G1_NATIVE_2X_BLIT=1`·`SYW2_G1_MIRROR2X=1`·`SYW2_G1_HD_SOURCE=scale2x`에 더해 **항상** `SYW2_G1_PRESENT_TRACE=1`(+`TRACE_RUN_ID`)을 넣는다(`tools/g1_saved_scene_probe.py:3423`·`:3460`). DESIGN §G1은 "1080p 물리 모니터보다 높이 1200이 크므로 창/전체화면 표시 정책을 기록"도 요구한다. 이 회차는 가능성 판정 분기다(PROMPT ③: 한 work 회차 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`).

- **U-0 최소 env(정적+1 run):** 스텁 코드에서 mirror·native 2× 경로가 `SYW2_G1_PRESENT_TRACE` 없이 설치·동작하는지 확인한다(설치 경로가 trace 초기화에 묶였는지). 그다음 격리 run 1회를 돈다. save006 로드, env = 위 3개만(trace 없음), 하네스 대신 직접 기동이며 기존 하네스 기동 함수 재사용은 허용한다. 측정: 크래시 없음 60초, 출력 창 1600×1200, 로드 장면 캡처를 같은 장면 하네스 candidate `loaded.png`(lap1097 v3·v4)와 비교한 픽셀 일치율, trace 파일 미생성 여부.
  - **PASS:** 크래시 0, 1600×1200, 일치율 ≥ 99%(UI 동적 영역은 마스크하고 공개).
  - **trace 의존이면:** 최소 수정을 넣는다. 예: mirror 설치를 trace env에서 분리하거나 trace 출력을 null로 둔다. TDD로 하고 하네스 경로는 불변으로 둔다. 그 뒤 같은 run을 다시 돈다.
- **U-1 시험판 구성(스테이징만):** 공유 temp `20261007_lap1099_work_hua0/user_test_staging/`에 다음을 둔다.
  - 현재 트리 bridge 빌드 `_inmm.dll`(SHA 기록)
  - Windows 기동 `.bat`(최소 env + 원본 EXE 실행; 원본 EXE·게임 데이터는 넣지 않고 사용자 게임 폴더에 두는 방식)
  - 한국어 안내문: 설치·원복(DLL 원래 파일 백업/복원), 표시 정책 — 1600×1200이 1080p 화면보다 큼 → 창 모드/스케일 선택지와 그 한계를 사실대로, 알려진 한계(HD 그림 = Scale2x, P6 등 명시 잔여)
  - 원본 `_inmm.dll`이 사용자 폴더에 있으면 덮어쓰기 대신 백업을 안내한다.
  - `260921_temp` 배치는 root/사용자 몫이며 이 회차에서는 하지 않는다.
- **U-2 시험판 기동 검증(격리 1 run):** U-1 스테이징 파일만 격리 게임 사본에 복사하고 `.bat`과 같은 env로 기동한다(Wine에서는 동등 env 주입으로 대신하고 그 사실을 공개). 확인: 타이틀 → save006 로드 → 왼클릭 선택 1회·미니맵 클릭 1회의 입력 대응(후보 화면 좌표 ×2 위치에 반응), 60초 크래시 0, 종료 뒤 원복 절차로 원래 DLL 복원 SHA MATCH.
- **판정:** U-0·U-2 PASS면 `FEASIBLE` → 다음 middle이 독립 재조립·SHA 대조 뒤 APPROVALS에 G1 사용자 시험 요청을 올린다. trace 의존 수정이 범위를 넘거나(여러 모듈 재구성) 표시 정책 해결 수단이 없으면 `BLOCKED`/`NOT_FEASIBLE`로 근거·대안을 기록한다.
- **공통 FAIL:** 원본/참고 쓰기, 크래시, 안전 위반. source를 바꾸면 lint·typecheck 뒤 기록 freeze 후 `make check` 1회.

backlog(유지): v3 ord 350 단발 UNKNOWN, `0x4676D0` 미러 여부(호출 관측 0), 화면 밖 `0x467410` 쓰기 추적, `0x465FC0` 화면 대상 2회/run, H-UL, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역(a1·a2 ord 125..136·219/221 포함).

## 5. 검사

- focused(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_cache_fill`·`test_g1_screen_watch`·`test_g1_saved_scene_probe`·`test_g1_overlay_blt`·`test_g1_panel_layer`) `.venv/bin/python` **300 passed/13.04s**(exit 0), 로그 `logs/gates/lap1098-middle-focused.log` SHA256 `030503ae52cdb453…`.
- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS에만.
- 전체 `make check`는 SKIP한다. 이 회차는 문서만 바꿨다. source·하네스·테스트는 lap1097 full PASS 1692 때와 같다(해시 4/4 일치).

## 다음 한 가지

work(Sonnet): §4 H-UA0 — U-0 최소 env(trace 의존 확인·1 run) → U-1 시험판 스테이징 → U-2 기동 검증 → FEASIBLE/BLOCKED 판정.

# 2026-10-06 | lap1071 | G1 work — H-S3t save000 UP+10 tick 단발 stale 귀속·수리(`0x468870` 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 독립 승인 아님(middle 검수 대기).
- 가설 / 사용자 관찰: lap1070 §4 — save000 키 hold `DOWN,UP`의 UP+10 tick 단발 stale(윗줄 x702..704)은 미후킹(또는 reject된) 게임 writer가 화면 윗 가장자리에 그린 것이고, 표본을 그 위치에 두면 마지막 writer EIP로 귀속된다.
- 예상 PASS / FAIL 조건: lap1070 §4 T-0(위치)·T-1(표본 귀속)·T-2(조건부 수리: 비진단 2/2 hold 창 합 ≤10·UP+10 위치 0, save006 nd hold 합 1·pair PASS·ps3 stale 열 비회귀, 안전 0·cleanup·source_unchanged·마지막40 0). FAIL = 크래시·안전 위반·save006 비회귀 깨짐.
- 변경 파일 / source fingerprint / 커밋: uncommitted. `tools/inmm_stub/g1_mirror2x.c` `10c98ad9…`, `g1_mirror2x.h` `1dc289d2…`, `direct_draw_trace.c` `c0f0cffe…`, `tests/test_g1_rect_fill.py` `1bc85bbc…`. 하네스 `tools/g1_saved_scene_probe.py` 불변(lap1069 `8816512f…`).
- 원본 SHA / 후보 / 환경 / fixture: 원본 `[HQ]Syw2plus 2002.exe` `b56986e018b4…08a8ac`(읽기·objdump만, probe `source_unchanged` 7/7 true). 후보 = 작업 트리 bridge(probe가 run마다 빌드). 비합성 save000(loaded 카메라 (39,53)·tick ≈50595)·save006(nd). 활성 플레이어/지도/군대는 fixture 그대로(부하 증명 아님).

## 실행(공유 temp `20261006_lap1071_work_hs3t/`, 로그 `logs/gates/lap1071_t{0,1,2}_*`, 순차, game 사본 각 run 뒤 삭제)

옵션(save000): `--hd-source scale2x --fixture save000 --scene-actions none --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys DOWN,UP --stale-mask 220-240` (+진단 run은 `--layer-drift --screen-watch --drift-samples "703,0;702,0;704,0"`). save006 nd(g)는 lap1065 nd 옵션(`--p4b-s-snapshot --reference-completed-states <lap888> --stale-mask 129-143,227-230,308-322`).
pair-result SHA 접두: a `83441532` b `c741f116` c `8e5595f1` d `0c46953c` e `51fab299` f `24394b05` g `38d9b8f8` h `dbf05e3b`. 스크립트 `run_t0.sh` `e33e602d`·`run_t1.sh` `25b11e82`·`run_t2.sh` `87d7e817`·`run_t2b.sh` `d17fcc43`·`mask_t0.py` `ffa452c5`(work 분석용; middle은 새로 재계산할 것).

## 측정값 / 판정

- **T-0 PASS(위치 확보)**: a(비진단, 수리 전) hold 창 ps3 ord 228·tick 50820·카메라 (53,67)·**3 px = (702,0)(703,0)(704,0)** — lap1069 d1·d2와 같은 좌표·tick. b 0. 수리 전 정상 속도 save000 7 run(lap1069 s1·s2·d1·d2, lap1071 a·b·d) 중 (702..704,0) 3 px 재현 4(d1·d2·a·d), 0 2(s1·b), s2는 다른 모양 117 px.
- **T-1 PASS(귀속)**: d(진단, 수리 전)에서 ord 228 3 px 재현, 화면 watch p228 표본 3점 (703,0)/(702,0)/(704,0) 모두 마지막 writer = 게임 스레드 tid 280 EIP **`0x467CCF`**(`0x467B00` 내부, 이미 hook·"mirrored/clipped" 정상)인데 값은 그 앞 writer **EIP `0x468992`**가 쓴 값(71/88/90)과 같다 — `0x467B00`은 목적지 의존 혼합이라 이미 칠해진 값을 다시 칠했을 뿐. 스냅샷(`snap`)은 그 앞 단계(`0x466BE0` 미러 뒤) 값 59/64/83에 머물렀다. **즉 stale 원인 = `0x468992`의 쓰기를 미러하는 hook이 없었다.**
  - objdump(원본 읽기만): `0x468870` = `83 EC 14 | 8B 54 24 1C | 53 …` 7 B 명령 경계, thiscall 6인자(x·y·w·h·rle·lut, 32비트), 목적지 `[ecx+0x1514] + y·[ecx+0x10] + x`, 클립 `[ecx+0x4D0..0x4DC]`, `0xFE n` = n 칸 건너뜀·그 외 = `lut[dst]`를 `0x46898F mov [edx+eax],cl`로 제자리 쓰기(watch EIP `0x468992` = 다음 명령), 종료 `0x4689B7 ret 0x18`, **호출처는 `0x41A1F0` 한 곳**(`mov ecx,0xE5BF18` = `G1_RENDERER_VA`, 반환 `0x41A1F5` = watch stack과 일치). 저장소 어디에도 `468870` 언급 없음 = 미후킹 신규 함수(형제 `0x4687F0`는 비클립, `0x4689C0`은 비클립 좌우 반전).
  - drift `w` 기록(p228): `0x466BE0`·`0x467B00` clipped 사각형이 (702..704,0)을 덮음 — 그 둘은 hook됨. 위 3 px의 중간 writer가 `0x468870`.
- **T-2(수리) PASS(partial)**: 테스트 먼저 RED(`test_shade_clip_hook_table_and_wrapper_contract` 1 failed) → `mirror_shade_clip`(= `mirror_shade_flip` 이름 치환 복제: 32비트 사각형·`g1_flip_rle_region` 화면 교집합·before 버퍼·원본 정확히 1회·`layer_drift_write_end` `G1_SHADE_CLIP`) + `G1_SHADE_CLIP 0x00468870`/`LEN 7`/old bytes `83 EC 14 8B 54 24 1C` + install/restore/원복·installed 체크 + 계수 `shade_468870_*` 10개·accessor 10개·details 블록 GREEN(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt` 66 passed, `mirror_details` worst-case 합 테스트 통과).
  - 수리 후 save000 정상 속도 run **e·h hold 창(ps3 ord 124..292) 합 0·0**, UP+10 tick 위치 0, 마지막40 0, p95 55/53 ms(수리 전 a 52·b 54·d 56), 안전·cleanup(`game_removed`)·`source_unchanged` true. 계수(e): `shade_468870_invocations` 1035·mirrored 101·changed 18·clipped 8·reject_bounds 934(전부 화면 밖 호출)·reject_target/size/guard 0.
  - **f(수리 후) = 부하 변형**: present 간격 p50 68·p95 131 ms(정상 50/53)·ps3 204개(정상 298)이고 hold 창 합 15(ord 119 72·120 13·132 15 등 tick 50776..50793, UP+10 tick 50820 위치 아님). 수리 전 c(진단)도 같은 속도 저하(p50 67·p95 129·ps3 211)에서 tick 50765 stale 139 → **수리와 무관한 부하 동반 일시 stale**(lap1056 r1·backlog와 같은 유형), 원인 위치 미조사.
  - **h는 `terrain_scroll_parity` HOLD**: `complete_records_equal` false 하나뿐 — action 0 상태 비교에서 owner 0 `wood` 163471→163571(+100, 자원 수입 tick 위상 1칸 차이), 최종 비교는 빈 diff. hook은 화면 버퍼만 쓰므로 게임 상태를 바꿀 수 없다(수리 전 a·e는 동일 항목 PASS). lap1009 s1·lap1069 d2와 같은 **lane 입력/tick 위상 경합**으로 보고 backlog에 공개하며 판정에 쓰지 않음.
  - **save006 nd(g)** exit 0·pair PASS·input_effect PASS: hold 창 합 **1**(ord 125, lap1065 nd1·nd2·lap1069 nd1과 같은 위치·값), ps3 stale 열 17개(0..15 로드 과도 + 125)가 lap1069 nd1과 **값까지 완전히 동일**, 마지막40 0, p95 53, `shade_468870` 호출 50(전부 화면 밖 reject_bounds, mirrored 0).
  - save000 pair 자체는 기존 사유 HOLD 유지(V2/V2s/V2q BLOCKED = scene-actions none 태그 부재, input_effect HOLD = 장면 동작 없음; 이번 변경이 만든 사유 아님).
- 한계: 수리 전 재현이 정상 속도 7 run 중 4라 수리 후 정상 속도 run 2/2 = 0은 통계적으로 약하다(귀속 근거는 writer EIP·좌표·호출처 일치로 독립). lap1069 s2 117 px(위치 미수집)는 이번 어느 run에서도 재현되지 않아 **UNKNOWN 유지**. 진단 모드 동반 영역·`0x467E60`은 미조사.

## 다음 한 가지

middle(Opus)이 `loop/ESCALATE_SOL` 항목으로 독립 재계산·수용. 수용 시 다음 work: 좌우 가장자리·모서리 스크롤(H-D2e 하네스 `--terrain-scroll-edge` 확장), 또는 HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택. backlog: lane 입력/tick 위상 경합(d2 baseline 23칸·h wood +100), 부하 동반 stale(c·f·lap1056 r1), s2 117 px UNKNOWN, `0x467E60`, 진단 동반 영역, save000 overlay BltFast rejects, 다중 팝업 heal.

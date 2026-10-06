# 2026-10-07 | lap1079 | G1 H-LD (부하 동반 stale 재현·귀속)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 승인·수용 판정은 하지 않는다(독립 검수는 다음 middle).
- 가설: lap1078 §5 — present 간격이 늘면(게임 프레임 하나에 여러 sim tick) 카메라 정지 뒤 남는 world 영역을 미러가 놓친다. candidate 게임 프로세스만 SIGSTOP/SIGCONT 듀티로 느리게 하면 재현되고, 진단 표본으로 writer를 귀속할 수 있다.
- 예상 PASS / FAIL: lap1078 §5(LD-0 테스트 GREEN·기본 꺼짐 불변·PID 1개·정지 잔존 0 / LD-1 present p50 ≥60 ms 달성 + 정지 카메라 stale ≥100 px/present 2회 중 1회 이상 = REPRODUCED, 두 듀티 모두 0 = NOT_REPRODUCED / LD-2 표본 3/3 writer 귀속). 공통 안전 7종 0·cleanup·source_unchanged·다른 프로세스 신호 0. FAIL = 정지 프로세스 잔존·다른 PID 신호·크래시.
- 변경 파일 / source fingerprint / 커밋: uncommitted. `tools/g1_saved_scene_probe.py`(`--candidate-throttle STOP_MS:RUN_MS`, `_parse_candidate_throttle`·`_candidate_throttle_option_error`·`_ProcInfo`/`_read_proc_info`/`_read_proc_state`·`_throttle_target_error`·`_CandidateThrottle`, `_run_lane(candidate_throttle=)`) SHA256 `6c9a3bb1a395…`, `tests/test_g1_saved_scene_probe.py`(새 테스트 8) `67ddbf8695ec…`. 제품 C/bridge 불변(이번 lap 변경은 하네스만, `inmm_stub` 소스 해시는 lap1077 그대로).
- 원본 SHA / 환경 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac`(읽기만, 모든 run `source_unchanged` true·cleanup ok·game 사본 삭제). 비합성 save000(`--scene-actions none`)·save006(`--p4b-s-snapshot`). scale2x HD, load 2.7~4.6(≤8)·run마다 대기 0 s, 순차. 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1079_work_hld`(스크립트 `run_ld.sh` `e80e90ca3af2`·`analyze_ld.py` `6826b9743`·`analyze_ld2.py` `568ef13a2`·`mask_ld.py` `f3a7de492`), 로그 `logs/gates/lap1079_ld_ld{1,2,5..10}.{log,exit}`.

## LD-0 하네스 (테스트 먼저 RED→GREEN)

- RED: 새 테스트 8건 전부 실패(`_parse_candidate_throttle` 등 부재) → GREEN: `tests/test_g1_saved_scene_probe.py` 213 passed(기존 205 + 8, 기존 경로 불변).
- 구현: candidate lane의 `proc.pid`(= `wine <private exe>` 게임 프로세스)만 대상. `/proc/<pid>/exe`는 공유 wine 로더라서 "private 사본" 일치는 `/proc/<pid>/cwd == private game 디렉터리`와 `/proc/<pid>/maps`에 private EXE 경로 매핑으로 대신 검증(사전등록의 exe·cmdline 일치에서의 편차 — 로더 exe는 모든 lane이 같아 구분력이 없다). baseline·wineserver·pid 불일치는 거부(테스트). 시작 = 첫 스크롤 키 input tick 도달 직후, 끝 = 마지막 관측 뒤(`finally`에서도 `stop()`이 항상 SIGCONT·상태 `T` 아님 검증, idempotent, 종료한 프로세스 허용). pair-result `candidate.candidate_throttle`에 stop 횟수·누적 정지 ms·최종 상태 기록. 기본 꺼짐(`candidate_throttle=None`), baseline lane에 넘기면 `ProbeError`.

## LD-1 재현 (순차)

| run | fixture·옵션 | 듀티 | hold 창 present p50 (고정 p50) | tps | hold 창 stale 합 / ≥100 px present | 비고 |
|---|---|---|---|---|---|---|
| ld1 `7a504c92d52c` | save000 DOWN,UP 키 hold | 20:30 | **50** (50) | 20.04 | **0 / 0** | stop 167회·3,373.5 ms |
| ld2 `8491c034fb9e` | 동일 | 20:30 | 50 (50) | 20.06 | 0 / 0 | 동일 |
| ld5 `82cc05dbd141` | 동일 | **40:30** | **70** (50) | 19.92 | 0 / 0 | stop 120회·4,826 ms, 칸 17/17(baseline 24/24) |
| ld6 `e62ea65aa98f` | 동일 | 40:30 | 70 (50) | 19.90 | 0 / 0 | 17/17 |
| ld7 `a0be48b02e07` | save006 LEFT,RIGHT edge | 40:30 | 71 (50) | 19.90 | **10,001 / 13** | ord 123·171..182, max 974 px |
| ld8 `e054419d9083` | 동일 | 40:30 | 70 (50) | 19.90 | **10,258 / 14** | ord 123·140·171..182 |

- 20:30은 게임이 지연을 흡수해 present p50이 50 ms 그대로라 사전등록 전제(≥60 ms)를 못 채웠다(ld1·ld2 stale 0은 **전제 미달**이므로 NOT_REPRODUCED 근거로 쓰지 않는다). 사전등록의 40:30 단계에서 p50 70 ms·tps 19.9를 달성했다. ld3·ld4(20:30 save006)는 이 이유로 실행하지 않았다(러너 취소; 도중 ld2는 완주).
- **save006 LEFT,RIGHT edge 40:30 = REPRODUCED 2/2**(결정론: ld7·ld8 ord 171..182 값 일치 746·749·763·758·771·749·792·838·837·859·966·974). 정지 카메라 (141,118)에서 present당 746~974 px, 12 present 연속. save000 DOWN,UP은 두 듀티에서 0. lap1056 r1·lap1074 x1과 같은 계열(save006 + 정지 카메라 + 느린 present).
- 안전 7종 0(전 run)·cleanup ok·source_unchanged true·정지 잔존 0(전 run `final_state R`·`final_state_not_stopped` true)·다른 PID 신호 0(대상 PID = lane의 `proc.pid` 1개). pair HOLD는 기대된 lane parity 차이(candidate만 느려 칸 수 17 vs 24 → `terrain_scroll_parity` HOLD, save000은 기존대로 `input_effect_comparison` HOLD)이며 lap1078 §5대로 gate가 아닌 기록이다.

## LD-2 귀속 (ld9 마스크 → ld10 진단)

- ld9(`1ee801acdb3e`, ld7 옵션 + `--stale-mask 170-183`): ord 171..182 stale = 유닛 덩어리 하나(bbox 54×35, y29..63, x531..643, present당 약 4 px씩 오른쪽 이동), 170·183 0, trace 계수와 마스크 n 일치. 고빈도(12 중 10) 좌표 중 (583,52)·(588,55)·(590,41) 선택.
- ld10(`8007383d7539`, + `--layer-drift --screen-watch --drift-samples "583,52;588,55;590,41"`): 같은 재현(hold 합 9,274·ord 171..181). stale 표본×present **21개 전부 귀속(100%)**, 마지막 writer **EIP `0x00467F97`**(게임 스레드 tid 280, mod 0, guard 0, 스택 `0x0041AA04`←`0x004789DE`) 21/21, 마지막 writer val == 덤프 scr 21/21. 표본별 7/7/7.
- 디스어셈블(원본, 읽기): `0x467F93 mov [eax+esi-1],bl`(RLE 픽셀 한 점 기록) — 함수 **`0x467E60`**(앞 함수 `0x467B00`은 `0x467E57 ret 0x14`로 끝남; `0x467E60` = `83 EC 08 55 56`(sub esp,8; push ebp; push esi, 5 B 경계), `0x467FC6 ret 0x1c`(스택 7 인자), ecx = 화면 렌더러 `0xE5BF18`)의 몸통이다. 호출처 `0x41A9FF`(복귀 `0x41AA04`) — lap1078 backlog의 `0x41A887`과 다른 두 번째 호출처. `0x467E60`은 `G1_BLEND_*` 계열 hook 목록에 없어 **미후킹**이다(`g1_mirror2x.c` define 확인). 팔레트·LUT 기반 반투명 RLE(0xFE = 건너뛰기 코드)로, `0x467B00`의 형제다.
- 판정: **LD-2 PASS(귀속)** — 부하 동반 stale의 원인은 미후킹 `0x467E60`이 화면 버퍼에 직접 쓰는 유닛 스프라이트. 정상 속도 run에서 stale 0인 이유(같은 함수가 정상 속도에서는 호출되지 않거나 present 간격 안에 gdb 없이 덮이는지)는 **미조사 UNKNOWN**.

## 판정 / 한계

- LD-0 PASS, LD-1 **REPRODUCED**(save006 LEFT,RIGHT edge, 듀티 40:30, 2/2), LD-2 **PASS**(표본 21/21 → `0x467E60`). work 판정이며 수용은 middle이 한다.
- 한계: ① 재현은 candidate만 인위적으로 느리게 한 조건이다(사용자 환경의 실제 부하 동일성은 UNKNOWN). ② 정상 속도에서의 `0x467E60` 호출 여부 미측정. ③ 귀속은 표본 3점 한정(전 stale 면적 분포 미측정). ④ 20:30은 전제 미달이라 NOT_REPRODUCED 근거 아님. ⑤ save000 DOWN,UP·UP/DOWN은 이 듀티에서 stale 0(0건 재현 없음)이며 다른 fixture·방향 재현은 미측정. ⑥ 게임 8회 launch(ld1·2·5·6·7·8·9·10).

## 검사

- `make lint`·`make typecheck` PASS, 하네스 `tests/test_g1_saved_scene_probe.py` 213 passed. 기록·인계 freeze 뒤 `make check`·`checks/safety.sh check` 결과는 STATUS 검증 상태에만 보강한다.

## 다음 한 가지

middle(Opus) H-LD 독립 검수(`loop/ESCALATE_SOL` 항목). 수용 시 work H-L2: `0x467E60` hook(old bytes `83 EC 08 55 56`, ret 0x1c, 7 인자) diff 미러 + 테스트 먼저(C 전수 모델), 재현 옵션 = ld7(save006 LEFT,RIGHT edge 40:30)에서 hold 합 10,001 → 0 확인 + 정상 속도 비회귀.

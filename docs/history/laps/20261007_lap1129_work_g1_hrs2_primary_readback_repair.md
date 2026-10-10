# 2026-10-07 | lap1129 | G1 work — H-RS2 PS26 primary 역읽기 수리(R-PB) 구현·격리 실행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 입력: STATUS 다음 한 가지, lap1128 middle 사전등록 §4(H-RS2). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP`·기존 `loop/ESCALATE_SOL` 없음.
- 원본 SHA: 읽기만(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…`), 모든 run `source_unchanged` True, cleanup ok, game 사본 삭제(`local/runtime/lap1129_hrs2_*`에 `game` 0). 디스크 여유 137GiB.
- fixture: `g7defeat`(lap982 orig `save001.dat` `57872666…`, 타이틀 불러오기 → ps 3→27→29), 비회귀는 new-game 경로(합성 아님).
- 가설 H-RS2: PS26 배너 준비의 primary 역읽기를 "마지막 present 논리 800×600 프레임"으로 대체하면 PS27 HUD가 원본처럼 보이고 첫 PS27 present stale 92,383이 0이 된다.

## 변경 파일(모두 uncommitted)

- `tools/inmm_stub/g1_primary_readback.h`(신규 `b33a5ffb4942`): 순수 헬퍼 `g1_primary_readback_applies/rect/copy`(NULL rect = 논리 800×600, 논리 프레임 밖·빈·역전 rect·목적지에 안 맞는 크기는 거부해 원본 호출 유지, 패킹 행 복사). DirectDraw 타입 없음.
- `tools/inmm_stub/g1_mirror2x.c`(`e628b15c7767`): 매 present 소스 논리 800×600을 `g_last_frame`에 보관(행 복사, 바로 위 해시 계산 직후 `g_last_frame_valid`·`g_last_frame_source_hash`), 진입점 `g1_mirror2x_primary_readback`(호출 계수는 수리 끔에도 셈, 목적지 Lock→8bpp·크기 확인→복사→dest hash 기록), **호출 지점 훅** `mirror_primary_readback_site`(`call 0x469300` at `0x4C7EE6`, 바이트 `E8 15 14 FA FF` 확인, selector 1·source == `[0xE5D434]`(primary)일 때만 후면 버퍼(`renderer+0x1520`)에 복사 후 0 반환, 나머지는 원본 `0x469300` 호출). env `SYW2_G1_PRIMARY_READBACK=0`이면 끔(기본 켬). 버퍼 할당 실패는 기능만 끄고 훅 설치는 막지 않는다. detach·`primitives_installed`에 편입.
- `tools/inmm_stub/g1_mirror2x.h`(`b0112c54aaec`)·`direct_draw_trace.c`(`20058edeb748`)·`Makefile`(`13ec7c1e0ccd`): 카운터 6종(`primary_readback_calls/converted/rejects/dest_hash/source_hash/return_address`)을 모든 mirror present 행에 기록, 헤더 의존성 추가. 서피스 훅(`hook_blt`·`hook_blt_fast`)은 최종적으로 변경 0(아래 실패 가설 1회 참고).
- 테스트(RED→GREEN) `tests/test_g1_primary_readback.py`(`0ac4b560ce13`): 헬퍼 경계(역할·NULL rect·잘림·0·역전·목적지 부족·복사 범위·거부 시 무쓰기)와 C 배선(env 기본 켬, present 보관·무효화 순서, 호출 지점 훅·원본 폴백·colorkey 제외, 설치·복원, 카운터 보고) 5 passed. `make lint`·`make typecheck` PASS.

## 실패 가설 1회(공개)

- 1차 구현은 `hook_blt_fast`/`hook_blt`에서 `source`가 primary·목적지 비-primary를 가로챘다. 격리 3 run(`attempt1_{a,b,off}`) 결과 `primary_readback_calls` **0**, PS27 HD 80.754%·stale 92,383 그대로 → 서피스 훅은 이 호출을 보지 못한다.
- 원인(trace 확인): PS27 present 소스 `0x01E71780`(desc 1600×1200, caps 2076 = 시스템 메모리 BACKBUFFER|COMPLEX|FLIP)은 `create_surface`가 아닌 플립 체인 후면 버퍼라 서피스 vtable이 복제되지 않는다(PS3 후면 버퍼 `0x01E75328`은 caps 2112 offscreen). 그래서 `0x469300` sel 1 BltFast는 호출 지점에서만 가로챌 수 있다. 서피스 훅 분기는 추측이라 제거하고 호출 지점 훅으로 교체했다(lap1128 정적 해석은 호출 지점·인자까지 맞았고 훅 층위만 달랐다).

## 격리 실행(2차, 호출 지점 훅)

`PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1129_hrs2_<r> --artifact-root <공유 temp>/20261007_lap1129_work_hrs2/<r> --hd-source scale2x --fixture g7defeat --scene-actions none --result-screen`(a·b 켬, off = `SYW2_G1_PRIMARY_READBACK=0`; 스크립트 `run_rs2.sh`, 로그 `logs/gates/lap1129-hrs2-{a,b,off}.log`·`.exit` = 2 = 기준 미달 FAIL 판정, lap1125~1127과 같은 종료 코드). 비회귀 `--new-game-path --new-game-start --new-game-act --new-game-menu`(`run_ng.sh`, exit 0, PASS).

새 스크립트 재계산 `recalc_lap1129.py`(공유 temp `06713c8272d0`) → `recalc_lap1129.json`(`0a32e3c63b8a`):

| 항목 | a(켬) | b(켬) | off(끔) |
|---|---|---|---|
| readback calls / converted / rejects | 1 / 1 / 0 | 1 / 1 / 0 | 1 / 0 / 0 |
| 반환 주소 | `0x004C7EEB` | 동일 | 동일 |
| RB-a dest hash == readback source hash == 마지막 PS3 present 소스 해시 | `0xA0DFD3A9` 일치 | 일치 | 불일치(복사 0) |
| PS27 presents / 첫 stale / HD min | 1,095 / 0 / 100% | 1,116 / 0 / 100% | 1,148 / 92,383 / 80.754% |
| RB-b ≤8 일치(배너 상자 제외, 2× 짝수 표본) | 99.0968% | 99.0968% | 81.9865% |
| RB-b 하단(논리 y≥440) 비검정 vs baseline 72,277 | 72,188 (0.9988) | 72,188 | 36 (0.0005) |
| 후보 출력 y≥880 비검정 | 289,037 | 289,037 | 164 |
| PS27 경과 p95 | 6ms | 6ms | 6ms |
| PS9(확인 뒤) HD min | 100% | 100% | 100% |
| PS29 HD min(harness, 전환 present 제외) | 98.36% | 98.36% | 98.36% |

- 캡처 `a/candidate/ps27.png`(`19ce8ba99bfb`, b와 동일)를 직접 열람: 하단 HUD·미니맵·F1~F11 칸·손 커서·우측 로고·상단 자원이 baseline(`f8e0cd5e2bd5`)과 같은 구도로 보인다. off `ps27.png`(`c658e289fdc1`)는 lap1127 c27 결함 캡처와 해시 동일(HUD 소실, 자원 아이콘 4× 확대).
- 안전: V1 outside·clip/viewport/palette/identity 안전 7종 0·fallback 0·dropped 0·scale2x PASS(켬 2·끔 모두)·`mirror_validator` BLOCKED는 lap1127 c27과 같은 오류 집합(PS29 converted present 누락·nearest oracle 0.7759)이라 기존 상태이며 이번 변경과 무관.
- 비회귀 new-game(`ng/new-game-path-result.json` `5ad4d185e724`): status PASS, PS3 1,746 present min 100%, PS23 4,190 present min 99.936%(lap1123 99.939%와 0.003%p 차, 장면 시점 차로 추정, 판정 영향 없음), PS5 min 98.719·PS7 min 98.166(lap1108~1110 기존 값 범주), readback calls 0(PS26 없음, 기대대로).

## 판정

- **RB-a PASS**, **RB-b PASS**(≤8 일치 99.10% ≥99%, 하단 비검정 0.9988 ±3% 안; 커서 32×32 주변은 제외하지 않았고 제외하면 일치율이 더 높아질 뿐이다), **RB-c PASS**(PS27 min 100% ≥98.6, PS9 100%), **RB-d PASS**(안전·fallback·dropped 0, p95 증가 0ms, 캡처 열람 정상). 끔 run은 기존 결함(164·4분면 81.99%·80.754%)을 재현했다.
- **H-RS2 `PASS(partial, 기술·격리)`**: 사전등록 수리 의도(PS27 HUD 복원)는 달성했다. PS27은 더 이상 HD coverage 결함이 아니다.
- 공개 한계: 승리 화면 UNKNOWN(같은 `0x4C7D00` 호출 지점을 쓰므로 같은 수리가 적용될 것으로 예상, fixture 없음) · `0x41C7E5`(PS22) 역읽기는 호출 지점 훅 밖(장면 미확인, 서피스 vtable 호출이라 다른 방식 필요) · flip 분기 `0x4C7EC7` Blt는 `[0xE5D424]`=0 환경에서 실행되지 않는다(미실행, 코드 미추가) · PS29 막대(7,874 px, 최저 98.36%)는 이번 대상 아님(H-RS3 `0x468BB0` 미러 대기)이며 값 불변 · PS29 마지막(→PS9 전환) present stale 478,002(HD 0.416%) 1개는 lap1126 backlog와 동일 · 수리는 후면 버퍼 800×600 왼쪽 위에만 쓰므로 후면 버퍼의 나머지 영역(HD 해상도 표면의 우·하 영역) 내용은 원본 역읽기가 복사하던 HD 이미지가 아니게 바뀐다(PS27 present는 왼쪽 위 800×600만 읽어 가시 영향 없음).
- 미커밋 파일 보존. 커밋 0, 시험판 재스테이징 없음(lap1104 판본 유지; 수리 수용 뒤 재스테이징 여부는 middle이 정한다).

## 다음 한 가지

middle(Opus): H-RS2 독립 검수(source SHA 6개 재확인·`recalc_lap1129.py` 대신 별도 스크립트로 RB-a~d 재계산·캡처 열람·`primary_readback_*` 카운터와 호출 주소 `0x004C7EEB` 확인) → 수용 시 work H-RS3(PS29 `0x468BB0` 미러, 호출처 `0x4B5493` 1곳) 사전등록. 사전등록의 서피스 훅 가정 오류(플립 체인 후면 버퍼는 vtable 미복제)는 공개했다.

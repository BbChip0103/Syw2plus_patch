# 2026-10-02 | lap 863 | G1 W70 — P4 `<30%` 승격 판정: 귀속 유지, 스크롤 결손은 캐시 이동, P4b 캐시 층 카드 발행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향/master-plan) 역할,
  effort는 세션에 비노출. 자동 폴백 아님. `loop/.lap_counter`는 863을 읽기만 했다(러너 evidence 블록은 lap=862 표기,
  PROMPT 규칙대로 파일 값 사용). 게임 코드/하네스/validator/바이너리 수정0, 게임 실행0, subagent0, 커밋0.
- 가설 / 사용자 관찰: lap862 work는 스크롤 뒤 30 present coverage p50 21.60%/12.70%를 P4 카드 §5.1의 "귀속 반증"으로 읽고
  승격했다. 이 세션의 가설: (1) blitter 5종 귀속은 고정 카메라에서 이미 성립하고, (2) 스크롤 뒤 결손은 원본이 지형 캐시를
  hook 밖 복사로 밀기 때문이며, (3) DOWN lane 불일치는 gdb에 묶인 스크롤 하네스의 산물이다.
- 예상 PASS / FAIL 조건(이 판정의): (1) 같은 raw의 키 전 present에서 유효 coverage ≥55%면 귀속 유지, 아니면 반증 수용.
  (2) 보호 원본에서 카메라 이동 시 캐시를 옮기는 복사와 캐시→화면 복사가 따로 확인되고, raw에서 이동 뒤 blitter 호출 수가
  전체 재그리기보다 훨씬 적으면서 대량 stale이 나오면 "캐시 이동" 귀속, 아니면 다른 writer 후보를 work census로 넘김.
  (3) baseline lane에서 다른 키가 정상 스크롤이면 "baseline은 키 스크롤 불가"가 아니라 첫 키 전달 문제로 분류.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W70_P4B_TERRAIN_CACHE_LAYER_LAP863.md`
  (SHA256 `41d02e4c0d31d12d0bc77febbc935154577da1daf08e76611aa40618147e01ef`), 신규
  `analysis/memory_maps/g1_w70_p4b_terrain_cache_scroll_lap863.md`
  (`e76890d5ffcd43893f878eb000e6dc07c9ed05d029c37e6f1cf30f103ac5d012`), 이 기록, 신규 보존본
  `docs/history/20261002_lap863_prior_lap862_escalate_sol_archive.md`(lap862 `loop/ESCALATE_SOL` 31줄 그대로, SHA256
  `f2284cd480c7bf8ad8ca78898aaa2a4e898dae6ffc96875cae2634908efaf45d`), P4 카드 머리에 정정 포인터 2줄(카드 SHA
  `094e7eeb01d3188f1103b3a5a4fb5561456e5b32e1dd6e7b62087721c0f42e58`), lap862 기록 끝에 전사 오류 정정 1줄(기록 SHA
  `281320836d…04bc97b5` → `8ab1e86891062565a1e67a00c47b3918a883ef6ccaf11af1f806056712f3adaa`), `docs/STATUS.md`,
  `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL`은 보존본과 `cmp` 일치 확인 뒤 제거했다
  (판정으로 해소, 다음 회차를 work로 보내기 위함 — lap853·858 선례). uncommitted(`LOOP_ALLOW_COMMITS=0`).
  G1 source 불변(열람만, STATUS lap862 블록 값과 일치): `g1_mirror2x.c` `e5b3c195…ebacb5c44`, `.h` `e94ea2a1…f926320d`,
  `g1_hd_asset.c` `7bdbc4b3…aea5405602`, `.h` `76476ba6…a051678899`, `direct_draw_trace.c` `c5e4f2d4…bd0b5612b0`,
  `tools/g1_saved_scene_probe.py` `2616ed30…3b572f3f`, `tests/test_g1_saved_scene_probe.py` `73820787…bf84547b`,
  `tests/test_g1_mirror2x.py` `1272c3ac…4ee6856`, `tests/test_g1_hd_identity_probe.py` `baf67c58…f310c90d8a0b`,
  `g1_census.c` `0d8c9143…a8291f1f`.
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` 직접 재해시
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. save006 `616b7997…89a0d064`는 lap862 기록에서 읽음
  (이번 lap 재해시 없음). 새 runtime 없음. lap862 raw는 격리 Wine/Xvfb 1600×1200·save006(558 unit records, 활성 8인 부하
  증명 아님)에서 만들어진 것이다.
- 실행 명령 / 로그: 읽기·재계산만. `sha256sum`(pair 2개·candidate raw 2개·census raw·source 10개·lap862 기록·ESCALATE_SOL·
  원본 EXE), python json 집계(candidate `trace_raw.jsonl`의 PS3 `mirror2x_present` 1901/1899개, lane별 `probe-result.json`의
  `terrain_redraw`, gdb `writer-events.jsonl` 4개의 target·buffer·시각 cluster), `i686-w64-mingw32-objdump -d -Mintel`(보호
  원본; 출력은 `/tmp` 임시 파일, 종료 전 삭제), 참고 저장소 `ghidra_output/FUN_004324e0.c`·`FUN_0041bf20.c` 열람(읽기만).
- 측정값 / 판정:
  - 이전 바퀴 검수: pair SHA r3 `761ade1d…ae62d7860`·r4 `0fe8b64a…edef9cfb12f6f`, candidate raw r3 `70d6e94c…f460dbdb`·
    r4 `f16a78a2…6e53d0cc`, census raw `2d379f28…450e35b6`, source 3파일, 기록·ESCALATE SHA 모두 기록과 일치. gate exit
    r3/r4/census 0, 최종 Fast 로그 `1226 passed, 5 skipped in 775.57s`·exit0 확인. 30 present p50 재계산 103,669(21.60%) /
    60,971(12.70%) 일치. writer 호출 수 r4 최종 425/52/0/407/667 일치. census 맵 PS9 64/64는 기록 인용(맵 파일 재집계 안 함).
    전사 오류 2건(r3 전환 seq `1580`→raw `1565`, probe SHA 자리 누락)은 raw·재해시로 확인해 lap862 기록 끝에 정정했다.
  - 고정 카메라(키 전 6~7 present): `covered−stale` 328,298~338,716 = 68.4~70.6%(r3·r4 동일 범위). B-3 기준 264,000 초과.
  - 스크롤: r3 전환 present seq1565에서 terrain 호출 +128(16/9/32/71), stale 30,313; 다음 present seq1566에서 stale 210,468,
    유효 104,266. r4는 seq1583 +128·stale 30,979 → seq1584 +134·stale 240,644 → seq1585 stale 42,632·유효 61,286.
    `hd_mask_outside_diff_subpixels`는 PS3 전 구간 0. 이후 약 1,900 present 동안 r3 19~25%, r4 11~20%.
  - 정적: `0x4324E0`이 `0x464E00(0xBA3D30,832,512)`로 렌더러를 캐시에 묶고, 카메라 이동 경로에서 `call 0x4DB1D0` 8곳
    (`0x432A2D`·`0x432AB5`·`0x432B38`·`0x432BD4`·`0x432C7C`·`0x432D4E`·`0x432E1D`·`0x432ED2`)으로 캐시를 민다. DOWN=(+1,+1)은
    `memmove(0xBA3D30,0xBAA530,0x61800)`(32행 위로). `0x4DB1D0`은 겹침 방향을 가르는 memmove다. `0x41BF20`은 `0x41BF57`에서
    `0x466280(0,0,832,512,0xBA3D30)`로 캐시→surface 복사. `0x4245D0`은 `0x41C770`(캐시 갱신 호출 포함) 뒤 `[0xB93E00]==0`일
    때만 `0x41BF20`을 부른다. gdb `asset_blitter_call`은 4개 lane 전부 buffer `0xba3d30`(1061·969·1186·1040).
  - 입력: baseline DOWN r3 keydown→keyup 1ms·불변, r4 keyup만·불변. 같은 lane의 RIGHT는 r3 `[158,101]→[159,100]`,
    r4 204ms·`[161,98]`. candidate DOWN 127ms·`[159,102]` / 250ms·`[160,103]`. 스크롤 경로는 `terrain_trace`(gdb attach) 안에만
    있다(`tools/g1_saved_scene_probe.py` 755행 이하). gdb blitter cluster: baseline 709건 0.5초, candidate 837·971건 1.0~1.1초.
  - **판정: P4 `<30%`는 귀속 반증 아님 — P4 `FEASIBLE` 유지 / 스크롤 결손 writer = `0x4324E0`의 캐시 memmove 8곳 /
    수리 경로 = 캐시 층 미러(P4b: 층 평면 + 이동 미러 + `0x466280` 전사) / 화면 평면 직접 이동·전체 재그리기 강제는 기각 /
    DOWN lane 불일치는 하네스 귀속 유력(lane별 fallback은 결함 확정), gdb 없는 pair로 먼저 측정 / PS3 census는 P4b 선행
    조건 아님, PS3 한정 snapshot opt-in만 허용 / 기준·validator 불변 / G1 HOLD.**
- 회귀 / 남은 위험 / 독립 검수·사용자 승인: 이 판정은 기존 raw의 산술과 정적 판독이며 새 실행 증거가 아니다. 캐시 층 미러는
  실행된 적이 없다. 복사 지연의 정확한 phase 순서, 8개 외 카메라 변화 분기(`0x432F82` 이하), 캐시의 다른 writer는 읽지
  않았다. DOWN 불일치의 gdb 귀속은 가설이다(baseline RIGHT가 정상이라는 것만 확인). 층 전사로 고정 coverage가 지금보다
  내려갈 수 있다. 스크롤 중 성능·두 번째 장면·HUD/tinted/GDI·전체 HD coverage ≥90%는 미측정. 2단 middle 검수·3단 사용자
  승인 없음. G1 마일스톤 판정 아님. 제품 코드·실행 증거가 늘지 않은 회차 1회째(lap862는 실행 증거 있음).
- 다음 한 가지: work가 P4b 카드 §4·§5를 수행한다 — gdb 없는 스크롤 pair와 lane 동일 키 순서로 하네스를 고치고, 캐시 층
  미러를 구현해 B'(고정 + DOWN + RIGHT) 를 잰다(수리 ≤3회).

## 검증 (문서만 변경)

- 기록 후 G1 source SHA 불변 확인, `make lint`/`make typecheck`, `checks/context_limits.py`, `checks/safety.sh check`,
  scoped `git diff --check`, 최종 `make check` 1회 — 결과 수치는 STATUS에만 보강한다(PROMPT ⑥ fingerprint 규칙).

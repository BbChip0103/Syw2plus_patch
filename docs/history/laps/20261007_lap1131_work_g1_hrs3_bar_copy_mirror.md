# 2026-10-07 | lap1131 | G1 work — H-RS3 PS29 결과 표 막대 writer `0x468BB0` 호출 지점 미러 구현·격리 실행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 입력: STATUS 다음 한 가지, lap1130 middle 사전등록 §5(H-RS3). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기, 비차단), `loop/STOP`·기존 `loop/ESCALATE_SOL` 없음.
- 원본 SHA: 읽기만(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b4…` MATCH, objdump로 호출 지점 `0x4B5440..0x4B54A0` 재확인: ecx=`0xE5BF18`, push 순서 = 사전등록 디코드(dst `[0xE5D42C]`·dst_pitch `[0xE5BF28]`·src·src_pitch `[0x105C5B4]`·sx0 0·sy0 0·sx1 n−1·sy1 0x11·dx `[esi]`·dy `[esi+4]`)와 일치). 모든 run `game` 사본 삭제(`local/runtime/lap1131_hrs3_*`에 `game` 0), 디스크 여유 132GiB.
- fixture: `g7defeat`(lap982 orig `save001.dat` `57872666…`, 타이틀 불러오기 → ps 3→27→29, 탭 병사·건물·자원 클릭, 확인 → PS9), 비회귀는 new-game 경로(합성 아님).
- 가설 H-RS3: 원본 `0x468BB0` 호출 뒤 같은 사각형을 기존 block copy 경로로 HD 미러하면 PS29 막대 present당 stale +72가 0이 되고 PS29 HD min ≥98.6%가 된다.

## 변경 파일(모두 uncommitted)

- `tools/inmm_stub/g1_bar_copy.h`(신규 `ff12d6299246`): 순수 헬퍼 `g1_bar_copy_rect`(포함 사각형 폭 = `sx1−sx0+1`·높이 = `sy1−sy0+1`, 음수·역전·화면 800×600 밖 목적지 거부, 64비트로 계산해 오버플로 방지)·`g1_bar_copy_source_span`(마지막 행은 폭만큼만 읽기)·`g1_bar_copy_pack`(strided → packed). 게임 타입 없음.
- `tools/inmm_stub/g1_mirror2x.c`(`1213c4abb660`): 호출 지점 훅 `mirror_bar_copy_site`(`call 0x468BB0` at `0x4B5493`, 바이트 `E8 18 37 FB FF` 확인, thiscall·스택 10인자, **원본을 먼저 호출**한 뒤 renderer == `0xE5BF18`·dst == `renderer+0x1514`·dst_pitch == `renderer+0x10`·사각형 유효·source 읽기 가능일 때만 packed 임시 버퍼로 `transfer_block_copy_to_screen`(기존 block copy: Scale2x·expected snapshot·covered 갱신)). 거부는 `bar_copy_468bb0_rejects`로 센다. env `SYW2_G1_BAR_COPY=0`이면 원본만(기본 켬, 호출 수는 끔에도 센다). detach·`primitives_installed`에 편입.
- `tools/inmm_stub/g1_mirror2x.h`(`d3af97ed6adf`)·`direct_draw_trace.c`(`5ee7c6e90021`)·`Makefile`(`f6b0a382c75a`): 카운터 4종(`bar_copy_468bb0_calls/mirrored/rejects/pixels`)을 모든 mirror present 행에 기록, 헤더 의존성 추가.
- 테스트(RED→GREEN) `tests/test_g1_bar_copy.py`(`c26bd8d51192`): 헬퍼 경계(포함 사각형 폭·높이, 화면 가장자리 허용/한 칸 밖 거부, 음수·역전·NULL·오버플로 거부와 출력 불변, span 마지막 행, pack 행 일치·무쓰기)와 C 배선(상수·바이트·env 기본 켬, 원본 호출이 검증·미러보다 먼저, 설치·복원, 카운터 보고) 3 passed(RED 때 2 failed). `make lint`·`make typecheck` PASS, `make`(DLL 빌드) PASS.

## 실패 가설

없음(1차 구현으로 PASS). 사전등록 상한(실패 2회/60분) 미사용.

## 격리 실행

`PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1131_hrs3_<r> --artifact-root <공유 temp>/20261007_lap1131_work_hrs3/<r> --hd-source scale2x --fixture g7defeat --scene-actions none --result-screen`(a·b 켬, off = `SYW2_G1_BAR_COPY=0`; 스크립트 `run_rs3.sh` `4b025e447f36`, 로그 `logs/gates/lap1131-hrs3-{a,b,off}.log`·`.exit` = 0/0/**2**(끔은 PS29 98.36% 기준 미달로 FAIL 판정, lap1125~1129와 같은 코드)). 비회귀 `--new-game-path --new-game-start --new-game-act --new-game-menu`(exit 0, PASS).

새 스크립트 재계산 `recalc_lap1131.py`(공유 temp `0b18cbb7036e`) → `recalc_lap1131.json`(`7470e620f183`), 전부 후보 `trace_raw.jsonl` raw에서:

| 항목 | a(켬) | b(켬) | off(끔) |
|---|---|---|---|
| `0x468BB0` calls / mirrored / rejects | 2,646 / 2,646 / 0 | 2,682 / 2,682 / 0 | 2,692 / 0 / 0 |
| 미러 픽셀 합 | 4,439,232 | 4,511,808 | 0 |
| PS29 presents(마지막 전환 present 제외) | 1,120 | 1,135 | 1,136 |
| PS29 HD min(제외) / stale max(제외) | **100% / 0** | **100% / 0** | 98.3596% / 7,874 |
| PS29 stale 증가 이벤트(제외 구간) | 0 | 0 | 333 |
| PS29 첫 present stale | 0 | 0 | 72 |
| PS29 마지막(→PS9 전환) present stale | 478,002 | 478,002 | 478,002 |
| PS27 HD min | 100% | 100% | 100% |
| PS9 HD min | 100% | 100% | 100% |
| PS29 / PS9 / PS27 경과 p95 | 13 / 12 / 6ms | 13 / 12 / 6ms | 12 / 12 / 6ms |
| 안전(clip_replay·viewport mutation/restore·identity invalid·palette violation·fallback) present 수 | 0 | 0 | 0 |
| hresult≠0 / dropped | 0 / 0 | 0 / 0 | 0 / 0(`dropped_count` 0) |
| readback calls / converted(H-RS2 유지) | 1 / 1 | 1 / 1 | 1 / 1 |

- 비회귀 new-game(`ng/new-game-path-result.json`): PS3 1,747 present min 100%, PS23 4,284 min 99.936%(lap1129 99.936% 동일), PS5 98.719·PS7 98.166·PS9 100%, `0x468BB0` calls 0(해당 장면 없음), readback calls 0, fallback·hresult 0, 결과 `status` PASS.
- 캡처 열람: `a/candidate/result_tab_soldiers.png`(후보 1600×1200)와 `a/baseline/result_tab_soldiers.png`(800×600)를 직접 열었다 — 빨강·보라 막대(그라데이션)가 baseline과 같은 위치·길이이고 라벨·탭·확인 버튼·배경이 같은 구도다. 후보 2× 표본과 baseline의 채널 차 >8 픽셀 수는 켬/끔이 같아(예: ps29 10,017·병사 탭 10,084, 둘 다 가장자리 Scale2x vs 원본 차) 이번 수리가 가시 색을 바꾸지 않는다 = stale은 nearest 출력이라 색 오류가 없었다는 lap1126 판정과 일치.

## 판정

- **RS3-a PASS**(calls > 0, mirrored = calls − rejects, rejects 0), **RS3-b PASS**(PS29 HD min 100% ≥98.6, present당 stale 증가 0, 병사·건물·자원 탭 전환 뒤에도 stale max 0), **RS3-c PASS**(PS27 100%·PS9 100%), **RS3-d PASS**(안전·fallback·hresult·dropped 0, scale2x PASS, 경과 p95 증가 PS29 +1ms ≤2ms, 캡처 정상). 끔 run은 98.3596%·+72/present·최대 7,874를 재현했다. 비회귀 PASS.
- **H-RS3 `PASS(partial, 기술·격리)`**: PS29 막대 stale이 사라졌다. 결과 화면 PS27·PS29는 더 이상 HD coverage 결함이 아니다(fixture: 패배 화면).
- 공개 한계(수리 대상 아님): PS29→PS9 전환 마지막 present stale 478,002(HD 0.416%) 1개는 켬·끔 모두 그대로(lap1126 backlog, 전환 present의 writer 계수는 이번에도 보지 않았다) · 승리 화면 UNKNOWN(fixture 없음, 같은 `0x468BB0` 경로일 가능성 높음) · 막대 정체값 7,874 vs 면적 7,980 차 106(lap1126 backlog)은 끔 run에서 7,874 그대로 재현했을 뿐 새 해석 없음 · 부분 사각형(18행) Scale2x는 가장자리가 외곽 1픽셀 링에서 전체 프레임 Scale2x와 다를 수 있다(기존 block copy 의미 그대로) · `0x41C7E5`(PS22) 역읽기·flip 분기 미커버는 H-RS2 한계 유지.
- 원본 SHA 불변·game 사본 삭제·전부 uncommitted. 시험판 재스테이징 없음(lap1104 판본 유지, 묶음 판단은 middle).

## 다음 한 가지

middle(Opus): H-RS3 독립 검수(source SHA 6개 재확인·`recalc_lap1131.py` 대신 별도 스크립트로 RS3-a~d 재계산·캡처 열람·호출 바이트/규약 `ret 0x28` objdump 대조) → 수용 시 RS2+RS3(+보류 H-P35)를 한 판본으로 묶어 재스테이징할지 판단, 또는 남은 HD coverage(승리 화면·타이틀 인트로) 다음 가설 사전등록.

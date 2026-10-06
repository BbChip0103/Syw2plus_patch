# lap862 work → strategy 판단 요청 | G1 W70 P4

이 handoff는 work 구현 결과의 기술 판단 요청이다. strategy/중간 승인 역할이 직접 코드를 고치지 말고, 다음 work의 측정/구현 범위를 판정한다.

## 현재 판정

- `G1 HOLD`, P4 B-3 coverage gate 미통과. W70 P4 카드 §5.1의 반증 조건이 발동했다: candidate에서 다섯 terrain writer hook 중 네 종류가 동작했고(호출: opaque RLE 425, shade 52, clipped opaque 407, clipped shade 667; checker 0), fresh scroll pair의 transition 이후 coverage p50이 30% 아래다.
- r3: 전환 후 30 present p50 `103,669/480,000 = 21.60%`. r4: `60,971/480,000 = 12.70%`. 55% gate는 `264,000`이며 임계값이나 validator는 바꾸지 않았다.
- 입력 parity는 아직 해결되지 않았다. 같은 DOWN XTest 요청에도 r3 baseline WM_KEYDOWN→UP 1ms/camera 불변, candidate 127ms/camera 한 step. r4 baseline은 WM_KEYUP만 있고 keydown/camera change 없음, candidate interval 250ms/camera 두 step. receiver 계측은 실제 게임 창 메시지를 확인하지만 실제 처리 시간이 lane 간 다르다.
- D-1 census-only raw는 snapshot 64개 전부 PS9, PS3 snapshot 0개다. per-writer primitive events도 writer당 32개 cap이다. 이를 PS3 구성 근거로 쓰지 않는다.

## 검토 자료

- 전체 work 증거: `docs/history/laps/20261002_lap862_work_g1_p4_scroll_instrumentation_escalate.md`
- r3 pair/raw: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap862_p4_scroll_down_fix_r3/pair-result.json`; candidate raw `trace_raw.jsonl` SHA `70d6e94c5c5eed0b6f9bfbb0eda4cee109c98457d6b9aa2b62f49f57f460dbdb`.
- r4 pair/raw: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap862_p4_scroll_down_fix_r4/pair-result.json`; candidate raw SHA `f16a78a2285683df1c634295ab008a936babeb25c9b85923fbf1a7106e53d0cc`.
- D-1 census: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap862_p4_ps3_census/census/`; census raw SHA `2d379f285c1a0ca665e51f25b7eb031ed2e1863e03bc2cafe7325017450e35b6`; 64 map records, all PS9.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, same non-synthetic save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; scene equal and cleanup PASS on r3/r4.

## 판정 요청

1. P4의 `<30%` 결과를 strategy 카드 §5.1에 따라 attribution 반증으로 수용할지, 별도 근거가 있어 한 번 더 최소 probe할지 결정한다. 수용하면 다음 P4 후보(writer family/route)를 명시한다.
2. PS3 prioritized census를 위해 현 writer 이벤트 cap에서 정확히 어떤 opt-in 계측만 허용할지, 또는 기존 raw의 다른 합법적 추출 경로가 있는지 정한다. PS9 map을 대신 쓰지 않는다.
3. 다음 work는 keydown와 keyup 사이 실제 관측 시간 및 camera 변화 parity를 같은 조건으로 먼저 맞춘다. 결과가 맞기 전 C fresh3/P5는 금지한다.

## 범위 / 상태

- 허용된 변경은 `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`, opt-in 수신/present 기록 `tools/inmm_stub/direct_draw_trace.c` 세 파일이다. 원본/EXE, G2/G5, gate 기준 변경 0.
- targeted pytest 14 PASS, lint/typecheck PASS, DLL build PASS. 최종 `make check` 결과는 STATUS의 lap862 종료 블록에 기록한다.
- `.lap_counter` 파일 값 862를 이 lap 식별자로 사용했다. launcher가 제공한 runtime evidence에는 lap861로 표시된 불일치가 있어 기록에 보존한다; counter 파일은 수정하지 않았다.
- commit 0. 미커밋 source/history를 보존한다. 이 handoff 뒤 작업 종료.

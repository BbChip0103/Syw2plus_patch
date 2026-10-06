# lap764 work — G5 미니맵 우클릭 명령효과 paired

- 날짜/lap: 2026-09-29 / 764
- 목표: G5 사용자 항목 (2) 중 미니맵 우클릭 이동을 원본20/v10 50으로 실제 paired 측정
- 가설: lap763에서 확인한 라우터 게이트 `0x97597c`를 격리 프로세스에서만 1로 열면, LUT가
  베이크된 미니맵 픽셀 우클릭이 선택 전원에 월드 좌표 명령을 기록한다.
- 역할/범위: work tier. 제품 EXE·원본 폴더·참고 저장소는 쓰지 않았고, 진단 probe와 테스트만 변경.

## 변경 파일

- `tools/g5_minimap_click_hittest_probe.py`: v2로 확장. original/candidate 선택, v10 후보 copy-only
  설치, 명시 55기 fixture, 원본20/v10 50 드래그 선택, gate 진단 write, baked-center 단일 우클릭,
  `pending_xy`와 명령 필드 변화 판정을 추가했다.
- `tests/test_g5_minimap_click_hittest_probe.py`: `pending_xy` 전원 변화·불변 판정과 LUT 좌표 회귀
  3개를 추가했다.
- `docs/STATUS.md`: 130줄 이하로 압축하고 lap764 결과/다음 middle 검수 큐를 반영했다.

## provenance / 실행

- 보호 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- v10 후보 SHA: `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`
- 환경: 각 실행별 새 full game copy, 새 Wine prefix, 전용 Xvfb 1600x1200, `WINEDLLOVERRIDES=ddraw=b`.
  fixture는 owner0/type2 55기를 기존 `SupplyProbe op=5`로 생성했으며 장부·빈 플레이어를 성공으로
  세지 않았다.
- 원본 실행:
  `PYTHONPATH=. .venv/bin/python -m tools.g5_minimap_click_hittest_probe --variant original --force-gate-flag --runtime-root local/runtime/g5-lap764-minimap-original-r2 --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260929_lap764_minimap_original_r2`
- 후보 실행:
  `PYTHONPATH=. .venv/bin/python -m tools.g5_minimap_click_hittest_probe --variant candidate --force-gate-flag --runtime-root local/runtime/g5-lap764-minimap-candidate --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260929_lap764_minimap_candidate`
- 결과 JSON: 위 각 artifact root의 `probe-result.json`; 캡처/gdb events/manifest/log도 동일 공유 temp에 보존.

## 결과

| variant | 선택 | baked target | pending_xy 변화 | 명령 변화 | hit-test 성공 | 판정 |
|---|---:|---|---:|---:|---:|---|
| original | 20/20 | `(90,553)` center | 20/20 | 20/20 | 2967 | PASS |
| v10 | 50/50 | `(90,553)` center | 50/50 | 50/50 | 1441 | PASS |

두 실행 모두 gate 전 값 `0x0`, 격리 write 후 `0x1`, LUT non-`0xff` 16200/32400, crash 0,
`alive_at_end=true`, `cleanup.ok=true`, `source_unchanged=true`였다. 실행 후 정확한 `game/` 3개는
삭제하고 output/manifest/prefix/log/JSON은 남겼다.

## 보정과 한계

첫 probe는 여러 미니맵 클릭을 먼저 넣고 `pending_xy`만 비교해 원본 0/20으로 FAIL했다. 결과 JSON과
기존 command-coverage의 `rclick_center` 증거를 대조해 측정 순서 오염과 command-only 누락을 원인으로
확정했다. v2는 선택 직후 단일 baked-center 클릭을 측정하고 `pending_xy`/command를 함께 기록했으며,
원본 재실행과 v10 paired에서 전원 변화로 재현했다. 첫 실패는 완료 증거로 승격하지 않는다.

`0x97597c`는 정상 로비 UI 경로가 아니라 진단 write로 연 조건이다. 따라서 미니맵 입력 경로의
원본/v10 차이와 50기 명령 전달은 PASS지만, 정상 game_type 선택 UI의 사용자 접근성·멀티 동기화·
G5 전체 A~H 독립 검수·사용자 3단 승인은 미검증이다.

## Fast 검증

- `make doctor`: PASS; 원본 SHA verified, runtime tools/libraries present.
- `make check`: pre-change **1131 passed, 5 skipped** in 665.08s; after v2 probe/test changes **1134 passed, 5 skipped** in 692.61s. Pinned stock/ESL reference 부재로 5 skip.
- `.venv/bin/python -m compileall -q tools/g5_minimap_click_hittest_probe.py tests/test_g5_minimap_click_hittest_probe.py`: PASS
- `.venv/bin/python -m ruff check tools/g5_minimap_click_hittest_probe.py tests/test_g5_minimap_click_hittest_probe.py`: PASS
- `pytest -q tests/test_g5_minimap_click_hittest_probe.py`: **3 passed**
- 다음 행동: 새 middle(Sol/Opus5)이 v10 항목 (1)+(2)와 G5 A~H를 독립 재검수한다.

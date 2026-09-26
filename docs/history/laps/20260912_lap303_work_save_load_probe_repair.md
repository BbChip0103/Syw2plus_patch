# 2026-09-12 | lap 303 | G1/S1 save-load 정적 probe U1~U5 수행

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
- 목표: lap302 §12 handoff의 U1~U5를 새 파일에서 수행한다. 제품 G1 합격·실행 허가·Stage B·runtime
  예산 요청은 범위 밖이다.
- 가설 / 예상 PASS·FAIL 조건: `FUN_004644A0`의 `[this+4]/[this+8]`를 호출 사슬과 함께 열거하고,
  도달 가능한 5개 고정 해상도와 두 동적 직접 writer를 보고하며, 중심식을 주소 고정 `sar/sar/sub`로
  확인하고 새 lap/probe provenance를 보존하면 PASS. 하나라도 원본 SHA/명령이 어긋나면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260912_lap303_work_save_load_layout_probe.py`
    SHA `257c056352db9ef9aebb7752cc489e355c9028df6c89ab3e2f22a79e1de7ae35`.
  - `logs/lap303/save_load_layout_probe.json`
    SHA `5079de5a336d4feba7b7422cc0f2b9066b681c16385fb31b09f192a6b869d540`.
  - `docs/STATUS.md`와 본 history 추가. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 없음.
  - 원본 sprite `../Syw2plus/yfnt/saveloadtitle.spr`, SHA
    `7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5`, header `[9,320,310,1]`.
  - offline Linux `.venv` + `/usr/bin/objdump`; 활성 플레이어/지도/군대 없음; 게임/Wine/Xvfb/
    Stage B/runtime/PNG 실행 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - lap302 middle probe 사전 독립 검수 exit0; 원본·lap299·lap301 SHA 불변.
  - `.venv/bin/python docs/history/laps/probes/20260912_lap303_work_save_load_layout_probe.py`
    두 회 실행 exit0, 출력 바이트 동일(`5079de5a…869d540`).
  - `make check` → **292 passed**, Ruff/compileall/mypy/CONTEXT_PASS; `bash checks/safety.sh check`
    → **SAFETY_PASS**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - U1 **PASS**: 직접 4개 + `[this+0x4]/[this+0x8]` 간접 16개 = 최소 20 writer; 호출 사슬과
    absolute-only count 게이트의 간접 경로 fail-open을 report에 기록.
  - U2 **PASS**: 320×200/640×480/800×600/1024×768/1280×1024 및 post-map 640×480/map-surface
    동적 writer 후보를 전제와 함께 보고. `320x200` 슬롯은 화면 밖으로 그대로 보고.
  - U3 **PASS**: 주소 고정 중심식 `sar(screen,1)-sar(dialog,1)`과 5개 해상도 geometry 대조.
  - U4 **PASS**: report `lap=303`, 실제 새 probe 파일명, 기존 lap299/lap301 로그 미수정.
  - U5 **PASS**: 미래 산출물 SHA pin 없음; 같은 세션 두 fresh run 바이트 동일성으로만 결정성 확인.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 G1~G4 증거 0, 실제 입력/scene pair 0,
  어느 해상도가 구성 시점에 살아 있는지·hitbox·slot 선택·load 전이는 UNKNOWN. 다음 새 middle
  (Sol/Opus5/high)이 lap303 source/report를 독립 검수해야 하며 제품/출시 승인 없음.
- 다음 한 가지: 다음 새 middle이 lap303 U1~U5 산출물과 fresh deterministic report를 독립 검수한다.

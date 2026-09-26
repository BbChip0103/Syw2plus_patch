# 2026-09-12 | lap 282 | G1 유닛 레코드 오프셋 상수 승격의 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code claude-opus-5 / high /
  middle tier(진단·계획·확인). hands-on 게임 코드 수정 없음. 자기 승인 없음.
- 가설 / 사용자 관찰: lap281이 기록한 `internal_id=+0x29C`, `x=+0x2A2`, `y=+0x2A4`
  상수 승격과 memory-map 인용이 원본 바이트로부터 **독립 재도출**되면 ACCEPT,
  하나라도 재도출되지 않으면 반려한다. 사용자 신규 관찰 없음.
- 예상 PASS / FAIL 조건: (1) lap281이 기록한 파일 SHA 5개가 현재 파일과 일치,
  (2) 세 상수가 정확한 값으로 중앙 정의되고 driver가 이를 사용하며 매직 리터럴이 남지 않음,
  (3) 새 objdump에서 slot0 절대주소·읽기 폭·slot*0x758 스케일링·x/y 참조 수 동일성·
  부호 해석 근거가 전부 재현되면 PASS. 하나라도 불일치면 FAIL로 반려한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap282_middle_unit_offset_review_probe.py`
  `cdfa7c3c921cf4070150e2b6bc0361c8022700c463b24dc6c41900e7b42ae764`,
  신규 `logs/lap282/unit_offset_review_probe.json` `e0f07f3a4352c51959919fc0b5eb6bc1f907a09596ae3e5d5d8d8c5e46f4be08`,
  본 기록과 `docs/STATUS.md`, `loop/ESCALATE_SOL` 갱신.
  **lap281이 건드린 5개 파일은 의도적으로 수정하지 않았다**(단일 작성자 규칙 유지 +
  lap281 기록 fingerprint 보존). 커밋 없음(`LOOP_ALLOW_COMMITS=0`), 미커밋 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  읽기 전용 원본 `Syw2plus/syw2plus_original.exe` SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (검수 전후 재계산 동일). 후보 EXE/DLL 없음. Linux 정적 도구 + 저장소 `.venv`.
  활성 플레이어·지도·군대·fixture는 N/A. 게임/Wine/Xvfb/Stage B/원본 재실행 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `objdump -D -Mintel -j .text` 신규 실행(306218 instruction rows 파싱),
  `.venv/bin/python docs/history/laps/probes/20260912_lap282_middle_unit_offset_review_probe.py`
  → exit 0, `failures=[]`, `logs/lap282/unit_offset_review_probe.json`.
  `pytest -q tests/test_runtime_env.py -k unit_record_offsets` → 1 passed.
  `make check` → **292 passed in 44.57s**, Ruff all passed, compileall, mypy 10 files
  Success, `CONTEXT_PASS`; `checks/safety.sh check` → `SAFETY_PASS`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **ACCEPT-WITH-CORRECTION (정적 범위).**
  독립 재도출로 확인한 것:
  1. lap281 기록 파일 SHA 5/5 일치(변경 보존됨, 사후 수정 없음).
  2. `tools/runtime_env.py:184-186`에 세 상수가 정확한 값으로 정의되고
     `runtime_driver.py:25-27,102,106-107`이 이를 import·사용하며,
     `0x29C/0x2A2/0x2A4` 매직 리터럴이 driver에 남아 있지 않다.
  3. slot0 절대주소 재계산: `0x66BA2C` / `0x66BA32` / `0x66BA34`.
  4. 읽기 폭: `internal_id` 참조 **67개 전부 DWORD PTR**(비-DWORD 0개), x/y는 WORD.
  5. 스케일링: 세 accessor 모두 `lea/shl 4/sub/lea`로 slot*235를 만든 뒤
     `[reg*8+...]`로 읽는다 → 8*235 = 1880 = `0x758` = `G1_UNIT_STRIDE`. 재계산 일치.
  6. 참조 수 동일성: `0x66BA32` **115**, `0x66BA34` **115** (lap281 기록과 동일).
  7. 필드 경계 배타성(lap281 미확인, 이번 신규): 선언된 필드 내부 바이트
     `0x66BA2D/2E/2F`, `0x66BA33`, `0x66BA35` 참조가 **0개**다. 즉 4/2/2 바이트
     폭 해석을 쪼개는 접근이 원본에 없다.
  8. 부호 해석 근거(lap281 미기록, 이번 신규): x/y 각각 `movsx` 읽기 **41회**.
     driver의 `<h`(signed short) 디코드가 원본 사용과 일치한다.
  9. 인용된 대표 쌍 `0x4069C7/0x4069D1`, `0x40815D/0x40816B`가 실제로 x/y 쌍이다.
  **정정 1건:** `analysis/memory_maps/population_runtime_bridge_0910.md`가
  "adjacent accessors at `0x40F5D0` and `0x40F5F0`"라고 적었으나 그 두 주소는
  **함수 진입점이 아니라 읽기 명령 주소**다(call site 각각 **0개**). 실제 호출되는
  accessor 진입점은 `0x40F5C0`(caller 74)와 `0x40F5E0`(caller 79)이고, 읽기는
  각각 `0x40F5D0`/`0x40F5F0`에서 일어난다. 같은 문장의 `0x40F540`은 진입점이
  맞아(caller 74) 인용 기준이 필드마다 섞여 있다. 오프셋 값·폭·스케일링은
  이 정정에 영향받지 않으므로 lap281 판정은 뒤집지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 PASS(292). 이 검수는
  **정적 레코드 레이아웃 타당성**의 2단 판정일 뿐이며 런타임 값 정확성,
  두 run의 동일성, 제품 증거, Stage B 허가, 마일스톤 종료가 아니다.
  middle은 자기 결과를 승인하지 않는다. 남은 위험: driver의 `type=u[0x8D]`,
  `0x66B790`, `0x758`, `0x8990C8`은 `runtime_env.py`에 동일 값 상수가
  이미 있는데도 매직 리터럴로 남아 있다(lap281 선언 범위 밖, 드리프트 사각).
  S1 실제 결정성, WM_CLOSE, G2~G4, G3 저장 포맷 `0x1B5A4` 넘침은 그대로 미해결.
  제품·마일스톤 사용자 승인 없음.
- 다음 한 가지: 상위(Astra)가 runtime 쌍/Stage B 예산과 G3 저장 포맷 방향을 결정한다.
  work tier로 넘길 명시적 handoff 2건은 `loop/ESCALATE_SOL` lap=282 블록에 있다.

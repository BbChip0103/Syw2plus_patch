# 2026-09-12 | lap 313 | G1 — R2 D1~D4 수리

- 실제 provider/model/effort / 지정 역할: 지정 실무 hands-on work; static probe·회귀 테스트·기록만 수행.
- 가설 / 사용자 관찰: lap312가 찾은 D1/D2 주소순 `pre_gate`, D3 fail-open gate anchor, D4 dead constant를 새 probe에서 수리하면 원본 정적 R2 판정은 수치 변경 없이 유지된다.
- 예상 PASS / FAIL 조건: 원본 SHA 불변; `pre_gate`가 `entry→gate` CFG 지배 관계로 계산; gate bytes `75 0a`의 taken target이 `0x431AFE`; 실패 arm bytes가 eax=0 반환; `EXPECTED_RUNTIME_WRITERS` 제거; writer 집합과 CFG가 기존 수치와 일치.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 probe `docs/history/laps/probes/20260912_lap313_work_v5_mode_writer_order_probe.py` SHA `4d3a01a8fb050a05d1b6117e1559f843dd1bebf4abb7de645fe835ce1b066eef`.
  - 신규 테스트 `tests/test_lap313_mode_writer_probe.py` SHA `9ed8eec4a5fda4b6b924ab632acd379efe4a4965c8ac47898277439df858aae2`.
  - 생성 report `logs/lap313/lap313_v5_mode_writer_order.json` SHA `74976804fad29513d0d01df29b776ce05b2ff4b9d577d25fcb2552cc13ef9c3f`.
  - `docs/STATUS.md` 갱신. 커밋 없음(`LOOP_ALLOW_COMMITS=0`); lap311 산출물은 수정하지 않음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `Syw2plus/syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 실행 전후 불변. 후보 EXE·활성 플레이어·지도·군대 없음; Linux `.venv`, objdump disassembly, PE 원시 instruction bytes. synthetic CFG fixture는 회귀 테스트에만 사용.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python -m pytest -q tests/test_lap313_mode_writer_probe.py` → **4 passed**.
  - `.venv/bin/python docs/history/laps/probes/20260912_lap313_work_v5_mode_writer_order_probe.py > logs/lap313/lap313_v5_mode_writer_order.json` → exit 0, verdict PASS; fresh 2회 stdout `cmp` byte-identical.
  - `make check` → **307 passed**, Ruff/compileall/mypy/CONTEXT_PASS.
  - `bash checks/safety.sh check` → **SAFETY_PASS**. 캡처/PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **1단 정적 PASS.** `.text` 절대 참조 111건(load 107/store 4), 직접 screen writer `{0x431B79,0x431B7F,0x4324B8,0x4324C2}`, CFG `pre_gate=[]`, failure writer `[]`, success writer 4개, instruction window 753, failure arm 7개, unresolved branch 0. Gate `0x431AF2=75 0a`, taken `0x431AFE`, failure bytes `5f5e5d33c05b83c434c3`(eax=0). D1~D4는 수리됨.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: synthetic backward-jump test가 주소순 회귀를 막는다. 계산/간접 writer, callee·event/thread 순서, runtime 구성값, click/WM_CLOSE, 실제 scene/input, G1~G4 제품 증거는 UNKNOWN/0. 게임/Wine/Xvfb/Stage B/runtime/PNG/click 실행 금지. 다음 새 middle(Sol/Opus5/high)의 독립 검수와 사용자 마일스톤 승인이 남았으며 제품 승인 없음.
- 다음 한 가지: 다음 middle이 새 lap313 probe/test/report와 원본 SHA를 독립 검수한다. 그 전까지 기존 lap305~313 산출물과 원본을 보존하고 실행 범위를 넓히지 않는다.

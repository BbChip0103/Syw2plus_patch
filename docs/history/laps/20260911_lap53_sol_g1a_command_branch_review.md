# 2026-09-11 | lap 53 | 목표 G1-A command branch 독립 검수

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-sol`/high middle. 현재 세션
  표면은 실제 model ID/effort를 별도 노출하지 않아 실행 증거로 주장하지 않는다. 게임 코드·helper·
  tests·원본·좌표·timeout은 수정하지 않았고 Wine/Xvfb/game/runtime을 실행하지 않았다.
- 가설 / 사용자 관찰: lap52 helper가 원본 `0x0049B6D0` predicate뿐 아니라 selected slot/type도
  contiguous pool read 전후 재확인하여 한 selection의 coherent snapshot만 승인한다.
- 예상 PASS / FAIL 조건: 원본 SHA/call-site 산술과 helper hash가 일치하고 selection count/slot,
  active, unit type, 두 predicate가 pool 전후 같은 identity/value임을 검증하며 stable false와 changed
  fixture가 fail-closed하면 PASS다. identity를 한 번만 읽거나 changed selection을 승인하면 FAIL이다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 본 이력,
  `docs/STATUS.md`, `loop/ESCALATE_SOL`만 갱신했다. helper/test/guard SHA는 각각
  `4d342899a70da505886a9c563baa063a991128ece794c908d1a56a0e024861a6`,
  `3d52693a1c7891a2854dd48912edc622a6750896b45f61a647645493ec27df4b`,
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`; Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본
  `../Syw2plus_re/Syw2plus/syw2plus_original.exe` SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음. 기존 Python
  synthetic fixture와 call-count ad-hoc probe만 사용했다. 활성 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`; 고정 원본 `objdump -h`, `objdump -d
  -Mintel`, `xxd`; call-count Python probe; `.venv/bin/python -m pytest -q tests/test_runtime_env.py
  tests/test_runtime_guards.py`; `make doctor`; `make check`; `bash checks/safety.sh check`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 원본의 유일 call `0x004992DF→0x0049B6D0`, BYTE
  `[0x009B524C+type*0x394]&8`, DWORD `[0x0066B790+slot*0x758+0x94] == 0`, group10 별도 생성은
  재확인했다. type58/slot7 주소 `0x009C21D4`/`0x0066EB8C`도 일치한다. 그러나 helper call count는
  selected slot/type 각 **1**, 두 predicate 각 **2**이고 그대로 `PASS_WITH_SINGLE_READS`를 반환한다.
  lap51/52의 pool 전후 selection identity 계약과 충돌하므로 **INDEPENDENT CONFIRM FAIL**이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted **43 passed**, 전체 Fast **113 passed**,
  Ruff/compileall/mypy/context PASS, doctor `ok=true`/original verified, safety `SAFETY_PASS`. 기존 테스트는
  changed selection/type을 포함하지 않아 exit0이 결함을 반박하지 않는다. live predicate/group2..5,
  G1 실제 출력/입력과 사용자 승인은 UNKNOWN/SKIP. patch/version/restore는 후보가 없어 SKIP다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 selection count/slot, active, unit type과 두
  predicate를 pool 전후 독립 snapshot으로 읽고 identity/value 변화 시 raw pool과 before/after evidence를
  보존해 reject하도록 helper/tests만 최소 수정한다. targeted/Fast/safety 뒤 새 Sol/high가 재검수한다.

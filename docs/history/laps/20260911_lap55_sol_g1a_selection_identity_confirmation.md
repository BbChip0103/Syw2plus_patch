# 2026-09-11 | lap 55 | 목표 G1-A selection identity coherence 독립 검수

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier Codex `gpt-5.6-sol`/high review.
  현재 세션 표면은 실제 model ID/effort를 별도 노출하지 않아 실행 증거로 주장하지 않는다. 게임 코드,
  helper/tests, 원본, 좌표, timeout은 수정하지 않았고 Wine/Xvfb/game/runtime을 실행하지 않았다.
- 가설 / 사용자 관찰: lap54 helper가 selection count/slot, active, unit type과 두 `0x0049B6D0`
  predicate를 한 contiguous pool read 전후 독립적으로 다시 읽어 같은 selection snapshot만 승인한다.
- 예상 PASS / FAIL 조건: 여섯 필드가 stable eligible 경로에서 각각 2회 읽히고, 각 필드 단독 변화가
  raw pool과 before/after evidence를 보존하며 fail-closed하고, stable-ineligible은 재시도 없이 즉시
  FAIL해야 PASS다. 원본 SHA/call-site 또는 검사와 충돌하면 승격하고 새 runtime은 금지한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 본 이력과
  `docs/STATUS.md`만 갱신하고 처리 완료된 `loop/ESCALATE_SOL` marker를 제거했다. helper/test/guard SHA는
  각각 `c43b20ccbd7bad3da4fa2d704bb36e73388ed9b2cb50709d8cc96f0aa321b2d4`,
  `6a38c6b8b304edc31e23c71c65b8f8c3dc8b5042a97f93397ce671cea0d4bb4f`,
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`; Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 원본
  `../Syw2plus_re/Syw2plus/syw2plus_original.exe` SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음. 기존 Python
  synthetic fixture와 독립 call-count/field-change probe만 사용했다. 활성 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`; 원본 `objdump -h`, `objdump -d -Mintel`,
  `xxd`; stable read-count 및 여섯 field-change one-off probe; `.venv/bin/python -m pytest -q
  tests/test_runtime_env.py tests/test_runtime_guards.py`; `make doctor`; `make check`;
  `bash checks/safety.sh check`. 새 로그/PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 원본 raw `0x992BE`에서 BYTE
  `[0x009B524C+unit_type*0x394]&8`, DWORD `[0x0066B790+slot*0x758+0x94] == 0`, 유일 call
  `0x004992DF→0x0049B6D0`과 entry raw `0x9B6D0`을 재확인했다. stable path의 count/slot/active/type/
  type-predicate/unit-predicate read count는 각각 **2**. 각 단독 변화 **6/6**은 selection/predicate change로
  reject되고 raw group `[2,3,4,5]`와 before/after를 보존했다. stable-ineligible은 pool 1회 후 즉시
  FAIL했다. lap54 수리는 **INDEPENDENT CONFIRM PASS**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted **44 passed**, 전체 Fast **114 passed**,
  Ruff/compileall/mypy/context PASS, doctor `ok=true`/original verified, safety `SAFETY_PASS`. current runtime
  manifest absent. 이는 synthetic helper contract 확인이며 live predicate/group2..5, production/drag/minimap,
  G1 실제 2배 출력과 사용자 승인은 UNKNOWN/SKIP이다. patch/version/restore는 후보가 없어 SKIP다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 current helper SHA를 대조하고 새 private copy/prefix/
  빈 display에서 `g1-baseline --screen 1600x1200x24 --timeout 90`을 정확히 1회 실행한다. 좌표/timeout/
  helper/binary를 바꾸거나 재시도하지 않는다. 성공이면 stable eligible group2..5/strict hit를, 실패면
  exact selection identity/predicate/raw pool과 cleanup을 보존하고 `loop/ESCALATE_SOL`로 넘긴다.

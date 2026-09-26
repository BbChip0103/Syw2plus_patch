# 2026-09-11 | lap 151 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  중간 tier(진단·계획·확인). hands-on 구현 없음.
- 가설 / 사용자 관찰: lap150 `prepare` RC2는 `runtime_env.prepare`의 source-root **계약 결함**이
  아니라 **호출 입력 오류**다. 커밋된 계약은 이미 중첩 게임 디렉터리를 가리킨다.
- 예상 PASS / FAIL 조건:
  - PASS(계약 무결): `DEFAULT_SOURCE`가 게임 설치 디렉터리이고, 과거 성공한 `prepare`가 모두 같은
    경로를 썼으며, 저장소 어느 문서도 `--source .../Syw2plus_re`를 지시하지 않는다 → 코드 변경 불필요.
  - FAIL(계약 결함): 저장소가 repo-root를 source로 지시하거나 `DEFAULT_SOURCE`가 repo-root면
    `validate_original_source`의 의미를 work tier가 고쳐야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 코드 변경 없음. 문서만 변경 —
  `docs/STATUS.md`, `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`(부록 추가),
  `docs/history/laps/20260911_lap151_middle_g1_source_root_contract_confirmation.md`(신규),
  `docs/history/laps/20260911_lap150_escalate_sol_original.md`(신규 archive),
  `loop/ESCALATE_SOL`(해소 후 제거). 전부 uncommitted (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (`tools/runtime_env.py:159 ORIGINAL_SHA256`). **이 세션은 작업 디렉터리 밖 파일의 해시를 계산할
  권한이 없어 원본 EXE SHA를 직접 재계산하지 못했다(SKIP).** 대신 `validate_original_source`가
  `prepare` 시점에 이 pin을 강제함을 정적으로 확인했다. 후보/실행/플레이어/지도/군대/fixture 없음.
  lap150 변경 4개 파일의 SHA는 재계산 결과 escalation 기록과 **완전 일치**했다:
  `tools/runtime_env.py` `69d0c54d…0296`, `tools/check_g1_presentation_trace.py` `22003230…8188`,
  `tests/test_runtime_env.py` `4206eee7…e128b`, `tests/test_g1_presentation_trace.py` `86f32f63…27bf9`.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum tools/runtime_env.py tools/check_g1_presentation_trace.py tests/test_runtime_env.py
  tests/test_g1_presentation_trace.py` (RC0, 4/4 일치);
  `ls -la /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/` 및 `.../Syw2plus_re/Syw2plus/`
  (읽기 전용); 저장소 grep(`Syw2plus_re`, `--source`, `_protected_roots`).
  `make check` / `checks/safety.sh check` / `.venv/bin/python`은 **세션 실행 권한 거부로 SKIP**
  (lap149와 같은 제약). 게임 실행·캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **계약 무결 = PASS.** 근거 4가지:
  1. `tools/runtime_env.py:155` `DEFAULT_SOURCE = REPO_ROOT.parent/"Syw2plus_re"/"Syw2plus"` —
     커밋된 기본값이 이미 중첩 게임 디렉터리다. `:2810`의 `--source` 기본값도 동일하고
     `patches/population/runtime_driver.py:118`도 같은 경로를 쓴다.
  2. `validate_original_source`(`:310-325`)의 계약은 "source root가 `syw2plus_original.exe`를
     **직접** 포함하는 게임 설치 디렉터리"다. repo root는 정의상 이 계약의 입력이 아니다.
  3. 과거 `prepare` 성공 lap은 전부 중첩 경로를 썼다: lap73, lap113, lap115, lap136.
     repo-root 문자열은 lap148·lap150 기록에만 나타난다.
  4. 저장소의 어떤 문서/Makefile/스크립트도 `--source .../Syw2plus_re`를 지시하지 않는다.
  안전 재검토: 승인 경로는 `_protected_roots()`(`REPO_ROOT/Syw2plus`,
  `REPO_ROOT.parent/Syw2plus`)와 같지도, 그 하위도 아니다(부모가 `Syw2plus_re`). 실 디렉터리이며
  symlink가 아니고, `syw2plus_original.exe`는 일반 파일이다. `local/runtime`과 상호 포함도 없다.
  → **승인된 source 입력: `--source`를 생략해 커밋된 `DEFAULT_SOURCE`를 쓴다**
  (= `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus`).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 오류 전파 경로를 찾았다. lap148 기록은 `prepare --source .../Syw2plus_re`로 적혀 있으면서도
    runtime 성공을 보고한다. 둘 중 하나는 사실이 아니다(lap148 runtime은 커밋되지 않은 inline
    스크립트였다). 이 부정확한 명령 문자열이 lap150에 그대로 복사된 것이 RC2의 실제 원인이다.
    **기록된 명령을 재현 근거로 쓰기 전에 커밋된 코드와 대조해야 한다**는 교훈을 남긴다.
  - 잔여 위험: `prepare`는 `_reject_links(source)`로 source 트리 전체를 걸어 symlink를 거부한다.
    이 세션은 작업 디렉터리 밖 `find`가 거부되어 하위 트리 symlink 유무를 확인하지 못했다(SKIP).
    work tier가 실행 전 `find <source> -type l`이 비었는지 먼저 확인해야 한다(알려진 RC2 원인).
  - lap150의 Fast 수치(179 PASS)는 이번에 재실행하지 못했다. 다만 그 tree의 파일 SHA 4개가
    byte-identical임을 확인했으므로 증거가 같은 bytes에 고정돼 있다. 이를 재실행으로 승격하지 않는다.
  - 사용자 마일스톤 승인: 없음. G1 미완료 판정 유지.
- uncommitted 문서 SHA (커밋 없음, `LOOP_ALLOW_COMMITS=0`):
  `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`
  `eb156c504c933196ef77b3498abe3c7da6df8388d230134537ec878ba371c491`;
  `docs/history/laps/20260911_lap150_escalate_sol_original.md`
  `50d1bc94cce4c5cf2fd4b4868eea93d01cb0db51fab101f7db68b5dd2d0c7fc1`.
  `docs/STATUS.md`와 이 lap 파일은 본 줄 추가로 다시 바뀌므로 해시를 고정하지 않는다.
- 다음 한 가지: work tier가 승인된 source로 fresh helper/bridge·private copy/prefix/display를
  새로 만들고 `g1-presentation-trace`를 **정확히 1회** 실행한다. 상세는
  `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md`의 lap151 부록.

# 2026-09-18 | lap 382 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, 실무(work) 역할.
  `docs/MODEL_ROUTING.md` 2026-09-18 오버라이드에 따라 중간계획/컨펌은 별도 Opus5/high 세션이
  맡고, 이 세션은 게임 구현만 수행했다.
- 가설 / 사용자 관찰: lap381 handoff(`docs/work/active/G2_STORAGE_LAYOUT_SONNET_HANDOFF_LAP381.md`)
  가 이미 닫힌 사실(C1: count는 WORD·겹침없음, H1: 8×200 WORD matrix shape)을 넘겨줬으므로,
  이번 lap은 재조사 없이 그 사실 위에서 `patches/population/base_preserving_storage_layout_v1.py`
  + 테스트만 새로 만들면 제품코드 산출로 streak를 리셋할 수 있다는 가설.
- 예상 PASS / FAIL 조건: (a) `layout(1200)`이 계획 §1 표와 바이트단위로 일치하고
  `map_va(v,1200)==v`가 모든 경계·±1에서 성립 (b) N∈{4001,9601,9904}에서 6영역/외래블록
  겹침없음·단조·32bit overflow없음·정렬불변식·외래블록 크기/순서불변 (c) SHA불일치 원본 거부,
  원본 파일 무변경 (d) `.rsrc` 이동과 9개 payload RVA/resource directory/SizeOfImage 일관 재기술,
  그 외 바이트는 원본과 동일 (e) `make check`/`safety.sh check` PASS 유지. 하나라도 FAIL이면
  구현을 되돌리고 blocker로 기록한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `patches/population/base_preserving_storage_layout_v1.py` (신규)
    SHA256 `278a00135f9a0b9e7dc2774d9fb0a4d0b16033ca96f678ea84fed32af6ba3a65`
  - `patches/population/test_base_preserving_storage_layout_v1.py` (신규)
    SHA256 `7d0cfb40677985568f27799155bfb6c66b6dc1cb4154ade375cacf89f03a365f`
  - `docs/STATUS.md` (갱신, 150→112줄로 압축; 압축 전 원문은
    `docs/history/laps/20260918_status_lap382_compaction.md`에 SHA `60a0d91d…d74659d5`로 보존)
  - `patches/population/offline_storage_v1.py`: **무수정**(frozen, import도 하지 않음).
  - uncommitted. `LOOP_ALLOW_COMMITS`는 기본0이며 이번 lap에서 사용자 명시 허용을 받지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `Syw2plus/syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    — 빌드 전/후 재확인, 무변경.
  - "후보 EXE"는 이번 카드의 범위 밖이다(§6 STOP). `build_layout_artifact()`가 만드는 것은
    실행 대상이 아닌 **PE-layout 산출물**(SizeOfImage/`.data` VirtualSize/`.rsrc` VA/9개 payload
    RVA만 갱신, 그 외 바이트는 원본과 동일)이며 테스트 안에서 `tmp_path`(pytest 임시디렉토리,
    격리)에만 `.pelayout` 확장자로 쓴다. 게임 실행/Wine/Xvfb 없음, 활성 플레이어/지도/군대
    fixture 없음(순수 바이트/헤더 계산이라 런타임 fixture가 필요 없다).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 -m pytest patches/population/test_base_preserving_storage_layout_v1.py -q` → 45 passed
  - `python3 -m pytest patches/population/ -q` → 90 passed (기존 45 + 신규 45, 회귀 없음)
  - `.venv/bin/python -m ruff check patches/population/base_preserving_storage_layout_v1.py
    patches/population/test_base_preserving_storage_layout_v1.py` → All checks passed
  - `make check` → `test`: **678 passed in 190.16s**; `lint`: ruff All checks passed +
    compileall 통과; `typecheck`: mypy 10파일 "Success: no issues found"; `checks/context_limits.py`
    → `CONTEXT_PASS`
  - `bash checks/safety.sh check` → `SAFETY_PASS`
  - 캡처 없음(이 카드는 화면/게임 실행을 만들지 않는다).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - N=1200 identity: **PASS** (`layout(1200)` 6영역 모두 old==new, `size_of_image==0xC8F000`;
    `build_layout_artifact(원본,1200)` 바이트가 원본과 **완전히 동일**함을 직접 diff로 확인).
  - N=4001/9601/9904 확장 회귀(겹침/단조/overflow/정렬/외래블록 불변): **PASS** (45건 테스트
    parametrize).
  - PE 기하 재기술 범위 검증(`test_build_layout_artifact_only_changes_documented_fields`):
    **PASS** — SizeOfImage, resource data directory rva, `.data` VirtualSize, `.rsrc`
    VirtualAddress, 9개 payload `OffsetToData` 필드 이외의 바이트가 하나도 바뀌지 않음을
    변경된 바이트 집합의 부분집합 관계로 직접 확인(N=4001 실측: `.rsrc` 새 RVA `0x119c000`,
    9개 payload 전부 delta `0x510000`, 사전 계산값과 정확히 일치).
  - launcher-before-Popen 거부: **PASS**(구조적) — `tools/runtime_env.py`의 `ORIGINAL_SHA256`
    pin이 이 모듈의 pin과 동일함을 확인하고, 확장 artifact의 SHA256이 그 pin과 다름을 확인했다.
    이 저장소의 모든 실제 launch 경로(`check_runtime`, `prepare`의 post-copy 해시 등)가 Popen
    이전에 이 pin을 비교해 실패를 raise하므로, 구조적으로 거부됨을 보였다. 실제 Wine/launcher
    프로세스를 띄워 재현하지는 않았다(게임 실행은 범위 밖).
  - Fast 게이트: **PASS**(`make check` rc0 678 passed, ruff/compileall/mypy10/CONTEXT_PASS,
    `SAFETY_PASS`). 실제 앱/24k/멀티 증거 아님(Fast일 뿐).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀 없음: 기존 633건 + 신규 45건 = 678건 전부 PASS, `offline_storage_v1.py`와 그 45건
    회귀도 그대로 PASS.
  - 남은 위험: (1) H1 매트릭스(`0x89A388` 8×200 WORD)의 **의미는 여전히 UNKNOWN**이므로 이
    모듈은 그 블록을 의미와 무관하게 "크기불변 foreign"으로만 다룬다 — 만약 실제 코드가 이
    블록의 절대 주소를 code operand로 하드코딩해 참조한다면(현재 미조사) 이 카드의 layout은
    맞지만 향후 code-fixup 카드가 별도로 그 참조를 찾아 고쳐야 한다. (2) `.data`의 새
    VirtualSize가 원본의 alignment slack(0x5C8)을 보존하는 방식으로 계산되는데, 이 slack
    구간 자체의 의미도 UNKNOWN이다(단순 linker 패딩으로 추정, 확증 아님). (3) 이 카드는
    code operand fixup을 전혀 하지 않으므로 산출물은 게임을 실행할 수 없다 — 이는 의도된
    범위 제한이며 결함이 아니다.
  - 독립 검수: **대기**. 다음 중간 lap(Opus5 또는 Sol/high)이 위 항목을 재확인해야 하며,
    이 기록의 "실제 provider/model" 자기 서명은 검수를 대체하지 않는다.
  - 사용자 마일스톤 승인: 없음, 요청하지 않음(APPROVALS.md 갱신 없음). 이 카드 완료는 G2
    제품 완료나 런타임 승인이 아니다(§6).
- 다음 한 가지: 다음 중간 lap이 STATUS.md "다음 한 가지"에 적힌 §4 검수 항목을 독립적으로
  재현하고 ACCEPT/REJECT를 판정한다. ACCEPT 시 Astra/Sol이 다음 실무 범위(예: 접근코드
  인벤토리 작성, 즉 어떤 명령이 여섯 영역의 절대주소를 operand로 갖는지 전수 조사)를 지정한다.

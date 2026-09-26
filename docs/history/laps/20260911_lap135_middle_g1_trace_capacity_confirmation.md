# 2026-09-11 | lap 135 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high / 중간 계획·독립 컨펌.
- 가설 / 사용자 관찰: lap134 Luna 구현의 fixed-array aggregate가 256개 상세 경계 이후 호출을
  stable key별로 손실 없이 합산하고, 용량 고갈·malformed key를 fail-closed한다는 기록은 새 중간
  세션에서 source/test SHA·산술·PE32 build를 재현하면 2단 기술 컨펌할 수 있다.
- 예상 PASS / FAIL 조건: 세 SHA 일치, key가 method/object/interface/original/present/state를 포함,
  summary total=`detailed+aggregated+dropped`, 256 경계 PASS, duplicate key·65 records BLOCKED,
  targeted/Fast/doctor/safety/fresh out-of-tree PE32 build PASS. 불일치나 필수 검사 실패는 FAIL 및 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임 코드 변경 없음. 문서만
  `docs/STATUS.md`, 본 기록을 갱신했다. source SHA는 `tools/inmm_stub/direct_draw_trace.c`
  `412315b1f5c1199d97a63d9bdee3a580fb12bed95cc6bcccb336c67466c4a121`,
  `tools/check_g1_presentation_trace.py` `a58a8aa13bd3affb25aaf7355ef5bf803c6fea0efb1320a6c27557f308ef4c1a`,
  `tests/test_g1_presentation_trace.py` `5d68f12e4d1ed071d27c5418d18519419f6e43af1ca1732bc5791537a36ec13d`;
  lap134 기록과 모두 일치. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` doctor verified. 제품
  EXE/DLL/assets 미변경. fresh build는 `/tmp/syw2plus_lap135_pe32.kkDnyn/_inmm.dll`, SHA256
  `2688994d771bd392041802cd8fc3c2927ce77a51ef4f6ec35dae5922964d114b`, `file` PE32 DLL/Intel 80386.
  테스트는 synthetic 256+aggregate/state transition/duplicate/65-record fixture; 플레이어·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; `.venv/bin/python -m pytest -q
  tests/test_g1_presentation_trace.py tests/test_direct_draw_abi.py`; `make check`; repository 밖 복사본에서
  `make clean all`, `file`, `sha256sum`, `i686-w64-mingw32-objdump -p`; `bash checks/safety.sh check`.
  historical lap128 trace는 SHA `b105fc3452dc1650aab58cd7c66aa79e97656964a121ab18d80713f6469d8539`,
  617행/PID 204/thread 208 단일로 대조했으나 현재 runtime 성공으로 승격하지 않았다. 새 PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 세 SHA PASS; source key와 validator key 일치 PASS;
  method summary 산술 대조 PASS; targeted **14 passed**; `make check` **169 passed** 및
  Ruff/compileall/mypy/context PASS; fresh PE32 build PASS; doctor original SHA/no-side-effect PASS;
  safety `SAFETY_PASS`. 판정 **MIDDLE CONFIRM PASS**. 게임 runtime/PNG/G1 제품 판정은 SKIP/미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: build는 기존 범위의 unused-parameter,
  FARPROC cast, stdcall-fixup warning을 출력했지만 PE32 생성과 필수 검사는 성공했다. C aggregate 경로의
  실제 실행, overflow 없는 final summary, owned WM_CLOSE→process exit→DLL detach, 1600×1200 출력·입력은
  미검증이다. 사용자 마일스톤 승인 없음.
- 다음 한 가지: 새 Luna/high work tier가 격리된 전체 게임 복사본·fresh Wine prefix·unused display에서
  한 번 runtime을 실행해 owned close, process exit/DLL detach, exactly-one final summary,
  aggregate dropped=0/overflow 없음, raw byte-exact 보존과 validator PASS를 같은 run으로 남긴다.

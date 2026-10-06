# 2026-09-29 | lap756 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high, 실무(work) 역할.
- 가설 / 사용자 관찰: 2026-09-29 00:59 사용자 판단(AskUserQuestion)이 G5 v9 milestone을 보류하고
  항목 (1)을 요구: 부대 미지정 드래그 50기 선택이 저장/로드 후 50기 전부 복원되어야 하며, 원본
  세이브 형식과 양방향 호환을 유지해야 한다(원본 EXE가 v10 세이브를 열어도 크래시 없이 앞 20기,
  v10이 원본 세이브를 열어도 정상). 정적 디스어셈블(`0x00440F0C`/`0x004412DC` 레거시 미러 호출부가
  각 저장/로드 루프의 **마지막** block-transfer 호출이 아님을 확인 — 각각 하나씩 더 있고
  (`0x00440F1E`/`0x004412EE`), 그 뒤로는 `fclose` 등가 호출과 return뿐)로 가설을 세움:
  `STREAM_SAVE_FN`/`STREAM_LOAD_FN`(`0x004DA39F`/`0x004DA4A9`)은 원본 CRT `fwrite`/`fread` 그 자체이므로
  `fread`의 표준 short-read(EOF에 예외 없이 짧은 count 반환) 동작을 이용해, 그 마지막 호출 뒤에
  magic+전체 50슬롯 배열을 추가로 쓰고/읽으면 파일 끝에 트레일러를 붙이는 것과 같아 이전
  빌드(원본/v1~v9)는 그 바이트를 아예 시도조차 하지 않고, v10은 magic 부재 시 기존 v7~v9 동작으로
  안전하게 폴백한다는 설계. 예상: FEASIBLE, 같은 lap에서 최소 구현+런타임 paired 측정까지.
- 예상 PASS / FAIL 조건: (a) v10 자체 save→load: count/entries 50개 전부 복원. (b) 원본 EXE가 v10
  세이브를 열어도 크래시 없음+레거시 20기 정상 복원. (c) v10이 원본(비-v10) 세이브를 열어도 크래시
  없음+기존 v7~v9와 동일한 앞 20기 복원(21~50 zero). 셋 다 PASS해야 항목 (1) 충족.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `patches/selection/g5_selection_cap50_v10.py`(신규), `patches/selection/test_g5_selection_cap50_v10.py`(신규,
  9 tests), `tools/g5_stale_tail_probe.py`(CANDIDATE_MODULES/CANDIDATE_SHAS에 v10 추가),
  `tools/g5_v10_foreign_save_load_probe.py`(신규, cross-build 로드 전용 probe). **uncommitted**
  (`LOOP_ALLOW_COMMITS=0` 기본, 사용자 명시 허용 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전 실행 후 재확인, 불변).
  v10 후보 `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`
  (v9 `18181cdef6c7…` + 2개 hook만 추가, `test_only_the_hook_sites_cave_and_section_header_differ_from_v9`로
  diff 범위 고정). 격리 Wine9.0/Xvfb 1600x1200, 단일플레이 solo, dense worker fixture 55기(seed type2).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1) `python3 tools/g5_stale_tail_probe.py --variant candidate --candidate-version v10
     --runtime-root local/runtime/20260929_lap756b_v10_full_restore_candidate
     --artifact-root .../temp/Syw2plus_patch/g5_lap756/v10_candidate_b` (48s, exit 0).
     결과 저장 `save001.dat` sha256 `ecef059463cb0e662621f6a122b2f43f9968966b08779ddb483c8d857131b0df`
     (temp에 `v10_candidate_b_save001.dat`로 보존).
  2) `python3 tools/g5_stale_tail_probe.py --variant original --candidate-version v10
     --runtime-root local/runtime/20260929_lap756d_original_selfsave
     --artifact-root .../temp/Syw2plus_patch/g5_lap756/original_selfsave` (48s, exit 0) — 원본 자체
     save 생성용. `save001.dat` sha256 `6675a35e23272f398710b586bdb7454ab8b2bbc151a27b1cd98cbc6635d28f2b`
     (temp에 `original_selfsave_save001.dat`로 보존).
  3) `python3 tools/g5_v10_foreign_save_load_probe.py --variant original
     --runtime-root local/runtime/20260929_lap756c_original_loads_v10_save
     --artifact-root .../temp/Syw2plus_patch/g5_lap756/original_loads_v10_save
     --seed-save .../v10_candidate_b_save001.dat` (33s, exit 0) — (b) 검증.
  4) `python3 tools/g5_v10_foreign_save_load_probe.py --variant candidate
     --runtime-root local/runtime/20260929_lap756e_v10_loads_original_save
     --artifact-root .../temp/Syw2plus_patch/g5_lap756/v10_loads_original_save
     --seed-save .../original_selfsave_save001.dat` (33s, exit 0) — (c) 검증.
  전부 `game` 복사본은 실행 종료 직후 삭제(디스크 위생), `prefix`/`output`/`probe.log`/캡처는 보존.
  최초 시도(이 lap의 v10 build v1, magic scratch를 `.rsrc` 내부에 둔 잘못된 초판)는 로드 시
  `0x0108F244`(scratch 주소) write access violation으로 **크래시**했다(`.rsrc`는 R+X이나 W가 아님을
  실측으로 발견) — `v1.STORAGE_END`(레거시 relocated-storage gap, R+W `.data` 안, 이미 쓰이는
  `SELECTION_BASE`/`CONTROL_GROUP_BASE`와 같은 섹션)로 scratch 위치를 옮겨 수정, 재현 0/2로 해소.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  (a) **PASS**: `selection_after_drag` count=50/nonzero=50 → `selection_after_load_no_deselect`
  count=50/nonzero=50, 50개 슬롯 전부(`legit_slots_after_load`) 일치, `commanded_outside_legit_selection`=[]
  (경로밖 오발행 없음), `legacy_after_load`(0x899024) 앞 20기 정상 유지(레거시 호환 회귀 없음),
  전체 `status=PASS_NO_STALE_TAIL_EFFECT`, 크래시 0.
  (b) **PASS**: 원본 EXE가 v10 세이브를 로드 → `crashed=False`, `legacy_after_load` count=20/nonzero=20,
  슬롯이 저장 시점 앞 20기와 일치. `status=FOREIGN_LOAD_PASS`.
  (c) **PASS**: v10이 원본(비-v10) 세이브를 로드 → `crashed=False`, `legacy_after_load`/`live_after_load`
  둘 다 count=20, `live_after_load`의 21~50번째 엔트리 전부 0(magic 부재 → 기존 v7~v9 폴백 그대로,
  회귀 없음). `status=FOREIGN_LOAD_PASS`.
  `make check` 1131 passed·5 skipped(714.79s, +9 신규 v10 pytest), ruff/mypy(0 issue)/`CONTEXT_PASS`,
  `checks/safety.sh check` → `SAFETY_PASS`. 4회 실행 전부 `source_unchanged=true`·`cleanup.ok=true`
  (고아 프로세스 0).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  제품 코드 변경은 v9 대비 hook 2곳(`0x00440F1E`/`0x004412EE`)+cave뿐(`test_only_the_hook_sites_*`로
  범위 고정), G5 체크리스트 A~H의 기존 판정(F 포함)에 영향 주는 다른 바이트 변경 없음 — 다만 (F)는
  이제 "앞 20기만 복원"이 아니라 "50기 전부 복원"으로 능력이 바뀌었으므로 middle이 A~H 표를 v10
  기준으로 다시 훑어야 한다(특히 F와, count>20 경계를 보는 다른 항목들과의 상호작용). 남은 위험:
  ① sidecar가 "매직 일치 후 배열 read가 도중에 잘리는" 극단적으로 드문 경우(세이브 중 크래시)는
  존재 클램프(`count<=50`)만 있고 별도 검증 없음(모듈 docstring `known_limit`에 명시). ② 이번
  runtime probe는 count=50(가득 찬 드래그)만 측정했고, 20<count<50 중간값·부대(Ctrl+숫자) 저장/로드
  조합은 미측정. ③ 아직 middle 독립 재검수 없음 — 이 lap은 work tier 정보제공이다.
  **다음 middle이 반드시 재확인해야 할 것**: v10 재빌드 SHA 일치, hook 2곳이 정말 "마지막
  block-transfer 호출"인지 원본 디스어셈블 재확인, `STORAGE_END` 위치가 다른 목적으로 쓰이지
  않는지 재확인.
- 다음 한 가지: 사용자 지시(2026-09-29 00:59) 순서대로, (1)의 middle 독립 재검수 전에 **(2) 미니맵
  우클릭 이동·특수능력 v의 원본20/후보50 paired 확인**(격리 환경 미니맵 렌더/입력 조건 조사)을 이어서
  진행하거나, middle이 먼저 (1)을 재검수한 뒤 (2)로 넘어간다 — 순서는 middle/사용자 판단.

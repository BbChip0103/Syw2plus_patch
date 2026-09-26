# lap356 middle — lap355 S1 direct-reader wiring 독립 검수

2026-09-12 / Codex 현재 세션 / 정확한 모델 ID 미주장 / high / middle(진단·계획·확인).
게임 코드·하네스 hands-on 수정과 게임/Wine/Xvfb/입력/PNG 실행은 0이다. 범위는
lap354 F1~F4 수리의 독립 판정이며 Stage B·제품·마일스톤 승인이 아니다.
runtime 주석은 lap355였지만 `loop/.lap_counter=356`이므로 PROMPT 계약대로 lap356을 사용했고 카운터 쓰기는 0이다.

## 0. 판정

**ACCEPT — lap354 F1~F4 repair scope only.** 현행 production wrapper는 private
`runtime_driver.read`를 쓰는 `--pid` 경로를 갖고, group/selected/PS WORD와 PlayerStruct
8×6을 pre/post에서 직접 읽는다. in-process collector token, pre/post 변화, PS35→PS3,
고정 fixture 8개 raw 일치가 모두 있어야 `PASS/LOAD_RESTORED_PLAYER_STRUCTS`가 된다.
외부 JSON에 복사한 `ps=3/open_succeeded=true/raw_hex`는
`UNKNOWN/UNTRUSTED_READER_EVIDENCE`이므로 lap354의 네 반려 사유는 해소됐다.

이 ACCEPT는 실제 load 완료 증거가 아니다. production `--pid` 경로는 현재 pre snapshot과
post snapshot을 **아무 load event나 wait 없이 즉시 연속 호출**한다. 따라서 실제 실행에서
`pre→load→post` 인과 경계를 만들지 못하며, 성공하더라도 그 실행의 load 증거로 승격할 수 없다.
이를 N15로 남기고 다음 work tier가 실행 없이 순서·exact-once·timeout 회귀를 먼저 잠근다.

## 1. 독립 근거

- lap355 기록의 세 현행 SHA를 재계산해 모두 일치했다:
  `runtime_env.py=77aaf0de…a38b`, `s1_load_evidence.py=157778e6…0924`,
  test=`91bc9059…c30e`. lap355 기록 자체 SHA는 `542cc461…6c72`다.
- 보호 원본은 1,032,192 bytes / `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  save000은 3,093,902 bytes / `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`다.
- `runtime_env.py:3359..3377`은 두 `read_s1_snapshot`과
  `read_post_player_structs`를 production branch에서 직접 호출한다. CLI는 manifest를
  `check_runtime`으로 검사하고 PID가 private prefix 소유 목록에 있을 때만
  `patches.population.runtime_driver.read`를 결선한다(`5310..5328`).
- `s1_load_evidence.py:160..185`는 각 snapshot마다 WORD 3곳과 계산된 PlayerStruct
  8곳/6B를 읽고 주소·폭을 남긴다. `311..446`은 token·phase·live input·PS35→3·
  8-record shape/provenance·pre/post 변화·fixture raw 일치를 fail-closed로 검사한다.
- lap354 독립 probe `b08d0c7b…07a4`를 수정 없이 fresh 실행해 rc0,
  `failures=[]`, F1~F4 전부 true를 재현했다. 대상 회귀도 fresh `15 passed`였다.
- `make doctor` rc0에서 보호 원본 verified, `make check` rc0에서 393 passed(63.86s),
  Ruff/compileall/mypy/`CONTEXT_PASS`; `checks/safety.sh check`는 `SAFETY_PASS`였다.
  optional runtime manifest 부재는 실제 runtime 검증을 하지 않았다는 상태와 일치하며 PASS 근거가 아니다.
- 기계/정적 검수는 **PASS**, 실제 runtime/load·입력·캡처는 **SKIP(0회)**, 제품 판정은 **UNKNOWN**이다.

## 2. N15와 Luna/high work handoff

한 바퀴에서 다음 하나만 구현한다. 실제 게임 실행 예산은 0회다.

1. accepted reader/evaluator와 offline `--post-json` 분리를 보존한다. live S1 경로에
   `pre snapshot → load trigger exactly once → bounded PS3 wait → post snapshot` 순서를 갖는
   event-boundary adapter를 둔다. 기존 승인된 private runtime/input helper와 좌표 provenance를
   재사용하고, 새 주소·hook·memory write를 만들지 않는다.
2. trigger 전 pre가 PS35인지 직접 확인하고, trigger는 정확히 한 번만 호출한다. wait는 지정된
   단일 deadline 안에서 PS WORD를 읽어 PS3 도달을 확인하며 자동 재클릭·예산 연장을 금지한다.
   PS3 뒤에만 group/selected/8×6 post snapshot을 읽어 evaluator로 넘긴다.
3. 합성 회귀가 호출 순서를 기록해 immediate `pre→post`가 제품 경로가 아님을 보이고,
   trigger 0/2회, PS3 timeout, 부분/read 오류가 PASS가 아닌지 검사한다. 외부 JSON·pre==post·
   fixture mismatch 회귀와 새 파일만 쓰는 artifact 정책을 보존한다.
4. targeted → lap354 F1~F4 → `make check` → safety를 fresh 실행한다. 실제 fixture 선택,
   좌표, run 수와 timeout 값을 바꾸거나 발효하지 않는다.

금지: 게임/Wine/Xvfb/클릭/PNG, EXE/DLL/save/fixture/pin/baseline/golden 변경, 과거 probe
재pin, Stage B/P6/WM_CLOSE/G2~G4 확대, 새 의존성, 커밋. work 결과는 다음 새 middle이
독립 검수하며, 실제 실행 봉투는 기존 lap349 Astra 권한으로 남긴다.

## 3. 미검증

실제 private load/open 성공, load 전후 PlayerStruct 변화, 두 run 결정성, S1 (A)+(B),
F2-R2, fresh 원본/후보 pair, WM_CLOSE, Stage B와 제품 G1~G4는 모두 UNKNOWN이다.
프로세스 exit 0과 393 passed는 이 항목들을 승인하지 않는다.

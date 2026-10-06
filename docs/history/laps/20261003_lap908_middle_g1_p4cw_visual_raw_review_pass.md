# 2026-10-03 | lap 908 | G1 W70 P4c-W 독립 raw·화면 검수

- 실제 provider/model/effort / 지정 역할: Codex native/API 새 세션, 지정 중간 tier(진단·계획·확인). 모델 ID/effort 메타데이터는 이 surface에 노출되지 않아 실제 Sol/high 호출을 주장하지 않는다. 이전 work 세션과 대화/검산은 독립이며 게임 hands-on 수정0·subagent0.
- 목표 / 가설: lap907 W1(clear와 compose가 같은 프레임 폭)·W2 GCC 경계 테스트 및 V2q 추가가 실제 fresh B′2 pair·C3 pair의 격자/우측 검은 쐐기를 제거했고 기존 gate를 유지했는지 확인한다.
- 예상 PASS/FAIL: lap900/903/906 카드 §6 그대로. current-source build 일치, V1 전 present 위반0, V2/V2s/V2q 모든 25tag≤2000, B′ E1~E4·scroll coverage·C ratio≥0.95/p95Δ≤16ms/coverage≥264000·last≥first×0.9, V3 원본/후보 직접 확인. 모호한 실제 근거충돌 또는 마일스톤이면 ESCALATE; P단계 이동 자체는 카드의 명시대로 마일스톤 아님.
- 변경파일 / 원본·후보SHA / source fingerprint / commit: 이 lap은 STATUS·INBOX·APPROVALS·이 기록·D-1 handoff만 변경한다. 게임·probe·tests·validator·기준 수정0, commit0(uncommitted). 원본 EXE의 실제 값은 아래 고정 SHA다. 후보는 EXE가 아닌 diagnostic DLL이며 5개 빌드의 SHA는 표와 recalculation.json에 보존.
- 보호 원본 EXE: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(fresh make doctor verified·manifest MATCH). 보호 save006 재해시 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` MATCH. 사본 EXE는 모두 원본 SHA, 기존 raw 수정0.
- 환경 / fixture: lap907 private 전체 game/prefix/display 각 lane. synthetic=false save006; B′의 실제 완료 상태는 8 player records·약572 unit이며 G2 8인 부하 PASS 아님. C의 performance scene identity units=0 표기는 동일성 필드의 기록 범위이며 전체 게임이 빈 판이었다는 뜻 아님. G2/G5 종료·G3 중단·G4 보류 유지. 새 게임runtime/사본 생성0.

## 독립 재계산

| pair | candidate DLL SHA256 | present 수 | V2q loaded/selection/drag/minimap/production | x736..767 같은 순서 |
|---|---|---:|---|---|
| pair1 | `640344bf2d44b2f423d3861d6d222bbb6575747a48ba9c96d9359810bb42dccb` | 1189 | 0,0,363,724,657 | 0,0,96,144,136 |
| pair2 | `a8309a9dbb8ee118e34ff2707abbd41fa5369984f4143cc08a74c19068599008` | 1126 | 308,272,570,398,236 | 0,45,14,87,48 |
| c1 | `bfee0ca2d36dd04e0b8783aad9d2c104c9407d23e7affb49da8eafda6d53f03e` | 1117 | 0,692,815,694,1016 | 0,0,0,0,0 |
| c2 | `7949ee77dcc4ca3e8dcb7599f7a7d7cde797e82538b28df7d33aee521d8b4cbf` | 1088 | 45,478,860,694,995 | 0,0,0,0,0 |
| c3 | `ee8d849ef326f850c827c18868366c16ddf2463d336882d8dc04f881b97ae718` | 1103 | 308,0,805,592,843 | 0,0,0,0,0 |

- 모든 5pair의 original_stub_inputs **45개×5**가 현재 입력 SHA와 일치한다. build의 `inmm_stub.c`와 `Makefile`은 builder가 의도적으로 생성한 두 변형이다: `_imeGetTime`에 supply_probe_poll 삽입·SRCS에 runtime_bridge.c 추가. 현재 builder 규칙을 문자열 전체에 적용해 각 사본과 byte-exact 일치를 검사했고, 나머지43개는 원문 SHA 일치. runtime_bridge.c도 manifest/current/copied SHA 일치. 원본 입력과 생성 입력을 혼동한 첫 검산 진단은 이 추적 가능한 검산 오류를 고친 뒤 해소했으며 제품 근거충돌 아님.
- 후보 trace 총 **5623 present**에서 V1 위반0, 전 raw의 현재 Scale2x validator 결과가 저장 결과와 동일(PASS). 모든25tag의 V2/V2s/V2q는 별도 NumPy RGB 배열 계수로 재계산했고 저장 JSON과 정확히 일치. tripwire 임계값2000 불변.
- B′ snapshot binary20개×2,378,832bytes의 SHA·헤더·run/pid/thread/tick·순번1..5/flags0를 재검수했다. 각 lane5상태는 완료-phase reference와 일치, 8owner 불변식 위반0, 양lane 전필드 차이0. input DOWN/RIGHT 절대r1 tick·camera 동일. candidate 30present coverage는 원시 seq에서 다시 선택해 저장 배열과 전부 일치, threshold264000·key전×0.9 PASS, layer move/transfer 증가·unsupported/outside0.
- pair1 scroll coverage DOWN/RIGHT = 346526/335727; lane snapshot header 상세는 recalculation.json.
- pair2 scroll coverage DOWN/RIGHT = 346526/335727; lane snapshot header 상세는 recalculation.json.
- c1 host monotonic/tick 원시 표본 ratio **1.002501691231**, raw histogram p95Δ **8ms**, first/last20 coverage **316980.0→332034.5**. snapshot/census/scroll-phase/perf-section row0.
- c2 host monotonic/tick 원시 표본 ratio **1.000001562912**, raw histogram p95Δ **8ms**, first/last20 coverage **316980.0→332034.5**. snapshot/census/scroll-phase/perf-section row0.
- c3 host monotonic/tick 원시 표본 ratio **1.000004964061**, raw histogram p95Δ **9ms**, first/last20 coverage **316980.0→332045.5**. snapshot/census/scroll-phase/perf-section row0.
- C state_samples의 PS3/camera 고정·tick 단조 및 monotonic duration, raw PS3 present의 first/last20 coverage·누적 histogram을 사용했다. 첫 검산에서 C raw에 없는 camera 필드로 필터한 빈배열은 검산 스크립트 결함으로 수정/재실행; 게임/하네스 실패나 재실행 아님.
- RED historical 재현: lap898 C1 validator BLOCKED(894개 V1 오류), lap854 P3c gate1 PASS. lap904 B′1 `[120,2434,2402,2708,2580]`, B′2 `[308,2179,2555,2950,2851]`로 RIGHT 뒤8tag V2q FAIL; GREEN r4 `[0,94,636,1348,825]` PASS. historical-only regression이며 새 runtime PASS로 승격하지 않음.

## V3·W2 판정

- V3 **PASS(이 장면/수리 범위)**: 5pair의 원본/후보 loaded를 나란히 열었고 candidate native1600×1200도 직접 열었다. 지형·성벽/건물·소용돌이·하단 HUD/정보/미니맵이 같은 비율과 자리에 있으며 대면적 검정 결손·색 이상·이전 얇은 타일격자는 보이지 않는다. 서로 다른 캡처 시점의 소용돌이/깃발 차이는 exact same-frame 검증이 아님을 보존한다. RIGHT 뒤 pair1/2 selection·pair1 minimap/production native 우측 crop에서 32열 검은 쐐기도 보이지 않는다.
- x736..767 잔여 pair1 minimap144/production136은 카드§4.2의 100~1500 구간이다. y mod32는 0..31에 분산하고 이전 16..31 전용 쐐기 모양이 사라졌다. 위치·전체 분포는 독립 JSON에 보존, V2/V2q PASS에 따라 부분 수용하며 실제 sprite/effect 시점별 귀속은 UNKNOWN. ≤100 사전예측이 전tag에서 맞았다고 적지 않는다. ≥1500 반증0이므로 새 진단카운터를 열지 않는다.
- W2 **PASS**: tests/test_g1_mirror2x.py의 실제 gcc -std=c11 -Wall -Wextra -Werror fixture가 새 header helper를 호출한다. cache768/800/negative origin·screen768 및 A==B 잔존 제거/화면 x800..831 불변을 확인. focused162 PASS. product reinvoke·compose_cache_layer가 같은 helper를 쓰고 source 계수도 실제 bounds를 사용함을 정독했다. static 문자열 테스트만으로 판정하지 않음. 기존 설치/old bytes/rollback 테스트 유지; 동적 실패주입·강제rollback은 여전히 미검증.
- STATUS 보조 pixel evidence SHA `cd320d1985621d1a6eaa1fd11c0a712b4495d6fca01eb37c8f5556a2eb14ad6f` 읽기 확인. 이것은 lap901 pre-mask source/캡처의 완성 RGB frame Scale2x top-left 비교이며 현재 palette-index 자산 단위 합성·동일 frame oracle이 아니다. 과거 이상을 보존하되 lap907 V3/gate를 반증하는 현재 근거로 채택하지 않는다.
- selection_target·minimap·production 효과는 양lane UNKNOWN을 그대로 유지한다. B′ pair 합격식의 필수 항목이 아니며 카드§4.3 수용 범위에 맞다. 미니맵 gate0→1→0/동일 무효과 parity만 수용. 이를 UI 입력 전체 PASS로 확대하지 않는다.

## 검증·판정·handoff

- 실행 명령: `make doctor`, `make lint`, `make typecheck` PASS; `.venv/bin/python -m pytest -q tests/test_g1_mirror2x.py tests/test_g1_scale2x_mask.py tests/test_g1_saved_scene_probe.py` **162 passed /7.06s**.
- raw 재현: `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap908_middle_review/recalculate.py`. script/source/raw 입력 read-audit481개 변화0. 재계산 JSON SHA `24d791b878379dae606981d9ede7a02be01a552657ccbe6b431abe0581aa42ad`, 스크립트 SHA `34b30960d7f55600043eeab57a4281ed0cfbf421a16d85864bfd4b338d78bf2a`.
- 전체 Fast `make check`는 이 기록·handoff·feedback를 다 쓴 뒤 마지막 1회 실행한다. 로그 `logs/gates/lap908-middle-final-check.log`, exit/pid 파일 같은 이름. 결과는 fingerprint 예외인 STATUS에만 보강하며 이 기록은 검사 후 수정하지 않는다. 과거 full-test-latest를 현재 PASS로 쓰지 않는다.
- 판정: **P4c-W·B′(연속2)·C(3) 기술검수 PASS(partial), G1 HOLD**. 화면 수리 범위 수용이며 전체 HD coverage≥90%·HUD/tinted/GDI·두 번째 장면·scroll-performance/전체 입력·사용자 마일스톤은 미완. 실제 모델 메타데이터 확인 불가를 기록했으며 명시하지 않은 model/effort를 승인근거로 만들지 않는다.
- ESCALATE_SOL 생성 조건 없음: 새 근거충돌/미설명 필수검증 실패 없음, P단계 전환은 카드가 비마일스톤으로 명시. G1 마감/사용자 승인 없음. 별도 권한/모델 호칭으로 승격 leader 권한을 주장하지 않음.
- 다음 한 가지: **work D-1 PS3 writer census 실행**. 기존 P4 lap858 D-1·P4b lap863§6 범위만 이어간다. `docs/work/active/G1_WORK_W70_D1_PS3_CENSUS_HANDOFF_LAP908.md`에 측정식/한계/중단조건 명시. P5 순서는 D-1 결과의 새 middle 검수 뒤 결정, 지금 구현하지 않음.

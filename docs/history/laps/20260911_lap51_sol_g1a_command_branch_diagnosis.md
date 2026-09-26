# 2026-09-11 | lap 51 | 목표 G1-A command branch 독립 진단

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-sol`/high middle. 현재
  세션 표면은 실제 model ID/effort를 별도 노출하지 않았다. 게임 코드·helper·tests·원본·좌표·
  timeout은 수정하지 않았고 Wine/Xvfb/game/runtime을 새로 실행하지 않았다.
- 가설 / 사용자 관찰: lap50의 slot1/group10 raw와 group2..5 부재가 같은 object의 group 해석
  오류인지, `0x0049B6D0`의 조건부 생성 전제를 helper가 누락한 것인지 독립 분류한다.
- 예상 PASS / FAIL 조건: lap50 artifact/source SHA와 원본 SHA가 일치하고 group10 생성부,
  group2..5 call site/predicate/대체 분기가 한 분류로 수렴하면 진단 PASS다. 실제 predicate 값이
  artifact에 없거나 구현 전제가 원본과 충돌하면 제품/하네스 승인은 하지 않고 work로 승격한다.
- 변경 파일 / source fingerprint / 커밋: 구현 변경 없음. 본 이력, `docs/STATUS.md`,
  `analysis/memory_maps/player_offsets.md`, `loop/ESCALATE_SOL`만 갱신했다. helper/test/guard SHA는
  `a589977c5ceaaa62e54d93e0352a368cfb77d6c2c1b95b57ea6369709916cd4b`,
  `d0a841b4844b87b67c09f6579693724e07f87a76528cf3458b2e3cc8781ca757`,
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`; Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 읽기 전용 lap50 private
  원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음.
  lap50 기본 2인 random game/slot1199 선택은 과거 FAIL evidence로만 대조했다. 새 fixture/run 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`rg`/`jq`/`sha256sum`, 고정 원본
  `objdump -h`, `objdump -d -Mintel`, `xxd`; lap50 selection PNG 직접 확인; `make doctor`;
  `make check`. aggregate/verdict/inputs SHA는 각각 `9dd1d92963ed0d773616f5cb629ac3fe599ffaeee726a6e85182d1bbfb1e241d`,
  `eac1a003738f879b8db7dc803c959e431e67ac53c1ccfd96dde08e5e27516f2b`,
  `5b49852f92c34177e8843929b9dbb73ccac0d7053bd49a0da85b7295016455bc`다.
- 측정값 / 판정: group10은 `0x00498F65..B5`에서 별도 생성되며 lap50 raw의 group/callback과
  일치해 **NOT GROUP2..5 CONFIRMED**다. group2..5의 유일 call은 `0x004992DF`이고
  `[0x009B524C+type*0x394]&8 != 0` 및 `[unit+0x94] == 0`일 때만 실행된다. false면
  `0x004992EC`의 별도 UI-list 경로로 간다. helper는 두 predicate를 보존하지 않고 group2..5를
  무조건 요구하므로 **HARNESS CONTRACT REVISE**다. lap50의 실제 predicate 값과 대체 경로의
  production 의미, reset 창 여부는 **UNKNOWN**이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: doctor top-level `ok=true`, 원본 verified;
  runtime manifest absent는 새 실행 금지 범위다. Fast **109 passed**, Ruff/compileall/mypy/context
  PASS; 별도 safety **SAFETY_PASS**. 후보가 없어 patch old/new, version reject, copy-only,
  non-overlap, restore는 SKIP.
  G1 production/drag/minimap/실제2배 출력과 사용자 승인은 미완료다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 helper/tests만 최소 수정해 selection/type과
  두 predicate를 pool 전후로 같은 값인지 검사하고 실패 diagnostics에 보존한다. predicate false는
  명시적 `49B6D0 ineligible` FAIL로 끝내며 좌표 클릭·대체 경로 완화·game run은 하지 않는다.
  targeted/Fast/safety PASS 뒤 새 Sol/high 독립 검수로 넘긴다.

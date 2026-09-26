# 2026-09-11 | lap 50 | 목표 G1-A live command-cell 단일 실행

- 실제 provider/model/effort / 지정 역할: 사용자 지정 Codex `gpt-5.6-luna`/high hands-on.
  source, tests, EXE/DLL/assets, 좌표, timeout, binary는 수정하지 않았다.
- 가설 / 사용자 관찰: lap49의 2단 하네스 수리 확인 뒤 새 private 무수정 원본에서
  `g1-baseline`이 live command-cell을 관측해 production 전제까지 연결할 수 있는지 확인한다.
- 예상 PASS / FAIL 조건: 원본 SHA, 격리, 1600×1200 root, 800×600 content, setup/PS3,
  live group2..5 cell, 필수 입력, cleanup을 같은 run에서 확인한다. 하나라도 실패하면
  재시도·수정 없이 증거를 Sol에 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음.
  source/test/guard SHA는 각각 `a589977c5ceaaa62e54d93e0352a368cfb77d6c2c1b95b57ea6369709916cd4b`,
  `d0a841b4844b87b67c09f6579693724e07f87a76528cf3458b2e3cc8781ca757`,
  `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`다. Git unborn,
  `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 및 private copy
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; run
  `local/runtime/20260911_055204_1721716_0`, 새 win32 prefix, private Xvfb 1600×1200×24,
  `ko_KR.UTF-8`, `ddraw=b`. fixture는 memory write/control bridge/resource grant 없는
  새 무수정 원본 기본 2인 random game이다. PS3/tick6, owner0/1 nation2/3 active2/2가 기록됐다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `prepare --timeout 60`, `check --manifest`, 정확히
  1회의 `g1-baseline --screen 1600x1200x24 --timeout 90`. aggregate SHA
  `9dd1d92963ed0d773616f5cb629ac3fe599ffaeee726a6e85182d1bbfb1e241d`, verdict SHA
  `eac1a003738f879b8db7dc803c959e431e67ac53c1ccfd96dde08e5e27516f2b`, inputs SHA
  `5b49852f92c34177e8843929b9dbb73ccac0d7053bd49a0da85b7295016455bc`, log SHA
  `1adcb490dc7291ef49dc972e0e88d25ec177e229d7fb97a781b75f6f5405b5f2`다. PNG 8개는
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에 보존됐다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): root/content, original hash, PS9→7→5→3,
  committed solo=1, local ready=1, tick6, unit selection 0→1, modules와 cleanup은 PASS.
  `required_inputs=false`, overall **FAIL**. 327 bounded attempts 모두 group2..5가 없고
  마지막 raw는 slot1/group10 하나(`x=199,y=498,w=68,h=22`, category/flag 0,
  click `0x00498ED0`, hit `0x0`)였다. production/drag/minimap은 SKIP이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: cleanup은 `ok=true`, prefix PID `[]`,
  global kill false. Fast는 lap49 precondition 109 passed를 유지하며, 이번 필수 runtime
  FAIL 뒤 재실행하지 않았다. G1 제품 2배 출력/입력 완료, G2~G4, 2단 독립 판정, 사용자 승인은
  미완료다. `loop/ESCALATE_SOL`에 Sol이 확인할 범위를 기록했다.
- 다음 한 가지: 새 Sol/high middle이 run artifact와 현재 helper/map을 독립 대조해 group10과
  group2..5 predicate/callback/layout/reset 의미를 분류하고, 필요한 수리 범위와 old bytes/
  version reject/원복 조건을 정한다. 그 전에는 runtime 재실행·좌표/timeout 변경·binary patch를
  하지 않는다.

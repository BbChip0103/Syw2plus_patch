# 2026-10-04 | lap 916 | G1 P5-H 독립검수

- 실제 provider/model/effort / 지정 역할: Codex API, actual model/effort 미노출, 사용자 지정 middle(진단·계획·컨펌).
  게임 hands-on 수정0·subagent0·자동 모델 폴백0. `.lap_counter` bytes `916` 읽기만.
- 목표/가설: lap915의 패널 층이 lap914 H1~H5 및 PH-a~d·시각·B′·C를 만족하는지 독립 확인.
- 성공/실패식: 원본/source/build/DLL/raw SHA 일치, PH-b 독립 RLE SHA, PH-c 전체 PS3 p50 0.82~0.86,
  PH-a/d 오류0, V1 위반0, V2/V2s/V2q≤2000, B′ 완전 상태 일치, C ratio≥0.95·p95Δ≤16ms, H2 자산 키/교체 경로 존재.
- 변경파일(uncommitted): 이 기록, `docs/work/active/G1_MIDDLE_W70_P5H_H2_KEY_REPAIR_LAP916.md`,
  `docs/STATUS.md`, `docs/feedback/APPROVALS.md`. 원본/source/harness/tests/validator/안전핀/기존raw/golden/INBOX/PROMPT 불변.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  비합성 save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 재계산 MATCH.
  save의 8 owner 슬롯은 활성8인 부하 증명이 아니다. 후보별 DLL SHA는 lap915 값과 MATCH, 아래 inventory에도 보존.
- 입력: 공유 temp `captures/20261004_{014900_lap915_p5h_pair2,015200_lap915_p5h_bprime1,015700_lap915_p5h_bprime2,
  020200_lap915_p5h_c1,020700_lap915_p5h_c2,021200_lap915_p5h_c3}/pair-result.json` 및 각각 bridge/trace/PNG/snapshot/manifest.
  실행 당시 fresh private game/prefix/display 6pair; 이번 회차 게임실행0. game 사본 제거·cleanup 기록 PASS 확인.
- 독립 계산: `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap916_middle_review/recalculate.py`.
  `recalculate.py` SHA `336ffb2959374d70ba90423bb562a6d883c2fad17b4754b0bbcf1d6299788f79`,
  `recalculation.json` SHA `fcd02f7e0ac0f413999dbe02a4d397373b940e0c3d64c6d01d64cbb0474a42ed`.
  입력492개 전후 read-audit changed0. 최초 임시 검산의 함수명 import 오기2회는 실제 symbol/인자를 확인해 수리 후 완주했다.
  제품/필수 테스트 실패가 아니고 원인을 모르는 재시도가 아니다.

## 독립 수치 / 판정

| 실행 | 현재 build 입력 | present / PS3 | PH-c 전체PS3 p50 | C ratio / p95Δ |
|---|---:|---:|---:|---|
| GREEN pair2 | 48 MATCH | 1159 / 980 | 0.8333520833 | N/A |
| B′1 | 48 MATCH | 1182 / 978 | 0.8333552083 | N/A |
| B′2 | 48 MATCH | 1180 / 983 | 0.8333500000 | N/A |
| C1 | 48 MATCH | 1057 / 897 | 0.8255333333 | 1.000000871842 / +9ms |
| C2 | 48 MATCH | 1077 / 893 | 0.8255125000 | 1.000013742009 / +11ms |
| C3 | 48 MATCH | 1075 / 897 | 0.8255083333 | 0.999996755732 / +9ms |

- PH-a 각 cumulative bound981/979/983/897/893/898, unbound/lock/pointer/pitch 오류0; PH-d key emitted0.
  반환주소 허용4곳·보호 EXE hook pin `51 53 8b 5c 24 10`·trampoline/rollback 소스 확인. 동적 강제 rollback 미실행.
- PH-b: 보호 pannelj.spr header `(9,831,143,1)`에서 offset3060 RLE를 독립 디코드, 전행/EOF 확인,
  앞800열×143 SHA `f649fe68a8f9a71b9e451c01cb5b0a1d79fbb06607cc8d566d3d30d108b66000` = 여섯 runtime frame SHA.
- PH-c: 위 표는 전체 PS3 present만 표본이다. lap915 다른 수치열은 표본 정의 부재로 그대로 재현 못함;
  같은 집합이라고 주장하거나 삭제하지 않는다. 전체PS3 독립식은 operator 기록과 MATCH·모두 PH-c 통과, coverage90% 미달.
- V1: 전체6730present 위반0·Scale2x validator 전부 PASS. V2/V2s/V2q 30tag 전부 PASS;
  run별 최대 V2 `149/65/25/58/8/11`, V2s `147/149/147/165/165/165`, V2q `715/687/729/888/811/861`.
- GREEN/B′: 완료 snapshot30개×2,378,832bytes SHA/sequence1..5/thread/owner 불변식·lap888 reference 일치,
  양lane 5시점 full state diff0. DOWN/RIGHT 30present median·고정카메라 first/last20 raw 재계산 MATCH·기준 통과.
- C: monotonic start/end·tick delta·raw histogram count/p95를 독립 재계산. 계측금지 row0·span≥18000ms, 성능3/3 PASS.
- V3: 공유 temp `*_hud.png` 6쌍과 pair2 layout 직접 확인, HUD 위치·패널 윤곽·키 처리 부분 PASS.
  C1/C2 초상화/선택내용은 동일하지 않다. 알려진 입력 HOLD를 새 PASS로 승격하지 않는다. 캡처는 cross-process이며 exact same-frame RGB oracle 아님.

## H2 구현 누락 / work 이관

- `panel_capture_frame`은 `(renderer,w,h)`만 받아 panel buffer를 Scale2x한다. 원천 src/writer/digest 키를 만들지 않는다.
  `mirror_panel_rle`의 원천 source는 capture로 전달되지 않는다. output frame SHA를 자산 키 대신 셀 수 없다.
- C/H 소스에 `SYW2_G1_HD_PACK` 소비 구현이 없고 panel 경로는 공통 asset ledger도 호출하지 않는다.
  lap914 H2·§3의 같은-key 교체 계약 미충족. **실행·화면 PASS(partial), P5-H HOLD_IMPLEMENTATION_MISSING_PANEL_ASSET_KEY, G1 HOLD**.
- 수리 대상이 분명한 구현 누락이다. lap914 §5→lap911 §6의 직접 work 이관 규칙 적용, P단계는 마일스톤 아님.
  설명되지 않는 실패/서로 어긋나는 실제 실행/사용자 제출 경계 없음. ESCALATE_SOL 생성0·새 계획 승인 주장0.
- next work 범위/RED 및 fresh 검증은 `G1_MIDDLE_W70_P5H_H2_KEY_REPAIR_LAP916.md`에 명시.
  P5-H 수리 전 P5-T 전환·G1 종료 없음. 기존 기준·validator·fixture·raw/golden 유지.

## Fast / 보존 / 종료

- `make doctor` PASS·원본 verified; optional global manifest 부재의 runtime ok:false는 과거와 동일, 이번 별도 runtime 미실행.
- `make lint`·`make typecheck` PASS, focused panel/mirror/mask/scale2x/saved-scene **168 passed /6.02s**.
- `checks/safety.py check` SAFETY_PASS, `checks/context_limits.py` CONTEXT_PASS. STATUS103/INBOX348/APPROVALS245 사전 soft limit 충족.
- 전체 Fast는 **이 기록과 handoff·APPROVALS 작성 뒤** `make check`로 완주한다. 로그
  `logs/gates/lap916-middle-final-check.log`, exit `logs/gates/lap916-middle-final-check.exit`; 결과는 STATUS만 보강한다.
  이전 exit0·source 불일치 full-test-latest를 현재 검증으로 사용하지 않는다. 최신 결과 기록 전에는 현재 전체Fast 미검증.
- 새로운 runtime/24k/144k/멀티/HD-pack 전달/두번째 장면/GDI/최종 입력/scroll 성능/coverage90%/사용자 G1 승인 미검증.
- 원본/기존492입력·counter 보존, 게임 사본 생성0·커밋/게시/deploy0. 다음 한 가지는 STATUS의 work H2 수리다.

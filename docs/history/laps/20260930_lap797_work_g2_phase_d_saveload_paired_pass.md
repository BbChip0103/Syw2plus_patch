# 2026-09-30 | lap 797 | G2 ESL2608 Phase D 저장/로드

- 실제 provider/model/effort / 지정 역할: Codex native work 세션 / 현재 모델·effort 런타임 미노출 / hands-on 구현.
- 가설 / 사용자 관찰: Phase A/B parity 뒤 후보 자체 N4K8 저장 왕복과 보호된 구세이브 fallback이
  normal·fixed_start 및 baseline·candidate에서 크래시·정체 없이 동작하는지 확인한다.
- 예상 PASS / FAIL 조건: 자체 save 생성→동일 슬롯 load 후 owner unit signature 보존; 구세이브 load는
  PS3 복귀·프로세스 생존이면 PASS. baseline의 N4K8 표식 부재는 FAIL로 세지 않는다.
- 변경 파일 / source fingerprint / 커밋: `tools/g2_esl2608_phase_d_saveload_probe.py` 신규,
  도구 SHA `271c279e3f76f48710146e0c0bbcc93efea7c042707d1fb38d6f151e226cb1fd`; 제품 EXE·원본·참고
  저장소 변경 없음, uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: normal baseline
  `cade60b2…b176a3`, candidate `83c7df80…fad60`; fixed baseline `f5f816ee…e1973`, candidate
  `1bdcadf9…9262f`; Wine win32 + private Xvfb 1600×1200 + ESL2608 overlay, fresh game fixture
  owner0 2 units; protected `Syw2plus/save/save000.dat` 3,093,902 B,
  SHA `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`.
- 실행 명령: `python3 tools/g2_esl2608_phase_d_saveload_probe.py --lane {normal,fixed_start}
  --variant {baseline,candidate} --runtime-root local/runtime/esl2608_lap797_* --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_esl2608_lap797/*`.
- 측정값 / 판정: 최종 fresh 4-way **4/4 PASS**; 각 own roundtrip `2→2` owner-unit signature,
  old-save load `PASS`, crash/timeout 0, prefix residue 0, game copy removed. baseline own save
  1,803,350 B/N4K8 absent; candidate own save 1,926,146 B/N4K8 at offset60; source data unchanged.
  최종 raw SHA: normal baseline `5ae0178f…2e5f76f`, normal candidate `65ebddb5…810cb6f`,
  fixed baseline `4851a5e8…9839c2a5`, fixed candidate `530fba11…749c6c0f`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 첫 r3/r4 시도는 bridge 경로·재개 좌표 하네스
  오류로 실패했으나 원인 수정 후 r5 및 나머지 3조합을 완주했다. 제품 후보 결함으로 승격하지 않는다.
  Phase D는 work PASS이며 middle 독립 검수·DxWnd·24k/144k·멀티·사용자 승인은 미완료.
- 다음 한 가지: Phase E fresh work — 지원 환경에서 멀티/전달 경로를 시도하고, Wine/IPX blocker면
  정확한 오류와 정적 명령·저장 ABI 대조로 제한한다.

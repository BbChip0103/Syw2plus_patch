# lap1290 work → fresh middle handoff

## 이유
`docs/STATUS.md`의 단일 다음 단계는 lap1289 H-G1ON2614 결과에 대한 fresh middle 독립 검수다. 현재 호출은 사용자 지정 일반 hands-on work 역할이므로 구현 작업자가 자신의 이전 결과를 승인하거나 middle 역할을 대신하지 않는다. 제품/마일스톤 판정을 진행하기 전에 역할 경계를 승격한다.

## 검수할 대상
- work 기록: `docs/history/laps/20261014_lap1289_work_g1_esl2614_winmm.md`
- 런타임 raw: 공유 temp `20261014_lap1289_g1on2614_retry1/`, `20261014_lap1289_g1on2614_soak1/`, `20261014_lap1289_g1on2614_mci/`의 `g1-esl2614-result.json`
- 주요 구현/테스트: `tools/inmm_stub/g1_winmm_proxy.c`, `.def`, `g1_winmm_forwarders.S`, `Makefile`, `tools/generate_g1_winmm_exports.py`, `tools/esl2614_runtime.py`, `tools/g1_esl2614_display_probe.py`, `tools/g1_saved_scene_probe.py`, `tests/test_g1_winmm_proxy.py`
- 주장된 DLL SHA256: `d2ce1637574340dbd306fa4a41a591461c899cc03c987568ee018b576ec65c53`; 공식 2614 EXE SHA256은 `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`.

## Middle의 독립 확인 항목
1. 현재 소스에서 proxy가 Wine/system WINMM의 export 189개를 name+ordinal로 전달하고 4 hook ordinal이 실제 정의와 일치하는지 새 계산한다. System32 원본 로드 경로 및 forwarded export 동작의 근거를 확인한다.
2. 공식 EXE 원본 SHA 불변, 사본/prefix/display/process cleanup 및 4 lane(new-game/save006 × off/on)의 JSON/raw 산출물을 대조한다. save006은 구 fixture이고 2614 자체 생성 save roundtrip이 아니라는 한계를 유지한다.
3. 480초 run의 3,623 presents, HD 100%, stale/fallback/safety 0, crash 0과 종료/cleanup를 raw에서 독립 재계산한다. 첫 harness guard 실패와 수정 후 재실행은 이력을 보존한다.
4. 기본 및 force-music run의 MCI call 0을 UNKNOWN으로 유지한다. 음악/효과음 성공을 승인하지 말고, 다음 오디오 probe가 실제 MCI 발화를 검증할 수 있는지 범위를 제시한다.
5. Windows·사용자 입력·긴 장시간·2614 자체 저장 재로드는 미검증으로 남긴다. 이 결과를 사용자 승인, G1 milestone 완료, 시험판 전달 승인으로 확대하지 않는다.

## 상태 / 제한
- 이번 lap은 문서 인계만 했다. 제품 소스, 테스트, 게임 실행, 후보 DLL, 원본 입력에는 변경이 없다.
- 사용자가 준 runtime evidence: `current_head=27dad8128791b70770dbabc6f21342eea76ef53c`, `source_match=no`, gate scope FAST source checks only. 이를 새 source verification으로 주장하지 않는다.
- runtime에서 제공된 이전 full-test는 2026-09-24 source `5e225d0e…`로 현재 증거가 아니다. 재사용/현재 PASS로 승격하지 않는다.
- worktree에는 lap1289 및 타 세션의 다수 미커밋 파일이 있다. 수정·정리·스테이징·커밋하지 않았다.
- middle 결과 뒤에도 G1 미결 항목이 남는다. G5는 INBOX의 2614 G5 별도 세션 지시 및 STATUS 순서를 따른다.

## 요청
fresh middle 역할이 위 항목만 독립 확인하고, 수용/보류와 최소 다음 행동을 `docs/STATUS.md`에 반영한 뒤 root가 다음 작업을 정한다. 이번 work 세션은 여기서 종료한다.

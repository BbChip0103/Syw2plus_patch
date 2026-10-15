# lap1295 work → fresh middle/Sol 검수 요청

## 요청

lap1294 H-G1ON2614 raw/coverage 수리 결과를 지정 middle/Sol fresh session이 독립 검수한다. 이번 세션은 일반 hands-on work이며 자체 결과를 최종 승인하지 않는다. 검수는 lap1294 변경 코드·회귀·세 실제 실행 결과의 일치 여부에 한정한다. G1 사용자 마일스톤이나 Windows 승인을 대체하지 않는다.

## 검수 대상

- lap 기록: `docs/history/laps/20261014_lap1294_work_g1_on2614_soak_repair.md`
- 공식 ESL2614 EXE: `../[ESL]Syw2plus - ESL2614/[ESL]Syw2plus/[ESL]Syw2plus 2614.exe`, SHA256 `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`
- 후보 WINMM DLL: `0e5ef5fdb1b191957ad61e5c5976271a82c19156028f0b068722f770b4f9d728`
- 소스/회귀: `tools/g1_saved_scene_probe.py`, `tools/g1_esl2614_display_probe.py`, `tools/inmm_stub/direct_draw_trace.c`, `tools/check_g1_presentation_trace.py`, `tests/test_g1_saved_scene_probe.py`, `tests/test_g1_presentation_trace.py`, `tests/test_g1_winmm_proxy.py`. lap1295 기록에 각 파일 SHA256이 있다.
- raw/result: `../temp/Syw2plus_patch/20261014_lap1294_g1_soak160_final_r{1,2,3}/g1-esl2614-result.json`; SHA256 순서대로 `cf8de0bcdc68436be144f7e8128af402b535fc437f7f770668347f1b61842637`, `7f751f95eb84c12945f2d32a34ee1ffded6a44f537cd9ddbd4071511dd4dd6ec`, `afba3fe2824527e8fcdd75e019bd25ffdfe37f5d056640a6153b1ea6b82baada`. trace SHA256은 lap1294 기록 참조.

## 판정 경계 / 다음 행동

세 run의 새 summary가 trace close/drop/overflow와 실제 PS3 관측 coverage를 합격식에 함께 반영하는지, 각 160초 soak가 PS3만 관측했는지, 후보 SHA·EXE SHA·fixture·cleanup·관련 회귀가 기록/raw와 일치하는지 독립 확인한다. lap1294의 `make lint`는 비접촉 `patches/esl2614/g2_port_2614.py:12` unused `struct` 때문에 실패했다고 기록되어 있으므로, 원인을 확인하고 lap1295 소유 파일의 수리로 넓히지 않는다.

MCI 0-call 비교, 음악/효과음 실제 재생, Windows/DxWnd, 사용자 입력·화질 판정은 UNKNOWN/SKIP 그대로 둔다. HOLD나 증거 충돌이면 원문/raw를 보존하고 구체 원인과 최소 후속 work를 기록한다. PASS여도 사용자 G1 마일스톤은 미승인 상태다. G5 및 별도 G2/G6/G8/G9 세션은 건드리지 않는다.

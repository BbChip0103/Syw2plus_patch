# 2026-10-07 | lap1151 | G1 work — H-TR3 묶음 시험판 재스테이징(lap1135판 대체)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. C·하네스·테스트 변경 0, 커밋 0.
- 가설 / 사용자 관찰: lap1150 사전등록 H-TR3 — 현재 트리(lap1135판 뒤 기본 켬 가시 수리 H-TM1·H-SC2 추가)로 save006 full pair가 사용자 시험 판정 경로에서 PASS하고, 그 DLL을 시험판으로 묶을 수 있다. 사용자 G1 시험 결과·새 INBOX 지시 없음(마지막 = lap1150 처리 메모), `loop/STOP`·`loop/ESCALATE_SOL` 없음.
- 예상 PASS / FAIL 조건: lap1150 §6 TR3-0~TR3-3 그대로. DLL 비타임스탬프 차이 0, 스테이징 정확히 4파일.
- 변경 파일 / source fingerprint / 커밋: 제품 source·테스트·하네스 변경 0(uncommitted 기존분 그대로). TR3-0 source SHA 12자리 6/6 일치: `g1_briefing_compose.h` `fa26be35c0b2`·`g1_mirror2x.c` `e3c6a1bcd754`·`g1_mirror2x.h` `a6eda22ba8a0`·`direct_draw_trace.c` `d3e372e276a7`·`Makefile` `de73c1045595`·`tests/test_g1_briefing_compose.py` `c19dd4548436`. 새 파일은 공유 temp(`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261007_lap1151_work_htr3/`)와 이 기록뿐.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만), pair 두 lane private EXE SHA 동일. fixture 비합성 `save006.dat` `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`(selected_index 7). 후보 DLL = pair `bridge/_inmm.dll` `8a3837fb9ef97c33bf60b451bdd47ca066a7e655b482ac9c9a2b5f2b72011d5f`(457,256 B). Wine 격리, 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1151_tr3_pair --artifact-root <공유 temp>/pair --hd-source scale2x --candidate-no-present-trace --candidate-no-unit-ticks`(setsid nohup, exit 0, 약 2분). 로그 `logs/gates/lap1151-tr3-pair.log` `7335beed0522`·`.exit`=0, `pair/pair-result.json` `ade828bbbcd9`. 스테이징 스크립트 `<공유 temp>/scripts/make_staging.py`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

## TR3-1 save006 full pair — PASS

- 최상위 `status` PASS·`scene_state_equal` true·`execution_source.unchanged` true·baseline/candidate `source_unchanged` true·두 lane `cleanup.ok`·`game_removed` true·`prefix_processes_after` []. 후보 창 1600×1200·scale 2.
- `input_effect_comparison` PASS(선택·빈 클릭·드래그 정확·드래그 캡처 결속·미니맵 게이트 복원·생산 효과·생산 완료 7/7 true). `minimap_diagnostic_parity` PASS(4 체크 true). V2·V2s·V2q gate PASS(5 tag 전부 PASS)·Scale2x gate PASS(mirror present 1,191 = scale2x present 1,191, 팔레트 위반 0, HD 마스크 밖 차이 0)·loaded 비교 PASS(v2s 단일 흑 1,912·비설명 36).
- **공개 사항 3개(lap1135 TR2-1 pair와 같은 값·같은 원인, 판정 영향 없음):** ① 후보 `trace_close.status` FAIL(`owned Win32 PID trace has a mismatched run_id`) ② 후보 `mirror_validator.status` BLOCKED(nearest oracle 최소 0.7759 < 0.999; `--candidate-no-present-trace` 경로) ③ production 캡처 `v2s_raw_status` FAIL(단일 흑 2,821 > 2,000, 비설명 200) — 공개 진단이며 gate는 W-1(비설명 ≤2,000)로 PASS. lap1135 대비 차이는 mirror present 1,192→1,191·event 2,276→2,275·present 최대 16→15 ms·production 단일 흑 2,833→2,821·비설명 186→200뿐이고 기타 비교 키는 전부 같다(키 집합 동일).
- 후보 prefix에 `inmm_unit_ticks.jsonl` 없음(파일은 baseline prefix에만 있고 baseline에는 `--candidate-no-unit-ticks`가 적용되지 않는다). run 뒤 `local/runtime/lap1151_tr3_pair/*/game` 0개, 디스크 여유 70G.

## TR3-2 DLL 동일성 — PASS

- 스테이징 DLL = `pair/bridge/_inmm.dll` 그대로. 대조(바이트 단위):
  - lap1149 on1 DLL(`29519743c515…`): 길이 457,256 일치, 차이 7바이트 = 오프셋 136·137·216·217·218·347140·347141(PE 파싱으로 확인: e_lfanew 0x80, 136~139 = COFF `TimeDateStamp`, 216~219 = 옵션 헤더 `CheckSum`, 347140~347143 = `.edata` export 디렉터리(파일 오프셋 347136) `TimeDateStamp`; 차이는 그 안의 바이트들뿐) → 비타임스탬프·비체크섬 차이 0.
  - lap1150 middle 재조립 DLL(`9f0404fb35e5…`): 길이 일치, 차이 6바이트 = 136·137·216·217·347140·347141, 같은 세 필드.
  - 문자열: `INMM_STUB_NO_UNIT_TICKS` 1회, `SYW2_G1_BRIEFING_COMPOSE` 1회 존재.
  - lap1135판 DLL(`6cbb12ac…`)과는 크기만 비교: 448,133 → 457,256 B(+9,123 B; H-TM1·H-SC2 코드).
- 이 동일성으로 lap1149 on1·on2 브리핑 측정이 스테이징 DLL에 적용된다(브리핑 재실행 없음).

## TR3-3 스테이징 — 완료(정확히 4파일)

- 위치 `<공유 temp>/user_test_staging/`: `_inmm.dll` `8a3837fb9ef9…`(위 SHA 전체)·`g1_trial_direct.bat` `2da323e8bf53…`·`g1_trial_via_dxwnd.bat` `29a35d2edf41…`(둘 다 lap1135 스테이징 byte 그대로, SHA 확인)·안내문 `G1_1600x1200_시험판_읽어주세요_20261007_lap1151.txt` `d577283c3848…`.
- 안내문 diff(`<공유 temp>/guide_diff.txt`, lap1135판 대비): ① 제목·DLL SHA 개정 ② "이 판은 12:53 전달 lap1135판(`6cbb12ac…`)을 대체(00:21판 `94213374…` 포함), 옛 판 결과면 어느 판인지 알려 달라" ③ 12:53판 대비 추가 수리 2개(⑤ 처음 실행 때 사용자 등록 창 바탕 화질, ⑥ 브리핑 초상화 화질; 위치·입력 동작 불변)와 기존 4개(①~④) 유지 문구 ④ 공개: 브리핑 화면에서만 프레임 간격 Wine 측정 약 +4~6 ms(체감·실제 Windows 미측정). 그 밖 문구 변경 없음.
- `260921_temp` 배치·APPROVALS 쓰기 0.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이 pair는 save006 인게임 장면 경로 증거이고 H-TM1·H-SC2 화질은 각각 lap1142·lap1149 격리 측정(위 DLL 동일성으로 연결)이다. 다른 장 브리핑·`0x41C020`·실제 Windows 표시/성능은 미측정(backlog 유지). middle 독립 검수 전, 사용자 시험 결과 없음. 모델 기술 수용은 사용자 합격이 아님.
- 검사: 전체 `make check` SKIP(C·하네스·테스트 source 변경 0, TR3-0 6/6 일치 = lap1149 full PASS 1823 passed·5 skipped 트리 그대로). `checks/safety.sh check`·`checks/context_limits.py` 결과는 STATUS 검증 줄에만 쓴다.
- 다음 한 가지: middle(Opus)이 새 스크립트로 pair-result raw 재계산·현재 트리 재조립 대조·안내문 열람 → 수용 시 APPROVALS lap1136 항목에 "lap1151판으로 대체" 메모 + 새 사용자 시험 요청, root 전달 `loop/ESCALATE_SOL`. 사용자 G1 시험 결과가 오면 그것이 최우선.

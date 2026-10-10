# 2026-10-10 | lap 1230 | G1 middle — 2611 historical PASS/raw 충돌 독립 확인·승격

- 지정 역할: middle(진단·계획·확인). Codex App native-hook/outside tmux; 실제 resolved model ID/effort를 이 surface에서 확인할 launch log가 없어 추정하지 않는다. MODEL_ROUTING 현재 middle 계약 `gpt-6.1-sol`/high; 게임·하네스 hands-on 수정 0·provider 폴백 0.
- 입력/순서: PROMPT ① G1 계약 → ② AGENTS/최신 INBOX/APPROVALS/STATUS/DESIGN 1~4 및 lap1229 → ③ 보호·역할·장기실행 규칙 → ④ 현재 큐의 전회 결과 독립 확인·검사 → ⑤ 기록 보존 → ⑥ 안전·QA 한계와 handoff. runtime lap counter=1230 읽기만, STOP 없음. STATUS67/INBOX224/APPROVALS34줄 확인 후 산출물 기록.
- 한 가지 가설: lap1229의 historical 충돌은 전사 오류가 아니라 no-present-trace의 소유권 ID 제거와 aggregate 종료 gate 누락으로 인한 false PASS이고, 이번 수리는 fresh 후보 종료를 실제 검증한다.
- 성공식: historical 두 후보의 raw SHA/ID/summary와 JSON 판정 직접 비교; fresh 후보는 run ID 단일 일치·summary 정확히1/drop0/detached/detach complete/flush complete·소유 PID=requested PID·matched window1/post 성공을 모두 충족. historical PASS 대 raw FAIL이면 수용 HOLD·승격 종료.
- 변경 파일: 본 기록, 이전 ESCALATE_SOL 원문 보존 파일, docs/STATUS.md, docs/feedback/APPROVALS.md, loop/ESCALATE_SOL. 독립 스크립트/결과는 공유 temp 아래. 게임 코드·하네스·테스트·원본·raw·전달물·golden·pin 변경 0, 커밋/푸시/배포 0.

## 독립 확인과 근거

- 새 검사 스크립트: `../temp/Syw2plus_patch/20261010_lap1230_middle_review/review.py`; 실행 `python3 ../temp/Syw2plus_patch/20261010_lap1230_middle_review/review.py`. 결과 `review.json` SHA256 `74da25306fc2388f1f1e7fc9184fea4baf675675d3a8da0096da1b113fd8b837`. production parser를 호출하지 않고 JSONL 직접 파싱·전파일SHA 재계산.
- historical TR-1 두 후보: pair PASS vs close FAIL(mismatched run_id), raw ID unknown만 존재·summary0. 6개 lane raw SHA는 각 probe의 기록과 MATCH. 단순 오타/잘린 해시가 아니라 실행 소유권·완주 증거 누락으로 인한 실질 충돌.
- fresh pair03: 후보 close PASS·raw ID g1-saved-candidate 단일·summary1/drop0/detached/detach complete/flush complete, Win32 owned PID276=requested PID276·match_count1/post true. baseline도 summary 완주 확인. scene equal 및 V2/V2s/V2q/Scale2x/input effect gate는 JSON PASS 관측(이번 픽셀 전수·실제 입력·새 런타임 재실행 아님). game 사본 없음·private prefix 보존 확인, cleanup/source_unchanged는 기존 실행 보고와 구분한다.
- 공식2612 EXE SHA `6562797d95ddb2013931ffb23ec10bf3fcac631af5f82efdd06a56ef95ce42e7`(2,000,896B), save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`(3,437,942B) 직접 MATCH. fixture synthetic=false; active8인/24k/144k 안정성을 의미하지 않는다.
- `tr1_1`: pair SHA `a98416dc0867434dc8d93f2b6ac113e8694a2b719e718b1060bfa32d01bd7fd0`; 후보 probe SHA `11c9c881a527e30cfbf94e9f5a833dcd27098757cef024109587ee7e06d0b11c`; raw SHA `5058f5fa1e391edd835d5f6158f29c3f3ccfbc64136bdec2e0519180a11c0df2`; run IDs=['unknown'], summary=0, owned PID request match=False.
- `tr1_2`: pair SHA `7cc5500a2b87296d821e8abbe0f2628ec3d1218b006a37725b912d2450dac695`; 후보 probe SHA `f041265a208c04f432530b61efe82562d57ddf33b216e6eab1ba94f583e483ab`; raw SHA `e46abe1845de082e924c1d18cb7db9a16671c01196b5d4f623f711aa25615718`; run IDs=['unknown'], summary=0, owned PID request match=False.
- `pair03_fresh`: pair SHA `138ba66567489ab63265f2a55066083ffff69cd6e84ee2196a5b72147b48ec27`; 후보 probe SHA `0c662a5bb1aa7b29220ff95582353b63434b7b845afafb9e68da206d045f9c58`; raw SHA `1a81e28b856cb51b7a356228568e38377bd0d9611adf9144adc2a55643037f43`; run IDs=['g1-saved-candidate'], summary=1, owned PID request match=True.

## 구현 검수/검사

- 소스 read-only 확인: `tools/g1_saved_scene_probe.py:4039`는 present flag만 pop하여 lane ID 보존. `:2742`는 ID·unique summary·drop0·detach/flush 검사, `:6655` candidate close/summary 실패를 HOLD로 집계한다. `:6170` 소유 PID 정상 close, `:6206` cleanup 뒤 raw summary 확인. historical 완주 없는 PASS와 구분 가능해진 수리 방향은 타당하나 전체 기술 수용은 HOLD.
- routing fixture의 history 제외는 archived 문서 복사만 제거하며 20초 timeout·exit75 재시도 단언은 유지. 이번 focused 원래 assertion 실행 GREEN; 전체 라우팅/전체 Fast 증거는 아님.
- `make doctor` PASS(`logs/gates/lap1230-middle-doctor.log`); 기본 setup은 새 private 런타임 검증 아님.
- `make lint` PASS(`lap1230-middle-lint.log`, Ruff/compileall), `make typecheck` PASS12(`lap1230-middle-typecheck.log`).
- `.venv/bin/python -m pytest -q tests/test_g1_saved_scene_probe.py tests/test_g1_new_game_path.py tests/test_model_routing.py -k 'owned_close or trace_close_summary or user_trial_disables or raw_worker_exit75'`: **8 passed,326 deselected/4.33s**, `logs/gates/lap1230-middle-targeted.log`.
- `make check` SKIP(승격 조건): 사용자 “실질 raw 충돌이면 보존·ESCALATE_SOL 생성 후 끝내라” 지시에 따라 historical 충돌 독립 확인 뒤 장기 전체검사/새게임/마감 시도 없음. source 달라진 과거 전체 Fast exit0은 현재 승인 근거 아님. 최종 안전/context/diff 수치는 STATUS에만 보강한다.
- 기존 ESCALATE 원문 byte-exact 보존: `docs/history/laps/20261010_lap1230_preserved_lap1229_escalate_sol.txt`, SHA256 `6a45d75c8de0a0a1dd757961c6d9f564e484680e027d1f7b66b440ae4bd3577b`. raw/과거 수용 원문/이미 전달된2611 파일은 그대로 보존한다.

## 판정·승격 handoff

- **H-TR2611(lap1223/lap1226) historical 기술 수용 HOLD:** 전달 사실·독립 픽셀/입력 관측은 취소하지 않지만, 두 TR-1 후보 모두 정상 close/summary가 없어 포괄 PASS를 그대로 승인 근거로 쓸 수 없다. APPROVALS/STATUS에 현재 정정 판정을 추가하며 과거 원문을 덮지 않는다. 이는 확인 결과이지 마일스톤 최종 승인 아님.
- **lap1229 2612: 후보 종료 수리의 국소 확인 PASS, 전체 기술 수용 HOLD.** 현재 source 전체 `make check`가 필요하며 위8개나 과거2171은 대체 불가. G1 마감·2612 trial 준비/전달 보류.
- 승격 담당(root/지정 Sol)은 historical 수용 범위 정정과 전달된2611판 처리(외부 행동은 root)를 결정하고, 기록·handoff 고정 뒤 동일 source 전체 Fast를 완주해 before/after fingerprint MATCH를 확인한다. 사용자 G1 판단과 구분한다.
- **work tier 명시 인계:** 이번8개 확인 범위에서 새 구현 결함 없음. 전체 Fast 실패가 source/fixture/harness 결함이면 work 소유(`tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`, `tests/test_g1_new_game_path.py`, `tests/test_model_routing.py`)로 최소 수리→원래 단언 targeted GREEN→필요 시 같은2612/save006 fresh 격리 pair→새 middle 검수. middle은 구현하지 않고 gate·pin 완화 금지, 별도G2 세션 파일 비접촉.
- 다음 한 가지는 STATUS만 정본. 현재 변경·근거를 보존하고 ESCALATE_SOL을 남겨 이 회차 종료. 새 런타임0·게임 사본0·시작한 targeted 프로세스 완주·실제Windows/사용자플레이/24k/144k 미검증.

## 수리 소스 SHA(독립 검사 snapshot)

- `tools/g1_saved_scene_probe.py` SHA256 `cf86b9e9d580b593d2e2c23c2f0d571deb2e4e1a3cb43037c5a4197d58f65ab9`.
- `tests/test_g1_saved_scene_probe.py` SHA256 `fbb21e02b55c15c1bfce674f1e54a2a7031f0cf8933ad65c54372d87f3d70d25`.
- `tests/test_model_routing.py` SHA256 `28cf8b2770e1855b23fd83ca943677b06dcd9911466c96fd8a07930bb78c7b62`.

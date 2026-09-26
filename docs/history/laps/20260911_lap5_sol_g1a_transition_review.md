# 2026-09-11 | lap 5 | G1-A PS7 전이 middle 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex; 런타임이 정확한 모델 ID/effort를 노출하지 않아
  `gpt-5.6-sol/high` 실제값은 미확인 / 사용자 지정 middle 진단·계획·컨펌 역할만 수행.
- 가설 / 사용자 관찰: lap4 PS13 실패는 confirm 좌표 오류가 아니라 PS7 기본 `여럿하기` 상태에서
  `혼자하기`를 선택하지 않은 setup 전제 오류이며, 이를 분리하면 한 번의 검증 가능한 Luna run이 된다.
- 예상 PASS / FAIL: lap4 manifest·EXE·화면·입력·cleanup이 기록과 일치하고 원인과 새 endpoint 측정식이
  하나로 좁혀지면 middle PASS; 충돌하거나 새 실행이 필요하면 UNKNOWN과 work handoff를 남긴다.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G1_A_EXECUTION_CARD.md`, `docs/STATUS.md`,
  이 기록, `loop/ESCALATE_SOL` 해소; 게임 코드/EXE/DLL/asset 및 tools/tests 수정 없음; uncommitted/unborn HEAD.
  검수 시 미승인 제안 SHA: `tools/runtime_env.py` `7aa1859ccf2c0173c6740f154262c83200c5786c6296edf6a59a5b5d978d71c8`,
  `tests/test_runtime_env.py` `a5143fa1d011fc1d9899ad5537ac6d2eec1b08b7fbbc30241a94b930d4f7794f`.
  보존 해시: card `4cd88ee8c39a5e7a321d64bceed028c954218ea5536f7c68a6cc7fe22fca4bca`,
  STATUS `dc28cba2052b767e249858fff799c0e66497deb525669535a206c7462b9a6b3d`,
  ESCALATE_SOL `34cbf16c70111c9d3a2b57e395a9e16e4aac0da937447b4f0c2d42571794b519`,
  loop.sh `d25baa1da48597bb521fa0977e65558776b708daa1a6dda9fadd76e9e897e8e9`,
  test_model_routing `0e9f2736d8b64394dcd99f62d60c2643f7b091fbbf07267b9d9246c696fe7c9d`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: lap4 manifest
  `fb57e4e2e74dadd6988aae453041ce7184427ed0526bdb434527e75866784597`, 원본/격리 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음;
  lap4 `:91`, 1600×1200 Xvfb, 800×600 content, 실제 PS3/활성 플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 문서·JSON·SHA·process read-only 검사와 캡처 시각 검수.
  lap4 `verdict.json` FAIL, `inputs.jsonl` 1행 PASS, 화면 `c0154462...5489`; 중단 run의 선택 후 화면
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260910_235604_20260910_235524_3364091_0_3366253_solo_mode_selected_1789052164375716444.png`,
  SHA `c6bd413791c93b1130def310f3b50980d7032491b4cba2caf21a3ae69bc80a11`.
- 측정값 / 판정: lap4의 root/content/module/cleanup PASS와 PS13/tick0 FAIL은 독립 일치.
  화면은 최초 PS7이 Internet TCP/IP가 선택된 `여럿하기`임을 보이며, 중단 run은 `(462,169)` 뒤
  `혼자하기` 선택 표시 변화만 입증한다. 원인은 **CONFIRMED**, revised card는 **DRAFT**;
  중단 run은 verdict/입력 JSON이 없어 actual gate **UNKNOWN**이며 G1-A/G1 제품 판정은 미완료.
- Fast: `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py`는
  **14 PASS**. 이어진 `make check`는 **81 PASS, 1 FAIL**, exit2. 실패는
  `tests/test_model_routing.py::test_worker_escalation_stops_for_explicit_middle_review`에서 work가
  `ESCALATE_SOL`을 생성했는데 `loopctl run 1`이 기대한 nonzero가 아니라 0을 반환한 역할 경계 회귀다.
  예상 밖 필수 게이트 실패이므로 재실행·수리·게임 실행 없이 승격한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 현재 제안 코드가 순간 PS4/5/6 관측을 필수화한
  부분은 근거가 없어 카드에서 제거했다. 혼자하기 후 confirm endpoint, 준비/시작, PS3 장면과 필수5입력은
  새 Luna run 필요. 사용자 마일스톤 승인 없음. 프로세스 검사에서 해당 prefix/Xvfb 잔류0.
- 다음 한 가지: 새 Sol/high가 loop controller의 escalation return-code 계약 실패를 독립 진단하고,
  최소 수리 범위와 검증식을 Luna/high에 넘긴다. 이 필수 게이트가 PASS하기 전 G1 run은 금지한다.

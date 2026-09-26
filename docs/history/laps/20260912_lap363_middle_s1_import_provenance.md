# 2026-09-12 | lap 363 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex 현재 세션, 정확한 모델 ID 미노출·미주장 / 사용자 지정 high / middle 진단·계획·확인. 저장소 MODEL_ROUTING의 Opus5-only와 차이를 공개하며 외부 모델 호출 0.
- 가설 / 사용자 관찰: lap362 ImportError는 시스템 Python의 형제-repo editable `tools` shadowing이다. repo root와 프로젝트 `.venv` provenance를 명시하면 역사 probe를 수정 없이 통과시킬 수 있다.
- 예상 PASS / FAIL 조건: 보호 입력·세 source·probe SHA 일치, current-repo import origin, 원본 probe exact-once rc0/`failures=[]`, doctor/Fast/safety PASS면 lap362 §3 RELEASE. 하나라도 다르면 STOP/승격.
- 변경 파일 / source fingerprint / 커밋: `docs/work/active/G1_S1_IMPORT_PROVENANCE_MIDDLE_LAP363.md`, `docs/STATUS.md`, `loop/ESCALATE_SOL`, 이 기록. 게임 코드·하네스·tests 변경 0; source SHA `ba0a7beb…7372c`/`fffc6444…fa65`/`7508e5c1…b8c7`; uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 1,032,192 B / `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 없음; Linux/Python offline. 활성 플레이어·지도·군대 N/A. save000 3,093,902 B / `1c703551…19da`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; repo-root `PYTHONPATH`+`.venv` wrapper가 current `runtime_env.__file__`을 출력한 뒤 `runpy.run_path`로 원본 lap354 probe `b08d0c7b…07a4`를 정확히 1회 실행; targeted pytest; `make check`; `bash checks/safety.sh check`. 로그/PNG 없음.
- 측정값 / 판정: origin=`/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch/tools/runtime_env.py`; probe rc0/`failures=[]`; targeted 21 passed; Fast는 기록 전 399 passed/63.70s, 기록 후 최종 현재 트리 399 passed/64.15s이며 Ruff/compileall/mypy/`CONTEXT_PASS`; safety `SAFETY_PASS`; doctor original verified, runtime manifest absent/side_effects=false. **ACCEPT / lap362 §3 RELEASE**.
- 패치 안전: EXE/DLL/patch bytes 생성·수정·복원 0; 원본 pin 일치. old/new bytes·combined overlap·restore는 N/A이며 captured fixture를 fresh runtime proof로 승격하지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 실제 게임/load/input/PNG 0회. pre slot1·open/load·두 run 결정성·S1 (A)+(B)·Stage B·WM_CLOSE·제품 G1~G4·사용자 승인은 UNKNOWN.
- 다음 한 가지: Luna/high work가 `docs/work/active/G1_S1_MIDDLE_EXECUTION_ENVELOPE_LAP362.md` §3만 세 허용 파일에 구현하고 실제 게임 0회로 targeted→lap354 probe→Fast→safety와 전후 SHA를 제출한다.
- 종료 문서 SHA: card `6311368607c912dd6c561c24b5a3891b73b46ec111c5c8a61d46ab2f7b604185`; STATUS `11c38a725cf645094c44d74951efcec43290f0ee8da581a9bfd3e5a5890fa336`(124줄, Blockers 표제 1개); `loop/ESCALATE_SOL=4a4f7d4eb19a0389108e63dd3b8b5611d93af97f33743fd6b35f349e1f5c8166`.

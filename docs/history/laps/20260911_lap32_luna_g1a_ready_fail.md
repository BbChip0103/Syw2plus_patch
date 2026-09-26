# 2026-09-11 | lap 32 | 목표 G1-A 새 원본 실행 — ready 입력 효과 FAIL

- 날짜/lap/목표: 2026-09-11 KST / lap32 / G1-A 원본 구성·입력·출력 경계
- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna`/high work 지정. 현재 호출의 실제 model ID/effort는 노출되지 않아 미확인. 게임/EXE/DLL/assets 변경 없음.
- 가설 / 사용자 관찰: lap31 Sol이 selector DWORD one-hot 및 confirm-time WORD=1 하네스를 독립 CONFIRMED했으므로, 새 격리 원본의 고정 입력이 PS9→PS5→PS3와 필수 입력 경계를 관측할 수 있어야 한다.
- 예상 PASS / FAIL 조건: G1-A 카드의 동일 새 manifest, 원본 SHA, private 1600×1200 display/prefix, 800×600 crop, selector, confirm, PS5→PS3, 전투·필수5입력, surface/module/cleanup을 한 run에서 확인. 필수 gate 실패 시 재시도·패치 없이 Sol 승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 코드/테스트/바이너리 변경 없음. 실행 하네스 `tools/runtime_env.py` SHA256 `e06c73a9d9602d1f036ab3f8ebcf306a3ee01e21945fd27b54daab502f6e5e49`; 관련 테스트 `tests/test_runtime_env.py` `5ea8ea87672577bde15dc67cf647a84e382fb1fe2c8f54e9645738546ea1f9fd`, `tests/test_runtime_guards.py` `93e3af951805a773ddd298d1636db84304d2cd708218c9eb68f64bfa126ff8e3`. 문서/`loop/ESCALATE_SOL`만 추가·갱신. Git unborn/uncommitted, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 및 새 private copy EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; manifest `local/runtime/20260911_033834_765190_0/manifest.json` SHA256 `057cf32ae1fe7a32929a4cbd68e5e005dced72258d612b6a3b495cc886664ded`; `DISPLAY=:91`, win32 prefix, `1600×1200×24` virtual desktop. fixture는 새로 복사한 무수정 원본의 기본 2인 임의게임이며 control bridge/save/resource grant/synthetic fixture 없음. ready gate에서 실패하여 실제 전투 활성 인원·지도·군대는 미측정.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `prepare --timeout 60` PASS → `check --manifest local/runtime/20260911_033834_765190_0/manifest.json` PASS → `g1-baseline --manifest local/runtime/20260911_033834_765190_0/manifest.json --screen 1600x1200x24 --timeout 90` FAIL. aggregate `local/runtime/20260911_033834_765190_0/output/g1_baseline.json`, log `output/g1-baseline.log`, evidence `output/g1_a/{provenance,window,surface,modules,inputs,scene,boundary,verdict}` 보존. ready before/after 전체 PNG SHA `b69e6b6cd16fd2711b740054d8a5208ffb8a25f7b2144d8ab8ec2bde88e03a3b` 동일; ready crop SHA `7d2f1f3ffc53275a65062262a1f4e4e8643b0d8d4326788d6b0ff6cd5b5832f9` 동일.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `verdict.json` overall **FAIL**. PASS: original hash, private 1600×1200 root, 800×600 content crop, PS9 surface (`0x00E5BF18`, mode3/800/600/8/800/600), selector one-hot transition, confirm PS5/committed mode1, module hashes, cleanup. FAIL: player-0 ready input effect; `surface_ps9_ps3=false`, `required_inputs=false`, `same_run_scene=false`. SKIP: PS3 surface/scene/boundary and 후속 전투·입력. `exit0`/PNG 존재를 성공으로 쓰지 않음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `make check` → 94 passed; Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` → `SAFETY_PASS`. G1 제품·G2~G4·사용자 마일스톤 승인 없음. 원본/참고 저장소 쓰기 없음. 재시도·패치 없이 Sol/high에 승격.
- 다음 한 가지: Sol/high가 보존 ready before/after·control crop와 production reader/input 결선을 독립 대조하여 실제 click 전달과 관측 계약의 원인을 분류하고, 필요 시 정확한 version/old bytes/원복 조건을 포함한 최소 work repair를 정한다. 새 게임 run은 그 판정 전 금지.

## 증거 경로

- manifest: `local/runtime/20260911_033834_765190_0/manifest.json`
- verdict: `local/runtime/20260911_033834_765190_0/output/g1_a/verdict.json`
- aggregate: `local/runtime/20260911_033834_765190_0/output/g1_baseline.json`
- inputs: `local/runtime/20260911_033834_765190_0/output/g1_a/inputs.jsonl`
- log: `local/runtime/20260911_033834_765190_0/output/g1-baseline.log`

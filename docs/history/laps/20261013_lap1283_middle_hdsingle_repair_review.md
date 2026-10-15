# 2026-10-13 | lap1283 | H-HDSINGLE fresh middle 수리 독립 검수

- 지정 역할: middle(진단·독립 확인). MODEL_ROUTING 현재 선택 Codex sol/high; App의 실제 resolved ID/effort는 노출되지 않아 추측하지 않는다. bounded native verifier 호출은 `verifier`, requested `gpt-6.1-sol`/high, fresh fork; provider/model 폴백 없음.
- ①~②: PROMPT 먼저 읽음 → AGENTS/최신 INBOX/APPROVALS 반려·미결 → STATUS 전체 → DESIGN 1~4/MODEL_ROUTING → lap1280/1281/1282 및 관련 주소 근거. 최신 DESIGN/INBOX가 PROMPT의 과거 G2/G4 수치보다 우선한다. runtime lap1283은 읽기만 했고 STOP 없음; 기존 ESCALATE_SOL은 lap1282 middle 역할 인계다.
- ③~④ 가설/종료 조건: writer의 합법 FE-run 분할이 그림·마스크·프레임 순서/offset·raw 구분을 보존하고, 새 후보/기존 실행 증거가 일치하면 수리 범위 기술 수용. 실질 충돌 또는 전달 경계는 근거와 ESCALATE_SOL로 root에 인계한다. 직접 게임/하네스 구현·후보 수정 없음.
- HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`; 기록 전 validation fingerprint `1d9b3d101a47bedb4ff26f80df046a6dede53e9c`, implementation fingerprint `688b6c39fe0bb8e20cd13d7907e33bc2a1a1558a`. 기록 추가가 validation fingerprint에 포함되는 점은 숨기지 않으며, 현재 기술 근거는 source 파일 SHA 대조로 범위를 확인한다. lap569 source mismatch 전체검사는 미사용.

## 독립 수리 확인 — PASS(scoped)

- writer `_avoid_spr_raw_collision`은 RLE 길이가 sheet area와 같을 때 `FE n (n>1)`을 `FE 1 FE (n-1)`로 바꾼다. 합법적 동일 투명 run, 길이 +2; `_encode_spr_native`는 변경 stream 길이로 뒤 프레임 offset을 다시 계산한다. sheet writer도 동일 분기를 사용하고 genuine raw branch는 그대로다. 분할할 run이 없으면 `ConvertError`로 거부한다.
- 독립 스크립트 `../temp/Syw2plus_patch/20261013_lap1283_middle_hdsingle/independent_native_review.py`는 기존 writer 검증 스크립트를 실행/수정하지 않고 raw부터 대조했다. lap1280 기존782개 파일 SHA/길이 모두 일치 → 새 후보도782개/187,750,678B, 변경3·불변779. 이전 후보·소스/팩/raw 보존.
- 이전 후보의 **11프레임/18,872px mask FAIL** 재현; 수리 후보 **61프레임 전체 mask 차이0**, 이전 payload를 강제 RLE로 해석한 결과와 새 후보의 mask/opaque indexed pixel 차이0. 같은 version/순서/count·원본2배 차원·payload 실제 길이·프레임 offset·exact decode 확인. 전체39,814프레임을 새로 재검사했다는 주장이 아니며 불변779개는 lap1280 동일 SHA 근거를 재사용한다.
- FOG01: 30프레임, payload368640→368642, raw area368640, 후보SHA `38ff2690d17e076d8639f69ea7d80f36c2f9d9bc1e5458c0fd543eae1446599c`.
- FOG11: 30프레임, payload368640→368642, raw area368640, 후보SHA `5a4f440fbd9b67ed65547c3012834b767b48e0c19f303a34f74ec31a82653e19`.
- itembox_gray_line: 1프레임, payload36960→36962, raw area36960, 후보SHA `34d98651a47460a3e1872f434687553806c1e2dd47b5f35ed16c637e2511e5ee`.
- 원본 세 asset SHA는 lap1280/1281과 동일. 독립 audit JSON SHA `bd2c44d68eebc443e791cd9a2b309c514d2d2654d0e1ead45fe9f8f6d38f7ad0`; 전체 후보 inventory digest `e5c00d4edf16f76126d678f24280e9e520f01d68a1a0d8445ed455936b790c49`(JSON inventory의 SHA256; 단일 파일 SHA가 아님).

## ④·⑥ 관련 검사 / 실행 근거

- `make doctor` setup/original SHA PASS(`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`); default runtime manifest 부재는 그대로 공개하며 새 실행 PASS로 쓰지 않는다.
- `.venv/bin/python -m pytest -q tests/test_g1_hd_convert.py tests/test_g1_hd_extract.py tests/test_g1_hd_pack.py tests/test_g1_hd_native_reader.py` → **150 passed/31.69s**, skip0. MinGW i686/Wine의 synthetic C reader collision-sheet/BMP/truncation 대조 포함; 실제61개 asset 전부를 C로 새 실행했다는 뜻은 아니다.
- `make lint`·`make typecheck` PASS. native raw audit PASS. 로그 `logs/gates/lap1283-middle-{doctor,targeted,lint,typecheck,native-review}.log`.
- lap1281 source3개 SHA MATCH; lap1280 대비 C/DLL source·extractor·실행 하네스 불변을 source snapshot으로 확인. middle 시작/종료 소스 대조는 별도 evidence에 기록한다. unchanged DLL의 lap1280 독립 재조립/정규화 일치 근거 재사용, 이번 DLL 재빌드 없음.
- **PASS(scoped runtime 재검수):** lap1281 official2613/G2G6G8/G2G6G8G9 각각 new-game/save006 off/on 총12lane의 result SHA·EXE/후보 설치 경로·owned close·summary1/detach complete/flush complete/drop0·cleanup true 확인. game/prefix 경로는12개씩 고유하고 game사본12개 모두 없음·prefix process 기록 empty·현재 해당lap 실행 process0. 후보6lane은 repaired_r1/782파일/187,750,678B, 기준6lane은 sidecar 없음. asset stream7,541records·엔진 직접 `_hd.*` opens0; capture36/36 SHA/차원 MATCH. 기존 실제 Wine 증거의 독립 대조이며 이번 새 게임 실행이 아니다.
- 후보 PS3 `mirror2x_present`는 official266/4·V8266/4·V89266/4(new-game/save006). raw stale/fallback/viewport restore failure/viewport field mutation/clip replay/palette/key mismatch max 모두0. `independent-ps3-safety.json`에 lane별 raw SHA·계수를 보존했다. 실제 key hit/reject rows는 official66/0·77/0, V879/1·77/0, V8973/1·77/0; 알려진 reject1 원인UNKNOWN은 유지하며 `shade_hit/lut_hit`를 reject로 세지 않는다.
- **검수기 가정 정정(raw 보존):** 보조 verifier의 `runtime_review/lap1281_runtime_metrics_audit.json`은 JSON 재직렬화+종료후 summary까지의 해시를 종료전 owned SHA와 비교해 0/6으로 보고했다. 원시 바이트를 다시 계산하면 **12/12 owned SHA가 정확히 같은 final raw의 종료전 prefix와 일치**하고 final SHA도12/12 MATCH. 후보 prefix line official2180/1288·V82260/1301·V892260/1301. 보존된 `lap1280_middle_hdsingle/dll_build/_G1MM.dll`의 실제 SHA도 `6dc88f98110975acc443c29d38eb738289c11df2d68165e0b98e2545edc49b7d` MATCH; 저장소의 다른 DLL을 비교한 것을 동일 후보 충돌로 쓰지 않는다. 최초 reviewer artifact는 수정/삭제하지 않고 `independent-prefix-dll-audit.json`에 raw prefix byte 수/최종 SHA·실제 DLL 경로·정정을 따로 보존한다. 재현은 해당 raw의 `read_bytes()[:matching_raw_prefix.bytes]` SHA256 계산이다. 따라서 새 제품/raw 충돌은 없으며 추가 work 수리는 필요 없다.
- 전체 `make check`/새 게임 실행/Windows/전달/마일스톤 승인 **SKIP**. 최신19:31 규칙에 따라 전달 후보 고정 후 root가 같은 source 전체검사1회 담당. 기존 full-test-latest(lap569) exit0은 현재 source 근거가 아니다.

## ⑤ 종료 기록 / 다음 한 가지

- 변경 책임은 이 lap기록·STATUS/INBOX의 최신 판정·ESCALATE_SOL과 이전 인계 원문 보존에 한정한다. 원본/참고/raw/안전핀/기존 미커밋 소스는 수정하지 않고 커밋/게시/deploy/전달도 수행하지 않는다.
- mirror validator BLOCKED·tree_plus reject1 원인UNKNOWN·Windows/DxWnd/BGM·사용자 화질/G1 미완료 및 과거 FAIL/미결 승인은 보존한다. display-only 검수는 G2 pool/8인/G9 자리행동 합격이 아니다.
- 전달/마일스톤 경계에서 root로 ESCALATE_SOL 인계하며 직접 다음 마일스톤으로 넘어가지 않는다. 추가 work-tier 수정은 새 기술 결함이 발견된 경우에만 명시적 handoff로 배정한다.
- **종료 판정: PASS(scoped 수리 기술 수용), 전달/마일스톤은 root 인계.** 현재 전달 후보 고정/전체gate는 수행하지 않았다. 이전 인계 전문 `docs/history/laps/20261013_lap1283_preserved_lap1282_escalate_sol.md`는 byte-exact/SHA `60642accd3e6a77f71a9aab5cfa0b58d22afc5b14169b5c2f52c82e499088d03` 유지. 후보는 이전 payload minimal re-encode이며 원 source pack 부재로 전체 재생성하지 않았다는 lap1281 한계도 보존한다; 독립61프레임 대조는 기존 authored opaque pixels 보존을 확인한다.
- 최종 기록 후 `checks/context_limits.py` CONTEXT_PASS·`checks/safety.py --require-game` SAFETY_PASS·`git diff --check` PASS. STATUS42/INBOX341/APPROVALS64줄(각130/350/250 이하), Blockers 정확히1개. source74파일 SHA 및 implementation fingerprint 불변 확인; 문서 수정에 따른 final validation fingerprint/최종파일SHA는 공유 evidence `final-session-check.json`에 보존한다. 새 PNG/game/prefix 생성0·기존 game/raw 삭제0·FULL_TEST/STOP 생성0·커밋0.

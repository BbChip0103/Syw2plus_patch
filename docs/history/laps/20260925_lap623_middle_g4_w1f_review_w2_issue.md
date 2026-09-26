# 2026-09-25 | lap 623 | 목표 G4 W1F 독립 검수 / W2 발행

- 실제 provider/model/effort / 지정 역할: Codex native session / 정확한 model ID·effort 비노출 / middle(진단·계획·확인), 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap622 보존 raw와 provenance가 W1 §4 `FEASIBLE_BASELINE`을 summary 없이 재현하며, 성공 load call 경계와 기존 AI shadow를 결합하면 §6 exact marker/first-edge를 read-only 계측으로 닫을 수 있다.
- 예상 PASS / FAIL 조건: raw hash·identity·180 PS3 samples/tick span·AI 이동·512 shadow mode/owner/ECX/reentry/rewind/forward·cleanup이 모두 일치해야 W1F ACCEPT. 하나라도 불일치하면 변경 보존 후 승격하고 W2를 발행하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품/하네스 source·binary·EXE·save·raw 변경 0; 문서 `docs/work/active/G4_W2_EXACT_POSTLOAD_MARKER_LAP623.md`, 이 기록, STATUS/INBOX/ESCALATE만 갱신; pre-Fast validation fingerprint `c8cf2cd35449f0f1fb9bcd382cc3d44821206243`; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본·private EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; bridge `39cc2603fc014c5813fd61898f59cd39ba517ed923c77f3a9638c0791c690c4f`; lap622 fresh private prefix/Xvfb `:91`, default two-player random, synthetic/control/resource/save/load/candidate 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `jq`로 `output/g1_baseline.json`·`inmm_ai_shadow.jsonl`·provenance를 직접 집계하고 `sha256sum`/원본·private·bridge·source 대조. 보존 경로 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g4_ai/20260925_172030_lap622_g4_w1f_fresh/`; manifest `789f76b0…72ef8`, baseline `efffe3d1…2528`, provenance `198710b2…8b16`, verdict `1530795a…8934`, shadow `cddf839f…f17a`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 180 samples, PS `{3}`, tick `11→5980` span5969/rewind0, 동일 AI 이동 identity10; shadow512행/tick1..512 unique512/AI448, owner·ECX·match·forward·reentry·rewind 오류 전부0, mode 유일값 `(3,1,0,0,0,0,0)`, postload=`UNOBSERVED`; provenance env/path/SHA/row-count PASS, cleanup PASS. **`ACCEPT / FEASIBLE_BASELINE`**. 전체 G1 tail `FAIL_NO_EFFECT`는 별도 유지.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: G4 제품 AI 개선/PASS·post-load·비지원 mode 음성·사용자 승인 아님. source 변경 없음. 목표 관련 Fast와 final `make check` 결과는 이 기록에 후속 반영한다.
- 다음 한 가지: work tier가 `G4_W2_EXACT_POSTLOAD_MARKER_LAP623.md`만 구현·검증하고, gate PASS일 때 pinned save000 fresh foreground를 정확히 1회 실행한다. 실패 시 재시도 없이 승격한다.

# 2026-10-02 | lap861 | G1 W70 P4 입력·전환 검수 — HOLD / 승격 인계

- 실제 provider/model/effort / 지정 역할: Codex API/native 세션, 정확한 model ID·effort 비노출. 사용자 지정 middle(진단·계획·확인), Sol/Opus 호출·모델 변경을 주장하지 않는다. 게임/하네스/테스트 구현 수정0, 빌드0, Wine 실행0, 커밋0.
- 목표 / 가설: lap860의 DOWN parity 충돌과 B-5 표본창 문제를 독립 확인하고, 수리 가능한 하네스 결함과 아직 입증되지 않은 제품 원인을 구분한다. 이전 대화 대신 PROMPT→AGENTS·INBOX·APPROVALS→STATUS→DESIGN1~4→P4 카드·lap860·직접 source/raw를 읽었다.
- 예상 PASS / FAIL: 동일 DOWN 입력 수신과 카메라 전환을 확인한 뒤의 30 present만 B-5 근거로 수용한다. 현재 raw로 원인을 설명할 수 없는 입력 불일치가 유지되면 사용자 stop 조건에 따라 보존·ESCALATE 후 종료한다. P4/P5 전환이나 G1 마일스톤 수용은 하지 않는다.
- 변경 파일: 이 기록, `docs/history/20261002_lap861_prior_lap860_escalate_sol_archive.md`, `loop/ESCALATE_SOL`, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`. uncommitted. lap counter는861 읽기만.
- 원본 / 후보 / fixture: fresh doctor가 보호 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 확인. 과거 pair의 save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`는 이전 기록 인용, 이번 fixture 파일 재해시는 하지 않음. 558 unit/8 player records는 활성8인 부하 증명이 아님. 후보 EXE/DLL 신규 생성 없음, DLL 전체 build-input 재검수 SKIP. source/test9개 SHA는 lap860 review와 직접 재계산해 전부 일치.
- 명령: `make doctor`; Python stdlib로 pair/raw/source9개 SHA·PS3 present 배열·coverage를 독립 재계산. 로그/캡처 신규 생성 없음. 재계산 JSON은 아래 공유 temp에 보존. 종료 문서검사는 STATUS에 결과를 기록한다.

## 독립 확인 결과

- Evidence / 높은 확신: DOWN baseline `[158,101]→[159,102]`, candidate `[158,101]` 불변; RIGHT candidate `[158,101]→[160,99]`. pair SHA `feaa61f1a47908838ce40b91c1e4e9ad33fdd2b7d3584de4527ff57905e4ad90`, raw SHA `8e0e06cbddfdd48e53a1769f529e4edc90225b553c3bd847bd4718f2d6970ede` 모두 lap860과 일치. 공통 save006 제한으로 DOWN을 면제할 수 없다.
- Evidence / 높은 확신: PS3 `mirror2x_present`1919개. 저장된 coverage30개는 인덱스21, seq1587~1616에 유일하게 대응한다. median57,136/480,000=11.9033%, 다음30 median47,778.5=9.9539%, 두 창 outside diff 최대0. 표본 숫자 자체는 재현되지만 이동 뒤의 정확한 구간이라는 주장은 입증되지 않음.
- Evidence / 높은 확신: `tools/g1_saved_scene_probe.py:706~724`는 입력 전 trace line cursor를 저장하고 키 주입→0.5초 대기→카메라 변화를 확인한다. `_terrain_scroll_coverage`(:169~210)는 그 cursor 이후 모든 PS3 present를 모으며 카메라 전환을 판별하지 않는다. 해당 raw30개에 camera 필드0. **입력 전 cursor를 이동 후 barrier로 쓰는 하네스 결함은 확정**, 첫 threshold present1은 회복 증거로 수용 불가.
- Evidence: `_send_key`(:132~139)는 전용 display에 XTest helper를 실행한다. `tools/x11_send_keys.py`는 기본 hold30ms·interval120ms, 호출은 repeat2이며 수신 게임의 ack/foreground 관측을 남기지 않는다. helper SHA `d6188bf547b3a167cf37f6a448cc86eae9f3023994af0bd6b86ede3405f463d7`. 프로세스 성공은 게임 키 수신 증거가 아니다.
- Inference / 중간 확신: 키 수신·포커스·관측 타이밍 문제를 후보 제품 회귀보다 먼저 구분해야 한다. 짧은 hold가 원인이라는 단정은 불가; timing/focus hypothesis는 fresh receiver 관측이 필요하다.
- Unknown: DOWN 미수신/지연과 후보 회귀 중 원인, 정확한 stale writer와 renderer buffer→present source 연결. `g1_mirror2x.c:551~565`의 mismatch mask 제거와 :473~478의 hook 합성 시 mask 설정은 정적 확인했으나 별도 writer 존재·주소를 입증하지 않았다. 새 writer hook을 승인하지 않는다.

## 명시적 work tier handoff / 승격 검수 조건

1. 승격 검수자는 입력/전환 계측을 수리 범위로 확정하고 **다음 work(Luna/Sonnet)에서 즉시 구현·private fresh pair**하도록 넘긴다. 재요약만 하는 세 번째 회차는 금지(PROMPT③). 이 일반 middle은 미설명 충돌을 자체 해소했다고 주장하지 않는다.
2. work 단일 작성자 범위: `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`; 필요한 opt-in receiver/present 계측만 `tools/inmm_stub/direct_draw_trace.c`에 한정한다. 공용 XTest helper·원본 게임 로직은 변경하지 않는다. 기존 trace/validator 계약을 보존하고 camera·sim tick·present seq 및 foreground/입력 전달 관측을 추가한다. renderer/source 연결은 최소 계측으로 확인하고 새 writer 구현은 증거 확보 전 금지.
3. DOWN 동일 계약으로 양 lane의 실제 수신·카메라 이동을 확인한다. timing 결함이면 probe에 hold 옵션을 명시하고 양쪽 동일 적용, 반환코드만 PASS로 세지 않는다. RIGHT fallback은 별도 진단으로 보존하며 DOWN PASS 대체 금지. 현0.5초 sleep 뒤부터 표본을 자르는 방식도 첫 이동 이후 프레임을 빠뜨리므로 수리안으로 불충분하다.
4. 회귀는 지연 입력 전에 threshold 이상 프레임이 있는 경우·카메라가 전혀 안 변한 경우·실제 전환 이후30개만 선택하는 경우를 다룬다. raw present와 같은 시점에 읽은 camera로 전환 seq를 식별하고 전환 구간 및 이후30 present를 보존한다. barrier 이후 coverage≥264,000·outside diff0·Scale2x validator 무수정·scene/source/cleanup PASS를 확인한다. 기존 B-5 판정/임계값은 완화하지 않는다.
5. barrier가 고정된 fresh pair에서 stale가 남으면 정확한 writer/destination/source/좌표를 좁혀 기존5 hook 내부 결함인지 판정한다. 추적 가능한 결함은 work가 수정→빌드→fresh 재실행 반복. 별도 writer 필요 시 주소·old bytes·destination 근거를 승격 검수자에게 먼저 제시한다. B 통과 전 C fresh3 pair·P5 금지.

## 보존 / 검증 한계

- PASS: fresh doctor(원본 SHA 일치, optional runtime manifest 부재), pair/raw/source9개 SHA와 coverage 독립 재계산. 새로운 게임 runtime/24k/144k 증명은0.
- 재계산: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap861_middle_p4_confirmation/review.json`, SHA `592f2dc3dba9d993049accd2fa9099ce6831a3577b2a83037b1ed4062b89d53e`.
- 직전 ESCALATE 전문 보존 SHA `e308355a8aaacf6fffd2c48236e2529441178afeac0a085bce8beaba3baa41af`; 기존 raw는 덮어쓰지 않았다.
- SKIP: fresh Wine, DLL build, lint/typecheck/full make check, patch 생성/원복·byte 검사. 사용자 근거 충돌 시 보존·승격·종료 지시가 PROMPT⑥ 및 patch-validation 일반 검사 순서보다 우선이다. 이전 full-test는 source_match=no이며 이번 PASS로 쓰지 않는다. 변경은 문서뿐이며 빠른 문서/안전 확인 결과는 STATUS에만 덧붙인다.
- 다음 행동/현재 큐는 STATUS만 따른다. G1/P4 HOLD, 사용자 승인 없음. 원본/참고/G2/G5 쓰기0. 기존 미커밋 파일 보존.

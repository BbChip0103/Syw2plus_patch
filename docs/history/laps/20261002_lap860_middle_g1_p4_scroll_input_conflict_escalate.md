# 2026-10-02 | lap860 | G1 W70 P4 independent middle review — HOLD / escalate

- 실제 provider/model/effort / 지정 역할: 현재 Codex API/native 세션, 정확한 model ID·effort 비노출; 사용자 지정 middle(진단·계획·확인). Sol/Opus로 모델을 변경하거나 별도 모델 호출을 했다고 주장하지 않는다. 게임 hands-on 수정·빌드·새 Wine 실행·커밋 0.
- 가설 / 검수 대상: lap859의 B-5 실패가 입력 하네스나 현 5 hook 내부 결함으로 설명되는지 확인한다. P4 카드 §4 B-5는 실제 카메라 이동 뒤 30 present 안에 coverage ≥264,000 및 outside diff0을 요구한다. G1 마일스톤·C gate 통과를 선언하지 않는다.
- 예상 PASS / FAIL: 동일 DOWN 입력의 baseline/candidate 이동을 대조하고 raw에서 실제 이동 후 회복을 증명해야 한다. 근거 충돌·불명확한 구현 근거는 최신 사용자 stop 규칙에 따라 즉시 ESCALATE한다. W70 P단계 자체는 마일스톤 경계가 아니다(lap858 판정 수용).
- 변경 파일: 이 기록, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, `loop/ESCALATE_SOL`, 직전 ESCALATE 원문 보존본 `docs/history/20261002_lap860_prior_lap859_escalate_sol_archive.md`. 원문 SHA256 `091283f4f4b158befb6d41bbe1a6203cc60914e5cbfb72ddbac6d0cb78f32a68`. 기존 work source/test 9개는 STATUS의 SHA와 전부 일치하며 수정하지 않았다. uncommitted, commit0.
- 입력 / 환경 / fixture: 보호 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`를 fresh `make doctor`로 확인. 직전 private Wine/Xvfb pair의 save006 비합성 fixture SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`. 8 player/558 unit records는 활성8인 부하 증명이 아니다. DLL/build 입력 전체 독립 대조는 중단 조건 도달로 SKIP; source 9개 대조만 완료.
- 명령 / 증거: `cat loop/PROMPT.md` 후 AGENTS→INBOX·APPROVALS→STATUS→DESIGN1~4→P4 카드·memory map·lap859 기록·ESCALATE 순으로 읽었다. `make doctor` PASS(original verified, optional runtime manifest absent). Python stdlib로 pair/raw SHA·PS3 present 및 coverage/counter를 독립 재계산했다. 새 raw·캡처를 만들지 않았다.
- 재계산 산출물: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap860_middle_p4_review/review.json`, SHA256 `1bef2ccc278312ad2282ea1c076e9c84bc02d0a966c5fc0b18e471bd0f469684`. 소스9개 SHA, 원본/후보 입력 관측, raw창 seq별 counter, 이전 pair 수치와 인용 여부를 분리해 보존했다.

## 확인한 사실과 중단 사유

1. R4 pair SHA `3e3417be17c0ea56ea6e9061648daff146652e06a83a6a718d6217f415a137a0`, candidate raw SHA `e72cc760b27f8956bfdd94368bde9cc93e0258b1870032d0a9e5a2a2ee1aa1af`(PS3 present889)은 pair의 raw SHA와 일치한다. 직전 고정 창 coverage66.53%·ratio1.00000186·p95+5ms는 **이전 주장 인용**이며 이 회차에서 고정 창 전체를 다시 검수하지 않았다. 새 source 검증 또는 runtime PASS로 승격하지 않는다.
2. DOWN-first pair SHA `feaa61f1a47908838ce40b91c1e4e9ad33fdd2b7d3584de4527ff57905e4ad90`, candidate raw SHA `8e0e06cbddfdd48e53a1769f529e4edc90225b553c3bd847bd4718f2d6970ede`(PS3 present1919)은 기록과 일치한다. **baseline DOWN은 `[158,101]→[159,102]`로 이동, candidate DOWN은 `[158,101]→[158,101]` 불변**이다. 따라서 “save006에서 DOWN이 움직이지 않아 RIGHT 대체”라는 공통 환경 해석은 근거가 없다. 후보 회귀인지 입력 전달/관측 타이밍인지 원인은 미확정이다. 사용자 stop 조건의 불명확·충돌 근거로 승격하며 임의 입력 예외·C gate를 허용하지 않는다.
3. candidate RIGHT fallback은 `[158,101]→[160,99]`. 저장된 30개 coverage 배열이 raw PS3 인덱스21~50(seq1587~1616)과 유일하게 일치하며 median **57,136(11.9033%)**, 다음30 median **47,778.5(9.9539%)**다. `outside_diff`는 해당 표본에서0. B-5 회복 증거는 FAIL/HOLD다.
4. `tools/g1_saved_scene_probe.py:706`은 키 전 line count를 취하고 `:708`의 입력 뒤 camera를 관측한다. 따라서 첫 표본318,138과 `first_threshold_present=1`은 **이동 후 회복 시점으로 인증할 수 없다**(raw에 camera-transition barrier 없음). 첫 표본이 실제 이동 전인지도 확정하지 않는다. median은 재계산과 일치하지만 잘못된 시점의 recovery PASS로 쓰면 안 된다.
5. raw seq1587→1588에서 covered335,892→318,369, stale17,754→214,852로 급증하며 terrain calls는 `[376,29,0,163,233]`으로 동일하다. seq1590에서 calls `[406,29,0,201,259]`, 유효57,326이며 seq1616·1646까지 terrain calls가 동일하다. **scroll 중 hook 재호출은 있었다**(기존5종이 전혀 호출되지 않았다는 결론 금지). 이후 hook 없는 present에서 mask 복구가 없음을 확인했다.
6. `g1_mirror2x.c:551~565`는 expected snapshot과 최종 source가 다르면 `g_covered[p]=0`; `:473~475`는 hook의 replay/composite에서만 covered를 재설정한다. unhooked writer/cached-surface copy 또는 지형 버퍼와 present source 간 좌표·합성 차이는 후보 원인이나 **정확한 writer는 입증되지 않았다**. 이 원인으로 구조적 BLOCKED·새 hook 범위를 자동 승인하지 않는다.

## 승격 검수와 명시적 work handoff

- 승격 middle/Sol: 동일 DOWN 입력 불일치의 원인과 입력 parity 수리 범위를 판정한다. baseline이 움직이므로 DOWN 고정 요구를 환경 예외로 없애지 않는다. 실제 카메라 전환을 raw present와 묶는 최소 하네스 수리 조건을 먼저 정한다.
- 그 판정에 따른 work tier(Luna/Sonnet): private 동일 fixture에서 입력 전/후 camera·실제 전환 시점·source surface/renderer를 계측해 재현한다. 추적 가능한 하네스 결함이면 즉시 수리→재실행하며 §③ 반복 원칙을 따른다. 현재 중간 세션은 게임 구현을 하지 않는다.
- stale 수리 work 범위는 정확한 writer/복사 경로를 확인한 뒤 정한다. 기존5 hook의 mask 좌표/합성 결함이면 그 안에서 수리한다. 새 `0x466280` 등 writer가 필요하면 주소/old bytes·destination 근거와 범위를 승격 검수자에게 제시한 뒤 명시 handoff로 넘긴다. 무조건 stale flag를 지우거나 nearest 픽셀을 HD로 세지 않는다.
- 수리 후 fresh B pair: 원본/후보 동일 입력에서 카메라 이동을 증명, 실제 전환 뒤30 present coverage≥264,000·outside diff0·Scale2x validator 무수정·scene/source/cleanup PASS. B 전부 PASS 전 C fresh3 pair 금지. G1 사용자 제출·P5·새 목표 전환 없음.

## 검사 / 한계 / 종료

- PASS: 새 `make doctor`, 위 SHA·raw 배열/counter 독립 재계산, source9개 SHA 일치. 직전 fast log `logs/gates/lap858-work-p4-fast-r3.log`의 마지막 mypy/CONTEXT_PASS를 읽었으나 현재 fingerprint의 통과가 아니다.
- SKIP: fresh runtime, DLL 재빌드, 전체 validator 재실행, focused pytest, `make lint`/`make typecheck`/`make check`. 근거 충돌을 발견하면 보존·ESCALATE 후 종료하라는 **이번 사용자 지시가 PROMPT⑥/patch-validation의 일반 Fast 실행 순서보다 우선**한다. 13분 전체 검사를 시작하거나 과거exit0으로 대체하지 않는다. 문서 보존 확인은 STATUS에 기록한다.
- 다음 한 가지: `loop/ESCALATE_SOL`의 DOWN parity 및 정확한 stale writer/transition 판정을 승격 작업자가 수행하고 work tier 수리 범위를 명시한다. P4 HOLD/G1 HOLD 유지. lap counter860 읽기만; 원본·참고·G2/G5 파일에 쓰기0.

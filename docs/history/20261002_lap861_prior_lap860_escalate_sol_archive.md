# lap860 middle → 승격 Sol: G1 W70 P4 HOLD, 입력 근거 충돌

사용자 stop 조건(불명확하거나 충돌하는 구현 근거)으로 종료한다.
게임 구현·하네스 수정·빌드·새 Wine 실행0, 커밋0. P4/P5 전환·G1 승인 없음.
직전 요청 전문은 docs/history/20261002_lap860_prior_lap859_escalate_sol_archive.md에 보존:
SHA256 091283f4f4b158befb6d41bbe1a6203cc60914e5cbfb72ddbac6d0cb78f32a68.

## 독립 확인한 충돌 / raw

- DOWN-first pair baseline DOWN: [158,101]→[159,102] 이동. candidate DOWN: [158,101] 불변.
  save006 공통 입력 제한으로 설명하거나 DOWN 요구를 RIGHT로 대체해 PASS할 근거가 없다.
  후보 입력 회귀/하네스 전달·관측 타이밍 중 원인은 미확정.
- candidate RIGHT: [158,101]→[160,99]. 저장된30 coverage 배열은 PS3 seq1587~1616과
  유일하게 일치, median57,136/480,000=11.9033%, 다음30 median47,778.5=9.9539%.
- 키 입력 전 raw line count부터 샘플링한다(g1_saved_scene_probe.py:706~724).
  첫318,138 및 first_threshold_present=1은 실제 이동 후 회복 증거로 인증할 수 없다.
  raw에 camera-transition barrier가 없고 첫 표본의 정확한 이동 전/후 귀속도 미확정이다.
- seq1587→1588 stale17,754→214,852, terrain calls[376,29,0,163,233] 동일.
  seq1590에서 calls[406,29,0,201,259]로 증가 후 seq1646까지 동일; 5 hook 재호출은
  실제 있었고 이후 present에서 재작성/회복이 없다. hook 전혀 미호출이라는 설명 금지.
- g1_mirror2x.c:551~565는 expected snapshot 불일치 시 covered mask를 내리고
  :473~475는 hook 합성 때만 mask를 다시 설정한다. 정확한 후속 writer/좌표·복사 경로는
  입증되지 않았다. cached-surface/block_copy는 가설이며 자동 범위 확대 근거가 아니다.

Pair: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap858_p4_scroll_down_r1/pair-result.json
Pair SHA feaa61f1a47908838ce40b91c1e4e9ad33fdd2b7d3584de4527ff57905e4ad90
Raw: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap858_p4_scroll_down_r1/candidate/trace_raw.jsonl
Raw SHA 8e0e06cbddfdd48e53a1769f529e4edc90225b553c3bd847bd4718f2d6970ede
Recalculation: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap860_middle_p4_review/review.json
SHA 1bef2ccc278312ad2282ea1c076e9c84bc02d0a966c5fc0b18e471bd0f469684

## 승격 검수자가 이어서 할 것 / 명시 work handoff

1. DOWN 원본/후보 입력 parity 원인을 판정하고 work(Luna/Sonnet) 최소 계측·수리 범위를 정한다.
   private same-save에서 입력 전달·camera 실제 전환과 present barrier를 묶어 검증한다.
2. stale를 만드는 정확한 writer/renderer buffer와 present source의 연결을 확인한다.
   현재5 hook 내부 mask·좌표 결함이면 work가 그 범위에서 수리→빌드→fresh pair 반복.
   별도 writer hook이 필요하면 주소/old bytes·destination 근거를 확인해 범위를 명시한다.
   단순 stale 제거/nearest를 HD로 세기/validator·임계값 완화 금지.
3. fresh B: 같은 입력으로 baseline/candidate 이동, 실제 전환 뒤30 present coverage≥264,000,
   outside diff0·Scale2x validator 무수정·scene/source/cleanup PASS. 그 전 C fresh3 pair 금지.
   추적 가능한 결함은 work가 원인 추적→수정→재실행 반복하며 재계획만 반복하지 않는다.

## 검증 한계

fresh make doctor PASS(보호 EXE SHA 일치), source/test9개 SHA는 lap859와 일치.
새 full Fast/runtime/DLL-build/focused-tests/validator 재실행 SKIP: 사용자 근거 충돌 stop 우선.
직전 full check exit0과 고정 장면 gate는 현재 source fingerprint/scroll gate 승인으로 쓰지 않는다.
기록: docs/history/laps/20261002_lap860_middle_g1_p4_scroll_input_conflict_escalate.md.

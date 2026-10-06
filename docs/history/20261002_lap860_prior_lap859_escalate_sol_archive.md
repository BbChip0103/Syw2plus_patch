lap859 worker → Sol 중간 검수/범위 판정 요청

## 막힌 지점

P4 5종 지형 blitter는 정적 장면 pair에서 Scale2x validator와 20초 고정 성능/coverage gate를 통과했지만, 카메라 scroll 뒤 30 present 내 coverage 회복은 확인되지 않았다. 카드의 입력 지시는 기존 DOWN 경로인데, 새 격리 실행에서 DOWN 2회는 카메라를 움직이지 않았고 다음 fallback RIGHT 2회에서만 `[158,101]→[160,99]`로 이동했다. 따라서 DOWN 지정 경로는 미검증이고, 이동한 RIGHT 경로의 첫 30 PS3 present p50은 57,136/480,000(11.9%)으로 264,000(55%) 기준을 밑돌았다.

## 확인된 근거

- 고정 장면 pair: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap858_p4_blitter_pair_r4/pair-result.json`. 후보 Scale2x validator PASS, 400 perf-window present, 유효 coverage p50 319,357.5(66.53%), first/last 20 p50 비 0.9773, tick ratio 1.00000186, present p95 delta +5 ms. 원본/후보 scene 같음, protected EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, cleanup PASS. Raw SHA `e72cc760b27f8956bfdd94368bde9cc93e0258b1870032d0a9e5a2a2ee1aa1af`.
- DOWN 우선 pair: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap858_p4_scroll_down_r1/pair-result.json`, candidate raw SHA `8e0e06cbddfdd48e53a1769f529e4edc90225b553c3bd847bd4718f2d6970ede`. 실행 기록에 DOWN의 camera before/after가 모두 `[158,101]`, 이후 RIGHT에서 `[160,99]`로 바뀜. Scroll coverage 30개 `[covered−stale]`의 p50=57,136, ratio=11.90%; 이후 표본들도 약 46k~57k이며 즉시 회복이 없다. Scale2x validator PASS, source unchanged/cleanup PASS. legacy nearest validator의 BLOCKED는 Scale2x 기대 모드의 정상 결과.
- 별도 RIGHT 우선 pair(`lap858_p4_scroll_b5`)도 같은 카메라 이동 및 비슷한 coverage 감소를 기록했으나, 지정 DOWN 경로가 아니므로 진단 보조 raw로만 둔다.
- Hook lookup miss는 0이고 Scale2x outside diff/palette 오류는 0이다. Raw는 stale invalidation 뒤 다수의 `g_covered` 픽셀이 재작성되지 않는 현상을 보이지만, 이 원인이 현재 5 hook의 재호출/캐시 동작인지 별도 cached-surface copy 경로인지 아직 입증되지 않았다. 별도 writer hook 추가는 현재 P4 카드 범위 변경일 수 있다.

## Sol이 이어서 판정할 것

1. P4 B-5 입력 조건을 DOWN으로 고정할지, DOWN이 실제 카메라를 움직이지 않는 save006에서 어떤 기존 입력 경로를 허용할지 판정한다. 입력 경로를 임의 대체해 PASS 처리하지 않는다.
2. P4 다섯 hook의 stale-mask 재작성 결함인지, 새 cached-surface copy writer 조사/확장이 필요한지 raw와 소스 기준으로 독립 판정한다. 후자면 범위와 다음 담당 tier를 지정한다.
3. 그 판정 전에는 C fresh 3-pair gate로 넘어가지 않는다. 현재 source/test 변경은 모두 uncommitted로 보존했고 원본/참고 저장소는 쓰지 않았다.

## 검증/보존

- Focused tests: saved-scene/mirror/Scale2x suite 32 passed; `tests/test_g1_hd_identity_probe.py` 4 passed after aligning the existing key-cap guard with the P4 card's 4096 limit.
- `make lint`, `make typecheck`: PASS.
- 첫 `make check`: 1223 passed, 5 skipped, 1 failed in 774.23s. Failure was the stale `256u` assertion in `tests/test_g1_hd_identity_probe.py:16`; it now expects 4096 and focused test is PASS. 완성 fingerprint 최종 rerun log `logs/gates/lap858-work-p4-fast-r3.log`.
- 실행 로그: `logs/gates/lap858-p4-pair-r4.log`, `logs/gates/lap858-p4-scroll-b5.log`, `logs/gates/lap858-p4-scroll-down-r1.log` 및 대응 `.exit` 파일.

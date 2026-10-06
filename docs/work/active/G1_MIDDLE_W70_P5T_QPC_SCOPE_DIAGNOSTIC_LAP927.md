# G1 P5-T-R — lap926 비용 계측 범위 검수 / work 인계 (lap927 middle)

중간 tier, solo. renderer/probe/tests/validator 수정·새 runtime·커밋0.
lap925의 R1~R4 및 §6을 유지한다. 이 문서는 기술 진단 인계이며 제품/마일스톤 승인 아니다.
현재 실행 큐는 STATUS만 따른다.

## 1. 독립 판정

- **R1 `PASS(partial)`**: 두 pair의 build 입력48개/current MATCH, DLL/trace/snapshot SHA MATCH.
  raw sim tick 단조·경계 도달·표본 배열/seq/coverage MATCH, focused11 PASS.
  GREEN DOWN24/RIGHT26, 계측 진단28/28은 정확히 경계 안 표본이며 INCOMPLETE/HOLD가 맞다.
  각 pair baseline/candidate snapshot5개는 decode한 상태가 전필드 동일하다.
  snapshot payload 전체 바이트가 같다는 뜻은 아니다(비계약 필드까지 포함한 binary 비교는 false).
- **P5-T/G1 HOLD**: PT-c는 lap925 규범대로 전환 뒤 첫30 present의 `(last.ts_ms-first.ts_ms)/29`이다.
  GREEN DOWN74.758621/RIGHT65.344828ms, 계측 진단64.965517/63.827586ms 모두52.0ms 초과.
  lap926의71/61ms는 경계 안 interval의 중앙값이다. 두 측정식을 바꾸거나 서로 대체하지 않는다.
- **계측 범위 차이 확정, 병목 UNKNOWN**: 진단 경계 안 구간의 기존 QPC section 합은
  DOWN1.644956/RIGHT1.476389ms/present, coarse 재호출 합은28.925926/28.555556ms/present다.
  같은 실행·같은 양 끝 present의 누적 차분을 N-1로 나눴다. reset을 가로질러 합산하지 않았다.
  이는 서로 다른 범위의 측정이다. GetTickCount 분해능만으로 큰 차이를 설명하거나
  QPC1.5ms를 전체 재호출 비용이라고 간주할 근거가 없다.

## 2. 소스 근거 / 한계

- `tools/inmm_stub/g1_mirror2x.c:1170`~1373: coarse timer는 거의 전체 mirror_reinvoke를 감싼다.
  QPC는 scratch_clear, invoke_original, hash_lookup, bind_compare/copy, Scale2x, compose 등의 부분 구간이다.
- 같은 파일1226~1303: clipped identity miss의 **임시 HeapAlloc/HeapFree, full bytes zero/fill,
  written-mask 생성과 viewport/buffer 변경/복원**은 기존 section 밖이다. zero/fill은246~260의 volatile byte loop다.
  보통 경로의 mask 생성, auxiliary_digest 등도 밖이다. `bind_copy_alloc`은
  `g1_hd_asset.c:515` 함수 안의 별도 identity cache 할당/복사만 재며 caller의 임시 할당은 포함하지 않는다.
- `direct_draw_trace.c:1629`~1674: marker 첫 active present에서 reset한 뒤 cumulative section을 기록한다.
  이번 검산은 그 뒤 구간의 차분이라 첫 reset 누락이 원인이라고 보지 않는다.
  `g1_perf_sections.c:33`~57의 QPC는 env opt-in으로 활성화되며 marker는 emission/reset 범위다.
  marker 밖에서도 env가 켜진 비용 계측은 실행된다. 계측 실행은 acceptance 근거가 아니다.
- clip prep가 실제 지배 병목이라는 주장은 아직 **가설**이다. 기존 L1/L2 cache miss/mismatch 관찰과
  covered0을 보존한다. 미러를 끄거나 negative cache로 매 프레임 검증을 생략하는 수리는 승인하지 않는다.

## 3. 다음 work 한 가지 — 누락 구간을 포함한 짧은 실제 비용 진단

**D1: 기존 opt-in 진단을 확장하여 전체 재호출 QPC와 exclusive clip 준비 비용을 같은 실행에서 측정한다.**
새 장기 계획/census/새 clock 경계/목표 변경 없이 바로 최소 구현·빌드·격리 probe한다.

1. `g1_mirror2x.c`, 기존 `g1_perf_sections.{h,c}`, `direct_draw_trace.c`와 관련 테스트만 단일 writer로 수정.
   기존 env opt-in, marker emission/reset, frequency를 재사용한다. per-call 로그/flush는 추가하지 않는다.
   QPC whole timer는 coarse start/end와 같은 유효 재호출 범위를 덮고 정상 종료마다 count/total을 남긴다.
   whole 누계는 `tinted`, `tinted_clip`, `other`를 구분한다. early-return/실패가 count를 왜곡하지 않도록 한다.
2. **exclusive `clip_prepare`**: 임시 할당/free, zero/fill, mask 루프, viewport/buffer 준비·복원만 측정한다.
   기존 original_call·bind_compare·bind_copy·Scale2x·compose 호출 시간은 이 bucket에서 제외한다.
   bytes/count도 남긴다. whole은 포괄 합계라 exclusive sections에 더하지 않는다.
   범위가 겹치면 단위/출력에 명시하고 차분에서 두 번 빼지 않는다. opt-in off에서 로직/렌더/캐시 key는 동일해야 한다.
3. 기존 RED→수리 회귀로 off/on, 누적 count, reset, early exit, 중복계산 방지를 잠근다.
   focused/lint/typecheck/DLL build 후 save006·기존 schedule·같은 mirror 범위의 격리 diagnostic pair를 완주한다.
   original SHA/old bytes·새 사본/prefix/display·20GiB·완료 cleanup·유지보수 I/O 비중첩 규칙 그대로다.
4. 두 키 경계 안 first/last present의 count/whole QPC/clip_prepare/existing sections 차분을 N-1로 나누고,
   같은 범위 coarse/interval·상태 parity·covered/mismatch를 함께 남긴다.
   whole과 section residual로 **재호출 내부인가 외부인가**, 내부이면 **clip 준비인가 나머지인가**를 판정한다.
   QPC whole이 작으면 whole 밖 frame 시간(원본 simulation/present/trace I/O 등)은 UNKNOWN으로 분리한다.
   근거 없이 특정 외부 병목을 확정하거나 범위를 바꾸지 않는다.
5. 귀속되면 동일 work에서 그 구간의 최소 수리→**비계측** GREEN 반복으로 이어간다(PROMPT③).
   병목을 못 가르면 수치·완료 raw와 구체 residual을 middle에 넘긴다. 루프를 새 strategy/사용자 승인 대기로 바꾸지 않는다.
   계측1회는 진단 시작점이며 추적 가능한 결함의 수정·재실행을 막는 횟수 예산이 아니다.
6. PT-c≤52.0ms·경계 안30개·PT-d/V1/V2/s/q/Scale2x·snapshot/input parity를 같은 source에서
   비계측 GREEN→B′1→B′2→C1~C3로 확인한 뒤 새 middle에 인계한다. 과거 실패/UNKNOWN은 보존한다.
   tinted_clip covered0, stale, HD90%, input-effect, GDI/두 번째 장면, 최종 사용자 승인은 별도 미검증이다.

## 4. 증거 / 승격 처리

공유temp `20261004_lap927_middle_review/recalculate.py`와 `recalculation.json`(SHA256
`3a0ff9fcfa5f309f2fdae9a6bc410d3ef883fa2f31ee2df901c4e1852a617fb7`)에 입력182파일과 재계산을 보존했다.
lap926 ESCALATE 원문은 `docs/history/20261004_lap927_prior_lap926_escalate_sol_archive.md`에 byte-exact 보존한다.
08:17 operator 지시의 중간 검수는 이 범위 판정·work 진단 인계로 처리한다. 새로운 raw 충돌·필수 게이트 원인불명
3회 실패·마일스톤 경계가 없으므로 일반 비용 UNKNOWN만으로 재승격하지 않는다. **P5-T/G1 HOLD는 해제하지 않는다.**
최종 fresh 전체Fast와 불변 감사는 문서 확정 뒤 실행하여 STATUS에만 기록한다.

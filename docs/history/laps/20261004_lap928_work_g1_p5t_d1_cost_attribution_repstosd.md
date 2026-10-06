# 2026-10-04 | lap928 | G1 P5-T D1 비용 귀속 및 최소 수리

- 지정 역할: hands-on work. 이 API에서 실제 model/effort를 읽을 수 없어 특정 모델 실행을 주장하지 않는다. 커밋0.
- 목표/가설: whole mirror 재호출과 clip preparation을 기존 opt-in QPC로 분리한다. clip preparation이 클립 frame 비용을 설명하면 byte-fill의 범위/동작은 유지하고 값비싼 1-byte loop만 줄인다.
- 이전 지시: `docs/work/active/G1_MIDDLE_W70_P5T_QPC_SCOPE_DIAGNOSTIC_LAP927.md`; 원시 경계·30 present·PT-c ≤52.0ms·validator·화면 기준 변경0.
- 수정: `tools/inmm_stub/g1_perf_sections.{h,c}`에 writer별 whole QPC와 exclusive clip-preparation 누계/bytes 추가, `tools/inmm_stub/g1_mirror2x.c`에서 호출/비교·cache bind 시간을 제외해 누적, `tools/inmm_stub/direct_draw_trace.c`에 기록. 최종 zero/fill은 정렬 전후 byte 보정 + x86 `rep stosl`; `tests/test_g1_mirror2x.py`에 off/on·reset·early-return/중복기록 source 계약 및 모든 offset/0~256 길이의 실제 함수 범위 회귀를 추가했다. 중간 4-byte C unroll은 기대 개선이 입증되지 않아 REP STOS로 대체.
- 원본 SHA: EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 비합성 save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`. 1600×1200, 원본 800×600, Scale2x, 새 private game/prefix/display. 모든 lane EXE SHA/`source_unchanged` MATCH, cleanup `game_removed=true`, 잔류 prefix process 0.

## 비용 진단

- 최초 instrumented DOWN first30: present interval **60.310ms/present**, coarse GetTickCount 재호출 delta 825ms/29 = **28.448ms/present**, whole QPC **35.609ms/present**, exclusive `clip_prepare` **33.650ms/present**, 기존 QPC sections **1.603ms/present**, whole−clip−sections residual **0.357ms/present**. Clip preparation은 3747 sample/29 interval, byte traffic 합계 4,148,854,554(같은 버퍼 쓰기 반복 포함; 고유 할당 크기가 아님). 이에 따라 QPC section만으로 전체 호출을 대표할 수 없고, clip preparation이 mirror 내부 비용을 설명한다.
- 최초 RIGHT 경계는 28 present라 30표본 PT-c를 계산하지 않았다. 진단 pair status/HOLD 및 시각 gate는 합격 아님. 범위 밖 frame interval 잔차와 clip bucket 안 세부 비용은 남는다.

## 수리 후 fresh 실행

각 pair의 재현 가능한 수치/입력 SHA는 공유 temp의 `captures/20261004_lap928_d1/recalculate.py` 및 `recalculation.json`에 있다. 계산은 input tick < sim_tick ≤ observation tick의 candidate rows를 쓰고, first30이 없는 창은 INCOMPLETE다.

| 실행 | pair/state | DOWN PT-c | RIGHT PT-c | 결과 |
|---|---|---:|---:|---|
| 4-byte unroll 시도 | HOLD / 표본29·29 | INCOMPLETE | INCOMPLETE | PT-c 증거로 쓰지 않음 |
| REP STOS fresh GREEN | PASS / snapshot·state parity PASS | 52.103ms | 51.345ms | DOWN 0.103ms 초과 |
| REP STOS GREEN2 | PASS / snapshot·state parity PASS | 50.586ms | 50.414ms | 30표본 모두 기준 PASS |
| B′1 | PASS / parity PASS | 56.069ms | 52.483ms | 성능 HOLD |
| B′1 diagnostic, 계측 ON | PASS / parity PASS | 51.828ms | 53.966ms | 진단 전용; first30 whole QPC 26.579/27.187ms, clip 24.704/25.507ms, 기존 section 1.531/1.393ms. frame–whole 잔차 약25.25/26.78ms는 mirror 밖 시간으로 남음 |
| B′2 | PASS / parity PASS | 50.345ms | 51.379ms | 성능 PASS |
| C1 / C2 / C3 `--performance-window` | 모두 PASS | tick ratio 1.002506 / 0.999997 / 0.999996 | p95 delta +8 / +9 / +8ms | 모두 ≥0.95 및 ≤16ms 통과 |

- B′1 성능 초과가 재실행 B′1 진단에서는 같은 크기로 재현되지 않아 source 원인으로 단정하지 않는다. B′ 연속2회 조건은 충족되지 않음(B′1 FAIL, B′2 PASS). GREEN2의 pass는 B′1 실패를 지우지 않는다.
- pair/state/cleanup PASS와 별개로 candidate `mirror_validator`는 BLOCKED(최저 nearest oracle 0.8096375; 첫 오류 0.999812 기준 미달)다. 화면/최종 입력/HD≥90%/GDI/두 번째 장면 및 G1 사용자 승인은 미검증이다. P5-T·G1 HOLD 유지.

## 산출물 / 검증 / 다음 한 가지

- runtime outputs: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/20261004_lap928_{p5t_d1_pair,d1_uninstrumented_r1,d1_uninstrumented_repstos,d1_uninstrumented_green2,d1_bprime1,d1_bprime1_diag,d1_bprime2,d1_c1,d1_c2,d1_c3}/`. 캡처·raw는 메인 저장소 밖에 보존.
- final source SHA: mirror `6c925a923ef0f7bae31b650d991abc83215c11542b0b942f104452a932696e82`; perf C/H `dea19cad12495b8c44f9f7311cfaeca902c895c60234c946501eb8202400547a` / `1e906d9ace98fa94856c79b1111eff86cafb87a3a39f09c3fb153432162ab5fd`; trace `f3981f86e9b0d6c25ade37c992453477f4a7d20f9d4eec9dfbfda87dbe8425d4`; focused test `13134088d772bc206f7a2f43496f5501d5cfc0a13a311ce3e97db716f8a05fa6`.
- focused `pytest`: 3 passed; `make lint`, `make typecheck`, `make -C tools/inmm_stub`: PASS (existing unrelated C cast/unused-parameter warnings remain). Full `make check` is after history/STATUS writes; its result is appended to STATUS only.
- final recomputation SHA `b89778d3f1d1a52b891b1fadf159979a4779f390850a784261a6936cfe05a3b0`; script SHA `deccaa360f738fbeeb8b1c3bd65eb9245f69e32d85d23e3beb75fc61d8cab1b5` (shared temp). Source fingerprint is uncommitted; candidate exe/original/reference/save untouched.
- 다음 한 가지: 새 middle tier가 source·QPC/raw 재계산·B′1 FAIL/B′2 PASS·candidate visual BLOCKED를 독립 검수하고, D1 residual과 이어갈 성능 work를 판정한다. G1 milestone/사용자 승인 없음.

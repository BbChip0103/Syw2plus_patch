# 2026-10-09 | lap 1200 | G1 work — H-HDB5: 효과 키 경로 테스트 공백 4개 + 직렬화 실패 overflow 표기

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1199 middle 사전등록 §7(`20261009_lap1199_middle_g1_hdb4_review_hdb5_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 러너 값 `loop/.lap_counter` = 1200(프롬프트 증거 lap=1199는 직전 값).
- 가설: lap1199 middle이 찾은 생존 변이 4개(m12b·m01·m08·m16)는 제품 결함이 아니라 테스트 공백이다. 호스트 실행 테스트로 닫을 수 있고, `trace_event`의 overflow `scope`는 직렬화·쓰기 실패와 개수 상한을 구분하도록 한 곳만 고치면 된다.
- 예상 PASS/FAIL (사전등록 §7): B5-1~B5-5 각 RED→GREEN, 변이 m12b·m01·m08·m16·B5-5 되돌림 RED, 기존 lap1198 28종·lap1199 RED 11종 그대로 RED, focused GREEN, lint·typecheck → `make check` 1회 PASS, 원본 EXE SHA 불변. **게임 run 0.**

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/direct_draw_trace.c` | `trace_event`: `trace_event_raw` 실패 시 `g_event_count < TRACE_MAX_EVENTS`이면 overflow `scope` = `serialize`, 아니면 기존 `event_limit`. 개수 상한 분기(처음 `if`)·필드·이벤트 의미 불변. C 변경은 이 한 곳뿐 |
| `tests/test_g1_hd_pack.py` | 로더 하네스에 `aux_draw_keep_keys` 도우미와 시나리오 `lut_content_change`, 테스트 `test_remap_table_content_change_makes_a_new_key_with_the_new_tables_colours_for_every_lut_writer`(B5-1: tinted `0x466EA0`·`0x466540`, remap 혼합 `0x4678C0`·`0x468360` 4 writer) |
| `tests/test_g1_blend_key.py` | B5-2 `test_level_ten_is_refused_even_when_eleven_slices_hold_valid_values`, B5-3 `test_set_remap_takes_the_level_of_every_call_and_the_slice_follows_it`·`test_set_remap_digests_the_256_byte_table_and_refuses_an_unreadable_or_missing_one`(**실제 `blend_key_set_remap`·`auxiliary_digest` 소스 본문을 추출해 호스트 gcc로 컴파일·실행**, `MAP_32BIT` 페이지로 DWORD 주소 재현), B5-4 `test_each_writers_trace_field_reads_its_own_writers_accessor`(각 `wsprintfA`의 `blend_4678C0_*`·`blend_468360_*` 필드를 서식 순서대로 인자의 접근자와 짝지어 `g1_mirror2x_blend_<clip7\|flip7>_<이름>()` 대응 확인, 각 writer 17필드) |
| `tests/test_g1_presentation_trace.py` | B5-5 `test_trace_overflow_names_a_serialize_failure_apart_from_the_event_cap`(실제 `trace_overflow`·`trace_event` 본문을 추출해 호스트 실행, `trace_event_raw`만 모의: 상한 아래 실패 → `serialize`, 상한 → `event_limit` 이며 상한 분기는 writer를 부르지 않음) |

파일 SHA256 앞 16자: `direct_draw_trace.c 27c8ee2289a4b115`·`test_g1_blend_key.py 282a6063c6c3c278`·`test_g1_hd_pack.py 69b106639af03c5e`·`test_g1_presentation_trace.py a40c6b6255026784`.

## 측정 (공유 temp `20261009_lap1200_work_hdb5/`: `mut.sh`, `mutation_lap1199_rerun.txt`, `mutation_lap1198_rerun.txt`)

- **새 테스트 RED→GREEN (변이 격리 복사본 `/tmp`):** m12b `(key->auxiliary_digest == auxiliary_digest || 1)` → B5-1 RED / m01 `level > SLICES` → B5-2 RED / m08 `if (!g_blend_key_level) …` → B5-3 2개 RED / m16 두 접근자 교환(lap1199 `swap_trace`와 같은 변이) → **B5-4만 RED**(기존 존재 확인 테스트는 통과 = 진짜 공백이었음) / B5-5 되돌림(`trace_overflow("event_limit")` 고정) → B5-5 RED. 원본 트리 변이 0(전부 복사본).
- **lap1199 독립 변이 19종 재실행(`mutation_lap1199.py`, 현재 트리 복사본):** base GREEN, RED 15 / 생존 4. 생존 4 = m04·m05·m10·m14 = lap1199 middle이 **동등 변이**로 판정한 4개와 같다. 공백이던 m01·m08·m12b·m16은 **RED로 바뀜**. lap1199의 RED 11개는 모두 그대로 RED.
- **lap1198 변이 28종 재실행:** 28/28 RED(`mutation_lap1198_rerun.txt`).
- focused 6파일(`test_g1_blend_key`·`hd_pack`·`hd_convert`·`mirror2x`·`rect_fill`·`presentation_trace`) **263 passed/30.72s**. `make lint`·`make typecheck` PASS. 변경한 `direct_draw_trace.c`는 mingw `-Wall -Wextra -O2` 컴파일 경고 0.
- 게임 run 0 → 디스크 여유 11 GB 그대로(사본 생성 없음). DLL 재빌드·실게임 확인 없음: `scope` 표기 변경은 다음 run 회차에서 자연 확인(사전등록대로).

## 판정

**H-HDB5 `PASS(partial, 기술·격리)` 후보 — middle 검수 전.** 사전등록 합격식의 테스트·변이 항목은 충족했고, `make check` 결과는 STATUS에 보강한다. 제품 결함은 드러나지 않았다(수리 없음). 기본 켬·사용자 전달 아님, 마일스톤 경계 아님.

공개:
1. B5-3·B5-5는 소스 본문 추출 방식이라 함수 이름·닫는 `\n}\n` 위치에 의존한다(리팩터링 시 추출 실패 = RED로 드러남, 오탐 방향).
2. B5-4는 접근자 짝을 정적으로 대조한다(trace 파일을 실제로 쓰지 않음). 실제 직렬화 대조는 게임 run의 metrics 줄로만 가능하다.
3. `serialize` 분기는 쓰기 실패·`g_trace_enabled == 0`도 포함한다(후자는 overflow 줄도 못 써서 출력 없음). 의미상 "상한 아래 실패"를 뜻한다.
4. `trace_overflow`는 총 2회만 방출한다(기존). `serialize` 마커가 그중 하나를 쓰므로, 같은 run에서 먼저 `serialize`가 2회 나오면 이후 `event_limit` 마커는 안 나온다(기존 상한 정책, 변경 없음).

## 다음 한 가지

middle이 H-HDB5를 검수(변이 재현·새 테스트 RED/GREEN 독립 재확인)한 뒤 효과 갈래를 마감한다. 그다음 backlog(lap1189): 기본 켬 전 전체 팩(`pack_hdf1`+로고+효과) 동시 실게임 확인 1회 → 사용자 시험판 재스테이징 판단(마일스톤 경계, root 전달). 사용자 G1 시험 결과가 오면 최우선.

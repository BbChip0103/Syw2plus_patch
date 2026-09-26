# ESL 2608 AI 상점개설 연구 후보 — 2026-09-25

## 범위와 근거

사용자 제공 `컴퓨터 연구,생산.xlsx`(SHA `ca845854924e2b6ea479fd78886641020329c55a2fe2d403ea345e34d81071ea`)는 건물 48/57/73의 기존 연구가 RID27=자원가치향상임을 확인한다. 2608 EXE의 상점 완료 게이트는 RID20을 읽지만 원본과 바이트 동일한 AI 선택표에는 RID20 후보가 없다. 주소·기존 바이트·분석 경계는 `analysis/memory_maps/esl2608_shop_ai_static_20260925.md`에 기록했다.

## 단일 변경

`patches/ai/shop_open_research_2608.py`와 회귀 `patches/ai/test_shop_open_research_2608.py`를 추가했다. 입력 EXE SHA `bf39cb73f395d677a1c27fda01698f849b23973a39fd9be8b22af0010cb60f27` 전용이다. 기존 143행과 RID27 세 행을 보존하고 `.shopai` 읽기 전용 섹션에 RID20 세 행을 덧붙여 AI 선택기의 모든 표 참조 10곳을 새 주소로 옮긴다. PE 이미지/initialized-data 크기, 헤더 여유·비중첩·범위·old instruction bytes를 검증한다. 소스 덮어쓰기/다른 버전/기존 출력은 거부하고 `restore_candidate()`는 원본 바이트를 정확히 복원한다. 최종 후보는 공유 temp의 `esl2608_shop/2608_shop_open.v2.candidate.exe`, SHA `0f3334668f5ed37d130726725f421515f031be2856efdde04a9c19ea572627f5`다. 초안 `2608_shop_open.candidate.exe`(SHA `d7c8b213…`)는 PE initialized-data 합계 수정 전 산출물이므로 사용 금지다. 원본/배포 EXE는 수정·배포하지 않았다.

## 검증 판정

- **PASS, 정적:** `.venv/bin/python -m pytest patches/ai/test_shop_open_research_2608.py -q` → 9 passed. SHA/old bytes/표 보존+추가/10 참조/PE 구조/버전 거부/복사 전용/원복/padding 변조 거부를 포함한다.
- **PASS, 정적:** 후보 PE 7섹션·`.shopai` RVA `0xD2D000`·raw `0x104000`·`SizeOfInitializedData=0xBB1000`·pefile warning 0. 후보의 기존 표 VA 절대참조는 0개이고 새 행은 `(15,48,65535,20,...)`, `(15,57,65535,20,...)`, `(15,73,65535,20,...)`, 다음 sentinel `0xFFFE`다. 원본 SHA 불변.
- **PASS, 정적:** `.venv/bin/python -m ruff check patches/ai/shop_open_research_2608.py patches/ai/test_shop_open_research_2608.py`, `.venv/bin/python -m mypy patches/ai/shop_open_research_2608.py --follow-imports=skip`, `bash checks/safety.sh check`.
- **PASS, 버전/원복:** 실제 2606 EXE를 CLI 입력으로 넣으면 크기 불일치 exit1로 거절하고 출력 파일은 만들지 않는다. 최종 후보 `restore_candidate()` 반환 bytes는 원본 2608 EXE와 완전 동일하며 SHA도 일치한다. `make doctor`의 overall `ok=true`, `side_effects=false`를 확인했다(선택적 runtime manifest는 없음).
- **FAIL, 런타임 진입:** 격리된 전체 2608 게임 복사본에서 fresh Win32 Wine prefix/미사용 Xvfb로 baseline을 두 차례(`ddraw=b`, `ddraw=n,b`) 띄웠지만 양쪽 모두 `SetVideoMode()` 대화상자에서 멈췄다. 캡처 `temp/Syw2plus_patch/captures/20260925_193327_esl2608_baseline_title.png`, `.../20260925_193737_esl2608_native_ddraw_title.png`. 후보 AI 연구/아이템 구매는 **SKIP(선행 실행 장애)**. 활성 AI/건물/자원/틱 fixture 없음; synthetic·memory-write·resource grant 없음.
- **FAIL, 전체 Fast:** `make check`는 **870 passed, 6 failed / 612.45s**로 끝났다. 실패는 변경 파일과 무관한 G2 `test_g2_full_unit_capacity_v1.py` 2건의 후보 고정 SHA 불일치 및 `test_g2_offline_storage_launch_gate.py` 4건의 허용 SHA 불일치다. 안전 pin은 갱신하지 않았다. 전체 raw 로그는 공유 temp `esl2608_shop/make_check.log`에 보존했다. 변경 후 표적 테스트는 9 passed다. `make lint`, `make typecheck`, `checks/context_limits.py`, `bash -n` 전 범위, `checks/safety.sh check`는 각각 PASS다. Fast 결과는 실제 AI 동작 증거가 아니다.

## 남은 위험

정적 후보 등록은 AI의 연구 가용성·가격 3000/3000·발주 시점·완료·실제 아이템 구매를 증명하지 않는다. 격리 런타임의 디스플레이 선행 장애를 해결하고 원본/후보의 같은 진영·건물·자원·tick 조건으로 반복 비교해야 한다. 다음 새 중간 세션의 독립 검수와 사용자 마일스톤 승인은 아직 없다. 커밋/배포는 0회.

## 사용자 추가 요청: 2606 장수7/전비·시작자리고정과 결합

2026-09-25 후속 지시에 따라 읽기 전용 2606 base와 두 변형 EXE를 바이트 비교한 뒤 `patches/ai/shop_open_legacy_combos_2608.py` 및 회귀 `patches/ai/test_shop_open_legacy_combos_2608.py`를 추가했다. 2606 변형은 각각 7바이트/6구간, 11바이트/8구간만 다르며 이 8구간의 2608 old bytes와 주변 ±256B가 동일하다. shop 후보 변경과 중첩 0. 두 조합은 2608 원본 SHA 고정·2606 base/변형 SHA·전체 diff·old bytes·문맥 hash·비중첩을 검증하고, 별도 새 파일만 생성하며 2608 원본으로 정확히 복원한다. 주소별 근거는 `analysis/memory_maps/esl2608_shop_ai_static_20260925.md`에 남겼다.

| 조합 | `260921_temp/` 새 파일 접미 | SHA-256 | shop 단독 대비 |
|---|---|---|---:|
| AI상점 + 장수7/전비1600-200-3000 | `_AI상점개설_장수7명_전비1600-200-3000.exe` | `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3` | 7B |
| 위 조합 + 시작자리고정 | `_AI상점개설_장수7명_전비1600-200-3000_시작자리고정.exe` | `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973` | 11B |

표적 `pytest patches/ai/test_shop_open_research_2608.py patches/ai/test_shop_open_legacy_combos_2608.py -q` **19 passed**, 해당 두 패처/두 테스트 Ruff PASS, 패처 2개 mypy PASS. 생성 후 독립 확인: 두 EXE 크기 1,069,056B, PE 7섹션, `SizeOfInitializedData=0xBB1000`, pefile warning0, `restore_candidate()` 모두 2608 원본 bytes와 동일. 원본 2608 SHA `bf39cb73…` 불변. **최종 `make check`는 887 passed / 622.23s, Ruff·compileall·mypy·CONTEXT_PASS**로 완료됐다(raw `temp/Syw2plus_patch/esl2608_shop/combo_make_check.log`). 앞선 별도 회차의 870 pass/6 fail 기록은 삭제하지 않는다. 안전 pin을 이 작업에서 바꾸지 않았고, 최종 현재 트리 검사 결과만 합격 근거로 쓴다. `SAFETY_PASS`와 shell syntax도 별도 확인했다. 실제 게임·장수 수·전비·시작자리·AI 연구/구매는 **SKIP(상기 baseline `SetVideoMode()` 선행 장애)**이며 정적 조합을 제품 PASS로 쓰지 않는다. 커밋/원본 덮어쓰기/자동 deploy 0회.

사용자 후속 요청으로 위 두 조합 파일명과 연결 JSON에서 `_런타임미검증` 문자열만 제거했다. rename 전후 바이너리 SHA는 각각 동일하며, 검증 공백은 파일명 대신 이 카드와 JSON `runtime_status`에 유지한다. shop 단독 후보 파일명은 이 요청 범위 밖이라 변경하지 않았다.

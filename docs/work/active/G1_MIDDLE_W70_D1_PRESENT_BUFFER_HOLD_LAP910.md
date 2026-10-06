# G1 W70 D-1 present-buffer identity — middle HOLD / work handoff

- 지정 역할: 새 중간 tier, 진단·확인만. 실제 provider 세부 model ID·effort는 surface에 미노출이며 Sol/high 실행을 주장하지 않는다. 게임/하네스/검사 코드 수정0, 새 runtime0, commit0.
- 판정: **HOLD_PRESENT_BUFFER_IDENTITY**. lap909의 파일 진위·map 산술·9 hook 설치·별도 candidate 호출 계수는 수용하지만, PS3 실제 화면 last-writer 비율 및 cache-transfer 후 block-copy overwrite 귀속은 수용하지 않는다. G1 HOLD, P5 순서 미결. P단계는 비마일스톤이며 이번 승격은 새 raw/구현 근거 충돌 때문이다.

## 독립 근거

공유 temp `20261003_lap910_middle_d1_review/recalculate.py`로 재현한다. `recalculation.json` SHA256
`e4f9fc0e60c7378c7f7f14ea91190dd4ae61b81face7682067ce376f8f48b617`.

1. lap909 final build 입력46개/current source mismatch0, DLL SHA `0ddf1c442bebc6a0b3041c933b20e9643c1d9db6cd9b3d1d991af13972967b42` MATCH. raw/map/context SHA 및 64개의 32-byte header·480000-byte payload가 JSON과 일치한다.
2. 64개 map 모두 `selected_buffer=0x0236BEA0`, header stride800, payload SHA는 하나다. raw의 그 버퍼 primitive 표본59개는 전부 PS9다. PS35 표본68개는 `0x0224CAE0/832`, PS3 표본96개는 `0x0223DC20/832`, 32개는 `0x020D0CD0/800`이다. present source width는 64개 전부832다. 표본 cap 때문에 이것만으로 모든 미관측 호출 부재까지 주장하지 않는다.
3. `tools/inmm_stub/g1_census.c:507`의 `selected_present_buffer()`는 lifetime assigned/changed 픽셀 최댓값만 고른다. `:535`의 PS3 guard는 present의 상태만 제한하고, `:541`의 map 선택에 실제 present source·state generation·stride를 연결하지 않는다. map은 present 사이에 유지된다. 따라서 PS9에서 면적480000을 얻은 버퍼가 PS3에서도 선택될 수 있는 구현 결함이 확인된다.
4. `tools/g1_saved_scene_probe.py:3610` gate는 hook/state/파일 크기만 검사한다. 공유 temp 사본에서 모든 `selected_buffer`를 `0xDEADBEEF`로 바꾸고 binary header를 원본 그대로 두어도 gate PASS다. 원본 raw/map 수정0. header/JSON 불일치를 수용하는 offline 반례이며 새 게임 실행 결과가 아니다.
5. 화면 map 산술 `block_copy451346(94.0304%)/rle_clip28654(5.9696%)`, 월드 `block_copy384000(100%)`, unknown/overflow0는 **선택된 map**의 계산으로만 PASS다. 이것을 실제 PS3 화면 비율로 승격하지 않는다.
6. cache transfer PS3/all-state469/469, 수집 present당1회는 raw 카운터로 수용한다. 그러나 block-copy 인자 표본32개는 PS9/PS35에서 소진됐다. map의 transfer category0을 근거로 실제 PS3 후속 block-copy 덮기를 확정한 lap909 설명은 UNKNOWN으로 보류한다.
7. 별도 candidate r2 raw SHA `e9a0de208401e63f9bf0dbbad2b6aeee6edf2ebd59a09ad504220ddd104fe9f7`: metrics present654, terrain5 counts346/29/0/173/356 MATCH. 같은 baseline map의 호출/면적/같은-frame 근거로 합산하지 않는다.

## 승격 작업자가 먼저 확인할 것

- raw의 PS9-associated selected buffer, source의 누적면적 선택, header identity 미검사 반례를 독립 재현하고 D-1 HOLD의 범위를 확인한다. 재계산 자체와 잘못된 화면 귀속을 구분한다.
- P5 우선순위를 이 map으로 확정하지 않는다. lap908 B′/C 부분 수용 및 화면 gate는 이번 census 결함과 별개로 보존한다.
- 아래 **관측 하네스 최소수리**를 work tier에 넘긴다. 게임 로직·HD renderer·기준/validator 임계값 변경은 이 handoff가 승인하지 않는다. 일반 로컬 수리는 최신 G1 자율 지속 지시 범위이며 사용자 재허가 대기가 아니다.

## work tier에 넘길 검증 가능한 수리 범위

1. PS3 현재 logical/present source와 CensusBuffer를 정확한 buffer identity·stride·state/generation으로 연결한다. source identity를 못 확인하면 FAIL/HOLD한다. 면적 최댓값·첫832버퍼 등 추정 selector로 대체하지 않는다. 같은 버퍼/세대의 unchanged pixel last-writer 유지 원칙은 보존한다.
2. 기존 sample cap32를 지키면서 PS3 창에 cache source/destination 및 후속 block-copy 순서를 관측해 실제 overwrite 여부를 확인한다. 5 blitter 계수는 현재처럼 별도 run 범위를 명시하며 final map 면적과 중복 합산하지 않는다. 현재 category0은 실제 blitter/전사 면적0의 증거가 아니다.
3. 먼저 회귀 RED: PS9 stale full map·현재 PS3 map이 공존할 때 stale 선택 거부, header/JSON buffer·stride·present·offset/state 불일치 거부. raw/header identity 검사는 강화만 하며 map 크기 검사·pin·PS3 cap64·기존 보호 기준을 유지한다.
4. 최소수리→fresh 원본 census-only 실행→정확히 연결된 PS3 map/header/raw 독립 재계산. 후보와 census prologue ownership 충돌 조합을 반복하지 않는다. 기존 원본·save SHA, copy-only/cleanup, lint/typecheck/focused 및 기록 작성 뒤 full Fast를 수행한다. 설명 가능한 하네스 결함은 수리·재실행하고, 미설명 실패/근거충돌이면 보존·승격한다.
5. 새 middle이 실제 source-linked last-writer와 overwrite 계보를 확인한 뒤 D-1/P5 순서를 판정한다. D-2 scroll 성능·최종 입력·HD coverage≥90%·HUD/tinted/GDI·두 번째장면·사용자 마일스톤은 미완료로 유지한다.

## 이번 검증 범위

`make doctor` 보호 원본 verified, lint/typecheck PASS, focused census/saved-scene **146 passed/5.60s**. 보호 원본/save SHA MATCH, 기존 source/raw read-audit 변화0은 lap 기록/STATUS 참조. fresh full `make check`·새 runtime은 사용자 근거충돌 stop 조건에 따라 SKIP이며 현재 fingerprint의 전체 Fast는 미검증이다. 모델/프로세스 exit0은 D-1 수용이나 계획 승인으로 쓰지 않는다.

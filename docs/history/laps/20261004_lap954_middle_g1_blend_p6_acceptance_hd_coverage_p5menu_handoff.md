# 2026-10-04 | lap 954 | G1 W70 lap953 반투명 writer 독립 수용 · 기준1 P6 분류 · 기준2 첫 HD coverage 집계 · P5 메뉴 block_copy 인계

- 실제 provider/model/effort / 지정 역할: middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 954 읽기만.
- 가설 / 사용자 관찰: lap953 w6/w7 raw와 watch EIP 표는 제품 helper 없이 재현되고, 두 writer는 원본 EXE 정적 코드상 혼합표/LUT 기반이다. 기준2 HD coverage는 기존 source-matched Scale2x raw에서 present별로 집계할 수 있다.
- 예상 PASS / FAIL 조건: PASS = w6 64 present 재계산 불일치0, SHA = 기록, w7 이벤트×키·건수 = lap951 기본, 디스어셈블 = 분석 문서. FAIL = 불일치·SHA 불일치·근거 충돌. HD coverage는 측정·공개만(기준2 원문 ≥90%, 새 임계값 없음).
- 변경 파일 / source fingerprint / 커밋: 새 카드 `docs/work/active/G1_MIDDLE_W70_BLEND_P6_ACCEPTANCE_HD_COVERAGE_P5MENU_HANDOFF_LAP954.md`, `analysis/memory_maps/g1_blend_writers_4672e0_467580_lap953.md` §5 확인 절 추가(본문 불변), 이 기록, STATUS. uncommitted. source 5파일 SHA = lap953 기록(카드 §1).
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 `game.exe` `b56986e0…a8ac`·save006 `616b7997…d064` 재해시 MATCH(read-only). w6/w7 `status PASS`·`source_unchanged`·`game_removed` true·non-synthetic. 8 player records는 활성8인 부하증명 아님.
- 실행 명령 / 로그 / 캡처: 공유 temp `20261004_lap954_middle_review/`: `recalc_lap954.py`(SHA `ce220a32e9f8787bef95fb8d5c703c0e85cab90926309bd47d1f524c57654741`) → `recalc_lap954.json`(`6ff6000256146ec9879d8bf0ab883bf86025c4d6b9a7be4fda4de49fd2dff93b`), `hd_coverage_lap945_raw.py`(`fbf5a42c0c07c506e5af5634b1dd6f378ae051e4742bbe76f1d7a5f08c2165fe`) → `hd_coverage_lap945_raw.json`(`4e9997a9aa7dc61bf998eabad07770bdca6fd9fcbf3f8aeeecf1c05d4ce2b4cc`), 마스크 `w6_last_mask.npy`(`ca87aff2…3c3d`)·`w6_p7_mask.npy`(`9a4ae205…5be`). 원본 EXE objdump `0x4672E0..0x4673E0`·`0x467580..0x4676D8`(read-only).
- 측정값 / 판정:
  - w6 재계산 불일치 0(64/64): last 523·p50 532·max 1,162(present 7, 0.242%), 로고 상자 텍스트 밖 0. blend bbox = args 16비트 부호확장 불일치 0(70건). watch EIP 표 = 기록. w7 = lap951 기본과 이벤트×키·건수 동일, blend/watch 이벤트·residual map 없음.
  - 가법 항등: w6 `unhooked + Σblend changed` = lap951 r6 `unhooked`(present 1~5·8·9·62~64 정확, 예 present 3 21,423) → shadow 차감 과흡수 없음. present 6·7 차이는 run별 회오리 종료 프레임 차.
  - lap953 measurement-only target **PASS(partial)** 수용. 기준1: `0x4672E0`(50% 평균+역 LUT)·`0x467580`(채널별 64×64 혼합표+역 LUT) **명시 잔여 P6** 최종 분류.
  - 기준2 명시 잔여(P6+P7+미분류): PS3 최악 21,423(4.463%), 정상 2,625(0.547%) = P6 2,102 + P7 441 + 미분류 82. **≤5% 측정 창 안 충족(부분) 유지**; 0.242%는 미분류 수치일 뿐. present 6~7 미분류는 회오리 사각형 밖이 대부분(1,055 중 318만 안) → "효과 끝 프레임" 가설 약함, UNKNOWN.
  - 기준2 HD coverage 첫 집계(lap945 Scale2x 후보 raw `6f524803…02d7`, 미러 source `b70d044a…` = 현재): PS3 891 present min 89.79%·p50 **90.42%**·≥90% 99.2%(idx 6~12 미달) → **경계, 판정 보류**; PS9 55 present **5.73% → FAIL**(메뉴 block_copy 미러 없음). V1 outside diff 0. **기준2 = FAIL**, G1 HOLD.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: HD coverage는 단일 기존 run이며 PS3 경계값은 run 변동에 민감하다. `0x467410`·`0x4676D0`은 미관측. G1 사용자 승인·D-2·P-6·P6/P7 HD HOLD. strategy 재호출·ESCALATE 조건 없음(PS9 미달은 계획된 P5 메뉴 미러 부재).
- 다음 한 가지: work(Sonnet) 1 lap — PS9 메뉴 block_copy `0x466280`(비-terrain src) 원천 hash 고정 확인 후 미러 identity/Scale2x 분기 구현, fresh save006 scale2x run에서 PS9·PS3 present별 `covered−stale` 실측(카드 §5).

# 2026-09-23 | lap 527 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / **middle**(중간계획·컨펌). 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap526 strategy K3 규칙으로 X를 원본 정적 자료에서 확정할 수 있다. 확정되면 S1(W36) 카드를 한 회차 안에 발행한다(K7).
- 예상 PASS / FAIL 조건: 원본 타입 행 추출이 기존 실측(type 5·7·46·110, §20 28타입)과 일치하면 추출을 신뢰하고 K3를 적용한다.
  적격 0이면 `ARM_FAIL`로 strategy에 회부한다. 불일치가 나오면 X를 확정하지 않고 S1 preflight 절차만 고정한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 문서만 바꿨다(uncommitted, 커밋 0).
  - 신규 `docs/work/active/G2_S1_DRIVEN_COMBAT_CYCLE_SOAK_LAP527.md` SHA256 `57c22476c62e009faae2f92391e2f305967493a4da5dceb589f480ea97ec0dcd`
  - 신규 `analysis/memory_maps/g2_type_row_fixture_x_selection_lap527.md` SHA256 `d69346e8c025c7bd98f21a5bb460b9b3338099e66745361b8827e476709c198d`
  - 추가 `loop/ESCALATE_SOL` §84, 갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`(lap527 처리 한 줄), 이 기록.
  - 제품 source·브리지·테스트 변경 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 재확인·불변. 게임 실행 0.
  카드가 지정한 후보는 EXE `a10024de…`(N=4001)이다. 브리지 DLL은 허용목록 변경으로 새 SHA가 된다(lap524 `c1c7cfde…`).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `objdump -Mintel -d -b pei-i386 -j .text Syw2plus_re/Syw2plus/syw2plus_original.exe`로 `FUN_0049BAA0` 호출 111건을 추출했다.
  - 스크립트와 산출: `temp/Syw2plus_patch/g2_capacity/20260923_lap527_w36_x_static_selection/`
    - `lap527_parse_rows.py` `60d19efa…2b9fa7`
    - `lap527_rows.json` `e29d3339…b07de9`
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 추출 양성 대조 **PASS**. type 5(35/1×1/`0x4028401`), 7(10/`0x14001`), 46(20/3×3/`0xE2082`), 110(10/`0x10005`)이 일치한다. §20 28타입 `+0x4C`는 28/28 일치한다.
  - **N184:** 후보 6종이 모두 적격이다. 비용은 2·3=13, 4=15, 12=17, 13=18, 10=20이다. ⇒ **X = type 2**.
  - **N185:** 정적 값이 곧 런타임 값인지는 가정이다. 카드가 시딩 전 읽기 전용 preflight를 강제한다.
  - **N186:** 정적 bit 0x4 행은 62개다. 후보 확장 근거로 쓰지 않는다.
  - 신규 발견: op8 계약 테스트 `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py:129`도 허용목록 문자열을 핀으로 잡고 있다. 카드가 두 테스트 모두 개정하도록 지시한다.
  - `checks/safety.sh check` exit0 `SAFETY_PASS`, `checks/context_limits.py` exit0 `CONTEXT_PASS`. source 변경이 없어서 `make check`는 생략했다(N22). 문서 무결성 검사이며 제품 증거가 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - type 2 행이 런타임에 달라지면 `ARM_FAIL`이다.
  - type 2가 국가 조건 등으로 Place/Gate에서 거부될 수 있다. 이 경우 시딩 receipt 실패로 `ARM_FAIL`이다.
  - 교전은 짝 owner(o XOR 1)끼리만 일어난다. 배치 주사 구간이 이미 겹쳐 있어 원거리 접근은 이번에도 입증 대상이 아니다(N87).
  - 저장/로드는 N=4001에서 lap452/453이 1회 왕복을 확인했다. 교전 중 왕복은 처음이다.
  - streak: 이 회차가 문서 회차 3회째다(lap525·526·527). §83 K7이 이 회차 1회만 허가했다. 다음 work가 게임 실행 없이 끝나면 STOP하고 사용자에게 보고한다.
  - 사용자 승인 상태 변화 없음. Q9·Q7-B·"8인"·스크립트 교전 범위·허용목록 확장 번복 여부는 사용자 전권이다.
- 다음 한 가지: **work(Sonnet5) W36 실행.** 카드 §2 repo 3파일 변경 → `make check` 전체 1회 → exit0이면 S1 24k 게임 1회를 foreground로 완주한다.

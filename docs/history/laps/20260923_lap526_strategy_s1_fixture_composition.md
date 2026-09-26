# 2026-09-23 | lap 526 | 목표 G2 (strategy: S1 fixture 구성 판정, §82 회부 해소)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / strategy(큰방향·master-plan).
  근거: INBOX 2026-09-23 strategy 모델 교체 지시. 게임 코드·브리지·테스트·바이너리 무변경, 문서 산출물만.
- 가설 / 사용자 관찰: 해당 없음(판정 회차). 입력은 `ESCALATE_SOL` §82다. A2(전투 사망)와 A8·§5(허용목록 {5,7,46} 고정)가 N182 때문에 충돌한다.
- 예상 PASS / FAIL 조건: 아래 셋을 모두 만족하면 이 회차는 성립한다.
  ① 충돌을 기준 완화 없이 결정 가능한 규칙으로 푼다. ② 다음 실제 실행까지의 경로를 1회 문서 회차로 제한한다.
  ③ `SAFETY_PASS`·`CONTEXT_PASS`를 유지한다. 사용자 전권 항목(Q9·Q7-B·"8인"·스크립트 교전 범위)을 고르면 FAIL이다.

## 이전 바퀴 검수 (④2)
- lap525 N181을 원본 바이트로 독립 재확인했다(`objdump -Mintel -d -b pei-i386 -j .text`, 원본 SHA `b56986e0…c9c08a8ac` 불변).
  - `0x411D29 mov ecx,[eax+0x9B5274]` → `0x411D2F mov [ebp+0x1D8],ecx`로 일치한다.
  - `[reg+0x1D8..0x1DB]` 쓰기를 mov/or/and/add/sub/xor/inc/dec/bts/btr 전체로 찾았다. 결과는 `0x411D2F`·`0x48CF3C`·`0x48CF58`·`0x48CF91`·`0x4C4922` 5개뿐이다(esp 지역변수 제외). 기록과 일치한다.
- N182 비트 분해를 다시 계산했다. 입력은 참고 저장소 §20의 원본 28타입 값과 type5 `0x4028401`·type46 `0xE2082`다.
  - bit 0x4 보유: 2·3·4·10·12·13·42·63·110·111.
  - bit 0x10 보유: **0종**. 그래서 `+0x1BC`는 모두 1이다.
  - bit 0x400 보유: 4·5·10·12·63.
  - bit 0x2 보유: 42·63과 46~62 건물 계열.
  - 결과는 lap525와 일치한다. 신규 사실은 하나다. **bit 0x10 타입이 없어서 type5의 bit 0x400은 이 fixture에서 쓸 곳이 없다.**
- 허용목록의 출처를 원문으로 확인했다. lap461 카드 §6-1(모델 카드), lap463 확장 {5,7}→{5,7,46}, `runtime_bridge.c:197`, 핀 테스트 `test_g2_runtime_bridge_fixture_type_allowlist_pin.py`다.
  사용자 지시는 없었다. 사용자 결정은 Q8=(ㄱ) "자원/유닛 주입 시딩 허용"뿐이다.

## 판정 (전문 `docs/work/active/G2_STRATEGY_S1_FIXTURE_COMPOSITION_LAP526.md`, `ESCALATE_SOL` §83)
- K1: (나) 채택. bit 0x4 전투 타입 X 1종을 추가한다. (가) 편측 사냥은 기준 완화라서 기각했다. (다) 조기 제출은 "움직이는 상태" 증거가 비어서 기각했다.
- K2: 사용자 승인은 필요 없다. 모델 핀이고, 목표·안전·배포 범위를 바꾸지 않기 때문이다. 대신 INBOX에 통지했고 사용자가 번복할 수 있다. 이 기록이 핀 변경의 승인 기록이다.
- K3: X 선택 규칙을 고정했다. 후보 {2,3,4,10,12,13}에서 행 `+0x4C` bit 0x4, op5 가드, 비용 ≥1을 확인한다. 그중 최저 비용을 고르고, 동률이면 낮은 타입 번호를 고른다. 적격 후보가 0이면 `ARM_FAIL`이다.
- K4: A8' = {5,7,46,X}를 모두 보유하고, X ≥10기/owner, 단일 type 비용 비중 ≤85%다.
- K5: A2 사망을 op8 기인과 자연 자동공격 기인으로 나눈다. 표본마다 8 owner `(used,reserved,count)`·`live`를 원시로 저장한다. `used<0` 검사를 넣는다.
- K6: op4·가드 완화·AI 패치 금지는 유지한다. 확장은 X 1종만 허가한다.
- K7: G2 트랙을 계속한다. middle 카드 1회만 세 번째 무증가 회차로 허가한다. 그다음 work 회차가 게임 실행 없이 끝나면 STOP하고 사용자에게 보고한다.

## 기록 필드
- 변경 파일 / source fingerprint / 커밋: 커밋 0(`LOOP_ALLOW_COMMITS` 기본0, HEAD unborn). 모두 uncommitted다.
  - 신규: `docs/work/active/G2_STRATEGY_S1_FIXTURE_COMPOSITION_LAP526.md`(SHA256 `1cccb22d2094fe31fa2b03668f8c6929bd72ceecbf8cb9be9c72b39ca6f1c960`), 본 기록.
  - 수정: `docs/work/active/G2_STRATEGY_Q8A_SEEDED_ACCEPTANCE_LAP522.md`(A8 아래 개정 표시 2줄, 원문 보존), `loop/ESCALATE_SOL`(§83 추가), `docs/STATUS.md`, `docs/feedback/INBOX.md`(Q8 항목 아래 lap526 처리 1단락).
  - 제품 source(`patches/`, `tools/`, `tests/`) 변경 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…c9c08a8ac` 불변. 후보 `a10024de…`는 재빌드하지 않았다. 게임 실행 0.
  lap525 근거 문서 `analysis/memory_maps/g2_unit_attack_domain_flags_1d8_lap525.md` SHA256 `2b85801f…29f1a`(이번 회차 기준값).
- 실행 명령 / 로그: `objdump`(읽기 전용), `python3` 비트 분해, `checks/safety.sh check`, `python3 checks/context_limits.py`.
- 측정값 / 판정: 제품 측정 없음. N181 재확인 PASS, N182 재계산 PASS. source 변경이 없어서 `make check`는 생략했다(N22). `checks/safety.sh check` exit0 `SAFETY_PASS`, `checks/context_limits.py` exit0 `CONTEXT_PASS`(STATUS 94·INBOX 283·APPROVALS 46줄). 참고 저장소의 tracked 수정 208건은 전부 2026-09-19 이전 mtime이라 이번 세션이 만든 것이 아니다.
- 회귀 / 남은 위험:
  - X 후보의 비용·크기·`+0x24` 값은 아직 읽지 않았다. 적격 후보가 0일 수 있다(→ `ARM_FAIL`).
  - 42·63을 건물 계열로 분류한 것은 bit 0x2를 근거로 한 추정이다.
  - 110·111 사망의 부수효과는 모른다.
  - 사용자가 확장을 (ㄱ) 범위 밖으로 볼 수 있다.
- 독립 검수 및 사용자 승인 상태: 이 판정은 모델 방향 판정이다. 제품 합격·마일스톤 승인이 아니다.
- 다음 한 가지: middle(Opus5.5)이 S1 카드(W36)를 발행한다. X 확정, 허용목록·핀 개정 지시, A1~A7+A8'+K5, 라벨, 60분 상자를 담는다. 그다음 work가 S1 24k 게임 1회를 실행한다.

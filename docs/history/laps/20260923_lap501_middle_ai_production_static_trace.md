# 2026-09-23 | lap 501 | G2 — AI 생산 정지 원인 정적 추적

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / **middle**
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. 이 lap은 자기 결과를 승인하지 않는다.
- **가설 / 사용자 관찰:** 사용자 2026-09-23 04:14 "AI 생산 정지 원인 분석부터 ㄱㄱ".
  lap459 N81/N82는 자원·`count_cap`·supply cap·풀을 **배제**만 하고 코드 원인을 찾지 않았고,
  이 저장소 `analysis/`에 AI 생산 결정 로직 문서가 **0건**이었다.
  가설: 정지 원인은 자원계가 아니라 **AI 생산 결정 경로의 게이트**에 있다.
- **예상 PASS / FAIL 조건:** PASS = 원본 바이트로 확인된 생산 결정 경로와, owner별 영구 정지를
  만들 수 있는 게이트 후보 목록 + 그것을 가르는 검증 가능한 probe 설계를 남긴다.
  FAIL = 경로를 바이트로 확정하지 못하거나, 후보를 좁히지 못한다.
  **비-목표:** 단일 원인 특정(런타임 값 필요) · AI/생산 로직 변경(여전히 (ㄴ) 대기).

## 변경 파일 / source fingerprint / 커밋

- 신규 `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md` (근거 본문)
- 신규 `docs/history/20260923_inbox_lap501_precompaction.md`
  (INBOX lap471~498 계보 원문 65줄, SHA256 `771f32491e8f179ef5f576df469d5c8fb4926f8d0c5143834616b0a6c3c09201`)
- 갱신 `docs/feedback/INBOX.md`(계보 압축 + lap501 추기) · `docs/STATUS.md` · `loop/ESCALATE_SOL` §64
- 신규 `docs/history/laps/20260923_lap501_middle_ai_production_static_trace.md` (이 파일)
- **제품 source 변경 0** (`tools/` `tests/` `patches/` `checks/` 무변경) · **커밋 0**(`LOOP_ALLOW_COMMITS=0`, uncommitted 보존)
- 분석 스크립트는 제품 트리에 넣지 않고 공유 temp에 둔다:
  `temp/Syw2plus_patch/20260923_lap501_middle_ai_production_stop_static_trace/`
  (`disasm_ai_production.py`, `disasm_ai_production.txt`, `disasm_0043e7f0.txt`,
  `dump_production_table.py`, `production_table_dump.txt`)

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

- 원본 `syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  — **읽기 전용으로 열었고 실행 전후 변경 없음**(스크립트가 매 실행 SHA를 재확인한 뒤에만 진행).
- **후보 SHA: 해당 없음** — 이 lap은 후보를 만들지도 실행하지도 않았다.
- **환경/지도/군대/fixture: 해당 없음 — 게임 실행 0회.** 순수 정적 분석이다.
- 참고 저장소 `Syw2plus_re`는 **읽기 전용 대조**로만 사용(쓰기 0).

## 실행 명령 / 로그 / 캡처 경로 및 해시

```
python3 disasm_ai_production.py   > disasm_ai_production.txt      # 0x406770/0x406B00/0x406C70
python3 (동 모듈 재사용)           > disasm_0043e7f0.txt           # 0x43E7F0
python3 dump_production_table.py  > production_table_dump.txt     # DAT_004EC514 전량
bash checks/safety.sh check                                        # SAFETY_PASS (exit 0)
python3 checks/context_limits.py                                   # CONTEXT_PASS
python3 -m pytest tests/ -q                                        # 결과는 아래 측정값에 기재
```

캡처 PNG 없음(시각 산출물 없는 lap). 원시 텍스트 산출물은 위 공유 temp 경로에 보존.

## 측정값 / 판정

**판정: PASS(정적 경로 확정 + 후보 좁힘) · 원인 특정은 `UNKNOWN`(런타임 값 필요).**

경로(전부 원본 바이트로 확인, Ghidra는 대조용):

```
FUN_00406770 @0x406770  per-unit AI dispatch
  G-1 UnitStruct+0x1F4 == 100
  G-2 tick DAT_008924B8 >= 0x32
  G-3 UnitStruct+0x1D8 & 0x80000
  G-4 (tick>>1) 짝수 && (tick>>1)%10 == 0      ⇒ 20 tick마다 1회
  └─ EVEN → FUN_00406B00 @0x406B00  생산 본체
       G-5 per-owner AI 활성 바이트 0x00956772 + owner*0x3ABC
       후보 추첨 FUN_00406C70(0) @0x406C70 (LCG 추첨 PC = 0x406D15, `div esi`)
       G-6 FUN_0043E7F0 @0x43E7F0  생산 유효성
           · 영웅 진영 불일치 / 영웅 사망 쿨다운(ctrl+0x4D0+kind*2) / 영웅 5기 상한(ctrl+0x980)
           · H-TYPEMAX  cur >= typemax           cur = 0x0089A388+(kind+owner*200)*2
                                                 typemax = type_spec+0x34 또는 0x00B3DE70+(kind+owner*0x19C)*2
           · H-AVAIL    0x00B3E000+(kind+owner*0x19C)*2 == 0
           · H-RATIO    cur*100/(ctrl+0x200A) > type_spec+0x32
       G-7 H-CROWD  건물 타일(+0x2A2,+0x2A4) ±5 의 11×11=121셀에서
                    동종·동소유 유닛 >= 7 이면 발주하지 않음
                    (type_spec+0x24 & (0x4|0x400) 인 kind에만 적용)
       G-8 발주 call 0x4AF5E0(unit_id, kind, 1)
```

- **타입 스펙 스트라이드 `0x394`를 바이트로 확정** — `lea` 사슬 9→19→57→229 후 `shl 2` = 916 = 0x394.
  레코드 베이스 `0x009B5228` 기준 `+0x24` 플래그 · `+0x28` 진영 · `+0x32` 비율상한 · `+0x34` 개수상한.
  `+0x32`가 참고 저장소가 `ai_production_ratio_cap`이라 부르는 필드와 **오프셋 일치**한다.
- **`0x66B790`/`0x758` 교차 확인:** G-7이 쓰는 `0x66B81D`(kind)·`0x66B81E`(owner)는
  이 저장소가 독립적으로 확정한 UnitStruct 풀 `0x66B790` + `0x8D`/`0x8E`와 **정확히 일치**
  (`analysis/memory_maps/g2_capacity_boundaries.md`). 두 문서가 서로를 지지한다.
- **생산표 `DAT_004EC514` 실측(원본 파일에서 직독):** rva `0xEC514`는 `.data` raw 범위
  (`0xEC000`+`0xD000`) 안이라 파일에 존재. 종료는 고정 143이 아니라 **다음 레코드 `+0x00` flag ==
  `0xFFFE` sentinel**. **143 엔트리 = 생산 65 + 연구 78**, flag 143건 전부 `0x000F`(4-bit 진영 마스크).
  참고 저장소 문서의 "143 = 78+65"와 **독립 일치**.
  **생산 건물 27종, 건물당 생산 kind 수 히스토그램 = {1종:5, 2종:10, 3종:8, 4종:4}.**
- **자체 결함 정정:** 표 덤프 초판이 종료 워드를 `+0x0E`로 잘못 잡아 365엔트리를 읽었다.
  바이트(`add eax,0x12` → `cmp word [eax-4],-2`)로 `+0x00`임을 확인해 정정, 143엔트리로 수렴.
  **판정 무영향**(정정 후 수치만 사용).
- **게이트 위계 결론:** 8개 게이트 중 **자원을 보는 것은 0개**. 영구 정지 후보는
  **H-RATIO · H-TYPEMAX · H-CROWD** 셋이고, 셋 다 "구성이 동결되면 판정도 동결"이다.
  lap500 N146(144k 소실 14기)이 보인 구성 동결과 정합.
- Fast 게이트: `SAFETY_PASS`(exit 0) · `CONTEXT_PASS` · pytest 결과는 STATUS 「검증 상태」에 기재.
  **이번 lap은 제품 source를 바꾸지 않았다**(2026-09-20 21:58 지시의 면제 조건 명시 충족).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **원인 특정은 아직 안 됐다.** H-RATIO/H-TYPEMAX/H-CROWD가 읽는 표
  (`0x9B5228`, `0x89A388`, `0xB3DE70`/`0xB3E000`, `0x956770`, 풀 `0x66B790`)는 전부
  rva `0xF9000` **바깥**이라 파일에 초기값이 없다 ⇒ **정적으로는 값을 알 수 없다.**
  어느 게이트가 owner5를 tick14,641에 멈췄는지는 읽기 전용 런타임 probe로만 가른다.
- **"농부60·나머지30" 비율 분포는 참고 저장소 주석 출처이며 이 lap이 검증하지 않았다.**
  실제 값 확인 전에는 G2 결론의 근거로 쓰지 않는다.
- **참고 저장소 오염 주의 2건:** (1) `decomp/cleaned/ai_strategy.c`는 "바이너리 미발견" 재현
  전용이라 원본 AI 근거가 아니다(사용 안 함). (2) `bprod_loop_is_owner1_only_0822.md`의
  "owner1 전용"은 **재현 엔진 결함**이고 원본 `FUN_00406B00`엔 소유자 고정 게이트가 없다
  (디스어셈블로 재확인) — 이 결함을 원본/후보로 옮기면 안 된다.
- **독립 검수 없음.** 이 lap은 middle 자기 결과다. 다음 새 세션이 §6 대조와 §5 표 덤프를
  원시에서 재계산해야 2단이 선다.
- **사용자 승인 상태 불변:** (ㄴ) AI/설정 변경 · Q7-B 3단 마일스톤 · (ㄱ) · (ㄷ)는 전부 사용자
  전권 대기. lap404=(가)·F4=(B)는 2026-09-23 04:13 확정(APPROVALS)이나 **착수 허가는 아니다.**
- 이 lap은 **work 카드를 발행하지 않았다** — §7 probe 설계를 인계 근거로 남기되, fixture 축
  G2 work 동결(lap499 §62)과 Q7 미판정 상태에서 카드 발행은 strategy/사용자 판정 사항이다.

## 다음 한 가지

`analysis/memory_maps/ai_production_decision_path_00406770_20260923.md` **§7의 읽기 전용
런타임 probe**로 H-RATIO / H-TYPEMAX / H-AVAIL / H-CROWD / H-STATE를 가른다.
메모리 **읽기만** 하므로 (ㄴ) 승인 대상이 아니고 AI/생산 로직을 건드리지 않는다.
**판정식을 데이터 개봉 전에 고정**하고(lap500 선례), lap500 N144가 확정한 **fixture 결정성**
때문에 같은 조건 새 run을 쌓지 말고 **기존 궤적 위에 관측 채널만 추가해 1회** 실행한다.
lap410 정정2대로 **`0x008990C8`·1200 하드코딩 진단 DLL 채널은 쓰지 않는다**(재배치 후보에서
0기를 보고한다). 모든 쌍이 어떤 이유로든 거부로 분류되면 원인 특정이고, 거부되지 않는 쌍이
남으면 **위 8게이트 밖에 원인이 있다**는 뜻이므로 그대로 보고한다.

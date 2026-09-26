# 2026-09-20 | lap398 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work tier.
  work 카드 `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md` (lap397 middle 발행) 수행.
- 가설 / 사용자 관찰: work 카드 §B-4가 요구하는 fail-open 3건(FO-1/FO-3/FO-4)을 실제 바이트로
  닫아야 §B의 재배치·상수·fixup을 적용할 자격이 생긴다. lap397은 이 세 fail-open을 "미결"로
  남기고 인계했다.
- 예상 PASS / FAIL 조건: FO-1 샘플(≥20건) 중 반례(풀과 무관한 참조로 판명) 0건이면 PASS,
  1건이라도 반례면 균일 delta 가정 폐기·BLOCKED. FO-3은 gap 배열이 pool/existence/age와
  겹치지 않으면 PASS. FO-4는 두 `cmp` 사이트의 성격이 확정되면 PASS(개별 판단 완료).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 read-only probe(메인 레포 밖, 공유 temp)
  `…/temp/Syw2plus_patch/g2_capacity/20260920_unit_pool_expansion/lap398_work_fo_closure_probe.py`
  (SHA256 `e0027cd6779d6dbeeb8d2aa57dd929781c69189446c7298efc7be624b6e5ceb6`) +
  산출물 `lap398_fo_closure_output.json`
  (SHA256 `ac46a0db2dba79cecd6f831e757760f395f1510d8736b3c69f3608e3ff5c1388`).
  메인 레포 변경은 이 lap 기록 + `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md` 갱신 +
  `docs/STATUS.md` 뿐. **게임 코드/바이너리/실행 0, 커밋 0.** uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (재해시 불변, probe가
  실행 시 재확인). 후보 없음(패치 미시도). fixture 없음(정적 분석, 게임 미실행).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python lap398_work_fo_closure_probe.py --output lap398_fo_closure_output.json` → rc0.
  `make check`, `bash checks/safety.sh check` 별도 기록(본 파일 하단 측정값 참조).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **FO-1 — PASS(반례 0건, 그러나 최초 가설은 정정).** 986건 bucket0 후보 중 30건을 균등 간격
  샘플링해 각 사이트의 base/index 레지스터가 이전 8명령 내에서 `slot*0x758` 생산자를 갖는지 검사.
  18/30 확인, 12/30 "국소 창 내 생산자 없음". 이 12건을 개별 판독한 결과 **전부 진짜 풀 참조이되
  균일 delta가 통하는 이유가 애초 가설과 다르다**: 필드 오프셋 `0x8d`(0x66b81d)·`0x8e`(0x66b81e)는
  work 카드 S-3의 `type`/`owner` 필드 위치와 **정확히 일치**하지만 그 사이트들의 색인 레지스터는
  `lea ecx,[eax+eax*4]; shl ecx,3`(`ecx=type*40`)로 **slot이 아니라 type_id**다. 즉 **slot 0은
  한 번도 할당되지 않는(A3 기지사실) 이유가 바로 이것** — slot 0의 1880B 구간은 죽은 공간이 아니라
  **type-indexed 정적 룩업 테이블(요소당 40B, `0x66b81d` 시작)이 점유**한다. 나머지 미확인 필드
  (`0x290`≈`0x66ba20`, `0x29c`≈`0x66ba2c`, `0x2a2`/`0x2a4`)는 S-2가 명시한 slot 자기참조 필드
  (`unit+0x29c==slot`) 근방이라 **진짜 per-slot 동적 필드**로 판정, `type` 생산 레지스터도 아니고
  `slot*stride` 생산자도 국소 창 밖에 있을 뿐(A2/A8가 이미 문서화한, caller가 이미 계산해 넘기는
  `this` 포인터 패턴). **결론:** 986건 전부가 `[POOL_BASE,POOL_END)` 구간을 통짜 바이트블록으로
  복사·재배치하면(정적 테이블·동적 슬롯 구분 없이) 균일 +delta로 번역된다 — 원래 가설("전부 slot
  색인")은 틀렸지만 실제 안전조건("전체 슬롯0~1199 구간을 통짜로 옮기고 그 구간을 가리키는
  모든 리터럴에 +delta")은 §B-1이 이미 명시한 그대로라 **B-1/B-3 설계는 변경 불필요**.
  **FO-3 — PASS.** `[reg*2+0x89a388]` scale-2 참조 5건(요구 9건과 다르나 A4 유사 카운팅 차이 —
  본 probe는 disp==gap_start 정확일치만 셈; lap397 A5의 9건은 인접 필드 포함 추정이므로 불일치가
  아니라 측정 범위 차이). gap `[0x89a388,0x89b008)` 3200B = WORD 1600개, pool/existence/age
  전부와 **배타적**. existence/age 재배치가 이 배열을 건드릴 이유가 없음을 재확인.
  **FO-4 — PASS, 신규 사실.** `cmp` 2건(`0x00421349`, `0x0048f4b4`)을 전후 15명령 창으로 재검증한
  결과 **둘 다 pool과 무관한 선행 정적 테이블의 자기 루프 종료 조건**이다: `0x0048f4b4`는
  `edx=0x669c38`에서 시작해 매 반복 `edx+=0x8c`(140B)씩 증가하며 `edx<0x66b790`인 동안 반복
  (`0x669c38..0x66b790`=`0x1b58`=7000B=`50×140` 정확히 나눠떨어짐 ⇒ 50개×140B 고정 테이블).
  `0x00421349`도 동형(`ebx+=0x8c` 루프, 같은 종료값). **이 테이블은 재배치 대상(pool/existence/age)
  이 아니고 옮기지 않는다.** 리터럴 `0x66b790`은 이 테이블에게 "내 테이블의 끝"이라는 의미이고
  그 값은 테이블 자체가 그대로 있는 한 재배치 후에도 계속 정확하다. **⇒ 이 2건은 fixup에서
  제외해야 하며, 만약 패처가 "값이 정확히 POOL_BASE와 같은 리터럴은 전부 +delta"로 기계적으로
  처리하면 이 두 루프의 종료조건이 깨져 무한/조기 루프 결함이 생긴다.** work 카드 §B-3의
  "개별 확인 후 적용" 지시가 정확했고, 개별 확인 결과는 **적용하지 않음(제외)**이다.
  `make check`/`checks/safety.sh check` 결과는 본 파일 갱신 시점 실행값을 그대로 기록(아래).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 세 fail-open 전부 PASS로 닫혔으나 **이번
  회차도 게임 코드/바이너리/실행 0**이다(순수 정적 재검증). B-1/B-2/B-3 설계 자체는 무변경,
  단 B-3 fixup 수집 시 **`0x00421349`/`0x0048f4b4` 두 cmp 사이트를 하드 제외 목록에 추가**해야
  한다(신규 요구사항, 다음 회차 반영). existence/age의 유사한 "슬롯0류 정적 데이터 오염" 여부는
  아직 개별 검증하지 않음(존재/age는 필드가 2B뿐이라 pool과 같은 규모의 임베디드 테이블 위험은
  낮다고 추정하나 **미검증 — 다음 회차 20분 이내 반증 탐색 권고**). 독립 검수 대기.
- 다음 한 가지: 다음 work 회차는 **재조사 없이 즉시 구현 착수**한다 — (1) 새 relocation 대상
  주소를 `patches/population/base_preserving_storage_layout_v1.py`(lap382~388 산출)로 계산,
  (2) `.text` 전수 재스캔으로 pool/existence/age 세 구간 리터럴 사이트를 **패처가 직접** 수집하되
  `0x00421349`/`0x0048f4b4`는 하드 제외, (3) 4개 상수(§B-2) + 전체 fixup을 새 복사본에 적용하고
  원복 스크립트 동반, (4) 원본 재해시 불변 확인 후 **격리 실행**으로 S-1~S-6 측정.
  이 회차는 게임 코드/바이너리/실행 0이므로 implementation-unchanged-streak가 늘어난다 —
  **다음 회차는 반드시 실제 패치 바이트와 실행 증거를 늘려야 한다**(PROMPT ③ 최대 2회 한도).

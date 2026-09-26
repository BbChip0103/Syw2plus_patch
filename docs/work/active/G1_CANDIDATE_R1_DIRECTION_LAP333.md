# lap333 Astra — 후보 R1 관측 우선, 실행은 middle/work로 분리

2026-09-12 / Codex gpt-6-astra / high / major direction/master-plan.
제품 계약 DESIGN §1~4와 APPROVALS 2026-09-12 01:03을 유지한다. M1 내부 연구 방향 결정이며
M1 종료·M2 진입·제품 승인·새 게임 실행은 없다. 현재 큐는 STATUS에만 둔다.

## 1. 결정과 이유

**선택 2: 1600×1200 출력 후보의 R1형 읽기 관측을 우선한다.**
원본 R1 n=1은 origin (240,145,8)을 관측했지만 후보의 창/입력/로드 전이를 입증하지 않는다.
Stage B 전체 재개 전에 후보에서 같은 진입의 관측 가능성을 좁게 확인한다.
이는 S1 결정성이나 WM_CLOSE 수리의 대체물이 아니며, 이후 Stage B의 선행 조건도 삭제하지 않는다.
선택 1(즉시 Stage B)은 S1/F2-R2·WM_CLOSE 미해결 상태에서 범위가 더 크므로 이번 카드에서 제외한다.
선택 3(원본 R1 n>1)은 후보 차이를 측정하지 못하므로 이번에는 허용하지 않는다.
같은 정적 증명 반복과 문서 추가를 구현 진전으로 세지 않는다. 다음 측정 대상은 후보 한 run의
실제 root/content/출력 구분·입력 변환·PS/pending/origin 시계열이며, 아직 그 데이터는 없다.

## 2. 허용 상한과 발효 조건

현재 실행 허가는 **0회**다. 아래 조건을 전부 충족하면 후보 연구 1 fresh run만 발효한다.
새 middle 봉투 ACCEPT → work 최소 하네스 변경/검사(필요한 경우) → 다음 새 middle 독립 검수
→ work 정확히 1회 실행 → 다음 새 middle artifact 판정 순서다. 이 세션은 후속 모델을 호출하지 않는다.

| 항목 | 상위 결정 | middle이 실행 전에 고정할 것 |
|---|---|---|
| 후보 | 기존 G1 원본 구도 정수2배 출력 경로만; 새로운 렌더러/게임 패치 금지 | 기존 빌드/설정 출처, 원본·사본 EXE와 DLL/설정 SHA, 실행 명령과 실제 주입 대상 |
| 격리 | 새 전체 사본·새 prefix·빈 display·소유 PID만 | prepare와 실행 artifact의 역할 구분, 소유 확인·실패 보존·종료 명령 |
| 시간 | 총 ≤90초, 40/20/15/15 상한 배분 유지 | 각 구간 시작/끝·단일 deadline·종료 15초 확보; 준비 복사 포함 범위 명시 |
| 입력 | PS9 이후 연구 클릭 최대 1회, 재클릭 0 | 후보 창 구조에서 client→root 변환과 좌표 출처; 원본 (296,505) 또는 2배 값을 무근거 복사 금지 |
| 읽기 | process_vm_readv만, PS/pending/origin 원시 표본 | 각 필드 주소/폭/바이트 근거·read 오류·불일치 처리·PS35 도달 식의 후보 적용 가능성 |
| 출력 | 별도 후보 연구 artifact, PNG/제품 comparator 소비 0 | run ID·variant·SHA·실제 창 크기·입력 수·단조시계열·cleanup·classification |

G1은 내부 렌더링 800×600의 정수2배 출력도 허용한다. 후보 content child가 반드시1600×1200이어야
한다는 새 조건을 만들지 않는다. root1600×1200만으로 확대 후보라고 판정하지도 않는다.
후보 식별은 wrapper/DLL/설정과 실제 로딩·창/입력 증거를 연결해야 한다.
기존 원본 R1 경로의 root=1600×1200/content=800×600 가드는 후보 검증 없이 일반화하지 않는다.
기존 lap332 probe는 원본 artifact 전수 1건을 전제한다. 원본 artifact·원본 전용 probe를 보존하고,
후보 artifact를 별도 이름/variant로 분리하여 그 과거 exact-once 범위를 바꾸지 않는다.
새 계약의 후보 run 수 1건은 별도 검증한다. 기대 SHA/건수를 자동 수정해 기존 검사를 통과시키지 않는다.

## 3. 검증과 중단 계약

PASS(연구 수집 유효성) = 검수한 후보/하네스 SHA 일치 + 소유/좌표 확인 + 허용 입력 수 준수 +
독립 PS 도달 근거 + 일관된 pre/post 표본 + 예산 준수 + cleanup 성공 + raw artifact 보존.
값 분류는 이 PASS와 분리한다. A/B 예상 좌표는 후보의 실제 논리 크기/스프라이트 근거를 먼저
명시하며 원본 A=(240,145)를 후보 정답으로 고정하지 않는다. 유효한 다른 값도 연구 결과다.
미도달·전역 미변화·timeout·수집 실패를 구별하고 UNKNOWN/실패 원인과 원시 표본을 남긴다.
pre==post·불완전 read·일관성 미확보는 성공으로 승격하지 않는다. 실패 시 연장/재시도 0회.
새 run은 결정성(n>1), hitbox 전체, 실제 save/load 완료, 동일상태 pair, WM_CLOSE 해결,
G1 합격을 증명하지 않는다. PS 레지스터 store 33건·계산/간접 writer fail-open도 유지한다.
필수 검사 예상 밖 실패, 근거 불명확/충돌, 마일스톤 경계이면 변경 보존→ESCALATE_SOL→종료한다.

## 4. 함께 요청된 결정

- **W3: 이번 카드에서 재pin 불허 유지.** 현 probe의 알려진 과거 실패를 PASS로 기록하지 않는다.
  후보 연구가 W3에 의존한다면 우회/자가 갱신하지 말고 정확한 의존 지점을 증거로 반환한다.
- **40/20/15/15: 보수적 상한 유지.** 4.278초는 n=1 전체 elapsed이며 구간별 분포 근거가 아니다.
  이번 후보 raw 기록에 구간별 시각을 남기되 자동 재배분·총 시간 확대를 하지 않는다.
- **원본 n>1: 불허 유지.** 후보 한 run은 원본 재현성 표본으로 합산하지 않는다.
- **N8/N9:** PS 9/35뿐 아니라 40/150/180 등 모든 표본을 공개하고 준비 manifest와 실제 run 설정을
  별도 출처로 표시한다. (W) player_offsets WORD 정정은 별도 대기 카드로 유지한다.
- Stage B/PNG·baseline/golden 갱신·원본 쓰기·ptrace/int3/디버거 계측·새 의존성·G2~G4 확대 금지 유지.

## 5. 선행 증거와 역할 인계

lap332 probe를 수정 없이 1회 재실행: rc0, failures=[], stdout SHA256
`5efe92a02f3b6a42a8dee5bdf98a7e00e5d941c7549fb72a7a96bf956cc31afc`.
이는 기존 검수 알고리즘의 재현이며 새 독립 알고리즘/새 runtime 검증이 아니다.
별도 PE section 매핑과 Capstone으로 C1을 다시 읽었다: 0x4233BF cmp eax,0x28,
0x4233C2 jg 0x42351F, 0x4233C8 je 0x423515, 이후 PS-1 테이블. 로그는
`logs/lap333/c1_disassembly.txt`. 원본 SHA는 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
과거 ACCEPT는 유지하되 C1이 모든 상태값 의미나 간접 writer 배제를 증명한다고 확대하지 않는다.

후보 식별·좌표 변환·PS 판정식 적용 가능성은 이번 상위 문서만으로 미확정이므로 실행을 보류한다.
승격 middle은 §2~3을 파일/함수/실패 검사까지 구체화하고 ACCEPT 또는 근거 있는 BLOCKED를 기록한다.
그 전에는 work 구현 카드를 발효하지 않는다. 실무 모델은 Luna/Sonnet5 high이며 최종 자가 승인은 금지한다.
이번 사용자 요청의 승격 파일명 ESCALATE_SOL을 사용한다. MODEL_ROUTING의 현재 middle 선택은 Opus5,
사용자 메시지는 Sol 승격을 명시하므로 runner는 실제 provider/model을 기록하고 충돌 시 자동 대체하지 않는다.
Astra 방향 확정은 middle 봉투 승인·제품 승인과 별개이며 프로세스 exit0으로 어느 승인도 대신하지 않는다.

## 부록 A — 소비한 lap332 ESCALATE_SOL 원문

원문 SHA256: `b2a6a107bdb3ff90313491f82cd2907e84b62d3bd4d964903b56ea403760c106`

```markdown
# ESCALATE — lap332 middle → Astra (상위 방향)

작성: 2026-09-12 / lap332 / Claude Code claude-opus-5 / high / middle.
소비 규칙: 다음 세션이 이 파일을 **부록 A로 소비**하고 삭제한다(lap325→lap326 §부록 A 선례).

## 왜 올리는가

lap332가 lap331 R1 관측을 **ACCEPT**해 R1 연구 레인이 닫혔다. 그러나 그 다음 카드는
middle 권한 밖의 **상위 방향 선택**이고, 현재 STATUS의 "다음 한 가지"는 이 검수로 소진됐다.
이 lap은 구현도 Stage B 실행도 시작하지 않고 현재 변경(문서·probe)만 보존한다.

## 확정된 입력 (lap332가 1차 출처로 재확인, 승격 아님)

- R1 단일 관측 성립: `OBSERVED/REACHED_CHANGED`, PS 9→35, pending 0→34, origin `(0,0,0)`→`(240,145,8)`,
  elapsed 4.278s, cleanup OK, 실행 정확히 1회(전 저장소 artifact 1건), PNG 0.
- 후보 A `(240,145)`가 run 자신의 스프라이트 헤더 `[9,320,310,1]`로 재계산해 일치하고,
  `tag==8`이 `push 8` 경로를 지목해 형제 경로(`push 0x3E8`)를 배제한다.
- **정정 C1(수치 영향 0):** 디스패처는 테이블 진입 전에 `cmp eax,0x28; jg; je` 사다리를 갖는다.
  관측된 PS `40/150/180`은 찢김이 아니라 정당한 상태값이다. 판정식 `PS==35`는 영향 없음.
- **이 관측은 content 800×600 원본 baseline이다.** 1600×1200 구성에서의 origin은 여전히 미관측.

## Astra가 골라야 할 것 (middle이 임의로 고르지 않는다)

1. **Stage B 재개** — APPROVALS 2026-09-12 01:03이 이미 승인한 "격리된 원본/1600×1200 후보 실제 비교를
   증거 성립까지 bounded repair → fresh validation". 미해결 WM_CLOSE 결함과 S1/F2-R2 결정성이 앞에 있다.
2. **후보 쪽 R1형 읽기 전용 관측 우선** — 같은 판정식·같은 봉투로 1600×1200 후보에서 origin을 읽어
   "원본 A → 후보에서 어떻게 되는가"를 먼저 고정한다. 후보 산출·봉투 재발행이 선행되어야 한다.
3. **R1 재현성(n>1) 허용 여부** — 현재 재클릭은 금지다. 결정성이 필요하면 Astra가 금지를 풀어야 한다.

## 함께 묶여 있어 단독 결정 금지인 항목

- **W3 재pin**(lap300 §4): 자가 갱신이라 middle/work 단독 금지, Astra/사용자 결정 대기 — 변동 없음.
- **배분 40/20/15/15 재평가**: 실측 단일 표본 4.278s만으로는 가정을 못 바꾼다.
- **(W) `player_offsets.md` 정정**(`0x00B92CC0`은 byte 아니라 WORD·'다음 상태 요청'): 별도 카드로 대기.
- **N8/N9**(lap332 신규, 수치 영향 0): 기록 공개 누락과 manifest `runtime_config` 오독 위험.

## 승격 작업자가 이어서 검증할 것

- lap332 probe `docs/history/laps/probes/20260912_lap332_middle_lap331_r1_artifact_probe.py`
  (`e8dc8c75…a1f9c367`, stdout `5efe92a0…6cc31afc`)를 1회 재실행해 `failures=[]`·rc0을 독립 재현한다.
- 정정 C1을 원본 바이트에서 독립 재유도해 lap326 §1 서술과의 차이를 확인한다.
- 위 세 선택지 중 하나를 근거와 함께 확정하고, 선택한 레인의 봉투(예산·실패모드·금지사항)를 발행한다.

## 이 파일이 아닌 것

제품 G1 합격, Stage B 허가, 마일스톤 종료/이동, 사용자 승인이 아니다. G2~G4 증거는 0이다.
`make check` 368 passed·`SAFETY_PASS`·probe rc0은 계획 승인도 제품 검증도 아니다.
```

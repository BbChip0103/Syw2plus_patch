# 2026-09-12 | lap 334 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code / `claude-opus-5` / high / middle(진단·계획·확인).
  게임 코드 hands-on 수정 없음. 사용자 지시의 Sol 승격을 MODEL_ROUTING의 Opus5 middle 선택으로 수행했고
  몰래 다른 모델로 대체하지 않았다. 실무 구현은 work tier(Luna/Sonnet5 high)로 넘긴다.
- 가설 / 사용자 관찰: (1) lap333이 STATUS 편집안 길이 assert(131>130)에서 중단했으므로 디스크 STATUS는
  손실 없이 130줄 계약을 지키고 있을 것이다. (2) lap333 §5가 "미확정"이라 적은 후보 식별·좌표 변환·
  PS35 적용 가능성은 이미 보존된 1차 증거(고정 ini pin, lap148/lap154 run, 동일 EXE 바이트)로 확정 가능하며,
  그렇다면 후보 R1 봉투를 BLOCKED가 아니라 ACCEPT로 발행할 수 있다.
- 예상 PASS / FAIL 조건: PASS = STATUS 130줄·블로커 1개·보존본 SHA 일치·변경 줄이 인계 3개 영역뿐,
  C1을 디스어셈블러 없이 원본 바이트에서 재유도, 후보 좌표 규약이 보존 run 두 건으로 판별됨,
  Fast/safety 통과, 실행·입력·쓰기 0. FAIL = 블로커/미결 유실, C1 불일치, 좌표 근거 충돌(그 경우 BLOCKED 반환).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`).
  신규 `docs/work/active/G1_CANDIDATE_R1_MIDDLE_ENVELOPE_LAP334.md`
  (221줄, 부록 A 포함; 최종 현물 SHA는 다음 세션이 직접 계산한다),
  신규 probe `docs/history/laps/probes/20260912_lap334_middle_candidate_r1_envelope_probe.py`
  `698993b8007999f0b0008fecc057df9f75315cf530e839f8afc5798ba55f7e2c`,
  신규 이 기록, 신규 `docs/history/laps/20260912_status_lap333_compaction.md`(lap334 편집 전 STATUS 원문 보존),
  갱신 `docs/STATUS.md`(130줄, 블로커 섹션 1개), 제거 `loop/ESCALATE_SOL`(원문 `299a1f1789f340bbb676de516aef4b8e8d5c0e3ee30b61144e04505585572a2d`를
  봉투 §부록 A로 소비·보존). **게임 코드/실행 하네스 변경 0** — `tools/runtime_env.py`는
  `997ff15b13115ccebd9d8832b3b066add589b755d9cc6e8a77d987696cc46eed`로 lap330 검수 SHA와 동일하다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 실측 불변(읽기 전용).
  후보 정의 = 동일 EXE + 고정 프로필(ini old `918e7043…aeea5a2` → candidate `f0ce9e64…2566785`).
  이번 바퀴는 **게임 실행 0회**이므로 환경/플레이어/지도/군대/fixture는 N/A. G2~G4 SKIP(증거 0).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260912_lap334_middle_candidate_r1_envelope_probe.py` → rc0,
  `failures=[]`, stdout SHA256 `d0b3c7225a904c2fc6aa066624c198438ba4faa275a3c9173cadec31e7eba893`
  (연속 2회 byte-identical). `make check` → 368 passed(56.31s), Ruff/compileall/mypy/CONTEXT_PASS, rc0.
  `bash checks/safety.sh check` → SAFETY_PASS. 캡처/PNG **0장**, 게임 실행·입력·메모리 쓰기 **0회**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  (1) **문서 실패 검수 PASS.** 현재 STATUS 130줄, SHA `b2d2c230…7ee1e5d`, `## ` 5개, 블로커 섹션 1개.
  보존본 body SHA `ec10aaec…8982cbbf`·130줄 일치. 줄 단위 차이는 0-based `[20,21,22,23,25,128]`뿐
  (다음 한 가지 4줄 + 블로커 머리말 1줄 + 바퀴 기록 1줄). 블로커 본문·미결·반려·provenance 유실 0.
  (2) **C1 CONFIRMED(독립).** `0x4233B8` 39바이트 실측 `0fbf0518d84e00 83f828 0f8f57010000 0f8447010000
  48 83f822 0f87f0feffff ff248538374200`, rel32 3건 계산으로 `jg 0x42351F`/`je 0x423515`/`ja 0x4232C8`,
  테이블 `0x423738`. **추가:** 34번 엔트리 = `0x0042341B` → PS35 판정식 수치 영향 0 재확인.
  (3) **좌표 변환 확정.** lap148(`f066bd82…d90e8`) scaled ×2 클릭 → PS9/tick0 FAIL,
  lap154(`bd74b47f…cae11`) unscaled `(184,560)` → PS9→PS7→PS3 PASS. 둘 다 client 1600×1200·scale [2,2].
  ⇒ 후보 클릭은 `content_crop + 논리(800×600) 좌표`, 배율 곱 없음. 현재 하네스 규약과도 일치.
  (4) **후보 식별 확정 가능.** 고정 ini pin + `ddraw=n,b` + private `game/ddraw.dll` 로드 단언 +
  prepare의 지원 DLL 해시. (5) **PS35 적용 가능.** EXE byte-identical·image base `0x400000`·정적 전역.
  (6) 봉투 **ACCEPT** 발행(§4~§12), 실행 예산은 여전히 **0회**. 마일스톤 종료/이동·제품 승인 없음.
- 자기 정정(N12, 수치 영향 0): 이 probe의 초판은 lap333 보존 검사를 **살아 있는 `docs/STATUS.md`**와 비교해서,
  이번 바퀴가 STATUS를 갱신하자 즉시 실패했다(W3와 같은 자기무효 함정). 기대값을 고쳐 통과시키지 않고 비교 대상을
  **불변 압축본 두 개**(`…status_lap332_compaction.md` 종료본 / `…status_lap333_compaction.md` 종료본)로 바꿨다.
  그 결과 판정은 이후 바퀴의 STATUS 편집과 무관하게 재현된다. 같은 이유로 probe 출력에서 살아 있는 STATUS
  해시도 제거했다 — 출력 SHA가 STATUS 편집마다 바뀌면 기록한 stdout SHA가 다음 검수자에게 무의미해진다.
  검수 대상 STATUS(편집 전) SHA는 `b2d2c230…7ee1e5d`(130줄)이고 초판 SHA는 이 문단이 유일한 기록이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Fast 368 passed·SAFETY_PASS·CONTEXT_PASS,
  보호 대상 원본 SHA 불변, 하네스 SHA 불변. 남은 위험: (a) 후보 run은 결정성(n>1)·hitbox·실제 save/load·
  동일상태 pair·WM_CLOSE·S1/F2-R2를 증명하지 못한다. (b) PS 레지스터 store 33건 fail-open과 계산/간접
  writer 미배제는 후보에서도 열려 있다. (c) **N10**: 압축본 파일명 규칙(`status_lapN_compaction`=lapN 종료
  시점)은 lap332 파일 제목 "lap333 편집 전"과 같은 뜻이며 규칙을 바꾸지 않았다. (d) **N11**: 하네스의
  `input_scale`/`scale`은 기록용이며 클릭에 곱해지지 않는다 — 후보 artifact에 `scale_applied=[1.0,1.0]`을
  명시해 오독을 막는다(이름 변경은 이번 범위 밖). (e) 후보 native ddraw teardown 결함(P6)은 이 카드가
  건드리지 않는다. 독립 검수: 이 봉투는 **다음 새 middle이 work 구현을 검수**한 뒤에야 1 run으로 이어진다.
  사용자 마일스톤 승인 없음. 자기 승인 없음.
- 다음 한 가지: **work tier(Luna/Sonnet5 high)가 봉투 §11을 구현한다** — `tools/runtime_env.py`에
  `g1-r1-candidate-load-origin`를 추가(원본 경로 거동 불변), 기하/모듈 게이트·무배율 클릭·
  `r1_load_origin_candidate.json` 분리·네 실패 모드+`BLOCKED_PRECONDITION`·원복 포함 cleanup,
  오프라인 회귀 테스트(×2 클릭 방지 단언 포함), `make check`+SAFETY_PASS. **실행 0회**, 커밋 0.

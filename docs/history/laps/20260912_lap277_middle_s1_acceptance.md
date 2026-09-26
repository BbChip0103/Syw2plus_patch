# 2026-09-12 | lap277 | G1 S1 수용 계약 확정과 work 조건부 승인

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high,
  middle tier(진단·계획·컨펌). 하위 모델·유료 subagent 호출 없음. 게임 코드 hands-on 없음.
  기록 lap 번호는 읽기 전용 `loop/.lap_counter`=277(러너 evidence의 lap=276과 다름, PROMPT 규칙대로 파일 값 사용).
- 가설 / 사용자 관찰: lap276 Astra의 승격 사유 — "lap271 §3 요약식의 부정 조건은 결측을 배제하지
  못한다" — 이 참인지 기계로 판정할 수 있다. 사용자 신규 관찰 없음. INBOX 신규 지시 없음.
- 예상 PASS / FAIL 조건: PASS=lap276 기록 SHA 전부 일치 + 측정식이 불충분함을 재현 가능한
  offline 케이스로 보이고 여섯 항목의 관측 출처·양성 조건·결측 규칙을 문서로 확정.
  FAIL=SHA 불일치, 필수 게이트 실패, 또는 측정식이 실제로 충분해 승격이 근거 없음으로 판명.
- 변경 파일 / source fingerprint / 커밋: **uncommitted**(LOOP_ALLOW_COMMITS=0). 게임/도구 코드 0건.
  신설 `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`
  `4d779ba6f9073caba67ebb45d06e8bc9b16520ab5d011f7cd205a9647387a1e2`
  신설 `docs/history/laps/probes/20260912_lap277_middle_s1_formula_probe.py`
  `0ab66933ba1a4535d7f0167c282dca8f0db9130407d6b3a72e8f7235941b6189`
  갱신 `docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`(§3 supersede 주석 추가, 원문 보존)
  `1008b1144f5dc88d18ebd2d1808b8f1fa519afbd2e829ccfde7d58dea7bcaed3`
  갱신 `docs/STATUS.md`(편집 전 `c9c85a51f0e90c95524352f27145df9cd9494195734aee47c50ac444c157dbb1`)
  갱신 `loop/ESCALATE_SOL`(lap277 항목 prepend, 이전 원문 전체 보존), 본 기록.
  `tools/runtime_env.py` / `tools/compare_g1_stage_b.py` / `tests/` / 원본 EXE는 **바이트 무변경**.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(SAFETY_PASS로 확인).
  후보 없음. 환경 Linux `.venv`, offline 합성 JSON만. 게임/Wine/Xvfb/PNG **0회**.
  활성 플레이어/지도/군대 해당 없음(런타임 미실행). fixture=probe 내부 합성 evidence 2쌍씩 7케이스.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap277_middle_s1_formula_probe.py`
  → `logs/lap277/s1_formula_probe.json` `d64676522417a71cfef97e9d563a1cfbecd7d4757757061219c98b28b0c98cb0` (exit 0)
  `.venv/bin/python docs/history/laps/probes/20260912_lap275_middle_f3_r2_r1_review_probe.py`
  → `logs/lap277/f3_review_recheck.json` `4672c78c34d6f8d083fc00ca66ce31fa0b04541bd361a0d18cf8e8f80fb9d770`
  (lap276 `logs/lap276/f3_review.json`과 **동일 해시** = 바이트 동일 재현)
  `make check` → `logs/lap277/make-check.log` `4f0fce02428dec605bca4b0b2add473636b14e8654291bee18117ab0c9a59be2`
  문서 갱신 후 재실행 `make check` → `logs/lap277/make-check-final.log`
  `232c9bbc478077772a5b1ee26080262467fbb673a4e9100a2edce03aa88508fa` (291 passed 47.31s, CONTEXT_PASS, SAFETY_PASS)
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `logs/lap277/safety.log`, SAFETY_PASS. 캡처 없음.
- 측정값 / 판정:
  make check **291 passed (47.46s)**, Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS.
  측정식 probe 7케이스 자체검사 **failures=[]**, verdict=`formula_insufficient`.
  · control_identical → overall PASS (케이스가 공허하지 않음을 보증)
  · blind_to_items_1_5_6 → nation/비선택 slot id/절대 selection count/scene camera/scene tick/
    minimap 직전 camera가 전부 달라도 **overall PASS** → 항목1·5·6 미포함 **확인(FAIL of formula)**
  · blind_to_foreign_owner → owner=2 개체가 후보에만 있어도 **overall PASS**
  · multiplicity_owner01_control → UNKNOWN_SCENE_MISMATCH (항목2·3 중복/개수는 owner0/1에서 **덮임**)
  · vacuous_missing_stage / vacuous_missing_selection_count → lap271 측정식 **참**인데 overall INCONCLUSIVE
    → 부정식의 **공허한 참 확인**
  · slot_demotion_control → 두 stage UNKNOWN_SLOT_CORRESPONDENCE (F2-R2 강등 규칙 **생존 확인**)
  판정: lap271 §3 요약 측정식 **FAIL(불충분) → 반려**. lap276 승격 사유 **타당**으로 확인.
  lap276 기록 SHA 10/10 일치 **PASS**. lap275 범위 승인 재현 **PASS**(새 검수기는 작성하지 않음 = 부분).
  work 인계 **조건부 APPROVE**(LAP277 §4 표 충족 조건).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  회귀 없음(도구 코드 무변경, 291 passed 동일 집합). 새 PASS 경로 생성 0, slot 강등 규칙 무변경.
  남은 위험: (a) `scene.owners`가 `range(8)`이고 offsets가 owner0/1만 봐서 **owner8~15는 장면 서명에
  구조적으로 안 보임** — G3에서 반드시 재론, 이번에 수리하지 않음. (b) 대체 측정식 (B)는 기계 검사가
  아니라 **기록 의무**라 사람이 빠뜨릴 수 있음. (c) tick 허용 오차는 미정이며 상위 권한.
  (d) M-d/M-e, R17/R31, R6-B-R2, 나머지 offline 8건은 미결 주차 그대로.
  독립 검수: 이 문서 자체는 **다음 새 middle**이 검수한다. 자기 승인 아님. 사용자 마일스톤 승인 없음.
  제품 G1~G4 신규 증거 **0**. Stage B/runtime 예산 승인 없음.
- 다음 한 가지: STATUS의 "다음 한 가지"만 참조 — work tier 새 세션의 S1 저장/불러오기 **정적** 조사
  1바퀴, LAP277 §4 산출물 표 여섯 행 작성. 게임/Wine/Xvfb/Stage B 예산0.

## 해시 (세션 종료 시점)

- `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`: `4d779ba6f9073caba67ebb45d06e8bc9b16520ab5d011f7cd205a9647387a1e2`
- `docs/history/laps/probes/20260912_lap277_middle_s1_formula_probe.py`: `0ab66933ba1a4535d7f0167c282dca8f0db9130407d6b3a72e8f7235941b6189`
- `logs/lap277/s1_formula_probe.json`: `d64676522417a71cfef97e9d563a1cfbecd7d4757757061219c98b28b0c98cb0`
- `logs/lap277/f3_review_recheck.json`: `4672c78c34d6f8d083fc00ca66ce31fa0b04541bd361a0d18cf8e8f80fb9d770`
- `logs/lap277/make-check.log`: `4f0fce02428dec605bca4b0b2add473636b14e8654291bee18117ab0c9a59be2`
- `docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`: `1008b1144f5dc88d18ebd2d1808b8f1fa519afbd2e829ccfde7d58dea7bcaed3`
- `docs/STATUS.md`: `d3aaf0a64e94bc30493b471f39275ac754b035f935d3b7df5249a2680c8700ff`
- `loop/ESCALATE_SOL`와 본 기록 자체의 해시는 세션 종료 후
  `sha256sum loop/ESCALATE_SOL docs/history/laps/20260912_lap277_middle_s1_acceptance.md`로 재계산한다.

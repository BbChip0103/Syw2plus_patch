# 2026-09-23 | lap 508 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle(중간계획·컨펌).
  카드 `docs/work/active/G2_Q8_USED_CEILING_QUANTIFICATION_LAP505.md`(W29) §5의 **middle 1회
  독립 검수**. 이 lap으로 §67 예산(work 1 + middle 1)이 **소진**된다.
- 가설 / 사용자 관찰: lap507(work)이 보고한 8 owner `used` 천장표와 `k=8 ⇒
  `NATURAL_ARRIVAL_ARITH_INFEASIBLE`가 원시에서 재현되는가. work 자기 결과이므로 2단이 아직 없다.
- 예상 PASS / FAIL 조건(사전 고정): `ceiling_table.json`의 `ceiling`/`per_kind`/`sum_typemax`/`k`/
  `theoretical_max` 필드를 **쓰지 않고** `type_specs.json` + `production_table.json`만으로 다시
  계산해 불일치 0이면 측정 ACCEPT. 1건이라도 어긋나면 REJECT. 해석(단서·라벨)은 별도 판정.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source **0건** 변경, 게임 신규
  실행 **0회**(lap507 완주 산출물 재계산만). 이 lap이 쓴 파일: 이 문서,
  `loop/ESCALATE_SOL` §69, `docs/STATUS.md`. 재계산 산출물은
  `temp/Syw2plus_patch/g2_capacity/20260923_lap508_middle_w29_recheck/`
  (`recalc_lap508.py` SHA `d621f000abbe3c4db61c8b6d6bc13b544ca17ec95fef50bc23e855bb8ac71c21`,
  `recalc_consolidated.txt` SHA `24bb0fadeec78b53672af5296fc5453354c435aa7a59b2742ce7e52290d6332d`,
  단계별 `recalc_step1..4.txt`). uncommitted(`LOOP_ALLOW_COMMITS` 미설정/0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 재계산 대상 원시는 lap507
  실행분 — 원본 `b56986e0…`, 후보 `a10024de…`, bridge dll `b4a8bad1…`, 격리 Wine prefix
  Xvfb `:4001`, 140×140(seed 42), 8인 AI 전원 활성, goal
  `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`. 원시 디렉터리
  `temp/Syw2plus_patch/g2_capacity/20260923_lap506_w29_used_ceiling/`
  (`ceiling_table.json` SHA `3f0e44f2…`, `type_specs.json` SHA `a23ba1d7…`,
  `production_table.json` SHA `7dbe6613…`, `samples.jsonl` SHA `f0450f93…`, 721줄).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 recalc_lap508.py`(위 경로, exit 0).
  게이트: `make check` → **796 passed / ruff·mypy 통과 / `CONTEXT_PASS`**,
  `checks/safety.sh check` → **`SAFETY_PASS`**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **집계 재계산 = `ACCEPT`(2단 성립).** owner 8/8 전부 일치, **불일치 0**:
    천장 [2445, 1070, 2445, 2050, 2445, 1190, 2050, 2445] 재현, `per_kind` 전 항목
    (`cost`·`typemax_eff`·`contribution`) 일치, `sum_typemax` 일치, 건물 종 수 일치,
    **k=8** 재현, 이론최대 **8,077**(Σtypemax 568) 재현.
  - 카드 §1 채택 조건 재확인: `cost[27]+cost[76]=20`, `cost[80]=0` — 둘 다 일치.
  - 교차 원시 대조: `samples.jsonl` 최종 표본의 `used`/`count`가 `ceiling_table.json`의
    `used_final`/`count_final`과 **불일치 0**. 표본 수 721·`final_tick` 24,029·`max_live` 775·
    `max_slot_index` 4,000·U3 불일치 0·`used>5000` 표본 0 — `run_summary.json` 주장과 전부 일치.
  - **신규 반증 시험(lap507 미실시): 721 표본 × 8 owner 전체에서 live `used`가 재계산 천장을
    넘은 표본 = 0.** 천장 모델은 이 실행으로 반증되지 않는다.
  - **해석 판정 = 라벨 유지·근거 강화 + 단서 정정 3건**(아래 N151~N153).
- 신규 관측 (원시 재계산에서 나온 것, lap507 보고에 없음):
  - **N151 — 무능력은 "현 종단 구성"보다 넓다.** 8 owner가 **보유한 건물 종의 합집합**
    {41,44,45,46,47,49,50,51,105}(27종 중 **9종**)을 한 owner가 전부 가져도 천장은 **2,835 < 5,000**.
    27종 중 **18종은 이 fixture에서 아무도 짓지 않았다**(53,54,55,56,58,59,60,61,64,65,67,68,70,
    71,72,74,106,107). ⇒ 카드 §3이 요구한 단서("현 종단 건물 구성 기준")는 맞지만 **보수적**이다.
    자연 도달 불가는 개별 owner의 종단 스냅샷이 아니라 **fixture 전체의 AI 건설 레퍼토리**에서
    온다. W26 §0-3 "건물 계층 부재" 관측과 같은 방향.
  - **N152 — 병목은 건물 "개수"가 아니라 "구성"이다.** 최선 순서로 고르면 27종 중 **7종**이면
    천장 5,072 > 5,000을 넘는다(45→64→53→61→65→67→46). 관측 owner는 이미 **6~8종**을 갖고도
    천장이 1,070~2,445에 그친다 — 고가치 종(64=1,150, 53=900, 61=482, 65=450, 67=445)을
    **아무도 짓지 않았고**, 보유한 45(1,250)·46(395) 외에는 전부 저가치 종이다.
    ⇒ lap507 §5의 "AI가 더 많은 생산건물을 짓지 않는 것이 병목"은 방향은 맞으나 부정확하다.
    정확히는 **"AI가 고가치 생산건물 종을 짓지 않는다"**이며, 이것이 다음 조사의 좁은 표적이다.
  - **N153 — "8 owner 전원 정지"(N141 계열 독법)는 이 실행에서 성립하지 않는다.** tick 18,000
    이후 `used` 증가분: owner0 +325, owner2 +285, owner3 +250, owner4 +135, owner1 +50, owner6 +10
    — **6/8이 창 끝까지 생산 중**이고 **owner4의 마지막 증가는 최종 표본 tick 24,029 그 자체**다.
    정지한 것은 **owner5(마지막 증가 14,625)와 owner7(16,392) 둘뿐**이다. ⇒ lap500 N145의
    "창 절단" 강등을 **owner 단위 원시로 재확인**하고, lap501·502·504가 owner5만 보고 추적한
    "AI 생산 정지"는 **owner5 국소 현상의 일반화**였다.
  - 부수 관측: `used`는 누적이 아니라 **라이브 장부**다 — owner0(tick 10,790→10,823)과
    owner6(23,596→23,629)에서 `used` **−20**·`count` **−2** 동반 감소(전투 손실 추정).
    ⇒ `used` 고정을 곧바로 "생산 정지"로 읽으면 안 된다(lap504 N149의 "`used` 착시" 지적을
    원시로 뒷받침). 천장 공식 Σ(typemax×cost)가 **동시 존재** 상한이라는 점과도 정합.
  - **여전히 UNKNOWN:** owner7은 tick 16,392부터 7,600틱 넘게 정지했는데 천장 대비 **56.3%**에
    불과하다 — 천장/typemax 포화(N149 H-TYPEMAX)로 **설명되지 않는다**. owner5(89.9%)와 대조적.
    owner5도 `count` 기준으로는 80/150(53.3%)이라 총량 포화가 아니라 **고가 kind만 포화**한 형태다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀: 없음(제품 source 무변경, 게임 실행 0, `SAFETY_PASS`·`CONTEXT_PASS`·796 passed).
  - **단일 출처 한계(명시):** owner별 `building_kinds_owned`(종단 건물 집합)는
    `ceiling_table.json`에만 있고 다른 원시로 교차 검증할 수 없다 — lap507 probe의 라이브 스캔을
    **신뢰해야만 하는 유일한 입력**이다. 이 값이 틀리면 천장표 전체가 흔들린다. 다만 그것과
    독립인 `used_final`이 8/8 모두 재계산 천장 이하이고(위 반증 시험 0건), owner1이 96.7%로
    바짝 붙어 있어 **정합적**이다.
  - 독립 검수: 이 lap이 lap507에 대한 **2단**이다. 이 lap 자신의 신규 관측(N151~N153)은
    아직 2단이 없다 — 다만 전부 위 스크립트 1개로 재현 가능한 산술이다.
  - 사용자 승인: 해당 없음(읽기 전용). Q8의 (ㄱ)/(ㄴ)/(ㄷ) 선택은 **사용자 전권** — 이 lap은
    판정식을 재적용해 `k=8`을 확인할 뿐 고르지 않는다.
- 다음 한 가지: **§67 예산 소진 ⇒ `loop/PROMPT.md` ④6에 따라 STOP.** 사용자 Q8 응답이
  들어오면 그때 재개한다. 회부는 `loop/ESCALATE_SOL` §69. 승격 작업자가 이어서 볼 것은
  (1) N151/N152가 Q8 선택지의 전제를 바꾸는지 — "건물을 더 짓게 하면 되는가"가 아니라
  "고가치 건물 종을 AI가 왜 못/안 짓는가"로 표적이 바뀐다, (2) N153이 lap501~504 "AI 생산 정지"
  계보의 전제(owner5 일반화)를 무효화하는지, (3) owner7의 56.3% 정지가 미설명으로 남는 점.

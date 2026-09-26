# 2026-09-23 | lap500 | G2 — N141 재현성 판정(주) + N142 owner2 분기 분류(rider)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / **middle(진단·계획·확인)**.
  권한 근거 `loop/ESCALATE_SOL` §62 "Work 동결 + 한정 예외"(§61-끝 항1 주 + 항2 rider, middle 1회차,
  게임실행0·source변경0, 판정식 사전 고정). 게임 구현은 하지 않았고 work 카드도 발행하지 않았다.
- **가설:** N141(8 owner 전원 장부 정지)이 W26 144k 1회의 성질인지, 시딩 축 전반의 성질인지.
  lap448 24k 원시(712표본)를 동일 판정식으로 재계산하면 구분된다.
- **예상 PASS / FAIL 조건(데이터 열기 전 고정):**
  `temp/Syw2plus_patch/g2_capacity/20260923_lap500_middle_n141_reproducibility/PREREGISTRATION.md`.
  `N141_REPRODUCED`(global_freeze_frac ≥ 0.10) / `N141_PARTIAL` / `N141_NOT_REPRODUCED` /
  `INDETERMINATE`(리더 아티팩트 배제 실패). rider는 Class A(차단·N68 동형)/B(생산 계속)/C(기타).
- **변경 파일 / source fingerprint / 커밋:** product source 변경 **0**. 이번 회차 산출물은 문서 3종
  (이 파일, `docs/STATUS.md`, `loop/ESCALATE_SOL` §63)과 공유 temp 분석 스크립트뿐. **커밋 0**(HEAD `unborn`).
- **원본 SHA / 후보 SHA / 환경 / 활성 인원 / 지도 / fixture:** 원본 `b56986e0…`(양 run 동일),
  후보 `a10024de…`(양 run 동일), 지도 100×100, anchors `[[2,2],[27,2],[52,2],[77,2],[2,52],[27,52],[52,52],[77,52]]`,
  8 owner 전원 `ai=1`, gate-legal 시딩 16 op, 시딩 후 상태 동일. **게임 실행 0회**(기존 원시 재계산만).
- **실행 명령 / 로그 / 경로·해시:**
  입력 `…/20260921_lap448_w21_step1_cap_proximity_soak_root_recovery/samples.jsonl`
  SHA256 `c3cf99a5ed700da17be84b651dff8b53622e07924788053405d1f2f4f0d075a4`, **712행**.
  대조 입력 `…/20260923_lap497_w26_seeded_cap_proximity_144k/samples.jsonl`(4,287행).
  산출 `…/20260923_lap500_middle_n141_reproducibility/`:
  `recompute.py`·`recompute_result.json`·`gap_analysis.py|txt`·`determinism.py|txt`·
  `determinism_usedcount.txt`·`resumption_proof.txt`·`death_reproduction.txt`.
  **비참조 원칙:** `run_summary.json`과 lap449 수치는 재계산 입력에서 제외하고 사후 대조만 했다.

## 측정값 / 판정

### 항1(주) — 사전 고정식 판정 = `N141_REPRODUCED`, 단 "독립 재현"은 **아니다**

lap448 24k: first_tick 312 · final_tick **24,029** · 712표본 · pid 단일 · owner 8인 완비 ·
필드결손0 · tick역행0 · `cap` 전표본 5000.
owner별 `last_change_tick`(freeze_frac): owner7 **2,582**(0.8925) · owner3 2,782(0.8842) ·
owner4 3,416(0.8578) · owner2 11,154(0.5358) · owner5 12,389(0.4844) · owner6 12,989(0.4594) ·
owner1 14,390(0.4011) · owner0 **16,290**(0.3221).
⇒ `global_freeze_onset` **16,290**, 이후 **7,739tick(32.21%)** 동안 8인 장부 전부 불변, `live` 1,247 고정.
**리더 아티팩트 배제 충족** — 꼬리 232표본에서 엔진 tick +7,706 단조 전진, `rss_kb` 78 ·
`vm_swap_kb` 77 · `host_mem_available_kb` 231 구별값, 벽시계 231.16s.
사전 고정식대로 0.3221 ≥ 0.10 ⇒ **`N141_REPRODUCED`** (W26의 0.281보다 오히려 크다).

### N144(중대·방법론) — 두 run은 독립 복제가 아니라 **같은 결정적 궤적**이다

lap448과 W26의 8 owner **`(used,count)` 변화 시퀀스가 tick 24,029까지 전부 동일**하고
(owner별 변화 9~19건, 8/8 완전일치) tick 편차는 최대 **29**(표집 간격 ≈33tick 이내)다.
`reserved`만 0/10이 엇갈리는데 이는 생산 예약이 표집 위상에 걸리는 alias다.
fixture도 동일함을 확인했다 — 후보 SHA·원본 SHA·지도·anchors·시딩 16 op 순서·시딩 후 owner 상태 전부 SAME.
⇒ **lap448은 W26을 더 짧은 창으로 본 같은 궤적이므로, 이번 재계산은 N141을 독립 확증하지 않는다.**
확증된 것은 **fixture의 결정성**이며, 같은 fixture를 다시 돌려도 새 정보가 없다는 뜻이다.

### N145(중대·N141 해석 정정) — "정지"는 종료가 아니라 **창 절단(censoring)** 이다

같은 궤적의 144k 연장에서 **8인 중 5인이 24k 창 이후에 상태를 재개**했다:
owner3 **33,753tick** 정지 후 재개(tick36,519) · owner1 **36,236**(tick50,609) · owner4 **27,210**(tick30,615) ·
owner2 19,471(tick30,615) · owner0 14,325(tick30,615). (owner5/6/7만 끝까지 재개 없음.)
즉 lap448의 24k 창은 owner3을 "21,247tick(88.4%) 동결"로 보고했을 것이나 **그 owner는 실제로 재개했다.**
또 lap448의 전원동결 꼬리 **7,739tick은 같은 run이 이미 재개해 보인 최대 간극 9,406tick보다 짧다.**
**W26에 되먹이면:** W26의 종단 전원정지 40,484tick은 이미 관측·재개된 최대 정지 36,236tick의
**1.12배**에 불과하다. ⇒ **"종단 정지"와 "더 긴 소강"을 현재 증거로 구분할 수 없다.**
lap498 N141의 "이 soak이 잰 것은 부하 지속이 아니라 **정지 상태 생존**"이라는 서술은
**그 강도로는 지지되지 않으며**, 정확한 서술은 **"run 종료 시점에 장부가 40,484tick 불변이었고,
이는 같은 궤적이 이미 재개해 보인 정지 길이와 같은 규모라 종단 여부는 UNKNOWN"** 이다.
⇒ **N141은 '중대·확정'에서 '해석 경고 + 미결'로 강등한다.** 보수적 부분("실제 플레이 증거가 아니다",
전투 축·건물 계층 미시험)은 **그대로 유지**된다 — 강등은 정지의 종국성에 한정된다.

### N146 — 사망·재생산은 **존재하되 극히 희박**하고, 그 대부분이 24k 창 **이후**다

W26 144k 전 구간: `count` 감소(사망) **9건/소실 14기**, 증가(생산) **116건/신규 117기**,
`live` 1,166→1,269. 사망 9건 중 **7건이 tick24,029 이후**(owner2 4 · owner0/1/4 각 1).
lap448 24k 전 구간: 사망 2건/**소실 4기**, 생산 84건/85기 — **lap461 N87의 "4기/1,166기"와 정확 일치**
(독립 재확인). ⇒ 엔진은 죽지 않았고 장부도 드물게 계속 움직였다. 동시에 144k 내내 사망이 14기뿐이라
**전투 축이 fixture에서 성립하지 않는다는 N87 결론은 수치로 재확인**된다.

### 항2(rider) — N142 owner2 분기: 24k에는 **없다**

lap448에서 `used+reserved>cap`인 owner-표본은 **1,263건**, 값은 **전부 정확히 `(4995,10)`**,
owner는 **owner4(619)·owner7(644) 둘뿐**, episode는 **2건이며 둘 다 `Class A`(차단·N68 동형)**:
owner4 enter tick3,416 · owner7 enter tick2,582, 둘 다 run 끝까지 열린 채 `used`·`count`(154) 불변.
**Class B(생산 계속) episode는 0건**이고 `used`가 정확히 5000인 초과 episode도 없다.
⇒ **W26 owner2형(`(4980,23)→(4990,13)→(5000,13)`, `count` 156→161 증가)은 24k 창에 존재하지 않는
144k 고유 분기**다. N142의 "N68 동형은 2건뿐" 구분은 유지되며, owner2형은 **차단이 아니라
cap 도달 상태에서 생산이 계속 도는 별개 기전**으로 분류한다. lap404 (가)/(나) 입력으로 이 구분을 쓴다.

### 무결성 / F4 게이트 (lap448 원시, 사전 고정)

`used` 음수 0 · int16 이탈 0 · 라이브 `used`>`cap` 표본 **0** · `count`>`count_cap` 0 ·
`live`==Σ`count` 712표본 전부 일치(불일치 **0**, work 파생 `sum_count`는 입력 아님) ⇒ **F4는 (C) 유지**.
**자체 결함 정정 1건:** 초판 무결성 검사가 `sample` 인덱스를 1-기반으로 가정해 "결손"을 오보했다.
실제 인덱스는 **0..711 연속**이며 데이터 결손은 **없다**(검사기 off-by-one, 판정 무영향).

### 사후 대조 (재계산 종료 후 개봉)

lap448 `run_summary.json`: final_tick 24,029 · sample_count 712 · U3 불일치 0 · `used`>5000 0 —
내 재계산과 **전부 일치**. 후보 `a10024de…`, `source_unchanged=true`, verdict `CAP_PROXIMITY_STABLE`.
lap449 middle이 보고한 1,263건 / 전부 `(4995,10)` / owner4·7 둘뿐도 **독립 재현 일치**.

## 회귀 / 남은 위험 / 독립 검수 및 승인 상태

- **위험(신규):** 유한 창 soak의 "전원 정지" 통계는 구조적으로 창 절단에 취약하다. 앞으로 이 축의
  판정문은 **꼬리 정지 길이 vs 같은 run의 최대 재개 간극** 비교를 반드시 동반해야 한다(N145).
- **재확인:** fixture 결정성(N144) 때문에 **같은 조건 재실행은 새 정보를 주지 않는다.** 종단 여부를
  가리려면 (ㄱ) 창 연장(≳200k) 또는 (ㄴ) 다른 seed/구성 또는 (ㄷ) (ㄴ)-승인 기반 AI/설정 변경이 필요하다.
- 이번 회차는 **middle 자기 산출**이므로 다음 새 세션의 독립 검수 대상이다(1단→2단 경계).
- **모델이 고르지 않는 것(불변):** Q7(A/B/C) · lap404 (가)/(나) · F4 (B)/(C) · (ㄴ) 착수 ·
  3단 사용자 마일스톤 승인 — 전부 사용자 전권 대기.
- **검사 결과:** product source 변경 0이라 2026-09-20 21:58 지시 + N22 면제 요건("이번 회차에
  source를 바꾸지 않았다") 충족 ⇒ 784 전체 `make check` 대신 표적 재실행:
  `test_runtime_env.py`/`test_g2_eight_owner_setup.py`/`test_g2_stock_stress.py`/
  `test_g2_stock_lifecycle.py`/`test_g2_official_creation.py` = **186 passed**(2.22s).
  `checks/safety.sh check` = **`SAFETY_PASS`**, `checks/context_limits.py` = **`CONTEXT_PASS`**.
  op4 배제 핀 3종 현존 재확인(`tools/runtime_env.py:5837` `"op4_used": False` /
  `tests/test_g2_stock_stress.py:20` / `tests/test_g2_eight_owner_setup.py:166`) — 수정·면제 없음.
  잔류 wine 프로세스 **0**. `git status` = `No commits yet on main`(HEAD `unborn`), **커밋 0**.
- **uncommitted 파일 해시(LOOP_ALLOW_COMMITS 미설정, ⑤ 규칙):**
  `docs/STATUS.md` `5071b6cb2e7a6fed1efe91a7bba006e70aa759a7a4b01a557f1291d489b407b6` ·
  이 파일 `74da3e4fd4523a0e7a30857dc8758b70af8102afde994a4efe411ce705156ef9` ·
  `docs/history/20260923_status_lap500_precompaction.md`
  `c0fe068d0da9bde50678e37e53a012ebd4c2985121ec4bc14a14b328e4507eea` ·
  `loop/ESCALATE_SOL` `db8435829f0d0a6cefb851e4328c75a13132b5fb5a897eac642a7e91bf669a8b`
  (§63 + handoff 4항 추기 후 최종값; 추기 전 중간값은 `81a27421…`).
- **INBOX 무변경:** `docs/feedback/INBOX.md`가 350줄 한도에 정확히 걸려 있어 이번 회차도 lap499와
  같이 추가하지 않았다. lap500 원문은 이 파일·STATUS·`ESCALATE_SOL` §63이 보유하며, 다음 압축 때
  W26 계보 항목에 포인터 1줄(“lap500 middle N141 강등 — §63”)을 넣기를 권장한다. 삭제·재해석 없음.

## 다음 한 가지

**사용자 Q7 응답 대기 → 없으면 STOP(PROMPT ④6).** §62가 허용한 middle 예외 1회차는 이 lap으로
소진됐다. 단 Q7-B 제출문은 **N145 정정을 반영해야 한다** — "정지 상태 생존"이 아니라 "종단 여부
UNKNOWN(창 절단), 장부 상태 지속성은 실측 지지, 전투·건물 축 미시험"으로 고쳐 사용자에게 올린다.

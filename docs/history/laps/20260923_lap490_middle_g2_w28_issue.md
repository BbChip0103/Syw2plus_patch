# 2026-09-23 | lap490 | 목표 G2 (활성8인 각각 전비5000 안정성)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(중간계획·컨펌)**.
  게임 코드 hands-on 수정 없음. 게임 실행 0. 문서 산출물 + 원시 재계산만.
  (세션 시작 2026-09-22 23:5x KST, 자정 경계를 넘어 기록 날짜는 09-23.)
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL` §54(lap489 strategy, Fable5) 처분에 따라
  **middle이 W28 카드 1장을 발행**한다(이번 회차는 발행 1회만 허용). 사용자 신규 지시 없음.
- 예상 PASS / FAIL 조건: PASS = ①lap489 §54가 의존한 결정적 원시 사실을 lap483/lap487 원시만으로
  독립 재현(불일치 0 또는 판정 무영향 정정) ②§53 교정 3건 + 추가 2건이 전부 카드 문언으로 박힘
  ③라벨 3종·op4 정확히 2콜·핀 3종 유지 ④새 카드 1장·게임 실행 0.
  FAIL = 원시가 §54 전제를 반증 / 교정 누락 / 카드 2장 이상 / op4 허용 확대.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md` (W28, `READY_FOR_WORK`)
  - 갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(§55), 이 기록 파일
  - **제품 source(tools/·patches/·tests/) 변경 0**, 게임 코드 0, 커밋 0 (`LOOP_ALLOW_COMMITS` 미설정),
    전부 uncommitted 보존. 커밋 없으므로 ⑤대로 파일 해시를 남긴다(작성 직후 값):
    W28 카드 SHA256 `bd333771cfa8c7ce9bcad811d2adb4ed0de3649d951f774f0f1d33cd7596c923`,
    재계산 결과 `recheck_lap490_result.json` `725cdcb76cab1c1c3e6ef139bd92d735b886baf4141d0dd51a29a049528fcc82`.
    (이 기록 파일 자체 해시는 이 줄 추가로 바뀌므로 남기지 않는다.)
  - 재계산 산출물: `temp/Syw2plus_patch/g2_capacity/20260922_lap490_middle_w28_issue/`
    (`recheck_lap490.py`, `recheck_lap490_result.json`)
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  이번 회차는 게임을 띄우지 않았다. 검수 대상 원시는 lap483(W25)·lap487(W27) 산출물이며
  해당 run의 후보/환경/fixture는 각 lap 기록에 있다. 참조한 원시 SHA256:
  lap483 `window_samples` `420dfe5e…`, 스크립트 `46f8da26…`;
  lap487 `window_samples` `75a1cb83…`, `supply_probe_call_log` `42202061…`,
  `positive_control_samples` `26ebcd7e…`, 스크립트 `a5182ac3…`.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 recheck_lap490.py` (위 temp 디렉터리, 결과 JSON 동시 저장)
  - `python3 -m pytest tests/test_g2_stock_stress.py tests/test_g2_eight_owner_setup.py -q` → **16 passed**
  - `bash checks/safety.sh check` → **SAFETY_PASS**
  - `python3 checks/context_limits.py` → **CONTEXT_PASS**
  - 새 캡처 없음.
  - **환경 관찰(내 조작 아님, 정리하지 않음):** 이 회차는 게임을 띄우지 않았는데도 bare wine 프로세스
    3종(`wineserver64 -p0` + `winedevice.exe`×2, **게임 exe 없음**)이 `WINEPREFIX=
    /home/dev_00/.wine_syw2_baseline`·`DISPLAY=:2`에서 00:05:04와 00:05:37에 **두 차례 새 PID로**
    나타났다 스스로 사라졌다. 부모는 `systemd --user`(고아 재부모화)이고, `checks/safety.sh`와 표적
    테스트에는 wine 호출이 없음을 grep으로 확인했으며 두 명령 직후 개수는 0이었다 ⇒ **기원 UNKNOWN**.
    AGENTS.md대로 붙거나 pkill하지 않았다. 이 회차의 잔류가 아니며(게임 실행 0) 다음 work가
    격리 prefix를 쓸 때 `.wine_syw2_baseline`과 display :2를 피하는지 확인할 것.
    이 저장소 러너는 `loop.sh --role=middle --laps=1`(PID 3943623) 1개, STOP 파일 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS(발행 완료) · spot-check = 측정 ACCEPT(정정 1건,
  판정 무영향)**
  - **lap483 원시 재현(불일치 0):** 350표본 tick719~3052, 표집 간격 6~7(mean 6.685),
    장부 전이 **정확히 2건**(tick1943 `{4995,10,5}→{4985,0,5}` 비균형 차감 / tick2270 사망),
    progress100 최초 tick1414 → 종결 tick1943 = **체류 529tick**, 그 구간 **79표본 전부** 5중 신호.
  - **lap483 신규 (N134):** `progress==100` 표본은 종결 이후 tick3052까지 이어져 **총 246건**
    ⇒ `progress==100` 단독은 계류 신호가 아니다. 차단 판정은 5중 신호 연접만 쓴다(카드 §2·§4-6).
  - **lap487 원시 재현(불일치 0):** 260표본 tick712~1408, 표집 간격 2~3(mean 2.687),
    `progress==100` **정확히 1건(tick1408=마지막 표본)**, `call2_fired=true` **0건**(N130),
    A 생존 260/260, 477콜 중 op4 **정확히 2콜**(히스토그램 `{0:470,1:2,4:2,6:2,7:1}`),
    콜#1 엔진 tick710 `{70,10,5}→{4995,10,5}`, 콜#2 엔진 tick1410 `before{4995,10,5}`→
    `after{4980,10,5}`(재개 전), 재개는 **tick 없는** 재읽기 `{4990,0,6}`에서만(N126).
  - **정정 (N131, 판정 무영향):** §54 spot-check 서술의 "콜#2 엔진 사후블록 tick1410
    `{used4995,reserved10,count5}`"는 원시의 **before** 블록이다. 원시 **after**는
    `{used4980,reserved10,count5}`이며 둘 다 "재개 전"이므로 결론(§1 OPEN·Q4 승인)은 그대로다.
    lap488·STATUS 서술이 원시와 일치한다.
  - **대조군 지연 재현:** 표본207(tick702)이 `progress==100`과 정산(`reserved`10→0·`used`40→50·
    `count`3→4)을 **같은 표본**에 담고 직전 표본은 tick698(`progress==99`) ⇒ **표본 tick 기준 지연 0**.
    `run_summary`의 `1`은 루프 종료 재읽기 tick(703) 기준 정의 결함(`w27_…py:454`) 확인.
    표집 간격 3~4(mean 3.353) ⇒ 참 지연은 `[0,4)`.
  - **신규 (N132):** 그 대조군에는 차단 predicate(progress100 ∧ `reserved`10 ∧ `command`15 ∧ 미정산)
    표본이 **0/208**이고 정산 표본에서 `producer_command`가 15→1로 함께 바뀐다 ⇒ 건강한 정산은
    predicate를 한 표본도 만들지 않는다(특이도 지지). lap483의 79표본 연속 성립은 이례적이다.
    W28은 대조군 표집을 ≤3tick으로 올려 이 특이도와 지연 분해능을 **run 내에서** 재확인한다.
  - **신규 (N133):** 실측 tick 속도 ≈ **33tick/s**(pending 698tick/21초) ⇒ 선입증 200tick≈6초,
    사후 관측 600tick≈18초. 관측 완주 의무의 벽시계 비용은 사실상 0이며 기존 cap 600s가 충분하다.
    또 lap483 종결은 발사 예정 시점(+200tick)보다 **약 329tick 뒤**라 무재개 경로에서도 종결 전에
    200tick 요건이 충족된다 — 단 완주를 위해 종결·정산·사망에서 표집을 멈추지 않아야 한다.
  - **W27 스크립트 자기모순 확인:** `w27_…py:745~754`가 콜#2 직후 재읽기에서 `used != 4980`이면
    `RuntimeError` ⇒ 재개 신호(`used`=4990)가 곧 예외 조건이었다(N128). 그 예외로 post-call2 표본
    0건·세 이벤트 배열 `[]`(N129, "사건 0건" 아님).
  - **발행물 W28 = `G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`**, §54 교정 5건 전부 반영:
    (1) 발사 전건을 **"progress100·5중 신호 연속 + 체류 ≥`T_block`200tick"의 선입증 직후**로 교체
    (W27의 "+50tick 창" 폐기), (2) **R1′**로 정정 — `used` +비용(정확히 +10) ∧ `reserved`10→0 ∧
    `count`+1은 **재개 신호이고 위반이 아니다**(사망/비균형 종결도 분류, 그 밖의 이탈만
    `ledger_reverted_by_engine`), (3) 모든 재읽기에 **tick 기록** + 콜#2 직후 재읽기를 표본으로
    기록(예외 금지) + 콜#2 엔진 tick 기준 **≥600tick 관측 완주**(정산·종결·사망에서 break 금지),
    (4) 표본마다 **append+flush** 증분 기록(`window_samples.jsonl`·`events.jsonl`)으로 예외가 기록을
    소거하지 못하게 함, (5) 대조군 지연을 **표본 tick 기준**으로 정의하고 분해능(`정산표본−직전표본`)을
    공개 + 대조군 표집을 ≤3tick으로 상향.
    추가 고정: 차단 감시 지평 `t0+700tick`(lap483 종결 529tick을 덮음), 인과 귀속 구간
    `T_attrib=50tick`(라벨은 불변, 귀속 강도만 사전 구분), `PRECONDITION_NOT_MET` 사유·`detail`
    사전 표(새 사유 실행 중 생성 금지), `detail=settled_at_tick<N>_without_headroom`은
    **H-gate 반대 증거 후보**로 미리 분류.
  - 무결성/경계: op4 허용은 카드 §4의 **정확히 2콜**, op4 배제 핀 3종 현존 확인
    (`tools/runtime_env.py:5837`, `tests/test_g2_stock_stress.py:20`,
    `tests/test_g2_eight_owner_setup.py:166`), 새 카드 **1장**, 게임 실행 0, 제품 코드 0,
    source 변경 0, 커밋 0, 표적 **16 passed**, `SAFETY_PASS`, `CONTEXT_PASS`, 잔류 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **§1(정산이 cap을 재검사하는가)은 여전히 OPEN.** W28은 그것을 닫으려는 단일 판별이며 결과가
    `no_blockage_ge_t_block_observed`로 떨어질 위험이 남는다(그 경우 §54대로 **재시도 없음**).
  - lap483과 lap487은 장부 수준에서 동일 구성인데 체류가 529tick vs ≤2tick(미측정)로 갈렸다.
    이 차이 자체는 이번 회차에 설명되지 않았다(UNKNOWN) — W28의 선입증이 run 내에서 직접 답한다.
  - **연속 무실행 3회차 경계:** lap488·489에 이어 lap490도 게임 실행 0이다. §54가 이번 회차를
    "발행 1회"로 명시 허용했으므로 범위 위반은 아니지만, **다음 work 회차는 게임 1회 실행 증거가
    의무**다. 그 다음 회차가 또 무실행이면 PROMPT③에 따라 strategy가 계속/중단을 먼저 판정해야 한다.
  - N120(비균형 차감 자연 발생 여부)·N123(N68 미재현)·(ㄴ)·lap404 (가)/(나)·F4 (B)/(C)·
    3단 마일스톤 사용자 승인은 **전부 사용자/strategy 전권 대기**이며 모델은 착수하지 않았다.
  - 이 회차의 발행물은 **middle의 자기 산출물이므로 독립 검수 대상**이다. 다음 work가 카드대로
    실행하고, 그 다음 middle이 **원시만으로** 재계산해 라벨을 확정한다.
- 다음 한 가지: **work(Sonnet5/high)가 W28 §4를 게임 1회·동기·foreground로 완주**하고
  (발사했으면 8단계 ≥600tick 관측 완주 포함) 라벨 후보와 원시를 남긴다. 라벨 확정은 그 다음 middle.

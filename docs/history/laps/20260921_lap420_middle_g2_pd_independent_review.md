# 2026-09-21 | lap 420 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, **middle(진단·계획·확인)**.
  STATUS「다음 한 가지」가 지정한 "lap419 W11 P-D 독립 검수"를 수행했다. 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap419(work/Sonnet5)가 W11 P-D를 실행해 **H1r 지지 / H2 기각**을 자기 판정으로
  남겼다. 요약본을 신뢰하지 않고 원시 `samples.jsonl` 994줄만으로 W11 §3 판정식을 재계산한다.
- 예상 PASS / FAIL 조건: (a) 판정식 입력(3565의 생존·owner·type·`+0x692`)이 원시 데이터에서 그대로
  재현되면 해당 결론 ACCEPT. (b) 서술과 원시 데이터가 어긋나면 그 부분만 정정하고 후속 카드 전제를
  다시 세운다. (c) 안전·게이트 주장(원본 불변·`SAFETY_PASS`·표적 6 passed·source 변경 0)을 독립 확인.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **제품/게임 코드 변경 0. 이번 회차에
  source를 바꾸지 않았다**(`tools/ patches/ checks/ tests/ Makefile`에 2026-09-21 01:00 이후 수정 파일 0건).
  추가한 것은 문서 2개와 temp 산출물뿐:
  `docs/history/laps/20260921_lap420_middle_g2_pd_independent_review.md`(이 파일),
  `docs/work/active/G2_POOL_FAULT_MOVE_FIELD_WRITER_LAP420.md`(W12),
  `temp/Syw2plus_patch/g2_capacity/20260921_lap420_middle_review/{recompute_lap419.py,findings.json}`,
  `docs/STATUS.md` 갱신. uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 2경로
  (`Syw2plus/`, `Syw2plus_patch/Syw2plus/`) 재해시 **일치**. 후보(marked compat)
  `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`(lap419 산출물 기재값).
  **이번 회차는 게임을 실행하지 않았다** — 검수 대상 fixture는 lap419의 것(op7 resource-only,
  8 owner/7 AI, `_custom_game_chain_inject_g2_eight_seed42`, N=4001, display `:3843`)이다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 재계산: `python3 temp/Syw2plus_patch/g2_capacity/20260921_lap420_middle_review/recompute_lap419.py`
    → `findings.json`. 입력은 lap419 `samples.jsonl` 994줄 단일 파일.
  - 표적 테스트: `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
    patches/population/test_runtime_bridge_contract.py -q` → **6 passed** (48.73s).
  - 안전: `checks/safety.sh check` → **SAFETY_PASS**.
  - `make check`(786)는 **재실행하지 않았다** — 이번 회차 source 변경 0이므로 INBOX 2026-09-20 21:58
    규칙에 해당한다(N22가 요구하는 "source를 바꾸지 않았다" 명시를 함께 남긴다).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **부분 ACCEPT / 부분 REJECT.**

  **ACCEPT — 원시 데이터로 재현된 것**
  1. fault 재현: `final_tick=11928`, `sample_count=994`, stall 확인 후 정상 종료. 일치.
  2. **H2 기각 ACCEPT(확정).** 슬롯 3565는 tick 10,205부터 11,928까지 **406 표본 전부**
     `alive=True`, `owner=4`, `type=76` 단일값이며 최초 생존 이후 `alive=False` 표본 **0개**.
     `alive`는 유닛 구조체가 아니라 **별도 존재배열 `0x017B8658`** 에서 읽으므로 구조체 손상과
     독립적인 신호다. "stale/사망/재할당" 조건은 어느 tick에서도 성립하지 않는다.
  3. lo밴드 `max_abs`는 994 표본 전부 **0**, 전 실행 이상 슬롯은 **{3565} 하나**(이상 레코드 241건). 일치.
  4. VA 산술 재검증: `0x0108C000 + 0x758*3565 = 0x016F0478`, `+0x692 = 0x016F0B0A`. 일치.
  5. 안전/게이트: 원본 2경로 불변, `SAFETY_PASS`, 표적 6 passed, source 변경 0. 전부 재현.

  **REJECT / 정정 — 서술이 원시 데이터와 어긋난 것**
  - **N32 — "`+0x692`만 튄다"는 거짓.** onset tick **11,915**에 `move`와 **동시에** 7개 필드가
    같이 변했다: `f674 0→10`, `f676 0→10`, `f2b8 0→10`, `f2ba 0→9`, `f2bc 0→10`, `f2be 0→10`,
    `f2a4 9→10`. 이후 11,928까지 그 필드들이 **함께 10→11→12→13으로 증가**한다. 한 슬롯의 모든
    필드는 probe의 **단일 `0x758`바이트 read** 한 번에서 나오므로 읽기 아티팩트가 아니다.
    ⇒ 흩어진 4개 클러스터(`0x2a2/0x2a4`, `0x2b8~0x2be`, `0x674/0x676`, `0x692`)가 같은 tick에
    작은 정합 카운터로 세팅되고 이후 보조를 맞춰 증가하는 모양은 **이웃 슬롯 오버런으로 설명되지 않는다.**
  - **N33 — "정상 드리프트대 ±44~50"은 밴드 통계 오귀속**(N31과 같은 계열의 반복). 슬롯 3565
    자신의 `move`는 onset 이전 **163 표본 전부 정확히 0**이다. 44~50은 `bands.hi.max_abs`, 즉
    hi밴드 약 2,801 슬롯의 최댓값이다. ⇒ 3565는 "드리프트하다 튄" 것이 아니라 **정지 상태(0)에서
    활성화되며 첫 값부터 범위 밖(19,579)** 이었다. 이 차이가 후속 카드의 방향을 바꾼다.
  - **N34 — "tick마다 진동(단조 증가·고착 아님)"은 표본설계가 뒷받침하지 않는다.** 정지
    tick(11,928)을 빼면 dense 구간의 **모든 tick이 표본 1개**이고 tick 내 위상은 통제되지 않았다.
    또 dense 범위 11,828~11,928 중 **21개 tick에 표본이 없다**(onset 구간의 11,916·11,922·11,927
    포함) — 표본 1회가 4,000 슬롯 × `0x758`바이트 ≈ 7.5MB 읽기로 약 0.037s 걸려 tick 주기와
    비슷하기 때문이다. 따라서 lap419 기록/카드의 "**매 tick** 샘플"은 달성되지 않았고,
    관측된 {19579, −26278, −6599, 0} 되풀이가 tick 단위 진동인지 tick 내 다중 변화의 위상
    앨리어싱인지는 **미결**이다.
  - **판정 문구 정정:** W11 §3의 두 갈래 중 **H2 기각은 확정**이나, 남은 갈래를 lap419처럼
    "H1r = 외부 wild write 확정"으로 읽을 근거는 없다. 관측 사실은 "**3565가 활성화되었고 그
    시점부터 `+0x692`가 범위 밖**"까지다. 원인 주체는 **미결**이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임 미실행, 제품/게임 코드 변경 **0**, 커밋 **0**.
  - **남은 한계 1(H2 잔여):** 표본 간격이 1~2 tick이라 "한 tick 안에서 사망→같은 owner/type으로
    재할당"은 원리적으로 배제되지 않는다. 확률은 낮고 H2 기각 결론을 뒤집을 근거는 없으나 기록해 둔다.
  - **남은 한계 2(잔류 관측):** 2026-09-20 23:56 기동한 `winedevice.exe` 2기(PID 2089059/2089068)가
    남아 있다. **lap419 실행분이 아니다**(lap419는 01:44 기동). AGENTS.md의 전역 정리 금지에 따라
    **정리하지 않고 관측만 기록**한다. lap419의 "자기 실행분 잔류 0" 주장 자체는 반증되지 않았다.
  - **남은 한계 3(provenance):** 저장소에 커밋이 없어(HEAD unborn) source 변경 0을 git diff로
    검증할 수 없다. mtime 기준(2026-09-21 01:00 이후 수정 0건)으로만 확인했다.
  - 이 검수 결론은 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c` stub 채널에
    근거하지 않는다(N21).
  - 사용자 마일스톤 승인은 없다. **G2는 여전히 제품 미완료다.**
- 다음 한 가지: **work(Sonnet5/high)가 새 카드
  `docs/work/active/G2_POOL_FAULT_MOVE_FIELD_WRITER_LAP420.md`(W12)를 수행한다.** lap419가 제안한
  "`0x016F0B0A`에 쓰는 미지의 외부 주체 추적"은 N32/N33 때문에 전제가 약하므로 **그대로 착수하지
  않는다.** W12는 먼저 **P-E 정적 판별**(후보 `.text`에서 변위 `0x692`를 목적지로 쓰는 store 전수)로
  "누산기 `0x0040bc86~0x0040bcff`(lap414 N26) 말고 기록자가 있는가"를 30분 상자로 가른 뒤, 같은
  회차에 **P-F 실행 probe**(스캔 범위를 줄여 tick당 표본 2회 이상 확보 + **slot<1200 저슬롯
  활성화 대조군** + 활성화 시점 경로점수 동시 기록)로 H5(자기 활성화 경로의 입력 결함) vs
  H6(외부 writer)을 가른다. `0x00414133`·`roster_add 0x0043ee39`·`0x00422dc7`은 계속 패치 금지이고
  lap418의 H1 기각도 되살리지 않는다.

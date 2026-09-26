# 2026-09-23 | lap 509 | 목표 G2 (F4(B) 전비 장부 32-bit 확장)

- **실제 provider/model/effort / 지정 역할:** Claude Code `claude-opus-5` / high / **middle(중간계획·컨펌)**.
  게임 코드 hands-on 수정 없음 — 카드 발행 + 범위 검수만 수행했다.
- **가설 / 사용자 관찰:** 2026-09-23 12:55 KST 사용자 "3은 앞으로 말하지 말고, 1 2 바로 ㄱㄱ".
  트랙① = F4(B) 전비 장부 32-bit 확장, middle이 카드부터 발행. F4=(B)는 2026-09-23 04:13 사용자 승인 완료.
  가설: STATUS/INBOX가 적어 둔 범위(writer 2 + reader 3 + 필드폭 + bulk save/load 포맷)가 정확하다면
  그대로 카드로 옮기면 된다.
- **예상 PASS / FAIL 조건:**
  PASS = ④2대로 그 바이트 주장을 원본에서 독립 확인한 뒤, work가 즉시 소비 가능한 측정식 고정 카드 1장 발행.
  FAIL = 주장이 원본과 불일치하면 카드를 쓰지 말고 정정 근거부터 남긴다.
  ⇒ **실제로 FAIL 쪽 분기가 열렸고**, 정정 2건을 확정한 뒤 정정된 범위로 카드를 발행했다.
- **변경 파일 / source fingerprint / 커밋:** 커밋 **없음**(`LOOP_ALLOW_COMMITS` 기본 0, uncommitted 보존).
  **제품 source(`patches/`·`tools/`·`checks/`) 변경 0.** 신규/수정 파일:

  | 파일 | SHA256 |
  |---|---|
  | `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md` (신규, W30 카드) | `4de2b53ca555837495498392bb6d6e2201d898f7e1f11560de543804bafffb4d` |
  | `analysis/memory_maps/g2_supply_ledger_200c_site_inventory_lap509_20260923.md` (신규, 주소 근거) | `91d9fcf9b0561ddc2b3e43de77055acbf5e48c7c02264624048609f2338d1735` |
  | `docs/history/laps/probes/20260923_lap509_middle_supply_ledger_site_inventory.py` (신규, 재현 probe) | `272346e6d54bd970f43005a60e4d03ee36d1731b3ab65d76f5bd8e7858b22771` |
  | `docs/history/20260923_inbox_lap509_ai_production_lineage_archive.md` (신규, INBOX 압축 원문) | `270c6b269bea2cb65a97bb553924f65b65fda03f70decf6b29cb849a57956949` |
  | `docs/feedback/INBOX.md` (압축 344→278줄, lap509 추기 후 최종 302줄) | `2afbdfa17ab6f63a207b7c0c9ecc4314b0b6814e17618040e1b9b23205e71189` |
  | `docs/STATUS.md` (갱신) | `d64990c025fb131a10f041f873d0a05303b49388d744cf92bb3084e0857ca805` |
  | `loop/ESCALATE_SOL` (§70 추가) | `24a2a918eb2b1de1345c4c772a149b84174d5a11785b259a7cfe8c4a7b4c83d6` |

- **원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:**
  원본 `Syw2plus/syw2plus_original.exe` SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 1,032,192B — **읽기만 했고 전후 불변**.
  **후보 없음. 게임 실행 0회. Wine/Xvfb 미사용. fixture 없음(정적 분석).**
  참조한 기존 산출물: lap507 W29 `type_specs.json`
  (`…/temp/Syw2plus_patch/g2_capacity/20260923_lap506_w29_used_ceiling/type_specs.json`)에서 `c_max`만 읽었다.
- **실행 명령 / 로그 / 캡처 경로 및 해시:**
  - `python3 docs/history/laps/probes/20260923_lap509_middle_supply_ledger_site_inventory.py` → **exit 0**,
    사전 고정 단언 **7/7 PASS**. 산출물
    `…/temp/Syw2plus_patch/g2_capacity/20260923_lap509_f4b_site_inventory/site_inventory.json`
    (SHA256 `f9d05771666c379696553b98fa9137edb12efe76b04829123c6f59dc53e303e0`).
  - `make check` → **796 passed (497.77s)** + ruff PASS + compileall + mypy(10 files) Success + `CONTEXT_PASS`.
  - `bash checks/safety.sh check` → `SAFETY_PASS`. `python3 checks/context_limits.py` → `CONTEXT_PASS`.
  - 캡처 PNG 없음(시각 작업 아님).
- **측정값 / 판정:**

  | 항목 | 결과 | 판정 |
  |---|---|---|
  | ④2 이전 범위 서술 독립 검수 | **불일치 2건 발견** | **정정** |
  | `+0x200c` 전수 사이트 | base+disp **5** + 절대주소 별칭 **4** = **9곳** | PASS(전수) |
  | STATUS가 적은 reader 3곳 | 전부 **`+0x2012`(limit)** 읽기 — `+0x200c` 아님 | **정정 확정** |
  | bulk save/load span | `[0x892410,0x975D8C)` 932,220B, save·load 즉시값 **동일** | PASS |
  | PlayerStruct 배열이 span 안에 포함 | `True` | PASS |
  | 구조적 최대 `used` = 1,200 × `c_max`65 | **78,000 > 32,767** | **F4 안전상한 닫힘** |
  | W30 카드 발행 | 1장 (활성 카드 총 1장) | PASS |
  | `make check` / safety / context | 796 passed / `SAFETY_PASS` / `CONTEXT_PASS` | PASS |

  **정정 ①(범위):** STATUS/INBOX의 "reader 3곳 `0x43EE03`/`0x43F0F3`/`0x43F43F`"는
  `hero_limit_supply_patch_sites_20260921.md`의 **`+0x2012` 문단**에서 온 문장이 STATUS로 전사되며
  필드가 `+0x2012`→`+0x200c`로 뒤바뀐 것이다. 원 문서는 정확했다. 진짜 `+0x200c` reader는
  `0x43EDFC`·`0x43F0E9`·`0x43F3B3`이고, **절대주소 별칭 4곳(`0x40DD12`·`0x40E03B`·`0x499767`·
  `0x499A0E`)은 어떤 기존 범위 서술에도 없었다.** 그 4곳의 게이트는
  `used(16b) + supply_in_production(+0x001C, **이미 32-bit**) + cost <= limit(16b)` 형태다.

  **정정 ②(저장):** bulk save/load가 고정 길이 raw 메모리 span 하나를 통째로 다루므로,
  **stride `0x3ABC`를 보존하는 한 저장 파일 길이·레이아웃은 불변**이고 호환 문제는 *포맷*이 아니라
  **2바이트 값 해석** 문제로 축소된다. lap393 D절 "work tier 단독 착수 금지"의 근거였던
  "bulk blob 포맷 변경"이 stride 보존 경로에서는 **불필요** ⇒ 그 금지가 부분 해소된다.
  stride를 바꾸는 경로(§2-C)는 lap385 통합 blocker 아래로 **여전히 금지**다.

  **부수(F4 안전상한):** `roster_add`(`0x43EE30`)는 cap을 보지 않고 `cmp ax,0x4b0`만 건다
  ⇒ 구조적 최대 `used` = 1,200 × 65 = **78,000 > 32,767**. lap395가 "어떤 uniform cap도 랩을 막지
  못한다"며 UNKNOWN으로 남긴 안전상한이 **숫자로 닫혔다**(실측 32,785와 정합). 32-bit에서는
  78,000 ≪ 2^31이라 랩이 **구조적으로 불가능**해진다. **도달성은 여전히 UNKNOWN**이며 주장하지 않는다.

- **회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:**
  - 제품 코드/바이너리/실제 실행 증거 증가 **0** — 이번 회차는 계획·검수 회차다.
    `implementation-unchanged-streak`가 2가 되므로 **다음 회차는 반드시 work(W30 구현)여야 하고**,
    또 문서로 끝나면 PROMPT③에 따라 strategy/Sol이 계속 여부를 먼저 판정한다.
  - **이 lap은 middle 자기 결과다.** W30 소비 결과는 다음 새 middle이 원시에서 독립 재계산해야 2단이 선다.
  - 남은 위험: (1) PlayerStruct 내 4바이트 구멍이 실제로 존재하는지 **미확인**(W30 M-0이 측정) —
    없으면 A·B 둘 다 실패하고 `BLOCKED`. (2) §6 교체 바이트는 middle이 종이 위에서 유도한 값이라
    work가 디스어셈블로 재확인해야 한다. (3) writer의 `edx` 상위 16비트 오염 — cost 적재 명령
    (`0x43EE93`/`0x43EF83`)을 `movzx`로 함께 바꾸지 않으면 쓰레기가 더해진다.
  - 사용자 승인: F4=(B)는 **승인됨**(2026-09-23 04:13). 그 승인은 **원본 패치 실행 허가가 아니며**
    G2 제품 합격/마일스톤 승인도 아니다. (ㄴ)·Q7-B·Q8((ㄱ)/(ㄷ))은 사용자 전권 대기 불변.
  - **미결(모델이 고르지 않음):** 12:55 지시 ③ "패치본(2601·2606) 실행 검증 제외"가 F4 후보 EXE까지
    포함하는가. 포함하면 F4는 정적·단위 증거까지만으로 끝나 **DESIGN 4절이 요구하는 실행 증거가
    없어 G2 제품 합격 근거로 쓸 수 없다.** 포함하지 않으면 별도 실행 카드가 필요하다.
- **다음 한 가지:** **work(Sonnet5)가 W30 `G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md`를 소비한다** —
  M-0(PlayerStruct 4바이트 구멍 맵: 정적 미참조 + 8 owner 런타임 상수성)부터 끝내고 A/B를 고른 뒤
  `patches/population/supply_ledger_32bit.py` + 회귀 테스트로 M-b~M-h를 기계로 고정한다.

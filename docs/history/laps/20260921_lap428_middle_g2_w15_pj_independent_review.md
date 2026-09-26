# 2026-09-21 | lap428 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(검수·중간계획)**.
  검수 대상은 lap427 work(`claude-sonnet-5`/high)의 W15 P-J 결과.
- 가설 / 사용자 관찰: `loop/ESCALATE_SOL` §14 항목1·2. lap427이 원시 476표본으로 낸
  **(J2) 외부 write 확정 + (J3) 블록/OOB write 확정**을 요약본 없이 원시 `samples.jsonl`만으로
  독립 재계산해 ACCEPT/REJECT하고, ACCEPT면 다음 표적 순서를 middle 권한으로 판정한다.
- 예상 PASS / FAIL 조건: PASS는 전 항목 재계산 일치 여부와 무관하게 **불일치를 수치로 특정**하고
  판정을 내리는 것. FAIL은 원시 산출물이 없거나 재계산이 불가능한 것.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **이번 회차에 source를 바꾸지 않았다**
  (N22 근거로 통합 `make check` 생략, 표적 6 passed만 실행). 게임 실행 0회, 제품 코드 0,
  명령 바이트 패치 0, 커밋 0. 신규 문서 4개(이 기록, W16 카드, `ESCALATE_SOL` §15, STATUS 갱신)와
  분석 스크립트 `temp/Syw2plus_patch/g2_capacity/20260921_lap428_middle_review/`
  (`recompute428.py`, `dense428.py`, `check428b.py`)뿐. 전부 uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` —
  `sha256sum Syw2plus/syw2plus_original.exe`로 **직접 재해시해 일치 확인**(safety.sh 결과에 의존하지 않음).
  후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
  검수 대상 fixture는 lap427의 op7/8owner/N=4001/seed42/display `:3846`. 이번 lap은 게임 미실행.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 recompute428.py` / `dense428.py` / `check428b.py`(입력은 lap427
  `temp/Syw2plus_patch/g2_capacity/20260921_lap427_unit_700_writer_attribution/samples.jsonl`, 476줄),
  `python3 -m pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**,
  `./checks/safety.sh check` → `SAFETY_PASS`.
  정적: `original.bin`/`candidate.bin`(lap424 산출물) + capstone 5.0.7 디스어셈블.

## 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN)

### 판정: **측정은 ACCEPT(불일치 0). 해석 중 (J3) "블록/OOB write 확정"은 REJECT → 근거 교체 후 SUPPORTED로 강등. (J2)는 ACCEPT하되 근거를 더 강한 것으로 교체.**

**A. 원시 재계산으로 일치 확인한 것(불일치 0)**

| 항목 | lap427 주장 | lap428 재계산 | 판정 |
|---|---|---|---|
| 표본 수 / 종료 | 476, `stop_tick_reached`, final_tick 10494 | 동일(tick 18→10528) | 일치 |
| 슬롯3565 `K` 변화점 | 단일, tick10400에 `0→22432` | 단일 변화점 `s382/t10399(0) → s383/t10400(22432)` | 일치 |
| 슬롯3565 `sib(+0x6fc)` | 같은 sample에 `0→16538` | **정확히 같은 경계** `s382→s383`, `0→16538`, 변화점 1개 | 일치 |
| 슬롯3565 `src(+0x388)` | 전 구간 `0` 불변 | 생존 **172**표본 전부 `0`, 변화점 0 | 일치(수 정정, 아래 N39) |
| 인과 `K→m→f688` | — | `m`·`f688`은 한 표본 뒤 `s384→s385`에서 변화 ⇒ **K 선행 확인** | lap426 V3 재확인 |
| 대조 슬롯3562 | `K`/`sib` 불변 | 생존 168표본 전부 `K=0`/`sib=0`/`base=9`/`f688=9`/`type=110`/`owner=4` 불변 | 일치 |
| band anomaly | 0 | `band_scan` 보유 314표본 전부 anomaly_count 0 | 일치 |

**내부 정합성(신규 검증):** `p_skipped_out_of_range`가 **정확히 93건**이고 이는 `s383..s475`
(=476−383)와 **완전 일치**하며, 가드 조건 `0 ≤ K ≤ 3758` 위반 여부와 **불일치 0건**이다. 즉
probe의 가드·기록 경로가 자기모순 없이 동작했다. dense 165표본이 tick10347~10460을 덮고
미샘플 tick은 **10350 하나뿐**(전이 tick10400에서 50 tick 떨어짐) ⇒ 전이 구간 누락 없음.
probe 읽기 상수도 카드 §3/§4와 바이트 일치: `POOL_BASE=0x0108C000`, `UNIT_STRIDE=0x758`,
`SRC=0x388`, `SIB=0x6FC`, `K=0x700`, 가드 `[0,3758]`.

**계측 전용 준수 확인:** `movement_state_probe_pj.py`에 `WriteProcessMemory`류 **0건**.
쓰기는 로그·`samples.jsonl`·격리 사본 EXE 설치(`game/syw2plus_original.exe`, 설치 직후 SHA 재확인)
뿐이다. 카드 §4 금지 주소 8개는 "이 probe가 쓰지 않는다"는 주석에만 등장하고 패치 0건.

**B. N39(정정, 경미) — 생존표본 수.** lap427 기록의 "생존 152표본"은 lap426이 lap425의 457표본
run에서 센 값을 그대로 옮긴 것이다. **이번 476표본 run에서 슬롯3565의 생존표본은 172**(대조
슬롯3562는 168)다. 결론(`src` 전 구간 불변)은 영향 없고 오히려 표본이 20개 더 많아 **강해진다**.
provenance 정정일 뿐 판정 변경 아님.

**C. N40(REJECT) — (J3) "블록/OOB write 확정"의 근거가 성립하지 않는다.**

카드 §3은 판별자를 이렇게 고정했다: "`0x413103`이 `+0x6fc`를, `0x413120`이 `+0x700`을 같은
패턴으로 쓰므로 둘은 같은 배열의 이웃 슬롯이다. **블록/OOB write는 이웃을 함께 더럽히고 단일
필드 store는 그러지 않는다.**" 앞 절(이웃 슬롯)은 참이지만 **뒤 절이 거짓**이다.

핀된 원본을 image base `0x400000`으로 직접 디스어셈블하면 `0x4130e6`~`0x41313a`가
**연속 필드를 훑는 언롤 루프**다:

```
0x4130e6  mov  [esi+0x6f8], ebp
0x4130ec  mov  eax, [esi+0x6fc]
0x4130f2  cmp  eax, ebp
0x4130f4  je   0x413109
0x4130f6  mov  cx, ax ; push 1 ; push ecx ; mov ecx,esi ; call 0x412f70
0x413103  mov  [esi+0x6fc], ebp      <<<
0x413109  mov  eax, [esi+0x700]
0x41310f  cmp  eax, ebp
0x413111  je   0x413126
0x413113  mov  dx, ax ; push 1 ; push edx ; mov ecx,esi ; call 0x412f70
0x413120  mov  [esi+0x700], ebp      <<<
0x413126  mov  eax, [esi+0x704]  ... 0x41313a  mov [esi+0x704], ebp
```

⇒ **정당한 단일 store 경로도 이웃을 함께 바꾼다.** `+0x6f8`/`+0x6fc`/`+0x700`/`+0x704`는 한
배열의 연속 원소이고 이 루틴은 그 전부에 차례로 쓴다. 따라서 "이웃 동시 변화"는 블록 write를
**가리지 못한다** — 카드가 저비용 판별자로 삼은 근거 자체가 무효다. lap427은 카드 규칙을 규칙대로
적용했으므로 절차 위반은 아니나, **결론의 강도는 "확정"이 아니다.**

**보강 한계:** 두 필드는 같은 sample 안에서 변했지만 그 sample 간격은 **20.3 ms**이고 dense 구간은
tick당 약 2표본이므로 이 창은 **약 2 tick**의 실행을 포함한다. 원자성(단일 명령)은 측정되지 않았다.

**D. N41(신규, (J2) 근거 교체 — 더 강한 배제) — `0x413120`은 관측된 값 쌍을 만들 수 없다.**

위 언롤 루프는 자기가 건드리는 모든 필드에 **같은 레지스터 `ebp`**를 쓴다. `ebp`는
`call 0x412f70`(thiscall) 사이에서 callee-saved라 `0x413103`과 `0x413120` 사이에 바뀌지 않는다.
⇒ 이 루틴이 한 번 지나가면 `[+0x6fc] == [+0x700]`이어야 한다. **관측은 16538 ≠ 22432**다.
⇒ `0x413120`(및 `0x413103`)은 **이 전이의 범인이 아니다** — lap427이 쓴 `+0x388` 논증은
`+0x388`을 복사하는 `0x40d733`/`0x40d79f`/`0x40f040`만 배제할 수 있었고 `0x413120`은
**논증 범위 밖이었는데도** 배제 목록에 들어가 있었다. 이번 lap이 그 구멍을 바이트로 메웠다.

정리하면 **(J2) 외부 write는 ACCEPT**이되 근거는 두 갈래다:
- `0x40d733`/`0x40d79f`/`0x40f040`: `src(+0x388)`가 전 구간 0 ⇒ 배제(lap427 논증, 유효).
- `0x413120`/`0x413103`: 균일 `ebp` 기록이라 서로 다른 두 값을 만들 수 없음 ⇒ 배제(**lap428 신규**).

**E. N42(신규 단서) — 값 패턴이 "복사"를 가리킨다.** `sib=16538=0x0000409A`,
`K=22432=0x000057A0`. 인접 DWORD 둘 다 **상위 WORD가 0**이고 값이 서로 다르다. 이는
`rep stos`류 **균일 채우기와 불합치**하고, 작은 정수 배열로부터의 **블록 복사(`memcpy`/`rep movsd`)
또는 구조체 복사**와 부합한다. 따라서 (J3)은 폐기가 아니라 **"블록 *복사*" 변종으로 좁혀 SUPPORTED**로
남긴다. 핀된 원본·후보 어디에도 연속 DWORD 쌍 `9a 40 00 00 a0 57 00 00`은 **0건**이므로 값은
런타임 생성이다(정적 상수표에서 온 복사가 아님).

**F. 후보 파리티.** `0x4130e0..0x413140` 프래그먼트는 원본과 후보가 **바이트 동일**(재배치 패치
대상 아님). `scan424_sites_700.json`의 17개 사이트는 image base `0x400000` 기준으로 **전부 바이트
일치**(검수 중 base를 `0x401000`으로 잘못 잡아 전건 불일치가 났고, 바이트 탐색으로 `0x400000`이
옳음을 확정해 정정했다 — scan 산출물에는 결함 없음).

**G. 남은 미해소(정직한 한계).** 관측된 값 쌍을 **어떤 가설도 아직 설명하지 못한다**: 언롤 루프는
균일 값이라 불가, `rep stos`는 균일 값이라 불가, 남은 것은 블록 복사인데 **복사원(source)이 미특정**이다.
`K=22432`는 여전히 1회 관측 값이며(전이 자체는 4회 재현) 게임이 실제 읽은 `P`는 가드로 미측정이다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 이 lap은 middle의 독립 검수이며 **자기 결과를 자기가 승인하지 않았다**. lap427 결과에 대한
  2단 검수로서 성립한다. 사용자 마일스톤 승인은 별개이며 **G2 제품 완료 아님**.
- 게임 실행 0회·제품 코드 0·커밋 0·source 변경 0. 원본 불변(직접 재해시), `SAFETY_PASS`, 표적 6 passed.
- P2 near-cap FAIL 기준은 낮추지 않았다. G3는 계속 포기 범위, G1/G4는 INBOX 00:20 지시로 잠정 중단.
- **연속 회차 위험:** lap426(middle)·lap428(middle) 사이 lap427만 게임을 실행했다. 다음 회차는
  반드시 work의 실행 증거 회차여야 한다(PROMPT ③ "제품/실행 증거가 늘지 않는 회차 연속 최대2회").
  W16은 그래서 정적 사변이 아니라 **실행 probe 1회**를 첫 단계로 못 박았다.

## 다음 한 가지

**work(Sonnet5/high)가 W16 `docs/work/active/G2_UNIT_700_CORRUPTION_EXTENT_LAP428.md`의 P-K를
실행해 오염 *구간의 범위*를 측정한다** — 같은 fixture로 `+0x6e0`~`+0x720` DWORD 창을 읽어
"몇 개의 연속 DWORD가 같은 순간에 더러워지는가"를 잰다. 길이 2면 표적 쌍 write, 더 길면 블록
복사이며 그 값열이 곧 복사원의 지문이다. 이 한 측정이 `ESCALATE_SOL` §14 항목2의 두 선택지
(잔존 site 정적 평가 / `sib=16538` 발생원 특정)를 **하나로 합친다** — middle 판정으로 항목2를
이렇게 닫았다(§15). 항목3(풀 재배치 안전성 재검토)은 아직 발동 조건에 도달하지 않아 열어 둔다.

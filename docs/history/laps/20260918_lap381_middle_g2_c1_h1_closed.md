# lap381 middle — 실행권한 복구 검증 · C1 종결 · H1 확정

- 날짜: 2026-09-18 18:12 KST
- lap: 381 (`loop/.lap_counter` = 381)
- 역할: 중간 tier 진단/계획/확인 (Claude Code claude-opus-5 / high)
- 목표: G2. STATUS "다음 한 가지" = lap380 실행권한 blocker 해소 · 범위 수정 · Sonnet handoff
- 게임 실행 0, 바이너리 편집 0, 제품 코드 0, 커밋 0

## 1. 가설

lap380은 구현 실패가 아니라 **환경(Bash 실행 권한) 실패**로 세 게이트를 못 돌렸다.
권한이 복구된 세션이면 (a) 세 게이트가 그대로 PASS하고, (b) lap380이 mapper 선행조건으로
남긴 C1/H1을 원본 바이트로 닫을 수 있다.

## 2. 변경 파일

| 파일 | 상태 | SHA256 |
|---|---|---|
| `docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py` | 수정(경로 1줄) | `80dc357f65ca75a056140363ad7188b231be11dd243ece30d0e83f815095ab7c` |
| `docs/history/laps/probes/20260918_lap381_middle_g2_c1_h1_access_width_probe.py` | 신규 | `0a66a29feb1ecdac7ce659171fd202a9be74a51cc6aeac11afe27c06d4e1b0b4` |
| `docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md` | 수정(§7 정정) | `933fdc868580f60f1bd5bcba6e75f3e15a375f441629127295d18b6d871fe16e` |
| `docs/work/active/G2_STORAGE_LAYOUT_SONNET_HANDOFF_LAP381.md` | 신규(handoff) | `43b0489bfdefbaef86553e256a4a0e63b4d357aec40505fcd1d1d76bc22c9c01` |
| `docs/STATUS.md` | 수정(**129줄**, cap130, Blockers 1개, `CONTEXT_PASS`) | `ad735d77ce0ae19936e7b9d399a374a36bd2648d1a3cf7e2008fb5f35dbaca26` |
| `loop/ESCALATE_SOL` | **소비·삭제** (원문 부록A 보존) | 삭제 전 `cb0955ede719ffc11243d885b0d254d6dc066944bf77701ee0e80909e186f7b7` |

원본 `Syw2plus/syw2plus_original.exe` = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
(보호 pin과 동일, 무변경). 원본/참고/공유 저장소 쓰기 0건.

lap380 probe는 `REPO = parents[3]`가 `docs/`로 해석돼 원본을 못 찾았다(STATUS가 예고한 결함).
`parents[4]`로 고친 것이 유일한 수정이며 단언은 건드리지 않았다.

## 3. 실행 명령과 수치

| 명령 | 결과 |
|---|---|
| `make check` | **rc0 — 633 passed / 129.48s**, Ruff `All checks passed`, compileall, mypy `10 source files` Success, `CONTEXT_PASS` |
| `checks/safety.sh check` | **rc0 — `SAFETY_PASS`** |
| `python3 …20260918_lap380_middle_g2_tail_layout_facts_probe.py` | **rc0, `failures=[]`** (전 단언 PASS) |
| `python3 …20260918_lap381_middle_g2_c1_h1_access_width_probe.py` | **rc0, `failures=[]`** |

lap380이 승격 대기로 남긴 세 명령이 전부 실측 PASS다. 이것은 Fast 게이트일 뿐이고
실제 앱/24k/멀티 증거가 아니다.

## 4. lap380 §1 표의 바이트 재유도 (PASS)

원본 PE에서 fresh 재유도: ImageBase `0x400000`, SectionAlignment/FileAlignment 모두 `0x1000`,
SizeOfImage `0xc8f000`, 섹션 4개.

```
.text   va=0x401000  vsz=0xe3ae5  raw=0x1000   rsz=0xe4000
.rdata  va=0x4e5000  vsz=0x6eec   raw=0xe5000  rsz=0x7000
.data   va=0x4ec000  vsz=0xb9fa38 raw=0xec000  rsz=0xd000   raw_end_va=0x4f9000
.rsrc   va=0xc8c000(rva) vsz=0x20f0 raw=0xf9000 rsz=0x3000
```

- `0x66B790 + 0x758*1200 == 0x892410` 성립 (unit_pool 끝 = bulk save 시작 = live state base).
- **여섯 저장영역과 그 사이 간극은 전부 `.data`의 BSS다** (`0x4f9000` raw_end 위). 새 사실.
- tail 위에 있는 섹션은 **`.rsrc` 하나뿐**이다.
- base relocation directory **부재** 확인 → tail 위 절대 VA는 전부 수동 fixup 대상.

## 5. C1 — **종결(CLOSED). count는 WORD다.**

lap380은 "count가 dword면 catB 첫 원소 하위 2바이트를 덮는다"를 mapper 선행조건으로 남겼다.
문제의 주소는 전부 BSS라 **파일에 바이트가 없다**. 따라서 판정 근거는 접근 코드의
x86 operand size뿐이다. `0x48bc92..0x48bcd9` 선형 디스어셈블(원본 바이트):

```
0x48bc92 66ff0508599700   inc   word ptr [0x975908]
0x48bca1 0fbf0dc8c28900   movsx ecx, word ptr [0x89c2c8]      ; count 읽기 = WORD
0x48bcae 89148d08b08900   mov   dword ptr [ecx*4+0x89b008], edx ; catA[count] = DWORD
0x48bcb5 66ff05c8c28900   inc   word ptr [0x89c2c8]           ; count 증가 = WORD
0x48bcbe 0fbf058ad58900   movsx eax, word ptr [0x89d58a]
0x48bccb 890c85cac28900   mov   dword ptr [eax*4+0x89c2ca], ecx ; catB[count] = DWORD
0x48bcd2 66ff058ad58900   inc   word ptr [0x89d58a]
```

`66` operand-size prefix가 raw 바이트에 그대로 보인다. probe는 세 alias
(`0x89c2c8`, `0x89d58a`, `0x975908`) 전체 참조에서 **operand size = {2} 뿐**,
4바이트 접근 **0건**으로 재확인했다. `0x89c2ca` 참조는 정확히 1개이며 DWORD(elem=4)다.

**판정:** manifest의 "live **dword** count field" 라벨은 **오기**다. `0x89c2c8`은 WORD count이고
catA end와 catB base 사이 2 B 간극이 **바로 그 count**다. **영역 겹침은 없다.**
lap380이 경고한 "조용한 손상" 분기는 닫혔고 mapper는 이 위에 쌓아도 된다.

## 6. H1 — **확정(CONFIRMED, shape만). 8×200 WORD matrix다.**

간극 `0x89a388..0x89b008` = `0xC80` = 3,200 B. lap380은 "크기 일치는 증거가 아니다"라며
외래 불변 블록으로만 취급하라고 했다. 참조 5개 전부 WORD, index scale 2:

```
0x43e887 668b3c7588a38900   mov   di,  word ptr [esi*2+0x89a388]
0x47f447 66833c4588a3890000 cmp   word ptr [eax*2+0x89a388], 0
0x47f8de 6639044d88a38900   cmp   word ptr [ecx*2+0x89a388], ax
0x49b373 66833c7588a3890000 cmp   word ptr [esi*2+0x89a388], 0
0x4a7f3f 0fbf144d88a38900   movsx edx, word ptr [ecx*2+0x89a388]
```

기하만으로는 "8행×200열"과 "200행×8열"을 못 가른다. 인덱스를 만드는 주소 산술이 가른다:

```
0x49b36a lea esi,[eax+eax*4]   ; 5*row
0x49b36d lea esi,[esi+esi*4]   ; 25*row
0x49b370 lea esi,[edx+esi*8]   ; 200*row + col
0x49b373 cmp word ptr [esi*2+0x89a388], 0
```
`0x47f8d2`에서 동일 사슬 독립 재현. 주소 = `0x89a388 + 2*(200*row + col)`,
span 3,200 B ⇒ **row는 8개**.

**판정:** row stride 200 elements, element WORD, 8행. H1의 **형태는 확정**.
다만 **의미는 UNKNOWN**이다 — 8이 owner 수와 같다는 것은 강한 읽기지만 증명이 아니고,
lap380이 든 반대 근거(owner roster는 PlayerStruct `+0xd4a` 4바이트 목록, owner 상한 250)는
이 블록이 owner roster가 **아님**을 보일 뿐 row 축의 정체를 정하지 않는다.

**mapper 영향:** 이 블록은 "외래 블록"이 아니라 저장 계열의 일부지만, 크기가
`8*200*2`로 **N과 무관**하다. 따라서 N을 올려도 **크기 불변**이고 **주소만** 아래쪽
삽입량만큼 이동한다.

## 7. 계획 문서 범위 정정 2건 (STATUS 지시)

lap380 계획 `G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md`를 이번 lap이 고쳤다.

1. **"외래 블록 delta 0"은 틀렸다.** 외래 블록은 **크기**가 불변이지 **delta 0**이 아니다.
   자기보다 아래에 삽입된 누적량만큼 주소가 이동한다. delta 0으로 구현하면 외래 블록이
   확장된 영역과 겹친다. §2 C3과 §3.2 계약을 "외래 블록: size invariant, delta = 자신보다
   낮은 주소의 누적 삽입량"으로 정정했다.
2. **private non-launchable PE-layout artifact는 필수다.** 단순 JSON 계산기로 축소 금지
   (Astra 원문 범위). §3에 명시했다.

## 8. PASS / FAIL / SKIP

- PASS: `make check`(633), safety 2종, lap380 tail probe rc0, lap381 C1/H1 probe rc0,
  원본 SHA 불변, C1 종결, H1 형태 확정.
- FAIL: 없음.
- SKIP: 게임 실행, 실제 24k/144k, mapper 구현(=Sonnet work tier 범위), H1 의미 규명.

## 9. fixture

원본 EXE `b569…a8ac` 정적 바이트만. 게임 프로세스/세이브/네트워크 fixture 없음.
capstone 5.0.7 디스어셈블은 읽기 전용이며 새 의존성 추가가 아니다(기설치).

## 10. 다음 행동

C1/H1이 닫혔으므로 lap380 계획 §3~§5의 선행조건이 **전부 충족**됐다.
다음 work 회차(Sonnet5/high)가 `patches/population/base_preserving_storage_layout_v1.py` +
테스트를 착수한다. 핸드오프 카드: `docs/work/active/G2_STORAGE_LAYOUT_SONNET_HANDOFF_LAP381.md`.

## 부록 A — lap380 `loop/ESCALATE_SOL` 원문 (소비, 삭제하지 않고 보존)

```
ESCALATE_SOL — lap380 (2026-09-18, middle Opus5/high)

## 사유: 필수 게이트 실행 불가 (환경), 구현 실패 아님

이 세션은 Bash 실행 권한이 없다. 다음이 전부 승인 대기로 거부됐고 비대화형이라 승인할 수 없었다:

  - make check
  - checks/safety.sh check
  - python3 docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py

읽기 전용 명령(ls/grep/sed/cat/wc)만 통과했다. 이전 lap들은 loop/loop.sh 러너가 띄웠고
이번 세션은 그 경로로 뜨지 않았다. 저장소에 .claude/settings.json 은 없다.

## 이번 lap이 실제로 남긴 것

- docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md  (STATUS가 지정한 Opus 산출물)
- docs/history/laps/20260918_lap380_middle_g2_base_preserving_storage_plan.md
- docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py  (작성됨, 미실행)
- 제품 코드/바이너리/원본/공유 파일 변경 0건. 게임 실행 0. 커밋 0.

## 승격 작업자가 이어서 검증할 것 (순서대로)

1. 실행 권한이 있는 세션에서 위 3개 명령을 실제로 돌린다. probe rc0, make check PASS,
   safety 2종 PASS, 보호 8 pin 불변을 실측으로 적는다.
   probe는 §1 표(여섯 저장영역·3중 alias 0x892410·BSS 여부·relocation dir 부재)를
   원본 바이트에서 fresh 재유도한다. 이번 lap은 손계산 정합성만 확인했다.

2. C1을 원본 바이트로 닫는다 (mapper 착수의 선행조건).
   manifest는 0x0089C2C8 을 category_slot_list_a 의 exclusive end 이자
   "live dword count field" 로 기술하는데, category_slot_list_b base 는 0x0089C2CA (= +2) 다.
   count 가 dword 면 catB 첫 원소의 하위 2바이트를 덮는다.
   → count 가 실제로 WORD 인가(라벨 오기), 아니면 두 영역이 진짜 겹치는가?
   0x0089D58A 의 list-B end/count alias 도 같은 형태다.
   추정으로 한쪽을 고르면 접근 위반 없이 조용한 손상이 난다. 반드시 바이트로 판정한다.

3. H1 을 확인하거나 기각한다. age end 0x0089A388 → catA base 0x0089B008 간극 0xC80 = 3,200 B
   = 8 x 200 x 2 로 STATUS 의 "고정 8x200 WORD matrix" 와 크기가 정확히 일치한다.
   크기 일치는 증거가 아니다. 반대 근거: owner roster 는 PlayerStruct +0xd4a 의 4바이트
   목록이고 owner 상한 시작값은 250 이다. 확인 전에는 외래 불변 블록으로만 취급한다.

4. 1~3 이 닫힌 뒤에만 Sonnet5/high 가 patches/population/base_preserving_storage_layout_v1.py 와
   테스트를 작성한다. 계약/회귀/중단조건은 계획 문서 §3~§5 참조.
   N=1200 항등이 최상위 회귀 앵커다. offline_storage_v1 은 frozen, 변경 금지.

## 승격 작업자가 판정해 줄 것

- 이 루프를 실행 권한 있는 세션으로만 돌릴 것인지(러너 경로 고정), 아니면 실행 불가
  세션에서도 문서 lap 을 허용할 것인지. 후자면 implementation-unchanged-streak 규칙과
  충돌한다: 진입 시 streak=1 이었고 이번 lap 도 제품 코드 0 이라 streak=2 다.
  PROMPT ③ 상 세 번째 무변경 회차는 Astra/Sol 의 계속/중단 판정이 먼저 필요하다.

- lap379 Sol 의 "integration/automatic broad patcher/runtime NO-GO" 는 유효하다.
  이번 layout-only 카드는 그것을 뒤집지 않으며, 완료돼도 G2 는 미완료다.
  tail 참조 이전 부채(lap379 재집계 17,584 linear 후보)는 그대로 남는다.

## 보존

현재 변경은 전부 uncommitted 로 보존한다. 삭제·되돌림 금지.
LOOP_ALLOW_COMMITS 는 0 이므로 커밋하지 않았다.
```

### 부록 A 처리 결과

- 항목 1 → §3/§4에서 실측 PASS로 **해소**.
- 항목 2 (C1) → §5에서 **CLOSED**.
- 항목 3 (H1) → §6에서 **CONFIRMED(shape)**, 의미는 UNKNOWN으로 남김.
- 항목 4 → 선행조건 충족, §10 handoff로 이관.
- 판정 요청 1(러너 경로) → **이번 세션은 실행 권한이 있었다.** 환경 blocker는 재현되지 않았고
  streak 갈등 전제가 사라졌다. 러너 경로 고정 여부는 여전히 Astra/사용자 결정 사항으로
  **미결 보존**한다(이번 lap이 임의로 정하지 않는다).
- 판정 요청 2(lap379 NO-GO 유효성) → **그대로 유효**. 이번 lap은 뒤집지 않는다.
  tail 참조 이전 부채 17,584 linear 후보도 그대로 남는다.

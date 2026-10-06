# 2026-09-28 | lap 750 | 목표 G5 (middle: v8 기준 체크리스트 A~H 최종 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·컨펌).
  게임 코드·EXE·probe 수정 없음(문서만).
- 가설 / 사용자 관찰: STATUS "다음 한 가지" — lap746~749 work가 H-STALE-TAIL(v8)·S3 대체경로(S4/S5)·
  홀드버튼 편차를 해소했다고 보고했으니, middle이 v8 기준 A~H를 최종 재검수하고 PASS면 사용자
  milestone 재상정 여부를 판단한다.
- 예상 PASS / FAIL 조건: v8 재빌드 SHA `ef46d1ac…` 일치, v7→v8 차이 1바이트, lap746/748/749 raw가 각
  lap 주장과 일치, 새 부작용 경로 없음 → PASS. raw가 주장과 다르거나 미검증 사용자 경로가 남으면 HOLD.
- 변경 파일 / 커밋: 문서만 — 이 파일, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`,
  `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(lap750 섹션 추가). 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA: 보호 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` =
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(세션 시작·종료 동일).
  v7 = `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`,
  v8 = `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`.

## 실행 명령 (전부 이번 세션에서 독립 실행)

1. `PYTHONPATH=. python3 -m patches.selection.g5_selection_cap50_v{7,8} "<[HQ]Syw2plus 2002.exe>" /tmp/lap750/v{7,8}.exe`
   → v7 `30efafa0…`, v8 `ef46d1ac…` **기록과 동일**. `cmp -l v7 v8` = **파일 오프셋 `0xFB1BD` 1바이트
   `0x14→0x32`뿐**. capstone: `0x108f1bc mov ecx,0x32; sub ecx,ebx; xor eax,eax; rep stosd` — 로드
   래퍼가 legacy count(≤20)만큼 복사한 뒤 나머지 `50-count`칸을 0으로 채운다(v7은 `20-count`).
2. `pytest -q patches/selection/test_g5_selection_cap50_v{7,8}.py` → **9 passed**. `checks/safety.sh check`
   → `SAFETY_PASS`. `checks/context_limits.py check` → `CONTEXT_PASS`. `make check` → 아래 "검증" 참고.
3. raw 재계산(공유 `temp/Syw2plus_patch/`): `20260928_lap747_v8_coverage/{original,original2,original3,
   candidate,candidate2,candidate3}`, `20260928_lap749_v8_coverage_hold/candidate{,2,3}`,
   `20260928_lap746_g5_h_stale_tail/{original,candidate,candidate2_negcount_save,v8_candidate}`,
   `20260928_lap748_g5_s4s5_{original,v8,v8_retry}`의 `probe-result.json`.
4. 정적: v8 전체에서 `call 0x4da4a9`/`0x4da39f`(블록 read/write) 호출지 전수, `push 0x892410`(저장 창)
   참조 전수, `0x108c000/0x108c004` 참조 전수, `.text` 안 `0x899024/0x899028` 절대참조 0건 확인.

## 재계산 결과

### 홀드버튼(lap747/749) — 결론 유지, lap749의 원인 설명은 정정

| 실행 | 창 | `pending_changed_to` 0x1000027 | 목표값이 curve에 보인 시점 |
|---|---|---|---|
| lap747 original ×3 | 3s | 20/20 ×3 | t=0.0 / 0.0 / 0.051 |
| lap747 v8 cand1 | 3s | 0/50 | 없음 |
| lap747 v8 cand2 | 3s | 50/50 | t=0.051(이동 중 4기는 0.35s까지 유지) |
| lap747 v8 cand3 | 3s | 3/50 | t=0.0에 이미 3기만(이동 중 유닛), 47기는 이미 0x1000001 |
| lap749 v8 ×3 | 10s | 50/50 ×3 | t=0.052 / curve 밖(2.4s 이후) / t=0.051 |

- `observe()`는 `act()`(클릭 서브프로세스) **반환 후** 샘플을 시작하고, 홀드 pending 표식은 한 샘플
  (≤50ms 로그 간격, 내부 10ms)만 보이는 transient다. 원본도 3회 중 2회는 t=0.0 첫 샘플에서만 잡혔다.
- 따라서 0/50·3/50은 **클릭→첫 샘플 사이에 transient가 이미 끝난 race**(3/50 = 아직 이동 중이라 표식이
  오래 남은 유닛만 잡힘)로 설명된다. lap749의 "50기 청크 재발행이 3초 창을 넘겨서"라는 설명은 raw가
  뒷받침하지 않는다 — lap749 3회 중 2회는 t≈0.05에 잡혀 3초 창으로도 50/50이었을 것이다.
- 관측될 때마다 50기가 같은 샘플에서 함께 바뀌었고(원본 20기와 같은 패턴), 단축키 H는 v8 6/6 50/50,
  v7→v8 차이는 명령 경로와 무관한 로드 래퍼 1바이트다. **홀드버튼 = PASS(probe race, 회귀 아님).**
  probe는 앞으로 "act 전에 샘플러 시작"이 필요하다(비차단 권고).

### (F) H-STALE-TAIL — S1/S2/S4 재계산 일치, **S5는 공허**, S3 미검증

| 실행 | load 후 count/비0칸 | 해제 후 | 로드 밖 명령 | S4 재시작 후 | S5 load 전→후 |
|---|---|---|---|---|---|
| lap746 원본 | 20/20 | 0/0 | 0 | — | — |
| lap746 v7 | 20/**50** | **-30**/0 | **30** | — | — |
| lap746 v8 | 20/20 | 0/0 | 0 | — | — |
| lap748 원본 | 20/20 | 0/0 | 0 | 0/0 | **0/0 → 0/0** |
| lap748 v8(retry) | 20/20 | 0/0 | 0 | 0/0 | **0/0 → 0/0** |

- S1/S2(같은 세이브 재로드)와 S4(재드래그 50 → 저장 → 재개 → 다시하기)는 기록과 일치, PASS.
- **S5는 S4 재시작 직후에 실행돼 `selection_before` count=0·전칸0, fixture 유닛도 이미 없음**
  (`tools/g5_stale_tail_probe.py:611-622`의 주석 "live 50-selection still selected"와 실제 순서 불일치).
  lap748 기록의 "50기 선택 이월 없음"은 S5에 대해 **raw가 뒷받침하지 않는다**. 다만 정적으로 저장 창
  `0x892410`을 읽는 로드는 `0x4412d7 push 0x892410`→`0x4412dc`(v8 `LOAD_WRAPPER`) 한 곳뿐이라, 다른
  세이브 로드도 S1과 같은 래퍼를 지난다 → **S5 = S1 runtime + 정적 귀속으로 PASS 처리 가능**(런타임
  S5 자체는 무효).
- **S3(초기메뉴→새 게임)는 여전히 UNKNOWN이고 이것이 남은 실제 위험이다.** v8에서 새 선택 count를
  쓰는 곳은 `0x412e6e` inc·`0x412ed2` dec·`LOAD_WRAPPER`뿐이고 명시적 0 초기화가 없다. `.text`에는
  `0x899024/0x899028` 절대참조가 0건이라, 원본이 새 게임 때 레거시 선택을 `this(0x892410)+오프셋`이나
  memset으로 비운다면 그 초기화는 옛 영역만 비우고 새 배열(`0x108c000`, 저장 창 밖)은 남는다. S4가
  0/0이 된 주체(유닛 해체 시 dec 50회인지, 재시작이 세이브 로드 경로 = `LOAD_WRAPPER`를 타는지)가
  귀속되지 않았으므로 S4 PASS를 S3로 일반화할 수 없다. 이월되면 새 판에서 count>0·옛 slot ID가 남아
  다른(적일 수도 있는) 유닛에 명령이 가는 H-STALE-TAIL과 같은 급의 결함이 된다.

## 항목별 판정 (v8 기준)

| 항목 | 판정 | 메모 |
|---|---|---|
| A 정적 전수 | PASS(보완) | `.text` 레거시 절대참조 0건 재확인. 새 배열 count 쓰기 3곳뿐 → "새 게임 초기화" 행 누락(S3). |
| B 선택 변화 | PASS | v7→v8은 로드 래퍼 1바이트, lap747 v8 드래그4종·더블클릭·Shift·51번째 거부 실측 PASS. |
| C 명령 | PASS(알려진 UNKNOWN/N/A) | 홀드버튼 위 정정 포함. 미니맵 우클릭·능력 v UNKNOWN, 건설·승선 N/A 유지. |
| D 부대 | PASS | lap747 v8 roundtrip `PASS_UI_ROUNDTRIP` 7/7, 사망 후 호출은 v6 이후 경로 불변. |
| E UI | PASS(조건부) | lap745 판정 유지(체력바 46/50 가림 PLAUSIBLE). |
| F 저장/로드 | **HOLD(좁음)** | S1/S2/S4 PASS, S5 런타임 공허(정적 귀속으로 수용), **S3 새 게임 이월 UNKNOWN**, 알려진 제한: 부대 미지정 선택 로드 후 20기. |
| G 멀티 | BLOCKED(env) 수용 | lap742/743 근거 유지. |
| H 장시간 | PASS | lap743 v7 8019 tick. v7→v8 1바이트는 로드 경로만. |

**종합: G5 v8 = `HOLD(좁은 조건부)` — 사용자 milestone 재상정·G1 착수 안 함.** 남은 것은 S3 한 경로의
귀속·실측뿐이다.

## 다음 한 가지 (work tier, 구현 우선, 1 lap)

1. **S4 재시작 초기화 주체 귀속(가장 싼 결정 실험):** `tools/g5_stale_tail_probe.py`에 S1 없이 "50 드래그
   → 다시하기 → 50칸 전체 dump"만 하는 모드를 추가해 **v7**(`30efafa0…`, 로드 래퍼가 20칸만 0 채움)로
   1회 실행. v7에서도 재시작 후 count=0·비0칸 0이면 재시작은 유닛 해체(dec) 경로로 비워지는 것 → S3도
   같은 해체를 탈 가능성이 높다. v7에서 21~50칸이 남으면 재시작은 세이브 로드 경로(`LOAD_WRAPPER`)로
   비워진 것 → 새 게임 경로는 별도 보장이 없다.
2. **S3 실측 재시도:** 같은 probe로 원본/v8 paired, fixture 생성 전(순정 로비 시작 직후)에 `초기메뉴`
   확인이 메인 메뉴로 가는지 먼저 확인하고, 가면 fixture 후 50 선택 → 초기메뉴 → 새 게임 → 50칸 dump.
   메인 메뉴로 끝내 못 가면 원본과 동일 제약으로 기록하되 1번 결과와 함께 판단.
3. 1이 "로드 경로" + 2가 불가/FAIL이면 **v9 최소 수정**: 새 게임 초기화 지점 한 곳(레거시 선택 초기화를
   하던 원본 명령)을 귀속해 새 배열 51칸(count+50) 0 채움을 추가, 바이트범위 pytest + `make check` + S1/S4
   + 핵심 회귀 1회. S5 순서 버그(S4 뒤 실행)는 S5 전에 50 재드래그를 넣어 같이 고친다.
4. 결과가 PASS(또는 원본과 동일)면 새 middle이 F만 재검수 → 사용자 milestone 재상정(멀티 BLOCKED,
   부대 미지정 선택 로드 후 20기, 미니맵/능력 v UNKNOWN, 건설·승선 N/A를 알려진 제한으로 명시).

## 검증

- `make check`: 결과는 STATUS 검증 상태에 기록(`/tmp/lap750/make_check.log`).
- 게임 실행 0회(middle, raw 재계산만), 원본/참고 저장소 쓰기 0, 게임 사본 생성 0.

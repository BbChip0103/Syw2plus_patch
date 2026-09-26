# lap366 middle — S1 원본-load cleanup/finalize 수리 범위 (work tier handoff)

2026-09-12 / lap366 / Codex 현재 세션 / 정확한 모델 ID는 노출되지 않아 주장하지 않음 /
사용자 지정 high·middle(진단·계획·확인). 외부 provider 호출, 게임 코드·하네스·tests hands-on
수정, 게임/Wine/Xvfb/입력/PNG 실행은 모두 0이다.

상위 계약은 `G1_S1_MIDDLE_EXECUTION_ENVELOPE_LAP362.md` §3이고, 직전 독립 판정은
`docs/history/laps/20260912_lap365_middle_s1_original_load_review.md`다. 이 문서는 lap365
F1~F3의 원인을 확인하고 모순 없는 수리 범위를 Luna/high work에 넘긴다. 실제 원본 run,
S1/Stage B/G1 판정, 제품·출시 승인, 마일스톤 종료/이동은 허가하지 않는다.

## 0. 판정

**lap365 REJECT를 CONFIRM하고, 아래 좁은 repair envelope를 RELEASE한다.**

| 항목 | 판정 | 현행 근거 |
|---|---|---|
| cleanup 실패 fail-closed | **FAIL** | `runtime_env.py:3846-3854`는 `cleanup.ok=false`를 기록하지만 앞선 PASS를 UNKNOWN으로 내리지 않음 |
| post 3초 범위 | **FAIL** | `:3762-3767`은 collector의 post snapshot만 제한하고 `:3777-3795` evaluate를 제한하지 않음 |
| artifact/cleanup 순서 | **계약 충돌 해소** | cleanup 결과를 포함하려면 final artifact는 cleanup 뒤 한 번만 써야 함 |
| 전체 150초 | **FAIL** | `:3870-3874` artifact write 전후 total deadline gate가 없음 |
| command 회귀 | **FAIL** | targeted 24개 중 새 command 검사는 dispatch 1개뿐이고 §3.4 (a)~(h)를 직접 호출해 잠그지 않음 |

현행 세 source SHA는 lap363 제출값과 일치한다. fresh targeted는 24 passed였지만 이는 위
command 계약을 시험하지 않으므로 구현 ACCEPT가 아니다.

## 1. lap362 §3.2~§3.3의 충돌 판정

다음 의미로 계약을 고정한다.

1. `post_finalize` 3초는 **PS3 도달 직후 시작하는 direct post snapshot + evaluate + 최종 JSON
   payload 준비**의 합산 상한이다. cleanup은 이 3초에 포함하지 않는다.
2. final artifact 경로는 cleanup 전에 만들지 않는다. owned cleanup이 끝난 뒤 cleanup 결과,
   residue PID, elapsed/deadline 판정을 포함한 **단일 새 artifact**를 쓴다.
3. 마지막 10초는 `cleanup_artifact` reserve다. cleanup과 final artifact 설치가 함께 소비하며,
   final artifact는 command 시작+150초보다 늦게 설치할 수 없다.
4. 3초/150초 초과, cleanup `ok=false`, finalization 실패 중 하나라도 있으면 기존 PASS를
   `status=UNKNOWN`으로 강등하고 명시적 classification/error를 남긴 뒤 command가 nonzero로
   끝난다. cleanup 실패 run이 PASS를 반환하거나 PASS artifact를 남기면 안 된다.
5. hard deadline 때문에 final write가 끝날 시간을 보장할 수 없으면 final 경로에 직접 쓰지 않는다.
   work는 같은 output 안의 fresh temporary payload와 bounded write/atomic install 같은 방식으로
   **완성본만** final 경로에 설치해야 한다. timeout 시 final PASS artifact는 없어야 하며 log,
   source snapshot, partial/failure 위치와 residue 진단은 보존한다. overwrite는 계속 거부한다.

이 판정은 예산 확대가 아니다. 기존 150초, operation 140초, final reserve 10초는 그대로다.
기존 `post_finalize` 이름을 유지할지는 구현 세부지만, evidence의 stage 이름과 실제 측정 범위가
일치해야 한다. 단순히 상수/문서 이름만 바꾸는 것은 수리가 아니다.

## 2. Luna/high work 수리 범위

허용 파일은 다음 세 개뿐이다.

- `tools/runtime_env.py`
- `tools/s1_load_evidence.py`
- `tests/test_s1_load_evidence.py`

필수 변경:

1. post snapshot과 evaluate의 elapsed를 같은 3초 창으로 합산하고, 초과 시 UNKNOWN/nonzero로
   fail closed한다. collector가 반환하는 post elapsed/deadline 근거를 command가 검증 가능해야 한다.
2. cleanup 후 `cleanup.ok`를 최종 status/classification에 결합한다. cleanup 실패 시 이전
   evaluation PASS를 보존용 nested result로 둘 수는 있으나 top-level PASS는 금지한다.
3. cleanup과 artifact finalization을 150초 전체 deadline 안의 마지막 10초에 결합한다.
   final artifact는 cleanup 결과를 포함하고 exact-once/overwrite 거부를 유지한다.
4. 실패 artifact/log에는 stage start/end/elapsed, last raw, trigger count/argv/좌표, cleanup/residue,
   deadline 종류를 보존한다. final artifact를 안전하게 설치하지 못한 경우 그 사실과 남은
   partial/log 경로를 stderr/예외에 명시한다.
5. offline `--post-json`, 기존 `g1-s1-load-evidence --pid`, 원본 R1/candidate R1 경로의 의미와
   public evidence schema는 이번 수리 때문에 약화하지 않는다.

## 3. 필수 합성 command 회귀 — lap362 §3.4 (a)~(h)

실제 Wine/game 없이 `g1_s1_original_load_evidence()`를 fake clock과 격리된 fake
prepare/process/input/read/cleanup 경계로 직접 호출한다. 단위 helper만 시험하거나 AST/문자열
존재만 확인하는 것으로 대체하지 않는다.

- (a) command timer가 source validation/prepare 전에 시작하며 prepare 지연이 150초와 60초를 소비한다.
- (b) trigger 지연이 event deadline과 total deadline을 함께 소비하고 자동 재클릭/재실행은 0회다.
- (c) direct pre가 `(PS,group,slot)!=(35,0,1)`이면 load trigger는 정확히 0회다.
- (d) load root 좌표는 `content_crop+(400,131)`이고 presentation scale을 곱하지 않는다.
- (e) helper는 기본 repeat1이며 focus/click callback과 collector 보고가 exact-once다.
- (f) prepare60/launch40/input20/pre2/trigger5/wait10/post+evaluate3/cleanup+artifact10의 각 cap과
  전체150을 경계값 안 PASS·경계 초과 UNKNOWN/nonzero로 잠근다.
- (g) cleanup `ok=false`, post/evaluate timeout, partial read 각각이 top-level PASS를 만들지 않고
  last raw/cleanup/residue/evaluation 원문을 보존한다.
- (h) 기존 artifact, snapshot, temporary/final 경로 충돌을 launch 전에 거부하고 어떤 파일도
  덮어쓰지 않는다. 성공 경로 final artifact 설치는 정확히 1회다.

추가로 cleanup 실패와 artifact deadline 초과에 대해 **artifact 내부 top-level status도 PASS가
아님**을 읽어 확인한다. 함수가 예외를 냈다는 사실만 검사해서는 안 된다.

## 4. work 검증과 반환 조건

work는 실제 게임/Wine/Xvfb/클릭/PNG를 0회로 유지하고 다음을 순서대로 제출한다.

1. 세 허용 파일의 편집 전/후 SHA256과 실제 provider/model/effort.
2. `.venv/bin/python -m pytest -q tests/test_s1_load_evidence.py` 전체 PASS와 신규 test node ID.
3. repo-root provenance를 출력한 뒤 원본 lap354 probe를 **정확히 1회** 실행하여 rc0/
   `failures=[]`; 역사 probe 자체는 수정·재pin하지 않는다.
4. `make check`, `.venv/bin/python checks/safety.py`, `bash checks/safety.sh check` fresh PASS.
5. 생성 파일/fixture/실행 0회와 남은 UNKNOWN을 LAP_TEMPLATE 형식으로 기록한다.

다음 새 middle이 SHA→diff→신규 command 회귀→lap354 exact-once→Fast→safety를 독립 검수하기
전 실제 원본 n=1 실행은 금지한다. exit0/테스트 수 증가는 자기 승인이나 제품 PASS가 아니다.

## 5. 금지와 다음 한 가지

원본/EXE/DLL/save/fixture/pin/reference/golden 수정, 과거 probe 재pin, timeout 확대, 재클릭,
게임/Wine/Xvfb/입력/PNG, Stage B/P6/WM_CLOSE/G2~G4, 새 의존성, 커밋은 금지한다.
W3/N14, lap331 identity UNKNOWN, S1 두 run 결정성은 그대로 남긴다.

**다음 한 가지:** Luna/high work가 §2~§4만 구현·검증하고 다음 middle 검수로 반환한다.

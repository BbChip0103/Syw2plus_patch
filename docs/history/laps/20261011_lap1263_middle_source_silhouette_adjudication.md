# 2026-10-11 | lap1263 | G1 tree_plus 원본 실루엣 독립 판정 / 근거 충돌 승격

- 지정 역할: middle(진단·계획·확인), fresh Codex App. MODEL_ROUTING 선택 sol/high; actual resolved ID/effort는 노출되지 않아 추측하지 않음. runtime counter1263 읽기만. HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`, 호출 source `fdb943bc3ce3d114998fe6cb507c18df88b0ea04`는 provenance이며 전체 Fast 합격 지문이 아님.
- 목표/가설: STATUS의 다음 한 가지 — lap1262가 중단한 root의 “원본 실루엣 밖 4화소 → 투명화” 지시를 exact source/sidecar와 대조. 성공식은 불투명 영역 비교·원본 stream identity·raw를 직접 확인하여 허용 수리 범위를 정하는 것; runtime reject0/G1 완료/전달 승인이 아님.
- ①~②: PROMPT 먼저 → AGENTS/INBOX 최신 지시·APPROVALS 미결/반려 → STATUS 전체 → DESIGN1~4/MODEL_ROUTING → lap1260/1261/1262·ESCALATE·해당 변환기/DLL의 좁은 코드 경로를 읽음. PROMPT의 오래된 G2 10000/G4 활성/Claude 고정은 최신 DESIGN/INBOX/MODEL_ROUTING을 우선. STOP 없음. STATUS72/INBOX324/APPROVALS52줄을 산출물 기록 전 확인.
- ③~④: hands-on 게임 코드/하네스/테스트/asset 수정0. 한 가지 source-mask 판정만 수행. 아래 직접 재계산이 root 원본외부 판정과 실질적으로 충돌하므로 사용자 escalation 조건에 따라 추가 수리·게임 실행·마감 없이 증거 보존/승격. 보조-only 상한을 새 카드로 초기화하지 않음.

## 직접 비교 근거

공유 temp `20261011_lap1263_middle_silhouette/`의 `compare.py`(SHA256 `480b0f5726721fe94bd720e891a9b46541ee27638cb43582ec6cff14d789f6b2`)로 재현. `evidence.json` SHA256 `976bb91778741d46fc0f5a49fb259c613ad05bc7de2e5eb082a97d9f497761e2`; 로그 `logs/gates/lap1263-silhouette-compare.log`. 모든 입력 읽기 전용.

| 입력 | SHA256 |
|---|---|
| 원본 `../[ESL]Syw2plus/fnt/tree_plus.spr` | `ba7b2503653f96cfc97ee7111852136c0fac8ecf7a00ae14414bbed781070a85` |
| lap1206 ref `fnt/tree_plus.spr/0000.png` | `ea98422518bb289b2e0fd7223c8928eacbfcb8cb4284764605781032cdc44221` |
| 사용자 upscaler `fnt/tree_plus.spr/0000.png` | `eef91ee4a1607d606ac59d3957edd267da63a21ea7c2c9c55bbb00d166c43883` |
| lap1258 sibling `fnt/tree_plus.spr.hd/0000.idx8` | `b2e246ea451f9d49999cc96a9a12db43ff29778719ecfe0bd5ad279530abfeef` |
| lap1260 actual key log | `84eaef270355bd914012545a0dcc0266cc16145291a30241dd2118c191a9962f` |
| lap1261 middle evidence | `77e58803e1ac16f4800230e18c9f4537e50d565111fb247a38328bb49cdd5062` |

- 공식2613 EXE SHA `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724` MATCH. objdump `--start-address=0x466ea0 --stop-address=0x466ff9` 저장 `writer_466ea0.txt` SHA `92243078f9a06603838a9dcc6a16bb9ae421de5e546234cc1fe99460dd63a8c9`. 원본 writer는 `0x466F8C` token 읽기, `0x466F8F` FE 비교, `0x466F99` skip 수만큼 열 증가, `0x466FC8` remap한 literal 저장, `0x466FD1` 행 너비 종료. 단순 외부 문서/기억 추정 아님.
- 소스 frame0 96×112, stream offset3060(0xBF4), 소비5761 B, FNV128=`44c611f6`, 팔레트=`cecc4681` MATCH. 원본 writer의 row-token 규칙을 독립 구현한 읽기 전용 decoder와 기존 extract의 idx/mask 완전 MATCH·행 overrun0·literal FE0. 원본 불투명5261.
- ref PNG의 원본 실루엣 차이0·불투명 색 차이0·게임 palette 동일. **sidecar 192×224 전체의 불투명 영역과 원본 mask 정수2배의 차이0(43,008 subpixels 비교)**. 사용자 upscaler PNG는 RGBA/192×224; alpha 단독을 원본 마스크로 삼지 않음.
- raw는 written5257/pack_opaque5261/opaque_unwritten4, first(51,104)/last(53,105). 첫/끝 위치는 원본 literal로 직접 확인: offset8799/index241, offset8806/index24. 주변 검사점(52,104)=offset8800/index106, (52,105)=offset8805/index241도 불투명. raw는 내부 2개 개별 좌표를 남기지 않았으므로 이 네 검사점을 실제 mismatch 전체 좌표라고 단정하지 않음. 전체 source-sidecar mask 동일성이므로 raw의 opaque-unwritten 어디든 원본에서는 opaque임은 확인됨.
- **판정: “원본 전체 실루엣 밖 화소” 주장은 반증. converter는 이미 ref silhouette을 강제하고 sidecar는 그 mask와 일치한다. 이 네 1배 화소에 대응하는 16 HD 화소를 투명화하는 것은 원본에 있는 디테일 삭제이므로 허용 근거 없음.** char 경로가 아니라 `fnt/tree_plus.spr.hd`가 실제 색인/raw 매핑이다(경로 전사 정정); 실루엣 판정 충돌 자체는 전사 오류가 아님.
- runtime identity-written mask가 4개를 놓친 원인은 **UNKNOWN**. clipping/cache/replay/source identity 중 어느 것인지 현재 raw만으로 귀속하지 않음. digest128 대응은 full runtime stream의 동일성을 새로 증명한 것이 아니며 실제 runtime mask 덤프도 없음. guard 완화/sidecar 수정/기존 reject1 삭제로 해결하지 않음. lap1260 새게임 clean dwell·absolute reject1과 기존 HOLD는 유지; 제품 크래시/화면 결함 재현 주장0.

## 명시적 handoff / 승격자가 결정할 범위

1. 승격 root/Sol은 root01:37의 작은 투명화 수리 항목을 위 source/raw로 정정하고 **asset·converter·silhouette guard 보존**을 확정한다. 앞서 전달한 HD판/새 H-HDLAYOUT 전달 경계/사용자 G1 마일스톤 수용을 이번 회차에서 판단하지 않는다.
2. work tier handoff는 기존 lap1261의 FEASIBLE display-only 변형2종 부팅·새게임·save006 타이틀로드 probe 그대로 재사용한다. default-on private DLL/runtime_bridge 미주입·unit/SFX/shadow/snapshot 진단 끔·G1 끔/켬 동일 variant 비교·PS/tick/camera/화면만 읽음·sidecar 불변·시작부터 key log. 해당 handoff 전체 안전/판정 계약 유지, stock-unit full pair 금지. **tree_plus 투명화/신규 converter 회귀는 제외**하고 알려진 reject를 absolute/key로 공개한다. 실게임 없이 보조 검수만 이어가는 카드 추가/같은 진단 run 반복은 하지 않는다.
3. 향후 실제 새 실행이 mask 문제의 제품 영향 또는 다른 reject를 드러낼 때만 work가 필요한 최소 runtime mask/replay 원인 확인·수리→관련 회귀→actual run을 수행한다. 원본 그림을 지워 수치를0으로 만드는 경로 금지. 이번 fresh middle은 게임 hands-on 구현하지 않고 소유권도 확대하지 않음.

## ⑤~⑥ 기록·검증·한계

- 변경파일: 이 lap 기록, byte-exact 보존 `20261011_lap1263_preserved_lap1262_escalate_sol.md`(원문 SHA `97b150d30dacc3420dc824d2cbaf3254fd4ce5bcb6c986d1bc9eca9bc131039e`), STATUS·INBOX 결과 메모, ignored ESCALATE_SOL. repo 밖 temp의 read-only 비교 스크립트/JSON/objdump가 증거. 기존 미커밋 구현6개 SHA는 evidence의 implementation_unchanged로 동결, 후속 검사에서 재확인. counter 쓰기0·game/prefix 생성0·원본/핀/raw/기존PNG 변경0·commit/delivery0.
- `make doctor`: setup/보호 원본 SHA verified·exit0. optional runtime manifest 없음(runtime.ok=false)은 fresh 실행 실패/성공으로 사용하지 않음.
- 비교 스크립트 assertion PASS: exact digest·raw/sidecar SHA·독립 row decode·palette·source/ref/sidecar mask. 최초 대화형 diagnostic은 Decoded.width 속성 오타로 실패; 실제 fw/fh로 즉시 정정 후 재계산 성공. 필수 gate/게임 실패가 아니며 원인 불명 재시도0.
- 전체 `make check`/lint/typecheck/build/patch생성·원복/fresh게임은 SKIP: 이번 회차 제품 소스0, PROMPT③·⑥ 문서-only 예외 및 사용자 검증 과잉 방지 지시 우선. 오래된 full-test-latest의 source mismatch/exit0 재사용0; source/도구 확인을 제품 진척/24k/144k/멀티/Windows PASS로 세지 않음.
- 독립 기술 판정은 원본 외부 실루엣 주장 반증에 한정. runtime mask 원인·variant 조합·H-HDLAYOUT 전달·사용자 마일스톤은 미검증/HOLD. 사용자 escalation 조건 때문에 loop/ESCALATE_SOL을 새 근거로 갱신 후 종료.
- 다음 한 가지는 STATUS에만 유지: 승격 root/Sol이 투명화 항목 정정·보존 범위를 확정하고, work에 기존 display-only actual probe를 돌려줌.

- 최종 fresh 검증: `.venv/bin/python checks/safety.py check --require-game` SAFETY_PASS, `.venv/bin/python checks/context_limits.py` CONTEXT_PASS, `git diff --check` exit0. 입력8개/구현6개 SHA 재확인MATCH·counter1263불변·Blockers1개·STATUS79/INBOX326/APPROVALS52줄. ESCALATE 존재·STOP생성0. 검사PASS는 문서/안전·읽기전용비교범위이며 실제게임/마일스톤PASS가 아님.

# 2026-09-30 | lap 819 | 목표 G1 (화면 전체 HD 그리기 전략)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(effort 세션 비노출), 지정 역할 strategy
  (계약 모델 Fable/Astra 자리를 lap770처럼 공개 대행; 자동 폴백 주장 아님). 게임 실행0, 제품/하네스
  source·binary 변경0, 커밋0.
- 가설 / 사용자 관찰: INBOX 22:2x 사용자 결정 "G1 = 고해상도 그림까지". 현재 W60 mirror는 sentinel 2×2 복제라
  coverage를 늘려도 nearest와 같은 그림이다. 원본 코드가 정한 쓰기 마스크 안을 원천 프레임 키에 묶인 2배 자산으로
  채우고(마스크 유도 치환), 자산 출처를 팔레트 인덱스 Scale2x로 두면 8bpp·night 팔레트·색상키와 충돌 없이 실제
  원본 그림 기반 2배 디테일 경로를 화면 전체로 확장할 수 있다. 최대 불확실성은 지형 writer 귀속(프리미티브 밖 가능).
- 예상 PASS / FAIL 조건: 원본 bytes로 프리미티브 인자 크기·타일 렌더 호출 구조를 확인하고, 사용자 기준을 측정
  가능한 지표·단계·합격식으로 옮긴 work 카드를 발행하면 PASS. 원본 bytes가 W60 전제와 충돌하면 카드 없이 승격.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W70_FULLSCREEN_HD_LAP819.md`
  (125줄, SHA256 `f439d6a372f456237af52f82167f7c602bb0a49a66e224fa18874ba885fe51cd`), 이 기록, `docs/STATUS.md`
  갱신, `docs/feedback/INBOX.md` 22:2x 항목 처리 하위줄 1개. uncommitted. 진입 HEAD `a944d6ca`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`
  SHA256 prefix `b56986e018b43293`(read-only objdump만). 후보 없음. 실행·fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `objdump -d -M intel --start-address=… "[HQ]Syw2plus 2002.exe"`로
  `0x403B20..0x403C10`과 10개 프리미티브의 첫 `ret` 확인. 읽은 문서: PROMPT, AGENTS, INBOX, APPROVALS tail,
  STATUS, DESIGN §1~5, MODEL_ROUTING, W60 카드, lap818 기록, `g1_mirror2x.c`, 참고 `rendering.md` §4.3~4.7·§6,
  `ingame_render_pipeline.md`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `ret 0x14`(5인자) `0x466d50 0x4664d0 0x466280 0x465e80 0x465b30`;
  **`ret 0x18`(6인자) `0x466540 0x466ea0`** — 현 5인자 wrapper 재사용 금지 사실로 카드에 고정; `ret 0x4`
  `0x464ec0 0x465080 0x463d30`(픽셀 writer 아님 추정, P1 확인). `0x403B20`은 `ret 0x1c`, `call 0x465250`과
  vtable `call [edx+0x30]` → 지형 writer UNKNOWN(P1 census 대상). `g1_mirror2x.c` 802줄(800 한도 초과) → 새 코드는
  새 파일. 전략 판정: **W70 계획 발행 PASS**(구현·G1 완료 아님). HD 출처 기본 = (a) Scale2x 팔레트 인덱스 공간,
  (b) `SYW2_G1_HD_PACK` 사용자 슬롯, xBRZ/hqx/ESRGAN은 32bpp/양자화 필요로 기본 제외.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 변경 없음. 참고문서의 `[추정]` 항목(지형 dirty flag,
  BltFast UI)은 사실로 승격하지 않고 P1 census로 판정한다. G1 합격 기준안(§3)은 사용자 3단 제출 형식이며 아직
  사용자 승인 없음. 마일스톤 경계·증거 충돌 아님 → ESCALATE_SOL 없음.
- 다음 한 가지: work **P1 writer census**(measurement-only, baseline/W70 공통 last-writer 맵·writer별 unique 픽셀·
  dest_read·인자 표본·원본 elapsed/tick 비교, save006 fresh pair 3회, attribution ≥95%).

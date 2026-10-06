# 2026-09-30 | lap 787 | 목표 G2 ESL2608 두 EXE 점검 계획

- 실제 provider/model/effort / 지정 역할: leader Codex native 세션(실제 model ID·effort 비노출), 독립 hash verifier Codex `gpt-5.6-sol/high`, 저장소 mapper Codex `gpt-5.6-luna/high`; middle tier 진단·계획·확인, 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap786 OFF hash 충돌은 마지막 `b` 전사 누락뿐이며, 최신 지시는 G1을 일시중단하고 ESL2608 일반/시작자리고정 G2 후보의 전체 paired 점검·수리·새 이름 전달을 앞당긴다.
- 예상 PASS / FAIL 조건: OFF `trace_raw.jsonl`/`trace.jsonl`이 같은 완전한 SHA면 provenance gate PASS. 두 baseline에서 현재 patch chain이 두 현 후보를 정확히 재생성하면 계획 FEASIBLE; 불일치면 HOLD.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `docs/work/active/G2_ESL2608_PAIRED_CHECKLIST_REPAIR_LAP787.md`, 이 기록, `docs/STATUS.md`; source fingerprint는 산출물 작성 후 final Fast가 검증하며 결과는 STATUS에만 기록; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: baseline 일반 `cade60b2…b176a3`, 고정 `f5f816ee…ee1973`; 현 후보 일반 `83c7df80…1fad60`, 고정 `1bdcadf9…49262f`; 이 회차는 read-only 파일/메모리 builder 재생성만, 게임·플레이어·지도·군대 fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`으로 lap785 OFF/ON 및 G2 네 EXE를 재확인. 두 baseline에 `pool4092_owner500.build_candidate`→`supply1500_500_5000.build_candidate`를 메모리 적용해 intermediate/final SHA와 현 파일 byte equality를 출력. 캡처·runtime 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): OFF raw와 trace 모두 `8798fafb…14b133b`, ON 둘 모두 `d3bc54cf…be74cc`; stale 63자리 hash 없음. 일반 chain `cade60b2→2642b7f7→83c7df80`, 고정 `f5f816ee→2f617567→1bdcadf9`, 두 final 모두 현 후보와 byte-equal. **계획 FEASIBLE/PASS**, 실제 G2 checklist는 SKIP(역할 경계).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: G1은 paused/HOLD, 승인 없음. 기존 Shift·생산·save/load 근거는 참고뿐이며 새 checklist PASS가 아니다. 실제 DxWnd bundle/profile은 repo와 `../260921_temp`에서 발견되지 않아 C단계 필수 입력 위험이고, 멀티는 기존 Wine/IPX 환경 blocker가 있다. G2 8인×10000 완료와 무관하다.
- 다음 한 가지: work tier가 계획 Phase A를 즉시 수행해 두 lane의 활성유닛>20/선택1·19·20/부대호출 후 Shift 단일추가·거부를 fresh paired raw로 재현·분류하고, 추적 가능한 결함은 같은 회차에서 수리·재실행한다.

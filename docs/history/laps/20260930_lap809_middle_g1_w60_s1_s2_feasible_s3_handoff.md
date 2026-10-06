# 2026-09-30 | lap 809 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex native 세션(정확한 backend model ID·effort 비노출) /
  지정 middle `gpt-5.6-sol`/high, 진단·계획·확인. 게임·bridge·EXE hands-on 수정 없음.
- 가설 / 사용자 관찰: lap808의 native2x mirror-OFF와 mirror-ON은 동일 type49/nation1 fixture와
  동일 minimap gate를 쓴 paired control이며, raw를 독립 재계산하면 W60 S1/S2를 `FEASIBLE`로
  승격하고 다음 work가 S3 디테일 경로 증명에 착수할 수 있다.
- 예상 PASS / FAIL 조건: 보호 원본·source·raw SHA가 기록과 일치하고, 양쪽 fixture/명령표/gate가
  같으며, OFF mirror0, ON converted PS3/5/7/9·mirror>0·primitive>0·oracle>=0.999·tick>=300,
  summary1/drop0·cleanup PASS면 수용한다. production `UNKNOWN`은 동일 raw no-effect일 때만
  `N/A(original parity, raw-only)`로 제한하며 G1 제품 PASS로 승격하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이번 middle은 이 기록,
  `docs/STATUS.md`, `loop/ESCALATE_SOL`만 수정. 검수 source SHA는 `runtime_env.py b0cdaa08…e542`,
  `g1_mirror2x_probe.py 8fe1a906…6ea8`, 관련 테스트 `3c6be60b…f1e2`/`30a84e8b…29f4`,
  `direct_draw_trace.c 4e4d6ee7…f9e2`, `g1_mirror2x.c 059dd5b7…7842`, `.h d2c8cb6b…84e9`.
  모두 uncommitted, 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본과 두 manifest의
  EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 같은 bridge
  `a3e9165e…d2ff`, Wine32/private prefix/Xvfb 1600×1200, default two-player random,
  synthetic=false, diagnostic memory write=true. 양쪽 owner0 nation1/types `[7,49]`, selected type49.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; `sha256sum`/`jq -s` raw 독립 재계산;
  `tools/g1_mirror2x_probe.py`; 원본 `objdump` old bytes 확인; targeted pytest
  **196 passed**, Ruff/compileall/mypy, `SAFETY_PASS`. OFF raw `60549c03…a5116`, ON raw
  `b9929bac…c904`; 1600×1200 캡처 SHA OFF `ae218d60…f467`, ON `945e4e50…70417`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): OFF 752 events·summary1/drop0·mirror0; ON
  1674 events·summary1/drop0·converted246(states 3/5/7/9)·mirror548·primitive21291·covered125889·
  oracle min1.0. 양쪽 raw command-table before/after 동일·stable, A6[0]=1, gate
  `00000000→01000000→00000000`, tick 300/301, minimap camera `[49,49]`, cleanup/prefix residue0,
  private game copy 제거. **판정: `PASS(S1/S2) / FEASIBLE`, G1 overall `HOLD(S3/user approval)`.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: runtime detour old bytes는 원본에서
  `0x466d50=83ec148b54241c`, `0x4664d0=55568b7424108be9`로 source pin과 일치하고 설치는 transactional
  exact-restore 회귀로 고정됐다. mirror-OFF는 같은 native2x/bridge에서 mirror 개입만 뺀 control로
  수용한다. fresh random 시작 좌표는 달라 replay-identical state hash는 아니므로 미세 부작용 부재의
  최종 증명으로 쓰지 않는다. generic verdict는 production UNKNOWN 때문에 BLOCKED이며, 본 판정은
  전략 S1/S2의 좁은 2단 수용이다. S3·최종 원본/후보 시각/입력·사용자 3단 승인은 미완료.
- 다음 한 가지: work tier가 전략 카드 S3만 수행한다. 한 sprite id/frame을 명시한 합성 2배 패턴으로
  교체해 최종 1600 캡처에서 마스크 내부가 2×2 복제가 아닌 디테일이고 마스크 밖은 불변임을 raw/캡처로
  증명한다. 기존 S1/S2·production raw-only N/A를 보존하고, 완료 후 새 middle 검수를 받는다.

# 2026-09-30 | lap 813 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex native 세션(표면이 모델 ID·effort를 노출하지 않음) / middle·컨펌 tier; 게임 코드·하네스 구현 수정 없음.
- 가설 / 사용자 관찰: lap812-r5의 same-save pair가 장면 동일성과 W60 표현 경로를 증명하되, 선택·미니맵·생산 입력은 효과 기반 precondition이 없어 G1 입력 parity를 아직 증명하지 못했을 수 있다.
- 예상 PASS / FAIL 조건: raw·PNG·bridge/source SHA와 scene state가 재계산에 일치하고 입력별 원본/후보 효과가 같은 의미 시점에서 직접 대응하면 PASS; 샘플 race, 원본 gate 미개방, 자연 tick과 입력 효과 혼합이면 HOLD.
- 변경 파일 / source fingerprint / 커밋: 이 기록, `docs/STATUS.md`, `docs/feedback/APPROVALS.md`, `loop/ESCALATE_SOL`, lap812 bridge SHA 전사 정정만 uncommitted; 제품/게임/하네스 코드 변경 없음. 검증 fingerprint는 마지막 Fast 결과에 기록한다.
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 직접 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; bridge 실제 SHA `0bacc0191bdab1a2a4ead6a95595f4d190cc718132d0cf157a018160b65d6a62`; baseline/candidate private game 삭제와 prefix residue 0 재확인.
- 실행 명령 / 근거: `sha256sum`으로 source/save/bridge/raw/PNG 재계산; Python `json`으로 scene/action/trace를 독립 집계; Pillow nearest로 loaded PNG를 재비교. pair JSON SHA `26c7e17a29bf9cb48720c37cf3b357e3fa33c6cd4e2514c579f7058b4d089d39`, baseline/candidate raw SHA `b6bc32d6…50a` / `e9a62309…3ae`, loaded PNG SHA `b677a0be…7bb` / `37f29f9f…174`.
- 측정값 / 판정: scene state는 양쪽 exact equal(PS3, players8, units558, canonical SHA `a18701fe3a943be6765c280d9f45c6aef1dbdf5bfa0046f08cd83b114cb1c915`). candidate trace 1382행, converted242(PS35=168/PS3=53/PS9=21), mirror270 success, primitive5336, covered max129835, oracle min1.0, summary1/drop0. loaded nearest는 직접 재계산해 diff118652/1920000, equal `0.9382020833`; 독립 tick의 동적 효과가 섞인 보조 구도 증거로만 수용하고 W60 same-frame oracle 임계치로 쓰지 않는다.
- 입력 판정: baseline selection은 slot982→151이나 candidate는 클릭 직후 982→982, 다음 drag 직전에는 설명 없이 slot151이므로 효과 샘플 race다. drag는 양쪽 1→0으로 새 선택 parity가 아니다. minimap은 양쪽 camera `[158,101]` 불변이며 카드가 요구한 동일 gate=1 대조가 없다. production은 양쪽 tick+24 동안 AI 생산 변화가 같지만 클릭 대상 큐 효과와 분리되지 않은 `OBSERVED`다. 세 항목 모두 PASS 승격 거부.
- 종합: **lap812 same-save identity + W60 presentation = PASS; G1 = `HOLD(input evidence)`**. 구현 근거 충돌은 없고 bridge SHA는 raw로 확인 가능한 단순 전사 오류라 즉시 정정했다. primitive 전체 coverage·성능·사용자 3단 승인도 미완료다.
- 다음 한 가지: work tier가 같은 save006 pair에서 효과 기반 wait와 고정 semantic target으로 selection→drag, 동일 gate=1 minimap, production queue를 한 fresh pair로 재측정한다. 상세 계약은 `loop/ESCALATE_SOL`.

# 2026-09-30 | lap 822 | work | G1 W70 P1 raw/provenance conflict

- 날짜/lap/목표: 2026-09-30, lap822, G1 W70 P1 독립 검수 진입 전 사전 대조.
- 역할/가설: 이번 세션은 hands-on work 역할이며 STATUS의 다음 단계는 middle/Sol 독립 검수다. lap821 기록의 r4/r5/r6 `source_width=0` 서술이 실제 raw와 일치하는지 read-only로 확인했다.
- 변경파일/제품 변경: 제품·패치·게임 binary 0. `loop/ESCALATE_SOL`, 이 lap 기록, `docs/STATUS.md`만 문서 변경 예정. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본/fixture: 보호 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; private Wine32/Xvfb 1600×1200, baseline logical 800×600, non-synthetic save006 PS3 scene. 이번 lap은 새 게임 실행 없음.
- raw/map: r4 raw `2787898400b6cf409c9461c2668b3e8762f4c499f19fea32d1b9ad6d9f6e4049`, map `36c0f31e8aa81b3edf75f359e5574c850e538d0368086bdcb2f09edecf7ee3d0`; r5 raw `eea8f27e92407aa972685448b6ffbc990a7cc284ea2fa909b0e886c3e56d91da`, map `1bde5bb5b473e2724ac7570cf4417c416aa739d34523123e1cc9446d23cd6ddf`; r6 raw `23d298d11beb82b03165119cd621e26bd399abd48f56ed92d7f47e73ba6aafa4`, map `faceb0087e78c115fb7afb96382dfb8e92fd65e06196bab0b9534e5f89c27683`.
- 실행/검사: `jq -s` event/source-width/assigned/map-bytes 재집계, `sha256sum`, `wc -l -c`, `git diff --check`, `python3 checks/context_limits.py`. 결과 `CONTEXT_PASS`, diff check PASS.
- 측정값: r4/r5는 각 `present_boundary=64`, source_width set `{0}`, assigned `480000/480000`. r6도 present 64·assigned `480000/480000`이나 source_width set `{0,832}`이며 0은 52회, 832는 12회; 832 항목은 source_height600/destination_width800이다.
- 판정: **BLOCKED / ESCALATE(evidence-source conflict)**. lap821 및 STATUS의 “r4/r5/r6 source_width=0” 기록과 r6 raw의 12개 `source_width=832`가 실질적으로 어긋난다. 단순 전사인지 source descriptor/stride의 정상 실행 차이인지 현 work 역할이 임의 판정하지 않는다. attribution 100%만으로 conflict를 승격하지 않는다.
- 다음 한 가지: Sol/middle이 r4/r5/r6 raw의 source-width·source-height·destination/source identity·selected buffer·map header·DirectDraw event를 독립 대조하고, 정상 메타데이터인지 계측/기록 결함인지 판정한다. 판정 전 candidate pair·하네스 완화·G1 완료 승격 금지.

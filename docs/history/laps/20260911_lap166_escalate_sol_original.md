# ESCALATE_SOL — lap166 P4 결과 중간-tier 독립 컨펌 요청

- lap: 166 / 목표: G1 / 역할: hands-on work tier
- 상태: P4 관측 probe는 성공했지만, 다음 close-path probe 또는 수리 범위가 중간-tier 승인 경계다. 제품 G1 완료/마일스톤 승인은 아니다.
- 핵심 판정: **J**. 새 private run `local/runtime/20260911_212619_1018825_0`에서 close 전에 30초 PS3 dwell을 수행했다. 1초 표본 30건 전체가 `ps=3`이고 tick은 `46,79,113,146,179,213,246,279,313,346,379,413,446,479,513,546,579,613,646,679,713,746,779,813,846,879,913,946,979,1013`으로 단조 증가했다. dwell +1/+10/+20/+30 캡처 SHA는 각각 `c456e97d…022e29`, `3ab525ff…92dfcd`, `f8737c50…c1186be`, `a7dd1757…42d306`으로 모두 다르고 PS3 scene `09e69652…f394a16`과도 다르다.
- close 후 기존 경로는 `post_result=true`로 close 전달됐지만 process exit false/summary 0으로 90초 timeout; finalization tick은 49개 표본에서 `1026` 고정. 따라서 정지는 close와 상관관계가 있으며, 원인은 아직 수정하지 않았다.
- 부가 증거: wrapper log 165줄 중 `DDERR_SURFACELOST` 100줄, 첫 timestamp `21:27:25.660`; raw trace 384 events, `blt_fast=256`, 마지막 `seq=384/call_seq=881`. 알려진 trace 상한·미flush·Lock 미후킹 맹점 때문에 PS3 호출 0건으로 해석하지 않는다.
- 검증: `make check` 192 passed, ruff/compileall/mypy/context/safety PASS; cleanup/config restore PASS. 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 유지. 상세 기록: `docs/history/laps/20260911_lap166_luna_g1_ps3_dwell_close_causality.md`; evidence: `local/runtime/20260911_212619_1018825_0/output/g1_presentation_trace/`.
- 승격 작업자가 이어서 검증할 것: (1) 위 산출물/SHA와 J 판정을 독립 재검수, (2) close가 인게임 tick 정지를 유발한다는 해석의 범위 확정, (3) 다음 단일 probe 또는 수정 범위를 승인. work tier는 이 세션에서 원인 수정·재실행·trace/로그 상한 변경을 하지 않는다.

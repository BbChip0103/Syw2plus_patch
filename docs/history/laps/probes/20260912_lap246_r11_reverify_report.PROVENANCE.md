# lap246 R11 재검수 — 하네스 결함 provenance

- probe: `20260912_lap246_r11_reverify_probe.py`
- attempt1 (보고서 미생성): 초기 판본은 C3 미러 디렉터리와 직접 관측 케이스가 같은 이름
  `work/"mutated"`를 써서 `direct_r11_behaviour(mutate=True)`의 `case.mkdir()`이
  `FileExistsError: /tmp/lap246_r11_dc64w0yk/mutated`로 죽었다. 측정 전 단계에서 죽었으므로
  보고서 파일은 만들어지지 않았고 부분 결과도 남기지 않았다.
  초기 판본 SHA256 `df1c839c5387bf68bd380cb343950e6815a52630a78ec64dc009755b20a63849`.
- 수리: 직접 관측 케이스 디렉터리를 `direct_control`/`direct_mutated`로 분리했다. 이것은
  하네스(리뷰 probe) 결함이며 SUT(`tests/test_review_probe_output.py`,
  `20260912_lap228_r6b_r3_review_probe.py`)나 임계값은 바꾸지 않았다.
  수리 판본 SHA256 `06a1991a27babcee94a06f4367a54868a6dc1dd632b8e2e6d87c8ffa65a0be67`.
- attempt2 = 채택된 보고서 `20260912_lap246_r11_reverify_report.json`
  SHA256 `5b4cf4bf5fd0d35a596247d73f8a7c158e73f96fe439f074cb8487be60faef63`.

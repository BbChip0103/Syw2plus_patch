# 보존본 — lap164 `loop/ESCALATE_SOL` 원문

lap165 middle tier가 이 승격을 해소하면서 원문을 여기에 보존했다.
판정은 `docs/history/laps/20260911_lap165_middle_g1_trace_blindspot_verdict.md`.
해소 직전 `loop/ESCALATE_SOL`의 실측 SHA256은 `697997f5187a9c4e0a26966ec75dde263eb4de66cef0971acc511b9c0e185693`다.
아래 `---` 이후가 그 파일의 본문이다(이 머리말 때문에 이 사본 파일의 해시는 위 값과 다르다).

---

# lap164 — G1 P3 fresh runtime 승격

## 승격 사유

승인된 P3를 새 private copy/prefix/display에서 `.venv/bin/python`으로 정확히 1회 실행했다.
helper/bridge build, prepare, manifest check, Fast 게이트는 통과했지만 `g1-presentation-trace`
는 90초 finalization timeout으로 `exit=2`, `process_exited=false`, `summary_count=0`,
`event_count=384`로 BLOCKED됐다. 필수 실행 실패이며 재시도하지 않는다.

## work tier가 보존한 결과

- run: `local/runtime/20260911_211043_913631_0`
- source EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- fresh bridge SHA: `5bb790acdf841f806e55ddbfc89050bc13c422ae7dfe30a5fb3c0d05e86f3ae8`
- fresh helper SHA: `7f74f168ce1787bc767803b085109cef73c8f3c35d810299dfa755a3bfc88d21`
- dxwrapper candidate: `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`
- restored game-copy `dxwrapper.ini` SHA: `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`
- environment: display `:91`, Wine win32 private prefix, screen `1600x1200x24`, logical `800x600`,
  scale `2x2`, default two-player random-game fixture; synthetic/memory-write/resource-grant false,
  diagnostic bridge true.
- input/scene: logical and X11 `(184,560)` unchanged; `PS9 -> PS7 -> PS3` and 1600x1200 captures
  were produced. PS3 capture is a visible game scene/HUD, not a black frame:
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260911_211120_20260911_211043_913631_0-presentation_915444_ps3_scene_1789128680509213475.png`
  SHA `af94e7982a133c78f6869d2ca171e5e3bddedbe9818c5706c902cf7a560b294a`.
- finalization reader: 78 samples, first `9.341s/ps=3/tick=16`, last
  `89.583s/ps=3/tick=16`; all ticks are exactly `16`, all PS values exactly `3`.
- close transport: PASS, pid `276`, hwnd `0x00020056`, matched thread `280`, `post_result=true`.
- liveness: pid `915444`, 36 threads; sample state `S` at `9.340s` and `R` at `14.448s`.
  Main tid `915444` gained `+310` jiffies while process total gained `+320` (about 96.9%).
- raw DirectDraw trace: 384 events; `program_state=3` count `0`, `program_state=2` count `30`.
  The trace ends at `ts_ms=503019226`; this conflicts with the live reader's stable `ps=3` and
  the visible PS3 capture and must not be silently interpreted.
- cleanup: PASS, owned processes after `[]`, global kill false, config restored true, sidecars removed.
  The fresh run's verdict/evidence/provenance/trace files remain in the run directory; no product or
  original binary was changed.

## middle tier가 이어서 검증할 것

1. 위 run의 evidence/provenance/raw trace와 캡처를 독립 재열람해 `tick=16` 정지와 visible PS3
   scene을 함께 설명하고, reader `ps=3` 대 raw trace `program_state=2/3=0` 불일치의 의미를 판정한다.
2. close helper 전달과 cleanup PASS를 재사용 가능한 사실로 유지하되, worker retry나 timeout/close/
   config 변경은 하지 않는다.
3. 위 충돌을 해소한 뒤에만 다음 probe를 승인한다. 후보는 handoff가 정한 해당 스레드 EIP/wchan
   관측 또는 PS3 dwell 관측이며, 이번 lap에서 어느 것도 실행하지 않는다.

## 보존 산출물 해시

- manifest `33686f12b7dc96b96f044c22dee12720cd751f94dc3675e1b0dc436c58b8a4d6`
- verdict `661cc7cec3641f6ecf823bf364e84c6d676840896caaf0cae541e95765ce9d4e`
- evidence `766111b1fd117f44e8d7d9a589e79dfaa8560767f4bd63f79e3d5087baa1e277`
- provenance `85d0b1f60209d18ac6aef4788726ce5bf9e3ac5bc7b82bc65f41812e9bba75f5`
- raw trace `07e42ffa118e30676089d48e9746d017ec8ba275d187fcb1c7717945d7ff5cbf`
- install trace `bcea762e809675929f4ec628bf260ce2b1955148695653ab0ec5c44ac2056e3d`

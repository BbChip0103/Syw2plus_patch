lap=801
role=work
status=BLOCKED
target=G2 ESL2608 DxWnd/profile windowed-scroll paired check

The required work was attempted in isolated full-game copies, private win32 Wine prefixes, and private
1600x1200 Xvfb displays. The probe was repaired and rerun more than three times: (1) stopped reading the
DxWnd launcher PID and resolved the exact target PID; (2) moved the writable profile from Z: to C:\dxwnd
after reproducing DxWnd's “No write capability on dxwnd.ini” dialog; (3) copied the target EXE to the same
C: volume as DxWnd to remove Z: path matching. The same DxWnd `/r:1` control launched notepad, but the
Syw2plus target produced no child process in every repaired run. No product EXE or source was modified.

Evidence to verify next:
- raw/probe outputs: `temp/Syw2plus_patch/g2_esl2608_lap801/dxwnd_normal_baseline_r{2,3,4,5}/`
- work implementation: `tools/g2_esl2608_dxwnd_scroll_probe.py`
- exact source/candidate hashes and failure classification: `docs/history/laps/20260930_lap801_work_g2_dxwnd_target_blocked.md`
- control result: DxWnd `/r:1` launched `notepad.exe` in the same private prefix.

Do not mark DxWnd/scroll PASS, do not retry the same Wine profile guess, and do not advance to load/multiplayer
or create new EXE deliverables until a middle/strategy worker supplies an environment or target-launch decision.

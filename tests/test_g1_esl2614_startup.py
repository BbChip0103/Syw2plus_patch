from __future__ import annotations

from pathlib import Path


def test_user_shaped_wine_launch_options_are_independent() -> None:
    from tools import g1_saved_scene_probe as probe

    assert probe._wine_dll_overrides(esl2614=True, native_ddraw=False) == "ddraw=b;winmm=n,b"
    assert probe._wine_dll_overrides(esl2614=True, native_ddraw=True) == "ddraw=n,b;winmm=n,b"
    assert probe._wine_dll_overrides(esl2614=False, native_ddraw=True) == "ddraw=b"
    assert probe._wine_debug_flags(user_shaped_startup=False) == "-all"
    assert probe._wine_debug_flags(user_shaped_startup=True) == "+seh,+loaddll"
    assert probe._wine_desktop_command() == ["wine", "explorer", "/desktop=Default,1600x1200"]
    assert probe._game_launch_command(Path("/game")) == [
        "wine", str(Path("/game") / probe.runtime_env.ORIGINAL_EXE),
    ]


def test_esl2614_startup_modes_are_opt_in_and_forwarded_independently() -> None:
    import inspect
    from tools import g1_esl2614_display_probe as runner
    from tools import g1_saved_scene_probe as probe

    parameters = inspect.signature(probe._run_lane).parameters
    assert parameters["native_ddraw"].default is False
    assert parameters["no_virtual_desktop"].default is False
    wrapper = inspect.getsource(runner.run_lane)
    assert "native_ddraw=native_ddraw" in wrapper
    assert "no_virtual_desktop=no_virtual_desktop" in wrapper

    source = Path(runner.__file__).read_text(encoding="utf-8")
    assert 'parser.add_argument("--candidate-native-ddraw"' in source
    assert 'parser.add_argument("--candidate-no-virtual-desktop"' in source
    assert 'parser.add_argument("--startup-only"' in source
    assert "args.candidate_native_ddraw" in source
    assert "args.candidate_no_virtual_desktop" in source
    assert "--startup-only requires --candidate-native-ddraw" in source


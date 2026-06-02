# -*- coding: utf-8 -*-

from guake.terminal import build_shell_argv


class FakeGeneralSettings:
    def __init__(self, default_shell, login_shell=False):
        self.default_shell = default_shell
        self.login_shell = login_shell

    def get_string(self, key):
        assert key == "default-shell"
        return self.default_shell

    def get_boolean(self, key):
        assert key == "use-login-shell"
        return self.login_shell


def test_build_shell_argv_uses_configured_shell(monkeypatch, tmp_path):
    configured_shell = tmp_path / "tmux"
    configured_shell.write_text("")
    monkeypatch.setenv("SHELL", "/bin/zsh")

    argv = build_shell_argv(FakeGeneralSettings(str(configured_shell)))

    assert argv == [str(configured_shell)]


def test_build_shell_argv_can_force_user_shell(monkeypatch, tmp_path):
    configured_shell = tmp_path / "tmux"
    configured_shell.write_text("")
    monkeypatch.setenv("SHELL", "/bin/zsh")

    argv = build_shell_argv(
        FakeGeneralSettings(str(configured_shell), login_shell=True),
        use_user_shell=True,
    )

    assert argv == ["/bin/zsh", "--login"]

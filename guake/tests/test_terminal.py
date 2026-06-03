# -*- coding: utf-8 -*-

from types import SimpleNamespace

import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

import guake.terminal

from guake.terminal import GuakeTerminal
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


class FakeTerminal:
    def __init__(self):
        self.fed_child = []

    def feed_child(self, text):
        self.fed_child.append(text)


class FakeKeymap:
    def __init__(self, keyval):
        self.keyval = keyval

    def translate_keyboard_state(self, hardware_keycode, state, group):
        return True, self.keyval, group, 0, Gdk.ModifierType(0)


def make_key_event(keyval, state, hardware_keycode=None, group=0):
    return SimpleNamespace(
        keyval=keyval,
        state=state,
        hardware_keycode=hardware_keycode,
        group=group,
    )


def patch_hardware_keyval(monkeypatch, keyval):
    monkeypatch.setattr(guake.terminal.Gdk.Display, "get_default", lambda: object())
    monkeypatch.setattr(
        guake.terminal.Gdk.Keymap,
        "get_for_display",
        lambda display: FakeKeymap(keyval),
    )


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


def test_ctrl_backspace_sends_backward_word_delete():
    terminal = FakeTerminal()
    event = make_key_event(Gdk.KEY_BackSpace, Gdk.ModifierType.CONTROL_MASK)

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert handled
    assert terminal.fed_child == ["\x17"]


def test_ctrl_delete_sends_forward_word_delete():
    terminal = FakeTerminal()
    event = make_key_event(Gdk.KEY_Delete, Gdk.ModifierType.CONTROL_MASK)

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert handled
    assert terminal.fed_child == ["\x1bd"]


def test_ctrl_word_delete_ignores_lock_modifiers():
    terminal = FakeTerminal()
    event = make_key_event(
        Gdk.KEY_BackSpace,
        Gdk.ModifierType.CONTROL_MASK
        | Gdk.ModifierType.LOCK_MASK
        | Gdk.ModifierType.MOD2_MASK,
    )

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert handled
    assert terminal.fed_child == ["\x17"]


def test_ctrl_word_delete_ignores_layout_modifiers():
    terminal = FakeTerminal()
    event = make_key_event(
        Gdk.KEY_BackSpace,
        Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD5_MASK,
    )

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert handled
    assert terminal.fed_child == ["\x17"]


def test_ctrl_word_delete_handles_backspace_control_keyvals(monkeypatch):
    patch_hardware_keyval(monkeypatch, Gdk.KEY_BackSpace)

    for keyval in (8, 127):
        terminal = FakeTerminal()
        event = make_key_event(keyval, Gdk.ModifierType.CONTROL_MASK, hardware_keycode=22)

        handled = GuakeTerminal.key_press(terminal, terminal, event)

        assert handled
        assert terminal.fed_child == ["\x17"]


def test_ctrl_word_delete_handles_backspace_control_keyvals_without_control_state(monkeypatch):
    patch_hardware_keyval(monkeypatch, Gdk.KEY_BackSpace)

    terminal = FakeTerminal()
    event = make_key_event(8, Gdk.ModifierType(0), hardware_keycode=22)

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert handled
    assert terminal.fed_child == ["\x17"]


def test_ctrl_word_delete_does_not_treat_ctrl_h_as_backspace(monkeypatch):
    patch_hardware_keyval(monkeypatch, Gdk.KEY_h)

    terminal = FakeTerminal()
    event = make_key_event(8, Gdk.ModifierType.CONTROL_MASK, hardware_keycode=43)

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert not handled
    assert terminal.fed_child == []


def test_ctrl_word_delete_handles_keypad_delete():
    terminal = FakeTerminal()
    event = make_key_event(Gdk.KEY_KP_Delete, Gdk.ModifierType.CONTROL_MASK)

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert handled
    assert terminal.fed_child == ["\x1bd"]


def test_ctrl_word_delete_passes_through_plain_delete_keys():
    terminal = FakeTerminal()
    event = make_key_event(Gdk.KEY_BackSpace, Gdk.ModifierType(0))

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert not handled
    assert terminal.fed_child == []


def test_ctrl_word_delete_passes_through_shift_modified_delete_keys():
    terminal = FakeTerminal()
    event = make_key_event(
        Gdk.KEY_Delete, Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
    )

    handled = GuakeTerminal.key_press(terminal, terminal, event)

    assert not handled
    assert terminal.fed_child == []

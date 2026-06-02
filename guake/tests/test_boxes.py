# -*- coding: utf-8 -*-

import gi
from types import SimpleNamespace
from unittest.mock import MagicMock

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

import guake.boxes as boxes

from guake.boxes import DualTerminalBox
from guake.boxes import TerminalBox


def test_terminal_mouse_selection_modifier_adds_shift_without_shift():
    event = Gdk.Event.new(Gdk.EventType.BUTTON_PRESS)
    event.state = Gdk.ModifierType(0)

    TerminalBox._reverse_terminal_mouse_selection_modifier(event)

    assert TerminalBox._get_event_state(event) & Gdk.ModifierType.SHIFT_MASK


def test_terminal_mouse_selection_modifier_removes_shift_with_shift():
    event = Gdk.Event.new(Gdk.EventType.BUTTON_PRESS)
    event.state = Gdk.ModifierType.SHIFT_MASK

    TerminalBox._reverse_terminal_mouse_selection_modifier(event)

    assert not TerminalBox._get_event_state(event) & Gdk.ModifierType.SHIFT_MASK


def test_terminal_mouse_selection_modifier_preserves_button_state():
    event = Gdk.Event.new(Gdk.EventType.MOTION_NOTIFY)
    event.state = Gdk.ModifierType.BUTTON1_MASK

    TerminalBox._reverse_terminal_mouse_selection_modifier(event)

    assert TerminalBox._get_event_state(event) & Gdk.ModifierType.BUTTON1_MASK


def test_split_inherits_tab_user_shell(monkeypatch):
    calls = []

    class FakeTerminalBox:
        def set_terminal(self, terminal):
            calls.append(("set-terminal", terminal))

        def show(self):
            calls.append(("show-terminal-box",))

    class FakeDualTerminalBox:
        ORIENT_H = DualTerminalBox.ORIENT_H
        ORIENT_V = DualTerminalBox.ORIENT_V

        def __init__(self, orientation):
            calls.append(("dual-init", orientation))

        def set_position(self, position):
            calls.append(("set-position", position))

        def set_child_first(self, child):
            calls.append(("set-child-first", child))

        def set_child_second(self, child):
            calls.append(("set-child-second", child))

        def show(self):
            calls.append(("show-dual-box",))

    monkeypatch.setattr(boxes, "TerminalBox", FakeTerminalBox)
    monkeypatch.setattr(boxes, "DualTerminalBox", FakeDualTerminalBox)

    terminal = SimpleNamespace(set_font=MagicMock(), font="font", font_scale=0)
    notebook = SimpleNamespace(
        terminal_spawn=MagicMock(return_value=terminal),
        terminal_attached=MagicMock(),
    )
    parent = SimpleNamespace(replace_child=MagicMock())
    root_box = SimpleNamespace(use_user_shell=True)
    terminal_box = SimpleNamespace(
        terminal=terminal,
        get_notebook=lambda: notebook,
        get_parent=lambda: parent,
        get_root_box=lambda: root_box,
        get_allocation=lambda: SimpleNamespace(width=100, height=100),
    )

    TerminalBox.split_no_save(terminal_box, DualTerminalBox.ORIENT_H)

    notebook.terminal_spawn.assert_called_once_with(use_user_shell=True)

# -*- coding: utf-8 -*-

import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

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

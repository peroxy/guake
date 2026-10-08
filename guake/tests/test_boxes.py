# -*- coding: utf-8 -*-

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import Gtk

import guake.boxes as boxes

from guake.boxes import DualTerminalBox
from guake.boxes import TerminalBox
from guake.boxes import TerminalHolder
from guake.boxes import swap_terminal_boxes


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


class FakePane(Gtk.DrawingArea, TerminalHolder):
    def __init__(self):
        super().__init__()
        self.set_size_request(20, 20)

    def get_guake(self):
        return None


class FakeRootHolder(Gtk.Box, TerminalHolder):
    def get_guake(self):
        return None


def make_quad_split():
    panes = [FakePane() for _ in range(4)]
    left = DualTerminalBox(DualTerminalBox.ORIENT_V)
    left.set_child_first(panes[0])
    left.set_child_second(panes[1])
    right = DualTerminalBox(DualTerminalBox.ORIENT_V)
    right.set_child_first(panes[2])
    right.set_child_second(panes[3])
    root = DualTerminalBox(DualTerminalBox.ORIENT_H)
    root.set_child_first(left)
    root.set_child_second(right)
    holder = FakeRootHolder()
    holder.add(root)
    window = Gtk.OffscreenWindow()
    window.add(holder)
    window.show_all()
    return root, (left, right), panes


def allocate(widget, width, height):
    rect = Gdk.Rectangle()
    rect.x, rect.y, rect.width, rect.height = 0, 0, width, height
    widget.size_allocate(rect)


def pane_sizes(panes):
    return [
        size for pane in panes for size in (pane.get_allocated_width(), pane.get_allocated_height())
    ]


def assert_scales_with_parent(box):
    for child in (box.get_child1(), box.get_child2()):
        assert box.child_get_property(child, "resize") is True
        assert box.child_get_property(child, "shrink") is False


def test_split_keeps_proportions_when_window_shrinks_and_grows():
    root, (left, right), panes = make_quad_split()
    allocate(root, 1000, 1000)
    for box in (root, left, right):
        box.set_position(500)
    allocate(root, 1000, 1000)
    before = pane_sizes(panes)

    allocate(root, 1000, 400)
    allocate(root, 1000, 1000)

    assert pane_sizes(panes) == pytest.approx(before, abs=2)


def test_split_panes_do_not_shrink_below_minimum_size():
    root, (left, right), panes = make_quad_split()
    allocate(root, 1000, 1000)
    for box in (root, left, right):
        box.set_position(500)
        assert_scales_with_parent(box)

    allocate(root, 100, 100)

    assert min(pane_sizes(panes)) >= 20


def test_swap_keeps_split_packing():
    _root, (left, right), panes = make_quad_split()

    swap_terminal_boxes(panes[0], panes[3])

    assert left.get_child1() is panes[3]
    assert right.get_child2() is panes[0]
    assert_scales_with_parent(left)
    assert_scales_with_parent(right)

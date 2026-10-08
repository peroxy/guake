# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
import os

from types import SimpleNamespace
from unittest.mock import MagicMock

import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

from guake.utils import FileManager
from guake.utils import FullscreenManager
from guake.utils import get_process_name


def test_file_manager(fs):
    fs.create_file("/foo/bar", contents="test")
    fm = FileManager()
    assert fm.read("/foo/bar") == "test"


def test_file_manager_hit(fs):
    f = fs.create_file("/foo/bar", contents="test")

    fm = FileManager(delta=9999)
    assert fm.read("/foo/bar") == "test"
    f.set_contents("changed")
    assert fm.read("/foo/bar") == "test"


def test_file_manager_miss(fs):
    f = fs.create_file("/foo/bar", contents="test")

    fm = FileManager(delta=0.0)
    assert fm.read("/foo/bar") == "test"
    f.set_contents("changed")
    assert fm.read("/foo/bar") == "changed"


def test_file_manager_clear(fs):
    f = fs.create_file("/foo/bar", contents="test")

    fm = FileManager(delta=9999)
    assert fm.read("/foo/bar") == "test"
    f.set_contents("changed")
    assert fm.read("/foo/bar") == "test"
    fm.clear()
    assert fm.read("/foo/bar") == "changed"


def test_process_name():
    assert get_process_name(os.getpid())


def test_fullscreen_state_event_does_not_request_fullscreen_again():
    window = MagicMock()
    notebook_manager = MagicMock()
    settings = SimpleNamespace(general=MagicMock())
    settings.general.get_boolean.return_value = True
    guake = SimpleNamespace(hidden=False, notebook_manager=notebook_manager)
    manager = FullscreenManager(settings, window, guake)

    manager.set_window_state(Gdk.WindowState.FULLSCREEN | Gdk.WindowState.FOCUSED)

    window.fullscreen.assert_not_called()
    assert manager.is_fullscreen()
    notebook_manager.set_notebooks_tabbar_visible.assert_called_once_with(False)

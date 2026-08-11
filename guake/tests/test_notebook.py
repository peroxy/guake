# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

import pytest

from guake.notebook import TerminalNotebook


@pytest.fixture
def nb(mocker):
    targets = [
        "guake.notebook.TerminalNotebook.terminal_spawn",
        "guake.notebook.TerminalNotebook.terminal_attached",
        "guake.notebook.TerminalNotebook.guake",
        "guake.notebook.TerminalBox.set_terminal",
    ]
    for target in targets:
        mocker.patch(target, create=True)
    return TerminalNotebook()


def test_zero_page_notebook(nb):
    assert nb.get_n_pages() == 0


def test_add_one_page_to_notebook(nb):
    nb.new_page()
    assert nb.get_n_pages() == 1


def test_add_two_pages_to_notebook(nb):
    nb.new_page()
    nb.new_page()
    assert nb.get_n_pages() == 2


def test_remove_page_in_notebook(nb):
    nb.new_page()
    nb.new_page()
    assert nb.get_n_pages() == 2
    nb.remove_page(0)
    assert nb.get_n_pages() == 1
    nb.remove_page(0)
    assert nb.get_n_pages() == 0


def test_rename_page(nb):
    t1 = "foo"
    t2 = "bar"
    nb.new_page()
    nb.rename_page(0, t1, True)
    assert nb.get_tab_text_index(0) == t1
    nb.rename_page(0, t2, False)
    assert nb.get_tab_text_index(0) == t1
    nb.rename_page(0, t2, True)
    assert nb.get_tab_text_index(0) == t2


def test_add_new_page_with_focus_with_label(nb):
    t = "test_this_label"
    nb.new_page_with_focus(label=t)
    assert nb.get_n_pages() == 1
    assert nb.get_tab_text_index(0) == t


def test_tabbar_alignment_stops_resizing_at_target_margin(nb, mocker):
    tab = mocker.Mock()
    tab.get_preferred_width.return_value = (100, 100)
    mocker.patch.object(nb, "iter_tabs", return_value=[tab])
    mocker.patch.object(nb, "get_allocated_width", return_value=1000)

    nb.action_box = mocker.Mock()
    nb.action_box.get_allocated_width.return_value = 100

    margin = 0
    resize_calls = []
    nb.tabbar_start_spacer = mocker.Mock()
    nb.tabbar_start_spacer.get_size_request.side_effect = lambda: (margin, -1)

    def set_size_request(width, height):
        nonlocal margin
        margin = width
        resize_calls.append((width, height))

    nb.tabbar_start_spacer.set_size_request.side_effect = set_size_request

    nb.update_tabbar_alignment()
    nb.update_tabbar_alignment()

    assert resize_calls == [(450, -1)]

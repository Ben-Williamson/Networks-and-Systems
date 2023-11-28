import curses
from curses.textpad import Textbox, rectangle


def main(stdscr):

    rows, cols = stdscr.getmaxyx()
    ulx, uly = 1, rows-3
    lrx, lry = cols-2, rows-1
    stdscr.addstr(uly-1, ulx, "Enter IM message: (hit Ctrl-G to send)")

    editwin = curses.newwin(lry-uly-1, lrx-ulx-1, uly+1,ulx+1)

    rectangle(stdscr, uly, ulx, lry, lrx)
    stdscr.refresh()

    box = Textbox(editwin)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    # message = box.gather()

curses.wrapper(main)
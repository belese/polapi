#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  log.py
#
#  Copyright 2017 belese <belese@belese>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
from resources.printer import PRINTER


class log:

    INFO = 10
    WARNING = 20
    ERROR = 30
    FATAL = 40

    def __init__(self):
        self.level = self.ERROR

    def log(self, *args, **kwarg):
        for msg in args:
            print(msg)
        if 'level' not in kwarg:
            level = self.INFO
        else:
            level == kwarg['level']
        if level > self.level:
            for msg in args:
                PRINTER.print_txt(msg)


LOG = log()


def main(args):
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

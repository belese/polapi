#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printer.py
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
import os.path

import cups
import PyPDF2
#from serial import Serial
from printer import Printer

HEADER = '/home/pi/polapi/polapi/media/header.pdf'
MIDDLE = '/home/pi/polapi/polapi/media/avecjoie.pdf'
FOOTER = '/home/pi/polapi/polapi/media/footer.pdf'
TICKETBIG = '/var/spool/cups-pdf/ANONYMOUS/MSxpsPS.pdf'
TICKETOK = '/tmp/ticket.pdf'


class Caisse(Printer):
    def print_img(self, photo_file, size):
        if not os.path.isfile(TICKETBIG):
            print "No ticket in printer, return"
            return
        self.print_header()
        option = {"media": size, "orientation-requested": "3",
                  "FeedDist": "1feed6mm"}
        print ("Print to size = %s" % size)
        #option = {"media" : size}
        self.cupconn.printFile(self.printer, photo_file, "None", option)
        self.print_middle()
        self.print_ticket()
        print ("End printing")
        # self.print_footer()

    def print_header(self):
        print 'header'
        option = {"orientation-requested": "3", "FeedDist": "1feed6mm"}
        self.cupconn.printFile(self.printer, HEADER, "None", option)

    def print_middle(self):
        option = {"orientation-requested": "3", "FeedDist": "0feed3mm"}
        self.cupconn.printFile(self.printer, MIDDLE, "None", option)

    def print_ticket(self):
        print 'ticket'
        self.scaleTicket()
        option = {"orientation-requested": "3", "FeedDist": "4feed15mm",
                  "media": "X48MMY128MM", "fit-to-page": "true"}
        self.cupconn.printFile(self.printer, TICKETOK, "None", option)

    def scaleTicket(self):
        pdfFileObj = open(TICKETBIG, 'rb')
        a = open(TICKETOK, 'wb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pdfWriter = PyPDF2.PdfFileWriter()
        pageObj = pdfReader.getPage(0)
        pageObj.trimBox.lowerLeft = (12, 12)
        pageObj.trimBox.upperRight = (192 + 12, 512 + 12)
        pageObj.cropBox.lowerLeft = (12, 12)
        pageObj.cropBox.upperRight = (192 + 12, 512 + 12)
        pdfWriter.addPage(pageObj)
        pdfWriter.write(a)
        a.close()

    def print_footer(self):
        option = {"orientation-requested": "3"}
        self.cupconn.printFile(self.printer, FOOTER, "None", option)


CAISSE = Caisse()


def main(args):
    # CAISSE.print_img("/tmp/photo.png","X48MMY48MM")
    CAISSE.print_ticket()
    # CAISSE.print_middle()
    # print 'start scaling'
    # CAISSE.scaleTicket()
    # print 'stop scaling'

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

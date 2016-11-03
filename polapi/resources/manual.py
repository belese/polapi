frm resoures.printer import PRINTER

def print_manual(manual) :
    for line in print_manual :
        PRINTER.print_txt(line)
    PRINTER.linefeed(3)

#! /usr/bin/env python

import sys
import argparse

from .ilp import wxConvert

__name__       = "converter-indic"
__doc__        = "python-converter-indic: Converts Indian languages to WX (ASCII) and vice-versa"
__author__     = "Irshad Ahmad"
__version__    = "1.5.0"
__license__    = "MIT"
__maintainer__ = "Irshad Ahmad"
__email__      = "irshad.bhat@research.iiit.ac.in"
__status__     = "Beta"
__all__        = ["ilp", "wxILP", "main"]

def main():
    # help messages
    src_enc_help = "select input-file encoding [utf|wx]"
    #trg_enc_help = "select output-file encoding [utf|wx]"
    format_help  = "select output format [text|ssf|conll|bio|tnt]"
    lang_help    = "select language [hin|tel|...] (3 letter ISO-639 code)"

    format_list = ["text", "ssf", "conll", "bio","tnt"]
    languages = ["hin", "tel", "tam", "mal", "kan", "ben", "ori", "pan", "mar"]

    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="converter-indic", description="wx-utf converter for Indain languages")
    parser.add_argument('--v', action="version", version="%(prog)s 1.5")
    parser.add_argument('--l', metavar='language', dest="lang", choices=languages, default="hin", help="%s" %lang_help)
    parser.add_argument('--s', metavar='source', dest="src_enc", choices=["utf","wx"], default="utf", help="%s" %src_enc_help)
    #parser.add_argument('--t', metavar='target', dest="trg_enc", choices=["utf","wx"], default="wx", help="%s" %trg_enc_help)
    parser.add_argument('--f', metavar='format', dest="format_", choices=format_list, default="text", help="%s" %format_help)
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")

    if len(sys.argv) == 1:
	parser.print_usage()
	sys.exit(0)

    args = parser.parse_args()

    # set conversion direction
    if args.src_enc=="utf": #and args.trg_enc=="wx":
        src_trg = "utf2wx"
    else: #args.src_enc=="wx" and args.trg_enc=="utf":
        src_trg = "wx2utf"

    # initialize converter object
    con = wxConvert(src_trg, args.format_, args.lang)
    # convert text
    for line in args.INFILE:
        line = con.convert(line)
        args.OUTFILE.write(line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()

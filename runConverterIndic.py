#! /usr/bin/env python

import sys
import argparse

from converter_indic.ilp import wxConvert

def main():
    # help messages
    src_enc_help = "select input-file encoding [utf|wx]"
    trg_enc_help = "select output-file encoding [utf|wx]"
    format_help  = "select output format [text|ssf|conll|bio|tnt]"
    lang_help    = "select language [hin|tel|...] (3 letter ISO-639 code)"

    format_list = ["text", "ssf", "conll", "bio","tnt"]
    languages = ["hin", "tel", "tam", "mal", "kan", "ben", "ori", "pan", "mar"]

    # parse command line arguments 
    parser = argparse.ArgumentParser(prog="convertor_indic", description="wx-utf convertor for Indain languages")
    parser.add_argument('--v', action="version", version="%(prog)s 1.5")
    parser.add_argument('--l', metavar='language', dest="lang", choices=languages, default="hin", help="%s" %lang_help)
    parser.add_argument('--s', metavar='source', dest="src_enc", choices=["utf","wx"], default="utf", help="%s" %src_enc_help)
    parser.add_argument('--t', metavar='target', dest="trg_enc", choices=["utf","wx"], default="wx", help="%s" %trg_enc_help)
    parser.add_argument('--f', metavar='format', dest="format_", choices=format_list, default="text", help="%s" %format_help)
    parser.add_argument('--i', metavar='input', dest="INFILE", type=argparse.FileType('r'), default=sys.stdin, help="<input-file>")
    parser.add_argument('--o', metavar='output', dest="OUTFILE", type=argparse.FileType('w'), default=sys.stdout, help="<output-file>")
    args = parser.parse_args()

    # set conversion direction
    if args.src_enc=="utf" and args.trg_enc=="wx":
        src_trg = "utf2wx"
    elif args.src_enc=="wx" and args.trg_enc=="utf":
        src_trg = "wx2utf"
    else:
        sys.stderr.write("EncodingError: source encoding is same as target encoding!\n")
        sys.exit(0)

    # initialize convertor object
    con = wxConvert(src_trg, args.format_, args.lang)
    # convert data
    for line in args.INFILE:
        line = con.convert(line)
        args.OUTFILE.write(line)

    # close files 
    args.INFILE.close()
    args.OUTFILE.close()

if __name__ == "__main__":
    main()

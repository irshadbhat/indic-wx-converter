#! /usr/bin/env python

# Copyright Irshad Ahmad Bhat 2016.

from __future__ import unicode_literals

import io
import re
import sys
import codecs
import socket
import argparse
import threading
from argparse import RawTextHelpFormatter

from .wx_format import WXC

PYV = sys.version_info[0]
_MAX_BUFFER_SIZE_ = 102400  # 100KB

if PYV >= 3:
    from io import StringIO
else:
    from StringIO import StringIO


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket, args, con):
        threading.Thread.__init__(self)
        self.ip = ip
        self.con = con
        self.port = port
        self.args = args
        self.csocket = clientsocket

    def run(self):
        data = self.csocket.recv(_MAX_BUFFER_SIZE_)
        fakeInputFile = StringIO(data)
        fakeOutputFile = StringIO("")
        processInput(fakeInputFile, fakeOutputFile, self.args, self.con)
        fakeInputFile.close()
        self.csocket.send(fakeOutputFile.getvalue())
        fakeOutputFile.close()
        self.csocket.close()


def processInput(ifp, ofp, args, con):
    if args.format_ == "ssf":
        if args.nested:
            sentences = re.finditer(
                r"(<Sentence id=.*?>\s*\n.*?)\n(.*?)\)\)\s*\n</Sentence>",
                ifp.read(),
                re.S)
        else:
            sentences = re.finditer(
                r"(<Sentence id=.*?>)(.*?)</Sentence>", ifp.read(), re.S)
        for sid_sentence in sentences:
            sid = sid_sentence.group(1)
            sentence = sid_sentence.group(2).strip()
            ofp.write('%s\n' % sid)
            consen = con.convert(sentence)
            ofp.write('%s' % consen)
            if args.nested:
                ofp.write("\t))\n")
            ofp.write("</Sentence>\n\n")
    else:
        for line in ifp:
            line = con.convert(line)
            ofp.write(line)


def main():
    format_list = 'text ssf conll bio tnt'.split()
    languages = 'hin tel tam mal kan ben ori pan mar nep guj bod kok asm urd'
    languages = languages.split()
    # help messages
    src_enc_help = "{utf, wx} select input-file encoding"
    format_help = "{text, ssf, conll, bio, tnt} select input-file format"
    lang_help = """select language (3 letter ISO-639 code)
                Hindi       : hin
                Telugu      : tel
                Tamil       : tam
                Malayalam   : mal
                Kannada     : kan
                Bengali     : ben
                Oriya       : ori
                Punjabi     : pan
                Marathi     : mar
                Nepali      : nep
                Gujarati    : guj
                Bodo        : bod
                Konkani     : kok
                Assamese    : asm
                Urdu        : urd"""
    ssf_help = "{inter, intra} specify ssf-type if file format (-f) is ssf"

    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog="converter-indic",
        description="wx-utf converter for Indian languages",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        '-v',
        '--version',
        action="version",
        version="%(prog)s 1.0.5")
    parser.add_argument(
        '-l',
        '--language',
        dest="lang",
        choices=languages,
        default="hin",
        metavar='',
        help="%s" % lang_help)
    parser.add_argument(
        '-s',
        '--source-enc',
        dest="src_enc",
        choices=["utf", "wx"],
        default="utf",
        metavar='',
        help="%s" % src_enc_help)
    parser.add_argument(
        '-f',
        '--format',
        dest="format_",
        choices=format_list,
        default="text",
        metavar='',
        help="%s" % format_help)
    parser.add_argument(
        '-t',
        '--ssf-type',
        dest="ssf_type",
        choices=["inter", "intra"],
        default=None,
        metavar='',
        help=ssf_help)
    parser.add_argument(
        '-n',
        '--nested',
        dest='nested',
        action='store_true',
        help="set this flag for nested ssf")
    parser.add_argument(
        '-m',
        '--no-mask',
        dest='mask',
        action='store_false',
        help="set this flag to keep off masking of"
             " roman strings in Indic text")
    parser.add_argument(
        '-i',
        '--input',
        dest="infile",
        type=str,
        metavar='',
        help="<input-file>")
    parser.add_argument(
        '-o',
        '--output',
        dest="outfile",
        type=str,
        metavar='',
        help="<output-file>")
    parser.add_argument(
        '-z',
        '--normalize',
        dest='norm',
        action='store_true',
        help="set this flag for utf normalizations"
             " without WX-Conversion")
    parser.add_argument(
        '-d',
        '--daemonize',
        dest='isDaemon',
        help='Do you want to daemonize me?',
        action='store_true',
        default=False)
    parser.add_argument(
        '-p',
        '--port',
        type=int,
        dest='daemonPort',
        default=5000,
        metavar='',
        help='Specify a port number')

    args = parser.parse_args()
    if args.norm and args.src_enc == 'wx':
        sys.stderr.write(
            "converter-indic: error: normalization (-z) is for `utf` only\n")
        sys.stderr.write(parser.parse_args(['-h']))
    if args.format_ == 'ssf' and not args.ssf_type:
        sys.stderr.write(
            "converter-indic: error: argument --t: not specified\n")
        sys.stderr.write(parser.parse_args(['-h']))

    # set conversion direction
    if args.src_enc == "utf":  # and args.trg_enc=="wx":
        src_trg = "utf2wx"
    else:  # args.src_enc=="wx" and args.trg_enc=="utf":
        src_trg = "wx2utf"

    # open files
    if args.infile:
        ifp = io.open(args.infile, encoding='utf-8')
    else:
        if PYV >= 3:
            ifp = codecs.getreader('utf8')(sys.stdin.buffer)
        else:
            ifp = codecs.getreader('utf8')(sys.stdin)

    if args.outfile:
        ofp = io.open(args.outfile, mode='w', encoding='utf-8')
    else:
        if PYV >= 3:
            ofp = codecs.getwriter('utf8')(sys.stdout.buffer)
        else:
            ofp = codecs.getwriter('utf8')(sys.stdout)

    # initialize converter object
    con = WXC(
        src_trg,
        args.format_,
        args.lang,
        args.ssf_type,
        args.nested,
        args.mask,
        args.norm)

    if args.isDaemon:
        host = "0.0.0.0"  # Listen on all interfaces
        port = args.daemonPort  # Port number

        tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tcpsock.bind((host, port))
        sys.stderr.write('Listening at %d\n' % port)

        while True:
            tcpsock.listen(4)
            # print "nListening for incoming connections..."
            (clientsock, (ip, port)) = tcpsock.accept()

            # pass clientsock to the ClientThread thread object being created
            newthread = ClientThread(ip, port, clientsock, args, con)
            newthread.start()
    else:
        processInput(ifp, ofp, args, con)

    # close files
    ifp.close()
    ofp.close()


if __name__ == '__main__':
    main()

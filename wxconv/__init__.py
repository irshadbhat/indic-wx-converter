#! /usr/bin/env python

import re
import sys
import socket
import argparse
import StringIO
import threading
from argparse import RawTextHelpFormatter

from .ilp import wxConvert

__name__ = "converter-indic"
__doc__ = "Converts Indian scripts to WX (ASCII) and vice-versa"
__author__ = "Irshad Ahmad"
__version__ = "1.0.5"
__license__ = "MIT"
__maintainer__ = "Irshad Ahmad"
__email__ = "irshad.bhat@research.iiit.ac.in"
__status__ = "Beta"
__all__ = ["ilp", "wxILP", "ssf_reader", "main"]

_MAX_BUFFER_SIZE_ = 102400  # 100KB


class ClientThread(threading.Thread):

    def __init__(self, ip, port, clientsocket, args, con):
        threading.Thread.__init__(self)
        self.ip = ip
        self.con = con
        self.port = port
        self.args = args
        self.csocket = clientsocket
        # print "[+] New thread started for "+ip+":"+str(port)

    def run(self):
        # print "Connection from : "+ip+":"+str(port)
        data = self.csocket.recv(_MAX_BUFFER_SIZE_)
        # print "Client(%s:%s) sent : %s"%(self.ip, str(self.port), data)
        fakeInputFile = StringIO.StringIO(data)
        fakeOutputFile = StringIO.StringIO("")
        processInput(fakeInputFile, fakeOutputFile, self.args, self.con)
        fakeInputFile.close()
        self.csocket.send(fakeOutputFile.getvalue())
        fakeOutputFile.close()
        self.csocket.close()
        # print "Client at "+self.ip+" disconnected..."


def processInput(ifp, ofp, args, con):
    if args.format_ == "ssf":
        if args.nested:
            sentences = re.finditer(
                "(<Sentence id=.*?>\s*\n.*?)\n(.*?)\)\)\s*\n</Sentence>",
                ifp.read(),
                re.S)
        else:
            sentences = re.finditer(
                "(<Sentence id=.*?>)(.*?)</Sentence>", ifp.read(), re.S)
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
    src_enc_help = "select input-file encoding [utf|wx]"
    format_help = "select input-file format [text|ssf|conll|bio|tnt]"
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
    ssf_help = "specify ssf-type [inter|intra] if file format (--f) is ssf"

    # parse command line arguments
    parser = argparse.ArgumentParser(
        prog="converter-indic",
        description="wx-utf converter for Indian languages",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument('--v', action="version", version="%(prog)s 1.0.5")
    parser.add_argument(
        '--l',
        metavar='language',
        dest="lang",
        choices=languages,
        default="hin",
        help="%s" %
        lang_help)
    parser.add_argument(
        '--s',
        metavar='source',
        dest="src_enc",
        choices=[
            "utf",
            "wx"],
        default="utf",
        help="%s" %
        src_enc_help)
    parser.add_argument(
        '--f',
        metavar='format',
        dest="format_",
        choices=format_list,
        default="text",
        help="%s" %
        format_help)
    parser.add_argument(
        '--t',
        metavar='ssf-type',
        dest="ssf_type",
        choices=[
            "inter",
            "intra"],
        default=None,
        help=ssf_help)
    parser.add_argument(
        '--n',
        dest='nested',
        action='store_true',
        help="set this flag for nested ssf")
    parser.add_argument(
        '--m',
        dest='mask',
        action='store_false',
        help="set this flag to keep off masking of"
        " roman strings in Indic text")
    parser.add_argument(
        '--i',
        metavar='input',
        dest="infile",
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="<input-file>")
    parser.add_argument(
        '--o',
        metavar='output',
        dest="outfile",
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="<output-file>")
    parser.add_argument(
        '--daemonize',
        dest='isDaemon',
        help='Do you want to daemonize me?',
        action='store_true',
        default=False)
    parser.add_argument(
        '--port',
        type=int,
        dest='daemonPort',
        default=5000,
        help='Specify a port number')

    args = parser.parse_args()
    if args.format_ == 'ssf' and not args.ssf_type:
        sys.stderr.write(parser.format_usage())
        sys.stderr.write(
            "converter-indic: error: argument --t: not specified\n")
        sys.exit(0)

    # set conversion direction
    if args.src_enc == "utf":  # and args.trg_enc=="wx":
        src_trg = "utf2wx"
    else:  # args.src_enc=="wx" and args.trg_enc=="utf":
        src_trg = "wx2utf"

    # initialize converter object
    con = wxConvert(
        src_trg,
        args.format_,
        args.lang,
        args.ssf_type,
        args.nested,
        args.mask)

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
        processInput(args.infile, args.outfile, args, con)

    # close files
    args.infile.close()
    args.outfile.close()

if __name__ == '__main__':
    main()

#!/usr/bin/env python

"""WX convertor: converts Indian languages to ASCII and vice-versa

WX notation is a transliteration scheme for representing Indian languages in ASCII.
For more details on WX go to <https://en.wikipedia.org/wiki/WX_notation>.
    
This module is a UTF (Indian Scripts) to Roman (WX) convertor and vice-versa that:

    - converts text in 10 Indian languages viz. Hindi, Tamil, Telegu, Malayalam, 
      Bengali, Kannada, Oriya, Punjabi, Marathi and Nepali.
    - handles 5 data formats viz. plain-text, ssf, conll, bio and tnt.

"""

__version__    = "1.5"
__license__    = "MIT"
__author__     = "Irshad Ahmad"
__maintainer__ = "Irshad Ahmad"
__credits__    = ["Irshad Ahmad", "Riyaz Ahmad", "Rashid Ahmad"]
__email__      = [
                 "irshad.bhat@research.iiit.ac.in",
                 "riyaz.bhat@research.iiit.ac.in",
                 "bhatirshad127@gmail.com",
                 "rashid101b@gmail.com"
                 ]

import os
import re
import sys

from wxILP import wxilp

class wxConvert():
    """WX convertor (UTF to WX and vice-versa)
    
    Used to convert text in Indian languages to ASCII. It can be used for 9 Indian 
    languages viz. Hindi, Tamil, Telegu, Malayalam, Bengali, Kannada, Oriya, Punjabi,
    Marathi and Nepali in 5 data formats viz. plain-text, ssf, conll, bio and tnt.
    """

    def __init__(self, order="wx2utf", format_="text", lang="hin"):
        self.lang = lang
        self.format_ = format_
        wxp = wxilp(self.lang, order)
        self.transform = wxp.wx2utf if order=="wx2utf" else wxp.utf2wx

    def convert_conll(self, line):
        """Convert CONLL data"""
        trans_LINES = list()
        line = line.split("\n")
        for line_ in line:
            line_ = line_.split()
            if not line_:
                trans_LINES.append("")
                continue
            if len(line_) != 10:
                sys.stderr.write("Warning: length mismatch at line\n")
            FORM, LEMMA, FEATS = line_[1], line_[2], line_[5].split("|")
            vib_id = [idx for idx,feat in enumerate(FEATS) if feat[:4]=="vib-"][0]
            vib = FEATS[vib_id].lstrip("vib-")
            vib = re.split("([+_0-9]+)", vib)
            vib = " ".join(vib).split()
            trans_FEATS = list()
            for word in [FORM, LEMMA]+vib:
                if word in ["+", "_"] or word.isdigit():
                  trans_FEATS.append(word)
                  continue
                trans_word = self.transform(word)
                trans_FEATS.append(trans_word)
            line_[1] = trans_FEATS[0] if trans_FEATS[0].strip() else "_"
            line_[2] = trans_FEATS[1] if trans_FEATS[1].strip() else "_"
            FEATS[vib_id] = "vib-%s" %"".join(trans_FEATS[2:])
            line_[5] = "|".join(FEATS)
            trans_LINES.append("%s" %"\t".join(line_))
        return "\n".join(trans_LINES)

    def convert(self, line):
        if self.format_=="text":
            trans_string = self.transform(line)
            return trans_string
        elif self.format_=="ssf":
            sys.stderr.write("to be implemented soon\n")
            sys.exit(0)
        elif self.format_=="conll":
            return self.convert_conll(line)
        elif self.format_ in ["bio", "tnt"]:
            trans_LINES = list()
            line = line.split("\n")
            for line_ in line:
                line_ = line_.split()
                if not line_:
                    trans_LINES.append("")
                    continue
                FORM = line_[0]
                line_[0] = self.transform(FORM)
                trans_LINES.append("%s" %"\t".join(line_))
            return "\n".join(trans_LINES)
        else: 
            sys.stderr("FormatError: invalid format :: %s\n" %self.format_)
            sys.exit(0)

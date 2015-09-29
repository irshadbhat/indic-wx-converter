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
from ssf_reader import SSFReader

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

    def convert_ssf(self, sentence):
	"""Convert SSF data"""
	consen = str()
	obj = SSFReader(sentence)
	obj.getAnnotations()
        for node,order in zip(obj.nodeList, obj.fs_order):
	    name = self.transform(node.name) if node.name not in self.special else node.name
	    parent = self.transform(node.parent) if node.parent not in self.special else node.parent
	    wordForm = self.transform(node.wordForm) if node.wordForm not in self.special else node.wordForm
            dmrel_ = 'dmrel' if node.dmrel else 'drel'
            ssfNode = [node.id, wordForm, node.posTag]
            if isinstance(node.af, tuple):
                nL = node.af
		lemma = self.transform(nL.lemma) if nL.lemma not in self.special else nL.lemma
		vib = self.transform(nL.vib) if nL.vib not in self.special else nL.vib
                features = ",".join((lemma, nL.cat, nL.gen, nL.num, nL.per, nL.case, vib, nL.tam))
            else:
                features = node.af
            fs = [
                    "af='%s'" % (features) if node.af else '',
                    "name='%s'" % (name) if name else None,
                    "head='%s'" % (node.head) if node.head else None,
                    "chunkId='%s'" % (node.chunkId) if (node.chunkId and node.chunkType == 'head') else None,
                    "chunkType='%s:%s'" % (node.chunkType, node.chunkId) if node.chunkType else None,
                    "posn='%s'" % (node.posn) if node.posn else None,
                    "vpos='%s'" % (node.vpos) if node.vpos else None,
                    "%s='%s:%s'" % (dmrel_, node.drel, parent) if node.drel else None,
                    "coref='%s:%s'" % (node.corel, node.coref) if node.coref else None,
                    "stype='%s'" % (node.stype) if node.stype else None,
                    "voicetype='%s'" % (node.voicetype) if node.voicetype else None,
                    "poslcat='%s'" % (node.poslcat) if node.poslcat else None,
                    "mtype='%s'" % (node.mtype) if node.mtype else None,
                    "troot='%s'" % (node.troot) if node.troot else None
                  ]
            fs_ = fs[:]
            for idx in order:
                fs.remove(fs_[idx])
                fs.insert(0, fs_[idx])
            fs = "<fs %s>" % (" ".join(filter(None, fs)))
            if node.id:
                consen += "%s\n" %("\t".join(ssfNode+[fs]))
            else:
                consen += "%s\n" %("\t))\t\t")

	return consen

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
            return self.transform(line)
        elif self.format_=="ssf":
	    self.special = set(['null', 'NULL', 'COMMA', 'SINGLE_QUOTE'])
	    return self.convert_ssf(line)
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

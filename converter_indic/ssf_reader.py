#!/usr/bin/python

import re
from collections import namedtuple, OrderedDict

__version__    = "1.5"
__license__    = "MIT"
__author__     = "Riyaz Ahmad"
__maintainer__ = "Irshad Ahmad"
__credits__    = ["Irshad Ahmad", "Riyaz Ahmad"]
__email__      = [
                 "irshad.bhat@research.iiit.ac.in",
                 "riyaz.bhat@research.iiit.ac.in",
                 ]

class SSFReader():
    def __init__ (self, sentence):
        self.tokens = list()
	self.fs_order = list()
        self.nodeList = list()
        self.sentence = sentence
	fs_node = ('af', 'name', 'head', 'chunkId', 'chunkType', 'posn', 'vpos', 
		  'drel', 'coref', 'stype', 'voicetype', 'poslcat', 'mtype', 'troot')
	nodes = ('id', 'wordForm', 'posTag', 'af', 'name', 'head', 'chunkId', 'chunkType', 'posn', 'vpos', 
		'drel', 'coref', 'stype', 'voicetype', 'poslcat', 'mtype', 'troot', 'corel', 'parent', 'dmrel')
        self.node = namedtuple('node', nodes)
	self.maping = dict(zip(fs_node, range(len(fs_node)))) 
        self.features = namedtuple('features', ('lemma', 'cat', 'gen', 'num', 'per', 'case', 'vib', 'tam'))
    
    def morphFeatures (self, af):
        """LEMMA, CAT, GEN, NUM, PER, CASE, VIB, TAM"""
	af = af[1:-1].split(",")
        assert len(af) == 8 # no need to process trash! FIXME
        return af

    def buildNode(self, id_, form_, tag_, pairs_):
        wordForm_, Tag_, name_, head_, posn_, vpos_, chunkId_, chunkType_, depRel_, = [str()]*9
        corel_, coref_, parent_, stype_, voicetype_, features_, poslcat_, mtype_, troot_ = [str()]*9
        wordForm_, Tag_ = form_, tag_
        for key, value in pairs_.items():
            if key == "af":
                lemma_, cat_, gen_, num_, per_, case_, vib_, tam_ = self.morphFeatures(value) 
                features_ = self.features(lemma_, cat_, gen_, num_, per_, case_, vib_, tam_)
            elif key == "name":
                name_ = re.sub("'|\"", '', value) #NOTE word is used as word in deprel
            elif key == "chunkType":
                assert len(value.split(":", 1)) == 2 # no need to process trash! FIXME
                chunkType_, chunkId_ = re.sub("'|\"", '', value).split(":", 1)
            elif key == "head":
                head_ = re.sub("'|\"", '', value)
            elif key == "posn":
                posn_ = re.sub("'|\"", '', value)
            elif key == "vpos":
                vpos_ = re.sub("'|\"", '', value)
            elif key == "poslcat":
                poslcat_ = re.sub("'|\"", '', value)
	    elif key == "mtype":
                mtype_ = re.sub("'|\"", '', value)
	    elif key == "troot":
                troot_ = re.sub("'|\"", '', value)
            elif key == "drel":
                assert len(value.split(":", 1)) == 2 # no need to process trash! FIXME
                depRel_, parent_ = re.sub("'|\"", '', value).split(":", 1)
                assert depRel_ and parent_ # no need to process trash! FIXME
	    elif key == "coref":
		try: corel_, coref_ = re.sub("'|\"", '', value).split(":")
		except ValueError: corel_, coref_ = '', re.sub("'|\"", '', value)
            elif key == "stype":
                stype_ = re.sub("'|\"", '', value)
            elif key == "voicetype":
                voicetype_ = re.sub("'|\"", '', value)

	self.fs_order.append([self.maping[x] for x in pairs_.keys() if x in self.maping][::-1])
        self.nodeList.append(self.node(id_, wordForm_, Tag_.decode("ascii", 'ignore').encode("ascii"), features_, \
			name_, head_, chunkId_, chunkType_, posn_, vpos_, depRel_, coref_, stype_, voicetype_, 
			poslcat_, mtype_, troot_, corel_, parent_, self.dmrel_))

    def FSPairs(self, FS):
        feats = OrderedDict()
	self.dmrel_ = False
        for feat in FS.split():
            if "=" not in feat: continue
	    if 'dmrel' in feat:
		self.dmrel_ = True
		feat = feat.replace("dmrel", "drel")
            feat = re.sub("af='+", "af='", feat)
            feat = re.sub("af='+", "af='", feat)
            attribute, value = feat.split("=")
            feats[attribute] = value

        return feats

    def getAnnotations(self):
        for line in self.sentence.split("\n"):
	    line = line.split('\t')
            if line[0].isdigit():
                assert len(line) == 4 # no need to process trash! FIXME
                id_, oBraces_, Tag_ = line[:3]
                attributeValue_pairs = self.FSPairs(line[3][4:-1])
                self.buildNode(id_, oBraces_, Tag_, attributeValue_pairs)
            elif line[0].replace(".", '', 1).isdigit():
                id_, wordForm_, Tag_ = line[:3]
                attributeValue_pairs = self.FSPairs(line[3][4:-1])
                assert wordForm_.strip() and Tag_.strip() # no need to process trash! FIXME
                self.buildNode(id_, wordForm_, Tag_, attributeValue_pairs)
            else:
                self.buildNode('', '))', '', {})

        return self

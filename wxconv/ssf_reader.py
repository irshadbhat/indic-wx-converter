#!/usr/bin/python

# Copyright Riyaz Ahmad Bhat, Irshad Ahmad Bhat 2015.

from __future__ import unicode_literals

import re
from collections import namedtuple, OrderedDict


class SSFReader():

    def __init__(self, sentence):
        self.tokens = list()
        self.fs_order = list()
        self.nodeList = list()
        self.sentence = sentence
        fs_node = (
            'af',
            'name',
            'head',
            'chunkId',
            'chunkType',
            'posn',
            'vpos',
            'drel',
            'coref',
            'stype',
            'voicetype',
            'poslcat',
            'mtype',
            'troot',
            'etype',
            'etype_root',
            'emph',
            'esubtype',
            'etype_name',
            'agr_num',
            'hon',
            'agr_cas',
            'agr_gen')  # NOTE add node
        nodes = (
            'id',
            'wordForm',
            'posTag',
            'af',
            'name',
            'head',
            'chunkId',
            'chunkType',
            'posn',
            'vpos',
            'drel',
            'coref',
            'stype',
            'voicetype',
            'poslcat',
            'mtype',
            'troot',
            'corel',
            'parent',
            'dmrel',
            'etype',
            'etype_root',
            'emph',
            'esubtype',
            'etype_name',
            'agr_num',
            'hon',
            'agr_cas',
            'agr_gen')  # NOTE add node

        self.node = namedtuple('node', nodes)
        self.maping = dict(zip(fs_node, range(len(fs_node))))
        self.features = namedtuple(
            'features',
            (
                'lemma',
                'cat',
                'gen',
                'num',
                'per',
                'case',
                'vib',
                'tam'))

    def morphFeatures(self, af):
        """LEMMA, CAT, GEN, NUM, PER, CASE, VIB, TAM"""
        af = af[1:-1].split(",")
        assert len(af) == 8  # NOTE no need to process trash!
        return af

    def buildNode(self, id_, form_, tag_, pairs_):
        feats_dict = dict()
        wordForm_, Tag_ = form_, tag_
        corel_, coref_, parent_, features_, chunkId_, \
            chunkType_, depRel_, = [str()] * 7  # NOTE add node
        for key, value in pairs_.items():
            if key == "af":
                lemma_, cat_, gen_, num_, per_, case_, \
                    vib_, tam_ = self.morphFeatures(value)
                features_ = self.features(
                    lemma_, cat_, gen_, num_, per_, case_, vib_, tam_)
            elif key == "chunkType":
                # no need to process trash! FIXME
                assert len(value.split(":", 1)) == 2
                chunkType_, chunkId_ = re.sub("'|\"", '', value).split(":", 1)
            elif key == "drel":
                # no need to process trash! FIXME
                assert len(value.split(":", 1)) == 2
                depRel_, parent_ = re.sub("'|\"", '', value).split(":", 1)
                assert depRel_ and parent_  # no need to process trash! FIXME
            elif key == "coref":
                try:
                    corel_, coref_ = re.sub("'|\"", '', value).split(":")
                except ValueError:
                    corel_, coref_ = '', re.sub("'|\"", '', value)
            else:
                feats_dict[key] = re.sub("'|\"", '', value)

        self.fs_order.append([self.maping[x]
                              for x in pairs_.keys()
                              if x in self.maping][::-1])
        self.nodeList.append(
            self.node(
                id_,
                wordForm_,
                Tag_,
                features_,
                feats_dict.get('name', ''),
                feats_dict.get('head', ''),
                chunkId_,
                chunkType_,
                feats_dict.get('posn', ''),
                feats_dict.get('vpos', ''),
                depRel_,
                coref_,
                feats_dict.get('stype', ''),
                feats_dict.get('voicetype', ''),
                feats_dict.get('poslcat', ''),
                feats_dict.get('mtype', ''),
                feats_dict.get('troot', ''),
                corel_,
                parent_,
                self.dmrel_,
                feats_dict.get('etype', ''),
                feats_dict.get('etype_root', ''),
                feats_dict.get('emph', ''),
                feats_dict.get('esubtype', ''),
                feats_dict.get('etype_name', ''),
                feats_dict.get('agr_num', ''),
                feats_dict.get('hon', ''),
                feats_dict.get('agr_cas', ''),
                feats_dict.get('agr_gen', '')))  # NOTE add node

    def FSPairs(self, FS):
        feats = OrderedDict()
        self.dmrel_ = False
        for feat in FS.split():
            if "=" not in feat:
                continue
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
            if '\t' not in line:
                raise ValueError('Corrupted ssf: Tabs broken into spaces')
            line = line.split('\t')
            if line[0].isdigit():
                # no need to process trash! FIXME
                assert len(line) == 4
                id_, oBraces_, Tag_ = line[:3]
                attributeValue_pairs = self.FSPairs(line[3][4:-1])
                self.buildNode(id_, oBraces_, Tag_, attributeValue_pairs)
            elif line[0].replace(".", '').isdigit():
                id_, wordForm_, Tag_ = line[:3]
                attributeValue_pairs = self.FSPairs(line[3][4:-1])
                # no need to process trash! FIXME
                assert wordForm_.strip() and Tag_.strip()
                self.buildNode(id_, wordForm_, Tag_, attributeValue_pairs)
            else:
                self.buildNode('', '))', '', {})

        return self

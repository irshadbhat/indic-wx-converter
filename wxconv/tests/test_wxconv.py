#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import re

from testtools import TestCase

from wxconv import WXC


class TestWX(TestCase):

    def setUp(self):
        super(TestWX, self).setUp()
        self.languages = 'hin urd ben guj mal pan tel tam kan ori'.split()
        self.test_dir = os.path.dirname(os.path.abspath(__file__))

    def test_raw_text(self):
        for lang in self.languages:
            wx_con = WXC(order='utf2wx', lang=lang)
            utf_con = WXC(order='wx2utf', lang=lang)
            with io.open('%s/plain_text/%s.txt' % (self.test_dir, lang),
                         encoding='utf-8') as fp:
                for line in fp:
                    wx = wx_con.convert(line)
                    utf = utf_con.convert(wx)
                    wx_ = wx_con.convert(utf)
                    self.assertEqual(wx, wx_)

    def test_other(self):
        for ext in ['ssf', 'conll', 'tnt']:
            wx_con = WXC(
                order='utf2wx',
                lang='hin',
                format_=ext,
                ssf_type='intra',
                rmask=False)
            utf_con = WXC(
                order='wx2utf',
                lang='hin',
                format_=ext,
                ssf_type='intra',
                rmask=False)
            with io.open('%s/%s/hin.%s' % (self.test_dir, ext, ext),
                         encoding='utf-8') as fp:
                if ext == "ssf":
                    sentences = re.finditer(
                        "(<Sentence id=.*?>)(.*?)</Sentence>", fp.read(), re.S)
                    for sid_sentence in sentences:
                        sentence = sid_sentence.group(2).strip()
                        wx = wx_con.convert(sentence)
                else:
                    for line in fp:
                        wx = wx_con.convert(line)
                        utf = utf_con.convert(wx)
                        wx_ = wx_con.convert(utf)
                        self.assertEqual(wx, wx_)

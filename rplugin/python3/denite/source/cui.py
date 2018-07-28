# -*- coding: utf-8 -*-

# 参考: https://qiita.com/iyuuya/items/8a7e9cc0c9dd6d0e4c32
from .base import Base


class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'cui'
        self.kind = 'file'

    def on_init(self, context):

    def gather_candidates(self, context):

    def _convert(self, info):

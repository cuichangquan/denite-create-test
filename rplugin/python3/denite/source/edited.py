# -*- coding: utf-8 -*-

from .base import Base
from denite import util
import logging

import os
import site
import re
import inflection
from subprocess import Popen, PIPE

logger = logging.getLogger('DeniteSourceEditedLog')
logger.setLevel(10)

class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'edited'
        self.kind = 'file'

    def on_init(self, context):
        cbname = self.vim.current.buffer.name
        context['__cbname'] = cbname
        self.root_path = util.path2project(self.vim, cbname, context.get('root_markers', ''))

        fh = logging.FileHandler(self.root_path + '/log/edited.log')
        logger.addHandler(fh)

    def gather_candidates(self, context):
        args = context['args']

        # TODO: 環境変数を利用する
        # 崔 昌権
        # 2018-05-01
        cmd_str1 = ('git log --author="崔 昌権" --after="2018-05-01" --pretty=format:%H')
        commits = self.exec_cmd(cmd_str1)
        commits = " ".join( commits.decode('utf-8').split('\n') )

        cmd_str2 = ('git show --pretty="format:" --name-only ' + commits)
        files = self.exec_cmd(cmd_str2).decode('utf-8').split('\n')
        files = list(set(filter(lambda str:str != '', files)))
        logger.debug(files)

        return [self._convert(f) for f in files]

    # ここの結果: 文字列ではbyteだ。
    def exec_cmd(self, cmd):
        return Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()[0]

    def _convert(self, file):
        return {
                    'word': file,
                    'action__path': file
                }

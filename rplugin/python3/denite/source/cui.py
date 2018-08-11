# -*- coding: utf-8 -*-

# 参考: https://qiita.com/iyuuya/items/8a7e9cc0c9dd6d0e4c32
# http://koturn.hatenablog.com/category/neovim
from .base import Base
from denite import util
import logging

import os
import site

logger = logging.getLogger('DeniteSourceCuiLog')
logger.setLevel(10)
fh = logging.FileHandler('cui.log')
logger.addHandler(fh)

# TODO
# source: log/development.logから以下の情報を取ってくる
# Log:  GET "/sai/admin" => SessionsController#login_for_org [時間]
# defualt_action: 「SessionsController#login_for_org」の gfアクション
class Source(Base):

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'cui'
        self.kind = 'file'

    def on_init(self, context):
        cbname = self.vim.current.buffer.name
        context['__cbname'] = cbname
        root_path = util.path2project(self.vim, cbname, context.get('root_markers', ''))
        context['__root_path'] = root_path
        context['__target_file'] = root_path + 'log/development.log'

    # def on_close(self, context):
        # TODO

        # このソースをみたほうが早い
        # https://github.com/5t111111/denite-rails/blob/master/rplugin/python3/denite/source/rails.py
        # これを分析してみたほうがいい。
        # https://github.com/Shougo/denite.nvim/blob/master/rplugin/python3/denite/__init__.py
    def gather_candidates(self, context):
        vim_opened_path = self.vim.command('!git rev-parse --show-toplevel')
        logger.info(vim_opened_path)

        return [
                {
                    'word': "file1",
                    'action__path': "~/sai/my-work-helper/agignore"
                    },
                {
                    'word': "file2",
                    'action__path': "~/sai/my-work-helper/command.txt"
                    },
                ]

    # def _convert(self, info):

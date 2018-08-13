# -*- coding: utf-8 -*-

# 参考: https://qiita.com/iyuuya/items/8a7e9cc0c9dd6d0e4c32
# http://koturn.hatenablog.com/category/neovim
from .base import Base
from denite import util
import logging

import os
import site
import re

logger = logging.getLogger('DeniteSourceCuiLog')
logger.setLevel(10)

# TODO
# source: log/development.logから以下の情報を取ってくる
# Log:  GET "/sai/admin" => SessionsController#login_for_org [時間]
# defualt_action: 「SessionsController#login_for_org」の gfアクション

# このソースをみたほうが早い
# https://github.com/5t111111/denite-rails/blob/master/rplugin/python3/denite/source/rails.py
# これを分析してみたほうがいい。
# https://github.com/Shougo/denite.nvim/blob/master/rplugin/python3/denite/__init__.py

class Source(Base):
    request_id_pattern = re.compile("\[[a-z0-9]{32}\]")
    request_path_pattern = re.compile("(\sStarted\s)(.*)(\sfor\s)")
    request_action_pattern = re.compile("(\sProcessing\sby\s)(.*)(\sas\s)")

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'cui'
        self.kind = 'file' # 結果的にファイルを開くので、fileで合っていると思う.

    def on_init(self, context):
        cbname = self.vim.current.buffer.name
        context['__cbname'] = cbname
        root_path = util.path2project(self.vim, cbname, context.get('root_markers', ''))
        context['__root_path'] = root_path
        context['__target_file'] = root_path + '/log/development.log'

        if 'denite-create-test' in root_path:
            fh = logging.FileHandler(root_path + '/log/cui.log')
            logger.addHandler(fh)

    # def on_close(self, context):

    # TODO: 10件のリクエストだけいいんだ
    def gather_candidates(self, context):
        target_file = context['__target_file']
        f = open(target_file, 'r')
        lines = f.readlines()
        f.close()
        target_lines = self._find_lines(lines)
        target_lines.reverse()
        return [self._convert(k, v) for k, v in target_lines]

    # [2018-08-06 10:31:29.948889 #1]  INFO -- : [ad6d6c30799cd639d4975cf063e5f1ae] Started GET "/xxx/admin" for 172.18.0.7 at 2018-08-06 10:31:29 +0900
    # [2018-08-06 10:31:39.006463 #1]  INFO -- : [ad6d6c30799cd639d4975cf063e5f1ae] Processing by SessionsController#create as HTML
    def _find_lines(self, lines):
        target_key_lines = {}
        target_value_lines = {}
        target_lines = []
        for line in lines:
            target_key_lines.update(self.make_target_key_lines(line))
            target_value_lines.update(self.make_target_value_lines(line))

        for request_id, key in target_key_lines.items():
            if request_id in target_value_lines:
                value = target_value_lines[request_id]
                if(key is not None) and (value is not None):
                    target_lines.append([key, value])

        return target_lines

    def make_target_key_lines(self, line):
        target_lines = {}
        if line.find("Started") >= 0:
            result = Source.request_id_pattern.search(line)
            if result is not None:
                request_id = result[0]
                request_path = self.get_request_path(line)
                if request_path is not None:
                    target_lines[request_id] = request_path
        return target_lines

    def make_target_value_lines(self, line):
        target_lines = {}
        if line.find("Processing") >= 0:
            result = Source.request_id_pattern.search(line)
            if result is not None:
                request_id = result[0]
                action = self.get_rails_action(line)
                if action is not None:
                    target_lines[request_id] = action
        return target_lines

    def get_request_path(self, line):
        result = Source.request_path_pattern.search(line)
        key = None
        if result is not None:
            key = line[:20] + '] ' + result[2]
        return key

    def get_rails_action(self, line):
        result = Source.request_action_pattern.search(line)
        value = None
        if result is not None:
            value = result[2]
        return value

    def _convert(self, key, value):
        return {
                    'word': key + ' => ' + value,
                    'action__path': value        # TODO
                }

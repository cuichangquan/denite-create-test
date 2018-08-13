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
    meta_keyword1 = "Started"
    meta_keyword2 = "Processing"
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
        return [self._convert(line) for line in target_lines]

    # [2018-08-06 10:31:29.948889 #1]  INFO -- : [ad6d6c30799cd639d4975cf063e5f1ae] Started GET "/xxx/admin" for 172.18.0.7 at 2018-08-06 10:31:29 +0900
    # [2018-08-06 10:31:39.006463 #1]  INFO -- : [ad6d6c30799cd639d4975cf063e5f1ae] Processing by SessionsController#create as HTML
    def _find_lines(self, lines):

        target_lines = []
        for line in lines:
          if(line.find(Source.meta_keyword1) >= 0 or line.find(Source.meta_keyword2) >= 0):
              target_lines.append(line)

        request_id = None
        log_key = None
        new_target_lines =[]
        for line in target_lines:
            if (request_id is not None) and (line.find(request_id)) and (log_key is not None):
                log_value = self._make_value_from_line(line)
                if (log_key is not None) and (log_value is not None):
                    new_target_lines.append(log_key + '=>' + log_value)
                request_id = None
                log_key = None
            else:
                result = Source.request_id_pattern.search(line)
                if result is not None:
                    request_id = result[0]
                    log_key = self._make_key_from_line(line)

        return new_target_lines

    def _make_key_from_line(self, line):
        result = Source.request_path_pattern.search(line)
        key = None
        if result is not None:
            key = line[:20] + '] ' + result[2]
        return key

    def _make_value_from_line(self, line):
        result = Source.request_action_pattern.search(line)
        value = None
        if result is not None:
            value = result[2]
        return value

    def _convert(self, info):

        return {
                    'word': info,
                    'action__path': "~/sai/my-work-helper/agignore"
                }

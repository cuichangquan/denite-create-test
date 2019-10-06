# -*- coding: utf-8 -*-
# 以下のようなRailsログにて、アクセス解析する
# 2019-03-03 11:17:53.541382 I [13042:puma 003] {request_id: d25efb37-436b-4fec-968a-afe1f1f79c9b, user_type: api_call} (29.6ms) Api::OrdersController -- Completed #update -- { :controller => "Api::OrdersController"・・・ }

from .base import Base
from denite import util
import logging

import os
import site
import re
import inflection

logger = logging.getLogger('DeniteSourceCuiApiLog')
logger.setLevel(10)

class Source(Base):
    # この行はone requestのなかで1つしかないと思っている

    # 最長: .*
    # 最短: .*?
    # 最長: .+
    # 最短: .+?
    # 最長: .?
    # 最短: .??
    pattern                    = re.compile("request_id: [a-z0-9-]{36}.*\s--\sCompleted\s#.*\s--\s(.*)")
    request_path_pattern       = re.compile(",\s?:method\s?=>\s?\"(.*)\",.*\s?:path\s?=>\s?\"(.*)\",")
    request_controller_pattern = re.compile(":controller\s?=>\s?\"(.*?)\",") # 最短マッチ
    request_action_pattern     = re.compile(":action\s?=>\s?\"(.*?)\",") # 最短マッチ

    # 文字に対して、色をつけているコード(ANSI color codes)
    # ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    default_log_file = '/log/development.log'

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'cui_api'
        self.kind = 'file'

    def on_init(self, context):
        cbname = self.vim.current.buffer.name
        context['__cbname'] = cbname
        self.root_path = util.path2project(self.vim, cbname, context.get('root_markers', ''))

        buffer_name = os.path.basename(cbname)
        _, ext = os.path.splitext(cbname)
        # 注意:
        #   - プロジェクトのRootの下でNeoVimを開いてください
        #   - development.log以外のファイルを処理したい時:
        #     - 拡張子: log
        #     - log/の下においてください。
        #     - vimで処理したいファイルを開いてください
        if (ext == '.log') and (buffer_name != '') and (buffer_name != 'development.log'):
            context['__target_file'] = cbname
        else:
            context['__target_file'] = self.root_path + Source.default_log_file

        # ログ見たいのであれば、development.logを denite-create-test/log/にいれてください。
        # tail -f log/cui_api.log
        if 'denite-create-test' in self.root_path:
            fh = logging.FileHandler(self.root_path + '/log/cui_api.log')
            logger.addHandler(fh)

    def gather_candidates(self, context):
        # logger.info(self.root_path)
        target_file = context['__target_file']
        f = open(target_file, 'r')
        lines = f.readlines()
        f.close()

        target_lines = self._find_lines(lines)
        target_lines.reverse()
        return [self._convert(date_time, line) for date_time, line in target_lines]

    # 2019-03-03 11:17:53.541382 I [13042:puma 003] {request_id: d25efb37-436b-4fec-968a-afe1f1f79c9b, user_type: api_call} (29.6ms) Api::OrdersController -- Completed #update -- { :controller => "Api::OrdersController"・・・ }
    def _find_lines(self, lines):
        target_lines = []
        for line in lines:
            result = Source.pattern.search(line)
            if result is not None:
                date_time = line[0:19]
                target_lines.append([date_time, result])
        return target_lines

    def _convert(self, date_time, result):
        params          = result[1]
        path            = self.get_request_path(params)
        controller_name = self.get_request_controller(params)
        action_name     = self.get_request_action(params)
        logger.info(path)
        logger.info(controller_name)
        logger.info(action_name)
        return {
                    'word': '['+ date_time + '] ' + path + ' => ' + controller_name + "#" + action_name,
                    'action__path': self.get_controller_full_name(controller_name),
                    'action__pattern': '\<def ' + action_name + '\>'
                }

    def get_request_path(self, params):
        request_path = Source.request_path_pattern.search(params)
        if request_path is not None:
            return request_path[1] + ' ' + request_path[2]

    def get_request_controller(self, params):
        request_controller = Source.request_controller_pattern.search(params)
        if request_controller is not None:
            return request_controller[1]

    def get_request_action(self, params):
        request_action = Source.request_action_pattern.search(params)
        if request_action is not None:
            return request_action[1]

    def get_controller_full_name(self, conroller_name):
        conroller_name = inflection.underscore(conroller_name).replace('::', '/')
        return self.root_path + '/app/controllers/' + conroller_name + '.rb'


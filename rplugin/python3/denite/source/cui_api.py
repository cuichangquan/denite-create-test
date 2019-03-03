# -*- coding: utf-8 -*-

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
    pattern = re.compile("request_id: [a-z0-9-]{36}.*ms\)\s(.*Controller)\s--\sCompleted\s#(.*)\s--\s(.*)")
    request_path_pattern = re.compile(",\s:path\s=>\s\"(.*)\",")
    # 文字に対して、色をつけているコード(ANSI color codes)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def __init__(self, vim):
        super().__init__(vim)
        self.name = 'cui_api'
        self.kind = 'file'

    def on_init(self, context):
        cbname = self.vim.current.buffer.name
        context['__cbname'] = cbname
        self.root_path = util.path2project(self.vim, cbname, context.get('root_markers', ''))
        context['__target_file'] = self.root_path + '/log/development.log'

        # if 'denite-create-test' in self.root_path:
        fh = logging.FileHandler(self.root_path + '/log/cui_api.log')
        logger.addHandler(fh)

    def gather_candidates(self, context):
        # logger.info(self.root_path)
        target_file = context['__target_file']
        f = open(target_file, 'r')
        lines_with_ansi_color_code = f.readlines()
        f.close()

        lines = []
        for line in lines_with_ansi_color_code:
            lines.append(Source.ansi_escape.sub('', line))

        target_lines = self._find_lines(lines)
        target_lines.reverse()
        return [self._convert(date_time, line) for date_time, line in target_lines]

    # 2019-03-03 11:17:53.541382 I [13042:puma 003] {request_id: d25efb37-436b-4fec-968a-afe1f1f79c9b, user_type: api_call} (29.6ms) Sys::Api::OrderSettlementsController -- Completed #update -- { :controller => "Sys::Api::OrderSettlementsController"・・・ }
    def _find_lines(self, lines):
        target_lines = []
        for line in lines:
            result = Source.pattern.search(line)
            logger.info(result)
            if result is not None:
                date_time = line[0:19]
                target_lines.append([date_time, result])
        return target_lines

    def _convert(self, date_time, result):
        controller_name = result[1]
        action_name     = result[2]
        params          = result[3]
        return {
                    'word': '['+ date_time + '] ' + self.get_request_path(params) + ' => ' + controller_name + "#" + action_name,
                    'action__path': self.get_controller_full_name(controller_name),
                    'action__pattern': '\<def ' + action_name + '\>'
                }

    def get_request_path(self, params):
        request_path = Source.request_path_pattern.search(params)
        if request_path is not None:
            return request_path[1]

    def get_controller_full_name(self, conroller_name):
        conroller_name = inflection.underscore(conroller_name).replace('::', '/')
        return self.root_path + '/app/controllers/' + conroller_name + '.rb'


# https://www.jdoodle.com/python3-programming-online
# import re
# request_path_pattern = re.compile(",\s:path\s=>\s\"(.*)\",")
# request_completed_pattern = re.compile("request_id: [a-z0-9-]{36}.*ms\)\s(.*Controller)\s--\sCompleted\s#(.*)\s--\s(.*)")
# line = '2019-03-03 11:17:53.541382 I [13042:puma 003] {request_id: d25efb37-436b-4fec-968a-afe1f1f79c9b, user_type: api_call} (29.6ms) Sys::Api::OrderSettlementsController -- Completed #update -- { :controller => "Sys::Api::OrderSettlementsController", :action => "update", :params => { "settlement" => { "settle_no" => "5555", "expiration_date" => "2019-08-06", "payment_url" => "http://localhost" }, "order_id" => "3", "order_settlement" => { "settlement" => { "settle_no" => "5555", "expiration_date" => "2019-08-06", "payment_url" => "http://localhost" } } }, :format => "*/*", :method => "PATCH", :path => "/sys/orders/3/settlement", :status => 200, :view_runtime => 1.71, :db_runtime => 16.05, :status_message => "OK" }'
# result = request_completed_pattern.search(line)
# print(result[0])
# print(result[1])
# print(result[2])
# print(result[3])
# request_path=request_path_pattern.search(line)
# print(request_path[0])
# print(request_path[1])

# 結果
# request_id: d25efb37-436b-4fec-968a-afe1f1f79c9b, user_type: api_call} (29.6ms) Sys::Api::OrderSettlementsController -- Completed #update -- { :controller => "Sys::Api::OrderSettlementsController", :action => "update", :params => { "settlement" => { "settle_no" => "5555", "expiration_date" => "2019-08-06", "payment_url" => "http://localhost" }, "order_id" => "3", "order_settlement" => { "settlement" => { "settle_no" => "5555", "expiration_date" => "2019-08-06", "payment_url" => "http://localhost" } } }, :format => "*/*", :method => "PATCH", :path => "/sys/orders/3/settlement", :status => 200, :view_runtime => 1.71, :db_runtime => 16.05, :status_message => "OK" }
# Sys::Api::OrderSettlementsController
# update
# { :controller => "Sys::Api::OrderSettlementsController", :action => "update", :params => { "settlement" => { "settle_no" => "5555", "expiration_date" => "2019-08-06", "payment_url" => "http://localhost" }, "order_id" => "3", "order_settlement" => { "settlement" => { "settle_no" => "5555", "expiration_date" => "2019-08-06", "payment_url" => "http://localhost" } } }, :format => "*/*", :method => "PATCH", :path => "/sys/orders/3/settlement", :status => 200, :view_runtime => 1.71, :db_runtime => 16.05, :status_message => "OK" }
# , :path => "/sys/orders/3/settlement",
# /sys/orders/3/settlement

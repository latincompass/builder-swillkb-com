#!/usr/bin/env python
# -*- coding: utf-8 -*-

# kb_builder builds keyboard plate and case CAD files using JSON input.
#
# Copyright (C) 2015  Will Stevens (swill)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import json
import logging
import time
import traceback

import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web

from config import config

builder_timeout = 7200

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IndexHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()

    def get(self):
        self.render('index.html')

    @tornado.gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
            data_hash = hashlib.sha1(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
            build_start = time.time()
            logger.info("Processing: %s" % (data_hash))
            
            import lib.builder as builder
            cad = builder.build(data_hash, data, config)
            
            processing_time = time.time() - build_start
            logger.info("Finished: %s" % (data_hash))
            logger.info("Processing took: {0:.2f} seconds".format(processing_time))
            self.write(cad)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s" % str(e))
            self.set_status(400)
            self.write({'error': 'Invalid JSON input', 'message': str(e)})
        except Exception as e:
            logger.error("Error processing request: %s" % str(e))
            logger.error(traceback.format_exc())
            self.set_status(500)
            self.write({'error': 'Internal server error', 'message': str(e)})


def make_app():
    settings = {
        'template_path': 'templates',
        'static_path': config['app']['static'],
        'debug': config['app']['debug']
    }
    return tornado.web.Application([
        (r"/", IndexHandler)
    ], **settings)


def main():
    tornado.options.options.log_file_prefix = config['app']['log']
    tornado.options.parse_command_line()
    logger.info("Started the kb_builder on port %d..." % config['app']['port'])
    app = make_app()
    app.listen(config['app']['port'])
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()

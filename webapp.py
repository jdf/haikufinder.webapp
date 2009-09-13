#
# Copyright (c) 2009, Jonathan Feinberg <jdf@pobox.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, 
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   3. The name of the author may not be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED 
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR 
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import with_statement
from haikufinder import HaikuFinder
from mako.template import Template
import web
import os.path
import re

thisdir = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(thisdir, "templates")
static = os.path.join(thisdir, "static")

class HaikuFindingPage:
    def __init__(self, content_type, template):
        with open(os.path.join(templates, template), "r") as t:
            self.content_type = content_type
            self.template = Template(t.read())
    
    def decorate(self, s):
        web.header('Content-Length', len(s))
        return s
    
    def GET(self):
        web.header('Content-Type', self.content_type)
        return self.decorate(self.template.render_unicode().encode('utf-8', 'replace'))
    
    def POST(self):
        haikus = HaikuFinder(web.input().text).find_haikus()
        web.header('Content-Type', self.content_type)
        if haikus:
            return self.decorate(self.template.render_unicode(haikus=haikus).encode('utf-8', 'replace'))
        else:
            return self.decorate(self.template.render_unicode(nonefound=True).encode('utf-8', 'replace'))

class HTMLPage(HaikuFindingPage):
    def __init__(self):
        HaikuFindingPage.__init__(self, "text/html", "index.html")
        
class TextPage(HaikuFindingPage):
    def __init__(self):
        HaikuFindingPage.__init__(self, "text/plain", "text.plain")

types = { 
         'css': 'text/css'
        }

class Resource:
    def __init__(self):
        self.cache = dict()
        
    def ct(self, resource):
        try:
            return types[resource.split(".")[-1].lower()]
        except:
            return "application/octet-stream"

    def GET(self, resource):
        if not self.cache.has_key(resource):
            if resource in os.listdir(static):
                ct = self.ct(resource)
                web.header("Content-Type", ct)
                with open(os.path.join(static,resource),"rb") as f:
                    r = f.read()
                self.cache[resource] = (ct,r)
            else:
                self.cache[resource] = None
                
        r = self.cache[resource]
        if r is None:
            return web.notfound()
        else:
            web.header("Content-Type", r[0])
            return r[1]

if __name__ == '__main__':
    urls = (
            r'/haikufinder/static/(.*)', Resource,            
            r'/haikufinder/text/?', TextPage,
            r'/haikufinder/?', HTMLPage,
            r'/text/?', TextPage,
            r'/static/(.*)', Resource,
            r'/', HTMLPage,
            )
    web.config.debug = False
    app = web.application(urls, globals())
    app.run()
    
    

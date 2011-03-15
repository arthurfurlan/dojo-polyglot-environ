#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Arthur Furlan <afurlan@afurlan.org>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or any later version.
#
# On Debian systems, you can find the full text of the license in
# /usr/share/common-licenses/GPL-2


import os
import sys
import glob
import optparse
import subprocess
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TMPL_DIR = os.path.join(ROOT_DIR, 'templates')
ICON_FILES = {
    'error': os.path.join(ROOT_DIR, 'images/error.png'),
    'success': os.path.join(ROOT_DIR, 'images/success.png'),
}

class DojoPolyglotEnviron:

    def _get_template_files(self, name='*'):
        '''
        List all available templates based on "name"
        '''

        return glob.glob(os.path.join(TMPL_DIR, name + '.*'))

    def _test_and_notify(self, command_args):
        '''
        Execute a command and notify if it was successful or not
        '''

        notify_args = ['notify-send', '-i']
        retcode = subprocess.call(command_args)
        if not retcode:
            notify_args.append(ICON_FILES['success'])
            notify_args.append('Tests passed.')
        else:
            notify_args.append(ICON_FILES['error'])
            notify_args.append('Tests failed.')
        subprocess.call(notify_args)

    def _test(self, fname, lang=None):
        '''
        Execute the file in order to check if the tests passed
        '''

        # create dict of "extensions vs. languages"
        lang_ext = {}
        for t in self._get_template_files():
            l, e = os.path.basename(t).split('.')
            lang_ext[e] = l

        # check if the file extension is supported
        extension = fname.split('.')[-1]
        if extension not in lang_ext and not lang:
            print 'ERROR: Extension "%s" not supported.' % extension
            return
        elif not lang:
            lang = lang_ext[extension]
        
        if '/' not in fname:
            fname = './' + fname
        command_args = [ lang, fname]
        self._test_and_notify(command_args)

    def do_create(self, lang, name):
        '''
        Create a new dojo file
        '''

        # check if the language is supported... it means, check if there is
        # an existent template for this language in the TMPL_DIR
        template = self._get_template_files(lang)
        if not template:
            print 'ERROR: Language "%s" not supported.' % lang
            return
       
        # create the output file name based on language
        output = os.path.basename(template[0])
        output = output.replace(lang, name, 1).lower()

        # write the content of the output file
        ft, fo = open(template[0]), open(output, 'w+')
        for line in ft:
            line = line.replace('CLASSNAME', name)
            line = line.replace('DATETIME', datetime.now().strftime('%Y-%m-%d %T'))
            fo.write(line)
        fo.close()
        os.chmod(output, 0744)

    def do_daemon(self, path, timeout):
        pass

    def run(self, args):
        '''
        Run the application via command line interface. Parse the arguments and
        execute the action based on them.
        '''

        usage = 'Usage: %prog OPTIONS'
        parser = optparse.OptionParser(usage=usage)

        # application actions
        parser.add_option('-c', metavar='DOJO',
            help='create a new dojo file')
        parser.add_option('-d', metavar='DOJO',
            help='start the daemon for a file')

        # application options
        parser.add_option('-l', metavar='LANG',
            help='language used in the dojo')
        parser.add_option('-t', metavar='TIME',
            help='session timeout (default: 300)')
        (opts, args) = parser.parse_args()

        if hasattr(opts, 'create'): # create a new dojo file
            return self.do_create(opts.language, opts.create)
        if hasattr(opts, 'daemon'): # start the daemon
            return self.do_daemon(opts.daemon, opts.timeout or 300)
        else:
            parser.print_help()


if __name__ == '__main__':
    dj = DojoPolyglotEnviron()
    sys.exit(dj.run(sys.argv[:1]))

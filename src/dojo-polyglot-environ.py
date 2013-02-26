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

import pygtk
pygtk.require('2.0')
import gtk

import os
import sys
import glob
import time
import gobject
import optparse
import threading
import subprocess
from datetime import datetime

gtk.gdk.threads_init()

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TMPL_DIR = os.path.join(ROOT_DIR, 'templates')
ICON_FILES = {
    'error': os.path.join(ROOT_DIR, 'images/error.png'),
    'success': os.path.join(ROOT_DIR, 'images/success.png'),
    'timeout': os.path.join(ROOT_DIR, 'images/timeout.png'),
}

class Error(Exception):
    pass

class DojoPolyglotEnviron(gtk.Window):

    def __init__(self):
        super(DojoPolyglotEnviron, self).__init__()
        self.last_mtime = 0
        self.test_passed = True
        self.paused = False
        self.tcount = 0

    def _get_template_files(self, name='*'):
        '''
        List all available templates based on "name"
        '''

        return glob.glob(os.path.join(TMPL_DIR, name + '.*'))

    def _format_time(self, seconds):
        minutes = seconds/60
        seconds = seconds%60
        return '%0.2d:%0.2d' % (minutes, seconds)

    def _test_and_notify(self, command_args):
        '''
        Execute a command and notify if it was successful or not
        '''

        notify_args = ['notify-send', '-i']
        retcode = subprocess.call(command_args)
        if not retcode:
            notify_args.append(ICON_FILES['success'])
            notify_args.append('Tests passed.')
            self.tray.set_from_stock(gtk.STOCK_YES)
            self.test_passed = True
        else:
            notify_args.append(ICON_FILES['error'])
            notify_args.append('Tests failed.')
            self.tray.set_from_stock(gtk.STOCK_NO)
            self.test_passed = False
        subprocess.call(notify_args)

    def _test_if_modified(self, path, timeout, lang=None):
        if not self.paused:
            mtime = os.stat(path).st_mtime
            if mtime > self.last_mtime:
                self.last_mtime = mtime
                self._test(path)

            self.tcount += 1
            self.tray.set_tooltip(self._format_time(timeout-self.tcount))

            if self.tcount >= timeout:
                self._timeout_message()
                self.tcount = 0

        return True

    def _test(self, path, lang=None):
        '''
        Execute the file in order to check if the tests passed
        '''

        # create dict of "extensions vs. languages"
        lang_ext = {}
        for t in self._get_template_files():
            l, e = os.path.basename(t).split('.')
            lang_ext[e] = l

        # check if the file extension is supported
        extension = path.split('.')[-1]
        if extension not in lang_ext and not lang:
            raise Error('Extension "%s" not supported.' % extension)
        elif not lang:
            lang = lang_ext[extension]

        if '/' not in path:
             path = './' + path
        command_args = ['env', lang, path]
        self._test_and_notify(command_args)

    def _timeout_message(self):
        '''
        This dialog code is broken, should be fixed later!

        message = 'Your time is up!'
        md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
            gtk.BUTTONS_OK, message)
        md.run()
        md.destroy()
        '''

        notify_args = ['zenity', '--warning', '--text', 'Your time is up!']
        subprocess.call(notify_args)

    def _toggle_pause(self):
        if self.paused:
            if self.test_passed:
                self.tray.set_from_stock(gtk.STOCK_YES)
            else:
                self.tray.set_from_stock(gtk.STOCK_NO)
        else:
            self.tray.set_from_stock(gtk.STOCK_MEDIA_PAUSE)
        self.paused = not self.paused

    def _on_tray_lclick(self, *args):
        self._toggle_pause()

    def _on_tray_rclick(self, *args):
        print "right click"

    def _create_tray(self):
        self.tray = gtk.StatusIcon()
        self.tray.set_from_stock(gtk.STOCK_YES)
        self.tray.connect("activate", self._on_tray_lclick)
        self.tray.connect("popup-menu", self._on_tray_rclick)
        self.tray.set_tooltip("Dojo Polyglot Environ")

    def do_create(self, lang, name):
        '''
        Create a new dojo file
        '''

        # check if the language is supported... it means, check if there is
        # an existent template for this language in the TMPL_DIR
        template = self._get_template_files(lang)
        if not template:
            raise Error('Language "%s" not supported.' % lang)

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

    def do_daemon(self, path, timeout, lang=None):
        self._create_tray();

#        t = threading.Thread(target=self._test_if_modified, args=(path, timeout, lang))
#        t.setDaemon(True)
#        t.start()

        gobject.timeout_add(1000, self._test_if_modified, path, timeout, lang)
        gtk.main()

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

        if opts.c: # create a new dojo file
            if opts.l is None:
                parser.error('-l LANG missing')
            return self.do_create(opts.l, opts.c)
        if opts.d: # start the daemon
            timeout = int(opts.t) if opts.t else 300
            return self.do_daemon(opts.d, timeout, opts.l)
        else:
            parser.print_help()

        gtk.main()


if __name__ == '__main__':
    try:
        dj = DojoPolyglotEnviron()
        dj.run(sys.argv[:1])
    except Error, msg:
        sys.stderr.write("ERROR: %s\n" % msg)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.stderr.write("interrupted\n")

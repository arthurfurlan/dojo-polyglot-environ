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
import glob
import subprocess
from datetime import datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def _get_template_files(name='*'):
    return glob.glob(os.path.join(TEMPLATES_DIR, name + '.*'))

def create(lang, name):
    ''' Creates the new dojo file '''

    # check if the language is supported... it means, check if there is
    # an existent template for this language in the TEMPLATES_DIR
    template = _get_template_files(lang)
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

def execute(fname, lang=None):
    ''' Execute the file in order to check if the tests passed '''

    # create dict of "extensions vs. languages"
    lang_ext = {}
    for t in _get_template_files():
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
    cmd_args = ['env', lang, fname]
    subprocess.call(cmd_args)

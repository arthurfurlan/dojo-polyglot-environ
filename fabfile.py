#!/usr/bin/env fab
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Arthur Furlan <afurlan@afurlan.org>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or any later version.
#
# On Debian systems, you can find the full text of the license in
# /usr/share/common-licenses/GPL-2


from fabric.api import *
from fabric.contrib import files
import os, glob, shutil, datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def create(lang, name):
    ''' Creates the new dojo file '''

    # check if the language is supported... it means, check if there is
    # an existent template for this language in the TEMPLATES_DIR
    template = os.path.join(TEMPLATES_DIR, lang)
    template = glob.glob(template + '.*')
    if not template:
        print 'ERROR: Language not supported.'
        return
    
    dtstr = datetime.datetime.now().strftime('%Y-%m-%d %T')

    # create the output file and rename to the same name of the class
    output = os.path.basename(template[0])
    output = output.replace(lang, name, 1).lower()
    shutil.copy(template[0], output)
    local(r"sed -i 's/CLASSNAME/%s/g' %s" % (name, output))
    local(r"sed -i 's/DATETIME/%s/g' %s" % (dtstr, output))
    local(r"chmod u+x %s" % output)

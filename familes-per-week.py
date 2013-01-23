#!/usr/bin/env python
#
# Copyright (c) 2013, 
# Виталий Волков <hash.3g@gmail.com> 
# Dave Crossland <dave@understandinglimited.com>
#
# Released under the Apache License version 2.0 or later.
# See accompanying LICENSE file for details.
# 
# gwf_files.py - prints date and number of TTF files
# in each published family for each revision of the repo
#

import csv
import hglib
import hglib.error
import hglib.util
import os
import re


GWF_REPO = os.environ.get('GWF_REPO') or '/media/X-Files/googlefontdirectory'


class g(object):
    pass


g.client = hglib.open(GWF_REPO)
g.iterrev = None
g.exclude = [
    "visibility\: sandbox",
    "visibility\: INTERNAL",
    '"visibility"\: "Sandbox"',
    '"visibility"\: "Internal"'
]


def lookup_metadata(f):
    result = False
    if re.search(r'METADATA(.json)?$', f[4], re.U):
        tries = 0
        try:
            fp = open(os.path.join(GWF_REPO, f[4]), 'r')
            content = fp.read()
            fp.close()

            for rule in g.exclude:
                if rule.lower() in content.lower():
                    break
                tries += 1
        except (IOError, OSError):
            print 'Unable to read', f[4], 'from revision',  g.iterrev[0]
            result = False
        if tries == len(g.exclude):
            result = True
        else:
            g.exclude_dirs.append(os.path.dirname(f[4]))
    return result


def lookup_fonts(f):
    if re.search('({0}).+\.ttf$'.format('|'.join(map(re.escape, g.exclude_dirs))), f[4], re.I):
        return True
    return False


def revision():
    fp = open('gwf_files.csv', 'w')

    doc = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    doc.writerow(['date', '/'])

    revs = reversed(g.client.log(revrange='tip:1'))

    files = []
    for rev in list(revs):
        g.iterrev = rev
        g.exclude_dirs = []

        print 'Updating to rev', rev, '...',
        g.client.update(rev=rev[0], clean=True)
        print ' done!'
        flist = list(g.client.manifest())
        files = filter(lookup_metadata, flist)

        # for files we got directory that has manifests
        if files:
            row = [rev[6].strftime('%Y-%m-%d %H:%M')]
            files = filter(lookup_fonts, flist)
            row.append(len(files))
            doc.writerow(row)

    fp.close()


if __name__ == '__main__':
    revision()

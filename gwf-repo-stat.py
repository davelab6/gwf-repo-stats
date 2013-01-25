#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, 
# Виталий Волков <hash.3g@gmail.com> 
# Dave Crossland <dave@understandinglimited.com>
#
# Released under the Apache License version 2.0 or later.
# See accompanying LICENSE file for details.
# 
# gwf-repo-stats.py - prints date and number of TTF files
# in each published family for each revision of the repo
#
# See README.md for details. Quick usage: 
#
# $ python gwf-repo-stats.py /home/user/googlefontdirectory;

import argparse
import csv
import hglib
import hglib.error
import hglib.util
import os
import re


class g(object):
    csv_file = 'gwf-repo-stats.csv'
    html_report_file = 'gwf-repo-stats.html'
    iterrev = None
    client = None
    exclude = [
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
            fp = open(os.path.join(g.gwf_repo, f[4]), 'r')
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


def html_report():
    if not os.path.exists(g.csv_file):
        return False
    fp = open(g.html_report_file, 'w')
    html = '''
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
            ['Date', 'Files'],
          %s
        ]);

        var options = {
          title: 'Company Performance'
        };

        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>
  </head>
  <body>
    <div id="chart_div" style="width: 900px; height: 500px;"></div>
  </body>
</html>
    '''

    reader = csv.reader(open(g.csv_file), delimiter=',')
    data = []
    i = 0
    for row in reader:
        if not i:
            i += 1
            continue
        data.append('["%s", %s]' % (row[0], row[1]))
    html = html % ','.join(data)
    fp.write(html)
    fp.close()
    return True


def revision():
    fp = open(g.csv_file, 'w')

    doc = csv.writer(fp, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    doc.writerow(['date', 'files'])

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
            print rev[6].strftime('%Y-%m-%d') + ',', 
            
            if g.count != 'families':
                files = filter(lookup_fonts, flist)
            row.append(len(files))
            print len(files)
            doc.writerow(row)

    fp.close()


def usage():
    parser = argparse.ArgumentParser(description='Analizer revisions of Google Web Font directory')
    parser.add_argument('gwf_repo', metavar='gwf_repo', type=str)
    parser.add_argument('--csv', help='Output csv file')
    parser.add_argument('--html', help='Output html report')
    parser.add_argument('--count', help='Valid values `files`|`families`', default='files')
    return parser.parse_args()


if __name__ == '__main__':
    args = usage()

    g.gwf_repo = args.gwf_repo
    g.client = hglib.open(g.gwf_repo)
    if args.csv:
        g.csv_file = args.csv
    if args.html:
        g.html_report_file = args.html
    if args.count:
        g.count = args.count
    revision()
    html_report()

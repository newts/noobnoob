#!/usr/bin/env python

"""Generate an "INDEX" file based on the content of "meta" files
in all sub-directories.  The index summarizes what tags are relevant
to which projects, to help people find relevant projects.
"""

import os, os.path
import email
from pprint import pprint

outfile = 'INDEX'

def main(args):
    results = dict()
    descriptions = []
    for root, dirs, files in os.walk('.'):
        #print 'Scanning "%s"...' % (root)
        # ignore hidden dirs like '.bzr' and '.git'
        dirs.sort()
        for d in dirs:
            #print 'Dir %s' % (d)
            if d.startswith('.'):
                dirs.remove(d)
                #print 'Removing %s' % (d)
        if root == '.':
            continue
        if 'meta' in files:
            path = os.path.join(root, 'meta')
            descriptions.append(parse(path, results))
        else:
            # Warn if there's no meta in a leaf dir
            if not dirs:
                print 'No "meta" file in %s' % (root)

    lines = [
            'This file lists the tags used by projects in this repository, and a list',
            'of projects associated with each tag.  The purpose is to help people find',
            'projects relevant to their needs, such as hardware or desired features.',
            '',
            'Do not edit this file.  Edit the "meta" files in sub-directories instead,',
            'and run generate-index.py to rebuild this file.',
            ]
    lines.extend(summarize(results, descriptions))
    lines.append('')
    #print '=========='
    #print '\n'.join(lines)
    fp = open(outfile, 'w')
    fp.write('\n'.join(lines))
    fp.close()
    print 'Wrote %i lines to %s' % (len(lines), outfile)

def parse(path, results):
    #print 'Parsing "%s"...' % (path)
    msg = email.message_from_file(open(path))
    #pprint(msg.items())
    description = ''

    path = os.path.dirname(path)
    if path.startswith('./'):
        path = path[2:]

    for k,v in msg.items():
        if k.strip() in ('', 'Description', ):
            description = v
            continue
        v = v.replace('\n', '')
        v = v.replace('  ', ' ')
        for v2 in v.split(', '):
            if v2.strip() in ('', ):
                continue
            key = (k,v2.strip())
            if key not in results:
                results[key] = []
            results[key].append(path)

    return (path, description)

def summarize(results, descriptions):
    lines = []

    # Show a one-liner for each project.
    lines.append('')
    lines.append('Summary of each project')
    lines.append('')
    descriptions.sort()
    for path, desc in descriptions:
        desc = desc.split('\n')[0]
        if not desc: continue
        lines.append('    %s:' % (path,))
        lines.append('        ' + desc)
        lines.append('')

    # Show the tags for each project, sorted by tag
    keys = results.keys()
    # TODO: move 'extras' section to bottom
    keys.sort()
    prev_lk = ''
    for lk,rk in keys:
        if lk != prev_lk:
            lines.append('')
            lines.append('%s' % (lk))
        prev_lk = lk
        lines.append('')
        lines.append('    %s:' % (rk))
        for v in results[(lk,rk)]:
            lines.append('        %s' % (v))

    return lines

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])


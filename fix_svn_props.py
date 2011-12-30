#!/usr/bin/env python

import os.path, subprocess
import argparse

import sys
if sys.version < '2.4':
    print 'This script requires Python 2.4 or greater'
    sys.exit(1)

# Every text-based file everywhere should have native line
# defaults.
EOL_EXTENSIONS = [".sh", ".txt", ".sql", ".properties",
                  ".java", ".jj",
                  ".py", ".pl", ".pm", ".rb",
                  ".js", ".css", ".html",
                  ".xml", ".xsd", ".wsdl", ".xsl"]
EOL = { x:"native" for x in EOL_EXTENSIONS }

# Mime is very specific.
MIME = {
    '.htm': 'text/html',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/js',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.jpg': 'image/jpg',
    '.jpeg': 'image/jpeg'
}

MIME_TEXT_EXTENSIONS = [".sh", ".bash", ".txt", ".sql", ".properties",
                        ".java", ".jj",
                        ".py", ".pl", ".pm", ".rb"]
MIME.update( { x:"text/plain" for x in MIME_TEXT_EXTENSIONS } )

MIME_XML_EXTENSIONS = [".xml", ".xsd", ".wsdl", ".wsdd", ".xsl"]
MIME.update( { x:"text/xml" for x in MIME_XML_EXTENSIONS } )

IGNORED = [".svn", ".hg", ".git", "build/", "/build", "test/working"]

def is_ignorable(name):
    for ignorable in IGNORED:
        if ignorable in name:
            return True
    return False

def is_subversion_controlled_dir(dirname):
    if os.path.isdir(os.path.join(dirname, ".svn")):
        return True
    return False

def visit(args, dirname, files):

    # We test once at directory level and again at file level to
    # try to skip directories before files

    if not os.path.isdir(dirname):
        return
    if is_ignorable(dirname):
        return

    if not is_subversion_controlled_dir(dirname):
        print "%s doesn't appear to be a subversion directory" % dirname
        return

    modified = False

    for file_name in files:
        subname = os.path.join(dirname, file_name)
        if not os.path.isfile(subname):
            continue
        if is_ignorable(subname):
            continue
        
        modified = fix_svn_properties_for_file(subname,
                                               mime=args['mime'], eol=args['eol'], test=args['test'])

    if not modified:
        print "%s had no files needing repair" % (dirname)

def fix_svn_properties_for_file(file_name, mime=True, eol=True, test=False):
    base, ext = os.path.splitext(file_name)

    modified = False
    # verify that this file is not:
    # ? outside of version control
    # I being ignored
    command_st = "svn status %s" % file_name
    output = subprocess.check_output(command_st, shell=True)
    if output.startswith("?") or output.startswith("I"):
        return

    # fix MIME types if necessary
    if mime and ext in MIME.keys():
        command_get = "svn propget svn:mime-type %s" % file_name
        output = subprocess.check_output(command_get, shell=True)
        # note that default format is text, which is fine for us
        # so only if there's output and it's incorrect do we fix
        if output and output.strip() != MIME[ext]:
            print "%s svn:mime-type [%s] should be [%s]" % (file_name, output.strip(), MIME[ext])
            modified = True
            if not test:
                command_set = "svn propset svn:mime-type '%s' %s" % (MIME[ext], file_name)
                subprocess.call(command_set, shell=True)

    # fix EOL settings if necessary
    if eol and ext in EOL.keys():
        command_get = "svn propget svn:eol-style %s" % file_name
        output = subprocess.check_output(command_get, shell=True)
        # again, default behavior here is correct
        if output and output.strip() != EOL[ext]:
            print "%s svn:eol-style [ is : should ] [ %s : %s ]" % (file_name, output.strip(), EOL[ext])
            modified = True
            if not test:
                command_set = "svn propset svn:eol-style '%s' %s" % (EOL[ext], file_name)
                subprocess.call(command_set, shell=True)

    return modified

def walk_directory(path, mime=True, eol=True, test=False):
    os.path.walk(path, visit, {'eol':eol, 'mime':mime, 'test':test} )

def walk_directories(paths, mime=True, eol=True, test=False):
    for path in paths:
        walk_directory(path, mime, eol, test)

if (__name__ == "__main__"):
 
    parser = argparse.ArgumentParser(prog="fix_svn_prop",
                                     description='Fix the svn properties for a given directory (recursive)')

    parser.add_argument('--mime', action="store_true", default=False,
                        help="For known types, set mime-type to appropriate type")
    parser.add_argument('--eol', action="store_true", default=False,
                        help="For known types, set eol-style (line end) to 'native'")
    parser.add_argument('--test', action="store_true", default=False,
                        help="List all transactions that would occur, but do not apply property changes.")

    parser.add_argument('--version', action='version', version='%(prog)s ' + str(VERSION))

    parser.add_argument('path', action="store", nargs='+',
                        help="One or more directories to walk")

    results = parser.parse_args()

    walk_directories(results.path, results.mime, results.eol, results.test)

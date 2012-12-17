#!/usr/bin/env python

VERSION="0.1.0"
DESCRIPTION="Fix the svn properties for a given directory (recursive)."
REQ_PYTHON = (2,7,0)

import sys

if sys.version_info < REQ_PYTHON:
    sys.stderr.write("%s requires python %s or later.\n" % (__file__, ".".join([str(x) for x in REQ_PYTHON])))
    sys.exit(1)

import argparse
import logging

LOG_FORMAT = '%(asctime)-15s %(name)s %(levelname)s: %(message)s'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    level=logging.DEBUG)
log = logging.getLogger("fix_svn_props")

import os.path, subprocess

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

def check_and_correct_property(file_name, property_type, property_ext, test):
    command_get = "svn propget %s %s" % (property_type, file_name)
    output_bytes = subprocess.check_output(command_get, shell=True)
    if not output_bytes:
        return
    output = output_bytes.decode('latin-1')
    output = output.strip()
    # note that default format is text, which is fine for us
    # so only if there's output and it's incorrect do we fix
    if output != property_ext:
        log.info("%s svn:mime-type [ is : should ] [ %s : %s ]" % (file_name, output, property_ext))
        modified = True
        if not test:
            command_set = "svn propset %s '%s' %s" % (property_type, property_ext, file_name)
            subprocess.call(command_set, shell=True)

def fix_svn_properties_for_file(file_name, mime=True, eol=True, test=False):
    base, ext = os.path.splitext(file_name)

    modified = False
    # verify that this file is not:
    # ? outside of version control
    # I being ignored
    command_st = "svn status %s" % file_name
    output_bytes = subprocess.check_output(command_st, shell=True)
    output = output_bytes.decode('latin-1')
    output = output.strip()
    if str(output).startswith("?") or str(output).startswith("I"):
        return

    if mime and ext in MIME.keys():
        check_and_correct_property(file_name, "svn:mime-type", MIME[ext], test)

    if eol and ext in EOL.keys():
        check_and_correct_property(file_name, "svn:eol-style", EOL[ext], test)

    return modified

def walk_directory(path, mime=True, eol=True, test=False):
    log.warn("walking: " + path)
    modified_any = False
    for (root, dir_names, file_names) in os.walk(path):
        if is_ignorable(root):
            continue
        for file_name in file_names:
            complete_path = os.path.join(root, file_name)
            modified = fix_svn_properties_for_file(complete_path, mime, eol, test)
            if not modified_any and modified:
                modified_any = True
    if not test and not modified_any:
        log.info("%s had no files needing repair" % (path))


def walk_directories(paths, mime=True, eol=True, test=False):
    log.warn("--test flag set, reporting only")
    for path in paths:
        if not is_subversion_controlled_dir(path):
            log.error("%s doesn't appear to be a subversion directory" % path)
            continue
        walk_directory(path, mime, eol, test)

if __name__ == "__main__":
 
    parser = argparse.ArgumentParser(prog="fix_svn_props",
                                     description=DESCRIPTION)

    parser.add_argument('--version', action='version', version=VERSION)

    parser.add_argument('--mime', action="store_true", default=False,
                        help="For known types, set mime-type to appropriate type")
    parser.add_argument('--eol', action="store_true", default=False,
                        help="For known types, set eol-style (line end) to 'native'")
    parser.add_argument('--test', action="store_true", default=False,
                        help="List all transactions that would occur, but do not apply property changes.")

    parser.add_argument('paths', action="store", nargs='+',
                        help="One or more directories to walk")

    results = parser.parse_args()

    args = parser.parse_args()
    arguments = vars(args)

    walk_directories(**arguments)

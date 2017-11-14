#!/usr/bin/env python

import argparse
import yaml
from StringIO import StringIO
import os.path

### argument parser

parser = argparse.ArgumentParser(description='YAMKCONF, Yet Another Make Configuration tool: preprocessor for Makefiles decorated with yaml config. A proof of concept implementation in python.')

parser.add_argument('--tab', help='tab width', default = 4, type=int, dest='tab_width')
parser.add_argument('-v', '--verbose', help='increase verbosity', action='count', dest='verbosity')
parser.add_argument('-o', '--output' , help='output file', default='Makefile', dest='output_file')

args = parser.parse_args()

### helper functions

def handle_yaml(yaml_document):
    """
    Converts a yaml document to a generator yielding strings
    denoting Make variable declarations
    """
    for rule in handle_prop(yaml_document):
        yield '.'.join(rule[0]) + ' = ' + rule[1] + '\n'

def handle_prop(prop):
    """
    Converts yaml tree(s) to a generator yielding 2-tuples of:
      * paths from the roots to leafs (leaf exclusive)
      * the leaf itself.
    """
    if type(prop) is str:
        yield ([], prop)
    else:
        for name in prop:
            for rule in handle_prop(prop[name]):
                yield ([name] + rule[0], rule[1])

def auto_fix_tabs(line, n = 4):
	"""
    Replaces soft tabs with hard tabs to prevent Make from choking on them
    """
	if line.startswith(' ' * n):
		return '\t' + auto_fix_tabs(line[n:], n = n)
	else:
		return line

### main processing

with open(args.output_file, 'w') as makefile:
    with open("Makefile.yamk", 'r') as stream:
        try:
            yaml_mode = False
            yaml_document = StringIO()
            for line in stream:
                if line.startswith('---'):
                    yaml_mode = True
                    if args.verbosity > 0:
                        print "<<< yaml on"
                elif line.startswith('...'):
                    yaml_mode = False
                    yaml_content = yaml.load(yaml_document.getvalue())
                    if args.verbosity > 1:
                        print yaml_content
                    for variable_rule in handle_yaml(yaml_content):
                        makefile.write(variable_rule)
                    yaml_document = StringIO()
                    if args.verbosity > 0:
                        print ">>> yaml off"
                elif line.startswith('%INCLUDE '):
                    if not yaml_mode:
                        raise ValueError('%INCLUDE can only be used inside a yaml document')
                    path = line.split('%INCLUDE ')[1].rstrip()
                    with open(path, 'r') as include_stream:
                        for line in include_stream:
                            if line.startswith('---') or line.startswith('...'):
                                # FIXME:
                                # if an included file contains multiple yaml documents, all document separators
                                # will be ignored. This has the advantage that we can just prepend all lines to the
                                # document wherein we include and only a single pass of the yaml parser is necessary
                                # In the future this should be modified to parsing all included documents seperately
                                # first, then convert to text again and prepend to the document wherein they are
                                # included. However, if we do that we lose the remote references...
                                # Maybe just write a custom parser to extract multiple documents in a file, or check
                                # if python yaml allows parsing a multi-document stream without parsing the individual
                                # documents?
                                pass
                            else:
                                yaml_document.write(line)
                    if args.verbosity > 0:
                        print "<<< include " + path + " >>>"
                else:
                    if yaml_mode:
                        yaml_document.write(line)
                    else:
                        makefile.write(auto_fix_tabs(line, args.tab_width))

            print "output written to " + args.output_file
        except yaml.YAMLError as exc:
            print(exc)

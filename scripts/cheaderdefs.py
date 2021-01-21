import argparse
import re
import sys
from collections import Callable


class Patterns(object):
    def __init__(self):
        self.define = re.compile(r'\s*#define\s+([A-Z_][A-Z0-9_]+)\s+(.*)')
        self.value_matchers = [
            (re.compile(r'\(\(DWORD\)0x([0-9a-fA-F]+)L\)'), 'wt.DWORD(0x{})')
        ]

    def convert(self, value):
        comment = None
        comment_index = value.find('//')
        if comment_index > -1:
            comment = value[comment_index+2:]
            value = value[:comment_index].strip()
        if value == 'NO_ERROR':
            value = '0'
        else:
            for expr, formatter in self.value_matchers:
                m = expr.match(value)
                if m:
                    value = m.group(1)
                if isinstance(formatter, str):
                    value = formatter.format(value)
                elif isinstance(formatter, Callable):
                    value = formatter(value)
        return value, comment



def create_parser(prog_name):
    parser = argparse.ArgumentParser(prog=prog_name)
    parser.add_argument('header', metavar='PATH', help='Path to C-header')
    parser.add_argument('--output', '-o', metavar='PATH', help='Path to output file', default=None)
    parser.add_argument('--add-import', '-ai', action='store_true', default=False, help='Add ctypes header')
    return parser


def parse_args(prog_name, args):
    parser = create_parser(prog_name)
    return parser.parse_args(args)


def scan_file(header):
    patterns = Patterns()
    matches = []
    with open(header, 'r') as f:
        for line in f:
            m = patterns.define.match(line)
            if m:
                name = m.group(1)
                value = m.group(2)
                value, comment = patterns.convert(value)
                matches.append((name, value, comment))
    return matches


def produce_output(matches, output=None, add_import=False):
    outfp = open(output, 'w') if output else sys.stdout
    if add_import:
        outfp.write('import ctypes\n')
        outfp.write('from ctypes import wintypes as wt\n')
        outfp.write('\n')
    for name, value, comment in matches:
        if comment:
            outfp.write('{} = {} #{}\n'.format(name, value, comment))
        else:
            outfp.write('{} = {}\n'.format(name, value))
    if output:
        outfp.close()


def main():
    opts = parse_args(sys.argv[0], sys.argv[1:])
    matches = scan_file(opts.header)
    produce_output(matches, opts.output, opts.add_import)


if __name__ == '__main__':
    main()

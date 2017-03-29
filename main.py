#!/usr/bin/python3
#
# The MIT License (MIT)
#
# Copyright (c) 2013 Andrian Nord
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
import io
import traceback

import ljd.rawdump.parser
import ljd.pseudoasm.writer
import ljd.ast.builder
import ljd.ast.validator
import ljd.ast.locals
import ljd.ast.slotworks
import ljd.ast.unwarper
import ljd.ast.mutator
import ljd.lua.writer
import ljd.util.log


def dump(name, obj, level=0):
    indent = level * '\t'

    if name is not None:
        prefix = indent + name + " = "
    else:
        prefix = indent

    if isinstance(obj, (int, float, str)):
        print(prefix + str(obj))
    elif isinstance(obj, list):
        print (prefix + "[")

        for value in obj:
            dump(None, value, level + 1)

        print (indent + "]")
    elif isinstance(obj, dict):
        print (prefix + "{")

        for key, value in obj.items():
            dump(key, value, level + 1)

        print (indent + "}")
    else:
        print (prefix + obj.__class__.__name__)

        for key in dir(obj):
            if key.startswith("__"):
                continue

            val = getattr(obj, key)
            dump(key, val, level + 1)


def decompile(file_in):
    header, prototype = ljd.rawdump.parser.parse(file_in)

    if not prototype:
        return 1

    # TODO: args
    # ljd.pseudoasm.writer.write(sys.stdout, header, prototype)

    ast = ljd.ast.builder.build(prototype)

    assert ast is not None

    ljd.ast.validator.validate(ast, warped=True)

    ljd.ast.mutator.pre_pass(ast)

    # ljd.ast.validator.validate(ast, warped=True)

    ljd.ast.locals.mark_locals(ast)

    # ljd.ast.validator.validate(ast, warped=True)

    try:
        ljd.ast.slotworks.eliminate_temporary(ast)
    except:
        None

    # ljd.ast.validator.validate(ast, warped=True)

    if True:
        ljd.ast.unwarper.unwarp(ast)

        # ljd.ast.validator.validate(ast, warped=False)

        if True:
            ljd.ast.locals.mark_local_definitions(ast)

            # ljd.ast.validator.validate(ast, warped=False)

            ljd.ast.mutator.primary_pass(ast)

            try:
                ljd.ast.validator.validate(ast, warped=False)
            except:
                print("Validate error.", file=sys.stdout)


    # Save file
    if file_in[-5:] == ".luac":
        file_out = file_in[:-5] + ".lua"
    else:
        file_out = file_in + ".lua"

    ljd.lua.writer.write(io.open(file_out, "w"), ast)
    ljd.lua.writer.write(sys.stdout, ast)

    return 0


def main():
    file_ins = sys.argv[1:]
    file_num = len(file_ins)
    files_failed = []

    for file_in in file_ins:
        try:
            decompile(file_in)
        except BaseException as e:
            if file_num == 1:
                print("\n" + "="*10 + file_in + "="*10)
                traceback.print_exc()
            else:
                files_failed.append(file_in)

    if file_num > 1 and len(files_failed) > 0:
        print("="*10 + "\nFailed files: ")
        for f in files_failed:
            print("\t" + f)

        ok = file_num - len(files_failed)
        rate = ok*100.0/file_num
        print("\n" + "="*10)
        print(str(file_num-len(files_failed)) + " of " + str(file_num) + " decompiled(" + str(rate) + "%).")

if __name__ == "__main__":
    retval = main()
    sys.exit(retval)

# vim: ts=8 noexpandtab nosmarttab softtabstop=8 shiftwidth=8

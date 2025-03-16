#!/usr/bin/python3

import re
import argparse
import os

unit_decode = {'M': 6, 'k': 3, '': 0, 'm': -3, 'u': -6, 'n': -9, 'p': -12}

def parse_value(value, resistor=False, micro=False):
    base_unit = -12
    base_text = "pF"
    extra_unit = "f|F"

    if resistor or micro:
        if micro:
            base_unit = -6
            base_text = "uOhm"
        else:
            base_unit = 0
            base_text = "Ohm"
        extra_unit = "Ohm|ohm|R|r|Ω"

    result = re.search(r"^\s*([0-9]+)[,.]?([0-9]*)\s*([Mkmunp]?)\s*(" + extra_unit + r")?\s*$", value)
    if result is None:
        raise ValueError(f"Unable to understand {value} as a value")

    whole = result.groups()[0]
    decimal = result.groups()[1] or ""
    unit = result.groups()[2] or ""
    decimal = decimal.rstrip('0')  # Ignore decimal trailing 0's, whole trailing is handled by the multiplier

    code = whole + decimal
    suffix_zeros = unit_decode[unit] - base_unit - len(decimal)
    if suffix_zeros < 0:
        raise ValueError(f"{value} has a too small part to encode in an integer base of {base_text}")

    suffix_string = "".ljust(suffix_zeros, "0")
    as_base = code + suffix_string
    as_base = as_base.lstrip('0')  # Ignore prefixed zeros

    multiplier = len(as_base) - len(as_base.rstrip('0'))
    if multiplier > 9:
        multiplier = 9

    code = as_base
    if multiplier > 0:
        code = code[0:-multiplier]
    code = code.rjust(3, '0')

    if len(code) > 3:
        stripped_code = code.rstrip('0')
        if len(stripped_code) > 3:
            raise ValueError(f"Too many significant digits in {value}")
        else:
            raise ValueError(f"{value} too large to encode in {base_text}")

    return code, multiplier, as_base, base_text

def main():
    argparser = argparse.ArgumentParser(description='Converts Farads (or Ohm) values into variation codes, outputting the code as the last line of output')
    argparser.add_argument('value', nargs=1, help="value including 'M', 'k', 'm', '',  'u', 'n' and 'p'")
    argparser.add_argument('-r', '--resistor', action='store_true', help="Switches to resistor mode")
    argparser.add_argument('-u', '--micro', action='store_true', help="Switches to resistor mode to micro ohms (for shunts)")

    args = argparser.parse_args()
    value = args.value[0]

    try:
        code, multiplier, as_base, base_text = parse_value(value, args.resistor, args.micro)
        print(f"Read {value} as {as_base + base_text} giving a code of:")
        print(f"{code}{multiplier}")
    except ValueError as e:
        print(e)
        os._exit(1)

if __name__ == "__main__":
    main()


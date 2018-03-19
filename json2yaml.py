#!/usr/bin/env python

import json
import sys
import yaml


def _utf8_encode(obj):
    if obj is None:
        return None
    if type(obj) is unicode:
        return obj.encode('utf-8')
    if type(obj) is list:
        return [_utf8_encode(value) for value in obj]
    if type(obj) is dict:
        obj_dest = {}
        for key, value in obj.iteritems():
            if not 'EXEC' in key:
                obj_dest[_utf8_encode(key)] = _utf8_encode(value)
        return obj_dest
    return obj


def main():
    obj = json.load(sys.stdin)
    utf8_obj = _utf8_encode(obj)
    yaml.dump(utf8_obj, stream=sys.stdout,
              default_flow_style=False, explicit_start=False)


if __name__ == '__main__':
    main()

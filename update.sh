#!/bin/sh

/usr/bin/env python increment.py &&
    /usr/bin/env python make_selection.py &&
    /usr/bin/env python generate.py

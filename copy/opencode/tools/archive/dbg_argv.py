# -*- coding: utf-8 -*-
import sys
print("argv:", sys.argv)
h = [a for a in sys.argv if a.startswith("--home=")]
print("home arg:", h)
if h:
    home = h[0].split("=", 1)[1]
    print("home value:", repr(home))
    print("home len:", len(home))

"""Created on Apr 23, 2013 by @author: lucag@icsi.berkeley.edu
"""

from depparsing import split
split_re = split.splitter('rasp')

def corrections(sentence):
    hole_count = 0
    offsetof = {}
    for i, w in enumerate(sentence):
        offsetof[i + 1] = max(0, i - hole_count)
        hole_count += len(split_re.findall(w)) - 1
    for j in range(hole_count + 1):
        offsetof[i + j + 1] = max(0, i + j - hole_count)
    return offsetof


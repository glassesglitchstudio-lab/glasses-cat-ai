import json, os, re, hashlib, math, random, heapq, sys, itertools
from collections import deque, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'x_fable_coder_dataset.json')

def is_placeholder(out):
    if 'def solution_' in out and 'pass' in out: return True
    if 'class DataStructure' in out and 'pass' in out: return True
    if 'slow_version' in out and 'fast_version' in out and 'process(item)' in out: return True
    if '# HATALI KOD' in out and '# DUZELTILMIS KOD' in out and 'pass' in out: return True
    if 'class CleanSolution' in out and 'self.implementation' in out: return True
    return False

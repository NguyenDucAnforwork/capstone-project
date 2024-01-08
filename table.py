from preprocess import *
import json

with open("moves.json", "r") as file:
    MOVES = json.load(file)

with open("eval.json", "r") as file:
    EVAL = json.load(file)


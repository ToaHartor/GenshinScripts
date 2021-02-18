import argparse
import json
import os

import utils.questlog as questlog

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", type=str, default='EN')

    args = parser.parse_args()

    with open(os.path.join(os.path.dirname(__file__), f'data/TextMap/Text{args.lang}.json')) as textmap_json:
        textmap = json.load(textmap_json)
        # characterAnalyser(textmap)
        # chapter debut ID (example) : 
        questlog.chapterLogger(textmap, 2018, args)

        # quest debug ID for multiple choices ending : 309
        # questlog.questLogger(textmap, 309, args)
# [WIP] GenshinScripts

A collection of scripts to be used with the data from https://github.com/Dimbreath/GenshinData (huge thanks to them btw)

## What does these scripts do

- Quests and chapters logging
- more to come

## Requirements

- Python 3.6+

## How to use it

- Python 3.6+ should be installed
- Download the data from https://github.com/Dimbreath/GenshinData and extract it in a data/ folder at the root of the project.
- The files structure should look like this :
```
GenshinScripts/     (main folder)
|-data/             (from Dimbreath/GenshinData)
| |-Excel/
| | |-_.json
| |  ...
| |-TextMap/
|   |-text_.json
|   ...
|-utils/
| |-_.py
| ...
|-main.py
|-README.md
```
- Now `main.py` can be used with the parameter `--lang EN|FR|JP|....` with the language being formatted like the textmaps in data/
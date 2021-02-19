import json
import os
import itertools
from pathlib import Path

import utils.rewards as rewards

def batchExtractChapters(textmap, args):
    chapterData = json.load(open(os.path.join(os.path.dirname(__file__), f'../data/Excel/ChapterExcelConfigData.json')))
    length = len(chapterData)

    for count, chapter in enumerate(chapterData):
        print(f'Chapter progress : {count+1}/{length} [{chapter["Id"]}]')
        chapterLogger(textmap, chapter['Id'], args)

def batchExtractQuests(textmap, args):
    questData = json.load(open(os.path.join(os.path.dirname(__file__), f'../data/Excel/MainQuestExcelConfigData.json')))
    questData = list(filter(lambda x: x if "ChapterId" not in x else None, questData))
    length = len(questData)

    for count, quest in enumerate(questData):
        print(f'Quest progress : {count+1}/{length} [{quest["Id"]}]')
        questLogger(textmap, quest['Id'], args)


def chapterLogger(textmap, chapterId, args):
    files = {"ChapterExcelConfigData": {},
            "MainQuestExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    chapterQuest = list(filter(lambda d: d['Id'] == chapterId, files["ChapterExcelConfigData"]))

    filePath = os.path.join(f'res/{textmap[str(chapterQuest[0]["ChapterNumTextMapHash"])]} - {args.lang}.txt')
    print(f'File written : {filePath}')
    # These two lines might be used later
    # beginQuest = chapterQuest[0]['BeginQuestId']
    # endQuest = chapterQuest[0]['EndQuestId']
    print(f'{textmap[str(chapterQuest[0]["ChapterNumTextMapHash"])]} [{chapterId}]')
    with open(filePath, 'w') as file:
        file.write(f'{textmap[str(chapterQuest[0]["ChapterNumTextMapHash"])]}\n\n')
        file.write(f'{textmap[str(chapterQuest[0]["ChapterTitleTextMapHash"])]}\n\n')
    
    # Searching for the Chapter ID and associated quests
    mainQuests = list(filter(lambda d: (d['ChapterId'] == chapterId if "ChapterId" in d else None), files["MainQuestExcelConfigData"]))
    mainQuests = sorted(mainQuests, key=lambda i: i['Id'])

    length = len(mainQuests)

    for current, mq in enumerate(mainQuests):
        print(f'Progress : {current+1}/{length}')
        questLogger(textmap, mq['Id'], args, filePath)


def questLogger(textmap, questId, args, filePath=""):
    #MainQuestExcelConfigData.json -> Contains Quest ID
    #TalkExcelConfigData.json  "QuestId" -> Quest ID in MainQuestExcelConfigData.json (Id)
    #                          "InitDialog" -> Beginning dialog ID in DialogExcelConfigData.json (Id)
                                
    #QuestExcelConfigData.json   "MainId" -> Quest ID in MainQuestExcelConfigData.json (Id)
    #                            "SubId" -> Quest part ID in TalkExcelConfigData.json (Id)

    #DialogExcelConfigData.json   Iterate over NextDialogs [], if there's more than one choice, then the traveler is talking

    #MainQuestExcelConfigData (Id)-> QuestExcelConfigData.json (MainId) -> (SubId) orderby "Order" asc -> TalkExcelConfigData.json (Id) -> (InitDialog) -> DialogExcelConfigData.json (Id) -> for text in NextDialogs[] -> empty then next

    # In "TalkRole", if "Type" is "TALK_ROLE_PLAYER" then traveler is talking
    #                else if it's "TALK_ROLE_NPC", then "Id" corresponds to "Id" in NpcExcelConfigData.json (and then you get the NPC name) 

    files = {"MainQuestExcelConfigData": {},
            "QuestExcelConfigData": {},
            "TalkExcelConfigData": {},
            "DialogExcelConfigData": {},
            "NpcExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    mainquest = list(filter(lambda d: d['Id'] == questId, files["MainQuestExcelConfigData"]))

    # Checking if the file already exists. Useful to not overwrite the file for each quest when the function is called in chapterLogger()
    textfile = Path(filePath)
    if textfile.is_file():
        openmode = 'a'
    else:
        filePath = os.path.join(f'res/Quest - {textmap[str(mainquest[0]["TitleTextMapHash"])]} - {args.lang}.txt')
        if Path(filePath).is_file():    # In order to append to the existing file the new version of the quest
            openmode = 'a'
        else:
            openmode = 'w'

    with open(filePath, openmode) as file:

        file.write(f'Main Quest : {textmap[str(mainquest[0]["TitleTextMapHash"])]}\n\n')
        file.write(f'{textmap[str(mainquest[0]["DescTextMapHash"])]}\n\n')
        # Writing rewards
        text = ''
        for r in mainquest[0]["RewardIdList"]:
            text += rewards.rewardsFormatter(textmap, r) + "\n"
        file.write(f'{textmap["276798818"]} : {text}\n' if len(mainquest[0]["RewardIdList"]) > 0 else "\n")

        print(f'Main Quest : {textmap[str(mainquest[0]["TitleTextMapHash"])]} [{mainquest[0]["Id"]}]')

        quest = list(filter(lambda d: d['MainId'] == questId, files["QuestExcelConfigData"]))
        quest = sorted(quest, key=lambda i: i['Order'])

        length = len(quest)

        for subcount, q in enumerate(quest):
            # if q['SubId'] >= beginQuest and q['SubId'] <= endQuest:
            print(f'Objective progress : {subcount+1}/{length} [{q["SubId"]}] ')
            file.write(f'\n--> {textmap[str(q["DescTextMapHash"])]}\n\n')

            talk = list(filter(lambda d: d['Id'] == q['SubId'], files["TalkExcelConfigData"]))
            for t in talk:
                dialog = list(filter(lambda d: (d['Id'] == t['InitDialog'] if 'InitDialog' in t else None), files["DialogExcelConfigData"]))
                for d in dialog:
                    # Putting branchID=[0] explicitely, as using list.append() inside could cause problems
                    dialogManager(textmap, d, files, file, [],  0, [0])
                    
        file.write("\n\n================================\n\n")

def dialogManager(textmap, dialog, files, file, IDList=[], branchLevel=0, branchID=[0], limitID=-1):
    # Just formatting
    leveling = ' '
    for _ in itertools.repeat(None, branchLevel):
        leveling += '---'
    leveling += ' '

    file.write(f'{str(branchID[branchLevel]) + leveling if branchID[branchLevel] > 0 else ""}[{dialog["Id"]}] {characterSearch(dialog, files["NpcExcelConfigData"], textmap)} : {textmap[str(dialog["TalkContentTextMapHash"])]}\n')
    IDList.append(dialog['Id'])
    
    # Bug resolution : infinite recursion for chapterID=2010, when having the same ID in NextDialog than the current dialog
    # This is actually a problem from the Genshin data, the following lines will resolve this
    if dialog['Id'] == 105010427:
        dialog['NextDialogs'] = [105010428,105010429]

    nextDialog = list(filter(lambda f: f['Id'] in list(filter(lambda d: d > dialog['Id'], dialog['NextDialogs'])), files["DialogExcelConfigData"]))

    if len(nextDialog) == 1:
        # When quest text go back to the first question (ex questID=309)
        if dialog["Id"] > nextDialog[0]['Id']:
            return -1
        # If IDs aren't consecutive for the first branch, then the next ID is the end of the branch
        elif nextDialog[0]['Id'] != dialog['Id'] + 1:
            return nextDialog[0]['Id']
        # If we're at the last branch nextDialog ID == limitID, then we're at the end of the branch
        elif branchID[branchLevel] > 0 and nextDialog[0]['Id'] == limitID:
            branchID.pop()
            dialogManager(textmap, nextDialog[0], files, file, IDList, branchLevel-1, branchID)
        # Else we have the normal behaviour
        else:
            return dialogManager(textmap, nextDialog[0], files, file, IDList, branchLevel, branchID, limitID)

    elif len(nextDialog) > 1:
        limitID = -1
        branchID.append(1)
        for i, branch in enumerate(nextDialog):
            if i == 0:  # We get the limit ID
                limitID = dialogManager(textmap, branch, files, file, IDList, branchLevel+1, branchID)
            else:   # And for the others, we stop at the limit ID found
                if branch['Id'] not in IDList:
                    branchID[branchLevel+1] = i+1
                    dialogManager(textmap, branch, files, file, IDList, branchLevel+1, branchID, limitID)
    return -1
        
def characterSearch(dialog, npcexcel, textmap):
    # Bugfix for chapterID=2011; DialogID=111000819 -> missing Type in TalkRole
    if "Type" in dialog["TalkRole"]:
        if dialog["TalkRole"]["Type"] == "TALK_ROLE_PLAYER":
            return textmap["4100208827"]
        elif dialog["TalkRole"]["Type"] == "TALK_ROLE_NPC":
            if dialog["TalkRole"]['Id'] != "":
                npcname = list(filter(lambda d: d['Id'] == int(dialog["TalkRole"]["Id"]), npcexcel))
                return textmap[str(npcname[0]["NameTextMapHash"])]
            return ""
    elif dialog["TalkRole"]["Id"] == "":
        if dialog["Id"] == 111000819:
            return textmap["4100208827"]
    return "" 
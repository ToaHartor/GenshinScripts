import json
import os
from pathlib import Path

def chapterLogger(textmap, chapterId, args):
    files = {"ChapterExcelConfigData": {},
            "MainQuestExcelConfigData": {}}

    for file in files:
        with open(os.path.join(os.path.dirname(__file__), f'../data/Excel/{file}.json')) as json_file:
            files[file] = json.load(json_file)

    chapterQuest = list(filter(lambda d: d['Id'] == chapterId, files["ChapterExcelConfigData"]))

    filePath = os.path.join(f'{textmap[str(chapterQuest[0]["ChapterNumTextMapHash"])]} - {args.lang}.txt')

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

    def characterSearch(dialog, npcexcel, textmap):
        if dialog["TalkRole"]["Type"] == "TALK_ROLE_PLAYER":
            return textmap["4100208827"]
        elif dialog["TalkRole"]["Type"] == "TALK_ROLE_NPC":
            npcname = list(filter(lambda d: d['Id'] == int(dialog["TalkRole"]["Id"]), npcexcel))
            return textmap[str(npcname[0]["NameTextMapHash"])]
        return ""  

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
        filePath = os.path.join(f'Quest - {textmap[str(mainquest[0]["TitleTextMapHash"])]} - {args.lang}.txt')
        openmode = 'w'

    def branchCondition(branch, limitID):
        if limitID == -1:
            return len(branch['NextDialogs']) > 0
        return branch['NextDialogs'][0] != limitID

    with open(filePath, openmode) as file:

        file.write(f'Main Quest : {textmap[str(mainquest[0]["TitleTextMapHash"])]}\n\n')
        file.write(f'{textmap[str(mainquest[0]["DescTextMapHash"])]}\n\n')
        print(f'Main Quest : {textmap[str(mainquest[0]["TitleTextMapHash"])]} [{mainquest[0]["Id"]}]')

        quest = list(filter(lambda d: d['MainId'] == questId, files["QuestExcelConfigData"]))
        quest = sorted(quest, key=lambda i: i['Order'])

        length = len(quest)

        for subcount, q in enumerate(quest):
            # if q['SubId'] >= beginQuest and q['SubId'] <= endQuest:
            print(f'Quest progress : {subcount+1}/{length} [{q["SubId"]}] ')
            file.write(f'\n--> {textmap[str(q["DescTextMapHash"])]}\n\n')

            talk = list(filter(lambda d: d['Id'] == q['SubId'], files["TalkExcelConfigData"]))
            for t in talk:
                dialog = list(filter(lambda d: d['Id'] == t['InitDialog'], files["DialogExcelConfigData"]))
                for d in dialog:
                    file.write(f'[{d["Id"]}] {characterSearch(d, files["NpcExcelConfigData"], textmap)} : {textmap[str(d["TalkContentTextMapHash"])]}\n')
                    nextDialog = list(filter(lambda f: f['Id'] in d['NextDialogs'], files["DialogExcelConfigData"]))
                    while len(nextDialog) > 0:
                        if len(nextDialog) == 1:
                            file.write(f'[{nextDialog[0]["Id"]}] {characterSearch(nextDialog[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(nextDialog[0]["TalkContentTextMapHash"])]}\n')
                            nextDialog = list(filter(lambda f: f['Id'] in nextDialog[0]['NextDialogs'], files["DialogExcelConfigData"]))
                        if len(nextDialog) > 1:
                            # We look for the first non-consecutive Id in the first branch, which would represent the end of the dialog branch, then limit others
                            limitID = -1
                            firstBranch = [nextDialog[0]]

                            file.write(f'1 --- [{firstBranch[0]["Id"]}] {characterSearch(firstBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(firstBranch[0]["TalkContentTextMapHash"])]}\n')
                            while len(firstBranch[0]['NextDialogs']) > 0:
                                if firstBranch[0]['NextDialogs'][0] != firstBranch[0]['Id'] + 1:
                                    break
                                firstBranch = list(filter(lambda f: f['Id'] in firstBranch[0]['NextDialogs'], files["DialogExcelConfigData"]))
                                file.write(f'1 --- [{firstBranch[0]["Id"]}] {characterSearch(firstBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(firstBranch[0]["TalkContentTextMapHash"])]}\n')
                                
                            if len(firstBranch[0]['NextDialogs']) > 0:
                                limitID = firstBranch[0]['NextDialogs'][0] 
                            
                            # Then we filter the others
                            branchID = 2
                            nextDialog.pop(0)
                                
                            for branch in nextDialog:
                                file.write(f'{branchID} --- [{branch["Id"]}] {characterSearch(branch, files["NpcExcelConfigData"], textmap)} : {textmap[str(branch["TalkContentTextMapHash"])]}\n')
                                
                                while branchCondition(branch, limitID):
                                    branch = list(filter(lambda f: f['Id'] in branch['NextDialogs'], files["DialogExcelConfigData"]))[0]
                                    file.write(f'{branchID} --- [{branch["Id"]}] {characterSearch(branch, files["NpcExcelConfigData"], textmap)} : {textmap[str(branch["TalkContentTextMapHash"])]}\n')

                                branchID += 1
                            # Finally, we continue the loop with the end dialog of all branches.
                            nextDialog = list(filter(lambda f: f['Id'] == limitID, files["DialogExcelConfigData"]))
        file.write("\n\n================================\n\n")
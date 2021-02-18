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

    # beginQuest = chapterQuest[0]['BeginQuestId']
    # endQuest = chapterQuest[0]['EndQuestId']

    with open(filePath, 'w') as file:
        # print(f'{textmap[str(chapterQuest[0]["ChapterNumTextMapHash"])]}\n')
        # print(f'{textmap[str(chapterQuest[0]["ChapterTitleTextMapHash"])]}\n')
        file.write(f'{textmap[str(chapterQuest[0]["ChapterNumTextMapHash"])]}\n\n')
        file.write(f'{textmap[str(chapterQuest[0]["ChapterTitleTextMapHash"])]}\n\n')
    
    # Searching for the Chapter ID and associated quests
    mainQuests = list(filter(lambda d: (d['ChapterId'] == chapterId if "ChapterId" in d else None), files["MainQuestExcelConfigData"]))
    mainQuests = sorted(mainQuests, key=lambda i: i['Id'])

    for mq in mainQuests:
        questLogger(textmap, mq['Id'], args, filePath)


def questLogger(textmap, questId, args, filePath=""):

    def characterSearch(dialog, npcexcel, textmap):
        if dialog["TalkRole"]["Type"] == "TALK_ROLE_PLAYER":
            return textmap["4100208827"]
        elif dialog["TalkRole"]["Type"] == "TALK_ROLE_NPC":
            npcname = list(filter(lambda d: d['Id'] == int(dialog["TalkRole"]["Id"]), npcexcel))
            return textmap[str(npcname[0]["NameTextMapHash"])]
        return ""

    #MainQuestExcelConfigData.json   Contient l'Id des quêtes
    #TalkExcelConfigData.json  "QuestId" -> Id de la quête dans MainQuestExcelConfigData.json (Id)
    #                          "InitDialog" -> Id du début du dialogue dans DialogExcelConfigData.json (Id)
                                
    #QuestExcelConfigData.json   "MainId" -> Id de la quête dans MainQuestExcelConfigData.json (Id)
    #                            "SubId" -> Id de la portion de quête dans TalkExcelConfigData.json (Id)

    #DialogExcelConfigData.json   Itérer sur NextDialogs [], si il y a plus d'un choix c'est le traveler qui parle, si il n'y a qu'un élément il n'y a rien
    # Dans "TalkRole", soit le "Type" est "TALK_ROLE_PLAYER" alors c'est un choix du traveler
    # Soit c'est "TALK_ROLE_NPC", dans ce cas il faut regarder "Id", correspondant à "Id" dans NpcExcelConfigData.json


    #MainQuestExcelConfigData (Id)-> QuestExcelConfigData.json (MainId) -> (SubId) orderby "Order" asc -> TalkExcelConfigData.json (Id) -> (InitDialog) -> DialogExcelConfigData.json (Id) -> for text in NextDialogs[] -> vide alors next  

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

        quest = list(filter(lambda d: d['MainId'] == questId, files["QuestExcelConfigData"]))
        quest = sorted(quest, key=lambda i: i['Order'])

        for q in quest:
            # if q['SubId'] >= beginQuest and q['SubId'] <= endQuest:
            # print(f'\n--> {textmap[str(q["DescTextMapHash"])]}\n')
            file.write(f'\n--> {textmap[str(q["DescTextMapHash"])]}\n\n')
            talk = list(filter(lambda d: d['Id'] == q['SubId'], files["TalkExcelConfigData"]))
            for t in talk:
                dialog = list(filter(lambda d: d['Id'] == t['InitDialog'], files["DialogExcelConfigData"]))
                for d in dialog:
                    # print(f'[{d["Id"]}] {characterSearch(d, files["NpcExcelConfigData"], textmap)} : {textmap[str(d["TalkContentTextMapHash"])]}')
                    file.write(f'[{d["Id"]}] {characterSearch(d, files["NpcExcelConfigData"], textmap)} : {textmap[str(d["TalkContentTextMapHash"])]}\n')
                    nextDialog = list(filter(lambda f: f['Id'] in d['NextDialogs'], files["DialogExcelConfigData"]))
                    while len(nextDialog) > 0:
                        if len(nextDialog) == 1:
                            # print(f'[{nextDialog[0]["Id"]}] {characterSearch(nextDialog[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(nextDialog[0]["TalkContentTextMapHash"])]}')
                            file.write(f'[{nextDialog[0]["Id"]}] {characterSearch(nextDialog[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(nextDialog[0]["TalkContentTextMapHash"])]}\n')
                            nextDialog = list(filter(lambda f: f['Id'] in nextDialog[0]['NextDialogs'], files["DialogExcelConfigData"]))
                        if len(nextDialog) > 1:
                            # We look for the first non-consecutive Id in the first branch, which would represent the end of the dialog branch, then limit others
                            limitID = -1
                            firstBranch = [nextDialog[0]]
                            # print(f'1 --- [{firstBranch[0]["Id"]}] {characterSearch(firstBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(firstBranch[0]["TalkContentTextMapHash"])]}')
                            file.write(f'1 --- [{firstBranch[0]["Id"]}] {characterSearch(firstBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(firstBranch[0]["TalkContentTextMapHash"])]}\n')
                            while len(firstBranch[0]['NextDialogs']) > 0:
                                if firstBranch[0]['NextDialogs'][0] != firstBranch[0]['Id'] + 1:
                                    break
                                firstBranch = list(filter(lambda f: f['Id'] in firstBranch[0]['NextDialogs'], files["DialogExcelConfigData"]))
                                # print(f'1 --- [{firstBranch[0]["Id"]}] {characterSearch(firstBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(firstBranch[0]["TalkContentTextMapHash"])]}')
                                file.write(f'1 --- [{firstBranch[0]["Id"]}] {characterSearch(firstBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(firstBranch[0]["TalkContentTextMapHash"])]}\n')
                                
                            if len(firstBranch[0]['NextDialogs']) > 0:
                                limitID = firstBranch[0]['NextDialogs'][0] 
                            
                            # Then we filter the others
                            branchID = 2
                            nextDialog.pop(0)
                                
                            for branch in nextDialog:
                                # print(f'{branchID} --- [{branch["Id"]}] {characterSearch(branch, files["NpcExcelConfigData"], textmap)} : {textmap[str(branch["TalkContentTextMapHash"])]}')
                                file.write(f'{branchID} --- [{branch["Id"]}] {characterSearch(branch, files["NpcExcelConfigData"], textmap)} : {textmap[str(branch["TalkContentTextMapHash"])]}\n')
                                # nextInBranch = list(filter(lambda f: f['Id'] in branch['NextDialogs'], files["DialogExcelConfigData"]))
                                
                                while branchCondition(branch, limitID):
                                    branch = list(filter(lambda f: f['Id'] in branch['NextDialogs'], files["DialogExcelConfigData"]))[0]
                                    file.write(f'{branchID} --- [{branch["Id"]}] {characterSearch(branch, files["NpcExcelConfigData"], textmap)} : {textmap[str(branch["TalkContentTextMapHash"])]}\n')

                                # while nextInBranch[0]['Id'] != limitID:
                                #     # print(f'{branchID} --- [{nextInBranch[0]["Id"]}] {characterSearch(nextInBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(nextInBranch[0]["TalkContentTextMapHash"])]}')
                                #     file.write(f'{branchID} --- [{nextInBranch[0]["Id"]}] {characterSearch(nextInBranch[0], files["NpcExcelConfigData"], textmap)} : {textmap[str(nextInBranch[0]["TalkContentTextMapHash"])]}\n')
                                #     nextInBranch = list(filter(lambda f: f['Id'] in nextInBranch[0]['NextDialogs'], files["DialogExcelConfigData"]))        
                                    
                                branchID += 1
                            # Finally, we continue the loop with the end dialog of all branches.
                            nextDialog = list(filter(lambda f: f['Id'] == limitID, files["DialogExcelConfigData"]))
        # print("\n================================\n")
        file.write("\n\n================================\n\n")
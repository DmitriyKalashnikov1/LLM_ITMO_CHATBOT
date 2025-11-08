import csv
import os
import re


def find_max_number_suffix(folder_path, prefix):

    max_number = None

    for filename in os.listdir(folder_path):
        # Проверяем, что файл начинается с префикса
        if filename.startswith(prefix):
            # Ищем числовое окончание
            match = re.search(rf'^{prefix}(\d+)(?:\..+)?$', filename)
            if match:
                number = int(match.group(1))
                if max_number is None or number > max_number:
                    max_number = number
    if not max_number is None:
        return max_number
    else:
        return 0

class ResultsSaver():
    PATH_TO_SAVEDIR = "./results/"
    DIALOG_FIELDS = ["turn_number", "role", "content", "model_response", "rating"]
    REPORT_FIELDS = ["model_name", "model_parameters", "lecture_title", "lecture_topic",
                     "system_prompt_id", "dialog_id", "overall_rating", "evaluation_notes"]
    PROMPT_FIELDS = ["system_prompt_id", "system_prompt", "description", "version"]

    dialogId = 0

    promptId = 0

    reportName = "report.csv"

    def __init__(self):
        reportPath = self.PATH_TO_SAVEDIR+self.reportName
        if not os.path.exists(reportPath):
            with open(reportPath, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self.REPORT_FIELDS)
                writer.writeheader()
        dms = find_max_number_suffix(self.PATH_TO_SAVEDIR, 'dialog')
        pms = find_max_number_suffix(self.PATH_TO_SAVEDIR, 'prompt')

        pOver = True
        dOver = True

        if (pms == 0):
            self.promptId = pms
            pOver = False
        else:
            self.promptId = pms + 1


        if (dms == 0):
            self.dialogId = dms
            dOver = False
        else:
            self.dialogId = dms + 1

        self.startNewPrompt(increment=False)
        self.startNewDialog(increment=False)
        print("result saver created")


    def startNewDialog(self, increment = True, overwrite=True):
        dPath = self.PATH_TO_SAVEDIR + "dialog" + str(self.dialogId) + ".csv"
        if (overwrite):
            with open(dPath, "w", newline="") as dfile:
                dwriter = csv.DictWriter(dfile, fieldnames=self.DIALOG_FIELDS)
                dwriter.writeheader()

        if(increment):
            self.dialogId += 1

    def startNewPrompt(self, increment = True, overwrite=True):
        pPath = self.PATH_TO_SAVEDIR + "prompt" + str(self.promptId) + ".csv"
        if (overwrite):
            with open(pPath, "w", newline="") as pfile:
                pwriter = csv.DictWriter(pfile, fieldnames=self.PROMPT_FIELDS)
                pwriter.writeheader()

        if increment:
            self.promptId += 1

    def saveDialog(self, messages, ratings):
        dPath = self.PATH_TO_SAVEDIR + "dialog" + str(self.dialogId) + ".csv"
        with open(dPath, "a", newline="") as dfile:
            dwriter = csv.DictWriter(dfile, fieldnames=self.DIALOG_FIELDS)

            for (tn, (message, rate)) in enumerate(zip(messages, ratings)):
                row = {}
                if message["role"] == "user":
                    row["turn_number"] = tn
                    row["role"] = "user"
                    row["content"] = message["content"]
                    row["model_response"] = ""
                    row["rating"] = rate
                else:
                    row["turn_number"] = tn
                    row["role"] = message["role"]
                    row["content"] = ""
                    row["model_response"] = message["content"]
                    row["rating"] = rate
                dwriter.writerow(row)

    def savePrompt(self, prompt ,description, version):
        pPath = self.PATH_TO_SAVEDIR + "prompt" + str(self.promptId) + ".csv"
        with open(pPath, "a", newline="") as pfile:
            pwriter = csv.DictWriter(pfile, fieldnames=self.PROMPT_FIELDS)
            row = {}
            row["system_prompt_id"] = self.promptId
            row["system_prompt"] = prompt
            row["description"] = description
            row["version"] = version
            pwriter.writerow(row)

    def addRowToReport(self, model_name, model_parameters, lecture_title, lecture_topic,
                      overall_rating, evaluation_notes):
        reportPath = self.PATH_TO_SAVEDIR + self.reportName
        with open(reportPath, "a", newline="") as rfile:
            rwriter = csv.DictWriter(rfile, fieldnames=self.REPORT_FIELDS)
            row = {}
            row["model_name"] = model_name
            row["model_parameters"] = model_parameters
            row["lecture_title"] = lecture_title
            row["lecture_topic"] = lecture_topic
            row["system_prompt_id"] = self.promptId
            row["dialog_id"] = self.dialogId
            row["overall_rating"] = overall_rating
            row["evaluation_notes"] = evaluation_notes
            rwriter.writerow(row)


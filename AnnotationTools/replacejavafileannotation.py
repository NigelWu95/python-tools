#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import re
import json
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class JavaFileProcessor:
    """批量处理Java代码文件注释信息"""
    def __init__(self, projectDir, suffix, targetTemplateFile):
        self.projectDir = projectDir
        self.suffix = suffix
        self.targetTemplateFile = targetTemplateFile

    def scanFile(self):
        #扫码项目文件夹下所有的文件
        targetFilesList = []

        for dirPath, dirNames, fileNames in os.walk(self.projectDir):
            for fileName in fileNames:
                if fileName.endswith(self.suffix):
                    targetFilesList.append(os.path.join(dirPath, fileName))
        
        return targetFilesList

    def getFileContent(self, file):
        with open(file, "r") as fp:
            allLines = fp.readlines()

        flag = False
        count = 0
        anotations = []
        codes = []

        for line in allLines:
            if "/**" in line:
                flag = True

            if "*/" in line:
                flag = False
                count += 1

            if flag or count == 1:
                # print line
                anotations.append(line)
            else:
                codes.append(line)

        fileContent = {}
        fileContent['anotations'] = anotations
        fileContent['codes'] = codes

        return fileContent

    def replaceContent(self, fileContent, targetTemplate, packageName):
        template = json.loads(json.dumps(targetTemplate))
        anotations = fileContent['anotations']

        for index in range(len(anotations)):
            line = anotations[index]

            if "*" not in line:
                continue

            if "Package Name" in line:
                anotations[index] = " * Package Name: wechat: " + packageName

            for key in template.keys():
                if key in line:
                    anotations[index] = key + template[key]

        wholeContent = anotations + fileContent['codes']

        return wholeContent

    def templateToJson(self, targetTemplateFile):
        templateJson = {}

        with open(targetTemplateFile, "r") as fp:
            allLines = fp.readlines()
        for line in allLines:
            if ":" in line:
                key = line[0:line.index(":") + 2]
                value = line[line.index(":") + 2:]
                templateJson[key] = value
            elif " " in line[3:]:
                key = line[0:line[3:].index(" ") + 4]
                value = line[line[3:].index(" ") + 4:]
                templateJson[key] = value
            else:
                key = line
                value = ""
                templateJson[key] = value

        return templateJson

    def rewriteFile(self):
        targetTemplate = self.templateToJson(self.targetTemplateFile)
        print targetTemplate

        for file in self.scanFile():
            print file + ":"
            filePath = file.split(os.sep)
            srcMainJavaIndex = filePath.index("java")
            packagePath = filePath[srcMainJavaIndex + 1:-1]
            packageName = ".".join(packagePath) + "\n"

            fileContent = self.getFileContent(file)
            finalContent = self.replaceContent(fileContent, targetTemplate, packageName)

            with open(file, "w+") as fp:
                fp.writelines(finalContent)

            print "OK!"

if __name__ == '__main__':
    # 三个参数依次是项目路径、修改注释的文件后缀、模板文件路径，如：
    # processor = JavaFileProcessor("codedemo", ".java", "annotationtemplate.java")
    processor = JavaFileProcessor(sys.argv[1], sys.argv[2], sys.argv[3])
    processor.rewriteFile()
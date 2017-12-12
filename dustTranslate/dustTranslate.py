import codecs
import argparse
import string
import random
import re
import json
import glob
import os
from tqdm import tqdm
from google.cloud import storage
from google.cloud import translate
from FileParser import PropertiesParser


class Config:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.config = self.loadConfig(config_dir=config_dir)
    
    def loadConfig(self, config_dir):
        with open(config_dir) as config_file:
            config = json.load(config_file)

        return config

class TagHandler:
    def __init__(self, path, filename, dirpath):
        self.dirpath = dirpath[2:].split('/')[2] + '/'
        self.source_lang_filepath = path['source_language'] + self.dirpath + filename + '.properties'
        self.dest_lang_filepath = path['destination_language'] + self.dirpath + filename + '.properties'
        self.langTags_source = PropertiesParser(self.source_lang_filepath).tags
        self.langTags_dest = PropertiesParser(self.dest_lang_filepath).tags

    def randomTagGenerator(self, size=8, chars=string.ascii_uppercase + string.digits):
        """
        Generate random uppercase string
        """ 

        return ''.join(random.choice(chars) for x in range(size))
    
    def randUniqueTag(self, size=8):
        """
        Generate a unique random uppercase string
        """
        notUnique = True
        tag = self.randomTagGenerator(size=size)
        if tag in self.langTags_source:
            while notUnique:
                tag = self.randomTagGenerator()
        else:
            self.langTags_source[tag] = ''
            self.langTags_dest[tag] = ''
            return tag
        
    def insertPhraseTag(self, string, translated_string):
        tag = self.randUniqueTag()
        self.langTags_source[tag] = string 
        self.langTags_dest[tag] = translated_string
        return tag

    def generatePropertiesFile(self):
        with codecs.open(self.source_lang_filepath, 'w', 'utf-8-sig') as file:
            for key, value in self.langTags_source.items():
                line = key + "=" + value + "\n"
                file.write(line)
                
        with codecs.open(self.dest_lang_filepath, 'w', 'utf-8-sig') as file:
            for key, value in self.langTags_dest.items():
                line = key + "=" + value + "\n"
                file.write(line)

class Dust:
    def __init__(self, filepath, _filename, path, dest_lang):
        # Arguments
        self.dest_lang = dest_lang
        self.filepath = filepath
        self._filename = _filename
        self.filename = self._filename[1:]
        self.dirpath = os.path.dirname(filepath)
        self.output_path = path['output_directory']
        
        self.raw = u''
        self.file_lines = []
        self.parseDust(self.filepath)
        
        self.authenticateGoogleCloudTranslateAPI()
        self.translator = translate.Client()
        self.tagHandler = TagHandler(path['properties'], self.filename.split('.')[0], self.dirpath)
        self.translateStrings()
        self.outputHTML()
        self.tagHandler.generatePropertiesFile()

    def authenticateGoogleCloudTranslateAPI(self):
        storage_client = storage.Client()
        buckets = list(storage_client.list_buckets())

    def parseDust(self, filename):
        with open(filename, encoding='utf-8') as file:
            for line in file:
                if "{@useContent" in line:
                    pass
                elif  "{/useContent}" in line:
                    pass
                else:
                    self.raw += line
        
        self.file_lines = self.raw.split("\n")

    def isBlank(self, string):
        if string and string.strip():
            return True
        else:
            return False

    def translateStrings(self):
        script = False
        for i, line in enumerate(tqdm(self.file_lines)):
            # Only matches text enclosed within a pair of HTML tags e.g. <div>Text</div>
            htmlTagPairPattern = re.compile(r"(?P<startTag><[^>]{0,}>)(?P<text>.+)(?P<endTag></[^>]{0,}>)")
            htmlTagPair = re.match(htmlTagPairPattern, line.strip())
            htmlTag = re.match(r"(<[^>]{0,}>)", line.strip())
            dustTag = re.fullmatch(r"{[^@}]+}|\[\[.+\]\]", line.strip())
            langTagPattern = re.compile(r"{@[^/}]+/}")
            langTag = re.search(langTagPattern, line)

           
            # Check line isn't whitespace or enclosed in <script> tag
            if self.isBlank(line) and not script:            
                if htmlTagPair is not None:
                    textWithinTags = htmlTagPair.groupdict()
                    text = textWithinTags['text']

                    if not re.fullmatch(langTagPattern, text.strip()):
                        # Perform translation
                        _translation = self.translator.translate(text, target_language=self.dest_lang)
                        translation = _translation['translatedText']
                        
                        _tag = self.tagHandler.insertPhraseTag(text, translation)
                        tag = "{@message type=\"content\" key=\"" + _tag + "\"/}"
                        
                        replacement = textWithinTags['startTag'] + tag + textWithinTags['endTag']
                        self.file_lines[i] = replacement

                elif "<script>" in line or "<script type=\"text/javascript\">" in line:
                    script = True
                elif htmlTag or dustTag:
                    pass
                elif not langTag:
                    _translation = self.translator.translate(line, target_language=self.dest_lang)
                    translation = _translation['translatedText']
                    _tag = self.tagHandler.insertPhraseTag(line, translation)
                    tag = "{@message type=\"content\" key=\"" + _tag + "\"/}"

                    self.file_lines[i] = tag
            elif "</script>" in line:
                script = False
                

    def outputHTML(self):
        with open(self.output_path + self.filename, 'w') as file:
            file.write("{@useContent bundle=\"" + self.output_path.split('/')[-2] + "/" + self.filename.split('.')[0] + ".properties" + "\"} \n")
            for line in self.file_lines:
                file.write(line)
                file.write("\n")
            file.write("{/useContent}")


class FileHandler:
    def __init__(self, language):
        self.input_files = self.loadFiles()
        self.processFiles(self.input_files, language, Config.config)


    def parseFileList(self):
        for entry in Config.config['input_files']:
            self.input_files.append(entry)

    def loadFiles(self):
        files = glob.glob(Config.config['input_directory'])
        for i, file in enumerate(files):
            files[i] = file.replace("\\", '/')
        return files

    def processFiles(self, file_list, language, path):
        for filepath in tqdm(file_list):
            print(filepath)
            _filename = os.path.basename(filepath)
            dustFile = Dust(filepath, _filename, path, language)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTML parser")
    parser.add_argument('language', type=str, help="Language")
    args = parser.parse_args()
    
    Config = Config(config_dir='./tasks/config.json')

    fileHandler = FileHandler(args.language)

import argparse
import configparser
import time
import constants.constants as ct
from constants.subparsers import SUBPARSERS
from fcr.train_set_fcr import create_train_set_fcr
from fcr.train_fcr import train_model_fcr
from fcr.test_fcr import test_model_fcr
from enhance.alto_improve import improve_alto
from ocr.pipe.apply import apply_on_images

# reads config.ini to change some constants
def read_config():

    configP = configparser.RawConfigParser() 
    configP.read(ct.CONFIG_PATH)

    section = "important config"
    ct.DEVICE = configP.get(section, "device")
    ct.FONTS = configP.get(section, "font_classes").split(",")
    supported_langs = set()
    for supported_lang in configP.get(section, "supported_languages").split(","):
        supported_langs.add(supported_lang)
    ct.SUPPORTED_LANGS = supported_langs

    section = "ocr config"
    whitelist= set()
    for c in configP.get(section, "whitelist"):
        whitelist.add(c)
    ct.WHITE_LIST = whitelist
    final = list()
    for pattern in configP.get(section, "target_types").split(","):
        final.append(pattern.split("->"))
    ct.BLOCK_TYPES_ALTO = final
    ct.MIN_YEAR = int(configP.get(section, "min_year"))
    ct.MAX_YEAR = int(configP.get(section, "max_year"))
    for vowel in configP.get(section, "vowels"):
        ct.VOWELS.add(vowel.lower())

    section = "language recognition config"
    ct.STOP_WORDS_THRESH = float(configP.get(section, "stop_words_thresh"))
    if ct.STOP_WORDS_THRESH != -1:
        stop_words = dict()
        for lang in ct.SUPPORTED_LANGS:
            stop_words[lang] = set()
            for stop_word in configP.get(section, lang+"_stop_words").split(","):
                if stop_word != "":
                    stop_words[lang].add(stop_word)
        ct.STOP_WORDS = stop_words

    section = "segmenter config"
    ct.P1 = int(configP.get(section, "p1"))
    ct.P2 = int(configP.get(section, "p2"))
    ct.P3 = int(configP.get(section, "p3"))
    ct.P4 = int(configP.get(section, "p4"))
    ct.P5 = int(configP.get(section, "p5"))
    ct.P6 = int(configP.get(section, "p6"))
    ct.P7 = float(configP.get(section, "p7"))
    ct.P8 = int(configP.get(section, "p8"))

#enhance action
def enhance(args):
    improve_alto(args.directory, args.required)

############################## start ##############################
print("\nStarting OCR Enhancement \n")
time.sleep(0.5)
parser_desc = "OCR Enhancement Command Line Tool"
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=parser_desc)
subs = parser.add_subparsers(help='sub-command help')

# setting up all actions stored in constants.subparsers
for subparser in SUBPARSERS:
    sub = subs.add_parser(subparser)
    for arg in SUBPARSERS[subparser]['args']:
        if arg[5] != 'store_true':
            sub.add_argument(arg[0], arg[1], required=arg[2], default=arg[3], type=arg[4], action=arg[5], help=arg[6])
        else:
            sub.add_argument(arg[0], arg[1], required=arg[2], default=arg[3], action=arg[5], help=arg[6])
    sub.set_defaults(func=eval(SUBPARSERS[subparser]['func']))

# parse action and options
if __name__ == '__main__':

    read_config()
    args = parser.parse_args()

    # Print the processed arguments
    print("Processed Arguments:")
    for arg, value in vars(args).items():
        print(f"{arg}: {value}")
            
    args.func(args)
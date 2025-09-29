import pyperclip
import pyautogui as pya
import time

from platform_utils import primary_modifier_key, supports_alt_tab


def funky(text):
    #split_text = [i for i in text]
    #split_text = cap_first_letter(split_text)

    return cap_sentences(text)


def cap_sentences(lst):
    #sentences = "".join(lst).split(".")
    sentences = lst.split(".")
    new_lst = []

    for sentence in sentences:
        split_sentence = [i for i in sentence]
        print(f"Sentence: {sentence} - Split: {split_sentence}")
        new_lst.append("".join(cap_first_letter(split_sentence)))
        
    print(f"new list -1 : {new_lst[-1]}")
        
    

    return cap_special(".".join(new_lst).strip())


def cap_special(text):
    print(text)
    split = [i for i in text]
    fin = []
    caps =False
    
    for char in split:
        print(char)
        if char in ['\t','\n','\r']:
            fin.append(char)
            caps = True
        else:
            if caps is True:
                try:
                    fin.append(char.upper())
                    caps = False
                except:
                    fin.append(char)
                
            else:
                fin.append(char)    
                    
    return "".join(fin).strip()
            

def cap_first_letter(lst):
    fin_list = []
    symbols = ["!", "?"]
    caps = True

    for index, char in enumerate(lst):

        if char == " ":
            fin_list.append(char)

        elif char in symbols:
            fin_list.append(char)
            caps = True

        elif char.isalpha() is True and caps == True:
            fin_list.append(char.upper())
            caps = False


        elif char.isalpha() is True:

            if(char.lower() == "i" and fin_list[-1] == " " and lst[index+1] == " "):
                fin_list.append(char.upper())
                print(f"CHAR I - {char}")


            elif(char.lower() == "i" and lst[index+1] in ["’","'"] and index != len(lst)):
                fin_list.append(char.upper())
                print(f"CHAR with apostrophe {char}")
                

            else:
                fin_list.append(char.lower())


        else:
            fin_list.append(char.lower())

    return fin_list


MODIFIER_KEY = primary_modifier_key()


def _maybe_switch_window():
    if supports_alt_tab():
        pya.hotkey('alt', 'tab')
        time.sleep(.01)


def _copy_selection():
    pyperclip.copy("")
    pya.hotkey(MODIFIER_KEY, 'c')
    time.sleep(.01)


def _paste_selection():
    pya.hotkey(MODIFIER_KEY, 'v')
    time.sleep(.01)


def upper_case():
    _maybe_switch_window()
    _copy_selection()
    pyperclip.copy(pyperclip.paste().upper())
    _paste_selection()
    time.sleep(.01)
    print("Upper ran")


def lower_case():
    _maybe_switch_window()
    _copy_selection()
    pyperclip.copy(pyperclip.paste().lower())
    _paste_selection()
    time.sleep(.01)


def title_case():
    _maybe_switch_window()
    _copy_selection()
    pyperclip.copy(pyperclip.paste().title())
    _paste_selection()
    time.sleep(.01)


def funky_case():
    _maybe_switch_window()
    _copy_selection()
    text = funky(pyperclip.paste().upper())
    pyperclip.copy(text)
    _paste_selection()
    time.sleep(.01)

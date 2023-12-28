import hashlib
import os
import glob
import pathlib
import datetime
import time
from pynput import keyboard

from tkinter import *
import tkinter.font as font
from tkinter.filedialog import askdirectory


baselines = pathlib.Path.home() / 'Desktop/baselines'

baseline_path = ''

files_changed = []
files_added = []
files_removed = []
files_all = []

log_file = open("logs.txt", "a")

def calculate_data_hash(filename):
    # Created array to store the files within the directory
    # files = {}
    # For loop goes through each file in the directory and provides a hash value
    # for file in [item for item in os.listdir('.') if os.path.isfile(item)]:
        # CHANGE HASH TO THE FOLLOWING:
        # = hashlib.sha256()

    hash_value = hashlib.sha1()
    with open(filename, 'rb') as f:
        chunk = 0
        while chunk != b'':
            chunk = f.read(1024)
            hash_value.update(chunk)
        return hash_value.hexdigest()

def calculate_name_hash(filename):
    hash_val = hashlib.sha1()
    hash_val.update(filename.encode())
    return hash_val.hexdigest()

def UpdateBaseline(dir, mode):
    if dir == "":
        message_folder_label.configure(text="Error: Folder not selected")

    elif os.path.isdir(baselines) == False:
        message_folder_label.configure(text="Baselines Folder doesn't exists, so creating it")
        os.makedirs(baselines)

        username = os.environ.get('USERNAME')
        current_datetime = datetime.datetime.now()
        string_logging = str(username) + " " + str(current_datetime)
        log_actions.set("Log: " + string_logging + "\n\tBaselines Folder Created:\n\tfor Dir: " + dir)
        print(log_actions.get())
        log_file.write("Log: " + string_logging + "\n\tBaselines Folder Created\n\tfor Dir: " + dir + '\n')

        message_folder_label.configure(text="Updating Baseline...")
        UpdateBaselineHelper(dir, mode)
        message_folder_label.configure(text="Updated Baseline Successfully")

    else:
        message_folder_label.configure(text="Updating Baseline...")

        username = os.environ.get('USERNAME')
        current_datetime = datetime.datetime.now()
        string_logging = str(username) + " " + str(current_datetime)
        log_actions.set("Log: " + string_logging + "\n\tBaseline Updated:\n\tfor Dir: " + dir)
        print(log_actions.get())
        log_file.write("Log: " + string_logging + "\n\tBaseline Updated\n\tfor Dir: " + dir + '\n')

        UpdateBaselineHelper(dir, mode)
        message_folder_label.configure(text="Updated Baseline Successfully")

def UpdateBaselineHelper(dir, mode):
    global name_hash, baseline_path
    if (mode == 'w'):
        name_hash = calculate_name_hash(dir)
        baseline_path = os.path.join(baselines, (name_hash + '.txt'))

        print("\tin Dir: " + baseline_path)
        log_file.write("\tin Dir: " + baseline_path + '\n')

    files = [os.path.abspath(f) for f in glob.glob(os.path.join(dir, '*')) if os.path.isfile(f)]
    with open(baseline_path, mode) as baseline:
        for f in files:
            hash = calculate_data_hash(os.path.join(dir, f))
            baseline.write(f)
            baseline.write("=")
            baseline.write(str(hash))
            baseline.write("\n")

    directories = [d for d in glob.glob(os.path.join(dir, '*')) if os.path.isdir(d)]
    for d in directories:
        UpdateBaselineHelper(d, 'a')

def getKeyHashesFromBaseline():
    global name_hash, baseline_path
    dict = {}

    with open(baseline_path, 'r') as baseline:
        for line in baseline:
            key, value = line.split('=')
            dict[key] = value[:-1]
    return dict

def ClearData():
    files_changed.clear()
    files_added.clear()
    files_removed.clear()
    files_all.clear()

    fm.configure(text="")
    fa.configure(text="")
    fr.configure(text="")

def CheckIntegrity(dir, number):
    ClearData()  # Clear data in all 4 lists

    if dir == "":
        message_folder_label.configure(text="Error: Folder not selected")

    else:
        CheckIntegrityHelper(dir, number)
        fm.configure(text='\n'.join(files_changed))
        fa.configure(text='\n'.join(files_added))
        fr.configure(text='\n'.join(files_removed))
        # message_folder_label.configure(text="Integrity Checked Successfully")

def CheckIntegrityHelper(dir, number):
    global name_hash, baseline_path

    if (number):
        name_hash = calculate_name_hash(dir)
        baseline_path = os.path.join(baselines, (name_hash + '.txt'))
        try:
            with open(baseline_path, 'r') as baseline:
                random = 99  # dummy code to handle an error
        except IOError:
            message_folder_label.configure(text='Error: Baseline file for specified folder not present')
            return

    files = [os.path.abspath(f) for f in glob.glob(os.path.join(dir, '*')) if os.path.isfile(f)]
    for x in files:
        files_all.append(x)
    dict = getKeyHashesFromBaseline()

    username = os.environ.get('USERNAME')
    current_datetime = datetime.datetime.now()
    string_logging = str(username) + " " + str(current_datetime)
    log_actions.set("Log: " + string_logging + "\n\tIntegrity Checked" + "\n\tfor Dir: " + dir)
    print(log_actions.get())
    log_file.write("Log: " + string_logging + "\n\tIntegrity Checked with the following result ->" + "\n\tfor Dir: " + dir + '\n')

    for f in files:
        # Checking for changed files
        temp_hash = calculate_data_hash(os.path.join(dir, f))
        if str(os.path.join(dir, f)) in dict.keys() and temp_hash != dict[f]:
            log_file.write('\tFiles were Modified\n')
            files_changed.append(os.path.abspath(f).replace(os.path.abspath(folder), "."))

        # Checking for added files
        if str(os.path.join(dir, f)) not in dict.keys():
            log_file.write('\tFiles were Added\n')
            files_added.append(os.path.abspath(f).replace(os.path.abspath(folder), "."))
    directories = [d for d in glob.glob(os.path.join(dir, '*')) if os.path.isdir(d)]
    for d in directories:
        CheckIntegrityHelper(d, 0)

    if number == 1:
        # checking for removed files
        for x in list(dict.keys()):
            if x not in files_all:
                log_file.write('\tFiles were Removed\n')
                files_removed.append(os.path.abspath(x).replace(os.path.abspath(folder), "."))
    message_folder_label.configure(text="Integrity Checked Successfully")

def open_file():
    global folder
    folder = askdirectory(parent=main_screen, title="Upload File")
    if folder:
        message_folder_label.configure(text="Folder Uploaded Successfully")
        selected_folder_label.config(text=folder)

        username = os.environ.get('USERNAME')
        current_datetime = datetime.datetime.now()
        string_logging = str(username) + " " + str(current_datetime)

        log_actions.set("Log: " + string_logging + "\n\tFolder Selected: " + folder)
        print(log_actions.get())
        log_file.write("Log: " + string_logging + "\n\tFolder Selected: " + folder + '\n')
        ClearData()
main_screen = Tk()
main_screen.geometry("600x650")
main_screen.iconbitmap("C:\\Users\\jeyes\\OneDrive\\Documents\\DESIGN-PROJECT\\File-Boss\\logo.ico")
main_screen['background']='#232621'
main_screen.title("File Boss")

username = os.environ.get('USERNAME')
current_datetime = datetime.datetime.now()
string_logging = str(username) + " " + str(current_datetime)

global log_actions
log_actions = StringVar()
log_actions.set("Log: " + string_logging + "\n\tApplication Booted")
print(log_actions.get())
log_file.write("Log: " + string_logging + "\n\tApplication Booted" + '\n')
# FOR BUTTONS:
brwseBtnFont = font.Font(family='Arial', size=10, weight='bold')
btnFont = font.Font(family='Arial', size=15, weight='bold')
btn_bg_clr = "#674ea7"
btn_hover_clr = "#8fce00"

# FOR LABELS:
fileUpldFont = ("Arial", 10)
label_font = ("Arial", 14)
label_fg_clr = "#ffffff"
label_bg_clr = "#232621"
error_label_clr = "#red"

folder = ""


changes_made_label = Label(main_screen, text="Select a folder:", wraplength=500, bg = label_bg_clr, font=label_font,fg= label_fg_clr,)
changes_made_label.place(relx=0.3, y=37, anchor='center')

browse_btn = Button(text="Click to Browse", font=brwseBtnFont,fg=label_fg_clr, height="2", width="15", bg=btn_bg_clr, command=open_file)
browse_btn.place(relx=0.7, y=40, anchor='center')

selected_folder_label = Label(main_screen, text="", wraplength=500, bg=label_bg_clr, font=label_font, fg="white",)
selected_folder_label.place(relx=0.5, y=125, anchor='center')

message_folder_label = Label(main_screen, text="", wraplength=500, bg=label_bg_clr, font=fileUpldFont, fg="green")
#message appears under click to browse button
message_folder_label.place(relx=0.7, y=80, anchor='center')

update_baseline_btn = Button(text="Update Baseline", font=btnFont, height="2", width="20", fg=label_fg_clr, bg=btn_bg_clr, command=lambda:UpdateBaseline(folder,'w'))
update_baseline_btn.place(relx=0.50, y=200, anchor='center')

check_integrity_btn = Button(text="Check File Integrity", font=btnFont, height="2", width="20", fg=label_fg_clr, bg=btn_bg_clr, command=lambda:CheckIntegrity(folder,1))
check_integrity_btn.place(relx=0.50, y=275, anchor='center')

''' -------------------------------------------- '''

fm_label = Label(main_screen, text="Files Modified:", wraplength=500, bg=label_bg_clr, font=label_font, fg=label_fg_clr)
fm_label.place(relx=0.2, y=400, anchor='center')

fm = Label(main_screen, text="", wraplength=500, bg=label_bg_clr, font=label_font, fg="white")
fm.place(relx=0.6, y=400, anchor='center')

fa_label = Label(main_screen, text="Files Added:", wraplength=500, bg=label_bg_clr, font=label_font, fg=label_fg_clr)
fa_label.place(relx=0.2, y=475, anchor='center')

fa = Label(main_screen, text="", wraplength=500, bg=label_bg_clr, font=label_font, fg="white")
fa.place(relx=0.6, y=475, anchor='center')

fr_label = Label(main_screen, text="Files Removed:", wraplength=500, bg=label_bg_clr, font=label_font, fg=label_fg_clr)
fr_label.place(relx=0.2, y=550, anchor='center')

fr = Label(main_screen, text="", wraplength=500, bg=label_bg_clr, font=label_font, fg="white")
fr.place(relx=0.6, y=550, anchor='center')

main_screen.mainloop()
'''
--------------------- END OF GUI ---------------------------
'''

''' 
Code below checks for any changes made after selecting a 
folder in the Integrity Checker Application using keyboard.Listener()
Press space key to end program

Note: This part of the program does not show changes made to files within subfolders but can detect changes
made within folders to an extent. For instance, adding or removing an item within the subfolder
will let you know that the subfolder has been modified.
'''
global stamp
global cached_stamp
global count

cached_stamp = 0
count = 0

'''
os.path.getmtime() method  is used to get the time(in seconds) of last modification 
of the specified path. 

The dict() function creates a dictionary.
'''
def files_to_timestamp(path):
    files = [os.path.join(path, f) for f in os.listdir(path)]
    return dict([(f, os.path.getmtime(f)) for f in files])

break_program = False
def on_press(key):
    global break_program
    # print(key)
    if key == keyboard.Key.space:
        print('------Program Terminated------')
        break_program = True
        return False

print("Application Closed")
username = os.environ.get('USERNAME')
current_datetime = datetime.datetime.now()
string_logging = str(username) + " " + str(current_datetime)
log_file.write("Log: " + string_logging + '\n\tApplication Closed\n')
print('------Program Started------')
print('Watching {} for changes...'.format(folder))

with keyboard.Listener(on_press=on_press) as listener:
    while break_program == False:
        '''
        folder comes from open_file() method [browsing]
        '''
        path_to_watch = folder
        print('program running...\t (press SPACE to TERMINATE) ')

        '''
        checks for subfolders
        '''
        directories = [d for d in glob.glob(os.path.join(folder, '*')) if os.path.isdir(d)]
        for d in directories:
            path_to_watch = d

        before = files_to_timestamp(path_to_watch)
        time.sleep(4)
        after = files_to_timestamp(path_to_watch)

        added = [f for f in after.keys() if not f in before.keys()]
        removed = [f for f in before.keys() if not f in after.keys()]
        modified = []

        for f in before.keys():
            if not f in removed:
                if os.path.getmtime(f) != before.get(f):
                    modified.append(f)

        if added:
            username = os.environ.get('USERNAME')
            current_datetime = datetime.datetime.now()
            string_logging = str(username) + " " + str(current_datetime)
            print('Item Added: {}'.format(', '.join(added)))
            log_file.write('Log: ' + string_logging + '\n\tItem Added: {}'.format(', '.join(added)) + '\n')
        if removed:
            username = os.environ.get('USERNAME')
            current_datetime = datetime.datetime.now()
            string_logging = str(username) + " " + str(current_datetime)
            print('Item Removed: {}'.format(', '.join(removed)))
            log_file.write('Log: ' + string_logging + '\n\tItem Removed: {}'.format(', '.join(removed)) + '\n')
        if modified:
            username = os.environ.get('USERNAME')
            current_datetime = datetime.datetime.now()
            string_logging = str(username) + " " + str(current_datetime)
            print('Item Modified: {}'.format(', '.join(modified)))
            log_file.write( 'Log: ' + string_logging + '\n\tItem Modified: {}'.format(', '.join(modified)) + '\n')
        before = after
    listener.join()
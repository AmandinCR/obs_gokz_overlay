import ftplib
import time
import os
import glob
import re
import hashlib
from obswebsocket import obsws, requests



# FTP Server Details
FTP_HOST = "example.server.net"
FTP_USER = "example_username"
FTP_PASS = "example_password"
FILE_PATH = "amandin.txt"
LOCAL_FILE = "amandin.txt"

# OBS Details
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASS = "amandinsucks"

# global variables
download_rate = 10 # in seconds
max_name_length = 12 # max characters of name displayed
vnl_time = 600 # in seconds
kzt_time = 300 # in seconds



def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{seconds:05.2f}"

def analyze_file():
    # read the file and store in data structure
    player_times = []
    map_text = ""
    started = ""
    with open(LOCAL_FILE, "r") as f:
        linecounter = 0
        for line in f:
            words = line.split()
            if linecounter == 0:
                # check if we should start the timer
                if words[0] == "0":
                    return True
            elif linecounter == 1:
                map_text = words[0]
            else:
                player_times.append((words[0][:max_name_length],float(words[1])))
            linecounter += 1
    
    # sort the player times and remove slower times
    fastest_times = {}
    for name, time in player_times:
        if name not in fastest_times or time < fastest_times[name]:
            fastest_times[name] = time
    filtered_times = [(name, time) for name, time in player_times if time == fastest_times[name]]
    filtered_times.sort(key=lambda x: x[1])
    
    # send player times to files
    update_player_text(filtered_times)
    
    print("file updated!")
    return False

def update_mode_text(kz_mode):
    with open("mode.txt", "w") as file:
        file.write(kz_mode.upper())

def update_group_text(group_id):
    with open("group.txt", "w") as file:
        file.write("GROUP " + group_id.upper())

def update_player_text(filtered_times):
    with open("player.txt", "w") as file:
        count = 1
        for name,time in filtered_times:
            spaces = " " * (max_name_length - len(name) + 2)
            formatted_time = format_time(time)
            text = str(count) + "  " + name + spaces + formatted_time + "\n"
            file.write(text)
            count += 1

def reset_files():
    # clear all player time text files 
    for file_name in glob.glob("player*.txt"):
        with open(file_name, "w") as file:
            file.write("")
   
    with open("map_name.txt", "w") as file:
        file.write("")
    
    with open("mode.txt", "w") as file:
        file.write("")
    
    with open("group.txt", "w") as file:
        file.write("")

    print("cleared the files!")

def fetch_file(ftp):
    try:
        with open(LOCAL_FILE, "wb") as f:
            ftp.retrbinary(f"RETR {FILE_PATH}", f.write)
        print(f".")
    except Exception as e:
        print(f"Error: {e}")

def send_whitelist(ftp, group_id, kz_mode):
    try:
        local_filename = "group" + group_id + "_" + kz_mode + "/whitelist.txt"
        print(local_filename)
        with open(local_filename, "rb") as f:
            ftp.storbinary(f"STOR {WHITELIST_PATH}", f)
        print(f"whitelist updated sucessfully.")
    except Exception as e:
        print(f"Error: {e}")

def get_file_hash():
    try:
        with open(LOCAL_FILE, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None



if __name__ == "__main__":
    # get group number and kz mode
    kz_mode = input("enter kz mode (kzt, vnl): ")
    group_id = input("enter group letter (a, b, c, etc...): ")
    
    # remove old data
    reset_files()

    # connect to obs
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASS)
    ws.connect()

    # hide obs countdown 
    response = ws.call(requests.GetSceneItemId(sceneName="game", sourceName="clocktext"))
    clock_id = response.datain["sceneItemId"]
    ws.call(requests.SetSceneItemEnabled(sceneName="game", sceneItemId=clock_id, sceneItemEnabled=False))
    started_clock = False

    try:
        # open an ftp connection
        with ftplib.FTP(FTP_HOST) as ftp:
            # use ftp credentials to log in
            ftp.login(FTP_USER, FTP_PASS)
            
            # update group/mode text
            update_group_text(group_id)
            update_mode_text(kz_mode)
            
            # every 10 seconds, update the file and update obs text files
            fetch_file(ftp)
            warmup = analyze_file()
            time.sleep(download_rate)
            
            last_hash = get_file_hash()
            start_time = time.time()
            max_time = 0
            if kz_mode == "vnl": max_time = vnl_time
            elif kz_mode == "kzt": max_time = kzt_time

            while time.time() - start_time < max_time:
                fetch_file(ftp)
                current_hash = get_file_hash()
                if current_hash and current_hash != last_hash:
                    warmup = analyze_file()
                    last_hash = current_hash
                    if (not started_clock) and (not warmup):
                        # show obs countdown
                        ws.call(requests.SetSceneItemEnabled(sceneName="game", sceneItemId=clock_id, sceneItemEnabled=True))
                        started_clock = True
            
                time.sleep(download_rate)

    except Exception as e:
        print(f"Connection Error: {e}")
    
    # close obs connection
    ws.disconnect()







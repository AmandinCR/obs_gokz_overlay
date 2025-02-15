import ftplib
import time
import os
import glob
import re
import hashlib

# FTP Server Details
FTP_HOST_NA = "example.example.net"
FTP_USER_NA = "example"
FTP_PASS_NA = "example"

FTP_HOST_EU = "example.example.net"
FTP_USER_EU = "example"
FTP_PASS_EU = "example"

FILE_PATH = "amandin.txt"
LOCAL_FILE = "amandin.txt"

# global variables
download_rate = 10 # in seconds
max_name_length = 12 # max characters of name displayed


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
        tmp_name = ""
        for line in f:
            words = line.split()
            if linecounter == 0:
                print("idk")
            elif linecounter == 1:
                map_text = words[0] + "\n" + (" "*50)
            elif linecounter % 2 == 0:
                tmp_name = words[0][:max_name_length]
            elif linecounter % 2 == 1:
                player_times.append((tmp_name,float(words[0])))
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

    # update map text
    update_map_text(map_text)
    
    print("file updated!")

def update_map_text(map_name):
    with open("map_name.txt", "w") as file:
        file.write(map_name)

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

def get_file_hash():
    try:
        with open(LOCAL_FILE, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def update_data(ftp):
    fetch_file(ftp)
    analyze_file()
    time.sleep(download_rate)
    
    last_hash = get_file_hash()
    
    while True:
        fetch_file(ftp)
        current_hash = get_file_hash()
        if current_hash and current_hash != last_hash:
            analyze_file()
            last_hash = current_hash
        time.sleep(download_rate)



if __name__ == "__main__":
    # get group number and kz mode
    kz_mode = input("enter kz mode (kzt, vnl): ")
    group_id = input("enter group letter (a, b, c, etc...): ")
    server = input("enter server (na, eu): ")
    
    # remove old data
    reset_files()
    
    # update group/mode text
    update_group_text(group_id)
    update_mode_text(kz_mode)

    try:
        # open an ftp connection
        if server == "na":
            with ftplib.FTP(FTP_HOST_NA) as ftp:
                # use ftp credentials to log in
                ftp.login(FTP_USER_NA, FTP_PASS_NA)
                
                # every few seconds, update the file and update obs text files
                update_data(ftp)

        elif server == "eu":
            with ftplib.FTP(FTP_HOST_EU) as ftp:
                # use ftp credentials to log in
                ftp.login(FTP_USER_EU, FTP_PASS_EU)
                
                # every few seconds, update the file and update obs text files
                update_data(ftp)
    except Exception as e:
        print(f"Connection Error: {e}")
    






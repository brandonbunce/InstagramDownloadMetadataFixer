from PIL import Image
from html.parser import HTMLParser
import time
import fnmatch
import os
from collections import Counter
import shutil
import magic
from pymediainfo import MediaInfo
import tkinter as tk
import tkinter.filedialog
import hashlib
from pathlib import Path

print("Starting InstagramDownloadMetadataFixer by Brandon Bunce")

def tk_update_status(string_input):
    tk_status = tk.Label(master = tk_root, text = string_input)
    tk_status.pack()
    tk_root.update()

def idmf_check_working_directory():
    # Make sure our working directory is set up.
    if not os.path.exists("output/photos"):
        os.makedirs("output/photos")
    if not os.path.exists("output/video"):
        os.makedirs("output/video")
    if not os.path.exists("output/audio"):
        os.makedirs("output/audio")

def idmf_delete_duplicates(target_dir):
    # Listing out all the files
    list_of_files = os.walk(target_dir)
  
    # In order to detect the duplicate files, define an empty dictionary.
    unique_files = dict()

    total_space_saved_in_bytes = 0
  
    for root, folders, files in list_of_files:
        for file in files:
            file_path = Path(os.path.join(root, file))
            # Converting all the content of our file into an md5 hash.
            Hash_file = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            if Hash_file not in unique_files:
                unique_files[Hash_file] = file_path
            else:
                # If the hash already exists, compare file sizes to ensure they are identical
                existing_file_path = unique_files[Hash_file]
                if os.path.getsize(file_path) == os.path.getsize(existing_file_path):
                    os.remove(file_path)
                    print(f"{file_path} has been deleted as a duplicate of {existing_file_path}")
                    duplicate_stats = os.stat(existing_file_path)
                    total_space_saved_in_bytes += duplicate_stats.st_size

                else:
                    print(f"{file_path} has the same hash but different size, not deleting.")
    print("Successfully removed duplicates, saving "+str(total_space_saved_in_bytes)+" bytes of data.")

def idmf_save_media(html_file_name, target_dir, image_list, dates_list):
    print("Saving media from "+str(html_file_name))
    for i in range(len(image_list)):
            if os.path.exists("source/"+image_list[i]):
                # For whatever reason, Instagram will randomly store media without a file extension,
                # so, we must determine the file type before we pass it to other libraries.
                file_type = magic.from_file("source/"+image_list[i], mime=True)
                #print(str(i)+ " - " +str(file_type) +" - "+str(media_links[i]))
                if file_type == "image/jpeg":
                    image = Image.open("source/"+image_list[i]).convert("RGB")
                    image.save(str(target_dir)+"photos/"+dates_list[i]+".jpg", "jpeg")
                if file_type == "video/mp4":
                    # Maybe we can do some transcoding here at some point, but highly unneeded
                    # since Instagram compresses well.
                    mp4info = MediaInfo.parse("source/"+image_list[i])
                    hasVideo = False
                    hasAudio = False
                    for track in mp4info.tracks:
                        if track.track_type == "Video":
                            hasVideo = True
                        if track.track_type == "Audio":
                            hasAudio = True
                    if hasAudio and hasVideo:
                        # MP4 contains a video.
                        shutil.copy("source/"+image_list[i], str(target_dir)+"video/"+dates_list[i]+".mp4")
                    elif hasAudio:
                        # MP4 is just an audio clip.
                        shutil.copy("source/"+image_list[i], str(target_dir)+"audio/"+dates_list[i]+".mp4")
            else:
                print("A reference exists to a file ("+str(image_list[i])+") that doesn't exist. Did you extract all media properly?")

# In this function, we will transform the date from what it is on the html file into
# a proper format we can use for the name.
def idmf_correct_media_dates(media_dates_list):
    date_counts = Counter(media_dates_list)
    corrected_image_dates_list = []

    for date in media_dates_list:
        if date_counts[date] > 1:
            #Append 00X based on the occurrence
            occurrence = date_counts[date] - 1
            new_date = f"{date}_{occurrence:03d}"
            date_counts[date] -= 1
        else:
            new_date = date

        corrected_image_dates_list.append(new_date)
    return corrected_image_dates_list

def idmf_parse_html_files(target_dir):
    global media_dates, media_links


    # Recursively search for matching files
    matching_files = []
    file_pattern = "message_*.html"
    for root, dirnames, filenames in os.walk(target_dir):
        for filename in fnmatch.filter(filenames, file_pattern):
            matching_files.append(os.path.join(root, filename))

    for file_path in matching_files:
    # For every file that matches our set file pattern...
        with open(file_path, 'r', encoding='utf-8') as html_file:
            source_code = html_file.read()
            print("Parsing: "+file_path)
            #tk_update_status(file_path)
            htmlParser.feed(source_code)

            # Make sure that multiple instances of filenames are corrected so they will not cause issues with the filesystem
            corrected_image_dates = idmf_correct_media_dates(media_dates_list=media_dates)
            idmf_save_media(file_path, "output/", media_links, corrected_image_dates)
        print("Finished parsing file with ("+str(len(media_links))+") unique files.")


# Global variables we use to keep track of collected data.
media_links = []
media_dates = []
checkingfordate = False
ignore_because_group_photo = False
object_media_total = 0
countdowntodate = 0

# Define what we will do when searching thru HTML files
class MyHTMLParser(HTMLParser):

    # When we observe a start tag (div)
    def handle_starttag(self, tag, attrs):
        global checkingfordate, countdowntodate, object_media_total, ignore_because_group_photo
        #print("Encountered a start tag:", tag)
        for attr, value in attrs:
            #print("     attr:", attr)
            #print("         value:", value)
            if tag == "img" or tag == "video" or tag == "audio":
                if attr == "src" and value != "files/Instagram-Logo.png":
                    #print("Extracted image: "+value)
                    # Record image reference
                    if ignore_because_group_photo:
                        ignore_because_group_photo = False
                        print("Ignoring "+value+" because it is the icon for the chat.")
                    if value == "":
                        print("A reference exists to nothing! Good job Instagram.")
                    else:
                        media_links.append(value)
                        countdowntodate = 0
                        object_media_total += 1
                        checkingfordate = True
            if tag == "div" and checkingfordate:
                countdowntodate += 1
                #print(countdowntodate)

    def handle_data(self, data):
        global checkingfordate, countdowntodate, object_media_total, ignore_because_group_photo
        #print("Encountered some data  :", data)
        if countdowntodate == 1 and checkingfordate:
            for i in range(object_media_total):
                # For every image we find in a message block, 
                # convert  the extracted date to the format we want 
                # (eg. Sep 30, 2022, 9:32PM TO 20220930_213200)
                time_object = time.strptime(data, '%b %d, %Y, %I:%M %p')
                formatted_time_object = time.strftime('%Y%m%d_%H%M%S', time_object)
                media_dates.append(formatted_time_object)
                #print("Added Timestamp: "+ formatted_time_object)
            
            # Because we found the date for the media, start looking for the next media.
            checkingfordate = False
            countdowntodate = 0
            object_media_total = 0
        if data == "Group photo":
            # If we are about to encounter the preview image for the group chat, ignore it in the start tags.
            ignore_because_group_photo = True                
htmlParser = MyHTMLParser()

# Specify the directory we want to search in.
tk_root = tk.Tk()
tk_root.title("InstagramDownloadMetadataFixer by Brandon Bunce")
tk_root.geometry("800x400")
tk_status = tk.Label(master = tk_root, text = "")
tk_status.pack()
search_directory = tkinter.filedialog.askdirectory(title="Select Instagram Root Directory (should contain comments/files/messages)")
#tk_root.mainloop()
#tk_root.withdraw()

# Make sure our working directory is set up.
idmf_check_working_directory()

# Parse all avaialbe html files
idmf_parse_html_files(search_directory)

delete_duplicates = input("Would you like to delete any duplicate files? (Spammed memes from your group chats)\nThis works by hashing files to determine if they are unique.\nPlease input (Y/N)\n")
if delete_duplicates.lower() == "y":
    print("Deleting duplicates...")
    idmf_delete_duplicates("output")
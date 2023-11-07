from PIL import Image
from html.parser import HTMLParser
import time
import fnmatch
import os
from collections import Counter
import shutil
import magic
from pymediainfo import MediaInfo
from tkinter.filedialog import askdirectory
import tkinter as tk
from tkinter import Tk
import hashlib
from pathlib import Path

print("Starting InstagramDownloadMetadataFixer by Brandon Bunce")

# Specify the directory we want to search in.
Tk().withdraw()
search_directory = askdirectory(title="Select Instagram Root Directory (should contain comments/files/messages)")

# Define what we will do when searching thru HTML files
class MyHTMLParser(HTMLParser):
    # When we observe a start tag (div)
    def handle_starttag(self, tag, attrs):
        global checkingfordate, countdowntodate, imageinmessagecount, isgroupphoto
        #print("Encountered a start tag:", tag)
        for attr, value in attrs:
            #print("     attr:", attr)
            #print("         value:", value)
            if tag == "img" or tag == "video" or tag == "audio":
                if attr == "src" and value != "files/Instagram-Logo.png":
                    #print("Extracted image: "+value)
                    # Record image reference
                    if isgroupphoto:
                        isgroupphoto = False
                        print("Ignoring "+value+" because it is the icon for the chat.")
                    if value == "":
                        print("A reference exists to nothing! Good job Instagram.")
                    else:
                        imagereferences.append(value)
                        countdowntodate = 0
                        imageinmessagecount += 1
                        checkingfordate = True
            if tag == "div" and checkingfordate:
                countdowntodate += 1
                #print(countdowntodate)

    def handle_data(self, data):
        global checkingfordate, countdowntodate, imageinmessagecount, isgroupphoto
        #print("Encountered some data  :", data)
        if countdowntodate == 1 and checkingfordate:
            for i in range(imageinmessagecount):
                # For every image we find in a message block, 
                # convert  the extracted date to the format we want 
                # (eg. Sep 30, 2022, 9:32PM TO 20220930_213200)
                time_object = time.strptime(data, '%b %d, %Y, %I:%M %p')
                formatted_time_object = time.strftime('%Y%m%d_%H%M%S', time_object)
                imagedates.append(formatted_time_object)
                #print("Added Timestamp: "+ formatted_time_object)
            
            # Because we found the date for the media, start looking for the next media.
            checkingfordate = False
            countdowntodate = 0
            imageinmessagecount = 0
        if data == "Group photo":
            # If we are about to encounter the preview image for the group chat, ignore it in the start tags.
            isgroupphoto = True                

htmlParser = MyHTMLParser()

# Define the pattern for matching HTML files with the name "message_x.html"
file_pattern = "message_*.html"

# Initialize a list to store the matching file paths
matching_files = []

# Make sure our working directory is set up.
if not os.path.exists("output/photos"):
    os.makedirs("output/photos")
if not os.path.exists("output/video"):
    os.makedirs("output/video")
if not os.path.exists("output/audio"):
    os.makedirs("output/audio")

# Recursively search for matching files
for root, dirnames, filenames in os.walk(search_directory):
    for filename in fnmatch.filter(filenames, file_pattern):
        matching_files.append(os.path.join(root, filename))

# Initialize these lists here to collect data for each HTML file
imagereferences = []
imagedates = []
checkingfordate = False
isgroupphoto = False
imageinmessagecount = 0
countdowntodate = 0

# Print the list of matching file paths
for file_path in matching_files:
    with open(file_path, 'r', encoding='utf-8') as html_file:
        source_code = html_file.read()
        print("Parsing: "+file_path)
        htmlParser.feed(source_code)

        # Make sure that multiple instances of filenames are corrected so they will not cause issues with the filesystem
        date_counts = Counter(imagedates)
        corrected_image_dates = []

        for date in imagedates:
            if date_counts[date] > 1:
                #Append 00X based on the occurrence
                occurrence = date_counts[date] - 1
                new_date = f"{date}_{occurrence:03d}"
                date_counts[date] -= 1
            else:
                new_date = date

            corrected_image_dates.append(new_date)

        # Open all the media and rename them to their corresponding formatted date in array.
        print("Saving media...")
        for i in range(len(imagereferences)):
            if os.path.exists("source/"+imagereferences[i]):
                # For whatever reason, Instagram will randomly store media without a file extension,
                # so, we must determine the file type before we pass it to other libraries.
                file_type = magic.from_file("source/"+imagereferences[i], mime=True)
                #print(str(i)+ " - " +str(file_type) +" - "+str(imagereferences[i]))
                if file_type == "image/jpeg":
                    image = Image.open("source/"+imagereferences[i]).convert("RGB")
                    image.save("output/photos/"+corrected_image_dates[i]+".jpg", "jpeg")
                if file_type == "video/mp4":
                    # Maybe we can do some transcoding here at some point, but highly unneeded
                    # since Instagram compresses well.
                    mp4info = MediaInfo.parse("source/"+imagereferences[i])
                    hasVideo = False
                    hasAudio = False
                    for track in mp4info.tracks:
                        if track.track_type == "Video":
                            hasVideo = True
                        if track.track_type == "Audio":
                            hasAudio = True
                    if hasAudio and hasVideo:
                        # MP4 contains a video.
                        shutil.copy("source/"+imagereferences[i], "output/video/"+corrected_image_dates[i]+".mp4")
                    elif hasAudio:
                        # MP4 is just an audio clip.
                        shutil.copy("source/"+imagereferences[i], "output/audio/"+corrected_image_dates[i]+".mp4")
            else:
                print("A reference exists to a file ("+str(imagereferences[i])+") that doesn't exist. Did you extract all media properly?")
    print("Finished parsing file with ("+str(len(imagereferences))+") unique files.")
    imagereferences.clear()
    imagedates.clear()
    corrected_image_dates.clear()
    checkingfordate = False
    countdowntodate = 0

delete_duplicates = input("Would you like to delete any duplicate files? (Spammed memes from your group chats)\nThis works by hashing files to determine if they are unique.\nPlease input (Y/N)\n")
if delete_duplicates.lower() == "y":
    print("Deleting duplicates...")
    # Listing out all the files
    list_of_files = os.walk("output")
  
    # In order to detect the duplicate files, define an empty dictionary.
    unique_files = dict()
  
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
                else:
                    print(f"{file_path} has the same hash but different size, not deleting.")
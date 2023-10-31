from PIL import Image
from html.parser import HTMLParser
import time
import fnmatch
import os

print("Starting InstagramDownloadMetadataFixer by Brandon Bunce")

val = input("Please input Instagram download root folder (should contain comments, files, message, and index.html\n")
#im = Image.open(val).convert("RGB")
#im.show()
#im.save()

# Define what we will do when searching thru HTML files
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global checkingfordate, countdowntodate, imageinmessagecount
        #print("Encountered a start tag:", tag)
        for attr, value in attrs:
            #print("     attr:", attr)
            #print("         value:", value)
            if tag == "img":
                if attr == "src" and value != "files/Instagram-Logo.png":
                    #print("Extracted image: "+value)
                    # Record image reference
                    imagereferences.append(value)
                    countdowntodate = 0
                    imageinmessagecount += 1
                    checkingfordate = True
            if tag == "div" and checkingfordate:
                countdowntodate += 1
                #print(countdowntodate)

    def handle_data(self, data):
        global checkingfordate, countdowntodate, imageinmessagecount
        #print("Encountered some data  :", data)
        if countdowntodate == 1 and checkingfordate:
            for i in range(imageinmessagecount):
                # Convert extracted date to the format we want (eg. Sep 30, 2022, 9:32PM TO 20220930_213200)
                time_obj = time.strptime(data, '%b %d, %Y, %I:%M %p')
                formatted_time_object = time.strftime('%Y%m%d_%H%M%S', time_obj)
                if (imageinmessagecount > 1):
                    imagedates.append(formatted_time_object +"_00"+str(i))
                    # 20230918_101032_002
                else:
                    imagedates.append(formatted_time_object)

                #print("Added Timestamp: "+ formatted_time_object)
            checkingfordate = False
            countdowntodate = 0
            imageinmessagecount = 0
                

htmlParser = MyHTMLParser()


# Specify the directory you want to search in
search_directory = r'C:\Users\Donut\Desktop\InstagramDownloadMetadataFixer\source'

# Define the pattern for matching HTML files with the name "message_x.html"
file_pattern = "message_*.html"

# Initialize a list to store the matching file paths
matching_files = []

# Recursively search for matching files
for root, dirnames, filenames in os.walk(search_directory):
    for filename in fnmatch.filter(filenames, file_pattern):
        matching_files.append(os.path.join(root, filename))

# Initialize these lists here to collect data for each HTML file
imagereferences = []
imagedates = []
checkingfordate = False
imageinmessagecount = 0
countdowntodate = 0

# Print the list of matching file paths
for file_path in matching_files:
    with open(file_path, 'r', encoding='utf-8') as html_file:
        source_code = html_file.read()
        print("Parsing: "+file_path)
        htmlParser.feed(source_code)

        # Open all the images and rename them to their corresponding formatted date in array.
        print("Saving images...")
        for i in range(len(imagereferences)):
            im = Image.open("source/"+imagereferences[i]).convert("RGB")
            im.save("output/"+imagedates[i]+".png", "png")

        print("Finished parsing file with ("+str(len(imagereferences))+") unique image(s).")
        imagereferences.clear()
        imagedates.clear()
        checkingfordate = False
        countdowntodate = 0

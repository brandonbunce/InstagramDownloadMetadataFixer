# InstagramDownloadMetadataFixer
Corrects the arbitrary filenames of photos/videos/audio downloaded from Instagram by using the HTML files provided, and renaming media based on the time it was sent.
(e.g. 309652536_5484494714960075_8826135696565401376_n_682982662784664.mp4 ---> 20230503_104100.mp4)

Are you a shameless data hoarder? Looking to organize all those wacky photos you've sent in your group chats and to your friends?
You probably tried downloading all your data from Instagram, which is cool and all, until you realize the file names are
completely arbitrary and cannot be organized at all with the rest of your photos.

The purpose of this repo is to correct this by renaming all media (and formatting it in a way you want) to when the media was sent, 
while also considering the quirks of how Instagram stores data (hint: its not pretty! Some files have no extensions, while some videos
in HTML files will point to nothing!)

## Usage:
1. Download release and run main.py (make sure all imports are installed).
2. Select source folder and destination folder.
3. Follow prompts from CLI (do you want to remove duplicates)
4. Enjoy your date-stamped photos.

## Tips:
- When requesting a data download from Instagram, it seems to be very prone to mistakes when requesting ALL of your data at once, so I advise requesting only what you want, such as your messsages.
- It is generally better to run this application on an SSD, or else you will be waiting on I/O and it'll run slow :(


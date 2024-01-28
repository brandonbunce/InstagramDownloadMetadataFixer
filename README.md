# InstagramDownloadMetadataFixer
Attempts to correct the arbitrary filenames of photos/videos/audio downloaded from Instagram based on the time they were sent. (eg. 240512253_529811541562402_295629182555036975_n_253256119992566.jpg ---> 20200612_211300.jpg)

Are you a shameless data hoarder? Looking to organize all those wacky photos you've sent and received in your group chats and DMs?
You probably tried downloading all your data from Instagram, which is cool and all, until you realize the file names are
completely arbitrary and cannot be organized at all with the rest of your photos.

The purpose of this repo is to correct this by renaming all media (and formatting it in a way you want) to when the media was sent, 
while also considering the quirks of how Instagram stores data (hint: its not pretty! Some files have no extensions, while some videos
in HTML files will point to nothing!)

Usage:
Download the latest release, run the python script (make sure you've got everything imported properly), and follow prompts to select your source folder, select your output folder, and to delete duplicates. Your images will be organized (as best as possible) in no time.

Tips:
When downloading data from Instagram, it may sometimes be better to request partial data downloads, such as with chats only, as sometimes the downloads can be incomplete when requesting a full one.

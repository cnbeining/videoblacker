videoblacker
============

Patch video's both part to bypass Letvcloud's transcode.

The very last way to bypass the bitrate limit, and "no one can break my work".

Not promoted, but it works.

Please kindly check https://github.com/cnbeining?tab=repositories and http://www.cnbeining.com/ for all the scripts I wrote to bypass Letvcloud.

See also:

https://github.com/cnbeining/audioblacker

https://github.com/cnbeining/videospeeder

https://github.com/cnbeining/FlvPatcher

http://www.cnbeining.com/2014/08/about-fuji-after-black-lazy-bag/


Requirement
-------

- Python 2.7
- ffmpeg, with own aac and *libx264* encoder  <--------IMPORTANT!!!!!!
- ffprobe
- Mediainfo
- Enough spare space: the size of the original video plus 2 (4 if use safe mode with auto-cleaning failed) times of the audio stream.

Usage
------

Usage:
   
    python videoblacker.py (-h) (-i input.mp4) (-o output.mp4) (-b 1900000) (-a 110000) (-s 1) 
    
    -h: Default: None
        Help.
    
    -i: Default: Blank
        Input file.
        If the file and audioblacker are not under the same path,
        it is suggested to use absolute path to avoid possible failure.
    
    -o Default: input-filename.black.mp4
       Output file.
       Would be in the same folder with the original file if not specified.
       
    -b: Default: 1900000
        Target bitrate.
    
    -a: Default: 110000
        Target audio bitrate.
        
    videoblacker would calculate both of the required black time,
    and choose the larger one to make sure your convert is successful.
    
    Please notice that if your original video/audio bitrate is too small,
    videoblacker would throw you an ERROR and quit.
    
    -s: Default: 1
        Use safe mode.
        Disabling would save you some (can be a lot!) space and time,
        if you know what you are doing.
        
        - 1:
        videoblacker would remux the file to MP4 at the very first.
        Good enough for most of the files.
        - 2:
        videoblacker would remux the file to h264 and aac at the very first,
        then remux them to MP4.
        I put it there in case you come across some videos-from-hell.


Author
-----

Beining, http://www.cnbeining.com/

License
-----

GNUv2 license.

Misc
-----

- You are not supposed to refer/mention/promote this software at any service within Chinese Mainland.

- This method is enlightened by @小丸到达. Check its Windows version, Maruku Toolbox: https://marukotoolbox.codeplex.com/

- Also thanks to the help of @StarBrilliant.

- Making blank video can be slower then expected, even with my 13-late MBP.

- Behaviour may be unpredictable with videos that have been processed by software like SinaHigh, FlvBugger(v2), FlvPatcher, audioblacker, videospeeder, etc.

History
----

0.1: The very beginning
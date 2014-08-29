#!/usr/bin/env python
#coding:utf-8
# Author:  Beining --<ACICFG>
# Contact: http://www.cnbeining.com/   |https://github.com/cnbeining/videoblacker
# Purpose: Patch video's both part to bypass Letvcloud's transcode.
# Created: 08/29/2014
# LICENSE: GNU v2

import sys
import os
import os, sys, subprocess, shlex, re
from subprocess import call
import uuid
import math
import shutil
import getopt



#----------------------------------------------------------------------
def probe_file(filename):
    cmnd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #print filename
    out, err =  p.communicate()
    #print out
    if err:
        print err
        return None
    return out


#----------------------------------------------------------------------
def time_to_sec(time_raw):
    """
    str->int
    
    ignore .*."""
    hr = int(time_raw.split(':')[0]) * 3600
    minute = int(time_raw.split(':')[1]) * 60
    sec = int(float(time_raw.split(':')[2]))
    return int(hr + minute + sec)

#----------------------------------------------------------------------
def get_abspath(filename):
    """str->str"""
    return str(os.path.abspath(filename))

#----------------------------------------------------------------------
def get_dimention_mediainfo(filename):
    """str->str
    path to dimention"""
    return str(os.popen('mediainfo \'--Inform=Video;%Width%x%Height%\' \'' + filename + '\'').read()).replace('x', '*').strip()

#----------------------------------------------------------------------
def process(filename, target_bitrate, audiobitrate, safe, outputfile):
    """str,int,int,str->?
    filename,outputfile comes with the path.
    safe=0: directly convert the file to m4a"""
    tmpdir = '/tmp/Audioblacker-' + str(uuid.uuid4())
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    audio_format = ''
    audio_duration = ''
    audio_bitrate = ''
    video_format = ''
    video_duration = ''
    video_bitrate = ''
    ff = ''
    if safe == 1:
        #directly to mp4
        print('INFO: Pre-processing video ...')
        os.system('ffmpeg -i \'' + filename + '\'  -c copy ' + tmpdir+'/orivideo.mp4' +'> /dev/null 2>&1')
        filename = tmpdir+'/orivideo.mp4'
    elif safe == 2:
        #All the f**king dramas......
        print('INFO: Pre-processing video ...')
        os.system('ffmpeg -i \'' + filename + '\'  -c copy ' + tmpdir+'/orivideo1.mp4' +'> /dev/null 2>&1')
        os.system('ffmpeg -i ' + tmpdir+'/orivideo1.mp4 -vbsf h264_mp4toannexb  -an -c:v copy ' + tmpdir+'/orivideo.h264' +'> /dev/null 2>&1')
        os.system('ffmpeg -i ' + tmpdir+'/orivideo1.mp4  -vn -f adts -c:a copy ' + tmpdir+'/oriaudio.aac' +'> /dev/null 2>&1')
        os.system('ffmpeg -i ' + tmpdir+'/orivideo.h264   -i '+ tmpdir+'/oriaudio.aac -bsf:a aac_adtstoasc -c copy ' + tmpdir+'/orivideo.mp4' +'> /dev/null 2>&1')
        filename = tmpdir+'/orivideo.mp4'
        try:
            os.remove(tmpdir+'/orivideo.h264')
            os.remove(tmpdir+'/oriaudio.aac')
            pass
        except:
            print('WARNING: Cannot delete temp file, watch out your free space!')
        filename = tmpdir+'/orivideo.mp4'
    print('INFO: Detecting video info...')
    os.system('ffmpeg -i \'' + filename + '\' -vn -c:a copy ' + tmpdir+'/audio.m4a')  # +' > /dev/null 2>&1')
    try:
        for line in probe_file(tmpdir+'/audio.m4a').split('\n'):
            if 'duration' in line:
                audio_duration = str(line.split('=')[1])
                break
        for line in probe_file(filename).split('\n'):
            if 'duration' in line:
                video_duration = str(line.split('=')[1])
                break
    except:
        print('ERROR: Cannot read video file!')
        shutil.rmtree(tmpdir)
        exit()
    #Calc...
    #time_by_video
    print('INFO: Doing calculation...')
    try:
        video_duration_sec = time_to_sec(video_duration)
        video_size_byte = int(os.path.getsize(filename))
        audio_duration_sec = time_to_sec(audio_duration)
        audio_size_byte = int(os.path.getsize(tmpdir+'/audio.m4a'))
        print(video_duration_sec)
        
    except:
        print('ERROR: Cannot calculate time, did you input a bitrate too high?')
        shutil.rmtree(tmpdir)
        exit()
    #!!!!!FLOAT DUE TO ACCURACY!!!!!
    target_byterate = target_bitrate / 8.0
    target_audiobyterate = audiobitrate / 8.0
    time_video = int(math.ceil((video_size_byte - target_byterate * video_duration_sec) / (target_byterate - 470)))
    time_audio = int(math.ceil((audio_size_byte - target_audiobyterate * audio_duration_sec) / (target_audiobyterate - 470)))
    if time_audio < 0 and time_video < 0:
        print('ERROR: Cannot calculate target, your target bitrate is higher than the original file!')
        shutil.rmtree(tmpdir)
        exit()
    if time_audio == 0 and time_video == 0:
        time_patch = 60
    elif time_audio > time_video:
        time_patch = time_audio + 10
    else:
        time_patch = time_video + 10
    #Make audio patch
    print('INFO: Making ' + str(time_patch) + ' secs of blank video, can be slow...')
    os.system('ffmpeg -filter_complex \'color=black:s=' + get_dimention_mediainfo(filename) + ':d=' + str(time_patch) + '\' -c:v libx264  -filter_complex \'aevalsrc=0:d=' + str(time_patch) + '\' -strict experimental -c:a aac ' + tmpdir + '/patch.mp4'+'> /dev/null 2>&1')
    f = open(tmpdir + '/patch.txt', 'w')
    ff = 'file \'' + filename + '\'' + '\n' + 'file \'' + tmpdir + '/patch.mp4\''
    py_path = sys.path[0]
    os.chdir(py_path)
    f.write(ff)
    f.close()
    print('INFO: Making final output file...')
    os.system('ffmpeg -f concat -i '+ tmpdir + '/patch.txt -c copy ' + outputfile +'> /dev/null 2>&1')
    print('Done!')
    #clean up
    try:
        shutil.rmtree(tmpdir)
    except:
        print('ERROR: Cannot remove temp dir, do it by yourself!')

#----------------------------------------------------------------------
def usage():
    """"""
    print('''Usage:
    
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
        ''')


#----------------------------------------------------------------------
if __name__=='__main__':
    argv_list = []
    argv_list = sys.argv[1:]
    filename = ''
    target_bitrate = 1900000
    outputfile = ''
    safe = 1
    audiobitrate = 110000
    try:
        opts, args = getopt.getopt(argv_list, "hi:b:a:o:s:", ['help', 'input','bitrate', 'audiobitrate'
                                                           'outputfile', 'safe'])
    except getopt.GetoptError:
        usage()
        exit()
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            exit()
        elif o in ('-i', '--input'):
            filename = a
            try:
                argv_list.remove('-i')
            except:
                break
        elif o in ('-b', '--bitrate'):
            target_bitrate = int(a)
            try:
                argv_list.remove('-b')
            except:
                break
        elif o in ('-a', '--audiobitrate'):
            audiobitrate = int(a)
            try:
                argv_list.remove('-a')
            except:
                break        
        elif o in ('-o', '--outputfile'):
            outputfile = a
            try:
                argv_list.remove('-o')
            except:
                break
        elif o in ('-s', '--safe'):
            safe = int(a)
            try:
                argv_list.remove('-s')
            except:
                break
    if filename == '':
        print('ERROR: No input file!')
        exit()
    if outputfile == '':
        outputfile = filename.split('.')[0]
        for i in filename.split('.')[1:-1]:
            outputfile = outputfile + '.' + i
        outputfile = outputfile + '.black.mp4'
    process(filename, target_bitrate, audiobitrate, safe, outputfile)
    exit()
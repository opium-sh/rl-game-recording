import subprocess
import time
import ffmpeg # pip install ffmpeg-python

APP_NAME = "F1™ 2017" #this can be just a part of applicastions window name
QUALITY = 25  # change recoding quality 0-25, 0 - perfect and large file , 25 -poor quality and small file
PRESET = "medium"  # change this to achieve smaller file sizes (slower -> smaller file size) Possible values are: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
SCALE_W = 640  #
SCALE_H = 480
CROP_W = 640
CROP_H = 225
CROP_X = 0
CROP_Y = 180
FPS = 30
CODEC = "libx264"  # try one of the following libx264_nvenc
OUT_FILENAME = APP_NAME + "_recording_" + time.strftime("%Y%m%d-%H%M%S")


def get_current_diplay_id():
    wcommand = subprocess.Popen(['w', '-hs'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = wcommand.communicate()
    return stdout.decode('utf-8').split()[2]


def get_window_id(name):
    xwininfo = subprocess.Popen(['xwininfo', '-tree', '-root'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = xwininfo.communicate()
    for line in stdout.decode('utf-8').splitlines():
        l = line.find(name)
        if l is not -1:
            return line.split()[0]


def get_window_attrs(window_id):
    xwininfo_id = subprocess.Popen(['xwininfo', '-id', window_id], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = xwininfo_id.communicate()
    w, h, x, y = ("",) * 4
    for line in stdout.decode('utf-8').splitlines():
        if line.find("Width") is not -1:
            w = line.split()[1]
        if line.find("Height") is not -1:
            h = line.split()[1]
        if line.find("Absolute upper-left X") is not -1:
            x = line.split()[3]
        if line.find("Absolute upper-left Y") is not -1:
            y = line.split()[3]
    return w, h, x, y


w, h, x, y = get_window_attrs(get_window_id(APP_NAME))
display_id = get_current_diplay_id()

print('Display id: ' + display_id + " W H X Y " + w + " " + h + " " + x + " " + y + " ")
(
    ffmpeg
        .input(display_id + ".0+" + x + "," + y, format='x11grab', video_size=(w, h), framerate=FPS)
        .filter('scale', SCALE_W, SCALE_H)
        .filter('crop', CROP_W, CROP_H, CROP_X, CROP_Y)
        .output(OUT_FILENAME + '.mkv', crf=QUALITY, preset=PRESET, vcodec=CODEC)
        #.output('pipe:', format='mpegts')
        .run()
)

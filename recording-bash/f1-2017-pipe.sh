#!/bin/bash
QUALITY=25 # change recoding quality 0-25, 0 - perfect and large file , 25  small file
PRESET="medium" # change this to achieve smaller file sizes (slower -> smaller file size) Possible values are: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
APP_WINDOW_NAME="F1™ 2017" #part of the game window name, use xwininfo -tree to find it
SCALE_TO="640:480"
CROP="640:225:0:180"
FPS=30
CODEC="libx264" # try one of the following libx264_nvenc
##############################################################################################
OUT_FILENAME=../data/screen_recording_data/recording\_$(date -d "today" +"%Y-%m-%d_%H-%M-%S")
#steam steam://rungameid/515220&
#sleep 10
CURRENT_XORG_DISPLAY_IDS=$(w -hs |awk '{print $3}')
CURRENT_DISPLAY_ID=$(echo "${CURRENT_XORG_DISPLAY_IDS}"|head -n 1) #hardcode any value like :0 :1 :2 
WINDOW_ID=$(xwininfo -tree -root |grep  "$APP_WINDOW_NAME"|awk '{print $1}'|head -n 1)
WINDOW_ATTR=$(xwininfo -id "${WINDOW_ID}")
if xprop -id $WINDOW_ID | grep -q '_NET_WM_STATE(ATOM) = _NET_WM_STATE_FULLSCREEN'; then
  FULLSCREEN_GAME=1
fi
#main game recording stuff
W=$(echo "${WINDOW_ATTR}"|grep Width|awk '{print $2}')
H=$(echo "${WINDOW_ATTR}"|grep Height|awk '{print $2}')
X=$(echo "${WINDOW_ATTR}"|grep "Absolute upper-left X"|awk '{print $4}')
Y=$(echo "${WINDOW_ATTR}"|grep "Absolute upper-left Y"|awk '{print $4}')
#-f alsa -ac 2 -i pulse -acodec aac -strict experimental
#if [[ -z "${FULLSCREEN_GAME}" ]]; then
#  ffmpeg  -y -video_size "$W"x"$H" -framerate "$FPS" -f x11grab -i "$CURRENT_DISPLAY_ID".0+"$X","$Y" -c:v "$CODEC" -crf "$QUALITY" -preset "$PRESET" "$OUT_FILENAME".mkv
#else
  ffmpeg  -y -video_size "$W"x"$H" -framerate "$FPS" -f x11grab -i "$CURRENT_DISPLAY_ID".0+"$X","$Y" -c:v "$CODEC" -vf "scale=$SCALE_TO[a]; [a]crop=$CROP" -crf "$QUALITY" -preset "$PRESET" -f mpegts pipe:1
#fi

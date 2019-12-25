#!/bin/bash
QUALITY=15 # change recoding quality 0-25, 0 - perfect and large file , 25  and small file
APP_WINDOW_NAME="F1™ 2017" #part of the game window name, use xwininfo -tree to find it
SCALE_TO="1024:768"

##############################################################################################
OUT_FILENAME=F1\-$(date -d "today" +"%Y%m%d-%H%M")
#steam steam://rungameid/515220&
#sleep 10
CURRENT_XORG_DISPLAY_IDS=$(w -hs |awk '{print $3}')
CURRENT_DISPLAY_ID=$(echo "${CURRENT_XORG_DISPLAY_IDS}"|head -n 1) #hardcode any value like :0 :1 :2 
WINDOW_ID=$(xwininfo -tree -root |grep  "$APP_WINDOW_NAME"|awk '{print $1}'|head -n 1)
WINDOW_ATTR=$(xwininfo -id "${WINDOW_ID}")
if xprop -id $WINDOW_ID | grep -q '_NET_WM_STATE(ATOM) = _NET_WM_STATE_FULLSCREEN'; then
  FULLSCREEN_GAME=1
fi

#execute when CRTL+c is pressed
trap recode 2
recode()
{
  #encode/rescale so the mkv is smaller, then delete original recording
  if [[ -z "${FULLSCREEN_GAME}" ]]; then
    ffmpeg -y -i "$OUT_FILENAME"_big.mkv -c:v libx264 -crf "$QUALITY" -preset fast "$OUT_FILENAME"_small.mkv
  else
    ffmpeg -y -i "$OUT_FILENAME"_big.mkv -vf scale="$SCALE_TO" -c:v libx264 -crf "$QUALITY" -preset fast "$OUT_FILENAME"_small.mkv
  fi
  rm -f "$OUT_FILENAME"_big.mkv
}
#main game recording stuff
W=$(echo "${WINDOW_ATTR}"|grep Width|awk '{print $2}')
H=$(echo "${WINDOW_ATTR}"|grep Height|awk '{print $2}')
X=$(echo "${WINDOW_ATTR}"|grep "Absolute upper-left X"|awk '{print $4}')
Y=$(echo "${WINDOW_ATTR}"|grep "Absolute upper-left Y"|awk '{print $4}')
echo ==============================================
echo $W $H $X $Y $WINDOW_ID  ======  \n $WINDOW_ATTR
echo ==============================================
echo Available screens:
echo $CURRENT_XORG_DISPLAY_IDS
echo Using $CURRENT_DISPLAY_ID by default.
echo ==============================================
#-f alsa -ac 2 -i pulse -acodec aac -strict experimental
ffmpeg  -y -video_size "$W"x"$H" -framerate 30 -f x11grab -i "$CURRENT_DISPLAY_ID".0+"$X","$Y" -c:v libx264 -crf 0 -preset ultrafast "$OUT_FILENAME"_big.mkv

# vidi18n

```bash
ffmpeg -i video.mkv -c:v libx264 -c:a aac -strict experimental -f dash -min_seg_duration 9000000 -y output/manifest.mpd
```

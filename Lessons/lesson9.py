# imports a video file and will change resolution of given video strem. Also changes the audio stream to be echoed.
# Outputs these altered streams into a single new video in an alternate format (webm) instead of the the given (mp4)

import ffmpeg

video = '../Project3/twitch_nft_demo.mp4'
input = ffmpeg.input(video)
audio = input.audio.filter('aecho', 0.8, 0.9, 500, 0.3)
video = input.video.filter('scale', width=640, height=480)
out = ffmpeg.output(audio, video, 'lowResAltFormat.webm').overwrite_output().run()
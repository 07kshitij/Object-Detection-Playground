class data:
    def __init__(self):
        self.getData()

    def getData(self):
        import os
        path = '.'

        files = ['25fps.mkv']
        orgFR = 25

        for file in files:
            frameRate = [20]
            imgSize = [960]
            for frame in frameRate:
                for img in imgSize:
                    os.system('ffmpeg -i {} -filter:v "setpts={}*PTS" {}fps.mkv'.format(file, orgFR/frame, frame))
                    os.system('ffmpeg -i {}fps.mkv -filter:v scale="{}:trunc(ow/a/2)*2" -c:a copy {}p_{}fps.mkv'.format(frame, img, img, frame))

if __name__ == "__main__":
    data()
import os


class data:
    def __init__(self):
        self.getData()

    def getData(self, params, source_file):
        path = "."

        orgFR = 25
        frame = params["frameRate"]
        img = params["imgSize"]

        os.system(
            'ffmpeg -i {} -filter:v "setpts={}*PTS" {}fps.mkv'.format(
                source_file, orgFR / frame, frame
            )
        )
        os.system(
            'ffmpeg -i {}fps.mkv -filter:v scale="{}:trunc(ow/a/2)*2" -c:a copy {}p_{}fps.mkv'.format(
                frame, img, img, frame
            )
        )

        return "{}p_{}fps.mkv".format(img, frame)


if __name__ == "__main__":
    data()

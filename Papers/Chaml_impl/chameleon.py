import os
import pprint
from shutil import copyfile
from itertools import product


class color:
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"
    REVERSE = "\033[0;0m"


class chameleon:
    def __init__(self):
        """ Initialize all parameters and env paths """
        self.configs = [
            {"frameRate": 20, "imgSize": 960, "models": "yolo"},
            {"frameRate": 25, "imgSize": 1280, "models": "yolo"},
        ]
        self.params = ["frameRate", "imgSize", "models"]

        self.model_path = os.path.join(
            os.getenv("HOME_PATH"), "Papers/Chaml_impl/darknet"
        )
        self.source_file = os.path.join(os.getenv("HOME_PATH"), "DataSet/25fps.mkv")
        self.model_data = os.path.join(
            os.getenv("HOME_PATH"), "Papers/Chaml_impl/darknet/data"
        )
        self.accuracy = 0.8
        self.threshold = 0.5
        self.top_config = 2
        self.colors = color()
        self.runChameleon()

    @staticmethod
    def getData(params, source_file):
        """ Convert the original videofile's params to those specified by `params` """
        orgFR = 25
        frame = params["frameRate"]
        img = params["imgSize"]

        os.system(
            'ffmpeg -loglevel quiet -i {} -filter:v "setpts={}*PTS" {}fps.mkv'.format(
                source_file, orgFR / frame, frame
            )
        )
        os.system(
            'ffmpeg -loglevel quiet -i {}fps.mkv -filter:v scale="{}:trunc(ow/a/2)*2" -c:a copy {}p_{}fps.mkv'.format(
                frame, img, img, frame
            )
        )

        return "{}p_{}fps.mkv".format(img, frame)

    @staticmethod
    def getImageDims(file):
        """ Returns the resolution the given video frame """
        os.system(
            "ffprobe -loglevel quiet -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 {} > tmp.txt".format(
                file
            )
        )
        with open("tmp.txt", "r") as f:
            dims = f.readlines()[0]
            dims = dims[:-1]  # Remove the newline character
            dims = [(int)(x) for x in dims.split(",")]
        os.system("rm -rf tmp.txt")
        return dims

    def scaleImage(self, file, dims):
        """ Scales the given file to the given resolution """
        path = file
        outfile = "out_" + file
        print(" +++ Converting ",path, " to ", outfile)
        os.system(
            "ffmpeg -loglevel quiet -i {} -vf scale={}:{} {}".format(
                path, dims[0], dims[0], outfile
            )
        )
        print(" +++ Conversion Done")
        # copyfile(outfile, path)
        # os.system("rm -rf {}".format(outfile))
        return outfile

    def runChameleon(self):
        """ Runs the Model """
        config = self.profile(1, self.configs, self.top_config)
        print(self.colors.BLUE, "Top k Configs : ", config, self.colors.REVERSE)

    def getFrames(self, file, frame=0, outfile="res0"):
        """ Extract the given frame from the given file """
        os.system(
            'ffmpeg -loglevel quiet -i {} -vf "select=eq(n\,{})" -vframes 1 {}.jpg'.format(
                file, frame, outfile
            )
        )
        os.system("mv {}.jpg {}".format(outfile, self.model_data))

    def updateSpatial(self, videos, configurations):
        # Todo : Implement paper
        return

    def updateTemporal(self):
        # Todo : Implement paper
        return

    @staticmethod
    def getGoldenConfig():
        return {"frameRate": 25, "imgSize": 1280, "models": "yolo"}

    def profile(self, segment, configurations, k):
        """ Profiles each of the knobs in the given configurations
            returns the top-k configurations with the least resource consumption """
        knobVals = dict()
        for knob in self.params:
            knobVals[knob] = list()

        for config in configurations:
            for key, val in config.items():
                if val not in knobVals[key]:
                    knobVals[key].append(val)

        print(knobVals)

        golden_config = self.getGoldenConfig()
        file = self.getData(golden_config, self.source_file)
        golden_dims = self.getImageDims(self.source_file)
        print(" +++ In profile : Golden Config Dims = " + str(golden_dims))
        curr_config = self.getGoldenConfig()
        knob_val_to_score = dict()

        for param in knobVals:
            curr_config = self.getGoldenConfig()
            for value in knobVals[param]:
                curr_config[param] = value
                print(
                    self.colors.BLUE,
                    "\n+++ Current Configuration : ",
                    curr_config,
                    self.colors.REVERSE,
                )
                print(
                    self.colors.BLUE,
                    "+++ Golden Configuration : ",
                    golden_config,
                    "\n",
                    self.colors.REVERSE,
                )
                F1_score = self.F1(segment, curr_config, file, golden_dims)
                knob_val_to_score[value] = F1_score

        accurate_configs = list()

        configs = list()
        allValues = list()

        for param in knobVals:
            allValues.append(knobVals[param])

        configs = list(product(allValues[0], allValues[1], allValues[2]))

        print(self.colors.GREEN, "All Configurations : ", configs, self.colors.REVERSE)

        for config in configs:
            score = 1
            for value in config:
                score *= knob_val_to_score[value]
            print(self.colors.YELLOW, config, score, self.colors.REVERSE)
            if score >= self.accuracy:
                return_val = dict()
                for n in range(len(self.params)):
                    return_val[self.params[n]] = config[n]
                accurate_configs.append(return_val)

        k = min(k, len(accurate_configs))
        # Sort accurate_configs by resource consumption - TODO

        return accurate_configs[0:k]

    @staticmethod
    def getbbox(file):
        """ Returns the Bounding Boxes of the classes detected by YOLO
            returns : list of tuples (Class, {Bounding Box : x1, x2, y1, y2}) """
        bounding_boxes = list()
        with open(file, "r") as f:
            lines = f.readlines()
            lines = lines[1:]
            for n in range(0, len(lines)):
                if n % 2 == 1:
                    box = [(int)(x) for x in lines[n].split()]
                    obj = lines[n - 1].split(":")[0]
                    grp = (obj, box)
                    bounding_boxes.append(grp)

        return bounding_boxes

    def F1(self, segment, curr_config, gold_file, golden_dims):
        """ Compute the F1 score for a given config. wrt the golden config. 
                    over `segment` no of segments """
        sum = 0
        curr_file = self.getData(curr_config, self.source_file)
        # curr_file = self.scaleImage(curr_file, golden_dims) - Doesn't Work :/
        for S in range(segment):
            self.getFrames(curr_file, S, "curr")
            self.getFrames(gold_file, S, "base")
            # self.scaleImage('curr.jpg', golden_dims)
            print(self.colors.RED, "\n +++ YOLO Running +++ \n", self.colors.REVERSE)
            self.runYOLO("curr.jpg", "base.jpg")
            sum += self.getF1score()

        return sum / segment

    def runYOLO(self, curr_file, golden_file):
        """ Runs the Object Detection Model YOLO """
        os.chdir(self.model_path)
        os.system(
            "./darknet detect cfg/yolov3.cfg yolov3.weights data/{} > {}".format(
                curr_file, "curr.txt"
            )
        )
        os.system(
            "./darknet detect cfg/yolov3.cfg yolov3.weights data/{} > {}".format(
                golden_file, "base.txt"
            )
        )
        print(self.colors.RED, "\n +++ YOLO Run completed +++ \n", self.colors.REVERSE)
        os.chdir("/home/kshitij/btp/Papers/Chaml_impl/")
        return

    def getF1score(self):
        """ Returns F1 score of the config wrt Golden Config for the current frame """

        path = self.model_path
        file_golden = ""
        file_current = ""
        for file in os.listdir(path):
            if file.endswith(".txt"):
                if file.endswith("base.txt"):
                    file_golden = file
                if file.endswith("curr.txt"):
                    file_current = file
        precision = 0.0
        recall = 0.0
        curr_bboxes = self.getbbox(os.path.join(path, file_current))
        gold_bboxes = self.getbbox(os.path.join(path, file_golden))
        total_detect = len(gold_bboxes)
        total_object = len(curr_bboxes)
        true_positive = 0
        # pprint.pprint(gold_bboxes)
        # pprint.pprint(curr_bboxes)
        for box_1 in curr_bboxes:
            for box_2 in gold_bboxes:
                if box_1[0] == box_2[0]:
                    x_left = max(box_1[1][0], box_2[1][0])
                    y_top = max(box_1[1][1], box_2[1][1])
                    x_right = min(box_1[1][2], box_2[1][2])
                    y_bottom = min(box_1[1][3], box_2[1][3])

                    if x_left > x_right or y_top > y_bottom:
                        continue

                    intersection = (x_right - x_left) * (y_bottom - y_top)

                    A1 = (box_1[1][2] - box_1[1][0]) * (box_1[1][3] - box_1[1][1])
                    A2 = (box_2[1][2] - box_2[1][0]) * (box_2[1][3] - box_2[1][1])

                    IoU = (intersection) / (A1 + A2 - intersection)
                    assert IoU >= 0.0
                    assert IoU <= 1.0
                    # print("IoU = {}".format(IoU))
                    if IoU >= self.threshold:
                        true_positive += 1
                        gold_bboxes.remove(box_2)
                        break

        precision = true_positive / total_detect
        recall = true_positive / total_object
        print(
            self.colors.MAGENTA,
            "\n +++ True Pos = {}, Golden Config Obj. Cnt = {}, Curr Config Obj. Cnt = {} +++\n".format(
                true_positive, total_detect, total_object
            ),
            self.colors.REVERSE,
        )
        try:
            F1 = 2 / ((1 / precision) + (1 / recall))
            print(self.colors.RED, " +++ F1 score = ", F1, self.colors.REVERSE)
            return F1
        except:
            ZeroDivisionError
            return 0


if __name__ == "__main__":
    # Run the Model
    chameleon()

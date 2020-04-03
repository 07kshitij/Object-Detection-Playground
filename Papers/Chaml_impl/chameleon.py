import os
import pprint
from shutil import copyfile

class chameleon:
    def __init__(self):
        # data.getData()
        self.params = {"frameRate": [20],
                       "imgSize": [960],
                       "models": ['yolo']}

        self.model_path = os.path.join(os.getenv('HOME_PATH'), 'Papers/Chaml_impl/darknet')
        self.source_file = os.path.join(os.getenv('HOME_PATH'), 'DataSet/25fps.mkv')
        self.model_data = os.path.join(os.getenv('HOME_PATH'), 'Papers/Chaml_impl/darknet/data')
        self.accuracy = 0.8
        self.threshold = 0.3
        self.top_config = 2
        print(self.model_path)
        self.runChameleon()

    @staticmethod
    def getData(params, source_file):
        path = '.'

        orgFR = 25
        frame = params['frameRate']
        img = params['imgSize']

        os.system(
            'ffmpeg -loglevel quiet -i {} -filter:v "setpts={}*PTS" {}fps.mkv'.format(source_file, orgFR/frame, frame))
        os.system(
            'ffmpeg -loglevel quiet -i {}fps.mkv -filter:v scale="{}:trunc(ow/a/2)*2" -c:a copy {}p_{}fps.mkv'.format(frame, img, img, frame))

        return '{}p_{}fps.mkv'.format(img, frame)

    @staticmethod
    def getImageDims(file):
        os.system(
            'ffprobe -loglevel quiet -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 {} > tmp.txt'.format(
                file)
        )
        with open('tmp.txt', 'r') as f:
            dims = f.readlines()[0]
            dims = dims[:-1]  # Remove the newline character
            dims = [(int)(x) for x in dims.split(',')]
        os.system('rm -rf tmp.txt')
        return dims

    def scaleImage(self, file, dims):
        path = os.path.join(self.model_data, file)
        outfile = os.path.join(self.model_data, 'out_' + file)
        os.system(
            'ffmpeg -loglevel quiet -i {} -vf scale={}:{} {}'.format(
                path, dims[0], dims[1], outfile)
        )
        copyfile(outfile, path)
        os.system('rm -rf {}'.format(outfile))

    def runChameleon(self):
        config = self.profile(1, self.params, self.top_config)
        print("Top k Configs : ", config)

    def getFrames(self, file, frame=0, outfile='res0'):
        os.system(
            'ffmpeg -loglevel quiet -i {} -vf "select=eq(n\,{})" -vframes 1 {}.jpg'.format(file, frame, outfile))
        os.system('mv {}.jpg {}'.format(outfile, self.model_data))

    def updateSpatial(self, videos, configurations):
        # Todo : Implement paper
        return

    def updateTemporal(self):
        # Todo : Implement paper
        return

    def profile(self, segment, configurations, k):
        golden_config = self.getGoldenConfig()
        file = self.getData(golden_config, self.source_file)
        golden_dims = self.getImageDims(self.source_file)
        print(" +++ In profile : Golden Config Dims = " + str(golden_dims))
        curr_config = golden_config
        knob_val_to_score = dict()
        for param in self.params:
            curr_config = golden_config
            for value in self.params[param]:
                curr_config[param] = value
                print("\n+++ Current Configuration : ", curr_config)
                print("+++ Golden Configuration : ", golden_config, "\n")
                F1_score = self.F1(segment, curr_config, file, golden_dims)
                knob_val_to_score[value] = F1_score

        accurate_configs = list()

        for config in configurations:
            config_score = 1
            for param in configurations.keys():
                config_score *= knob_val_to_score[configurations[param][0]]
            if config_score >= self.accuracy:
                accurate_configs.append(config)

        return accurate_configs

    @staticmethod
    def getGoldenConfig():
        return {"frameRate": 25, "imgSize": 1080, "models": 'yolo'}

    @staticmethod
    def getbbox(file):
        # Redirect YOLO's output to a file having a list of dicts
        # returns : list of tuples (Class, {Bounding Box : x1, x2, y1, y2})
        bounding_boxes = list()
        prev = ''
        curr = ''
        with open(file, 'r') as f:
            lines = f.readlines()
            prev = ''
            curr = ''
            lines = lines[1:]
            for n in range(0, len(lines)):
                if n % 2 == 1:
                    box = [(int)(x) for x in lines[n].split()]
                    obj = lines[n - 1].split(':')[0]
                    grp = (obj, box)
                    bounding_boxes.append(grp)

        return bounding_boxes

    def F1(self, segment, curr_config, gold_file, golden_dims):
        sum = 0
        curr_file = self.getData(curr_config, self.source_file)
        for S in range(segment):
            self.getFrames(curr_file, S, 'curr')
            self.getFrames(gold_file, S, 'base')
            # self.scaleImage('curr.jpg', golden_dims)
            print("\n\n +++ YOLO Running +++ \n\n")
            self.runYOLO('curr.jpg', 'base.jpg')
            sum += self.getF1score()

        return sum / segment

    def runYOLO(self, curr_file, golden_file):
        os.chdir(self.model_path)
        os.system(
            './darknet detect cfg/yolov3.cfg yolov3.weights data/{} > {}'.format(curr_file, 'curr.txt'))
        os.system(
            './darknet detect cfg/yolov3.cfg yolov3.weights data/{} > {}'.format(golden_file, 'base.txt'))
        print("\n\n +++ YOLO Run completed +++ \n\n")
        os.chdir('/home/kshitij/btp/Papers/Chaml_impl/')
        return

    def getF1score(self):

        path = '/home/kshitij/btp/Papers/Chaml_impl/darknet'
        file_golden = ''
        file_current = ''
        for file in os.listdir(path):
            if file.endswith('.txt'):
                if file.endswith('base.txt'):
                    file_golden = file
                if file.endswith('curr.txt'):
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

                    if(x_left > x_right or y_top > y_bottom):
                        continue

                    intersection = (x_right - x_left) * (y_bottom - y_top)

                    A1 = (box_1[1][2] - box_1[1][0]) * \
                        (box_1[1][3] - box_1[1][1])
                    A2 = (box_2[1][2] - box_2[1][0]) * \
                        (box_2[1][3] - box_2[1][1])

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
        print("\n +++ True Pos = {}, Golden Config Obj. Cnt = {}, Curr Config Obj. Cnt = {} +++\n".format(
            true_positive, total_detect, total_object))
        try:
            F1 = 2 / ((1 / precision) + (1 / recall))
            print(F1)
            return F1
        except:
            ZeroDivisionError
            return 0


if __name__ == "__main__":
    chameleon()

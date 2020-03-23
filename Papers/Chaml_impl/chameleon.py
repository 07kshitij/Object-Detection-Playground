from getdata import data
import os
import pprint

class chameleon:
    def __init__(self):
        # data.getData()
        self.params = {"frameRate" : [25, 20, 10, 5, 2], 
                "imgSize" : [1080, 960, 840, 720, 600], 
                "models" : []}
        self.model_path = '/home/kshitij/darknet'
        self.accuracy = 0.8
        self.threshold = 0.9
        self.runChameleon()

    def runChameleon(self):
        # Todo : 
        # Group videos according to similarity (updateSpatial)
        # Split video to frames
        # 
        path = '../../DataSet'
        files = []
    
        for file in os.listdir(path):
            if file.endswith('.mkv'):
                files.append(file)
        itr = 0
        # for file in files:
        #     self.getFrames(os.path.join(path, file), 10, 'res0_' + str(itr))
        #     itr += 1
        self.getF1score(1, 1)
    
    def getFrames(self, file, frame = 0, outfile = 'res0'):
        os.system('ffmpeg -i {} -vf "select=eq(n\,{})" -vframes 1 {}.jpg'.format(file, frame, outfile))

    def updateSpatial(self):
        # Todo : Implement paper
        return
    
    def updateTemporal(self):
        # Todo : Implement paper
        return

    def profile(self, segment, configurations, k):
        golden_config = self.getGoldenConfig()
        curr_config = golden_config
        knob_val_to_score = dict()
        for param in self.params:
            curr_config = golden_config
            for value in self.params[param]:
                curr_config[param] = value
                F1_score = self.getF1score(curr_config, golden_config)
                knob_val_to_score[value] = F1_score

        accurate_configs = list()

        for config in configurations:
            config_score = 1
            for param in configurations.keys():
                config_score *= knob_val_to_score[param]
            if config_score >= self.accuracy:
                accurate_configs.append(config)

        return accurate_configs

    def getGoldenConfig(self):
        # Todo : See how to set params for this 
        return        

    def getbbox(self, file):
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

    def getF1score(self, curr_config, golden_config):
        # Run for all bounding boxes and calculate accuracy
        path = './darknet/'
        file_golden = ''
        file_current = ''
        for file in os.listdir(path):
            if file.endswith('.txt'):
                if file.endswith('base.txt'):
                    file_golden = file
                else:
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

                    A1 = (box_1[1][2] - box_1[1][0]) * (box_1[1][3] - box_1[1][1])
                    A2 = (box_2[1][2] - box_2[1][0]) * (box_2[1][3] - box_2[1][1])

                    IoU = (intersection) / (A1 + A2 - intersection)
                    assert IoU >= 0.0
                    assert IoU <= 1.0
                    if IoU >= self.threshold:
                        true_positive += 1
                        gold_bboxes.remove(box_2)
                        break

        precision = true_positive / total_detect
        recall = true_positive / total_object
        F1 = 2 / ((1 / precision) + (1 / recall))
        return F1

if __name__ == "__main__":
    chameleon()
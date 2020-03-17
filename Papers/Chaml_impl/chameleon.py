from getdata import data
import os

class chameleon:
    def __init__(self):
        data.getData()
        self.params = {"frameRate" : [25, 20, 10, 5, 2], 
                "imgSize" : [1080, 960, 840, 720, 600], 
                "models" : []}
        self.accuracy = 0.8
        self.threshold = 0.9
        self.runChameleon()

    def runChameleon(self):
        path = '.'
        files = []

        for file in os.listdir(path):
            if file.endswith('.mkv'):
                files.append(file)


        # for file in files:

    def updateSpatial(self):
        return
    
    def updateTemporal(self):
        return

    def profile(self, segment, configurations,  k):
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
        return        

    def getbbox(config):
        return

    def getF1score(self, curr_config, golden_config):

        precision = 0.0
        recall = 0.0

        curr_bboxes = self.getbbox(curr_config)
        gold_bboxes = self.getbbox(golden_config)

        

            bb1 = self.getbbox(curr_config)
            bb2 = self.getbbox(golden_config)

            x_left = max(bb1['x1'], bb2['x1'])
            y_top = max(bb1['y1'], bb2['y1'])
            x_right = min(bb1['x2'], bb2['x2'])
            y_bottom = min(bb1['y2'], bb2['y2'])

            if(x_left > x_right or y_top > y_bottom):
                return 0.0

            intersection = (x_right - x_left) * (y_bottom - y_top)

            A1 = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
            A2 = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

            IoU = (intersection) / (A1 + A2 - intersection)
            assert IoU >= 0.0
            assert IoU <= 1.0

        return

if __name__ == "__main__":
    chameleon()
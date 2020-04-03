Contains implementation of certain papers as a part of my B.Tech Thesis Project

**Object Detection Models Used**

1. **YOLOv3: An Incremental Improvement** (2018)  (Joseph Redmon, Ali Farhadi)  
	[[official site](https://pjreddie.com/darknet/yolo/)]

## Usage

```
git clone https://github.com/07kshitij/Object-Detection-Playground.git

cd Object-Detection-Playground/

python3 -m venv vision

source .env

cd Papers/Chaml_impl/darknet

wget https://pjreddie.com/media/files/yolov3.weights

cd ..

python3 chameleon.py

```
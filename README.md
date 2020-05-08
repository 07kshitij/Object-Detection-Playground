Contains implementation of certain papers as a part of my **B.Tech Thesis Project**

> #### Object Detection Models Used

1. **YOLOv3: An Incremental Improvement** (2018)  (Joseph Redmon, Ali Farhadi)  
	[[official site](https://pjreddie.com/darknet/yolo/)]
    
> #### Papers

 1.  **\*Chameleon: Scalable Adaptation of Video Analytics** (Junchen Jiang, Ganesh Ananthanarayanan, Peter Bodik, Siddhartha Sen, Ion Stoica) 

**\*** : Implementation in Progress
> #### Requirements 
* python 3

> #### Usage

1. ##### Clone this Repository

```
$ git clone https://github.com/07kshitij/Object-Detection-Playground.git

$ cd Object-Detection-Playground/
```
2. ##### Setup a Virtual Environment
```
$ python3 -m venv vision
```
3. ##### Set Environment Variables
Change the value of the field `HOME_PATH` in the file `.env` to the path of the directory where you've cloned this repository followed by this command

```
$ source .env
```
4. ##### Download Model Weights ( YOLOv3 )

```
$ cd Papers/Chaml_impl/darknet
$ wget https://pjreddie.com/media/files/yolov3.weights
```
 5. ##### Run the Code ( Chameleon )
```
$ cd ..
$ python3 chameleon.py
```
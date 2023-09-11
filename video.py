import torch
import numpy as np
import cv2
import time
import RPi.GPIO as GPIO




class GooseDetection:
    """
    Class implements Yolo5 model to make inferences on a youtube video using OpenCV.
    """
    
    def __init__(self, capture_index, model_name):
        """
        Initializes the class with youtube url and output file.
        :param url: Has to be as youtube URL,on which prediction is made.
        :param out_file: A valid output file name.
        """
        self.capture_index = capture_index
        self.model = self.load_model(model_name)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.confidence_arr = [False, False, False, False]
        print("\n\nDevice Used:",self.device)



    def get_video(self):
        return cv2.VideoCapture(self.capture_index)
    

    def load_model(self, model_name):
        """
        Loads custom model if provided
        Defaults to yolov5 general model if not provided
        """

        if model_name:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path = model_name, force_reload = True)
        else:
            model = torch.hub.load('ultrlytics/yolov5', 'yolov5', pretrained = True)
        return model

        

    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
     
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord


    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def goose_confidence(self):
        '''
        [T, T, T, T] FIRE
        [T, T, F, T] DONT FIRE

        Only 4 values in confidence_arr at a time
        '''
        i = 1
       
        while i < 4:
            self.confidence_arr[i-1] = self.confidence_arr[i]
            i = i +1
            
        self.confidence_arr[3] = True
        i = 0
        while i < 3:
            if(self.confidence_arr[i] == False):
                return
            i = i+1
        self.zigzag(True, False)
        self.confidence_arr = [False, False, False, False]
        
    def shoot(self):
        '''
        Where we decide what shooting type we should use
        '''
        self.zigzag(True, False)



    def zigzag(self, full, far):
        
        
        #assume servos are set to active
        if(full):
            add= 2/6
            duty = 8
        elif ~full and far:
            add = 1/6
            duty = 8.5
        elif(~full and ~far):
            add = 1/6
            duty = 9.25
        else:
            print("error: invalid zigzag input")
            return


        #start at furthest left
        tilt.ChangeDutyCycle(8.5)
        pan.ChangeDutyCycle(5.5)
        time.sleep(5)
        GPIO.output(22, 1) #laser on

        i = 0
        while(i < 6):
            GPIO.output(22, 1)
            if(i%2 == 0):
                pan.ChangeDutyCycle(3.5)
            else:
                pan.ChangeDutyCycle(5.5)
            duty = duty + add
            tilt.ChangeDutyCycle(duty)
            
            
            time.sleep(0.5)
            i = i +1
        GPIO.output(22, 0)
        


    def circle(self):
        tilt.start(8.5)  # Initialization
        pan.start(4.5)
        #start at top of circle
        pan.ChangeDutyCycle(4.5)
        tilt.ChangeDutyCycle(8.5)
        time.sleep(4)
        i = 0
        tilt_add = 1/6
        pan_add = 1/6
        pan_duty = 4.5
        tilt_duty = 8.5
        GPIO.output(22, 1)
        while i < 24:
            if i < 12:
                if(i <= 6):
                    pan_duty = pan_duty - pan_add
                    pan.ChangeDutyCycle(pan_duty)
                else:
                    pan_duty = pan_duty + pan_add
                    pan.ChangeDutyCycle(pan_duty)
                tilt_duty = tilt_duty + tilt_add
                tilt.ChangeDutyCycle(tilt_duty)
            else:
                if(i <= 18):
                    pan_duty = pan_duty + pan_add
                    pan.ChangeDutyCycle(pan_duty)
                else:
                    pan_duty = pan_duty - pan_add
                    pan.ChangeDutyCycle(pan_duty)
                tilt_duty = tilt_duty - tilt_add
                tilt.ChangeDutyCycle(tilt_duty)
            time.sleep(0.1)
            i = i + 1
        GPIO.output(22, 0)
        pan.stop()
        tilt.stop()





    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.6:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                bgr = (0, 255, 0) 
                #GPIO.output(22, 1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                #cv2.putText(frame, f"confidence: {row[4]}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bgr, 2)
                self.goose_confidence()
                
                
            #GPIO.output(22, 0)

        return frame

    
        




    def __call__(self):
        """
        This function is called when class is executed, it runs the loop to read the video frame by frame,
        and write the output into a new file.
        :return: void
        """
        cap = self.get_video()
        assert cap.isOpened()

        

        while True:
            
            
            ret, frame = cap.read()
            assert ret
            
            frame = cv2.resize(frame,(416,416))

            #start_time = time()

            results = self.score_frame(frame)

            frame = self.plot_boxes(results, frame)
           
            #end_time = time()
            #fps = 1 / np.round(end_time - start_time, 2)
            #cv2.putText(frame, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2)
            cv2.imshow("YOLOv5 Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        tilt.stop()
        pan.stop()
        GPIO.cleanup()
    
    


# Create a new object and execute.
GPIO.setmode(GPIO.BCM)

#activating GPIO pins
GPIO.setup(27, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)


tilt = GPIO.PWM(27, 50)  # PWM frequency is 50Hz
pan = GPIO.PWM(17,50)
GPIO.output(22, 0)

tilt.start(8.5)  # Initialization
pan.start(4.5)

#tilt.start(8.5)  # Initialization
#pan.start(4.5)

#GPIO.output(22, 1)


detection = GooseDetection(capture_index = 0, model_name = 'best.pt')
detection()


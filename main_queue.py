"""
Save multi-camera data into multiple videos using concurent.futures
Author:
    - Gauresh Shirodkar
Date: Jan 25, 2022
"""
import threading
import logging
import cv2
import time
import concurrent.futures
import queue

# Initialize the logging module
logging.basicConfig(level=logging.DEBUG)
logging.info("[Logging] Use logging python package")

# Flag to display video
DISPLAY_VIDEO = False

# Path for video capture
vid_1 = cv2.VideoCapture("/dev/video0")
vid_2 = cv2.VideoCapture("/dev/video2")

video_1_read_queue = []
video_1_write_queue = []
video_2_read_queue = []
video_2_write_queue = []

class ReadWriteVideo1(queue.Queue):

    def __init__(self):
        """
        Author: Gauresh Shirodkar
        Date: Jan 25, 2022
        Function Description: Initialize ROS node with it's parameters and topics
        """

        super().__init__(maxsize=0)

        # Variables
        self.frame_1 = None
        self.start_time_1 = None

        # define a video capture object
        self.result_1 = cv2.VideoWriter('filename_1.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (640, 480))

    def read_video_1(self, event_1):
        """
        Author: Gauresh Shirodkar
        Date: Jan 25, 2022

        Method Description: Read frames from video
        param : None
        return : None
        """
        self.start_time_1 = time.perf_counter()

        # Capture the video frame
        ret_1, self.frame_1 = vid_1.read()
        if ret_1:
            logging.debug('Reading Video 1 .....')

            # Display the resulting frame
            if DISPLAY_VIDEO:
                cv2.imshow('frame_1', self.frame_1)
            logging.debug('Video 1 image dimension %s', str(self.frame_1.shape))

            data = self.frame_1
            video_1_write_queue.append(data)
            self.put(data)
            logging.debug("Length of video_1_write_queue : %s", str(len(video_1_write_queue)))
            logging.debug("Event Read: %s", str(not event_1.is_set()))
            event_1.clear()

        else:
            logging.error('Problem with video 1')


    def write_video_1(self, event_1):
        """
        Author: Gauresh Shirodkar
        Date: Jan 25, 2022

        Method Description: Method to write video
        param : None
        return : None
        """
        data = self.get()
        self.result_1.write(data)
        video_1_read_queue.append(data)
        logging.debug("Length of video_1_read_queue : %s", str(len(video_1_read_queue)))
        logging.debug("Event Write: %s", str(not event_1.is_set()))

        logging.debug('FPS - Video 1 : %s', str(1/(time.perf_counter() - self.start_time_1)))
        time.sleep(0.03)


class ReadWriteVideo2(queue.Queue):

    def __init__(self):
        """
        Author: Gauresh Shirodkar
        Date: Jan 25, 2022
        Function Description: Initialize ROS node with it's parameters and topics
        """

        super().__init__(maxsize=0)

        # Variables
        self.frame_2 = None
        self.start_time_2 = None

        # define a video capture object
        self.result_2 = cv2.VideoWriter('filename_2.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (640, 480))


    def read_video_2(self, event_2):
        """
        Author: Gauresh Shirodkar
        Date: Jan 25, 2022

        Method Description: Read frames from video
        param : None
        return : None
        """
        self.start_time_2 = time.perf_counter()

        # Capture the video frame
        ret_2, self.frame_2 = vid_2.read()
        if ret_2:
            logging.debug('Reading Video 2 .....')

            # Display the resulting frame
            if DISPLAY_VIDEO:
                cv2.imshow('frame_2', self.frame_2)
            logging.debug('Video 2 image dimension %s', str(self.frame_2.shape))

            data = self.frame_2
            video_2_write_queue.append(data)
            self.put(data)
            logging.debug("Length of video_2_write_queue : %s", str(len(video_2_write_queue)))
            logging.debug("Event Read: %s", str(not event_2.is_set()))
            event_2.clear()

        else:
            logging.error('Problem with video 2')


    def write_video_2(self, event_2):
        """
        Author: Gauresh Shirodkar
        Date: Jan 25, 2022

        Method Description: Method to write video
        param : None
        return : None
        """

        data = self.get()
        self.result_2.write(data)
        video_2_read_queue.append(data)
        logging.debug("Length of video_1_read_queue : %s", str(len(video_2_read_queue)))
        logging.debug("Event Write: %s", str(not event_2.is_set()))

        logging.debug('FPS - Video 2 : %s', str(1 / (time.perf_counter() - self.start_time_2)))


def video_1_read(read_and_write_video1, event_1):

    while vid_1.isOpened() and (not event_1.is_set()):
        read_and_write_video1.read_video_1(event_1)
        logging.debug("While : video_1_read ..... ")
    logging.debug("video_1_read ..... ")


def video_1_write(read_and_write_video1, event_1):

    while vid_1.isOpened() or (not event_1.is_set()):
        read_and_write_video1.write_video_1(event_1)
        logging.debug("While : video_1_write ..... ")
        logging.debug("  ")
    logging.debug("video_1_write ..... ")

def video_2_read(read_and_write_video2, event_2):

    while vid_2.isOpened() and (not event_2.is_set()):
        read_and_write_video2.read_video_2(event_2)
        logging.debug("While : video_2_read ..... ")
    logging.debug("video_2_read ..... ")


def video_2_write(read_and_write_video2, event_2):

    while vid_2.isOpened() or (not event_2.is_set()):
        read_and_write_video2.write_video_2(event_2)
        logging.debug("While : video_2_write ..... ")
        logging.debug("  ")
    logging.debug("video_2_write ..... ")


# Entry point
if __name__ == '__main__':
    read_and_write_video1 = ReadWriteVideo1()
    read_and_write_video2 = ReadWriteVideo2()
    event_1 = threading.Event()
    event_2 = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        ex.submit(video_1_read, read_and_write_video1, event_1)
        ex.submit(video_1_write, read_and_write_video1, event_1)
        ex.submit(video_2_read, read_and_write_video2, event_2)
        ex.submit(video_2_write, read_and_write_video2, event_2)

        time.sleep(0.03)
        event_1.set()
        time.sleep(0.03)
        event_2.set()

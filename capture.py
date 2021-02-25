#!/usr/bin/env python3

"""
    A script to capture the speaker audio and screen

    TODO: Get audio stream
    TODO: provide video stream
"""

import numpy as np
import cv2

import time
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, Wnck, GdkPixbuf

def windows2png():
    """Capture all windows and save to file
    """
    screen = Gdk.Screen.get_default()
    for i, window in enumerate(screen.get_window_stack()):
        pb = Gdk.pixbuf_get_from_window(window, *window.get_geometry())
        pb.savev("{}.png".format(i), "png", (), ())

def array_from_pixbuf(p):
    """Convert from GdkPixbuf to numpy array"

    Args:
        p (GdkPixbuf): The GdkPixbuf provided from some window handle

    Returns:
        ndarray: The numpy array arranged for the pixels in height, width, RGBA order
    """
    w,h,c,r=(p.get_width(), p.get_height(), p.get_n_channels(), p.get_rowstride())
    assert p.get_colorspace() == GdkPixbuf.Colorspace.RGB
    assert p.get_bits_per_sample() == 8
    if  p.get_has_alpha():
        assert c == 4
    else:
        assert c == 3
    assert r >= w * c
    a=np.frombuffer(p.get_pixels(),dtype=np.uint8)
    if a.shape[0] == w*c*h:
        return a.reshape( (h, w, c), order = 'C' )
    else:
        b=np.zeros((h,w*c),'uint8')
        for j in range(h):
            b[j,:]=a[r*j:r*j+w*c]
        return b.reshape( (h, w, c) )

def array_to_cv2(pix_array, colorspace=cv2.COLOR_RGB2BGR):
    return cv2.cvtColor(pix_array, colorspace)

class WindowCapture():
    def __init__(self, window_title="Zoom Meeting", activation_delay = 0.1):
        """Captures from GUI window of specified title. Serves as a handle on 
            that window as long as it is still available. If the window is 
            covered up by another window after init finishes, the window can
            still be captured from. 
            
            Thie captures from specific Gtk windows using Wnck, which means
            it is likely only compatible on Linux gui environments.
            Wnck API Reference: https://lazka.github.io/pgi-docs/Wnck-3.0/classes/Screen.html
            Gdk API Reference: https://lazka.github.io/pgi-docs/Gdk-3.0/classes/Screen.html

        Args:
            window_title (str, optional): Name of the window to capture from. 
                Defaults to "Zoom Meeting".
            activation_delay (float, optional): How long in seconds to wait for
                a window to be activated so that the correct handle will be 
                acquired. If the wrong window is captured, increase this number.
        """
        self.window, self.window_title, self.activation_delay = None, None, None
        Gtk.init([])  # necessary since we're not using a Gtk.main() loop
        self.set_window(window_title=window_title,activation_delay=activation_delay)

    def _get_active_window_(self):
        """Gets a handle on the active Gdk window.

        Returns:
            Gdk.Window: The window handle.
        """
        screen = Gdk.Screen.get_default()
        return screen.get_active_window()

    def _activate_window_(self):
        """This function uses Wnck to set a window as the active/focused window on 
            the user's screen. It is especially useful when combined with Gdk to 
            get active window pixels. Note: Gdk has no direct way of accessing a 
            window by title.

        Returns:
            bool: True if window found and activated, else False
        """
        screen = Wnck.Screen.get_default()
        screen.force_update()  # recommended per Wnck documentation
        found_win = False
        for window in screen.get_windows():
            name = window.get_name()
            if (name == self.window_title):
                found_win = True
                window.activate(0)
                time.sleep(self.activation_delay)

                ##should be the proper solution but Wnck/Pygi is kinda trash; 
                ##the active boolean never returns true and proper activate times fail.
                # window.activate(int(time.time()))
                # while(not window.is_active()):
                #     time.sleep(self.activation_delay)
                break

        # clean up Wnck (saves resources, check documentation)
        window = None
        screen = None
        Wnck.shutdown()
        return found_win
    
    def set_window(self, window_title, activation_delay = 0.1):
        """Set the window we are going to capture from

        Args:
            window_title ([type]): [description]
            activation_delay (float, optional): How long in seconds to wait for
                a window to be activated so that the correct handle will be 
                acquired. Some computers may take longer to do this. Defaults to 0.1.
                NOTE: This delay is a workaround for Wnck's inability to get window state.

        Raises:
            ValueError: [description]
        """
        self.window_title = window_title
        self.activation_delay = activation_delay
        if (self._activate_window_()):
            self.window = self._get_active_window_()
        else:
            raise ValueError(f'Unable to get/find window with title "{self.window_title}" for capture.')


    def test_fps(self, frames = 100):
        """Gives an estimate of the frames per second capture rate
        Args:
            frames (int, optional): Number of frames to aquire for test. Defaults to 100.
        Returns:
            float: The determined FPS for capture.
        """
        i = 1
        start = time.time()
        while (i <= frames):
            pb = Gdk.pixbuf_get_from_window(self.window, *self.window.get_geometry())
            i += 1
        fps = (frames / (time.time() - start))
        print("--- achieved %s fps ---" % fps)
        return fps

    def get_cv_img(self):
        """Get a new frame from window in OpenCV format.
        Returns:
            cv::_OutputArray: Most recent window frame in cv output format.
        """
        return cv2.cvtColor(self.get_numpy_img(), cv2.COLOR_RGB2BGR) # cv2 works in BGR colorspace

    def get_numpy_img(self):
        """Get a new frame from window as a Numpy array in RGBA format
        Returns:
            ndarray: (Height, Width, Channels) shaped array
        """
        pb = Gdk.pixbuf_get_from_window(self.window, *self.window.get_geometry())
        return array_from_pixbuf(pb)


    def save_window_png(self, filename = "0"):
        """Save current window frame to png
        Args:
            filename (str, optional): Filename to save as (without extension). Defaults to "0".
        """
        pb = Gdk.pixbuf_get_from_window(self.window, *self.window.get_geometry())
        pb.savev(f"{filename}.png", "png", (), ())



class PartcipantDetector():
    def __init__(self,image, epsilon = 0.01, detect_rate = 1, display_box = False, debug = False,
        gallery_color_rgba = np.array([26,26,26,255]), active_color_rgba = np.array([35,217,89,255]), 
        crop_percentX = 0.99, crop_percentY = 0.89, aspectRatio = 1.77):        
        """Detects participants in a video call and provides frames/video from 
            that call. Current model assumes use of Zoom in gallery mode.
        
        #TODO separate detection code from box detection code (make use of detect_rate)
        #TODO optimize this for frequent function calls/video streaming. 
            Possible options for optimization include: scaling down image before
            running box detection, only running detection when major image changes
            occur.

        Args:
            image (ndarray): The RGBA image to work off of.
                The array values are expected to be readonly.
            epsilon (float, optional): How sensitive the box detector is.
                A higher value results in boxes with imperfections being detected
                more often. Defaults to 0.1.
            detect_rate (int, optional): How often in Hz to check participant 
                window positions and active participant. Defaults to 1 Hz.
            display_box (bool, optional): Whether to display detection boxes 
                around frames. Defaults to False.
            debug (bool, optional): Activates a number of debug outputs 
            gallery_color_rgba (ndarray, optional): The RGBA color surrounding the participant window. 
                Defaults to np.array([26,26,26,255]) which is the Zoom default.
            active_color_rgba (ndarray, optional): The primary color of the box
                 that highlights the active user.. Defaults to np.array([35,217,89,255]).
            crop_percentX (float, optional): How much extra content to keep 
                from image window width-wise; lower percents remove more from 
                the right side. Defaults to 0.99.
            crop_percentY (float, optional): How much extra content to keep 
                from image window height-wise; lower percents remove more from 
                the bottom side. Defaults to 0.89.
            aspectRatio (float, optional): The predicted aspect ratio of 
                participant videos. Used to filter out false positives. Defaults to 1.77.
        """        
        self.img_arr = image
        self.epsilon = epsilon
        self.detect_rate = detect_rate
        self.display_box = display_box
        self.debug = debug
        self.gallery_color = gallery_color_rgba
        self.active_color = active_color_rgba
        self.crop_percentX = crop_percentX
        self.crop_percentY = crop_percentY
        self.aspectRatio = aspectRatio

    def detect_new(self,image):
        self.img_arr = image
        self.detect()

    def detect(self):
        #crop out extra bars around window edges
        self.img_arr = self.img_arr[0:int(self.img_arr.shape[0]*self.crop_percentY),
                                    0:int(self.img_arr.shape[1]*self.crop_percentX),...] 
        if self.debug: print(f"Cropped image array shape: {self.img_arr.shape}")
        img = array_to_cv2(self.img_arr,cv2.COLOR_RGB2BGR)
        masked = self.img_arr.copy()
        
        gal_mask = (self.img_arr == self.gallery_color).all(-1)
        
        masked[gal_mask] = 255
        masked[np.logical_not(gal_mask)] = 0
        
        ##We can find the active partipant using the color...
        # active_mask = (self.img_arr == self.active_color).all(-1)
        # masked[...,:4][active_mask] = [0,0,0,0]
        
        #reference: https://stackoverflow.com/a/11427501/5715374
        gray = array_to_cv2(masked,cv2.COLOR_RGB2GRAY)
        if self.debug: cv2.imshow("Full", gray)

        _,thresh = cv2.threshold(gray,127,255,1)
        contours,_ = cv2.findContours(thresh,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours,key=cv2.contourArea,reverse=True)
        rects = [] # a list of found rects in descending (greatest first) area order
        
        #find the interesting rectangles
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt,self.epsilon*cv2.arcLength(cnt,True),True)
            if len(approx)==4: #rectangles have 4 sides
                area = cv2.contourArea(cnt)
                # print(cv2.contourArea(cnt))
                if area < 100: #ignore tiny rectangles
                    continue
                _,_,w,h = cv2.boundingRect(cnt)
                ar = w/h
                if (ar > 3*self.aspectRatio or ar < self.aspectRatio/3): #bad aspect ratio
                    if self.debug: print(f"rejected aspect ratio of {ar}")
                    continue
                if self.debug: print(f"Aspect ratio = {ar}")
                rects.append(cnt)

        first = True
        color = (0,0,255)
        display = False
        participants = []
        for rect in rects:
            x,y,w,h = cv2.boundingRect(rect)
            participants.append(img[y:y+h, x:x+w]) #crop participant image to bounding box.
            #the first participant has the largest area and is thus most likely the active participant
            if first: 
                first = False
                color = (0,255,0)
            else:
                color = (0,0,255)
            if self.display_box:
                cv2.drawContours(img,[rect],0,color,2)
        if self.debug: print(f"Detected {len(rects)} participants.")
        return participants

def test_pipeline_fps(wc, pd, frames = 100):    
    """Gives an estimate of the frames per second capture rate
        for the image capture and box detection pipeline
    Args:
        wc (WindowCapture): A handle on the current window capture
        pd (Participant): A handle on the participant detector
        frames (int, optional): Number of frames to aquire for test. Defaults to 100.
    Returns:
        float: The determined FPS for capture.
    """
    i = 1

    start = time.time()
    while (i <= frames):
        pd.detect_new(wc.get_numpy_img())
        i += 1
    fps = (frames / (time.time() - start))
    print("--- achieved %s fps ---" % fps)
    return fps


#TODO: unsorted participant list/self is always user 0 (but hold onto active participant info), publish separate audio, video, and info streams with same topic order, with arrays of participants for each
def main():

    x = WindowCapture(window_title="Zoom Meeting")
    # x.test_fps()
    detector = PartcipantDetector(x.get_numpy_img(), debug=True, display_box=False)
    participants = detector.detect()
    # test_pipeline_fps(x,detector)


    for i, part in enumerate(participants):
        cv2.imshow(f"Participant {i}",part)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    x = None

if __name__ == "__main__":
    main()
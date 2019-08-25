## ======== DESCRIPTION ======== ##

# Center for Research and Advanced Studies of the National Polytechnic
# Institute of Mexico (CINVESTAV-IPN)

# This program is the base of a graphic user interface to control a optical
# digital fluorescence microscope powered by a Raspberry Pi and camera module.
# The core code is an open example that has been modified. This code can be
# found in the next link:
# http://smokespark.blogspot.mx/2015/05/a-python-graphical-user-interface-for.html

# The goal of this project is to use this GUI as an interface for in situ
# research and observation of biological samples in brightfield and three
# fluorescence channels.
# The user will be able of control exposure time, AWB, ISO, brightness and
# other parameters for image acquisition.
# Also, it is possible to save the image in different formats.

# People in charge of this project:
# Samuel Bernardo Tristan-Landin, M.Sc.
# Alan Gonzalez-Suarez, Ph.D.
# Rocio Jimenez-Valdez, Ph.D.
# Jose Luis Garcia-Cordero, Ph.D.


## ======== PRELIMINARY CONSIDERATIONS AND INSTRUCTIONS ======== ##

# Please follow this instructions prior to GUI use to ensure its functionality.

# 1. This GUI is intended to use in Raspbian and Python 2.7, make sure to
#    compile using this OS and Python version.
#    NOTE: New versions of Raspbian don't have Python 2 IDLE installed.
#    i)   Go to "Preferences / Add/Remove Software".
#    ii)  Search and install package "IDE for Python (v2.7) using Tkinter".
#    iii) Go to "Preferences / Main Menu Editor / Programming".
#    iv)  Check "IDLE (using Python-2.7)" box.
#    v)   Go to GUI file and right click on it.
#    vi)  On "Open with:" select "IDLE (using Python-2.7)".

# 2. Install OpenCV library.
#    i)   Open Terminal.
#    ii)  Run following commands in this specific order:
#        ~ $ sudo sudo apt-get update
#        ~ $ sudo sudo apt-get upgrade
#        ~ $ sudo apt install python-opencv

# 3. Install Pytho9n ImagingTk using the following command on Terminal:
#        ~ $ sudo sudo apt-get install python-imaging-tk

# 4. Verify the version of the Raspberry Pi Camera you have, because the
#    resolution in the script is managed depeding on the model.
#    In this case, Raspberry Pi Camera V2 (8MPx, 3280x2464 px). We strongly
#    recommend the use of this camera due to the design of the optical system.

# 5. In order to use the Power LEDs for the fluorescence fields, use a proper
#    interface to isolate the control circuit from the power circuit, such as
#    an optocoupler or a relay. Note that Raspberry Pi does not have enough
#    power to correctly feed the Power LEDs.

# 6. Split the memory of the Raspberry Pi to have enoough buffer to capture
#    image with the full resolution of the CMOS sensor.
#    i)   Write the following commands in the terminal:
#        ~ $ sudo raspi-config
#    ii)  Navigate with your keyboard arrows, select option number 7,
#         "Advanced Options", then option A3, "Memory Split".
#         Erase the number and write down 256 (MB).

# If images show a warm color or color is not even, follow the step bellow:

# 7. Write the following commands in the terminal:
#        ~ $ sudo rpi-update
#    This updates Raspberry Pi kernel.


## ======== DECLARING LIBRARIES ======== ##

import Tkinter as tk
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from fractions import Fraction
import tkMessageBox as messagebox
import tkFileDialog
import pygame
import time
import cv2
import threading
import picamera
import picamera.array
import RPi.GPIO as GPIO  
import numpy as np
import io
import os
from datetime import datetime, timedelta

# Bright Field LED pin configuration.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pin = 18
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)

# Blue Fluorescence excitation LED pin (UV LED) configuration.
pin3 = 23
GPIO.setup(pin3,GPIO.OUT)
GPIO.output(pin3, GPIO.LOW)

# Green Fluorescence excitation LED pin (Blue LED) configuration.
pin2 = 24
GPIO.setup(pin2,GPIO.OUT)
GPIO.output(pin2, GPIO.LOW)

# Red Fluorescence excitation LED pin (Green-Ambar LED) configuration.
pin4 = 25
GPIO.setup(pin4,GPIO.OUT)
GPIO.output(pin4, GPIO.LOW)

# Declaring Camera
camera = picamera.PiCamera()
previewstatus = 0
numImages = 1
timelapse = 0


## camera.hflip = True
camera.vflip = True
captureCount = 0


## ======== THREADED FUNCTIONS DECLARATION ======== ##
# Creating threading classes. 
# The use of threads make the program more stable by preventing it to freeze
# when performing a looped action, such as taking a single photo or a time
# lapse. Also, this allows to perform different calculations in parallel.

class imageSequenceThread(threading.Thread):
        def __init__(self, timelapse):
                threading.Thread.__init__(self)
                self.timelapse = timelapse
                self._stop = threading.Event()
        def run(self):
                while not self._stop.isSet():
                        GPIO.output(pin, GPIO.HIGH)
                        camera.resolution = (3280,2464)
                        timestr = time.strftime("%d-%m-%H-%M-%S-img")
                        camera.capture(timestr +'.png')
                        GPIO.output(pin, GPIO.LOW)
                        time.sleep(self.timelapse)
        def stop(self):
                self.flag = False

# Previous while loop inside the thread captures timelapse images.
# First, tunrs on the LED, then presets the camera resolution and last captures
# the image.
# Once the image is captured, the program waits a defined time to take the next
# picture.
# This time lapse works only for brightfield.


## ======== DEFINIG FUNCTIONS ======== ##
# Here we define the functions for the camera control.

def centre_window(w, h):
	ws = root.winfo_screenwidth()
	hs = root.winfo_screenheight()
	x = (ws/2)
	y = (hs/2)
	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	
def brightnessScale(value):
        camera.brightness = int(value)

def contrastScale(value):
        camera.contrast = int(value)
        
def saturationScale(value):
        camera.saturation = int(value)
        
def exposureTimeScale(value):
# This command controls the exposure time in the RasPi Camera.
        camera.shutter_speed = int(value)*1000

def sharpnessScale(value):
        camera.sharpness = int(value)
# Preset values for white balance of the camera. Each observation mode has
# its own gains.
# Do not change unless it is necessary. You can use a scale bar (commented
# down in the script) to tune these gains.

def awb_modes(value):
        if value == "Red EmF":
                camera.awb_mode= 'off'
                camera.awb_gains = (1.1,1.1)
        if value == "Green EmF":
                camera.awb_mode= 'off'
                camera.awb_gains = (1.2,1.2)
        if value == "B Field":
                camera.awb_mode= 'off'
                camera.awb_gains = (1.5,1.2)
        elif value != "Red EmF" and value != "Green EmF" and value != "B Field":
                camera.awb_mode = value


# This function is used to tune the gains of the white balance for different
# filters.
# Use this only if it is necesary. Do not forget to enable the scale bars in
# the GUI Section (also commented).

### def setAWB_gains():
###        value1 = g1.get()
###        value2 = g2.get()
###        camera.awb_mode = "off"
###        camera.awb_gains = (value1, value2)
###        preview()


# This function helps to select an exposure mode similar to the ones you can
# use in a digital camera.
def exposure_modes(value):
        camera.exposure_mode= value

        
# This function helps to select an effect similar to the ones you can use in a digital camera.        
def effects(value):
        camera.image_effect = value


# This function helps you to manually modify the ISO sensibility.   
def isocam(value):
        if value == "auto":
                camera.iso = 0
        else:
                camera.iso = int(value)


# This function helps you to manually rotate the image.  
def rotate():
    camera.rotation += 90
    print "Rotation", camera.rotation, "degrees"
    preview()


# This function helps you to make an horizontal flip to the image.
def hflip():
    value = hon.get()
    if value == False:
        camera.hflip = False
    else:
        camera.hflip = True


# This function helps you to make a vertical flip to the image.
def vflip():
    value = von.get()
    if value == False:
        camera.vflip = False
    else:
        camera.vflip = True


# This function defines parameters for the live preview of the camera. It
# allows you to observe the samples in real time.
def previewCamera():
    global previewstatus
    global var1
    global var5

# First, the script verifies the status of the button. Then, sets the
# configuration of the live preview.
    if previewstatus == 0:
        previewstatus = 1
        previewbtn_text.set("Preview Off")
        camera.resolution = (3280,2464)
        camera.preview_fullscreen = False
        camera.preview_window = (700, 200, 510, 384)
        camera.video_stabilization = TruLEDstatus = True
        camera.brightness=sBright.get()
        camera.contrast=sContrs.get()
        camera.saturation=sSat.get()
        awb_modes(var1.get())
        isocam(var5.get())
        camera.start_preview()
        
    else:
        camera.stop_preview()
        previewbtn_text.set("Preview On")
        previewstatus = 0

        
# This function defines the the paramters to capture and image. The parameters
# can be changed with the respetive scale bars or the exposure mode.
# Images are automatically stored in TIFF format.

def still():
    global img
    global imgaux
    global captureCount
    global var1
    global var5
    camera.shutter_speed = int(sExpT.get())* 1000
    camera.brightness=sBright.get()
    camera.contrast=sContrs.get()
    camera.saturation=sSat.get()
    isocam(var5.get())
    awb_modes(var1.get())
    camera.resolution = (3280,2464)
    # Storing capture on a matrix in order to be used with OpenCV.
    img = picamera.array.PiRGBArray(camera, size = (3280,2464))
    camera.capture(img, 'bgr', resize = (3280,2464))
    # Storing an auxiliar image to be used as display on Canvas.
    imgaux = img.array
    res = cv2.resize(imgaux, (510,384))
    img2 = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    img2FromArray = Image.fromarray(img2)
    imgtk = ImageTk.PhotoImage(image =img2FromArray)
    canvas.itemconfig(img_canvas,imag = imgtk)
    canvas.imgtk = imgtk
    # Automatic Storage in TIFF format.
    captureCount += 1
    strc = str(captureCount)
    extStr = ".tiff"
    cv2.imwrite('image' + strc + extStr, imgaux)


# The next 3 functions help to perform a gamma correction of the most recently
# taken image.
# The preview of the gamma corrected image is shown in an alternate window.

def gamma_value(value):
        global gamma
        gamma = float(value)

def gamma_correction(imgGammaAux, value):
        table = np.array([((i / 255.0) ** value) * 255
        for i in np.arange(0, 256)]).astype("uint8")
        # Build a table mapping the pixel values [0, 255] to their adjusted
        # gamma values.
        return cv2.LUT(imgGammaAux, table)
        # Apply gamma correction using the lookup table.

def gammaPreview():
        global gammaImg
        gammaWindow = Toplevel()
        ws = gammaWindow.winfo_screenwidth()
        hs = gammaWindow.winfo_screenheight()
        x = (ws/2)
        y = (hs/2)
        gammaWindow.geometry('%dx%d+%d+%d' % (600, 450, x, y))

        imgG = Image.open('start.gif')
        imgG = imgG.resize((480/2, 594/2), Image.ANTIALIAS)
        imgGc = ImageTk.PhotoImage(imgG)
        canvasframe2 = Frame(gammaWindow, width = 600, height = 400)
        canvasframe2.grid(row=0, column=2, sticky=W+E+N+S)
        canvas2=Canvas(canvasframe2, width=510, height=383)
        img_canvas2=canvas2.create_image(510/2,400/2,image = imgGc, anchor = CENTER)
        canvas2.grid(row=0, column=0)

        gframe2 = Frame(gammaWindow, width = 600, height = 50)
        gframe2.grid(row=1, column=2, sticky=W+E+N+S)
        gammalabel = Label(gframe2, text="Gamma Correction")
        gammalabel.grid(row=1, column=0)
        setGamma = Scale(gframe2, from_=0, to=3, resolution = 0.5,orient=HORIZONTAL, command = gamma_value)
        setGamma.grid(row=1, column=1)
        
        var8g = StringVar(gammaWindow)
        var8g.set("TIFF") # initial value
        optionExp = OptionMenu(gframe2, var8g, 'TIFF', 'JPEG', 'PNG', 'BMP', 'DATA')
        optionExp.grid(row =1, column = 3)
        var8label = Label(gframe2, text="File Options")
        var8label.grid(row=1, column=2)
        
        exportbtn_text = StringVar(gammaWindow)
        exportbtn = Button(gframe2, textvariable=exportbtn_text, command=export_image_corrected)
        exportbtn_text.set("Export Image")
        exportbtn.grid(row=1, column=4)

        try:
                gammaImg = gamma_correction(imgaux,2.4)
                res = cv2.resize(gammaImg, (510,384))
                gammaImg2 = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
                img2FromArrayG = Image.fromarray(gammaImg2)
                imgtk2 = ImageTk.PhotoImage(image =img2FromArrayG)
                canvas2.itemconfig(img_canvas2,imag = imgtk2)
                canvas2.imgtk2 = imgtk2

        except:
                messagebox.showerror("Error", "Image has not been taken, please take an image.")
                gammaWindow.destroy()

        gammaWindow.mainloop()

               
# The next 4 functions define the control of the switching on/off for the LEDs.
def led():
    if GPIO.input(pin):
        GPIO.output(pin,GPIO.LOW)
        ledbtn_text.set("  BrFld OFF  ")
        print "LED off"

    else:
        camera.framerate = 30
        GPIO.output(pin,GPIO.HIGH)
        GPIO.output(pin2,GPIO.LOW)
        GPIO.output(pin3,GPIO.LOW)
        GPIO.output(pin4,GPIO.LOW)
        ledbtn_text.set("  BrFld ON  ")
        gfluorledbtn_text.set("  BL OFF  ")
        bfluorledbtn_text.set("  UVL OFF  ")
        rfluorledbtn_text.set("  GL OFF  ")
        # Setting parameters to default configuration for the channel.
        sExpT.set(0)
        sSharp.set(0)
        sSat.set(0)
        sContrs.set(0)
        sBright.set(50)
        var1.set("B Field")
        var3.set("auto")
        var5.set("400")
        isocam(var5.get())
        awb_modes(var1.get())
        exposure_modes(var3.get())
        print "WhiteLED on"

def GREENFluorled():
    if GPIO.input(pin2):
        GPIO.output(pin2,GPIO.LOW)
        gfluorledbtn_text.set("  BL OFF  ")
        print "LED off"

    else:
##        var5.set("200")
        isocam(var5.get())
        time.sleep(3)
        camera.framerate = 1
        GPIO.output(pin2,GPIO.HIGH)
        GPIO.output(pin,GPIO.LOW) 
        GPIO.output(pin3,GPIO.LOW)
        GPIO.output(pin4,GPIO.LOW)
        ledbtn_text.set("  BrFld OFF  ")
        gfluorledbtn_text.set("  BL ON  ")
        bfluorledbtn_text.set("  UVL OFF  ")
        rfluorledbtn_text.set("  GL OFF  ")
        print "LED on"
        # Setting parameters to default configuration for the channel.
##        sExpT.set(700)
##        sSharp.set(0)
##        sSat.set(0)
##        sContrs.set(0)
##        sBright.set(50)
        var1.set("Green EmF")
##        var3.set("off")
##        awb_modes(var1.get())
##        exposure_modes(var3.get())

def BLUEFluorled():
    if GPIO.input(pin3):
        GPIO.output(pin3,GPIO.LOW)
        bfluorledbtn_text.set("  UVL OFF  ")
        print "LED off"
        camera.awb_mode = "off"
        camera.awb_gains = (1.2, 1.2)

    else:
##        var5.set("200")
        isocam(var5.get())
        time.sleep(3)
        camera.framerate = 1
        GPIO.output(pin3,GPIO.HIGH)
        GPIO.output(pin,GPIO.LOW) 
        GPIO.output(pin2,GPIO.LOW)
        GPIO.output(pin4,GPIO.LOW)
        ledbtn_text.set("  BrFld OFF  ")
        gfluorledbtn_text.set("  BL OFF  ")
        bfluorledbtn_text.set("  UVL ON  ")
        rfluorledbtn_text.set("  GL OFF  ")
        print "LED on"
        # Setting parameters to default configuration for the channel.
##        sExpT.set(500)
##        sSharp.set(0)
##        sSat.set(0)
##        sContrs.set(0)
##        sBright.set(50)
        var1.set("Green EmF")
##        var3.set("off")
##        exposure_modes(var3.get())
##        awb_modes(var1.get())
        

def REDFluorled():
    global var1
    
    if GPIO.input(pin4):
        GPIO.output(pin4,GPIO.LOW)
        rfluorledbtn_text.set("  GL OFF  ")
        print "LED off"

    else:
##        exposure_modes("auto")
##        var5.set("200")
        isocam(var5.get())
        time.sleep(3)
        var3.set("off")
        exposure_modes(var3.get())
        camera.framerate = 1
        GPIO.output(pin4,GPIO.HIGH)
        GPIO.output(pin,GPIO.LOW) 
        GPIO.output(pin2,GPIO.LOW)
        GPIO.output(pin3,GPIO.LOW)
        ledbtn_text.set("  BrFld OFF  ")
        bfluorledbtn_text.set("  UVL OFF  ")
        gfluorledbtn_text.set("  BL OFF  ")
        rfluorledbtn_text.set("  GL ON  ")
        print "LED on"
        # Setting parameters to default configuration for the channel.
##        sExpT.set(500)
##        sSharp.set(0)
##        sSat.set(0)
##        sContrs.set(0)
##        sBright.set(50)
        var1.set("Red EmF")
##        awb_modes(var1.get())


#The next 2 functions define the start and the stop of the time lapse captures.
#You can change the delay time with the respctive scale bar, which is in minutes.
def startLapse():
        try:
                timelapse = yy.get()*60
                global thread1
                thread1 = imageSequenceThread(timelapse)
                thread1.start()
                TLButton.config(state = DISABLED)
                stopTLButton.config(state = NORMAL)
                print "Starting image timelapse sequence\n"
                print "Image timelapse sequence: Started\n"
        except:
                print "Can't start image timelapse sequence!!"

def stopLapse():
        try:
                if thread1.isAlive():
                        thread1._stop.set()
                        TLButton.config(state = NORMAL)
                        stopTLButton.config(state = DISABLED)
                        GPIO.output(pin, GPIO.LOW)
                        print "Stopping image sequence"
                        print "Please wait until the last cycle finishes..."
                messagebox.showwarning("Wait", "Image Sequence Stopped")
                print "Image timelapse sequence: stopped"
        except:
                print "Can't stop image timelapse sequence!!"
                GPIO.output(pin, GPIO.LOW)
                camera.stop_preview()
                      
def filenames():
	frame = 0
	fileName = time.strftime("/home/pi/Desktop/images/%d-%m-%Y:%H:%M:%S",time.localtime())
	while frame < 1:
		yield '%s%00d.jpg' % (fileName, frame)
		frame += 1

		
# The next 2 functions help to export the images in different formats, for both
# the original imagen and the gamma corrected one.
def export_image():
        global imgaux
        global captureCount
        
        captureCount += 1
        strc = str(captureCount)
        if var8.get() == "PNG":
                extStr = ".png"
        if var8.get() == "JPEG":
                extStr = ".jpeg"
        if var8.get() == "TIFF":
                extStr = ".tiff"
        if var8.get() == "DATA":
                extStr = ".data"
        if var8.get() == "BMP":
                extStr = ".bmp"

        cv2.imwrite('image' + strc + extStr, imgaux)

def export_image_corrected():
        global gammaImg
        global captureCount
        strc = str(captureCount)
        if var8.get() == "PNG":
                extStr = ".png"
        if var8.get() == "JPEG":
                extStr = ".jpeg"
        if var8.get() == "TIFF":
                extStr = ".tiff"
        if var8.get() == "DATA":
                extStr = ".data"
        if var8.get() == "BMP":
                extStr = ".bmp"

        cv2.imwrite('gc-image' + strc + extStr, gammaImg)


# This function helps to the correctly closing of the program, by turning off
# the LEDs and camera.
def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
                GPIO.output(pin, GPIO.LOW)
                GPIO.output(pin2, GPIO.LOW)
                GPIO.output(pin3, GPIO.LOW)
                GPIO.output(pin4, GPIO.LOW)
                camera.close()
                root.destroy()
                
def about_sw():
        messagebox.showinfo("About", "On behalf of CINVESTAV-IPN, thanks for using our program.          Bio-ARTS Laboratory, Monterrey, Mexico 2017-2019.")

def contact():
        messagebox.showinfo("Contact", "Contact us via e-mail: josegc@gmail.com, slandintl@gmail.com")

def troubleshooting():
        trbshWindow = Tk()
        trbshWindow.title("Troubleshooting")
        ws = trbshWindow.winfo_screenwidth()
        hs = trbshWindow.winfo_screenheight()
        x = (ws/2)
        y = (hs/2)
        trbshWindow.geometry('%dx%d+%d+%d' % (600, 450, x, y))
        S = tk.Scrollbar(trbshWindow)
        T = tk.Text(trbshWindow, height=600, width=450)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        T.pack(side=tk.LEFT, fill=tk.Y)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        T.tag_configure('normal', font=('Arial', 12))
        quote = """
FAQ - Trobuleshooting.

1.- Why my LEDs are not working or their light is weak?
R: If there is no warning or error in the Python Shell, the problem could be
   that the LEDs are not connected properly. Please verify that they are
   connected to the correct pins. Remember that the pinout does not follow a
   sequence. If the LEDs are properly connected, verify that you have your
   Raspberry Pi connected to a 3A power source. Note that if you are using the
   recommended Power LEDs in the article, you will need an external power
   supply source. Do not forget to correctly isolate the digital control
   circuit from the power circuit.

2.- Why is my camera not responding?
R: Raspberry Pi Camera is a very delicate device. Protect it with a case before
   you start working. If the camera is not responding, verify that you're
   connecting it to the camera terminal on the Raspberry Pi. A common problem
   is also that the camera is not enabled, you can enable it from the Raspberry
   Pi Configuration inside the Preferences menu in the Start Menu of Raspbian.
   Once you do this, reebot the device. If the problem continues, verify that
   the connections of the sensor are not loose, if this is the case, gently
   press them to make the proper conection.

3.- Why does the program can not capture images?
R: One of the common problems in this program is that the buffer is not enough
   to capture a full resolution image. To fix this follow the instruction #4 in
   the Instruction menu.

4.- Why is the program not running?
R: This could be due to the Python version in which you're running the program.
   Check that the version of Python you're using is 2.7. Otherwise, many of the
   errors you will find are sintaxis errors. Also check that you have OpenCV and
   Tkinter installed.

5.- My camera is working, but is taking weird pictures, with different colors or
    very warm or cold colors:
R: Sometimes and upgrade or update in the Raspbian OS could help to the native
   image processing of the camera. Please type the following command in the
   terminal:

        ~ $ sudo rpi-update
        
   Reboot your Raspberry Pi and try the script again.


== We're continously working in the troubleshooting, so please, feel free to
send us your concerns to solve them and to improve the program.

== This is an Open Source code, feel free to modify or improve it.

"""
        
        T.insert(tk.END, quote,'normal')
        tk.mainloop()

def instructions():
        InstructionsWindow = Tk()
        InstructionsWindow.title("Instructions")
        ws = InstructionsWindow.winfo_screenwidth()
        hs = InstructionsWindow.winfo_screenheight()
        x = (ws/2)
        y = (hs/2)
        InstructionsWindow.geometry('%dx%d+%d+%d' % (600, 450, x, y))
        S = tk.Scrollbar(InstructionsWindow)
        T = tk.Text(InstructionsWindow, height=600, width=450)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        T.pack(side=tk.LEFT, fill=tk.Y)
        S.config(command=T.yview)
        T.config(yscrollcommand=S.set)
        T.tag_configure('normal', font=('Arial', 12))
        quote = """
General Instructions.

Please follow this instructions prior to GUI use to ensure its functionality.

1. This GUI is intended to use in Raspbian and Python 2.7, make sure to
   compile using this OS and Python version.
   NOTE: New versions of Raspbian don't have Python 2 IDLE installed.
   i)   Go to "Preferences / Add/Remove Software".
   ii)  Search and install package "IDE for Python (v2.7) using Tkinter".
   iii) Go to "Preferences / Main Menu Editor / Programming".
   iv)  Check "IDLE (using Python-2.7)" box.
   v)   Go to GUI file and right click on it.
   vi)  On "Open with:" select "IDLE (using Python-2.7)".
   
2. Install OpenCV library.
   i)   Open Terminal.
   ii)  Run following commands in this specific order:
       ~ $ sudo sudo apt-get update
       ~ $ sudo sudo apt-get upgrade
       ~ $ sudo apt install python-opencv

3. Install Python ImagingTk using the following command on Terminal:
       ~ $ sudo sudo apt-get install python-imaging-tk

4. Verify the version of the Raspberry Pi Camera you have, because the
   resolution in the script is managed depeding on the model.
   In this case, Raspberry Pi Camera V2 (8MPx, 3280x2464 px). We strongly
   recommend the use of this camera due to the design of the optical system.

5. In order to use the Power LEDs for the fluorescence fields, use a proper
   interface to isolate the control circuit from the power circuit, such as
   an optocoupler or a relay. Note that Raspberry Pi does not have enough
   power to correctly feed the Power LEDs.

6. Split the memory of the Raspberry Pi to have enoough buffer to capture
   image with the full resolution of the CMOS sensor.
   i)   Write the following commands in the terminal:
       ~ $ sudo raspi-config
   ii)  Navigate with your keyboard arrows, select option number 7,
        "Advanced Options", then option A3, "Memory Split".
        Erase the number and write down 256 (MB).

If images show a warm color or color is not even, follow the step bellow:

7. Write the following commands in the terminal:
       ~ $ sudo rpi-update
   This updates the Raspberry Pi kernel.

"""

        T.insert(tk.END, quote,'normal')
        tk.mainloop()
                
#---------------------------------GUI declaration section-----------------------------------------------#
root = Tk()
root.title("The BioARTS Lab Mini-microscope")
#Centering window on screen and declaring size of the window.
centre_window(1030, 525) #-225,330. 800x480 para tablet
#Let's make some menu bars
camera.awb_mode
#-----------------------------------Menu bar----------------------------------------------------#
menubar = Menu(root)
filemenu = Menu(menubar, tearoff = 0)
filemenu.add_command(label = "Exit", command = on_closing)
menubar.add_cascade(label = "File", menu = filemenu)

helpmenu = Menu(menubar, tearoff = 0)
helpmenu.add_command(label = "Instructions", command = instructions)
helpmenu.add_command(label = "Troubleshooting", command = troubleshooting)
helpmenu.add_command(label = "Contact", command = contact)
helpmenu.add_command(label = "About...", command = about_sw)
menubar.add_cascade(label="Help", menu=helpmenu)

#The following frame will allow us to organize all the functions we have for the camera manual controls like
#brightness, exposure time, saturation among others. The organization is made with buttons and scale bars.
#The configuration of the frame includes the settings for the canvas, which is used to display the last captured image.

##display = Frame(root, bg = "orange", width = 500, height = 500)
##display.pack(side=RIGHT, expand = 1)

cameraParameters = Frame(root, width = 150, height =350)
cameraParameters.grid(row=0,column=0, sticky="n")

#Just to separate display canvas from camera parameters a little bit.
space1 = Frame(root, width = 15, height = 350)
space1.grid(row=0, column=1, sticky="n")

img = Image.open('start.gif')
img = img.resize((480/2, 594/2), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
canvasframe = Frame(root, width = 510, height = 400)
canvasframe.grid(row=0, column=2, sticky=W+E+N+S)
canvas=Canvas(canvasframe, width=510, height=383)
img_canvas=canvas.create_image(510/2,383/2,image = img, anchor = CENTER)
canvas.grid(row=0, column=0)

previewlabel = Label(canvasframe, text="   Capture Preview   ")
previewlabel.grid(row=1, column=0, columnspan = 5)

paramlabel = Label(cameraParameters, text="   Camera Parameters   ")
paramlabel.grid(row=0, column=0, columnspan = 2)

var1 = StringVar(root)
var1.set("auto") # initial value
optionAWBModes = OptionMenu(cameraParameters, var1, "B Field","Red EmF", "Green EmF", "auto", "sunlight", "cloudy", "shade", "tungsten", "fluorescent", "incandescent", "flash", "horizon","off", command = awb_modes)
optionAWBModes.grid(row =1, column = 1)
var1label = Label(cameraParameters, text="AWB")
var1label.grid(row=1, column=0)

var2 = StringVar(root)
var2.set("none") # initial value
optionEffects = OptionMenu(cameraParameters, var2, "none", "negative", "blur", command = effects)
optionEffects.grid(row =2, column = 1)
var2label = Label(cameraParameters, text="Effects")
var2label.grid(row=2, column=0)

var3 = StringVar(root)
var3.set("auto") # initial value
optionExpMode = OptionMenu(cameraParameters, var3, 'auto', 'off', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow','beach','verylong','fixedfps','antishake','fireworks',command = exposure_modes)
optionExpMode.grid(row =3, column = 1)
var3label = Label(cameraParameters, text="Exposure Modes")
var3label.grid(row=3, column=0)

##var4 = StringVar(root)
##var4.set("auto") # initial value
##channelOption= OptionMenu(cameraParameters, var4, "auto","Red", "Green", "Blue", command = channelsplit)
##channelOption.grid(row =4, column = 4)
##var4label = Label(root, text="Channels")
##var4label.grid(row=4, column=3)

var5 = StringVar(root)
var5.set("auto") # initial value
ISOOption= OptionMenu(cameraParameters, var5, "auto","100", "200", "320","400", "500", "640", "800",command = isocam)
ISOOption.grid(row =4, column = 1)
var5label = Label(cameraParameters, text="ISO")
var5label.grid(row=4, column=0)

sBright = Scale(cameraParameters, from_=25, to=75, resolution=1, orient=HORIZONTAL, command = brightnessScale)
sBright.grid(row=5, column=1)
sBright.set(camera.brightness)
##print "Brightness", camera.brightness
sBrightlabel = Label(cameraParameters, text="Brightness")
sBrightlabel.grid(row=5, column=0)
root.update()

sContrs = Scale(cameraParameters, from_=-50, to=50, resolution=1, orient=HORIZONTAL, command = contrastScale)
sContrs.grid(row=6, column=1)
sContrs.set(camera.contrast)
##print "Contrast", camera.contrast
sContrslabel = Label(cameraParameters, text="Contrast")
sContrslabel.grid(row=6, column=0)

sSat = Scale(cameraParameters, from_=-100, to=100, resolution=1, orient=HORIZONTAL, command = saturationScale)
sSat.grid(row=7, column=1)
sSat.set(camera.saturation)
##print "Saturation", camera.saturation
root.update()
sSatlabel= Label(cameraParameters, text="Saturation")
sSatlabel.grid(row=7, column=0)
root.update()

sSharp = Scale(cameraParameters, from_=-100, to=100, resolution=10, orient=HORIZONTAL, command = sharpnessScale)
sSharp.grid(row=8, column=1)
sSharp.set(camera.sharpness)
root.update()
sSharplabel= Label(cameraParameters, text="Sharpness")
sSharplabel.grid(row=8, column=0)
root.update()

sExpT = Scale(cameraParameters, from_=0, to=1000, resolution = 50,orient=HORIZONTAL,  command = exposureTimeScale)
sExpT.grid(row=9, column=1)
##print "Exposure Time ms", camera.shutter_speed
root.update()
sexpt= Label(cameraParameters, text="Exposure Time ms")
sexpt.grid(row=9, column=0)
root.update()

yy = Scale(cameraParameters, from_=0, to=20, resolution=1, orient=HORIZONTAL)
yy.grid(row=10, column=1)

if timelapse == 0:
        yy.set(1)

yz = Label(cameraParameters, text="Timelapse delay min")
yz.grid(row=10, column=0)

#####################################################################################################
### Enable these scale bars to use with the code for the AWB gins modification.

##g1 = Scale(root, from_=0, to=8, resolution=0.1, orient=HORIZONTAL)
##g1.grid(row=8, column=4)
##
##g1label = Label(root, text="      Red Gain      ")
##g1label.grid(row=8, column=3)
##root.update()
##
##g2 = Scale(root, from_=0, to=8, resolution=0.1, orient=HORIZONTAL)
##g2.grid(row=9, column=4)
##
##g2label = Label(root, text="      Blue Gain      ")
##g2label.grid(row=9, column=3)
##root.update()
##
##gainButton = Button(root, bg="cyan", text="       Set Gains!      ", command=setAWB_gains)
##gainButton.grid(row=10, column=4)
###############################################################################

##--------------------------Illumination Options--------------------------------------------
lightOpt = Frame(root, width = 150, height = 150)
lightOpt.grid(row=1,column=0, sticky="n")
lightlabel = Label(lightOpt, text="   Illumination Options   ")
lightlabel.grid(row=0, column=0, columnspan = 3)

space1 = Frame(root, width = 15, height = 150)
space1.grid(row=1, column=1, sticky="n")

ledbtn_text = StringVar()
ledButton = Button(lightOpt, textvariable=ledbtn_text, command=led)
ledbtn_text.set("  BrFld OFF  ")
ledButton.grid(row=1, column=1)

gfluorledbtn_text = StringVar()
gfluorledButton = Button(lightOpt, textvariable=gfluorledbtn_text, command=GREENFluorled)
gfluorledbtn_text.set("  BL OFF  ")
gfluorledButton.grid(row=1, column=2)

bfluorledbtn_text = StringVar()
bfluorledButton = Button(lightOpt, textvariable=bfluorledbtn_text, command=BLUEFluorled)
bfluorledbtn_text.set("  UVL OFF  ")
bfluorledButton.grid(row=2, column=1)

rfluorledbtn_text = StringVar()
rfluorledButton = Button(lightOpt, textvariable=rfluorledbtn_text, command=REDFluorled)
rfluorledbtn_text.set("  GL OFF  ")
rfluorledButton.grid(row=2, column=2)

##--------------------------Capture Options--------------------------------------------
capOpt = Frame(root, width = 510, height = 150)
capOpt.grid(row=1,column=2, sticky="n")
caplabel = Label(capOpt, text="   Capture Options   ")
caplabel.grid(row=0, column=0, columnspan = 5)

previewbtn_text = StringVar()
previewButton = Button(capOpt, textvariable=previewbtn_text, command=previewCamera)
previewbtn_text.set("Preview On")
previewButton.grid(row=1, column=0)

takeStillButton = Button(capOpt, text="   Take still  ", command=still)
takeStillButton.grid(row=2,column=0)

TLbtn_text = StringVar()
TLButton = Button(capOpt, textvariable=TLbtn_text, command=startLapse)
TLbtn_text.set("Start Time Lapse")
TLButton.grid(row=1, column=1)

stopTLbtn_text = StringVar()
stopTLButton = Button(capOpt, textvariable=stopTLbtn_text, command=stopLapse)
stopTLbtn_text.set("Stop Time Lapse")
stopTLButton.config(state = DISABLED)
stopTLButton.grid(row=2, column=1)

#-----------------------------------Image Processing----------------------------------------------
IPFrame = Frame(root, width = 500, height = 400)
IPFrame.grid(row=0, column=4, sticky=W+E+N+S)
50
IPlabel = Label(IPFrame, text="   Image Processing   ")
IPlabel.grid(row=0, column=0, columnspan = 3)

compresslabel = Label(IPFrame, text="              ")
compresslabel.grid(row=10, column=0, columnspan = 3)
compresslabel = Label(IPFrame, text="   Image compression options   ")
compresslabel.grid(row=11, column=0, columnspan = 3)

var8 = StringVar(root)
var8.set("TIFF") # initial value
optionExp = OptionMenu(IPFrame, var8, 'TIFF', 'JPEG', 'PNG', 'BMP', 'DATA')
optionExp.grid(row =12, column = 1)
var8label = Label(IPFrame, text="File Options")
var8label.grid(row=12, column=0)

gammabtn_text = StringVar()
gammabtn = Button(IPFrame, textvariable=gammabtn_text, command=gammaPreview)
gammabtn_text.set("Gamma")
gammabtn.grid(row=13, column=1)

exportbtn_text = StringVar()
exportbtn = Button(IPFrame, textvariable=exportbtn_text, command=export_image)
exportbtn_text.set("Export Image")
exportbtn.grid(row=14, column=1)

#-----Quit Section---
quitframe = Frame(root, width = 500, height = 150)
quitframe.grid(row=1,column=4, sticky="n")

space3 = Frame(quitframe, width = 15, height = 30)
space3.grid(row=0, column=0, sticky="n")
quitButton = Button(quitframe, bg="pink", text="       Quit      ", command=on_closing)
quitButton.grid(row=1, rowspan = 2, column=1)

#------App icon-----
ico = Image.open('microscopeicon.gif')
ico = ico.resize((480/2, 594/2), Image.ANTIALIAS)
ico = ImageTk.PhotoImage(ico)

root.config(menu = menubar)
root.tk.call('wm', 'iconphoto',root._w,ico)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

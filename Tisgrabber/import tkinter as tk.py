import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

# Dummy functions for camera and motor control
# Replace these with your actual functions

def get_camera_frame(selected_camera):
    return cv2.imread('example.jpg')  # Replace with actual camera feed

def adjust_camera_settings(exposure, gain):
    pass  # Implement actual adjustment here

def move_motor(motor_number, steps):
    pass  # Implement actual motor movement here

# Initialize Tkinter window
root = tk.Tk()
root.title('Camera and Motor Control')

# Camera selection
frame_camera_select = ttk.LabelFrame(root, text='Select Camera')
frame_camera_select.pack(padx=10, pady=10)

camera_list = ['Camera 1', 'Camera 2', 'Camera 3']  # Add your cameras here
combo_camera = ttk.Combobox(frame_camera_select, values=camera_list)
combo_camera.grid(row=0, column=0)

# Camera frame display
lbl_camera = tk.Label(root)
lbl_camera.pack()

def update_camera_frame():
    frame = get_camera_frame(combo_camera.get())
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    lbl_camera.imgtk = imgtk
    lbl_camera.config(image=imgtk)
    lbl_camera.after(10, update_camera_frame)  # Update every 10 ms

# Start camera button
btn_start_camera = ttk.Button(frame_camera_select, text='Start', command=update_camera_frame)
btn_start_camera.grid(row=0, column=1)


root.mainloop()
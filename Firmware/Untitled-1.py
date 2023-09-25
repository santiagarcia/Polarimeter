
import ctypes
# import tisgrabber as tis

TIS_DLL = ctypes.cdll.LoadLibrary("C:\\Users\\57317\\Documents\\The Imaging Source Europe GmbH\\TIS Grabber DLL\\bin\\x64\\tisgrabber_x64.dll")
import tisgrabber as tis
def capture_image():
    # Initialize the camera
    
    camera_handle = TIS_DLL.InitCamera()
    if camera_handle is None:
        print('Failed to initialize camera')
        return
    
    # Set camera parameters (e.g., exposure, gain, etc.)
    TIS_DLL.SetParameters(camera_handle)
    
    # Capture the image
    image_data = TIS_DLL.CaptureImage(camera_handle)
    if image_data is None:
        print('Failed to capture image')
        return
    
    # Save the image
    with open('captured_image.jpg', 'wb') as f:
        f.write(image_data)
    
    # Close the camera
    TIS_DLL.CloseCamera(camera_handle)

# Capture an image
if __name__ == '__main__':
    capture_image()
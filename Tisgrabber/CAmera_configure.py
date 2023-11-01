import tisgrabber as IC
import cv2


def manual_calibration(Camera):
    Camera.StartLive(1)
    while True:
        Camera.SnapImage()
        image = Camera.GetImage()
        cv2.imshow('Manual Calibration', image)
        key = cv2.waitKey(1)
        if key == 27:  # Press 'ESC' to exit
            break
    Camera.StopLive()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    Camera = IC.TIS_CAM()
    Camera.open('DMx 41BU02 8410421')  # Replace with your camera model
    if Camera.IsDevValid() == 1:
        manual_calibration(Camera)
    else:
        print('No device selected.')
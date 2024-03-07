import time
import tisgrabber as IC
from polarimeter_functions import *

Camera = IC.TIS_CAM()
Camera.open('DMx 41BU02 8410421')
Camera.StartLive(1)
Camera.SnapImage()
measure_irradiance(Camera)

calibration = pd.read_csv('complete_calibration.csv')
d_m1 = calibration['1'][0]*2
d_m2 = calibration['2'][0]*2
d_m3 = calibration['3'][0]*2
d_m4 = calibration['4'][0]*2
# s_m1 = calibration['1'][1]
# s_m2 = calibration['2'][1]
# s_m3 = calibration['3'][1]
# s_m4 = calibration['4'][1]
d_ms = [d_m1, d_m2, d_m3, d_m4]
# s_ms = [s_m1, s_m2, s_m3, s_m4]
save_path = '../Data/CalibrationTestDP/'

# angles = np.array([
#     [0, 0, 90, 90], [0, 0, 90, 0], [0, 0, 315, 45], [0, 0, 45, 315], [0, 0, 0, 315], [0, 0, 0, 45],
#     [45, 90, 90, 90], [45, 90, 90, 0], [45, 90, 315, 45], [45, 90, 45, 315], [45, 90, 0, 315], [45, 90, 0, 45],
#     [337.5, 315, 90, 90], [337.5, 315, 90, 0], [337.5, 315, 315, 45], [337.5, 315, 45, 315], [337.5, 315, 0, 315],
#     [337.5, 315, 0, 45],
#     [22.5, 45, 90, 90], [22.5, 45, 90, 0], [22.5, 45, 315, 45], [22.5, 45, 45, 315], [22.5, 45, 0, 315],
#     [22.5, 45, 0, 45],
#     [22.5, 90, 90, 90], [22.5, 90, 90, 0], [22.5, 90, 315, 45], [22.5, 90, 45, 315], [22.5, 90, 0, 315],
#     [22.5, 90, 0, 45],
#     [45, 90, 90, 90], [45, 90, 90, 0], [45, 90, 315, 45], [45, 90, 45, 315], [45, 90, 0, 315], [45, 90, 0, 45]])

sb_angles = np.array([
    [0, 0, 90, 90], [0, 0, 0, 270], [0, 0, 225, 45], [0, 0, 90, 270], [0, 0, 315, 0], [0, 0, 0, 90],
    [45, 90, 90, 45], [0, 0, 0, 270], [0, 0, 225, 45], [0, 0, 90, 270], [0, 0, 315, 0], [0, 0, 0, 90],
    [292.5, 225, 90, 45], [0, 0, 0, 270], [0, 0, 225, 45], [0, 0, 90, 270], [0, 0, 315, 0], [0, 0, 0, 90],
    [45, 90, 90, 45], [0, 0, 0, 270], [0, 0, 225, 45], [0, 0, 90, 270], [0, 0, 315, 0], [0, 0, 0, 90],
    [0, 45, 90, 45], [0, 0, 0, 270], [0, 0, 225, 45], [0, 0, 90, 270], [0, 0, 315, 0], [0, 0, 0, 90],
    [22.5, 0, 90, 45], [0, 0, 0, 270], [0, 0, 225, 45], [0, 0, 90, 270], [0, 0, 315, 0], [0, 0, 0, 90],
    [315, 270, 0, 315]

])

df = pd.DataFrame(columns=['Name', 'Counts'])
data = {}


ser = serial.Serial('COM8', 115200)
it = 0
for angle, name in zip(sb_angles, names):
    for angl, d_m, i in zip(angle, d_ms, range(1, 5)):
        if angl == 0:
            var = []
            print(f'Inside zero angle for motor {i}')
        else:
            print(f'Moving motor {i}')
            move_motor(ser, i, d_m * angl)
            print('Waiting until the motor finishes')
            time.sleep(angl * 0.3)
    Camera.SnapImage()
    image = Camera.GetImage()
    data[name] = image  # directly just for bright field
    cv.imwrite(f'{save_path}/{name}.png', image)
    print(f'Image {name} saved, iteration {it}')
    it += 1
# m00, m01, m02, m03, m10, m12, m11, m13, m21, m20, m23, m30, m31, m32, m33, m22 = mueller_mat(data)

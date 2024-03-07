import time
import timeit

import serial
import plotly.graph_objects as go
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import cv2 as cv
import os

names = ['HV', 'HH', 'HP', 'HM', 'HR', 'HL',
         'VV', 'VH', 'VP', 'VM', 'VR', 'VL',
         'MV', 'MH', 'MP', 'MM', 'MR', 'ML',
         'PV', 'PH', 'PP', 'PM', 'PR', 'PL',
         'LV', 'LH', 'LP', 'LM', 'LR', 'LL',
         'RV', 'RH', 'RP', 'RM', 'RR', 'RL', 'zero']

names_mm = ['m00', 'm02', 'm10', 'm12',
            'm20', 'm22', 'm30', 'm32',
            'm01', 'm03', 'm11', 'm13',
            'm21', 'm23', 'm31', 'm33']


def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0)
    # total_irradiance = np.sum(image)
    total_irradiance = np.mean(image)
    return total_irradiance


# Function to move motor
def move_motor(ser, motor_number, steps):
    command = f"{motor_number},{steps}\n"
    ser.write(command.encode())
    print("Number of bytes in input buffer x1: " + str(ser.in_waiting))
    ser.flushInput()


def calibration_spr(ser, cam, motor_number, step, iterations):
    irradiance_ = []
    position_ = []
    time_ = []
    position = 0
    for it in range(iterations):
        move_motor(ser, motor_number, step)
        # time.sleep(0.15)
        irradiance = measure_irradiance(cam)
        # print(irradiance)
        irradiance_.append(irradiance)
        times = timeit.timeit()
        time_.append(times)
        position = position + step
        position_.append(position)
    df = pd.DataFrame({'Position': position_, 'Irradiance': irradiance_, 'Time': time_})
    df.to_csv(f'Calibration_motor_{motor_number}.csv')
    return df


def steps_per_degree(df, motor_number):
    df.Irradiance = (df.Irradiance / df.Irradiance.max()) * 2 - 1
    df.Irradiance = cv.GaussianBlur(np.array(df.Irradiance.values), ksize=(0, 0), sigmaX=50,
                                    borderType=cv.BORDER_REPLICATE)
    change_indexes = np.where(np.diff(np.sign(df.Irradiance)))[0] + 1
    change_positions = df.Position.iloc[change_indexes]
    position_diffs = np.diff(change_positions)
    average_position_diff = np.mean(position_diffs)
    change_Time = df.Time.iloc[change_indexes]
    Time_diffs = np.diff(change_Time)
    average_Time_diff = np.mean(Time_diffs)

    max_freq = np.pi / average_position_diff
    fitted_curve = 0.5 * np.sin((max_freq) * df['Position'] + 1500)
    fig = go.Figure()
    # Scatter plot for the original data
    fig.add_trace(go.Scatter(x=df.Position, y=df['Irradiance'], mode='markers', name='Original Data'))
    # Line plot for the fitted curve
    fig.add_trace(go.Scatter(x=df.Position, y=fitted_curve, mode='lines', name='Fitted Curve', line=dict(color='red')))

    # Set axis labels and plot title
    fig.update_layout(title=f'Fitted Sinusoidal Curve motor {motor_number}',
                      xaxis_title='Position',
                      yaxis_title='Irradiance')

    # Show the interactive plot
    fig.write_html(f'Malus_Motor_{motor_number}.html')
    print(
        f'The motor takes {2 * average_position_diff} steps to run 360 degrees. Taking {2 * average_position_diff / 360} steps to move 1 degree')
    print(
        f'The motor takes {2 * average_Time_diff} seconds to run 360 degrees. Taking {2 * average_Time_diff / 360} seconds to move 1 degree')

    return 2 * average_position_diff / 360, 2 * average_Time_diff / 360


# Function to calibrate the polarizer
def calibrate_element(ser, cam, motor_number, spd):
    initial_position = 0

    # Measure irradiance
    initial_irradiance = measure_irradiance(cam)

    # Initialize variables to track the previous, current, and next intensities
    prev_intensity = initial_irradiance
    current_intensity = initial_irradiance
    next_intensity = initial_irradiance

    # Move the motor in steps until the intensity starts increasing
    while True:
        move_motor(ser, motor_number, spd)

        # Update intensities
        prev_intensity = current_intensity
        current_intensity = next_intensity
        next_intensity = measure_irradiance(cam)
        #
        # if current_intensity < 10:
        #     ser.close()
        #     # Intensity has reached a minimum point, break the loop
        #     break
        #
        if current_intensity < prev_intensity and current_intensity < next_intensity and current_intensity < 10:
            ser.close()
            # Intensity has reached a minimum point, break the loop
            break
    time.sleep(5)
    print('Waiting 5 seconds')
    # ser = serial.Serial('COM8', 115200)
    # print('Port opened')
    # # Move the motor back to the position with minimum intensity
    # move_motor(ser, motor_number, spd * 359)

    # Optionally, you can measure the intensity at this position
    final_irradiance = measure_irradiance(cam)

    print(
        f"Calibration complete. Initial Irradiance: {initial_irradiance}, Minimum Irradiance: {current_intensity}, Final Irradiance: {final_irradiance}")


def mueller_mat(data):
    mm = {}
    mm['m00'] = data['HH'] + data['HV'] + data['VH'] + data['VV']
    # m00 = m00 / m00.mean()
    mm['m02'] = data['PH'] + data['PV'] - data['MH'] - data['MV']
    # m02 = m02 / m02.mean()
    mm['m10'] = data['HH'] - data['HV'] + data['VH'] - data['VV']
    # m10 = m10 / m10.mean()
    mm['m12'] = data['PH'] - data['PV'] - data['MH'] + data['MV']
    # m12 = m12 / m12.mean()
    mm['m20'] = data['HP'] - data['HM'] + data['VP'] - data['VM']
    # m20 = m20 / m20.mean()
    mm['m22'] = data['PP'] - data['PM'] - data['MP'] + data['MM']
    # m22 = m22 / m22.mean()
    mm['m30'] = data['HR'] - data['HL'] + data['VR'] - data['VL']
    # m30 = m30 / m30.mean()
    mm['m32'] = data['PR'] - data['PL'] - data['MR'] + data['ML']
    # m32 = m32 / m32.mean()
    mm['m01'] = data['HH'] + data['HV'] - data['VH'] - data['VV']
    # m01 = m01 / m01.mean()
    mm['m03'] = data['RH'] + data['RV'] - data['LH'] - data['LV']
    # m03 = m03 / m03.mean()
    mm['m11'] = data['HH'] - data['HV'] - data['VH'] + data['VV']
    # m11 = m11 / m11.mean()
    mm['m13'] = data['RH'] - data['RV'] - data['LH'] + data['LV']
    # m13 = m13 / m13.mean()
    mm['m21'] = data['HP'] - data['HM'] - data['VP'] + data['VM']
    # m21 = m21 / m21.mean()
    mm['m23'] = data['RP'] - data['RM'] - data['LP'] + data['LM']
    # m23 = m23 / m23.mean()
    mm['m31'] = data['HR'] - data['HL'] - data['VR'] + data['VL']
    # m31 = m31 / m31.mean()
    mm['m33'] = data['LL'] - data['RL'] - data['LR'] + data['RR']
    # m33 = m33 / m33.mean()
    return mm


def bf_mm_measure(path):
    data = {}
    for name in names:
        int = cv.imread(f'{path}/{name}.png',cv.IMREAD_GRAYSCALE)
        int = int.astype('float')
        # int = int[:, :, 1]
        # int = int.astype('float')
        int = int / int.max()
        data[name] = int

    mm = mueller_mat(data)
    return mm


ob_names = ['diattenuation_1', 'polarizance_1', 'depolarization_1', 'tetha', 'degree_polarization',
            'orientation', 'optical_activity', 'linear_birrefringence', 'dichroism', 'retardance',
            'diattenuation_2', 'polarizance_2', 'depolarization']


def mm_observables(mm):
    observables = {}
    observables[ob_names[0]] = np.sqrt((mm['m01'] ** 2 + mm['m02'] ** 2 + mm['m03'] ** 2)) / (mm['m00'])
    observables[ob_names[0]] = observables[ob_names[0]] - np.mean(observables[ob_names[0]])

    observables[ob_names[1]] = np.sqrt((mm['m10'] ** 2 + mm['m20'] ** 2 + mm['m30'] ** 2)) / mm['m00']
    observables[ob_names[1]] = observables[ob_names[1]] - np.mean(observables[ob_names[1]])

    observables[ob_names[2]] = 1 - (
        np.sqrt((mm['m00'] ** 2 + mm['m11'] ** 2 + mm['m22'] ** 2 + mm['m33'] ** 2) - mm['m00'] ** 2)) \
                               / (np.sqrt(3 * mm['m00']))
    observables[ob_names[2]] = observables[ob_names[2]] - np.mean(observables[ob_names[2]])

    observables[ob_names[3]] = 1 / 2 * np.arctan(np.sqrt(mm['m20'] ** 2 + mm['m30'] ** 2) / mm['m10'])

    observables[ob_names[4]] = np.sqrt(mm['m01'] ** 2 + mm['m02'] ** 2 + mm['m03'] ** 2) / mm['m00']
    observables[ob_names[4]] = 1 - observables[ob_names[4]]
    observables[ob_names[5]] = 1 / 2 * np.arctan2(mm['m21'], mm['m12'])
    observables[ob_names[6]] = 1 / 2 * np.arcsin(mm['m13']) - np.arcsin(mm['m31'])
    observables[ob_names[7]] = np.sqrt((mm['m11'] - mm['m22']) ** 2 + (mm['m12'] + mm['m21']) ** 2)
    observables[ob_names[8]] = np.sqrt(mm['m01'] ** 2 + mm['m02'] ** 2)

    # Mean matrix from the experimental matrix
    experimental_mean_matrix = np.array(
        [[np.mean(mm['m00']), np.mean(mm['m01']), np.mean(mm['m02']), np.mean(mm['m03'])],
         [np.mean(mm['m10']), np.mean(mm['m11']), np.mean(mm['m12']), np.mean(mm['m13'])],
         [np.mean(mm['m20']), np.mean(mm['m21']), np.mean(mm['m22']), np.mean(mm['m23'])],
         [np.mean(mm['m30']), np.mean(mm['m31']), np.mean(mm['m32']), np.mean(mm['m33'])]])

    N, M = mm['m00'].shape
    Pseudo_color = np.array(np.zeros((N, M, 3)))
    MDia = np.zeros([4, 4])
    MPol = np.zeros([4, 4])
    MDia[0, 0] = 1
    MPol[0, 0] = 1

    for i in range(N):
        for j in range(M):

            Current_Mueller = np.array([[mm['m00'][i, j], mm['m01'][i, j], mm['m02'][i, j], mm['m03'][i, j]], \
                                        [mm['m10'][i, j], mm['m11'][i, j], mm['m12'][i, j], mm['m13'][i, j]], \
                                        [mm['m20'][i, j], mm['m21'][i, j], mm['m22'][i, j], mm['m23'][i, j]], \
                                        [mm['m30'][i, j], mm['m31'][i, j], mm['m32'][i, j], mm['m33'][i, j]]])
            if mm['m00'][i, j] == 0:
                mm['m00'][i, j] = 0.000001

            Normal_mueller = mm['m00'][i, j]
            Current_Mueller = Current_Mueller / Normal_mueller

            # diattenuation and its matrix
            D_value = np.sqrt(Current_Mueller[0, 1] ** 2 + Current_Mueller[0, 2] ** 2 + Current_Mueller[0, 3] ** 2)
            if D_value > 2:
                Pseudo_color[i, j, 0] = 0
            else:
                Pseudo_color[i, j, 0] = D_value

            D = np.array([[Current_Mueller[0, 1]], [Current_Mueller[0, 2]], [Current_Mueller[0, 3]]])

            # Assignment of the values to the matrix
            MDia[0, 1:4] = D.T
            MDia[1:4, 0:1] = D

            Identy = np.eye(3)
            D_mod = np.round(np.linalg.norm(D), 3)

            if D_mod == 0:
                D[0, 0] = D[0, 0] + 0.01
                D_mod = np.round(np.linalg.norm(D), 3)

            if D_mod >= 1:
                D_mod = 0.999

            D_uni = (1 / D_mod) * D
            Raiz = np.sqrt(1 - D_mod ** 2)
            md = Raiz * Identy + (1 - Raiz) * (D_uni @ (D_uni.T))

            # Assignment of the values to the matrix
            MDia[1:4, 1:4] = md

            # Multiply the original mueller matrix by the diattenuation matrix
            M_prim = (Current_Mueller @ np.linalg.pinv(MDia))

            # POLARIZANCE AND IT'S MATRIX

            P_value = np.sqrt(Current_Mueller[1, 0] ** 2 + Current_Mueller[2, 0] ** 2 + Current_Mueller[3, 0] ** 2)
            if P_value > 2:
                Pseudo_color[i, j, 1] = 0
            else:
                Pseudo_color[i, j, 1] = P_value

            Pol_vector = np.array([[Current_Mueller[1, 0]], [Current_Mueller[2, 0]], [Current_Mueller[3, 0]]])

            # DEPOLARIZATION
            if Current_Mueller[0, 0] == 0:
                DP_value = 0
            else:
                DP_value = 1 - (np.sqrt(((Current_Mueller[1, 1] ** 2 + Current_Mueller[2, 2] ** 2 + Current_Mueller[
                    3, 3] ** 2 + Current_Mueller[0, 0] ** 2) - Current_Mueller[0, 0] ** 2)) / (
                                        np.sqrt(3) * Current_Mueller[0, 0]))
                Pseudo_color[i, j, 2] = DP_value
                if DP_value == np.nan:
                    Pseudo_color[i, j, 2] = 0
                if DP_value == np.inf:
                    Pseudo_color[i, j, 2] = 0
                if DP_value == -np.inf:
                    Pseudo_color[i, j, 2] = 0
                if DP_value == -np.nan:
                    Pseudo_color[i, j, 2] = 0

    observables[ob_names[9]] = -1.35 * Pseudo_color[:, :, 2]
    observables[ob_names[10]] = Pseudo_color[:, :, 0]
    observables[ob_names[11]] = Pseudo_color[:, :, 1]
    observables[ob_names[12]] = Pseudo_color[:, :, 2]

    return observables


def mfig(data, folder, name, zmin, zmax):
    fig = px.imshow(data, color_continuous_scale='Bluered_r', range_color=(zmin, zmax))
    # fig = px.imshow(data, color_continuous_scale='turbo', range_color=(zmin, zmax))
    # fig.update_traces(zmin=zmin, zmax=zmax)
    fig.write_html(f'{folder}/{name}.html')


def write_data_png(path, data, names):
    print('Inside the function')
    for name in names:
        img = data[name]
        img = img - img.min()
        img = img / img.max()
        # print(name)
        # if not os.path.exists(f"{path}/Results"):
        #     os.makedirs(f"{path}/Results")
        cv.imwrite(f'{path}/Results/{name}.png', img*255)


def write_data_html(path, data, names):
    for name in names:
        img = data[name]
        fig = px.imshow(img, color_continuous_scale='turbo')
        if not os.path.exists(f"{path}/Results"):
            os.makedirs(f"{path}/Results")
        fig.write_html(f'{path}/Results/{name}.html')

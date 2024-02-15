import time
import serial
import tisgrabber as IC
import plotly.graph_objects as go
import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import cv2 as cv

def measure_irradiance(Camera):
    Camera.SnapImage()
    image = Camera.GetImage()
    image = cv2.flip(image, 0)
    total_irradiance = np.sum(image)
    return total_irradiance

# Function to move motor
def move_motor(motor_number, steps):
    command = f"{motor_number},{steps}\n"
    ser.write(command.encode())

def calibration_spr(cam,motor_number, step,iterations):
    irradiance_ = []
    position_ = []
    position = 0
    for it in range(iterations):
        move_motor(motor_number, step)
        irradiance = measure_irradiance(cam)
        # print(irradiance)
        irradiance_.append(irradiance)
        position = position + step
        position_.append(position)
    df = pd.DataFrame({'Position': position_,'Irradiance':irradiance_})
    df.to_csv(f'Calibration_motor_{motor_number}.csv')
    return df

def steps_per_degree(df, motor_number):
    df.Irradiance = (motor_1.Irradiance / motor_1.Irradiance.max()) * 2 -1
    df.Irradiance = cv.GaussianBlur(np.array(motor_1.Irradiance.values), ksize=(0, 0), sigmaX=50, borderType=cv.BORDER_REPLICATE)
    change_indexes = np.where(np.diff(np.sign(df.Irradiance)))[0] + 1
    change_positions = df.Position.iloc[change_indexes]
    position_diffs = np.diff(change_positions)
    average_position_diff = np.mean(position_diffs)

    max_freq = np.pi / average_position_diff
    fitted_curve = 0.5 * np.sin( (max_freq) * motor_1['Position'] + 1500)
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
    print(f'The motor takes {2*average_position_diff} steps to run 360 degrees. Taking {2*average_position_diff/360} steps to move 1 degree')
    return 2*average_position_diff/360

# Function to calibrate the polarizer
def calibrate_element(cam,motor_number,spd):

    initial_position = 0

    # Measure irradiance
    initial_irradiance = measure_irradiance(cam)

    # Initialize variables to track minimum intensity and corresponding position
    min_intensity = initial_irradiance
    min_intensity_position = initial_position
    steps = 0
    # Move the motor in steps until the intensity starts increasing
    while True:
        move_motor(motor_number, spd)
        current_irradiance = measure_irradiance(cam)

        if current_irradiance > min_intensity:
            # Intensity has started increasing, break the loop
            break

    # Move the motor back to the position with minimum intensity
    move_motor(motor_number, spd*359)

    # Optionally, you can measure the intensity at this position
    final_irradiance = measure_irradiance(cam)

    print(f"Calibration complete. Initial Irradiance: {initial_irradiance}, Minimum Irradiance: {min_intensity}, Final Irradiance: {final_irradiance}")


def mueller_mat(data):
    m00 = data['HH'] + data['HV'] + data['VH'] + data['VV']
    # m00 = m00 / m00.mean()
    m02 = data['PH'] + data['PV'] - data['MH'] - data['MV']
    # m02 = m02 / m02.mean()
    m10 = data['HH'] - data['HV'] + data['VH'] - data['VV']
    # m10 = m10 / m10.mean()
    m12 = data['PH'] - data['PV'] - data['MH'] + data['MV']
    # m12 = m12 / m12.mean()
    m20 = data['HP'] - data['HM'] + data['VP'] - data['VM']
    # m20 = m20 / m20.mean()
    m22 = data['PP'] - data['PM'] - data['MP'] + data['MM']
    # m22 = m22 / m22.mean()
    m30 = data['HR'] - data['HL'] + data['VR'] - data['VL']
    # m30 = m30 / m30.mean()
    m32 = data['PR'] - data['PL'] - data['MR'] + data['ML']
    # m32 = m32 / m32.mean()
    m01 = data['HH'] + data['HV'] - data['VH'] - data['VV']
    # m01 = m01 / m01.mean()
    m03 = data['RH'] + data['RV'] - data['LH'] - data['LV']
    # m03 = m03 / m03.mean()
    m11 = data['HH'] - data['HV'] - data['VH'] + data['VV']
    # m11 = m11 / m11.mean()
    m13 = data['RH'] - data['RV'] - data['LH'] + data['LV']
    # m13 = m13 / m13.mean()
    m21 = data['HP'] - data['HM'] - data['VP'] + data['VM']
    # m21 = m21 / m21.mean()
    m23 = data['RP'] - data['RM'] - data['LP'] + data['LM']
    # m23 = m23 / m23.mean()
    m31 = data['HR'] - data['HL'] - data['VR'] + data['VL']
    # m31 = m31 / m
    # 31.mean()
    m33 = data['LL'] - data['RL'] - data['LR'] + data['RR']
    # m33 = m33 / m33.mean()
    return m00, m01, m02, m03, m10, m12, m11, m13, m21, m20, m23, m30, m31, m32, m33, m22
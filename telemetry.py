import argparse
import os
import socket
import struct
import pandas as pd
import time
import pygame

UDP_IP = "127.0.0.1"
UDP_PORT = 20778

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCKET.bind((UDP_IP, UDP_PORT))
SOCKET.settimeout(1)

FLOAT_VALUES = [
    "totalTime",
    "lapTime",
    "lapDistance",
    "totalDistance",
    "m_x",
    "m_y",
    "m_z",
    "speed",
    "m_xv",
    "m_yv",
    "m_zv",
    "m_xr",
    "m_yr",
    "m_zr",
    "m_xd",
    "m_yd",
    "m_zd",
    "m_susp_pos_rl",
    "m_susp_pos_rr",
    "m_susp_pos_fl",
    "m_susp_pos_fr",
    "m_susp_vel_rl",
    "m_susp_vel_rr",
    "m_susp_vel_fl",
    "m_susp_vel_fr",
    "wheelSpeed_rl",
    "wheelSpeed_rr",
    "wheelSpeed_fl",
    "wheelSpeed_fr",
    "throttle",
    "steer",
    "brake",
    "clutch",
    "gear",
    "gforceLat",
    "gforceLon",
    "lap",
    "engineRate",
    "sliProNativeSupport",
    "carRacePosition",
    "kersLevel",
    "kersMaxLevel",
    "drs",
    "tractionControl",
    "antiLockBrakes",
    "fuelInTank",
    "fuelCapacity",
    "inPits",
    "sector",
    "sector1",
    "sector2",
    "brakesTemp_rl",
    "brakesTemp_rr",
    "brakesTemp_fl",
    "brakesTemp_fr",
    "tyrePress_rl",
    "tyrePress_rr",
    "tyrePress_fl",
    "tyrePress_fr",
    "teamID",
    "totalRaceLaps",
    "trackSize",
    "lastLapTime",
    "maxRpm",
    "idleRpm",
    "maxGears",
    "sessionType",
    "drsAllowed",
    "trackNumber",
    "flag",
    "era",
    "engineTemp",
    "gforceVert",
    "m_ang_vel_x",
    "m_ang_vel_y",
    "m_ang_vel_z",
]
BYTE_VALUES = [
    "tyreTemp_rl",
    "tyreTemp_rr",
    "tyreTemp_fl",
    "tyreTemp_fr",
    "tyreWear_rl",
    "tyreWear_rr",
    "tyreWear_fl",
    "tyreWear_fr",
    "tyreCompound",
    "frontBrakeBias",
    "fuelMix",
    "currentLapInvalid",
    "tyreDamage_rl",
    "tyreDamage_rr",
    "tyreDamage_fl",
    "tyreDamage_fr",
    "frontLeftWingDamage",
    "frontRightWingDamage",
    "rearWingDamage",
    "engineDamage",
    "gearBoxDamage",
    "exhaustDamage",
    "pitLimiterStatus",
    "pitSpeedLimit",
]
MPS_MPH_KMH = 2.23694 * 1.609344  # mps -> mph -> kmh
LIST_KEYS = FLOAT_VALUES + BYTE_VALUES
NUM_BYTES = len(FLOAT_VALUES) * [4] + len(BYTE_VALUES) * [1]


class WheelGetter:
    def __init__(self, wheel_index=0):
        pygame.init()
        self.wheel = pygame.joystick.Joystick(wheel_index)
        self.wheel.init()
        self.num_axes = self.wheel.get_numaxes()
        self.num_buttons = self.wheel.get_numbuttons()
        self.schema = [
            "wheel",
            "brake",
            "throttle",
            "clutch",
            "unused_1",
            "unused_2",
            "unused_3",
            "unused_4",
            "gearUP",
            "gearDOWN",
            "drs",
            "leftRedUpper",
            "unused_5",
            "unused_6",
            "unused_7",
            "unused_8",
            "unused_9",
        ]
        print("Initialized Wheel: %s" % self.wheel.get_name())

    def get(self):
        out = [0] * (self.num_axes + self.num_buttons)
        it = 0
        pygame.event.pump()
        for i in range(self.num_axes):
            out[it] = self.wheel.get_axis(i)
            it += 1
        for i in range(self.num_buttons):
            out[it] = self.wheel.get_button(i)
            it += 1
        out_dict = dict(zip(self.schema, out))
        return out_dict


def data_loop(output_dir):
    wheel_getter = WheelGetter()
    wheel_cols = sorted(wheel_getter.get().keys())
    recording = False
    while True:
        try:
            telemetry_data, addr = SOCKET.recvfrom(1289)
            wheel_data = wheel_getter.get()
        except socket.timeout:
            if not recording:
                print("Waiting for telemetry data")
            else:
                recording = False
            continue
        if telemetry_data:
            if not recording:
                output_file = os.path.join(output_dir, "telemetry_{}.csv".format(time.strftime("%Y%m%d-%H%M%S")))
                if os.path.exists(output_file):
                    print("File exists: {}".format(output_file))
                    exit(0)
                print("Saving to: {}".format(output_file))
                df = pd.DataFrame(data=[], columns=["timestamp"] + LIST_KEYS + wheel_cols)
                df.to_csv(output_file, index=False)
                recording = True
            x = 0
            df["timestamp"] = [time.time()]
            for i in range(len(LIST_KEYS)):
                if NUM_BYTES[i] == 4:
                    value = struct.unpack("f", telemetry_data[x : x + 4])[0]
                else:
                    value = struct.unpack("b", telemetry_data[x : x + 1])[0]
                if i != 7:
                    df[LIST_KEYS[i]] = [value]
                else:
                    df[LIST_KEYS[i]] = [value * MPS_MPH_KMH]
                x += NUM_BYTES[i]

            for col in wheel_cols:
                df[col] = wheel_data[col]
            df.to_csv(output_file, mode="a", header=False, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", help="Show help.", action="help")
    parser.add_argument("-o", "--output_dir", help="Storage output folder.", required=False, default="", type=str)
    args = parser.parse_args()

    data_loop(args.output_dir)

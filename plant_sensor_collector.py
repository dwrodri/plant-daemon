import signal
import sys
import time
from datetime import datetime
import spidev
import RPi.GPIO as GPIO
import requests
from tzinfo import timezone
from typing import List

TRANSMIT_SIZE = 30


spi_ch = 0
# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

# to use Raspberry Pi board pin numbers
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

def get_adc(channel: int) -> int:
    # Make sure ADC channel is 0 or 1
    if channel != 0:
        channel = 1

    # Construct SPI message
    #  First bit (Start): Logic high (1)
    #  Second bit (SGL/DIFF): 1 to select single mode
    #  Third bit (ODD/SIGN): Select channel (0 or 1)
    #  Fourth bit (MSFB): 0 for LSB first
    #  Next 12 bits: 0 (don't care)
    msg = 0b11
    msg = ((msg << 1) + channel) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    return adc

def upload_data(data_queue: List[Tuple[datetime, int]]):
    pass

def main(sensors: int):
    data_queues = [[],[]]
    try:
        while True:
            # Read ADC channels which provide latest read of moisture sensors
            for sensor_channel in range(sensors):
                data_queues[sensor_channel].append((datetime.now(timezone.utc), get_adc(sensor_channel)))
                if len(data_queue[sensor_channel]) >= TRANSMIT_SIZE:
                    upload_data(data_queue[sensor_channel])
            time.sleep(0.5)
    finally:
        GPIO.cleanup()
                



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect data from the sensors and send over to planthub')
    parser.add_argument('-s', '--sensors', type=int, choices=[1,  2], required=True, help='Number of sensors (either  1 or  2).')
    args = parser.parse_args()
    main(args)

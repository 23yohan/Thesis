import numpy
import serial
import time
import matplotlib

# Baud Rates
DATA_BAUD = 921600
CLI_BAUD = 115200

config_name = '/Users/matthew/Documents/University/Thesis/Thesis/configFiles/basicProfile060622.cfg'
cli_port = {}
data_port = {}


def init_serial():
    # This function only works for mac setups
    global cli_port
    global data_port

    cli_port = serial.Serial('/dev/tty.usbmodemR20910491', CLI_BAUD)
    data_port = serial.Serial('/dev/tty.usbmodemR20910494', DATA_BAUD)

    return cli_port, data_port


def init_config_file(config, cli):
    # Function reads through a config file and processes the parameters

    config_param = [line.rstrip('\r\n') for line in open(config)]

    for i in config_param:
        cli.write((i + '\n').encode())
        print(i)
        time.sleep(0.01)


def parse_config(config_file_name):
    config_param = {}  # Empty dictionary to store the parameters

    config = [line.rstrip('\r\n') for line in open(config_file_name)]

    for i in config:
        split_data = i.split(' ')

        # Receiving and Transmitting antennas config (Change with different config files)
        numTx = 2
        numRx = 4

        # Get the profile config information
        if "profileCfg" in split_data[0]:
            startFreq = int(float(split_data[2]))
            idleTime = int(split_data[3])
            rampEndTime = float(split_data[5])
            freqSlopeConst = float(split_data[8])
            numAdcSamples = int(split_data[10])
            numAdcSamplesRoundTo2 = 1;

            while numAdcSamples > numAdcSamplesRoundTo2:
                numAdcSamplesRoundTo2 = numAdcSamplesRoundTo2 * 2;

            digOutSampleRate = int(split_data[11]);

        elif "frameCfg" in split_data[0]:
            chirpStartIdx = int(split_data[1]);
            chirpEndIdx = int(split_data[2]);
            numLoops = int(split_data[3]);
            numFrames = int(split_data[4]);
            framePeriodicity = float(split_data[5]);

        # Combine the read data to obetain the configuration parameters
        numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
        config_param["numDopplerBins"] = numChirpsPerFrame / numTx
        config_param["numRangeBins"] = numAdcSamplesRoundTo2
        config_param["rangeResolutionMeters"] = (3e8 * digOutSampleRate * 1e3) / (
                2 * freqSlopeConst * 1e12 * numAdcSamples)
        config_param["rangeIdxToMeters"] = (3e8 * digOutSampleRate * 1e3) / (
                2 * freqSlopeConst * 1e12 * config_param["numRangeBins"])
        config_param["dopplerResolutionMps"] = 3e8 / (
                2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * config_param["numDopplerBins"] * numTx)
        config_param["maxRange"] = (300 * 0.9 * digOutSampleRate) / (2 * freqSlopeConst * 1e3)
        config_param["maxVelocity"] = 3e8 / (4 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * numTx)

        return config_param

def main():
    cli, data = init_serial()
    init_config_file(config_name, cli)


if __name__ == '__main__':
    main()

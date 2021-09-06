# Copyright (c) 2021 Arm Limited. All rights reserved.

# Virtual Streaming Interface instance 0 Python script: Audio Input

import logging
import wave

# Set verbosity level
#verbosity = logging.DEBUG
#verbosity = logging.INFO
verbosity = logging.ERROR

# [debugging] Verbosity settings
level = { 10: "DEBUG",  20: "INFO",  30: "WARNING",  40: "ERROR" }
logging.basicConfig(format='Py: [%(levelname)s]\t%(message)s', level = verbosity)
logging.info("Verbosity level is set to " + level[verbosity])


# Data, user registers and IRQ
Data = [0] * 0x2000     # Data buffer
Regs = [0] * 32         # User registers
IRQ  =  0               # Interrupt request

# DMA registers
DMA_Control   = 0
DMA_BlockSize = 0

# DMA Control register definitions
DMA_Control_Enable_Msk    = 1<<0
DMA_Control_Direction_Msk = 1<<1
DMA_Control_Direction_P2M = 0<<1
DMA_Control_Direction_M2P = 1<<1

# Timer registers
Timer_Control  = 0
Timer_Interval = 0

# Timer Control register definitions
Timer_Control_Run_Msk      = 1<<0
Timer_Control_Periodic_Msk = 1<<1
Timer_Control_Trig_IRQ_Msk = 1<<2

# User registers
CONTROL     = 0  # Regs[0]
CHANNELS    = 0  # Regs[1]
SAMPLE_BITS = 0  # Regs[2]
SAMPLE_RATE = 0  # Regs[3]

# User CONTROL register definitions
CONTROL_ENABLE_Msk = 1<<0


# Write CONTROL register
def wrCONTROL(data):
    global CONTROL
    if ((data ^ CONTROL) & CONTROL_ENABLE_Msk) != 0:
        if (data & CONTROL_ENABLE_Msk) != 0:
            logging.info("Enable Receiver")
            openWAVE('test.wav')
            if ((DMA_Control & DMA_Control_Enable_Msk) != 0):
                loadAudioFrames(DMA_BlockSize)
        else:
            logging.info("Disable Receiver")
            closeWAVE()
    CONTROL = data

# Write CHANNELS register
def wrCHANNELS(data):
    global CHANNELS
    CHANNELS = data
    logging.info("Number of channels: {}".format(data))

# Write SAMPLE_BITS register
def wrSAMPLE_BITS(data):
    global SAMPLE_BITS
    SAMPLE_BITS = data
    logging.info("Sample bits: {}".format(data))

# Write SAMPLE_RATE register
def wrSAMPLE_RATE(data):
    global SAMPLE_RATE
    SAMPLE_RATE = data
    logging.info("Sample rate: {}".format(data))


AudioFrames = bytearray()

# Open WAVE file
def openWAVE(name):
    global WAVE
    logging.info("Open WAVE file: {}".format(name))
    WAVE = wave.open(name, 'rb')
    logging.info("  Number of channels: {}".format(WAVE.getnchannels()))
    logging.info("  Sample bits: {}".format(WAVE.getsampwidth()))
    logging.info("  Sample rate: {}".format(WAVE.getframerate()))
    logging.info("  Number of frames: {}".format(WAVE.getnframes()))

# Read WAVE frames
def readWAVE(n):
    global WAVE, AudioFrames
    logging.info("Read WAVE frames")
    AudioFrames = WAVE.readframes(n)

# Close WAVE file
def closeWAVE():
    global WAVE
    logging.info("Close WAVE file")
    WAVE.close()


# Load audio frames into data buffer
def loadAudioFrames(block_size):
    global Data
    logging.info("Load audio frames into data buffer")
    frame_size = CHANNELS * ((SAMPLE_BITS + 7) // 8)
    frames_max = block_size // frame_size
    readWAVE(frames_max)
    n = len(AudioFrames)
    for i in range(n>>2):
        Data[i] = ((AudioFrames[(4*i) + 0] <<  0) |
                   (AudioFrames[(4*i) + 1] <<  8) |
                   (AudioFrames[(4*i) + 2] << 16) |
                   (AudioFrames[(4*i) + 3] << 24))
    for i in range(n>>2, block_size>>2):
        Data[i] = 0      


# Initialize
def init():
    logging.info("Python function init() called")


# Read/Write data buffer
def rwData(cmd, addr, data):
    global Data
    logging.info("Python function rwData() called")

    if   cmd == "read":
        data = Data[addr]
        logging.debug("Read at index {}: {}".format(addr, data))
    elif cmd == "write":
        Data[addr] = data
        logging.debug("Write at index {}: {}".format(addr, data))
    else:
        logging.error("Unknown command {}".format(cmd))

    return data


# Read/Write user registers
def rwRegs(cmd, addr, data):
    global Regs
    logging.info("Python function rwRegs() called")

    if   cmd == "read":
        data = Regs[addr]
        logging.debug("Read at index {}: {}".format(addr, data))
    elif cmd == "write":
        if   addr == 0:
            wrCONTROL(data)
        elif addr == 1:
            wrCHANNELS(data)
        elif addr == 2:
            wrSAMPLE_BITS(data)
        elif addr == 3:
            wrSAMPLE_RATE(data)
        Regs[addr] = data
        logging.debug("Write at index {}: {}".format(addr, data))
    else:
        logging.error("Unknown command {}".format(cmd))

    return data


# Read/Write interrupt request
def rwIRQ(cmd, addr, data):
    global IRQ
    logging.info("Python function rwIRQ() called")

    if   cmd == "read":
        data = IRQ
        logging.debug("Read interrupt request: {}".format(data))
    elif cmd == "write":
        IRQ = data
        logging.debug("Write interrupt request: {}".format(data))
    else:
        logging.error("Unknown command {}".format(cmd))

    return data


# Write DMA registers
def wrDMA(cmd, addr, data):
    global DMA_Control, DMA_BlockSize
    logging.info("Python function wrDMA() called")

    if   addr == 0:
        DMA_Control = data
        logging.debug("Write DMA_Control: {}".format(data))
    elif addr == 2:
        DMA_BlockSize = data
        logging.debug("Write DMA_BlockSize: {}".format(data))
    else:
        logging.error("Unknown address {}".format(addr))

    return data


# Write Timer registers
def wrTimer(cmd, addr, data):
    global Timer_Control, Timer_Interval
    logging.info("Python function wrTimer() called")

    if   addr == 0:
        Timer_Control = data
        logging.debug("Write Timer_Control: {}".format(data))
    elif addr == 1:
        Timer_Interval = data
        logging.debug("Write Timer_Interval: {}".format(data))
    else:
        logging.error("Unknown address {}".format(addr))

    return data


# Timer event
def timerEvent(cmd, addr, data):
    logging.info("Python function timerEvent() called")

    if ((DMA_Control & DMA_Control_Enable_Msk) != 0):
        loadAudioFrames(DMA_BlockSize)

    return data


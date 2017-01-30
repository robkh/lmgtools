#!/usr/bin/python

# powerlog450.py
#
# Log measured values from ZES Zimmer LMG450 Power Analyzer
#
# 2012-07, Jan de Cuveland
# 2017-01, Robert Khasanov

import argparse, sys, time, lmg450

VAL = "count sctc cycr utrms itrms udc idc ucf icf uff iff p pf freq".split()

def main():
    parser = argparse.ArgumentParser(
        description = "Log measured values from ZES Zimmer LMG450 Power Meter")
    parser.add_argument("-p", "--port", dest="comport", default='/dev/ttyS0', help = "COM port connected to LMG450")
    parser.add_argument("-b", "--baudrate", dest="baudrate", default=115200, help = "Baudrate of the interface")
    # add rtscts arg
    parser.add_argument("logfile", help = "Log file name")
    parser.add_argument("-v", "--verbose", dest = "verbose", type = int, default=0, help = "Verbose")
    parser.add_argument("-l", "--lowpass", dest = "lowpass", action="store_true", default=False,
                        help = "Enable 60 Hz low pass filter")
    parser.add_argument("-i", "--interval", dest="interval", type=float, default=0.5,
                        help = "Measurement interval in seconds")
    args = parser.parse_args()

    print "connecting to port", args.comport, "at baudrate", args.baudrate
    lmg = lmg450.lmg450(args.comport, args.baudrate)
     
    print "performing device reset"
    lmg.reset()
     
    print "device found:", lmg.read_id()[1]

    print "setting up device"
    errors = lmg.read_errors()

        # set measuremnt interval
    lmg.send_short_cmd("CYCL " + str(args.interval));

        # 60Hz low pass
    if args.lowpass == True:
        lmg.send_short_cmd("FAAF 0");
        lmg.send_short_cmd("FILT 4");

    lmg.set_ranges(10., 250.)
    lmg.select_values(VAL)

    log = open(args.logfile, "w");
    i = 0
    try:
        lmg.cont_on()
        log.write("# time " + " ".join(VAL) + "\n")
        print "writing values to", args.logfile
        print "press CTRL-C to stop"
        while True:
            data = lmg.read_values()
            i += 1
            data.insert(0, time.time())
            if args.verbose:
                sys.stdout.write(" ".join([ str(x) for x in data ]) + "\n")
            else:
                sys.stdout.write("\r{0}".format(i))
            sys.stdout.flush()
            log.write(" ".join([ str(x) for x in data ]) + "\n")
            log.flush()
    except KeyboardInterrupt:
        print
     
    lmg.cont_off()
    log.close()

    lmg.disconnect()
    print "done,", i, "measurements written"


if __name__ == "__main__":
    main()

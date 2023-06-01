#!/usr/bin/python

import sys, os
import cv2 

def demo(image):

    cv2.putText()

def main(args):

    from echolib_wrapper import EcholibWrapper
    processor = lambda d: EcholibWrapper(d, args.out_channel, args.in_channel)

    demo = processor(TSRDemo(cfg_filename, weights_filename, catalog_folder=catalog_folder))

    try:
        demo.run()
    except KeyboardInterrupt:
        pass

if __name__=='__main__':
    main(args)


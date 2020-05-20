import cv2
import sys
import os
import numpy as np
import logging as log
from time import time
from openvino.inference_engine import IENetwork, IEPlugin

im_path = '~/Documents/MSDS462/assignment6/test/testcars/5.jpg'

def main():
    log.basicConfig(format="[ %(levelname)s ] %(message)s", level=log.INFO, stream=sys.stdout)
    model_xml = "~/Documents/MSDS462/assignment6/IR_model/IR_model.xml"
    model_bin = "~/Documents/MSDS462/assignment6/IR_model/IR_model.bin"

    # Plugin initialization for specified device
    plugin = IEPlugin(device="MYRIAD")

    # Read IR
    log.info("Loading network files:\n\t{}\n\t{}".format(model_xml, model_bin))
    net = IENetwork(model=model_xml, weights=model_bin)

    log.info("Preparing input blobs")
    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))

    # Prepare image
    n, c, h, w = net.inputs[input_blob].shape
    print(n, c, h, w)
    prepimg = np.ndarray(shape=(n, c, h, w))

    # Read image as grayscale
    im = cv2.imread(im_path, 0)    

    # Resize image
    resized_image = cv2.resize(im, (28, 28), interpolation = cv2.INTER_CUBIC)
    
    # Change data layout from HW to NCHW
    prepimg[0,0,:,:] = resized_image

    # Loading model to the plugin
    log.info("Loading model to the plugin")
    exec_net = plugin.load(network=net)
    del net

    # Start sync inference
    log.info("Starting inference ({} iterations)".format(1))
    infer_time = []
    t0 = time()
    res = exec_net.infer(inputs={input_blob: prepimg})
    infer_time.append((time()-t0)*1000)
    log.info("Average running time of one iteration: {} ms".format(np.average(np.asarray(infer_time))))
    
    # Processing output blob
    log.info("Processing output blob")
    res = res[out_blob]
    print(res)

    del exec_net
    del plugin

if __name__ == "__main__":
    main()

import struct

import tensorflow as tf
import numpy as np

export_dir = "/home/klein/dev/OpenNMT-tf/models/averaged-ende-export500k/export/manual/1519808686"
quantize = False

with tf.Session() as sess:
    meta_graph = tf.saved_model.loader.load(sess, ["serve"], export_dir)
    variables = tf.trainable_variables()
    variables_value = sess.run(variables)

    with open("model.bin", "wb") as model:
        model.write(struct.pack("I", len(variables)))
        for tensor, value in zip(variables, variables_value):
            if "kernel" in tensor.name:
                value = np.transpose(np.squeeze(value))
            model.write(struct.pack("H", len(tensor.name) + 1))
            model.write(tf.compat.as_bytes(tensor.name))
            model.write(struct.pack('B', 0))
            model.write(struct.pack("B", len(value.shape)))
            for dim in value.shape:
                model.write(struct.pack("I", dim))
            if quantize:
                value *= 1000
                value = value.astype(np.int16)
            model.write(struct.pack("B", value.dtype.itemsize))
            model.write(struct.pack("I", value.size))
            model.write(value.tobytes())
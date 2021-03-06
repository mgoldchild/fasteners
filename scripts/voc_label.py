"""
original: http://pjreddie.com/media/files/voc_label.py
"""

import argparse
import os
import pickle
import sys
import xml.etree.ElementTree as ET
from os import getcwd, listdir
from os.path import join

sets = []
classes = []
voc_dir_name = ""


def convert(size, box):
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(image_id):
    in_file = open(voc_dir_name + "/Annotations/%s.xml" % (image_id))
    out_file = open(voc_dir_name + "/labels/%s.txt" % (image_id), "w")
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)

    for obj in root.iter("object"):
        difficult = obj.find("difficult").text
        cls = obj.find("name").text
        if (
            cls not in classes or int(difficult) == 1
        ):  # TODO: Y if difficult is 1 then it will be skipped?
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find("bndbox")
        b = (
            float(xmlbox.find("xmin").text),
            float(xmlbox.find("xmax").text),
            float(xmlbox.find("ymin").text),
            float(xmlbox.find("ymax").text),
        )
        bb = convert((w, h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + "\n")


def get_all_images(image_set):
    return (
        open(voc_dir_name + "/ImageSets/Main/%s.txt" % image_set).read().strip().split()
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsname", "-d", help="dataset name", type=str)
    parser.add_argument(
        "--sets",
        "-s",
        help="comma split of string of filename type. e.g. train,valid,test",
        type=str,
    )
    parser.add_argument(
        "--classes",
        "-c",
        help="comma split string of class name. e.g. S001,S002,S003",
        type=str,
    )
    args = parser.parse_args()

    if args.classes is None:
        raise Exception("classes is need!")
    classes = args.classes.split(",")

    if args.sets is None:
        raise Exception("sets is need!")
    sets = args.sets.split(",")

    if args.dsname is None:
        raise Exception("dataset name is need!")
    voc_dir_name = "datasets_voc/{}".format(args.dsname)

    print("classes", classes)
    print("sets", sets)
    print("voc_dir_name", voc_dir_name)

    label_dir = "{}/labels".format(voc_dir_name)
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)

    for image_set in sets:
        image_ids = get_all_images(image_set)
        for image_id in image_ids:
            convert_annotation(image_id)

        wd = getcwd()
        # Create full path file
        list_file = open("%s.txt" % (image_set), "w")
        for image_id in image_ids:
            list_file.write("%s/%s/JPEGImages/%s.jpg\n" % (wd, voc_dir_name, image_id))
        list_file.close()

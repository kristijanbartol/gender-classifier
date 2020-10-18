import os
import cv2
from PIL import Image
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl
from copy import deepcopy
from scipy.spatial.transform import Rotation as rot
import torch
import h5py
import json
import math
import copy
from random import random

from const import PELVIS, H36M_KPTS_15, H36M_PARTS_15, KPTS_17, BODY_PARTS_17, \
        KPTS_15, OPENPOSE_PARTS_15, RADIUS, K
from data_utils import fit_to_frame


DATASET_DIR = './dataset/'

PEOPLE3D_H = 480
PEOPLE3D_W = 640

GRID_SIZE = 100

GREEN = (0, 255, 0)
RED = (255, 0, 0)


def draw_keypoints(kpts_2d, h, w):
    img = np.zeros((h, w, 3), np.uint8)

    for kpt_idx, kpt in enumerate(kpts_2d):
        kpt = tuple(kpt[:2])
        print(kpt)
        if kpt_idx == 5:
            img = cv2.circle(img, kpt, radius=1, color=(0, 255, 0), thickness=-1)
        else:
            img = cv2.circle(img, kpt, radius=1, color=(0, 0, 255), thickness=-1)

    cv2.imshow('2d keypoints', img)
    cv2.waitKey(0)


def draw_txt(txt_path):
    kpts_2d = []
    with open(txt_path) as f:
        lines = [x[:-1] for x in f.readlines()][1:]
    for line_idx, line in enumerate(lines):
        if line_idx + 1 in KPTS_15:
            kpts_2d.append([float(x) for x in line.split(' ')])
    kpts_2d = np.array([x[:3] for x in kpts_2d], dtype=np.float32)
    draw_keypoints(kpts_2d, 480, 640)


def draw_openpose(json_fpath, img_path):
    # TODO: Put original image as background.
    #img = np.zeros((1000, 1000, 3), dtype=np.uint8)
    img = cv2.imread(img_path)

    with open(json_fpath) as fjson:
        data = json.load(fjson)
    pose_2d = np.array(data['people'][0]['pose_keypoints_2d'], dtype=np.float32)
    pose_2d = np.delete(pose_2d, np.arange(2, pose_2d.size, 3))
    print(pose_2d)
    for idx in range(int(pose_2d.shape[0] / 2)):
        coord = (pose_2d[idx*2], pose_2d[idx*2+1])
        print(coord)
        img = cv2.circle(img, coord, radius=1, color=(0, 255, 0), thickness=-1)

    for part in OPENPOSE_PARTS_15:
        start_point = (pose_2d[part[0]*2], pose_2d[part[0]*2+1])
        end_point = (pose_2d[part[1]*2], pose_2d[part[1]*2+1])
        img = cv2.line(img, start_point, end_point, (255, 0, 0), thickness=1)

    cv2.imshow('2d keypoints', img)
    cv2.waitKey(0)


### USED IN MAIN ###

def prepare_orig_img(orig_img):
    bigger_dim_size = np.max(orig_img.shape)
    scale_factor = bigger_dim_size / float(GRID_SIZE)
    new_h = int(orig_img.shape[0] / scale_factor)
    new_w = int(orig_img.shape[1] / scale_factor)
    orig_img = cv2.resize(orig_img, (new_w, new_h))

    h, w, _ = orig_img.shape
    h_off = int((GRID_SIZE - h) / 2)
    w_off = int((GRID_SIZE - w) / 2)

    full_img = np.zeros((GRID_SIZE, GRID_SIZE, 3), 
            dtype=np.uint8)
    full_img[h_off:h_off+h, w_off:w_off+w] = orig_img
    return full_img


def write_text(pose_2d_img, y_pred, y_targ):
    return cv2.putText(pose_2d_img,
            'Male' if y_pred == 0 else 'Female', 
            (GRID_SIZE, 0), 
            cv2.FONT_HERSHEY_SIMPLEX,
            0.1, 
            GREEN if y_pred == y_targ else RED,
            2)


def draw_pose_2d(pose_2d, img_size):

    def is_zero(kpt):
        return not np.any(kpt)

    pose_2d = pose_2d[:, :2]
    pose_2d = fit_to_frame(pose_2d, GRID_SIZE)

    img = np.zeros((GRID_SIZE, GRID_SIZE, 3), 
            dtype=np.uint8)

    for kpt in pose_2d:
        if is_zero(kpt):
            continue
        img = cv2.circle(img, tuple(kpt), radius=1, 
                color=(0, 255, 0), thickness=-1)

    for part in OPENPOSE_PARTS_15:
        start_point = tuple(pose_2d[part[0]])
        end_point = tuple(pose_2d[part[1]])
        if is_zero(start_point) or is_zero(end_point):
            continue
        img = cv2.line(img, start_point, end_point, 
                (255, 0, 0), thickness=1)

    return img


def create_grid(pose_2ds, Y_pred, Y_targ, img_paths):
    img_grid = np.zeros(
            (pose_2ds.shape[0] * 2,  GRID_SIZE, GRID_SIZE, 3),
            dtype=np.uint8)
    pose_2ds = copy.deepcopy(pose_2ds)
    pose_2ds = np.squeeze(pose_2ds, axis=3)
    pose_2ds = np.swapaxes(pose_2ds, 1, 2)

    for pose_idx, pose_2d in enumerate(pose_2ds):
        orig_img = cv2.imread(img_paths[pose_idx])
        img_size = max(orig_img.shape[0], orig_img.shape[1])
        print(f'{img_paths[pose_idx]}: {img_size}')
        orig_img = prepare_orig_img(orig_img)

        pose_2d_img = draw_pose_2d(pose_2d, img_size)
        pose_2d_img = write_text(pose_2d_img, 
                Y_pred[pose_idx],
                Y_targ[pose_idx])

        img_grid[2*pose_idx] = pose_2d_img
        img_grid[2*pose_idx+1] = orig_img

    return img_grid

####################


if __name__ == '__main__':
    pass


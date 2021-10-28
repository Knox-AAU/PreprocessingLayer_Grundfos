"""
This module adds the MI functionality for the segmentation of documents.
"""

import os
import argparse
import random
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision.transforms import transforms
import cv2
import numpy as np


SEED = 1234
random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False


CHECKPOINT_PATH = os.path.join(os.getcwd(),'classification',"model_196000.pth")

CATEGORIES2LABELS = {
    0: "bg",
    1: "text",
    2: "title",
    3: "list",
    4: "table",
    5: "figure"
}

CATEGORIES2COLORS = {
    "text": [0, 0, 255],
    "title": [0, 255, 255],
    "list": [255, 0, 255],
    "table": [255, 0 , 0],
    "figure": [0, 255, 0]
}


def __get_instance_segmentation_model__(num_classes):
    """
    Initializes the MI-model.
    """
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256

    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask,
        hidden_layer,
        num_classes
    )
    return model

def infer_image_from_matrix(image):
    """
    Runs inference on an image. The image is passed as a matrix.
    Returns a list of predictions for the image.
    """
    num_classes = 6

    # Get model and send to GPU
    model = __get_instance_segmentation_model__(num_classes)
    model.cuda()

    # Assure model exists and prepare it
    assert os.path.exists(CHECKPOINT_PATH)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
    model.load_state_dict(checkpoint['model'])
    model.eval()

    rat = 1300 / image.shape[0]
    image = cv2.resize(image, None, fx=rat, fy=rat)

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor()
    ])
    image = transform(image)

    # Classify document elements
    with torch.no_grad():
        prediction = model([image.cuda()])

    return prediction

def infer_image_from_file(image_path):
    """
    Runs inference on an image. The image is passed as a path to an image file.
    Returns a list of predictions for the image.
    """
    num_classes = 6

    # Get model and send to GPU
    model = __get_instance_segmentation_model__(num_classes)
    model.cuda()

    # Assure model exists and prepare it
    assert os.path.exists(CHECKPOINT_PATH)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
    model.load_state_dict(checkpoint['model'])
    model.eval()

    # Ensure that image exists
    assert os.path.exists(image_path)

    # Transform image
    image = cv2.imread(image_path)
    rat = 1300 / image.shape[0]
    image = cv2.resize(image, None, fx=rat, fy=rat)

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor()
    ])
    image = transform(image)

    # Classify document elements
    with torch.no_grad():
        prediction = model([image.cuda()])

    return prediction

def infer_image_with_mask(image_path: str, output_path: str, minimum_score: float = 0.7):
    """
    Runs inference on an image. The image is passed as a path to an image file.
    Writes a new image with masks showing the predictions.
    """
    num_classes = 6

    # Get model and send to GPU
    model = __get_instance_segmentation_model__(num_classes)
    model.cuda()

    # Assure model exists and prepare it
    assert os.path.exists(CHECKPOINT_PATH)
    checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
    model.load_state_dict(checkpoint['model'])
    model.eval()

    # Ensure that image exists
    assert os.path.exists(image_path)

    # Transform image
    image = cv2.imread(image_path)
    rat = 1300 / image.shape[0]
    image = cv2.resize(image, None, fx=rat, fy=rat)

    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor()
    ])
    image = transform(image)

    # Classify document elements
    with torch.no_grad():
        prediction = model([image.cuda()])

    image = torch.squeeze(image, 0).permute(1, 2, 0).mul(255).numpy().astype(np.uint8)

    for pred in prediction:
        for idx, mask in enumerate(pred['masks']):
            if pred['scores'][idx].item() < minimum_score:
                continue

            box = list(map(int, pred["boxes"][idx].tolist()))
            label = CATEGORIES2LABELS[pred["labels"][idx].item()]

            score = pred["scores"][idx].item()

            image = overlay_annotations(image, box, label, score)

    cv2.imwrite(output_path, image)

def multi_infer(in_dir: str, out_dir: str, minimum_score: float = 0.7):
    """
    Runs inference on all images in a specified directory
    """
    for file in os.listdir(in_dir,):
        if file.endswith(".png"):
            infer_image_with_mask(os.path.join(in_dir,file), os.path.join(out_dir, os.path.basename(file)), minimum_score)


def overlay_annotations(image, box, label, score):
    """
    Creates the overlay mask and adds it to the image.
    """
    mask_color = CATEGORIES2COLORS[label]
    image = image.copy()
    
    # draw on color mask
    cv2.rectangle(
        image,
        (box[0], box[1]),
        (box[2], box[3]),
        mask_color, 2
    )

    (label_size_width, label_size_height), base_line = \
        cv2.getTextSize(
            "{}: {:.3f}".format(label, score),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.3, 1
        )

    cv2.rectangle(
        image,
        (box[0], box[1] + 10),
        (box[0] + label_size_width, box[1] + 10 - label_size_height),
        (223, 128, 255), # Color of the box with the label
        cv2.FILLED
    )

    cv2.putText(
        image,
        "{}: {:.3f}".format(label, score),
        (box[0], box[1] + 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.3, (0, 0, 0), 1
    )

    return image

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar = "IN", type = str, help = "Input path. Either a PNG-file or a directory of PNGs.")
    parser.add_argument("output", metavar = "OUT", type = str, help = "Output path. Either a PNG-file or a directory.")
    parser.add_argument("-s", "--score", metavar = "S", type = float, default = 0.7, help = "Minimum threshold for the prediction accuracy. Value between 0 to 1.")
    argv = parser.parse_args()

    if os.path.isfile(argv.input) and os.path.isfile(argv.output):
        if argv.input.endswith(".png") and argv.output.endswith(".png"):
            infer_image_with_mask(argv.input, argv.output, argv.score)
        else:
            print("Wrong file endings. Input and out files must be PNG-format.")
    elif os.path.isdir(argv.input) and os.path.isdir(argv.output):
        multi_infer(argv.input, argv.output, argv.score)
    else:
        print("Could not find input file/directory.")
    exit()

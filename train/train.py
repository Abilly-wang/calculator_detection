from ultralytics import YOLO
import xml.etree.ElementTree as ET
import os
import shutil


def get_calculator_dicts(directory):
    dataset_dicts = []
    images_dir_path = os.path.join(directory, 'images')
    ann_dir_path = os.path.join(directory, 'labels')
    for filename in [file for file in os.listdir(ann_dir_path) if file.endswith('.xml')]:
        # Construct the corresponding path to the annotation file (assuming it's a .xml)
        annotation_path = os.path.join(ann_dir_path, filename)
        
        # Parse the XML file or however your annotations are stored
        tree = ET.parse(annotation_path)
        root = tree.getroot()
        
        # Construct the full path to the image file
        img_path = os.path.join(images_dir_path, root.find('filename').text)
        # Initialize the record dictionary
        record = {}
        
        # Populate required fields for Detectron2
        record["file_name"] = img_path
        record["height"] = int(root.find('./size/height').text)
        record["width"] = int(root.find('./size/width').text)
        record["image_id"] = os.path.splitext(filename)[0]
        
        # Initialize the list of annotations (bounding boxes)
        objs = []
        for member in root.findall('object'):
            # Extract the points of the bounding box
            xmin = int(member.find('bndbox/xmin').text)
            ymin = int(member.find('bndbox/ymin').text)
            xmax = int(member.find('bndbox/xmax').text)
            ymax = int(member.find('bndbox/ymax').text)
            
            center_x = ((xmin + xmax) / 2) / record["width"]
            center_y = ((ymin + ymax) / 2) / record["height"]
            width = (xmax - xmin) / record["width"]
            height = (ymax - ymin) / record["height"]

            # Format according to Detectron2's specifications
            obj = {
                "bbox": [center_x, center_y, width, height],
                "class": 0, # assuming calculator is the only category
            }
            objs.append(obj)
        
        record["annotations"] = objs
        dataset_dicts.append(record)

    length = int(len(dataset_dicts) * 0.9)
    train_data = dataset_dicts[:length]
    val_data = dataset_dicts[length:]
    base_dir = os.path.join('./dataset', 'dataset_yolo')
    image_dir = os.path.join(base_dir, 'images')
    label_dir = os.path.join(base_dir, 'labels')
    for d in train_data:
        label_dir_train = os.path.join(label_dir, 'train')
        image_dir_train = os.path.join(image_dir, 'train')
        os.makedirs(label_dir_train, exist_ok=True)
        os.makedirs(image_dir_train, exist_ok=True)
        file_name  = d['image_id'] + '.txt'
        # copy images to dataset_yolo/images
        shutil.copy(d["file_name"], image_dir_train)
        with open(os.path.join(label_dir_train, file_name), 'w') as f:
            for obj in d['annotations']:
                f.write(str(obj['class']) + ' ' + ' '.join([str(a) for a in obj['bbox']]) + '\n')
    for d in val_data:
        label_dir_val = os.path.join(label_dir, 'val')
        image_dir_val = os.path.join(image_dir, 'val')
        os.makedirs(label_dir_val, exist_ok=True)
        os.makedirs(image_dir_val, exist_ok=True)
        file_name  = d['image_id'] + '.txt'
        # copy images to dataset_yolo/images
        shutil.copy(d["file_name"], image_dir_val)
        with open(os.path.join(label_dir_val, file_name), 'w') as f:
            for obj in d['annotations']:
                f.write(str(obj['class']) + ' ' + ' '.join([str(a) for a in obj['bbox']]) + '\n')

# get_calculator_dicts('./data')  
# model = YOLO('./yolov8n-oiv7.pt')
# results = model.train(data='dataset.yaml', epochs=100, imgsz=640,device='0', batch=2, workers=0, freeze=20)
# model = YOLO('./runs/detect/train7/weights/best.pt')
# predictions = model.predict(source='./datasets/dataset_yolo/images/val')
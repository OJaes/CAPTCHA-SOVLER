import argparse
from PIL import Image, ImageDraw
import os
from ultralytics import YOLO
from os.path import basename

def split_image_into_grid(image_path, output_folder, grid_size):
    image = Image.open(image_path)
    image_width, image_height = image.size

    cell_width = image_width // grid_size
    cell_height = image_height // grid_size

    cropped_images = []
    os.makedirs(output_folder, exist_ok=True)

    i = 0
    for row in range(grid_size):
        for col in range(grid_size):
            i += 1
            left = col * cell_width
            upper = row * cell_height
            right = (col + 1) * cell_width
            lower = (row + 1) * cell_height
            cropped_image = image.crop((left, upper, right, lower))

            cropped_image_path = os.path.join(output_folder, f"image_{i}.png")
            cropped_image.save(cropped_image_path)
            cropped_images.append(cropped_image_path)

    return cropped_images

def has_fire_hydrant(results, fire_hydrant_index):
    for result in results:
        for box in result.boxes:
            if box.cls == fire_hydrant_index:
                return True
    return False

def predict_images(model, image_paths, fire_hydrant_index):
    true_images = []
    for image_path in image_paths:
        results = model(image_path)
        if has_fire_hydrant(results, fire_hydrant_index):
            true_images.append(image_path)
    return true_images

def combine_images(original_image_path, true_images, grid_size, output_path):
    original_image = Image.open(original_image_path)
    image_width, image_height = original_image.size

    cell_width = image_width // grid_size
    cell_height = image_height // grid_size

    draw = ImageDraw.Draw(original_image)
    for true_image in true_images:
        image_num = int(os.path.splitext(os.path.basename(true_image))[0].split('_')[1])
        row = (image_num - 1) // grid_size
        col = (image_num - 1) % grid_size
        left = col * cell_width
        upper = row * cell_height
        right = (col + 1) * cell_width
        lower = (row + 1) * cell_height

        draw.rectangle([left, upper, right, lower], outline='red', width=5)
        center_x = left + cell_width // 2
        center_y = upper + cell_height // 2
        v_size = min(cell_width, cell_height) // 4
        draw.line((center_x - v_size, center_y, center_x, center_y + v_size), fill='green', width=50)
        draw.line((center_x, center_y + v_size, center_x + v_size, center_y - v_size), fill='green', width=50)

    original_image.save(output_path)

def main():
    image_path = input("입력 이미지의 경로를 입력하세요: ")
    grid_size = int(input("이미지를 나눌 그리드 크기를 입력하세요: "))

    # 고정된 경로 설정
    model_path = '../model/best_custom.pt'
    output_folder = '../test_images/testing'
    checked_image_path = '../result/checked_{}.jpg'

    cropped_images = split_image_into_grid(image_path, output_folder, grid_size)
    model = YOLO(model_path)
    fire_hydrant_index = list(model.names.keys())[list(model.names.values()).index('fire hydrant')]
    true_images = predict_images(model, cropped_images, fire_hydrant_index)
    true_image_numbers = [os.path.splitext(os.path.basename(path))[0].split('_')[1] for path in true_images]

    combine_images(image_path, true_images, grid_size, checked_image_path.format(basename(image_path)))
    print(f"체크된 이미지를 저장했습니다: {checked_image_path.format(basename(image_path))}")

    for image_path in cropped_images:
        os.remove(image_path)

    input("프로그램을 종료하려면 Enter 키를 누르세요...")

if __name__ == "__main__":
    main()

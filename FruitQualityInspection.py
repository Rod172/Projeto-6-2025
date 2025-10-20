import cv2
import numpy as np
import os

def segment_fruit(img, fruit_type):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Intervalos HSV para cores típicas de cada fruta
    hsv_ranges = {
        'banana': ([20, 100, 100], [30, 255, 255]),
        'maca': ([0, 50, 50], [10, 255, 255]),        # Maçã vermelha
        'laranja': ([10, 150, 150], [25, 255, 255]),
        'tomate': ([0, 80, 80], [10, 255, 255]),
        'morango': ([0, 120, 70], [6, 255, 255])
    }
    lower, upper = hsv_ranges[fruit_type]
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    fruit_segment = cv2.bitwise_and(img, img, mask=mask)
    return fruit_segment, mask

def analyze_quality(segmented, mask, fruit_type):
    # Grayscale
    gray = cv2.cvtColor(segmented, cv2.COLOR_BGR2GRAY)
    # Defeitos: regiões escuras dentro da fruta segmentada (threshold inverso)
    defect_mask = cv2.inRange(gray, 0, 50)
    # Conta pixels suspeitos
    defect_pixels = cv2.countNonZero(defect_mask & mask)
    total_pixels = cv2.countNonZero(mask)
    percent_defective = defect_pixels / max(total_pixels, 1) * 100

    criterios = {
        'banana': lambda p: p < 5,
        'maca': lambda p: p < 5,
        'laranja': lambda p: p < 8,
        'tomate': lambda p: p < 8,
        'morango': lambda p: p < 10
    }
    if criterios[fruit_type](percent_defective):
        msg = f"{fruit_type.capitalize()} está boa ({percent_defective:.2f}% defeitos)"
    else:
        msg = f"{fruit_type.capitalize()} está ruim ({percent_defective:.2f}% defeitos)"
    return msg

def main():
    frutas = ['banana', 'maca', 'laranja', 'tomate', 'morango']
    for fruta in frutas:
        folder = fruta  # pasta com o nome da fruta
        for img_name in os.listdir(folder):
            if img_name.endswith('.jpg'):
                img_path = os.path.join(folder, img_name)
                img = cv2.imread(img_path)
                if img is None:
                    print(f'Imagem não encontrada: {img_path}')
                    continue
                fruit_segment, mask = segment_fruit(img, fruta)
                resultado = analyze_quality(fruit_segment, mask, fruta)
                print(f"{fruta.capitalize()} - {img_name}: {resultado}")
                cv2.imshow(f'{fruta} - {img_name}', fruit_segment)
                cv2.waitKey(200)  # tempo de exibição da imagem, pode ajustar
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()


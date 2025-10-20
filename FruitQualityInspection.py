import cv2
import numpy as np
import os
from colorama import Fore, Style, init

init(autoreset=True)

def segment_fruit(img, fruit_type):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if fruit_type == 'banana':
        # Captura amarelo (madura) e marrom (ligeiramente passada)
        mask_yellow = cv2.inRange(hsv, np.array([20, 60, 60]), np.array([40, 255, 255]))
        mask_brown = cv2.inRange(hsv, np.array([5, 30, 20]), np.array([25, 180, 120]))
        mask = cv2.bitwise_or(mask_yellow, mask_brown)

        # Adiciona tons esverdeados (para detectar bananas verdes)
        mask_green = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        mask = cv2.bitwise_or(mask, mask_green)
    else:
        hsv_ranges = {
            'maca': ([0, 50, 50], [10, 255, 255]),
            'laranja': ([10, 150, 150], [25, 255, 255]),
            'tomate': ([0, 80, 80], [10, 255, 255]),
            'morango': ([0, 120, 70], [6, 255, 255])
        }
        lower, upper = hsv_ranges[fruit_type]
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

    # Remove sombras (baixa saturação + brilho)
    shadow_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 60, 120]))
    mask = cv2.bitwise_and(mask, cv2.bitwise_not(shadow_mask))

    # Limpeza de ruído
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    fruit_segment = cv2.bitwise_and(img, img, mask=mask)
    return fruit_segment, mask


def analyze_quality(segmented, mask, fruit_type):
    gray = cv2.cvtColor(segmented, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(segmented, cv2.COLOR_BGR2HSV)

    # Faixa de tons escuros/marrom (podres, mas sem contar sombra)
    lower_bad = np.array([5, 30, 20])
    upper_bad = np.array([25, 160, 120])

    defect_bad = cv2.inRange(hsv, lower_bad, upper_bad)

    # Pixels muito escuros (pretos/cinza escuro)
    defect_dark = cv2.inRange(gray, 0, 70)  # limite mais baixo para ignorar sombra leve

    # Combina e limpa
    defect_mask = cv2.bitwise_or(defect_bad, defect_dark)
    kernel = np.ones((5, 5), np.uint8)
    defect_mask = cv2.morphologyEx(defect_mask, cv2.MORPH_OPEN, kernel)

    # Conta pixels
    defect_pixels = cv2.countNonZero(defect_mask & mask)
    total_pixels = cv2.countNonZero(mask)
    percent_defective = defect_pixels / max(total_pixels, 1) * 100

    # --- Verificação de verde (banana não madura)
    not_ripe_msg = ""
    if fruit_type == 'banana':
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_pixels = cv2.countNonZero(green_mask & mask)
        percent_green = green_pixels / max(total_pixels, 1) * 100
        if percent_green > 7:
            not_ripe_msg = Fore.YELLOW + " (not ripe: green banana)"

    # Critérios ajustados
    criterio_banana = 20  # antes 12, mais tolerante para evitar falsos "bad"
    criterio_default = 8
    criterio = criterio_banana if fruit_type == 'banana' else criterio_default

    # Classificação
    if percent_defective < criterio and not not_ripe_msg:
        msg = (Fore.GREEN + f"{fruit_type.capitalize()} is good ({percent_defective:.2f}% defects)")
    elif not_ripe_msg:
        msg = (Fore.YELLOW + f"{fruit_type.capitalize()} is not ripe ({percent_green:.2f}% green)" + not_ripe_msg)
    else:
        msg = (Fore.RED + f"{fruit_type.capitalize()} is bad ({percent_defective:.2f}% defects)")
    return msg


def main():
    frutas = ['banana', 'maca', 'laranja', 'tomate', 'morango']
    for fruta in frutas:
        folder = fruta  # pasta com o nome da fruta
        for img_name in os.listdir(folder):
            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(folder, img_name)
                img = cv2.imread(img_path)
                if img is None:
                    print(f'Image not found or cannot be read: {img_path}')
                    continue
                fruit_segment, mask = segment_fruit(img, fruta)
                resultado = analyze_quality(fruit_segment, mask, fruta)
                fruit_segment, mask = segment_fruit(img, fruta)
                resultado = analyze_quality(fruit_segment, mask, fruta)
                print(f"{fruta.capitalize()} - {img_name}: {resultado}")
                cv2.imshow(f'{fruta} - {img_name}', fruit_segment)
                cv2.waitKey(0)  # usa 0 pra esperar até você apertar uma tecla

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

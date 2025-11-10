import cv2
import numpy as np
import os
from colorama import Fore, Style, init
import pandas as pd  # ✅ Adicionado para gerar relatórios Excel
from Frutas_data import obter_hsv

init(autoreset=True)


def segment_fruit(img, fruit_type):
    """
    Segmenta a fruta na imagem.
    - Mantém a configuração específica para banana.
    - Para outros tipos tenta usar hsv_ranges; se não existir, usa fallback Otsu.
    Retorna (fruit_segment_bgr, mask_binary).
    """
    try:
        ft = (str(fruit_type) or "").strip().lower()
    except Exception:
        ft = ""

    # tratamento específico para banana (mantido)
    if ft == 'banana':
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Captura amarelo (madura) e marrom (ligeiramente passada)
        mask_yellow = cv2.inRange(hsv, np.array([20, 60, 60]), np.array([40, 255, 255]))
        mask_brown = cv2.inRange(hsv, np.array([5, 30, 20]), np.array([25, 180, 120]))
        mask = cv2.bitwise_or(mask_yellow, mask_brown)
        # Adiciona tons esverdeados (bananas verdes)
        mask_green = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        mask = cv2.bitwise_or(mask, mask_green)
    else:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_ranges = {
            'maçã': ([0, 50, 50], [10, 255, 255]),
            'laranja': ([10, 150, 150], [25, 255, 255]),
            'tomate': ([0, 80, 80], [10, 255, 255]),
            'morango': ([0, 120, 70], [6, 255, 255]),
            # adicione aqui outras frutas conforme necessário, ex: 'melancia': ([..],[..])
        }
        if ft in hsv_ranges:
            lower, upper = hsv_ranges[ft]
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        else:
            # fallback genérico: Otsu + limpeza morfológica
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # tenta decidir se precisa inverter (fundo claro)
            try:
                if np.mean(gray[mask == 255]) > np.mean(gray[mask == 0]):
                    mask = cv2.bitwise_not(mask)
            except Exception:
                pass
            # pequena nota de aviso (console)
            print(f"[WARN] segment_fruit: sem hsv_ranges para '{ft}', usando fallback Otsu")

    # Remove sombras (baixa saturação + brilho)
    try:
        shadow_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 60, 120]))
        mask = cv2.bitwise_and(mask, cv2.bitwise_not(shadow_mask))
    except Exception:
        pass

    # Limpeza de ruído
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    fruit_segment = cv2.bitwise_and(img, img, mask=mask)
    return fruit_segment, mask


def analyze_quality(segmented, mask, fruit_type):
    # normaliza nome da fruta
    try:
        ft_raw = str(fruit_type or "").strip()
    except Exception:
        ft_raw = ""
    ft_key = ft_raw.title()  # mapeia para chaves em Frutas_data (ex: "Pera", "Maçã")
    ft_lower = ft_raw.lower()

    gray = cv2.cvtColor(segmented, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(segmented, cv2.COLOR_BGR2HSV)

    # tenta obter faixa 'podre' específica da fruta
    hsv_info = None
    try:
        hsv_info = obter_hsv(ft_key)
    except Exception:
        hsv_info = None

    if hsv_info and isinstance(hsv_info, dict) and 'podre' in hsv_info:
        lower_bad, upper_bad = hsv_info['podre']
        lower_bad = np.array(lower_bad)
        upper_bad = np.array(upper_bad)
    else:
        # fallback genérico
        lower_bad = np.array([5, 30, 20])
        upper_bad = np.array([25, 160, 120])

    defect_bad = cv2.inRange(hsv, lower_bad, upper_bad)
    # Pixels muito escuros (possível podridão/queimadura)
    defect_dark = cv2.inRange(gray, 0, 70)

    # Combina e limpa
    defect_mask = cv2.bitwise_or(defect_bad, defect_dark)
    kernel = np.ones((5, 5), np.uint8)
    defect_mask = cv2.morphologyEx(defect_mask, cv2.MORPH_OPEN, kernel)

    # Conta pixels SOBRE a máscara da fruta (mask) passada pela segmentação
    defect_pixels = cv2.countNonZero(cv2.bitwise_and(defect_mask, defect_mask, mask=mask))
    total_pixels = cv2.countNonZero(mask)
    percent_defective = (defect_pixels / max(total_pixels, 1)) * 100

    # verifica presença de verde (para bananas/limites específicos)
    percent_green = 0.0
    not_ripe_msg = ""
    if ft_lower == 'banana':
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_pixels = cv2.countNonZero(cv2.bitwise_and(green_mask, green_mask, mask=mask))
        percent_green = (green_pixels / max(total_pixels, 1)) * 100
        if percent_green > 7:
            not_ripe_msg = Fore.YELLOW + " (verde: pouca maturação)"

    # limites por fruta (usa load_reference_data se disponível)
    try:
        ref = load_reference_data()
    except Exception:
        ref = {}
    ref_info = ref.get(ft_lower, {})
    defect_limit = ref_info.get('defect_limit', 20 if ft_lower == 'banana' else 8)
    green_limit = ref_info.get('green_limit', 7)

    classification = "Boa"
    if percent_green > green_limit and ft_lower == 'banana':
        classification = "Verde"
        msg = (Fore.YELLOW + f"{ft_raw.title()} não está maduro ({percent_green:.2f}% verde){not_ripe_msg}")
    elif percent_defective >= defect_limit:
        classification = "Ruim"
        msg = (Fore.RED + f"{ft_raw.title()} está ruim ({percent_defective:.2f}% defeitos)")
    else:
        classification = "Boa"
        msg = (Fore.GREEN + f"{ft_raw.title()} está bom ({percent_defective:.2f}% defeitos)")

    return msg, percent_defective, classification


# ✅ NOVA FUNÇÃO: upload interativo de imagem do usuário
def upload_image():
    print(Fore.CYAN + "\n=== Upload de imagem ===")
    path = input("Digite o caminho completo da imagem: ").strip()
    if not os.path.exists(path):
        print(Fore.RED + "❌ Arquivo não encontrado.")
        return None, None

    fruit_type = input("Digite o tipo da fruta (banana, maçã, laranja, tomate, morango): ").lower()
    return path, fruit_type


# ✅ NOVA FUNÇÃO: definir dados técnicos de referência
def load_reference_data():
    return {
        'banana': {'defect_limit': 20, 'green_limit': 7},
        'maçã': {'defect_limit': 8},
        'laranja': {'defect_limit': 10},
        'tomate': {'defect_limit': 10},
        'morango': {'defect_limit': 12}
    }


# ✅ NOVA FUNÇÃO: gerar relatório em Excel
def save_report(results, filename="relatorio_analise.xlsx"):
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)
    print(Fore.CYAN + f"\n📊 Relatório salvo em: {filename}")


def main():
    frutas = ['banana', 'maçã', 'laranja', 'tomate', 'morango']
    ref_data = load_reference_data()  # ✅ Dados técnicos padrão
    resultados = []  # ✅ Armazena resultados para o relatório

    print(Fore.MAGENTA + "Deseja analisar imagens de pastas padrão ou enviar manualmente?")
    modo = input("(1) Pastas padrão  |  (2) Upload manual  → ").strip()

    if modo == "2":
        # --- Upload manual ---
        while True:
            img_path, fruta = upload_image()
            if not img_path:
                break

            img = cv2.imread(img_path)
            if img is None:
                print(f'Erro ao ler imagem: {img_path}')
                continue

            fruit_segment, mask = segment_fruit(img, fruta)
            resultado, defeitos, classificacao = analyze_quality(fruit_segment, mask, fruta)
            print(f"{fruta.capitalize()} - {img_path}: {resultado}")

            resultados.append({
                "Fruta": fruta,
                "Arquivo": os.path.basename(img_path),
                "Defeitos (%)": round(defeitos, 2),
                "Classificação": classificacao,  # ✅ Nova coluna
                "Resultado": resultado.replace(Fore.GREEN, "").replace(Fore.RED, "").replace(Fore.YELLOW, "")
            })

            cv2.imshow(f'{fruta} - {os.path.basename(img_path)}', fruit_segment)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            again = input("Analisar outra imagem? (s/n): ").lower()
            if again != 's':
                break
    else:
        # --- Modo original (pasta padrão) ---
        for fruta in frutas:
            folder = fruta
            for img_name in os.listdir(folder):
                if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(folder, img_name)
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f'Image not found or cannot be read: {img_path}')
                        continue
                    fruit_segment, mask = segment_fruit(img, fruta)
                    resultado, defeitos, classificacao = analyze_quality(fruit_segment, mask, fruta)
                    print(f"{fruta.capitalize()} - {img_name}: {resultado}")

                    resultados.append({
                        "Fruta": fruta,
                        "Arquivo": img_name,
                        "Defeitos (%)": round(defeitos, 2),
                        "Classificação": classificacao,  # ✅ Nova coluna
                        "Resultado": resultado.replace(Fore.GREEN, "").replace(Fore.RED, "").replace(Fore.YELLOW, "")
                    })

                    cv2.imshow(f'{fruta} - {img_name}', fruit_segment)
                    cv2.waitKey(0)

        cv2.destroyAllWindows()

    # ✅ Gera relatório Excel no final
    if resultados:
        save_report(resultados)


if __name__ == '__main__':
    main()

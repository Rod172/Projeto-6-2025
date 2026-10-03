# Lista de frutas comuns (50 a 100 itens)
fruits_list = [
    # Tropicais
    "Abacate", "Abacaxi", "Açaí", "Banana", "Caju", "Carambola", "Coco", "Cupuaçu", "Graviola", "Manga",
    "Mamão", "Maracujá", "Pitaia", "Pitanga", "Tamarindo", "Melancia", "Melão", "Jaca", "Kiwi", "Goiaba",

    # Cítricas
    "Laranja", "Limão", "Tangerina", "Mexerica", "Pomelo", "Toranja", "Lima-da-pérsia", "Kumquat",

    # Vermelhas e silvestres
    "Morango", "Framboesa", "Amora", "Mirtilo", "Cranberry", "Groselha", "Cereja", "Uva",

    # Frutas de clima temperado
    "Maçã", "Pera", "Pêssego", "Nectarina", "Ameixa", "Damasco", "Caqui", "Figo", "Romã",

    # Outras conhecidas mundialmente
    "Tomate", "Abóbora", "Pepino", "Azeitona", "Papaia", "Mangostão", "Lichia", "Rambutã", "Durian", "Noni",
    "Jabuticaba", "Jenipapo", "Uvaia", "Pequi", "Seriguela", "Acerola", "Grumixama", "Araçá", "Cambuci", "Bacuri"
]

# Dicionário opcional com informações básicas (exemplo)
fruits_info = {
    # 🟢 Tropicais
    "Abacate": {"Cor típica": "Verde", "Tipo": "Tropical", "Origem": "México e América Central"},
    "Abacaxi": {"Cor típica": "Amarela", "Tipo": "Tropical", "Origem": "América do Sul"},
    "Açaí": {"Cor típica": "Roxa", "Tipo": "Tropical", "Origem": "Amazônia"},
    "Banana": {"Cor típica": "Amarela", "Tipo": "Tropical", "Origem": "Sudeste Asiático"},
    "Caju": {"Cor típica": "Vermelha ou amarela", "Tipo": "Tropical", "Origem": "Brasil"},
    "Carambola": {"Cor típica": "Amarela", "Tipo": "Tropical", "Origem": "Sudeste Asiático"},
    "Coco": {"Cor típica": "Marrom", "Tipo": "Tropical", "Origem": "Ásia e Oceania"},
    "Cupuaçu": {"Cor típica": "Marrom", "Tipo": "Tropical", "Origem": "Amazônia"},
    "Graviola": {"Cor típica": "Verde", "Tipo": "Tropical", "Origem": "América Central"},
    "Manga": {"Cor típica": "Amarela ou vermelha", "Tipo": "Tropical", "Origem": "Índia"},
    "Mamão": {"Cor típica": "Alaranjada", "Tipo": "Tropical", "Origem": "América Central"},
    "Maracujá": {"Cor típica": "Amarela ou roxa", "Tipo": "Tropical", "Origem": "Brasil"},
    "Pitaia": {"Cor típica": "Rosa", "Tipo": "Tropical", "Origem": "América Central"},
    "Pitanga": {"Cor típica": "Vermelha", "Tipo": "Tropical", "Origem": "Brasil"},
    "Tamarindo": {"Cor típica": "Marrom", "Tipo": "Tropical", "Origem": "África"},
    "Melancia": {"Cor típica": "Verde por fora, vermelha por dentro", "Tipo": "Tropical", "Origem": "África"},
    "Melão": {"Cor típica": "Amarela ou esverdeada", "Tipo": "Tropical", "Origem": "Irã"},
    "Jaca": {"Cor típica": "Verde", "Tipo": "Tropical", "Origem": "Índia"},
    "Goiaba": {"Cor típica": "Verde por fora, rosa por dentro", "Tipo": "Tropical", "Origem": "América do Sul"},

    # 🍊 Cítricas
    "Laranja": {"Cor típica": "Laranja", "Tipo": "Cítrica", "Origem": "Sudeste Asiático"},
    "Limão": {"Cor típica": "Verde ou amarelo", "Tipo": "Cítrica", "Origem": "Índia"},
    "Tangerina": {"Cor típica": "Laranja", "Tipo": "Cítrica", "Origem": "China"},
    "Mexerica": {"Cor típica": "Laranja", "Tipo": "Cítrica", "Origem": "China"},
    "Pomelo": {"Cor típica": "Amarelada", "Tipo": "Cítrica", "Origem": "Sudeste Asiático"},
    "Toranja": {"Cor típica": "Rosa ou laranja", "Tipo": "Cítrica", "Origem": "Barbados"},
    "Lima-da-pérsia": {"Cor típica": "Amarela", "Tipo": "Cítrica", "Origem": "Oriente Médio"},
    "Kumquat": {"Cor típica": "Laranja", "Tipo": "Cítrica", "Origem": "China"},

    # 🍓 Vermelhas e silvestres
    "Morango": {"Cor típica": "Vermelha", "Tipo": "Silvestre", "Origem": "Europa"},
    "Framboesa": {"Cor típica": "Rosa", "Tipo": "Silvestre", "Origem": "Europa"},
    "Amora": {"Cor típica": "Roxa ou preta", "Tipo": "Silvestre", "Origem": "América do Norte"},
    "Mirtilo": {"Cor típica": "Azul", "Tipo": "Silvestre", "Origem": "América do Norte"},
    "Cranberry": {"Cor típica": "Vermelha", "Tipo": "Silvestre", "Origem": "América do Norte"},
    "Groselha": {"Cor típica": "Vermelha", "Tipo": "Silvestre", "Origem": "Europa"},
    "Cereja": {"Cor típica": "Vermelha", "Tipo": "Silvestre", "Origem": "Europa"},
    "Uva": {"Cor típica": "Verde, roxa ou preta", "Tipo": "Silvestre", "Origem": "Mediterrâneo"},

    # 🍎 Frutas de clima temperado
    "Maçã": {"Cor típica": "Vermelha ou verde", "Tipo": "Temperada", "Origem": "Ásia Central"},
    "Pera": {"Cor típica": "Verde ou amarela", "Tipo": "Temperada", "Origem": "Europa"},
    "Pêssego": {"Cor típica": "Alaranjada", "Tipo": "Temperada", "Origem": "China"},
    "Nectarina": {"Cor típica": "Vermelha", "Tipo": "Temperada", "Origem": "China"},
    "Ameixa": {"Cor típica": "Roxa", "Tipo": "Temperada", "Origem": "China"},
    "Damasco": {"Cor típica": "Alaranjada", "Tipo": "Temperada", "Origem": "China"},
    "Caqui": {"Cor típica": "Laranja", "Tipo": "Temperada", "Origem": "Japão"},
    "Figo": {"Cor típica": "Roxo", "Tipo": "Temperada", "Origem": "Oriente Médio"},
    "Romã": {"Cor típica": "Vermelha", "Tipo": "Temperada", "Origem": "Irã"},

    # 🍅 Outras conhecidas
    "Tomate": {"Cor típica": "Vermelha", "Tipo": "Solanácea", "Origem": "América do Sul"},
    "Abóbora": {"Cor típica": "Laranja", "Tipo": "Cucurbitácea", "Origem": "América Central"},
    "Pepino": {"Cor típica": "Verde", "Tipo": "Cucurbitácea", "Origem": "Índia"},
    "Azeitona": {"Cor típica": "Verde ou preta", "Tipo": "Oleaginosa", "Origem": "Mediterrâneo"},
    "Papaia": {"Cor típica": "Alaranjada", "Tipo": "Tropical", "Origem": "América Central"},
    "Mangostão": {"Cor típica": "Roxa", "Tipo": "Tropical", "Origem": "Sudeste Asiático"},
    "Lichia": {"Cor típica": "Rosa", "Tipo": "Tropical", "Origem": "China"},
    "Rambutã": {"Cor típica": "Vermelha", "Tipo": "Tropical", "Origem": "Sudeste Asiático"},
    "Durian": {"Cor típica": "Verde amarelado", "Tipo": "Tropical", "Origem": "Malásia"},
    "Noni": {"Cor típica": "Verde esbranquiçado", "Tipo": "Tropical", "Origem": "Polinésia"},

    # 🍇 Frutas brasileiras nativas
    "Jabuticaba": {"Cor típica": "Roxa", "Tipo": "Nativa", "Origem": "Brasil"},
    "Jenipapo": {"Cor típica": "Amarelada", "Tipo": "Nativa", "Origem": "Brasil"},
    "Uvaia": {"Cor típica": "Amarela", "Tipo": "Nativa", "Origem": "Brasil"},
    "Pequi": {"Cor típica": "Amarela", "Tipo": "Nativa", "Origem": "Cerrado Brasileiro"},
    "Seriguela": {"Cor típica": "Vermelha", "Tipo": "Nativa", "Origem": "Nordeste do Brasil"},
    "Acerola": {"Cor típica": "Vermelha", "Tipo": "Nativa", "Origem": "Caribe"},
    "Grumixama": {"Cor típica": "Roxa", "Tipo": "Nativa", "Origem": "Brasil"},
    "Araçá": {"Cor típica": "Amarela ou verde", "Tipo": "Nativa", "Origem": "Brasil"},
    "Cambuci": {"Cor típica": "Verde", "Tipo": "Nativa", "Origem": "Mata Atlântica"},
    "Bacuri": {"Cor típica": "Amarela", "Tipo": "Nativa", "Origem": "Amazônia"}
}


# -----------------------------
# 3️⃣ Parâmetros analíticos (HSV)
# -----------------------------
# Faixas HSV médias para análise de maturação:
# - Verde
# - Madura
# - Podre
# Valores aproximados, podem ser calibrados conforme amostras reais.

fruit_hsv_ranges = {
    # --- Tropicais ---
    "Abacate": {
        "verde": ([35, 50, 40], [85, 255, 255]),
        "madura": ([25, 60, 60], [45, 200, 200]),
        "podre": ([10, 30, 20], [25, 150, 120])
    },
    "Abacaxi": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([20, 150, 150], [35, 255, 255]),
        "podre": ([10, 40, 20], [25, 180, 120])
    },
    "Açaí": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([120, 50, 50], [160, 255, 255]),
        "podre": ([5, 30, 20], [25, 160, 120])
    },
    "Banana": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([20, 60, 60], [40, 255, 255]),
        "podre": ([5, 30, 20], [25, 160, 120])
    },
    "Caju": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([0, 120, 70], [15, 255, 255]),
        "podre": ([5, 30, 20], [25, 120, 100])
    },
    "Carambola": {
        "verde": ([40, 50, 50], [80, 255, 255]),
        "madura": ([25, 80, 80], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 180, 120])
    },
    "Coco": {
        "verde": ([35, 50, 40], [85, 255, 255]),
        "madura": ([20, 70, 60], [35, 255, 200]),
        "podre": ([5, 20, 20], [25, 160, 100])
    },
    "Cupuaçu": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([10, 100, 60], [25, 255, 255]),
        "podre": ([5, 30, 20], [25, 140, 100])
    },
    "Graviola": {
        "verde": ([35, 50, 40], [85, 255, 255]),
        "madura": ([25, 80, 80], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 180, 120])
    },
    "Manga": {
        "verde": ([40, 50, 50], [85, 255, 255]),
        "madura": ([20, 60, 60], [40, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 100])
    },
    "Mamão": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([20, 80, 80], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 180, 120])
    },
    "Maracujá": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([25, 80, 80], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 120])
    },
    "Pitaia": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([160, 70, 70], [180, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 100])
    },
    "Pitanga": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([0, 120, 70], [10, 255, 255]),
        "podre": ([5, 30, 20], [25, 160, 120])
    },
    "Tamarindo": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([15, 50, 50], [30, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 120])
    },
    "Melancia": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([0, 120, 70], [10, 255, 255]),
        "podre": ([5, 30, 20], [25, 160, 120])
    },
    "Melão": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([25, 100, 100], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 120])
    },
    "Jaca": {
        "verde": ([35, 50, 40], [85, 255, 255]),
        "madura": ([25, 80, 80], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 150, 120])
    },
    "Kiwi": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([40, 40, 40], [75, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 100])
    },
    "Goiaba": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([0, 120, 70], [15, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 100])
    },
    "Laranja": {
        "verde": ([35, 50, 40], [80, 255, 255]),
        "madura": ([10, 150, 150], [25, 255, 255]),
        "podre": ([5, 30, 20], [20, 160, 120])
    },
    "Limão": {
        "verde": ([40, 50, 50], [85, 255, 255]),
        "madura": ([25, 100, 100], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 120])
    },
    "Tangerina": {
        "verde": ([35, 50, 40], [85, 255, 255]),
        "madura": ([10, 150, 150], [25, 255, 255]),
        "podre": ([5, 30, 20], [20, 160, 120])
    },
    "Morango": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([0, 120, 70], [6, 255, 255]),
        "podre": ([0, 0, 0], [25, 120, 80])
    },
    "Amora": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([120, 50, 50], [160, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 120])
    },
    "Framboesa": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([170, 70, 70], [180, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 120])
    },
    "Uva": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([120, 50, 50], [160, 255, 255]),
        "podre": ([5, 30, 20], [25, 160, 100])
    },
    "Maçã": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([0, 70, 70], [10, 255, 255]),
        "podre": ([5, 30, 20], [25, 120, 100])
    },
    "Pera": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([25, 80, 80], [35, 255, 255]),
        "podre": ([10, 30, 20], [25, 150, 120])
    },
    "Pêssego": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([10, 100, 100], [25, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 120])
    },
    "Ameixa": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([130, 60, 60], [160, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 120])
    },
    "Caqui": {
        "verde": ([35, 50, 50], [85, 255, 255]),
        "madura": ([10, 100, 100], [25, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 100])
    },
    "Figo": {
        "verde": ([35, 50, 40], [85, 255, 255]),
        "madura": ([120, 50, 50], [160, 255, 255]),
        "podre": ([10, 30, 20], [25, 160, 100])
    },
    "Tomate": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([0, 80, 80], [10, 255, 255]),
        "podre": ([5, 30, 20], [25, 160, 120])
    },
    "Romã": {
        "verde": ([35, 40, 40], [85, 255, 255]),
        "madura": ([0, 100, 70], [10, 255, 255]),
        "podre": ([5, 30, 20], [25, 150, 120])
    },
}


# -----------------------------
# 4️⃣ Funções utilitárias
# -----------------------------

def listar_frutas():
    return fruits_list

def obter_info(fruta):
    return fruits_info.get(fruta.capitalize(), "Informações não disponíveis.")

def obter_hsv(fruta):
    return fruit_hsv_ranges.get(fruta.capitalize(), None)

if __name__ == "__main__":
    print(f"🍎 Total de frutas cadastradas: {len(fruits_list)}\n")
    for fruta in fruits_list[:10]:
        print(" -", fruta)
    print("\nExemplo HSV (Banana):", obter_hsv("Banana"))
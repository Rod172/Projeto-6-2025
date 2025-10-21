
import cv2
import numpy as np
import os
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from tkinter import Tk, Button, Label, filedialog
from PIL import Image, ImageTk

# ===========================================
# 1. CARREGAR DATASET E TREINAR MODELO
# ===========================================

dataset_path = "dataset"
classes = ["verde", "madura", "podre"]

X, y = [], []

def extrair_caracteristicas(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    return [
        np.mean(h), np.std(h),
        np.mean(s), np.std(s),
        np.mean(v), np.std(v)
    ]

# Carregar imagens do dataset
for label, classe in enumerate(classes):
    folder = os.path.join(dataset_path, classe)
    for arquivo in os.listdir(folder):
        path = os.path.join(folder, arquivo)
        img = cv2.imread(path)
        if img is None:
            continue
        img = cv2.resize(img, (200, 200))
        X.append(extrair_caracteristicas(img))
        y.append(label)

X = np.array(X)
y = np.array(y)

# Divisão treino/teste e treinamento SVM
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = SVC(kernel='rbf', gamma='scale')
model.fit(X_train, y_train)

# ===========================================
# 2. FUNÇÃO PARA SELECIONAR IMAGEM E CLASSIFICAR
# ===========================================

def abrir_imagem():
    global img_label
    path = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png")])
    if path:
        img_cv = cv2.imread(path)
        img_cv_resized = cv2.resize(img_cv, (200, 200))
        
        # Extrair características e classificar
        features = np.array(extrair_caracteristicas(img_cv_resized)).reshape(1, -1)
        pred = model.predict(features)[0]
        classe_pred = classes[pred].upper()
        
        # Converter para PIL para exibir no Tkinter
        img_rgb = cv2.cvtColor(img_cv_resized, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        # Atualizar label
        img_label.config(image=img_tk)
        img_label.image = img_tk
        resultado_label.config(text=f"Classificação: {classe_pred}")

# ===========================================
# 3. INTERFACE GRÁFICA COM TKINTER
# ===========================================

root = Tk()
root.title("Inspeção de Qualidade de Frutas")
root.geometry("300x350")

btn = Button(root, text="Abrir Imagem", command=abrir_imagem)
btn.pack(pady=10)

img_label = Label(root)
img_label.pack(pady=10)

resultado_label = Label(root, text="", font=("Arial", 14, "bold"))
resultado_label.pack(pady=10)

root.mainloop()

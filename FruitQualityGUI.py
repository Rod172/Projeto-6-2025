from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QToolButton, QSizePolicy,
    QDialog, QCheckBox, QDialogButtonBox, QTableWidget, QTableWidgetItem, QStyle, QSpinBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage
from FruitQualityInspection import segment_fruit, analyze_quality, save_report
from Frutas_data import fruits_list

import cv2
import sys
import os
import numpy as np
import re
import shutil

def imread_unicode(path):
    """
    Lê imagem mesmo se o caminho tiver caracteres Unicode (ex: 'Área de Trabalho').
    Usa np.fromfile + cv2.imdecode para contornar limitações do cv2.imread em Windows.
    """
    try:
        data = np.fromfile(path, dtype=np.uint8)
        if data.size == 0:
            return None
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None

def strip_ansi(s):
    if not isinstance(s, str):
        return s
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', s)

class FruitQualityGUI(QWidget):
    def __init__(self, image_folder="."):
        super().__init__()
        self.setWindowTitle("Fruit Quality Inspection")
        self.image_folder = image_folder
        # garante que subpastas para todas as frutas existam antes de coletar imagens
        self.ensure_fruit_folders()
        # Coleta imagens recursivamente (caminhos completos)
        self.image_files_all = self.collect_images(self.image_folder)  # todas as imagens
        self.image_files = []  # lista filtrada (pelo tipo selecionado)
        self.current_index = 0
        self.results = []  # Armazena resultados para relatório
        self.init_ui()
        # aplica filtro inicial (garante sincronização)
        self.filter_images_by_fruit(self.fruit_combo.currentText())
    
    def ensure_fruit_folders(self):
        """Cria subpastas para todas as frutas listadas em Frutas_data.fruits_list
           e garante que cada pasta contenha um arquivo .gitkeep (para controle de versão)."""
        try:
            for f in fruits_list:
                folder_name = str(f).strip().lower()
                dest = os.path.join(self.image_folder, folder_name)
                os.makedirs(dest, exist_ok=True)
                # cria .gitkeep dentro da pasta (se ainda não existir)
                try:
                    gitkeep = os.path.join(dest, ".gitkeep")
                    if not os.path.exists(gitkeep):
                        with open(gitkeep, "w", encoding="utf-8") as fh:
                            fh.write("")  # arquivo vazio apenas para manter a pasta no git
                except Exception:
                    pass
        except Exception as e:
            print(f"Falha ao garantir pastas de frutas: {e}")

    def _is_image_file(self, filename):
        """Retorna True se filename tiver extensão típica de imagem e não começar com '.'."""
        if not filename or filename.startswith('.'):
            return False
        ext = os.path.splitext(filename)[1].lower()
        return ext in {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}

    def collect_images(self, folder):
        # coleta recursiva de imagens ignorando arquivos ocultos (ex: .gitkeep) e não-imagens
        files = []
        for root, dirs, filenames in os.walk(folder):
            # opcional: ignorar pastas ocultas
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for fn in filenames:
                if not self._is_image_file(fn):
                    continue
                full = os.path.join(root, fn)
                files.append(full)
        return sorted(files)

    def init_ui(self):
        # layout principal responsivo: usa QSplitter para permitir redimensionamento pelo usuário
        from PyQt5.QtWidgets import QSplitter, QWidget, QHeaderView

        self.setMinimumSize(1000, 640)

        # --- coluna esquerda widget ---
        left_widget = QWidget()
        left_col = QVBoxLayout(left_widget)
        self.btn_add = QPushButton("Adicionar imagem")
        self.btn_add.setToolTip("Enviar imagem para a pasta da fruta selecionada")
        self.btn_add.clicked.connect(self.upload_image)
        left_col.addWidget(self.btn_add)

        # dropdown entre o botão "Adicionar" e a lista
        self.fruit_combo = QComboBox()
        # popula o dropdown com os itens de Frutas_data.fruits_list (remove vazios/entradas que começam com '.')
        items = []
        for f in fruits_list:
            try:
                s = str(f).strip()
            except Exception:
                continue
            if not s or s.startswith('.'):
                continue
            items.append(s)
        # ordena alfabeticamente (opcional)
        items = sorted(items, key=lambda x: x.lower())
        self.fruit_combo.addItems(items)
        self.fruit_combo.currentIndexChanged.connect(self.on_fruit_changed)
        left_col.addWidget(self.fruit_combo)

        self.image_list = QListWidget()
        self.image_list.setMinimumWidth(220)
        self.image_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.image_list.itemClicked.connect(self.on_list_item_clicked)
        left_col.addWidget(self.image_list, stretch=1)

        left_bottom = QHBoxLayout()
        self.btn_refresh = QPushButton("Atualizar")
        self.btn_refresh.clicked.connect(self.reload_images)
        left_bottom.addWidget(self.btn_refresh)
        self.btn_delete = QPushButton("Excluir")
        self.btn_delete.clicked.connect(self.delete_image)
        left_bottom.addWidget(self.btn_delete)
        left_col.addLayout(left_bottom)

        # --- coluna direita widget ---
        right_widget = QWidget()
        right_col = QVBoxLayout(right_widget)
        menu_layout = QHBoxLayout()
        self.btn_start = QPushButton("Iniciar (Analisar atual)")
        self.btn_next = QPushButton("Próxima Imagem")
        self.btn_process_all_fruits = QPushButton("Processar todas as frutas")
        self.btn_process_selected = QPushButton("Processar tipos selecionados")
        self.btn_download = QPushButton("Baixar Resultado (Amostra)")
        self.btn_download.setEnabled(False)
        # botão de alternar tema (dark/light)
        self.btn_toggle_theme = QPushButton("Dark Mode")
        self.btn_toggle_theme.setCheckable(True)
        self.btn_toggle_theme.setChecked(False)
        self.btn_toggle_theme.setToolTip("Alternar modo escuro/claro")

        # dar políticas expansíveis aos botões para melhor responsividade
        for b in (self.btn_start, self.btn_next, self.btn_process_all_fruits, self.btn_process_selected):
            b.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # aplicar cores destacadas por função
        btn_colors = {
            self.btn_add: "#27ae60",                # verde (Adicionar)
            self.btn_refresh: "#2980b9",            # azul (Atualizar)
            self.btn_delete: "#c0392b",             # vermelho (Excluir)
            self.btn_start: "#2ecc71",              # verde claro (Iniciar)
            self.btn_next: "#3498db",               # azul (Próxima)
            self.btn_process_all_fruits: "#e67e22", # laranja (Processar tudo)
            self.btn_process_selected: "#8e44ad",   # roxo (Processar selecionados)
            self.btn_download: "#16a085",           # teal (Download)
            self.btn_toggle_theme: "#34495e"        # cinza escuro (Toggle tema)
        }
        for btn, color in btn_colors.items():
            try:
                # stylesheet sem propriedade 'filter' (compatível com Qt)
                btn.setStyleSheet(
                    f"QPushButton{{background-color: {color}; color: white; border: none; padding:6px 10px; border-radius:6px;}}"
                    f"QPushButton:disabled{{background-color: #bdc3c7; color: #7f8c8d;}}"
                )
            except Exception:
                pass

        menu_layout.addWidget(self.btn_start)
        menu_layout.addWidget(self.btn_next)
        menu_layout.addWidget(self.btn_process_all_fruits)
        menu_layout.addWidget(self.btn_process_selected)
        menu_layout.addStretch()
        menu_layout.addWidget(self.btn_toggle_theme)
        menu_layout.addWidget(self.btn_download)
        right_col.addLayout(menu_layout)

        # imagem (expande) + preview (fixo mínimo) dentro de splitter interno
        content_splitter = QSplitter(Qt.Horizontal)
        # imagem
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.img_label.setStyleSheet("border: 1px solid gray; background: white;")
        img_container = QWidget()
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(0, 0, 0, 0)
        img_layout.addWidget(self.img_label)
        content_splitter.addWidget(img_container)

        # painel de pré-visualização com paginação
        preview_container = QWidget()
        pv_layout = QVBoxLayout(preview_container)
        pv_layout.setContentsMargins(6, 2, 6, 2)

        # controles de paginação (prev / next / page label / page size)
        pg_layout = QHBoxLayout()
        self.btn_prev_pg = QPushButton("◀")
        self.btn_next_pg = QPushButton("▶")
        self.lbl_page = QLabel("Página 0/0")
        self.spin_page_size = QSpinBox()
        self.spin_page_size.setRange(5, 200)
        self.spin_page_size.setValue(25)
        self.spin_page_size.setToolTip("Itens por página")
        pg_layout.addWidget(self.btn_prev_pg)
        pg_layout.addWidget(self.btn_next_pg)
        pg_layout.addWidget(self.lbl_page)
        pg_layout.addStretch()
        pg_layout.addWidget(QLabel("Itens por página:"))
        pg_layout.addWidget(self.spin_page_size)
        pv_layout.addLayout(pg_layout)

        # --- Conexões e estado inicial da paginação ---
        self.btn_prev_pg.clicked.connect(self.preview_prev_page)
        self.btn_next_pg.clicked.connect(self.preview_next_page)
        self.spin_page_size.valueChanged.connect(self.set_preview_page_size)
        # inicializa atributos de paginação antes do primeiro update
        self.preview_page = 0
        self.preview_page_size = self.spin_page_size.value()
        # (não chamar update ainda — a tabela será criada abaixo)
        
         # tabela
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["Fruta", "Arquivo", "Defeitos (%)", "Classificação"])
        self.preview_table.setMinimumWidth(320)
        self.preview_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setAlternatingRowColors(True)
        # estiliza cabeçalho e linhas
        self.preview_table.setStyleSheet(
            "QHeaderView::section{background:#34495e; color: white; padding:4px;}"
            "QTableWidget{gridline-color:#ecf0f1;}"
            "QTableWidget::item{padding:6px;}"
        )
        # redimensionamento de colunas
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        pv_layout.addWidget(self.preview_table)
        # agora que a tabela existe, atualiza a visualização inicial
        self.update_results_preview()
        content_splitter.addWidget(preview_container)
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 1)

        right_col.addWidget(content_splitter, stretch=1)

        # label para mostrar resultado (necessário para show_result)
        self.result_label = QLabel("Resultado:")
        self.result_label.setMinimumHeight(20)
        right_col.addWidget(self.result_label)

        # splitter principal (esquerda / direita) — o usuário pode redimensionar
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([260, 900])

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Slots
        self.btn_start.clicked.connect(self.start_analysis)
        self.btn_next.clicked.connect(self.next_image)
        self.btn_process_all_fruits.clicked.connect(self.process_all_fruits)
        self.btn_process_selected.clicked.connect(self.process_selected_fruits)
        self.btn_download.clicked.connect(self.download_result)

        # Mostra primeira imagem se existir
        # inicializa lista e visual
        self.filter_images_by_fruit(self.fruit_combo.currentText())
        if self.image_files:
            self.show_image()
        else:
            self.img_label.setText("Nenhuma imagem encontrada para o tipo selecionado.")

    def populate_image_list(self):
        """Preenche a QListWidget com os nomes das imagens e adiciona botão de lixeira em cada item."""
        self.image_list.clear()
        if not getattr(self, 'image_files', None):
            return
        for i, p in enumerate(self.image_files):
            name = os.path.basename(p)
            item = QListWidgetItem()
            # widget composto para o item: label + botão delete
            w = QWidget()
            h = QHBoxLayout()
            h.setContentsMargins(6, 4, 6, 4)
            h.setSpacing(6)
            lbl = QLabel(name)
            lbl.setToolTip(p)
            h.addWidget(lbl)
            h.addStretch()
            btn = QToolButton()
            btn.setToolTip("Excluir este arquivo")
            # usar ícone padrão do style para evitar problemas de renderização com emoji
            try:
                icon = self.style().standardIcon(QStyle.SP_TrashIcon)
                btn.setIcon(icon)
                btn.setIconSize(QSize(14, 14))
            except Exception:
                # fallback para emoji caso estilo não disponível
                btn.setText("🗑")
            # estilo do botão de lixeira (pequeno, destaque vermelho)
            btn.setFixedSize(26, 26)
            btn.setStyleSheet("QToolButton{background-color: #c0392b; color: white; border-radius:4px;} QToolButton:hover{background-color:#e74c3c;}")
            # captura o índice atual no lambda (idx=i)
            btn.clicked.connect(lambda _, idx=i: self.delete_image_by_index(idx))
            h.addWidget(btn)
            w.setLayout(h)
            # importante: ajusta sizeHint do item para evitar corte do widget
            item.setSizeHint(w.sizeHint())
            self.image_list.addItem(item)
            self.image_list.setItemWidget(item, w)
        # define seleção atual (garante índice válido)
        if 0 <= self.current_index < self.image_list.count():
            self.image_list.setCurrentRow(self.current_index)
        else:
            self.current_index = 0
            if self.image_list.count():
                self.image_list.setCurrentRow(0)

    def reload_images(self):
        """Recarrega lista de imagens do diretório e atualiza lista."""
        self.image_files_all = self.collect_images(self.image_folder)
        # tenta manter o mesmo arquivo selecionado (por nome)
        prev = None
        cur_item = self.image_list.currentItem()
        if cur_item is not None:
            # obtém texto do widget dentro do item
            w = self.image_list.itemWidget(cur_item)
            if w and w.layout() and w.layout().itemAt(0):
                prev = w.layout().itemAt(0).widget().text()
        # refiltra pela fruta atual e atualiza lista
        self.filter_images_by_fruit(self.fruit_combo.currentText())
        # procura item anterior por nome
        if prev:
            for i in range(self.image_list.count()):
                it = self.image_list.item(i)
                w = self.image_list.itemWidget(it)
                if w and w.layout() and w.layout().itemAt(0):
                    if w.layout().itemAt(0).widget().text() == prev:
                        self.current_index = i
                        self.image_list.setCurrentRow(i)
                        break
        self.show_image()

    def on_image_selected(self, idx):
        """Compatível: atualiza seleção por índice (não usado na nova lista)."""
        if idx < 0 or idx >= len(self.image_files):
            return
        self.current_index = idx
        self.show_image()

    def on_list_item_clicked(self, item):
        """Handler quando o usuário clica em um item da QListWidget."""
        idx = self.image_list.row(item)
        if idx < 0 or idx >= len(self.image_files):
            return
        self.current_index = idx
        self.show_image()

    def start_analysis(self):
        if not self.image_files:
            QMessageBox.warning(self, "Aviso", "Nenhuma imagem para analisar.")
            return

        img_path = self.image_files[self.current_index]
        img_name = os.path.basename(img_path)
        img = imread_unicode(img_path)
        if img is None:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir a imagem: {img_path}")
            return

        fruta = self.fruit_combo.currentText()
        fruit_segment, mask = segment_fruit(img, fruta)
        resultado_msg, defeitos, classificacao = analyze_quality(fruit_segment, mask, fruta)

        resultado_plain = strip_ansi(resultado_msg)
        item = {
            "Fruta": fruta,
            "Arquivo": img_name,
            "Defeitos (%)": round(defeitos, 2),
            "Classificação": classificacao,
            "Resultado": resultado_plain
        }
        existing = next((r for r in self.results if r["Arquivo"] == img_name), None)
        if existing:
            self.results.remove(existing)
        self.results.append(item)
        self.btn_download.setEnabled(True)

        self.show_result(classificacao, defeitos, resultado_plain)

        # mostra janela OpenCV redimensionada para caber na tela (protege contra imagens maiores que o monitor)
        try:
            screen = QApplication.primaryScreen()
            if screen:
                geom = screen.availableGeometry()
                max_w, max_h = geom.width(), geom.height()
            else:
                max_w, max_h = 800, 600
            h, w = fruit_segment.shape[:2]
            scale = min(1.0, (max_w - 100) / w, (max_h - 100) / h)
            disp = fruit_segment
            if scale < 1.0:
                new_w, new_h = int(w * scale), int(h * scale)
                disp = cv2.resize(fruit_segment, (new_w, new_h), interpolation=cv2.INTER_AREA)
            cv2.namedWindow(f'{fruta} - {img_name}', cv2.WINDOW_NORMAL)
            cv2.imshow(f'{fruta} - {img_name}', disp)
            cv2.waitKey(1)
        except Exception:
            # se falhar, apenas ignore para não travar a UI
            pass

    def next_image(self):
        if not self.image_files:
            return
        self.current_index = (self.current_index + 1) % len(self.image_files)
        # atualiza lista sem disparar o evento
        if hasattr(self, 'image_list'):
            self.image_list.blockSignals(True)
            self.image_list.setCurrentRow(self.current_index)
            self.image_list.blockSignals(False)
        self.show_image()

    def process_all(self):
        if not self.image_files:
            QMessageBox.warning(self, "Aviso", "Nenhuma imagem para processar.")
            return

        self.results = []
        for idx in range(len(self.image_files)):
            self.current_index = idx
            img_path = self.image_files[self.current_index]
            img_name = os.path.basename(img_path)
            img = imread_unicode(img_path)
            if img is None:
                continue
            # tenta inferir tipo pela pasta pai
            parent = os.path.basename(os.path.dirname(img_path)).lower()
            fruta = parent if parent in ['banana', 'maca', 'laranja', 'tomate', 'morango'] else self.fruit_combo.currentText()
            if fruta in [self.fruit_combo.itemText(i) for i in range(self.fruit_combo.count())]:
                self.fruit_combo.setCurrentText(fruta)

            fruit_segment, mask = segment_fruit(img, fruta)
            resultado_msg, defeitos, classificacao = analyze_quality(fruit_segment, mask, fruta)

            item = {
                "Fruta": fruta,
                "Arquivo": img_name,
                "Defeitos (%)": round(defeitos, 2),
                "Classificação": classificacao,
                "Resultado": strip_ansi(resultado_msg)
            }
            self.results.append(item)
            # atualiza lista visual enquanto processa
            if hasattr(self, 'image_list'):
                self.image_list.blockSignals(True)
                self.image_list.setCurrentRow(self.current_index)
                self.image_list.blockSignals(False)
            self.show_image()
            QApplication.processEvents()

        self.btn_download.setEnabled(bool(self.results))
        QMessageBox.information(self, "Processamento", f"Processadas {len(self.results)} imagens. Você pode baixar o relatório.")

    def download_result(self):
        if not self.results:
            QMessageBox.information(self, "Nenhum resultado", "Ainda não há resultados para salvar.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar relatório", "relatorio_analise.xlsx",
                                                   "Excel Files (*.xlsx);;CSV Files (*.csv)", options=options)
        if not file_path:
            return

        _, ext = os.path.splitext(file_path)
        try:
            if ext.lower() == '.csv':
                import pandas as pd
                df = pd.DataFrame(self.results)
                df.to_csv(file_path, index=False)
            else:
                save_report(self.results, filename=file_path)
            QMessageBox.information(self, "Salvo", f"Relatório salvo em: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar relatório: {e}")

    def show_image(self):
        if not self.image_files:
            self.img_label.clear()
            return
        img_path = self.image_files[self.current_index]
        img_name = os.path.basename(img_path)
        image = imread_unicode(img_path)
        if image is not None:
            parent = os.path.basename(os.path.dirname(img_path)).lower()
            if parent in ['banana', 'maca', 'laranja', 'tomate', 'morango']:
                self.fruit_combo.blockSignals(True)
                self.fruit_combo.setCurrentText(parent)
                self.fruit_combo.blockSignals(False)

            # mantém lista sincronizada
            if hasattr(self, 'image_list'):
                self.image_list.blockSignals(True)
                self.image_list.setCurrentRow(self.current_index)
                self.image_list.blockSignals(False)

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            # guarda pixmap original e atualiza escala
            self.current_pixmap = pixmap
            self._update_pixmap_scaled()
            self.img_label.setToolTip(img_path)
        else:
            self.img_label.setText('Erro ao ler imagem')

    def resizeEvent(self, event):
        # atualiza escala quando a janela for redimensionada
        try:
            self._update_pixmap_scaled()
        except Exception:
            pass
        return super().resizeEvent(event)

    def _update_pixmap_scaled(self):
        if not getattr(self, 'current_pixmap', None):
            return
        lbl = self.img_label
        pm = self.current_pixmap
        if pm.isNull():
            return
        scaled = pm.scaled(max(10, lbl.width()-10), max(10, lbl.height()-10),
                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl.setPixmap(scaled)

    def show_result(self, classification, defects_percent, text):
        self.result_label.setText(f'Resultado: {classification}  |  Defeitos: {defects_percent:.2f}%')
        self.result_label.setToolTip(str(text))
        # atualiza painel de pré-visualização (exibe os últimos resultados)
        self.update_results_preview()

    def update_results_preview(self, page=None, page_size=None):
        """Popula preview_table com resultados paginados (mais recentes primeiro)."""
        if page is None:
            page = getattr(self, 'preview_page', 0)
        if page_size is None:
            page_size = getattr(self, 'preview_page_size', 25)
        total = len(self.results)
        # resultados mais recentes primeiro
        rows_all = list(reversed(self.results))
        # calcula paginação
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))
        start = page * page_size
        end = start + page_size
        page_rows = rows_all[start:end]
        self.preview_table.setRowCount(len(page_rows))
        for r, item in enumerate(page_rows):
            fruta = item.get("Fruta", "")
            arquivo = item.get("Arquivo", "")
            defeitos = str(item.get("Defeitos (%)", ""))
            cls = item.get("Classificação", "")
            self.preview_table.setItem(r, 0, QTableWidgetItem(fruta))
            self.preview_table.setItem(r, 1, QTableWidgetItem(arquivo))
            self.preview_table.setItem(r, 2, QTableWidgetItem(defeitos))
            self.preview_table.setItem(r, 3, QTableWidgetItem(cls))
        # atualiza label de página
        self.preview_page = page
        self.preview_page_size = page_size
        self._update_preview_page_label(total, total_pages)
        # ajusta colunas para caber
        self.preview_table.resizeColumnsToContents()

    def _update_preview_page_label(self, total_items, total_pages):
        if total_items == 0:
            self.lbl_page.setText("Página 0/0")
        else:
            self.lbl_page.setText(f"Página {self.preview_page+1}/{total_pages}  —  {total_items} itens")

    def preview_prev_page(self):
        if self.preview_page > 0:
            self.preview_page -= 1
            self.update_results_preview()

    def preview_next_page(self):
        total = len(self.results)
        page_size = self.preview_page_size
        total_pages = max(1, (total + page_size - 1) // page_size)
        if self.preview_page < total_pages - 1:
            self.preview_page += 1
            self.update_results_preview()

    def set_preview_page_size(self, v):
        self.preview_page_size = v
        self.preview_page = 0
        self.update_results_preview()

    # ---------------- Dark mode ----------------
    def toggle_dark_mode(self):
        """Alterna modo escuro/claro quando o botão é pressionado."""
        enabled = bool(self.btn_toggle_theme.isChecked())
        self.apply_dark_mode(enabled)

    def apply_dark_mode(self, enabled: bool):
        """Aplica stylesheet de dark mode (se enabled True) ou limpa (modo claro)."""
        self.dark_mode = bool(enabled)
        if enabled:
            dark_styles = """
            QWidget { background: #2b2b2b; color: #e6e6e6; }
            QListWidget { background: #232323; color: #e6e6e6; }
            QTableWidget { background: #232323; color: #e6e6e6; gridline-color:#444444; }
            QHeaderView::section { background: #3b3b3b; color: #ffffff; padding:4px; }
            QLabel { color: #e6e6e6; }
            QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit { background: #333333; color: #e6e6e6; border: 1px solid #444444; }
            QToolTip { background: #353535; color: #ffffff; border: 1px solid #4a4a4a; }
            QToolButton { background: transparent; color: #e6e6e6; }
            """
            # aplica apenas à janela (não sobrepõe estilos inline dos botões coloridos)
            self.setStyleSheet(dark_styles)
            self.btn_toggle_theme.setText("Light Mode")
            # ajusta estilos do botão toggle para indicar estado
            self.btn_toggle_theme.setStyleSheet("QPushButton{background:#555555;color:white;border:none;padding:6px;border-radius:6px;} QPushButton:checked{background:#1abc9c;}")
        else:
            # limpa stylesheet para voltar ao estilo claro (os botões mantêm seus estilos inline)
            self.setStyleSheet("")
            self.btn_toggle_theme.setText("Dark Mode")
            # reaplica cor padrão do toggle (mesmo que btn_colors já o fez; garante consistência)
            try:
                self.btn_toggle_theme.setStyleSheet("QPushButton{background-color:#34495e;color:white;border:none;padding:6px;border-radius:6px;}")
            except Exception:
                pass

        # pequenas correções visuais na tabela após trocar o tema
        try:
            self.preview_table.viewport().update()
        except Exception:
            pass
        # atualiza label/result preview para garantir contraste
        if hasattr(self, 'result_label'):
            # destaca resultado com fundo sutil no dark mode
            if self.dark_mode:
                self.result_label.setStyleSheet("background:#2f2f2f; padding:4px; border-radius:4px;")
            else:
                self.result_label.setStyleSheet("")

    # conectar o botão após criação do UI (garanta que o slot exista)
    # a conexão é feita logo após init_ui ser executado — fazemos checagem aqui para segurança
    def showEvent(self, event):
        # conectar slots de tema / paginação apenas uma vez
        try:
            if hasattr(self, 'btn_toggle_theme') and not getattr(self, '_theme_connected', False):
                self.btn_toggle_theme.clicked.connect(self.toggle_dark_mode)
                self._theme_connected = True
        except Exception:
            pass
        super().showEvent(event)

    def upload_image(self):
        """Seleciona arquivo e copia para a pasta do projeto (subpasta do tipo de fruta)."""
        options = QFileDialog.Options()
        src_path, _ = QFileDialog.getOpenFileName(self, "Selecionar imagem para enviar", "",
                                                  "Imagens (*.png *.jpg *.jpeg);;Todos os arquivos (*)",
                                                  options=options)
        if not src_path:
            return

        # determina destino: pasta do projeto / subpasta do tipo selecionado
        fruta = self.fruit_combo.currentText()
        dest_dir = os.path.join(self.image_folder, fruta)
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível criar pasta de destino: {e}")
            return

        base = os.path.basename(src_path)
        name, ext = os.path.splitext(base)
        dest = os.path.join(dest_dir, base)
        # evita sobrescrever: gera sufixo se já existir
        i = 1
        while os.path.exists(dest):
            dest = os.path.join(dest_dir, f"{name}_{i}{ext}")
            i += 1
        try:
            shutil.copy2(src_path, dest)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao copiar a imagem: {e}")
            return

        # atualiza lista e seleciona a imagem recém enviada
        self.reload_images()
        # encontra índice pelo basename
        basename = os.path.basename(dest)
        for idx, p in enumerate(self.image_files):
            if os.path.basename(p) == basename and os.path.dirname(p).lower().endswith(fruta.lower()):
                self.current_index = idx
                break
        if hasattr(self, 'image_list'):
            self.image_list.blockSignals(True)
            self.image_list.setCurrentRow(self.current_index)
            self.image_list.blockSignals(False)
        self.show_image()
        QMessageBox.information(self, "Enviado", f"Imagem enviada para: {dest}")

    def delete_image(self):
        """Exclui o arquivo da imagem atualmente selecionada (com confirmação)."""
        if not self.image_files:
            QMessageBox.information(self, "Nenhum arquivo", "Não há imagem selecionada para excluir.")
            return

        img_path = self.image_files[self.current_index]
        img_name = os.path.basename(img_path)
        # string corrigida: não deixa literal aberto
        msg = f"Excluir o arquivo?\n{img_name}\n\nEsta ação removerá o arquivo do disco."
        resp = QMessageBox.question(self, "Confirmar exclusão", msg, QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return

        try:
            os.remove(img_path)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao excluir o arquivo:\n{e}")
            return

        # atualiza listas e UI
        self.image_files_all = self.collect_images(self.image_folder)
        self.filter_images_by_fruit(self.fruit_combo.currentText())
        # ajusta índice para próximo item válido
        if self.current_index >= len(self.image_files):
            self.current_index = max(0, len(self.image_files) - 1)
        if self.image_files:
            self.show_image()
        else:
            self.img_label.setText("Nenhuma imagem encontrada para o tipo selecionado.")
        QMessageBox.information(self, "Excluído", f"Arquivo excluído: {img_name}")

    def delete_image_by_index(self, idx):
        """Excluir item pelo índice (invocado pelo botão de cada item)."""
        if idx < 0 or idx >= len(self.image_files):
            return
        self.current_index = idx
        self.delete_image()

    def filter_images_by_fruit(self, fruta):
        """Atualiza self.image_files usando self.image_files_all filtrando pela pasta pai."""
        fruta = (fruta or "").lower()
        if not self.image_files_all:
            self.image_files = []
            self.populate_image_list()
            return
        filtered = []
        for p in self.image_files_all:
            parent = os.path.basename(os.path.dirname(p)).lower()
            if parent == fruta:
                filtered.append(p)
        # se não houver imagens na subpasta, mantém lista vazia (podemos também mostrar todas)
        self.image_files = filtered
        self.current_index = 0
        self.populate_image_list()

    def on_fruit_changed(self, idx):
        """Handler quando o usuário muda o tipo de fruta — refiltra as imagens."""
        fruta = self.fruit_combo.currentText()
        self.filter_images_by_fruit(fruta)
        # mostra primeira imagem do filtro (se existir)
        if self.image_files:
            self.current_index = 0
            # atualiza lista visual sem disparar evento
            if hasattr(self, 'image_list'):
                self.image_list.blockSignals(True)
                self.image_list.setCurrentRow(self.current_index)
                self.image_list.blockSignals(False)
            self.show_image()
        else:
            # limpa a visualização se não houver imagens para o tipo
            self.img_label.setText(f"Nenhuma imagem encontrada para '{fruta}'")

    def select_fruits_dialog(self):
        """Abre diálogo com checkboxes para escolher tipos de fruta; retorna lista escolhida."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Selecionar tipos de fruta")
        v = QVBoxLayout(dlg)
        checks = []
        # lista de opções baseada no combo (mantém ordem)
        for i in range(self.fruit_combo.count()):
            name = self.fruit_combo.itemText(i)
            cb = QCheckBox(name)
            # checa o atual por padrão
            if name == self.fruit_combo.currentText():
                cb.setChecked(True)
            v.addWidget(cb)
            checks.append(cb)
        v.addStretch()
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        v.addWidget(bb)
        if dlg.exec() != QDialog.Accepted:
            return []
        return [cb.text() for cb in checks if cb.isChecked()]

    def process_images_for_fruits(self, fruits):
        """Processa imagens para cada fruta em 'fruits' (lista de nomes)."""
        if not fruits:
            QMessageBox.information(self, "Nenhum tipo selecionado", "Nenhum tipo foi selecionado.")
            return
        original_results = list(self.results)
        total = 0
        for fruta in fruits:
            # filtra imagens desta fruta
            self.filter_images_by_fruit(fruta)
            for idx in range(len(self.image_files)):
                self.current_index = idx
                img_path = self.image_files[self.current_index]
                img_name = os.path.basename(img_path)
                img = imread_unicode(img_path)
                if img is None:
                    continue
                fruit_segment, mask = segment_fruit(img, fruta)
                resultado_msg, defeitos, classificacao = analyze_quality(fruit_segment, mask, fruta)
                item = {
                    "Fruta": fruta,
                    "Arquivo": img_name,
                    "Defeitos (%)": round(defeitos, 2),
                    "Classificação": classificacao,
                    "Resultado": strip_ansi(resultado_msg)
                }
                # substitui existente do mesmo arquivo
                existing = next((r for r in self.results if r["Arquivo"] == img_name), None)
                if existing:
                    self.results.remove(existing)
                self.results.append(item)
                total += 1
                # atualiza UI enquanto processa
                if hasattr(self, 'image_list'):
                    self.image_list.blockSignals(True)
                    self.image_list.setCurrentRow(self.current_index)
                    self.image_list.blockSignals(False)
                self.show_image()
                # atualizar preview incremental (mantém UI responsiva)
                self.update_results_preview()
                QApplication.processEvents()
        self.btn_download.setEnabled(bool(self.results))
        QMessageBox.information(self, "Processamento concluído", f"Processadas {total} imagens.")

    def process_all_fruits(self):
        """Processa imagens de todas as frutas (varre todas as subpastas encontradas)."""
        # extrai lista de frutas únicas a partir das pastas das imagens
        fruits = set()
        for p in self.image_files_all:
            parent = os.path.basename(os.path.dirname(p)).lower()
            if parent:
                fruits.add(parent)
        fruits = sorted(list(fruits))
        if not fruits:
            QMessageBox.information(self, "Nada a processar", "Não foram encontradas subpastas com imagens.")
            return
        self.process_images_for_fruits(fruits)

    def process_selected_fruits(self):
        """Abre diálogo para escolher tipos e processa os selecionados."""
        choices = self.select_fruits_dialog()
        if not choices:
            return
        self.process_images_for_fruits(choices)

if __name__ == "__main__":
    # usa a pasta do script como padrão (modifique se quiser outro caminho)
    folder = os.path.dirname(__file__)
    app = QApplication(sys.argv)
    window = FruitQualityGUI(folder)
    window.show()
    sys.exit(app.exec_())
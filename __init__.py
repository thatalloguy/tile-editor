import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import utils
import os

level = {}

level[(0, 0)] = ['grass']
level[(1, 0)] = ['water']
level[(2, 0)] = ['stone']
level[(0, 1)] = ['stone']
level[(2, 1)] = ['water']
level[(0, 2)] = ['grass']
level[(1, 2)] = ['grass']
level[(2, 2)] = ['grass']


class LevelRenderer(QWidget):
    TILE_SIZE = 32

    def __init__(self, level, tiles, tile_lut):
        super().__init__()
        self._currentLevel = level
        self._tiles = tiles
        self._tile_lut = tile_lut

    def paintEvent(self, event):
        painter = QPainter(self)


        width = self.width()
        height = self.height()

        for y in range(height // LevelRenderer.TILE_SIZE):
            for x in range(width // LevelRenderer.TILE_SIZE):
                content = level.get((x, y))
                if content is None:
                    continue
                for tile_name in content:
                    tile_index = self._tile_lut.get(tile_name)
                    if tile_index is None:
                        continue
                    tile_item = self._tiles.item(tile_index)
                    image = tile_item.data(Qt.UserRole + 2)
                    offsetX, offsetY = tile_item.data(Qt.UserRole + 3)
                    painter.drawImage(x * LevelRenderer.TILE_SIZE - offsetX, y * LevelRenderer.TILE_SIZE - offsetY, image)



class LevelEditor(LevelRenderer):
    def __init__(self, level, tiles, tile_lut, tile_selection_model):
        super(LevelEditor, self).__init__(level, tiles, tile_lut)
        self._tileSelectionModel = tile_selection_model
        self._tileToPaint = None
        self._isDrawing = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            current = self._tileSelectionModel.currentIndex()
            if not current.isValid():
                return
            print(current)
            self._isDrawing = True
            self._tileToPaint = self._tiles.itemFromIndex(current).text()
        else:
            #gum het weg
            self._tileToPaint = None
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        x = event.x() // self.TILE_SIZE
        y = event.y() // self.TILE_SIZE
        images = self._currentLevel.setdefault((x, y), [])
        if self._tileToPaint is None:
            if images:
                images.pop(-1)
                self.repaint()
            return

        if images and images[-1] == self._tileToPaint:
            return

        images.append(self._tileToPaint)
        self.repaint()
    def mouseReleaseEvent(self, event):
        self._isDrawing = False


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()

        #init de "tile" systeem niet aankommen!!!!! want het werkt
        self._current_file = None


        tiles = QStandardItemModel()
        tile_lut = {}

        for name, tile_path in utils.scan_tiles():
            tile_item = QStandardItem(name)
            tile_lut[name] = tiles.rowCount()
            tile_item.setIcon(QIcon(os.path.abspath(tile_path)))
            image = QImage(os.path.abspath(tile_path))

            tile_item.setData(tile_path)
            tile_item.setData(image, Qt.UserRole + 2)
            offsetX = (image.width() - LevelRenderer.TILE_SIZE) // 2
            offsetY = (image.height() - LevelRenderer.TILE_SIZE)

            tile_item.setData((offsetX, offsetY), Qt.UserRole + 3)
            tiles.appendRow(tile_item)

        #window dingen ook niet aankomen het werkt !!!!

        self.setWindowTitle('AlloStudio')

        main_widget = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_widget)

        title_list_view = QListView()
        title_list_view.setModel(tiles)
        main_widget.addWidget(title_list_view)

        renderer = LevelEditor(level, tiles, tile_lut, title_list_view.selectionModel())
        main_widget.addWidget(renderer)

        #MENUUUUUUUUUU
        bar = QMenuBar()
        self.setMenuBar(bar)
        file_menu = bar.addMenu('File')
        save_action = file_menu.addAction("Save")
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save)

        save_as_action = file_menu.addAction("Save As")
        save_as_action.setShortcut(("SHIFT+S"))
        save_as_action.triggered.connect(self._saveAs)

        open_action = file_menu.addAction("Open")
        open_action.triggered.connect(self._open)
        open_action.setShortcut(QKeySequence.Open)




    def _saveAs(self):
        result = QFileDialog.getSaveFileName(self, 'Save', '.', 'Level files (*.json)')
        if not result or not result[0]:
            return
        self._current_file = result[0]
        self._save()
    def _save(self):
        if self._current_file is None:
            self._saveAs()
        save_data = {}
        for key, value in level.items():
            save_data['%d_%d' % key] = value
        with open(self._current_file, 'w') as fh:
            json.dump(save_data, fh)

    def _open(self):
        result = QFileDialog.getOpenFileName(self, 'Open', '.', 'Level files (*.json)')
        if not result or not result[0]:
            return
        self._current_file = result[0]
        with open(self._current_file, 'r') as fh:
            load_data = json.load(fh)
        level.clear()
        for key, value in load_data.items():
            x, y = key.split('_')
            level[int(x), int(y)] = value
        self.repaint()




if __name__ == '__main__':
    app = QApplication([])

    window = MainApplication()
    window.show()

    app.exec_()
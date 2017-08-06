from collections import OrderedDict

from PyQt5 import QtWidgets, QtGui, Qt


class ColorPicker(QtWidgets.QWidget):

    def __init__(self, width, height):
        self.width = width
        self.height = height

        super().__init__()

        self.colors = OrderedDict([
            ('RED', (255, 0, 0)),
            ('GREEN', (0, 255, 0)),
            ('BLUE', (0, 0, 255)),
            ('YELLOW', (255, 255, 0)),
            ('GRAY', (100, 100, 100)),
            ('BLACK', (0, 0, 0)),
        ])

        self.btn_colors = {}

        self.active_color = None

        self.active_color_elem = None

        self.init_ui()

    def init_ui(self):

        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        layout = Qt.QHBoxLayout()

        for name, color in self.colors.items():
            btn = Color(color[0], color[1], color[2], name)
            btn.setFixedSize(self.height - 20, self.height - 20)

            layout.addWidget(btn)
            self.btn_colors[name] = btn
        self.setLayout(layout)

        for name, button in self.btn_colors.items():
            # keep this order
            button.clicked.connect(self.choose_color)
            button.clicked.connect(button.highlight)

    def choose_color(self):
        print("CHOOSE COLOR")
        for name, button in self.btn_colors.items():
            button.unhighlight()


class Color(QtWidgets.QPushButton):

    def __init__(self, r=0, g=0, b=0, name='TEST', x=None, y=None):
        super().__init__()
        self.highlighted = False
        self.color = QtGui.QColor(r, g, b)
        self.name = name
        self.x = x
        self.y = y

        self.css_highlighted = """
            background-color: rgb(%d, %d, %d);
            color: white;
            border: 5px solid green;
            border-radius: 20px;
        """ % (r, g, b)
        self.css_not_highlighted = """
            background-color: rgb(%d, %d, %d);
            color: white;
            border-radius: 20px;
        """ % (r, g, b)

        self.setStyleSheet(self.css_not_highlighted)

    def highlight(self):
        print("HIGHLIGHT")
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)

    def unhighlight(self):
        self.highlighted = False
        self.setStyleSheet(self.css_not_highlighted)

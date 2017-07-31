from PyQt5 import Qt, QtWidgets


class ShapePicker(QtWidgets.QWidget):
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

        super().__init__()

        self.shapes = {
            'CIRCLE': 0,
            'LINE': 1
        }

        self.btn_shapes = {}

        self.active_shape = 'LINE'

        self.init_ui()

    def init_ui(self):
        if self.width and self.height:
            self.setFixedWidth(self.width)
            self.setFixedHeight(self.height)
        layout = Qt.QVBoxLayout()

        for name, color in self.shapes.items():
            btn = Shape(name)
            if self.width and self.height:
                btn.setFixedSize(self.width - 20, self.height/2 - 10)

            layout.addWidget(btn)
            self.btn_shapes[name] = btn
        self.setLayout(layout)

        for name, button in self.btn_shapes.items():
            # keep this order
            button.clicked.connect(self.choose_shape)
            button.clicked.connect(button.highlight)

    def choose_shape(self):
        for name, btn in self.btn_shapes.items():
            btn.unhighlight()

        for name, btn in self.btn_shapes.items():
            if btn.highlighted:
                self.active_shape = btn.name


class Shape(QtWidgets.QPushButton):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.highlighted = False

        self.css_highlighted = """
            background-color: rgb(250, 250, 250);
            border: 5px solid green;
            border-radius: 2px;
        """

        self.css_not_highlighted = """
            background-color: rgb(150, 150, 150);
            border-radius: 2px;
        """

        self.setStyleSheet(self.css_not_highlighted)

    def highlight(self):
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)

    def unhighlight(self):
        self.highlighted = False
        self.setStyleSheet(self.css_not_highlighted)

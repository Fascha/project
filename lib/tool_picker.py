from PyQt5 import Qt, QtWidgets


class ToolPicker(QtWidgets.QWidget):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        super().__init__()

        self.tools = {
            'DRAW': 0,
            'SELECT': 1,
            'MOVE': 2,
        }

        self.btn_tools = {}

        self.active_tool = 'DRAW'

        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        layout = Qt.QVBoxLayout()

        for name, color in self.tools.items():
            btn = Tool(name)
            btn.setFixedHeight(self.height/len(self.tools) - 10)
            layout.addWidget(btn)
            self.btn_tools[name] = btn
        self.setLayout(layout)

        for name, button in self.btn_tools.items():
            # keep this order
            button.clicked.connect(self.choose_tool)
            button.clicked.connect(button.highlight)

    def choose_tool(self):
        for name, tool in self.btn_tools.items():
            tool.unhighlight()

        for name, tool in self.btn_tools.items():
            if tool.highlighted:
                self.active_tool = tool.name


class Tool(QtWidgets.QPushButton):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.highlighted = False

        self.css_highlighted = """
            background-color: rgb(250, 250, 250);
            border: 5px solid green;
            border-radius: 20px;
        """

        self.css_not_highlighted = """
            background-color: rgb(150, 150, 150,);
            border-radius: 20px;
        """

        self.setStyleSheet(self.css_not_highlighted)

    def highlight(self):
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)

    def unhighlight(self):
        self.highlighted = False
        self.setStyleSheet(self.css_not_highlighted)

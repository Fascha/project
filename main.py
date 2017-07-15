import lib.wiimote as wiimote
import time
import sys

from PyQt5 import Qt, QtGui, QtCore, QtWidgets


"""
TODO:

    - mapping from 4 IR sensors to display pixels



    - at least 3 interaction techniques
        - selection
        - copy(cut) & paste
        - load & save

    - change brush/pen/color with gesture


"""


class PaintArea(QtWidgets.QWidget):

    def __init__(self, width=1024, height=768):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.grid = True
        self.points = []
        self.setMouseTracking(True) # only get events when button is pressed
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Drawable')
        # self.show()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            # self.points = []
            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
            # try:
            #     self.points = custom_filter(self.points) # needs to be implemented outside!
            # except NameError:
            #     pass
            self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = False
            self.update()

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.points.append((ev.x(), ev.y()))
            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))
        qp.setPen(QtGui.QColor(0, 155, 0))
        # qp.drawPolyline(self.poly(self.points))

        for point in self.points:
            qp.drawEllipse(point[0]-1, point[1] - 1, 2, 2)
            # print(point)

        if self.grid:
            qp.setPen(QtGui.QColor(255, 100, 100, 20))  # semi-transparent
            for x in range(0, self.width(), 20):
                qp.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 20):
                qp.drawLine(0, y, self.width(), y)
        qp.end()

    def add_point(self, x, y):
        if self.drawing:
            self.points.append((x, y))

            self.update()

    def start_drawing(self):
        print("Started drawing")
        self.drawing = True

    def stop_drawing(self):
        print("Stopped drawing")
        self.drawing = False


class ColorPicker(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.colors = {
            'RED': (255, 0, 0),
            'GREEN': (0, 255, 0),
            'YELLOW': (255, 255, 0),
            'GRAY': (100, 100, 100),
            'BLACK': (0, 0, 0),
            }

        self.btn_colors = []

        self.active_color = None

        self.init_ui()

    def init_ui(self):
        layout = Qt.QHBoxLayout()

        for name, color in self.colors.items():
            btn = Color(color[0], color[1], color[2], name)
            layout.addWidget(btn)
            self.btn_colors.append(btn)
        self.setLayout(layout)

        for button in self.btn_colors:
            # keep this order
            button.clicked.connect(self.choose_color)
            button.clicked.connect(button.highlight)

    def choose_color(self):
        for button in self.btn_colors:
            button.unhighlight()





class Color(QtWidgets.QPushButton):
    def __init__(self, r=0, g=0, b=0, name='TEST'):
        super().__init__()
        self.highlighted = False
        self.color = QtGui.QColor(r, g, b)
        self.name = name

        self.css_highlighted = """
            background-color: rgb(%d, %d, %d);
            color: white;
            border: 5px solid green;
        """ % (r, g, b)
        self.css_not_highlighted = """
            background-color: rgb(%d, %d, %d);
            color: white;
            border: 2px solid gray;
        """ % (r, g, b)

        self.setStyleSheet(self.css_not_highlighted)

    def highlight(self):
        print("highlight")
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)

    def unhighlight(self):
        self.hightlighted = False
        self.setStyleSheet(self.css_not_highlighted)



class PaintApplication():

    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080

    name_hard = 'Nintendo RVL-CNT-01-TR'

    RED = QtGui.QColor(255, 0, 0)
    GREEN = QtGui.QColor(0, 255, 0)
    YELLOW = QtGui.QColor(255, 255, 0)
    GRAY = QtGui.QColor(100, 100, 100)
    BLACK = QtGui.QColor(0, 0, 0)

    def __init__(self):

        self.wm = None

        self.setup_ui()

        self.window.show()

    def setup_ui(self):
        self.window = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.window.setLayout(self.main_layout)

        self.window.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.setup_config_ui()
        self.setup_paint_area_ui()

    def setup_config_ui(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("WiiMote connection status"))
        self.label_wm_connection_status = QtWidgets.QLabel("Not connected")
        self.label_wm_connection_status.setAlignment(Qt.Qt.AlignCenter)
        self.fill_label_background(self.label_wm_connection_status, self.RED)
        layout.addWidget(self.label_wm_connection_status)

        layout.addWidget(QtWidgets.QLabel("Enter your WiiMotes Mac Address:"))
        self.line_edit_br_addr = QtWidgets.QLineEdit()
        self.line_edit_br_addr.setText('B8:AE:6E:1B:5B:03')
        layout.addWidget(self.line_edit_br_addr)
        self.button_connect = QtWidgets.QPushButton("Connect")
        self.button_connect.clicked.connect(self.connect_wm)
        layout.addWidget(self.button_connect)

        # layout.addSpacerItem(QtWidgets.QSpacerItem(0, 300))

        self.main_layout.addLayout(layout, 0, 0, 12, 2, Qt.Qt.AlignCenter)

    def setup_paint_area_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # layout.addWidget(QtWidgets.QLabel("MENU COLORS ETC"), 1, Qt.Qt.AlignCenter)
        layout.addWidget(ColorPicker(), 1, Qt.Qt.AlignCenter)

        self.paint_area = PaintArea()
        layout.addWidget(self.paint_area, 11)

        self.main_layout.addLayout(layout, 0, 2, 12, 10)

    def connect_wm(self):
        addr = self.line_edit_br_addr.text()
        print("Connecting to %s (%s)" % (self.name_hard, addr))
        self.wm = wiimote.connect(addr, self.name_hard)
        print("Connected")

        self.fill_label_background(self.label_wm_connection_status, self.GREEN)
        self.label_wm_connection_status.setText("Connected to %s" % addr)

        self.wm.buttons.register_callback(self.handle_buttons)
        self.wm.ir.register_callback(self.handle_ir_data)

    def handle_buttons(self, buttons):
        for button in buttons:
            if button[0] == 'A':
                if button[1]:
                    self.paint_area.start_drawing()
                elif not button[1]:
                    self.paint_area.stop_drawing()

    def handle_ir_data(self, ir_data):
        if len(ir_data) > 0:
            for ir_object in ir_data:
                if ir_object['id'] < 50:
                    self.paint_area.add_point(ir_object['x'], ir_object['y'])
        print(ir_data)

    def fill_label_background(self, label, color):
        label.setAutoFillBackground(True)

        palette = label.palette()
        palette.setColor(label.backgroundRole(), color)
        label.setPalette(palette)


def main():

    addr_hard = 'B8:AE:6E:1B:5B:03'
    name_hard = 'Nintendo RVL-CNT-01-TR'

    print("Test")

    # print(("Connecting to %s (%s)" % (name_hard, addr_hard)))
    # wm = wiimote.connect(addr_hard, name_hard)
    #
    # app = QtWidgets.QApplication([])
    # global pa
    # pa = PaintArea()
    #
    #
    # wm.ir.register_callback(pa.add_point)
    # wm.buttons.register_callback(handle_button_press)



    app = QtWidgets.QApplication([])
    paint_app = PaintApplication()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

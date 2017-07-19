import lib.wiimote as wiimote
import time
import sys

from functools import partial

from PyQt5 import Qt, QtGui, QtCore, QtWidgets


"""
TODO:

    - mapping from 4 IR sensors to display pixels



    - at least 3 interaction techniques
        - selection
        - copy(cut) & paste
        - load & save


    - change brush/pen/color with gesture
        - gesture for color + selection with left/right gesture
        - gesture for brush size + in- or decrease with left/right gesture
        - different pen: shape dependent on rotation of wiimote


"""

class Mapping:

    def __init__(self):
        pass


class GestureRecognizer:

    """
    Created by Fabian Schatz
    """

    """
    $1
    - resample (128 samples per gesture recording)
    - rotate
    - calc distance to check which gesture


    widget aktuelle geste anzeigen

    übersicht über alle gesten
    """
    def __init__(self):
        pass


class PaintArea(QtWidgets.QWidget):
    """
    Created by Fabian Schatz
    """

    def __init__(self, width=1024, height=768):
        super().__init__()
        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.grid = True
        self.points = []
        self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()

        self.current_cursor_point = None

        self.active_color = QtGui.QColor(255, 255, 255)
        self.active_size = 5

    def init_ui(self):
        self.setWindowTitle('Drawable')

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
            # self.points.append((ev.x(), ev.y(), self.active_color))
            self.points.append(Pixel(ev.x(), ev.y(), self.active_color, self.active_size))
            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        # lines
        # qp.setBrush(QtGui.QColor(20, 255, 190))
        # dots

        # qp.drawPolyline(self.poly(self.points))
        ad = QtGui.QPainterPath()

        for point in self.points:
            qp.setPen(point.color)
            qp.drawEllipse(point.x-point.size//2, point.y - point.size//2, point.size, point.size)

            # refactor to draw a path instead of ellipses
            # set start point of path with moveTo(x,y)
            # only append avg of ir data to points
            # ad.lineTo(point.x-point.size//2, point.y - point.size//2)
        qp.drawPath(ad)

        if self.grid:
            qp.setPen(QtGui.QColor(255, 100, 100, 20))  # semi-transparent
            for x in range(0, self.width(), 20):
                qp.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 20):
                qp.drawLine(0, y, self.width(), y)

        if self.current_cursor_point:
            qp.setPen(QtGui.QColor(255, 0, 0))
            qp.drawRect(self.current_cursor_point[0]-10, self.current_cursor_point[1]-10, 20, 20)

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

    def increase_pen_size(self):
        self.active_size += 1

    def decrease_pen_size(self):
        if self.active_size > 1:
            self.active_size -= 1


class Pixel:
    """
    Created by Fabian Schatz
    """

    def __init__(self, x, y, color, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.size = size


class Path:
    """
    Created by Fabian Schatz
    """

    def __init__(self, points=[], color_r=255, color_g=255, color_b=255, stroke_width=1, opacity=1):
        self.points = points
        self.stroke_width = stroke_width
        self.color_r = color_r
        self.color_g = color_g
        self.color_b = color_b
        self.opacity = opacity
        self.css = None

    def add_point(self, x, y):
        self.points.append((x, y))

    def set_color(self, r, g, b):
        if r and g and b:
            pass
        else:
            raise ValueError()

    def update_css(self):
        self.css = """
            stroke-width: %d;
            fill-color: rgb(%d, %d, %d);
            stroke-opacity: %d;
        """ % (self.stroke_width, self.r, self.g, self.b, self.opacity)


class ColorPicker(QtWidgets.QWidget):
    """
    Created by Fabian Schatz
    """

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

        for button in self.btn_colors:
            if button.highlighted:
                self.active_color = button.color


class Color(QtWidgets.QPushButton):
    """
    Created by Fabian Schatz
    """
    def __init__(self, r=0, g=0, b=0, name='TEST'):
        super().__init__()
        self.highlighted = False
        self.color = QtGui.QColor(r, g, b)
        self.name = name

        self.css_highlighted = """
            background-color: rgb(%d, %d, %d);
            color: white;
            border: 5px solid green;
            border-radius: 20px;
        """ % (r, g, b)
        self.css_not_highlighted = """
            background-color: rgb(%d, %d, %d);
            color: white;
        """ % (r, g, b)

        self.setStyleSheet(self.css_not_highlighted)

        self.setFixedWidth(100)
        self.setFixedHeight(100)

    def highlight(self):
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)

    def unhighlight(self):
        self.highlighted = False
        self.setStyleSheet(self.css_not_highlighted)


class PaintApplication:
    """
    Created by Fabian Schatz
    """

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
        self.label_wm_connection_status.setFixedHeight(100)
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

        self.color_picker = ColorPicker()
        # layout.addWidget(self.color_picker, 1, Qt.Qt.AlignCenter)

        tl = QtWidgets.QHBoxLayout()

        btn_m = QtWidgets.QPushButton("-")
        btn_p = QtWidgets.QPushButton("+")

        btn_m.setMinimumHeight(100)
        btn_p.setMinimumHeight(100)

        tl.addWidget(btn_m)
        tl.addWidget(btn_p)
        tl.addWidget(self.color_picker)
        layout.addLayout(tl, 1)

        self.paint_area = PaintArea()
        layout.addWidget(self.paint_area, 11)

        self.main_layout.addLayout(layout, 0, 2, 12, 10)

        btn_p.clicked.connect(self.paint_area.increase_pen_size)
        btn_m.clicked.connect(self.paint_area.decrease_pen_size)

        for color in self.color_picker.btn_colors:
            color.clicked.connect(partial(self.update_pen_color, color.color))

    def update_pen_color(self, color):
        self.paint_area.active_color = color

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

            x = [ir_object['x'] for ir_object in ir_data]
            y = [ir_object['y'] for ir_object in ir_data]

            if self.paint_area.drawing:
                for ir_object in ir_data:
                    if ir_object['id'] < 50:
                        self.paint_area.points.append(Pixel(ir_object['x'], ir_object['y'], self.paint_area.active_color, self.paint_area.active_size))

            self.paint_area.current_cursor_point = (sum(x)//len(x), sum(y)//len(y))
            self.paint_area.update()
        print(ir_data)

    def fill_label_background(self, label, color):
        label.setAutoFillBackground(True)

        palette = label.palette()
        palette.setColor(label.backgroundRole(), color)
        label.setPalette(palette)


def main():

    addr_hard = 'B8:AE:6E:1B:5B:03'
    name_hard = 'Nintendo RVL-CNT-01-TR'

    app = QtWidgets.QApplication([])
    paint_app = PaintApplication()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

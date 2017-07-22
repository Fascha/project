import lib.wiimote as wiimote
import lib.gestures as gestures
from lib.wiimote_mapping import Mapping
import time
import sys

from functools import partial

import numpy as np

from PyQt5 import Qt, QtGui, QtCore, QtWidgets

"""
TODO:

    - mapping from 4 IR sensors to display pixels ---- DONE ----

    - reconstructure UI and maximise painting area

    - at least 3 interaction techniques
        - selection
        - copy(cut) & paste
        - load & save


    - change brush/pen/color with gesture
        - gesture for color + selection with left/right gesture
        - gesture for brush size + in- or decrease with left/right gesture
        - different pen: shape dependent on rotation of wiimote


    mapToGlobal

    wiimote ircam: 1024x768
        mitte ist bei width/2 und height/2
        => 512/384 in die matrize reinschmeisen und dann bekommen wir koordinaten wo wir hinzeigen
        => matrize jedes mal neu berechnen

"""



class Mapping_safe:

    SRC_W = 1024
    SRC_H = 768

    def __init__(self, dest_w, dest_h):
        self.DEST_W = dest_w
        self.DEST_H = dest_h
        self.sx1 = 0
        self.sy1 = 0
        self.sx2 = self.SRC_W
        self.sy2 = 0
        self.sx3 = self.SRC_H
        self.sy3 = self.SRC_W
        self.sx4 = 0
        self.sy4 = self.SRC_H

    def calc_source_to_dest_matrix(self, s1, s2, s3, s4):

        self.sx1 = s1[0]
        self.sy1 = s1[1]
        self.sx2 = s2[0]
        self.sy2 = s2[1]
        self.sx3 = s3[0]
        self.sy3 = s3[1]
        self.sx4 = s4[0]
        self.sy4 = s4[1]

        self.calc_scale_to_source()
        self.calc_source_to_dest()

    def calc_scale_to_source(self):
        source_points_123 = np.matrix([[self.sx1, self.sx2, self.sx3],
                                       [self.sy1, self.sy2, self.sy3],
                                       [1, 1, 1]])

        source_point_4 = [[self.sx4],
                          [self.sy4],
                          [1]]

        self.scale_to_source = np.linalg.solve(source_points_123, source_point_4)

        l, m, t = [float(x) for x in self.scale_to_source]

        self.unit_to_source = np.matrix([[l*self.sx1, m*self.sx2, t*self.sx3],
                                         [l*self.sy1, m*self.sy2, t*self.sy3],
                                         [l, m, t]])

    def calc_source_to_dest(self):
        dx1 = 0
        dy1 = 0
        dx2 = self.DEST_W
        dy2 = 0
        dx3 = self.DEST_W
        dy3 = self.DEST_H
        dx4 = 0
        dy4 = self.DEST_H

        dest_points_123 = np.matrix([[dx1, dx2, dx3],
                                     [dy1, dy2, dy3],
                                     [1, 1, 1]])

        dest_point_4 = np.matrix([[dx4],
                                  [dy4],
                                  [1]])

        self.scale_to_dest = np.linalg.solve(dest_points_123, dest_point_4)
        l, m, t = [float(x) for x in self.scale_to_dest]

        self.unit_to_dest = np.matrix([[l*dx1, m*dx2, t*dx3],
                                       [l*dy1, m*dy2, t*dy3],
                                       [l, m, t]])

        self.source_to_unit = np.linalg.inv(self.unit_to_source)

        self.source_to_dest = self.unit_to_dest @ self.source_to_unit

    def process_ir_data(self, x=512, y=384):
        x, y, z = [float(w) for w in (self.source_to_dest @ np.matrix([[x],
                                                                       [y],
                                                                       [1]]))]

        return self.dehomogenize(x, y, z)

    def dehomogenize(self, x, y, z):
        return x/z, y/z


class GestureRecognizer:
    """
    Created by Fabian Schatz & Marco Jakob
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
        self.current_recording = []
        self.recognition_mode = False
        pass


class PaintArea(QtWidgets.QWidget):
    """
    Created by Fabian Schatz
    """

    def __init__(self, width=1024, height=768):
        super().__init__()
        self.resize(width, height)
        print("SIZE OF PAINT AREA: ", self.size())
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.grid = True
        self.recognition_mode = False
        self.points = []

        self.current_mode = 'LINE'

        self.paint_objects = []

        self.current_paint_object = None

        self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()

        self.current_cursor_point = None

        self.active_color = QtGui.QColor(255, 255, 255)
        self.active_size = 20
        self.active_shape = 'LINE'

        # soem reference points for testing
        self.paint_objects.append(Pixel(0, 0, self.active_color, self.active_size))
        self.paint_objects.append(Pixel(0, self.height(), self.active_color, self.active_size))
        self.paint_objects.append(Pixel(self.width(), 0, self.active_color, self.active_size))
        self.paint_objects.append(Pixel(self.width(), self.height(), self.active_color, self.active_size))
        self.paint_objects.append(Pixel(self.width()/2, self.height()/2, self.active_color, self.active_size))
        #     self.paint_area.points.append(Pixel(600, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(700, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(800, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(900, 100, self.paint_area.active_color, self.paint_area.active_size))

    def init_ui(self):
        self.setWindowTitle('Drawable')

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.drawing = True

            if self.active_shape == 'LINE':
                self.current_paint_object = Line(color=self.active_color, size=self.active_size)
                self.current_paint_object.add_point(ev.x(), ev.y())
                self.paint_objects.append(self.current_paint_object)
            elif self.active_shape == 'CIRCLE':
                self.current_paint_object = Pixel(ev.x(), ev.y(), self.active_color)

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
            if self.active_shape == 'LINE':
                self.current_paint_object.add_point(ev.x(), ev.y())
            elif self.active_shape == 'CIRCLE':
                self.paint_objects.append(Pixel(ev.x(), ev.y(), self.active_color, self.active_size))

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

        for elem in self.paint_objects:
            if type(elem) == Line:
                line_pen = QtGui.QPen()
                line_pen.setColor(elem.color)
                line_pen.setWidth(elem.size)
                qp.setPen(line_pen)
                qp.drawPolyline(self.poly(elem.points))

            elif type(elem) == Pixel:
                pixel_pen = QtGui.QPen()
                pixel_pen.setColor(elem.color)
                pixel_pen.setWidth(elem.size)
                qp.setPen(pixel_pen)
                qp.drawEllipse(elem.x, elem.y, elem.size, elem.size)

        if self.grid:
            qp.setPen(QtGui.QColor(255, 100, 100, 50))  # semi-transparent
            for x in range(0, self.width(), 20):
                qp.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 20):
                qp.drawLine(0, y, self.width(), y)

        if self.current_cursor_point:
            qp.setPen(QtGui.QColor(255, 0, 0))

            qp.drawRect(self.current_cursor_point[0] - 10, self.current_cursor_point[1] - 10, 20, 20)
            qp.drawRect(self.current_cursor_point[0] - 10, self.current_cursor_point[1] - 10, 20, 20)

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


class Line:

    def __init__(self, color, size=5):
        self.points = []
        self.size = size
        self.color = color

    def add_point(self, x, y):
        self.points.append((x, y))


class Path:
    """
    Created by Fabian Schatz
    """

    def __init__(self, color, points=[], color_r=255, color_g=255, color_b=255, stroke_width=1, opacity=1):
        self.points = points
        self.stroke_width = stroke_width
        self.color = color
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


class ShapePicker(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.shapes = {
            'CIRCLE': 0,
            'LINE': 1
        }

        self.btn_shapes = []

        self.active_shape = None

        self.init_ui()

    def init_ui(self):
        layout = Qt.QHBoxLayout()

        for name, color in self.shapes.items():
            btn = Shape(name)
            layout.addWidget(btn)
            self.btn_shapes.append(btn)
        self.setLayout(layout)

        for button in self.btn_shapes:
            # keep this order
            button.clicked.connect(self.choose_shape)
            button.clicked.connect(button.highlight)

    def choose_shape(self):
        for shape in self.btn_shapes:
            shape.unhighlight()

        for shape in self.btn_shapes:
            if shape.highlighted:
                self.active_shape = shape.name


class Shape(QtWidgets.QPushButton):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.highlighted = False

        self.css_highlighted = """
            background-color: rgb(50, 50, 50, 0.6);
            border: 5px solid green;
            border-radius: 20px;
        """

        self.css_not_highlighted = """
            background-color: rgb(50, 50, 50, 0.6);
        """

        self.setStyleSheet(self.css_not_highlighted)

    def highlight(self):
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)


    def unhighlight(self):
        self.highlighted = False
        self.setStyleSheet(self.css_not_highlighted)


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
        print("CHOOSE COLOR")
        for button in self.btn_colors:
            button.unhighlight()


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
        print("HIGHLIGHT")
        self.highlighted = True
        self.setStyleSheet(self.css_highlighted)

    def unhighlight(self):
        self.highlighted = False
        self.setStyleSheet(self.css_not_highlighted)


class PaintApplication:
    """
    Created by Fabian Schatz
    """

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 600

    name_hard = 'Nintendo RVL-CNT-01-TR'

    RED = QtGui.QColor(255, 0, 0)
    GREEN = QtGui.QColor(0, 255, 0)
    YELLOW = QtGui.QColor(255, 255, 0)
    GRAY = QtGui.QColor(100, 100, 100)
    BLACK = QtGui.QColor(0, 0, 0)
    recognition_mode = False
    current_recording = []

    def __init__(self):

        self.wm = None

        self.dOne = gestures.DollarRecognizer()

        self.setup_ui()

        self.mapping = Mapping(1920, 1080)
        print("ASSERTED: (99.44448537537721, 847.1789582258892)")
        testdata = [(500, 300), (950, 300), (900, 700), (450, 690)]
        self.mapping.calculate_source_to_dest(testdata)
        print("RESULT: ", self.mapping.get_pointing_point())

        self.mapping = Mapping(self.paint_area.width(), self.paint_area.height())

        # MAPPING TEST

        self.window.show()

    def set_recognition_mode(self, value):
        # catch some wrong paramaters
        if value is True:
            self.current_recording = []
            self.recognition_mode = True
        else:
            self.recognition_mode = False
            print(self.current_recording)
            # self.dOne.AddTemplate(self.current_recording, "ColorGesture")
            self.dOne.dollar_recognize(self.current_recording)


    def setup_ui(self):
        self.window = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QGridLayout()
        self.window.setLayout(self.main_layout)

        print("WINDOWS SIZE BEFORE MAX: ", self.window.size())

        # self.window.resize()
        # self.window.showFullScreen()
        print("WINDOWS SIZE AFTER MAX: ", self.window.size())
        self.window.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.setup_config_ui()
        self.setup_paint_area_ui()

    def setup_config_ui(self):
        layout = QtWidgets.QVBoxLayout()


        self.num_ir_objects = QtWidgets.QLabel("0")
        fo = QtGui.QFont("Times", 128)
        self.num_ir_objects.setFont(fo)
        self.num_ir_objects.setFixedHeight(300)
        layout.addWidget(self.num_ir_objects)

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

        tl = QtWidgets.QHBoxLayout()

        self.shape_picker = ShapePicker()
        tl.addWidget(self.shape_picker)

        self.color_picker = ColorPicker()

        btn_m = QtWidgets.QPushButton("-")
        btn_p = QtWidgets.QPushButton("+")

        btn_m.setMinimumHeight(100)
        btn_p.setMinimumHeight(100)

        tl.addWidget(btn_m)
        tl.addWidget(btn_p)

        self.color_picker.setFixedHeight(1*self.WINDOW_HEIGHT/12)
        tl.addWidget(self.color_picker)
        layout.addLayout(tl)

        # width needs rethinking
        self.paint_area = PaintArea(width=(11*self.WINDOW_WIDTH/12), height=(11*self.WINDOW_HEIGHT/12))

        self.paint_area.setFixedHeight(11*self.WINDOW_HEIGHT/12)
        self.paint_area.setFixedWidth(11*self.WINDOW_WIDTH/12)
        # layout.addWidget(self.paint_area, 11)
        layout.addWidget(self.paint_area)

        # print("SIZE:", self.paint_area.size())
        # print("GEOMETRY:", self.paint_area.geometry())
        # print("WIDTH:", self.paint_area.width())
        # print("HEIGHT:", self.paint_area.height())

        self.main_layout.addLayout(layout, 0, 2, 12, 10)



        btn_p.clicked.connect(self.paint_area.increase_pen_size)
        btn_m.clicked.connect(self.paint_area.decrease_pen_size)

        for shape in self.shape_picker.btn_shapes:
            shape.clicked.connect(partial(self.update_shape, shape.name))

        for color in self.color_picker.btn_colors:
            color.clicked.connect(partial(self.update_pen_color, color.color))



         # corner points
        self.paint_area.points.append(Pixel(0, 0, self.paint_area.active_color, 50))
        self.paint_area.points.append(Pixel(self.paint_area.width()/2, self.paint_area.height()/2, self.paint_area.active_color, 50))
        self.paint_area.points.append(Pixel(self.paint_area.width(), 0, self.paint_area.active_color, 50))
        self.paint_area.points.append(Pixel(self.paint_area.width(), self.paint_area.height(), self.paint_area.active_color, 50))
        self.paint_area.points.append(Pixel(0, self.paint_area.height(), self.paint_area.active_color, 50))

    def update_shape(self, shape):
        self.paint_area.active_shape = shape

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
            # elif button[0] == 'B':
            #     if button[1]:
            #         self.start_recognition()
            #     elif not button[1]:
            #         self.stop_recognition()

    def start_recognition(self):
        self.set_recognition_mode(True)

    def stop_recognition(self):
        self.set_recognition_mode(False)

    def handle_ir_data(self, ir_data):

        # links oben in ir cam: x=0 y=786
        # rechts oben in ir cam: x=1023 y=786
        # links unten in ir cam: x=0 y=0
        # rechts unten in ir cam: x=1023 y=0

        self.num_ir_objects.setText("%d" % len(ir_data))

        # for ir in ir_data:
        #     print("x: %d\ty: %d\tid: %d" %(ir['x'], ir['y'], ir['id']))

        # there needto be the four markers for the corners
        if len(ir_data) == 4:

            x = [ir_object['x'] for ir_object in ir_data]
            y = [ir_object['y'] for ir_object in ir_data]

            # calc matrix
            if x[0] < 1023:
                sensor_coords = []
                for ir_object in ir_data:
                    sensor_coords.append((ir_object['x'], ir_object['y']))
                # print(sensor_coords)

                self.mapping.calculate_source_to_dest(sensor_coords)

                # map data
                mapped_data = self.mapping.get_pointing_point()

                # print("MAPPED_DATA:", mapped_data)
                # print()

                if self.paint_area.drawing:
                    # rechts links vertauscht
                    # self.paint_area.paint_objects.append(Pixel(mapped_data[1], mapped_data[0], self.paint_area.active_color, self.paint_area.active_size))

                    self.paint_area.paint_objects.append(Pixel(mapped_data[0], mapped_data[1], self.paint_area.active_color, 30))

                self.paint_area.current_cursor_point = mapped_data

                self.paint_area.update()


        # if self.recognition_mode:
        #     coord = self.paint_area.current_cursor_point
        #     self.current_recording.append(coord)
        # # print(ir_data)
        #     self.paint_area.points.append(Pixel(mapped_data[0], mapped_data[1], self.paint_area.active_color, self.paint_area.active_size))
        #
        #     self.paint_area.current_cursor_point = (mapped_data[0], mapped_data[1])
        #
        #     self.paint_area.points.append(Pixel(100, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(200, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(300, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(400, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(500, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(600, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(700, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(800, 100, self.paint_area.active_color, self.paint_area.active_size))
        #     self.paint_area.points.append(Pixel(900, 100, self.paint_area.active_color, self.paint_area.active_size))
        #
        #     self.paint_area.update()

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

import lib.wiimote as wiimote
from lib.gestures import GestureRecognition
from lib.wiimote_mapping import Mapping
import sys
from functools import partial
from lib.shapes import *
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


class UndoHandler(QtWidgets.QUndoCommand):
    """
    Created by Marco Peisker
    """

    def __init__(self, paint_objects):
        super().__init__()
        self.paint_objects = paint_objects
        self.deleted_obj = None

    def undo(self):
        print("undo", self.paint_objects)
        self.deleted_obj = self.paint_objects[-1]
        self.paint_objects.pop()

    def redo(self):
        if self.deleted_obj is not None:
            self.paint_objects.append(self.deleted_obj)


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

        self.stack = QtWidgets.QUndoStack()

        self.grid = True
        self.recognition_mode = False
        # self.points = []

        self.current_mode = 'LINE'

        self.paint_objects = []

        self.current_paint_object = None

        # self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()

        self.current_cursor_point = None

        self.active_color = QtGui.QColor(255, 255, 255)
        self.active_size = 20
        self.active_shape = 'LINE'

        # some reference points for testing
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
                # self.current_paint_object = Pixel(ev.x(), ev.y(), self.active_color)
                self.current_paint_object = Circles(ev.x(), ev.y(), self.active_color)
                self.paint_objects.append(self.current_paint_object)

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
            self.stack.push(UndoHandler(self.paint_objects))
            self.update()

    def mouseMoveEvent(self, ev):
        if self.drawing:
            if self.active_shape == 'LINE':
                self.current_paint_object.add_point(ev.x(), ev.y())
            elif self.active_shape == 'CIRCLE':
                # self.paint_objects.append(Pixel(ev.x(), ev.y(), self.active_color, self.active_size))
                self.current_paint_object.add_point(ev.x(), ev.y())

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
            pen = QtGui.QPen()
            pen.setColor(elem.color)
            pen.setWidth(elem.size)
            qp.setPen(pen)
            if type(elem) == Line:
                qp.drawPolyline(self.poly(elem.points))

            elif type(elem) == Pixel:
                qp.drawEllipse(elem.x, elem.y, elem.size, elem.size)

            elif type(elem) == Circles:
                for circle in elem.points:
                    qp.drawEllipse(circle[0], circle[1], elem.size, elem.size)

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
        self.current_paint_object.add_point(x, y)
        self.update()

        # if self.drawing:
        #     self.points.append((x, y))
        #     self.update()

    def start_drawing(self):
        print("Started drawing")
        self.drawing = True

    def stop_drawing(self):
        print("Stopped drawing")
        self.drawing = False

    # Undo function to remove last step from the stack
    def undo_drawing(self):
        if len(self.paint_objects) != 0:
            self.stack.undo()
            self.update()

    # Redo function
    def redo_drawing(self):
        self.stack.redo()
        self.update()

    def increase_pen_size(self):
        self.active_size += 1

    def decrease_pen_size(self):
        if self.active_size > 1:
            self.active_size -= 1


class ShapePicker(QtWidgets.QWidget):

    def __init__(self, width, height):
        self.width = width
        self.height = height

        super().__init__()

        self.shapes = {
            'CIRCLE': 0,
            'LINE': 1
        }

        self.btn_shapes = []

        self.active_shape = 'LINE'

        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        layout = Qt.QHBoxLayout()

        for name, color in self.shapes.items():
            btn = Shape(name)
            btn.setFixedSize(self.height - 20, self.height - 20)

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

    def __init__(self, width, height):
        self.width = width
        self.height = height

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

        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        layout = Qt.QHBoxLayout()

        for name, color in self.colors.items():
            btn = Color(color[0], color[1], color[2], name)
            btn.setFixedSize(self.height - 20, self.height - 20)

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

        # self.setFixedWidth(100)
        # self.setFixedHeight(100)

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

    # WINDOW_WIDTH = 1200
    # WINDOW_HEIGHT = 600

    name_hard = 'Nintendo RVL-CNT-01-TR'

    RED = QtGui.QColor(255, 0, 0)
    GREEN = QtGui.QColor(0, 255, 0)
    YELLOW = QtGui.QColor(255, 255, 0)
    GRAY = QtGui.QColor(100, 100, 100)
    BLACK = QtGui.QColor(0, 0, 0)

    def __init__(self):

        screen = QtWidgets.QDesktopWidget().screenGeometry(-1)
        print(" Screen width: " + str(screen.width()) + "x" + str(screen.height()))
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.wm = None

        self.setup_ui()

        self.gesture_recognition = GestureRecognition()
        self.recognition_data = []
        self.recognition_mode_enabled = False

        self.mapping = Mapping(1920, 1080)
        print("ASSERTED: (99.44448537537721, 847.1789582258892)")
        test_data = [(500, 300), (950, 300), (900, 700), (450, 690)]
        self.mapping.calculate_source_to_dest(test_data)
        print("RESULT: ", self.mapping.get_pointing_point())

        self.mapping = Mapping(self.paint_area.width(), self.paint_area.height())

        self.window.show()

    def setup_ui(self):
        self.window = QtWidgets.QWidget()

        print("WINDOWS SIZE BEFORE MAX: ", self.window.size())

        self.window.showFullScreen()
        self.window.resize(self.screen_width, self.screen_height)

        print("WINDOWS SIZE AFTER MAX: ", self.window.size())

        self.main_layout = QtWidgets.QGridLayout()
        self.window.setLayout(self.main_layout)

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
        # self.line_edit_br_addr.setText('18:2a:7b:c6:4c:e7')
        layout.addWidget(self.line_edit_br_addr)
        self.button_connect = QtWidgets.QPushButton("Connect")
        self.button_connect.clicked.connect(self.connect_wm)
        layout.addWidget(self.button_connect)

        # layout.addSpacerItem(QtWidgets.QSpacerItem(0, 300))

        self.main_layout.addLayout(layout, 0, 0, 12, 2, Qt.Qt.AlignCenter)

    def setup_paint_area_ui(self):
        layout = QtWidgets.QVBoxLayout()

        top_line_widget = QtWidgets.QWidget()
        top_line_widget.setFixedHeight(1*self.screen_height/12)
        top_line_widget_layout = QtWidgets.QHBoxLayout()

        top_line_widget_layout.setAlignment(Qt.Qt.AlignCenter)

        top_line_widget.setLayout(top_line_widget_layout)

        # for debugging
        # top_line_widget.setStyleSheet("border: 5px solid green; border-radius: 20px;")

        self.shape_picker = ShapePicker(top_line_widget.width(), top_line_widget.height())
        self.shape_picker.setFixedHeight(top_line_widget.height())
        top_line_widget_layout.addWidget(self.shape_picker)

        self.color_picker = ColorPicker(top_line_widget.width(), top_line_widget.height())

        btn_m = QtWidgets.QPushButton("-")
        btn_p = QtWidgets.QPushButton("+")

        btn_m.setFixedSize(top_line_widget.height() - 20, top_line_widget.height() - 20)
        btn_p.setFixedSize(top_line_widget.height() - 20, top_line_widget.height() - 20)

        top_line_widget_layout.addWidget(btn_m)
        top_line_widget_layout.addWidget(btn_p)

        top_line_widget_layout.addWidget(self.color_picker)

        layout.addWidget(top_line_widget)

        self.paint_area = PaintArea(width=(11*self.screen_width/12), height=(11*self.screen_height/12))

        self.paint_area.setFixedHeight(11*self.screen_height/12)
        self.paint_area.setFixedWidth(11*self.screen_width/12)

        layout.addWidget(self.paint_area)

        self.main_layout.addLayout(layout, 0, 2, 12, 10)

        btn_p.clicked.connect(self.paint_area.increase_pen_size)
        btn_m.clicked.connect(self.paint_area.decrease_pen_size)

        for shape in self.shape_picker.btn_shapes:
            shape.clicked.connect(partial(self.update_shape, shape.name))

        for color in self.color_picker.btn_colors:
            color.clicked.connect(partial(self.update_pen_color, color.color))

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
            elif button[0] == 'B':
                if button[1]:
                    self.start_recognition()
                elif not button[1]:
                    self.stop_recognition()
            # Undo last step
            elif button[0] == 'Minus':
                if button[1]:
                    self.paint_area.undo_drawing()
                elif not button[1]:
                    # do something
                    print("Undo button not pressed")
            # Redo last step
            elif button[0] == 'Plus':
                if button[1]:
                    self.paint_area.redo_drawing()
                elif not button[1]:
                    # do something
                    print("Redo button not pressed")

    def start_recognition(self):
        print("Started Recognition Mode")
        self.recognition_mode_enabled = True
        self.recognition_data = []
        # self.set_recognition_mode(True)

    def stop_recognition(self):
        print("Stopped Recognition Mode")
        self.recognition_mode_enabled = False
        gesture = self.gesture_recognition.get_gesture(self.recognition_data)
        # handle gesture etc
        print(gesture)

        # self.set_recognition_mode(False)

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
                # sensor_coords = []
                # for ir_object in ir_data:
                #     sensor_coords.append((ir_object['x'], ir_object['y']))

                # more pythonic
                sensor_coords = [(ir_object['x'], ir_object['y']) for ir_object in ir_data]

                self.mapping.calculate_source_to_dest(sensor_coords)

                # map data
                mapped_data = self.mapping.get_pointing_point()

                if self.paint_area.drawing:
                    # self.paint_area.paint_objects.append(Pixel(mapped_data[0], mapped_data[1],
                    #                                            self.paint_area.active_color, 30))

                    # self.paint_area.add_point(mapped_data[0], mapped_data[1])
                    self.paint_area.add_point(*mapped_data)

                self.paint_area.current_cursor_point = mapped_data

                if self.recognition_mode_enabled:
                    self.recognition_data.append(mapped_data)

                self.paint_area.update()

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

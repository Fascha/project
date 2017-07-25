import lib.wiimote as wiimote
from lib.gestures import GestureRecognition
from lib.wiimote_mapping import Mapping
import sys
import math
from functools import partial
from lib.shapes import *
from PyQt5 import Qt, QtGui, QtCore, QtWidgets
from collections import OrderedDict

"""
TODO:

    - mapping from 4 IR sensors to display pixels ---- DONE ----

    - reconstructure UI and maximise painting area:
        - elements:
            - shapepicker

            - colorpicker

            - toolpicker

            - wiimote:
                - lineedit for mac addr
                - button to connect
                - status of connection

            - count ir makers


    - superclass for all shapes with:
        - def add_point(x, y)
        - def move(vector)


    - rotate

    - scale/zoom

    - irmarkes@wiimote buttons

    - at least 3 interaction techniques
        - selection
        - copy(cut) & paste
        - load & save

    - gesture recognition
        - recognize gesture ---- DONE ----
        - save new gesture

    - DEMO RELEASE IN GITHUB

    - change brush/pen/color with gesture
        - gesture for color + selection with left/right gesture ---- tbd Marco Peisker ----
        - gesture for brush size + in- or decrease with left/right gesture
        - different pen: shape dependent on rotation of wiimote

    - mapToGlobal

    wiimote ircam: 1024x768 ---- DONE ----
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

        self.selection_rect = None

        # self.setMouseTracking(True)  # only get events when button is pressed
        self.init_ui()

        self.current_cursor_point = None

        self.active_color = QtGui.QColor(255, 255, 255)
        self.active_size = 20
        self.active_shape = 'LINE'

        # some reference points for testing
        # self.paint_objects.append(Pixel(0, 0, self.active_color, self.active_size))
        one = Circles(self.active_color, self.active_size)
        one.add_point(0, 0)
        self.paint_objects.append(one)

        two = Circles(self.active_color, self.active_size)
        two.add_point(self.width() - 2 * self.active_size, 0)
        self.paint_objects.append(two)

        three = Circles(self.active_color, self.active_size)
        three.add_point(self.width() - 2 * self.active_size, self.height() - 2 * self.active_size)
        self.paint_objects.append(three)

        four = Circles(self.active_color, self.active_size)
        four.add_point(self.width() / 2 - self.active_size, self.height() / 2 - self.active_size)
        self.paint_objects.append(four)

        five = Circles(self.active_color, self.active_size)
        five.add_point(0, self.height() - self.active_size * 2)
        self.paint_objects.append(five)

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
                self.current_paint_object = Circles(color=self.active_color, size=self.active_size)
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
            if elem.selected:
                pen.setColor(QtGui.QColor(255, 255, 255))
            else:
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

        if self.selection_rect:
            qp.setBrush(QtGui.QColor(2, 250, 250, 64))
            qp.drawRect(self.selection_rect)

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

        if self.active_shape == 'LINE':
            self.current_paint_object = Line(color=self.active_color, size=self.active_size)
            self.paint_objects.append(self.current_paint_object)
        elif self.active_shape == 'CIRCLE':
            self.current_paint_object = Circles(color=self.active_color, size=self.active_size)
            self.paint_objects.append(self.current_paint_object)

    def stop_drawing(self):
        print("Stopped drawing")
        self.drawing = False
        self.stack.push(UndoHandler(self.paint_objects))
        self.update()

    # Undo function to remove last step from the stack
    def undo_drawing(self):
        if len(self.paint_objects) != 0:
            self.stack.undo()
            self.update()

    # Redo function
    def redo_drawing(self):
        self.stack.redo()
        self.update()

    # Select previous color with left D-Pad key
    def select_previous_color(self):
        #print("active color ", self.active_color)
        self.update()

    # Select next color with right D-Pad key
    def select_next_color(self):
        self.update()

    def increase_pen_size(self):
        self.active_size += 1

    def decrease_pen_size(self):
        if self.active_size > 1:
            self.active_size -= 1


class ShapePicker(QtWidgets.QWidget):
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

        super().__init__()

        self.shapes = {
            'CIRCLE': 0,
            'LINE': 1
        }

        # self.btn_shapes = []

        self.btn_shapes = {}

        self.active_shape = 'LINE'

        self.init_ui()

    def init_ui(self):
        if self.width and self.height:
            self.setFixedWidth(self.width)
            self.setFixedHeight(self.height)
        layout = Qt.QHBoxLayout()

        for name, color in self.shapes.items():
            btn = Shape(name)
            if self.width and self.height:
                btn.setFixedSize(self.height - 20, self.height - 20)

            layout.addWidget(btn)
            # self.btn_shapes.append(btn)
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
            border-radius: 20px;
        """

        self.css_not_highlighted = """
            background-color: rgb(150, 150, 150);
            border-radius: 20px;
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


class ToolPicker(QtWidgets.QWidget):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        super().__init__()

        self.tools = {
            'DRAW': 0,
            'SELECT': 1,
            'MOVE': 2,
            'ROTATE': 3
        }

        self.btn_tools = {}

        self.active_tool = 'DRAW'

        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        layout = Qt.QHBoxLayout()

        for name, color in self.tools.items():
            btn = Tool(name)
            btn.setFixedSize(self.height - 20, self.height - 20)

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


class PaintApplication:
    """
    Created by Fabian Schatz
    """

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

        self.active_area = 'paint_area'

        self.mapping = Mapping(1920, 1080)
        print("ASSERTED: (99.44448537537721, 847.1789582258892)")
        test_data = [(500, 300), (950, 300), (900, 700), (450, 690)]
        self.mapping.calculate_source_to_dest(test_data)
        print("RESULT: ", self.mapping.get_pointing_point())

        # self.mapping = Mapping(self.paint_area.width(), self.paint_area.height())

        self.paint_area_absolut_x_pos = self.window.width() - self.paint_area.width()
        self.paint_area_absolut_y_pos = self.window.height() - self.paint_area.height()

        self.mapping = Mapping(self.window.width(), self.window.height())

        self.select_area_start_pos = None
        self.select_area_end_pos = None
        self.selection_mode_enabled = False
        self.dragging_mode = False
        self.select_tlx = None
        self.select_tly = None
        self.select_brx = None
        self.select_bry = None
        self.selected_objects = []
        self.direction_list = []

        self.moving = False
        self.moving_coords = []

        self.last_known_cursor_coord = None

        # stuff selected at startup

        self.tool_picker.btn_tools['DRAW'].click()
        self.shape_picker.btn_shapes['LINE'].click()
        self.color_picker.btn_colors['RED'].click()

        self.window.show()

    def setup_ui(self):
        self.window = QtWidgets.QWidget()

        print("WINDOWS SIZE BEFORE MAX: ", self.window.size())

        self.window.showFullScreen()
        self.window.resize(self.screen_width, self.screen_height)

        print("WINDOWS SIZE AFTER MAX: ", self.window.size())

        # self.main_layout = QtWidgets.QGridLayout()
        # self.window.setLayout(self.main_layout)
        #
        # self.setup_config_ui()
        # self.setup_paint_area_ui()

        self.main_layout = QtWidgets.QHBoxLayout()
        self.window.setLayout(self.main_layout)

        self.setup_left_column(2 * self.window.width() / 12)
        self.setup_paint_area(10 * self.window.width() / 12, self.window.height())

    def setup_left_column(self, width):
        """
            - shapepicker

            - colorpicker

            - toolpicker

            - wiimote:
                - lineedit for mac addr
                - button to connect
                - status of connection

            - count ir makers

        """

        left_colum_widget = QtWidgets.QWidget()
        left_colum_widget.setFixedWidth(width)
        layout = QtWidgets.QVBoxLayout()
        left_colum_widget.setLayout(layout)

        self.shape_picker = ShapePicker(width, 100)
        layout.addWidget(self.shape_picker)

        self.color_picker = ColorPicker(width, 100)
        layout.addWidget(self.color_picker)

        self.tool_picker = ToolPicker(width, 100)
        layout.addWidget(self.tool_picker)

        self.btn_m = QtWidgets.QPushButton("-")
        self.btn_p = QtWidgets.QPushButton("+")

        layout.addWidget(self.btn_m)
        layout.addWidget(self.btn_p)

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

        layout.addWidget(QtWidgets.QLabel("Number of tracked IR-Markers:"))
        self.num_ir_objects = QtWidgets.QLabel("0")
        font = QtGui.QFont("Helvetica", 32)
        self.num_ir_objects.setFont(font)
        self.num_ir_objects.setFixedHeight(300)
        layout.addWidget(self.num_ir_objects)

        # needed so the elements do not stretch the whole hieght and therefore have huge white gaps inbetween
        layout.addStretch()

        self.main_layout.addWidget(left_colum_widget)

    def setup_paint_area(self, width, height):
        self.paint_area = PaintArea(width=width, height=height)

        self.main_layout.addWidget(self.paint_area)

        self.btn_p.clicked.connect(self.paint_area.increase_pen_size)
        self.btn_m.clicked.connect(self.paint_area.decrease_pen_size)

        for name, btn in self.shape_picker.btn_shapes.items():
            btn.clicked.connect(partial(self.update_shape, btn.name))

        for name, color in self.color_picker.btn_colors.items():
            color.clicked.connect(partial(self.update_pen_color, color.color))

        for name, tool in self.tool_picker.btn_tools.items():
            tool.clicked.connect(partial(self.update_tool, tool.name))

    # deprecated (can be deleted)
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

    # deprecated (can be deleted)
    def setup_paint_area_ui(self):
        layout = QtWidgets.QVBoxLayout()

        top_line_widget = QtWidgets.QWidget()
        top_line_widget.setFixedHeight(1 * self.screen_height / 12)
        top_line_widget_layout = QtWidgets.QHBoxLayout()

        top_line_widget_layout.setAlignment(Qt.Qt.AlignCenter)

        top_line_widget.setLayout(top_line_widget_layout)

        # for debugging
        # top_line_widget.setStyleSheet("border: 5px solid green; border-radius: 20px;")


        self.shape_picker = ShapePicker(top_line_widget.width(), top_line_widget.height())
        self.shape_picker.setFixedHeight(top_line_widget.height())
        top_line_widget_layout.addWidget(self.shape_picker)

        self.color_picker = ColorPicker(top_line_widget.width(), top_line_widget.height())

        self.tool_picker = ToolPicker(top_line_widget.width(), top_line_widget.height())

        btn_m = QtWidgets.QPushButton("-")
        btn_p = QtWidgets.QPushButton("+")

        btn_m.setFixedSize(top_line_widget.height() - 20, top_line_widget.height() - 20)
        btn_p.setFixedSize(top_line_widget.height() - 20, top_line_widget.height() - 20)

        top_line_widget_layout.addWidget(btn_m)
        top_line_widget_layout.addWidget(btn_p)

        top_line_widget_layout.addWidget(self.color_picker)

        top_line_widget_layout.addWidget(self.tool_picker)

        layout.addWidget(top_line_widget)

        self.paint_area = PaintArea(width=(11 * self.screen_width / 12), height=(11 * self.screen_height / 12))

        self.paint_area.setFixedHeight(11 * self.screen_height / 12)
        self.paint_area.setFixedWidth(11 * self.screen_width / 12)

        layout.addWidget(self.paint_area)

        self.main_layout.addLayout(layout, 0, 2, 12, 10)

        btn_p.clicked.connect(self.paint_area.increase_pen_size)
        btn_m.clicked.connect(self.paint_area.decrease_pen_size)

        for name, btn in self.shape_picker.btn_shapes.items():
            btn.clicked.connect(partial(self.update_shape, btn.name))

        for color in self.color_picker.btn_colors:
            color.clicked.connect(partial(self.update_pen_color, color.color))

        for tool in self.tool_picker.btn_tools:
            tool.clicked.connect(partial(self.update_tool, tool.name))

    def update_shape(self, shape):
        self.paint_area.active_shape = shape

    def update_pen_color(self, color):
        self.paint_area.active_color = color

    def update_tool(self, tool):
        self.paint_area.active_tool = tool
        self.tool_picker.active_tool = tool

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
            # if button[0] == 'A' and not self.dragging_mode:
            if button[0] == 'A':
                if button[1]:
                    if self.tool_picker.active_tool == 'DRAW':
                        self.paint_area.start_drawing()
                    elif self.tool_picker.active_tool == 'SELECT':
                        if len(self.selected_objects) > 0:
                            for obj in self.selected_objects:
                                obj.selected = False
                        self.selection_mode_enabled = True
                        self.select_area_start_pos = None
                        self.select_area_end_pos = None
                    elif self.tool_picker.active_tool == 'MOVE':
                        self.start_moving()
                elif not button[1]:
                    if self.tool_picker.active_tool == 'DRAW':
                        self.paint_area.stop_drawing()
                    elif self.tool_picker.active_tool == 'SELECT':
                        self.selection_mode_enabled = False
                        self.paint_area.selection_rect = None
                        self.selected_objects = self.get_selected_objects()
                    elif self.paint_area.active_tool == 'MOVE':
                        # self.tool_picker.btn_tools['MOVE'].click()
                        # self.dragging_mode = True
                        self.stop_moving()
            # elif button[0] == 'A' and self.dragging_mode:
            #     if button[1]:
            #         pass
            #         self.tool_picker.active_tool == 'MOVE'
            #     elif not button[1]:
            #         self.dragging_mode = False
            #         self.tool_picker.btn_tools['SELECT'].click()
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
            # Select previous color with left button click
            elif button[0] == 'Left':
                if button[1]:
                    self.paint_area.select_previous_color()
                elif not button[1]:
                    # do something
                    print("Left button not pressed")
            # Select next color with right button click
            elif button[0] == 'Right':
                if button[1]:
                    self.paint_area.select_next_color()
                elif not button[1]:
                    # do something
                    print("Right button not pressed")

            elif button[0] == 'Up':
                print("UP")
                if button[1]:
                    for elem in self.paint_area.paint_objects:
                        elem.move((100, 100))
                    self.paint_area.update()
                elif not button[1]:
                    # do something
                    print("Right button not pressed")

            elif button[0] == 'Down':
                if button[1]:
                    # self.paint_area.select_next_color()
                    print("DOWN")
                    for elem in self.paint_area.paint_objects:
                        elem.move((-100, -100))

                    self.paint_area.update()
                elif not button[1]:
                    # do something
                    print("Right button not pressed")



    def moveObjects(self, objects):
        movement_data = self.calculateDirection()
        for i in range(len(objects)):
            for j in range(len(objects[i].points)):
                newX = objects[i].points[j][0] + (movement_data[0]*movement_data[2])/10
                newY = objects[i].points[j][1] + (movement_data[1]*movement_data[3])/10
                objects[i].points[j] = (newX, newY)

    def calculateDirection(self):
        self.direction_list
        x1 = self.direction_list[0][0]
        y1 = self.direction_list[0][1]
        x2 = self.direction_list[1][0]
        y2 = self.direction_list[1][1]
        distX = math.sqrt(math.pow((x2-x1),2))
        distY = math.sqrt(math.pow((y2-y1),2))
        if x1 < x2:
            directionX = 1
        else:
            directionX = -1
        if y1 < y2:
            directionY = 1
        else:
            directionY = -1

        return distX, distY, directionX, directionY

    def get_selected_objects(self):
        selected_objects = []
        for obj in self.paint_area.paint_objects:
            for point in obj.points:
                if point[0] > self.select_tlx and point[0] < self.select_brx:
                    print("in x range")
                    if point[1] > self.select_tly and point[1] < self.select_bry:
                        print("in x and y range so should be selected")
                        selected_objects.append(obj)
                        obj.selected = True
                        break

        return selected_objects

    def start_recognition(self):
        print("Started Recognition Mode")
        self.recognition_mode_enabled = True
        self.recognition_data = []
        # self.set_recognition_mode(True)

    def stop_recognition(self):
        print("Stopped Recognition Mode")
        self.recognition_mode_enabled = False
        if len(self.recognition_data) > 0:
            gesture = self.gesture_recognition.get_gesture(self.recognition_data)
            # handle gesture etc
            print(gesture)
            print(gesture.name)
            self.handle_gesture(gesture)

            # self.set_recognition_mode(False)

    def start_moving(self):
        self.last_known_cursor_coord = None
        self.moving = True

    def stop_moving(self):
        self.moving = False
        self.moving_coords = []

    def handle_gesture(self, gesture):
        if gesture.name == 'Swipe left':
            if self.active_area == 'paint_area':
                self.paint_area.undo_drawing()
            elif self.active_area == 'color_picker':
                # nextcolor
                pass
        elif gesture.name == 'Swipe right':
            if self.active_area == 'paint_area':
                self.paint_area.redo_drawing()
            elif self.active_area == 'color_picker':
                # previouscolor
                pass
        elif gesture.name == 'Circle clockwise':
            self.shape_picker.btn_shapes['CIRCLE'].click()
        elif gesture.name == 'Circle counterclockwise':
            self.shape_picker.btn_shapes['LINE'].click()
        elif gesture.name == 'C_shape':
            self.selection_mode = 'colorpicker'
        elif gesture.name == 'mirrored_C_shape':
            self.selection_mode = 'standard'
            print("standard")

    def handle_ir_data(self, ir_data):

        # links oben in ir cam: x=0 y=786
        # rechts oben in ir cam: x=1023 y=786
        # links unten in ir cam: x=0 y=0
        # rechts unten in ir cam: x=1023 y=0

        self.num_ir_objects.setText("%d" % len(ir_data))
        led_list = [0, 0, 0, 0]
        for x in range(len(ir_data)):
            led_list[x] = 1
        self.wm.set_leds(led_list)

        # for ir in ir_data:
        #     print("x: %d\ty: %d\tid: %d" %(ir['x'], ir['y'], ir['id']))

        # there needto be the four markers for the corners
        if len(ir_data) == 4:

            x = [ir_object['x'] for ir_object in ir_data]
            y = [ir_object['y'] for ir_object in ir_data]

            # calc matrix
            if x[0] < 1023:
                # more pythonic
                sensor_coords = [(ir_object['x'], ir_object['y']) for ir_object in ir_data]

                self.mapping.calculate_source_to_dest(sensor_coords)

                # map data
                mapped_data = self.mapping.get_pointing_point()

                ###############
                ## from here on we can do everything with the calculated "cursor" pos
                ###############

                # setting cursor pos
                self.paint_area.current_cursor_point = mapped_data

                # checking if cursor position is in paint area
                if mapped_data[0] > self.paint_area_absolut_x_pos and mapped_data[1] > self.paint_area_absolut_y_pos:
                    if self.paint_area.drawing:
                        # drawing into the paint area
                        self.paint_area.add_point(*mapped_data)

                # recording data for gesture recognition
                if self.recognition_mode_enabled:
                    self.recognition_data.append(mapped_data)

                if len(self.direction_list) < 2:
                    self.direction_list.append(self.paint_area.current_cursor_point)
                elif len(self.direction_list) == 2:
                    self.direction_list[0] = self.direction_list[1]
                    self.direction_list = self.direction_list[:1]
                    self.direction_list.append(self.paint_area.current_cursor_point)

                if self.dragging_mode:
                    self.moveObjects(self.selected_objects)

                # handle toolpicker states /selected tool

                if self.tool_picker.active_tool == 'SELECT' and self.selection_mode_enabled:
                    if not self.select_area_start_pos:
                        self.select_area_start_pos = mapped_data

                    self.select_area_end_pos = mapped_data

                    print("SELECTED OBJECTS:", self.selected_objects)
                    self.update_selection_rect()

                if self.tool_picker.active_tool == 'MOVE' and self.moving:
                    if self.last_known_cursor_coord:
                        move_vector = (mapped_data[0] - self.last_known_cursor_coord[0], mapped_data[1] - self.last_known_cursor_coord[1])


                        for elem in self.selected_objects:
                            elem.move(move_vector)

                        print(move_vector)
                        print("SELECTED OBJECTS:", self.selected_objects)

                    self.last_known_cursor_coord = mapped_data
                #     self.moving_coords.append(mapped_data)
                #
                #     if len(self.moving_coords) > 1:
                #         p2 = self.moving_coords[-1]
                #         p1 = self.moving_coords[-2]
                #         move_vector = (p2[0] - p1[0], p2[1] - p1[1])
                #
                #         for obj in self.selected_objects:
                #             obj.move(move_vector)
                #
                        # print(move_vector)
                print(self.moving_coords)
                self.paint_area.update()

    def update_selection_rect(self):
        if self.select_area_end_pos[0] > self.select_area_start_pos[0]:
            tlx = self.select_area_start_pos[0]
            brx = self.select_area_end_pos[0]
        else:
            tlx = self.select_area_end_pos[0]
            brx = self.select_area_start_pos[0]

        if self.select_area_end_pos[1] > self.select_area_start_pos[1]:
            tly = self.select_area_start_pos[1]
            bry = self.select_area_end_pos[1]
        else:
            tly = self.select_area_end_pos[1]
            bry = self.select_area_start_pos[1]

        self.select_tlx = tlx
        self.select_tly = tly
        self.select_brx = brx
        self.select_bry = bry

        tl = QtCore.QPoint(tlx, tly)
        br = QtCore.QPoint(brx, bry)

        self.paint_area.selection_rect = QtCore.QRect(tl, br)

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

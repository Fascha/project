import sys
from functools import partial

from PyQt5 import Qt, QtGui, QtCore, QtWidgets

import lib.wiimote as wiimote
from lib.color_picker import ColorPicker
from lib.gestures import GestureRecognition
from lib.paint_area import PaintArea
from lib.shape_picker import ShapePicker
from lib.tool_picker import ToolPicker
from lib.wiimote_mapping import Mapping

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






    TODO bis Dienstag 01.07 23:59:

    - Code cleanup (Comments)
    - Code Rafactoring (Decomposition, eigene Files für Klassen etc.)
    - Code Refactoring (Pythonic vs non-pythonic)
    - PEP8


    - Cursor mit aktueller Farbe einfärben ---- DONE ----

    - Video
    - Paper


    OPTIONAL:
        - Auslagern der Gestendaten in File und einlesen des Files
        - Rotation
        - Delete
        - Scale

"""




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

        # used for testing the IR Mapping
        # print("ASSERTED: (99.44448537537721, 847.1789582258892)")
        # test_data = [(500, 300), (950, 300), (900, 700), (450, 690)]
        # self.mapping.calculate_source_to_dest(test_data)
        # print("RESULT: ", self.mapping.get_pointing_point())

        self.mapping = Mapping(self.window.width(), self.window.height())

        self.select_area_start_pos = None
        self.select_area_end_pos = None
        self.selection_mode_enabled = False

        self.select_tlx = None
        self.select_tly = None
        self.select_brx = None
        self.select_bry = None
        self.selected_objects = []

        self.moving = False
        self.moving_coords = []

        self.last_known_cursor_coord = None

        # initial selected tool/color/shape
        self.tool_picker.btn_tools['DRAW'].click()
        self.shape_picker.btn_shapes['LINE'].click()
        self.color_picker.btn_colors['RED'].click()

        self.window.show()

    def setup_ui(self):
        self.window = QtWidgets.QWidget()

        self.window.showFullScreen()
        self.window.resize(self.screen_width, self.screen_height)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.window.setLayout(self.main_layout)

        self.setup_left_column(8 * self.window.width() / 128)
        self.setup_paint_area(120 * self.window.width() / 128, self.window.height())

        self.connect_fake_buttons_for_wiimote()

    def setup_left_column(self, width):
        """
        This function will setup the left colum of the UI.
        It includes a WiiMote Section containing a LineEdit to enter your Mac Address and a Button to Connect.
        Additionally it contains a visual representation of the currently selected Shape and Tool

        :param width: desired width of the colum as an int
        """

        left_colum_widget = QtWidgets.QWidget()
        left_colum_widget.setFixedWidth(width)
        layout = QtWidgets.QVBoxLayout()
        left_colum_widget.setLayout(layout)

        self.shape_picker = ShapePicker(width, 100)
        layout.addWidget(self.shape_picker)

        self.color_picker = ColorPicker(width, 100)

        layout.addSpacing(50)

        self.tool_picker = ToolPicker(width, 3*self.window.height()/12)
        layout.addWidget(self.tool_picker)

        self.btn_m = QtWidgets.QPushButton("-")
        self.btn_p = QtWidgets.QPushButton("+")

        layout.addSpacing(200)
        self.label_wm_connection_status = QtWidgets.QLabel("Not connected")
        self.label_wm_connection_status.setAlignment(Qt.Qt.AlignCenter)
        self.label_wm_connection_status.setFixedHeight(100)
        self.fill_label_background(self.label_wm_connection_status, self.RED)
        layout.addWidget(self.label_wm_connection_status)

        layout.addWidget(QtWidgets.QLabel("Mac Address:"))
        self.line_edit_br_addr = QtWidgets.QLineEdit()
        # default value of you own wiimote
        self.line_edit_br_addr.setText('B8:AE:6E:1B:5B:03')
        layout.addWidget(self.line_edit_br_addr)
        self.button_connect = QtWidgets.QPushButton("Connect")
        self.button_connect.clicked.connect(self.connect_wm)
        layout.addWidget(self.button_connect)

        # needed so the elements do not stretch the whole height and therefore have huge white gaps inbetween
        layout.addStretch()

        self.main_layout.addWidget(left_colum_widget)

    def setup_paint_area(self, width, height):
        self.paint_area = PaintArea(width=width, height=height)

        self.main_layout.addWidget(self.paint_area)

    def connect_fake_buttons_for_wiimote(self):
        """
        This function connects UI elements so we can use them as Fake Buttons and invoke a clickevent
        partial is used so we can add parameters to the connection
        """
        self.btn_p.clicked.connect(self.paint_area.increase_pen_size)
        self.btn_m.clicked.connect(self.paint_area.decrease_pen_size)

        for name, btn in self.shape_picker.btn_shapes.items():
            btn.clicked.connect(partial(self.update_shape, btn.name))

        for name, color in self.color_picker.btn_colors.items():
            color.clicked.connect(partial(self.update_pen_color, color.color))

        for name, tool in self.tool_picker.btn_tools.items():
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
            if button[0] == 'A':
                if button[1]:
                    if self.paint_area.color_screen:
                        self.paint_area.color_screen = False
                        for color in self.paint_area.color_btns_overview:
                            if color.x <= self.paint_area.current_cursor_point[0] <= color.x + color.width():
                                if color.y <= self.paint_area.current_cursor_point[1] <= color.y + color.height():
                                    color.click()
                                    break
                        self.paint_area.update()
                    else:
                        if self.tool_picker.active_tool == 'DRAW':
                            if len(self.selected_objects) > 0:
                                for obj in self.selected_objects:
                                    obj.selected = False
                            self.paint_area.start_drawing()
                        elif self.tool_picker.active_tool == 'SELECT':
                            if len(self.selected_objects) > 0:
                                for obj in self.selected_objects:
                                    obj.selected = False
                            self.start_selection()
                        elif self.tool_picker.active_tool == 'MOVE':
                            self.start_moving()
                elif not button[1]:
                    if self.tool_picker.active_tool == 'DRAW':
                        self.paint_area.stop_drawing()
                    elif self.tool_picker.active_tool == 'SELECT':
                        self.stop_selection()
                        self.selected_objects = self.get_selected_objects()
                    elif self.paint_area.active_tool == 'MOVE':
                        self.stop_moving()
            elif button[0] == 'B':
                if button[1]:
                    self.start_recognition()
                elif not button[1]:
                    self.stop_recognition()
            # Undo last step
            elif button[0] == 'Minus':
                if button[1]:
                    self.paint_area.undo_drawing()
            # Redo last step
            elif button[0] == 'Plus':
                if button[1]:
                    self.paint_area.redo_drawing()
            # elif button[0] == 'Up':
            #     if button[1]:
            #         for elem in self.paint_area.paint_objects:
            #             elem.move((100, 100))
            #         self.paint_area.update()
            # elif button[0] == 'Down':
            #     if button[1]:
            #         for elem in self.paint_area.paint_objects:
            #             elem.move((-100, -100))
                    self.paint_area.update()
            elif button[0] == 'One':
                self.paint_area.increase_pen_size()
            elif button[0] == 'Two':
                self.paint_area.decrease_pen_size()

    def start_selection(self):
        self.selection_mode_enabled = True
        self.select_area_start_pos = None
        self.select_area_end_pos = None

    def stop_selection(self):
        self.selection_mode_enabled = False
        self.paint_area.selection_rect = None

    def get_selected_objects(self):
        """
        This function iterates over all paint_objects and compares every point of the object
        with the coordinates of the selection rect. If we get a match the object is appended to the selection
        and the objects selected variable is set to true
        :return: all matched objects as a list
        """
        selected_objects = []
        if self.select_tlx and self.select_tly and self.select_brx and self.select_bry:
            for obj in self.paint_area.paint_objects:
                for point in obj.points:
                    if self.select_tlx < point[0] < self.select_brx:
                        if self.select_tly < point[1] < self.select_bry:
                            selected_objects.append(obj)
                            obj.selected = True
                            break
        else:
            print("TLX/Y and BRX/Y not defined")
        return selected_objects

    def start_recognition(self):
        print("Started Recognition Mode")
        self.recognition_mode_enabled = True
        self.recognition_data = []

    def stop_recognition(self):
        print("Stopped Recognition Mode")
        self.recognition_mode_enabled = False
        if len(self.recognition_data) > 0:
            gesture = self.gesture_recognition.get_gesture(self.recognition_data)
            print(gesture.name)
            self.handle_gesture(gesture)

    def start_moving(self):
        self.last_known_cursor_coord = None
        self.moving = True

    def stop_moving(self):
        self.moving = False
        self.moving_coords = []

    def handle_gesture(self, gesture):
        """
        This function handles all available gestures defined in the __init__ of lib/gestures.py

        :param gesture: Gesture name as String
        """

        if gesture.name == 'Swipe left':
            if self.active_area == 'paint_area':
                self.paint_area.undo_drawing()
        elif gesture.name == 'Swipe right':
            if self.active_area == 'paint_area':
                self.paint_area.redo_drawing()
        elif gesture.name == 'Circle clockwise':
            self.shape_picker.btn_shapes['CIRCLE'].click()
        elif gesture.name == 'Circle counterclockwise':
            self.shape_picker.btn_shapes['LINE'].click()
        elif gesture.name == 'Z_shape':
            self.tool_picker.btn_tools['SELECT'].click()
        elif gesture.name == 'M_shape':
            self.tool_picker.btn_tools['MOVE'].click()
        elif gesture.name == 'C_shape':
            self.paint_area.color_screen = True
            self.paint_area.update()
        elif gesture.name == 'mirrored_C_shape':
            self.tool_picker.btn_tools['DRAW'].click()
            if len(self.selected_objects) > 0:
                for obj in self.selected_objects:
                    obj.selected = False

    def handle_ir_data(self, ir_data):
        """
        This function is registered as a callback to the WiiMote.
        It gets called everytime there is new IR-Data available from the WiiMote

        Some Reference Points of the IR-Camera
        top left: x=0 y=786
        top right: x=1023 y=786
        bottom left: x=0 y=0
        bottom right: x=1023 y=0

        :param ir_data: List of up to 4 recognized IR Markers
        """

        # visual representation of the number of ir markers recognized
        # for each marker a led on the bottom end of the wiimote will light up
        led_list = [0, 0, 0, 0]
        for x in range(len(ir_data)):
            led_list[x] = 1
        self.wm.set_leds(led_list)

        # there need to be the four markers for the corners
        # if there are not 4 markers our projective transformation won't work
        if len(ir_data) == 4:

            # needed so we don't get an error when connecting the WiiMote
            if ir_data[0]['x'] < 1023:
                sensor_coords = [(ir_object['x'], ir_object['y']) for ir_object in ir_data]
                self.mapping.calculate_source_to_dest(sensor_coords)

                mapped_data = self.mapping.get_pointing_point()
                # from here on we can do everything with the calculated "cursor" pos

                # setting cursor pos
                self.paint_area.current_cursor_point = mapped_data

                if self.paint_area.drawing:
                    # drawing into the paint area
                    self.paint_area.add_point(*mapped_data)

                # recording data for gesture recognition
                if self.recognition_mode_enabled:
                    self.recognition_data.append(mapped_data)

                # handle toolpicker states
                # selection tool
                # checking if the current state is the selection state
                if self.tool_picker.active_tool == 'SELECT' and self.selection_mode_enabled:
                    if not self.select_area_start_pos: # if there is no start position set yet we will set it
                        self.select_area_start_pos = mapped_data
                    # we constantly update the end position so we get a responsive selection rect
                    self.select_area_end_pos = mapped_data

                    self.update_selection_rect()

                if self.tool_picker.active_tool == 'MOVE' and self.moving:
                    if self.last_known_cursor_coord:
                        move_vector = (mapped_data[0] - self.last_known_cursor_coord[0],
                                       mapped_data[1] - self.last_known_cursor_coord[1])

                        for elem in self.selected_objects:
                            elem.move(move_vector)

                    self.last_known_cursor_coord = mapped_data

                self.paint_area.update()

    def update_selection_rect(self):
        """
        This function determines the top left corner and the bottom right corner of the selection rect
        This is needed to be able to pull the rect in every direction, without this calculation we could
        only pull the rect from the top left to the bottom right

        Qt Documentation:
        Constructs a rectangle with the given topLeft and bottomRight corners.
        """

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

    @staticmethod
    def fill_label_background(label, color):
        label.setAutoFillBackground(True)
        palette = label.palette()
        palette.setColor(label.backgroundRole(), color)
        label.setPalette(palette)


def main():
    app = QtWidgets.QApplication([])
    paint_app = PaintApplication()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

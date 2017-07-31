from PyQt5 import QtCore, QtWidgets, QtGui
from functools import partial
from lib.color_picker import Color

from lib.shapes import Line, Circles

from lib.undo_handler import UndoHandler


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

        self.current_mode = 'LINE'

        self.paint_objects = []

        self.current_paint_object = None
        self.selection_rect = None

        self.init_ui()

        self.current_cursor_point = None

        self.active_color = QtGui.QColor(128, 255, 128)
        self.active_size = 20
        self.active_shape = 'LINE'

        self.setup_color_screen()

    def setup_color_screen(self):
        self.color_btns_overview = []
        self.color_screen = False

        num_x = 20
        num_y = 20

        btn_width = self.width()/num_x
        btn_height = self.height()/num_y

        for x in range(num_x):
            for y in range(num_y):
                btn = Color(255/num_x*x, 255/num_y*y, 255/num_x*(x+y) % 255, x=x*btn_width, y=y*btn_height)
                btn.setFixedSize(btn_width, btn_height)
                btn.clicked.connect(partial(self.set_active_color, btn.color))
                self.color_btns_overview.append(btn)

    def set_active_color(self, color):
        self.active_color = color

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
                self.current_paint_object = Circles(color=self.active_color, size=self.active_size)
                self.paint_objects.append(self.current_paint_object)

            self.update()
        elif ev.button() == QtCore.Qt.RightButton:
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
                self.current_paint_object.add_point(ev.x(), ev.y())

            self.update()

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())

        if self.color_screen:
            for elem in self.color_btns_overview:
                qp.setBrush(elem.color)
                qp.drawRect(elem.x, elem.y, self.width()/10, self.height()/10)

        else:
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

                elif type(elem) == Circles:
                    for circle in elem.points:
                        qp.drawEllipse(circle[0], circle[1], elem.size, elem.size)

            if self.grid:
                qp.setPen(QtGui.QColor(255, 100, 100, 64))  # semi-transparent
                for x in range(0, self.width(), 30):
                    qp.drawLine(x, 0, x, self.height())
                for y in range(0, self.height(), 30):
                    qp.drawLine(0, y, self.width(), y)

        # drawing the current cursor position for visual reference
        if self.current_cursor_point:
            qp.setPen(QtGui.QColor(255, 0, 0))
            qp.setBrush(self.active_color)

            qp.drawRect(self.current_cursor_point[0] - 10, self.current_cursor_point[1] - 10, 20, 20)
            qp.drawRect(self.current_cursor_point[0] - 10, self.current_cursor_point[1] - 10, 20, 20)

        # drawing the selection rect if there is one
        if self.selection_rect:
            qp.setBrush(QtGui.QColor(2, 250, 250, 64))
            qp.drawRect(self.selection_rect)

        qp.end()

    def add_point(self, x, y):
        self.current_paint_object.add_point(x, y)
        self.update()

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

    def undo_drawing(self):
        if len(self.paint_objects) != 0:
            self.stack.undo()
            self.update()

    def redo_drawing(self):
        self.stack.redo()
        self.update()

    def increase_pen_size(self):
        self.active_size += 1

    def decrease_pen_size(self):
        if self.active_size > 1:
            self.active_size -= 1

from PyQt5 import QtWidgets


class UndoHandler(QtWidgets.QUndoCommand):
    """
    Created by Marco Peisker
    """

    def __init__(self, paint_objects):
        super().__init__()
        self.paint_objects = paint_objects
        self.deleted_obj = None

    def undo(self):
        self.deleted_obj = self.paint_objects[-1]
        self.paint_objects.pop()

    def redo(self):
        if self.deleted_obj is not None:
            self.paint_objects.append(self.deleted_obj)

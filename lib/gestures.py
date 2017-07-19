import json
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from sklearn import svm

import wiimote
import sys

from scipy import fft

"""
json file used for library of gestures so no initial learning of gestures has to be done

"""


class WiimoteNode(Node):
    """
    Outputs sensor data from a Wiimote.

    Supported sensors: accelerometer (3 axis)
    Text input box allows for setting a Bluetooth MAC address.
    Pressing the "connect" button tries connecting to the Wiimote.
    Update rate can be changed via a spinbox widget. Setting it to "0"
    activates callbacks every time a new sensor value arrives (which is
    quite often -> performance hit)
    """

    nodeName = "Wiimote"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='out'),
            'accelY': dict(io='out'),
            'accelZ': dict(io='out'),
        }
        self.wiimote = None
        self._acc_vals = []

        # update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        # super()
        Node.__init__(self, name, terminals=terminals)

    def update_all_sensors(self):
        if self.wiimote is None:
            return
        self._acc_vals = self.wiimote.accelerometer
        # todo: other sensors...
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
        self.update()

    # def ctrlWidget(self):
    #     return self.ui

    def connect_wiimote(self, btaddr, model=None):
        # self.btaddr = str(self.text.text()).strip()
        if self.wiimote is not None:
            self.wiimote.disconnect()
            self.wiimote = None
            # self.connect_button.setText("connect")
            return
        if len(btaddr) == 17:
            # self.connect_button.setText("connecting...")
            if model:
                self.wiimote = wiimote.connect(btaddr, model)
            else:
                self.wiimote = wiimote.connect(btaddr)
            if self.wiimote is None:
                self.connect_button.setText("try again")
            else:
                # self.connect_button.setText("disconnect")
                # self.set_update_rate(self.update_rate_input.value())

                # setting rate of samples
                self.set_update_rate(60)

    def set_update_rate(self, rate):
        if rate == 0:  # use callbacks for max. update rate
            self.update_timer.stop()
            self.wiimote.accelerometer.register_callback(self.update_accel)
        else:
            self.wiimote.accelerometer.unregister_callback(self.update_accel)
            self.update_timer.start(1000.0 / rate)

    def process(self, **kwdargs):
        x, y, z = self._acc_vals
        return {'accelX': np.array([x]), 'accelY': np.array([y]), 'accelZ': np.array([z])}


fclib.registerNodeType(WiimoteNode, [('Sensor',)])


class FftNode(Node):
    """
    implement an FftNode that reads in information from a BufferNode and outputs a frequency spectrogram.
    """

    nodeName = 'Fft'

    def __init__(self, name):
        terminals = {
            'inX': dict(io='in'),
            'inY': dict(io='in'),
            'inZ': dict(io='in'),
            'fft': dict(io='out')
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        x = kwds['inX']
        y = kwds['inY']
        z = kwds['inZ']

        avg = (x + y + z) / 3

        freq = [np.abs(fft(avg) / len(avg))[1:len(avg) // 2]]

        return {'fft': freq}


fclib.registerNodeType(FftNode, [('Custom',)])


class SvmNode(Node):
    """
    Support Vector Machine that can be switched between training mode and recognition mode via buttons in the UI and
    on the WiiMote.
    In training mode it continually reads in a date from the accelerometer.
    When starting recognition mode the SVM is getting trained with all saved data.
    While in recognition Mode the data is getting saved and then handed to the SVM for a prediction.
    """

    nodeName = 'Svm'

    def __init__(self, name):
        terminals = {
            'inX': dict(io='in'),
            'inY': dict(io='in'),
            'inZ': dict(io='in'),
            'gesture': dict(io='out')
        }

        self.training_mode = False
        self.recognition_mode = False

        self.cutoff_length = 0

        self.saved_gestures = {}
        self.current_recording = []

        self.category_to_gesture = {}

        self.classifier = svm.SVC()

        Node.__init__(self, name, terminals=terminals)

    def set_training_mode(self, value):
        # catch some wrong paramaters
        if value is True:
            self.current_recording = []
            self.training_mode = True
        else:
            self.training_mode = False

    def add_gesture(self, name):
        print("Saved Gesture with name: %s" % name)
        self.saved_gestures[name] = self.current_recording

    def set_recognition_mode(self, value):
        # catch some wrong paramaters
        if value is True:
            self.svm_train_classifier()
            self.current_recording = []
            self.recognition_mode = True
        else:
            self.recognition_mode = False
            prediction = self.svm_classification()
            if prediction:
                prediction = self.category_to_gesture[prediction[0]]
            print("Prediction is: ", prediction)
            return prediction

    def svm_train_classifier(self):
        """
        Here all saved gestures are handed into a Fast Fourier Transformation to extract the present frequency spectrum.
        After that the data normalized to the length of the gesture with the fewest samples
        Finally the frequency data is handed to the SVM for training.
        """

        # needed because a SVM needs more than 1 class
        if len(self.saved_gestures.keys()) <= 1:
            print("Not enough gestures!")
        else:
            training_data = []
            categories = []
            id = 0

            for gesture, value in self.saved_gestures.items():
                id += 1
                # needed to map the id returned from the SVM to a name of a gesture
                self.category_to_gesture[id] = gesture
                categories.append(id)

                x = []
                y = []
                z = []
                for elem in value:
                    x.append(elem[0][0])
                    y.append(elem[1][0])
                    z.append(elem[2][0])

                training_data.append(self.get_fft(x, y, z))

            # normalized length of fft
            self.cutoff_length = min([len(l) for l in training_data])

            normalized_fft = []
            for l in training_data:
                normalized_fft.append(l[:self.cutoff_length])

            training_data = normalized_fft

            self.classifier.fit(training_data, categories)

    def svm_classification(self):
        """
        Here the date from the recognition is handed into a Fast Fourier Transformation.
        After that it is normalized to the number of samples from the shortest gesture.
        This step is needed because a constraint of a SVM is that the length of the feature vectors and the vector for
        the prediction need to be the same.
        """

        if len(self.saved_gestures.keys()) <= 1:
            print("Not enough gestures!")
            return None
        else:
            x = []
            y = []
            z = []
            for elem in self.current_recording:
                x.append(elem[0][0])
                y.append(elem[1][0])
                z.append(elem[2][0])

            gesture_fft = self.get_fft(x, y, z)

            if len(gesture_fft) > self.cutoff_length:
                print("bigger than cutoff")
                gesture_fft = gesture_fft[:self.cutoff_length]
            elif len(gesture_fft) < self.cutoff_length:

                print("smaller than cutoff")
                temp = np.zeros(self.cutoff_length)
                for x in range(len(gesture_fft)):
                    temp[x] = gesture_fft[x]
                gesture_fft = temp
            else:
                pass

            return self.classifier.predict(gesture_fft)

    def get_fft(self, x, y, z):
        """
        Here the avarage of the x, y, z data from the accelerometer is handed into the Fast Fourier Transformation.
        """
        avg = (np.array(x) + np.array(y) + np.array(z)) / 3
        return np.abs(fft(avg) / len(avg))[1:len(avg) // 2]

    def process(self, **kwds):
        x = kwds['inX']
        y = kwds['inY']
        z = kwds['inZ']

        # appending data to the current recording if we are in training or recognition mode
        if self.training_mode:
            self.current_recording.append((x, y, z))
        elif self.recognition_mode:
            self.current_recording.append((x, y, z))
        else:
            # do not append samples if we are not in training or recognition mode
            pass
        return None


fclib.registerNodeType(SvmNode, [('Custom',)])


class ActivityRecognition():
    RED = QtGui.QColor(255, 0, 0)
    GREEN = QtGui.QColor(0, 255, 0)
    YELLOW = QtGui.QColor(255, 255, 0)
    GRAY = QtGui.QColor(100, 100, 100)
    BLACK = QtGui.QColor(0, 0, 0)

    def __init__(self, app):
        self.app = app

        self.training_mode = False
        self.recognition_mode = False

        self.init_ui()
        self.setup_nodes()
        self.connect_buttons()

        self.win.show()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def init_ui(self):
        width, height = self.app.desktop().width(), self.app.desktop().height()

        self.win = QtGui.QWidget()
        self.win.setWindowTitle('Activity Recognition')
        self.win.setGeometry(width / 4, height / 4, width / 2, height / 2)

        self.main_layout = QtGui.QGridLayout()
        self.win.setLayout(self.main_layout)

        self.setup_left_group()
        # self.setup_middle_group()
        self.setup_right_group()

    def setup_left_group(self):
        left_group = QtGui.QGroupBox()
        left_layout = QtGui.QGridLayout()

        wm_label = QtGui.QLabel("Enter your mac address")
        self.wm_addr = QtGui.QLineEdit()
        self.wm_addr.setPlaceholderText("Enter your mac address here")
        self.wm_addr.setText("B8:AE:6E:1B:5B:03")
        self.wm_connect_btn = QtGui.QPushButton("Connect")

        left_layout.addWidget(wm_label, 1, 1, 1, 2)
        left_layout.addWidget(self.wm_addr, 2, 1, 1, 2)
        left_layout.addWidget(self.wm_connect_btn, 3, 1, 1, 2)

        self.training_hint = QtGui.QLabel("You can toggle Training Mode by pressing 'A' on your WiiMote!\n" +
                                          "To activate recognition mode HOLD down the 'B' button!")

        self.training_label = QtGui.QLabel("NO WIIMOTE CONNECTED")
        self.training_label.setAlignment(QtCore.Qt.AlignCenter)
        self.training_label.setAutoFillBackground(True)
        self.training_btn = QtGui.QPushButton("Activate Training Mode")

        left_layout.addWidget(self.training_hint, 4, 1, 1, 2)
        left_layout.addWidget(self.training_label, 5, 1, 1, 2)
        left_layout.addWidget(self.training_btn, 6, 1, 1, 2)

        self.save_label = QtGui.QLabel("Enter a name for your gesture:")
        self.save_label.setAlignment(QtCore.Qt.AlignCenter)
        self.save_text = QtGui.QLineEdit()
        self.save_text.setPlaceholderText("Enter Gesture Name")
        self.save_btn = QtGui.QPushButton("Save Gesture")

        left_layout.addWidget(self.save_label, 7, 1, 1, 2)
        left_layout.addWidget(self.save_text, 8, 1, 1, 2)
        left_layout.addWidget(self.save_btn, 9, 1, 1, 2)

        left_group.setLayout(left_layout)
        self.main_layout.addWidget(left_group, 1, 1, 1, 1)

    def setup_middle_group(self):
        middle_group = QtGui.QGroupBox()
        middle_layout = QtGui.QGridLayout()

        l1 = QtGui.QLabel()
        l1.setText("MIDDLE GROUP")
        middle_layout.addWidget(l1, 1, 1)

        self.spectrogram_widget = pg.PlotWidget()
        self.spectrogram_widget.setYRange(0, 128)
        middle_layout.addWidget(self.spectrogram_widget, 2, 1)

        middle_group.setLayout(middle_layout)
        self.main_layout.addWidget(middle_group, 1, 2, 1, 5)

    def setup_right_group(self):
        right_group = QtGui.QGroupBox()
        right_layout = QtGui.QGridLayout()

        self.connected_status_label = QtGui.QLabel()
        self.connected_status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.connected_status_label.setAutoFillBackground(True)

        connected_status_palette = self.connected_status_label.palette()
        connected_status_palette.setColor(self.connected_status_label.backgroundRole(), self.RED)
        connected_status_palette.setColor(self.connected_status_label.foregroundRole(), self.BLACK)
        self.connected_status_label.setPalette(connected_status_palette)

        self.connected_status_label.setText("NOT CONNECTED")
        right_layout.addWidget(self.connected_status_label, 1, 1)

        self.recording_status_label = QtGui.QLabel()
        self.recording_status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.recording_status_label.setAutoFillBackground(True)

        recording_status_palette = self.recording_status_label.palette()
        recording_status_palette.setColor(self.recording_status_label.backgroundRole(), self.RED)
        recording_status_palette.setColor(self.recording_status_label.foregroundRole(), self.BLACK)
        self.recording_status_label.setPalette(recording_status_palette)

        self.recording_status_label.setText("Not Recording")
        right_layout.addWidget(self.recording_status_label, 2, 1)

        self.recognized_gesture_heading = QtGui.QLabel("Recognized Gesture:")
        self.recognized_gesture = QtGui.QLabel("UNKNOWN GESTURE")

        right_layout.addWidget(self.recognized_gesture_heading, 3, 1, 1, 1)
        right_layout.addWidget(self.recognized_gesture, 4, 1, 1, 1)

        self.known_gestures = QtGui.QLabel()
        self.known_gestures.setText("Saved Gestures:\n")
        right_layout.addWidget(self.known_gestures, 5, 1, 3, 1)

        right_group.setLayout(right_layout)
        self.main_layout.addWidget(right_group, 1, 7, 1, 1)

    def setup_nodes(self):
        # Create an empty flowchart with a single input and output
        self.fc = Flowchart(terminals={})

        self.wiimote_node = self.fc.createNode('Wiimote')
        self.fft_node = self.fc.createNode('Fft')
        self.svm_node = self.fc.createNode('Svm')

        self.fc.connectTerminals(self.wiimote_node['accelX'], self.svm_node['inX'])
        self.fc.connectTerminals(self.wiimote_node['accelY'], self.svm_node['inY'])
        self.fc.connectTerminals(self.wiimote_node['accelZ'], self.svm_node['inZ'])

    def connect_buttons(self):
        # self.training_btn.clicked.connect(self.toggle_training_mode)
        self.wm_connect_btn.clicked.connect(self.connect_wm)
        self.save_btn.clicked.connect(self.save_gesture)

    def save_gesture(self):
        name = self.save_text.text().strip()
        print(len(name))
        if len(name) == 0:
            name = "Unknown Name"

        self.known_gestures.setText(self.known_gestures.text() + "\n" + name)
        self.svm_node.add_gesture(name)

        self.save_text.setText("")

    def connect_wm(self):
        btaddr = self.wm_addr.text().strip()
        print(btaddr)
        self.wiimote_node.connect_wiimote(btaddr, model='Nintendo RVL-CNT-01-TR')

        self.training_label.setText("Training Mode OFF")
        self.connected_status_label.setText("CONNECTED")
        connected_status_palette = self.connected_status_label.palette()
        connected_status_palette.setColor(self.connected_status_label.backgroundRole(), self.GREEN)
        connected_status_palette.setColor(self.connected_status_label.foregroundRole(), self.BLACK)
        self.connected_status_label.setPalette(connected_status_palette)

        self.wiimote_node.wiimote.buttons.register_callback(self.handle_wm_button)

    def handle_wm_button(self, buttons):
        if len(buttons) > 0:
            for button in buttons:
                # if button[0] == 'A':
                    # if button[1]:
                        # self.toggle_training_mode()
                if button[0] == 'B':
                    if button[1]:
                        self.start_recognition_mode()
                    else:
                        self.stop_recognition_mode()

    def toggle_training_mode(self):
        self.training_mode = not self.training_mode
        print('New State (Training Mode): ', self.training_mode)
        if self.training_mode:
            self.svm_node.set_training_mode(True)
            self.training_btn.setText("Deactivate Training Mode")
            self.training_label.setText("Training Mode ON")
            training_status_palette = self.training_label.palette()
            training_status_palette.setColor(self.training_label.backgroundRole(), self.YELLOW)
            training_status_palette.setColor(self.training_label.foregroundRole(), self.BLACK)
            self.training_label.setPalette(training_status_palette)

            self.recording_status_label.setText("Recording Training Data")
            p = self.recording_status_label.palette()
            p.setColor(self.recording_status_label.backgroundRole(), self.YELLOW)
            self.recording_status_label.setPalette(p)
        else:
            self.svm_node.set_training_mode(False)
            self.training_btn.setText("Activate Training Mode")
            self.training_label.setText("Training Mode OFF")
            training_status_palette = self.training_label.palette()
            training_status_palette.setColor(self.training_label.backgroundRole(), self.GRAY)
            self.training_label.setPalette(training_status_palette)

            self.recording_status_label.setText("Not Recording")
            p = self.recording_status_label.palette()
            p.setColor(self.recording_status_label.backgroundRole(), self.RED)
            p.setColor(self.recording_status_label.foregroundRole(), self.BLACK)
            self.recording_status_label.setPalette(p)

    def start_recognition_mode(self):
        print("Start recognition Mode")
        self.recognized_gesture.setText("UNKNOWN")
        self.svm_node.set_recognition_mode(True)
        self.recording_status_label.setText("Recording Recognition Data")
        p = self.recording_status_label.palette()
        p.setColor(self.recording_status_label.backgroundRole(), self.YELLOW)
        self.recording_status_label.setPalette(p)

    def stop_recognition_mode(self):
        print("Stop recognition Mode")
        gesture = self.svm_node.set_recognition_mode(False)
        if gesture:
            self.recognized_gesture.setText(gesture)
            p = self.recognized_gesture.palette()
            p.setColor(self.recognized_gesture.backgroundRole(), self.GREEN)
            self.recognized_gesture.setPalette(p)

        else:
            self.recognized_gesture.setText("Not enough gestures! Save another one!")
            p = self.recognized_gesture.palette()
            p.setColor(self.recognized_gesture.backgroundRole(), self.RED)
            self.recognized_gesture.setPalette(p)

        self.recording_status_label.setText("Not Recording")
        p = self.recording_status_label.palette()
        p.setColor(self.recording_status_label.backgroundRole(), self.RED)
        self.recording_status_label.setPalette(p)


def main():
    app = QtGui.QApplication([])

    activity_recognition = ActivityRecognition(app)


if __name__ == '__main__':
    main()

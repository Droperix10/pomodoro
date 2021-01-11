from main_window_ui import Ui_MainWindow
from configparser import ConfigParser
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import settings_window_ui
import sys
from PyQt5 import QtMultimedia


class SettingsWindow(QtWidgets.QMainWindow):
    submitted = QtCore.pyqtSignal([str, str, str])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = settings_window_ui.Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.show()

        self.setWindowTitle("Settings")
        self.load_settings()
        self.ui.pushButton.clicked.connect(self.save_settings)

    def load_settings(self):
        config = ConfigParser()
        config.read("config.ini")

        self.ui.pomodoro_length.setText(config.get('main', 'study time'))
        self.ui.short_break_length.setText(config.get('main', 'short break'))
        self.ui.long_break_length.setText(config.get('main', 'long break'))

    def save_settings(self):
        config = ConfigParser()
        config.read("config.ini")
        config.set("main", "study time", self.ui.pomodoro_length.text())
        config.set("main", "short break", self.ui.short_break_length.text())
        config.set("main", "long break", self.ui.long_break_length.text())
        with open('config.ini', 'w') as f:
            config.write(f)

        self.submitted.emit(self.ui.pomodoro_length.text(),
                            self.ui.short_break_length.text(),
                            self.ui.long_break_length.text())
        self.close()


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Pomodoro")
        # all time here in seconds, in comments are default values
        self.study_time = 1500  # 1500 is 25 minutes
        self.short_break_time = 300  # 300 is 5 minutes
        self.long_break_time = 900  # 900 is 15 minutes
        self.remaining_seconds = self.study_time

        self.beep_noise = "bugle_tune.wav"  # sound played
        self.last_countdown = ""
        self.studies_today = 1
        self.last_countdown = "study"

        self.setup_settings()
        self.ui.button.clicked.connect(self.start_timer)
        self.ui.actionSettings.triggered.connect(self.open_settings_window)

    def change_times(self, study_time, short_break_time, long_break_time):
        self.study_time = int(study_time)
        self.short_break_time = int(short_break_time)
        self.long_break_time = int(long_break_time)

    def open_settings_window(self):
        self.settings_dialog = SettingsWindow()
        self.settings_dialog.submitted.connect(self.change_times)

    def setup_settings(self):
        config = ConfigParser()
        try:
            config.read("config.ini")
            self.study_time = int(config.get('main', 'study time'))
            self.short_break_time = int(config.get('main', 'short break'))
            self.long_break_time = int(config.get('main', 'long break'))
            self.remaining_seconds = int(config.get("main", 'study time'))

        except:
            config.read("config.ini")
            config.add_section("main")
            config.set("main", "study time", "1500")
            config.set("main", "short break", "300")
            config.set("main", "long break", "900")
            with open('config.ini', 'w') as f:
                config.write(f)

    def start_timer(self):

        self.ui.button.setText("Pause")
        self.ui.button.clicked.connect(self.pause_timer)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.countdown)
        self.timer.start(1000)

    def pause_timer(self):
        self.timer.stop()

        self.ui.button.setText("Resume")
        self.ui.button.clicked.connect(self.start_timer)

    def countdown(self):
        if self.remaining_seconds == 0:
            self.timer.stop()
            self.ui.timer_display.setText("00:00")

            self.ui.button.setText("Start")
            self.ui.button.clicked.connect(self.start_timer)
            self.remaining_seconds = self.study_time

            if self.last_countdown == "study":
                if self.studies_today % 4 == 0:
                    self.remaining_seconds = self.long_break_time
                else:
                    self.remaining_seconds = self.short_break_time
                self.last_countdown = "break"
                self.studies_today += 1
                self.ui.times_studied.setText(
                    f"🍅 {self.studies_today - 1} times today")

                QtMultimedia.QSound.play(self.beep_noise)

            elif self.last_countdown == "break":
                self.remaining_seconds = self.study_time
                self.last_countdown = "study"

                QtMultimedia.QSound.play(self.beep_noise)


        else:
            # countdown from 25 minutes to 0
            minutes = int(
                (self.remaining_seconds - (self.remaining_seconds % 60)) / 60)

            # displaying 0 minutes as 00:00 not as 0:00
            if minutes == 0:
                minutes = "00"
            else:
                minutes = str(minutes)

            seconds = self.remaining_seconds % 60

            # displaying 0 seconds as 00:00 not as 00:0
            if seconds == 0:
                seconds = "00"
            else:
                seconds = str(seconds)

            if len(minutes) == 1:
                minutes = "0" + minutes
            if len(seconds) == 1:
                seconds = "0" + seconds

            self.ui.timer_display.setText(f"{minutes}:{seconds}")
            self.remaining_seconds -= 1


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QtWidgets.QApplication([])

    widget = MainApp()
    widget.show()

    app.exec_()

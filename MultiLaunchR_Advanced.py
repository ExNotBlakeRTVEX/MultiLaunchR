import os
import sys
import subprocess
import tempfile
import shutil
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QFileDialog, QSpinBox, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer

class MultiLaunchR(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MultiLaunchR - Advanced Instance Launcher")
        self.setFixedSize(500, 350)
        self.processes = []

        layout = QVBoxLayout()

        # Executable Input
        self.path_label = QLabel("Executable Path:")
        layout.addWidget(self.path_label)

        self.path_input = QLineEdit()
        layout.addWidget(self.path_input)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_exe)
        layout.addWidget(browse_button)

        # Instance Count
        self.instance_label = QLabel("Number of Instances:")
        layout.addWidget(self.instance_label)

        self.instance_spinbox = QSpinBox()
        self.instance_spinbox.setMinimum(1)
        self.instance_spinbox.setMaximum(100)
        layout.addWidget(self.instance_spinbox)

        # Option: Use fake profiles
        self.profile_checkbox = QCheckBox("Use fake user profiles (for Chrome, Discord, etc.)")
        layout.addWidget(self.profile_checkbox)

        # Option: Use Sandboxie
        self.sandboxie_checkbox = QCheckBox("Use Sandboxie (must be installed)")
        layout.addWidget(self.sandboxie_checkbox)

        # Option: Auto-kill and relaunch
        relaunch_layout = QHBoxLayout()
        self.autokill_checkbox = QCheckBox("Auto-close after (sec):")
        relaunch_layout.addWidget(self.autokill_checkbox)

        self.kill_time = QSpinBox()
        self.kill_time.setMinimum(1)
        self.kill_time.setMaximum(9999)
        relaunch_layout.addWidget(self.kill_time)

        layout.addLayout(relaunch_layout)

        self.relaunch_checkbox = QCheckBox("Auto-relaunch every (sec):")
        layout.addWidget(self.relaunch_checkbox)

        self.relaunch_time = QSpinBox()
        self.relaunch_time.setMinimum(1)
        self.relaunch_time.setMaximum(9999)
        layout.addWidget(self.relaunch_time)

        # Launch Button
        launch_button = QPushButton("Launch Instances")
        launch_button.clicked.connect(self.launch_instances)
        layout.addWidget(launch_button)

        self.setLayout(layout)

        self.relaunch_timer = QTimer()
        self.relaunch_timer.timeout.connect(self.relaunch_instances)

    def browse_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Executable")
        if path:
            self.path_input.setText(path)

    def launch_instances(self):
        exe_path = self.path_input.text()
        instance_count = self.instance_spinbox.value()

        if not exe_path or not os.path.exists(exe_path):
            self.path_label.setText("Executable Path: (Invalid file!)")
            self.path_label.setStyleSheet("color: red;")
            return

        self.kill_all_instances()

        for i in range(instance_count):
            if self.profile_checkbox.isChecked():
                # Create temp user profile folder
                profile_dir = tempfile.mkdtemp(prefix=f"userprofile_{i}_")
                cmd = [exe_path, f'--user-data-dir={profile_dir}']
            else:
                cmd = [exe_path]

            if self.sandboxie_checkbox.isChecked():
                # Sandboxie integration (SbieCtrl required)
                cmd = ["C:\\Program Files\\Sandboxie-Plus\\Start.exe", "/box:DefaultBox"] + cmd

            try:
                proc = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.processes.append((proc, cmd))
            except Exception as e:
                self.path_label.setText(f"Error: {e}")
                self.path_label.setStyleSheet("color: red;")
                break

        # Auto-close timer
        if self.autokill_checkbox.isChecked():
            QTimer.singleShot(self.kill_time.value() * 1000, self.kill_all_instances)

        # Auto-relaunch timer
        if self.relaunch_checkbox.isChecked():
            self.relaunch_timer.start(self.relaunch_time.value() * 1000)

    def kill_all_instances(self):
        for proc, _ in self.processes:
            if proc.poll() is None:
                try:
                    proc.kill()
                except:
                    pass
        self.processes.clear()

    def relaunch_instances(self):
        print("[*] Relaunching...")
        self.launch_instances()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MultiLaunchR()
    window.show()
    sys.exit(app.exec())

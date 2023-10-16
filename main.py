import subprocess
import sys
import pkg_resources
import json

REQUIRED_PACKAGES = [
    'requests',
    'PyQt5',
    'gitpython',
]

def install_missing_packages():
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    for package in REQUIRED_PACKAGES:
        if package not in installed_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)

install_missing_packages()


from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QSpacerItem,QSizePolicy, QLineEdit, QVBoxLayout,QGridLayout, QPushButton, QDialog, QFormLayout, QDialogButtonBox,QHBoxLayout
from PyQt5.QtGui import QPixmap,QPalette # Import QPixmap for handling images
from PyQt5.QtCore import Qt  # Import QPixmap for handling images
import requests
from git import Repo



class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        
        self.setWindowTitle("Authentication Required")
        self.setStyleSheet("background-color: #0e1425;")  # Set the background color here
        
                # Create a QLabel for the text
        text_label = QLabel("CodeLock®")
        text_label.setStyleSheet("color: white;font-weight: bold; font-size: 20px;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        # Create a layout for the image
        text_layout = QVBoxLayout()
        text_layout.addWidget(text_label)

        self.username_line_edit = QLineEdit()
        self.password_line_edit = QLineEdit()
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.company_line_edit = QLineEdit()

        self.username_line_edit.setStyleSheet("background-color: #222d4b;")
        self.password_line_edit.setStyleSheet("background-color: #222d4b;")
        self.company_line_edit.setStyleSheet("background-color: #222d4b;")


        self.logo_label = QLabel(self)
        self.pixmap = QPixmap("codelocklogo.png")
        self.logo_label.setPixmap(self.pixmap)
        self.logo_label.setScaledContents(True)  # Ensure the image scales properly
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image
        self.logo_label.setFixedSize(100, 100)  # Adjust the size as needed

        layout = QGridLayout()
        layout.addWidget(self.logo_label, 2, 0, 1, 1)  # Image in row 0, column 0
        layout.addLayout(text_layout,2 , 1, 1, 1)  # Text layout in row 1, column 0

       
        form_layout = QFormLayout()
        
        # Create labels for form elements
        company_label = QLabel("Company ID:")
        email_label = QLabel("Email:")
        password_label = QLabel("Password:")

        # Set the text color to white for the labels using style sheets
        company_label.setStyleSheet("color: white;")
        email_label.setStyleSheet("color: white;")
        password_label.setStyleSheet("color: white;")

        form_layout = QFormLayout()

        # Add form elements to the layout
        
        form_layout.addRow(company_label, self.company_line_edit)
        form_layout.addRow(email_label, self.username_line_edit)
        form_layout.addRow(password_label, self.password_line_edit)     
        
        palette = self.password_line_edit.palette()
        palette.setColor(QPalette.Text, Qt.white)
        self.password_line_edit.setPalette(palette)

        palette = self.username_line_edit.palette()
        palette.setColor(QPalette.Text, Qt.white)
        self.username_line_edit.setPalette(palette)

        palette = self.company_line_edit.palette()
        palette.setColor(QPalette.Text, Qt.white)
        self.company_line_edit.setPalette(palette)
        

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Get the individual buttons within the button box
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)

        # Set the background color for each button
        ok_button.setStyleSheet("background-color: #3898ec;")  # Change 'blue' to your desired color
        cancel_button.setStyleSheet("background-color: #3898ec;")  # Change 'red' to your desired color


        # Set text color to white for the buttons
        self.button_box.setStyleSheet("color: white;")

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)  # Add the grid layout with the image and text layout
        main_layout.addWidget(self.logo_label)  # Add the logo label to the top
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)
        
        

        self.setLayout(main_layout)
        self.resize(315, 250)

    def get_credentials(self):
        return self.username_line_edit.text(), self.password_line_edit.text(), self.company_line_edit.text()

class OTPDialog(QDialog):
    def __init__(self, parent=None):
        super(OTPDialog, self).__init__(parent)
        print("OTPDialog init")
        self.setWindowTitle("Enter One Time Password")


        self.otp_line_edit = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("OTP:", self.otp_line_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_otp(self):
        return self.otp_line_edit.text()

def main():
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        username, password, company_id= login_dialog.get_credentials()
        
        repo = Repo('.', search_parent_directories=True)
        repo_url = repo.remotes.origin.url
        post_params = {
            "accountId": company_id,
            "email": username,
            "password": password,
            "repository_id": repo_url,
        }

        response = requests.post('https://api.codelock.ai/api/v1/verify-hook', json=post_params)
        response_data = ""
        if response.status_code == 200:
            response_data = response.json()
        else:
            print(f"Request failed with status {response.status_code}.")

        if 'user_id' not in response_data:
            print("Authentication failed!")
            sys.exit(1)
        
        if response_data.get('requireOTP', True):
            otp_dialog = OTPDialog()
            if otp_dialog.exec() == QDialog.Accepted:
                otp = otp_dialog.get_otp()
                print("OTP: ", otp)
                otp_json = {
                    "email": username,
                    "otp": otp,
                    "repository_id": repo_url
                }
                otp_response = requests.post('https://api.codelock.ai/api/v1/verify-hook-otp', json=otp_json)
                otp_response_data = otp_response.json()
                if otp_response_data.get('code', 1) != 0:
                    print("Incorrect OTP!")
                    sys.exit(1)
        print("Authentication successful!")

    user_id = response_data.get("user_id")


    branch = subprocess.check_output(['git', 'symbolic-ref', '--short', 'HEAD']).decode('utf-8').strip()


    repo_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode('utf-8').strip()

    local_sha = sys.argv[1]

    hook_trigger_payload = {
        "user_id": user_id,
        "branch": branch,
        "repository_id": repo_url,
        "commit_id": local_sha
    }


    hook_trigger_response = requests.post('https://api.codelock.ai/api/v1/trigger-git-hook', json=hook_trigger_payload)

    if hook_trigger_response.status_code != 200:
        print(f"Error triggering git hook: {hook_trigger_response.text}")
        return 1

 
    return 0
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


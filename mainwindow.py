# This Python file uses the following encoding: utf-8
from datetime import datetime
import sys
import pandas as pd

#from PyQt5.uic.properties import QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow,  QPushButton, QFileDialog, QTableWidgetItem

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_parserGUI_3 import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.printAll = False
        self.printSellected = False

        self.ui.pushButton.clicked.connect(self.tableBuilder)

    def timeDif(self, use_out, use_in):
        # Find difference and return value
        delta = use_in - use_out
        return str(delta)


    # To be implemented in future versions
    def getUser(self):
        return None


    def getStart(self):
        temp = self.ui.dateEdit.date()
        start_date = temp.toPython().strftime('%b %d %Y %H:%M:%S')
        return start_date


    def getStop(self):
        temp = self.ui.dateEdit_2.date()
        end_date = temp.toPython().strftime('%b %d %Y %H:%M:%S')
        return end_date


    def screenData(self, line, last_date):
        if 'Time:' in line:
            ### Info for database.csv ###
            # Get date and time
            last_date = line.strip().split('Time: ', 1)[1].split(' PDT')[0]
            last_date_stamp = datetime.strptime(last_date, '%a %b %d %Y %H:%M:%S')
            last_date = last_date_stamp.strftime('%b %d %Y')
            # Get license type
            lic_type = (line.strip().split('Time:')[0].split(' ', 1)[1]).split(' ')[0]
            return 'Time:', last_date_stamp, lic_type, last_date
        elif 'OUT:' in line:
            ### Info for database.csv ###
            # Get time
            last_out = datetime.strptime(line.strip().split('OUT: ')[0].split(' ')[0], '%H:%M:%S').time()
            # Get date
            date_out = datetime.strptime(last_date, '%b %d %Y').date()
            last_out_stamp = datetime.combine(date_out, last_out)
            # Get license type
            lic_type = (line.strip().split('OUT:')[0].split(' ', 1)[1]).split(' ')[0]
            return 'OUT:', last_out_stamp, lic_type, last_date
        elif 'IN:' in line:
            ### Info for database.csv ###
            # Get time
            last_in = datetime.strptime(line.strip().split('IN: ')[0].split(' ')[0], '%H:%M:%S').time()
            # Get date
            date_in = datetime.strptime(last_date, '%b %d %Y').date()
            last_in_stamp = datetime.combine(date_in, last_in)
            # Get license type
            lic_type = (line.strip().split('IN:')[0].split(' ', 1)[1]).split(' ')[0]
            return 'IN:', last_in_stamp, lic_type, last_date
        else:
            return 'None', 'None', 'None', last_date


    def getFileDir(self):
        return None

    def lineParser(self, Lines):

        lic_type = ""
        last_date = datetime.now().strftime('%b %d %Y')
        last_out_stamp = datetime.now().strftime('%b %d %Y')
        last_in_stamp = datetime.now().strftime('%b %d %Y')
        lic_inst = []
        for line in Lines:
            data_kind, data, lic, last_date = self.screenData(line, last_date)
            if data_kind == 'Time:':
                lic_type = lic
            elif data_kind == 'OUT:':
                last_out_stamp = data
            elif data_kind == 'IN:':
                last_in_stamp = data
                ######################
                # Get total time out
                delta_time = self.timeDif(last_out_stamp, last_in_stamp)
                lic_inst.append([lic_type, last_out_stamp.strftime('%a %b %d %Y %H:%M:%S'), last_in_stamp.strftime('%a %b %d %Y %H:%M:%S'), delta_time])
        return lic_inst

    def tableBuilder(self):
        filepath = QFileDialog.getOpenFileName(self, caption='Open file', dir='.')[0]
        file = open(filepath)
        Lines = file.readlines()
        file.close()
        lic_inst = self.lineParser(Lines)

        df_db = pd.DataFrame(lic_inst, columns=['License Type', 'Start Time', 'End Time', 'Delta Time'])
        if self.ui.radioButton.isChecked():
            df_db.to_csv(datetime.now().strftime('%H_%M_%S') + '_database.csv', sep='\t', encoding='utf-8', index=False)
        df_db['Start Time'] = pd.to_datetime(df_db['Start Time'])
        df_db['End Time'] = pd.to_datetime(df_db['End Time'])
        start_date = self.getStart()
        end_date = self.getStop()
        mask = (df_db['Start Time'] >= start_date)
        df_sel = df_db.loc[mask]
        mask = (df_sel['End Time'] <= end_date)
        df_pres = df_sel.loc[mask]
        if self.ui.radioButton_2.isChecked():
            df_sel.to_csv(datetime.now().strftime('%H_%M_%S') + '__from_' + str(start_date) + '_until_' + str(end_date)
                          + '_database.csv', sep='\t', encoding='utf-8', index=False)


        df_pres = df_pres.reset_index()
        r = 0
        for index, row in df_pres.iterrows():
            rose = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rose)
            print(str(row))
            print(str(index))
            self.ui.tableWidget.setItem(rose, 0, QTableWidgetItem(str(row['License Type'])))
            self.ui.tableWidget.setItem(rose, 1, QTableWidgetItem(str(row['Start Time'])))
            self.ui.tableWidget.setItem(rose, 2, QTableWidgetItem(str(row['End Time'])))
            self.ui.tableWidget.setItem(rose, 3, QTableWidgetItem(str(row['Delta Time'])))
            r += 1
        return None


def main():
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

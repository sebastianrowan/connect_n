# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import random
import numpy as np
from classes import Player, GameButton, GameMode

# from PySide6.QtWidgets import QApplication, QDialog
# from PySide6.QtCore import QFile
# from PySide6.QtUiTools import QUiLoader

from PyQt6 import uic, QtWidgets
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import QRect

Form, Window = uic.loadUiType("board_dialog.ui")         

class BoardDialog(QtWidgets.QDialog, Form):
    def __init__(self, parent=None):
        super(BoardDialog, self).__init__(parent)
        self.setupUi(self)
        self.combo_box_mode.addItems(["Dice Roll", "Coin Toss"])
        self.generate_button.clicked.connect(self.generate_board)
        self.genValueButton.clicked.connect(self.take_turn)
        self.resetButton.clicked.connect(self.reset_board)
        self.passButton.clicked.connect(self.pass_turn)
        self.game_buttons = {}
        self.turn_active = False
        self.player_colors = { # Make this dynamic later
            'Player 1': "#ff5555",
            'Player 2': "#5555ff",
            'Match': "#55ff55",
            'No Match': "#999999"
        }
        
    def generate_board(self):
        for btn in self.game_buttons.values():
            try:
                btn.button.deleteLater()
            except:
                pass
        self.game_buttons = {}
        rows = self.spin_box_row.value()
        cols = self.spin_box_col.value()
        self.board_array = np.empty((rows, cols), dtype="<U10")
        size = int(min((700 / cols), (500 / rows)))
        
        if self.combo_box_mode.currentText() == "Coin Toss":
            self.mode = GameMode("Coin Toss", "Toss Coin", 1, 2)
        elif self.combo_box_mode.currentText() == "Dice Roll":
            self.mode = GameMode("Dice Roll", "Roll Dice", 2, 6)
        self.genValueButton.setText(self.mode.verb)    
        self.win_condition = 4 # get value from dialog later
        for i in range(rows):
            for j in range(cols):
                btn_name = f"button{i}_{j}"
                btn_value = self.mode.generate_button_value(0.2) # 20% chance of generating a free space
                x = int(20 + ((700 - (size * cols))/2) + (size * j))
                y = int(20 + (size * i))
                self.add_button(btn_name, btn_value, size, x, y, i, j)
        self.update_board()
        self.genValueButton.setEnabled(True)
             
    def reset_board(self):
        for btn in self.game_buttons.values():
            btn.status = "No Match"
        
        self.currentPlayerLabel.setText("Player 1")
        self.currentPlayerLabel.setStyleSheet(f"color:{self.player_colors['Player 1']}")
        self.passButton.setEnabled(False)
        self.turn_active = False
        self.genValueButton.setEnabled(True)
        self.update_board()
        
    def add_button(self, name, value, size, x, y, i, j):
        button = QPushButton(self)
        button.setText(str(value))
        button.setObjectName(name)
        button.setGeometry(QRect(x, y, size, size))
        button.clicked.connect(self.button_clicked)
        button.show()
        
        gbutton = GameButton(name, value, "No Match", button, i, j)
        self.game_buttons[name] = gbutton        
            
    def button_clicked(self):
        sending_button = self.sender()
        button_name = sending_button.objectName()
        game_button = self.game_buttons[button_name]
        
        if game_button.status == "Match":
            game_button.status = self.currentPlayerLabel.text()
            i = game_button.i
            j = game_button.j
            self.board_array[i,j] = self.currentPlayerLabel.text()
            
            for btn in self.game_buttons.values():
                if btn.status == "Match":
                    btn.status = "No Match"
        
            self.update_board()
            self.end_turn()
    
    def take_turn(self):
        val = self.mode.generate_value()
        self.valueLabel.setText(str(val))
        
        self.turn_active = True  
        self.genValueButton.setEnabled(False)
        current_player = self.currentPlayerLabel.text()
        
        for btn in self.game_buttons.values():
            if (btn.value == val or btn.value == "Free Space") and btn.status == "No Match":
                btn.status = "Match"
                
        count = 0
        for btn in self.game_buttons.values():
            if btn.status == "Match":
                count += 1
        if count == 0:
            self.passButton.setEnabled(True)
            
        self.update_board()
        
    def pass_turn(self):
        self.update_board()
        self.end_turn()
            
    def update_board(self):
        for btn in self.game_buttons.values():
            color = self.player_colors[btn.status]
            btn.button.setStyleSheet(f"background-color:{color}")

    def end_turn(self):
        current_player = self.currentPlayerLabel.text()
        win = self.check_win(current_player)
        if not win: # make this more dynamic
            if current_player == "Player 1":
                self.currentPlayerLabel.setText("Player 2")
                self.currentPlayerLabel.setStyleSheet(f"color:{self.player_colors['Player 2']}")
            else:
                self.currentPlayerLabel.setText("Player 1")
                self.currentPlayerLabel.setStyleSheet(f"color:{self.player_colors['Player 1']}")
            self.passButton.setEnabled(False)
            self.turn_active = False
            self.genValueButton.setEnabled(True)
        else:
            self.currentPlayerLabel.setText(f"{current_player} Wins!")
    
    def check_win(self, player):
        n_to_win = self.win_condition 
        h = self.check_horizontal(self.board_array, n_to_win, player)
        v = self.check_vertical(self.board_array, n_to_win, player)
        d = self.check_diagonal(self.board_array, n_to_win, player)
        w = h + v + d
        
        if w > 0:
            return True
        else:
            return False

    def check_horizontal(self, a, n_to_win, player):
        n = n_to_win - 1
        h = a[:,:(-1 * n):]
        hc = (h == player) * 1
        hc = hc * ((h == a[:,n::]) * 1)
        
        for i in range(n-1):
            s = (i + 1)
            e = (-1 * (n - (i + 1)))
            c = a[:,s:e:]
            hc = hc * ((h == c) * 1)
        
        return(np.sum(hc))
    
    def check_vertical(self, a, n_to_win, player):
        n = n_to_win - 1
        v = a[:(-1 * n):,:]
        vc = (v == player) * 1
        vc = vc * ((v == a[n::,:]) * 1)
        
        for i in range(n-1):
            s = (i + 1)
            e = (-1 * (n - (i + 1)))
            c = a[s:e:,:]
            vc = vc * ((v == c) * 1)
        
        return(np.sum(vc))
    
    def check_diagonal(self, a, n_to_win, player):
        n = n_to_win - 1
        d = a[:(-1 * n):,:(-1 * n):]
        dc = (d == player) * 1
        dc = dc * ((d == a[n::,n::]) * 1)
        
        for i in range(n-1):
            s = (i + 1)
            e = (-1 * (n - (i + 1)))
            c = a[s:e:,s:e:]
            dc = dc * ((d == c) * 1)
        
        return(np.sum(dc))
    
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = BoardDialog()
    widget.show()
    sys.exit(app.exec())

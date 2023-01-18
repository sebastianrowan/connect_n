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

Form, Window = uic.loadUiType("board_dialog.ui")         

class BoardDialog(QtWidgets.QDialog, Form):
    def __init__(cls, parent=None):
        super(BoardDialog, cls).__init__(parent)
        cls.setupUi(cls)
        cls.combo_box_mode.addItems(["Dice Roll", "Coin Toss"])
        cls.generate_button.clicked.connect(cls.generate_board)
        cls.genValueButton.clicked.connect(cls.take_turn)
        cls.resetButton.clicked.connect(cls.reset_board)
        cls.passButton.clicked.connect(cls.pass_turn)
        cls.game_buttons = {}
        cls.turn_active = False
        cls.player_colors = { # Make this dynamic later
            'Player 1': "#ff5555",
            'Player 2': "#5555ff",
            'Match': "#55ff55",
            'No Match': "#999999"
        }
        
    def generate_board(cls):
        for btn in cls.game_buttons.values():
            try:
                btn.button.deleteLater()
            except:
                pass
        cls.game_buttons = {}
        rows = cls.spin_box_row.value()
        cols = cls.spin_box_col.value()
        cls.board_array = np.empty((rows, cols), dtype="<U10")
        size = min((700 / cols), (500 / rows))
        
        if cls.combo_box_mode.currentText() == "Coin Toss":
            cls.mode = GameMode("Coin Toss", "Toss Coin", 1, 2)
        elif cls.combo_box_mode.currentText() == "Dice Roll":
            cls.mode = GameMode("Dice Roll", "Roll Dice", 2, 6)
        cls.genValueButton.setText(cls.mode.verb)    
        cls.win_condition = 4 # get value from dialog later
        for i in range(rows):
            for j in range(cols):
                btn_name = f"button{i}_{j}"
                btn_value = cls.mode.generate_button_value(0.2) # 20% chance of generating a free space
                x = 20 + ((700 - (size * cols))/2) + (size * j)
                y = 20 + (size * i)
                cls.add_button(btn_name, btn_value, size, x, y, i, j)
        cls.update_board()
        cls.genValueButton.setEnabled(True)
             
    def reset_board(cls):
        for btn in cls.game_buttons.values():
            btn.status = "No Match"
        
        cls.update_board()
        
    def add_button(cls, name, value, size, x, y, i, j):
        button = QPushButton(cls)
        button.setText(str(value))
        button.setObjectName(name)
        button.setGeometry(x, y, size, size)
        button.clicked.connect(cls.button_clicked)
        button.show()
        
        gbutton = GameButton(name, value, "No Match", button, i, j)
        cls.game_buttons[name] = gbutton        
            
    def button_clicked(cls):
        sending_button = cls.sender()
        button_name = sending_button.objectName()
        game_button = cls.game_buttons[button_name]
        
        if game_button.status == "Match":
            game_button.status = cls.currentPlayerLabel.text()
            i = game_button.i
            j = game_button.j
            cls.board_array[i,j] = cls.currentPlayerLabel.text()
            
            for btn in cls.game_buttons.values():
                if btn.status == "Match":
                    btn.status = "No Match"
        
            cls.update_board()
            cls.end_turn()
    
    def take_turn(cls):
        val = cls.mode.generate_value()
        cls.valueLabel.setText(str(val))
        
        cls.turn_active = True  
        cls.genValueButton.setEnabled(False)
        current_player = cls.currentPlayerLabel.text()
        
        for btn in cls.game_buttons.values():
            if (btn.value == val or btn.value == "Free Space") and btn.status == "No Match":
                btn.status = "Match"
                
        count = 0
        for btn in cls.game_buttons.values():
            if btn.status == "Match":
                count += 1
        if count == 0:
            cls.passButton.setEnabled(True)
            
        cls.update_board()
        
    def pass_turn(cls):
        cls.update_board()
        cls.end_turn()
            
    def update_board(cls):
        for btn in cls.game_buttons.values():
            color = cls.player_colors[btn.status]
            btn.button.setStyleSheet(f"background-color:{color}")

    def end_turn(cls):
        current_player = cls.currentPlayerLabel.text()
        win = cls.check_win(current_player)
        if not win: # make this more dynamic
            if current_player == "Player 1":
                cls.currentPlayerLabel.setText("Player 2")
                cls.currentPlayerLabel.setStyleSheet(f"color:{cls.player_colors['Player 2']}")
            else:
                cls.currentPlayerLabel.setText("Player 1")
                cls.currentPlayerLabel.setStyleSheet(f"color:{cls.player_colors['Player 1']}")
            cls.passButton.setEnabled(False)
            cls.turn_active = False
            cls.genValueButton.setEnabled(True)
        else:
            cls.currentPlayerLabel.setText(f"{current_player} Wins!")
    
    def check_win(cls, player):
        n_to_win = cls.win_condition
        print(player)
        print(cls.board_array)     
        h = cls.check_horizontal(cls.board_array, n_to_win, player)
        v = cls.check_vertical(cls.board_array, n_to_win, player)
        d = cls.check_diagonal(cls.board_array, n_to_win, player)
        w = h + v + d
        print(h)
        print(v)
        print(d)
        print(w)
        
        if w > 0:
            return True
        else:
            return False

    def check_horizontal(cls, a, n_to_win, player):
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
    
    def check_vertical(cls, a, n_to_win, player):
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
    
    def check_diagonal(cls, a, n_to_win, player):
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

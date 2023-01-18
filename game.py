from classes import Player
from board_dialog import BoardDialog
import sys
import numpy as np

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication

    
def main():
    #game = Game(3,3,2)
    #print(game.board)
    #app = QApplication(sys.argv)
    app = QApplication([])
    dlg = BoardDialog()
    dlg.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()
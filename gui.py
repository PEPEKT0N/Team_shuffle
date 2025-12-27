import sys
from typing import List, Tuple

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
)

from pydantic import ValidationError

from dota_team_shuffle import Players, split_team


class TeamGeneratorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Генератор команд")
        self.setMinimumSize(650, 600)

        self.inputs: List[QLineEdit] = []

        self.reveal_order: List[Tuple[int, int, str]] = []
        self.reveal_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_player)

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Введите имена 10 игроков")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title)

        main_layout.addSpacing(10)

        players_box = QGroupBox("Игроки")
        players_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        players_box.setContentsMargins(0, 0, 0, 0)


        players_layout = QVBoxLayout(players_box)
        players_layout.setContentsMargins(20, 20, 20, 20)
        players_layout.setSpacing(10)

        for i in range(10):
            edit = QLineEdit()
            edit.setPlaceholderText(f"Игрок {i + 1}")
            self.inputs.append(edit)
            players_layout.addWidget(edit)

        main_layout.addWidget(players_box)

        self.generate_button = QPushButton("Разделить на команды")
        self.generate_button.clicked.connect(self.generate_teams)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2979FF;
                color: white;
                font-size: 14px;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        main_layout.addWidget(self.generate_button)

        teams_layout = QHBoxLayout()

        self.team1_layout, self.team1_slots = self._create_team_column("👖 Команда Штаны:")
        self.team2_layout, self.team2_slots = self._create_team_column("🐝 Команда Шмаль:")

        teams_layout.addLayout(self.team1_layout)
        teams_layout.addLayout(self.team2_layout)

        main_layout.addLayout(teams_layout)

    def _create_team_column(self, title_text: str):
        layout = QVBoxLayout()

        title = QLabel(title_text)
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title)

        slots: List[QLabel] = []

        for _ in range(5):
            label = QLabel("—")
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 6px;
                    border: 1px solid #CCCCCC;
                    border-radius: 4px;
                    min-height: 24px;
                }
            """)
            slots.append(label)
            layout.addWidget(label)

        layout.addStretch()

        return layout, slots

    def generate_teams(self):
        if self.timer.isActive():
            self.timer.stop()

        players = [edit.text() for edit in self.inputs]

        try:
            validated = Players(players=players)
            team_1, team_2 = split_team(validated.players)

            for label in self.team1_slots + self.team2_slots:
                label.setText("—")

            self.reveal_order.clear()
            for i in range(len(team_1)):
                self.reveal_order.append((1, i, team_1[i]))
                self.reveal_order.append((2, i, team_2[i]))

            self.reveal_index = 0
            self.timer.start(1200)

        except ValidationError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_next_player(self):
        if self.reveal_index >= len(self.reveal_order):
            self.timer.stop()
            return

        team_number, index, name = self.reveal_order[self.reveal_index]

        if team_number == 1:
            self.team1_slots[index].setText(name)
        else:
            self.team2_slots[index].setText(name)

        self.reveal_index += 1


def main():
    app = QApplication(sys.argv)
    window = TeamGeneratorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QTextBrowser, QTextEdit, QPlainTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from module.capture_screen import CaptureScreen
from module.moji import moji
from module.youdao import youdao
from module.weblio import weblio
from module.anki_api import AnkiConnector

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Anki卡片制作')
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        # 牌组和模板名称选择
        selectionLayout = QHBoxLayout()

        self.deckNameCombo = QComboBox(self)
        self.deckNameCombo.addItem("HT")
        self.deckNameCombo.addItem("manga")
        selectionLayout.addWidget(self.deckNameCombo)

        self.modelNameCombo = QComboBox(self)
        self.modelNameCombo.addItem("manga")
        selectionLayout.addWidget(self.modelNameCombo)

        layout.addLayout(selectionLayout)

        self.expressionEdit = QLineEdit(self)
        self.expressionEdit.textChanged.connect(self.on_text_changed)
        self.expressionEdit.setPlaceholderText('单词')
        layout.addWidget(self.expressionEdit)

        # 使用QPlainTextEdit代替QTextEdit以支持多行输入和自动换行，同时保持纯文本格式
        self.sentenceEdit = QPlainTextEdit(self)
        self.sentenceEdit.setPlaceholderText('句子')
        self.sentenceEdit.setMaximumHeight(50)  # 设置一个初始最大高度
        layout.addWidget(self.sentenceEdit)

        # 使用QTextEdit来代替QTextBrowser以支持文本编辑
        self.definitionEdit = QTextEdit(self)  # 修改这里
        self.definitionEdit.setMaximumHeight(150)
        self.definitionEdit.setPlaceholderText('Moji & Youdao')
        layout.addWidget(self.definitionEdit)

        self.captureButton = QPushButton('截图', self)
        self.captureButton.clicked.connect(self.captureScreen)
        layout.addWidget(self.captureButton)

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setText("- 截图选定范围后回车或者双击 -")
        layout.addWidget(self.imageLabel)

        self.sendButton = QPushButton('发送到 Anki', self)
        self.sendButton.clicked.connect(self.on_send_to_anki)
        layout.addWidget(self.sendButton)

        self.setLayout(layout)

    def captureScreen(self):
        self.captureWin = CaptureScreen(self.updateImageDisplay)
        self.captureWin.show()

    def updateImageDisplay(self, imagePath):
        pixmap = QPixmap(imagePath)
        self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def on_text_changed(self):
        word = self.expressionEdit.text()
        if word:
            definition = '<hr class="rd213">'.join([moji(word), youdao(word), weblio(word)])
            print(definition)
            self.definitionEdit.setHtml(definition)  # 使用setHtml而不是setText

    def on_send_to_anki(self):
        word = self.expressionEdit.text()
        definition = self.definitionEdit.toHtml()  # 获取HTML内容
        deckName = self.deckNameCombo.currentText()
        modelName = self.modelNameCombo.currentText()
        sentence = self.sentenceEdit.toPlainText()
        if word and definition and deckName and modelName:
            try:
                connector = AnkiConnector()
                connector.create_note(deckName=deckName,
                                      modelName=modelName,
                                      expression=word,
                                      sentence=sentence,
                                      meaning=definition,
                                      image_path='cache/picture.jpg',
                                      exp_path='cache/audio-exp.mp3',
                                      sen_path='cache/audio-sen.mp3')
            except Exception as e:
                print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())

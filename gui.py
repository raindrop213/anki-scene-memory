import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QPlainTextEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from module.capture_screen import CaptureScreen
from module.moji import moji
from module.youdao import youdao
from module.weblio import weblio
from module.anki_api import AnkiConnector
import configparser

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini') # 加载配置
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Anki卡片制作')
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout()

        # 牌组和模板名称选择
        selectionLayout = QHBoxLayout()

        self.deckNameCombo = QComboBox(self)
        decks = self.config.get('anki', 'decks').split(',')
        for deck in decks:
            if deck:
                self.deckNameCombo.addItem(deck.strip())
        selectionLayout.addWidget(self.deckNameCombo)

        self.modelNameCombo = QComboBox(self)
        models = self.config.get('anki', 'models').split(',')
        for model in models:
            if model:
                self.modelNameCombo.addItem(model.strip())
        selectionLayout.addWidget(self.modelNameCombo)

        layout.addLayout(selectionLayout)

        # 添加切换按钮以选择翻译来源
        sourceSelectionLayout = QHBoxLayout()
        self.mojiButton = QPushButton("Moji", self)
        self.mojiButton.setCheckable(True)
        self.mojiButton.setChecked(True)  # 默认选中
        self.mojiButton.clicked.connect(self.on_source_selection_changed)
        sourceSelectionLayout.addWidget(self.mojiButton)

        self.youdaoButton = QPushButton("Youdao", self)
        self.youdaoButton.setCheckable(True)
        self.youdaoButton.setChecked(True)  # 默认选中
        self.youdaoButton.clicked.connect(self.on_source_selection_changed)
        sourceSelectionLayout.addWidget(self.youdaoButton)

        self.weblioButton = QPushButton("Weblio", self)
        self.weblioButton.setCheckable(True)
        self.weblioButton.clicked.connect(self.on_source_selection_changed)  # 默认不选中
        sourceSelectionLayout.addWidget(self.weblioButton)

        layout.addLayout(sourceSelectionLayout)

        self.expressionEdit = QLineEdit(self)
        self.expressionEdit.textChanged.connect(self.on_text_changed)
        self.expressionEdit.setPlaceholderText('单词')
        layout.addWidget(self.expressionEdit)

        # 句子编辑框和复制按钮的布局
        sentenceLayout = QHBoxLayout()
        self.sentenceEdit = QPlainTextEdit(self)
        self.sentenceEdit.setPlaceholderText('句子')
        self.sentenceEdit.setMaximumHeight(50)
        sentenceLayout.addWidget(self.sentenceEdit)

        # 创建复制到句子框的按钮
        self.pasteButton = QPushButton('⧉', self)  # 你可以使用更合适的文本或图标
        self.pasteButton.setFixedWidth(50)  # 设置按钮宽度为20
        self.pasteButton.setMaximumHeight(50)
        self.pasteButton.clicked.connect(self.pasteText)
        sentenceLayout.addWidget(self.pasteButton)

        layout.addLayout(sentenceLayout)

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

    def pasteText(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.sentenceEdit.setPlainText(text)

    def captureScreen(self):
        self.captureWin = CaptureScreen(self.updateImageDisplay)
        self.captureWin.show()

    def updateImageDisplay(self, imagePath):
        pixmap = QPixmap(imagePath)
        self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # 当复选框状态改变时调用
    def on_source_selection_changed(self):
        # 更新占位文本以反映当前的翻译源选择
        sources = []
        if self.mojiButton.isChecked():
            sources.append("Moji")
        if self.youdaoButton.isChecked():
            sources.append("Youdao")
        if self.weblioButton.isChecked():
            sources.append("Weblio")
        placeholderText = " & ".join(sources) if sources else "请选择词典"
        self.definitionEdit.setPlaceholderText(placeholderText)

        self.on_text_changed()

    def on_text_changed(self):
        word = self.expressionEdit.text()
        if word:
            sources = []
            if self.mojiButton.isChecked():
                sources.append(moji(word))
            if self.youdaoButton.isChecked():
                sources.append(youdao(word))
            if self.weblioButton.isChecked():
                sources.append(weblio(word))

            definition = '<hr class="rd213">'.join(sources)
            self.definitionEdit.setHtml(definition)

    def on_send_to_anki(self):
        word = self.expressionEdit.text()
        definition = self.definitionEdit.toHtml()  # 获取HTML内容
        deckName = self.deckNameCombo.currentText()
        modelName = self.modelNameCombo.currentText()
        sentence = self.sentenceEdit.toPlainText()
        if word and definition and deckName and modelName and sentence:
            try:
                connector = AnkiConnector(config=self.config)
                connector.create_note(deckName=deckName,
                                      modelName=modelName,
                                      expression=word,
                                      sentence=sentence,
                                      meaning=definition,
                                      image_path='cache/picture.jpg',
                                      exp_path='cache/audio-exp.mp3',
                                      sen_path='cache/audio-sen.mp3')
            except Exception as e:
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setText("发生错误")
                error_dialog.setInformativeText(str(e))
                error_dialog.setWindowTitle("错误")
                error_dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())

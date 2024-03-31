import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QPlainTextEdit, QCheckBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from module.capture_screen import CaptureScreen
from module.moji import moji
from module.youdao import youdao
from module.weblio import weblio
from module.mecab import MeCabConverter
from module.anki_api import AnkiConnector
import webbrowser
import yaml


class MyPlainTextEdit(QPlainTextEdit):
    textSelected = pyqtSignal(str)  # 定义一个信号，用来发送所选文本

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        selectedText = self.textCursor().selectedText()  # 获取所选文本
        if selectedText:  # 如果有选中的文本，发出信号
            self.textSelected.emit(selectedText)

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config('config.yaml')  # 加载配置文件
        self.cixingColors = self.config['mecab']['cixingcolor']  # 加载词性颜色配置
        self.initUI()
        self.toggleAlwaysOnTop()  # 添加这行来应用初始的置顶设置

    def load_config(self, filepath):
        """加载YAML配置文件"""
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def initUI(self):
        self.setWindowTitle('Anki卡片制作')
        self.setWindowIcon(QIcon('docs/icon.png'))  # 设置窗口图标
        self.setGeometry(100, 100, 400, 700)

        layout = QVBoxLayout()

        # 牌组和模板名称选择
        selectionLayout = QHBoxLayout()

        self.deckNameCombo = QComboBox(self)
        decks = self.config['anki']['decks']
        for deck in decks:
            self.deckNameCombo.addItem(deck)
        selectionLayout.addWidget(self.deckNameCombo)

        self.modelNameCombo = QComboBox(self)
        models = self.config['anki']['models']
        for model in models:
            self.modelNameCombo.addItem(model)
        selectionLayout.addWidget(self.modelNameCombo)

        # 创建带有 GitHub 图标的按钮
        self.githubButton = QPushButton(self)
        self.githubButton.setIcon(QIcon('./docs/icon-github.svg'))
        self.githubButton.setFixedWidth(30)
        self.githubButton.clicked.connect(self.openGithub)
        selectionLayout.addWidget(self.githubButton)

        layout.addLayout(selectionLayout)  # 将选择布局添加到主布局中

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
        self.weblioButton.clicked.connect(self.on_source_selection_changed)
        sourceSelectionLayout.addWidget(self.weblioButton)

        self.screenButton = QPushButton("截图", self)
        self.screenButton.setCheckable(True)
        self.screenButton.setChecked(True)  # 默认选中
        self.screenButton.setFixedWidth(50)
        self.screenButton.clicked.connect(self.toggleCaptureArea)  # 显示和隐藏下面的截图框和截图键
        sourceSelectionLayout.addWidget(self.screenButton)

        layout.addLayout(sourceSelectionLayout)

        self.expressionEdit = QLineEdit(self)
        self.expressionEdit.textChanged.connect(self.on_text_changed)
        self.expressionEdit.setPlaceholderText('单词')
        layout.addWidget(self.expressionEdit)

        # 句子编辑框和复制按钮的布局
        sentenceLayout = QHBoxLayout()
        self.sentenceEdit = MyPlainTextEdit(self)
        self.sentenceEdit.setPlaceholderText('句子')
        self.sentenceEdit.setMaximumHeight(50)
        self.sentenceEdit.textSelected.connect(self.on_text_selected)  # 连接信号到槽函数
        sentenceLayout.addWidget(self.sentenceEdit)

        # 创建复制到句子框的按钮
        self.pasteButton = QPushButton('⧉', self)  # 你可以使用更合适的文本或图标
        self.pasteButton.setFixedWidth(50)  # 设置按钮宽度为20
        self.pasteButton.setMinimumHeight(50)
        self.pasteButton.clicked.connect(self.pasteText)
        sentenceLayout.addWidget(self.pasteButton)

        layout.addLayout(sentenceLayout)

        # 注音框
        self.pronunciationEdit = QWebEngineView(self)
        self.pronunciationEdit.setMinimumHeight(150)
        layout.addWidget(self.pronunciationEdit)
        self.sentenceEdit.textChanged.connect(self.on_sentence_changed)

        # 使用QTextEdit来代替QTextBrowser以支持文本编辑
        self.definitionEdit = QTextEdit(self)
        self.definitionEdit.setMinimumHeight(150)
        self.definitionEdit.setPlaceholderText('Moji & Youdao')
        layout.addWidget(self.definitionEdit)

        self.captureButton = QPushButton('截图', self)
        self.captureButton.clicked.connect(self.captureScreen)
        layout.addWidget(self.captureButton)

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setText("- 截图选定范围后回车或者双击 -")
        self.imageLabel.setMinimumHeight(150)
        layout.addWidget(self.imageLabel)

        # 发送和置顶按钮的水平布局
        sendAndPinLayout = QHBoxLayout()

        self.sendButton = QPushButton('发送到 Anki', self)
        self.sendButton.clicked.connect(self.on_send_to_anki)
        sendAndPinLayout.addWidget(self.sendButton)

        self.pinButton = QPushButton('🔝', self)  # 假设你有一个置顶图标pin-icon.png
        self.pinButton.setCheckable(True)
        self.pinButton.setChecked(True)  # 默认置顶
        self.pinButton.setFixedWidth(25)
        self.pinButton.clicked.connect(self.toggleAlwaysOnTop)
        sendAndPinLayout.addWidget(self.pinButton)

        layout.addLayout(sendAndPinLayout)  # 添加新的水平布局到主布局

        self.statusLabel = QLabel("- ready -")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setWordWrap(True)  # 允许文本换行
        self.statusLabel.setMinimumHeight(20)
        self.statusLabel.setMaximumWidth(self.width() - 20)  # 设置最大宽度为窗口宽度减去一定的边距
        layout.addWidget(self.statusLabel)  # 将状态栏标签添加到布局中

        self.setLayout(layout)

    def toggleCaptureArea(self):
        # This method will toggle the visibility of the capture area and button
        if self.captureButton.isVisible():
            self.captureButton.hide()
            self.imageLabel.hide()
        else:
            self.captureButton.show()
            self.imageLabel.show()

    def on_sentence_changed(self):
        sentence = self.sentenceEdit.toPlainText()
        if sentence:
            processor = MeCabConverter()
            results = processor.process_text(sentence)
            annotated_sentence = ""
            for word_info in results:
                background_color = self.cixingColors.get(word_info['pos'], "white")  # Default to white if POS not found
                word_html = f"<span style='background-color: {background_color};line-height:2;'>{word_info['word']}</span>"

                if word_info['furigana']:
                    annotated_sentence += f"<ruby>{word_html}<rt style='font-size: 0.6em;'>{word_info['furigana']}</rt></ruby>"
                else:
                    annotated_sentence += word_html

            self.pronunciationEdit.setHtml(annotated_sentence)


    def toggleAlwaysOnTop(self):
        if self.pinButton.isChecked():
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def on_text_selected(self, text):
        # 将选中的文本设置到单词编辑框中
        self.expressionEdit.setText(text)

    def updateStatusMessage(self, message):
        """更新状态栏消息的方法。"""
        self.statusLabel.setText(message)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.statusLabel:
            self.statusLabel.setMaximumWidth(self.width() - 20)

    def openGithub(self):
        webbrowser.open('https://github.com/raindrop213/anki-scene-memory')

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
        
        try:
            if word and definition and deckName and modelName and sentence:
                connector = AnkiConnector(config=self.config)
                note_id = connector.create_note(deckName=deckName,
                                                modelName=modelName,
                                                expression=word,
                                                sentence=sentence,
                                                meaning=definition,
                                                image_path='cache/picture.jpg',
                                                exp_path='cache/audio-exp.mp3',
                                                sen_path='cache/audio-sen.mp3')
                self.updateStatusMessage(f'Created note with ID:{note_id}')
            else:
                self.updateStatusMessage(f'One or more information are empty.')
        except Exception as e:
            self.updateStatusMessage(f"失败: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())

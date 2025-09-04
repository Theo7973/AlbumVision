from PySide6.QtCore import QFile, QTextStream

class ThemeManager:
    @staticmethod
    def apply_theme(app, theme: str):
        """Apply dark, light, or auto theme to the whole app"""
        theme = theme.lower()
        if theme == "dark theme":
            qss_file = QFile("app/resources/themes/dark.qss")
        elif theme == "light theme":
            qss_file = QFile("app/resources/themes/light.qss")
        else:
            # Auto = system default → clear stylesheet
            app.setStyleSheet("")
            return

        if qss_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(qss_file)
            app.setStyleSheet(stream.readAll())

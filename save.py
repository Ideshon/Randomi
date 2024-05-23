from PyQt5.QtWidgets import QFileDialog

def saveToFile(widget):
    filePath, _ = QFileDialog.getSaveFileName(widget, "Save File", "", "Text Files (*.txt)")
    if filePath:
        try:
            with open(filePath, 'w', encoding='utf-8') as file:
                file.write(widget.entry.toPlainText() + '\n---END---\n')
                file.write(widget.result_output.toPlainText() + '\n---END---\n')
                file.write(widget.template_label.toPlainText() + '\n---END---\n')
        except Exception as e:
            widget.result_output.setText(f"Error saving file: {str(e)}")

def loadFromFile(widget):
    filePath, _ = QFileDialog.getOpenFileName(widget, "Open File", "", "Text Files (*.txt)")
    if filePath:
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                content = file.read()
            parts = content.split('---END---\n')
            if len(parts) >= 3:
                widget.entry.setPlainText(parts[0].strip())
                widget.result_output.setPlainText(parts[1].strip())
                widget.template_label.setPlainText(parts[2].strip())
        except Exception as e:
            widget.result_output.setText(f"Error loading file: {str(e)}")

# штука
if (__name__ == '__main__'):
    main()
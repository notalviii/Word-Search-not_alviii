"""Punto de entrada de Word Search Book Maker."""

from app.ui.application import WordSearchBookMakerApp


def main() -> None:
    app = WordSearchBookMakerApp()
    app.mainloop()


if __name__ == "__main__":
    main()

import sys
from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property

import theme
from main_window import MainWindow


class AppContext(ApplicationContext):
    def run(self):
        self.window.show()
        return appctxt.app.exec_()

    def get_design(self):
        qt_creator_file = self.get_resource("PyChan.ui")
        return qt_creator_file

    @cached_property
    def window(self):
        return MainWindow(self.get_design())


if __name__ == '__main__':
    theme.set_theme()
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)

import time

from pywinauto.application import Application
import pywinauto.findwindows as fw
from pywinauto.backend import registry
import subprocess


class UIAutomationConfig(object):

    def __init__(self, backend, app_path, window_title):
        """
        Initialize the instance of class UIAutomation
        :param backend: the accessibility technology of application,
                       'uia' or 'win32'. 'uia' is recommended.
                 :type string
        'uia': Microsoft UI Automation, browsers or app developed based on the
        following frameworks:WinForms, WPF and Qt5.
        'win32': app developed based on MFC, VB6 or Most old legacy apps.

        :param app_path: If the path of the application is not in the
                         environment variable, the absolute path is used to
                         connect the specified already running application.
                  type: string
        :param window_title: the title of the window in application.
        :return: UIAutomation object
        """
        self.backend = backend
        self.backend_obj = registry.backends[backend]
        self.app_path = app_path
        self.dlg_title = window_title
        self.app = None
        self.window = None

    def app_kill(self):
        """
        Kill the application that is already open.
        :return: None
        """
        if self.app is not None:
            self.app.kill()
            self.app = None

    def app_start(self, start_cmd_line, set_focus=True):
        """
        Call '_connect_to_window()' to start the application and connect the
        specified window.
        :param start_cmd_line: the cmd line of starting application.
                         type: string
        :param set_focus: set application window focus, default is True.
                    type: bool
        """
        try:
            self._connect_to_window(start_cmd_line, set_focus)
        except WindowsError as winerr:
            self._log_write('Invalid command line:"{0}".'
                            .format(start_cmd_line))
            raise winerr
        except Exception as e:
            self.app_kill()
            raise e

    def get_element_text(self, element_object):
        """
        Get the title of specified element.
        :param element_object: element object returned through find_element()
                            or find_element_by_path()
        :return: element title string if no exception, otherwise return None.
        """
        if element_object is not None:
            try:
                text = element_object.window_text()
                return text
            except Exception as e:
                self._log_write(e)
                return None

    def check_element_text(self, expect_text, ele_auto_id=None,
                           ele_class_name=None, ele_control_type=None,
                           ele_framework_id=None):
        """
        Check the text of specified element in current UI or not.
        :param expect_text: the expected text of the element that needs to
                             be checked.
                       type: string
        :param ele_class_name: element class name, get from 'ClassName' in
                              'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :param ele_control_type: element control type, get from 'ControlType' in
                               'inspect.exe' if exist.
                        :type hex int.
        ex: In 'inspect.exe',the ControlType:UIA_TextControlTypeId (0xC364),then
            ele_control_type=0xC364.

        :param ele_auto_id: The automation id of element,get from 'AutomationId'
                            in 'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :param ele_framework_id: The framework id of element, get from
                                'FrameworkId' in 'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :return: True if the text of the element being queried is the same as
                 the expected text, otherwise False.
        """
        is_ele_find, element = \
            self.find_element(class_name=ele_class_name,
                              control_type=ele_control_type,
                              auto_id=ele_auto_id,
                              framework_id=ele_framework_id)
        if is_ele_find:
            element_text = element.window_text()
            if element_text != expect_text:
                error_info = '"{0}" not matched with: "{1}" '.format(
                    element_text, expect_text)
                self._log_write(error_info)
                is_ele_find = False
        return is_ele_find

    def find_element(self, class_name=None, title=None,
                     control_type=None, auto_id=None, framework_id=None,
                     top_level_only=False):
        """
        Find only one element based on the criterias of the specified element.
        To find the elements more accurately, the more attributes the better.
        :param class_name:element class name, get from 'ClassName' in
                              'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :param title: element title, get from 'Name' in 'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :param control_type: element control type, get from 'ControlType' in
                               'inspect.exe' if exist.
                        :type hex int.
        :param auto_id: The automation id of element,get from 'AutomationId'
                            in 'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :param framework_id: The framework id of element, get from
                                'FrameworkId' in 'inspect.exe' if exist.
                        :type refer 'inspect.exe'
        :param top_level_only: Top level elements only, default is False, if set
                    true, will only find the first layer children in desktop.
                    Recommend set it to False.
                        :type bool
        :return: find result(bool) and element (object).
                 Found: True and element object,
                 Not Found: False and None.
        """
        eles_info = fw.find_elements(process=self.process,
                                     backend=self.backend,
                                     class_name=class_name, title=title,
                                     control_type=control_type,
                                     auto_id=auto_id,
                                     framework_id=framework_id,
                                     top_level_only=top_level_only)
        elements = []
        for ele_info in eles_info:
            elements.append(
                self.backend_obj.generic_wrapper_class(ele_info))
        if len(elements) > 1:
            find_error = "FIND_ERROR: {0} elements matched with the " \
                         "criterias.".format(len(elements))
            self._log_write(find_error)
            return False, None
        elif len(elements) == 0:
            self._log_write("FIND_ERROR: No element matched with the "
                            "criterias.")
            return False, None
        else:
            return True, elements[0]

    def find_element_by_path(self, child_indexes):
        """
        According the attributes of element will find one or more elements, in
        order to accurately find only one element, the element path is used.
        :param child_indexes: All the ancestors of the element, include itself.
                              The index under their parent.
                        :type list
        Get the child index from 'inspect.exe'
           ex: |-"Trusted Platform Module (TPM) Management on Local Computer"
                 |-"WorkSpace" pane
                   |-"TPM Computer" window
                     |-"Max" button
                     |-"Min" button
                     |-"Close" button
                 |-""title bar
            The first layer is the launched app. Begin with the first layer's
            child and the child's index starts at 0,the "WorkSpace" pane is the
            0th child of it parent, and so on,if we want to locate the "Close"
            button, we need the child indexes of "WorkSpace", "TPM Computer" and
            "Close", so the child_indexes=[0,0,2]

        :return: find result(bool) and element (object).
                 Found: True and element object,
                 Not Found: False and None.
        """
        if len(child_indexes) != 0:
            current_obj = self.window
            for i in range(len(child_indexes)):
                index = child_indexes[i]
                childs = current_obj.children()
                if len(childs) - 1 >= index:
                    current_obj = childs[index]
                else:
                    error_info = ("The child_indexes[{0}]={1} is not exist."
                                  .format(i, child_indexes[i]))
                    self._log_write(error_info)
                    return False, None
            return True, current_obj
        else:
            find_error = "FIND_ERROR: The child_indexes is empty."
            self._log_write(find_error)
            return False, None

    def _connect_to_window(self, app_start_cmd, set_focus):
        """
        Start the specified application and connect the already running process.
        :param app_start_cmd: the cmd_line to start the application.
        :param set_focus: set the specified window focus or not.
                   type: bool
        :return: None
        """
        proc = subprocess.Popen(app_start_cmd)
        # Wait for the app to start, or the connection may go wrong.
        time.sleep(2)
        try:
            self.app = Application(backend=self.backend).connect(
                path=self.app_path)
        except Exception as e:
            proc.kill()
            raise e
        self.process = self.app.process
        for window in self.app.windows():
            if window.window_text() == self.dlg_title:
                self.window = window
        if self.window is None:
            title_err = Exception('WINDOW_TITLE_ERROR: '
                                  'No such window: "{0}"'
                                  .format(self.dlg_title))
            raise title_err
        if set_focus:
            self.window.set_focus()

    def _log_write(self, msg):
        """
        Write log.
        :param msg: the log message.
              type: string
        :return: None
        """
        print(msg)


if __name__ == '__main__':
    try:
        dm = UIAutomationConfig(backend='uia', app_path='mmc.exe',
                                window_title="Trusted Platform Module (TPM) "
                                             "Management on Local Computer")
        dm.app_start("mmc.exe TPM.msc")

        # check expected text by the attributes with element.
        check_result = dm.check_element_text('The TPM is ready for use.',
                                             ele_auto_id='status')
        print(check_result)

        # find element by its attributes.
        find_result, tpm_object = dm.find_element(auto_id='status')
        if find_result:
            print(dm.get_element_text(tpm_object))

        # find element by child_indexes path
        child_indexes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0]
        is_find, tpm_ele = dm.find_element_by_path(child_indexes)
        if is_find:
            print(dm.get_element_text(tpm_ele))
        dm.app_kill()
    except Exception as e:
        print(e)

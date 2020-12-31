import io
import os
import re
from enum import Enum

from termcolor import cprint
from SoftwareAbstractionLayer import lib_constants
from SoftwareAbstractionLayer import lib_parse_config
# from HardwareAbstractionLayer.library import write_log
from SoftwareAbstractionLayer.debugscreen import DebugScreen, Vt100Cmd

# A mapping of ANSI text style codes to style names, "+" means the:
# attribute is set, "-" -- reset; example:
# TODO: currently, only +bold is used, should look into set/rest method
TEXT = {
    0: "default",
    1: "+bold",
    3: "+italics",
    4: "+underscore",
    7: "+reverse",
    9: "+strikethrough",
    22: "-bold",
    23: "-italics",
    24: "-underscore",
    27: "-reverse",
    29: "-strikethrough",
}

# A mapping of ANSI foreground color codes to color names.
FG_ANSI = {
    30: "black",
    31: "red",
    32: "green",
    33: "brown",
    34: "blue",
    35: "magenta",
    36: "cyan",
    37: "white",
    39: "default"  # white.
}

# A mapping of ANSI background color codes to color names.
BG_ANSI = {
    40: "black",
    41: "red",
    42: "green",
    43: "brown",
    44: "blue",
    45: "magenta",
    46: "cyan",
    47: "white",
    49: "default"  # black.
}

# An alias for compatibility.
FG = FG_ANSI
FG_DEFAULT = 39
BG = BG_ANSI
BG_DEFAULT = 49
TEXT_DEFAULT = 0

# Inverted dict for config parse
FG_INV = {v: k for k, v in FG.items()}
BG_INV = {v: k for k, v in BG.items()}
TEXT_INV = {v: k for k, v in TEXT.items()}

VT100_ESC = b'\x1b'

# Internal usage for _char_matrix
COLUMN_CONTENT = 0
COLUMN_FG = 1
COLUMN_BG = 2
COLUMN_TEXT = 3


class EntryType(Enum):
    """
    Enum type for return value of ScreenParser.get_selectable_page()
    """
    UNKNOWN = 0
    MENU = 1
    DROP_DOWN = 2
    CHECKBOX_CHECKED = 3
    CHECKBOX_UNCHECKED = 4
    INPUT_BOX = 5
    SELECTABLE_TXT = 6
    DISABLE_TXT = 7
    SUBTITLE = 8


SELECTABLE_ENTRY_S = {
    EntryType.MENU,
    EntryType.DROP_DOWN,
    EntryType.CHECKBOX_CHECKED,
    EntryType.CHECKBOX_UNCHECKED,
    EntryType.INPUT_BOX,
    EntryType.SELECTABLE_TXT
}


class ScreenParserError(Exception):
    """This is base class for exceptions in vt100_screen_parser"""
    pass


def _parse_without_esc(byte_input, events):
    """
    If an input not start with \x1b take it as draw string cmd
    append to events, return the left bytes start with \x1b
    """
    idx = byte_input.find(VT100_ESC)
    try:
        if idx > 0:
            events.append(Vt100Cmd("draw", [byte_input[:idx].decode('ascii')]))
            return byte_input[idx:]
        elif idx == 0:
            return byte_input
        else:
            events.append(Vt100Cmd("draw", [byte_input.decode('ascii')]))
            return b''
    except UnicodeDecodeError:
        return byte_input


def parse_edk_shell(inputs):
    """
    Function Name       : parse_edk_shell()
    Parameters          : inputs
    Functionality       : parse the output of EDK/EFI shell serial output
                          return string
    Function Invoked    : DebugScreen.serial_output_split()
    Return Value        : str
    """
    events = []
    ret_str = ""
    debug_screen = DebugScreen()
    if isinstance(inputs, bytes):
        inputs = [inputs]
    if isinstance(inputs, list):
        for i in inputs:
            i = _parse_without_esc(i, events)
            events.extend(debug_screen.serial_output_split(i))

    for event in events:
        if event.name == "draw":
            assert len(event.param) == 1, "vt100 debugScreen draw param number not 1"
            ret_str += event.param[0]

    return ret_str


class ScreenParser:

    def __init__(self, tc_id=None, script_id=None, loglevel="ALL"):
        """
        Function Name       : __init__()
        Parameters          : tc_id, script_id, loglevel
        Functionality       : Initialize ScreenParser
        Function Invoked    : ScreenParser._init_screen_info()
                              ScreenParser._init_platform_config()
                              ScreenParser._init_char_matrix()
        Return Value        : None
        """
        self._tc_id = tc_id
        self._script_id = script_id
        self._loglevel = loglevel
        # to get return from pyte.DebugScreen, temporary solution
        self._stringIO = io.StringIO()
        self._buff = None
        self._screen_info = None
        self._debug_screen = DebugScreen()
        self._init_platform_config()
        self._init_screen_info()
        self.cur_fg = FG_DEFAULT
        self.cur_bg = BG_DEFAULT
        self.cur_text_attribute = TEXT_DEFAULT
        self._init_char_matrix()

    class ScreenItem:
        """
        Inner class, data structure for ScreenParser._screen_info
        """
        def __init__(self, content, beg, end, fg_color, bg_color, text_atr=0):
            self.content = content
            self.beg = beg
            self.end = end
            self.fg_color = fg_color
            self.bg_color = bg_color
            self.text = text_atr

        def __repr__(self):
            return "({},{},{},{},{},{})".format(self.content, self.beg,
                                                self.end, self.fg_color,
                                                self.bg_color, self.text)

    def _init_char_matrix(self):
        self._char_matrix = []
        for row in range(self._height):
            self._char_matrix.append([])
            for _ in range(self._width):
                self._char_matrix[row].append([' ', FG_DEFAULT, BG_DEFAULT,
                                               TEXT_DEFAULT])

    def _init_platform_config(self):
        """
        Read platform specific config
        """
        SUT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  r"system_configuration.ini")
        config = lib_parse_config.ParseConfig()
        section = config.get_value(SUT_CONFIG, 'SUT_Config', 'SUT_TYPE')
        section += '_BIOS_Display'

        # internal alias
        def _get_value(key):
            return config.get_value_with_type(SUT_CONFIG, section, key)

        def _get_tri_attribute(key):
            ret = []
            atr = _get_value(key)
            try:
                ret.append(FG_INV[atr[0]])
                ret.append(BG_INV[atr[1]])
                ret.append(TEXT_INV[atr[2]])
            except KeyError as e:
                write_log(lib_constants.LOG_ERROR,
                          "Some attribute not legal: %s, please check" % atr,
                          self._tc_id,
                          self._script_id,
                          loglevel=self._loglevel)
                raise e
            except IndexError as e:
                write_log(lib_constants.LOG_ERROR,
                          "Please give three attributes: %s" % atr,
                          self._tc_id,
                          self._script_id,
                          loglevel=self._loglevel)
                raise e
            return ret

        self._width = _get_value('width')
        self._height = _get_value('height')

        highlight = _get_tri_attribute('highlight')
        self._highlight_fg = highlight[0]
        self._highlight_bg = highlight[1]
        highlight_popup = _get_tri_attribute('highlight_popup')
        self._highlight_popup_fg = highlight_popup[0]
        self._highlight_popup_bg = highlight_popup[1]
        scroll = _get_tri_attribute('scroll')
        self._page_fg = scroll[0]
        self._page_bg = scroll[1]
        selectable = _get_tri_attribute('selectable')
        self._selectable_fg = selectable[0]
        self._selectable_bg = selectable[1]
        disable = _get_tri_attribute('disable')
        self._disable_fg = disable[0]
        self._disable_bg = disable[1]
        self._disable_text = disable[2]
        self._default_bg = BG_INV[_get_value('default_bg')]
        self._home_footer_bg = BG_INV[_get_value('home_footer_bg_color')]
        subtitle = _get_tri_attribute('subtitle')
        self._subtitle_fg = subtitle[0]
        self._subtitle_bg = subtitle[1]

        self._header_beg = _get_value('header_beg')
        self._header_end = _get_value('header_end')
        self._value_beg = _get_value('value_beg')
        self._des_beg = _get_value('des_beg')
        self._footer_beg = self._height - 5
        self._footer_end = self._height

        self._scroll_down_char = _get_value('scroll_down_char')
        self._scroll_up_char = _get_value('scroll_up_char')

        self._header_regex_top = re.compile(_get_value('header_regex_top'))
        self._header_regex_mid = re.compile(_get_value('header_regex_mid'))
        self._header_regex_bottom = re.compile(_get_value('header_regex_bottom'))
        self._footer_regex_top = re.compile(_get_value('footer_regex_top'))
        self._footer_regex_mid = re.compile(_get_value('footer_regex_mid'))
        self._footer_regex_bottom = re.compile(_get_value('footer_regex_bottom'))
        self._popup_regex_top = re.compile(_get_value('popup_regex_top'))
        self._popup_regex_mid = re.compile(_get_value('popup_regex_mid'))
        self._popup_regex_bottom = re.compile(_get_value('popup_regex_bottom'))

    def _init_screen_info(self):
        """
        Function Name       : _init_screen_info()
        Parameters          : None
        Functionality       : Initialize _screen_info
                              _screen_info each row describe a row in screen,
                              maintain a list of ScreenItem.
                              ex:
                                [
                                    [
                                        ("Press <Enter> to ", 0, 10, 37, 40),
                                        ("      ", 10, 80, 30, 47)
                                    ]
                                    [ScreenItem0, ScreenItem1]
                                ]
        Function Invoked    : None
        Return Value        : None
        """
        if self._screen_info is not None:
            self._screen_info.clear()
        else:
            self._screen_info = []

        for _ in range(self._height):
            self._screen_info.append([])

    def clean_screen_data(self):
        """
        Function Name       : clean_screen_data()
        Parameters          : None
        Functionality       : Initialize _screen_info and _char_matrix
        Function Invoked    : ScreenParser._init_screen_info()
                              ScreenParser._init_char_matrix()
        Return Value        : None
        """
        self._init_screen_info()
        self._init_char_matrix()

    def feed(self, byte_input):
        """
        Function Name       : feed()
        Parameters          : byte_input: vt100 formated serial output
                                         type: Bytes or list(Bytes)
        Functionality       : Feed serial input to pyte or other vt100 parser,
                              parse the return into _screen_info
        Function Invoked    : pyte.stream.feed()
                              ScreenParser._parse_screen()
        Return Value        : None
        """
        def _unicode_replace(_byte):
            # workaround for PC_ANSI terminal type
            # replace unreadable character to readale VT100 terminal format
            _d = {
                b'\xbf': b'\\',
                b'\xd9': b'/',
                b'\xc0': b'\\',
                b'\xb3': b'|',
                b'\xc4': b'-',
                b'\xda': b'/',
                b'\x10': b'>',
                b'\x18': b'^',
                b'\x19': b'v'
            }
            for k, v in _d.items():
                _byte = _byte.replace(k, v)
            return _byte
        self._buff = []
        if isinstance(byte_input, bytes):
            byte_input = [byte_input]
        if isinstance(byte_input, list):
            for inputs in byte_input:
                inputs = _unicode_replace(inputs)
                inputs = _parse_without_esc(inputs, self._buff)
                self._buff.extend(self._debug_screen.serial_output_split(inputs))

        if self._buff:
            self._parse_screen()

    def get_whole_page(self):
        """
        Function Name       : get_whole_page()
        Parameters          : None
        Functionality       : parse serial input,
                              return whole screen in list(str)
        Function Invoked    :
        Return Value        :
                              [
                                "/---------------------------------\" # line 0
                                "|     Config TDP Configurations   |" # line 1
                                "\---------------------------------/" # line 2
                              ]
        """
        page = []
        for i in range(self._height):
            content = self._get_row_content(i)
            page.append(content)

        return page

    def get_selectable_page(self):
        """
        Function Name       : get_selectable_page()
        Parameters          : None
        Functionality       : parse self._screen_info,
                              return all the selectable formated BIOS info.
        Function Invoked    : ScreenParser._get_whole_page_info(),
        Return Value        :
           dict{
               "entries":[
                 # ("entry_txt", EntryType),
                 ("> Advanced", EntryType.MENU)
                 ("Intel(R) Virtualization Technology    <Disabled>",
                   EntryType.DROP_DOWN),
                 ("L3 Cache RAM                22528KB  |   22528KB   ",
                   EntryType.SELECTABLE_TXT)
               ]
               "title": "str"
               "description": "str"
               "highlight_idx": int # index of highlighed entry
               "is_scrollable_up": boolean
               "is_scrollable_down": boolean
               "is_dialogue_box": boolean
           }
        """
        page = self._get_whole_page_info(selectable_only=True, kv_sep=True)
        return page

    def get_value_by_key(self, key):
        """
        Function Name       : get_value_by_key()
        Parameters          : key
        Functionality       : Get all value with certain key.
                              If is popup menu, return empty list
        Function Invoked    : _get_whole_page_info()
        Return Value        : list(str)
        """
        values = []
        page = self._get_whole_page_info(selectable_only=False, kv_sep=True)
        if page["is_popup"]:
            return values
        for entry in page["entries"]:
            if len(entry) != 3:
                continue
            k, v, t = entry
            if key.upper() in k.strip().upper():
                values.append(v.strip())
        return values

    def _get_whole_page_info(self, selectable_only=True, kv_sep=False):
        """
        Function Name       : _get_whole_page_info()
        Parameters          : selectable_only: If set, the entries in page_ret["entries"]
                                    only contain entry of selectable type.
                                    Otherwise, will include all types.
                              kv_sep: If set, the returned entry will formatted in
                                    (key, value, type). Otherwise will be (key+value, type).
        Functionality       : Parse the whole page and return dict as get_selectable_page.
        Function Invoked    : ScreenParser._init_page_dict(),
                              ScreenParser._init_header(),
                              ScreenParser._init_footer(),
                              ScreenParser._init_workspace(),
                              ScreenParser._popup_parse(),
                              ScreenParser._non_popup_parse()
        Return Value        : Same as get_selectable_page()
        """
        page_ret = {}
        # init return dict
        self._init_page_dict(page_ret)
        # check if data is enough to parse
        if not self._check_screen_available():
            write_log(lib_constants.LOG_WARNING,
                      "no screen data, return empty dict",
                      self._tc_id,
                      self._script_id,
                      loglevel=self._loglevel)
            return page_ret

        self._init_header(page_ret)
        self._init_footer()
        self._init_workspace()

        # all dict value set done in this self._popup_parse
        if not self._popup_parse(page_ret):
            self._non_popup_parse(page_ret, selectable_only, kv_sep)
        return page_ret

    def _check_screen_available(self):
        """
        check if empty row in screen
        if empty return False
        """
        for items in self._screen_info:
            if not items:
                return False
        return True

    def _init_page_dict(self, page):
        page["entries"] = []
        page["title"] = None
        page["description"] = None
        page["highlight_idx"] = None
        page["is_scrollable_up"] = False
        page["is_scrollable_down"] = False
        page["is_dialog_box"] = False
        page["is_popup"] = False

    def _init_header(self, page_ret):
        """
            Set self.header_beg, self.header_end, return title.
            If no header return None.
            Match /--------\ for header_beg in the first 6 rows,
            if not matched set to default [0, 6).
            Then match \--------/ for header_end at row header_beg + 2.
        """
        title = None
        search_beg = self._header_beg
        search_end = self._header_end
        # header may not start from the first row
        for i in range(search_beg, search_end):
            top = self._get_row_content(i)
            match = re.match(self._header_regex_top, top)
            if match:
                self._header_beg = i
                mid = self._get_row_content(i+1)
                match = re.match(self._header_regex_mid, mid)
                if match:
                    title = match.group(1).strip()
                else:
                    write_log(lib_constants.LOG_WARNING,
                              "no tilte after header top, leave it None",
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
                bottom = self._get_row_content(i+2)
                match = re.match(self._header_regex_bottom, bottom)
                if match:
                    self._header_end = i + 3
                    break
                else:
                    write_log(lib_constants.LOG_WARNING,
                              "header has no bottom, use default",
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
        else:
            # maybe home page
            write_log(lib_constants.LOG_DEBUG,
                      "header regex not matched, use default config",
                      self._tc_id,
                      self._script_id,
                      loglevel=self._loglevel)

        page_ret["title"] = title

    def _init_footer(self):
        """
            set self._footer_beg and self._footer_end,
            indicate the begin row number and end row number of footer
            first match /-----------------\
            if not matched, match black bg
        """
        bottom_set = False
        # reverse iterate, from bottom up, regex match
        for idx in reversed(range(self._height)):
            content = self._get_row_content(idx)
            if not bottom_set:
                # if footer bottom not found till default footer begin
                if idx < self._footer_beg:
                    write_log(lib_constants.LOG_DEBUG,
                              "footer bottom \"{}\" not matched,"
                              " change scheme to match"
                              " color".format(self._footer_regex_bottom),
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
                    break

                match = re.match(self._footer_regex_bottom, content)
                if match:
                    self._footer_end = idx + 1
                    bottom_set = True
            else:
                if idx < self._footer_end - 5:
                    write_log(lib_constants.LOG_WARNING,
                              "footer begin not found in 5 lines"
                              "before footer end, use default",
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
                    break

                match = re.match(self._footer_regex_top, content)
                if match:
                    self._footer_beg = idx
                    break

        if not bottom_set:
            # change to match color, for home page
            # if all bg color are black it's footer
            for idx in reversed(range(self._height)):
                if not bottom_set:
                    if idx < self._footer_beg:
                        write_log(lib_constants.LOG_WARNING,
                                  "footer not found, use default config",
                                  self._tc_id,
                                  self._script_id,
                                  loglevel=self._loglevel)
                        break

                    if self._check_row_fg_bg_text(idx,
                                                  bg=self._home_footer_bg):
                        bottom_set = True
                        self._footer_end = idx + 1
                else:
                    if idx < self._footer_end - 7:
                        write_log(lib_constants.LOG_WARNING,
                                  "footer begin not found in 7 lines"
                                  " before footer end, use default",
                                  self._tc_id,
                                  self._script_id,
                                  loglevel=self._loglevel)
                        break
                    if self._check_row_fg_bg_text(idx,
                                                  bg=self._home_footer_bg):
                        # still footer
                        continue
                    else:
                        self._footer_beg = idx + 1
                        break

    def _init_workspace(self):
        self._workspace_beg = self._header_end
        self._workspace_end = self._footer_beg
        if self._workspace_beg >= self._workspace_end:
            raise ScreenParserError("no workspace")

    def _check_row_fg_bg_text(self, idx, fg=None, bg=None,
                              text=None, beg=0, end=None):
        """
        Check if row[beg:end] is all in fg, bg color, text attribute.
        If one char not in the given format, return False
        Only check the given parameter
        """
        if end is None:
            end = self._width
        # if empty return False
        if not self._screen_info[idx]:
            return False
        for item in self._screen_info[idx]:
            # make sure item in [beg, end)
            if item.beg < end and item.end > beg:
                if fg is not None and item.fg_color != fg:
                    return False
                elif bg is not None and item.bg_color != bg:
                    return False
                elif text is not None and item.text != text:
                    return False
        return True

    def _check_exist_row_fg_bg_text(self, idx, fg=None, bg=None, text=None,
                                    beg=0, end=None, non_whitespace=True):
        """
        Check if row[beg:end] exist at least one char in fg, bg color
        and text attribute.
        Only check the given parameter.
        If non_whitespace set, check visible char in those format.
        """
        if end is None:
            end = self._width
        for item in self._screen_info[idx]:
            if item.beg < end and item.end > beg:
                fg_flag = True
                bg_flag = True
                text_flag = True
                non_whitespace_flag = True
                if fg is not None and item.fg_color != fg:
                    fg_flag = False
                if bg is not None and item.bg_color != bg:
                    bg_flag = False
                if text is not None and item.text != text:
                    text_flag = False
                if non_whitespace:
                    # check the real visible non-whitespace char.
                    _beg = max(0, beg-item.beg)
                    _end = min(end, item.end) - item.beg
                    non_whitespace_flag = item.content[_beg: _end].strip()
                if fg_flag and bg_flag and text_flag and non_whitespace_flag:
                    return True
        return False

    def _check_exist_disable(self, idx, beg=0, end=None, non_whitespace=True):
        # wrapper of _check_exist_row_fg_bg_text()
        return self._check_exist_row_fg_bg_text(idx,
                                                fg=self._disable_fg,
                                                bg=self._disable_bg,
                                                text=self._disable_text,
                                                beg=beg,
                                                end=end,
                                                non_whitespace=non_whitespace)

    def _check_exist_highlight(self, idx, beg=0,
                               end=None, non_whitespace=True):
        # wrapper of _check_exist_row_fg_bg_text()
        return self._check_exist_row_fg_bg_text(idx,
                                                fg=self._highlight_fg,
                                                bg=self._highlight_bg,
                                                beg=beg,
                                                end=end,
                                                non_whitespace=non_whitespace)

    def _check_exist_highlight_popup(self, idx, beg=0,
                                     end=None, non_whitespace=True):
        # wrapper of _check_exist_row_fg_bg_text()
        return self._check_exist_row_fg_bg_text(idx,
                                                fg=self._highlight_popup_fg,
                                                bg=self._highlight_popup_bg,
                                                beg=beg,
                                                end=end)

    def _popup_parse(self, page_ret):
        """
            parse if is pop up, return boolean
            If True, fill the page_ret
        """
        popup_beg = 0
        popup_end = 0
        col_beg = 0
        col_end = 0
        entries = []
        """
        In case that two dialog box overlapped, search for the last one,
        always find the last /----------\
        /------------------------------------\
        |  /------------------------------\  |
        |  |                              |  |
        |12|Please enter enough characters|  |
        |  |    Press ENTER to continue   |  |
        \--|                              |--/
           \------------------------------/
        """
        for idx in range(self._workspace_beg, self._workspace_end):
            content = self._get_row_content(idx)
            match = re.search(self._popup_regex_top, content)
            if match:
                # get col_beg and col_end by re.search, get area
                popup_beg = idx
                col_beg = match.span()[0]
                col_end = match.span()[1]
                scroll = match.group(1)
                # in case background dialog box can scroll up
                # but the foreground one cannot
                # assign a new value every time
                page_ret["is_scrollable_up"] = scroll == self._scroll_up_char

        # popup beg not found
        if popup_beg == 0:
            return False

        # start from last begining to search mid and end
        for idx in range(popup_beg+1, self._workspace_end):
            # match mid till end
            # check every row for highlight
            content = self._get_row_content(idx)
            mid_match = re.search(self._popup_regex_mid, content)
            if mid_match:
                # using the beginning to set col_beg and col_end
                # to get the content of dialog box
                # better not strip, for input popup box
                txt = content[col_beg+1: col_end-1]
                # Currently, only check if highlight color exist
                if self._check_exist_highlight_popup(idx,
                                                     col_beg,
                                                     col_end):
                    page_ret["highlight_idx"] = len(entries)
                # check bg color black, or bg color white for input box
                # if bg color is white but content is all space, is empty input box
                if self._check_exist_row_fg_bg_text(idx,
                                                    bg=self._highlight_bg,
                                                    beg=col_beg,
                                                    end=col_end,
                                                    non_whitespace=False) or \
                        self._check_exist_row_fg_bg_text(idx,
                                                         bg=self._default_bg,
                                                         beg=col_beg,
                                                         end=col_end,
                                                         non_whitespace=False):
                    entries.append((txt, '', EntryType.INPUT_BOX))
                else:
                    entries.append((txt, '', EntryType.SELECTABLE_TXT))

            else:
                end_match = re.search(self._popup_regex_bottom, content)
                if end_match:
                    popup_end = idx + 1
                    scroll = end_match.group(1)
                    if scroll == self._scroll_down_char:
                        page_ret["is_scrollable_down"] = True
                    break
                else:
                    write_log(lib_constants.LOG_WARNING,
                              "popup menu mid break, ignore",
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)

        if entries and page_ret["highlight_idx"] is None:
            # not an option popup, maybe dialog box
            # define dialog box, disable_txt and inputbox
            # iterate again, change selectable txt to disable txt
            page_ret["is_dialog_box"] = True
            for i in range(len(entries)):
                if entries[i][-1] == EntryType.SELECTABLE_TXT:
                    entries[i] = (entries[i][0], entries[i][1], EntryType.DISABLE_TXT)
                else:
                    pass

        if popup_end == 0:
            write_log(lib_constants.LOG_WARNING,
                      "popup begin, but end not found, ignore",
                      self._tc_id,
                      self._script_id,
                      loglevel=self._loglevel)
        else:
            page_ret["entries"] = entries

        page_ret["is_popup"] = True
        return True

    def _non_popup_parse(self, page_ret, selectable_only=True, kv_sep=False):
        """
        parse non popup, fill the page_ret dict
        TODO: for a highlighted entry more than 1 row
        return as one entry
        """
        page_ret["is_scrollable_up"] = self._is_scrollable_up()
        page_ret["is_scrollable_down"] = self._is_scrollable_down()
        entries = []
        # skip the scroll up/down char row
        entry_beg = self._workspace_beg + 1
        entry_end = self._workspace_end - 1
        idx = entry_beg
        highlight_idx = None
        desc_full = ""
        # in this while loop, idx may add more than 1 in one loop
        # for one entry may take two or more lines,
        # will add idx in self._get_complete_kv_thru_rows
        # so get description in another method
        while idx < entry_end:
            entry_type = EntryType.UNKNOWN
            content = self._get_row_content(idx)
            key = content[:self._value_beg]
            value = content[self._value_beg:self._des_beg]
            desc = content[self._des_beg:]
            # empty line
            if not content.strip():
                pass

            if self._check_exist_highlight(idx,
                                           beg=0,
                                           end=self._des_beg,
                                           non_whitespace=False):
                # in case highlight entries take more than one line
                if highlight_idx is None:
                    highlight_idx = len(entries)

            # for key extend to value area, attach value directly without space
            kv = key + value

            # disable text, fg black, bg white
            # may split two lines disable options or checkbox type, no matter
            # if a row exist disable format char, consider it disable
            # assume no circumstances like disable key but selectable value or
            # disable value and selectable key
            if self._check_exist_disable(idx, beg=0, end=self._des_beg):
                # non-selectable
                key, value, desc, idx = self._get_complete_kv_thru_rows(idx, is_disable=True)
                entry_type = EntryType.DISABLE_TXT
            # subtitle
            elif self._check_exist_row_fg_bg_text(idx,
                                                  fg=self._subtitle_fg,
                                                  bg=self._subtitle_bg,
                                                  beg=0,
                                                  end=self._value_beg):
                # non-selectable
                entry_type = EntryType.SUBTITLE
            # menu start with >, take it no more than one line
            elif key.strip().startswith('> '):
                entry_type = EntryType.MENU
                key = kv
                value = ''
                if highlight_idx == len(entries):
                    key, desc, idx = self._get_complete_highlight_key_thru_rows(idx)
            # option <>, key may more than one line, value not
            elif value.strip().startswith('<'):
                key, value, desc, idx = self._get_complete_kv_thru_rows(idx)
                kv = key + value
                entry_type = EntryType.DROP_DOWN
            # checkbox/input box, take key may be more than one line, value not
            elif value.strip().startswith('[') and value.strip().endswith(']'):
                key, value, desc, idx = self._get_complete_kv_thru_rows(idx)
                kv = key + value
                if value.strip() == '[ ]':
                    entry_type = EntryType.CHECKBOX_UNCHECKED
                elif value.strip() == '[X]':
                    entry_type = EntryType.CHECKBOX_CHECKED
                else:
                    entry_type = EntryType.INPUT_BOX
            # selectable txt
            elif self._check_exist_row_fg_bg_text(idx,
                                                  fg=self._selectable_fg,
                                                  bg=self._selectable_bg,
                                                  beg=0,
                                                  end=self._value_beg) or \
                    kv.strip():
                """
                1. In some page, long selectable text will take whole row
                rather than break in to multi-lines, which break the key, value format.
                Judge it by (only one whitespace or no whitespace between key value)
                2. Still some platform system info is selectable text, which
                is in key, value format.
                Judge it by (2 whitespace between key and value)

                If 1, return entire row as key.
                If 2, will contencate thru rows.
                """
                if key.strip() and value.strip():
                    if key.endswith('  '):
                        key, value, desc, idx = self._get_complete_kv_thru_rows(idx)
                    else:
                        key = kv
                        value = ''
                        if highlight_idx == len(entries):
                            key, desc, idx = self._get_complete_highlight_key_thru_rows(idx)
                entry_type = EntryType.SELECTABLE_TXT

            if entry_type != EntryType.UNKNOWN:
                if entry_type in SELECTABLE_ENTRY_S or not selectable_only:
                    if kv_sep:
                        entries.append((key.strip(), value.strip(), entry_type))
                    else:
                        entries.append((kv.strip(), entry_type))

            # contencate description
            if desc.strip():
                desc_full += desc

            idx += 1

        page_ret["description"] = desc_full
        page_ret["entries"] = entries
        page_ret["highlight_idx"] = highlight_idx
        pass

    def _get_complete_kv_thru_rows(self, idx, is_disable=False):
        """
        If key or value takes more than 1 row, concatenate it thru rows,
        return complete key, complete value,
        complete description, ending idx inclusive last row
        return key, value, des, idx.
        is_disable: If set, will only concatenate disable_txt.
                    If not set, will not concatenate disable_txt.
        """
        content = self._get_row_content(idx)
        key = content[:self._value_beg].strip()
        value = content[self._value_beg:self._des_beg].strip()
        desc = content[self._des_beg:].strip()
        existence = None
        free_space = self._value_beg - len(content[:self._value_beg].rstrip()) - 3
        free_space = free_space if free_space >= 0 else 0

        idx += 1
        # skip the scroll down char
        while idx < self._workspace_end - 1:
            content = self._get_row_content(idx)
            _key = content[:self._value_beg].strip()
            _value = content[self._value_beg:self._des_beg].strip()
            _desc = content[self._des_beg:].strip()
            # menu is not supposed to take 2 row, for now
            if _key.startswith('> '):
                break
            # is_disable is false, break at disable text
            elif not is_disable and self._check_exist_disable(idx, beg=0, end=self._des_beg):
                break
            # is_disable is true, break at selectable text
            elif is_disable and not self._check_exist_disable(idx, beg=0, end=self._des_beg):
                break
            elif not _key and not _value:
                break
            elif _key and _value:
                break
            elif _key and not _value:
                if len(_key.split()[0]) > free_space:
                    free_space = self._value_beg - len(content[:self._value_beg].rstrip()) - 3
                    free_space = free_space if free_space >= 0 else 0
                else:
                    break

                if existence is None:
                    existence = "key"
                elif existence == "key":
                    pass
                else:
                    write_log(lib_constants.LOG_WARNING,
                              "independent value(%s)"
                              " following independent key" % _value,
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
                    break
                key += ' ' + _key
            else:
                # not _key and _value
                if existence is None:
                    existence = "value"
                elif existence == "value":
                    pass
                else:
                    # independent key following independent value
                    break
                value += ' ' + _value
            # concatencate description
            if _desc.strip():
                desc += ' ' + _desc
            idx += 1

        idx -= 1
        return key, value, desc, idx

    def _get_complete_highlight_key_thru_rows(self, idx):
        """
        If highlighted key takes more than 1 row, concatenate it thru rows,
        return complete key, complete description, ending idx inclusive last row
        return key, des, idx.
        """
        content = self._get_row_content(idx)
        key = content[:self._des_beg]
        cur_key = key
        desc = content[self._des_beg:]
        idx += 1
        # skip the scroll down char
        while idx < self._workspace_end - 1:
            if self._check_exist_highlight(idx,
                                           beg=0,
                                           end=self._des_beg,
                                           non_whitespace=False):
                next_content = self._get_row_content(idx)
                next_key = next_content[:self._des_beg]
                if len(cur_key.rstrip()) == self._des_beg:
                    key = key.strip() + next_key.strip()
                else:
                    key = key.strip() + ' ' + next_key.strip()
                cur_key = next_key
                idx += 1
            else:
                break
        idx -= 1
        return key, desc, idx

    def _is_scrollable_up(self):
        # check if ^ exist after header, and in color page_fg, page_bg
        row_no = self._workspace_beg
        content = self._get_row_content(row_no)
        idx = content.find(self._scroll_up_char)
        if idx != -1:
            if self._check_row_fg_bg_text(row_no,
                                          fg=self._page_fg,
                                          bg=self._page_bg,
                                          beg=idx,
                                          end=idx+1):
                return True

        return False

    def _is_scrollable_down(self):
        # check if v exist before footer, and in color page_fg, page_bg
        row_no = self._workspace_end - 1
        content = self._get_row_content(row_no)
        idx = content.find(self._scroll_down_char)
        if idx != -1:
            if self._check_row_fg_bg_text(row_no,
                                          fg=self._page_fg,
                                          bg=self._page_bg,
                                          beg=idx,
                                          end=idx+1):
                return True

        return False

    def _merge_screen_info(self):
        """
        merge the _char_matrix to _screen_info, for following process
        """
        for i in range(len(self._char_matrix)):
            new_row = []
            item0 = self.ScreenItem(self._char_matrix[i][0][COLUMN_CONTENT],
                                    0,
                                    1,
                                    self._char_matrix[i][0][COLUMN_FG],
                                    self._char_matrix[i][0][COLUMN_BG],
                                    self._char_matrix[i][0][COLUMN_TEXT])
            for j in range(1, len(self._char_matrix[i])):
                if(item0.fg_color == self._char_matrix[i][j][COLUMN_FG] and
                        item0.bg_color == self._char_matrix[i][j][COLUMN_BG] and
                        item0.text == self._char_matrix[i][j][COLUMN_TEXT]):
                    item0.content += self._char_matrix[i][j][COLUMN_CONTENT]
                    item0.end = j + 1
                else:
                    new_row.append(item0)
                    item0 = self.ScreenItem(self._char_matrix[i][j][COLUMN_CONTENT],
                                            j,
                                            j + len(self._char_matrix[i][j][COLUMN_CONTENT]),
                                            self._char_matrix[i][j][COLUMN_FG],
                                            self._char_matrix[i][j][COLUMN_BG],
                                            self._char_matrix[i][j][COLUMN_TEXT])
            new_row.append(item0)
            self._screen_info[i] = new_row

    def _insert_screen_info(self, row, new_item):
        """
        Insert into a char matrix, maintain all the char attribute
        including fg, bg, text
        """
        if row >= self._height:
            msg = "row number:%s > screen height:%s,"\
                  " please check configuration" % (row+1, self._height),
            write_log(lib_constants.LOG_ERROR,
                      msg,
                      self._tc_id,
                      self._script_id,
                      loglevel=self._loglevel)
            raise ScreenParserError(msg)
        if new_item.end > self._width:
            # overflow, discard, ecountered such circumstance
            new_item.end = self._width
        for i in range(new_item.beg, new_item.end):
            self._char_matrix[row][i][COLUMN_CONTENT] = new_item.content[i-new_item.beg]
            self._char_matrix[row][i][COLUMN_FG] = new_item.fg_color
            self._char_matrix[row][i][COLUMN_BG] = new_item.bg_color
            self._char_matrix[row][i][COLUMN_TEXT] = new_item.text

    def _parse_screen(self):
        """
        Function Name       : _parse_screen()
        Parameters          : None
        Functionality       : Parse _buff to _screen_info by pyte regulation,
                              only support three APIs now.
                              ex:
                                  ["cursor_position", [1, 1], {}]
                                  ["select_graphic_rendition", [37], {}]
                                  ["draw", ["Press <Enter> to "], {}]
                              Ignore if other functions showed up.
                              All terms respect the pyte naming rules.
        Function Invoked    : ScreenParser._insert_screen_info(),
                              ScreenParser._merge_screen_info()
        Return Value        : None
        """
        beg = -1
        row = -1
        for event in self._buff:
            e_name_s = event.name
            e_args_l = event.param
            # e_kwargs_d = event[2]

            if e_name_s == "display_attributes":
                assert len(e_args_l) == 1, 'select_graphic_rendition param num not 1'
                cur = e_args_l[0]
                if cur == 0:
                    self.cur_fg = FG_DEFAULT
                    self.cur_bg = BG_DEFAULT
                    self.cur_text_attribute = TEXT_DEFAULT
                elif cur in FG:
                    self.cur_fg = cur
                elif cur in BG:
                    self.cur_bg = cur
                elif cur in TEXT:
                    # TODO: pending to implement +/-
                    self.cur_text_attribute = cur
                else:
                    write_log(lib_constants.LOG_WARNING,
                              "display attribute not found: {},"
                              " ignore".format(cur),
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
            elif e_name_s == "cursor_position_start":
                assert len(e_args_l) == 2, 'cursor_position para num not 2'
                row = e_args_l[0] - 1  # convert start from 1 to 0
                beg = e_args_l[1] - 1
            elif e_name_s == "draw":
                assert len(e_args_l) == 1, 'draw param number error'
                if beg == -1 or row == -1:
                    continue

                # '\n' is not expected in BIOS setup,
                # but still seen, ignore the '\n'
                content = e_args_l[0].replace('\n', '')
                if not content:
                    continue

                # rough work around to strip debug message from debug IFWI,
                # current string 'EC Command' has been found to be appended
                # to the end of BIOS data, stripped it
                if 'EC Command' in content:
                    content = content.split('EC Command')[0]

                item = self.ScreenItem(content,
                                       beg, beg+len(content),
                                       self.cur_fg,
                                       self.cur_bg,
                                       self.cur_text_attribute)
                self._insert_screen_info(row, item)
                # look into cursor set methodology here.
                # cursor moved as draw
                beg += len(content)
            else:
                write_log(lib_constants.LOG_WARNING,
                          "function {} not support,"
                          " ignore".format(e_name_s),
                          self._tc_id,
                          self._script_id,
                          loglevel=self._loglevel)
                pass
        self._merge_screen_info()

    def _get_row_content(self, row_no):
        """
        get whole row content text
        """
        content = ""
        row = self._screen_info[row_no]
        for item in row:
            content += item.content
        return content

    def print_screen_info_debug(self):
        """
        For debug, will not submit to code repo
        """
        for row in self._screen_info:
            print(row)

    def print_screen_txt(self):
        """
        Print screen with plain text
        """
        for i in range(len(self._screen_info)):
            print(self._get_row_content(i))

    def print_screen_colored(self):
        """
        Print screen with ANSI color scheme
        Not all terminal supported
        """
        # A workaround for win prompt cmd
        if os.name == 'nt':
            os.system('color')
        for row in self._screen_info:
            for item in row:
                fg = FG[item.fg_color]
                fg = fg.replace('default', 'white')
                fg = fg.replace('black', 'grey')
                fg = fg.replace('brown', 'yellow')
                bg = BG[item.bg_color]
                bg = bg.replace('default', 'black')
                bg = bg.replace('black', 'grey')
                bg = bg.replace('brown', 'yellow')
                bg = 'on_' + bg
                attrs = []
                # only use bold attr, hardcoded, pending to support others
                if item.text == 1:
                    attrs.append('bold')
                cprint(item.content, fg, bg, attrs=attrs, end='')
            print('')


def write_log(level, msg, test_case_id, script_id, toolname='None',
              info_fetched="None", loglevel="ALL", tbd="None"):
    print(msg)


class ScreenParserMEBx(ScreenParser):
    """
    Inherited from ScreenParser used for MBEx setup only.
    For some config difference and UI elements difference.
    """
    def _init_platform_config(self):
        super()._init_platform_config()
        SUT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  r"system_configuration.ini")
        config = lib_parse_config.ParseConfig()
        section = 'MEBx_Display'

        self._value_beg = config.get_value_with_type(SUT_CONFIG, section, 'value_beg')
        self._des_beg = config.get_value_with_type(SUT_CONFIG, section, 'des_beg')

        selectable = config.get_value_with_type(SUT_CONFIG, section, 'selectable')
        self._selectable_fg = FG_INV[selectable[0]]
        self._selectable_bg = BG_INV[selectable[1]]

        subtitle = config.get_value_with_type(SUT_CONFIG, section, 'subtitle')
        self._subtitle_fg = FG_INV[subtitle[0]]
        self._subtitle_bg = BG_INV[subtitle[1]]

        popup_bg = config.get_value_with_type(SUT_CONFIG, section, 'popup_bg')
        self._popup_bg = BG_INV[popup_bg]

    def _get_first_last_bg(self, idx, bg):
        items = [item for item in self._screen_info[idx] if item.bg_color == bg]
        if not items:
            return 0, 0
        return items[0].beg, items[-1].end

    def _popup_parse(self, page_ret):
        # MBEx popup may not have rim like /------\, only blue background
        # Take blue background as popup also
        if super()._popup_parse(page_ret):
            return True

        row_beg = 0
        row_end = 0
        col_beg = 0
        col_end = 0
        entries = []

        # search for popup begin by background color
        for i in range(self._workspace_beg, self._workspace_end):
            col_beg, col_end = self._get_first_last_bg(i, self._popup_bg)
            if col_end > col_beg:
                row_beg = i
                break

        if row_beg == 0:
            return False

        # search for popup end by background color
        for i in range(row_beg, self._workspace_end):
            beg, end = self._get_first_last_bg(i, self._popup_bg)
            if beg == col_beg and end == col_end:
                continue
            else:
                row_end = i
                if end > beg:
                    write_log(lib_constants.LOG_ERROR,
                              "popup width not consistent row {}".format(i+1),
                              self._tc_id,
                              self._script_id,
                              loglevel=self._loglevel)
                break

        for idx in range(row_beg, row_end):
            content = self._get_row_content(idx)
            txt = content[col_beg+1: col_end-1]
            # Currently, only check if highlight color exist
            if self._check_exist_highlight_popup(idx,
                                                 col_beg,
                                                 col_end):
                page_ret["highlight_idx"] = len(entries)
            # check bg color black, or bg color white for input box
            # if bg color is white but content is all space, is empty input box
            if self._check_exist_row_fg_bg_text(idx,
                                                bg=self._highlight_bg,
                                                beg=col_beg,
                                                end=col_end,
                                                non_whitespace=False) or \
                    self._check_exist_row_fg_bg_text(idx,
                                                     bg=self._default_bg,
                                                     beg=col_beg,
                                                     end=col_end,
                                                     non_whitespace=False):
                entries.append((txt, '', EntryType.INPUT_BOX))
            else:
                entries.append((txt, '', EntryType.SELECTABLE_TXT))

        if entries and page_ret["highlight_idx"] is None:
            page_ret["is_dialog_box"] = True
            for i in range(len(entries)):
                if entries[i][-1] == EntryType.SELECTABLE_TXT:
                    entries[i] = (entries[i][0], entries[i][1], EntryType.DISABLE_TXT)
                else:
                    pass

        page_ret["entries"] = entries
        return True


if __name__ == '__main__':
    s = []
    for i in range(48):
        with open('./SoftwareAbstractionLayer/parser/tgl/{}.txt'.format(i), 'rb') as f:
            s.append(f.read())

    screenParser = ScreenParser()
    for i in range(48):
        print("------------------------------------------------{}---------"
              "-----------------------------------------------".format(i))
        screenParser.feed(s[i])
        # screenParser.print_screen_info_debug()
        # screenParser.print_screen_txt()
        screenParser.print_screen_colored()
        ret = screenParser.get_selectable_page()
        screenParser.get_value_by_key("Processor 1 version")
        print(ret)

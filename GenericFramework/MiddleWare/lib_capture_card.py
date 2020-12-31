import subprocess
import re

"""This function is used to take screenshots. Before calling, make sure the
zip file of ffmpeg has been unzipped and the path of ffmpeg has been added
to the environment variable"""


def capture_with_card(capture_card_name, target_img_path):
    """Capture the screen with capture card
    :param capture_card_name: capture card name,
                              get from DeviceManager-Cameras.
                        type: string;
    :param target_img_path: save path of the capture image. The Image format
                            can be .jpg or .png.
                        type: string
    :return: True if capture successfully, otherwise False
    :raise: ffmpegError
    """

    def log_write(msg):
        print(msg)

    try:
        if capture_card_name == "":
            log_write("error:'capture_card_name' is invalid")
            return False
        if target_img_path == "":
            log_write("error:'target_img_path' is invalid")
            return False
        command_line = 'ffmpeg -y -f dshow -i video="%s" -frames:v 1 %s' \
                       % (capture_card_name, target_img_path)
        proc = subprocess.Popen(command_line, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        """Whether the screenshot is successful or not, the stdout of cmd
        is empty. So need to analyze the stderr."""

        def is_successful(stderr):
            """
            Judge whether the screenshot is successful or not.
            :param stderr: the output of ffmpeg .
                    type: string;
            :return: True if no errors, otherwise False
            """
            # I/O error: include invalid video device, invalid file path.
            io_err = ".*I/O.*error"
            io_err_pattern = re.compile(io_err, flags=re.DOTALL)
            video_err_match = io_err_pattern.findall(stderr)

            # invalid error: output format isn't a image format.
            invalid_err = ".*Invalid argument.*"
            invalid_err_pattern = re.compile(invalid_err, flags=re.DOTALL)
            invalid_err_match = invalid_err_pattern.findall(stderr)
            if len(video_err_match) != 0 or len(invalid_err_match) != 0:
                log_write(stderr)
                return False
            else:
                return True

        return is_successful(err.decode('utf-8'))
    except Exception as e:
        log_write(e)


if __name__ == '__main__':
    capture_with_card('usb3.0 capture video', r'C:\your\image\path.png')

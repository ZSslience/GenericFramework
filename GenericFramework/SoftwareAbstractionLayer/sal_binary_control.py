import os
import shutil


def binctrl_read_bytes(binary_path, bytes_offset, bytes_length):
    """
    Function Name       : binctrl_read_bytes()
    Parameters          : binary_path(str): abs/relevant path of binary file
                          bytes_offset(int): offset addr i.e 0x00000024, 0x24
                          bytes_length(int): target byte(s) length, i.e 1
    Functionality       : Binary read bytes with the offset and length given
    Function Invoked    : os to ensure target file exists and input valid
    Return Value        : return (byte, hex, bin) of bytes read out,
                          otherwise bool: (False, False, False)
    """
    if os.path.exists(binary_path):
        with open(binary_path, 'rb') as buf:
            if bytes_offset < os.path.getsize(binary_path):
                buf.seek(bytes_offset, 0)
                read_bytes = buf.read(bytes_length)
                read_hex = read_bytes.hex()
                read_bit = '{0:08b}'.format(int(read_hex, 16))
                print("%s byte(s) data from offset %s: (byte)%s (hex)%s (bin)%s"
                      % (bytes_length, hex(bytes_offset), read_bytes, 
                         read_hex, read_bit))
                buf.close()
                return (read_bytes, read_hex, read_bit)
    return (False, False, False)


def binctrl_edit_and_save(binary_path, bytes_offset, repl_length,
                          repl_hex_string, suffix="_new"):
    """
    Function Name       : binctrl_edit_and_save()
    Parameters          : binary_path(str): abs/relevant path of binary file
                          bytes_offset(int): offset addr i.e 0x00000024, 0x24
                          repl_length(int): target byte(s) length, i.e 2
                          repl_hex_string(str): replaced hex string, i.e 'fe01'
                          suffix(str): Optional param for new file name suffix
    Functionality       : Generate _new named binary with offset data replaced.
    Function Invoked    : shutil and os to ensure binary generation
    Return Value        : return (str) of new binary path of data replaced,
                          otherwise bool: False
    """
    if os.path.exists(binary_path):
        with open(binary_path, 'rb') as buf:
            if bytes_offset < os.path.getsize(binary_path):
                saved_path = '.'.join(binary_path.split(".")[0:-1]) + suffix +\
                    "." + binary_path.split(".")[-1]
                shutil.copyfile(binary_path, saved_path)
                buf.seek(bytes_offset, 0)
                to_be_edit_bytes = buf.read(repl_length)
                override_bytes = bytes.fromhex(repl_hex_string)
                with open(saved_path, 'rb+') as buf_w:
                    if len(to_be_edit_bytes) == len(override_bytes):
                        print("%s[%s] from offset %s replaced with: %s[%s]" %
                            (to_be_edit_bytes, len(to_be_edit_bytes), 
                             hex(bytes_offset), override_bytes, 
                             len(override_bytes)))
                        buf_w.seek(bytes_offset, 0)
                        print("Save changes to %s" % (saved_path))
                        buf_w.write(bytearray.fromhex(repl_hex_string))
                        buf_w.flush()
                        buf_w.close()
                    else:
                        print("%s not matched target byte(s) length" %
                              (repl_hex_string))
                        return False
                buf.close()
                return saved_path
    return False


def binctrl_search_offset(binary_path, search_bytes):
    """
    Function Name       : binctrl_search_offset()
    Parameters          : binary_path(str): abs/relevant path of binary file
                          search_bytes(byte): byte(s) to be searched
                                              i.e: b'_FIT_' or b'\x00\xff'
    Functionality       : search all matched offsets with the query bytes given
    Function Invoked    : os to ensure target file exists
    Return Value        : return [list] of matched offsets for user to read or
                          edit binary, otherwise bool: False
    """
    if os.path.exists(binary_path):
        with open(binary_path, 'rb') as buf:
            ret_offsets = []
            # prev_offset = 0x0
            start_offset = 0x0
            offset = 0x0
            while offset != -0x1:
                print("Start to search from offset: %s" % hex(start_offset))
                buf.seek(start_offset, 0)
                s = buf.read()
                offset = s.find(search_bytes)
                if offset != -0x1:
                    print("Searched bytes matched offset: %s" % hex(offset))
                    save_offset = start_offset + offset
                    ret_offsets.append(save_offset)
                    # prev_offset = save_offset
                    start_offset = save_offset + len(search_bytes)
                else:
                    print("Searched bytes not matched offset")
                    break
            if len(ret_offsets) > 0:
                print("All %s matched offsets are stored int type list: %s" %
                      (len(ret_offsets), ret_offsets))
                # [hex(i) for i in ret_offsets]))
                return ret_offsets
    return False


if __name__ == "__main__":
    # A demo to enable Intel Test Menu of binary
    bin_path = r"p:\ath\to\binary\file.bin"
    byte_offset = binctrl_search_offset(bin_path, b'ITST')
    binctrl_read_bytes(bin_path, byte_offset[0] + 8, 1)
    binctrl_edit_and_save(bin_path, byte_offset[0] + 8, 2, 'fe00', "_copy")

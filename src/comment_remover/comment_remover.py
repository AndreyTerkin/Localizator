class CommentRemover:
    def __init__(self, text, single_row_sign=None, multi_row_sign_left=None, multi_row_sign_right=None):
        self._text = text
        self._single_row_sign = single_row_sign
        self._multi_row_sign = dict(
            left=multi_row_sign_left,
            right=multi_row_sign_right
        )
        self._deleted_rows_map = {}
        self._deleted_row_fragments = {}

    @property
    def deleted_rows_map(self):
        return self._deleted_rows_map

    @property
    def deleted_row_fragments(self):
        return self._deleted_row_fragments

    def remove_all_comments(self):
        self.remove_multi_row_comment()
        self.remove_single_row_comment()

    def remove_single_row_comment(self):
        rows_to_delete = []
        line_index = 0
        for line in self._text:
            if line.find(self._single_row_sign) >= 0:
                comment_index = line.find(self._single_row_sign)
                if self._check_if_row_is_empty(line, last_index=comment_index):
                    rows_to_delete.append(line_index)
                else:
                    self._store_text_fragment(line_index, comment_index, line[comment_index:])
                    self._text[line_index] = line[:comment_index]
            line_index += 1
        # remove marked lines starting from the end
        rows_to_delete.reverse()
        for index in rows_to_delete:
            self._deleted_rows_map[index] = self._text[index]
            del self._text[index]

    def remove_multi_row_comment(self):
        # TODO: this case will cause code with compile error
        # TODO:     //*
        # TODO:     // bla-bla-bla */ text
        rows_to_delete = []
        is_comment_opened = False
        for line_index in range(0, len(self._text)):
            repeat = True
            while repeat:
                line = self._text[line_index]
                repeat = False
                if not is_comment_opened:
                    open_index = line.find(self._multi_row_sign['left'])
                    if open_index >= 0:
                        close_index = line.find(self._multi_row_sign['right'])
                        if close_index >= 0:
                            self._store_text_fragment(line_index, open_index,
                                                      line[open_index:close_index+len(self._multi_row_sign['right'])])
                            # cut off multi comment in one line
                            self._text[line_index] = line[:open_index] +\
                                                     line[close_index+len(self._multi_row_sign['right']):]
                            repeat = True
                        else:
                            if self._check_if_row_is_empty(line, last_index=open_index):
                                rows_to_delete.append(line_index)
                            else:
                                self._store_text_fragment(line_index, open_index, line[open_index:])
                                self._text[line_index] = line[:open_index]
                            is_comment_opened = True
                elif is_comment_opened:
                    close_index = line.find(self._multi_row_sign['right'])
                    if close_index >= 0:
                        if self._check_if_row_is_empty(line, start_index=close_index+len(self._multi_row_sign['right'])):
                            rows_to_delete.append(line_index)
                        else:
                            self._store_text_fragment(line_index, 0,
                                                      line[:close_index + len(self._multi_row_sign['right'])])
                            self._text[line_index] = line[close_index + len(self._multi_row_sign['right']):]
                            repeat = True
                        is_comment_opened = False
                    else:
                        rows_to_delete.append(line_index)
        # remove marked lines starting from the end
        rows_to_delete.reverse()
        for index in rows_to_delete:
            self._deleted_rows_map[index] = self._text[index]
            del self._text[index]

    def _store_text_fragment(self, row_number, col_number, text):
        if row_number in self._deleted_row_fragments:
            previous_fragments_len = 0
            for fragment in self._deleted_row_fragments[row_number].values():
                previous_fragments_len += len(fragment)
            full_row_col_number = col_number + previous_fragments_len
            self._deleted_row_fragments[row_number][full_row_col_number] = text
        else:
            self._deleted_row_fragments[row_number] = {
                col_number: text
            }

    @staticmethod
    def _check_if_row_is_empty(line, start_index=None, last_index=None):
        if start_index is None:
            start_index = 0
        if last_index is None:
            last_index = len(line)-1

        if start_index >= last_index:
            return True

        line_length = len(line[:last_index])
        if line[start_index:last_index].count(' ') + line[start_index:last_index].count('\t') == line_length:
            return True
        else:
            return False

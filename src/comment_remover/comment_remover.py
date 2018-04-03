from src.comment_remover.multi_line_comment_signs import CommentSign


class CommentRemover:
    def __init__(self,
                 single_row_sign=None,
                 multi_row_sign_left=None,
                 multi_row_sign_right=None):
        self._single_row_sign = single_row_sign
        self._multi_row_signs = [
            {
                CommentSign.Left: multi_row_sign_left,
                CommentSign.Right: multi_row_sign_right
            }
        ]
        self._rows_to_delete = []
        self._deleted_rows_map = {} # row index map to line text in reverse order
        self._deleted_row_fragments = {} # row index map to map of text start index to text

    @property
    def deleted_rows_map(self):
        return self._deleted_rows_map

    @property
    def deleted_row_fragments(self):
        return self._deleted_row_fragments

    def add_multi_row_comment_sign(self, left, right):
        self._multi_row_signs.append({
            CommentSign.Left: left,
            CommentSign.Right: right
        })

    def remove_all_comments(self, text):
        for comment_sign_pair in self._multi_row_signs:
            self.remove_multi_row_comment(text, comment_sign_pair)
        if not self._single_row_sign is None:
            self.remove_single_row_comment(text)
        self.remove_marked_rows(text)

    def remove_single_row_comment(self, text):
        line_index = 0
        for line in text:
            if line.find(self._single_row_sign) >= 0:
                comment_index = line.find(self._single_row_sign)
                if self._check_if_row_is_empty(line, last_index=comment_index):
                    self._add_row_to_remove(line_index)
                else:
                    if line.endswith('\n'):
                        self._store_text_fragment(line_index, comment_index, line[comment_index:-1])
                        text[line_index] = line[:comment_index] + '\n'
                    else:
                        self._store_text_fragment(line_index, comment_index, line[comment_index:])
                        text[line_index] = line[:comment_index]
            line_index += 1

    def remove_multi_row_comment(self, text, comment_sign_pair):
        # TODO: this case will cause code with compile error
        # TODO:     //*
        # TODO:     // bla-bla-bla */ text
        is_comment_opened = False
        for line_index in range(0, len(text)):
            repeat = True
            while repeat:
                line = text[line_index]
                repeat = False
                if not is_comment_opened:
                    open_index = line.find(comment_sign_pair[CommentSign.Left])
                    if open_index >= 0:
                        # TODO: case of '/*/' cause wrong behaviour and memory overflow as a result
                        close_index = line.find(comment_sign_pair[CommentSign.Right])
                        if close_index >= 0:
                            new_line = line[:open_index] +\
                                       line[close_index + len(comment_sign_pair[CommentSign.Right]):]
                            if self._check_if_row_is_empty(new_line):
                                self._add_row_to_remove(line_index)
                            else:
                                # cut off multi comment in one line
                                self._store_text_fragment(line_index, open_index,
                                                          line[open_index:close_index + len(
                                                               comment_sign_pair[CommentSign.Right])])
                                text[line_index] = new_line
                                repeat = True
                        else:
                            if self._check_if_row_is_empty(line, last_index=open_index):
                                self._add_row_to_remove(line_index)
                            else:
                                if line.endswith('\n'):
                                    self._store_text_fragment(line_index, open_index, line[open_index:-1])
                                    text[line_index] = line[:open_index] + '\n'
                                else:
                                    self._store_text_fragment(line_index, open_index, line[open_index:])
                                    text[line_index] = line[:open_index]
                            is_comment_opened = True
                elif is_comment_opened:
                    close_index = line.find(comment_sign_pair[CommentSign.Right])
                    if close_index >= 0:
                        if self._check_if_row_is_empty(line, start_index=close_index+len(comment_sign_pair[CommentSign.Right])):
                            self._add_row_to_remove(line_index)
                        else:
                            self._store_text_fragment(line_index, 0,
                                                      line[:close_index + len(comment_sign_pair[CommentSign.Right])])
                            text[line_index] = line[close_index + len(comment_sign_pair[CommentSign.Right]):]
                            repeat = True
                        is_comment_opened = False
                    else:
                        self._add_row_to_remove(line_index)

    def remove_marked_rows(self, text):
        self._rows_to_delete.sort(reverse=True)
        for index in self._rows_to_delete:
            self._deleted_rows_map[index] = text[index]
            del text[index]

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

    def _add_row_to_remove(self, row_number):
        if not row_number in self._rows_to_delete:
            self._rows_to_delete.append(row_number)

    @staticmethod
    def _check_if_row_is_empty(line, start_index=None, last_index=None):
        if start_index is None:
            start_index = 0
        if last_index is None:
            last_index = len(line)

        if start_index >= last_index:
            return True

        line_length = len(line[start_index:last_index])
        if line[start_index:last_index].count(' ')\
                + line[start_index:last_index].count('\t')\
                + line[start_index:last_index].count('\n')\
                == line_length:
            return True
        else:
            return False

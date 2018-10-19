import re


class LanguageWordsSearcher():
    def __init__(self):
        self._search_pattern = '[а-яА-ЯёЁ]+[0-9\t .,-:!?#$%№(){}«—»/\*]*'

    '''
    Returns dictionary of found text fragments with its start and end indexes:
      key: number of row
      value: list of tuples
        start of fragment,
        end of fragment,
        fragment text
    '''
    def find_all_text_fragments(self, text):
        row_to_fragments_map = {}
        for index in range(0, len(text)):
            line = text[index]
            if not '{0}' in line:
                mapper = self.find_words_in_line(line)
                if len(mapper) != 0:
                    row_to_fragments_map[index] = mapper
        return row_to_fragments_map

    '''
    Returns list of found text fragments with its start and end indexes:
      value: list of tuples
        start of fragment,
        end of fragment,
        fragment text
    '''
    def find_words_in_line(self, line):
        mapper = []
        for match in re.finditer(self._search_pattern, line):
            item = (
                match.start(),
                match.end(),
                match.group()
            )
            mapper.append(item)
        return self._merge_neighbors(mapper)

    def _merge_neighbors(self, mapper):
        merged_mapper = []
        index = 0
        max_index = len(mapper) - 1
        indexes_to_merge = []
        while index <= max_index:
            if index == 0:
                indexes_to_merge.append(index)
                index += 1
                continue

            if mapper[index][0] == mapper[index-1][1]:
                indexes_to_merge.append(index)
            else:
                if len(indexes_to_merge) == 1:
                    merged_mapper.append(mapper[index-1])
                else:
                    merged_mapper.append(self._merge_given_chunks(indexes_to_merge, mapper))
                indexes_to_merge.clear()
                indexes_to_merge.append(index)
            index += 1
        if index == max_index+1 and len(indexes_to_merge) > 0:
            merged_mapper.append(self._merge_given_chunks(indexes_to_merge, mapper))
            indexes_to_merge.clear()
        return merged_mapper

    def _merge_given_chunks(self, indexes_to_merge, mapper):
        text = ''
        for i in indexes_to_merge:
            text += mapper[i][2]
        new_item = (
            mapper[indexes_to_merge[0]][0],
            mapper[indexes_to_merge[-1]][1],
            text
        )
        return new_item


if __name__ == "__main__":
    text = '            <dd>Дата и время отбора: @(variable.Property.InnerProperty?.ToString() ?? "не указана")</dd>\n'
    searcher = LanguageWordsSearcher()
    a = searcher.find_words_in_line(text)
    pass
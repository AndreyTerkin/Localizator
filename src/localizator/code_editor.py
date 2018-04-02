from src.localizator.entity_type import EntityType


class CodeEditor:
    def __init__(self,related_path):
        self._related_path = related_path.replace('\\', '.')
        self._properties = []
        self._entity_type = None
        self._entity_name = None

    _possible_method_modifiers_after_public = [
        'virtual',
        'static',
        'const',
        'override',
        'readonly'
    ]

    @property
    def properties(self):
        return self._properties

    def add_resources_to_entity(self, file, entity_type):
        print('Opening file {0}...'.format(file))
        f = open(file, 'r+', encoding='utf-8-sig')
        text = f.readlines()

        if len(text) == 0:
            print(' File is empty')
            return None

        self._entity_type = entity_type
        any_changes = False
        if self._entity_type == EntityType.Class:
            entity_index, self._entity_name = self._find_entity(text, 'class') # take in account returned status
            any_changes = self._find_and_edit_reference_attribute(text)
            any_changes += self._edit_attributes(text, entity_index, 'Display')
            any_changes += self._edit_attributes(text, entity_index, 'Required')
        else: # self._entity_type == EntityType.ENUM:
            entity_index, self._entity_name = self._find_entity(text, 'enum') # take in account returned status
            any_changes += self._edit_attributes(text, entity_index, 'Description')

        if not any_changes:
            print("  There is nothing to change...")
        else:
            f.seek(0)
            f.truncate()
            for line in text:
                f.write(line)
        # f.close
        print('Resources successfully added to entity code')
        return self._entity_name

    @staticmethod
    def _find_entity(text, type):
        index = 0
        for line in text:
            if type in line:
                words = text[index].split(' ')
                entity_name = words[words.index(type) + 1]
                # cut off extra part one by one to the list and choose the most short
                entity_name = min(list(map(
                    lambda symbol:
                        entity_name[:entity_name.find(symbol)] if entity_name.find(symbol) > 0 else entity_name,
                    ['\n', '\t', ':']
                )))
                return index, entity_name
            index += 1
        return False

    def _find_and_edit_reference_attribute(self, text):
        attr_name = "Reference"
        status, attr_start, attr_end = self._check_resource_usage(text, 0, attr_name)

        if status is None:
            print('  Class {0}: No Reference attribute'.format(self._entity_name))
            return False

        if status is True:
            print('  Class {0}: ResourceType already used in ReferenceAttribute'.format(self._entity_name))
            return False

        # TODO: cover all cases of commenting with /**/
        if text[attr_start].find('//') < text[attr_start].find('[Reference'):
            print('  Class {0}: ReferenceAttribute is commented. Line {1}'.format(self._entity_name, attr_start + 1))
            return False

        # edit attribute name
        ref_name = None
        chunks = text[attr_start].split('"')
        if len(chunks) == 1:
            print('  Class {0}: Reference name already uses strong typed resource name in Reference attribute. Line {1}'
                  .format(self._entity_name, attr_start + 1))
            return False

        for chunk in chunks:
            index = 0
            if attr_name in chunk:
                ref_name = chunks[index + 1]
                break
            index += 1
        self._properties.append(('TableName', ref_name))
        new_name = "nameof(Resources.{0}.{1}/Resource.TableName)".format(self._related_path, self._entity_name)

        empty_space = text[attr_start][:text[attr_start].find('[')]
        parameters = text[attr_start].split(',')
        text[attr_start] = parameters[0]
        for index in range(1, len(parameters), 1):
            text[attr_start + index - 1] += ','
            text.insert(attr_start + index, '\n\t' + empty_space + parameters[index].strip())
            attr_end += 1
        text[attr_start] = text[attr_start].replace("\"{0}\"".format(ref_name), new_name)

        # add reference attribute resource type parameter
        text[attr_end] = text[attr_end].replace(")]", ",")
        text.insert(attr_end + 1, '\n\t' + empty_space + "ResourceType = typeof(Resources.{0}.{1}.Resource))]\n"
                    .format(self._related_path, self._entity_name))
        return True

    def _edit_attributes(self, text, search_start, attrib_name):
        next_line = search_start
        any_changes = False
        while True:
            status, next_line = self._find_and_edit_next_property(text, next_line, attrib_name)
            if next_line == len(text):
                break
            any_changes += status
        return any_changes

    def _find_and_edit_next_property(self, text, current_line, attr_name):
        status, attr_start, attr_end = self._check_resource_usage(text, current_line, attr_name)

        if status is None:
            return False, len(text)

        if status is True:
            print('  {0} {1}: Skipped property because of it\'s already use resources'
                  .format(self._entity_type.name, self._entity_name))
            return False, attr_end + 1

        # TODO: cover all cases of commenting with /**/
        if -1 < text[attr_start].find('//') < text[attr_start].find('[{0}'.format(attr_name)):
            print('  {0} {1}: {2}Attribute is commented. Line {3}'
                  .format(self._entity_type.name, self._entity_name, attr_name, attr_start + 1))
            return False, attr_end + 1

        property_name, offset = self._find_property_name(text, attr_end + 1)
        if property_name is None:
            print('  {0} {1}: Property name not found after {2}Attribute definition. Line {3}'
                  .format(self._entity_type.name, self._entity_name, attr_name, attr_start + 1))
            return False, attr_end + 1

        # TODO: combine
        # TODO: some strange shit happens here!!!
        if attr_name  == 'Required':
            attr_property, required_message, index = self._find_attribute_property(
                text, attr_name, 'ErrorMessage', attr_start, attr_end)
            if index is None:
                return False, attr_end + 1
            new_property = 'ErrorMessageResourceType = typeof(Resources.{1}.{2}.Resource),\n{0}\tErrorMessageResourceName = nameof(Resources.{1}.{2}.Resource.{3})'\
                .format(offset, self._related_path, self._entity_name, property_name + 'Required')
            text[index] = text[index].replace(attr_property, new_property)
            self._properties.append((property_name + 'Required', required_message))
            return True, attr_end + 2

        attr_property, display_name, index = self._find_attribute_property(
            text, attr_name, 'Name', attr_start, attr_end)
        new_name = "nameof(Resources.{0}.{1}.Resource.{2})"\
            .format(self._related_path, self._entity_name, property_name)
        self._properties.append((property_name, display_name.replace('"', '')))

        if self._entity_type == EntityType.Class:
            text[index] = text[index].replace(display_name, new_name)
            text[attr_end] = text[attr_end].replace(")]", ",")
        else: # self._entity_type == EntityType.Enum
            text[index] = '{0}[Display(Name = {1},\n'.format(offset, new_name)

        # add display attribute resource type parameter
        text.insert(attr_end + 1, offset + "\tResourceType = typeof(Resources.{0}.{1}.Resource))]\n"
                    .format(self._related_path, self._entity_name))
        return True, attr_end + 2

    def _find_property_name(self, text, search_start):
        property_name = None
        offset = ''
        for index in range(search_start, len(text), 1):
            if self._entity_type == EntityType.Class:
                if "public" in text[index]:
                    words = text[index].split(' ')
                    word_with_public = max(list(map(
                        lambda w: w if w.endswith('public') else '', words
                    )))
                    tabs_count = word_with_public.count('\t')
                    space_count = words.index(word_with_public)
                    additional_modifiers = list(map(lambda mod:
                                                    mod in words, CodeEditor._possible_method_modifiers_after_public)
                                                ).count(True)
                    property_name = words[words.index(word_with_public) + 2 + additional_modifiers]
                    offset = '\t' * tabs_count + ' ' * space_count
                    break
                if 'private' in text[index]:
                    # TODO: skip private property
                    break
            else: # self._entity_type == EntityType.Enum
                property_name = text[index][:text[index].find('=')].strip()
                offset = text[index][:text[index].find(property_name)]
                break
        return property_name, offset

    def _find_attribute_property(self, text, attr_name, attr_property_name, attr_start, attr_end):
        property = None
        property_value = None
        index = attr_start
        for index in range(attr_start, attr_end + 1, 1):
            if attr_property_name in text[index]:
                property, property_value = self._find_attribute_property_value(text[index], attr_property_name)
                break
        if property is None:
            print('  {0} {1}: {2}Attribute property name {3} not found. Line {4}'
                  .format(self._entity_type.name, self._entity_name, attr_name, attr_property_name, attr_start + 1))
            return None, None, None

        return property, property_value, index

    def _find_attribute_property_value(self, line, attr_property_name):
        left_separator = '='
        if line.find(attr_property_name) == -1:
            return None, None
        prop_start = line[line.find(attr_property_name):]
        prop = prop_start[:prop_start.find('")')+1]
        return prop, prop[prop.find(left_separator) + 1:].strip()

    @staticmethod
    def _value_is_string(text):
        return len(text) > 1 and text[0] == '"' and text[len(text)-1] == '"'

    @staticmethod
    def _check_resource_usage(text, current_line, attribute_name):
        attr_start, attr_end = CodeEditor._find_attribute_boundaries(text, current_line, attribute_name)
        if attr_start is None:
            return None, None, None

        # check if resources are already used
        for index in range(attr_start, attr_end + 1, 1):
            if "ResourceType" in text[index]:
                return True, attr_start, attr_end

        return False, attr_start, attr_end

    @staticmethod
    def _find_attribute_boundaries(text, current_line, attribute_name):
        attr_start = None
        attr_end = None

        # find start of display attribute definition
        for index in range(current_line, len(text), 1):
            if "[{0}(".format(attribute_name) in text[index]:
                attr_start = index
                break

        if attr_start is None:
            return None, None

        # find end of display attribute definition
        for index in range(attr_start, len(text), 1):
            if "]" in text[index]:
                attr_end = index
                break
        return attr_start, attr_end
import os
import subprocess
import xml.etree.ElementTree as ET


class XMLEditor:
    xml_template = "../../templates/resource_schema.xml"
    languages = ['', '.en']

    @staticmethod
    def create_resources(project_folder, project_file, related_path, entity_name, properties):
        print('Creating resource files for entity {0}'.format(entity_name))
        if len(properties) == 0:
            print('There is no properties to add into resources')
            return

        target_folder = os.path.join(project_folder, 'Resources', related_path, entity_name, 'Resource.resx')
        if os.path.exists(target_folder):
            print('Resource files for entity {0} already exist'.format(entity_name))
            return

        target_folder = os.path.join(project_folder, 'Resources', related_path, entity_name)
        XMLEditor.create_resource_file(properties, target_folder)
        XMLEditor.generate_strong_type_resource_classes(project_folder, related_path, entity_name)
        XMLEditor.add_resources_to_project(project_folder, project_file, related_path, entity_name)
        print('Creating resource files was successfully')

    @staticmethod
    def create_resource_file(properties, target_folder):
        try:
            print('  Creating directory {0}...'.format(target_folder))
            os.makedirs(target_folder)
        except FileExistsError:
            print('    Directory {0} already exists'.format(target_folder))

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        tree = ET.ElementTree(file=XMLEditor.xml_template)
        root = tree.getroot()

        for prop in properties:
            data_item = ET.SubElement(root, "data", {
                "name": prop[0],
                "xml:space": "preserve"
            })
            value_item = ET.SubElement(data_item, "value")
            value_item.text = prop[1]
        XMLEditor._indent(root)

        tree = ET.ElementTree(root)
        with open(target_folder + "\\Resource.resx", "wb") as f:
            print('  Creating file {0}\\Resource.res...'.format(target_folder))
            tree.write(f, encoding='utf-8')
        print('    File was created successfully')
        with open(target_folder + "\\Resource.en.resx", "wb") as f:
            print('  Creating file {0}\\Resource.en.resx...'.format(target_folder))
            tree.write(f, encoding='utf-8')
        print('    File was created successfully')

    @staticmethod
    def generate_strong_type_resource_classes(project_folder, related_path, entity_name):
        target_folder = os.path.join(project_folder, 'Resources', related_path, entity_name)
        input_file = os.path.join(target_folder, 'Resource.resx')
        for lang in XMLEditor.languages:
            output_file = os.path.join(target_folder, 'Resource{0}.Designer.cs'.format(lang))
            print('  Generating strong typed resource file {0}...'.format(output_file))
            if lang == '':
                subprocess.check_output([
                    'resgen',
                    input_file,
                    '/str:C#,EAE_LIMS.DBModel.Resources.{0}.{1},Resource,{2}'
                        .format(related_path.replace('\\', '.'), entity_name, output_file),
                    '/publicClass'],
                    shell = True
                )
            else:
                open(output_file, 'w').close()
        print('  Remove extra file {0}\\Resource.resources...'.format(target_folder))
        os.remove(os.path.join(target_folder, 'Resource.resources'))
        print('    File was removed successfully')
        pass

    @staticmethod
    def add_resources_to_project(project_folder, project_file, related_path, entity_name):
        target_file = os.path.join(project_folder, project_file)
        print('  Start to add resources to project file {0}'.format(target_file))

        print('    Reading file {0}...'.format(target_file))
        tree = ET.ElementTree(file=target_file)
        root = tree.getroot()
        ET.register_namespace('', "http://schemas.microsoft.com/developer/msbuild/2003")

        namespace, tag_name = XMLEditor._tag_uri_and_name(root)
        iter = root.iter("{0}{1}".format('{' + namespace + '}', 'ItemGroup'))

        # find Compile tags
        print('    Adding Compile attributes')
        compile_element_group = None
        stop_search = False
        for item_group in iter:
            for compile in item_group:
                if compile.tag == "{0}{1}".format('{' + namespace + '}', 'Compile'):
                    compile_element_group = item_group
                    stop_search = True
                    break
            if stop_search:
                break

        # add new Compile tags
        for lang in XMLEditor.languages:
            embedded_res = ET.SubElement(compile_element_group, 'Compile', {
                "Include": "Resources\{0}\{1}\Resource{2}.Designer.cs"
                                 .format(related_path, entity_name, lang)
            })
            depend_upon = ET.SubElement(embedded_res, 'DependentUpon')
            depend_upon.text = 'Resource{0}.resx'.format(lang)
            auto_gen = ET.SubElement(embedded_res, 'AutoGen')
            auto_gen.text = 'True'
            design_time = ET.SubElement(embedded_res, 'DesignTime')
            design_time.text = 'True'
        XMLEditor._indent(compile_element_group)  # pretty print

        # find EmbeddedResource tags
        print('    Adding EmbeddedResource attributes')
        embedded_resources_group = None
        stop_search = False
        for item_group in iter:
            for embedded_resource in item_group:
                if embedded_resource.tag == "{0}{1}".format('{' + namespace + '}', 'EmbeddedResource'):
                    embedded_resources_group = item_group
                    stop_search = True
                    break
            if stop_search:
                break

        # add new EmbeddedResource tags
        for lang in XMLEditor.languages:
            embedded_res = ET.SubElement(embedded_resources_group, 'EmbeddedResource', {
                "Include": "Resources\{0}\{1}\Resource{2}.resx"
                                 .format(related_path, entity_name, lang)
            })
            generator = ET.SubElement(embedded_res, 'Generator')
            generator.text = 'PublicResXFileCodeGenerator'
            las_gen_output = ET.SubElement(embedded_res, 'LastGenOutput')
            las_gen_output.text = 'Resource{0}.Designer.cs'.format(lang)
            custom_namespace = ET.SubElement(embedded_res, 'CustomToolNamespace')
            custom_namespace.text = 'EAE_LIMS.DBModel.Resources.{0}.{1}'\
                .format(related_path.replace('\\', '.'), entity_name)
        XMLEditor._indent(embedded_resources_group) # pretty print

        tree = ET.ElementTree(root)
        with open(target_file, "wb") as f:
            print('    Saving changes...')
            tree.write(f, xml_declaration=True, encoding='utf-8')
        print('      Successfully saved')

    @staticmethod
    def _tag_uri_and_name(elem):
        if elem.tag[0] == "{":
            uri, ignore, tag = elem.tag[1:].partition("}")
        else:
            uri = None
            tag = elem.tag
        return uri, tag

    '''
    copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way
    '''
    @staticmethod
    def _indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                XMLEditor._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
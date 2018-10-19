from src.localizator.entity_type import EntityType
from src.localizator.localizator import Localizator


if __name__ == "__main__":
    project_file = "C:\\Projects\\Proj1\\Model\\Model.csproj"
    file = "C:\\Projects\\Proj1\\Model\\Class1.cs"

    entity_type = EntityType.Class
    # entity_type = EntityType.Enum

    black_list = [
        'References',
        'Reference',
        'Sample',
        'Orders',
        'Equipment.cs',
        'ReportHeader.cs',
        'SpecificationTestComponent.cs',
        'DynamicTableRecord.cs',
        '_Customized\AdmRole.cs'
    ]

    localizator = Localizator(project_file)
    localizator.localize_datamodel_file(file, entity_type)
    # localizator.localize_datamodel(init_class_dir, entity_type, black_list)

    # root_directory = "C:\\Projects\\Proj1"
    # file = "C:\\Projects\\Proj1\\Views\\View1.cshtml"
    # output_projects = [
    #     "C:\\Projects\\Proj1\\Resources2.csproj",
    #     "C:\\Projects\\Proj1\\Resources1.csproj",
    # ]
    # file = "C:\\Projects\\Scripts\\Localizator\\src\\comment_remover\\file_with_comments.txt"
    # localizator.localize_view_file(root_directory, file, output_projects)

    print('Done')
    pass

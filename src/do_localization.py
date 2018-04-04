from src.localizator.entity_type import EntityType
from src.localizator.localizator import Localizator


if __name__ == "__main__":
    init_class_dir = "C:\\Projects\\EAE.LIMS\\DataModel\\Classes"
    init_enum_dir = "C:\\Projects\\EAE.LIMS\\DataModel\\Enums"

    project_file = "C:\\Projects\\EAE.LIMS\\DataModel\\DataModel.csproj"

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
    # localizator.localize_datamodel(init_class_dir, entity_type, black_list)

    root_directory = "C:\\Projects\\EAE.LIMS\\EAE.LIMS"
    file = "C:\\Projects\\EAE.LIMS\\EAE.LIMS\\Views\\Reports\\Reports.cshtml"
    output_projects = [
        "C:\\Projects\\EAE.LIMS\\DefaultResources\\DefaultResources.csproj",
        "C:\\Projects\\EAE.LIMS\\NILEDResources\\NILEDResources.csproj",
    ]
    # file = "C:\\Projects\\Scripts\\Localizator\\src\\comment_remover\\file_with_comments.txt"
    localizator.localize_view_file(root_directory, file, output_projects)

    print('Done')
    pass

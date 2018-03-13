import xmltodict


class MvzDataset:
    maevizMapping = None
    name = None
    version = None
    dataFormat = None
    typeId = None
    featureTypeName = None
    convertedFeatureTypeName = None
    geometryType = None
    datasetPropertyName = None
    metadata = None
    fileDescriptors = None

    location = None
    description = None
    # properties = None

    def __init__(self, filename):
        with open(filename, 'rt', encoding='UTF16') as mvz_xml:
            mvz = xmltodict.parse(mvz_xml.read())

        # set mvz data
        try:
            meta_info_obj = mvz['mapped-dataset-properties']
            loc_obj = meta_info_obj['dataset-id']
            self.datasetPropertyName = "mapped-dataset-properties"
        except:
            pass

        try:
            meta_info_obj = mvz['file-dataset-properties']
            loc_obj = meta_info_obj['dataset-id']
            self.datasetPropertyName = "file-dataset-properties"
        except:
            pass

        try:
            meta_info_obj = mvz['raster-dataset-properties']
            loc_obj = meta_info_obj['dataset-id']
            self.datasetPropertyName = "raster-dataset-properties"
        except:
            pass

        try:
            meta_info_obj = mvz['gis-dataset-properties']
            self.datasetPropertyName = "gis-dataset-properties"
            loc_obj = meta_info_obj['dataset-id']
            self.featureTypeName = meta_info_obj['@feature-type-name']
            self.convertedFeatureTypeName = meta_info_obj['@converted-feature-type-name']
            self.geometryType = meta_info_obj['@geometry-type']
            self.set_feature_type_name(self.featureTypeName)
            self.set_converted_feature_type_name(self.convertedFeatureTypeName)
            self.set_geometry_type(self.geometryType)
            # self.properties = mvz['gis-dataset-properties']['properties']
        except:
            pass

        try:
            meta_info_obj = mvz['dataset-properties']
            loc_obj = meta_info_obj['dataset-id']
            self.datasetPropertyName = "dataset-properties"
        except:
            pass

        self.set_maeviz_mapping(meta_info_obj)
        self.set_metadata(meta_info_obj)

        # setter variable values
        try:
            self.name = meta_info_obj['@name']
        except:
            pass
        try:
            self.version = meta_info_obj['@version']
        except:
            pass
        try:
            self.dataFormat = meta_info_obj['@data-format']
        except:
            pass
        try:
            self.typeId = meta_info_obj['@type-id']
        except:
            pass
        try:
            self.location = loc_obj['location']
        except:
            pass
        try:
            self.description = loc_obj['desription']
        except:
            pass

    # check and set metadata
    def set_metadata(self, meta_info_obj):
        self.metadata = Metadata()
        if (meta_info_obj != None):
            try:  # check meta_info_obj to see if it has metadata tag
                metadata_obj = meta_info_obj["metadata"]
                if (metadata_obj != None):
                    table_metadata_obj = metadata_obj['table-metadata']
                    if (table_metadata_obj != None):
                        table_metadata = TableMetadata()
                        column_metadata_obj = table_metadata_obj['column-metadata']
                        if (column_metadata_obj != None):
                            column_metadatas = []
                            if (type(column_metadata_obj) is not list):
                                column_metadata = self.load_column_metadata(column_metadata_obj)
                                column_metadatas.append(column_metadata)
                            else:
                                for cm_obj in column_metadata_obj:
                                    column_metadata = self.load_column_metadata(cm_obj)
                                    column_metadatas.append(column_metadata)
                            table_metadata.set_column_metadata(column_metadatas)
                            self.metadata.set_table_metadata(table_metadata)
            except:
                pass

    def load_column_metadata(self, column_metadata_obj):
        column_metadata = ColumnMetadata()
        try:
            column_metadata.set_friendly_name(column_metadata_obj['@friendly-name'])
        except:
            pass
        try:
            column_metadata.set_field_length(column_metadata_obj['@field-length'])
        except:
            pass
        try:
            column_metadata.set_unit(column_metadata_obj['@unit'])
        except:
            pass
        try:
            column_metadata.set_sig_figs(column_metadata_obj['@sig-figs'])
        except:
            pass
        try:
            column_metadata.set_column_id(column_metadata_obj['@column-id'])
        except:
            pass
        try:
            column_metadata.set_unit_type(column_metadata_obj['@unit-type'])
        except:
            pass
        try:
            column_metadata.set_is_numeric(column_metadata_obj['@is-numeric'])
        except:
            pass
        try:
            column_metadata.set_is_result(column_metadata_obj['@is-result'])
        except:
            pass

        return column_metadata

    # set maeviz-mapping objects
    def set_maeviz_mapping(self, meta_info_obj):
        if (meta_info_obj != None):
            try:
                maeviz_mapping_obj = meta_info_obj['maeviz-mapping']
                self.maevizMapping = MaevizMapping()
                self.maevizMapping.set_schema(maeviz_mapping_obj['@schema'])
                mappings = []
                try:
                    mappings_obj = maeviz_mapping_obj['mapping']
                    if (type(mappings_obj) is not list):
                        mapping = Mapping()
                        try:
                            mapping.set_from_id(mappings_obj['@from'])
                        except Exception as e:
                            pass
                        try:
                            mapping.set_to_id(mappings_obj['@to'])
                        except Exception as e:
                            pass
                        mappings.append(mapping)
                    else:  # list of collections.OrderedDict
                        for mapping_obj in mappings_obj:
                            mapping = Mapping()
                            try:
                                mapping.set_from_id(mapping_obj['@from'])
                            except Exception as e:
                                pass
                            try:
                                mapping.set_to_id(mapping_obj['@to'])
                            except Exception as e:
                                pass
                            mappings.append(mapping)
                    self.maevizMapping.set_mapping(mappings)
                except Exception as e:
                    pass
            except Exception as e:
                pass

    def set_dataset_property_name(self, dataset_property_name):
        self.datasetPropertyName = dataset_property_name


    def get_dataset_property_name(self):
        return self.datasetPropertyName


    def set_name(self, name):
        self.name = name


    def get_name(self):
        return self.name


    def set_version(self, version):
        self.version = version


    def get_version(self):
        return self.version


    def set_data_format(self, data_format):
        self.dataFormat = data_format


    def get_data_format(self):
        return self.dataFormat


    def set_type_id(self, type_id):
        self.typeId = type_id


    def get_type_id(self):
        return self.typeId


    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_feature_type_name(self, feature_type_name):
        self.featureTypeName = feature_type_name


    def get_feature_type_name(self):
        return self.featureTypeName


    def set_converted_feature_type_name(self, converted_feature_type_name):
        self.convertedFeatureTypeName = converted_feature_type_name


    def get_converted_feature_type_name(self):
        return self.convertedFeatureTypeName


    def set_geometry_type(self, geometry_type):
        self.geometryType = geometry_type


    def get_geometry_type(self):
        return self.geometryType

    def set_location(self, location):
        self.location = location

    def get_location(self):
        return self.location

    def set_file_descriptors(self, file_descriptors):
        self.fileDescriptors = file_descriptors


class MaevizMapping:
    schema = None
    mapping = None

    def __init__(self):
        self.schema = None
        self.mapping = None

    def set_schema(self, schema):
        self.schema = schema

    def get_schema(self):
        return self.schema

    def set_mapping(self, mapping):
        self.mapping = mapping

    def get_mapping(self):
        return self.mapping


class Mapping:
    from_id = None
    to_id = None

    def __init__(self):
        self.from_id = None
        self.to_id = None

    # setters
    def set_from_id(self, from_id):
        self.from_id = from_id

    def get_from_id(self):
        return self.from_id

    def set_to_id(self, to_id):
        self.to_id = to_id

    def get_to_id(self):
        return self.to_id


class ColumnMetadata:
    friendlyName = None
    fieldLength = None
    unit = None
    columnId = None
    sigFigs = None
    unitType = None
    isNumeric = None
    isResult = None

    def __init__(self):
        self.friendlyName = None
        self.fieldLength = None

    def set_friendly_name(self, friendly_name):
        self.friendlyName = friendly_name

    def get_friendly_name(self):
        return self.friendlyName

    def set_field_length(self, field_length):
        self.fieldLength = field_length

    def get_field_length(self):
        return self.fieldLength

    def set_unit(self, unit):
        self.unit = unit

    def get_unit(self):
        return self.unit

    def set_column_id(self, column_id):
        self.columnId = column_id

    def get_column_id(self):
        return self.columnId

    def set_sig_figs(self, sig_figs):
        self.sigFigs = sig_figs

    def get_sig_figs(self):
        return self.sigFigs

    def set_unit_type(self, unit_type):
        self.unitType = unit_type

    def get_unit_type(self):
        return self.unitType

    def set_is_numeric(self, is_numeric):
        self.isNumeric = is_numeric

    def get_is_numeric(self):
        return self.isNumeric

    def set_is_result(self, is_result):
        self.isResult = is_result

    def get_is_result(self):
        return self.isResult


class Metadata:
    tableMetadata = None

    def __init__(self):
        self.tableMetadata = TableMetadata()

    def set_table_metadata(self, table_metadata):
        self.tableMetadata = table_metadata

    def get_table_metadata(self):
        return self.tableMetadata


class TableMetadata:
    column_metadata = None

    def __init__(self):
        self.column_metadata = ColumnMetadata()

    def set_column_metadata(self, column_metadata):
        self.column_metadata = column_metadata

    def get_column_metadata(self):
        return self.column_metadata


class Property:
    name = None
    value = None
    type = None
    category = None

    def __init__(self):
        self.name = None

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_type(self, type):
        self.type = type

    def get_type(self):
        return self.type

    def set_category(self, category):
        self.category = category

    def get_category(self):
        return self.category

class Dataset:
    id = None
    deleted = None
    title = None
    description = None
    date = None
    creator = None
    contributors = None
    fileDescriptors = None
    dataType = None
    storedUrl = None
    format = None
    sourceDataset = None
    spaces = None

    def __init__(self):
        id = None

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_deleted(self, deleted):
        self.deleted = deleted

    def get_deleted(self):
        return self.deleted

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_date(self, date):
        self.date = date

    def get_date(self):
        return self.date

    def set_creator(self, creator):
        self.creator = creator

    def get_creator(self):
        return self.creator

    def set_contributors(self, contributors):
        self.contributors = contributors

    def get_contributors(self):
        return self.contributors

    def set_file_descriptors(self, file_descriptors):
        self.fileDescriptors = file_descriptors

    def get_file_descriptors(self):
        return self.fileDescriptors

    def set_data_type(self, data_type):
        self.dataType = data_type

    def get_data_type(self):
        return self.dataType

    def set_stored_url(self, stored_url):
        self.storedUrl = stored_url

    def get_stored_url(self):
        return self.storedUrl

    def set_format(self, format):
        self.format = format

    def get_format(self):
        return self.format

    def set_source_dataset(self, source_dataset):
        self.sourceDataset = source_dataset

    def get_source_dataset(self):
        return self.sourceDataset

    def set_spaces(self, spaces):
        self.spaces = spaces

    def get_spaces(self):
        return self.spaces

    def addFileDescriptor(self, fileDescriptor):
        if (fileDescriptor != None):
            self.get_fileDescriptors().append(fileDescriptor)

    def set_fileDescriptors(self, fileDescriptors):
        self.fileDescriptors = fileDescriptors

    def get_fileDescriptors(self):
        return self.fileDescriptors

class Space:
    id = None
    name = None
    datasetIds = None

    def __init__(self):
        id = None

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_dataset_ids(self, dataset_ids):
        self.datasetIds = dataset_ids

    def get_dataset_ids(self):
        return self.datasetIds

    def add_dataset_id(self, id):
        if (id != None):
            (self.get_dataset_ids()).append(id)

class FileDescriptor:
    id = None
    deleted = None
    filename = None
    mimeType = None
    size = None
    dataURL = None
    md5sum = None

    def __init__(self):
        id = None

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_deleted(self, deleted):
        self.deleted = deleted

    def get_deleted(self):
        return self.deleted

    def set_filename(self, filename):
        self.filename = filename

    def get_filename(self):
        return self.filename

    def set_mime_type(self, mime_type):
        self.mimeType = mime_type

    def get_mime_type(self):
        return self.mimeType

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.size

    def set_data_url(self, data_url):
        self.dataURL = data_url

    def get_data_url(self):
        return self.dataURL

    def set_md5sum(self, md5sum):
        self.md5sum = md5sum

    def get_md5sum(self):
        return self.md5sum
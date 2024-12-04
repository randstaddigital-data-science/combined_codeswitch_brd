# import pandas as pd
# import ast

# def transform_slash_features(value):
#     if '/' in value:
#         split_parts = value.split('/')
#         transformed_value = split_parts[-2]
#     else:
#         transformed_value = value
#     return transformed_value

# def remove_quotations(value):
#     return value.strip('"')

# def extract_value(value):
#     try:
#         if isinstance(value, str):
#             value = ast.literal_eval(value)

#         if isinstance(value, list):
#             return [{f"{i}_{k}": v for k, v in item.items()} for i, item in enumerate(value) if isinstance(item, dict)]
#         elif isinstance(value, dict):
#             return [{k: v} for k, v in value.items()]
#     except Exception as e:
#         print(f"Warning: Error processing value: {value},Exception {e}")
#         pass

# def transform_features(raw_data, features_to_transform):
#     transformed_data = raw_data.copy()

#     for feature in features_to_transform:
#         new_values = raw_data[feature].apply(extract_value)

#         for i, item in enumerate(new_values.iloc[0]):
#             for key, value in item.items():
#                 transformed_data[f"{feature}_{key}"] = new_values.apply(lambda x: x[i][key] if isinstance(x, list) and len(x) > i and key in x[i] else None)
#     transformed_data = transformed_data.drop(features_to_transform, axis=1)
#     return transformed_data
# def columns_similar_check(data, columns_to_check):
#     res = all(data[column].equals(data[columns_to_check[0]]) for column in columns_to_check)
#     if res:
#         print(f"Same Values: {columns_to_check}")
#     else:
#         print("Not Same Values")

# def columns_same_value(data, columns_to_check):
#     non_similar_value_columns = [column for column in columns_to_check if data[column].nunique() != 1]
#     if not non_similar_value_columns:
#         print(f"One Value: {columns_to_check}")
#     else:
#         print(f"Not One Value: {non_similar_value_columns}")

# def combine_similar_rows_columns(transformed_data, similar_rows_columns, drop_columns):
#     combined_columns = '__'.join(similar_rows_columns)
#     transformed_data[combined_columns] = transformed_data[similar_rows_columns[0]]
#     transformed_data.drop(similar_rows_columns, axis=1, inplace=True)

# def drop_columns(transformed_data, columns_to_drop):
#     transformed_data.drop(columns=columns_to_drop, axis=1, inplace=True)

# def perform_eda(raw_data):
#     raw_data['FlatFileSource_ConnectionName'] = raw_data['FlatFileSource_ConnectionName'].apply(transform_slash_features)
#     raw_data['FlatFileDestination_ConnectionName'] = raw_data['FlatFileDestination_ConnectionName'].apply(transform_slash_features)

#     features_to_transform = ['FlatFileSource_Property', 'OleDbSource_Property', 'MergeJoinTransform_JoinInput',
#                              'MergeJoinTransform_JoinCondition', 'LookupTransform_LookupOutputColumn',
#                              'LookupTransform_LookupSource', 'LookupTransform_LookupCondition',
#                              'OleDbDestination_Property', 'FlatFileDestination_Property']
#     transformed_data = transform_features(raw_data, features_to_transform)

#     transformed_data['FlatFileSource_Property_1_#text'] = transformed_data['FlatFileSource_Property_1_#text'].apply(remove_quotations)
#     transformed_data['FlatFileDestination_Property_1_#text'] = transformed_data['FlatFileDestination_Property_1_#text'].apply(remove_quotations)

#     # Combine and drop similar rows and columns
#     similar_rows_columns_1 = ['FlatFileSource_Name', 'FlatFileSource_ConnectionName', 'OleDbSource_Name',
#                               'OleDbDestination_Name', 'FlatFileDestination_Name', 'FlatFileDestination_ConnectionName',
#                               'LookupTransform_LookupSource_@Name']
#     combine_similar_rows_columns(transformed_data, similar_rows_columns_1, similar_rows_columns_1)

#     similar_rows_columns_2 = ['MergeJoinTransform_JoinInput_0_@SourceName', 'OleDbDestination_Property_0_@Name']
#     combine_similar_rows_columns(transformed_data, similar_rows_columns_2, similar_rows_columns_2)

#     similar_rows_columns_3 = ['MergeJoinTransform_JoinInput_1_@SourceName', 'OleDbDestination_Property_1_@Name']
#     combine_similar_rows_columns(transformed_data, similar_rows_columns_3, similar_rows_columns_3)

#     similar_rows_columns_4 = ['OleDbDestination_Property_0_#text', 'OleDbDestination_Property_1_#text']
#     combine_similar_rows_columns(transformed_data, similar_rows_columns_4, similar_rows_columns_4)

#     # Drop specific columns
#     one_value_columns = ['FlatFileSource_DataType', 'OleDbSource_ConnectionName', 'OleDbSource_ReadSolids',
#                          'LookupTransform_InputName', 'LookupTransform_DestinationName', 'OleDbDestination_ConnectionName',
#                          'FlatFileDestination_DataType', 'FlatFileDestination_Format',
#                          'FlatFileSource_Property_0_@Name', 'OleDbSource_Property_@Name',
#                          'MergeJoinTransform_JoinInput_0_@OutputName', 'MergeJoinTransform_JoinInput_1_@OutputName',
#                          'LookupTransform_LookupOutputColumn_@ColumnName', 'LookupTransform_LookupOutputColumn_@DataType',
#                          'LookupTransform_LookupSource_@ConnectionName', 'FlatFileDestination_Property_0_@Name',
#                          'FlatFileDestination_Property_1_@Name', 'FlatFileDestination_Property_1_#text']
#     drop_columns(transformed_data, one_value_columns)

#     irrelevant_columns = ['FlatFileSource_Format', 'FlatFileSource_Property_1_#text', 'MergeJoinTransform_Name',
#                             'OleDbSource_Property_#text', 'FlatFileSource_ColumnDelimiter',
#                             'LookupTransform_Name', 'ExpressionTransform_Name', 'FlatFileSource_Property_0_#text',
#                             'FlatFileSource_Property_1_@Name', 'FlatFileDestination_Property_0_#text']
#     drop_columns(transformed_data, irrelevant_columns)

#     return transformed_data
import pandas as pd
import ast

def transform_slash_features(value):
    if '/' in value:
        split_parts = value.split('/')
        transformed_value = split_parts[-2]
    else:
        transformed_value = value
    return transformed_value

def remove_quotations(value):
    return value.strip('"')

def extract_value(value):
    try:
        if isinstance(value, str):
            value = ast.literal_eval(value)

        if isinstance(value, list):
            return [{f"{i}_{k}": v for k, v in item.items()} for i, item in enumerate(value) if isinstance(item, dict)]
        elif isinstance(value, dict):
            return [{k: v} for k, v in value.items()]
    except Exception as e:
        print(f"Warning: Error processing value: {value}, Exception {e}")
        pass

def transform_features(raw_data, features_to_transform):
    transformed_data = raw_data.copy()

    for feature in features_to_transform:
        new_values = raw_data[feature].apply(extract_value)

        for i, item in enumerate(new_values.iloc[0]):
            for key, value in item.items():
                transformed_data[f"{feature}_{key}"] = new_values.apply(
                    lambda x: x[i][key] if isinstance(x, list) and len(x) > i and key in x[i] else None
                )
    transformed_data = transformed_data.drop(features_to_transform, axis=1)
    return transformed_data

def combine_similar_rows_columns(transformed_data, similar_rows_columns):
    combined_columns = '__'.join(similar_rows_columns)
    transformed_data[combined_columns] = transformed_data[similar_rows_columns[0]]
    transformed_data.drop(similar_rows_columns, axis=1, inplace=True)

def drop_columns(transformed_data, columns_to_drop):
    transformed_data.drop(columns=columns_to_drop, axis=1, inplace=True)

def perform_eda(raw_data):
    raw_data['FlatFileSource_ConnectionName'] = raw_data['FlatFileSource_ConnectionName'].apply(transform_slash_features)
    raw_data['FlatFileDestination_ConnectionName'] = raw_data['FlatFileDestination_ConnectionName'].apply(transform_slash_features)

    features_to_transform = ['FlatFileSource_Property', 'OleDbSource_Property', 'MergeJoinTransform_JoinInput',
                             'MergeJoinTransform_JoinCondition', 'LookupTransform_LookupOutputColumn',
                             'LookupTransform_LookupSource', 'LookupTransform_LookupCondition',
                             'OleDbDestination_Property', 'FlatFileDestination_Property']
    transformed_data = transform_features(raw_data, features_to_transform)

    transformed_data['FlatFileSource_Property_1_#text'] = transformed_data['FlatFileSource_Property_1_#text'].apply(remove_quotations)
    transformed_data['FlatFileDestination_Property_1_#text'] = transformed_data['FlatFileDestination_Property_1_#text'].apply(remove_quotations)

    # Combine and drop similar rows and columns
    similar_rows_columns = [
        ['FlatFileSource_Name', 'FlatFileSource_ConnectionName', 'OleDbSource_Name', 'OleDbDestination_Name', 
         'FlatFileDestination_Name', 'FlatFileDestination_ConnectionName', 'LookupTransform_LookupSource_@Name'],
        ['MergeJoinTransform_JoinInput_0_@SourceName', 'OleDbDestination_Property_0_@Name'],
        ['MergeJoinTransform_JoinInput_1_@SourceName', 'OleDbDestination_Property_1_@Name'],
        ['OleDbDestination_Property_0_#text', 'OleDbDestination_Property_1_#text']
    ]

    for group in similar_rows_columns:
        combine_similar_rows_columns(transformed_data, group)

    # Drop specific columns
    one_value_columns = ['FlatFileSource_DataType', 'OleDbSource_ConnectionName', 'OleDbSource_ReadSolids',
                         'LookupTransform_InputName', 'LookupTransform_DestinationName', 'OleDbDestination_ConnectionName',
                         'FlatFileDestination_DataType', 'FlatFileDestination_Format',
                         'FlatFileSource_Property_0_@Name', 'OleDbSource_Property_@Name',
                         'MergeJoinTransform_JoinInput_0_@OutputName', 'MergeJoinTransform_JoinInput_1_@OutputName',
                         'LookupTransform_LookupOutputColumn_@ColumnName', 'LookupTransform_LookupOutputColumn_@DataType',
                         'LookupTransform_LookupSource_@ConnectionName', 'FlatFileDestination_Property_0_@Name',
                         'FlatFileDestination_Property_1_@Name', 'FlatFileDestination_Property_1_#text']
    drop_columns(transformed_data, one_value_columns)

    irrelevant_columns = ['FlatFileSource_Format', 'FlatFileSource_Property_1_#text', 'MergeJoinTransform_Name',
                          'OleDbSource_Property_#text', 'FlatFileSource_ColumnDelimiter',
                          'LookupTransform_Name', 'ExpressionTransform_Name', 'FlatFileSource_Property_0_#text',
                          'FlatFileSource_Property_1_@Name', 'FlatFileDestination_Property_0_#text']
    drop_columns(transformed_data, irrelevant_columns)

    return transformed_data

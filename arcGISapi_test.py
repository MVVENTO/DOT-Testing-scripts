
########### Update Spatial layer ############
# As content publishers, you may be required to keep certain web layers up to date. As new data arrives, you may have to append new features, update existing features etc.
#  There are a couple of different options to accomplish this:

# Method 1: editing individual features as updated datasets are available
# Method 2: overwriting feature layers altogether with updated datasets

# sample found here -> https://developers.arcgis.com/python/samples/updating-features-in-a-feature-layer/



############ Method 1  ###############
# Edit individual features
# Connect to the GIS
from arcgis.gis import GIS
from arcgis import features
import pandas as pd

#Access the portal using "amazing_arcgis_123" as password for the given Username. 
gis = GIS("https://pythonapi.playground.esri.com/portal")

# read the initial csv
csv1 = 'data/updating_gis_content/capitals_1.csv'
ferries_df_1 = pd.read_csv(csv1)
ferries_df_1.head()

# print the number of records in this csv
ferries_df_1.shape

import os
import datetime as dt
import shutil

# assign variables to locations on the file system 
cwd = os.path.abspath(os.getcwd())
data_pth = os.path.join(cwd, r'data/updating_gis_content/')

# create a unique timestamp string to append to the file name
now_ts = str(int(dt.datetime.now().timestamp()))

# copy the file, appending the unique string and assign it to a variable
my_csv = shutil.copyfile(os.path.abspath(csv1),
                        os.path.join(data_pth, 'ferries_1_' + now_ts + '.csv'))

my_csv            

# add the initial csv file and publish that as a web layer
item_prop = {'title':'Ferries spreadsheet ' + now_ts}
csv_item = gis.content.add(item_properties=item_prop, data=my_csv)
csv_item

# publish the csv item into a feature layer
ferries_item = csv_item.publish()
ferries_item

# update the item metadata
item_prop = {'title':'USA Capitals'}
ferries_item.update(item_properties = item_prop, thumbnail='data/updating_gis_content/ferries.png')
ferries_item

# read the second csv set
csv2 = 'data/updating_gis_content/ferries_2.csv'
ferries_df_2 = pd.read_csv(csv2)
ferries_df_2.head()

# get the dimensions of this csv
ferries_df_2.shape

ferries_flayer = ferries_item.layers[0]
ferries_fset = ferries_flayer.query() #querying without any conditions returns all the features
ferries_fset.sdf.head()

overlap_rows = pd.merge(left = ferries_fset.sdf, right = ferries_df_2, how='inner',
                       on = 'FMS ID')
overlap_rows

features_for_update = [] #list containing corrected features
all_features = ferries_fset.features

# inspect one of the features
all_features[0]

# get the spatial reference of the features since we need to update the geometry
ferries_fset.spatial_reference

from arcgis import geometry #use geometry module to project Long,Lat to X and Y
from copy import deepcopy

for FMS_ID in overlap_rows['FMS ID']:
    # get the feature to be updated
    original_feature = [f for f in all_features if f.attributes['FMS ID'] == FMS_ID][0]
    feature_to_be_updated = deepcopy(original_feature)
    
    print(str(original_feature))
    
    # get the matching row from csv
    matching_row = ferries_df_2.where(ferries_df_2.FMS_ID == FMS_ID).dropna()
    
    #get geometries in the destination coordinate system
    input_geometry = {'y':float(matching_row['latitude']),
                       'x':float(matching_row['longitude'])}
    output_geometry = geometry.project(geometries = [input_geometry],
                                       in_sr = 4326, 
                                       out_sr = ferries_fset.spatial_reference['latestWkid'],
                                      gis = gis)
    
    # assign the updated values
    feature_to_be_updated.geometry = output_geometry[0]
    feature_to_be_updated.attributes['FMSID'] = float(matching_row['FMSID'])               # FMSID : FMS ID
    feature_to_be_updated.attributes['PROJ_ID_DE'] = int(matching_row['PROJ_ID_DE'])       # PROJ_ID_DE : Project Description
    feature_to_be_updated.attributes['FYCons'] = matching_row['FYCons'].values[0]          # FYCons : Construction FY
    feature_to_be_updated.attributes['FYDesign'] = matching_row['FYDesign'].values[0]      # FYDesign : Design FY
    feature_to_be_updated.attributes['FundStatus'] = float(matching_row['FundStatus'])     # FundStatus : Funding Status
    feature_to_be_updated.attributes['ProjStatus'] = matching_row['ProjStatus'].values[0]  # ProjStatus : Project Status
    feature_to_be_updated.attributes['Cost'] = int(matching_row['Cost'])                   # Cost : Cost
    feature_to_be_updated.attributes['Planned_Or_Committed'] = int(matching_row['Planned_Or_Committed']) # Planned_Or_Committed : Planned Or Committed
    
    #add this to the list of features to be updated
    features_for_update.append(feature_to_be_updated)
    
    print(str(feature_to_be_updated))
    print("========================================================================")

features_for_update

cities_flayer.edit_features(updates= features_for_update)

#select those rows in the capitals_2.csv that do not overlap with those in capitals_1.csv
new_rows = cities_df_2[~cities_df_2['city_id'].isin(overlap_rows['city_id'])]
print(new_rows.shape)


new_rows.head()

features_to_be_added = []

# get a template feature object
template_feature = deepcopy(features_for_update[0])

# loop through each row and add to the list of features to be added
for row in new_rows.iterrows():
    new_feature = deepcopy(template_feature)
    
    #print
    print("Creating " + row[1]['name'])
    
    #get geometries in the destination coordinate system
    input_geometry = {'y':float(row[1]['latitude']),
                       'x':float(row[1]['longitude'])}
    output_geometry = geometry.project(geometries = [input_geometry],
                                       in_sr = 4326, 
                                       out_sr = cities_fset.spatial_reference['latestWkid'],
                                      gis = gis)
    
    # assign the updated values
    new_feature.geometry = output_geometry[0]
    new_feature.attributes['longitude'] = float(row[1]['longitude'])
    new_feature.attributes['city_id'] = int(row[1]['city_id'])
    new_feature.attributes['state'] = row[1]['state']
    new_feature.attributes['capital'] = row[1]['capital']
    new_feature.attributes['latitude'] = float(row[1]['latitude'])
    new_feature.attributes['name'] = row[1]['name']
    new_feature.attributes['pop2000'] = int(row[1]['pop2000'])
    new_feature.attributes['pop2007'] = int(row[1]['pop2007'])
    
    #add this to the list of features to be updated
    features_to_be_added.append(new_feature)

# take a look at one of the features we created
features_to_be_added[0]

cities_flayer.edit_features(adds = features_to_be_added)

### Apply edits from 3rd spreedsheet ####

# read the third csv set
csv3 = 'data/updating_gis_content/capitals_annex.csv'
cities_df_3 = pd.read_csv(csv3)
cities_df_3.head()

#find the number of rows in the third csv
cities_df_3.shape


#Get the existing list of fields on the cities feature layer
cities_fields = cities_flayer.manager.properties.fields

# Your feature layer may have multiple fields, 
# instead of printing all, let us take a look at one of the fields:
cities_fields[1]

for field in cities_fields:
    print(f"{field.name:13}|  {field.alias:13}|  {field.type:25}|  {field.sqlType}")

######  prepare additional columns ####
# get a template field
template_field = dict(deepcopy(cities_fields[1]))
template_field

# get the list of new fields to add from the third spreadsheet, that are not in spread sheets 1,2
new_field_names = list(cities_df_3.columns.difference(cities_df_1.columns))
new_field_names

fields_to_be_added = []
for new_field_name in new_field_names:
    current_field = deepcopy(template_field)
    if new_field_name.lower() == 'class':
        current_field['sqlType'] = 'sqlTypeVarchar'
        current_field['type'] = 'esriFieldTypeString'
        current_field['length'] = 8000
    current_field['name'] = new_field_name.lower()
    current_field['alias'] = new_field_name
    fields_to_be_added.append(current_field)
    
len(fields_to_be_added)

#inspect one of the fields
fields_to_be_added[3]

######### Adding additional ######

cities_flayer.manager.add_to_definition({'fields':fields_to_be_added})

new_cities_fields = cities_flayer.manager.properties.fields
len(new_cities_fields)


for field in new_cities_fields:
    print(f"{field.name:10}|  {field.type}")

# Run a fresh query on the feature layer so it includes the new features from
# csv2 and new columns from csv3
cities_fset2 = cities_flayer.query()
cities_features2 = cities_fset2.features

features_for_update = []
for city_id in cities_df_3['city_id']:
    # get the matching row from csv
    matching_row = cities_df_3.where(cities_df_3.city_id == city_id).dropna()
    
    print(str(city_id) + " Adding additional attributes for: " + matching_row['name'].values[0])
    
    # get the feature to be updated
    original_feature = [f for f in cities_features2 if f.attributes['city_id'] == city_id][0]
    feature_to_be_updated = deepcopy(original_feature)
    
    # assign the updated values
    feature_to_be_updated.attributes['class'] = matching_row['class'].values[0]
    feature_to_be_updated.attributes['white'] = int(matching_row['white'])
    feature_to_be_updated.attributes['black'] = int(matching_row['black'])
    feature_to_be_updated.attributes['ameri_es'] = int(matching_row['ameri_es'])
    feature_to_be_updated.attributes['asian'] = int(matching_row['asian'])
    feature_to_be_updated.attributes['hawn_pl'] = int(matching_row['hawn_pl'])
    feature_to_be_updated.attributes['hispanic'] = int(matching_row['hispanic'])
    feature_to_be_updated.attributes['males'] = int(matching_row['males'])
    feature_to_be_updated.attributes['females'] = int(matching_row['females'])
    
    #add this to the list of features to be updated
    features_for_update.append(feature_to_be_updated)

# inspect one of the features
features_for_update[-1]

# apply the edits to the feature layer
cities_flayer.edit_features(updates= features_for_update)

########## Verify that changes have been made #########

cities_fset3 = cities_flayer.query()
cities_fset3.sdf.head(5)

print("Feature class has been updated!")



############ Method 2  ###############
# Overwrite 

# Import libraries
from arcgis.gis import GIS
from arcgis import features
import pandas as pd

# Connect to the GIS
gis = GIS(url='https://pythonapi.playground.esri.com/portal')

# import libraries so you use unique file names for creating items
# and services to this geosaurus.maps.arcgis.com organization
# if you've download the samples or are working with your own organization
# or Enterprise, this may not be necessary and you could just read the 
# csv data directly instead of copyting the file:
#
 my_csv = os.path.join(data_path, csv_file)


import datetime as dt
import os
import shutil

# assign path variables for data
data_path = os.path.join('data', 'updating_gis_content')
csv_file = 'capitals_1.csv'

# assign variable to current timestamp to make unique file to add to portal
now = int(dt.datetime.now().timestamp())

# copy original file for adding to portal
my_csv = shutil.copy2(os.path.join(data_path, csv_file),
                     os.path.join(data_path, csv_file.split('.')[0] + '_' + str(now) + '.csv'))


# read the initial csv
ferries_df_1 = pd.read_csv(my_csv)
ferries_df_1.head()

# print the number of records in this csv
ferries_df_1.shape

# add the csv as an item
item_prop = {'title':'USA Capitals spreadsheet_' + str(now)}
csv_item = gis.content.add(item_properties=item_prop, data=my_csv)
csv_item

# publish the csv item into a feature layer
ferries_item = csv_item.publish()
ferries_item

# update the item metadata
item_prop = {'title':'Ferries 2'}
ferries_item.update(item_properties = item_prop, 
                   thumbnail=os.path.join('data','updating_gis_content','ferries_terminals.png'))
ferries_item

map1 = gis.map('USA')
map1

map1.zoom = 3
map1.center = [39, -98]

map1.add_layer(ferries_item)

ferries_item.url

# read the second csv set
csv2 = os.path.join('data', 'updating_gis_content', 'capitals_2.csv')
ferries_df_2 = pd.read_csv(csv2)
ferries_df_2.head(5)

# get the dimensions of this csv
ferries_df_2.shape

updated_df = ferries_df_1.append(ferries_df_2)
updated_df.shape

updated_df.drop_duplicates(subset='FMS ID', keep='last', inplace=True)
# we specify argument keep = 'last' to retain edits from second spreadsheet
updated_df.shape

updated_df.head(5)

import os
if not os.path.exists(os.path.join('data', 'updating_gis_content','updated_ferries_csv')):
    os.mkdir(os.path.join('data', 'updating_gis_content','updated_ferries_csv'))

updated_df.to_csv(os.path.join('data', 'updating_gis_content',
                               'updated_ferries_csv', 'ferries_1.csv'))

from arcgis.features import FeatureLayerCollection
ferries_flayer_collection = FeatureLayerCollection.fromitem(ferries_item)

#call the overwrite() method which can be accessed using the manager property
ferries_flayer_collection.manager.overwrite(os.path.join('data', 'updating_gis_content',
                               'updated_ferries_csv', 'ferries_1.csv'))

ferries_flayer = cities_item.layers[0] #there is only 1 layer
ferries_flayer.query(return_count_only=True) #get the total number of features

map2 = gis.map("USA")
map2

map2.zoom = 3
map2.center = [39, -98]

map2.add_layer(ferries_item)


print("Feature class has been overwritten!")

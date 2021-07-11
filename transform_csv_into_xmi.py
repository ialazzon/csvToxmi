from pyecore.resources import ResourceSet, URI
from pyecore.valuecontainer import BadValueError
from pyecore.ecore import EString,EClass
import csv
import argparse

# Create the parser
my_parser = argparse.ArgumentParser(description='Transform csv data to xmi conforming to an Ecore meta-model')

# Add the arguments
my_parser.add_argument('source_meta_model',
                       metavar='source_meta_model',
                       type=str,
                       help='the path to the source meta-model')

my_parser.add_argument('root_element',
                       metavar='root_element',
                       type=str,
                       help='the name of the root element in the source meta-model')

my_parser.add_argument('mapping_model',
                       metavar='mapping_model',
                       type=str,
                       help='the path to the mapping model which conforms to mappingCSVtoEMF.ecore')

my_parser.add_argument('output_model',
                       metavar='output_model',
                       type=str,
                       help='the name of the output model which will contain the xmi data')

# Execute the parse_args() method
args = my_parser.parse_args()
source_meta_model = args.source_meta_model
root_element = args.root_element
mapping_model = args.mapping_model
output_model = args.output_model

#Read the mapping model file
rset = ResourceSet()
resource = rset.get_resource(URI('mappingCSVtoEMF.ecore'))
mm_root = resource.contents[0]
rset.metamodel_registry[mm_root.nsURI] = mm_root
resource = rset.get_resource(URI(mapping_model))
model_root = resource.contents[0]

dataFiles = model_root.datafile
n=len(dataFiles)

#Function get_num_fields returns the number of fields in the csv file corresponding to the class.
#This is done by reading the mapping instances.
def get_num_fields(className):
    count = 0
    mappings = model_root.mapping
    for mapping in mappings:
        if mapping.className == className:
            count+=1
    return count
    
#Function get_feature_name returns the name of the feature in class className and whose
#corresponding field number in the CSV file is fieldNumber.
def get_feature_name(className, fieldNumber):
    mappings = model_root.mapping
    for mapping in mappings:
        if mapping.className == className and mapping.fieldNum == fieldNumber:
            return mapping.featureName

resource = rset.get_resource(URI(source_meta_model))
root = resource.contents[0]
A = root.getEClassifier(root_element)
a_instance = A()

#First Pass
for dataFile in dataFiles:
    className = dataFile.className
    fileName = dataFile.fileName
    with open(fileName, newline='',errors="ignore") as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',')
        for row in file_reader:
            num_fields = get_num_fields(className)
            theClass = root.getEClassifier(className)
            instance = theClass()
            for i in range(num_fields):
                if type(instance.__getattribute__(get_feature_name(className,i+1))) is int:
                    instance.__setattr__(get_feature_name(className,i+1),int(row[i]))
                elif type(instance.__getattribute__(get_feature_name(className,i+1))) is float:
                    instance.__setattr__(get_feature_name(className,i+1),float(row[i]))
                elif type(instance.__getattribute__(get_feature_name(className,i+1)))== str:
                    instance.__setattr__(get_feature_name(className,i+1),row[i])
            a_instance.__getattribute__(className.lower()).append(instance)
            
#Function find_instance returns the instance of class className whose id is equal to id.
def find_instance(className, id):
    for child in a_instance.eAllContents():
        if className == child.__class__.__name__:
            if str(child.__getattribute__('id'))==id:
                return child

#Function find_instance_using_line_number returns the instance of class className at index line_num-1.
def find_instance_using_line_number(className, line_num):
    list_instances = a_instance.__getattribute__(className.lower())
    return list_instances[line_num-1]

#Second Pass
for dataFile in dataFiles:
    className = dataFile.className
    fileName = dataFile.fileName
    with open(fileName, newline='',errors="ignore") as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',')
        line_num = 0
        for row in file_reader:
            line_num +=1
            num_fields = get_num_fields(className)
            instance = find_instance_using_line_number(className,line_num)
            for i in range(num_fields):
                if type(instance.__getattribute__(get_feature_name(className,i+1))) is int:
                    pass
                elif type(instance.__getattribute__(get_feature_name(className,i+1))) is float:
                    pass
                elif type(instance.__getattribute__(get_feature_name(className,i+1)))== str:
                    pass
                else:
                    for df in dataFiles:
                        try:
                            instance.__setattr__(get_feature_name(className,i+1), root.getEClassifier(df.className)())
                        except BadValueError:
                            continue
                            
                        try:
                            tmp_instance = find_instance( df.className  ,row[i])
                            if tmp_instance is not None:
                                instance.__setattr__(get_feature_name(className,i+1), tmp_instance)
                        except (AttributeError):
                            continue
                    
resource = rset.create_resource(URI(output_model))
resource.append(a_instance)
resource.save()
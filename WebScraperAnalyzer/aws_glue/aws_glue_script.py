Sure, here is an example code for 'aws_glue_script.py':

#python
import sys

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType

# Initialize GlueContext and SparkContext
glueContext = GlueContext(SparkContext.getOrCreate())

# Get job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Extract data from S3
dynamic_frame = glueContext.create_dynamic_frame_from_options(
                  "s3",
                  {"paths": ["s3://my-bucket/input-data"]},
                  "csv",
                  {"delimiter": ","},
                  "first_row_as_header",
                  {"header": True}
)

# Apply transformations
dynamic_frame = RenameField.apply(frame=dynamic_frame, old_name="Name", new_name="FullName")
dynamic_frame = SelectFields.apply(frame=dynamic_frame, paths=["FullName", "Address", "Phone"])
dynamic_frame = ApplyMapping.apply(frame=dynamic_frame, mappings=[("FullName", "string", "name", "string"),
                                                                   ("Address", "string", "address", "string"),
                                                                   ("Phone", "string", "phone", "string")])
# Convert dynamic frame to data frame
data_frame = dynamic_frame.toDF()

# Add column to the data frame
def get_city(address):
    return address.split(",")[0].strip()

get_city_udf = udf(get_city, StringType())
data_frame = data_frame.withColumn("city", get_city_udf(col("address")))

# Select columns to export to S3
data_frame = data_frame.select("name", "address", "city", "phone")

# Write data frame to S3 in CSV format
data_frame.write.mode("overwrite").format("csv").option("header", "true").save("s3://my-bucket/output-data")

# Print completion message
print("EtlJob has successfully executed")


This is just an example and you would need to modify some parts of the code to fit your specific use case. Make sure to set the correct AWS S3 bucket paths and replace the data mappings with your desired column mappings.
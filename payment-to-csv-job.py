import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print("Starting JOB....")
# Script generated for node PostgreSQL
PostgreSQL_node1713493144767 = glueContext.create_dynamic_frame.from_options(
    connection_type = "postgresql",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "fraud_dataset_view",
        "connectionName": "db-arch-02",
    },
    transformation_ctx = "PostgreSQL_node1713493144767"
)

print("Clean S3 Bucket....")
glueContext.purge_s3_path("s3://eliezerraj-908671954593-dataset/payment/glue-job/", options={"retentionPeriod": 0}, transformation_ctx="")

print("Loading files to S3 ....")
# Script generated for node Amazon S3
AmazonS3_node1713493279068 = glueContext.write_dynamic_frame.from_options(frame=PostgreSQL_node1713493144767, connection_type="s3", format="csv", connection_options={"path": "s3://eliezerraj-908671954593-dataset/payment/glue-job/", "partitionKeys": []}, transformation_ctx="AmazonS3_node1713493279068")

job.commit()
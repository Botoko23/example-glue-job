import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Amazon S3
AmazonS3_node1708783631007 = glueContext.create_dynamic_frame.from_options(format_options={"quoteChar": -1, "withHeader": True, "separator": ",", "optimizePerformance": False}, connection_type="s3", format="csv", connection_options={"paths": ["s3://sales-2019/sales.csv"], "recurse": True}, transformation_ctx="AmazonS3_node1708783631007")

# Script generated for node Evaluate Data Quality
EvaluateDataQuality_node1708784412691_ruleset = """
    Rules = [
    ColumnValues "event_time" matches "^2019.*$"
        
    ]
"""

EvaluateDataQuality_node1708784412691 = EvaluateDataQuality().process_rows(frame=AmazonS3_node1708783631007, ruleset=EvaluateDataQuality_node1708784412691_ruleset, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1708784412691", "enableDataQualityCloudWatchMetrics": True, "enableDataQualityResultsPublishing": True, "resultsS3Prefix": "s3://sales-2019/data-quality-fail/"}, additional_options={"observations.scope":"ALL","performanceTuning.caching":"CACHE_NOTHING"})

assert EvaluateDataQuality_node1708784412691[EvaluateDataQuality.DATA_QUALITY_RULE_OUTCOMES_KEY].filter(lambda x: x["Outcome"] == "Failed").count() == 0, "The job failed due to failing DQ rules for node: AmazonS3_node1708783631007"

# Script generated for node originalData
originalData_node1708786050377 = SelectFromCollection.apply(dfc=EvaluateDataQuality_node1708784412691, key="originalData", transformation_ctx="originalData_node1708786050377")

# Script generated for node product_df_select
product_df_select_node1708786714412 = SelectFields.apply(frame=originalData_node1708786050377, paths=["event_time", "product_id", "category_code", "brand", "price", "event_year", "event_month"], transformation_ctx="product_df_select_node1708786714412")

# Script generated for node S3 Target
S3Target_node1711003763448 = glueContext.getSink(path="s3://partitioned-sales-bucket", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["event_year", "event_month"], enableUpdateCatalog=True, transformation_ctx="S3Target_node1711003763448")
S3Target_node1711003763448.setCatalogInfo(catalogDatabase="sales_db",catalogTableName="sales_table")
S3Target_node1711003763448.setFormat("glueparquet", compression="snappy")
S3Target_node1711003763448.writeFrame(product_df_select_node1708786714412)
job.commit()
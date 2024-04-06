import boto3
import sagemaker
from sagemaker import Session
from sagemaker import get_execution_role

if __name__ == "__main__":

    # Loading enviroment variables...
    print("Loading enviroment variables... ")

    model_package_group_name = "FraudModelPackageGroup"
    role = get_execution_role()
    sm_client = boto3.client(service_name="sagemaker")
    sm_runtime = boto3.client(service_name="sagemaker-runtime")

    # find the latest approved model package
    print("Find the latest approved model package... ")

    # get a list of approved model packages from the model package group you specified earlier
    approved_model_packages = sm_client.list_model_packages(
          ModelApprovalStatus='Approved',
          ModelPackageGroupName=model_package_group_name,
          SortBy='CreationTime',
          SortOrder='Descending'
      )

    try:
        latest_approved_model_package_arn = approved_model_packages['ModelPackageSummaryList'][0]['ModelPackageArn']
    except Exception as e:
        print("Failed to retrieve an approved model package:", e)

    print("latest_approved_model_package_arn: ",latest_approved_model_package_arn)

    # retrieve required information about the model
    latest_approved_model_package_descr = sm_client.describe_model_package(ModelPackageName = latest_approved_model_package_arn)

    # model artifact uri (tar.gz file)
    model_artifact_uri = latest_approved_model_package_descr['InferenceSpecification']['Containers'][0]['ModelDataUrl']
    # sagemaker image in ecr
    image_uri = latest_approved_model_package_descr['InferenceSpecification']['Containers'][0]['Image']

    print("model_artifact_uri: ", model_artifact_uri)
    print("image_uri: ", image_uri)

    # Create the model...
    print("Create the model... ")
    from time import gmtime, strftime

    model_name = "xgboost-fraud-model-v3-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    print("Model name: " + model_name)

    #  environment variables
    env_vars = {"SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
                "SAGEMAKER_ENABLE_CLOUDWATCH_METRICS": "false"}

    create_model_response = sm_client.create_model(
        ModelName=model_name,
        Containers=[
            {
                "Image": image_uri,
                "Mode": "SingleModel",
                "ModelDataUrl": model_artifact_uri,
                "Environment": env_vars,
            }
        ],
        ExecutionRoleArn=role,
    )

    print("Created Model Arn: " + create_model_response["ModelArn"])

    # Create endpoint configuration...
    print("Create endpoint configuration... ")

    xgboost_epc_name = "mlops-epc-fraud-model-v3-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())

    endpoint_config_response = sm_client.create_endpoint_config(
        EndpointConfigName=xgboost_epc_name,
        ProductionVariants=[
            {
                "VariantName": "byoVariant",
                "ModelName": model_name,
                "ServerlessConfig": {
                    "MemorySizeInMB": 4096,
                    "MaxConcurrency": 20,
                },
            },
        ],
    )

    print("Endpoint Configuration Arn: " + endpoint_config_response["EndpointConfigArn"])

    # Create endpoint configuration...
    print("Create endpoint ... ")
    endpoint_name = "xgboost-serverless-ep-fraud-model-v3-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())

    create_endpoint_response = sm_client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=xgboost_epc_name,
    )

    print("Endpoint Arn: " + create_endpoint_response["EndpointArn"])

    # wait for endpoint to reach a terminal state (InService) using describe endpoint
    print("Wait for endpoint to reach a terminal state (InService) using describe endpoint ... ")
    import time

    describe_endpoint_response = sm_client.describe_endpoint(EndpointName=endpoint_name)

    while describe_endpoint_response["EndpointStatus"] == "Creating":
        describe_endpoint_response = sm_client.describe_endpoint(EndpointName=endpoint_name)
        print(describe_endpoint_response["EndpointStatus"])
        time.sleep(15)

    describe_endpoint_response

    print("Process finished ... ")
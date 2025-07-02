import os
import subprocess
import logging
from model_registry import ModelRegistry, utils

def create_model_registry(registry, name, endpoint, bucket, path, region="us-east-1", description=""):
    try:
        model = registry.register_model(
            name=name,
            uri=utils.s3_uri_from(endpoint=endpoint, bucket=bucket, region=region, path=path),
            version="1.0.0",
            description=description,
            model_format_name="onnx",
            model_format_version="1",
            storage_key="my-data-connection",
            metadata={
                "int_key": 1,
                "bool_key": False,
                "float_key": 3.14,
                "str_key": "str_value",
            }
        )
        logging.info(f"Model '{model.name}' registered successfully.")
        return model
    except Exception as e:
        logging.error(f"Failed to register model: {e}")
        raise

def get_env_or_oc(var, oc_cmd):
    value = os.environ.get(var)
    if value:
        return value
    try:
        return subprocess.check_output(oc_cmd, shell=isinstance(oc_cmd, str)).strip().decode("utf-8")
    except Exception as e:
        logging.error(f"Failed to get {var}: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Get host from env or oc
    host = os.environ.get("HOST")
    if not host:
        cmd = (
            "oc describe svc modelregistry-sample -n rhoai-model-registries "
            "| grep 'routing.opendatahub.io/external-address-rest:' "
            "| awk -F': ' '{print $2}' "
            "| sed 's/^[[:space:]]*//;s/:443$//;s/^https\\?:\\/\\///'"
        )
        host_svc_address = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout.strip()
        host = f"https://{host_svc_address}"

    author = get_env_or_oc("AUTHOR", ["oc", "whoami"])
    user_token = get_env_or_oc("USER_TOKEN", ["oc", "whoami", "-t"])

    registry = ModelRegistry(host, author=author, user_token=user_token)

    create_model_registry(
        registry,
        name=os.environ.get("MODEL_NAME", "item-encoder"),
        endpoint=os.environ.get("MODEL_ENDPOINT", "http://minio-dspa.rec-sys-test.svc.cluster.local:9000"),
        bucket=os.environ.get("MODEL_BUCKET", "item-encoder"),
        path=os.environ.get("MODEL_PATH", "item-encoder.pth"),
        region=os.environ.get("MODEL_REGION", "us-east-1"),
        description=os.environ.get("MODEL_DESCRIPTION", "This is test model for demonstration purposes")
    )

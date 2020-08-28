from kubernetes import client, config
from kubernetes.client.rest import ApiException
import random
import string
import time
import os

# usage: docker run --rm --net=host  -v `pwd`/.kube/config:/root/.kube/config --env SERVICE_NUM=500  hub.c.163.com/qingzhou/istio/loadgen

def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


config.load_kube_config()
v1 = client.CoreV1Api()

ns = "loadgen"
nsObject = client.V1Namespace(metadata={"name": "loadgen"})

appsv1 = client.AppsV1Api()
selector = client.V1LabelSelector(match_labels={"app": "loadgen"})
deployment = client.V1Deployment(
    metadata={
        "name": "backend",
        "namespace": ns
    },
    spec={
        "replicas": 1,
        "selector": selector,
        "strategy": {
            "rollingUpdate": {
                "maxSurge": 1,
                "maxUnavailable": 1
            }
        },
        "template": {
            "metadata": {
                "labels": {
                    "app": "loadgen"
                }
            },
            "spec": {
                "containers": [
                    {
                        "name": "loadgen",
                        "image": "solsson/http-echo"
                    }
                ]
            }

        }
    }
)

try:
    service_num = int(os.environ.get("SERVICE_NUM", 1))
except:
    print("invalid env argument SERVICE_NUM %s" %
          os.environ.get("SERVICE_NUM"))
    exit(1)

to_create_namespace = os.environ.get("CREATE_NAMESPACE") != "0"
to_create_workload = os.environ.get("CREATE_WORKLOAD") != "0"

try:
    if to_create_namespace:
        v1.create_namespace(nsObject)
        time.sleep(1)

    if to_create_workload:
        appsv1.create_namespaced_deployment(namespace=ns, body=deployment)

    while service_num:
        service_num = service_num - 1

        service_meta = {
            "name": "loadgen-service-" + get_random_string(5),
            "namespace": ns
        }

        service_spec = {
            "selector": {
                "app": "loadgen"
            },
            "ports": [
                {
                    "port": 8080,
                    "targetPort": 80
                }
            ]
        }

        service = client.V1Service(metadata=service_meta, spec=service_spec)
        v1.create_namespaced_service(namespace=ns, body=service)

except ApiException as e:
    print("Error: %s\n" % e)

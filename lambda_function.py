import json
import sys

from kubernetes import client, config, watch
from k8s import k8s_deploy

def deploy(registry, image, name=None):
    print('deploying {} from {}'.format(image, registry))
    name = name or image.split(':')[0].split('/').pop()
    k8s_deploy(image, name)

def lambda_handler(event, context):
    config.load_kube_config()
    for record in event['Records']:
        msg = json.loads(record['Sns']['Message'])
        print(msg)
        deploy(msg.get('registry'), msg.get('image'), msg.get('name'))


    return {} 

if __name__ == '__main__':
    lambda_handler(json.load(sys.stdin), {})

from os import path

from kubernetes import client, config

def create_service_object(name, ports):
    service = client.V1Service()
    service.api_version = "v1"
    service.kind = "Service"
    service.metadata = client.V1ObjectMeta(name=name)

    spec = client.V1ServiceSpec()
    spec.selector = {"app": name}
    spec.type = 'LoadBalancer'
    spec.ports = [client.V1ServicePort(
            protocol=p.get('protocol', "TCP"), 
            port=p.get('port'), 
            target_port=p.get('target_port', p.get('port'))
        ) for p in ports if p.get('port') 
    ]
    service.spec = spec
    return service

def create_deployment_object(image, name, ports=[], replicas=1):
    container_ports = [client.V1ContainerPort(container_port=p) for p in ports]
    # Configure Pod template container
    container = client.V1Container(
        name=name,
        image=image,
        ports=container_ports)
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=replicas,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name='{}-deployment'.format(name)),
        spec=spec)

    return deployment


def create_deployment(api_instance, deployment, namespace='default'):
    # Create deployement
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace=namespace)
    print("Deployment created. status='%s'" % str(api_response.status))


def k8s_deploy(image, name, ports=[], namespace='default'):
    extensions_v1beta1 = client.ExtensionsV1beta1Api()
    # Create a deployment object with client-python API. The deployment we
    # created is same as the `nginx-deployment.yaml` in the /examples folder.
    p_valid_list = [p for p in ports if p.get('port')]
    p_target_list = [p.get('target_port', p.get('port')) for p in p_valid_list]
    deployment = create_deployment_object(image, name, p_target_list)

    create_deployment(extensions_v1beta1, deployment, namespace)

    if len(p_valid_list) == 0:
        return

    service = create_service_object(name, p_valid_list)
    core_v1api = client.CoreV1Api()
    core_v1api.create_namespaced_service(namespace=namespace, body=service)


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()
    k8s_deploy('nginx', 'nginx', [{'port': 80}])


if __name__ == '__main__':
    main()

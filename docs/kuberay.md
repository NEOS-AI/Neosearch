# Kuberay

[Kuberay](https://github.com/ray-project/kuberay) is a toolkit to run Ray applications on Kubernetes.

## Basic Usage

```bash
# Add the Helm repo
helm repo add kuberay https://ray-project.github.io/kuberay-helm/
helm repo update

# Confirm the repo exists
helm search repo kuberay --devel

# Install both CRDs and KubeRay operator v1.1.0.
helm install kuberay-operator kuberay/kuberay-operator --version 1.1.0

# Check the KubeRay operator Pod in `default` namespace
kubectl get pods
# NAME                                READY   STATUS    RESTARTS   AGE
# kuberay-operator-6fcbb94f64-mbfnr   1/1     Running   0          17s
```

Then deploy with the following yaml file:
```yaml
apiVersion: ray.io/v1alpha1
kind: RayCluster
metadata:
  name: example-cluster
spec:
  headGroupSpec:
    replicas: 1
    template:
      spec:
        containers:
        - name: ray-head
          image: rayproject/ray:latest
  workerGroupSpecs:
  - replicas: 2
    template:
      spec:
        containers:
        - name: ray-worker
          image: rayproject/ray:latest
```

Ray provides a dashboard for monitoring your cluster’s health, job progress, and resource usage. You can port-forward the dashboard service to your local machine:
```bash
kubectl port-forward service/example-cluster-head 8265:8265
```

## Why Ray?

Ray offers a range of capabilities to be integrated within the environment to achieve a better standpoint both on an application and organizational level.

- **Scalability**: Ray enables horizontal scaling, which divides work among numerous employees.
- **Integrations**: Google Cloud leverages the strength of GKE for managed infrastructure to provide a smooth interface between Ray and Kubernetes.
- **Dynamic Resource Allocation**: Resources can be dynamically allocated using Ray’s autoscaler in response to workload needs.
- **Robust Libraries**: Ray’s libraries, such as Ray Serve and Ray Tune, are appropriate for workloads on Google Cloud since they are optimized for AI, machine learning, and distributed data processing.

Ray cluster operations on Kubernetes are made easier by KubeRay, a Kubernetes operator.
Taking advantage of Kubernetes’ robust orchestration features, KubeRay enables you to deploy, operate, and scale Ray applications on a Kubernetes cluster by offering Kubernetes Custom Resource Definitions (CRDs) including RayCluster, RayJob, and RayService.

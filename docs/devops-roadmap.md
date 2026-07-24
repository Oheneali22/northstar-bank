# Northstar Bank DevOps Roadmap

This roadmap uses Northstar Bank as a hands-on path from source control to operating an observable application on AWS. The goal is not to memorize every configuration field. The goal is to understand system boundaries, make safe changes, verify outcomes, and troubleshoot using evidence.

## Completed

- Git feature-branch and pull-request workflow
- GitHub Actions continuous integration
- Web and API tests, linting, and production builds
- Multi-stage Docker images
- Docker Compose development stack
- Immutable image publication to private Amazon ECR repositories
- GitHub OIDC authentication to AWS
- Terraform remote state in a protected S3 bucket
- Terraform-managed VPC across two Availability Zones
- Public and private subnets with a cost-conscious single NAT gateway
- Terraform-managed Amazon EKS cluster and managed worker node
- EKS Pod Identity and EBS CSI integration
- Plain Kubernetes manifests for configuration, secrets, storage, PostgreSQL, API, and web
- Kubernetes troubleshooting with pods, events, logs, PVCs, probes, and rollout state
- Internal application verification through `kubectl port-forward`

## Completed: Controlled Public Entry

- Installed AWS Load Balancer Controller with dedicated Pod Identity and IAM permissions.
- Defined a Kubernetes Ingress for the web Service.
- Provisioned and inspected an internet-facing Application Load Balancer.
- Verified public application traffic through the ALB.
- Kept the Core API and PostgreSQL private.
- Deferred DNS and TLS until a suitable domain is available.

The ALB incurs an additional hourly charge and must be removed at the end of the exercise.

## Current: Continuous Delivery

1. Promote the exact immutable ECR SHA tested by CI.
2. Choose a deployment path that can securely reach the IP-restricted EKS API.
3. Automate deployment and rollout verification.
4. Fail delivery when readiness checks fail.
5. Practice release history and rollback.

## Kubernetes Reliability and Security

- Dedicated ServiceAccounts and least-privilege RBAC
- NetworkPolicies between web, API, and database
- Rolling-update and graceful-termination settings
- PodDisruptionBudgets
- Horizontal Pod Autoscaling and Metrics Server
- Review resource requests and limits
- Replace local lab credentials with managed secret delivery
- Explain the limitations of a one-node learning cluster

## Observability

### Metrics

- Prometheus
- Grafana
- kube-state-metrics
- Node metrics
- Scrape the Core API `/metrics` endpoint
- Application and Kubernetes dashboards
- Availability, error-rate, latency, and resource-pressure alerts

### Logs

- Centralized collection with CloudWatch or Loki
- Structured application logs
- Request-ID-based investigation

### Traces

- Introduce distributed tracing after metrics and logs are understood
- Follow a request through web, API, and dependencies

## Operational Exercise

- Kill a pod and observe self-healing
- Break database connectivity and follow readiness failures
- Deploy a bad image tag and inspect rollout failure
- Use events, logs, metrics, and dashboards to identify the cause
- Roll back to a healthy revision
- Write a concise incident runbook

## Cost-Safe Teardown

1. Remove public Ingress and wait for the ALB to be deleted.
2. Remove application workloads.
3. Delete PostgreSQL PVC and verify EBS deletion.
4. Destroy the Terraform-managed EKS and VPC environment.
5. Keep the inexpensive S3 state bucket and private ECR images unless intentionally retiring the project.

## Architecture Journey

```text
Developer push
      |
      v
GitHub Actions CI
      |
      v
Immutable images in private ECR
      |
      v
Continuous delivery
      |
      v
AWS ALB -> Ingress -> Web Service -> Web Pod
                                  |
                                  v
                         Core API Service -> API Pod
                                                  |
                                                  v
                                      PostgreSQL -> EBS
      |
      v
Metrics + logs + traces -> dashboards + alerts -> incident response
```

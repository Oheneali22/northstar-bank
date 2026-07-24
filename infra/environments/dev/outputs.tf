output "aws_account_id" {
  description = "AWS account currently selected by the provider credentials."
  value       = data.aws_caller_identity.current.account_id
}

output "aws_region" {
  description = "AWS region selected for this environment."
  value       = var.aws_region
}

output "selected_availability_zones" {
  description = "First two available Availability Zones considered for the development platform."
  value       = local.availability_zones
}

output "vpc_id" {
  description = "ID of the development VPC."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Subnets intended for internet-facing load balancers and the NAT gateway."
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "Subnets where the EKS worker nodes will run."
  value       = module.vpc.private_subnets
}

output "eks_cluster_name" {
  description = "Name used to connect kubectl and deployment tools to the EKS cluster."
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Kubernetes API endpoint created by EKS."
  value       = module.eks.cluster_endpoint
}

output "resource_name_prefix" {
  description = "Prefix that future AWS resources will use for consistent naming."
  value       = local.name_prefix
}

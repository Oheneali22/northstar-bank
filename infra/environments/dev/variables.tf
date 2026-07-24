variable "aws_region" {
  description = "AWS region where the development platform will run."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used consistently in AWS resource names and tags."
  type        = string
  default     = "northstar-bank"
}

variable "environment" {
  description = "Deployment environment represented by this Terraform root module."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "Private IPv4 address range reserved for the development VPC."
  type        = string
  default     = "10.10.0.0/16"
}

variable "kubernetes_version" {
  description = "Kubernetes version used by the EKS control plane."
  type        = string
  default     = "1.35"
}

variable "node_instance_types" {
  description = "EC2 instance types allowed for the EKS managed worker-node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "IPv4 CIDR ranges allowed to reach the public EKS Kubernetes API endpoint."
  type        = list(string)

  validation {
    condition = length(var.cluster_endpoint_public_access_cidrs) > 0 && alltrue([
      for cidr in var.cluster_endpoint_public_access_cidrs : can(cidrnetmask(cidr))
    ])
    error_message = "Provide at least one valid IPv4 CIDR range, normally your public IP followed by /32."
  }
}

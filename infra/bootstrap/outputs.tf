output "state_bucket_name" {
  description = "S3 bucket used by Northstar Bank Terraform root modules."
  value       = aws_s3_bucket.terraform_state.id
}

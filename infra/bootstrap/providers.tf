provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "northstar-bank"
      ManagedBy = "Terraform"
      Purpose   = "TerraformState"
    }
  }
}

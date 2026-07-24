terraform {
  backend "s3" {
    bucket       = "northstar-bank-terraform-state-942909611186"
    key          = "environments/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}

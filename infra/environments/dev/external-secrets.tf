data "aws_secretsmanager_secret" "northstar_database" {
  name = "Northbank-secret"
}

data "aws_iam_policy_document" "external_secrets_pod_identity" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
    ]

    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "external_secrets" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:DescribeSecret",
      "secretsmanager:GetSecretValue",
    ]
    resources = [data.aws_secretsmanager_secret.northstar_database.arn]
  }
}

resource "aws_iam_policy" "external_secrets" {
  name        = "${local.name_prefix}-external-secrets"
  description = "Allows External Secrets Operator to read the Northstar development database secret."
  policy      = data.aws_iam_policy_document.external_secrets.json
  tags        = local.common_tags
}

resource "aws_iam_role" "external_secrets" {
  name               = "${local.name_prefix}-external-secrets"
  assume_role_policy = data.aws_iam_policy_document.external_secrets_pod_identity.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "external_secrets" {
  role       = aws_iam_role.external_secrets.name
  policy_arn = aws_iam_policy.external_secrets.arn
}

resource "aws_eks_pod_identity_association" "external_secrets" {
  cluster_name    = module.eks.cluster_name
  namespace       = "external-secrets"
  service_account = "external-secrets"
  role_arn        = aws_iam_role.external_secrets.arn
}

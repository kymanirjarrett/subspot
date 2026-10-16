# Infrastructure

AWS resources are defined as CloudFormation templates and linted with `cfn-lint` in pre-commit.

| Template | Creates |
| --- | --- |
| `data-bucket.yml` | Encrypted, versioned, private S3 bucket for raw source data |

```bash
aws cloudformation deploy --template-file infra/data-bucket.yml \
  --stack-name subspot-data-dev --parameter-overrides Environment=dev
```

Planned: ingestion Lambda, Glue catalog and Athena workgroup, Step Functions weekly retrain, and
an AWS Budgets alarm so the project can't run up a bill.

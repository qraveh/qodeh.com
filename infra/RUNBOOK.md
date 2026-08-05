# qodeh.com — AWS S3 + CloudFront migration runbook

State as of 2026-08-05: Route53 zone `Z0617893M0JOC567V5M` live and authoritative
(NS switched at GoDaddy, verified globally). Site still serves from GitHub Pages.
Account 181188392834, region us-east-1. Everything below runs via `aws login`
session credentials (no stored keys) and is executed by Claude once authorized.

Naming: site bucket `qodeh-com-site`, logs bucket `qodeh-com-logs`
(no dots in bucket names — avoids S3 TLS wildcard quirks; OAC doesn't need
the bucket to match the domain).

## 1. ACM certificate (us-east-1, DNS-validated)

```bash
ARN=$(aws acm request-certificate --domain-name qodeh.com \
  --subject-alternative-names www.qodeh.com --validation-method DNS \
  --query CertificateArn --output text)
# Read the two validation CNAMEs and UPSERT them into Z0617893M0JOC567V5M,
# then: aws acm wait certificate-validated --certificate-arn "$ARN"
```

## 2. S3 buckets

```bash
aws s3api create-bucket --bucket qodeh-com-site
aws s3api put-public-access-block --bucket qodeh-com-site \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api create-bucket --bucket qodeh-com-logs
aws s3api put-public-access-block --bucket qodeh-com-logs \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
# Lifecycle: expire raw access logs after 400 days (tunable later).
```

## 3. CloudFront function + distribution

- Publish `infra/cloudfront-viewer-request.js` as function `qodeh-url-rewrite`
  (runtime cloudfront-js-2.0), associate on viewer-request of the default behavior.
- Distribution: aliases `qodeh.com`, `www.qodeh.com`; origin S3 REST endpoint for
  `qodeh-com-site` with **Origin Access Control** (sigv4, always sign); default
  root object `index.html`; viewer protocol redirect-to-https; HTTP/2+3;
  compression on; custom error response 404 -> `/404.html` (status 404);
  **standard logging (v2) to `qodeh-com-logs`** — this is the permanent
  per-request history that outlives the console reports' 60-day window;
  price class `PriceClass_All` (best latency incl. Israel edge).
- After creation: S3 bucket policy on `qodeh-com-site` allowing
  `cloudfront.amazonaws.com` with `AWS:SourceArn` = the distribution ARN.

## 4. GitHub Actions OIDC deploy

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com
# Role qodeh-site-deploy: trust policy federated to that provider, condition
#   token.actions.githubusercontent.com:sub = "repo:qraveh/qodeh.com:ref:refs/heads/main"
# Inline policy: s3:ListBucket on the bucket; s3:PutObject/GetObject/DeleteObject
#   on qodeh-com-site/*; cloudfront:CreateInvalidation on the distribution.
gh variable set AWS_DEPLOY_ROLE_ARN --repo qraveh/qodeh.com --body "<role arn>"
gh variable set AWS_S3_BUCKET --repo qraveh/qodeh.com --body "qodeh-com-site"
gh variable set AWS_CF_DISTRIBUTION_ID --repo qraveh/qodeh.com --body "<dist id>"
```

`.github/workflows/deploy-aws.yml` is already authored and inert until those
variables exist. First deploy: run it via workflow_dispatch, verify the
distribution URL serves the site correctly (Host-independent check).

## 5. Budget alarm

```bash
# Budget "qodeh-monthly" $2/mo, notify raveh@qodeh.com at 80% actual.
aws budgets create-budget --account-id 181188392834 --budget '{...}' \
  --notifications-with-subscribers '[{...}]'
```

## 6. Final cutover (only after user OK)

1. UPSERT in Z0617893M0JOC567V5M: `qodeh.com.` A + AAAA as **ALIAS** to the
   distribution (`dXXXX.cloudfront.net`, zone `Z2FDTNDATAQYW2`); repoint
   `www.qodeh.com.` CNAME to `dXXXX.cloudfront.net` (TTLs already low: 600/1800).
2. Verify: site on both hosts, TLS, 404 page, a PDF fetch, mail MX unchanged.
3. Retire `deploy.yml` (Pages) after a soak period; GitHub Pages remains
   functional as instant rollback (flip the A records back) until then.

## Verification checklist (post-cutover)

- [ ] `curl -I https://qodeh.com/` -> 200, `x-cache` header present (CloudFront)
- [ ] `curl -I https://www.qodeh.com/foo?q=1` -> 301 to `https://qodeh.com/foo?q=1`
- [ ] `curl -I https://qodeh.com/about` -> 301 `/about/`; `/about/` -> 200
- [ ] `curl -I https://qodeh.com/nope` -> 404 with site 404 page
- [ ] MX/autodiscover/SRV unchanged via 8.8.8.8
- [ ] Next day: Popular Objects report shows objects; logs bucket receiving

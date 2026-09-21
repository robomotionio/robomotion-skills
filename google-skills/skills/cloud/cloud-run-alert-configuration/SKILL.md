---
name: cloud-run-alert-configuration
metadata:
  category: Serverless
description: >-
  Configures best-practice, high-signal alerting policies for Google Cloud Run
  resources (services, jobs, and worker pools) based on seasoned SRE practices. Use
  when analyzing, recommending, writing, or deploying Terraform PromQL alerting
  policies to monitor Cloud Run error rates (4xx/5xx), request latency, container instance
  saturation (warning/critical), container CPU/memory utilization and allocation, billable
  instance time, job execution status, and worker pool queue backlog. Don't use for
  GKE workloads (use gke-alert-configuration) or Compute Engine VMs.
allowed-tools:
  - terraform
  - gcloud
---

# Cloud Run Alert Configuration

Production-grade observability for Google Cloud Run using Terraform and PromQL
(Cloud Monitoring). Grounded in SRE practices, this skill focuses strictly on
actionable user impact and scaling bounds.

--------------------------------------------------------------------------------

## CRITICAL RULES

*   **Gcloud SDK Prerequisites**: For this and any other `gcloud`-related tasks in
    this skill (such as resource discovery, parameter inspection, or metric scope
    centralization), ensure that the Google Cloud SDK (`gcloud`) is installed,
    authenticated, and configured with the target project (e.g. via
    `gcloud auth print-access-token` and `gcloud config get-value project`). If
    `gcloud` is missing or unconfigured, instruct the user to configure the SDK
    or fall back to parsing local workspace `.tf` files.
*   **Autonomous Discovery (Config First, CLI Second)**: Never prompt for names,
    regions, or ceilings if discoverable.
    *   **Config First**: Prioritize parsing local `.tf` files in the workspace.
        Look for `google_cloud_run_v2_service`, `google_cloud_run_service`,
        `google_cloud_run_v2_job`, `max_instance_count`, and Knative `maxScale`
        annotations (`autoscaling.knative.dev/maxScale` or `run.googleapis.com/maxScale`).
    *   **CLI Second (gcloud Fallback)**: If not discoverable via configuration,
        verify the `gcloud` SDK is present and configured with a valid project
        (`gcloud config get-value project`). Then execute `gcloud run services list --format="json"`,
        `gcloud run jobs list --format="json"`, or `gcloud monitoring metrics-scopes list`.
*   **Workload Routing**: Always classify the workload target and follow its
    specific reference guide:
    *   For HTTP Services follow [services.md](references/services.md)
    *   For Cloud Run Jobs follow [jobs.md](references/jobs.md)
    *   For Worker Pools follow [worker_pools.md](references/worker_pools.md)
*   **Explicit Defaults & User Overrides**:
    *   Always use explicit defaults for all constants specified in
        the target workload's reference file (SLO targets, latency thresholds,
        SLAs, saturation ceilings).
    *   State the defaults being applied in the final summary output and clearly
        notify the user that any default constant can be customized or
        overridden via Terraform variables or prompt input.
*   **Metric Scope Centralization**: Run `gcloud beta monitoring metrics-scopes
    list projects/[PROJECT_ID]`. If a scoping project
    (`locations/global/metricsScopes/[SCOPING_PROJECT_ID]`) exists, set
    `project = "[SCOPING_PROJECT_ID]"` in Terraform resources.
*   **PromQL `duration` (Retest Window) Rules**:
    *   **Lookbacks $\le$ 25h**: Set `duration = "300s"` (5m buffer) to absorb
        transient blips and scale-up lag (except immediate job failure alerts
        which use `duration = "0s"`).
    *   **Lookbacks $> 25$h** (e.g. 3d/7d Slow Burn): **Omit `duration`
        entirely** (or set to `0s`). Cloud Monitoring rejects PromQL queries
        with `duration` set on lookbacks >25h (`INVALID_ARGUMENT`).

*   **Terraform Standards**: Output clean `.tf` configurations using
    `google_monitoring_alert_policy` and `condition_prometheus_query_language`.
    Include `alert_strategy { auto_close = "604800s" }` and parameterize
    `notification_channels = var.notification_channels`.

## WORKFLOW STEPS

### 1. Discovery & Target Identification (Config First, CLI Second)

*   **Config First**: Scan workspace `.tf` files for `google_cloud_run_v2_service`,
    `google_cloud_run_service`, `google_cloud_run_v2_job`, and worker pool resources.
*   **CLI Second**: If not found in config, verify `gcloud` is installed and has a valid project
    configured (`gcloud config get-value project`), then run `gcloud` discovery commands.
*   Group targets by workload type: HTTP Services, Jobs, or Worker Pools.
*   Identify the scoping project using `gcloud monitoring metrics-scopes`.

### 2. Configure Alerts

*   Route to the corresponding guide to generate the alert policies:
    *   **HTTP Services**: Open [services.md](references/services.md). Apply the
        comprehensive alerting suite covering availability SLOs (5xx), request
        latency (P95/P99), client errors (4xx), container instance saturation,
        container CPU/memory utilization, traffic anomalies, and billable
        instance time.
    *   **Batch Jobs**: Open [jobs.md](references/jobs.md). Apply immediate job
        execution failure alerts.
    *   **Worker Pools**: Open [worker_pools.md](references/worker_pools.md).
        Apply the 4-policy standard suite (Task Success SLO Fast/Slow Burn,
        Backlog ETD, Message Age SLA).

### 3. Terraform Generation & Review

*   Write the HCL configuration to `.tf` files with explicitly parameterized
    defaults.
*   State the applied defaults and remind the user of their ability to override
    any constant.
*   Provide a clear plain-English breakdown of the PromQL logic and triggering
    thresholds.

--------------------------------------------------------------------------------

## Additional Resources

*   [Google Cloud Run Documentation](https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run.md.txt)
*   [Google Cloud Monitoring PromQL Documentation](https://docs.cloud.google.com/monitoring/promql/promql-in-monitoring.md.txt)
*   [Google Cloud Alerting Policies in Terraform](https://docs.cloud.google.com/monitoring/alerts/terraform.md.txt)
*   [Google SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)

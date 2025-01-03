from google.cloud import monitoring_v3
import time

# Replace with your GCP Project ID
project_id = "your-project-id"

# Create a metric
def create_custom_metric():
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    # Define metric descriptor
    descriptor = monitoring_v3.MetricDescriptor()
    descriptor.type = "custom.googleapis.com/app/cpu_usage"
    descriptor.metric_kind = monitoring_v3.MetricDescriptor.MetricKind.GAUGE
    descriptor.value_type = monitoring_v3.MetricDescriptor.ValueType.DOUBLE
    descriptor.description = "Tracks CPU usage percentage for the application"

    # Labels for metric
    descriptor.labels.append(
        monitoring_v3.LabelDescriptor(key="instance_id", value_type="STRING", description="Instance ID")
    )

    # Create metric
    descriptor = client.create_metric_descriptor(name=project_name, metric_descriptor=descriptor)
    print(f"Created custom metric: {descriptor.name}")

# Write data points
def write_time_series():
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/app/cpu_usage"
    series.resource.type = "gce_instance"
    series.resource.labels["instance_id"] = "1234567890123456789"  # Replace with your instance ID
    series.resource.labels["zone"] = "us-central1-a"  # Replace with your instance zone

    # Add data point
    point = monitoring_v3.Point()
    point.value.double_value = 80.0  # Simulated CPU usage (80%)
    now = time.time()
    point.interval.end_time.seconds = int(now)
    point.interval.start_time.seconds = int(now)

    series.points.append(point)
    client.create_time_series(name=project_name, time_series=[series])
    print("Uploaded data point.")

# Create an alert policy
def create_alert_policy():
    client = monitoring_v3.AlertPolicyServiceClient()
    project_name = f"projects/{project_id}"

    condition = monitoring_v3.AlertPolicy.Condition(
        display_name="High CPU Usage",
        condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
            filter='metric.type="custom.googleapis.com/app/cpu_usage" AND resource.type="gce_instance"',
            comparison=monitoring_v3.ComparisonType.COMPARISON_GT,
            threshold_value=75,  # Alert if CPU > 75%
            duration={"seconds": 60},  # For 60 seconds
            aggregations=[{"alignment_period": {"seconds": 60}, "per_series_aligner": "ALIGN_MEAN"}],
        ),
    )

    alert_policy = monitoring_v3.AlertPolicy(
        display_name="CPU Usage Alert Policy",
        conditions=[condition],
        combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.AND,
        notification_channels=[],  # Add notification channels here
        enabled=True,
    )

    policy = client.create_alert_policy(name=project_name, alert_policy=alert_policy)
    print(f"Created alert policy: {policy.name}")

# Execute functions
create_custom_metric()
write_time_series()
create_alert_policy()

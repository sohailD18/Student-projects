"""
OptiFlow - AI-Based Business Process Optimizer
AI Engine for Bottleneck Detection and Process Analysis

This module implements statistical analysis algorithms to:
1. Detect process bottlenecks using standard deviation and moving averages
2. Identify performance anomalies
3. Generate optimization recommendations
4. Calculate efficiency scores and impact metrics
"""

import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from decimal import Decimal


class ProcessAnalyzer:
    """
    Core AI engine for analyzing business process performance.
    Uses statistical methods to identify bottlenecks and optimization opportunities.
    """

    def __init__(self, confidence_threshold: float = 1.5):
        """
        Initialize the analyzer.

        Args:
            confidence_threshold: Number of standard deviations above mean to flag as bottleneck
                                Default 1.5 (loose), 2.0 (standard), 2.5 (strict)
        """
        self.confidence_threshold = confidence_threshold

    def calculate_mean(self, data: List[float]) -> float:
        """Calculate arithmetic mean of a dataset."""
        if not data:
            return 0.0
        return statistics.mean(data)

    def calculate_median(self, data: List[float]) -> float:
        """Calculate median of a dataset."""
        if not data:
            return 0.0
        return statistics.median(data)

    def calculate_std_dev(self, data: List[float]) -> float:
        """Calculate standard deviation of a dataset."""
        if len(data) < 2:
            return 0.0
        return statistics.stdev(data)

    def calculate_variance(self, data: List[float]) -> float:
        """Calculate variance of a dataset."""
        if len(data) < 2:
            return 0.0
        return statistics.variance(data)

    def calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate a specific percentile of the dataset."""
        if not data:
            return 0.0
        return statistics.quantiles(data, n=100)[percentile - 1] if len(data) > 1 else data[0]

    def calculate_moving_average(self, data: List[float], window: int = 3) -> List[float]:
        """
        Calculate moving average over a window.

        Args:
            data: List of values
            window: Window size for moving average

        Returns:
            List of moving averages
        """
        if not data or window <= 0:
            return []

        moving_avgs = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            window_data = data[start:i + 1]
            moving_avgs.append(statistics.mean(window_data))

        return moving_avgs

    def detect_outliers(self, data: List[float]) -> Tuple[List[float], List[float]]:
        """
        Detect outliers using the IQR (Interquartile Range) method.

        Args:
            data: List of values

        Returns:
            Tuple of (lower_outliers, upper_outliers)
        """
        if len(data) < 4:
            return [], []

        sorted_data = sorted(data)
        q1 = statistics.quantiles(sorted_data, n=4)[0]
        q3 = statistics.quantiles(sorted_data, n=4)[2]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        lower_outliers = [x for x in data if x < lower_bound]
        upper_outliers = [x for x in data if x > upper_bound]

        return lower_outliers, upper_outliers

    def detect_bottlenecks(self, step_data: Dict[str, List[float]]) -> List[Dict]:
        """
        Detect bottlenecks in process steps using statistical analysis.

        Args:
            step_data: Dictionary mapping step names to execution time lists

        Returns:
            List of bottleneck detections with metadata
        """
        bottlenecks = []

        for step_name, times in step_data.items():
            if len(times) < 3:
                continue

            mean_time = self.calculate_mean(times)
            std_dev = self.calculate_std_dev(times)
            median_time = self.calculate_median(times)

            # Calculate threshold
            threshold = mean_time + (self.confidence_threshold * std_dev)

            # Find outlier instances
            outliers = [t for t in times if t > threshold]

            if outliers:
                avg_outlier_time = self.calculate_mean(outliers)
                normal_time = self.calculate_mean([t for t in times if t <= threshold])

                # Calculate deviation percentage
                deviation_pct = ((avg_outlier_time - normal_time) / normal_time) * 100 if normal_time > 0 else 0

                bottlenecks.append({
                    'step_name': step_name,
                    'mean_time': mean_time,
                    'median_time': median_time,
                    'std_dev': std_dev,
                    'threshold': threshold,
                    'outlier_count': len(outliers),
                    'outlier_times': outliers,
                    'avg_outlier_time': avg_outlier_time,
                    'normal_time': normal_time,
                    'deviation_percentage': deviation_pct,
                    'total_executions': len(times),
                    'severity': self._calculate_severity(deviation_pct, len(outliers), len(times))
                })

        # Sort by severity
        bottlenecks.sort(key=lambda x: x['severity'], reverse=True)
        return bottlenecks

    def _calculate_severity(self, deviation_pct: float, outlier_count: int, total_count: int) -> float:
        """
        Calculate severity score for a bottleneck.

        Args:
            deviation_pct: Percentage deviation from normal
            outlier_count: Number of outliers
            total_count: Total number of executions

        Returns:
            Severity score (0-100)
        """
        # Outlier frequency weight
        frequency_weight = (outlier_count / total_count) * 50 if total_count > 0 else 0

        # Deviation magnitude weight (capped at 50)
        deviation_weight = min(deviation_pct / 2, 50)

        severity = frequency_weight + deviation_weight
        return min(severity, 100)

    def calculate_efficiency_score(self, execution_times: List[float],
                                    target_time: Optional[float] = None) -> Dict:
        """
        Calculate efficiency score for a process or step.

        Args:
            execution_times: List of execution times
            target_time: Target execution time (optional)

        Returns:
            Dictionary with efficiency metrics
        """
        if not execution_times:
            return {
                'efficiency_score': 0,
                'avg_time': 0,
                'median_time': 0,
                'p95_time': 0,
                'consistency_score': 0
            }

        avg_time = self.calculate_mean(execution_times)
        median_time = self.calculate_median(execution_times)

        # Calculate 95th percentile
        sorted_times = sorted(execution_times)
        p95_index = int(len(sorted_times) * 0.95)
        p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]

        # Calculate coefficient of variation (consistency)
        std_dev = self.calculate_std_dev(execution_times)
        cv = (std_dev / avg_time * 100) if avg_time > 0 else 0
        consistency_score = max(0, 100 - cv)

        # Calculate efficiency score
        if target_time and target_time > 0:
            efficiency_score = max(0, min(100, (target_time / avg_time) * 100))
        else:
            # Use relative efficiency based on consistency
            efficiency_score = (consistency_score + 100) / 2

        return {
            'efficiency_score': round(efficiency_score, 2),
            'avg_time': round(avg_time, 2),
            'median_time': round(median_time, 2),
            'p95_time': round(p95_time, 2),
            'consistency_score': round(consistency_score, 2),
            'std_dev': round(std_dev, 2)
        }

    def generate_recommendations(self, bottlenecks: List[Dict]) -> List[Dict]:
        """
        Generate actionable recommendations based on bottleneck analysis.

        Args:
            bottlenecks: List of detected bottlenecks

        Returns:
            List of recommendations with priority and impact
        """
        recommendations = []

        for bottleneck in bottlenecks:
            step_name = bottleneck['step_name']
            severity = bottleneck['severity']
            deviation = bottleneck['deviation_percentage']
            normal_time = bottleneck['normal_time']

            # Determine priority
            if severity >= 70:
                priority = 'critical'
            elif severity >= 50:
                priority = 'high'
            elif severity >= 30:
                priority = 'medium'
            else:
                priority = 'low'

            # Generate specific recommendations
            if deviation > 100:
                category = 'bottleneck'
                title = f"Critical Bottleneck: {step_name} exceeds normal time by {deviation:.1f}%"
                description = (
                    f"Step '{step_name}' is experiencing severe performance issues. "
                    f"Normal execution time: {normal_time:.2f} minutes, but outlier instances "
                    f"are averaging {bottleneck['avg_outlier_time']:.2f} minutes. "
                    f"This occurs in {bottleneck['outlier_count']} out of {bottleneck['total_executions']} executions."
                )
                recommendation_text = (
                    f"1. Investigate root causes of delays in {step_name}\n"
                    f"2. Consider parallel processing or automation\n"
                    f"3. Review resource allocation during peak loads\n"
                    f"4. Implement queue management if applicable"
                )
                potential_savings = bottleneck['avg_outlier_time'] - normal_time

            elif deviation > 50:
                category = 'performance'
                title = f"Performance Issue: {step_name} exceeds baseline by {deviation:.1f}%"
                description = (
                    f"Step '{step_name}' shows significant performance variation. "
                    f"Execution times are inconsistent, indicating potential optimization opportunities."
                )
                recommendation_text = (
                    f"1. Optimize the workflow for {step_name}\n"
                    f"2. Review and eliminate unnecessary sub-steps\n"
                    f"3. Consider partial automation of manual tasks\n"
                    f"4. Implement monitoring for early warning"
                )
                potential_savings = bottleneck['avg_outlier_time'] - normal_time

            elif bottleneck['outlier_count'] / bottleneck['total_executions'] > 0.3:
                category = 'process'
                title = f"Process Variability: {step_name} inconsistent performance"
                description = (
                    f"Step '{step_name}' shows high variability in execution times. "
                    f"This inconsistency suggests the process may need standardization."
                )
                recommendation_text = (
                    f"1. Standardize the procedure for {step_name}\n"
                    f"2. Create clear SOPs (Standard Operating Procedures)\n"
                    f"3. Training for personnel executing this step\n"
                    f"4. Implement validation checks"
                )
                potential_savings = bottleneck['std_dev'] * 0.5

            else:
                category = 'automation'
                title = f"Automation Opportunity: {step_name}"
                description = (
                    f"Step '{step_name}' shows moderate delays that could be improved "
                    f"through selective automation or optimization."
                )
                recommendation_text = (
                    f"1. Evaluate automation tools for {step_name}\n"
                    f"2. Streamline decision points\n"
                    f"3. Reduce manual handoffs"
                )
                potential_savings = normal_time * 0.2

            recommendations.append({
                'step_name': step_name,
                'title': title,
                'category': category,
                'priority': priority,
                'description': description,
                'recommendation': recommendation_text,
                'current_value': bottleneck['avg_outlier_time'],
                'target_value': normal_time,
                'potential_savings': round(potential_savings, 2),
                'impact_score': round(severity, 2),
                'analysis_data': bottleneck
            })

        return recommendations

    def analyze_trends(self, time_series_data: List[Tuple[datetime, float]]) -> Dict:
        """
        Analyze trends in time series data.

        Args:
            time_series_data: List of (timestamp, value) tuples

        Returns:
            Dictionary with trend analysis
        """
        if len(time_series_data) < 2:
            return {'trend': 'insufficient_data', 'direction': 'neutral'}

        # Sort by timestamp
        sorted_data = sorted(time_series_data, key=lambda x: x[0])
        values = [v for _, v in sorted_data]

        # Calculate simple linear regression slope
        n = len(values)
        x = list(range(n))
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi ** 2 for xi in x)

        if n * sum_x2 - sum_x ** 2 == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        # Determine trend
        if slope > 0.1:
            direction = 'increasing'
            trend = 'degrading' if values[-1] > values[0] else 'improving'
        elif slope < -0.1:
            direction = 'decreasing'
            trend = 'improving' if values[-1] < values[0] else 'degrading'
        else:
            direction = 'stable'
            trend = 'stable'

        # Calculate percent change
        if values[0] != 0:
            percent_change = ((values[-1] - values[0]) / values[0]) * 100
        else:
            percent_change = 0

        return {
            'trend': trend,
            'direction': direction,
            'slope': round(slope, 4),
            'percent_change': round(percent_change, 2),
            'start_value': round(values[0], 2),
            'end_value': round(values[-1], 2),
            'data_points': n
        }

    def calculate_process_health(self, metrics: Dict) -> Dict:
        """
        Calculate overall process health score.

        Args:
            metrics: Dictionary of process metrics

        Returns:
            Health assessment with score and recommendations
        """
        weights = {
            'cycle_time': 0.3,
            'efficiency': 0.25,
            'quality': 0.25,
            'bottleneck_score': 0.2
        }

        weighted_score = 0
        for key, weight in weights.items():
            value = metrics.get(key, 0)
            # Normalize to 0-100
            normalized = min(max(value, 0), 100)
            weighted_score += normalized * weight

        # Determine health level
        if weighted_score >= 80:
            health_level = 'excellent'
            color = 'green'
        elif weighted_score >= 60:
            health_level = 'good'
            color = 'blue'
        elif weighted_score >= 40:
            health_level = 'fair'
            color = 'yellow'
        else:
            health_level = 'poor'
            color = 'red'

        return {
            'health_score': round(weighted_score, 2),
            'health_level': health_level,
            'health_color': color,
            'metrics': metrics
        }


class ProcessDataCollector:
    """
    Helper class to collect and format data from Django models
    for analysis by the AI engine.
    """

    @staticmethod
    def collect_step_execution_times(process_id: int, step_id: int = None) -> Dict[str, List[float]]:
        """
        Collect execution times for analysis.

        Args:
            process_id: BusinessProcess ID
            step_id: Optional ProcessStep ID to filter

        Returns:
            Dictionary mapping step names to execution time lists
        """
        from core.models import OperationalData, ProcessStep

        query = OperationalData.objects.filter(
            process_id=process_id,
            status='completed'
        ).exclude(execution_time__isnull=True)

        if step_id:
            query = query.filter(step_id=step_id)

        step_data = {}
        for log in query.select_related('step'):
            step_name = log.step.name if log.step else 'Process Level'
            if step_name not in step_data:
                step_data[step_name] = []
            step_data[step_name].append(log.execution_time)

        return step_data

    @staticmethod
    def collect_time_series(process_id: int, days: int = 30) -> List[Tuple[datetime, float]]:
        """
        Collect time series data for trend analysis.

        Args:
            process_id: BusinessProcess ID
            days: Number of days to look back

        Returns:
            List of (timestamp, execution_time) tuples
        """
        from core.models import OperationalData
        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=days)

        logs = OperationalData.objects.filter(
            process_id=process_id,
            status='completed',
            created_at__gte=cutoff_date
        ).exclude(execution_time__isnull=True).order_by('created_at')

        return [(log.created_at, log.execution_time) for log in logs]


def analyze_process(process_id: int, confidence_threshold: float = 1.5) -> Dict:
    """
    Main function to perform complete process analysis.

    Args:
        process_id: BusinessProcess ID to analyze
        confidence_threshold: Statistical confidence threshold

    Returns:
        Complete analysis results
    """
    analyzer = ProcessAnalyzer(confidence_threshold=confidence_threshold)
    collector = ProcessDataCollector()

    # Collect data
    step_data = collector.collect_step_execution_times(process_id)
    time_series = collector.collect_time_series(process_id)

    # Perform analysis
    bottlenecks = analyzer.detect_bottlenecks(step_data)
    recommendations = analyzer.generate_recommendations(bottlenecks)
    trend_analysis = analyzer.analyze_trends(time_series)

    # Calculate overall metrics
    all_times = []
    for times in step_data.values():
        all_times.extend(times)

    efficiency_metrics = analyzer.calculate_efficiency_score(all_times)
    health_metrics = analyzer.calculate_process_health({
        'cycle_time': efficiency_metrics.get('efficiency_score', 0),
        'efficiency': efficiency_metrics.get('efficiency_score', 0),
        'quality': efficiency_metrics.get('consistency_score', 0),
        'bottleneck_score': 100 - (bottlenecks[0]['severity'] if bottlenecks else 0)
    })

    return {
        'process_id': process_id,
        'bottlenecks': bottlenecks,
        'recommendations': recommendations,
        'efficiency_metrics': efficiency_metrics,
        'trend_analysis': trend_analysis,
        'health_assessment': health_metrics,
        'analyzed_at': datetime.now().isoformat()
    }

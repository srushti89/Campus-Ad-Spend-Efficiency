"""
Analysis utilities for Campus Ad Spend Efficiency project

This module contains utility functions for:
- Attribution modeling
- Statistical analysis
- Performance optimization
- ROI calculations
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

class ChannelAnalyzer:
    """Advanced analytics for channel performance"""
    
    def __init__(self):
        self.attribution_results = {}
        self.optimization_results = {}
    
    def pareto_analysis(self, df, value_col='revenue', entity_col='channel'):
        """
        Perform Pareto analysis to identify top performing entities
        Returns the 80/20 breakdown
        """
        
        # Calculate total value by entity
        entity_values = df.groupby(entity_col)[value_col].sum().sort_values(ascending=False)
        
        # Calculate cumulative percentage
        total_value = entity_values.sum()
        entity_values_pct = (entity_values / total_value * 100).cumsum()
        
        # Find entities that contribute to 80% of value
        top_entities = entity_values_pct[entity_values_pct <= 80].index
        
        # Calculate statistics
        top_entity_count = len(top_entities)
        total_entity_count = len(entity_values)
        top_entity_percentage = (top_entity_count / total_entity_count) * 100
        top_entity_value_percentage = entity_values_pct.iloc[top_entity_count - 1]
        
        return {
            'top_entities': top_entities.tolist(),
            'top_entity_count': top_entity_count,
            'total_entity_count': total_entity_count,
            'top_entity_percentage': top_entity_percentage,
            'top_entity_value_percentage': top_entity_value_percentage,
            'entity_values': entity_values,
            'cumulative_percentages': entity_values_pct
        }
    
    def calculate_efficiency_scores(self, df):
        """
        Calculate efficiency scores for each channel using multiple metrics
        """
        
        # Group by channel and calculate metrics
        channel_metrics = df.groupby('channel').agg({
            'cost': 'sum',
            'revenue': 'sum',
            'conversions': 'sum',
            'clicks': 'sum',
            'impressions': 'count'
        })
        
        # Calculate derived metrics
        channel_metrics['roas'] = channel_metrics['revenue'] / channel_metrics['cost']
        channel_metrics['cost_per_conversion'] = channel_metrics['cost'] / channel_metrics['conversions']
        channel_metrics['conversion_rate'] = channel_metrics['conversions'] / channel_metrics['clicks']
        channel_metrics['ctr'] = channel_metrics['clicks'] / channel_metrics['impressions']
        
        # Normalize metrics for scoring (higher is better)
        scaler = MinMaxScaler()
        
        # For metrics where lower is better, invert them
        channel_metrics['cost_efficiency'] = 1 / channel_metrics['cost_per_conversion']
        
        # Select metrics for scoring
        scoring_metrics = ['roas', 'cost_efficiency', 'conversion_rate', 'ctr']
        
        # Normalize scores
        normalized_scores = pd.DataFrame(
            scaler.fit_transform(channel_metrics[scoring_metrics]),
            index=channel_metrics.index,
            columns=scoring_metrics
        )
        
        # Calculate composite efficiency score
        weights = {'roas': 0.4, 'cost_efficiency': 0.3, 'conversion_rate': 0.2, 'ctr': 0.1}
        normalized_scores['efficiency_score'] = sum(
            normalized_scores[metric] * weight for metric, weight in weights.items()
        )
        
        return channel_metrics.join(normalized_scores[['efficiency_score']])
    
    def budget_optimization(self, channel_metrics, total_budget, min_budget_pct=0.05):
        """
        Optimize budget allocation based on efficiency scores and constraints
        """
        
        # Calculate current allocation
        current_budget = channel_metrics['cost'].copy()
        current_total = current_budget.sum()
        
        # Scale to match total budget
        current_allocation = current_budget / current_total * total_budget
        
        # Calculate optimal allocation based on efficiency scores
        efficiency_weights = channel_metrics['efficiency_score'] / channel_metrics['efficiency_score'].sum()
        optimal_allocation = efficiency_weights * total_budget
        
        # Apply minimum budget constraint
        min_budget = total_budget * min_budget_pct
        
        # Adjust for minimum constraints
        channels_below_min = optimal_allocation < min_budget
        if channels_below_min.any():
            # Set minimum budget for channels below threshold
            optimal_allocation[channels_below_min] = min_budget
            
            # Redistribute remaining budget among other channels
            remaining_budget = total_budget - (channels_below_min.sum() * min_budget)
            remaining_channels = ~channels_below_min
            
            if remaining_channels.any():
                remaining_weights = efficiency_weights[remaining_channels]
                remaining_weights = remaining_weights / remaining_weights.sum()
                optimal_allocation[remaining_channels] = remaining_weights * remaining_budget
        
        # Calculate expected improvement
        allocation_change = optimal_allocation - current_allocation
        efficiency_scores = channel_metrics['efficiency_score']
        
        # Estimate performance improvement (simplified model)
        expected_improvement = (allocation_change * efficiency_scores).sum() / current_total
        
        return {
            'current_allocation': current_allocation,
            'optimal_allocation': optimal_allocation,
            'allocation_change': allocation_change,
            'allocation_change_pct': (allocation_change / current_allocation * 100),
            'expected_improvement_pct': expected_improvement * 100,
            'reallocation_summary': self._create_reallocation_summary(
                current_allocation, optimal_allocation, channel_metrics
            )
        }
    
    def _create_reallocation_summary(self, current, optimal, metrics):
        """Create a summary of budget reallocation recommendations"""
        
        change_pct = (optimal - current) / current * 100
        
        summary = pd.DataFrame({
            'current_budget': current,
            'optimal_budget': optimal,
            'change_amount': optimal - current,
            'change_pct': change_pct,
            'efficiency_score': metrics['efficiency_score'],
            'current_roas': metrics['roas']
        })
        
        # Categorize changes
        summary['recommendation'] = 'maintain'
        summary.loc[summary['change_pct'] > 10, 'recommendation'] = 'increase'
        summary.loc[summary['change_pct'] < -10, 'recommendation'] = 'decrease'
        
        return summary.sort_values('change_pct', ascending=False)
    
    def attribution_comparison(self, journey_df, conversion_value_col='conversion_value'):
        """
        Compare different attribution models
        """
        
        models = {
            'last_touch': self._last_touch_attribution,
            'first_touch': self._first_touch_attribution,
            'linear': self._linear_attribution,
            'time_decay': self._time_decay_attribution
        }
        
        results = {}
        
        for model_name, model_func in models.items():
            attributed_value = model_func(journey_df, conversion_value_col)
            results[model_name] = attributed_value
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame(results)
        comparison_df['variance'] = comparison_df.var(axis=1)
        comparison_df['mean_attribution'] = comparison_df[list(models.keys())].mean(axis=1)
        
        self.attribution_results = {
            'model_results': results,
            'comparison': comparison_df,
            'correlation_matrix': comparison_df[list(models.keys())].corr()
        }
        
        return self.attribution_results
    
    def _last_touch_attribution(self, df, value_col):
        """Last-touch attribution model"""
        return df.groupby('channel').agg({value_col: 'sum'})
    
    def _first_touch_attribution(self, df, value_col):
        """First-touch attribution model"""
        # Assuming user journey is sorted by timestamp
        first_touch = df.groupby('user_id').first()
        return first_touch.groupby('channel').agg({value_col: 'sum'})
    
    def _linear_attribution(self, df, value_col):
        """Linear attribution model"""
        # Equal weight to all touchpoints in a user's journey
        user_touchpoint_counts = df.groupby('user_id')['channel'].count()
        df_attributed = df.copy()
        df_attributed['attributed_value'] = df_attributed.apply(
            lambda row: row[value_col] / user_touchpoint_counts[row['user_id']], axis=1
        )
        return df_attributed.groupby('channel')['attributed_value'].sum()
    
    def _time_decay_attribution(self, df, value_col, decay_rate=7):
        """Time-decay attribution model"""
        df_sorted = df.sort_values(['user_id', 'timestamp'])
        
        def calculate_time_weights(group):
            if len(group) == 1:
                group['time_weight'] = 1.0
                return group
            
            # Calculate days from conversion
            max_time = group['conversion_timestamp'].max()
            group['days_to_conversion'] = (max_time - group['timestamp']).dt.days
            
            # Apply exponential decay
            group['time_weight'] = np.exp(-group['days_to_conversion'] / decay_rate)
            
            # Normalize weights to sum to 1 per user
            total_weight = group['time_weight'].sum()
            group['time_weight'] = group['time_weight'] / total_weight
            
            return group
        
        df_weighted = df_sorted.groupby('user_id').apply(calculate_time_weights)
        df_weighted['attributed_value'] = df_weighted[value_col] * df_weighted['time_weight']
        
        return df_weighted.groupby('channel')['attributed_value'].sum()
    
    def statistical_significance_test(self, control_metrics, treatment_metrics, metric='conversion_rate'):
        """
        Test statistical significance between control and treatment groups
        """
        
        control_values = control_metrics[metric]
        treatment_values = treatment_metrics[metric]
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(control_values, treatment_values)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(control_values) - 1) * control_values.var() + 
                             (len(treatment_values) - 1) * treatment_values.var()) / 
                             (len(control_values) + len(treatment_values) - 2))
        
        cohens_d = (treatment_values.mean() - control_values.mean()) / pooled_std
        
        # Calculate confidence interval for the difference
        diff_mean = treatment_values.mean() - control_values.mean()
        diff_se = pooled_std * np.sqrt(1/len(control_values) + 1/len(treatment_values))
        ci_lower = diff_mean - 1.96 * diff_se
        ci_upper = diff_mean + 1.96 * diff_se
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'is_significant': p_value < 0.05,
            'effect_size_cohens_d': cohens_d,
            'mean_difference': diff_mean,
            'confidence_interval': (ci_lower, ci_upper),
            'control_mean': control_values.mean(),
            'treatment_mean': treatment_values.mean()
        }

class ReportGenerator:
    """Generate analysis reports and visualizations"""
    
    def __init__(self):
        self.figures = []
    
    def create_channel_performance_report(self, channel_metrics):
        """Create comprehensive channel performance report"""
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Channel Performance Analysis', fontsize=16, fontweight='bold')
        
        # ROAS by channel
        channel_metrics.sort_values('roas', ascending=True).plot(
            x='channel', y='roas', kind='barh', ax=axes[0,0], color='skyblue'
        )
        axes[0,0].set_title('Return on Ad Spend (ROAS) by Channel')
        axes[0,0].set_xlabel('ROAS')
        
        # Cost per conversion
        channel_metrics.sort_values('cost_per_conversion', ascending=True).plot(
            x='channel', y='cost_per_conversion', kind='barh', ax=axes[0,1], color='lightcoral'
        )
        axes[0,1].set_title('Cost per Conversion by Channel')
        axes[0,1].set_xlabel('Cost per Conversion ($)')
        
        # Conversion rate
        channel_metrics.sort_values('conversion_rate', ascending=True).plot(
            x='channel', y='conversion_rate', kind='barh', ax=axes[1,0], color='lightgreen'
        )
        axes[1,0].set_title('Conversion Rate by Channel')
        axes[1,0].set_xlabel('Conversion Rate (%)')
        
        # Efficiency score
        if 'efficiency_score' in channel_metrics.columns:
            channel_metrics.sort_values('efficiency_score', ascending=True).plot(
                x='channel', y='efficiency_score', kind='barh', ax=axes[1,1], color='gold'
            )
            axes[1,1].set_title('Efficiency Score by Channel')
            axes[1,1].set_xlabel('Efficiency Score')
        
        plt.tight_layout()
        return fig
    
    def create_attribution_comparison_chart(self, attribution_results):
        """Create attribution model comparison chart"""
        
        comparison_df = attribution_results['comparison']
        models = [col for col in comparison_df.columns if col not in ['variance', 'mean_attribution']]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Attribution by model
        comparison_df[models].plot(kind='bar', ax=ax1)
        ax1.set_title('Attribution Value by Model')
        ax1.set_xlabel('Channel')
        ax1.set_ylabel('Attributed Value')
        ax1.legend(title='Attribution Model')
        ax1.tick_params(axis='x', rotation=45)
        
        # Model correlation heatmap
        correlation_matrix = attribution_results['correlation_matrix']
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax2)
        ax2.set_title('Attribution Model Correlation')
        
        plt.tight_layout()
        return fig
    
    def create_budget_optimization_report(self, optimization_results):
        """Create budget optimization report"""
        
        summary = optimization_results['reallocation_summary']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Budget Optimization Analysis', fontsize=16, fontweight='bold')
        
        # Current vs Optimal Budget
        x = np.arange(len(summary))
        width = 0.35
        
        axes[0,0].bar(x - width/2, summary['current_budget'], width, label='Current', alpha=0.8)
        axes[0,0].bar(x + width/2, summary['optimal_budget'], width, label='Optimal', alpha=0.8)
        axes[0,0].set_xlabel('Channel')
        axes[0,0].set_ylabel('Budget ($)')
        axes[0,0].set_title('Current vs Optimal Budget Allocation')
        axes[0,0].set_xticks(x)
        axes[0,0].set_xticklabels(summary.index, rotation=45)
        axes[0,0].legend()
        
        # Budget change percentage
        colors = ['red' if x < 0 else 'green' for x in summary['change_pct']]
        axes[0,1].bar(range(len(summary)), summary['change_pct'], color=colors, alpha=0.7)
        axes[0,1].set_xlabel('Channel')
        axes[0,1].set_ylabel('Change (%)')
        axes[0,1].set_title('Recommended Budget Change (%)')
        axes[0,1].set_xticks(range(len(summary)))
        axes[0,1].set_xticklabels(summary.index, rotation=45)
        axes[0,1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Efficiency vs Current ROAS
        axes[1,0].scatter(summary['current_roas'], summary['efficiency_score'], 
                         s=summary['current_budget']/100, alpha=0.6)
        axes[1,0].set_xlabel('Current ROAS')
        axes[1,0].set_ylabel('Efficiency Score')
        axes[1,0].set_title('Efficiency Score vs ROAS (bubble size = budget)')
        
        # Recommendation summary
        rec_counts = summary['recommendation'].value_counts()
        axes[1,1].pie(rec_counts.values, labels=rec_counts.index, autopct='%1.1f%%')
        axes[1,1].set_title('Budget Recommendation Summary')
        
        plt.tight_layout()
        return fig

def main():
    """Example usage of analysis utilities"""
    
    # This would be used in the notebooks
    print("Analysis utilities loaded successfully!")
    print("Available classes:")
    print("- ChannelAnalyzer: Advanced channel performance analysis")
    print("- ReportGenerator: Create visualizations and reports")

if __name__ == "__main__":
    main()

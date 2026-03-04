#!/usr/bin/env python3
"""
创建演示 GIF 的脚本
展示数据分析工具的核心功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import seaborn as sns
from datetime import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def create_demo_data():
    """创建演示数据"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, 100).cumsum(),
        'customers': np.random.poisson(50, 100),
        'revenue': np.random.normal(5000, 1000, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })
    return data

def create_animated_demo():
    """创建动画演示"""
    data = create_demo_data()
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Data Analysis Toolkit - Live Demo', fontsize=20, fontweight='bold')
    
    def animate(frame):
        # 清空所有子图
        for ax in axes.flat:
            ax.clear()
        
        # 获取当前帧的数据
        current_data = data.iloc[:frame+10]
        
        # 1. 销售趋势
        axes[0, 0].plot(current_data['date'], current_data['sales'], 
                       color='#2E86AB', linewidth=2)
        axes[0, 0].set_title('📈 Sales Trend Analysis', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('Cumulative Sales')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. 客户分布
        axes[0, 1].hist(current_data['customers'], bins=15, 
                       color='#A23B72', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('👥 Customer Distribution', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Number of Customers')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        # 3. 收入箱线图
        category_data = [current_data[current_data['category'] == cat]['revenue'].values 
                        for cat in ['A', 'B', 'C']]
        bp = axes[1, 0].boxplot(category_data, labels=['Category A', 'Category B', 'Category C'],
                               patch_artist=True)
        for patch, color in zip(bp['boxes'], ['#F18F01', '#C73E1D', '#6A994E']):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        axes[1, 0].set_title('💰 Revenue by Category', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('Revenue')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # 4. 统计摘要
        axes[1, 1].axis('off')
        stats_text = f"""
        📊 Statistics Summary
        
        Total Records: {len(current_data)}
        
        Sales:
        • Mean: ${current_data['sales'].mean():.2f}
        • Std: ${current_data['sales'].std():.2f}
        
        Customers:
        • Mean: {current_data['customers'].mean():.1f}
        • Max: {current_data['customers'].max()}
        
        Revenue:
        • Total: ${current_data['revenue'].sum():.2f}
        • Mean: ${current_data['revenue'].mean():.2f}
        
        Progress: {frame+10}/{len(data)} records
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, 
                       verticalalignment='center', family='monospace',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
    
    # 创建动画
    frames = min(90, len(data) - 10)  # 限制帧数
    anim = FuncAnimation(fig, animate, frames=frames, interval=100, repeat=True)
    
    # 保存为 GIF
    output_path = 'demo_animation.gif'
    print(f"Creating animated demo GIF... (this may take a while)")
    writer = PillowWriter(fps=10)
    anim.save(output_path, writer=writer, dpi=100)
    print(f"✅ Demo GIF created: {output_path}")
    
    plt.close()

def create_static_showcase():
    """创建静态展示图"""
    data = create_demo_data()
    
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 标题
    fig.suptitle('🚀 Data Analysis Toolkit - Feature Showcase', 
                fontsize=24, fontweight='bold', y=0.98)
    
    # 1. 数据清洗
    ax1 = fig.add_subplot(gs[0, 0])
    before_after = pd.DataFrame({
        'Before': [100, 95, 90, 85],
        'After': [100, 100, 100, 100]
    }, index=['Complete', 'Valid', 'Unique', 'Quality'])
    before_after.plot(kind='bar', ax=ax1, color=['#E63946', '#06D6A0'])
    ax1.set_title('🧹 Data Cleaning', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Score (%)')
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2. 统计分析
    ax2 = fig.add_subplot(gs[0, 1])
    stats = data['revenue'].describe()
    ax2.barh(range(len(stats)), stats.values, color='#2E86AB')
    ax2.set_yticks(range(len(stats)))
    ax2.set_yticklabels(stats.index)
    ax2.set_title('📊 Statistical Analysis', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Value')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # 3. 数据可视化
    ax3 = fig.add_subplot(gs[0, 2])
    data.groupby('category')['revenue'].sum().plot(kind='pie', ax=ax3, 
                                                   autopct='%1.1f%%',
                                                   colors=['#F18F01', '#C73E1D', '#6A994E'])
    ax3.set_title('📈 Data Visualization', fontsize=14, fontweight='bold')
    ax3.set_ylabel('')
    
    # 4. 数据比较
    ax4 = fig.add_subplot(gs[1, 0])
    comparison = pd.DataFrame({
        'Dataset A': np.random.normal(100, 15, 50),
        'Dataset B': np.random.normal(110, 20, 50)
    })
    comparison.boxplot(ax=ax4, patch_artist=True)
    ax4.set_title('🔍 Data Comparison', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Value')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. 数据转换
    ax5 = fig.add_subplot(gs[1, 1])
    formats = ['CSV', 'JSON', 'Excel', 'Parquet', 'SQL']
    counts = [100, 95, 90, 85, 80]
    ax5.barh(formats, counts, color=['#06D6A0', '#118AB2', '#073B4C', '#EF476F', '#FFD166'])
    ax5.set_title('🔄 Data Conversion', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Support Level (%)')
    ax5.grid(True, alpha=0.3, axis='x')
    
    # 6. 数据导出
    ax6 = fig.add_subplot(gs[1, 2])
    export_types = ['Full', 'Filtered', 'Aggregated', 'Sampled']
    export_counts = [1000, 750, 500, 250]
    ax6.bar(export_types, export_counts, color='#A23B72')
    ax6.set_title('💾 Data Export', fontsize=14, fontweight='bold')
    ax6.set_ylabel('Records')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(True, alpha=0.3, axis='y')
    
    # 7. 数据合并
    ax7 = fig.add_subplot(gs[2, 0])
    merge_methods = ['Inner', 'Outer', 'Left', 'Right']
    merge_results = [80, 120, 100, 90]
    ax7.bar(merge_methods, merge_results, color=['#E63946', '#F18F01', '#06D6A0', '#118AB2'])
    ax7.set_title('🔗 Data Merging', fontsize=14, fontweight='bold')
    ax7.set_ylabel('Merged Records')
    ax7.grid(True, alpha=0.3, axis='y')
    
    # 8. 质量检查
    ax8 = fig.add_subplot(gs[2, 1])
    quality_metrics = ['Completeness', 'Validity', 'Consistency', 'Accuracy']
    quality_scores = [95, 92, 88, 90]
    colors_quality = ['#06D6A0' if s >= 90 else '#FFD166' if s >= 80 else '#E63946' 
                     for s in quality_scores]
    ax8.barh(quality_metrics, quality_scores, color=colors_quality)
    ax8.set_title('✅ Quality Check', fontsize=14, fontweight='bold')
    ax8.set_xlabel('Score (%)')
    ax8.axvline(x=90, color='red', linestyle='--', alpha=0.5, label='Threshold')
    ax8.legend()
    ax8.grid(True, alpha=0.3, axis='x')
    
    # 9. 数据采样
    ax9 = fig.add_subplot(gs[2, 2])
    sample_methods = ['Random', 'Stratified', 'Systematic', 'Cluster']
    sample_sizes = [100, 120, 110, 90]
    ax9.bar(sample_methods, sample_sizes, color='#6A994E')
    ax9.set_title('🎲 Data Sampling', fontsize=14, fontweight='bold')
    ax9.set_ylabel('Sample Size')
    ax9.tick_params(axis='x', rotation=45)
    ax9.grid(True, alpha=0.3, axis='y')
    
    plt.savefig('demo_showcase.png', dpi=150, bbox_inches='tight')
    print("✅ Static showcase created: demo_showcase.png")
    plt.close()

def create_quick_demo():
    """创建快速演示（用于 README）"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle('Data Analysis Toolkit - Quick Demo', fontsize=18, fontweight='bold')
    
    data = create_demo_data()
    
    # 1. 趋势分析
    axes[0].plot(data['date'], data['sales'], color='#2E86AB', linewidth=2)
    axes[0].fill_between(data['date'], data['sales'], alpha=0.3, color='#2E86AB')
    axes[0].set_title('📈 Trend Analysis', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Date')
    axes[0].set_ylabel('Sales')
    axes[0].grid(True, alpha=0.3)
    axes[0].tick_params(axis='x', rotation=45)
    
    # 2. 分布分析
    axes[1].hist(data['revenue'], bins=20, color='#A23B72', alpha=0.7, edgecolor='black')
    axes[1].set_title('📊 Distribution Analysis', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Revenue')
    axes[1].set_ylabel('Frequency')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # 3. 分类分析
    category_revenue = data.groupby('category')['revenue'].sum()
    axes[2].bar(category_revenue.index, category_revenue.values, 
               color=['#F18F01', '#C73E1D', '#6A994E'])
    axes[2].set_title('💰 Category Analysis', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Category')
    axes[2].set_ylabel('Total Revenue')
    axes[2].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('demo_quick.png', dpi=150, bbox_inches='tight')
    print("✅ Quick demo created: demo_quick.png")
    plt.close()

if __name__ == '__main__':
    print("🎬 Creating demo materials...")
    print()
    
    # 创建快速演示（最快）
    print("1. Creating quick demo...")
    create_quick_demo()
    print()
    
    # 创建静态展示
    print("2. Creating static showcase...")
    create_static_showcase()
    print()
    
    # 创建动画演示（最慢）
    print("3. Creating animated demo...")
    print("   (This will take 1-2 minutes...)")
    create_animated_demo()
    print()
    
    print("✅ All demo materials created successfully!")
    print()
    print("Generated files:")
    print("  • demo_quick.png - Quick demo for README")
    print("  • demo_showcase.png - Full feature showcase")
    print("  • demo_animation.gif - Animated demo")

"""
数据分析工具演示脚本
展示完整的数据分析工作流
"""
import pandas as pd
import numpy as np
from data_analyzer import DataAnalyzer
from data_cleaner import DataCleaner
from data_visualizer import DataVisualizer

def create_sample_data():
    """创建示例数据"""
    print("=" * 60)
    print("步骤 1: 创建示例数据")
    print("=" * 60)
    
    # 创建一个销售数据集
    np.random.seed(42)
    n = 200
    
    data = {
        'Date': pd.date_range('2024-01-01', periods=n),
        'Product': np.random.choice(['A', 'B', 'C', 'D'], n),
        'Sales': np.random.randint(100, 1000, n),
        'Revenue': np.random.uniform(1000, 10000, n),
        'Cost': np.random.uniform(500, 5000, n),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'Customer_Rating': np.random.uniform(1, 5, n)
    }
    
    df = pd.DataFrame(data)
    
    # 添加一些缺失值
    df.loc[np.random.choice(df.index, 10), 'Sales'] = np.nan
    df.loc[np.random.choice(df.index, 5), 'Customer_Rating'] = np.nan
    
    # 添加一些重复行
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)
    
    # 添加一些异常值
    df.loc[np.random.choice(df.index, 3), 'Revenue'] = df['Revenue'].max() * 3
    
    # 保存到文件
    df.to_csv('demo_data.csv', index=False)
    print(f"✓ 创建了 {len(df)} 行示例数据")
    print(f"✓ 保存到: demo_data.csv")
    print()
    
    return df

def demo_analyzer():
    """演示数据分析器"""
    print("=" * 60)
    print("步骤 2: 数据分析")
    print("=" * 60)
    
    analyzer = DataAnalyzer()
    analyzer.load_file('demo_data.csv')
    
    print("\n分析数据...")
    results = analyzer.analyze()
    
    print("\n生成报告...")
    analyzer.print_report()
    
    print("\n导出报告...")
    analyzer.export_report('demo_analysis_report.json')
    analyzer.export_report('demo_analysis_report.txt')
    print()

def demo_cleaner():
    """演示数据清洗器"""
    print("=" * 60)
    print("步骤 3: 数据清洗")
    print("=" * 60)
    
    df = pd.read_csv('demo_data.csv')
    
    print(f"\n原始数据: {len(df)} 行")
    print(f"缺失值: {df.isnull().sum().sum()} 个")
    
    cleaner = DataCleaner(df)
    
    print("\n执行清洗操作...")
    cleaner.handle_missing_values(strategy='fill')
    cleaner.remove_duplicates()
    cleaner.remove_outliers(columns=['Revenue'], method='iqr', threshold=1.5)
    
    clean_df = cleaner.get_cleaned_data()
    
    print(f"\n清洗后数据: {len(clean_df)} 行")
    print(f"缺失值: {clean_df.isnull().sum().sum()} 个")
    
    print("\n清洗日志:")
    for log in cleaner.get_log():
        print(f"  - {log}")
    
    # 保存清洗后的数据
    clean_df.to_csv('demo_data_clean.csv', index=False)
    print(f"\n✓ 清洗后的数据保存到: demo_data_clean.csv")
    print()
    
    return clean_df

def demo_visualizer(df):
    """演示数据可视化器"""
    print("=" * 60)
    print("步骤 4: 数据可视化")
    print("=" * 60)
    
    viz = DataVisualizer(df)
    
    print("\n生成图表...")
    viz.plot_distribution(columns=['Sales', 'Revenue', 'Cost'])
    viz.plot_correlation()
    viz.plot_boxplot(columns=['Sales', 'Revenue', 'Cost'])
    viz.plot_categorical('Product')
    viz.plot_categorical('Region')
    
    print(f"\n✓ 共生成 {len(viz.figures)} 个图表")
    
    print("\n保存图表...")
    viz.save_all('demo_plots')
    print()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("数据分析工具演示")
    print("=" * 60)
    print()
    
    # 1. 创建示例数据
    df = create_sample_data()
    
    # 2. 数据分析
    demo_analyzer()
    
    # 3. 数据清洗
    clean_df = demo_cleaner()
    
    # 4. 数据可视化
    demo_visualizer(clean_df)
    
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print("  - demo_data.csv (原始数据)")
    print("  - demo_data_clean.csv (清洗后数据)")
    print("  - demo_analysis_report.json (JSON报告)")
    print("  - demo_analysis_report.txt (文本报告)")
    print("  - demo_plots/ (图表目录)")
    print()

if __name__ == "__main__":
    main()

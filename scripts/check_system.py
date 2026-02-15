"""
系统环境检查脚本
检查依赖是否正确安装
"""
import sys
import os

def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("    需要 Python 3.8 或更高版本")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    
    dependencies = {
        'tkinter': 'Tkinter (GUI)',
        'ttkbootstrap': 'ttkbootstrap (主题)',
        'matplotlib': 'matplotlib (图表)',
        'pandas': 'pandas (数据处理)',
        'sklearn': 'scikit-learn (机器学习)',
        'jieba': 'jieba (中文分词)',
        'numpy': 'numpy (数值计算)',
        'openpyxl': 'openpyxl (Excel)',
        'fpdf': 'fpdf (PDF)'
    }
    
    results = {}
    for module, name in dependencies.items():
        try:
            if module == 'tkinter':
                import tkinter
            else:
                __import__(module)
            print(f"  ✓ {name}")
            results[module] = True
        except ImportError:
            print(f"  ✗ {name} - 未安装")
            results[module] = False
    
    return results

def check_directories():
    """检查必要的目录"""
    print("\n检查目录结构...")
    
    directories = ['data', 'logs', 'modules', 'ui', 'tests', 'docs']
    all_exist = True
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"  ✓ {directory}/")
        else:
            print(f"  ✗ {directory}/ - 不存在")
            all_exist = False
    
    return all_exist

def check_files():
    """检查必要的文件"""
    print("\n检查关键文件...")
    
    files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'start.sql',
        'README.md'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - 不存在")
            all_exist = False
    
    return all_exist

def check_database():
    """检查数据库"""
    print("\n检查数据库...")
    
    db_path = 'data/teaching_assistant.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"  ✓ 数据库存在 ({size} bytes)")
        return True
    else:
        print(f"  - 数据库不存在（首次运行时会自动创建）")
        return True

def print_summary(results):
    """打印总结"""
    print("\n" + "=" * 50)
    print("检查完成！")
    print("=" * 50)
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n✓ 所有检查通过，系统可以正常运行！")
        print("\n运行命令:")
        print("  python main.py")
    else:
        print("\n⚠ 发现一些问题，请先解决：")
        
        if not results.get('python_version', True):
            print("\n1. 升级 Python 到 3.8 或更高版本")
        
        missing_deps = [k for k, v in results.items() if k.startswith('dep_') and not v]
        if missing_deps:
            print("\n2. 安装缺失的依赖包:")
            print("   pip install -r requirements.txt")
        
        if not results.get('directories', True) or not results.get('files', True):
            print("\n3. 确保项目文件完整")

def main():
    """主函数"""
    print("=" * 50)
    print("AI 智能教学助手系统 - 环境检查")
    print("=" * 50)
    print()
    
    results = {}
    
    # 检查 Python 版本
    results['python_version'] = check_python_version()
    
    # 检查依赖
    dep_results = check_dependencies()
    for k, v in dep_results.items():
        results[f'dep_{k}'] = v
    
    # 检查目录
    results['directories'] = check_directories()
    
    # 检查文件
    results['files'] = check_files()
    
    # 检查数据库
    results['database'] = check_database()
    
    # 打印总结
    print_summary(results)

if __name__ == "__main__":
    main()

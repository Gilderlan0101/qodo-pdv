from setuptools import setup
import os

# Ler dependências do requirements.txt
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

# Ler README
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return 'Qodo PDV - Sistema completo de Ponto de Venda'

setup(
    name='qodo',
    version='0.1.0',
    description='Sistema completo de PDV (Ponto de Venda) com múltiplos recursos e integrações',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Qodo Tech',
    author_email='dacruzgg01@gmail.com',
    url='https://github.com/Gilderlan0101/qodo-pdv',
    
    # ✅ Use find_packages para automatizar
    packages=['qodo'] + [
        f'qodo.{subpkg}' for subpkg in [
            'auth', 'conf', 'core', 'logs', 'model', 'routes', 
            'schemas', 'services', 'utils', 'controllers'
        ]
    ],
    package_dir={'': 'src'},
    
    # ✅ Incluir dados do pacote
    include_package_data=True,
    package_data={
        'qodo': ['*.md', 'static/logo/*.png'],
    },
    
    # ✅ Dependências otimizadas
    install_requires=read_requirements(),
    
    # ✅ Classifiers atualizados (sem warnings)
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    
    keywords='pdv ponto-de-venda venda checkout fastapi sqlite mysql',
    python_requires='>=3.8',
    
    entry_points={
        'console_scripts': [
            'qodo-pdv=qodo.main:main',
            'qodo-server=qodo.main:main',
        ],
    },
    
    project_urls={
        'Documentation': 'https://github.com/Gilderlan0101/qodo-pdv',
        'Source': 'https://github.com/Gilderlan0101/qodo-pdv',
        'Tracker': 'https://github.com/Gilderlan0101/qodo-pdv/issues',
    },
)
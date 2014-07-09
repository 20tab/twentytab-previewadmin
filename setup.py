from setuptools import setup, find_packages
import previewadmin

setup(name='twentytab-previewadmin',
      version=previewadmin.__version__,
      description='A django app that initializes admin changelist view with a useful tool to have a preview of instances',
      author='20tab S.r.l.',
      author_email='info@20tab.com',
      url='https://github.com/20tab/twentytab-previewadmin',
      license='MIT License',
      install_requires=[
          'Django >=1.6',
      ],
      packages=find_packages(),
      include_package_data=True,
      package_data={
          '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
      }
)

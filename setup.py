from setuptools import find_packages,setup
from typing import List

HYPEN_E_DOT='-e .'
def get_requirements(file_path:str)->List[str]:
    '''
    this function will return the list of requirements in present in requirements.txt file
    '''
    requirements=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    
    return requirements

setup(
name='Build_autonomouAI_agent_to_analyze_GitHub_pull-_requests_and_reviews_the_code',
version='0.0.1',
author='Prathamesh',
author_email='prathameshpawar1702@gmail.com',
packages=find_packages(),
install_requires=get_requirements('requirements.txt')

)
#!/usr/bin/env python3

from ansiblemddoc.Config import SingleConfig
import sys
import yaml
import os
from os import walk
from ansiblemddoc.Utils import SingleLog,FileUtils
from mdutils.mdutils import MdUtils

class IndexWriter:


    def __init__(self):
        self.config = SingleConfig()
        self.log = SingleLog()


    def render(self):
        self.createIndexMDFile()


    def createIndexMDFile(self):

        self.log.info("(createIndexMDFile) Create Index MD File")
        role_name = self.config.get_base_dir()[self.config.get_base_dir().rfind('/')+1:]
        page_title = "Role: "+role_name

        mdFile = MdUtils(file_name=self.config.get_output_dir()+"/index.md")

        self.createMDFileContent(mdFile)

        mdFile.create_md_file()
        self.log.info("(createIndexMDFile) Create Index MD File Complete")
    
    def createMDFileContent(self, mdFile):
        author = ''
        description = ''
        company = ''
        license = ''
        min_ansible_version = ''
        dependencies = []

        galaxy_metafile = self.config.get_base_dir()+'/meta/main'+self.config.yaml_extension

        if os.path.isfile(galaxy_metafile):
            with open(galaxy_metafile, 'r') as stream:
                try:
                    metadata = yaml.safe_load(stream)
                    author = metadata.get("galaxy_info").get('author')
                    description = metadata.get("galaxy_info").get('description')
                    company = metadata.get("galaxy_info").get('company')
                    license = metadata.get("galaxy_info").get('license')
                    min_ansible_version = metadata.get("galaxy_info").get('min_ansible_version')
                    dependencies = metadata.get('dependencies')

                except yaml.YAMLError as exc:
                    print(exc)
        else:
            self.log.info(
                f"(createIndexMDFile) No meta/main{self.config.yaml_extension} file")
        
        role_name = self.config.get_base_dir()[self.config.get_base_dir().rfind('/')+1:]
        mdFile.new_header(level=1, title='Home')

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Role Name') 
        mdFile.new_line(role_name) 
        mdFile.new_line()

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Description') 
        mdFile.new_line(description)
        mdFile.new_line()

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Dependencies') 

        if dependencies != []:
            for dependency in dependencies:
                if isinstance(dependency, dict):
                    for dep_part in dependency:
                        mdFile.new_line("> "+dep_part+": "+dependency[dep_part])
                else:
                    mdFile.new_line("> "+ dependency)

                mdFile.new_line()
        else:
            mdFile.new_line('None')
        mdFile.new_line()


        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Requirements')
        mdFile.new_header(level=3, title='Role')
        requirements = self.createMDFileRoleRequirements()
        if requirements != []:
            for requirement in requirements:
                mdFile.new_line("> "+ requirement)
                mdFile.new_line()
        else:
            mdFile.new_line('None')
        mdFile.new_line()

        mdFile.new_header(level=3, title='Collection')
        requirements = self.createMDFileCollectionRequirements()
        if requirements != []:
            for requirement in requirements:
                mdFile.new_line("> "+ requirement)
                mdFile.new_line()
        else:
            mdFile.new_line('None')
        mdFile.new_line()




        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Information') 

        table_entries = ["Author", "Company", "License","Minimum Ansible Version"]
        table_entries.extend([author, company, license, str(min_ansible_version)])
        mdFile.new_line()

        mdFile.new_table(columns=4, rows=2, text=table_entries, text_align='center')



    def createMDFileRoleRequirements(self):
        requirements = []
        roles_file = self.config.get_base_dir()+'/roles/requirements.yml'

        if os.path.isfile(roles_file):
            with open(roles_file, 'r') as stream:
                try:
                    roles = yaml.safe_load(stream)
                    for role in roles:
                        requirements.append(role.get('name') + ' (' + role.get('src') + ')')
                except yaml.YAMLError as exc:
                    print(exc)
        return requirements


    def createMDFileCollectionRequirements(self):
        requirements = []
        collections_file = self.config.get_base_dir()+'/collections/requirements.yml'

        if os.path.isfile(collections_file):
            with open(collections_file, 'r') as stream:
                try:
                    collections = yaml.safe_load(stream).get('collections')
                    for collection in collections:
                        requirements.append(collection.get('name'))
                except yaml.YAMLError as exc:
                    print(exc)
        return requirements


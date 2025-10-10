#!/usr/bin/env python3

from ansiblemddoc.Config import SingleConfig
import sys
import yaml
import os
import shutil
from os import walk
from ansiblemddoc.Utils import SingleLog,FileUtils
from mdutils.mdutils import MdUtils
from ansiblemddoc.AutoDocumenterIndex import IndexWriter
from ansiblemddoc.AutoDocumenterTasks import TasksWriter
from ansiblemddoc.AutoDocumenterVariables import VariablesWriter
from ansiblemddoc.AutoDocumenterFilesTemplates import FilesTemplatesWriter
from ansiblemddoc.AutoDocumenterAppendix import AppendixWriter

from ansiblemddoc.AutoDocumenterBase import WriterBase

class RolesWriter(WriterBase):
    """
    Writer class to handle documentation generation for projects with roles directory
    """

    def render(self):
        """
        Main render method that processes all roles in the roles directory
        """
        if not hasattr(self.config, 'has_roles_directory') or not self.config.has_roles_directory:
            self.log.info("No roles directory found, skipping roles documentation")
            return

        roles = self.config.get_roles_list()
        if not roles:
            self.log.info("No roles found in roles directory")
            return

        self.log.info(f"Found {len(roles)} roles to document: {', '.join(roles)}")

        # Create main roles documentation directory
        roles_output_dir = os.path.join(self.config.get_output_dir(), "roles")
        self.makeDocsDir(roles_output_dir)

        # Create index for all roles
        self.create_roles_index(roles, roles_output_dir)

        # Process each role
        for role_name in roles:
            self.log.info(f"Processing role: {role_name}")
            self.process_role(role_name, roles_output_dir)

    def create_roles_index(self, roles, output_dir):
        """
        Create an index page listing all roles
        """
        self.log.info("Creating roles index")

        mdFile = MdUtils(file_name=os.path.join(output_dir, "index"))
        mdFile.new_header(level=1, title="Roles Documentation")
        mdFile.new_line()

        mdFile.new_line("This project contains the following roles:")
        mdFile.new_line()

        for role in roles:
            role_link = f"[{role}](./{role}/index.md)"
            mdFile.new_line(f"- {role_link}")

        mdFile.new_line()
        mdFile.create_md_file()

    def process_role(self, role_name, roles_output_dir):
        """
        Process a single role and generate its documentation
        """
        role_path = os.path.join(self.config.get_base_dir(), "roles", role_name)
        role_output_dir = os.path.join(roles_output_dir, role_name)

        self.makeDocsDir(role_output_dir)

        # Temporarily change config to point to the role directory
        original_base_dir = self.config.get_base_dir()
        original_output_dir = self.config.output_dir
        original_playbook_main = getattr(self.config, 'playbook_main', None)

        self.config.set_base_dir(role_path)
        self.config.output_dir = role_output_dir
        # Clear playbook_main for roles - they shouldn't use main playbook files
        self.config.playbook_main = None
        self.config._set_is_role()

        try:
            # Generate role documentation using existing writers
            self.log.info(f"Generating index for role {role_name}")
            indexWriter = RoleIndexWriter(role_name)
            indexWriter.render()

            self.log.info(f"Generating tasks documentation for role {role_name}")
            tasksWriter = TasksWriter()
            tasksWriter.render()

            self.log.info(f"Generating variables documentation for role {role_name}")
            variablesWriter = VariablesWriter()
            variablesWriter.render()

            if self.config.output_files is True or self.config.output_templates is True:
                self.log.info(f"Generating files/templates documentation for role {role_name}")
                filesTemplatesWriter = FilesTemplatesWriter()
                filesTemplatesWriter.render()

            if self.config.appendix is not None:
                self.log.info(f"Generating appendix for role {role_name}")
                appendixWriter = AppendixWriter()
                appendixWriter.render()

        except Exception as e:
            self.log.error(f"Error processing role {role_name}: {str(e)}")

        finally:
            # Restore original config
            self.config.set_base_dir(original_base_dir)
            self.config.output_dir = original_output_dir
            self.config.playbook_main = original_playbook_main
            self.config._set_is_role()


class RoleIndexWriter(IndexWriter):
    """
    Specialized index writer for individual roles
    """

    def __init__(self, role_name):
        super().__init__()
        self.role_name = role_name

    def createIndexMDFile(self):
        self.log.info(f"Creating index MD file for role {self.role_name}")

        mdFile = MdUtils(file_name=os.path.join(self.config.get_output_dir(), "index"))

        self.createMDFileContent(mdFile)

        mdFile.create_md_file()
        self.log.info(f"Index MD file created for role {self.role_name}")

    def createMDFileContent(self, mdFile):
        """
        Create the content for the role index file
        """
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
                    if metadata and 'galaxy_info' in metadata:
                        galaxy_info = metadata.get("galaxy_info")
                        author = galaxy_info.get('author', '')
                        description = galaxy_info.get('description', '')
                        company = galaxy_info.get('company', '')
                        license = galaxy_info.get('license', '')
                        min_ansible_version = galaxy_info.get('min_ansible_version', '')
                    if metadata and 'dependencies' in metadata:
                        dependencies = metadata.get('dependencies', [])

                except yaml.YAMLError as exc:
                    self.log.error(f"Error reading meta file: {exc}")
        else:
            self.log.info(f"No meta/main{self.config.yaml_extension} file found for role {self.role_name}")

        mdFile.new_header(level=1, title=f'Role: {self.role_name}')
        mdFile.new_line()

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Description')
        mdFile.new_line(str(description) if description else f"Documentation for {self.role_name} role")
        mdFile.new_line()

        if author:
            mdFile.new_line("---")
            mdFile.new_header(level=2, title='Author')
            mdFile.new_line(str(author))
            mdFile.new_line()

        if company:
            mdFile.new_line("---")
            mdFile.new_header(level=2, title='Company')
            mdFile.new_line(str(company))
            mdFile.new_line()

        if license:
            mdFile.new_line("---")
            mdFile.new_header(level=2, title='License')
            mdFile.new_line(str(license))
            mdFile.new_line()

        if min_ansible_version:
            mdFile.new_line("---")
            mdFile.new_header(level=2, title='Minimum Ansible Version')
            mdFile.new_line(str(min_ansible_version))
            mdFile.new_line()

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Dependencies')

        if dependencies and len(dependencies) > 0:
            for dependency in dependencies:
                if isinstance(dependency, str):
                    mdFile.new_line(f"- {dependency}")
                elif isinstance(dependency, dict):
                    role_name = str(dependency.get('role', 'Unknown'))
                    mdFile.new_line(f"- {role_name}")
        else:
            mdFile.new_line("No dependencies")

        mdFile.new_line()
        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Documentation Sections')
        mdFile.new_line("- [Tasks](./tasks/)")
        mdFile.new_line("- [Variables](./variables/)")
        if self.config.output_files:
            mdFile.new_line("- [Files](./files/)")
        if self.config.output_templates:
            mdFile.new_line("- [Templates](./roletemplates/)")
        mdFile.new_line()


class ProjectIndexWriter(IndexWriter):
    """
    Index writer for projects with roles directory
    """

    def createIndexMDFile(self):
        self.log.info("Creating project index MD file")

        mdFile = MdUtils(file_name=os.path.join(self.config.get_output_dir(), "index"))

        self.createMDFileContent(mdFile)

        mdFile.create_md_file()
        self.log.info("Project index MD file created")

    def createMDFileContent(self, mdFile):
        """
        Create the content for the project index file
        """
        project_name = os.path.basename(self.config.get_base_dir())

        mdFile.new_header(level=1, title=f'Project: {project_name}')
        mdFile.new_line()

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Description')
        mdFile.new_line(f"Documentation for Ansible project {project_name}")
        mdFile.new_line()

        # Check for playbook files
        playbook_files = []
        for file in os.listdir(self.config.get_base_dir()):
            if file.endswith(('.yml', '.yaml')) and ('playbook' in file.lower() or file == 'site.yml' or file == 'main.yml'):
                playbook_files.append(file)

        if playbook_files:
            mdFile.new_line("---")
            mdFile.new_header(level=2, title='Playbooks')
            for playbook in playbook_files:
                mdFile.new_line(f"- {playbook}")
            mdFile.new_line()

        # List roles
        roles = self.config.get_roles_list()
        if roles:
            mdFile.new_line("---")
            mdFile.new_header(level=2, title='Roles')
            mdFile.new_line("This project includes the following roles:")
            mdFile.new_line()
            for role in roles:
                role_link = f"[{role}](./roles/{role}/index.md)"
                mdFile.new_line(f"- {role_link}")
            mdFile.new_line()

        # Add Requirements section
        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Requirements')

        mdFile.new_header(level=3, title='Collections')
        collections_requirements = self.createMDFileCollectionRequirements()
        if collections_requirements:
            for requirement in collections_requirements:
                mdFile.new_line(f"- {requirement}")
        else:
            mdFile.new_line("None")
        mdFile.new_line()

        mdFile.new_header(level=3, title='External Roles')
        roles_requirements = self.createMDFileRoleRequirements()
        if roles_requirements:
            for requirement in roles_requirements:
                mdFile.new_line(f"- {requirement}")
        else:
            mdFile.new_line("None")
        mdFile.new_line()

        mdFile.new_line("---")
        mdFile.new_header(level=2, title='Documentation Sections')
        if roles:
            mdFile.new_line("- [Roles Documentation](./roles/)")

        # Only include project-level sections if they exist
        project_has_tasks = os.path.exists(os.path.join(self.config.get_output_dir(), "tasks"))
        project_has_variables = os.path.exists(os.path.join(self.config.get_output_dir(), "variables"))
        project_has_files = os.path.exists(os.path.join(self.config.get_output_dir(), "files"))
        project_has_templates = os.path.exists(os.path.join(self.config.get_output_dir(), "roletemplates"))

        if project_has_tasks:
            mdFile.new_line("- [Tasks](./tasks/)")
        if project_has_variables:
            mdFile.new_line("- [Variables](./variables/)")
        if project_has_files and self.config.output_files:
            mdFile.new_line("- [Files](./files/)")
        if project_has_templates and self.config.output_templates:
            mdFile.new_line("- [Templates](./roletemplates/)")
        mdFile.new_line()

    def createMDFileCollectionRequirements(self):
        """
        Parse collections/requirements.yml and return list of collections
        """
        requirements = []
        collections_file = self.config.get_base_dir() + '/collections/requirements.yml'

        if os.path.isfile(collections_file):
            with open(collections_file, 'r') as stream:
                try:
                    data = yaml.safe_load(stream)
                    if data and 'collections' in data:
                        collections = data.get('collections')
                        for collection in collections:
                            if isinstance(collection, str):
                                requirements.append(collection)
                            elif isinstance(collection, dict) and 'name' in collection:
                                requirements.append(collection.get('name'))
                except yaml.YAMLError as exc:
                    self.log.error(f"Error reading collections file: {exc}")
        return requirements

    def createMDFileRoleRequirements(self):
        """
        Parse roles/requirements.yml and return list of external roles
        """
        requirements = []
        roles_file = self.config.get_base_dir() + '/roles/requirements.yml'

        if os.path.isfile(roles_file):
            with open(roles_file, 'r') as stream:
                try:
                    roles = yaml.safe_load(stream)
                    if roles:
                        for role in roles:
                            if isinstance(role, str):
                                requirements.append(role)
                            elif isinstance(role, dict):
                                name = role.get('name', 'Unknown')
                                src = role.get('src', '')
                                if src:
                                    requirements.append(f"{name} ({src})")
                                else:
                                    requirements.append(name)
                except yaml.YAMLError as exc:
                    self.log.error(f"Error reading roles requirements file: {exc}")
        return requirements
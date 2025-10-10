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
from ansiblemddoc.AutoDocumenterRoles import RolesWriter, ProjectIndexWriter

from ansiblemddoc.AutoDocumenterBase import WriterBase

class Writer(WriterBase):

    def render(self):

        if os.path.exists(self.config.get_output_dir()) and len(os.listdir(self.config.get_output_dir())) > 0 and self.config.clear_output is False:
            SingleLog.print("There are existing files in the output directory ",self.config.get_output_dir())
            clear_results = FileUtils.query_yes_no("Do you want to clear the directory and rebuild all the docs?")
            if clear_results == "yes":
                shutil.rmtree(self.config.get_output_dir())

        if os.path.exists(self.config.get_output_dir()) and self.config.output_overwrite is False:
            SingleLog.print("The files in the output directory will be overwritten: ",self.config.get_output_dir())
            overwrite_results = FileUtils.query_yes_no("Do you want to continue?")
            if overwrite_results != "yes":
                sys.exit()

        self.makeDocsDir(self.config.get_output_dir())

        # Check if we have roles directory and handle accordingly
        if hasattr(self.config, 'has_roles_directory') and self.config.has_roles_directory:
            SingleLog.print("Detected project with roles directory, generating documentation for all roles", "")

            # Generate main project documentation
            indexWriter = ProjectIndexWriter()
            indexWriter.render()

            # Generate documentation for all roles in roles directory
            rolesWriter = RolesWriter()
            rolesWriter.render()

            # Generate playbook-level documentation
            # Process playbook documentation if main-file is specified or meaningful tasks exist
            if hasattr(self.config, 'playbook_main') and self.config.playbook_main is not None:
                SingleLog.print("Generating playbook documentation for main file", self.config.playbook_main)
                playbookTasksWriter = PlaybookTasksWriter()
                playbookTasksWriter.render()
            elif self.has_meaningful_project_tasks():
                SingleLog.print("Generating project tasks documentation", "")
                tasksWriter = TasksWriter()
                tasksWriter.render()
            else:
                SingleLog.print("Skipping project tasks documentation - no meaningful tasks found", "")

            variablesWriter = VariablesWriter()
            variablesWriter.render()

        else:
            # Original behavior for single role projects
            indexWriter = IndexWriter()
            indexWriter.render()

            tasksWriter = TasksWriter()
            tasksWriter.render()

            variablesWriter = VariablesWriter()
            variablesWriter.render()

        if self.config.output_files is True or self.config.output_templates is True:
            filesTemplatesWriter = FilesTemplatesWriter()
            filesTemplatesWriter.render()

        if self.config.appendix is not None:
            appendixWriter = AppendixWriter()
            appendixWriter.render()

    def has_meaningful_project_tasks(self):
        """
        Check if the project has meaningful tasks (not just empty/comment files)
        Used for multi-role projects to avoid documenting empty task structures
        """
        tasks_dir = os.path.join(self.config.get_base_dir(), "tasks")

        if not os.path.exists(tasks_dir):
            return False

        for filename in os.listdir(tasks_dir):
            if filename.endswith(('.yml', '.yaml')):
                filepath = os.path.join(tasks_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read().strip()

                        # Skip completely empty files
                        if not content:
                            continue

                        # Skip files with only comments
                        non_comment_lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
                        if not non_comment_lines:
                            continue

                        # Try to parse YAML to see if it has actual tasks
                        try:
                            data = yaml.safe_load(content)
                            if data and isinstance(data, list) and len(data) > 0:
                                # Check if any item has meaningful content
                                for item in data:
                                    if isinstance(item, dict) and len(item) > 0:
                                        # Has at least one meaningful dictionary entry
                                        return True
                            elif data and isinstance(data, dict) and len(data) > 0:
                                # Single task as dict
                                return True
                        except yaml.YAMLError:
                            # If YAML parsing fails but content exists, assume it's meaningful
                            return True
                except Exception:
                    pass

        return False


class PlaybookTasksWriter(WriterBase):
    """
    Special writer for playbook-level documentation when --main-file is specified
    Focuses on documenting playbook structure (roles, tasks) rather than detailed task files
    """

    def render(self):
        """
        Generate playbook-level documentation
        """
        # Create tasks output directory
        self.makeDocsDir(self.config.get_output_tasks_dir())

        # Generate playbook flow and main documentation
        self.createPlaybookMDFile()

    def createPlaybookMDFile(self):
        """
        Create documentation for the main playbook file
        """
        playbook_file = self.config.playbook_main
        output_file = os.path.join(self.config.get_output_tasks_dir(), "playbook")

        mdFile = MdUtils(file_name=output_file)
        mdFile.new_header(level=1, title=f'Playbook: {playbook_file}')
        mdFile.new_line()

        try:
            playbook_path = os.path.join(self.config.get_base_dir(), playbook_file)
            with open(playbook_path, 'r') as f:
                playbook_data = yaml.safe_load(f)

            if playbook_data and isinstance(playbook_data, list):
                for play_idx, play in enumerate(playbook_data):
                    if isinstance(play, dict):
                        play_name = play.get('name', f'Play {play_idx + 1}')
                        mdFile.new_header(level=2, title=play_name)

                        # Document play attributes
                        if 'hosts' in play:
                            mdFile.new_line(f"**Hosts:** {play['hosts']}")
                        if 'become' in play:
                            mdFile.new_line(f"**Become:** {play['become']}")
                        if 'gather_facts' in play:
                            mdFile.new_line(f"**Gather Facts:** {play['gather_facts']}")

                        # Document variables
                        if 'vars' in play:
                            mdFile.new_line("**Variables:**")
                            for var_name, var_value in play['vars'].items():
                                mdFile.new_line(f"- `{var_name}`: {var_value}")

                        # Document roles
                        if 'roles' in play:
                            mdFile.new_line("**Roles:**")
                            for role in play['roles']:
                                if isinstance(role, str):
                                    role_link = f"[{role}](../roles/{role}/index.md)"
                                    mdFile.new_line(f"- {role_link}")
                                elif isinstance(role, dict):
                                    role_name = role.get('role', 'Unknown')
                                    role_link = f"[{role_name}](../roles/{role_name}/index.md)"
                                    mdFile.new_line(f"- {role_link}")

                        # Document tasks if present
                        if 'tasks' in play and play['tasks']:
                            mdFile.new_line("**Tasks:**")
                            for task in play['tasks']:
                                if isinstance(task, dict) and 'name' in task:
                                    mdFile.new_line(f"- {task['name']}")

                        mdFile.new_line()

        except Exception as e:
            self.log.error(f"Error reading playbook file {playbook_file}: {str(e)}")
            mdFile.new_line(f"Error reading playbook file: {str(e)}")

        mdFile.create_md_file()

        # Generate a simple flow diagram for playbook
        self.createPlaybookFlowFile()

    def createPlaybookFlowFile(self):
        """
        Create a flow diagram showing playbook -> roles relationship
        """
        flow_file = os.path.join(self.config.get_output_tasks_dir(), "flow")
        mdFile = MdUtils(file_name=flow_file)
        mdFile.new_header(level=1, title='Playbook Flow')

        try:
            playbook_path = os.path.join(self.config.get_base_dir(), self.config.playbook_main)
            with open(playbook_path, 'r') as f:
                playbook_data = yaml.safe_load(f)

            mdFile.new_line("```mermaid")
            mdFile.new_line("graph LR")

            if playbook_data and isinstance(playbook_data, list):
                playbook_name = self.config.playbook_main.replace('.', '_').replace('/', '_')
                roles_found = set()  # Keep track of roles to avoid duplicates

                # Collect all roles from all plays
                for play in playbook_data:
                    if isinstance(play, dict) and 'roles' in play:
                        for role in play['roles']:
                            if isinstance(role, str):
                                roles_found.add(role)
                            elif isinstance(role, dict) and 'role' in role:
                                roles_found.add(role.get('role'))

                # Create direct connections: playbook -> roles
                for role_name in sorted(roles_found):
                    mdFile.new_line(f"{playbook_name}({self.config.playbook_main}) --> {role_name}({role_name})")

                # If no roles found, show at least the playbook
                if not roles_found:
                    mdFile.new_line(f"{playbook_name}({self.config.playbook_main})")

            mdFile.new_line("```")

        except Exception as e:
            self.log.error(f"Error creating playbook flow: {str(e)}")
            mdFile.new_line("```mermaid")
            mdFile.new_line("graph LR")
            mdFile.new_line(f"Error[Error reading {self.config.playbook_main}]")
            mdFile.new_line("```")

        mdFile.create_md_file()
#!/usr/bin/env python3

from ansiblemddoc.Config import SingleConfig
import sys
import yaml
import os
from os import walk
from ansiblemddoc.Utils import SingleLog,FileUtils
from mdutils.mdutils import MdUtils

from ansiblemddoc.AutoDocumenterBase import WriterBase

class TasksWriter(WriterBase):

    tasks_dir = None
    handlers_dir = None
    flow = {}

    def render(self):

        self.tasks_dir = self.config.get_base_dir()+"/tasks"
        self.log.info("Tasks directory: "+self.tasks_dir)

        self.handlers_dir = self.config.get_base_dir()+"/handlers"
        self.log.info("Tasks directory: "+self.handlers_dir)

        self.makeDocsDir(self.config.get_output_tasks_dir())

        self.createMDFlowFile(self.tasks_dir, self.config.get_output_tasks_dir())

        if hasattr(self.config, 'playbook_main'):
           if self.config.playbook_main is not None:
              self.log.debug("(func getFlowData) render file using:"+self.config.playbook_main)
              self.createMDFile(self.config.get_base_dir(), self.config.playbook_main,self.config.get_output_dir())

        if (self.config.tasks != None and self.config.tasks['combinations'] != None):
            self.iterateOnCombinations(self.tasks_dir, self.config.tasks['combinations'], self.config.get_output_tasks_dir())
        else:
            self.iterateOnFilesAndDirectories(self.tasks_dir, self.config.get_output_tasks_dir())

        self.makeDocsDir(self.config.get_output_handlers_dir())

        if (self.config.handlers != None and self.config.handlers['combinations'] != None):
            self.iterateOnCombinations(self.handlers_dir, self.config.handlers['combinations'], self.config.get_output_handlers_dir())
        else:
            self.iterateOnFilesAndDirectories(self.handlers_dir,self.config.get_output_handlers_dir())


    def createMDFile(self, dirpath, filename, output_directory):
        self.log.info("(createMDFile) Create MD File")
        self.log.debug("(createMDFile) dirpath: "+dirpath)
        self.log.debug("(createMDFile) filename: "+filename)
        self.log.debug("(createMDFile) output_directory: "+output_directory)

        if output_directory.find(self.config.get_output_tasks_dir()) != -1:
            docspath = dirpath.replace(self.tasks_dir,self.config.get_output_tasks_dir())
        else:
            docspath = dirpath.replace(self.handlers_dir,self.config.get_output_handlers_dir())
        if docspath == self.config.get_base_dir():
            docspath =  self.config.get_output_dir()

        self.log.debug("(createMDFile) docspath: "+docspath)

        if not os.path.exists(docspath):
            os.makedirs(docspath)

        mdFile = MdUtils(file_name=docspath+"/"+filename.replace(self.config.yaml_extension,''))
        mdFile.new_header(level=1, title=filename)
        self.addTasks(dirpath+"/"+filename, mdFile)

        mdFile.create_md_file()
        self.log.info("(createMDFile) Create MD File Complete")

    def addTasks(self, filename, mdFile):
        self.log.debug("(addTasks) Filename: " + filename)

        def process_tasks(tasks, indent=0):
            """
            Processa e scrive i task trovati, includendo sia task normali che quelli all'interno di blocchi.
            """
            if tasks is not None:
                for task in tasks:
                    try:
                        # Gestire i blocchi
                        if 'block' in task.keys():
                            if 'name' in task.keys():
                                mdFile.new_paragraph(' ' * indent + '* Block: ' + str(task["name"]))
                            else:
                                mdFile.new_paragraph(' ' * indent + '* Block: (Unnamed block)')
                            process_tasks(task["block"], indent + 4)

                        # Gestire un task normale (fuori dai blocchi)
                        elif 'name' in task.keys():
                            mdFile.new_paragraph(' ' * indent + '* ' + str(task["name"]))

                        # Fallback: gestione di task senza nome
                        else:
                            mdFile.new_paragraph(' ' * indent + '* Task without description:')
                            mdFile.new_line("```")
                            mdFile.new_paragraph(
                                yaml.safe_dump(task, default_flow_style=False, allow_unicode=True)
                            )
                            mdFile.new_line("```")

                        # Scrivere i tag, se esistenti
                        if 'tags' in task.keys():
                            mdFile.write('  \n')
                            mdFile.write('Tags: ', color='green')
                            if isinstance(task["tags"], list):
                                mdFile.write(",".join(task["tags"]))
                            else:
                                mdFile.write(task["tags"])

                    except Exception as e:
                        self.log.error(f"Errore durante la gestione del task: {e}")
                        print(f"Errore durante il task: {e}")

        # Carica il file YAML e processa il contenuto
        with open(filename, 'r') as stream:
            try:
                playbook = yaml.safe_load(stream)
                if playbook is not None:
                    for element in playbook:
                        if 'tasks' in element.keys():
                            self.log.debug("(addTasks) found tasks")
                            mdFile.new_paragraph('* Tasks:')
                            process_tasks(element['tasks'], indent=4)

                        elif 'block' in element.keys():
                            self.log.debug("(addTasks) found top-level block")
                            process_tasks([element], indent=0)

                        elif isinstance(element, dict) and 'name' in element.keys():
                            self.log.debug("(addTasks) found top-level task")
                            process_tasks([element], indent=0)

            except yaml.YAMLError as exc:
                self.log.error(f"Errore YAML: {exc}")
                print(exc)


    def createMDCombinationFile(self, comboFilename, directory, output_directory, filenamesToCombine):

        self.log.info("(createMDCombinationFile) Create MD Combination File")
        self.log.debug("(createMDCombinationFile) comboFilename: "+comboFilename)
        self.log.debug("(createMDCombinationFile) directory: "+directory)
        self.log.debug("(createMDCombinationFile) output_directory: "+output_directory)

        comboFilenameAbs = output_directory+"/"+comboFilename
        comboFileDirectory = comboFilenameAbs[0:int(comboFilenameAbs.rfind('/'))]

        if not os.path.exists(comboFileDirectory):
            os.makedirs(comboFileDirectory)

        mdFile = MdUtils(file_name=comboFilenameAbs)

        mdFile.new_header(level=1, title='Tasks: '+comboFilename[comboFilename.rfind('/')+1:])
        mdFile.new_line("---")
        for filename in filenamesToCombine:
            mdFile.new_line("")
            mdFile.new_header(level=2, title=filename['name'])

            self.addTasks(directory+"/"+filename['name'], mdFile)

        mdFile.create_md_file()

    def createMDFlowFile(self, directory, output_directory):

        self.log.debug("(func createMDFlowFile) dir: "+directory)
        # Reset flow data for each flow file generation
        self.flow = {}

        mdFile = MdUtils(file_name=output_directory+"/flow")
        mdFile.new_header(level=1, title='Flow')

        self.getFlowData(directory)

        mdFile.new_line("```mermaid")
        mdFile.new_line("graph LR")


        for connection in self.flow:
            if self.flow[connection] != []:
                seen = set()
                unique_connectTo = [x for x in self.flow[connection] if x['include'] not in seen and not seen.add(x['include'])]
                for connectTo in unique_connectTo:
                    to = connectTo['include']
                    mdFile.new_line(connection+"("+connection+") --> "+to+"("+to+")")

        mdFile.new_line("```")

        mdFile.create_md_file()

    def getFlowData(self, directory):
        self.log.debug("(func getFlowData) dir:"+directory)

        # If we're generating documentation for a role (directory ends with /roles/role_name/tasks)
        if hasattr(self.config, 'is_role') and self.config.is_role == True:
            self.log.debug("(func getFlowData) processing role - using role tasks/main file")
            self.getFlowDataForFile(directory, f'main{self.config.yaml_extension}')
        # If we're in the main project directory, process the main playbook file
        elif hasattr(self.config, 'playbook_main') and self.config.playbook_main is not None:
            self.log.debug("(func getFlowData) main project - using playbook_main: "+self.config.playbook_main)
            self.getFlowDataForFile(self.config.get_base_dir(), self.config.playbook_main)
        # For main project without playbook_main, look for main.yml in project root
        elif directory.endswith('/tasks') and self.config.get_base_dir() + '/tasks' == directory:
            self.log.debug("(func getFlowData) main project - using project root main file")
            self.getFlowDataForFile(self.config.get_base_dir(), f'main{self.config.yaml_extension}')
        # Fallback to main.yml in current directory
        else:
            self.log.debug("(func getFlowData) fallback - using directory main file")
            self.getFlowDataForFile(directory, f'main{self.config.yaml_extension}')
        # Skip getOrphanedFlowData for roles to avoid mixing flows
        if not (hasattr(self.config, 'is_role') and self.config.is_role == True):
            self.getOrphanedFlowData(directory)

    def getFlowDataForFile(self, directory, filename):
        self.log.debug("(func getFlowDataForFile) dir: "+directory+" filename: "+filename)
        with open(directory+"/"+filename, 'r') as stream:
            try:
                tasks = yaml.safe_load(stream)
                if tasks != None:
                    for task in tasks:
                        rel_dir=os.path.relpath(directory,self.config.get_base_dir())
                        # For roles, remove 'tasks/' prefix to maintain consistency with YAML references
                        if hasattr(self.config, 'is_role') and self.config.is_role == True and rel_dir == 'tasks':
                            rel_dir = ''
                        self.log.debug("(func getFlowDataForFile) relative directory path: "+rel_dir)
                        if 'tasks' in task.keys():
                            for btask in task["tasks"]:
                                self.log.debug("(func getFlowDataForFile) main file")
                                try:
                                    # Build consistent filename for flow nodes
                                    flow_filename = filename if rel_dir == '' else rel_dir+"/"+filename
                                    if 'ansible.builtin.include_tasks' in btask.keys():
                                        self.getTaskReuseFile(btask, "ansible.builtin.include_tasks", flow_filename, directory)
                                    elif 'ansible.builtin.import_tasks' in btask.keys():
                                        self.getTaskReuseFile(btask, "ansible.builtin.import_tasks", flow_filename, directory)
                                    elif 'ansible.builtin.include_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "ansible.builtin.include_role", flow_filename)
                                    elif 'ansible.builtin.import_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "ansible.builtin.import_role", flow_filename)
                                    elif 'include_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "include_role", flow_filename)
                                    elif 'import_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "import_role", flow_filename)
                                except Exception:
                                    pass
                        if 'block' in task.keys():
                            for btask in task["block"]:
                                try:
                                    # Build consistent filename for flow nodes
                                    flow_filename = filename if rel_dir == '' else rel_dir+"/"+filename
                                    if 'ansible.builtin.include_tasks' in btask.keys():
                                        self.getTaskReuseFile(btask, "ansible.builtin.include_tasks", flow_filename, directory)
                                    elif 'ansible.builtin.import_tasks' in btask.keys():
                                        self.getTaskReuseFile(btask, "ansible.builtin.import_tasks", flow_filename, directory)
                                    elif 'ansible.builtin.include_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "ansible.builtin.include_role", flow_filename)
                                    elif 'ansible.builtin.import_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "ansible.builtin.import_role", flow_filename)
                                    elif 'include_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "include_role", flow_filename)
                                    elif 'import_role' in btask.keys():
                                        self.getTaskRoleFile(btask, "import_role", flow_filename)
                                except Exception:
                                    pass
                        try:
                            self.log.debug("(func getFlowDataForFile) tasks file")
                            # Build consistent filename for flow nodes
                            flow_filename = filename if rel_dir == '' else rel_dir+"/"+filename
                            if 'ansible.builtin.include_tasks' in task.keys():
                                self.getTaskReuseFile(task, "ansible.builtin.include_tasks", flow_filename, directory)
                            elif 'ansible.builtin.import_tasks' in task.keys():
                                self.getTaskReuseFile(task, "ansible.builtin.import_tasks", flow_filename, directory)
                            elif 'ansible.builtin.include_role' in task.keys():
                                self.getTaskRoleFile(task, "ansible.builtin.include_role", flow_filename)
                            elif 'ansible.builtin.import_role' in task.keys():
                                self.getTaskRoleFile(task, "ansible.builtin.import_role", flow_filename)
                            elif 'include_role' in task.keys():
                                self.getTaskRoleFile(task, "include_role", flow_filename)
                            elif 'import_role' in task.keys():
                                self.getTaskRoleFile(task, "import_role", flow_filename)
                        except Exception:
                            pass
            except yaml.YAMLError as exc:
                print(exc)

    def getTaskReuseFile(self, task, reuse_type, filename, directory):
        self.log.debug("(func getTaskReuseFile) filename: "+filename)
        self.log.debug("(func getTaskReuseFile) reuse_type: "+reuse_type)
        if 'file' in task[reuse_type]:
            self.log.info("getTaskReuseFilec fix include/import con file")
            tmp_task=task[reuse_type]
            task[reuse_type]=tmp_task['file']
        if task[reuse_type].startswith('{{') is False:
            if filename not in self.flow.keys():
                self.flow[filename] = []
            self.flow[filename].append({"include": task[reuse_type]})
            self.getFlowDataForFile(directory, task[reuse_type])

    def getTaskRoleFile(self, task, reuse_type, filename):
        self.log.debug("(func getTaskRoleFile) filename: "+filename)
        self.log.debug("(func getTaskRoleFile) reuse_type: "+reuse_type)

        # Extract role name from task
        role_name = None
        if isinstance(task[reuse_type], dict):
            # Format: name: role_name
            role_name = task[reuse_type].get('name')
        elif isinstance(task[reuse_type], str):
            # Direct string format
            role_name = task[reuse_type]

        if role_name and not role_name.startswith('{{'):
            if filename not in self.flow.keys():
                self.flow[filename] = []
            # Represent roles with 'role:' prefix to distinguish from tasks
            role_reference = f"role:{role_name}"
            self.flow[filename].append({"include": role_reference})


    def getOrphanedFlowData(self, directory):
        for (dirpath, dirnames, filenames) in walk(directory):
            for filename in filenames:
                relativeFilename = (os.path.relpath(dirpath, directory)+"/"+filename).replace("./","")
                if relativeFilename not in self.flow.keys():
                    self.getFlowDataForFile(directory, relativeFilename)

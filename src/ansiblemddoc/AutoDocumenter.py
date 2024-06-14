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
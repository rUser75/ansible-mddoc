#!/usr/bin/python3

import os
import sys
import subprocess


class install():
    bin = [
        {
            "origin": "src/bin/ansible-mddoc",
            "dest": "ansible-mddoc"
        },
    ]

    libs = [
        {
            "origin": "src/ansiblemddoc",
            "dest": "ansiblemddoc"
        },
    ]
    extra = []

    def __init__(self):

        self.current_file_dir = os.path.dirname(os.path.abspath(__file__))

        self.dest_libs_dir = "/usr/local/lib/python3.6/site-packages"  # Default value
        self.dest_bin = "/usr/bin"
        self.user_home = os.environ["HOME"]
        self.dry = False

        # Parse arguments
        if len(sys.argv) < 2:
            self.print_help()
            sys.exit(0)

        for i in range(1, len(sys.argv)):
            param = sys.argv[i]
            if param == "--dry":
                self.dry = True
            elif param == "--env":
                if i + 1 < len(sys.argv):
                    self.dest_libs_dir = sys.argv[i + 1]
                else:
                    print("Error: --env option requires a path argument.")
                    sys.exit(1)
            elif param == "--help" or param == "-h":
                self.print_help()
            elif param == "--install":
                self.install()
            elif param == "--uninstall":
                self.uninstall()
            else:
                self.print_help()
                sys.exit(1)

    def print_help(self):
        print("About: use install.py --<install | uninstall> [--dry] [--env=path]")
        print("parameters: " + str(sys.argv))

    def link_mod(self, file, type, action):
        ori = None
        dest = None

        # Make a symlink in bin location
        if type == "bin":
            if "lib" in file.keys():
                ori = os.path.join(self.dest_libs_dir, file["lib"])
            elif "origin" in file.keys():
                ori = os.path.join(self.current_file_dir, file["origin"])

            dest = os.path.join(self.dest_bin, file["dest"])

        # Make a symlink in python 3 libraries location
        if type == "lib":
            dest = os.path.join(self.dest_libs_dir, file["dest"])
            ori = os.path.join(self.current_file_dir, file["origin"])

        # Make other hardcoded links
        if type == "extra":
            dest = file["dest"]
            ori = os.path.join(self.current_file_dir, file["origin"])

        if ori is not None and dest is not None:

            if action == "add":
                cmd = "sudo ln -s " + ori + " " + dest
            elif action == "rm":
                cmd = "sudo rm " + dest

            if self.dry is False:
                print(cmd)
                return_code = subprocess.call(cmd, shell=True)
            else:
                print("dry run: " + cmd)

    def install(self):
        print("Install")
        for i in self.bin:
            self.link_mod(i, "bin", "add")
        for j in self.libs:
            self.link_mod(j, "lib", "add")
        for k in self.extra:
            self.link_mod(k, "extra", "add")

    def uninstall(self):
        print("Uninstall")
        for i in self.bin:
            self.link_mod(i, "bin", "rm")
        for j in self.libs:
            self.link_mod(j, "lib", "rm")
        for k in self.extra:
            self.link_mod(k, "extra", "rm")


if __name__ == "__main__":
    i = install()


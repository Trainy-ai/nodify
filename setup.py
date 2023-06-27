# -------------------------------------------------------------------------
# Copyright (c) Trainy, Inc. All rights reserved.
# --------------------------------------------------------------------------

import setuptools
import os
import pathlib
import subprocess


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            version = line.split(delim)[1]

    if os.getenv("TORCH_TB_PROFILER_BUILD_VERSION"):
        version = os.getenv("TORCH_TB_PROFILER_BUILD_VERSION")
    return version


class build_frontend(setuptools.Command):
    """Build the frontend"""

    description = "run `npm run build` on frontend directory"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        cwd = pathlib.Path().absolute()
        root = pathlib.Path(__file__).parent.absolute()
        os.chdir(root / "frontend")
        subprocess.run(["npm", "run", "build"], check=True)
        # restore the working directory
        os.chdir(cwd)


INSTALL_REQUIRED = [
    "HolisticTraceAnalysis",
]

setuptools.setup(
    name="nodify_plugin",
    version=get_version(os.path.join("nodify_plugin", "__init__.py")),
    description="Nodify Tensorboard Plugin.",
    long_description=read("./README.md"),
    long_description_content_type='text/markdown',
    author="Trainy Team",
    author_email="founders@trainy.ai",
    readme="README.md",
    cmdclass={"build_frontend": build_frontend},
    packages=setuptools.find_packages(),
    package_data={
        "nodify_plugin": ["static/**"],
    },
    entry_points={
        "tensorboard_plugins": [
            "example_basic = nodify_plugin.plugin:NodifyPlugin",
        ],
    },
    install_requires=INSTALL_REQUIRED,
    license="BSD-3",
    keywords="pytorch tensorboard profile plugin",
)

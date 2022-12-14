import pkg_resources  # part of setuptools
import textwrap

EPILOG = textwrap.dedent(
    f"""\
                            Version {pkg_resources.require("digipics")[0].version}, part of:
                            digipics (https://gitlab.com/steviehs/digipics)
                            Copyright (C)2021-2022 Stephan Skrodzki
                            """
)

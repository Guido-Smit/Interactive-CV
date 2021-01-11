import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="Interactive CV",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":["Sounds","Music","maps","Artwork"]}},
    description = "Interactive CV",
    executables = executables,
    version = "0.1"
    )
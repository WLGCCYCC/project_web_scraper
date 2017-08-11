from cx_Freeze import setup, Executable

base = None


executables = [Executable("project_web_scraper.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {

        'packages':packages,
    },

}

setup(
    name = "YellowPages Web Scr",
    options = options,
    version = "1.0",
    description = 'Auto collect contact information',
    executables = executables
)
import re
import sys

mode = sys.argv[1]
pattern = r"\$ (\S*)(.*)"

with open("test.script","r") as s:
    scripts = s.read()
scripts = re.sub(r"#.*","",scripts,flags=re.MULTILINE)
args = re.findall(pattern,scripts)


def convert(args,mode):
    sanitize_script = []
    for command, argv in args:
        if command.startswith("mygit"):
            if not mode:
                command = f"./{command}.py"
            else:
                command = f"2041 {command}"
        if "mygit-status" in command:
            command = ("").join([command,argv,'| grep -Ev "\.py|\.sh|\.md|\.script"'])
        else:
            command = ("").join([command,argv])
        sanitize_script.append(f"echo \'$ {command}\'\n")
        sanitize_script.append(f"{command}\n")

    with open("autotest.sh","w") as script:
        script.writelines(sanitize_script)

convert(args,mode)
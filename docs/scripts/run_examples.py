#from pathlib import Path
import subprocess
import textwrap
import shlex
import shutil

from .config import commands, example_dir, doc_dir

def create_example_doc():
    if not example_dir.is_dir():
        raise ValueError("Path to examples is not a directoy")
#    
#    if not doc_dir.is_dir():
#        raise ValueError("Path to doc dir for examples is not a directoy")

    doc_dir.mkdir(exist_ok=True)
    
    # Create/Cleanup help output
    help_dir = doc_dir / 'help'
    shutil.rmtree(help_dir, ignore_errors=True)
    help_dir.mkdir(exist_ok=True)
    
    # Create/Cleanup run output
    run_dir = doc_dir / 'run'
    shutil.rmtree(run_dir,ignore_errors=True)
    run_dir.mkdir(exist_ok=True)
    
    def run_command(entry, cmd):
        header = f'$ python {entry.name} {cmd}\n'
        command = ['python', entry] + shlex.split(cmd)
        result = subprocess.run( command,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cmd_output = textwrap.indent( header + result.stdout.decode('utf-8'), prefix='    ')
        return f".. code-block:: shell-session\n\n{cmd_output}"
        
    
    
    for entry in  example_dir.glob('*.py'):
        print(f"Creating example output for: {entry.stem}")
        # Print help
        command = '-h'
        cmd_output = run_command(entry, command)
    #    output = f'$ python {entry.name} -h\n'
        output_file = help_dir / f'{entry.stem}_help.rst'
        output_file.write_text(cmd_output)
        
        if entry.stem not in commands:
            continue
        for suffix, command in commands[entry.stem].items():
            cmd_output = run_command(entry, command)
            output_file = run_dir / f'{entry.stem}_{suffix}.rst'
            output_file.write_text(cmd_output)

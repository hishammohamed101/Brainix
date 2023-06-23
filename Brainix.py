import subprocess

def execute_tool(tool, arguments):
    command = [tool] + arguments
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode('utf-8').strip(), error.decode('utf-8').strip()

def use_tool(tool, arguments):
    if tool == 'binwalk':
        output_dir = 'binwalk_output'
        execute_tool('binwalk', ['-dd', f'"{output_dir}"', '--run-as=root'] + arguments)
        return output_dir
    elif tool == 'foremost':
        output_dir = 'foremost_output'
        execute_tool('foremost', ['-T', '-o', output_dir] + arguments)
        return output_dir
    elif tool == 'audacity':
        subprocess.Popen(["audacity", arguments[0]], stdin=subprocess.PIPE)
        return None
    elif tool == 'zsteg':
        return execute_tool('zsteg', arguments)[0]
    elif tool == 'wireshark':
        subprocess.Popen(["wireshark"] + arguments, stdin=subprocess.PIPE)
        return None
    else:
        help_output, _ = execute_tool(tool, ['--help'])
        if help_output:
            print(help_output)
            execute_choice = input("Do you want to execute any specific options for this tool? (yes/no): ")
            if execute_choice.lower() == 'yes':
                execute_options = input("Enter the options to execute (e.g., extract -sf): ")
                execute_command = [tool] + execute_options.split() + arguments
                output, _ = execute_tool(tool, execute_command)
                return output
        else:
            print("No help available for the selected tool.")
        return None

def analyze_challenge(file_path):
    with open("recon1.txt", "w") as f:
        # Execute tools and save the output to recon1.txt
        recon_summary = execute_tool('file', [file_path])[0] + '\n'
        recon_summary += execute_tool('strings', [file_path])[0] + '\n'
        recon_summary += execute_tool('exiftool', [file_path])[0] + '\n'
        f.write(recon_summary)

    # Search for flags using grep and print the entire line if a flag is found
    grep_args = ['-irn', '-E', '-e', 'flag', '-e', 'Flag', '-e', 'f14g', '-e', 'FLAG', '-e', 'F14G', 'recon1.txt']
    flags, _ = execute_tool('grep', grep_args)
    if flags:
        print("Possible flag(s) found:")
        flag_lines = flags.split('\n')
        for line in flag_lines:
            if line.strip():
                print(line)
    else:
        print("No flags found.")

    # Execute binwalk and save the output to binwalk_output.txt
    binwalk_output_dir = use_tool('binwalk', ['-M', file_path])
    if binwalk_output_dir:
        binwalk_output_file = f'{binwalk_output_dir}/binwalk_output.txt'
        binwalk_flags, _ = execute_tool('grep', grep_args + [binwalk_output_file])
        if binwalk_flags:
            print("Possible flag(s) found in binwalk output:")
            flag_lines = binwalk_flags.split('\n')
            for line in flag_lines:
                if line.strip():
                    print(line)
        else:
            print("No flags found in binwalk output.")

    # Execute foremost and save the output to foremost_output.txt
    foremost_output_dir = use_tool('foremost', ['-i', file_path])
    if foremost_output_dir:
        foremost_output_file = f'{foremost_output_dir}/audit.txt'
        foremost_flags, _ = execute_tool('grep', grep_args + [foremost_output_file])
        if foremost_flags:
            print("Possible flag(s) found in foremost output:")
            flag_lines = foremost_flags.split('\n')
            for line in flag_lines:
                if line.strip():
                    print(line)
        else:
            print("No flags found in foremost output.")

    # Prompt user for additional tool usage
    additional_tools = [
        'wireshark', 'audacity', 'zsteg', 'steghide',
        'stegcracker', 'autopsy', 'xplico', 'galleta', 'extundelete', 'hashdeep',
        'magicrescue', 'scalpel', 'pdfid', 'img_cat'
    ]
    user_choice = input("Do you want to use additional tools? (yes/no): ")
    if user_choice.lower() == 'yes':
        print("Additional tools available:")
        for i, tool in enumerate(additional_tools, start=1):
            print(f"{i}. {tool}")
        user_tool_choice = input("Select a tool by entering the corresponding number (or enter 'q' to quit): ")
        while user_tool_choice.lower() != 'q':
            try:
                selected_tool_index = int(user_tool_choice) - 1
                if 0 <= selected_tool_index < len(additional_tools):
                    selected_tool = additional_tools[selected_tool_index]
                    print(f"Using {selected_tool}:")
                    help_choice = input("Do you want to see the help for this tool? (yes/no): ")
                    if help_choice.lower() == 'yes':
                        help_output, _ = execute_tool(selected_tool, ['--help'])
                        if help_output:
                            print(help_output)
                            execute_choice = input("Do you want to execute any specific options for this tool? (yes/no): ")
                            if execute_choice.lower() == 'yes':
                                execute_options = input("Enter the options to execute : ")
                                execute_command = [selected_tool] + execute_options.split() + [file_path]
                                output = use_tool(selected_tool, execute_command)
                                if output:
                                    print(output)
                                else:
                                    print("No output generated.")
                        else:
                            print("No help available for the selected tool.")
                    else:
                        execute_choice = input("Do you want to execute this tool without any options? (yes/no): ")
                        if execute_choice.lower() == 'yes':
                            execute_command = [selected_tool]
                            if selected_tool == 'audacity':
                                execute_command.append(file_path)
                            use_tool(selected_tool, execute_command)
                        else:
                            print("Tool usage skipped.")
                else:
                    print("Invalid tool selection.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")
            user_tool_choice = input("Select a tool by entering the corresponding number (or enter 'q' to quit): ")

def main():
    file_path = input("Enter the path to the challenge file: ")
    analyze_challenge(file_path)

if __name__ == "__main__":
    main()

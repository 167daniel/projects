import paramiko
import pandas as pd
import time
import re
from tabulate import tabulate


def parse_report_data(report_data, df):
    report_data = report_data.splitlines()
    date = report_data[2].strip().strip(",").strip('"')
    # Iterate over the lines and extract the relevant information
    for line in report_data:
        line = line.strip().strip('"').strip()  # Remove leading/trailing whitespace and "

        if line.startswith("ok: [switch-"):
            switch_pattern = r'(\d+)'
            switch = re.search(switch_pattern, line, re.MULTILINE).group(0)

        if line.startswith(('Vlan', 'FastEthernet', 'TenGigabitEthernet', 'GigabitEthernet')):
            if " is down," in line:
                flag = False
            else:
                flag = True
            interface = line.split()[0]

        elif line.startswith('Output queue:'):
            regex = r'Output queue: (\d+/\d+)'
            output_queue = re.search(regex, line).group(1)

        elif "packets input" in line:
            packets_input = line.split()[0]

            regex = r'(\d+) bytes'
            num_bytes = re.search(regex, line).group(1)

            regex = r'(\d+)\s+no buffer'
            buffer = re.search(regex, line).group(1)

        elif line.startswith("Received "):
            regex = r'Received (\d+) broadcasts'
            broadcast = re.search(regex, line).group(1)

            regex = r'Received \d+ broadcasts \((\d+) (?:IP )?multicasts\)'
            multicast = re.search(regex, line).group(1)

            if flag:
                record = {"date": date, "switch_number": switch, "interface_name": interface,
                          "output_queue(size/max)": output_queue, "packets_input": packets_input, "bytes": num_bytes,
                          "buffer": buffer, "broadcast": broadcast, "multicast": multicast}

                # Add the record to the DataFrame
                df = df.append(record, ignore_index=True)

    return df


def connect_ssh_and_run_playbook(hostname, port, username, password):
    # Establish SSH connection
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password)

    # Open an interactive shell session
    shell = client.invoke_shell()

    # Send the command to change to the directory containing the playbook
    shell.send('cd /etc/ansible\n')

    # Send the command to execute the playbook with elevated privileges
    shell.send('sudo ansible-playbook -i inventory ./playbooks/collect_interfaces2.yml\n')

    # Wait for the command to execute and receive the output
    output = ''
    count = 0
    while "PLAY RECAP" not in output:
        output += shell.recv(1024).decode()
        if 'password for study' in output and count == 0:
            # Send the password again when prompted
            count += 1
            shell.send(password + '\n')
            time.sleep(1)  # Wait for the command to execute and receive the output

    return output, client


# column names for DF
column_names = ["date", "switch_number", "interface_name", "output_queue(size/max)", "packets_input", "bytes", "buffer",
                "broadcast", "multicast"]

csv_path = "./DB_cisco_ios_logs/interfaces_full_report.csv"

# SSH connection parameters
hostname = '132.66.51.153'
port = 22
username = 'study'
password = 'Study'

# connect to server and run playbook, output will contain the results of the playbook report
output, client = connect_ssh_and_run_playbook(hostname, port, username, password)

# Extract the report data from the output
report_start_index = output.find('"report_data": ')
if report_start_index != -1:
    report_start_index += len('"report_data": ') - 40
    report_end_index = output.find('PLAY RECAP') - 4
    report_data_str = output[report_start_index:report_end_index]

    # Process the report data and obtain the DataFrame
    report_df = pd.DataFrame(columns=column_names)
    report_df = parse_report_data(report_data_str, report_df)

    print(tabulate(report_df, headers='keys'))

else:
    print("Report data not found in output.")

# Close the SSH connection
client.close()

'''
This is my script for CyberPatriot.
Speciffically my windows script to automate password policies.
Will automate more eventually
'''

import os
import sys
import win32security as security
import win32net as net
import win32netcon as netcon
import tempfile
import subprocess
import re

def setPasswordPolicy():
    """
    Sets Local Password Policy
    """

    # Get Current Policy
    currentPassword = net.NetUserModalsGet(None, 0)
    
    # Modify password policy
    currentPassword['min_passwd_len'] = 12 # Min Password Length
    currentPassword['max_passwd_age'] = 90 * 24 * 3600 # Max Password age in Seconds (90 days)
    currentPassword['min_passwd_age'] = 30 * 24 * 3600 # Min Password age in Seconds (30 days)
    currentPassword['password_hist_len'] = 8 # remembers 8 passwords

    net.NetUserModalsSet(None, 0, currentPassword)

    print("               #     Password Policy    # ")
    print(f'Min Password Length:           {currentPassword['min_passwd_len']}')
    print(f'Max Password Age:              {currentPassword['max_passwd_age'] / 3600 * 24}')
    print(f'Min Password Age:              {currentPassword['min_passwd_age'] / 3600 * 24}')
    print(f'Password History:              {currentPassword['password_hist_len']}')

    # Get Account Lockout Policy
    currentAccount = net.NetUserModalsGet(None, 3)

    currentAccount['lockout_duration'] = 30 * 60 # Lock for 30 mins
    currentAccount['lockout_observation_window'] = 30 * 60 # 30 min window
    currentAccount['lockout_threshold'] = 3

    net.NetUserModalsSet(None, 3, currentAccount)

    print("               # Account Lockout Policy # ")
    print(f'Lockout Duration:              {currentAccount['lockout_duration'] / 60}')
    print(f'Lockout Observation Window:    {currentAccount['lockout_observation_window'] / 60}')
    print(f'Lockout Threshold:             {currentAccount['lockout_threshold']}')

    # Edit Security Policies that cannot be adjusted via pywin32

    exportCfg = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".cfg")
    importCfg = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".cfg")
    exportCfg.close()
    importCfg.close()

    try:
        currentPolicy = subprocess.run(
            ['secedit', '/export', '/cfg', exportCfg.name, '/quiet'],
            capture_output=True,
            text=True
        )

        if currentPolicy.returncode != 0:
            print(f"Error exporting policy: {currentPolicy.stderr}")
            return
        
        content = ''

        # Read Exported Policy
        with open(exportCfg.name, 'r', encoding="utf-8") as f:
            content = f.read()

        settings = {
            'PasswordComplexity': '1',
            'MinimumPasswordLength': '12',
            'ClearTextPassword': '0',
            'RequireLogonToChangePassword': '1'
        }

        modifiedContent = content

        for setting, value in settings.items():
            pattern = rf'^{setting}\s*=\s*\d+'
            replacement = f'{setting} = {value}'

            if re.search(pattern, modifiedContent, re.MULTILINE):
                modifiedContent = re.sub(pattern, replacement, modifiedContent, flags=re.MULTILINE)
            else:
                systemAccessPattern = r'\[System Access\]'
                if re.search(systemAccessPattern, modifiedContent):
                    modifiedContent = re.sub(
                        systemAccessPattern,
                        f'[System Access]\n{replacement}',
                        modifiedContent,
                        count=1
                    )
                else:
                    modifiedContent +=  f'\n[System Access]\n{replacement}\n'

        with open(importCfg.name, 'w', encoding='utf-8') as f:
            f.write(modifiedContent)

        # import modified policy
        db_path = os.path.join(tempfile.gettempdir(), 'secedit.sdb')
        result = subprocess.run(
            ['secedit', '/configure', '/db', db_path, '/cfg', importCfg.name, '/quiet'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f'Error importing policy {result.stderr}')
            return
        
        # Force Policy Update
        subprocess.run(['gpupdate', '/force'], capture_output=True)

        print("Password Policies have been updated")

    finally:
        try:
            os.unlink(exportCfg.name)
            os.unlink(importCfg.name)
        except:
            pass

def isServiceRunning(service_name):
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
             f"(Get-Service -Name '{service_name}' -ErrorAction Stop).Status -eq 'Running'"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().lower() == "true"
    except subprocess.CalledProcessError:
        return False

def main():
    print(r'''
--------------------------------------------------------------------------------------------------------------
     _______. __    __   __  .__   __. ____    ____  _______   __    __    ______  __  ___ 
    /       ||  |  |  | |  | |  \ |  | \   \  /   / |       \ |  |  |  |  /      ||  |/  / 
   |   (----`|  |__|  | |  | |   \|  |  \   \/   /  |  .--.  ||  |  |  | |  ,----'|  '  /  
    \   \    |   __   | |  | |  . `  |   \_    _/   |  |  |  ||  |  |  | |  |     |    <   
.----)   |   |  |  |  | |  | |  |\   |     |  |     |  '--'  ||  `--'  | |  `----.|  .  \  
|_______/    |__|  |__| |__| |__| \__|     |__|     |_______/  \______/   \______||__|\__\ 
  ''')
                                                                                           
    print("--------------------------------------------------------------------------------------------------------------")
    print("This script will change things like the password policy and harden the system")
    print("Please do not execute unless you know what you are doing")
    print("")

    print("Are Forensics questions comepleted? (Y/N)")
    forensics = input("")
    forensics = forensics.lower()

    forensicsCompletion = forensics == "y"

    if forensicsCompletion:
        print("Great job")
        setPasswordPolicy()

        servicesToCheck = [
            "TlntSvr",          # Telnet
            "ftpsvc",           # FTP
            "RemoteRegistry",   # Remote Registry
            "RemoteAccess",     # Routing and Remote Access
            "SNMP",             # SNMP
            "SSDPSRV",          # SSDP Discovery
            "W3SVC",            # IIS Web Server
            "TermService",      # Remote Desktop
            "TeamViewer",       # TeamViewer
        ]

        print("               #   Disabling Services   # ")
        for service in servicesToCheck:
            if isServiceRunning(service):
                yes = input(f'Check the Readme. Should {service} be DISABLED? (Y/N): ')
                if yes.lower() == "y" or yes.lower() == "yes":
                    try:
                        # Stop the service
                        subprocess.run(
                            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", 
                             "-Command", f"Stop-Service -Name '{service}' -Force; Set-Service -Name '{service}' -StartupType Disabled"],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        print(f"{service} has been stopped and disabled")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to disable {service}: {e.stderr}")

    else:
        print("This script can and will cause forensic question answers to be removed")
        print("as the answers to those forensic questions can be unauthorized files or software")
        print("Go do Forenics Questions before executing this script.")

def exit():
    print("Check out my Github for more of my projects and scripts at: https://github.com/ShinyDuck21")
    input("Press Enter to exit...")

if __name__ == "__main__":
    # === Main Logic ===
    main()
    exit()
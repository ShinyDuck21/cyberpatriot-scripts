#!/usr/bin/env python3

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
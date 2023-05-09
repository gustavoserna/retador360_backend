import os
import subprocess

class CommandsLinux():

    def getDuration(self, path_video):
        print('Linux Space')
        cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 {}'.format(path_video)
        result = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.readline()
        stderr = result.stderr.readline()
        if stderr != b'':
            #print(stderr)
            return("Error")
        else:
            return(int(float(stdout.decode('utf-8'))))

        
    def executeCommands(self,cmds,homePath,fileNames):
        print('Linux Space')
        exit_code = os.system('mkdir {}/cache'.format(homePath))
        if type(cmds) == list and len(cmds) > 0:
            for i in range(len(cmds)):
                #result = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                exit_code = os.system(command=cmds[i])
                #print('index = \t{} \n Filename= \t{}'.format(i,fileNames[i]))
                if exit_code != 0:
                    return("Error")
                elif i == 0:
                    exit_code = os.system('mv {}/{} {}/cache/'.format(homePath,fileNames[i],homePath))
                elif i == len(cmds) - 1:
                    os.system(command='rm -f {}/cache/*'.format(homePath))
                    os.system(command='rm -rf {}/cache'.format(homePath))
                    os.chdir( '{}/'.format(homePath))
                    os.system(command='find . ! -name "{}" -type f -exec rm -f {{}} +'.format(fileNames[i+1]))
            return 0
        else:
            return("Error")
        
class CommandsWindows:

    def executeCommands(self,cmds,homePath,fileNames):
        print('Linux Windows')
        exit_code = os.system('mkdir {}\\cache'.format(homePath))
        if type(cmds) == list and len(cmds) > 0:
            for i in range(len(cmds)):
                #result = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                exit_code = os.system(command=cmds[i])
                if exit_code != 0:
                    return("Error")
                elif i == 0:
                    exit_code = os.system('move {}\\{} {}\\cache'.format(homePath,fileNames[i],homePath))
                elif i == len(cmds) - 1:
                    os.system(command='del {}\\cache\\* /s /q'.format(homePath))
                    os.system(command='rmdir {}\\cache'.format(homePath))
                    os.chdir('{}\\'.format(homePath))
                    os.system(command='for %i in (*) do if not "%~i" == "{}" del "%~i"'.format(fileNames[i+1]))
            return 0
        else:
            return("Error")
        
    def getDuration(self,path_video):
        print('Linux Windows')
        cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 {}'.format(path_video)
        result = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.readline()
        stderr = result.stderr.readline()
        if stderr != b'':
            #print(stderr)
            return("Error")
        else:
            return(int(float(stdout.decode('utf-8'))))
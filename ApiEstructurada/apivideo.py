import os
import time
if os.name == 'nt':
    from command import CommandsWindows as cmd
    separator = '\\'
else:
    from command import CommandsLinux as cmd
    separator = '/'

class ApiVideo(): 
    def __init__(self, jsonData):
            self.jsonData = jsonData
            self.commands = cmd()
            pass

    def processVideo(self):
        request_data = self.jsonData
        print(type(request_data))
        print(type(self.jsonData))
        commands = []
        videoPath = None
        audio = None
        options = None
        audioPath = None
        outputName = None
        fileNames = []
        logoPositions = {
            "center" : "overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2",
            "top-left" : "overlay=x=main_w*0.01:y=main_h*0.01",
            "top-right" : "overlay=x=main_w-overlay_w-(main_w*0.01):y=main_h*0.01",
            "bottom-left": "overlay=x=main_w*0.01:y=main_h-overlay_h-(main_h*0.01)",
            "bottom-right" : "overlay=x=main_w-overlay_w-(main_w*0.01):y=main_h-overlay_h-(main_h*0.01)"
        }

        if request_data:
            if 'videoPath' in request_data:
                videoPath = request_data['videoPath']
            
            if 'audioPath' in request_data:
                audio = request_data['audioPath']

            if 'options' in request_data:
                options = request_data['options']
            
            if 'outputName' in request_data:
                outputName = request_data['outputName']

            ffmpegPath = "C:{}ffmpeg{}bin{}ffmpeg.exe"
            reverse = options['reverse']
            slowMo = options["slowMo"]
            logoDict = options['logo']

            splitPathVideo = os.path.split(videoPath)
            videoHead = splitPathVideo[0]
            videoName = splitPathVideo[1]
            fileNames.append(videoName)

            if logoDict['selected']:
                logoPath = logoDict['path']
                positions = logoDict['positions']
                # print(type(positions))
                comlex = ' -filter_complex \"'
                logoCommand = 'ffmpeg -y -i {}{}{}'.format(videoHead,separator,videoName)
                logo = ' -i {}'.format(logoPath)
                for i in positions[:-1]:
                    logo += ' -i {}'.format(logoPath)
                
                logoCommand += logo+comlex
                
                for i in range(len(positions)):
                    position = str(logoPositions[positions[i]])
                    # print(position)
                    logoCommand += position
                    if i != len(positions) - 1:
                        logoCommand += ","
                    else:
                        logoCommand += "\""
                
                if reverse['selected'] or slowMo['selected'] :
                    videoName = "afterlogo.mp4"
                    fileNames.append(videoName)
                else:
                    videoName = outputName+'_'+str(int(time.time()))+'.mp4'
                    fileNames.append(videoName)
                logoCommand += " {}{}{}".format(videoHead,separator,videoName)
                # print(logoCommand)
                commands.append(logoCommand)

            duration = self.commands.getDuration(videoPath)
            if (type(duration) != int):
                return "No able to get video duration"
            
            cmd = ''

            if (reverse['selected']):
                cmd = 'ffmpeg -y -i {}{}{} -filter_complex \"'.format(videoHead,separator,videoName)
                if (slowMo['selected']):
                    if audio['selected']:
                        videoName = 'afterSloRev.mp4'
                        fileNames.append(videoName)
                    else:
                        videoName = outputName+'_'+str(int(time.time()))+'.mp4'
                        fileNames.append(videoName)
                    reverseDur = reverse['duration']
                    slowDur = slowMo['duration']
                    revFrom = reverseDur['from']
                    revTo = reverseDur['to']
                    sloFrom = slowDur['from']
                    sloTo = slowDur['to']
                    velocity = slowMo['velocity']
                    if revFrom < sloFrom:
                        if sloFrom == revTo:
                            zeroTrim = {'video':['[0:v]trim=0:{},setpts=PTS-STARTPTS[v0];'.format(revFrom),'[v0]'],
                                        'audio':['[0:a]atrim=0:{},asetpts=PTS-STARTPTS[a0];'.format(revFrom),'[a0]']}
                            firstTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v1];'.format(revFrom,revTo),'[v1]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a1];'.format(revFrom,revTo),'[a1]']}
                            reversetrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v2];'.format(revFrom,revTo),'[v2]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a2];'.format(revFrom,revTo),'[a2]']}
                            thirdTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v3];'.format(revFrom,revTo),'[v3]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a3];'.format(revFrom,revTo),'[a3]']}
                            slowTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v4];'.format(sloFrom,sloTo),'[v4]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a4];'.format(sloFrom,sloTo),'[a4]']}
                            fifthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v5];'.format(sloTo,duration),'[v5]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a5];'.format(sloTo,duration),'[a5]']}
                            trimSection = zeroTrim['video'][0]+zeroTrim['audio'][0]+firstTrim['video'][0]+firstTrim['audio'][0]+reversetrim['video'][0]+reversetrim['audio'][0]+thirdTrim['video'][0]+thirdTrim['audio'][0]+slowTrim['video'][0]+slowTrim['audio'][0]+fifthTrim['video'][0]+fifthTrim['audio'][0]
                            reverseC = {'video': ['{}reverse[vr];'.format(reversetrim['video'][1]), '[vr]'],
                                    'audio': ['{}areverse[ar];'.format(reversetrim['audio'][1]), '[ar]']}
                            slowC = {'video': ['{}setpts=PTS/{}[vs];'.format(slowTrim['video'][1],velocity), '[vs]'],
                                    'audio': ['{}atempo={}[as];'.format(slowTrim['audio'][1],velocity), '[as]']}
                            concat = ' '+zeroTrim['video'][1]+zeroTrim['audio'][1]+firstTrim['video'][1]+firstTrim['audio'][1]+reverseC['video'][1]+reverseC['audio'][1]+thirdTrim['video'][1]+thirdTrim['audio'][1]+slowC['video'][1]+slowC['audio'][1]+fifthTrim['video'][1]+fifthTrim['audio'][1]+' concat=n=6:v=1:a=1 '
                            cmd += trimSection+reverseC['video'][0]+reverseC['audio'][0]+slowC['video'][0]+slowC['audio'][0]+concat+'\" -an {}{}{}'.format(videoHead,separator,videoName)
                        else:
                            zeroTrim = {'video':['[0:v]trim=0:{},setpts=PTS-STARTPTS[v0];'.format(revFrom),'[v0]'],
                                        'audio':['[0:a]atrim=0:{},asetpts=PTS-STARTPTS[a0];'.format(revFrom),'[a0]']}
                            firstTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v1];'.format(revFrom,revTo),'[v1]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a1];'.format(revFrom,revTo),'[a1]']}
                            reversetrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v2];'.format(revFrom,revTo),'[v2]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a2];'.format(revFrom,revTo),'[a2]']}
                            thirdTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v3];'.format(revFrom,revTo),'[v3]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a3];'.format(revFrom,revTo),'[a3]']}
                            fouthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v4];'.format(revTo,sloFrom),'[v4]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a4];'.format(revTo,sloFrom),'[a4]']}
                            slowTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v5];'.format(sloFrom,sloTo),'[v5]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a5];'.format(sloFrom,sloTo),'[a5]']}
                            sixthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v6];'.format(sloTo,duration),'[v6]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a6];'.format(sloTo,duration),'[a6]']}
                            trimSection = zeroTrim['video'][0]+zeroTrim['audio'][0]+firstTrim['video'][0]+firstTrim['audio'][0]+reversetrim['video'][0]+reversetrim['audio'][0]+thirdTrim['video'][0]+thirdTrim['audio'][0]+fouthTrim['video'][0]+fouthTrim['audio'][0]+slowTrim['video'][0]+slowTrim['audio'][0]+sixthTrim['video'][0]+sixthTrim['audio'][0]
                            reverseC = {'video': ['{}reverse[vr];'.format(reversetrim['video'][1]), '[vr]'],
                                    'audio': ['{}areverse[ar];'.format(reversetrim['audio'][1]), '[ar]']}
                            slowC = {'video': ['{}setpts=PTS/{}[vs];'.format(slowTrim['video'][1],velocity), '[vs]'],
                                    'audio': ['{}atempo={}[as];'.format(slowTrim['audio'][1],velocity), '[as]']}
                            concat = zeroTrim['video'][1]+zeroTrim['audio'][1]+firstTrim['video'][1]+firstTrim['audio'][1]+reverseC['video'][1]+reverseC['audio'][1]+thirdTrim['video'][1]+thirdTrim['audio'][1]+fouthTrim['video'][1]+fouthTrim['audio'][1]+fifthTrim['video'][1]+slowC['audio'][1]+slowC['video'][1]+sixthTrim['audio'][1]+' concat=n=7:v=1:a=1 '
                            cmd += trimSection+reverseC['video'][0]+reverseC['audio'][0]+slowC['video'][0]+slowC['audio'][0]+concat+'\" -an {}{}{}'.format(videoHead,separator,videoName)
                    else:
                        if sloTo == revFrom:
                            zeroTrim = {'video':['[0:v]trim=0:{},setpts=PTS-STARTPTS[v0];'.format(sloFrom),'[v0]'],
                                        'audio':['[0:a]atrim=0:{},asetpts=PTS-STARTPTS[a0];'.format(sloFrom),'[a0]']}
                            slowTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v1];'.format(sloFrom,sloTo),'[v1]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a1];'.format(sloFrom,sloTo),'[a1]']}
                            secondTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v2];'.format(revFrom,revTo),'[v2]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a2];'.format(revFrom,revTo),'[a2]']}
                            reversetrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v3];'.format(revFrom,revTo),'[v3]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a3];'.format(revFrom,revTo),'[a3]']}
                            fouthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v4];'.format(revFrom,revTo),'[v4]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a4];'.format(revFrom,revTo),'[a4]']}
                            fifthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v5];'.format(revTo,duration),'[v5]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a5];'.format(revTo,duration),'[a5]']}
                            trimSection = zeroTrim['video'][0]+zeroTrim['audio'][0]+slowTrim['video'][0]+slowTrim['audio'][0]+secondTrim['video'][0]+secondTrim['audio'][0]+reversetrim['video'][0]+reversetrim['audio'][0]+fouthTrim['video'][0]+fouthTrim['audio'][0]+fifthTrim['video'][0]+fifthTrim['audio'][0]
                            reverseC = {'video': ['{}reverse[vr];'.format(reversetrim['video'][1]), '[vr]'],
                                    'audio': ['{}areverse[ar];'.format(reversetrim['audio'][1]), '[ar]']}
                            slowC = {'video': ['{}setpts=PTS/{}[vs];'.format(slowTrim['video'][1],velocity), '[vs]'],
                                    'audio': ['{}atempo={}[as];'.format(slowTrim['audio'][1],velocity), '[as]']}
                            concat = zeroTrim['video'][1]+zeroTrim['audio'][1]+slowC['video'][1]+slowC['audio'][1]+secondTrim['video'][1]+secondTrim['audio'][1]+reversetrim['video'][1]+reversetrim['audio'][1]+fouthTrim['video'][1]+fouthTrim['audio'][1]+fifthTrim['video'][1]+fifthTrim['audio'][1]+' concat=n=6:v=1:a=1 '
                            cmd += trimSection+reverseC['video'][0]+reverseC['audio'][0]+slowC['video'][0]+slowC['audio'][0]+concat+'\" -an {}{}{}'.format(videoHead,separator,videoName)
                        else:
                            zeroTrim = {'video':['[0:v]trim=0:{},setpts=PTS-STARTPTS[v0];'.format(sloFrom),'[v0]'],
                                        'audio':['[0:a]atrim=0:{},asetpts=PTS-STARTPTS[a0];'.format(sloFrom),'[a0]']}
                            slowTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v1];'.format(sloFrom,sloTo),'[v1]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a1];'.format(sloFrom,sloTo),'[a1]']}
                            secondTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v2];'.format(sloTo,revFrom),'[v2]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a2];'.format(sloTo,revFrom),'[a2]']}
                            thirdTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v3];'.format(revFrom,revTo),'[v3]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a3];'.format(revFrom,revTo),'[a3]']}
                            reversetrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v4];'.format(revFrom,revTo),'[v4]'],
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a4];'.format(revFrom,revTo),'[a4]']}
                            fifthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v5];'.format(revFrom,revTo),'[v5]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a5];'.format(revFrom,revTo),'[a5]']}
                            sixthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v6];'.format(revTo,duration),'[v6]'],                
                                        'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a6];'.format(revTo,duration),'[a6]']}
                            trimSection = zeroTrim['video'][0]+zeroTrim['audio'][0]+slowTrim['video'][0]+slowTrim['audio'][0]+secondTrim['video'][0]+secondTrim['audio'][0]+thirdTrim['video'][0]+thirdTrim['audio'][0]+reversetrim['video'][0]+reversetrim['audio'][0]+fifthTrim['video'][0]+fifthTrim['audio'][0]+sixthTrim['video'][0]+sixthTrim['audio'][0]
                            reverseC = {'video': ['{}reverse[vr];'.format(reversetrim['video'][1]), '[vr]'],
                                    'audio': ['{}areverse[ar];'.format(reversetrim['audio'][1]), '[ar]']}
                            slowC = {'video': ['{}setpts=PTS/{}[vs];'.format(slowTrim['video'][1],velocity), '[vs]'],
                                    'audio': ['{}atempo={}[as];'.format(slowTrim['audio'][1],velocity), '[as]']}
                            concat = zeroTrim['video'][1]+zeroTrim['audio'][1]+slowC['video'][1]+slowC['audio'][1]+secondTrim['video'][1]+secondTrim['audio'][1]+thirdTrim['video'][1]+thirdTrim['audio'][1]+reverseC['video'][1]+reverseC['audio'][1]+fifthTrim['video'][1]+fifthTrim['audio'][1]+sixthTrim['video'][1]+sixthTrim['audio'][1]+' concat=n=7:v=1:a=1 '
                            cmd += trimSection+reverseC['video'][0]+reverseC['audio'][0]+slowC['video'][0]+slowC['audio'][0]+concat+'\" -an {}{}{}'.format(videoHead,separator,videoName)
                else:
                    videoName = 'afterReverse.mp4'
                    reverseDur = reverse['duration']
                    revFrom = reverseDur['from']
                    revTo = reverseDur['to']
                    zeroTrim = {'video':['[0:v]trim=0:{},setpts=PTS-STARTPTS[v0];'.format(revFrom),'[v0]'],
                                'audio':['[0:a]atrim=0:{},asetpts=PTS-STARTPTS[a0];'.format(revFrom),'[a0]']}
                    firstTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v1];'.format(revFrom,revTo),'[v1]'],
                                'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a1];'.format(revFrom,revTo),'[a1]']}
                    reversetrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v2];'.format(revFrom,revTo),'[v2]'],
                                'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a2];'.format(revFrom,revTo),'[a2]']}
                    thirdTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v3];'.format(revFrom,revTo),'[v3]'],
                                'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a3];'.format(revFrom,revTo),'[a3]']}
                    fouthTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v4];'.format(revTo,duration),'[v4]'],                
                                'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a4];'.format(revTo,duration),'[a4]']}
                    trimSection = zeroTrim['video'][0]+zeroTrim['audio'][0]+firstTrim['video'][0]+firstTrim['audio'][0]+reversetrim['video'][0]+reversetrim['audio'][0]+thirdTrim['video'][0]+thirdTrim['audio'][0]+fouthTrim['video'][0]+fouthTrim['audio'][0]
                    reverseC = {'video': ['{}reverse[vr];'.format(reversetrim['video'][1]), '[vr]'],
                                    'audio': ['{}areverse[ar];'.format(reversetrim['audio'][1]), '[ar]']}
                    concat = zeroTrim['video'][1]+zeroTrim['audio'][1]+firstTrim['video'][1]+firstTrim['audio'][1]+reverseC['video'][1]+reverseC['audio'][1]+thirdTrim['video'][1]+thirdTrim['audio'][1]+fouthTrim['video'][1]+fouthTrim['audio'][1]+' concat=n=5:v=1:a=1 '
                    cmd += trimSection+reverseC['video'][0]+reverseC['audio'][0]+concat+'\" -an {}{}{}'.format(videoHead,separator,videoName)
            elif (slowMo['selected']):
                cmd = 'ffmpeg -i {} -filter_complex \"'.format(videoName)
                slowDur = slowMo['duration']
                sloFrom = slowDur['from']
                sloTo = slowDur['to']
                zeroTrim = {'video':['[0:v]trim=0:{},setpts=PTS-STARTPTS[v0];'.format(sloFrom),'[v0]'],
                            'audio':['[0:a]atrim=0:{},asetpts=PTS-STARTPTS[a0];'.format(sloFrom),'[a0]']}
                slowTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v1];'.format(sloFrom,sloTo),'[v1]'],
                            'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a1];'.format(sloFrom,sloTo),'[a1]']}
                secondTrim = {'video':['[0:v]trim={}:{},setpts=PTS-STARTPTS[v2];'.format(sloTo,duration),'[v2]'],
                            'audio':['[0:a]atrim={}:{},asetpts=PTS-STARTPTS[a2];'.format(sloTo,duration),'[a2]']}
                trimSection = zeroTrim['video'][0]+zeroTrim['audio'][0]+slowTrim['video'][0]+slowTrim['audio'][0]+secondTrim['video'][0]+secondTrim['audio'][0]
                slowC = {'video': ['{}setpts=PTS/{}[vs];'.format(slowTrim['video'][1],velocity), '[vs]'],
                                    'audio': ['{}atempo={}[as];'.format(slowTrim['audio'][1],velocity), '[as]']}
                concat = zeroTrim['video'][1]+zeroTrim['audio'][1]+slowC['video'][1]+slowC['audio'][1]+secondTrim['video'][1]+secondTrim['audio'][1]+' concat=n=3:v=1:a=1 '
                videoName = 'afterSlow.mp4'
                cmd += trimSection+slowC['video'][0]+slowC['audio'][0]+concat+'\" -an {}{}{}'.format(videoHead,separator,videoName)
            
            if cmd != '':
                commands.append(cmd)
            
            if audio['selected']:
                audioPath = audio['path']
                commandAudio = 'ffmpeg -y -i {}{}{} -i {} -map 0:v -map 1:a -c:v copy -c:a copy -shortest'.format(videoHead,separator,videoName,audioPath,)
                videoName = outputName+'_'+str(int(time.time()))+'.mp4'
                commandAudio += ' {}{}{}'.format(videoHead,separator,videoName)
                fileNames.append(videoName)
                commands.append(commandAudio)
            for cmd in commands:
                print(cmd)
            resultCommands = self.commands.executeCommands(commands, videoHead, fileNames)
            result = "Video procesado" if (type(resultCommands) == int) else "No se pudo procesar el video"
            return result
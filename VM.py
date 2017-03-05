import os
import sys
class Parser(object):
    def __init__(self, file):
       self.f=open(file)
       self.lineL=None
       self.current=None

    def hasMoreCommands(self):
        for line in self.f:
            self.lineL=line.strip()
            command=self.lineL.split()
            if command and (not command[0].startswith('/')):
                yield 1
        yield 0

    def advance(self):
        #！！！！
        condition=self.hasMoreCommands().next()
        if condition:
            self.current=self.lineL
            return 1
        else:
            return 0

    def commandType(self):
        command=self.current.split()[0]
        operator=['add','sub','neg','eq','gt',\
            'lt','and','or','not']
        if command in operator:
            return 'C_ARITHMETIC'
        elif command=='push':
            return 'C_PUSH'
        elif command=='pop':
            return 'C_POP'
        elif command=='label':
            return 'C_LABLE'
        elif command=='goto':
            return 'C_GOTO'
        elif command=='if-goto':
            return 'C_IF'
        elif command=='function':
            return 'C_FUNCTION'
        elif command=='call':
            return 'C_CALL'
        elif command=='return':
            return 'C_RETURN'

        return None
        

    def arg1(self):
        commands=self.current.split()
        commandType=self.commandType()
        if commandType=='C_ARITHMETIC':
            return commands[0]
        elif commandType=='C_RETURN':
            return None
        else:
            return commands[1]

    def arg2(self):
        commands=self.current.split()
        commandType=self.commandType()
        if commandType in ('C_PUSH','C_POP','C_FUNCTION','C_CALL'):
            return commands[2]
        else:
            return None

class CodeWriter(object):
    def __init__(self,path):
        self.f_output=open(path,'a+')
        self.label_num=0
        self.call_num=1
        init='@256\n'+'D=A\n'+'@SP\n'+'M=D\n'+'@5\nD=A\n@SP\nM=M+D\n'+'@Sys.init\n'+'0;JEQ\n'
        self.f_output.write(init)

    def writeLable(self,name):
        commandAsm='('+name+')\n'
        self.f_output.write(commandAsm)

    def writeIf(self,name):
        commandAsm='@SP\n'+'A=M-1\n'+'D=M\n'+'@SP\n'+'M=M-1\n'+'@'+name+'\n'+'D;JNE\n'
        self.f_output.write(commandAsm)

    def writeGoto(self, name):
        commandAsm='@'+name+'\n'+'0;JEQ\n'
        self.f_output.write(commandAsm)

    def writeFunction(self, functionName, numLocals):
        commandAsm='('+functionName+')\n'+'@'+numLocals+'\n'+'D=A\n'+'@'+functionName+'$0\n'+'D;JEQ\n'+'@R14\n'+'M=D-1\n'+'('+functionName+'$1)\n'+\
            '@R14\n'+'D=M\n'+'@LCL\n'+'A=M+D\n'+'M=0\n'+'@R14\n'+'M=M-1\n'+'D=M\n'+'@'+functionName+'$1\n'+'D;JGE\n'+\
            '('+functionName+'$0)\n'+'@'+numLocals+'\n'+'D=A\n'+'@SP\n'+'M=M+D\n'
        self.f_output.write(commandAsm)

    def writeCall(self, functionName, numArgs):
        commandAsm='@'+numArgs+'\n'+'D=A\n'+'@'+functionName+'$Arg0'+str(self.call_num)+'\n'+'D;JNE\n@SP\nM=M+1\n'+'('+functionName+'$Arg0'+str(self.call_num)+')\n'+\
            '@'+functionName+'$rb'+str(self.call_num)+'\n'+'D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'+'@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'+\
           '@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'+'@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'+'@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'+\
           '@'+numArgs+'\nD=A\n'+'@'+functionName+'$Arg0s'+str(self.call_num)+'\n'+'D;JNE\n@1\nD=A\n'+'('+functionName+'$Arg0s'+str(self.call_num)+')\n'+\
           '\n@5\nD=A+D\n@SP\nD=M-D\n@ARG\nM=D\n'+'@SP\nD=M\n@LCL\nM=D\n'+'@'+functionName+'\n'+'0;JEQ\n'+'('+functionName+'$rb'+str(self.call_num)+')\n'
        self.call_num+=1
        self.f_output.write(commandAsm)

    def writeReturn(self):
        commandAsm='@LCL\nD=M\n@R15\nM=D\n'+'@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n@SP\nM=M-1\n'+\
            '@ARG\nD=M\n@SP\nM=D+1\n'+'@R15\nA=M-1\nD=M\n@THAT\nM=D\n'+'@2\nD=A\n@R15\nA=M-D\nD=M\n@THIS\nM=D\n'+\
            '@3\nD=A\n@R15\nA=M-D\nD=M\n@ARG\nM=D\n'+'@4\nD=A\n@R15\nA=M-D\nD=M\n@LCL\nM=D\n'+\
            '@5\nD=A\n@R15\nA=M-D\nA=M\n0;JEQ\n'
        self.f_output.write(commandAsm)


    def writeArithmetic(self,command):
        if command in ('add','sub','and','or'):
            if command=='add':
                operator='+'
            elif command=='sub':
                operator='-'
            elif command=='and':
                operator='&'
            elif command=='or':
                operator='|'
            commandAsm='@SP\n'+'A=M-1\n'+'D=M\n'+'A=A-1\n'+\
                'M=M'+operator+'D\n'+'@SP\nM=M-1\n'
            self.f_output.write(commandAsm)
        elif command in ('eq','gt','lt'):
            if command=='eq':
                option='JEQ'
            elif command=='gt':
                option='JGT'
            elif command=='lt':
                option='JLT'
            commandAsm='@SP\n'+'A=M-1\n'+'D=M\n'+'A=A-1\n'+'D=M-D\n'+\
                '@'+'label'+str(self.label_num)+'\n'+'D;'+option+'\n'+'@SP\n'+'A=M-1\n'+'A=A-1\n'+'M=0\n'+\
                '@SP\n'+'M=M-1\n'+'@end'+str(self.label_num)+'\n'+'0;JMP\n'+'(label'+str(self.label_num)+')\n'+'@SP\n'+\
                'A=M-1\n'+'A=A-1\n'+'M=-1\n'+'@SP\n'+'M=M-1\n'+'(end'+str(self.label_num)+')\n'
            self.label_num+=1
            self.f_output.write(commandAsm)
        elif command in ('neg','not'):
            if command=='neg':
                operator='-'
            elif command=='not':
                operator='!'
            commandAsm='@SP\n'+'A=M-1\n'+'M='+operator+'M\n'
            self.f_output.write(commandAsm)


    def writePushPop(self, type, segment, index):
        global sfile
        if type=='C_PUSH':
            if segment in ('argument','local'):
                if segment=='argument':
                    option='ARG'
                elif segment=='local':
                    option='LCL'
                commandAsm='@'+index+'\n'+'D=A\n'+\
                     '@'+option+'\n'+'A=M+D\n'+'D=M\n'+\
                     '@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            elif segment=='constant':
                commandAsm='@'+index+'\n'+'D=A\n'+'@SP\n'+\
                    'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            elif segment=='temp':
                commandAsm='@'+str(5+int(index))+'\n'+'D=M\n'+'@SP\n'+\
                    'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            elif segment in ('this','that'):
                if segment=='this':
                    option='THIS'
                elif segment=='that':
                    option='THAT'
                commandAsm='@'+index+'\n'+'D=A\n'+'@'+option+'\n'+'A=M+D\n'+\
                    'D=M\n'+'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n' # same as argument and local solution
            elif segment=='pointer':
                if index=='0':
                    option='THIS'
                else:
                    option='THAT'
                commandAsm='@'+option+'\n'+'D=M\n'+'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            elif segment=='static':
                prefix=sfile.split('.')[0]
                option=prefix+'.'+index
                commandAsm='@'+option+'\n'+'D=M\n'+'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            self.f_output.write(commandAsm)
        elif type=='C_POP':
            if segment in ('argument','local','this','that'):
                if segment=='argument':
                    option='ARG'
                elif segment=='local':
                    option='LCL'
                elif segment=='this':
                    option='THIS'
                elif segment=='that':
                    option='THAT'
                commandAsm='@'+index+'\n'+'D=A\n'+\
                    '@'+option+'\n'+'A=M+D\n'+'D=A\n'+\
                    '@R13\n'+'M=D\n'+'@SP\n'+'A=M-1\n'+\
                    'D=M\n'+'@R13\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M-1\n'
            elif segment=='temp':
                commandAsm='@SP\n'+'A=M-1\n'+'D=M\n'+'@'+str(5+int(index))+'\n'+\
                    'M=D\n'+'@SP\n'+'M=M-1\n'
            elif segment=='pointer':
                    if index=='0':
                        option='THIS'
                    else:
                        option='THAT'
                    commandAsm='@'+option+'\n'+'D=A\n'+\
                    '@R13\n'+'M=D\n'+'@SP\n'+'A=M-1\n'+\
                    'D=M\n'+'@R13\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M-1\n'
            elif segment=='static':
                prefix=sfile.split('.')[0]
                option=prefix+'.'+index
                commandAsm='@SP\n'+'A=M-1\n'+'D=M\n'+'@'+option+'\n'+\
                    'M=D\n'+'@SP\n'+'M=M-1\n'

            self.f_output.write(commandAsm)

if __name__=='__main__':
    path=os.path.dirname(os.path.abspath(__file__))
    file=sys.argv[1]
    ofilename=file.split('.')[0]+'.asm'
    if '.vm' not in file:
        #if the argument is a file, list all the vm files 
        allFiles=os.listdir(path+'\\'+file)
        vmFiles=[]
        for f in allFiles:
            if '.vm' in f:
                vmFiles.append(f)
        filenames=vmFiles
    else:
        filenames=[file]

    if len(filenames)==1:
        codeWriter=CodeWriter(path+'\\'+ofilename)
    else:
        path=path+'\\'+file
        codeWriter=CodeWriter(path+'\\'+ofilename)

    for sfile in filenames:
        parser=Parser(path+'\\'+sfile)
        while parser.advance():
            commandType=parser.commandType()
            arg1=parser.arg1()
            arg2=parser.arg2()
            if commandType=='C_ARITHMETIC':
                codeWriter.writeArithmetic(arg1)
            elif commandType in ('C_PUSH','C_POP'):
                codeWriter.writePushPop(commandType,arg1,arg2)
            elif commandType=='C_LABLE':
                labelname=f_name+'$'+arg1
                codeWriter.writeLable(labelname)
            elif commandType=='C_GOTO':
                labelname=f_name+'$'+arg1
                codeWriter.writeGoto(labelname)
            elif commandType=='C_IF':
                labelname=f_name+'$'+arg1
                codeWriter.writeIf(labelname)
            elif commandType=='C_FUNCTION':
                f_name=arg1
                codeWriter.writeFunction(arg1,arg2)
            elif commandType=='C_CALL':
                codeWriter.writeCall(arg1,arg2)
            elif commandType=='C_RETURN':
                codeWriter.writeReturn()
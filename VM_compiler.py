import os
import sys
import string
class JackTokenizer(object):
    keywords=['class','constructor','function','method','field',\
        'static','var','int','char','boolean','void','true',\
        'false','null','this','let','do','if','else','while',\
        'return']
    symbols=['{','}','(',')','[',']','.',',',';','+','-',\
        '*','/','&','|','<','>','=','~']
    integerConstant=[str(i) for i in range(10)]

    def __init__(self,file):
        self.f=open(file)
        self.current=None
        self.tokenGenerator=self.hasMoreTokens()


    def hasMoreTokens(self):
        def deal(line):
            part=line
            process=False
            for k in JackTokenizer.keywords:
                if k in part and part.index(k)==0 and part[len(k)]==' ':
                    tokens.append(k)
                    cut=part[len(k):].strip()
                    process=True
                    if cut:
                        deal(cut)
                    break

            if not process:
                for sym in JackTokenizer.symbols:
                    if sym in part and part.index(sym)==0:
                        tokens.append(sym)
                        cut=part[len(sym):].strip()
                        process=True
                        if cut:
                            deal(cut)
                        break
            
            if not process:
                for n in JackTokenizer.integerConstant:
                    if n in part and part.index(n)==0:
                        end=0
                        for index in range(len(part)):
                            if part[index] not in JackTokenizer.integerConstant:
                                end=index
                                break
                        if end==0:
                            end=len(part)
                        tokens.append(part[:end])
                        cut=part[end:].strip()
                        process=True
                        if cut:
                            deal(cut)
                        break

            if not process:
                if part.startswith('"'):
                    end=part.index('"',1)
                    tokens.append(part[:end+1])
                    cut=part[end+1:].strip()
                    process=True
                    if cut:
                        deal(cut)

            # Finally deal with the identifier, example id, 3 representive ways: id/id+operator[+/-/*/]/id(expression)
            if not process:
                indexs=[]
                symbolsPlusSpace=JackTokenizer.symbols[:]
                symbolsPlusSpace.append(' ')
                for sym in symbolsPlusSpace:
                    if sym in part:
                        indexs.append(part.index(sym))
                # Temporarily not support checking space between indentifier and operator: a = 1 + 5
                if indexs:
                    indexs.sort()
                    tokens.append(part[:indexs[0]])
                    cut=part[indexs[0]:].strip()
                    process=True
                    if cut:
                        deal(cut)
                else:
                    tokens.append(part.split()[0])
                    cut=part[len(tokens[-1]):].strip()
                    process=True
                    if cut:
                        deal(cut)

        for line in self.f:
            tokens=[]
            if line.strip() and  line.strip()[0] not in ('/','*'):
                deal(line.strip())
                for token in tokens:
                    if token=='/' and tokens[tokens.index('/')+1]=='/':
                        break
                    self.current=token
                    yield 1
        yield 0

    def advance(self):
        try:
            condition=self.tokenGenerator.next()
        except StopIteration:
            condition=0
        
        if condition:
            return 1
        else:
            return 0

    def tokenType(self):
        if self.current in JackTokenizer.keywords:
            return 'KEYWORD'
        elif self.current in JackTokenizer.symbols:
            return 'SYMBOL'
        elif self.current[0] in JackTokenizer.integerConstant:
            return 'INT_CONST'
        elif self.current.startswith('"'):
            return 'STRING_CONST'
        elif self.current[0] not in range(10) and \
            (self.current[0] in string.letters or self.current=='_'):
            return 'IDENTIFIER'

    # follow the suggested API, seems to be a little bit clumsy
    def keyWord(self):
        if self.tokenType()=='KEYWORD':
            return self.current

    def symbol(self):
        if self.tokenType()=='SYMBOL':
            return self.current
        else:
            return None

    def identifier(self):
        if self.tokenType()=="IDENTIFIER":
            return self.current
        else:
            return None

    def intVal(self):
        if self.tokenType()=='INT_CONST':
            return self.current
        else:
            return None

    def stringVal(self):
        if self.tokenType()=='STRING_CONST':
            return self.current
        else:
            return None

class SymbolTable(object):
    def __init__(self):
        self.classTable={}
        self.table={'next':self.classTable}

    def startSubroutine(self):
        self.table={'next':self.classTable}

    def define(self,name,dtype,kind):

        if kind in ('static', 'field'):
            table=self.table['next']
        else:
            table=self.table

        index=self.varCount(kind)
        table[name]=[dtype,kind]
        table[name].append(str(index))

    def varCount(self,kind):
        if kind in ('static', 'field'):
            table=self.table['next']
        else:
            table=self.table
        index=0
        for i in table.values():
            if str(type(i))!="<type 'dict'>" and i[1]==kind:
                index+=1

        return index

    def kindOf(self,name):

        for i in self.table.keys():
            if i==name:
                return self.table[i][1]

        for j in self.table['next'].keys():
            if j==name:
                return self.table['next'][j][1]

        return None

    def typeOf(self,name):
        for i in self.table.keys():
            if i==name:
                return self.table[i][0]

        for j in self.table['next'].keys():
            if j==name:
                return self.table['next'][j][0]

        return None

    def indexOf(self,name):

        for i in self.table.keys():
            if i==name:
                return self.table[i][2]

        for j in self.table['next'].keys():
            if j==name:
                return self.table['next'][j][2]

        return None


class VMWriter(object):

    def __init__(self,foutput):
        self.f_output=open(foutput,'w+')

    def writePush(self,segment,index):
        self.f_output.write('push '+segment+' '+index+'\n')

    def writePop(self,segment,index):
        self.f_output.write('pop '+segment+' '+index+'\n')

    def writeArithmetic(self,command):
        self.f_output.write(command+'\n')

    def writeLable(self,label):
        self.f_output.write('label '+label+'\n')

    def writeGoto(self,label):
        self.f_output.write('goto '+label+'\n')

    def writeIf(self,label):
        self.f_output.write('if-goto '+label+'\n')

    def writeCall(self,name,nArgs):
        self.f_output.write('call '+name+' '+nArgs+'\n')

    def writeFunction(self,name,nArgs):
        self.f_output.write('function '+name+' '+nArgs+'\n')

    def writeReturn(self):
        self.f_output.write('return\n')

    def close(self):
        self.f_output.close()

class CompilationEngine(object):

    # used to order label
    main=None
    whilenum=0
    ifnum=0
    # used to fix bugs related to parameterlist count. eg. a(identifier)
    cprocess_boolean=False

    def __init__(self,file):
        self.tokenizer=JackTokenizer(file)
        self.token=None
        self.subname=None
        # expression processing tricks, deal with a=b+c
        self.afterequation=False
        self.command=None
        # save kind and index from self.command
        self.skind=None
        self.sindex=None
        # operator reload, if position==1 and self.token='-' return neg
        self.position=0
        # reload '='
        self.inparameter=False
        # fix the return bugs eg. return a; 
        self.return_states=False
        # fix the arguments count bugs, eg. a(x,y,z)
        self.inargument=False
        # fix the array assignment bugs, eg, a[i]=a+b+c
        self.array_assignment=False
        # start to parse
        self.compileClass()
        global className
        global table

    def compileClass(self):

        while self.tokenizer.advance():
            self.token=self.tokenizer.current
            if self.token=='class':
                pass
            elif self.tokenizer.identifier():
                # might implement some codes to check filename==classname
                CompilationEngine.main=self.token
            elif self.tokenizer.symbol():
                pass
            elif self.token in ('static','field'):
                self.compileClassVarDec()
            elif self.token in ('constructor','function','method'):
                self.compileSubroutine()
        vmwriter.close()

    # classVarDec: ('static'|'field') type varname (',',varName);
    # not support the error checking
    def compileClassVarDec(self):
        name=[]
        while True:
            if self.token in ('static','field'):
                kind=self.token
            elif self.token in ('int','char','boolean','void'):
                dtype=self.token
            elif self.token in className:
                dtype=self.token
            elif self.tokenizer.identifier():
                name.append(self.token)
            elif self.token==',':
                self.tokenizer.advance()
                self.token=self.tokenizer.current
                if self.tokenizer.identifier():
                    name.append(self.token)
            elif self.token==';':
                for n in name:
                    table.define(n, dtype, kind)
                return

            if self.tokenizer.advance():
                self.token=self.tokenizer.current
        
    # subroutineDec ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody
    # subroutineBody '{' varDec* statements '}'
    def compileSubroutine(self):
        constructor_boolean=False
        method_boolean=False
        def subroutineBody():
            nArgs=0
            while self.tokenizer.advance():
                self.token=self.tokenizer.current
                if self.token=='{':
                    pass
                elif self.token=='var':
                    self.compileVarDec()
                    nArgs=table.varCount('local')
                else:
                    vmwriter.writeFunction(CompilationEngine.main+'.'+self.subname,str(nArgs))
                    if constructor_boolean:
                        field_count=table.varCount('field')
                        vmwriter.writePush('constant',str(field_count))
                        vmwriter.writeCall('Memory.alloc','1')
                        vmwriter.writePop('pointer','0')
                    elif method_boolean:
                        vmwriter.writePush('argument','0')
                        vmwriter.writePop('pointer','0')
                    self.compileStatements()
                    if self.token=='}':
                        return

        while True:
            table.startSubroutine()
            if self.token=='function':
                pass
            elif self.token=='constructor':
                constructor_boolean=True
            elif self.token=='method':
                method_boolean=True
            elif self.token in ('int','char','boolean','void'):
                return_type=self.token
            elif self.token in className:
                pass
            elif self.tokenizer.identifier():
                self.subname=self.token
            elif self.token=='(':
                if method_boolean:
                    table.define('this','data_class','argument')
                self.compileParameterList()
                if self.token==')':
                    pass
                subroutineBody()
                CompilationEngine.ifnum=0
                CompilationEngine.whilenum=0
                return

            if self.tokenizer.advance():
                self.token=self.tokenizer.current

    # parameterList (type varName (',' type varName*))? 
    def compileParameterList(self):
        name=None
        dtype=None
        while self.tokenizer.advance():
            self.token=self.tokenizer.current
            if self.token==')':
                if name and dtype:
                    table.define(name,dtype,'argument')
                return
            elif self.token in ('int','char','boolean','void'):
                dtype=self.token
            elif self.token in className:
                dtype=self.token
            elif self.tokenizer.identifier():
                name=self.token
            elif self.token==',':
                if name and dtype:
                    table.define(name,dtype,'argument')
                    name=None
                    dtype=None

    def compileVarDec(self):
        name=[]
        while True:
            if self.token=='var':
                kind='local'
            elif self.token in ('int','char','boolean','void'):
                dtype=self.token
            elif self.token in className:
                dtype=self.token
            elif self.tokenizer.identifier():
                name.append(self.token)
            elif self.token==',':
                self.tokenizer.advance()
                self.token=self.tokenizer.current
                if self.tokenizer.identifier():
                    name.append(self.token)
            elif self.token==';':
                for n in name:
                    table.define(n,dtype,kind)
                return

            if self.tokenizer.advance():
                self.token=self.tokenizer.current


    def compileStatements(self):
        # emulate do while structure
        while True:
            if self.token=='let':
                self.compileLet()
            elif self.token=='if':
                self.compileIf()
                # in order to identify else, compileIf reads one more token
                continue
            elif self.token=='while':
                self.compileWhile()
            elif self.token=='do':
                self.compileDo()
            elif self.token=='return':
                self.compileReturn()
            else:
                return

            if self.tokenizer.advance():
                self.token=self.tokenizer.current

    def compileDo(self):
        # finished
        self.compileExpression()
        if self.token==';':
            vmwriter.writePop('temp','0')
            pass
    
    def compileLet(self):
        # finished
        self.compileExpression()
        if self.token==';':
            pass


    def compileWhile(self):
         CompilationEngine.whilenum+=1
         whilenum=CompilationEngine.whilenum
         while self.tokenizer.advance():
            self.token=self.tokenizer.current
            if self.token=='(':
                self.inparameter=True
                self.afterequation=True
                vmwriter.writeLable(self.subname+'w1'+str(whilenum))
                self.compileExpression()
                self.afterequation=False
                self.inparameter=False
                vmwriter.writeArithmetic('not')
                vmwriter.writeIf(self.subname+'w2'+str(whilenum))
                if self.token==')':
                    pass
            elif self.token=='{':
                self.tokenizer.advance()
                self.token=self.tokenizer.current
                self.compileStatements()
                vmwriter.writeGoto(self.subname+'w1'+str(whilenum))
                if self.token=='}':
                    vmwriter.writeLable(self.subname+'w2'+str(whilenum))
                    return

    def compileReturn(self):
        self.afterequation=True
        self.return_states=True
        process_boolean=self.compileExpression()
        if (not process_boolean) and (not CompilationEngine.cprocess_boolean):
            vmwriter.writePush('constant','0')
        if self.token==';':
            vmwriter.writeReturn()
            self.afterequation=False
            self.return_states=False
            CompilationEngine.cprocess_boolean=False
            return
       

    def compileIf(self):
        i=0
        CompilationEngine.ifnum+=1
        ifnum=CompilationEngine.ifnum
        while self.tokenizer.advance():
            self.token=self.tokenizer.current
            if self.token=='(':
                self.inparameter=True
                self.afterequation=True
                self.compileExpression()
                self.afterequation=False
                self.inparameter=False
                vmwriter.writeArithmetic('not')
                vmwriter.writeIf(self.subname+'f1'+str(ifnum))
                if self.token==')':
                    pass
            elif self.token=='{':
                self.tokenizer.advance()
                self.token=self.tokenizer.current
                
                # implement goto L2
                if i==1:
                    vmwriter.writeGoto(self.subname+'f2'+str(ifnum))
                    vmwriter.writeLable(self.subname+'f1'+str(ifnum))
                    i+=1
                else:
                    i+=1

                self.compileStatements()
                if self.token=='}':
                    pass
            elif self.token=='else':
                pass
            else:
                if i==2:
                    vmwriter.writeLable(self.subname+'f2'+str(ifnum))
                else:
                    vmwriter.writeLable(self.subname+'f1'+str(ifnum))
                return


    def compileExpression(self):
        op_cal=['+','-','*','/','&','|','<','>','=']
        opstack=[]
        process_boolean=False
        self.position=0
        while self.compileTerm() or self.token in op_cal:
            process_boolean=True
            self.position+=1
            if self.token=='=' and not self.inparameter:
                self.afterequation=True
            elif self.token in op_cal:
                opstack.append(self.token)
        else:
            for o in opstack:
                if o=='+':
                    vmwriter.writeArithmetic('add')
                elif o=='-':
                    vmwriter.writeArithmetic('sub')
                elif o=='*':
                    vmwriter.writeCall('Math.multiply','2')
                elif o=='/':
                    vmwriter.writeCall('Math.divide','2')
                elif o=='&':
                    vmwriter.writeArithmetic('and')
                elif o=='|':
                    vmwriter.writeArithmetic('or')
                elif o=='<':
                    vmwriter.writeArithmetic('lt')
                elif o=='>':
                    vmwriter.writeArithmetic('gt')
                elif o=='=':
                    vmwriter.writeArithmetic('eq')

            if self.token==';':
                self.afterequation=False
                if self.command:
                    exec self.command
                    # reset the self.command execution argument
                    self.command=None
                    self.skind=None
                    self.sindex=None
                elif self.array_assignment:
                    vmwriter.writePop('temp','1')
                    vmwriter.writePop('pointer','1')
                    vmwriter.writePush('temp','1')
                    vmwriter.writePop('that','0')
                    self.array_assignment=False
                self.position=0



            return process_boolean


    def compileTerm(self):
        op=['+','-','*','/','&','|','<','>','=']
        names=[]

        while self.tokenizer.advance():
            self.token=self.tokenizer.current
            if self.tokenizer.intVal():
                vmwriter.writePush('constant',self.token)
                return 'intergerConstant'
            elif self.tokenizer.stringVal():
                strings=self.token.split('"')[1]
                length=len(strings)
                vmwriter.writePush('constant',str(length))
                vmwriter.writeCall('String.new','1')
                for s in range(length):
                    ascii=ord(strings[s])
                    vmwriter.writePush('constant',str(ascii))
                    vmwriter.writeCall('String.appendChar','2')
                return 'StringConstant'
            elif self.tokenizer.keyWord() in ('true','false','null','this'):
                if self.token=='true':
                    vmwriter.writePush('constant','1')
                    vmwriter.writeArithmetic('neg')
                elif self.token in ('false','null'):
                    vmwriter.writePush('constant','0')
                else:
                    vmwriter.writePush('pointer','0')
                return 'keywordconstant'
            elif self.tokenizer.identifier():
                names.append(self.token)
                kind=table.kindOf(self.token)
                index=table.indexOf(self.token)
                self.tokenizer.advance()
                self.token=self.tokenizer.current
                if self.token=='[':
                    if not self.afterequation:

                        self.afterequation=True
                        self.array_assignment=True

                        self.command=vmwriter.writePush(kind,index)
                        self.compileExpression()
                        vmwriter.writeArithmetic('add')
                        self.afterequation=False
                    else:
                        vmwriter.writePush(kind,index)
                        self.compileExpression()
                        vmwriter.writeArithmetic('add')
                        vmwriter.writePop('pointer','1')
                        vmwriter.writePush('that','0')
                    if self.token==']':
                        return 'Array'
                elif self.token=='(':
                    self.afterequation=True
                    self.inargument=True
                    if names[0] in className:
                        n=self.compileExpressionList()
                        vmwriter.writeCall('.'.join(names),str(n))
                    elif len(names)==1:
                        # method call within the same class
                        vmwriter.writePush('pointer','0')
                        n=self.compileExpressionList()
                        n+=1
                        vmwriter.writeCall(CompilationEngine.main+'.'+names[0],str(n))
                    else:
                        if m_kind=='field':
                            m_kind='this'
                        vmwriter.writePush(m_kind,m_index)
                        n=self.compileExpressionList()
                        n+=1
                        type=table.typeOf(names[0])
                        # ! not check the method in corresponding class
                        vmwriter.writeCall(type+'.'+names[1],str(n))
                    self.afterequation=False
                    self.inargument=False
                    # confirm the return value is ')'
                    return 'SubroutineCall'
                elif self.token=='.':
                    # deal with eg. a.j+1
                    '''
                    if names[0] not in className:
                        vmwriter.writePush(kind,index)
                        vmwriter.writePop('pointer','0')'''
                    m_kind=kind
                    m_index=index
                    continue
                else:
                    if not self.afterequation:
                        self.skind=kind
                        self.sindex=index
                        # constructor set its copy
                        if kind=='field':
                            self.command="vmwriter.writePop('this',self.sindex)"
                        else:
                            self.command="vmwriter.writePop(self.skind,self.sindex)"
                    else:
                        if kind=='field':
                            vmwriter.writePush('this',index)
                        else:
                            vmwriter.writePush(kind,index)
                        if self.inargument or self.return_states:
                            CompilationEngine.cprocess_boolean=True
                    return False
 
            elif self.token=='(':
                self.compileExpression()
                if self.token==')':
                    pass
                return True
            # unary operator and token '-' reload
            elif self.token in ('-','~') and self.position==0:
                unaryOp=self.token
                if self.compileTerm():
                    pass
                # if(~x):
                elif self.token==')':
                    if unaryOp=='-':
                        vmwriter.writeArithmetic('neg')
                    elif unaryOp=='~':
                        vmwriter.writeArithmetic('not')
                    return False

                if unaryOp=='-':
                    vmwriter.writeArithmetic('neg')
                elif unaryOp=='~':
                    vmwriter.writeArithmetic('not')
                return True
            else:
                return False

    
    def compileExpressionList(self):
        n=0
        while True:
            process_boolean=self.compileExpression()
            if process_boolean or CompilationEngine.cprocess_boolean:
                CompilationEngine.cprocess_boolean=False
                n+=1
            if self.token==',':
                self.position=0
                continue
            elif self.token==')':
                return n

if __name__=='__main__':
    className=[]
    path=os.path.dirname(os.path.abspath(__file__))
    file=sys.argv[1]
    jackFiles=[]
    if '.jack' not in file:
        allFiles=os.listdir(path+'\\'+file)
        for f in allFiles:
            if '.jack' in f:
                jackFiles.append(f)
                className.append(f.split('.')[0])
            elif '.vm' in f:
                className.append(f.split('.')[0])
    else:
        jackFiles.append(file)
        className.append(file.split('.')[0])

    if '.jack' in file:
        f_output=path+'\\'+file.split('.')[0]+'.vm'
        f_input=path+'\\'+file
        table=SymbolTable()
        vmwriter=VMWriter(f_output)
        compilationEngine=CompilationEngine(f_input)
    else:
        path=path+'\\'+file
        for ofile in jackFiles:
            f_output=path+'\\'+ofile.split('.')[0]+'.vm'
            f_input=path+'\\'+ofile
            table=SymbolTable()
            vmwriter=VMWriter(f_output)
            compilationEngine=CompilationEngine(f_input)

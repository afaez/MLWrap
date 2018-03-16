import importlib
import json
from pase.reflect.reflector import traverse_package, fullname
import pase.config
import os
import re


def write_into_box(msg, fp, boxchar = '-', padchar = ' ', paddingrepeat = 2):

    def repeat_to_length(string_to_expand, length):
        return (string_to_expand * (int(length/len(string_to_expand))+1))[:length]

    paddingrepeat = repeat_to_length(padchar, paddingrepeat)
    comment = paddingrepeat + " {msg} ".format(msg=msg) + paddingrepeat
    wrapcomment = repeat_to_length(boxchar,len(comment))
    print("\n\n#"+wrapcomment +"#",file=fp)
    print("#" + comment + "#",file=fp)
    print("#" + wrapcomment+"#\n",file=fp)

def getjavaSource_OptionsPredicate():
    return """package de.upb.crc901.mlplan.evaluablepredicates.mlplan.{package1}.{package2}.{classname};

    import java.util.Arrays;
    import java.util.List;

    import de.upb.crc901.mlplan.evaluablepredicates.mlplan.OptionsPredicate;
    /*
    {doc}
    */
    public class {javaClassName} extends OptionsPredicate {{
        
        private static List<Object> validValues = Arrays.asList(new Object[]{{}});

        @Override
        protected List<? extends Object> getValidValues() {{
            return validValues;
        }}
    }}
    """
def getjavaSource_NumericalOption():
    return """
    package de.upb.crc901.mlplan.evaluablepredicates.mlplan.{package1}.{package2}.{classname};
    /*
    {doc}
    */

    import de.upb.crc901.mlplan.evaluablepredicates.mlplan.NumericRangeOptionPredicate;

    public class {javaClassName} extends NumericRangeOptionPredicate {{
        
        @Override
        protected double getMin() {{
            return 1;
        }}

        @Override
        protected double getMax() {{
            return 1;
        }}

        @Override
        protected int getSteps() {{
            return -1;
        }}

        @Override
        protected boolean needsIntegers() {{
            return {needsInt};
        }}
    }}
    """

def getjavaSource_BoolOption():
    return """package de.upb.crc901.mlplan.evaluablepredicates.mlplan.{package1}.{package2}.{classname};

    import java.util.Arrays;
    import java.util.List;

    import de.upb.crc901.mlplan.evaluablepredicates.mlplan.OptionsPredicate;
    /*
    {doc}
    */
    public class {javaClassName} extends OptionsPredicate {{
        
        private static List<Object> validValues = Arrays.asList(new Object[]{{"true", "false"}});

        @Override
        protected List<? extends Object> getValidValues() {{
            return validValues;
        }}
    }}
    """

def write_skript(predicatefilename = "predicates.txt", scriptname = "script.txt", package1 = "pp", package2 = "as", configsupertype = "sklearn.cross_decomposition.CCA"):
    classpath = "sklearn.ensemble.RandomForestClassifier"
    genfolder = "../../_gen/"
    predicatefilename = genfolder + predicatefilename
    scriptname = genfolder + scriptname
    javasrc = "../../_gen/mlplan/"
    dirsrc = javasrc + "{package1}/{package2}/{classname}/"
    filesrc = "{javaClassName}.java"

    script = open(scriptname,mode="w")
    allPredicates = {}
    dic = {}
    import sys
    write_into_box("PP Classes", fp = sys.stdout)
    for classpath in pase.config.lookup.allsubtypes(configsupertype):
        print(classpath+ ":String")
        pckgSplit = classpath.split(".")
        clazz = traverse_package(pckgSplit)
        obj = clazz()
        params = obj.get_params()
        classname = pckgSplit[-1]

        alldocs = obj.__doc__.split("----------")
        i = 1
        while (i -1) < len(alldocs) and (not alldocs[i-1].strip().endswith("Parameters")):
            i += 1
        if i >= len(alldocs):
            # print("coultn't get doc from " + classpath)
            paradocs =""
        else:
            #print("doc from " + classpath + "\n " + alldocs[i])
            paradocs = alldocs[i]

        optiondocs = {}
        for methodname in params.keys():
            dic[methodname] = None
            startpos = paradocs.find("    " + methodname)
            endpos = len(paradocs)
            for othermethod in params.keys():
                if othermethod == methodname:
                    continue
                place =  paradocs.find("    " + othermethod)
                if place > startpos and place < endpos:
                    endpos = place
            optiondocs[methodname] = paradocs[startpos:endpos]



        planLine = "sl_{classname};\t\t\tslChoose_{package1}_{package2}(config); config; ; ; associateWithAssertion('{classpath}',config)".format(classname=classname, classpath=classpath, package1=package1, package2=package2)
        # wekaBF;	wekaChooseSubsetSearcher(config); config; ; ; associateWithAssertion('weka.attributeSelection.BestFirst',config)

        firstLine = "sl_{classname};\t\t\tslConfigure_{package1}_{package2}(config); config,pipe; associated('{classpath}',config); ; de.upb.crc901.mlplan.services.MLPipelinePlan:addAttributeSelection(config,'{classpath}',pipe)".format(classname=classname, classpath=classpath, package1=package1, package2=package2)
        #wekaBF;	configureWekaSearcher(config, fs); config,fs,oList,oArray; associated('weka.attributeSelection.BestFirst',config) ; ; 
        lines = []
        predicates = []
        allPredicates[classname] = predicates
        for methodname in params.keys():

            if isinstance(params[methodname], None.__class__):
                continue
            # generate grammar
            # create option line
            lineName = "sl-{classname}-set-{methodname}".format(classname=classname,methodname=methodname)

            javaClassName = "OptionsFor_{classname}_{methodname}".format(classname=classname, methodname=methodname)

            optionLine = "{linename};\t\t{linename}(c,p); c,p; ; ;  noop()".format(linename=lineName)

            lines.append(optionLine)

            optionLine = "{linename};\t\t{linename}(c,p); c,p,t; ; {javaclass}(t); de.upb.crc901.mlplan.services.MLPipelinePlan:addOptions(c,p,'-{methodname}', t)".format(linename=lineName, javaclass=javaClassName, methodname=methodname)

            # append option line to the list and add -> to the first line
            lines.append(optionLine)
            firstLine += "\t->\t{lineName}(config,pipe)".format(lineName=lineName)


            # add predicates


            javaPath = "de.upb.crc901.mlplan.evaluablepredicates.mlplan.{package1}.{package2}.{classname}.{javaClassName}".format(classname=classname, javaClassName = javaClassName, package1=package1, package2=package2)

            predicates.append("{javaClassName} = {javaPath}".format(javaPath=javaPath, javaClassName=javaClassName))

            # generate java predicate file:
            type_ = params[methodname]
            needsString = False
            needsBool = False
            needsInt = "false"
            if isinstance(type_, str):
                needsString = True
            if isinstance(type_, bool):
                needsBool = True
            elif isinstance(type_, int):
                needsInt = "true"


            # calculate docstring:
            optionsdoc = optiondocs[methodname]


            # write java source
            directorypath = dirsrc.format(classname=classname, package1=package1, package2 = package2)
            if not os.path.exists(directorypath):
                os.makedirs(directorypath)

            methodsrc = directorypath + filesrc.format(javaClassName=javaClassName)
            javafile = open(methodsrc, mode = "w")
            if needsString:
                source = getjavaSource_OptionsPredicate().format(doc = optionsdoc, javaClassName=javaClassName, classname=classname, package1=package1, package2=package2)
            elif needsBool:
                source = getjavaSource_BoolOption().format(doc = optionsdoc, javaClassName=javaClassName, classname=classname, package1=package1, package2=package2)
            else:
                source = getjavaSource_NumericalOption().format(doc = optionsdoc, javaClassName=javaClassName, needsInt=needsInt, classname=classname, package1=package1, package2=package2)
            print(source, file=javafile)
            javafile.close()

        # Write grammar 
        write_into_box(classname, script)
        print(planLine, file=script)
        print(firstLine,file=script)

        write_into_box("Option Configuration for {classname}".format(classname=classname), script, boxchar='-', paddingrepeat= 4)
        for optionLine in lines:
            print(optionLine,file=script)


    script.close()

    predicates = open(predicatefilename, mode="w")
    for classname in allPredicates:


        #write_into_box(classname, predicates)

        for predicate in allPredicates[classname]:
            print(predicate, file=predicates)

    predicates.close()

    write_into_box("options for pp", fp = sys.stdout)
    for o in dic:
        print("-"+o+ ":String")




if __name__ == "__main__": 
    write_skript()
    

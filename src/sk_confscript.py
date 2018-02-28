import importlib
import json
from pase.reflect.reflector import traverse_package, fullname
import pase.config
import os

script = open("script.txt",mode="w+")

classpath = "sklearn.ensemble.RandomForestClassifier"

def repeat_to_length(string_to_expand, length):
    return (string_to_expand * (int(length/len(string_to_expand))+1))[:length]

def write_into_box(msg, fp):

    
    comment = "### {msg} ###".format(msg=msg)
    wrapcomment = repeat_to_length("#",len(comment))
    print("\n\n"+wrapcomment,file=fp)
    print(comment,file=fp)
    print(wrapcomment+"\n",file=fp)


javasrc = "../../mlplan/"

dirsrc = javasrc + "{classname}/"
filesrc = "{javaClassName}.java"

allPredicates = {}

javasourceStringOptions = """package de.upb.crc901.mlplan.evaluablepredicates.mlplan.{classname};

import java.util.Arrays;
import java.util.List;

import de.upb.crc901.mlplan.evaluablepredicates.mlplan.OptionsPredicate;

public class {javaClassName} extends OptionsPredicate {{
	
	private static List<Integer> validValues = Arrays.asList(new Integer[]{{1, 2, 3}});

	@Override
	protected List<? extends Object> getValidValues() {{
		return validValues;
	}}
}}
"""
javasourceIntOptions = """
package de.upb.crc901.mlplan.evaluablepredicates.mlplan.{classname};

import de.upb.crc901.mlplan.evaluablepredicates.mlplan.NumericRangeOptionPredicate;

public class {javaClassName} extends NumericRangeOptionPredicate {{
	
	@Override
	protected double getMin() {{
		return 0;
	}}

	@Override
	protected double getMax() {{
		return 3;
	}}

	@Override
	protected int getSteps() {{
		return 1;
	}}

	@Override
	protected boolean needsIntegers() {{
		return {needsInt};
	}}
}}
"""


for classpath in pase.config.lookup.allsubtypes("$base_sk_classifier_config$"):
    pckgSplit = classpath.split(".")
    clazz = traverse_package(pckgSplit)
    obj = clazz()
    params = obj.get_params()
    classname = pckgSplit[-1]

    #0 classname
    #1 classpath
    firstLine = "sl_{classname};\t\t\tslCreateBaseClassifier(c); c,p; ; ; de.upb.crc901.services.mlpipeline.MLPipelinePlan:setClassifier(c,'{classpath}',p)".format(classname=classname, classpath=classpath)

    lines = []
    predicates = []
    allPredicates[classname] = predicates
    #AllowedTreeDepthForRandomForests = de.upb.crc901.mlplan.evaluablepredicates.mlplan.randomforest.AllowedTreeDepthForRandomForests

    for methodname in params.keys():

        if isinstance(params[methodname], None.__class__):
            continue

        # create option line
        lineName = "sl-{classname}-set-{methodname}".format(classname=classname,methodname=methodname)

        javaClassName = "OptionsFor_{classname}_{methodname}".format(classname=classname, methodname=methodname)


        optionLine = "{linename};\t\t{linename}(c,p); c,p,t; ; {javaclass}(t); de.upb.crc901.services.mlpipeline.MLPipelinePlan:addOptions(c,p,'-{methodname}', t)".format(linename=lineName, javaclass=javaClassName, methodname=methodname)

        # append option line to the list and add -> to the first line
        lines.append(optionLine)
        firstLine += "\t->\t{lineName}(c,p)".format(lineName=lineName)


        # add predicates


        javaPath = "de.upb.crc901.mlplan.evaluablepredicates.mlplan.{classname}.{javaClassName}".format(classname=classname, javaClassName = javaClassName)

        predicates.append("{javaClassName} = {javaPath}".format(javaPath=javaPath, javaClassName=javaClassName))

        # generate java predicate file:
        type_ = params[methodname]
        needsString = False
        needsInt = "false"
        if isinstance(type_, str):
            needsString = True
        elif isinstance(type_, int):
            needsInt = "true"

        methodsrc = (dirsrc+filesrc).format(classname=classname, javaClassName=javaClassName)
        if not os.path.exists(dirsrc.format(classname=classname)):
            os.makedirs(dirsrc.format(classname=classname))
        javafile = open(methodsrc, mode = "w+")
        if needsString:
            source = javasourceStringOptions.format(javaClassName=javaClassName, classname=classname)
        else:
            source = javasourceIntOptions.format(javaClassName=javaClassName, needsInt=needsInt, classname=classname)
        print(source, file=javafile)
        javafile.close()

    
    write_into_box(classname, script)
    print(firstLine,file=script)
    comment = "\n### Options Predicates for {classname} ###\n".format(classname=classname)
    print(comment,file=script)
    for optionLine in lines:
        print(optionLine,file=script)


script.close()

predicates = open("predicates.txt",mode="w+")
for classname in allPredicates:


    #write_into_box(classname, predicates)

    for predicate in allPredicates[classname]:
        print(predicate, file=predicates)

predicates.close()




# estimators = all_estimators()
# dic = {}
# for cutClassName in pase.config.lookup.allsubtypes("$base_sk_classifier_config$"):
#     # cutClassName = str(class_)[8:len(str(class_))-2]
#     # if(not pase.config.lookup.class_known(cutClassName)):
#     #     print("skipping class: " + cutClassName)
#     #     continue
#     pckgSplit = cutClassName.split(".")
#     clazz = traverse_package(pckgSplit)
#     try:
#         call = cutClassName + "("
#         obj = clazz()
#         params = obj.get_params()

#         first = True
#         for entry in params:
#             if entry not in dic:
#                 dic[entry] = {"classes":[], "type":""}
#             dic[entry]["classes"].append(cutClassName)
#             if isinstance(params[entry], None.__class__):
#                 dic[entry]["type"] = "complex/multitype"
#             else:
#                 type_ = fullname(params[entry])
#                 dic[entry]["type"] = type_
#         #print(cutClassName + ":String")

#     except:
#         pass
#         # print("Could not instantiate", cutClassName)

# f = open("out.txt", mode='w')
# for option in dic:
#     print("#  Classes: " + (", ".join(dic[option]["classes"])), file=f)
#     print("#  Type: " + dic[option]["type"], file=f)
#     print("-" + option + ":String\n", file=f)
# f.close()
# f = open("sk_params.json", mode='w')
# json.dump(dic, f, indent=4, sort_keys=True)
# f.close()
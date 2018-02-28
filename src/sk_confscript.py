from sklearn.utils.testing import all_estimators
import importlib
import json
from pase.reflect.reflector import traverse_package, fullname
import pase.config

estimators = all_estimators()
dic = {}
for cutClassName in pase.config.lookup.allsubtypes("$base_sk_classifier_config$"):
    # cutClassName = str(class_)[8:len(str(class_))-2]
    # if(not pase.config.lookup.class_known(cutClassName)):
    #     print("skipping class: " + cutClassName)
    #     continue
    pckgSplit = cutClassName.split(".")
    clazz = traverse_package(pckgSplit)
    try:
        call = cutClassName + "("
        obj = clazz()
        params = obj.get_params()

        first = True
        for entry in params:
            if entry not in dic:
                dic[entry] = {"classes":[], "type":""}
            dic[entry]["classes"].append(cutClassName)
            if isinstance(params[entry], None.__class__):
                dic[entry]["type"] = "complex/multitype"
            else:
                type_ = fullname(params[entry])
                dic[entry]["type"] = type_
        #print(cutClassName + ":String")

    except:
        pass
        # print("Could not instantiate", cutClassName)

f = open("out.txt", mode='w')
for option in dic:
    print("#  Classes: " + (", ".join(dic[option]["classes"])), file=f)
    print("#  Type: " + dic[option]["type"], file=f)
    print("-" + option + ":String\n", file=f)
f.close()
# f = open("sk_params.json", mode='w')
# json.dump(dic, f, indent=4, sort_keys=True)
# f.close()
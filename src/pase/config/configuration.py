import os
import pase.constants.error_msg as error
import logging
import json

def resolve_inheritance(config):
    """Resolves the 'extends' attribute from classes.
        A class can define an 'extends' array filled with other classes from the configuration.
        The class will inherit all the attributes from the other classes. 
    """ 
    resolvedClasses = list()
    unresolvedClasses = list()
    for classpath in config:
        if classpath in resolvedClasses:
            # this was resolved by a previous iteration. 
            continue
        else:
            # resolve the one class
            classconfig = config[classpath]
            unresolvedClasses.append(classpath)
            resolve_inheritance_inner(config, classconfig, unresolvedClasses, resolvedClasses)
            unresolvedClasses.remove(classpath)
            resolvedClasses.append(classpath)


    
def resolve_inheritance_inner(baseconfig, classconfig,  unresolved, resolved):
    """ Resolves the inheritance of the given class-config by recursively resolving the class-configs which are extended by the given class-config.
    By the end of the method all the extended classes will be contained in the resolved set. 

    Some examples: 

    If A extends B, because B doesn't inherit anything, all of the attributes from B are immediately added to A. Now A and B are resolved.

    If A extends B and B extends C, first B needs to be resolved. 
    So 'A' will be added to 'unresolved' and resolveInheritance(B, {A}, {})  will be called.
    Afterwards 'B' will be added to resolved and it's attributes will be added to A.

    If A extends B and B extends C and C extends A, there is a circled dependency.
    After one recursion steps, resolveInheritance(C, {A, B}, {}) will be called. Then because 'C' extends a class from the unresolved set a runtime exception will be thrown.

    @inheritSet Set of classes that are inheriting from this classes configuration. 
    If the given classconfig inherits from one of the classes in this set a RuntimeException will be thrown to indicate that a circled dependency has occurred.
    """
    if "extends" in classconfig:
        # Go once through the array to check for circled dependency.
        for superconfig in classconfig["extends"]:
            if superconfig in unresolved:
                raise ValueError("Circled dependency in Inheritance in ClassesConfig:"
                            + " The given class and class: " + superconfig + " extend from each other.")

        for superclasspath in classconfig["extends"]:
            superconfig = baseconfig[superclasspath]
            if superclasspath not in resolved:
                # first resolve the base config
                unresolved.append(superclasspath)
                resolve_inheritance_inner(baseconfig, superconfig, unresolved, resolved)
                resolved.add(superclasspath)
                unresolved.remove(superclasspath)
            # now add everything from super config to this class config
            for fieldname in superconfig:
                if "extends" == fieldname:
                    # don't want to change inheritance or else funny things happen when calling resolveInheritances twice.
                    continue
                
                superfield = superconfig[fieldname]
                extended = False # flag that indicates if extension is complete
                if fieldname in classconfig:
                    basefield = classconfig[fieldname]
                    if isinstance(basefield, list) and isinstance(superfield, list):
                        extended = True
                        basefield.extend(superfield)
                    elif isinstance(basefield, dict) and isinstance(superfield, dict):
                        extended = True
                        basefield.update(superfield)

                if not extended:
                    classconfig[fieldname] = superfield


# Get the path to the configurations
app_path = os.getenv("PASE_CONFIG_PATH")
if app_path is None:
    app_path = ".."
    #raise EnvironmentError(error.const.environment_variable_is_not_set.format("PASE_CONFIG_PATH"))
# load classes.json
_classes_file = open(app_path + "/conf/classes.json")
CLASSES_DICT = json.load(_classes_file)
_classes_file.close()

resolve_inheritance(CLASSES_DICT)
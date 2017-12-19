import jsonpickle

# Use plainlibs classes to serialize complex class hierarchy:

from plainlib.package1.b import A, B

b1 = B(1,2)
b2 = B(3,4)

a1 = A(b1)

jstring1 = jsonpickle.encode(a1) 

print(jstring1)
# Prints: {"py/object": "plainlib.package1.b.A", "ref": {"py/object": "plainlib.package1.b.B", "a": 1, "b": 2}}


a2 = A(None)
a2.ref = a2  #let a2 reference itself.

jstring2 = jsonpickle.encode(a2)

print(jstring2)
# Prints: {"py/object": "plainlib.package1.b.A", "ref": {"py/id": 0}} 

a3 = jsonpickle.decode(jstring2)

assert a3 == a3.ref


# Use a neural network from scikit learn:

from sklearn.neural_network import MLPClassifier

# Register jsonpickle_numpy handler to allow support for numpy.
import jsonpickle.ext.numpy as jsonpickle_numpy
jsonpickle_numpy.register_handlers()

X = [[0., 0.], [1., 1.]]
y = [0, 1]
clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5, 2), random_state=1)
clf.fit(X, y)

jstring3 = jsonpickle.encode(clf)

# print(jstring3) uncomment to see a huge wall of json text in the output.

clf_dup = jsonpickle.decode(jstring3)


# Assert that the restored model predicts like the initial one.
assert (clf_dup.predict([[2., 2.], [-1., -2.]]) == clf.predict([[2., 2.], [-1., -2.]])).all()

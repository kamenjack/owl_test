from owlready2 import *

onto = get_ontology("http://test.org/onto.owl")

with onto:
    class Department(Thing):
        pass

    class System(Thing):
        pass

    class Symptom(Thing):
        pass

    class belongsTo(ObjectProperty):
        domain = [System]
        range = [Department]

    class hasSymptom(ObjectProperty):
        domain = [System]
        range = [Symptom]

    dept1 = Department("Mechanical")
    system1 = System("Communication")
    symptom1 = Symptom("PTC")
    system1.belongsTo = [dept1]
    system1.hasSymptom = [symptom1]

    dept2 = Department("Engineering")
    system2 = System("Track_Structures")
    symptom2 = Symptom("ROW_NDF")
    system2.belongsTo = [dept2]
    system2.hasSymptom = [symptom2]

    system3 = System("Lavatories_Toilets")
    symptom3 = Symptom("To_Be_Determined")
    system3.belongsTo = [dept1]
    system3.hasSymptom = [symptom3]

onto.save(file="example.rdf", format="rdfxml")
onto.save(file="example.owl", format="rdfxml")


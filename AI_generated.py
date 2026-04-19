import pandas as pd
import re
from owlready2 import *

# 1. Read CSV
csv_file = "LTS Delays Codes with ID (1).csv"
df = pd.read_csv(csv_file)

# 2. Helper function
def safe_name(value):
    value = str(value).strip()
    value = value.replace("&", "and")
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s/-]+", "_", value)
    if not value:
        value = "Unnamed"
    if value[0].isdigit():
        value = "_" + value
    return value

# 3. Create ontology
onto = get_ontology("http://test.org/lts_delay_ontology.owl")

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

department_dict = {}
system_dict = {}
symptom_dict = {}

for _, row in df.iterrows():
    dept_name = str(row["Dept/Roll-up Name"]).strip()
    system_name = str(row["System Name"]).strip()
    symptom_name = str(row["Symptom/Component Name"]).strip()

    # Department
    if dept_name not in department_dict:
        department_instance = Department(f"Department_{safe_name(dept_name)}")
        department_instance.label = [dept_name]
        department_dict[dept_name] = department_instance
    else:
        department_instance = department_dict[dept_name]

    # System
    system_key = (dept_name, system_name)
    if system_key not in system_dict:
        system_instance = System(f"System_{safe_name(dept_name)}_{safe_name(system_name)}")
        system_instance.label = [system_name]
        system_instance.belongsTo = [department_instance]
        system_dict[system_key] = system_instance
    else:
        system_instance = system_dict[system_key]

    # Symptom
    symptom_key = (dept_name, system_name, symptom_name)
    if symptom_key not in symptom_dict:
        symptom_instance = Symptom(
            f"Symptom_{safe_name(dept_name)}_{safe_name(system_name)}_{safe_name(symptom_name)}"
        )
        symptom_instance.label = [symptom_name]
        symptom_dict[symptom_key] = symptom_instance
    else:
        symptom_instance = symptom_dict[symptom_key]

    if symptom_instance not in system_instance.hasSymptom:
        system_instance.hasSymptom.append(symptom_instance)

onto.save(file="lts_delay_ontology.owl", format="rdfxml")


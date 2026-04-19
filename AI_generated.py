import pandas as pd
import re
from owlready2 import *

# 1. Read CSV
csv_file = "LTS Delays Codes with ID (1).csv"
df = pd.read_csv(csv_file)

# 2. Helper function: convert text into safe OWL names
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

# 4. Dictionaries for deduplication
department_dict = {}
system_dict = {}
symptom_dict = {}

# 5. Build ontology
for _, row in df.iterrows():
    dept_name = str(row["Dept/Roll-up Name"]).strip()
    system_name = str(row["System Name"]).strip()
    symptom_name = str(row["Symptom/Component Name"]).strip()

    # Department deduplication
    department_key = dept_name
    if department_key not in department_dict:
        department_instance = Department(f"Department_{safe_name(dept_name)}")
        department_dict[department_key] = department_instance
    else:
        department_instance = department_dict[department_key]

    # System deduplication
    system_key = (dept_name, system_name)
    if system_key not in system_dict:
        system_instance = System(f"System_{safe_name(dept_name)}_{safe_name(system_name)}")
        system_instance.belongsTo = [department_instance]
        system_dict[system_key] = system_instance
    else:
        system_instance = system_dict[system_key]

    # Symptom deduplication
    symptom_key = (dept_name, system_name, symptom_name)
    if symptom_key not in symptom_dict:
        symptom_instance = Symptom(
            f"Symptom_{safe_name(dept_name)}_{safe_name(system_name)}_{safe_name(symptom_name)}"
        )
        symptom_dict[symptom_key] = symptom_instance
    else:
        symptom_instance = symptom_dict[symptom_key]

    # Relation: System -> Symptom
    if symptom_instance not in system_instance.hasSymptom:
        system_instance.hasSymptom.append(symptom_instance)

# 6. Save ontology
onto.save(file="lts_delay_ontology.owl", format="rdfxml")
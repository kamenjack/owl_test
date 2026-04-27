import pandas as pd
import re
import types
from owlready2 import *

# =========================
# 1. Read CSV
# =========================
csv_file = "LTS Delays Codes with ID (1).csv"
df = pd.read_csv(csv_file)

# =========================
# 2. Helper function
# =========================
def safe_name(value):
    value = str(value).strip()
    value = value.replace("&", "and")
    value = re.sub(r"[^\w\s/-]", "", value)
    value = re.sub(r"[\s/-]+", "_", value)
    if not value:
        value = "Unnamed"
    if value[0].isdigit():
        value = "_" + value
    return value

# =========================
# 3. Create ontology
# =========================
onto = get_ontology("http://test.org/lts_delay_class_based.owl")

with onto:
    class Department(Thing):
        pass

    class System(Thing):
        pass

    class Symptom(Thing):
        pass

    class has_System(ObjectProperty):
        domain = [Department]
        range = [System]

    class has_Symptom(ObjectProperty):
        domain = [System]
        range = [Symptom]

# =========================
# 4. Store created classes
# =========================
department_classes = {}
system_classes = {}
symptom_classes = {}

department_to_systems = {}
system_to_symptoms = {}

# =========================
# 5. Create classes from CSV
# =========================
for _, row in df.iterrows():
    dept_name = str(row["Dept/Roll-up Name"]).strip()
    system_name = str(row["System Name"]).strip()
    symptom_name = str(row["Symptom/Component Name"]).strip()

    # internal names: add prefixes to avoid collisions
    dept_class_name = f"Dept_{safe_name(dept_name)}"
    system_class_name = f"Sys_{safe_name(system_name)}"
    symptom_class_name = f"Sym_{safe_name(symptom_name)}"

    # ---- Department subclass ----
    if dept_name not in department_classes:
        department_class = types.new_class(
            dept_class_name,
            (onto.Department,)
        )
        department_class.label = [dept_name]
        department_classes[dept_name] = department_class
        department_to_systems[dept_name] = set()
    else:
        department_class = department_classes[dept_name]

    # ---- System subclass ----
    if system_name not in system_classes:
        system_class = types.new_class(
            system_class_name,
            (onto.System,)
        )
        system_class.label = [system_name]
        system_classes[system_name] = system_class
        system_to_symptoms[system_name] = set()
    else:
        system_class = system_classes[system_name]

    # ---- Symptom subclass ----
    if symptom_name not in symptom_classes:
        symptom_class = types.new_class(
            symptom_class_name,
            (onto.Symptom,)
        )
        symptom_class.label = [symptom_name]
        symptom_classes[symptom_name] = symptom_class
    else:
        symptom_class = symptom_classes[symptom_name]

    # collect relationships
    department_to_systems[dept_name].add(system_name)
    system_to_symptoms[system_name].add(symptom_name)

# =========================
# 6. Add restrictions
# =========================
with onto:
    # Department -> System
    for dept_name, system_name_set in department_to_systems.items():
        department_class = department_classes[dept_name]
        system_class_list = [system_classes[name] for name in system_name_set]

        if len(system_class_list) == 1:
            department_class.is_a.append(
                onto.has_System.some(system_class_list[0])
            )
        else:
            department_class.is_a.append(
                onto.has_System.some(Or(system_class_list))
            )

    # System -> Symptom
    for system_name, symptom_name_set in system_to_symptoms.items():
        system_class = system_classes[system_name]
        symptom_class_list = [symptom_classes[name] for name in symptom_name_set]

        if len(symptom_class_list) == 1:
            system_class.is_a.append(
                onto.has_Symptom.some(symptom_class_list[0])
            )
        else:
            system_class.is_a.append(
                onto.has_Symptom.some(Or(symptom_class_list))
            )

# =========================
# 7. Save ontology
# =========================
onto.save(file="lts_delay_class_based.owl", format="rdfxml")
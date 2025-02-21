import csv
import json
import random
import re
import os
from collections import defaultdict

# Define djinn lists by element
venus_djinn = ["Flint", "Granite", "Quartz", "Vine", "Sap", "Ground", "Bane", "Echo", "Steel", "Mud", "Flower", "Meld", "Petra", "Salt", "Geode", "Mold", "Crystal"]
mercury_djinn = ["Fizz", "Sleet", "Mist", "Spritz", "Hail", "Tonic", "Dew", "Fog", "Sour", "Spring", "Shade", "Steam", "Rime", "Gel", "Eddy", "Balm", "Serac"]
mars_djinn = ["Forge", "Fever", "Corona", "Scorch", "Ember", "Flash", "Torch", "Cannon", "Spark", " Kindle", "Char", "Coal", "Reflux", "Core", "Tinder", "Shine", "Fury", "Fugue"]
jupiter_djinn = ["Gust", "Breeze", "Zephyr", "Smog", "Kite", "Squall", "Luff", "Breath", "Blitz", "Ether", "Waft", "Haze", "Wheeze", "Aroma", "Whorl", "Gasp", "Lull", "Gale"]

# Define summons list
summons = ["Zagan", "Megaera", "Flora", "Moloch", "Ulysses", "Eclipse", "Haures", "Coatlicue", "Daedalus", "Azul", "Catastrophe", "Charon", "Iris"]

# Define summon exclusion rules
summon_exclusions = {
    "Use Ulysses in battle": ["Ulysses"],
    "Use Flora in battle": ["Flora"],
    "Use Moloch in battle": ["Moloch"],
    "Use a Tier 6 summon (or higher) in battle": ["Coatlicue", "Azul", "Daedalus", "Catastrophe", "Charon", "Iris"]
}

# Keep track of excluded summons based on selected objectives
excluded_summons = set()

def get_available_summons():
    """Get list of available summons excluding those that are banned."""
    return [s for s in summons if s not in excluded_summons]

def generate_summon_objective():
    """Generate a random summon objective using only available summons."""
    available = get_available_summons()
    if len(available) < 2:
        # If we don't have enough summons, use what's available or return a default
        if len(available) == 1:
            return f"Learn {available[0]}"
        return "No valid summons available"
    selected_summons = random.sample(available, 2)
    return f"Learn {selected_summons[0]} or {selected_summons[1]}"

def update_excluded_summons(objective_name):
    """Update the excluded summons list based on an objective."""
    if objective_name in summon_exclusions:
        excluded_summons.update(summon_exclusions[objective_name])

# Define which category 6 objectives should be replaced
replaceable_objectives = {
    "Learn Zagan or Megaera",
    "Learn Moloch or Flora",
    "Learn Ulysses or Coatlicue",
    "Learn Eclipse or Haures",
    "Learn two of Azul, Catastrophe or Daedalus",
    "Learn Iris or Charon"
}

def should_replace_objective(obj):
    """Check if an objective should be replaced with a new summon objective."""
    return obj.get('name', '') in replaceable_objectives

def generate_summon_objective():
    """Generate a random summon objective using only available summons."""
    available = get_available_summons()
    if len(available) < 2:
        # If we don't have enough summons, use what's available or return a default
        if len(available) == 1:
            return f"Learn {available[0]}"
        return "No valid summons available"
    selected_summons = random.sample(available, 2)
    return f"Learn {selected_summons[0]} or {selected_summons[1]}"        
        
def generate_djinn_objective(used_djinn):
    """
    Generate a random djinn objective following the specified rules.
    
    Args:
        used_djinn: Set of djinn that have already been used in other objectives
    
    Returns:
        tuple: (objective_text, primary_element) or (None, None) if no valid combination possible
    """
    elements = {
        "Venus": [d for d in venus_djinn if d not in used_djinn],
        "Mercury": [d for d in mercury_djinn if d not in used_djinn],
        "Mars": [d for d in mars_djinn if d not in used_djinn],
        "Jupiter": [d for d in jupiter_djinn if d not in used_djinn]
    }
    
    # Filter out elements that don't have enough djinn for primary element (need 2)
    valid_primary_elements = [e for e, djinn_list in elements.items() if len(djinn_list) >= 2]
    
    # Filter out elements that don't have any djinn for secondary element (need 1)
    valid_secondary_elements = [e for e, djinn_list in elements.items() if len(djinn_list) >= 1]
    
    if not valid_primary_elements or not valid_secondary_elements:
        return None, None
    
    # Select primary element (for 2 djinn)
    primary_element = random.choice(valid_primary_elements)
    
    # Select two djinn from primary element
    try:
        primary_djinn = random.sample(elements[primary_element], 2)
    except ValueError:
        return None, None
    
    # Select secondary element and one djinn
    valid_secondary = [e for e in valid_secondary_elements if e != primary_element]
    if not valid_secondary:
        return None, None
        
    secondary_element = random.choice(valid_secondary)
    try:
        secondary_djinn = [random.choice(elements[secondary_element])]
    except IndexError:
        return None, None
    
    # Format the objective - always list primary element djinn first
    return f"Befriend {primary_djinn[0]}, {primary_djinn[1]}, or {secondary_djinn[0]}", primary_element

def generate_summon_objective():
    """Generate a random summon objective."""
    selected_summons = random.sample(summons, 2)
    return f"Learn {selected_summons[0]} or {selected_summons[1]}"

def find_csv_file():
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if csv_files:
        return csv_files[0]
    return None

def csv_to_bingo_json(csv_file_path, output_file_path):
    bingo_list = {}
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            
            for row in csv_reader:
                try:
                    classification = int(row['Classification'])
                    id = int(row['ID'])
                    objective = row['Objective']
                    core_tags = [tag.strip() for tag in row['Core Tags'].split(',') if tag.strip()]
                    supp_tags = [tag.strip() for tag in row['Supplementary Tags'].split(',') if tag.strip()]
                    restrictions = [r.strip() for r in row['Mutually Exclusive With'].split(',') if r.strip()]
                    
                    if classification not in bingo_list:
                        bingo_list[classification] = []
                    
                    bingo_list[classification].append({
                        "name": objective,
                        "types": core_tags,
                        "id": id,
                        "SuppTags": supp_tags,
                        "Restrictions": restrictions
                    })
                except ValueError as e:
                    print(f"Error processing row: {row}. Error: {e}")
                    continue
        
        # Convert the dictionary to the desired format
        formatted_bingo_list = []
        for i in range(1, max(bingo_list.keys()) + 1):
            if i in bingo_list:
                formatted_bingo_list.append(f"bingoList[{i}] = {json.dumps(bingo_list[i], indent=2)};")
            else:
                formatted_bingo_list.append(f"bingoList[{i}] = [];")
        
        # Write the formatted bingo list to a JavaScript file
        with open(output_file_path, 'w') as js_file:
            js_file.write("var bingoGenerator = require(\"./generators/generator_bases/srl_generator_v5.js\");\n")
            js_file.write("var bingoList = [];\n\n")
            js_file.write("\n\n".join(formatted_bingo_list))
        print(f"Bingo list has been generated and saved to {output_file_path}")
        return bingo_list
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def is_valid_objective(objective, selected_objectives, classification_count, max_per_classification, classification):
    for selected in selected_objectives:
        if str(selected.get('id', '')) in objective.get('Restrictions', []) or str(objective.get('id', '')) in selected.get('Restrictions', []):
            return False
    
    if any(obj['name'] == objective['name'] for obj in selected_objectives):
        return False
    
    if classification_count[classification] >= max_per_classification:
        return False
    
    return True

def check_tag_occurrences(selected_objectives, tag_limits):
    tag_counts = defaultdict(int)
    for obj in selected_objectives:
        for tag in obj.get('types', []):
            if tag in tag_limits:
                tag_counts[tag] += 1
    
    violations = {}
    for tag, count in tag_counts.items():
        if tag_limits[tag] != '-' and count > int(tag_limits[tag]):
            violations[tag] = count
    
    return violations

def is_valid_reroll_objective(objective, selected_objectives, classification_count, max_per_classification, classification, tag_limits):
    # Check basic validity
    if not is_valid_objective(objective, selected_objectives, classification_count, max_per_classification, classification):
        return False
    
    # Check tag limits
    temp_selected = selected_objectives + [objective]
    violations = check_tag_occurrences(temp_selected, tag_limits)
    
    return len(violations) == 0

def classify_into_buckets(classification):
    if classification in [2, 3, 4, 8]:
        return "A"
    elif classification in [5, 6, 7, 9]:
        return "B"
    elif classification in [11, 12, 21, 23]:
        return "C"
    elif classification in [10, 13, 14, 15, 16]:
        return "D"
    elif classification in [17, 18, 19, 20]:
        return "E"
    elif classification in [22, 24, 25]:
        return "F"
    else:
        return "Unknown"

# Define class types and their properties
class_table = {
    "Enchanter": {"type": "Dual", "adept": ("Venus", "Mars"), "element": "Jupiter"},
    "Savage": {"type": "Dual", "adept": ("Venus", "Mars"), "element": ("Mars", "Venus")},
    "Cavalier": {"type": "Dual", "adept": ("Venus", "Mars"), "element": "Mercury"},
    "Scholar": {"type": "Dual", "adept": ("Jupiter", "Mercury"), "element": ("Mercury", "Jupiter")},
    "Ascetic": {"type": "Dual", "adept": ("Jupiter", "Mercury"), "element": "Mars"},
    "Shaman": {"type": "Dual", "adept": ("Jupiter", "Mercury"), "element": "Venus"},
    "Ninja": {"type": "Triple", "adept": ("Venus", "Mars"), "element": "Jupiter", 
              "text": "Have someone be a Ninja (V, Ma | J)"},
    "Ranger": {"type": "Triple", "adept": ("Mercury", "Jupiter"), "element": "Mars",
               "text": "Have someone be a Ranger (Me, J | Ma)"},
    "Medium": {"type": "Triple", "adept": ("Mercury", "Jupiter"), "element": "Venus",
               "text": "Have someone be a Medium (Me, J | V)"},
    "Dragoon": {"type": "Triple", "adept": ("Venus", "Mars"), "element": "Mercury",
                "text": "Have someone be a Dragoon (V, Ma | Me)"},
    "Beasterkeeper": {"type": "Quad", "adept": "All", "element": "All",
                     "text": "Have someone be a Beastkeeper (T. Whip)"},
    "Punchinello": {"type": "Quad", "adept": "All", "element": "All",
                    "text": "Have someone be a Punchinello (M. Card)"},
    "Necrolyte": {"type": "Quad", "adept": "All", "element": "All",
                  "text": "Have someone be a Necrolyte (Tomega.)"}
}

def get_classes_by_type(class_type):
    """Get all classes of a specific type."""
    return [name for name, info in class_table.items() if info["type"] == class_type]

def are_classes_compatible(class1, class2):
    """Check if two classes can coexist in objectives."""
    info1 = class_table[class1]
    info2 = class_table[class2]
    
    if info1["type"] == "Triple" and info2["type"] == "Dual":
        return info1["adept"] != info2["adept"]
    elif info1["type"] == "Dual" and info2["type"] == "Triple":
        return info1["adept"] != info2["adept"]
    return True

def generate_class_objectives(num_objectives):
    """Generate the specified number of class objectives."""
    objectives = []
    used_types = set()
    
    while len(objectives) < num_objectives:
        # Decide objective type with 2:1:1 ratio for Dual:Triple:Quad
        if "Quad" not in used_types and random.random() < 0.25:
            obj_type = "Quad"
        elif "Triple" not in used_types and random.random() < 0.33:
            obj_type = "Triple"
        else:
            obj_type = "Dual"
        
        if obj_type in used_types:
            continue
            
        available_classes = get_classes_by_type(obj_type)
        
        if obj_type == "Dual":
            # Pick two different dual classes
            class1 = random.choice(available_classes)
            class2 = random.choice([c for c in available_classes if c != class1])
            
            # Check compatibility with existing Triple objectives
            triple_obj = next((obj for obj in objectives if class_table[obj["class"]]["type"] == "Triple"), None)
            if triple_obj and (not are_classes_compatible(class1, triple_obj["class"]) or 
                             not are_classes_compatible(class2, triple_obj["class"])):
                continue
                
            objectives.append({
                "name": f"Have a {class1} and {class2} in the party simultaneously",
                "class": class1,
                "second_class": class2,
                "type": "Dual"
            })
        else:  # Triple or Quad
            selected_class = random.choice(available_classes)
            
            # Check compatibility with existing Dual objectives
            dual_objs = [obj for obj in objectives if class_table[obj["class"]]["type"] == "Dual"]
            if any(not are_classes_compatible(selected_class, obj["class"]) for obj in dual_objs):
                continue
                
            objectives.append({
                "name": class_table[selected_class]["text"],
                "class": selected_class,
                "type": obj_type
            })
            
        used_types.add(obj_type)
    
    return objectives    
    
def select_random_objectives(bingo_list, race_mode=False, remove_easy=False, harder_board=False, 
                           tag_limits=None, bucket_mode=False, bucket_hard_mode=False, 
                           exclude_boss_objectives=False, randomize_djinn=False):
    all_classifications = list(bingo_list.keys())
    selected_objectives = []
    classification_count = defaultdict(int)
    max_per_classification = 2 if race_mode else float('inf')
    
# Handle Bucket C replacements if randomize_djinn is enabled
    if randomize_djinn:
        # Store original Bucket C objectives
        bucket_c_classifications = [11, 12, 21, 23]
        original_bucket_c = {}
        for c in bucket_c_classifications:
            if c in bingo_list:
                original_bucket_c[c] = bingo_list[c].copy()
                bingo_list[c] = []  # Clear original objectives
        
        # Determine number of Bucket C objectives needed
        bucket_c_count = 5 if bucket_mode and bucket_hard_mode else 4
        
        # Generate new Bucket C objectives
        num_21 = random.randint(0, 1)  # 0 or 1 objective from 21
        num_23 = random.randint(0, 1)  # 0 or 1 objective from 23
        remaining_slots = bucket_c_count - num_21 - num_23
        
        # Ensure we have at least one of each type
        min_11 = 1
        min_12 = 1
        
        # Calculate remaining slots after minimums
        extra_slots = remaining_slots - min_11 - min_12
        
        # For each extra slot, give 2/3 chance for 11 and 1/3 chance for 12
        extra_11 = sum(1 for _ in range(extra_slots) if random.random() < 2/3)
        
        # Calculate final numbers
        num_11 = min(4, min_11 + extra_11)  # Cap at 4 objectives from 11
        num_12 = remaining_slots - num_11
        
        # Track used elements
        used_primary_elements = set()
        
        # Generate bucket C objectives
        bucket_c_objectives = []
        
        # Clear excluded summons at the start of generation
        excluded_summons.clear()
        
        # Add objectives from 21 and 23 if selected
        if num_21 and 21 in original_bucket_c:
            objectives_21 = [obj for obj in original_bucket_c[21] 
                           if not (exclude_boss_objectives and "Boss" in obj.get('types', []))]
            if objectives_21:
                selected_obj = random.choice(objectives_21)
                bucket_c_objectives.append(selected_obj)
                bingo_list[21] = [selected_obj]  # Add to bingo_list for classification tracking
        
        if num_23 and 23 in original_bucket_c:
            objectives_23 = [obj for obj in original_bucket_c[23]
                           if not (exclude_boss_objectives and "Boss" in obj.get('types', []))]
            if objectives_23:
                selected_obj = random.choice(objectives_23)
                # Update excluded summons based on the selected objective
                update_excluded_summons(selected_obj['name'])
                bucket_c_objectives.append(selected_obj)
                bingo_list[23] = [selected_obj]  # Add to bingo_list for classification tracking

        # Track all used djinn
        used_djinn = set()

        # Generate djinn objectives (category 11)
        for _ in range(num_11):
            attempts = 0
            while attempts < 100:  # Prevent infinite loop
                objective_text, primary_element = generate_djinn_objective(used_djinn)
                if objective_text is None:
                    attempts += 1
                    continue

                if primary_element not in used_primary_elements:
                    used_primary_elements.add(primary_element)

                    # Extract djinn names from the objective text
                    djinn_names = [name.strip() for name in objective_text.replace("Befriend ", "").replace(" or ", ",").split(",")]
                    used_djinn.update(djinn_names)

                    new_obj = {
                        "name": objective_text,
                        "types": [],  # Empty types to avoid tag limit issues
                        "id": random.randint(10000, 99999),
                        "SuppTags": [],
                        "Restrictions": []
                    }
                    bucket_c_objectives.append(new_obj)
                    if 11 not in bingo_list:
                        bingo_list[11] = []
                    bingo_list[11].append(new_obj)  # Add to bingo_list for classification tracking
                    break
                attempts += 1

            if attempts >= 100:
                print(f"Warning: Unable to generate more valid djinn objectives. Only generated {len(bingo_list[11])} objectives.")
                break
        
        # Add objectives from category 12
        if num_12 > 0:
            class_objectives = generate_class_objectives(num_12)
            for obj in class_objectives:
                new_obj = {
                    "name": obj["name"],
                    "types": [],  # Empty types to avoid tag limit issues
                    "id": random.randint(10000, 99999),
                    "SuppTags": [],
                    "Restrictions": []
                }
                bucket_c_objectives.append(new_obj)
                if 12 not in bingo_list:
                    bingo_list[12] = []
                bingo_list[12].append(new_obj)
        
        # Add all bucket C objectives to selected_objectives directly
        for obj in bucket_c_objectives:
            classification = next(c for c in bucket_c_classifications if obj in bingo_list[c])
            selected_objectives.append(obj)
            classification_count[classification] += 1

    if bucket_mode:
        bucket_objectives = {
            "A": [], "B": [], "C": [], "D": [], "E": [], "F": []
        }
        
        # Define bucket_limits before using it
        if bucket_hard_mode:
            bucket_limits = {
                "A": 1, "B": 4, "C": 5, "D": 7, "E": 5, "F": 3
            }
        else:
            bucket_limits = {
                "A": 4, "B": 5, "C": 4, "D": 7, "E": 4, "F": 1
            }

        def select_from_bucket(bucket):
            objectives = bucket_objectives[bucket]
            random.shuffle(objectives)
            for objective in objectives:
                if exclude_boss_objectives and "Boss" in objective.get('types', []):
                    continue
                classification = next(c for c in all_classifications if objective in bingo_list[c])
                if is_valid_objective(objective, selected_objectives, classification_count, max_per_classification, classification):
                    selected_objectives.append(objective)
                    classification_count[classification] += 1
                    print(f"Selected: {objective['name']} from Bucket {bucket}")
                    return True
            return False

        # First, populate bucket_objectives
        for classification, objectives in bingo_list.items():
            bucket = classify_into_buckets(classification)
            if bucket != "Unknown":
                bucket_objectives[bucket].extend(objectives)

        # Initial selection phase
        bucket_selections = []
        for bucket, limit in bucket_limits.items():
            bucket_selections.extend([bucket] * limit)
        random.shuffle(bucket_selections)

        # Select objectives in random order
        for bucket in bucket_selections:
            if not select_from_bucket(bucket):
                print(f"Warning: Unable to find valid objective from Bucket {bucket}")

        # Reroll loop
        while True:
            violations = check_tag_occurrences(selected_objectives, tag_limits)
            if not violations:
                break
            
            print("\nTag occurrence limits exceeded:")
            for tag, count in violations.items():
                print(f"{tag}: {count} occurrences (limit: {tag_limits[tag]})")
            
            reroll = input("Do you want to reroll the objectives that violate these limits? (y/n): ").lower() == 'y'
            if not reroll:
                break

            # Process objectives from most recent to oldest
            for i in range(len(selected_objectives) - 1, -1, -1):
                obj = selected_objectives[i]
                # Check if this objective contributes to any violations
                contributes_to_violation = False
                for tag in violations:
                    if tag in obj.get('types', []):
                        contributes_to_violation = True
                        break
                
                if contributes_to_violation:
                    # Get the bucket of the violating objective
                    classification = next(c for c in all_classifications if obj in bingo_list[c])
                    bucket = classify_into_buckets(classification)
                    
                    # Remove the violating objective
                    selected_objectives.pop(i)
                    classification_count[classification] -= 1
                    print(f"Removed violating objective: {obj['name']} from Bucket {bucket}")
                    
                    # Select a new objective from the same bucket
                    if not select_from_bucket(bucket):
                        print(f"Warning: Unable to find valid replacement objective from Bucket {bucket}")

    else:
        def select_objective(classifications):
            for classification in classifications:
                objectives = bingo_list[classification]
                random.shuffle(objectives)
                for objective in objectives:
                    if exclude_boss_objectives and "Boss" in objective.get('types', []):
                        continue
                    if is_valid_objective(objective, selected_objectives, classification_count, max_per_classification, classification):
                        selected_objectives.append(objective)
                        classification_count[classification] += 1
                        print(f"Selected: {objective['name']} from Classification {classification}")
                        return True
            return False

        if race_mode:
            high_classifications = [c for c in all_classifications if c > 21]
            random.shuffle(high_classifications)
            select_objective(high_classifications[:1])

            initial_classifications = [c for c in all_classifications if 3 <= c <= 21]
            random.shuffle(initial_classifications)
            for classification in initial_classifications:
                if len(selected_objectives) >= 24:
                    break
                select_objective([classification])

            if harder_board:
                harder_classifications = [c for c in all_classifications if 16 <= c <= 21]
                while len(selected_objectives) < 25:
                    if not select_objective(harder_classifications):
                        print(f"Warning: Unable to find more valid objectives from harder range. Stopping at {len(selected_objectives)} objectives.")
                        break
            else:
                while len(selected_objectives) < 25:
                    if not select_objective(initial_classifications):
                        print(f"Warning: Unable to find more valid objectives. Stopping at {len(selected_objectives)} objectives.")
                        break
        else:
            random.shuffle(all_classifications)
            for classification in all_classifications:
                select_objective([classification])
            
            while len(selected_objectives) < 25:
                if not select_objective(all_classifications):
                    print(f"Warning: Unable to find more valid objectives. Stopping at {len(selected_objectives)} objectives.")
                    break

        # Check tag occurrences and offer rerolls
        while True:
            violations = check_tag_occurrences(selected_objectives, tag_limits)
            if not violations:
                break
            
            print("\nTag occurrence limits exceeded:")
            for tag, count in violations.items():
                print(f"{tag}: {count} occurrences (limit: {tag_limits[tag]})")
            
            reroll = input("Do you want to reroll the objectives that violate these limits? (y/n): ").lower() == 'y'
            if not reroll:
                break
            
            # Remove the most recently added objective for each violated tag
            for tag in violations:
                for i in range(len(selected_objectives) - 1, -1, -1):
                    if tag in selected_objectives[i].get('types', []):
                        obj = selected_objectives.pop(i)
                        classification_count[next(c for c in all_classifications if obj in bingo_list[c])] -= 1
                        break

            # Reroll the removed objectives
            if bucket_mode:
                while len(selected_objectives) < 25:
                    reroll_successful = False
                    for bucket in bucket_objectives:
                        if len([obj for obj in selected_objectives if classify_into_buckets(next(c for c in all_classifications if obj in bingo_list[c])) == bucket]) < bucket_limits[bucket]:
                            if select_from_bucket(bucket):
                                reroll_successful = True
                                break
                    if not reroll_successful:
                        break
            else:
                reroll_classifications = all_classifications
                if race_mode:
                    if remove_easy:
                        reroll_classifications = [c for c in all_classifications if c > 2]
                    if harder_board:
                        reroll_classifications = [c for c in reroll_classifications if c > 21 or 16 <= c <= 21]
                    if len([obj for obj in selected_objectives if next(c for c in all_classifications if obj in bingo_list[c]) > 21]) == 1:
                        reroll_classifications = [c for c in reroll_classifications if c <= 21]

                while len(selected_objectives) < 25:
                    reroll_successful = False
                    for classification in reroll_classifications:
                        objectives = bingo_list[classification]
                        random.shuffle(objectives)
                        for objective in objectives:
                            if exclude_boss_objectives and "Boss" in objective.get('types', []):
                                continue
                            if is_valid_reroll_objective(objective, selected_objectives, classification_count, max_per_classification, classification, tag_limits):
                                selected_objectives.append(objective)
                                classification_count[classification] += 1
                                print(f"Rerolled: {objective['name']} from Classification {classification}")
                                reroll_successful = True
                                break
                        if reroll_successful:
                            break
                    if not reroll_successful:
                        break

    # Check for and replace category 6 objectives with summon objectives if randomize_djinn is enabled
    if randomize_djinn:
        for i, obj in enumerate(selected_objectives):
            # Only replace if it's a category 6 objective that matches our criteria
            if any(obj == cat6_obj for cat6_obj in bingo_list.get(6, [])) and should_replace_objective(obj):
                # Replace with a simple summon objective
                selected_objectives[i] = {"name": generate_summon_objective()}

    return selected_objectives

def main():
    # Check for CSV file in the current directory
    default_csv = find_csv_file()
    if default_csv:
        use_default = input(f"Found CSV file: {default_csv}. Use this file? (y/n): ").lower() == 'y'
        if use_default:
            csv_file_path = default_csv
        else:
            csv_file_path = input("Enter the path to your CSV file: ")
    else:
        csv_file_path = input("Enter the path to your CSV file: ")

    js_output_path = 'bingo_list.js'
    bingo_list = csv_to_bingo_json(csv_file_path, js_output_path)
    
    if bingo_list is None:
        print("Failed to generate bingo list. Exiting.")
        return

    bucket_mode = input("Use bucket classification mode? (y/n): ").lower() == 'y'
    
    if bucket_mode:
        bucket_hard_mode = input("Use hard mode for bucket classification? (y/n): ").lower() == 'y'
        race_mode = False
        remove_easy = False
        harder_board = False
    else:
        bucket_hard_mode = False
        race_mode = input("Enable Race Mode? (y/n): ").lower() == 'y'
        remove_easy = False
        harder_board = False
        
        if race_mode:
            remove_easy = input("Remove easy objectives (categories 1 and 2)? (y/n): ").lower() == 'y'
            if remove_easy:
                harder_board = input("Generate a harder board (use categories 16-21 for remaining objectives)? (y/n): ").lower() == 'y'
    
    # New: Add option for randomized djinn objectives
    randomize_djinn = input("Enable randomized Djinn/Summon/Class objectives? (y/n): ").lower() == 'y'
    
    exclude_boss_objectives = input("Are you playing a mode that provides bonuses for beating bosses? (y/n): ").lower() == 'y'
    
    # Define tag limits
    tag_limits = {
        "Whirlwind": "5", "Lash": "2", "Pound": "2", "Scoop": "2", "Reveal": "2",
        "Douse": "2", "Frost": "2", "Growth": "1", "Cyclone": "2", "Sand": "2",
        "Parch": "2", "Burst": "2", "Grind": "-", "Hover": "-",
        "Lift": "1", "Carry": "1", "Force": "1", "Blaze": "2", "Teleport": "2",
        "Mind Read": "1", "RarePsy": "1"
    }
    
    selected_objectives = select_random_objectives(
        bingo_list, race_mode, remove_easy, harder_board, 
        tag_limits, bucket_mode, bucket_hard_mode, 
        exclude_boss_objectives, randomize_djinn
    )
   
    # Ask user if they want to use the default output file name
    default_output = 'selected_objectives.txt'
    use_default_output = input(f"Use default output file name '{default_output}'? (y/n): ").lower() == 'y'
    if use_default_output:
        output_file = default_output
    else:
        output_file = input("Enter the desired output file name: ")

    with open(output_file, 'w') as file:
        json.dump([{"name": obj['name']} for obj in selected_objectives], file, indent=2)
    
    print(f"\nSelected objectives have been written to {output_file}")
    print(f"Total objectives selected: {len(selected_objectives)}")

    classification_count = defaultdict(int)
    for classification, objectives in bingo_list.items():
        for obj in objectives:
            if obj in selected_objectives:
                classification_count[classification] += 1

    for i, obj1 in enumerate(selected_objectives):
        for j, obj2 in enumerate(selected_objectives[i+1:], start=i+1):
            if str(obj1.get('id', '')) in obj2.get('Restrictions', []) or str(obj2.get('id', '')) in obj1.get('Restrictions', []):
                print(f"Warning: Mutual exclusivity violated between {obj1['name']} and {obj2['name']}")
    
    for classification, count in classification_count.items():
        if count > 2:
            print(f"Warning: Classification {classification} has {count} objectives (more than 2)")

if __name__ == "__main__":
    main()

import json
from django.http import JsonResponse
from .models import Filiere, Etudiant, Utilisateur, Module, Note
import os
import random
from django.db.models import Q, Avg

current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the intents.json file
intents_path = os.path.join(current_dir, 'intents.json')

# Load the JSON file
with open(intents_path, 'r', encoding='utf-8') as file:
    intents = json.load(file)["intents"]

# Function to match the user message with an intent
def match_intent(user_message):
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_message:
                return intent
    return None  # Default to unknown if no match is found

# The chatbot response view
def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').lower()
        matched_intent = match_intent(user_message)

        if not matched_intent:
            return JsonResponse({"response": "Sorry, I didn't understand your question."})

        tag = matched_intent["tag"]

        # Handle dynamic intents based on the tag

        # 1. Get the number of students in a Filiere
        if tag == "students_in_filiere":
            filiere_name = user_message.split("filiere")[-1].strip()
            if not filiere_name:
                response = random.choice(matched_intent.get("responses", []))
                return JsonResponse({"response": response})
            try:
                filiere = Filiere.objects.get(nom__iexact=filiere_name)
                student_count = Etudiant.objects.filter(groupe__filiere=filiere).count()
                return JsonResponse({"response": f"There are {student_count} students in Filiere {filiere_name}."})
            except Filiere.DoesNotExist:
                return JsonResponse({"response": f"Filiere '{filiere_name}' not found."})

        # 2. Get email of an Enseignant
        elif tag == "email_of_enseignant":
            for pattern in matched_intent.get("patterns", []):
                if pattern.lower() in user_message:
                    enseignant_name = user_message.replace(pattern.lower(), '').strip()

                    if not enseignant_name:
                        response = random.choice(matched_intent.get("responses", []))
                        return JsonResponse({"response": response})

                    enseignant = Utilisateur.objects.filter(
                        is_enseignant=True
                    ).filter(
                        Q(nom__icontains=enseignant_name) | Q(prenom__icontains=enseignant_name)
                    ).first()

                    if enseignant:
                        return JsonResponse({"response": f"The email of {enseignant.nom} {enseignant.prenom} is {enseignant.email}."})
                    return JsonResponse({"response": f"Enseignant '{enseignant_name}' not found."})

        # 3. Get Module Information
        elif tag == "module_information":
            for pattern in matched_intent.get("patterns", []):
                if pattern.lower() in user_message:
                    module_name = user_message.replace(pattern.lower(), '').strip()
                    if not module_name:
                        response = random.choice(matched_intent.get("responses", []))
                        return JsonResponse({"response": response})
                    try:
                        modules = Module.objects.filter(nom__iexact=module_name)

                        if modules.exists():
                            module_details = "\n".join([
                                f"Module: {module.nom}, Code: {module.code}, Semester: {module.semestre} \n"
                                for module in modules
                            ])                         
                            return JsonResponse({"response": f"Modules: {module_details}"})
                        else:
                            return JsonResponse({"response": f"No modules found with the name '{module_name}'."})
                    except Module.DoesNotExist:
                        return JsonResponse({"response": f"Module '{module_name}' not found."})

        # 4. Get Filiere Information
        elif tag == "filiere_info":
            for pattern in matched_intent.get("patterns", []):
                if pattern.lower() in user_message:
                    filiere_name = user_message.replace(pattern.lower(), '').strip()
                    if not filiere_name:
                        response = random.choice(matched_intent.get("responses", []))
                        return JsonResponse({"response": response})

                    try:
                        filiere = Filiere.objects.get(nom__iexact=filiere_name)
                        return JsonResponse({"response": f"Filiere : {filiere.nom} => Description : {filiere.description or 'pas de description'} => Encadrant : {filiere.encadrant} ."})
                    except Filiere.DoesNotExist:
                        return JsonResponse({"response": f"Filiere '{filiere_name}' not found."})

        # 5. Calculate Module Grade Average
        elif tag == "note_average":
            for pattern in matched_intent.get("patterns", []):
                if pattern.lower() in user_message:
                    module_name = user_message.replace(pattern.lower(), '').strip()

                    if not module_name:
                        response = random.choice(matched_intent.get("responses", []))
                        return JsonResponse({"response": response})

                    try:
                       # Get all modules by name
                        modules = Module.objects.filter(nom__iexact=module_name)

                        if modules.exists():
                            module_details = []
                            for module in modules:
                                # Calculate the average grade for each module
                                average_note = Note.objects.filter(module=module).aggregate(Avg('note_finale'))['note_finale__avg']
                                
                                # Add module details and average grade to the list
                                if average_note is not None:
                                    module_info = f"Module: {module.nom}, Code: {module.code}, Semester: {module.semestre}, Average Grade: {average_note:.2f}"
                                else:
                                    module_info = f"Module: {module.nom}, Code: {module.code}, Semester: {module.semestre}, Average Grade: No grades available"
                                
                                module_details.append(module_info)

                            return JsonResponse({"response": "\n".join(module_details)})
                        else:
                            return JsonResponse({"response": "No modules found with the given name."})

                    except Module.DoesNotExist:
                        return JsonResponse({"response": f"Module '{module_name}' not found."})

        # 6. Get Module Professor Information
        elif tag == "module_professor":
            for pattern in matched_intent.get("patterns", []):
                if pattern.lower() in user_message:
                    module_name = user_message.replace(pattern.lower(), '').strip()
                    if not module_name:
                        response = random.choice(matched_intent.get("responses", []))
                        return JsonResponse({"response": response})

                    # Get all modules with the specified name
                    modules = Module.objects.filter(nom__iexact=module_name)

                    if modules.exists():
                        module_details = []
                        for module in modules:
                            enseignant = module.enseignant
                            if enseignant:
                                module_info = f"{enseignant.nom} {enseignant.prenom} teaches {module.nom} in Master {module.filiere}."
                            else:
                                module_info = f"No professor found for module {module.nom}."
                            
                            module_details.append(module_info)

                        return JsonResponse({"response": "\n".join(module_details)})
                    else:
                        return JsonResponse({"response": f"No modules found with the name '{module_name}'."})

        # 7. Get Student Notes
        elif tag == "student_notes":
            for pattern in matched_intent.get("patterns", []):
                if pattern.lower() in user_message:
                    student_identifier = user_message.replace(pattern.lower(), '').strip()
                    if not student_identifier:
                        response = random.choice(matched_intent.get("responses", []))
                        return JsonResponse({"response": response})

                    try:
                        # Try filtering by both `nom` and `cne`
                        etudiant = Etudiant.objects.filter(Q(nom__iexact=student_identifier) | Q(cne__iexact=student_identifier)).first()
                        print(etudiant)
                        if etudiant:
                            # Fetch and format the student's notes
                            notes = Note.objects.filter(etudiant=etudiant)
                            print(notes)
                            if notes.exists():
                                notes_table = [] 
                                for note in notes:
                                    formatted_note = f"Module: {note.module.nom}, DS: {str(note.note_ds or 'N/A')}, TP: {str(note.note_tp or 'N/A')}, Exam: {str(note.note_exam or 'N/A')}, Final: {str(note.note_finale or 'N/A')}"
                                    notes_table.append(formatted_note)

                                return JsonResponse({"response": notes_table})

                            else:
                                return JsonResponse({"response": f"No notes found for student '{etudiant.nom} {etudiant.prenom}'."})
                        else:
                            return JsonResponse({"response": f"No student found with identifier '{student_identifier}'."})
                    except Exception as e:
                        return JsonResponse({"response": f"An error occurred: {str(e)}"})


        # Handle FAQs and static responses
        elif tag == "static_faq":
            response = random.choice(matched_intent.get("responses", []))
            return JsonResponse({"response": response})

        elif tag == "number":
            response = random.choice(matched_intent.get("responses", []))
            return JsonResponse({"response": response})

        # Fallback response if none of the tags match
        elif "responses" in matched_intent:
            response = random.choice(matched_intent["responses"])
            return JsonResponse({"response": response})

        return JsonResponse({"response": "Sorry, I didn't understand your question."})

    return JsonResponse({"response": "Invalid request method."})

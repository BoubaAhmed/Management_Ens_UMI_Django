import json
from django.http import JsonResponse
from .models import Filiere, Etudiant, Utilisateur, Module
import os
import random
from django.db.models import Q


current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the intents.json file
intents_path = os.path.join(current_dir, 'intents.json')

# Load the JSON file
with open(intents_path, 'r', encoding='utf-8') as file:
    intents = json.load(file)["intents"]


def match_intent(user_message):
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_message:
                return intent
    return None  # Default to unknown if no match is found


def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').lower()
        matched_intent = match_intent(user_message)

        if not matched_intent:
            return JsonResponse({"response": "Sorry, I didn't understand your question."})

        tag = matched_intent["tag"]

        # Handle dynamic intents
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

        elif tag == "module_information":
            module_name = user_message.split("module")[-1].strip()
            if not module_name:
                response = random.choice(matched_intent.get("responses", []))
                return JsonResponse({"response": response})

            try:
                module = Module.objects.get(nom__iexact=module_name)
                return JsonResponse({"response": f"Module: {module.nom}, Code: {module.code}, Semester: {module.semestre}"})
            except Module.DoesNotExist:
                return JsonResponse({"response": f"Module '{module_name}' not found."})


        elif tag == "student_notes":
            student_info = user_message.split("student")[-1].strip()
            return JsonResponse({"response": f"Please provide the student's name or ID to fetch their notes."})

        elif tag == "contact_support":
            return JsonResponse({"response": "You can contact support at support@schoolmanagement.com."})

        elif tag == "create_filiere":
            return JsonResponse({"response": "To create a new filiere, please provide its name, description, and assigned encadrant."})

        elif tag == "filiere_info":
            return JsonResponse({"response": "Please provide the name or ID of the filiere to fetch its details."})

        elif tag == "create_student":
            return JsonResponse({"response": "To register a student, please provide their name, email, CNI, CNE, and assigned group."})

        elif tag == "note_average":
            return JsonResponse({"response": "Please provide the module code to calculate its average note."})

        elif tag == "validate_cni":
            return JsonResponse({"response": "The CNI must follow the format: one uppercase letter followed by 6 digits (e.g., X123456)."})
            
        elif tag == "validate_cne":
            return JsonResponse({"response": "The CNE must follow the format: one uppercase letter followed by 9 digits (e.g., X123456789)."})
        
        elif tag == "module_professor":
            return JsonResponse({"response": "Please provide the module code to fetch its professor details."})

        elif "responses" in matched_intent:
            response = random.choice(matched_intent["responses"])
            return JsonResponse({"response": response})

        return JsonResponse({"response": "Sorry, I didn't understand your question."})

    return JsonResponse({"response": "Invalid request method."})

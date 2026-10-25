import subprocess
subprocess.check_call(["pip", "install", "--no-cache-dir", "preshed==3.0.9"])
import spacy
nlp = spacy.load("en_core_web_sm")
print("SUCCESS WITH PRESHED 3.0.9:", nlp("Hello world!"))


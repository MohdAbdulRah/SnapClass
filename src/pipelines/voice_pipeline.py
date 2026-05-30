import librosa
from resemblyzer import VoiceEncoder,preprocess_wav
import numpy as np 
import io 
import streamlit as st 

#loads only once.
#Future calls reuse the same model.
@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

#For first time user registration added Voice
def get_voice_embeddings(audio_bytes):
    try:
        encoder = load_voice_encoder()
        audio,sr = librosa.load(io.BytesIO(audio_bytes),sr=16000)  #Sample rate is how many times per second your system “listens” to sound and converts it into numbers — in your project, 16,000 times per second.which the Resemblyzer Expects
        #loads audio i.e array of samples [0.001,-0.98,........]
        wav = preprocess_wav(audio) #Normalizes audio. Removes issues like:varying loudness,inconsistent form
        embedding = encoder.embed_utterance(wav) #convert voice into 256 dimensional vector
        return embedding.tolist()  #Gives in list format
    except Exception as e:
        st.error('Voice Recognition Error')
        return None

#Find which student matches the new voice sample. (new_embedding : Voice extracted from classroom audio,candidate_dict : Stored students,threshold : 0.65 : Minimum similarity required.)
def identify_speaker(new_embedding,candidate_dict,threshold=0.65):
    if new_embedding is None or not candidate_dict: #No voice or no students.
        return None,0.0
    
    best_sid = None  #best_matching_student
    best_score = -1.0 #Highest Similarity Score

    for sid,store_embedding in candidate_dict.items():  #sid = student Id,store_embedding = student Voice
        if store_embedding:
            similarity = np.dot(new_embedding,store_embedding) #Dot product measures closeness.Higher = more similar.(new voice embedding,for each student voice embedding)
            if similarity > best_score:
                best_score = similarity #Finding the best match
                best_sid = sid
    if best_score >= threshold:  #If we found out the best one that is greater than threshold  return that student id and score
        return best_sid,best_score
    return None,best_score #If we hadnt found anything


#Process an entire classroom recording.
def process_bulk_audio(audio_bytes,candidate_dict,threshold=0.65):
    try:
        encoder = load_voice_encoder()
        audio,sr = librosa.load(io.BytesIO(audio_bytes),sr=16000)
        segments = librosa.effects.split(audio,top_db=30)
        # Detect Speech Segments
        # 0s - 2s silence                            It returns
        # 2s - 6s Student1                           [
        # 6s - 8s silence                               [3200,2300],[1200,2300]
        # 8s - 10s Student2                           ]
        identified_results = {}

        for start,end in segments:  #Loop over each detected speech chunk
            if (end-start) < sr*0.5: #Only speech > 0.5 seconds is processed
                continue
            segment_audio = audio[start:end] #Extracting that audio
            wav = preprocess_wav(segment_audio) #Preprocessing Audio
            embedding = encoder.embed_utterance(wav) #Generate new embedding for this Audio

            sid,score = identify_speaker(embedding,candidate_dict,threshold) #Now identify which speaker is this by caling from the above function
            if sid:
                if sid not in identified_results  or score > identified_results[sid]: #A student may speak multiple times. Keep the strongest Match
                    identified_results[sid] = score
        return identified_results # return students that can be marked present 
    except Exception as e:
        st.error(f"Bulk Process Error : {e}")
        return {}



# Student registers voice
#           ↓
# Generate embedding
#           ↓
# Store in Supabase
#           ↓
# Teacher records classroom audio
#           ↓
# Split audio into speech segments
#           ↓
# Generate embedding for each segment
#           ↓
# Compare with all stored students
#           ↓
# Highest similarity wins
#           ↓
# Similarity > threshold?
#           ↓
# YES → Present
# NO  → Ignore
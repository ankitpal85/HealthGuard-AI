"""
Voice & Vision AI Health Assistant Page for HealthGuard AI
Provides image-based medical analysis (Prescriptions, Lab Reports, Skin Rashes, Food photos)
and voice-controlled healthcare query processing.
"""

import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.vision_voice_tool import analyze_medical_image_tool, process_voice_query_tool


def show_vision_voice():
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(20,184,166,0.15), rgba(79,142,247,0.15));
                border: 1px solid rgba(20,184,166,0.3); border-radius: 16px; padding: 20px; margin-bottom: 24px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="font-size: 2.2rem;">👁️🎙️</div>
            <div>
                <h2 style="margin:0; color:#14b8a6; font-size:1.5rem;">Voice & Vision AI Healthcare Assistant</h2>
                <p style="margin:4px 0 0; color:#94a3b8; font-size:0.9rem;">
                    Upload Prescriptions & Lab Reports • Skin Rash Diagnostics • Speech-to-Text Voice Queries
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([
        "🖼️ Vision AI Image Analysis",
        "🎙️ Voice-Controlled Queries"
    ])

    # ── TAB 1: Vision AI ───────────────────────────────────────────────────
    with tab1:
        st.markdown("### 🖼️ Medical Document & Visual Condition Analysis")
        st.markdown("Upload or describe medical images for AI document parsing, prescription OCR, diagnostic lab interpretation, or dermatological skin pattern review.")

        category = st.selectbox(
            "Select Analysis Category",
            ["Prescription", "Lab Report", "Skin Condition", "Food / Meal"]
        )

        uploaded_file = st.file_uploader(f"Upload {category} Image (PNG, JPG, PDF)", type=["png", "jpg", "jpeg"])

        text_desc = st.text_area(
            "Medical Description / Extracted Image Text",
            placeholder="e.g. Rx: Dolo 650mg TDS x 3 days, Pantoprazole 40mg OD before meals. Or: Lab Report shows Fasting Blood Sugar 126 mg/dL."
        )

        if st.button("🚀 Analyze Medical Image with Vision AI"):
            if uploaded_file or text_desc:
                combined_desc = text_desc if text_desc else f"Uploaded image file: {uploaded_file.name}"
                with st.spinner(f"Analyzing {category} image using Multimodal Health AI..."):
                    res = analyze_medical_image_tool.invoke({
                        "image_description": combined_desc,
                        "category": category
                    })
                    st.markdown("---")
                    st.markdown(res)
            else:
                st.warning("Please upload an image file or provide a text description.")

    # ── TAB 2: Voice AI ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 🎙️ Hands-Free Voice Controlled Assistant")
        st.markdown("Speak or input voice commands to inquire about your medications, log vitals hands-free, or consult the health agent.")

        # HTML5 / Web Speech API Microphone Integration
        speech_html = """
        <div style="background: rgba(30,41,59,0.7); border: 1px solid rgba(79,142,247,0.2); border-radius: 12px; padding: 20px; text-align: center;">
            <p style="color:#e2e8f0; font-weight:600;">🎙️ Click button below to record voice query using browser Speech Recognition:</p>
            <button id="start-record-btn" onclick="startDictation()" style="background: linear-gradient(135deg, #14b8a6, #4f8ef7); border:none; color:white; padding:12px 24px; border-radius:30px; font-weight:bold; cursor:pointer; font-size:1rem;">
                🎙️ Start Voice Input
            </button>
            <div id="transcript-box" style="margin-top:16px; color:#38bdf8; font-style:italic; font-size:1.1rem;"></div>
        </div>

        <script>
        function startDictation() {
            if (window.hasOwnProperty('webkitSpeechRecognition')) {
                var recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = "en-US";
                recognition.start();

                document.getElementById('transcript-box').innerHTML = "Listening... Speak now!";

                recognition.onresult = function(e) {
                    var text = e.results[0][0].transcript;
                    document.getElementById('transcript-box').innerHTML = '<strong>Heard:</strong> "' + text + '"';
                    recognition.stop();
                };

                recognition.onerror = function(e) {
                    recognition.stop();
                    document.getElementById('transcript-box').innerHTML = "Voice error or browser microphone permission required.";
                }
            } else {
                document.getElementById('transcript-box').innerHTML = "Web Speech API not supported in this browser window. Use text input below.";
            }
        }
        </script>
        """
        st.components.v1.html(speech_html, height=180)

        voice_text = st.text_input("Or enter transcribed voice command:", placeholder="What are my scheduled medications for today?")

        if st.button("Process Spoken Voice Command"):
            if voice_text:
                resp = process_voice_query_tool.invoke({"audio_transcript": voice_text})
                st.success(resp)
            else:
                st.warning("Please provide or speak a voice query.")

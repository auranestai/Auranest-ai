import streamlit as st
import anthropic
import base64

# Page configuration
st.set_page_config(
    page_title="AuraNest AI | Aging-in-Place Safety Audit",
    page_icon="🏠",
    layout="centered"
)

# Initialize Anthropic Client using Streamlit secrets
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

st.title("🏠 AuraNest AI")
st.subheader("Instant Home Safety & Aging-in-Place Audits")
st.markdown(
    "Upload photos or video walkthrough frames of your parent's home. "
    "Our multimodal spatial intelligence engine will instantly scan for fall hazards, "
    "ADA compliance gaps, and generate a professional contractor-ready remediation plan."
)

with st.form("audit_form"):
    st.markdown("### 1. Tell us about the resident")
    resident_context = st.text_area(
        "Care Context (e.g., Mom is 79, uses a cane, has mild balance issues, main concerns are bathroom and stairs):",
        placeholder="Enter details here..."
    )
    
    st.markdown("### 2. Upload Property Walkthrough Media")
    uploaded_files = st.file_uploader(
        "Upload images or video frames (JPEG, PNG, WEBP):",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True
    )
    
    submit_button = st.form_submit_button(label="Generate Safety Audit Report")

if submit_button:
    if not uploaded_files:
        st.warning("Please upload at least one image or video frame of the home space.")
    elif not resident_context:
        st.warning("Please provide a short care context description.")
    else:
        with st.spinner("Analyzing spatial geometry and safety hazards... Please wait (~30 seconds)."):
            try:
                # Prepare image blocks for Claude API
                content_blocks = []
                
                for uploaded_file in uploaded_files:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode("utf-8")
                    
                    # Determine media type
                    file_type = uploaded_file.type
                    if "image" in file_type:
                        media_type = file_type
                    else:
                        media_type = "image/jpeg" # Default fallback
                        
                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image,
                        }
                    })
                
                # Append user text prompt context
                prompt_text = f"""
                Resident Context: {resident_context}
                
                Please perform a comprehensive aging-in-place safety audit based on the uploaded home images, following your system persona instructions.
                """
                content_blocks.append({
                    "type": "text",
                    "text": prompt_text
                })

                # Call Claude 3.5 Sonnet API
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    system=(
                        "You are AuraNest AI, an elite senior safety, ADA compliance, "
                        "and aging-in-place spatial auditing engine. Output a structured Markdown report."
                    ),
                    messages=[
                        {
                            "role": "user",
                            "content": content_blocks
                        }
                    ]
                )

                # Display Results
                st.success("Audit Successfully Completed!")
                st.markdown("---")
                st.markdown(message.content[0].text)
                
                # Provide download button for report
                st.download_button(
                    label="Download Audit Report (Markdown)",
                    data=message.content[0].text,
                    file_name="AuraNest_Safety_Audit.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

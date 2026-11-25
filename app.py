import streamlit as st
from pypdf import PdfReader
from openai import OpenAI


# Connect the application to OpenRouter.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    timeout=60.0,
    max_retries=0
)


st.title("AI Study Assistant")
st.write("Upload a PDF document to generate a study summary.")


uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type="pdf"
)


if uploaded_file is not None:

    try:
        # Open the uploaded PDF.
        reader = PdfReader(uploaded_file)
        page_count = len(reader.pages)

        st.success(f"Uploaded successfully: {uploaded_file.name}")
        st.write(f"Number of pages: {page_count}")

        # Display a preview from the first page.
        first_page = reader.pages[0]
        first_page_text = first_page.extract_text()

        if first_page_text and first_page_text.strip():
            st.subheader("First-page preview")
            st.write(first_page_text[:500])

        # Extract text from every readable page.
        extracted_pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text and page_text.strip():
                extracted_pages.append(page_text)

        # Combine all extracted pages.
        full_text = "\n".join(extracted_pages)

        if full_text.strip():

            st.write(f"Extracted characters: {len(full_text)}")

            # Remove unnecessary whitespace.
            cleaned_text = " ".join(full_text.split())

            st.write(f"Cleaned characters: {len(cleaned_text)}")

            # Calculate the total number of words.
            word_count = len(cleaned_text.split())

            st.write(f"Word count: {word_count}")

            # Generate the AI summary.
            if st.button("Generate Summary"):

                st.info("The summary request has started.")

                try:
                    with st.spinner("Generating summary..."):

                        response = client.chat.completions.create(
                            model=(
                                "nvidia/"
                                "nemotron-3-ultra-550b-a55b:free"
                            ),
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are an AI study assistant. "
                                        "Use only the supplied study material. "
                                        "Do not add unsupported information. "
                                        "If something is unclear, state that "
                                        "it is unclear."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        "Create a complete but concise study summary under 450 words."
                                        "Cover every major section of the document."
                                        "Use clear headings and bullet points."
                                        "Do not repeat information or add unsupported facts."
                                        "Complete every sentence.\n\n"
                                        f"Study material:\n{cleaned_text}"
                                    )
                                }
                            ],
                            max_tokens=1200
                        )

                    summary = response.choices[0].message.content
                    
                    finish_reason = response.choices[0].finish_reason
                    
                    if finish_reason == "length":
                        st.warning(
                            "The summary reached the output limit and may be incomplete."
                        )
                
                

                    if summary and summary.strip():
                        st.subheader("Generated Summary")
                        st.markdown(summary)
        
                        
                    else:
                        st.warning(
                            "The AI model returned an empty response."
                        )

                except Exception as api_error:
                    st.error("Summary generation failed.")
                    st.code(
                        f"{type(api_error).__name__}: {api_error}"
                    )
      
            if st.button("Generate Flashcards"):
                try:
                    with st.spinner("Generating flashcards....."):
                        flashcard_response = client.chat.completions.create(
                            model = "nvidia/nemotron-3-ultra-550b-a55b:free",
                            messages = [
                                {
                                    "role":"system",
                                    "content": (
                                        "You are an AI study assistant. "
                                        "Create flashcards only from the supplied study material."
                                        "Do not add unsupported information."
                                    )
                                },
                                {
                                    "role":"user",
                                    "content": f"""
                                        Create exactly five useful study flashcards from the material below.
                                        
                                        Use this format:
                                        
                                        ### Flashcard 1
                                        **Question:** Write the question here.
                                        
                                        **Answer:** Write the answer here.
                                        
                                        Continue the same format for all five flashcards. 
                                        Keep the answers concise and clear.
                                        
                                        If an answer is not clearly stated in the material, do not guess.
"                                       State that the information is not specified in the document.

                                        Study material:
                                        {cleaned_text}
                                        """
                            
                                }
                            ],
                            max_tokens=800
                        )
                        
                        flashcards =(
                            flashcard_response.choices[0].message.content
                        )
                        
                        if flashcards:
                            st.subheader("Generated Flashcards")
                            st.markdown(flashcards)
                        else:
                            st.warning(
                                "The AI model returned no flashcards."
                            )
                             
                except Exception as api_error:
                    st.error("Flashcard generation failed.")
                    st.code(
                        f"{type(api_error).__name__}:{api_error}"
                    )
        
        else:
            st.warning(
                "No readable text was found in this PDF. "
                "It may be a scanned or image-only document."
            )
                    

    except Exception as pdf_error:
        st.error("The PDF could not be processed.")
        st.code(f"{type(pdf_error).__name__}: {pdf_error}")
import streamlit as st
import os
from src.make_a_book.outline_generator import OutlineCreator
from src.make_a_book.chapter_generator import ChapterCreator
from src.make_a_book.audiobook_generator import AudiobookGenerator

# Page config
st.set_page_config(
    page_title="Book Generator",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'outline' not in st.session_state:
    st.session_state.outline = None
if 'chapters' not in st.session_state:
    st.session_state.chapters = None
if 'book_title' not in st.session_state:
    st.session_state.book_title = ""
if 'book_saved' not in st.session_state:
    st.session_state.book_saved = False
if 'saved_filename' not in st.session_state:
    st.session_state.saved_filename = ""

def save_book_content(title, outline, chapters=None):
    """Save the book content to a file and return the content."""
    content = f"# {title}\n\n"
    content += "## Outline\n\n"
    content += outline
    content += "\n\n"
    
    if chapters:
        content += "## Chapters\n\n"
        for i, chapter in enumerate(chapters, 1):
            content += f"### Chapter {i}\n\n"
            content += chapter
            content += "\n\n"
    
    return content

def save_book_to_file(title, outline, chapters=None):
    """Actually save the book content to a physical file."""
    content = save_book_content(title, outline, chapters)
    filename = f"{title.replace(' ', '_').lower()}_book.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def main():
    st.title("📚 AI Book Generator")
    st.markdown("Generate complete books using AI - from outline to chapters!")
    
    # Sidebar for API key check
    with st.sidebar:
        st.header("Settings")
        
        # Check if API keys are available
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not anthropic_key or anthropic_key == "your_api_key_here":
            st.error("⚠️ Please set your ANTHROPIC_API_KEY in the .env file")
            st.stop()
        else:
            st.success("✅ Anthropic API Key loaded")
            
        if not openai_key or openai_key == "your_api_key_here":
            st.warning("⚠️ OpenAI API Key needed for audiobook generation")
        else:
            st.success("✅ OpenAI API Key loaded")
    
    # Main content
    st.header("1. Book Details")
    
    # Input form
    with st.form("book_form"):
        book_title = st.text_input(
            "Book Title", 
            placeholder="Enter your book title...",
            value=st.session_state.book_title
        )
        
        prompt = st.text_area(
            "Book Topic/Prompt", 
            placeholder="Describe what your book should be about...",
            height=100
        )
        
        generate_outline = st.form_submit_button("Generate Outline", type="primary")
    
    # Generate outline
    if generate_outline and prompt:
        if not book_title:
            st.error("Please enter a book title")
        else:
            st.session_state.book_title = book_title
            
            with st.spinner("Generating outline..."):
                outline_generator = OutlineCreator()
                outline = outline_generator.create_outline(prompt)
                st.session_state.outline = outline
                st.session_state.chapters = None  # Reset chapters
                st.rerun()
    
    # Show outline below the form
    if st.session_state.outline:
        st.header("2. Generated Outline")
        
        # Custom CSS for smaller font
        st.markdown("""
        <style>
        .outline-container {
            font-size: 0.85em;
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
            max-height: 400px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="outline-container">{st.session_state.outline}</div>', unsafe_allow_html=True)
        
        # Feedback section
        st.subheader("Feedback")
        col_feedback, col_generate = st.columns([3, 1])
        
        with col_feedback:
            feedback = st.text_area(
                "Provide feedback to improve the outline",
                placeholder="What changes would you like?",
                height=100
            )
        
        with col_generate:
            st.write("")  # Spacing
            if st.button("Regenerate Outline"):
                if feedback:
                    updated_prompt = f"{prompt}\n\nUser feedback: {feedback}"
                    with st.spinner("Updating outline..."):
                        outline_generator = OutlineCreator()
                        outline = outline_generator.create_outline(updated_prompt)
                        st.session_state.outline = outline
                        st.rerun()
    
    # Chapter generation section
    if st.session_state.outline:
        st.header("3. Generate Chapters")
        
        col_chapters, col_download = st.columns([3, 1])
        
        with col_chapters:
            if not st.session_state.chapters:
                if st.button("🚀 Generate Full Book", type="primary"):
                    with st.spinner("Generating chapters... This may take a few minutes."):
                        # Create chapter generator
                        outline_generator = OutlineCreator()
                        # Create chapter generator using the same LM configuration
                        import dspy
                        anthropic_lm = dspy.LM(
                            model="anthropic/claude-sonnet-4-5-20250929",
                            api_key=os.getenv("ANTHROPIC_API_KEY")
                        )
                        chapter_generator = ChapterCreator(anthropic_lm)
                        
                        # Parse chapters from outline
                        chapters_info = chapter_generator.parse_outline_chapters(st.session_state.outline)
                        
                        if not chapters_info:
                            chapters_info = [
                                ("Chapter 1: Introduction", "Introduction to the topic"),
                                ("Chapter 2: Main Content", "Core content and concepts"),
                                ("Chapter 3: Conclusion", "Summary and final thoughts")
                            ]
                        
                        # Generate chapters with progress
                        chapters = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, (title, description) in enumerate(chapters_info):
                            status_text.text(f"Generating {title}...")
                            chapter_content = chapter_generator.create_chapter(
                                st.session_state.outline, title, description
                            )
                            chapters.append(chapter_content)
                            progress_bar.progress((i + 1) / len(chapters_info))
                        
                        st.session_state.chapters = chapters
                        
                        # Auto-save the book
                        saved_filename = save_book_to_file(
                            st.session_state.book_title, 
                            st.session_state.outline, 
                            chapters
                        )
                        st.session_state.book_saved = True
                        st.session_state.saved_filename = saved_filename
                        
                        status_text.text("✅ All chapters generated and book saved!")
                        st.rerun()
            else:
                st.success(f"✅ Generated {len(st.session_state.chapters)} chapters!")
                
                if st.session_state.book_saved:
                    st.info(f"📁 Book automatically saved as: `{st.session_state.saved_filename}`")
                
                # Display chapters in expandable sections
                for i, chapter in enumerate(st.session_state.chapters, 1):
                    with st.expander(f"Chapter {i}", expanded=False):
                        st.markdown(chapter)
        
        with col_download:
            st.write("")  # Spacing
            if st.session_state.chapters:
                # Generate download content
                book_content = save_book_content(
                    st.session_state.book_title, 
                    st.session_state.outline, 
                    st.session_state.chapters
                )
                
                filename = f"{st.session_state.book_title.replace(' ', '_').lower()}_book.md"
                
                st.download_button(
                    label="📥 Download Book",
                    data=book_content,
                    file_name=filename,
                    mime="text/markdown",
                    type="secondary"
                )
            else:
                # Download outline only
                outline_content = save_book_content(st.session_state.book_title, st.session_state.outline)
                filename = f"{st.session_state.book_title.replace(' ', '_').lower()}_outline.md"
                
                st.download_button(
                    label="📄 Download Outline",
                    data=outline_content,
                    file_name=filename,
                    mime="text/markdown"
                )
    
    # Audiobook Generation Section
    if st.session_state.chapters and st.session_state.book_saved:
        st.header("4. Create Audiobook")
        
        st.markdown("Convert your book to an audiobook using text-to-speech!")
        
        # Voice options
        col_voice, col_options = st.columns([2, 1])
        
        with col_voice:
            voice_option = st.selectbox(
                "Select Voice",
                options=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                help="Choose the voice for your audiobook"
            )
            
            speed = st.slider(
                "Speech Speed",
                min_value=0.25,
                max_value=4.0,
                value=1.0,
                step=0.25,
                help="Adjust the speaking speed (1.0 = normal)"
            )
        
        with col_options:
            st.write("")  # Spacing
            include_outline = st.checkbox("Include outline in audiobook", value=True)
            
            chapter_breaks = st.checkbox("Add pauses between chapters", value=True)
        
        # Voice customization
        st.subheader("Voice Customization")
        
        # Voice selection guide (collapsed by default)
        with st.expander("Voice Characteristics Guide"):
            st.markdown("""
            **Voice Options:**
            - **Alloy**: Balanced, neutral tone
            - **Echo**: Calm, soothing voice  
            - **Fable**: Warm, storytelling voice
            - **Onyx**: Deep, authoritative voice
            - **Nova**: Bright, energetic voice
            - **Shimmer**: Soft, gentle voice
            """)
        
        # Voice instructions
        default_instructions = ("Read with excitement and enthusiasm! You're a friendly storyteller reading to children. Use varied intonation, dramatic pauses for suspense, and express emotions clearly. Make it engaging and fun!")
        
        voice_instructions = st.text_area(
            "Voice Instructions",
            value=default_instructions,
            height=120,
            help="Customize how the narrator should read your book. You can specify accent, tone, energy level, and speaking style."
        )
        
        # Example instructions
        with st.expander("Example Instructions"):
            st.markdown("""
            **Child-Friendly Examples:**
            - "Read with high energy and excitement, like telling a bedtime story to a 5-year-old"
            - "Use a gentle, soothing voice with a slight British accent, perfect for bedtime"
            - "Dramatic and theatrical, with exaggerated emotions for comedy and suspense"
            - "Warm and nurturing voice, speaking slowly and clearly for young listeners"
            
            **Style Controls:**
            - Accent: "with a British accent", "in a Southern drawl"
            - Energy: "high-energy and enthusiastic", "calm and soothing"
            - Pace: "speak slowly and clearly", "speak at a normal pace"
            - Emotion: "express emotions dramatically", "use varied intonation"
            """)
        
        # Audio generation section
        st.subheader("Generate Audio")
        
        if st.button("🎧 Create Audiobook", type="primary"):
            # Check if OpenAI API key is available
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key or openai_key == "your_api_key_here":
                st.error("❌ OpenAI API Key required for audiobook generation")
            else:
                with st.spinner("Generating audiobook... This may take several minutes."):
                    try:
                        audiobook_gen = AudiobookGenerator()
                        
                        # Create progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        total_items = len(st.session_state.chapters)
                        if include_outline:
                            total_items += 1
                        
                        status_text.text("Creating book folder and saving text files...")
                        progress_bar.progress(10)
                        
                        book_folder, audio_files = audiobook_gen.generate_audiobook(
                            book_title=st.session_state.book_title,
                            outline=st.session_state.outline,
                            chapters=st.session_state.chapters,
                            voice=voice_option,
                            speed=speed,
                            include_outline=include_outline,
                            voice_instructions=voice_instructions
                        )
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Audiobook generation complete!")
                        
                        st.success(f"""
                        🎉 **Audiobook Created Successfully!**
                        
                        📁 **Folder**: `{book_folder}`
                        
                        **Contents:**
                        - 📄 Text files in `text/` folder
                        - 🎵 Audio files in `audio/` folder
                        - 🎧 {len(audio_files)} audio files generated
                        
                        **Audio Files:**
                        """)
                        
                        # Show list of generated audio files
                        for audio_file in audio_files:
                            filename = os.path.basename(audio_file)
                            st.text(f"  🎵 {filename}")
                            
                    except Exception as e:
                        st.error(f"❌ Error generating audiobook: {str(e)}")
                        st.text("Please check your OpenAI API key and try again.")
        
        # Preview section
        st.subheader("Preview")
        if st.button("🔊 Preview Voice (First Paragraph)"):
            # Check if OpenAI API key is available
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key or openai_key == "your_api_key_here":
                st.error("❌ OpenAI API Key required for voice preview")
            else:
                with st.spinner("Generating voice preview..."):
                    try:
                        from openai import OpenAI
                        import tempfile
                        import re
                        
                        # Extract first paragraph from first chapter
                        first_chapter = st.session_state.chapters[0]
                        
                        # Clean and extract first paragraph
                        cleaned_text = re.sub(r'#{1,6}\s*', '', first_chapter)  # Remove headers
                        paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
                        
                        preview_text = paragraphs[0] if paragraphs else "This is a preview of the selected voice."
                        
                        # Limit preview to reasonable length
                        if len(preview_text) > 300:
                            sentences = preview_text.split('. ')
                            preview_text = '. '.join(sentences[:3]) + '.'
                        
                        # Generate audio with instructions
                        client = OpenAI(api_key=openai_key)
                        
                        # Prepare API parameters
                        api_params = {
                            "model": "gpt-4o-mini-tts",
                            "voice": voice_option,
                            "input": preview_text,
                            "speed": speed
                        }
                        
                        # Add instructions if provided
                        if voice_instructions and voice_instructions.strip():
                            api_params["instructions"] = voice_instructions
                        
                        response = client.audio.speech.create(**api_params)
                        
                        # Save to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                            response.stream_to_file(temp_file.name)
                            
                            # Display audio player
                            st.success("🎵 Voice preview generated!")
                            st.audio(temp_file.name)
                            
                            # Show preview text
                            st.markdown("**Preview text:**")
                            st.text_area("", value=preview_text, height=100, disabled=True)
                            
                    except Exception as e:
                        st.error(f"❌ Error generating preview: {str(e)}")
                        st.text("Please check your OpenAI API key and try again.")

if __name__ == "__main__":
    main()
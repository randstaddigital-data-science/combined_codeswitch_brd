import streamlit as st
from code_switch.functions import convert_code, generate_documentation, check_syntax
from code_switch.language_detection import detect_language

def main():
    st.title("Code Switch")

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("code_switch/style.css")

    # Add header section with image and description
    header_col1, header_col2 = st.columns([1, 2])

    with header_col1:
        st.image(
            "./Images/Code_Conversion_Design.jpeg",  # Replace with your actual image path
            use_column_width=True
        )

    with header_col2:
        st.markdown("""
        ### Welcome to Code Switch

**Code Switch** is a powerful AI-driven tool designed to help developers efficiently convert their code between multiple programming languages. Whether you’re modernizing systems, switching platforms, or learning new languages, Code Switch streamlines the process with its advanced capabilities.

With **Code Switch**, you can easily translate your code while maintaining accuracy and performance. Beyond conversion, the tool offers syntax validation and detailed code explanations, ensuring your code is not only translated but also optimized for the target language.

##### Key Features:
- 🔄 **Automatic Source Language Detection**: Detect the original code language, making the process fast and seamless.
- 💻 **Multi-Language Support**: Translate code across Python, Java, C++, and COBOL, covering both modern and legacy languages.
- ✨ **Syntax Validation**: Ensure error-free code for Python and Java with built-in validation.
- 📝 **Code Explanation**: Generate detailed explanations of your code for better understanding and documentation.

**Code Switch** simplifies complex coding tasks, allowing you to focus on innovation rather than manual translation. 

Simply upload or paste your code below to get started!
        """)

    # Add a separator
    st.markdown("---")

    st.subheader("Upload Source Code and Select Target Language:")
    uploaded_file = st.file_uploader("Upload Source Code", type=["txt"])
    target_language = st.selectbox(
        "Select Target Language", ["Python", "Java", "C++", "COBOL"]
    )
    source_code = st.text_area(
        "Or paste your source code here",
        height=300,
        placeholder="Paste your source code here...",
    )

    if uploaded_file is not None:
        source_code = uploaded_file.read().decode("utf-8")

    if "converted_code" not in st.session_state:
        st.session_state.converted_code = ""
    if "documentation" not in st.session_state:
        st.session_state.documentation = ""
    if "syntax_result" not in st.session_state:
        st.session_state.syntax_result = ""

    if source_code:
        detected_language = detect_language(source_code)
        st.info(f"Detected Source Language: {detected_language}")

        if st.button("Convert Code"):
            if detected_language != "Unknown":
                with st.spinner("Converting..."):
                    converted_code = convert_code(
                        source_code, detected_language, target_language
                    )
                    st.session_state.converted_code = converted_code
                    st.session_state.documentation = ""
                    st.session_state.syntax_result = ""

        # Use containers for better spacing
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Code:")
                st.markdown(f"```{detected_language.lower()}\n{source_code}\n```")

            with col2:
                st.subheader("Converted Code:")
                if st.session_state.converted_code:
                    st.markdown(
                        f"```{target_language.lower()}\n{st.session_state.converted_code}\n```"
                    )

        if st.session_state.converted_code:
            st.markdown("###")

            # Syntax check button
            if st.button("Evaluate Code (Python & Java only)"):
                with st.spinner("Checking Syntax....."):
                    syntax_output = check_syntax(
                        st.session_state.converted_code, target_language
                    )
                    st.session_state.syntax_result = (
                        f"Syntax Check Output:\n{syntax_output}"
                    )

            # Display Syntax Check Result
            if st.session_state.syntax_result:
                st.subheader("Syntax Check Result:")
                st.write(st.session_state.syntax_result)

                # Generate Explanation button appears after syntax result
                if st.button("Generate Explanation"):
                    with st.spinner("Generating..."):
                        documentation = generate_documentation(
                            st.session_state.converted_code, target_language
                        )
                        st.session_state.documentation = documentation

        # Display Code Explanation
        if st.session_state.documentation:
            st.subheader("Code Explanation:")
            st.markdown(
                f"<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>{st.session_state.documentation}</div>",
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()

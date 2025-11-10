from src.make_a_book.outline_generator import OutlineCreator
from src.make_a_book.chapter_generator import ChapterCreator
import os


def get_user_choice():
    """Get user's choice for next steps."""
    print("\n" + "="*50)
    print("What would you like to do next?")
    print("1. Provide feedback and regenerate outline")
    print("2. Proceed to generate chapters")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def save_book_content(title, outline, chapters=None):
    """Save the book content to a file."""
    filename = f"{title.replace(' ', '_').lower()}_book.md"
    
    with open(filename, 'w') as f:
        f.write(f"# {title}\n\n")
        f.write("## Outline\n\n")
        f.write(outline)
        f.write("\n\n")
        
        if chapters:
            f.write("## Chapters\n\n")
            for i, chapter in enumerate(chapters, 1):
                f.write(f"### Chapter {i}\n\n")
                f.write(chapter)
                f.write("\n\n")
    
    return filename


def main():
    print("Welcome to the Book Generator!")
    
    # Create outline generator
    outline_generator = OutlineCreator()
    
    # Get user input
    prompt = input("Enter your book topic or prompt: ")
    book_title = input("Enter a title for your book: ")
    
    print("\nGenerating book outline...")
    outline = outline_generator.create_outline(prompt)
    
    print("\n" + "="*50)
    print("BOOK OUTLINE")
    print("="*50)
    print(outline)
    
    while True:
        choice = get_user_choice()
        
        if choice == '1':
            # Get feedback and regenerate
            feedback = input("\nWhat changes would you like to the outline? ")
            updated_prompt = f"{prompt}\n\nUser feedback: {feedback}"
            
            print("\nRegenerating outline with your feedback...")
            outline = outline_generator.create_outline(updated_prompt)
            
            print("\n" + "="*50)
            print("UPDATED BOOK OUTLINE")
            print("="*50)
            print(outline)
            
        elif choice == '2':
            # Generate chapters
            print("\nProceeding to generate chapters...")
            
            # Create chapter generator using the same LM
            chapter_generator = ChapterCreator(outline_generator.generate_outline.lm)
            
            # Parse chapters from outline
            chapters_info = chapter_generator.parse_outline_chapters(outline)
            
            if not chapters_info:
                print("Could not parse chapters from outline. Generating generic chapters...")
                chapters_info = [
                    ("Chapter 1: Introduction", "Introduction to the topic"),
                    ("Chapter 2: Main Content", "Core content and concepts"),
                    ("Chapter 3: Conclusion", "Summary and final thoughts")
                ]
            
            chapters = []
            for i, (title, description) in enumerate(chapters_info, 1):
                print(f"\nGenerating {title}...")
                chapter_content = chapter_generator.create_chapter(outline, title, description)
                chapters.append(chapter_content)
                print(f"✓ {title} completed")
            
            # Save the complete book
            filename = save_book_content(book_title, outline, chapters)
            print(f"\n✓ Book saved as: {filename}")
            break
            
        elif choice == '3':
            # Save outline only and exit
            filename = save_book_content(book_title, outline)
            print(f"\nOutline saved as: {filename}")
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()

Build a complete, working Quizlet-style study app for my personal use. Reproduce the familiar flashcard and studying experience as closely as practical, with advanced features available for free. Use an original app name and original assets.
There must be no subscriptions, payments, ads, premium tiers, study limits, or locked features. This is a private, single-user app, so do not require account creation.
Main requirements
Build the actual functioning app, not just a visual mockup. Every button and study mode must work, and my sets and progress must persist after refreshing or closing the app.
1. Dashboard and organization
    •    Show recent sets, folders, favorites, and study progress.
    •    Create, rename, duplicate, archive, and delete sets and folders.
    •    Search and sort sets.
    •    Resume unfinished study sessions.
    •    Include a useful demo set, but allow me to delete it.
2. Set editor
    •    Create unlimited sets with a title, description, and term-definition cards.
    •    Support rich text, images on either side, math notation, code blocks, and multiple languages.
    •    Add, delete, duplicate, and reorder cards.
    •    Autosave edits and display save status.
    •    Import pasted term-definition lists with configurable separators.
    •    Import CSV, TSV, and app backup JSON files.
    •    Export sets to CSV and JSON.
    •    Preview imports and let me fix formatting before saving.
    •    Warn before destructive actions and provide undo where practical.
3. Flashcards
    •    Flip cards with a click, tap, or keyboard shortcut.
    •    Choose whether terms or definitions appear first.
    •    Shuffle cards, star difficult cards, and study only starred cards.
    •    Include text-to-speech, autoplay, and adjustable playback speed.
    •    Track cards as known or still learning.
    •    Support fullscreen studying and swipe controls on mobile.
    •    Preserve session progress.
4. Learn mode
Create an adaptive study experience that combines:
    •    Flashcards.
    •    Multiple-choice questions.
    •    Typed-answer questions.
    •    Repeated practice of missed or difficult cards.
    •    Progress toward mastery.
    •    Configurable session length and question types.
Use a transparent mastery system and spaced repetition to schedule reviews. A missed answer should return sooner, while consistently correct answers should appear less often.
Allow strict or flexible answer checking. Flexible checking should normalize capitalization, whitespace, and configurable punctuation differences. Support alternate accepted answers and a manual “I was correct” override. Do not automatically accept answers that change the meaning.
Multiple-choice distractors must be distinct, exclude the correct answer, and avoid duplicate choices. Handle small sets gracefully.
5. Test mode
    •    Generate customizable tests using multiple choice, true/false, written answers, and matching.
    •    Let me choose question count, question types, which side to answer, and whether to use starred cards.
    •    Support optional timers.
    •    Grade submitted tests and show correct answers with explanations when available.
    •    Review missed questions and retake them.
    •    Save test history and scores.
    •    Provide a clean print layout.
True/false questions and matching answers must be generated consistently from the set, with no ambiguous answer mappings.
6. Write and spell practice
    •    Dedicated typed-answer practice.
    •    Optional hints and progressive answer reveals.
    •    Dictation using text-to-speech, where I type what I hear.
    •    Let me select the language and available voice.
    •    Track mistakes and repeat missed cards.
7. Match game
    •    Display shuffled term and definition tiles.
    •    Remove correct pairs and give clear feedback for incorrect pairs.
    •    Include a timer, personal bests, and replay.
    •    Support keyboard use and touch.
    •    Handle repeated terms or definitions without creating impossible or unfair matches.
8. Advanced study features
    •    Study statistics: accuracy, mastery, review history, time studied, and daily activity.
    •    Daily review queue based on spaced repetition.
    •    Study goals and optional local reminders when the browser supports them.
    •    Combine multiple sets into one study session without modifying the originals.
    •    Filter sessions by starred, missed, unmastered, or overdue cards.
    •    Add explanations and notes to individual cards.
    •    Support image-based questions and optional image-labeling diagrams.
9. Optional AI tools
Include an optional AI integration for:
    •    Turning pasted notes or uploaded text-based documents into editable flashcards.
    •    Generating practice questions.
    •    Explaining answers.
    •    Providing hints.
    •    Tutoring me using the selected set as context.
The core app must work fully without an AI provider or API key. AI must be explicitly enabled and clearly labeled. Never send my study material to an external service without my action.
Do not claim that paid AI API usage is free. Explain any provider charges in settings. Keep API credentials out of source code and logs; use server-side environment variables when a backend is available.
Generated flashcards must be presented for review before being added to a set. AI explanations should distinguish information in my cards from additional information.
Design
Use a polished interface inspired by Quizlet’s familiar layout and interactions:
    •    A clean dashboard with set cards and folder navigation.
    •    A set page with a prominent flashcard viewer and study-mode controls.
    •    Readable typography, rounded cards, subtle shadows, and consistent spacing.
    •    Blue or indigo accents, with light and dark themes.
    •    Responsive layouts for desktop, tablet, and phone.
    •    Clear loading, empty, success, and error states.
    •    Accessible contrast, visible focus indicators, reduced-motion support, and keyboard navigation.
Avoid excessive animations and decorative elements that distract from studying.
Storage and privacy
Default to a local-first architecture:
    •    Use IndexedDB for sets, images, progress, and session history.
    •    Use localStorage only for small preferences.
    •    Make core study features available offline after the app has loaded.
    •    Provide complete backup and restore, including images and progress.
    •    Validate imported files before changing existing data.
    •    Explain that browser storage can be cleared and encourage downloadable backups.
    •    Do not include analytics or tracking.
    •    Do not scrape Quizlet or require a Quizlet login.
Technical implementation
If this workspace already has a framework, use it. Otherwise, use React and TypeScript with an appropriate modern build setup.
Keep components, storage, question generation, grading, and study scheduling modular. Implement real persistence and working interactions. Do not leave placeholder buttons, fake statistics, or unfinished modes.
For large imports and sets, keep the interface responsive. Handle unavailable speech voices, blocked audio playback, storage failures, invalid imports, and sets with too few cards.
Completion criteria
Before finishing, verify that:
    1    I can create and edit a set, reload the app, and retain all changes.
    2    Flashcards, Learn, Test, Write, Spell, and Match work.
    3    Study progress and test history persist.
    4    Imports, exports, and complete backup restoration work.
    5    Images and multilingual text survive backup restoration.
    6    Core studying works without an account, AI key, or payment.
    7    The app works on mobile and supports keyboard navigation.
    8    Incorrect answers, duplicate cards, and small sets behave sensibly.
Implement this in stages if necessary, but continue until the requested core features work. Prioritize reliable studying and data persistence before optional AI features. Provide setup instructions, a concise explanation of the architecture, and an honest list of any remaining limitations.

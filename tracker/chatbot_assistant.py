import os
from typing import List, Dict, Optional

try:
    # OpenAI Python SDK v1.x
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class ChatbotAssistant:
    """Simple console-based chatbot powered by OpenAI.

    Reads API key from the OPENAI_API_KEY environment variable by default.
    Falls back to prompting the user once if not configured.
    """

    def __init__(self, default_model: str = "gpt-4o-mini") -> None:
        self.default_model = default_model
        self.client: Optional[OpenAI] = None  # type: ignore
        self._messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": (
                    "You are WorkBuddy's helpful wellness and productivity assistant. "
                    "Answer concisely and help the user with focus, wellness, and technical questions."
                ),
            }
        ]
        # Attempt lazy setup from environment
        self._ensure_client_initialized()

    def _ensure_client_initialized(self, maybe_api_key: Optional[str] = None) -> bool:
        """Ensure OpenAI client is initialized. Returns True on success."""
        if self.client is not None:
            return True
        if OpenAI is None:
            print("❌ OpenAI SDK not installed. Please install 'openai' and try again.")
            return False

        api_key = maybe_api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return False

        try:
            self.client = OpenAI(api_key=api_key)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            self.client = None
            return False

    def set_api_key(self, api_key: str) -> bool:
        """Explicitly set API key and initialize the client."""
        return self._ensure_client_initialized(maybe_api_key=api_key)

    def reset_conversation(self) -> None:
        """Start a new conversation context."""
        self._messages = self._messages[:1]

    def ask(self, user_message: str, model: Optional[str] = None) -> Optional[str]:
        """Send a message and get the assistant's reply as plain text."""
        if not self._ensure_client_initialized():
            return None

        self._messages.append({"role": "user", "content": user_message})
        try:
            # Using Chat Completions for broad compatibility
            completion = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=self._messages,  # type: ignore
                temperature=0.3,
                max_tokens=600,
            )
            reply = completion.choices[0].message.content or ""
            self._messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"❌ OpenAI request failed: {e}")
            return None

    def start_chat_session(self) -> None:
        """Interactive console chat loop. Type 'exit' to leave, 'new' for new chat."""
        print("\n🤖 AI Chat Assistant (powered by OpenAI)")
        print("Type your message and press Enter. Commands: 'new' to reset, 'exit' to return.")

        if not self._ensure_client_initialized():
            # One-time prompt for API key (not stored)
            api_key = input("Enter OpenAI API key (sk-...): ").strip()
            if not self.set_api_key(api_key):
                print("❌ Invalid API key or initialization failed. Exiting chat.")
                return

        while True:
            try:
                user_input = input("Chat> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in {"exit", "quit", "q"}:
                    print("👋 Ending chat session.")
                    break
                if user_input.lower() in {"new", "reset"}:
                    self.reset_conversation()
                    print("✨ Started a new chat context.")
                    continue

                reply = self.ask(user_input)
                if reply is None:
                    print("❌ Could not get a response. Check your internet connection and API key.")
                    continue

                print(f"\nAssistant: {reply}\n")
            except KeyboardInterrupt:
                print("\n👋 Ending chat session.")
                break 
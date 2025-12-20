# Luffy Chatbot 🛡️ ルフィ

An AI-powered security assistant for the MailShieldAI dashboard.

## Features

- **Bilingual Support**: Responds in English first, then Japanese
- **Neo-Tokyo Aesthetic**: Glassmorphism, neon effects, dark mode
- **Email Security Analysis**: Detects phishing, malware, BEC, spam
- **Quick Actions**: Pre-defined queries for common tasks
- **Responsive Design**: Works on desktop and mobile

## Components

| Component | Description |
|-----------|-------------|
| `luffy-chatbot.tsx` | Main chatbot component with FAB |
| `luffy-header.tsx` | Chat header with status indicator |
| `luffy-input.tsx` | Message input with send button |
| `luffy-message.tsx` | Message bubbles with markdown support |
| `luffy-quick-actions.tsx` | Quick action chips |
| `ui/luffy-avatar.tsx` | Custom avatar component |

## Hooks

- `useLuffyChat` - Chat state management
- `useChatInput` - Input handling

## API

The chatbot uses `/api/luffy` endpoint for Gemini integration.

### Environment Variables

```env
GOOGLE_GEMINI_API_KEY=your-api-key
```

## Styling

CSS in `styles/chatbot.css` with:
- CSS custom properties for theming
- Glassmorphism effects
- Neon border animations
- Accessibility support (reduced motion, focus states)

## Usage

```tsx
import { LuffyChatbot } from "@/components/luffy-chatbot"

export default function Layout({ children }) {
  return (
    <>
      {children}
      <LuffyChatbot />
    </>
  )
}
```

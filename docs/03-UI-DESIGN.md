# Language Tutor - UI/UX Design Specification

**Version:** 1.0  
**Date:** January 2026  

---

## 1. Design Principles

### 1.1 Core Principles

1. **Clarity First**: Clean, uncluttered interface focused on learning
2. **Responsive**: Works seamlessly on desktop, tablet, and mobile
3. **Accessibility**: WCAG 2.1 AA compliant
4. **Consistent**: Unified design language across all pages
5. **Encouraging**: Positive reinforcement for learner progress

### 1.2 Target User Considerations

| User Type | UI Priority |
|-----------|-------------|
| Middle School | Fun, visual, gamified elements |
| University | Efficient, professional, feature-rich |
| Researchers | Information-dense, keyboard shortcuts |
| General | Simple, intuitive, welcoming |

---

## 2. Layout Structure

### 2.1 Desktop Layout (≥1024px)

```
┌──────────────────────────────────────────────────────────────┐
│                         HEADER                                │
│  [Logo] Language Tutor          [Language: 🇬🇧▼] [Settings]  │
├──────────┬───────────────────────────────────────────────────┤
│          │                                                    │
│  SIDEBAR │                   MAIN CONTENT                     │
│          │                                                    │
│  [Chat]  │  ┌────────────────────────────────────────────┐   │
│  [Gram]  │  │                                            │   │
│  [Exer]  │  │           Page-specific content            │   │
│  [Train] │  │                                            │   │
│          │  │                                            │   │
│  ──────  │  │                                            │   │
│          │  │                                            │   │
│  Stats:  │  │                                            │   │
│  Level   │  └────────────────────────────────────────────┘   │
│  Streak  │                                                    │
│          │                                                    │
└──────────┴───────────────────────────────────────────────────┘
```

### 2.2 Mobile Layout (<768px)

```
┌─────────────────────────────┐
│ [≡] Language Tutor    [⚙️]  │
├─────────────────────────────┤
│                             │
│                             │
│      MAIN CONTENT           │
│      (Full width)           │
│                             │
│                             │
├─────────────────────────────┤
│ [Chat] [Gram] [Exer] [Train]│
│         Bottom Nav          │
└─────────────────────────────┘
```

---

## 3. Color System

### 3.1 Primary Palette

```css
:root {
  /* Primary - Deep Blue (Trust, Learning) */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  
  /* Secondary - Emerald (Success, Progress) */
  --secondary-50: #ecfdf5;
  --secondary-500: #10b981;
  --secondary-600: #059669;
  
  /* Accent - Amber (Highlights, Warnings) */
  --accent-50: #fffbeb;
  --accent-500: #f59e0b;
  
  /* Neutral */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-500: #6b7280;
  --gray-700: #374151;
  --gray-900: #111827;
}
```

### 3.2 Semantic Colors

| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Success | `#10b981` | `#34d399` |
| Error | `#ef4444` | `#f87171` |
| Warning | `#f59e0b` | `#fbbf24` |
| Info | `#3b82f6` | `#60a5fa` |

### 3.3 Language-Specific Accents

| Language | Accent Color | Usage |
|----------|--------------|-------|
| English | `#1e40af` (Royal Blue) | Tags, borders |
| Chinese | `#dc2626` (Red) | Cultural association |
| Russian | `#1e3a8a` (Navy) | Cultural association |
| Japanese | `#be123c` (Rose) | Cultural association |

---

## 4. Typography

### 4.1 Font Stack

```css
/* Primary (UI) */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Monospace (Code, Examples) */
font-family: 'JetBrains Mono', 'Fira Code', monospace;

/* CJK Support */
font-family: 'Noto Sans SC', 'Noto Sans JP', sans-serif;
```

### 4.2 Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 2.25rem (36px) | 700 | 1.2 |
| H2 | 1.875rem (30px) | 600 | 1.3 |
| H3 | 1.5rem (24px) | 600 | 1.4 |
| Body | 1rem (16px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Caption | 0.75rem (12px) | 400 | 1.4 |

---

## 5. Component Specifications

### 5.1 Chat Interface

```
┌────────────────────────────────────────────────────┐
│  Chat Tutor                          [🇬🇧 English ▼] │
│                                      [Level: Beginner ▼] │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ 🤖 Hello! I'm your language tutor.          │ │
│  │    What would you like to practice today?    │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│         ┌──────────────────────────────────────┐  │
│         │ User message appears on the right    │  │
│         └──────────────────────────────────────┘  │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ 🤖 Response with helpful explanation...     │ │
│  │    ├─ Grammar tip: ...                      │ │
│  │    └─ Example: ...                          │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
├────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────┐ [Send] │
│ │ Type your message...                   │        │
│ └────────────────────────────────────────┘        │
└────────────────────────────────────────────────────┘
```

**Specifications:**
- Messages have max-width of 80%
- AI messages: left-aligned, light background
- User messages: right-aligned, primary color
- Streaming text has cursor animation
- Code/examples use monospace font

### 5.2 Grammar Correction Tool

```
┌────────────────────────────────────────────────────┐
│  Grammar Check                       [🇯🇵 Japanese ▼] │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │ Enter your text here...                    │   │
│  │                                            │   │
│  │                                            │   │
│  │                                     [Check]│   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  ═══════════════ Results ═══════════════════════  │
│                                                    │
│  Original:                                        │
│  "私は学校行きます" (strikethrough on errors)      │
│                                                    │
│  Corrected:                              [Copy 📋] │
│  "私は学校に行きます" (highlighted corrections)    │
│                                                    │
│  ┌────────────────────────────────────────────┐   │
│  │ ⚠️ Missing particle                        │   │
│  │ Location: after 学校                       │   │
│  │ Should be: 学校に (destination particle)   │   │
│  │ Explanation: に marks the destination...   │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Error Type Colors:**
- Grammar: Red badge
- Spelling: Orange badge
- Punctuation: Yellow badge
- Word Choice: Blue badge
- Style: Purple badge

### 5.3 Exercise Panel

```
┌────────────────────────────────────────────────────┐
│  Exercises          [🇨🇳 Chinese ▼] [Level: Intermediate ▼] │
├────────────────────────────────────────────────────┤
│                                                    │
│  Topic: [Measure Words        ▼]                  │
│  Type:  [Multiple Choice ▼] [Fill Blank] [Trans]  │
│                                     [Generate]    │
│                                                    │
│  ════════════════════════════════════════════════ │
│                                                    │
│  Question 1 of 5                    Score: 3/5    │
│  ┌────────────────────────────────────────────┐   │
│  │                                            │   │
│  │  Complete: 三___书 (three books)           │   │
│  │                                            │   │
│  │  ○ 个                                      │   │
│  │  ○ 本  ← (selected, correct: ✓ green)      │   │
│  │  ○ 只                                      │   │
│  │  ○ 张                                      │   │
│  │                                            │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  💡 Explanation:                                  │
│  本 (běn) is the measure word for books...       │
│                                                    │
│  [Previous]                              [Next]   │
│                                                    │
│  ████████████░░░░░░░░ 60% Complete                │
│                                                    │
└────────────────────────────────────────────────────┘
```

### 5.4 Training Panel

```
┌────────────────────────────────────────────────────┐
│  Model Training                                    │
├────────────────────────────────────────────────────┤
│  [Training Data] [Fine-tuning]                    │
│  ─────────────────────────────────────────────────│
│                                                    │
│  Datasets:                                        │
│  ┌────────────────────────────────────────────┐   │
│  │ ☑ General Tutoring (45 examples)     [Edit]│   │
│  │ ☐ Japanese Grammar (23 examples)     [Edit]│   │
│  │ + Create New Dataset                       │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  Examples in "General Tutoring":                  │
│  ┌────────────────────────────────────────────┐   │
│  │ System: You are a language tutor...        │   │
│  │ User: How do I use conditionals?           │   │
│  │ Assistant: Conditionals are...             │   │
│  │                                            │   │
│  │ ⭐⭐⭐⭐☆  [Approve] [Edit] [Delete]        │   │
│  └────────────────────────────────────────────┘   │
│                                                    │
│  [Export Training Data]                           │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 6. Interactive States

### 6.1 Button States

| State | Visual |
|-------|--------|
| Default | Solid background |
| Hover | Slightly darker, shadow |
| Active | Darker, pressed effect |
| Disabled | Opacity 50%, no pointer |
| Loading | Spinner icon |

### 6.2 Input States

| State | Visual |
|-------|--------|
| Default | Gray border |
| Focus | Primary color border, glow |
| Error | Red border, error message |
| Disabled | Gray background, no input |

### 6.3 Loading States

```
Chat: Streaming dots animation (...)
API calls: Spinner with "Loading..."
Exercises: Skeleton placeholder
Full page: Centered spinner
```

---

## 7. Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, bottom nav |
| Tablet | 640-1023px | Collapsible sidebar |
| Desktop | ≥ 1024px | Full sidebar |
| Large | ≥ 1280px | Wider content area |

---

## 8. Accessibility

### 8.1 Requirements

- All interactive elements keyboard accessible
- Focus indicators visible
- Color contrast ratio ≥ 4.5:1
- Alt text for images
- ARIA labels for icons
- Screen reader announcements for dynamic content

### 8.2 Keyboard Shortcuts (Future)

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Enter` | Send message |
| `Ctrl/Cmd + /` | Open help |
| `Tab` | Navigate elements |
| `Escape` | Close modals |

---

## 9. Animation Guidelines

### 9.1 Timing

| Type | Duration | Easing |
|------|----------|--------|
| Micro (hover) | 150ms | ease-out |
| Small (toggle) | 200ms | ease-in-out |
| Medium (modal) | 300ms | ease-in-out |
| Large (page) | 400ms | ease-out |

### 9.2 Principles

- Animations should feel natural
- Avoid blocking user actions
- Reduce motion for accessibility (prefers-reduced-motion)
- Use GPU-accelerated properties (transform, opacity)

---

## 10. Dark Mode

### 10.1 Color Adjustments

| Element | Light | Dark |
|---------|-------|------|
| Background | `#ffffff` | `#0f172a` |
| Surface | `#f8fafc` | `#1e293b` |
| Text Primary | `#111827` | `#f1f5f9` |
| Text Secondary | `#6b7280` | `#94a3b8` |
| Border | `#e5e7eb` | `#334155` |

### 10.2 Implementation

```css
/* System preference */
@media (prefers-color-scheme: dark) {
  :root {
    --background: #0f172a;
    /* ... */
  }
}

/* Manual toggle */
.dark {
  --background: #0f172a;
  /* ... */
}
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial UI specification |

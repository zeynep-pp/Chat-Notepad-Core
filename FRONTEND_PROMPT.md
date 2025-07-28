# 🎨 Frontend Implementation Prompt for Days 3-4 Advanced Features

## Overview
Implement the frontend components and integrations for the advanced ChatNotePad.AI features including version tracking, command history, AI suggestions, and multi-language translation.

## 🏗️ Architecture Requirements

### State Management
Use your preferred state management solution (Zustand, Redux, Context API) to handle:
- Version history state
- Command history and statistics
- AI suggestions cache
- Translation state
- User preferences

### API Integration
All backend APIs are ready at `http://localhost:8000/api/v1/`:
- Version Management: `/notes/{id}/versions/*`
- Command History: `/history/*`
- AI Services: `/ai/*`

## 🔧 Core Components to Implement

### 1. Version Management Components

#### VersionTimeline Component
```typescript
interface VersionTimelineProps {
  noteId: string;
  onVersionSelect: (versionId: string) => void;
  onRestoreVersion: (versionId: string) => void;
}

// Features:
// - Display chronological list of note versions
// - Show version numbers, timestamps, and change descriptions
// - Visual timeline with dots/lines
// - Click to preview version
// - Restore button with confirmation
// - Auto-refresh when new versions are created
```

#### DiffViewer Component
```typescript
interface DiffViewerProps {
  noteId: string;
  version1: number;
  version2: number;
  mode: 'inline' | 'side-by-side';
}

// Features:
// - Split-pane or inline diff visualization
// - Syntax highlighting for markdown
// - Line-by-line comparison
// - Added/removed/modified indicators
// - Expandable unchanged sections
// - Copy functionality
```

#### RestoreVersionModal Component
```typescript
interface RestoreVersionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  versionDetails: {
    versionNumber: number;
    createdAt: string;
    description?: string;
  };
}

// Features:
// - Confirmation dialog
// - Show version preview
// - Warning about losing current changes
// - Option to create backup before restore
```

#### VersionIndicator Component
```typescript
interface VersionIndicatorProps {
  currentVersion: number;
  totalVersions: number;
  hasUnsavedChanges: boolean;
}

// Features:
// - Display current version info in editor header
// - Unsaved changes indicator
// - Quick access to version timeline
// - Auto-save status
```

### 2. Command History Components

#### CommandHistoryPanel Component
```typescript
interface CommandHistoryPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

// Features:
// - Sliding panel or modal
// - Paginated command list
// - Filter by success/failure, date range
// - Command execution time display
// - Re-run command functionality
// - Export history option
```

#### HistorySearchInput Component
```typescript
interface HistorySearchInputProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  placeholder?: string;
}

interface SearchFilters {
  searchIn: 'command' | 'input' | 'output' | 'all';
  dateRange?: { start: Date; end: Date };
  successOnly?: boolean;
}

// Features:
// - Debounced search input
// - Advanced filter options
// - Search in command, input, or output
// - Keyboard shortcuts (Ctrl+K)
// - Recent searches dropdown
```

#### CommandStatsCard Component
```typescript
interface CommandStatsCardProps {
  timeRange: '7d' | '30d' | '90d';
  onTimeRangeChange: (range: string) => void;
}

// Features:
// - Statistics overview cards
// - Charts for command usage over time
// - Success rate visualization
// - Most popular commands list
// - Performance metrics
```

#### PopularCommandsWidget Component
```typescript
interface PopularCommandsWidgetProps {
  commands: PopularCommand[];
  onCommandClick: (command: string) => void;
}

// Features:
// - Quick access widget in sidebar
// - Recent and popular command suggestions
// - Click to insert command
// - Frequency indicators
// - Customizable display count
```

### 3. AI Features Components

#### SuggestionDropdown Component
```typescript
interface SuggestionDropdownProps {
  isVisible: boolean;
  suggestions: Suggestion[];
  selectedIndex: number;
  onSelect: (suggestion: string) => void;
  onClose: () => void;
  position: { x: number; y: number };
}

// Features:
// - Floating dropdown near cursor
// - Keyboard navigation (arrow keys, enter)
// - Different suggestion types (content, command, style)
// - Confidence indicators
// - Debounced API calls
// - Smart positioning to avoid viewport edges
```

#### AIAssistantButton Component
```typescript
interface AIAssistantButtonProps {
  currentText: string;
  cursorPosition: number;
  onSuggestion: (suggestion: string) => void;
}

// Features:
// - Floating action button or toolbar button
// - Context menu with AI options
// - Quick suggestions for selected text
// - Style improvement suggestions
// - Loading states and error handling
```

#### TranslationModal Component
```typescript
interface TranslationModalProps {
  isOpen: boolean;
  onClose: () => void;
  sourceText: string;
  onTranslated: (translatedText: string, targetLang: string) => void;
}

// Features:
// - Modal with source and target text areas
// - Language selector dropdown
// - Auto-detect source language
// - Translate button with loading state
// - Copy to clipboard functionality
// - Replace or insert options
```

#### LanguageSelector Component
```typescript
interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (langCode: string) => void;
  supportedLanguages: LanguageOption[];
}

// Features:
// - Searchable dropdown
// - Flag icons for languages
// - Recent languages section
// - Popular languages shortcuts
// - Keyboard navigation
```

## 🔌 Integration Points

### Editor Integration
```typescript
// Add to your main editor component
const EditorWithAdvancedFeatures = () => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [cursorPosition, setCursorPosition] = useState(0);

  // Auto-suggestion logic
  const handleTextChange = useCallback(
    debounce(async (text: string, position: number) => {
      if (text.length > 10) {
        const context = text.substring(Math.max(0, position - 50), position + 50);
        try {
          const response = await fetch('/api/v1/ai/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              context: context,
              text: text,
              cursor_position: position,
              context_type: 'content'
            })
          });
          const data = await response.json();
          setSuggestions(data.suggestions);
          setShowSuggestions(true);
        } catch (error) {
          console.error('Suggestion error:', error);
        }
      }
    }, 500),
    []
  );

  // Version auto-save logic
  const handleAutoSave = useCallback(
    debounce(async (noteId: string, content: string) => {
      try {
        await fetch(`/api/v1/notes/${noteId}/versions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            change_description: 'Auto-saved version'
          })
        });
      } catch (error) {
        console.error('Auto-save error:', error);
      }
    }, 30000), // Auto-save every 30 seconds
    []
  );

  return (
    <div className="editor-container">
      <EditorHeader>
        <VersionIndicator {...versionProps} />
        <AIAssistantButton {...aiProps} />
      </EditorHeader>
      
      <EditorContent
        onChange={handleTextChange}
        onCursorChange={setCursorPosition}
      />
      
      {showSuggestions && (
        <SuggestionDropdown
          suggestions={suggestions}
          position={getCursorPosition()}
          onSelect={handleSuggestionSelect}
          onClose={() => setShowSuggestions(false)}
        />
      )}
      
      <VersionTimeline noteId={noteId} />
      <CommandHistoryPanel />
      <TranslationModal />
    </div>
  );
};
```

### Keyboard Shortcuts
```typescript
const keyboardShortcuts = {
  'Ctrl+H': () => setShowCommandHistory(true),
  'Ctrl+Shift+V': () => setShowVersionTimeline(true),
  'Ctrl+T': () => setShowTranslationModal(true),
  'Ctrl+Space': () => triggerSuggestions(),
  'Ctrl+Z': () => restorePreviousVersion(),
  'Escape': () => closeAllModals()
};
```

## 📱 Responsive Design Considerations

### Mobile Adaptations
- Convert modals to full-screen on mobile
- Touch-friendly button sizes
- Swipe gestures for version navigation
- Collapsible panels for better space usage
- Bottom sheet components for mobile actions

### Accessibility
- ARIA labels for all interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Focus management in modals
- Color contrast compliance

## 🎨 UI/UX Guidelines

### Visual Design
- Use consistent color scheme with your existing design
- Add subtle animations for state transitions
- Loading skeletons for API calls
- Toast notifications for actions (save, restore, translate)
- Progress indicators for long operations

### User Experience
- Auto-save indicators to reduce anxiety
- Optimistic updates where possible
- Graceful error handling with retry options
- Contextual help tooltips
- Onboarding tour for new features

## 🧪 Testing Strategy

### Unit Tests
- Component rendering tests
- API integration mocks
- State management logic
- Keyboard interaction tests

### Integration Tests
- End-to-end user workflows
- Version restoration flow
- Translation workflow
- Command history search

### Performance Tests
- Suggestion API debouncing
- Large version history handling
- Memory leaks in long sessions

## 🚀 Implementation Priority

### Phase 1 (High Priority)
1. **VersionIndicator** - Basic version display
2. **SuggestionDropdown** - Core AI suggestion functionality
3. **CommandHistoryPanel** - Basic history viewing

### Phase 2 (Medium Priority)
1. **VersionTimeline** - Full version management
2. **DiffViewer** - Version comparison
3. **TranslationModal** - Translation features

### Phase 3 (Low Priority)
1. **CommandStatsCard** - Analytics dashboard
2. **PopularCommandsWidget** - Command suggestions
3. **Advanced keyboard shortcuts**

## 🔧 Development Notes

### Environment Setup
Make sure your frontend can connect to the backend:
```javascript
// Add to your environment variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Error Handling
```typescript
const useAdvancedFeatures = () => {
  const [isOnline, setIsOnline] = useState(true);
  
  const withErrorHandling = async (apiCall: () => Promise<any>) => {
    try {
      return await apiCall();
    } catch (error) {
      if (error.status === 429) {
        showToast('Rate limit exceeded. Please try again later.', 'warning');
      } else if (error.status === 401) {
        // Handle authentication error
        redirectToLogin();
      } else {
        showToast('An error occurred. Please try again.', 'error');
      }
      throw error;
    }
  };

  return { withErrorHandling, isOnline };
};
```

This comprehensive implementation will provide users with a powerful, modern note-taking experience with advanced AI capabilities, version control, and multi-language support. Focus on user experience and performance while maintaining code quality and accessibility standards.
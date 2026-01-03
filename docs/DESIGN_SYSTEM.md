# Phishly Admin - Modern Design System

## Overview
The Phishly Admin interface has been redesigned with a modern, professional aesthetic inspired by [shadcn/ui](https://ui.shadcn.com/). The design emphasizes clarity, consistency, and professionalism while avoiding overly playful elements like emojis.

## Design Philosophy
- **Minimal & Professional**: Clean interface without excessive decoration
- **Consistent**: Unified design language across all pages
- **Accessible**: High contrast ratios and readable typography
- **Modern**: Contemporary UI patterns and interactions

## Color System

### HSL-Based Tokens
All colors use HSL (Hue, Saturation, Lightness) values for easy theme customization:

```css
:root {
    /* Neutral Palette */
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    
    /* Component Colors */
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    
    /* Brand Colors */
    --primary: 221.2 83.2% 53.3%;        /* Blue #3b82f6 */
    --primary-foreground: 210 40% 98%;
    
    /* Semantic Colors */
    --secondary: 210 40% 96.1%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    
    --destructive: 0 84.2% 60.2%;        /* Red for warnings */
    --success: 142.1 76.2% 36.3%;        /* Green for success */
    --warning: 38 92% 50%;                /* Orange for warnings */
    
    /* UI Elements */
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;           /* Focus ring color */
    
    --radius: 0.5rem;                     /* Default border radius */
}
```

### Usage
Colors should be referenced using `hsl(var(--token))` format:
```css
.button {
    background-color: hsl(var(--primary));
    color: hsl(var(--primary-foreground));
    border: 1px solid hsl(var(--border));
}
```

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
```

### Font Smoothing
```css
-webkit-font-smoothing: antialiased;
-moz-osx-font-smoothing: grayscale;
```

### Type Scale
- **Headings**: 1.5rem - 2.5rem with letter-spacing: -0.025em
- **Body**: 0.875rem - 1rem
- **Small**: 0.75rem - 0.8125rem
- **Line Height**: 1.6 for body text

## Component Patterns

### Buttons
```html
<!-- Primary Button -->
<button class="btn-primary">Create Campaign</button>

<!-- Secondary Button -->
<button class="btn-secondary">Cancel</button>

<!-- Icon Button -->
<button class="btn-icon">⚙</button>
```

**Styles:**
- Border radius: `var(--radius)` (0.5rem)
- Padding: `0.5rem 1rem`
- Font weight: 500-600
- Subtle shadow on primary: `0 1px 2px 0 rgb(0 0 0 / 0.05)`
- Smooth transitions: `0.15s ease`

### Cards
```html
<div class="stat-card">
    <div class="stat-header">
        <span class="stat-icon">✉</span>
        <span class="stat-label">Emails Sent</span>
    </div>
    <div class="stat-value">1,842</div>
</div>
```

**Characteristics:**
- Background: `hsl(var(--card))`
- Border: `1px solid hsl(var(--border))`
- Border radius: `var(--radius)`
- Subtle hover shadow
- No heavy drop shadows

### Status Badges
```html
<span class="status-badge status-active">Active</span>
<span class="status-badge status-completed">Completed</span>
<span class="status-badge status-draft">Draft</span>
```

**Color Coding:**
- **Active**: Green background with green text
- **Completed**: Gray/muted styling
- **Draft**: Amber/yellow styling
- **Paused**: Red/destructive styling

### Tables
```html
<table class="data-table">
    <thead>
        <tr>
            <th>Campaign</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Q4 Security Test</td>
            <td><span class="status-badge status-active">Active</span></td>
            <td>
                <button class="btn-icon">◉</button>
                <button class="btn-icon">✎</button>
            </td>
        </tr>
    </tbody>
</table>
```

**Features:**
- Striped rows with subtle background: `hsl(var(--muted) / 0.3)`
- Hover state: `hsl(var(--accent))`
- Border-collapse with 1px borders

## Icon System

### Minimal Unicode Icons
Instead of emojis, we use minimal Unicode symbols:

| Purpose | Icon | Unicode |
|---------|------|---------|
| Dashboard | ▤ | U+25A4 |
| Email/Campaigns | ✉ | U+2709 |
| Templates/Menu | ☰ | U+2630 |
| Targets/Circle | ◉ | U+25C9 |
| Analytics/Chart | ▦ | U+25A6 |
| Settings/Gear | ⚙ | U+2699 |
| Info | ⓘ | U+24D8 |
| User/Dot | ● | U+25CF |
| View/Eye | ◉ | U+25C9 |
| Edit/Pencil | ✎ | U+270E |
| Warning | ⚠ | U+26A0 |

### Usage
```html
<span class="icon">✉</span>
```

**Styling:**
- Font size: 1.25rem for nav icons
- Color: `hsl(var(--muted-foreground))`
- Active state: `hsl(var(--foreground))`

## Layout Structure

### Sidebar + Main Content
```
┌─────────────────────────────────────┐
│ Sidebar (280px) │  Main Content     │
│                 │                   │
│  - Logo         │  - Header         │
│  - Navigation   │  - Breadcrumbs    │
│  - User Info    │  - Content Area   │
└─────────────────────────────────────┘
```

**Sidebar:**
- Width: 280px (fixed)
- Background: `hsl(var(--card))`
- Border right: `1px solid hsl(var(--border))`
- Position: Fixed left

**Main Content:**
- Margin left: 280px
- Padding: 2rem
- Background: `hsl(var(--background))`

### Responsive Breakpoint
At `768px`:
- Sidebar collapses to icon-only (70px)
- Icon labels hidden
- Main content adjusts margin

## Page-Specific Patterns

### Dashboard
- 4-column stats grid (auto-fit, min 280px)
- Recent campaigns table
- Quick action cards

### Analytics
- Filter panel (collapsible)
- 6 KPI cards in responsive grid
- Time series chart (Chart.js)
- Campaign performance table
- Department breakdown cards
- Device/browser pie charts
- Vulnerable users table
- Event timeline

### Campaigns
- Campaign list with status badges
- Action buttons (View, Edit, Delete)
- Create/Edit modals

### Targets
- Groups table
- Stats summary (total groups, total targets)
- CSV import functionality
- Member viewer modal

### Email Templates
- Template cards grid (auto-fill, min 350px)
- Preview thumbnails
- Edit/Delete actions
- Create template modal

## Interactions

### Hover States
- Buttons: Slight opacity change or background darkening
- Cards: Subtle shadow elevation
- Table rows: Background color change to `hsl(var(--accent))`
- Links: Color change to `hsl(var(--primary))`

### Focus States
- Ring: `0 0 0 3px hsl(var(--ring) / 0.2)`
- Outline removed: `outline: none`
- Applied to: inputs, buttons, selects

### Transitions
- Default: `all 0.15s ease`
- Cards: `box-shadow 0.15s ease`
- No excessive animation

## Accessibility

### Contrast Ratios
- Text on white: `hsl(222.2 84% 4.9%)` - WCAG AAA
- Muted text: `hsl(215.4 16.3% 46.9%)` - WCAG AA
- Primary button: Tested for 4.5:1 minimum

### Focus Indicators
- Visible focus ring on all interactive elements
- Ring color: `hsl(var(--ring))`
- Width: 3px with 20% opacity

### Semantic HTML
- Proper heading hierarchy (h1 → h2 → h3)
- `<nav>` for navigation
- `<aside>` for sidebar
- `<main>` for content area

## Implementation Notes

### CSS Variables Compatibility
Legacy variables are maintained for backward compatibility:
```css
--primary-color: hsl(var(--primary));
--bg-primary: hsl(var(--background));
--text-primary: hsl(var(--foreground));
```

### File Structure
- **dashboard.css**: Core design system + dashboard page
- **analytics.css**: Analytics-specific components
- **campaigns.css**: Campaign management styles
- **targets.css**: Target groups styles
- **email_templates.css**: Template gallery styles
- **login.css**: Login page styles

### Chart.js Integration
Version: 4.4.1 (CDN)
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js"></script>
```

**Theme:**
- Grid lines: `hsl(var(--border))`
- Text color: `hsl(var(--muted-foreground))`
- Tooltips: Custom background matching `hsl(var(--card))`

## Migration from Old Design

### Changes Made
1. **Removed all emoji icons** (🐟📊📧📝👥📈⚙️ℹ️👤)
   - Replaced with minimal Unicode symbols
   
2. **Updated color system**
   - Migrated from hex codes to HSL tokens
   - Implemented semantic color naming
   
3. **Modernized components**
   - Buttons: Removed heavy shadows, added subtle effects
   - Cards: Border-only style instead of drop shadows
   - Tables: Improved row striping and hover states
   
4. **Typography improvements**
   - Added font smoothing
   - Tighter letter spacing on headings
   - Consistent type scale

5. **Enhanced interactions**
   - Smoother transitions (0.15s ease)
   - Better focus states
   - Hover effects on all interactive elements

## Future Enhancements

### Potential Additions
- Dark mode support (duplicate HSL values for dark theme)
- More component variants (ghost buttons, outline buttons)
- Animation library for complex interactions
- Icon library replacement (consider Lucide or Heroicons)
- Custom focus-visible styles for keyboard navigation

### Theme Customization
To create a custom theme, modify the HSL values in `:root`:
```css
:root {
    /* Example: Purple theme */
    --primary: 262.1 83.3% 57.8%;
    --ring: 262.1 83.3% 57.8%;
}
```

---

**Last Updated**: January 2026  
**Design Version**: 2.0  
**Framework**: Vanilla CSS with CSS Custom Properties  
**Inspiration**: shadcn/ui, Radix UI, Tailwind CSS

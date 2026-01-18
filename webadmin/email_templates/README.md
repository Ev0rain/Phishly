# Email Templates

This directory contains HTML email templates used in phishing simulation campaigns.

## Template Variables

Templates can include the following variables that will be replaced during campaign execution:

### User Information
- `{{employee_name}}` - Target employee's full name
- `{{username}}` - Target employee's username
- `{{email}}` - Target employee's email address
- `{{department}}` - Target employee's department

### Company Information
- `{{company_name}}` - Company name
- `{{ceo_name}}` - CEO's name
- `{{manager_name}}` - Manager's name

### Tracking & Links
- `{{tracking_link}}` - Unique tracking link (REQUIRED - used to track clicks)
- `{{unsubscribe_link}}` - Unsubscribe/opt-out link

### Campaign Metadata
- `{{timestamp}}` - Current timestamp
- `{{due_date}}` - Formatted due date
- `{{ip_address}}` - Simulated IP address

## Template Structure

Each email template should be a complete HTML document with inline CSS. External stylesheets and JavaScript are not supported.

### Best Practices

1. **Always include `{{tracking_link}}`** - This is essential for tracking campaign engagement
2. **Use inline CSS** - Email clients don't support external stylesheets
3. **Keep it realistic** - Templates should mimic real phishing attempts
4. **Mobile responsive** - Use max-width and responsive design patterns
5. **Test rendering** - Preview templates before using in campaigns

### Example Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Subject</title>
    <style>
        /* Inline CSS here */
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <div class="content">
        <p>Dear {{employee_name}},</p>
        
        <!-- Email content -->
        
        <a href="{{tracking_link}}">Click Here</a>
    </div>
</body>
</html>
```

## Adding New Templates

### Via Web Interface (Recommended)
1. Navigate to Templates page in admin dashboard
2. Click "Import Template"
3. Fill in template name, subject, and tags
4. Upload HTML file
5. Template will be copied here and added to database

### Manual Addition
1. Create HTML file following best practices above
2. Save to this directory with descriptive filename (lowercase, underscores)
3. Add entry to database (manual process until DB integration complete)

## Template Tags

Use tags to categorize templates for easy filtering:

- **Scenario-based**: `executive`, `financial`, `it-security`, `hr`, `support`
- **Urgency**: `urgent`, `scheduled`, `reminder`
- **Type**: `credentials`, `survey`, `alert`, `policy`, `delivery`
- **Platform**: `microsoft`, `google`, `linkedin`, `social`

## Security Notes

⚠️ **Important**: These templates are for **authorized security awareness testing only**.

- Only use with explicit authorization
- Never send to unauthorized recipients
- Always include opt-out mechanisms
- Comply with organizational policies
- Document all campaign activities

## Example Templates Included

1. **ceo_compromise.html** - CEO email compromise / wire transfer scam
2. **password_reset.html** - IT security password reset request
3. **invoice_request.html** - Overdue invoice payment notice

Additional templates can be imported through the admin interface.

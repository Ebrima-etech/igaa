# Django Admin Styling Configuration
# Add this to admin.py files for professional admin interface

from django.contrib import admin

# Professional Admin Header and Branding
admin.site.site_header = "GIA Hajj Operations - Admin"
admin.site.site_title = "GIA Admin"
admin.site.index_title = "Welcome to Administration"

# Custom CSS for Django Admin
ADMIN_CSS = """
<style>
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #f3f4f6;
        --text: #111827;
        --border: #e5e7eb;
        --success: #22c55e;
    }

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
            sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    #header {
        background: linear-gradient(to right, var(--primary), var(--primary-dark));
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.15);
        padding: 20px 40px;
    }

    #header h1 {
        color: white;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    #header h1 a {
        color: white;
    }

    #header h1 a:hover {
        color: rgba(255, 255, 255, 0.9);
    }

    #branding h2 {
        color: white;
        font-size: 14px;
        font-weight: 500;
        opacity: 0.9;
        margin-top: 10px;
    }

    .module h2 {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 15px 20px;
        font-size: 16px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
    }

    .module {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        margin-bottom: 30px;
        background: white;
    }

    .module table {
        width: 100%;
        border-collapse: collapse;
    }

    .module tbody tr:hover {
        background: var(--secondary);
    }

    .module tbody td {
        padding: 15px 20px;
        border-bottom: 1px solid var(--border);
        color: var(--text);
    }

    .module thead th {
        background: var(--secondary);
        padding: 12px 20px;
        text-align: left;
        font-weight: 600;
        color: var(--text);
        border-bottom: 2px solid var(--border);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    a {
        color: var(--primary);
        text-decoration: none;
    }

    a:hover {
        color: var(--primary-dark);
        text-decoration: underline;
    }

    .button, input[type="submit"], input[type="button"],
    input[type="reset"], button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
    }

    .button:hover, input[type="submit"]:hover, input[type="button"]:hover,
    input[type="reset"]:hover, button:hover {
        background: var(--primary-dark);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .button.default {
        background: var(--secondary);
        color: var(--text);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .button.default:hover {
        background: #e5e7eb;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .success {
        background: var(--success) !important;
    }

    .success:hover {
        background: #16a34a !important;
    }

    input[type="text"], input[type="email"], input[type="password"],
    input[type="date"], input[type="datetime"], input[type="number"],
    input[type="url"], textarea, select {
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 14px;
        font-family: inherit;
        transition: all 0.3s ease;
    }

    input[type="text"]:focus, input[type="email"]:focus, input[type="password"]:focus,
    input[type="date"]:focus, input[type="datetime"]:focus, input[type="number"]:focus,
    input[type="url"]:focus, textarea:focus, select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }

    .fieldset {
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 20px;
        background: white;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text);
    }

    .paginator {
        font-size: 13px;
        margin: 20px 0;
        padding: 20px;
        background: white;
        border: 1px solid var(--border);
        border-radius: 6px;
    }

    .paginator a, .paginator span {
        padding: 8px 12px;
        margin: 0 2px;
    }

    .paginator .this-page {
        background: var(--primary);
        color: white;
        border-radius: 4px;
        padding: 8px 12px;
    }

    .errornote, .notice {
        border-radius: 6px;
        padding: 15px 20px;
        margin-bottom: 20px;
        font-size: 14px;
    }

    .errornote {
        background: #fee2e2;
        border: 1px solid #fca5a5;
        color: #7f1d1d;
    }

    .notice {
        background: #dbeafe;
        border: 1px solid #93c5fd;
        color: #1e3a8a;
    }
</style>
"""

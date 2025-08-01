# BaaS SMS/MCP Server

[![smithery badge](https://smithery.ai/badge/@jjunmomo/baas-mcp)](https://smithery.ai/server/@jjunmomo/baas-mcp)
[![npm version](https://badge.fury.io/js/baas-sms-mcp.svg)](https://badge.fury.io/js/baas-sms-mcp)
[![PyPI version](https://badge.fury.io/py/baas-sms-mcp.svg)](https://badge.fury.io/py/baas-sms-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables Claude to generate SMS/MMS implementation code for your projects. When you ask Claude to implement messaging features, it will generate code that directly calls the BaaS API at `https://api.aiapp.link`, eliminating the need for you to write API integration code manually.

## Features

- **Code Generation**: Claude generates ready-to-use SMS/MMS code for your projects
- **Direct API Integration**: Generated code calls `https://api.aiapp.link` directly
- **Multi-Framework Support**: Generates code for React, Vue, Node.js, Python, Django, and more
- **Complete Implementation**: Includes error handling, validation, and status checking
- **Copy-Paste Ready**: Generated code can be directly copied to your project
- **Project Isolation**: Multi-tenant support with project-based access control
- **Real-time Status**: Code for checking delivery status and message history

## Use Cases

- **Authentication**: SMS verification codes for user registration/login
- **Notifications**: Order confirmations, shipping updates, alerts
- **Marketing**: Promotional messages, event notifications
- **Two-Factor Authentication**: Security verification messages
- **Customer Support**: Automated support messages and updates

## Installation

### Installing via Smithery

To install BaaS SMS/MMS Messaging Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@jjunmomo/baas-mcp):

```bash
npx -y @smithery/cli install @jjunmomo/baas-mcp --client claude
```

### Using npm (Recommended)

```bash
npm install -g baas-sms-mcp
```

Or run directly without installation:
```bash
npx baas-sms-mcp
```

### Using pip

```bash
pip install baas-sms-mcp
```

### From Source

```bash
git clone https://github.com/your-org/baas-sms-mcp.git
cd baas-sms-mcp
npm install

## Configuration

Set the following environment variables:

```bash
export BAAS_API_KEY="your_baas_api_key_here"  
export PROJECT_ID="your_project_uuid_here"
```

Note: `BAAS_API_BASE_URL` is fixed to `https://api.aiapp.link` and doesn't need to be configured.

## Usage

### Command Line

After installation, you can run the server directly:

```bash
baas-sms-mcp
```

### With Claude Desktop

Add this server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "npx",
      "args": ["baas-sms-mcp"],
      "env": {
        "BAAS_API_KEY": "your_api_key",
        "PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

Or if installed globally:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "baas-sms-mcp",
      "env": {
        "BAAS_API_KEY": "your_api_key",
        "PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

### Programmatic Usage

```python
from baas_sms_mcp import main

# Run the MCP server
main()
```

## How It Works

When you ask Claude to implement SMS/MMS features in your project:

1. **You ask:** "Implement SMS verification in my React app"
2. **Claude generates:** Complete code that calls `https://api.aiapp.link` directly
3. **You copy:** The generated code into your project
4. **It works:** Your app sends SMS through BaaS API automatically

## Developer Examples

### Example 1: React SMS Verification

**Prompt to Claude:**
> "Create a React component with SMS verification for user registration"

**Claude will generate code like this (copy-paste ready):**

```javascript
// Backend API endpoint (Express.js)
app.post('/api/send-sms', async (req, res) => {
  const { phoneNumber, message, memberCode } = req.body;
  
  try {
    // Direct call to BaaS API
    const response = await fetch('https://api.aiapp.link/message/sms', {
      method: 'POST',
      headers: {
        'x_api_key': process.env.BAAS_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        recipients: [{ 
          phone_number: phoneNumber, 
          member_code: memberCode || `member_${Date.now()}` 
        }],
        message: message,
        callback_number: "02-1234-5678", // Your business number
        project_id: process.env.PROJECT_ID,
        channel_id: 1 // SMS channel
      })
    });
    
    const result = await response.json();
    res.json(result);
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Frontend React component
import React, { useState } from 'react';

function SMSVerification() {
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState('phone'); // 'phone' or 'verify'

  const sendCode = async () => {
    const verificationCode = Math.floor(100000 + Math.random() * 900000);
    
    const response = await fetch('/api/send-sms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phoneNumber: phone,
        message: `[Your App] 인증번호는 ${verificationCode}입니다. 5분 내에 입력해주세요.`,
        memberCode: 'user_' + Date.now()
      })
    });
    
    const result = await response.json();
    if (result.success) {
      setStep('verify');
      // Store code for verification (use secure storage in production)
      sessionStorage.setItem('verificationCode', verificationCode);
    }
  };

  return (
    <div>
      {step === 'phone' ? (
        <div>
          <input 
            type="tel" 
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="010-1234-5678"
          />
          <button onClick={sendCode}>인증번호 발송</button>
        </div>
      ) : (
        <div>
          <input 
            type="text" 
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="인증번호 입력"
          />
          <button onClick={() => {/* verify logic */}}>인증 확인</button>
        </div>
      )}
    </div>
  );
}
```

### Example 2: Order Confirmation MMS

**Prompt to Claude:**
> "Send MMS with order details and product image when order is placed"

**Claude will generate:**

```python
# Python/Django example
def send_order_confirmation(order_id, customer_phone):
    order = Order.objects.get(id=order_id)
    
    message = f"""
    Order Confirmation #{order.id}
    
    Items: {order.get_items_summary()}
    Total: ${order.total}
    
    Thank you for your order!
    """
    
    # Send MMS with product image
    result = send_mms(
        recipients=[{
            "phone_number": customer_phone,
            "member_code": f"customer_{order.customer.id}"
        }],
        message=message,
        subject="Order Confirmation",
        callback_number="02-1234-5678",
        image_urls=[order.get_product_image_url()]
    )
    
    return result
```

### Example 3: Real-time Status Checking

**Prompt to Claude:**
> "Create a webhook endpoint that checks SMS delivery status"

**Claude will generate:**

```javascript
// Real-time status checking
app.get('/sms-status/:groupId', async (req, res) => {
  const { groupId } = req.params;
  
  try {
    const status = await checkMessageStatus(groupId);
    
    res.json({
      groupId: status.group_id,
      status: status.status,
      delivered: status.success_count,
      failed: status.failed_count,
      pending: status.pending_count,
      messages: status.messages
    });
  } catch (error) {
    res.status(500).json({ error: "Failed to check status" });
  }
});
```

## Available Tools

### 1. send_sms

Send SMS message to one or multiple recipients.

**Parameters:**
- `recipients`: List of recipients with `phone_number` and `member_code`
- `message`: SMS message content (max 2000 characters)
- `callback_number`: Sender callback number
- `project_id`: Project UUID (required)
- `baas_api_key`: BaaS API key for authentication (required)

**Example:**
```python
await send_sms(
    recipients=[
        {"phone_number": "010-1234-5678", "member_code": "user123"}
    ],
    message="Hello, this is a test SMS!",
    callback_number="02-1234-5678"
)
```

**Response:**
```json
{
    "success": true,
    "group_id": 12345,
    "message": "SMS sent successfully",
    "sent_count": 1,
    "failed_count": 0
}
```

### 2. send_mms

Send MMS message with images to one or multiple recipients.

**Parameters:**
- `recipients`: List of recipients with `phone_number` and `member_code`
- `message`: MMS message content (max 2000 characters)
- `subject`: MMS subject line (max 40 characters)
- `callback_number`: Sender callback number
- `image_urls`: List of image URLs to attach (max 5 images, optional)
- `project_id`: Project UUID (optional, uses env var if not provided)

**Example:**
```python
await send_mms(
    recipients=[
        {"phone_number": "010-1234-5678", "member_code": "user123"}
    ],
    message="Check out this image!",
    subject="Image MMS",
    callback_number="02-1234-5678",
    image_urls=["https://example.com/image.jpg"]
)
```

### 3. get_message_status

Get message sending status by group ID.

**Parameters:**
- `group_id`: Message group ID to check status

**Response:**
```json
{
    "group_id": 12345,
    "status": "성공",
    "total_count": 1,
    "success_count": 1,
    "failed_count": 0,
    "pending_count": 0,
    "messages": [
        {
            "phone": "010-1234-5678",
            "name": "홍길동",
            "status": "성공",
            "reason": null
        }
    ]
}
```

### 4. get_send_history

Get message sending history for a project.

**Parameters:**
- `project_id`: Project UUID (optional, uses env var if not provided)
- `offset`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 20, max: 100)
- `message_type`: Filter by message type ("SMS", "MMS", "ALL")

## Error Handling

The server provides comprehensive error handling with the following error codes:

- `MISSING_PROJECT_ID`: PROJECT_ID is required
- `INVALID_RECIPIENTS_COUNT`: Recipients count must be between 1 and 1000
- `MESSAGE_TOO_LONG`: Message length exceeds maximum allowed
- `SUBJECT_TOO_LONG`: Subject length exceeds 40 characters
- `TOO_MANY_IMAGES`: Maximum 5 images allowed for MMS
- `API_ERROR`: External API call failed
- `INTERNAL_ERROR`: Internal server error

## API Integration

This MCP server integrates with the BaaS API endpoints:

- `POST /message/sms` - Send SMS messages
- `POST /message/mms` - Send MMS messages  
- `GET /message/send_history/sms/{group_id}/messages` - Get message status

## Quick Start Templates

### Authentication Service Template

```javascript
// Express.js SMS verification service
const express = require('express');
const app = express();

// Store verification codes (use Redis/Database in production)
const verificationCodes = new Map();

app.post('/send-verification', async (req, res) => {
  const { phoneNumber, memberCode } = req.body;
  const code = Math.floor(100000 + Math.random() * 900000);
  
  // Store code with expiration (5 minutes)
  verificationCodes.set(phoneNumber, {
    code,
    expires: Date.now() + 5 * 60 * 1000
  });
  
  // Claude will use your MCP server to send SMS
  const result = await sendSMS({
    recipients: [{ phone_number: phoneNumber, member_code: memberCode }],
    message: `Your verification code: ${code}`,
    callback_number: "02-1234-5678"
  });
  
  res.json({ success: result.success });
});

app.post('/verify-code', (req, res) => {
  const { phoneNumber, code } = req.body;
  const stored = verificationCodes.get(phoneNumber);
  
  if (stored && stored.code == code && Date.now() < stored.expires) {
    verificationCodes.delete(phoneNumber);
    res.json({ success: true, message: "Verified!" });
  } else {
    res.json({ success: false, message: "Invalid or expired code" });
  }
});
```

### E-commerce Notification Template

```python
# Django e-commerce SMS notifications
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    if created:
        # New order - send confirmation SMS
        send_sms(
            recipients=[{
                "phone_number": instance.customer.phone,
                "member_code": f"customer_{instance.customer.id}"
            }],
            message=f"Order #{instance.id} confirmed! Total: ${instance.total}. We'll notify you when it ships.",
            callback_number="02-1234-5678"
        )
    
    elif instance.status == 'shipped':
        # Order shipped - send tracking SMS with image
        send_mms(
            recipients=[{
                "phone_number": instance.customer.phone,
                "member_code": f"customer_{instance.customer.id}"
            }],
            message=f"Order #{instance.id} shipped! Track: {instance.tracking_number}",
            subject="Order Shipped",
            callback_number="02-1234-5678",
            image_urls=[instance.get_shipping_label_url()]
        )
```

### React Admin Dashboard Template

```jsx
// React component for SMS campaign management
import React, { useState } from 'react';

function SMSCampaign() {
  const [recipients, setRecipients] = useState('');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState(null);

  const sendCampaign = async () => {
    const recipientList = recipients.split('\n').map((line, index) => {
      const [phone, name] = line.split(',');
      return { phone_number: phone.trim(), member_code: name?.trim() || `user_${index}` };
    });

    // Claude will help implement this API call
    const response = await fetch('/api/send-sms-campaign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipients: recipientList,
        message,
        callback_number: "02-1234-5678"
      })
    });

    const result = await response.json();
    setStatus(result);
  };

  return (
    <div className="sms-campaign">
      <h2>SMS Campaign</h2>
      <textarea
        placeholder="Phone numbers (one per line): 010-1234-5678,John"
        value={recipients}
        onChange={(e) => setRecipients(e.target.value)}
      />
      <textarea
        placeholder="Message content"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button onClick={sendCampaign}>Send Campaign</button>
      {status && (
        <div className="status">
          Sent: {status.sent_count}, Failed: {status.failed_count}
        </div>
      )}
    </div>
  );
}
```

## Development

### Installing Development Dependencies

```bash
uv sync --group dev
```

### Code Formatting

```bash
uv run black baas_sms_mcp/
```

### Type Checking

```bash
uv run mypy baas_sms_mcp/
```

### Testing

```bash
uv run pytest
```

### Building Package

```bash
uv build
```

### Publishing to PyPI

```bash
uv publish
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Language

- [English](README.md)
- [한국어](README.ko.md)

## Support

For support and questions, please contact: support@aiapp.link

# Slack Leave Bot

A simple Slack bot that identifies leave and WFH requests and responds with a form link.

## Features

- 🔍 Automatically detects leave requests (vacation, sick leave, time off, etc.)
- 🏠 Identifies Work From Home (WFH) requests
- 📝 Responds with the same form link for both cases
- ☁️ Deploys easily on Vercel (free tier)

## Workflow

```
User Message → Bot Analyzes Keywords → Identifies Type → Responds with Form Link
```

### Supported Keywords

**Leave:**
- leave, off, vacation, holiday, absent
- sick, medical, emergency, PTO, time off
- not coming, won't be in, taking off

**WFH:**
- wfh, work from home, working from home
- remote, home office, working remotely

## Setup Instructions

### 1. Create a Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it "Leave Bot" and select your workspace
4. Go to "OAuth & Permissions" and add these Bot Token Scopes:
   - `chat:write`
   - `app_mentions:read`
   - `channels:history`
   - `groups:history`
   - `im:history`
   - `mpim:history`
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 2. Enable Event Subscriptions

1. In your Slack app settings, go to "Event Subscriptions"
2. Toggle "Enable Events" to ON
3. You'll need to deploy to Vercel first to get the URL (see step 3)
4. Once deployed, set Request URL to: `https://your-app.vercel.app/api/slack`
5. Under "Subscribe to bot events", add:
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
   - `app_mention`
6. Save Changes

### 3. Deploy to Vercel

1. Install Vercel CLI (optional but recommended):
   ```bash
   npm i -g vercel
   ```

2. Clone or create the project directory:
   ```bash
   mkdir slack-leave-bot
   cd slack-leave-bot
   ```

3. Add your files (api/slack.py, vercel.json, requirements.txt)

4. Login to Vercel:
   ```bash
   vercel login
   ```

5. Deploy:
   ```bash
   vercel
   ```

6. Set environment variables in Vercel:
   - Go to your project settings in Vercel dashboard
   - Navigate to "Environment Variables"
   - Add:
     - `SLACK_BOT_TOKEN`: Your Bot User OAuth Token from Slack
     - `FORM_LINK`: Your Google Form or any form URL

   Or set them via CLI:
   ```bash
   vercel env add SLACK_BOT_TOKEN
   vercel env add FORM_LINK
   ```

7. Redeploy to apply environment variables:
   ```bash
   vercel --prod
   ```

### 4. Update Slack Event Subscription URL

1. Copy your Vercel deployment URL (e.g., `https://your-app.vercel.app`)
2. Go back to Slack App settings → Event Subscriptions
3. Set Request URL to: `https://your-app.vercel.app/api/slack`
4. Slack will verify the endpoint (it should show "Verified" ✓)

### 5. Test the Bot

1. Invite the bot to a channel: `/invite @Leave Bot`
2. Send a test message:
   - "I'm taking leave tomorrow"
   - "Working from home today"
   - "@Leave Bot I need to take a day off"

## Project Structure

```
slack-leave-bot/
├── api/
│   └── slack.py          # Main bot logic
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Customization

### Modify Keywords

Edit the `identify_request_type()` function in `api/slack.py`:

```python
leave_keywords = ['your', 'custom', 'keywords']
wfh_keywords = ['your', 'wfh', 'keywords']
```

### Customize Responses

Edit the `generate_response()` function to change the bot's messages.

### Change Form Link

Update the `FORM_LINK` environment variable in Vercel.

## Troubleshooting

### Bot doesn't respond:
- Check if bot is invited to the channel
- Verify `SLACK_BOT_TOKEN` is set correctly in Vercel
- Check Vercel function logs for errors

### "URL verification failed":
- Ensure your Vercel deployment is live
- Check that the endpoint returns the challenge correctly
- Verify the URL is exactly: `https://your-app.vercel.app/api/slack`

### Bot responds to its own messages:
- The code already filters bot messages - check if `bot_id` is present

## Next Steps

- Add a database to track leave requests
- Implement approval workflows
- Add calendar integration
- Send reminders for pending requests
- Add analytics dashboard

## License

MIT

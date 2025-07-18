# Supabase Setup Guide

## 1. Project Creation

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign in with GitHub
4. Click "New project"
5. Fill project details:
   - **Name:** `chatnotepad-backend`
   - **Database Password:** Create a strong password (save it!)
   - **Region:** Europe (West) - Frankfurt
   - **Pricing Plan:** Free tier
6. Click "Create new project"
7. Wait for project setup (2-3 minutes)

## 2. Database Setup

### Step 1: Run SQL Schema
1. Navigate to **SQL Editor** in your Supabase dashboard
2. Click "New query"
3. Copy and paste the contents of `database/schema.sql`
4. Click "Run" to execute

### Step 2: Verify Tables
1. Navigate to **Table Editor**
2. Verify these tables were created:
   - `user_preferences`
   - `command_history`
   - `user_notes`
   - `note_versions`
   - `user_settings`

## 3. Environment Variables Setup

### Step 1: Get API Keys
1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy the following values:
   - **Project URL**
   - **anon (public) key**
   - **service_role (secret) key**

### Step 2: Create .env File
Create a `.env` file in your project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRATION_HOURS=24

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Other configurations
ENVIRONMENT=development
```

### Step 3: Security Notes
- **Never commit** your `.env` file to version control
- **anon key** is safe to use in frontend
- **service_role key** should ONLY be used in backend (has admin privileges)
- Generate a random JWT_SECRET: `openssl rand -base64 32`

## 4. Authentication Setup

### Enable Email Authentication
1. Go to **Authentication** → **Settings**
2. Ensure "Enable email confirmations" is checked
3. Configure email templates if needed

### Configure Auth Providers (Optional)
1. Go to **Authentication** → **Providers**
2. Enable providers you want (Google, GitHub, etc.)

## 5. Row Level Security (RLS)

RLS is automatically enabled with the schema. This ensures:
- Users can only access their own data
- Authentication is required for all operations
- Data is isolated per user

## 6. Testing Setup

### Test Database Connection
Run this in your project:

```bash
pip3 install -r requirements.txt
python3 -c "from app.config.supabase import supabase_config; print('✅ Supabase connection successful!')"
```

### Test Authentication
1. Start your FastAPI server: `uvicorn app.main:app --reload`
2. Go to `http://localhost:8000/docs`
3. Test the `/auth/signup` endpoint
4. Test the `/auth/signin` endpoint

## 7. Production Setup

### Environment Variables
Set these in your production environment:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `JWT_SECRET`
- `OPENAI_API_KEY`

### Database Backup
1. Go to **Settings** → **Database**
2. Enable automated backups
3. Set backup retention period

## 8. Monitoring

### Database Usage
- Monitor in **Settings** → **Usage**
- Track API requests, database size, bandwidth

### Authentication Metrics
- Monitor in **Authentication** → **Users**
- Track signups, active users, sessions

## Troubleshooting

### Common Issues

1. **Connection Error:**
   - Check SUPABASE_URL format
   - Verify project is not paused (free tier)

2. **Authentication Fails:**
   - Verify SUPABASE_ANON_KEY is correct
   - Check if email confirmation is required

3. **Permission Denied:**
   - Verify RLS policies are correctly applied
   - Check if user is authenticated

4. **Service Role Issues:**
   - Verify SUPABASE_SERVICE_ROLE_KEY is correct
   - Only use service role in backend

### Support
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
- [GitHub Issues](https://github.com/supabase/supabase/issues)
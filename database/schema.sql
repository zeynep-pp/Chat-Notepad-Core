-- ChatNotePad.Ai Database Schema
-- Run this SQL in Supabase SQL Editor

-- ============================================
-- User Preferences Table
-- ============================================
CREATE TABLE user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one preferences record per user
    UNIQUE(user_id)
);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Command History Table
-- ============================================
CREATE TABLE command_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    command TEXT NOT NULL,
    input_text TEXT NOT NULL,
    output_text TEXT,
    agent_used VARCHAR(50),
    success BOOLEAN DEFAULT true,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes separately
CREATE INDEX idx_command_history_user_id ON command_history (user_id);
CREATE INDEX idx_command_history_created_at ON command_history (created_at);

-- ============================================
-- User Notes Table
-- ============================================
CREATE TABLE user_notes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    is_favorite BOOLEAN DEFAULT false,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes separately
CREATE INDEX idx_user_notes_user_id ON user_notes (user_id);
CREATE INDEX idx_user_notes_created_at ON user_notes (created_at);
CREATE INDEX idx_user_notes_is_favorite ON user_notes (is_favorite);

-- Add updated_at trigger for notes
CREATE TRIGGER update_user_notes_updated_at
    BEFORE UPDATE ON user_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Note Versions Table (for version history)
-- ============================================
CREATE TABLE note_versions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    note_id UUID NOT NULL REFERENCES user_notes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    change_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(note_id, version_number)
);

-- Create indexes separately
CREATE INDEX idx_note_versions_note_id ON note_versions (note_id);
CREATE INDEX idx_note_versions_user_id ON note_versions (user_id);
CREATE INDEX idx_note_versions_created_at ON note_versions (created_at);

-- ============================================
-- User Settings Table (extended settings)
-- ============================================
CREATE TABLE user_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    setting_key VARCHAR(100) NOT NULL,
    setting_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique settings per user
    UNIQUE(user_id, setting_key)
);

-- Create indexes separately
CREATE INDEX idx_user_settings_user_id ON user_settings (user_id);

-- Add updated_at trigger for settings
CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON user_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Row Level Security (RLS) Policies
-- ============================================

-- Enable RLS on all tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE command_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- User Preferences Policies
CREATE POLICY "Users can view their own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own preferences" ON user_preferences
    FOR DELETE USING (auth.uid() = user_id);

-- Command History Policies
CREATE POLICY "Users can view their own command history" ON command_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own command history" ON command_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User Notes Policies
CREATE POLICY "Users can view their own notes" ON user_notes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own notes" ON user_notes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own notes" ON user_notes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own notes" ON user_notes
    FOR DELETE USING (auth.uid() = user_id);

-- Note Versions Policies
CREATE POLICY "Users can view their own note versions" ON note_versions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own note versions" ON note_versions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User Settings Policies
CREATE POLICY "Users can view their own settings" ON user_settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own settings" ON user_settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own settings" ON user_settings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own settings" ON user_settings
    FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- Additional Tables for Advanced Features
-- ============================================

-- Team/Collaboration Management
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member', -- owner, admin, member, viewer
    permissions JSONB DEFAULT '{}',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- Real-time Collaboration
CREATE TABLE note_collaborations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES user_notes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cursor_position INTEGER DEFAULT 0,
    selection_start INTEGER DEFAULT 0,
    selection_end INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(note_id, user_id)
);

CREATE TABLE collaboration_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id UUID NOT NULL REFERENCES user_notes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    operation_type VARCHAR(20) NOT NULL, -- insert, delete, retain
    position INTEGER NOT NULL,
    content TEXT,
    length INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Plugin System
CREATE TABLE plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plugin_id UUID NOT NULL REFERENCES plugins(id) ON DELETE CASCADE,
    config JSONB DEFAULT '{}',
    is_enabled BOOLEAN DEFAULT true,
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, plugin_id)
);

-- Rate Limiting
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    requests_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    window_duration INTEGER DEFAULT 3600, -- seconds
    max_requests INTEGER DEFAULT 100,
    UNIQUE(user_id, endpoint)
);

-- AI Configurations
CREATE TABLE ai_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- openai, anthropic, google, etc
    model VARCHAR(100) NOT NULL,
    config JSONB DEFAULT '{}',
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cloud Storage Integrations
CREATE TABLE storage_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- dropbox, gdrive, onedrive, etc
    access_token TEXT,
    refresh_token TEXT,
    config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Context & Suggestions
CREATE TABLE suggestion_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    context_type VARCHAR(50) NOT NULL, -- command, content, style
    context_data JSONB NOT NULL,
    frequency INTEGER DEFAULT 1,
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Create indexes for performance
-- ============================================
CREATE INDEX idx_teams_owner_id ON teams (owner_id);
CREATE INDEX idx_team_members_team_id ON team_members (team_id);
CREATE INDEX idx_team_members_user_id ON team_members (user_id);
CREATE INDEX idx_note_collaborations_note_id ON note_collaborations (note_id);
CREATE INDEX idx_note_collaborations_user_id ON note_collaborations (user_id);
CREATE INDEX idx_collaboration_operations_note_id ON collaboration_operations (note_id);
CREATE INDEX idx_user_plugins_user_id ON user_plugins (user_id);
CREATE INDEX idx_rate_limits_user_id ON rate_limits (user_id);
CREATE INDEX idx_ai_configs_user_id ON ai_configs (user_id);
CREATE INDEX idx_storage_configs_user_id ON storage_configs (user_id);
CREATE INDEX idx_suggestion_contexts_user_id ON suggestion_contexts (user_id);

-- ============================================
-- Add updated_at triggers
-- ============================================
CREATE TRIGGER update_teams_updated_at
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plugins_updated_at
    BEFORE UPDATE ON plugins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_configs_updated_at
    BEFORE UPDATE ON ai_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_storage_configs_updated_at
    BEFORE UPDATE ON storage_configs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Row Level Security for new tables
-- ============================================

-- Enable RLS on all new tables
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE note_collaborations ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaboration_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE plugins ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_plugins ENABLE ROW LEVEL SECURITY;
ALTER TABLE rate_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE suggestion_contexts ENABLE ROW LEVEL SECURITY;

-- Teams Policies
CREATE POLICY "Users can view teams they own or are members of" ON teams
    FOR SELECT USING (
        auth.uid() = owner_id OR 
        EXISTS (
            SELECT 1 FROM team_members 
            WHERE team_id = teams.id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create teams" ON teams
    FOR INSERT WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Team owners can update their teams" ON teams
    FOR UPDATE USING (auth.uid() = owner_id);

CREATE POLICY "Team owners can delete their teams" ON teams
    FOR DELETE USING (auth.uid() = owner_id);

-- Team Members Policies
CREATE POLICY "Users can view team members for teams they belong to" ON team_members
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM teams 
            WHERE id = team_id AND (
                owner_id = auth.uid() OR 
                EXISTS (SELECT 1 FROM team_members WHERE team_id = teams.id AND user_id = auth.uid())
            )
        )
    );

-- User Plugins Policies
CREATE POLICY "Users can manage their own plugins" ON user_plugins
    FOR ALL USING (auth.uid() = user_id);

-- Rate Limits Policies
CREATE POLICY "Users can view their own rate limits" ON rate_limits
    FOR SELECT USING (auth.uid() = user_id);

-- AI Configs Policies
CREATE POLICY "Users can manage their own AI configs" ON ai_configs
    FOR ALL USING (auth.uid() = user_id);

-- Storage Configs Policies
CREATE POLICY "Users can manage their own storage configs" ON storage_configs
    FOR ALL USING (auth.uid() = user_id);

-- Suggestion Contexts Policies
CREATE POLICY "Users can manage their own suggestion contexts" ON suggestion_contexts
    FOR ALL USING (auth.uid() = user_id);

-- ============================================
-- Sample Data (Optional)
-- ============================================

-- Insert default preferences for all existing users
INSERT INTO user_preferences (user_id, preferences)
SELECT 
    id,
    '{"theme": "light", "language": "en", "editor_settings": {}, "command_history_enabled": true, "auto_save_enabled": true}'::jsonb
FROM auth.users
ON CONFLICT (user_id) DO NOTHING;
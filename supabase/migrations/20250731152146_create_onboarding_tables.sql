-- Create onboarding related tables for Aura application

-- 3.2 虚拟形象表设计 (avatars)
CREATE TABLE IF NOT EXISTS avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    image_url TEXT,
    abilities JSONB,
    initial_dialogue_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3.1 用户 Profile 表设计 (profiles)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    nickname TEXT,
    gender TEXT CHECK (gender IN ('male', 'female', 'secret', 'lgbtq+')),
    birth_year INTEGER,
    birth_month INTEGER,
    birth_day INTEGER,
    birth_hour INTEGER,
    birth_minute INTEGER,
    birth_second INTEGER,
    birth_location TEXT,
    birth_longitude NUMERIC,
    birth_latitude NUMERIC,
    selected_avatar_id UUID REFERENCES avatars(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3.3 用户画像分析结果表设计 (user_profiles_analysis)
CREATE TABLE IF NOT EXISTS user_profiles_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3.7 他人 Profile 表设计 (other_profiles)
CREATE TABLE IF NOT EXISTS other_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    gender TEXT CHECK (gender IN ('male', 'female', 'secret', 'lgbtq+')),
    birth_year INTEGER,
    birth_month INTEGER,
    birth_day INTEGER,
    birth_hour INTEGER,
    birth_minute INTEGER,
    birth_second INTEGER,
    birth_location TEXT,
    birth_longitude NUMERIC,
    birth_latitude NUMERIC,
    relation_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default avatars
INSERT INTO avatars (name, description, image_url, abilities, initial_dialogue_prompt) VALUES
(
    '星语者·小满',
    '温柔而智慧的星相导师，擅长通过星盘解读人生密码，给予温暖的指引。',
    '/avatars/xiaoman.png',
    '["星座分析", "生辰八字", "人际关系", "情感咨询"]'::jsonb,
    '你好呀，我是小满~✨ 很高兴遇见你！我是一位星语者，专门帮助大家通过星相了解自己的内心世界。你想聊聊什么呢？'
),
(
    '塔罗师·月影',
    '神秘的塔罗牌大师，通过古老的智慧为迷茫的灵魂指引方向。',
    '/avatars/yueying.png',
    '["塔罗占卜", "灵性指导", "直觉洞察", "人生指引"]'::jsonb,
    '欢迎来到神秘的塔罗世界，我是月影。🌙 在这里，每一张牌都承载着宇宙的智慧。有什么困惑想要寻求答案吗？'
),
(
    '易学士·天机',
    '深谙易经之道的智者，运用古老的东方智慧解答人生疑惑。',
    '/avatars/tianji.png',
    '["易经卜卦", "五行分析", "运势预测", "传统文化"]'::jsonb,
    '道法自然，易理通达。我是天机，一位研习易学多年的学者。😌 让我们一起探索命运的奥秘吧！'
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE other_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for profiles table
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Create policies for user_profiles_analysis table
CREATE POLICY "Users can view own analysis" ON user_profiles_analysis
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analysis" ON user_profiles_analysis
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policies for other_profiles table
CREATE POLICY "Users can view own other profiles" ON other_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own other profiles" ON other_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own other profiles" ON other_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own other profiles" ON other_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- Avatars table is public readable
CREATE POLICY "Avatars are publicly readable" ON avatars
    FOR SELECT USING (true);

-- Create indexes for better performance
CREATE INDEX idx_profiles_user_id ON profiles(id);
CREATE INDEX idx_profiles_avatar_id ON profiles(selected_avatar_id);
CREATE INDEX idx_user_profiles_analysis_user_id ON user_profiles_analysis(user_id);
CREATE INDEX idx_other_profiles_user_id ON other_profiles(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_avatars_updated_at BEFORE UPDATE ON avatars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_analysis_updated_at BEFORE UPDATE ON user_profiles_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_other_profiles_updated_at BEFORE UPDATE ON other_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

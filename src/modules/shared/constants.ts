export const VALID_CATEGORIES = [
  'Technology', 'Business', 'Finance', 'Productivity',
  'Education', 'Career', 'Marketing', 'Health',
  'Entertainment', 'Lifestyle',
] as const

export const TAG_MIN_COUNT = 5
export const TAG_MAX_COUNT = 10
export const SUMMARY_MAX_LENGTH = 500
export const TAKEAWAY_MAX_COUNT = 5

export const CATEGORY_KEYWORDS: Record<string, string[]> = {
  Technology: [
    'software', 'code', 'programming', 'app', 'web', 'api', 'cloud',
    'data', 'algorithm', 'javascript', 'python', 'react', 'database',
    'server', 'frontend', 'backend', 'devops', 'docker', 'kubernetes',
    'ai', 'machine learning', 'blockchain', 'cybersecurity',
  ],
  Business: [
    'startup', 'entrepreneur', 'saas', 'revenue', 'growth',
    'business model', 'marketing strategy', 'fundraising', 'pitch',
    'venture capital', 'acquisition', 'market', 'b2b', 'b2c',
  ],
  Finance: [
    'investing', 'stock', 'trading', 'crypto', 'bitcoin', 'portfolio',
    'etf', 'dividend', 'retirement', 'tax', 'budget', 'saving',
    'wealth', 'financial planning', 'economy', 'inflation',
  ],
  Productivity: [
    'productivity', 'time management', 'habit', 'focus', 'workflow',
    'organization', 'gtd', 'todo', 'efficiency', 'automation',
    'second brain', 'note-taking', 'project management',
  ],
  Education: [
    'course', 'tutorial', 'learn', 'study', 'lesson', 'class',
    'online learning', 'certification', 'degree', 'mooc',
    'skill', 'training', 'workshop', 'bootcamp',
  ],
  Career: [
    'career', 'job', 'interview', 'resume', 'salary', 'promotion',
    'remote work', 'freelance', 'networking', 'leadership',
    'professional development', 'work-life balance',
  ],
  Marketing: [
    'seo', 'content marketing', 'social media', 'branding',
    'digital marketing', 'email marketing', 'conversion',
    'analytics', 'advertising', 'campaign', 'growth hacking',
  ],
  Health: [
    'health', 'wellness', 'nutrition', 'exercise', 'mental health',
    'meditation', 'sleep', 'fitness', 'yoga', 'diet',
    'healthcare', 'medical', 'immunity', 'stress',
  ],
  Entertainment: [
    'movie', 'film', 'music', 'game', 'tv show', 'netflix',
    'youtube', 'podcast', 'celebrity', 'comedy', 'anime',
    'streaming', 'concert', 'review',
  ],
  Lifestyle: [
    'travel', 'minimalism', 'design', 'fashion', 'food',
    'photography', 'home', 'garden', 'pet', 'hobby',
    'relationship', 'parenting', 'self-care',
  ],
}

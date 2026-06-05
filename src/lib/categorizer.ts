const categoryRules: { category: string; keywords: string[] }[] = [
  {
    category: 'DevOps',
    keywords: [
      'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins',
      'ci/cd', 'continuous integration', 'continuous deployment',
      'github actions', 'gitlab ci', 'devops', 'helm', 'istio',
      'prometheus', 'grafana', 'elk stack', 'vagrant', 'puppet', 'chef',
    ],
  },
  {
    category: 'MLOps',
    keywords: [
      'mlops', 'kubeflow', 'mlflow', 'dvc', 'feature store',
      'model deployment', 'model serving', 'model registry',
      'pipeline', 'torchserve', 'triton', 'onnx', 'ml pipeline',
      'data pipeline', 'feature engineering',
    ],
  },
  {
    category: 'Cloud',
    keywords: [
      'aws', 'azure', 'gcp', 'google cloud', 'amazon web services',
      'lambda', 'ec2', 's3', 'cloud function', 'serverless',
      'cloud run', 'cloud storage', 'cloud computing', 'vpc',
      'cloudformation', 'pulumi', 'cloud native',
    ],
  },
  {
    category: 'Data Science',
    keywords: [
      'data science', 'data analysis', 'data visualization',
      'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn',
      'jupyter', 'notebook', 'data mining', 'statistics',
      'regression', 'classification', 'clustering',
      'dimensionality reduction', 'data wrangling',
    ],
  },
  {
    category: 'Machine Learning',
    keywords: [
      'machine learning', 'deep learning', 'neural network',
      'supervised learning', 'unsupervised learning', 'reinforcement learning',
      'cnn', 'rnn', 'lstm', 'transformer', 'attention mechanism',
      'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'xgboost',
      'lightgbm', 'catboost', 'random forest', 'svm', 'gradient boosting',
      'hyperparameter', 'cross-validation', 'overfitting', 'underfitting',
      'loss function', 'backpropagation', 'embedding', 'tokenizer',
      'llm', 'large language model', 'gpt', 'bert', 'diffusion model',
      'gan', 'autoencoder', 'transfer learning', 'fine-tuning',
    ],
  },
  {
    category: 'AI',
    keywords: [
      'artificial intelligence', 'chatgpt', 'prompt engineering',
      'ai agent', 'ai assistant', 'computer vision', 'nlp',
      'natural language processing', 'speech recognition',
      'image recognition', 'object detection', 'semantic segmentation',
      'pose estimation', 'ocr', 'chatbot', 'rag', 'retrieval augmented',
      'generative ai', 'ai ethics', 'responsible ai', 'hallucination',
      'chain-of-thought', 'vector database', 'embeddings', 'semantic search',
      'langchain', 'llamaindex', 'autogpt', 'function calling',
      'multimodal', 'vision transformer', 'yolo', 'stable diffusion',
      'midjourney', 'dall-e', 'whisper', 'tts', 'text-to-speech',
    ],
  },
  {
    category: 'Programming',
    keywords: [
      'python', 'javascript', 'typescript', 'rust', 'golang', 'go ',
      'java', 'c++', 'c#', 'ruby', 'swift', 'kotlin', 'scala',
      'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt',
      'node.js', 'deno', 'bun', 'express', 'django', 'flask',
      'fastapi', 'spring boot', 'asp.net', 'rails', 'laravel',
      'tailwind', 'bootstrap', 'css', 'html', 'sql', 'nosql',
      'postgresql', 'mongodb', 'redis', 'graphql', 'rest api',
      'grpc', 'websocket', 'microservice', 'algorithm', 'data structure',
      'leetcode', 'coding', 'programming', 'software engineering',
      'clean code', 'design pattern', 'solid', 'tdd', 'testing',
      'jest', 'pytest', 'git', 'web development', 'frontend', 'backend',
      'full stack', 'api', 'sdk', 'compiler', 'debugging', 'refactoring',
    ],
  },
  {
    category: 'Finance',
    keywords: [
      'stock', 'trading', 'investment', 'investing', 'crypto',
      'bitcoin', 'ethereum', 'blockchain', 'defi', 'nft',
      'personal finance', 'budget', 'saving', 'retirement',
      'mortgage', 'loan', 'credit', 'tax', 'accounting',
      'financial planning', 'wealth management', 'dividend',
      'forex', 'options trading', 'market analysis', 'economy',
      'inflation', 'recession', 'bull market', 'bear market',
      'portfolio', 'asset allocation', 'risk management',
    ],
  },
  {
    category: 'Business',
    keywords: [
      'business', 'startup', 'entrepreneur', 'saas', 'b2b', 'b2c',
      'growth hacking', 'marketing', 'sales', 'leadership',
      'management', 'strategy', 'business model', 'revenue',
      'fundraising', 'venture capital', 'angel investor', 'pitch',
      'product market fit', 'go to market', 'customer acquisition',
      'retention', 'churn', 'unit economics', 'lifetime value',
      'acquisition cost', 'pivot', 'scaling', 'operations',
      'supply chain', 'logistics', 'ecommerce', 'd2c',
    ],
  },
  {
    category: 'Productivity',
    keywords: [
      'productivity', 'time management', 'gtd', 'getting things done',
      'pomodoro', 'habit', 'routine', 'focus', 'deep work',
      'todo', 'task management', 'project management', 'agile',
      'scrum', 'kanban', 'jira', 'notion', 'obsidian', 'roam',
      'second brain', 'knowledge management', 'note-taking',
      'eisenhower matrix', 'atomic habits', 'morning routine',
      'goals', 'okr', 'prioritization', 'procrastination',
    ],
  },
  {
    category: 'Career',
    keywords: [
      'career', 'job', 'interview', 'resume', 'cv', 'linkedin',
      'networking', 'salary', 'negotiation', 'promotion',
      'career change', 'remote work', 'freelance', 'contractor',
      'side project', 'portfolio', 'personal brand', 'mentorship',
      'professional development', 'upskilling', 'layoff',
      'job search', 'hiring', 'recruiting', 'work-life balance',
      'burnout', 'impostor syndrome',
    ],
  },
  {
    category: 'Health',
    keywords: [
      'health', 'mental health', 'anxiety', 'depression', 'therapy',
      'meditation', 'mindfulness', 'sleep', 'nutrition', 'diet',
      'wellness', 'wellbeing', 'healthcare', 'medical', 'disease',
      'symptom', 'treatment', 'medicine', 'doctor', 'hospital',
      'immune', 'vitamin', 'supplement', 'yoga', 'stress',
      'self-care', 'recovery', 'addiction',
    ],
  },
  {
    category: 'Fitness',
    keywords: [
      'workout', 'exercise', 'gym', 'fitness', 'running', 'jogging',
      'cycling', 'swimming', 'weight training', 'strength training',
      'hiit', 'cardio', 'calisthenics', 'bodybuilding',
      'muscle', 'protein', 'pre-workout', 'crossfit', 'pilates',
      'stretching', 'mobility', 'marathon', 'triathlon',
      'personal trainer', 'fitness tracker', 'steps',
    ],
  },
  {
    category: 'Relationships',
    keywords: [
      'relationship', 'dating', 'marriage', 'partner', 'love',
      'communication', 'conflict resolution', 'attachment',
      'intimacy', 'trust', 'boundary', 'breakup', 'divorce',
      'family', 'parenting', 'friendship', 'social skills',
      'empathy', 'listening', 'couples therapy',
    ],
  },
  {
    category: 'Education',
    keywords: [
      'course', 'tutorial', 'lesson', 'class', 'lecture',
      'university', 'college', 'school', 'degree', 'certification',
      'online learning', 'mooc', 'coursera', 'udemy', 'edx',
      'study', 'exam', 'test prep', 'homework', 'assignment',
      'scholarship', 'student', 'teacher', 'professor',
      'learning', 'skill', 'knowledge', 'textbook', 'curriculum',
      'bootcamp', 'workshop', 'webinar',
    ],
  },
  {
    category: 'Entertainment',
    keywords: [
      'movie', 'film', 'tv show', 'series', 'netflix', 'disney+',
      'hbo', 'hulu', 'amazon prime', 'anime', 'cartoon',
      'music', 'song', 'album', 'concert', 'festival',
      'comedy', 'stand-up', 'podcast', 'youtube video',
      'celebrity', 'actor', 'actress', 'director', 'review',
      'trailer', 'documentary', 'reality show', 'talk show',
      'vlog', 'influencer', 'tiktok', 'trending',
    ],
  },
  {
    category: 'Gaming',
    keywords: [
      'game', 'gaming', 'video game', 'pc game', 'console',
      'playstation', 'xbox', 'nintendo', 'steam', 'epic games',
      'rpg', 'fps', 'mmo', 'battle royale', 'open world',
      'minecraft', 'fortnite', 'call of duty', 'gta', 'league of legends',
      'valorant', 'counter-strike', 'dota', 'overwatch',
      'esports', 'streamer', 'twitch', 'speedrun', 'walkthrough',
      'gameplay', 'mod', 'indie game', 'mobile game',
    ],
  },
  {
    category: 'Travel',
    keywords: [
      'travel', 'trip', 'vacation', 'holiday', 'destination',
      'hotel', 'flight', 'airbnb', 'backpacking', 'road trip',
      'solo travel', 'adventure', 'explore', 'wanderlust',
      'passport', 'visa', 'itinerary', 'travel guide',
      'hiking', 'camping', 'beach', 'mountain', 'city break',
      'travel tips', 'nomad', 'digital nomad',
    ],
  },
  {
    category: 'News',
    keywords: [
      'breaking news', 'latest', 'update', 'report', 'headline',
      'politics', 'election', 'policy', 'legislation', 'government',
      'world news', 'local news', 'climate', 'environment',
      'technology news', 'science news', 'space news',
      'alert', 'coverage', 'investigation', 'journalism',
    ],
  },
]

function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace('www.', '')
  } catch {
    return url
  }
}

export function categorize(title: string, url: string): string {
  const text = `${title} ${getDomain(url)}`.toLowerCase()

  for (const rule of categoryRules) {
    for (const keyword of rule.keywords) {
      if (text.includes(keyword)) {
        return rule.category
      }
    }
  }

  if (/\.(org|edu|gov)\b/.test(getDomain(url))) return 'Education'
  if (/(youtube\.com|youtu\.be)/i.test(url)) return 'Entertainment'

  return 'Other'
}

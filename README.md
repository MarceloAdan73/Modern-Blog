# 🚀 Modern Blog Platform

> **Developed with AI Assistance** 🤖 + **Human Expertise** 👨‍💻

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue%20JS-3.0-4FC08D.svg)](https://vuejs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.3-38B2AC.svg)](https://tailwindcss.com/)
[![GraphQL](https://img.shields.io/badge/GraphQL-Strawberry-E10098.svg)](https://strawberry.rocks/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-336791.svg)](https://www.postgresql.org/)

A full-stack blogging platform built with **FastAPI** for the backend and **Vue 3** for a modern reactive frontend, featuring a stunning glassmorphism UI with dark/light theme support and an integrated **GraphQL Explorer**.

---

## 🌐 Live Application

| Service | URL |
|---------|-----|
| **🔗 Live App** | [https://modern-blog-tkzl.onrender.com/](https://modern-blog-tkzl.onrender.com/) |
| **📚 REST API Docs** | [https://modern-blog-tkzl.onrender.com/docs](https://modern-blog-tkzl.onrender.com/docs) |
| **🔷 GraphQL Playground** | [https://modern-blog-tkzl.onrender.com/graphql](https://modern-blog-tkzl.onrender.com/graphql) |

### Application Screenshots

![Modern Blog - Dark Theme](static/images/screenshot1.png)

![Post Management Interface](static/images/screenshot2.png)

---

## ✨ Features

### 🔐 Authentication & Users
- User registration with validation
- Secure login with password hashing (Werkzeug)
- Profile management (name, bio, location, website)
- Account deletion with cascade post removal

### 📝 Post Management
- Create, read, update, delete posts
- Status workflow: **Published**, **Draft**, **Review**, **Archived**
- Tag system (up to 5 tags per post)
- Word count and excerpt generation
- Content editor with character limits

### 📊 Dashboard & Analytics
- Platform-wide statistics (total users, posts)
- Most active user tracking
- User statistics (post count, word count, average words)
- Last post date tracking

### 🔍 Search & Discovery
- Real-time search with autocomplete
- Result highlighting
- Post filtering by status
- Demo content fallback when database is empty

### 🔷 GraphQL API
- Full CRUD operations via GraphQL
- Interactive GraphQL Explorer in frontend
- Strawberry GraphQL with type safety
- GraphiQL IDE integrated

### 🎨 Frontend & UX
- **🌙🌞 Dark/Light Theme** - Persistent toggle with localStorage
- **✨ Glassmorphism UI** - Frosted glass aesthetic with backdrop blur
- **🎨 Gradient Backgrounds** - Animated particle effects
- **📱 Fully Responsive** - Optimized for desktop, tablet, and mobile
- **🔔 Toast Notifications** - Non-intrusive feedback system
- **⬆️ Scroll to Top** - Floating navigation button
- **💫 Smooth Animations** - Vue transition effects throughout

---

## 🛠 Technology Stack

### Backend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.100.0 |
| ORM | SQLAlchemy | 1.4.46 |
| Server | Uvicorn | 0.23.2 |
| GraphQL | Strawberry | Latest |
| Validation | Pydantic | (bundled) |
| Security | Werkzeug | 2.3.7 |
| Runtime | Python | 3.11.9 |

### Frontend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Vue 3 (CDN) | Composition API |
| Styling | Tailwind CSS | 3.3.0 |
| Icons | Font Awesome | 6.0.0 |
| Fonts | Google Fonts | Oswald + Poppins |

### Database
| Environment | Engine | Notes |
|-------------|--------|-------|
| Development | SQLite | Local `blog.db` |
| Production | PostgreSQL | Render.com managed |

### Deployment
| Service | Configuration |
|---------|---------------|
| Platform | Render.com |
| Runtime | Python 3.11 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python main.py` |
| Auto-deploy | GitHub integration |

---

## 🏗 Project Structure

```
modern-blog/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration (SQLite/PostgreSQL)
├── graphql_schema.py    # Strawberry GraphQL schema (CRUD)
├── requirements.txt     # Python dependencies
├── runtime.txt          # Python version (3.11.9)
├── build.sh             # Build script for Render
├── .env                 # Environment variables
├── models/
│   ├── models.py        # SQLAlchemy models (User, Post)
│   └── schemas.py       # Pydantic schemas for validation
├── templates/
│   └── index.html       # Single Page Application (Vue 3)
└── static/
    ├── favicon.ico
    └── images/          # Screenshots and assets
```

---

## 📦 REST API

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/profile` | Update profile |
| DELETE | `/api/auth/profile` | Delete account |

### Post Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | List all posts |
| POST | `/api/posts` | Create new post |
| GET | `/api/posts/my-posts` | Get user's posts |
| GET | `/api/posts/{id}` | Get specific post |
| PUT | `/api/posts/{id}` | Update post |
| DELETE | `/api/posts/{id}` | Delete post |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Platform statistics |
| GET | `/api/users/{id}/stats` | User statistics |

---

## 🔷 GraphQL API

### Endpoint
- **URL:** `/graphql`
- **IDE:** GraphiQL (built-in)

### Queries
```graphql
{
  posts {
    id
    title
    content
    excerpt
    status
    tags
    authorName
    createdAt
  }
}
```

### Mutations

**Create Post**
```graphql
mutation {
  createPost(postData: {
    title: "My New Post"
    content: "Post content here..."
    excerpt: "Brief description"
    status: "Published"
    tags: "[\"tech\", \"news\"]"
    authorName: "John Doe"
  }) {
    id
    title
    status
    createdAt
  }
}
```

**Update Post**
```graphql
mutation {
  updatePost(id: 1, postData: {
    title: "Updated Title"
    status: "Published"
  }) {
    id
    title
    status
  }
}
```

**Delete Post**
```graphql
mutation {
  deletePost(id: 1)
}
```

### GraphQL Explorer
The frontend includes an interactive **GraphQL Explorer** accessible from the Dashboard Metrics panel after login:
- Query editor with syntax highlighting
- Variables input (JSON format)
- Real-time result display
- Pre-loaded example queries
- Error handling display

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/MarceloAdan73/Modern-Blog.git
cd Modern-Blog

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The application will be available at `http://localhost:10000`

### Demo Credentials
| Field | Value |
|-------|-------|
| Username | `user` |
| Password | `123456` |

---

## 🌍 Deployment

### Render.com Configuration
1. Connect your GitHub repository
2. Configure the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Environment:** Python 3.11
3. Add PostgreSQL database (optional, uses SQLite locally)
4. Enable auto-deploy from main branch

The application automatically detects PostgreSQL connection strings and switches from SQLite accordingly.

---

## 🔄 Development Journey

| Milestone | Status |
|-----------|--------|
| FastAPI backend with SQLAlchemy ORM | ✅ Complete |
| User authentication system | ✅ Complete |
| Post CRUD with status workflow | ✅ Complete |
| Tag system | ✅ Complete |
| Dashboard analytics | ✅ Complete |
| Glassmorphism UI with dark/light theme | ✅ Complete |
| GraphQL API with Strawberry | ✅ Complete |
| Interactive GraphQL Explorer | ✅ Complete |
| Render.com deployment | ✅ Complete |
| Real-time search | ✅ Complete |

---

## 👨‍💻 Developer

**Marcelo**  
[![GitHub](https://img.shields.io/badge/GitHub-MarceloAdan73-181717.svg)](https://github.com/MarceloAdan73)

---

*"This project showcases how AI can accelerate development while maintaining code quality and architectural integrity."*

⭐ Star this repo if you found it helpful!

| Links | |
|-------|---|
| 🚀 [Live Demo](https://modern-blog-tkzl.onrender.com/) | 📚 [API Docs](https://modern-blog-tkzl.onrender.com/docs) |
| 🔷 [GraphQL](https://modern-blog-tkzl.onrender.com/graphql) | 🐛 [Report Issue](https://github.com/MarceloAdan73/Modern-Blog/issues) |

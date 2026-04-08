# 🚀 Modern Blog Platform

> **Developed with AI Assistance** 🤖 + **Human Expertise** 👨‍💻

A full-stack blogging platform built with **FastAPI** for the backend and **Vue 3** for a modern reactive frontend, featuring a stunning glassmorphism UI with dark/light theme support and an integrated **GraphQL Explorer**.

---

## 🌐 Live Application

**🔗 Live URL:** [https://modern-blog-tkzl.onrender.com/](https://modern-blog-tkzl.onrender.com/)  
**📚 API Documentation (Swagger):** [https://modern-blog-tkzl.onrender.com/docs](https://modern-blog-tkzl.onrender.com/docs)  
**🔷 GraphQL Playground:** [https://modern-blog-tkzl.onrender.com/graphql](https://modern-blog-tkzl.onrender.com/graphql)

### Application Screenshots

![Modern Blog - Dark Theme](static/images/screenshot1.png)

![Post Management Interface](static/images/screenshot2.png)

---

## ✨ Key Features

### Core Functionality
- **🔐 User Authentication** - Register, login, profile management
- **📝 Post Management** - Create, read, update, delete posts with status workflow (Published, Draft, Review, Archived)
- **🏷️ Tag System** - Organize posts with up to 5 tags each
- **📊 Dashboard Analytics** - Platform and user statistics
- **🔍 Real-time Search** - Instant search with autocomplete and result highlighting

### API & Backend
- **REST API** - Full CRUD operations with FastAPI
- **GraphQL API** - Complete query interface with Strawberry (CRUD operations)
- **GraphQL Explorer** - Interactive query builder in the frontend
- **PostgreSQL/SQLite** - Seamless database switching (dev to prod)
- **Swagger Documentation** - Auto-generated API docs

### Frontend & UX
- **🌙🌞 Dark/Light Theme** - Persistent theme toggle with localStorage
- **✨ Glassmorphism UI** - Modern frosted glass aesthetic with backdrop blur
- **🎨 Gradient Backgrounds** - Animated particle effects
- **📱 Fully Responsive** - Optimized for desktop, tablet, and mobile
- **🔔 Toast Notifications** - Non-intrusive feedback system
- **⬆️ Scroll to Top** - Floating navigation button
- **📋 Demo Content** - Pre-loaded sample posts when database is empty

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

---

## 🏗 Project Structure

```
modern-blog/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration
├── graphql_schema.py    # Strawberry GraphQL schema (CRUD)
├── requirements.txt     # Python dependencies
├── runtime.txt          # Python version (3.11.9)
├── .env                 # Environment variables
├── models/
│   ├── models.py        # SQLAlchemy models (User, Post)
│   └── schemas.py       # Pydantic schemas
├── templates/
│   └── index.html       # Single Page Application (Vue 3)
└── static/
    ├── favicon.ico
    └── images/          # Screenshots and assets
```

---

## 📦 API Endpoints

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

### Queries
| Operation | Description |
|-----------|-------------|
| `posts` | Fetch all posts (sorted by date) |

### Mutations
| Operation | Description |
|-----------|-------------|
| `createPost` | Create a new post |
| `updatePost` | Update an existing post |
| `deletePost` | Delete a post |

### Example Query
```graphql
{
  posts {
    id
    title
    content
    excerpt
    status
    authorName
    createdAt
    tags
  }
}
```

### Example Mutation (Create Post)
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

### Example Mutation (Update Post)
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

### Example Mutation (Delete Post)
```graphql
mutation {
  deletePost(id: 1)
}
```

### GraphQL Explorer
The frontend includes an interactive **GraphQL Explorer** accessible from the Dashboard Metrics panel after login. Features:
- Query editor with syntax highlighting
- Variables input (JSON format)
- Real-time result display
- Pre-loaded example queries

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
- **Username:** `user`
- **Password:** `123456`

---

## 🌍 Deployment

### Render.com Configuration
- **Auto-deploy** from GitHub
- **Start Command:** `python main.py`
- **Environment:** Python 3.11
- **Database:** Managed PostgreSQL

The application automatically detects PostgreSQL connection strings and switches from SQLite accordingly.

---

## 👨‍💻 Developer

**Marcelo**  
[GitHub Profile](https://github.com/MarceloAdan73)

---

*"This project showcases how AI can accelerate development while maintaining code quality and architectural integrity."*

⭐ Star this repo if you found it helpful!

🚀 [Live Demo](https://modern-blog-tkzl.onrender.com/) | 📚 [API Docs](https://modern-blog-tkzl.onrender.com/docs) | 🔷 [GraphQL](https://modern-blog-tkzl.onrender.com/graphql)
